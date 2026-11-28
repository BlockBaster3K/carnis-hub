package com.carnis.mod.entity.ai;

import com.carnis.mod.block.HiveBody;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * Проход мобов улья сквозь плоть: компенсация гравитации и сброс пути
 * (задача N4).
 *
 * <p>Сама проходимость сделана в {@link HiveBody} — коллизия клетки плоти
 * пуста для мобов namespace {@code carnis}. Здесь два следствия, без которых
 * она не работает.
 *
 * <p><b>1. Гравитация.</b> Когда коллизия клетки пуста, моб внутри плоти
 * падает: опоры под ним больше нет. Улей под землёй — значит моб проваливался
 * бы в пещеры и к бедроку. Пока моб внутри плоти, его вертикальная скорость не
 * накапливается вниз; как только он вышел — падает как все. Это не парение:
 * вверх моб не поднимается, а внутри улья «метра» падения просто нет.
 *
 * <p><b>2. Кэш пути.</b> {@code PathNavigation.createPath} возвращает прежний
 * путь, если цель не менялась (проверено по исходникам 1.20.1: условие
 * {@code path != null && !path.isDone() && set.contains(targetPos)}), — то есть
 * маршрут, построенный до входа в плоскость, моб не пересчитал бы. Поэтому при
 * смене «в плоти / не в плоти» вызывается {@code navigation.stop()}: следующий
 * поиск идёт с чистого листа.
 *
 * <p><b>Почему это не телепорт.</b> Заказчик оговорил отдельно. Моб идёт
 * обычным ходом: скорость, поворот, анимация — штатные, снимается только
 * столкновение с плотью и только у своих.
 */
public final class HivePhasing {
    /** Ключ в persistent data: был ли моб в плоти на прошлой проверке. */
    private static final String INSIDE_KEY = "carnis_hive_inside";
    /** Насколько часто пересчитывать (в тиках) — задаёт HivePhasingEvents. */
    public static final int TICK_INTERVAL = 4;

    private HivePhasing() {
    }

    /**
     * Пересчитать состояние моба. Вызывается раз в {@link #TICK_INTERVAL}
     * тиков из {@code HivePhasingEvents}.
     */
    public static void tick(Mob mob) {
        if (!(mob.level() instanceof ServerLevel level)) return;
        boolean inside = insideHive(level, mob);

        if (inside) {
            // Опоры под мобом нет — не даём накопить падение.
            Vec3 motion = mob.getDeltaMovement();
            if (motion.y < 0.0D) {
                mob.setDeltaMovement(motion.x, 0.0D, motion.z);
            }
            mob.fallDistance = 0.0F;
        }

        // Смена режима — повод пересчитать маршрут: кэш мог быть построен до
        // того, как плоть стала проходимой, или наоборот — при выходе.
        boolean wasInside = mob.getPersistentData().getBoolean(INSIDE_KEY);
        if (wasInside != inside) {
            mob.getPersistentData().putBoolean(INSIDE_KEY, inside);
            mob.getNavigation().stop();
        }
    }

    /** Находится ли моб в клетке плоти. */
    public static boolean insideHive(ServerLevel level, Mob mob) {
        return HiveBody.isHiveBody(level.getBlockState(mob.blockPosition()));
    }

    /**
     * Стоит ли моб вплотную к плоти — тогда у него есть повод искать вход.
     *
     * <p>Без этой проверки моб у стены не начнёт новый маршрут: старый уже
     * построен «в обход», а пересчёт запускается только по смене режима или по
     * новой цели.
     */
    public static boolean touchesHive(ServerLevel level, Mob mob) {
        BlockPos base = mob.blockPosition();
        if (HiveBody.isHiveBody(level.getBlockState(base))) return true;
        for (Direction direction : Direction.values()) {
            BlockPos next = base.relative(direction);
            if (!level.hasChunkAt(next)) continue;
            if (HiveBody.isHiveBody(level.getBlockState(next))) return true;
        }
        return false;
    }

    /** Для проверок урона: моб сейчас в плоти и ему нечем дышать? (нет — проход). */
    public static boolean isPhasing(Mob mob) {
        return mob.level() instanceof ServerLevel level && insideHive(level, mob);
    }
}
