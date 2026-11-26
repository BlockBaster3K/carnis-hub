package com.carnis.mod.util;

import net.minecraft.core.BlockPos;
import com.carnis.mod.init.ModBlockTags;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

import java.util.HashMap;
import java.util.Map;
import java.util.WeakHashMap;

/** Утилиты поиска блоков Улья и оценки подавления роста флоры. */
public final class HiveGrowthSuppression {
    /** Кэш изолирован по уровню и радиусу; packed BlockPos остаётся ключом самой записи. */
    private static final Map<Level, Map<Integer, Map<Long, Boolean>>> NEAR_HIVE_CACHE = new WeakHashMap<>();

    private HiveGrowthSuppression() {
    }

    /** Проверяет, входит ли блок в тег блоков Улья. */
    public static boolean isHiveBlock(Level level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        return state.is(ModBlockTags.HIVE_BLOCKS);
    }

    /** Ищет блок Улья в кубе с центром в указанной позиции. */
    public static boolean isNearHive(Level level, BlockPos pos, int radius) {
        if (radius < 0) {
            return false;
        }

        long packedPos = pos.asLong();
        synchronized (NEAR_HIVE_CACHE) {
            Map<Integer, Map<Long, Boolean>> levelCache = NEAR_HIVE_CACHE.get(level);
            if (levelCache != null) {
                Map<Long, Boolean> radiusCache = levelCache.get(radius);
                if (radiusCache != null) {
                    Boolean cached = radiusCache.get(packedPos);
                    if (cached != null) {
                        return cached;
                    }
                }
            }
        }

        boolean found = false;
        BlockPos.MutableBlockPos cursor = new BlockPos.MutableBlockPos();
        search:
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dy = -radius; dy <= radius; dy++) {
                for (int dz = -radius; dz <= radius; dz++) {
                    cursor.setWithOffset(pos, dx, dy, dz);
                    if (isHiveBlock(level, cursor)) {
                        found = true;
                        break search;
                    }
                }
            }
        }

        synchronized (NEAR_HIVE_CACHE) {
            NEAR_HIVE_CACHE
                    .computeIfAbsent(level, ignored -> new HashMap<>())
                    .computeIfAbsent(radius, ignored -> new HashMap<>())
                    .put(packedPos, found);
        }
        return found;
    }

    /** Возвращает долю обычного роста, если рядом найден блок Улья. */
    public static float getSuppressionFactor(Level level, BlockPos pos, int radius, int strength) {
        if (!isNearHive(level, pos, radius)) {
            return 1.0F;
        }
        int boundedStrength = Math.max(0, Math.min(100, strength));
        return 1.0F - boundedStrength / 100.0F;
    }

    /** Сбрасывает результаты поиска; вызывается периодически серверным обработчиком. */
    public static void clearCache() {
        synchronized (NEAR_HIVE_CACHE) {
            NEAR_HIVE_CACHE.clear();
        }
    }
}
