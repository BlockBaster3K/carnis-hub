package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** A bounded night-time incursion attempt once per level every 600 ticks. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class InfectionEvents {
    private static final long INTERVAL_TICKS = 600L;
    private static final long BIOMASS_LIMIT = 200L;
    private static final int ATTEMPTS = 12;
    private static final int RADIUS = 16;

    private InfectionEvents() { }

    @SubscribeEvent
    public static void onLevelTick(TickEvent.LevelTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.level instanceof ServerLevel level)
                || level.getGameTime() % INTERVAL_TICKS != 0
                || !level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)
                || level.getDifficulty() == Difficulty.PEACEFUL
                || !level.dimensionType().hasSkyLight()
                || CarnisWorldData.get(level).getBiomassPoints() >= BIOMASS_LIMIT) return;

        long dayTime = Math.floorMod(level.getDayTime(), 24000L);
        if (dayTime < 13000L || dayTime >= 23000L) return;

        // Reservoir sampling chooses uniformly without allocating a full candidate list.
        // This traverses loaded entities only once per interval, never loads chunks.
        Animal chosen = null;
        int seen = 0;
        for (Entity entity : level.getAllEntities()) {
            if (!(entity instanceof Animal animal) || !animal.isAlive()
                    || !"minecraft".equals(BuiltInRegistries.ENTITY_TYPE.getKey(animal.getType()).getNamespace())) continue;
            if (level.random.nextInt(++seen) == 0) chosen = animal;
        }
        if (chosen == null || !level.hasChunkAt(chosen.blockPosition())
                || containsTendril(level, new ChunkPos(chosen.blockPosition()))) return;

        for (int i = 0; i < ATTEMPTS; i++) {
            int dx = level.random.nextInt(RADIUS * 2 + 1) - RADIUS;
            int dz = level.random.nextInt(RADIUS * 2 + 1) - RADIUS;
            if (dx * dx + dz * dz > RADIUS * RADIUS) continue;
            BlockPos column = chosen.blockPosition().offset(dx, 0, dz);
            if (!level.hasChunkAt(column)) continue;
            BlockPos pos = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, column);
            if (!level.hasChunkAt(pos) || level.isOutsideBuildHeight(pos)
                    || !level.getBiome(pos).is(BiomeTags.IS_OVERWORLD)
                    || Vec3.atBottomCenterOf(pos).distanceToSqr(chosen.position()) > RADIUS * RADIUS
                    || containsTendril(level, new ChunkPos(pos))
                    || !ModEntities.canSpawnTendril(ModEntities.PARASITIC_TENDRIL.get(), level,
                            MobSpawnType.NATURAL, pos, level.random)) continue;
            AABB bounds = ModEntities.PARASITIC_TENDRIL.get().getDimensions()
                    .makeBoundingBox(pos.getX() + .5D, pos.getY(), pos.getZ() + .5D);
            if (!level.noCollision(bounds) || !level.getFluidState(pos).isEmpty()) continue;
            // EntityType.spawn performs normal entity initialization and insertion.
            ModEntities.PARASITIC_TENDRIL.get().spawn(level, pos, MobSpawnType.NATURAL);
            return;
        }
    }

    private static boolean containsTendril(ServerLevel level, ChunkPos chunk) {
        AABB bounds = new AABB(chunk.getMinBlockX(), level.getMinBuildHeight(), chunk.getMinBlockZ(),
                chunk.getMinBlockX() + 16, level.getMaxBuildHeight(), chunk.getMinBlockZ() + 16);
        return !level.getEntitiesOfClass(ParasiticTendrilEntity.class, bounds, Entity::isAlive).isEmpty();
    }
}
