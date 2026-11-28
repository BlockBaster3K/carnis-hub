package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.ai.HivePhasing;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.EntityLeaveLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;

/**
 * Тик прохода мобов улья сквозь плоть (задача N4).
 *
 * <p><b>Зачем свой список.</b> Обход {@code level.getEntities()} каждый тик
 * стоил бы на порядок дороже: на сервере живут сотни сущностей, а проверять
 * надо единицы. Список ведут события входа/выхода сущности с уровня, поэтому
 * платим только за мобов мода.
 *
 * <p><b>Зачем прореживание.</b> Режим «в плоти / не в плоти» меняется на
 * границе блока, то есть за несколько десятых секунды. Проверять каждого моба
 * каждый тик — расточительство; {@code HivePhasing.TICK_INTERVAL} тиков вполне
 * хватает, и мобы разнесены по корзинам по {@code id}, чтобы не проверять всех
 * в один тик.
 *
 * <p><b>Зачем WeakHashMap по уровням.</b> Уровни умирают (переход между
 * измерениями, остановка сервера). Слабая ссылка не держит мир живым.
 */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HivePhasingEvents {
    private static final Map<ServerLevel, List<Mob>> HIVE_MOBS = new WeakHashMap<>();

    private HivePhasingEvents() {
    }

    @SubscribeEvent
    public static void onJoin(EntityJoinLevelEvent event) {
        if (event.getLevel().isClientSide()) return;
        if (!(event.getLevel() instanceof ServerLevel level)) return;
        if (!(event.getEntity() instanceof Mob mob)) return;
        if (!com.carnis.mod.block.HiveBody.mayPhase(mob)) return;
        List<Mob> mobs = HIVE_MOBS.computeIfAbsent(level, ignored -> new ArrayList<>());
        // Идемпотентно: после перехода между измерениями сущность «входит»
        // повторно.
        if (!mobs.contains(mob)) mobs.add(mob);
    }

    @SubscribeEvent
    public static void onLeave(EntityLeaveLevelEvent event) {
        if (!(event.getLevel() instanceof ServerLevel level)) return;
        List<Mob> mobs = HIVE_MOBS.get(level);
        if (mobs != null) mobs.remove(event.getEntity());
    }

    @SubscribeEvent
    public static void onLevelTick(TickEvent.LevelTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        if (!(event.level instanceof ServerLevel level)) return;
        List<Mob> mobs = HIVE_MOBS.get(level);
        if (mobs == null || mobs.isEmpty()) return;

        int interval = HivePhasing.TICK_INTERVAL;
        int bucket = (int) (level.getGameTime() % interval);
        for (int i = mobs.size() - 1; i >= 0; i--) {
            Mob mob = mobs.get(i);
            if (mob.isRemoved() || !mob.isAlive()) {
                mobs.remove(i);
                continue;
            }
            // Прореживание: моб проверяется в свой тик, разнесённо по id.
            if (Math.floorMod(mob.getId() + bucket, interval) != 0) continue;
            HivePhasing.tick(mob);
        }
    }
}
