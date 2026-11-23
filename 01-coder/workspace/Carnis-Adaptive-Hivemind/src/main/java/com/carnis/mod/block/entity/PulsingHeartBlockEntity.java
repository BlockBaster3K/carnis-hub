package com.carnis.mod.block.entity;

import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.HiveSentinelEntity;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import com.carnis.mod.world.infection.InfectionTickQueue;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import software.bernie.geckolib.animatable.GeoBlockEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

public final class PulsingHeartBlockEntity extends BlockEntity implements GeoBlockEntity {
    public static final int PULSE_INTERVAL_TICKS = 100;
    public static final int PULSE_RADIUS = 8;
    private static final RawAnimation PULSE_ANIMATION = RawAnimation.begin().thenLoop("animation.pulsing_heart.pulse");
    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private final Set<Long> infected = new HashSet<>();
    private final List<Long> generatedTissue = new ArrayList<>();
    private long biomass;
    private UUID sentinel;
    private boolean initialized;

    public PulsingHeartBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.PULSING_HEART.get(), pos, state); }
    public int getInfectedBlocksCount() { return infected.size(); }
    public void seedGeneratedTissue(List<BlockPos> positions) {
        for (BlockPos pos : positions) generatedTissue.add(pos.asLong());
        setChanged();
    }
    public long getBiomass() { return biomass; }
    public void addBiomass(long value) {
        if (value <= 0) return;
        biomass = biomass > Long.MAX_VALUE - value ? Long.MAX_VALUE : biomass + value;
        setChanged();
    }
    public void observeInfection(BlockPos pos, boolean present) {
        if (pos.distSqr(worldPosition) > 32D * 32D) return;
        if (present ? infected.add(pos.asLong()) : infected.remove(pos.asLong())) setChanged();
    }
    public void sentinelDied(UUID id) {
        if (id.equals(sentinel)) {
            if (level instanceof ServerLevel server) HiveNetwork.get(server).consumeSentinelDeath(id);
            sentinel = null; setChanged();
        }
    }
    @Override protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putLongArray("InfectedPositions", new ArrayList<>(infected));
        tag.putLongArray("GeneratedTissuePending", generatedTissue);
        tag.putInt("infected_blocks_count", infected.size());
        tag.putLong("ClusterBiomass", biomass);
        if (sentinel != null) tag.putUUID("Sentinel", sentinel);
    }
    @Override public void load(CompoundTag tag) {
        super.load(tag); infected.clear();
        for (long p : tag.getLongArray("InfectedPositions")) infected.add(p);
        generatedTissue.clear();
        for (long p : tag.getLongArray("GeneratedTissuePending")) generatedTissue.add(p);
        biomass = Math.max(0, tag.getLong("ClusterBiomass"));
        sentinel = tag.hasUUID("Sentinel") ? tag.getUUID("Sentinel") : null;
        initialized = false;
    }
    public static void serverTick(Level world, BlockPos pos, BlockState state, PulsingHeartBlockEntity heart) {
        if (!(world instanceof ServerLevel level)) return;
        if (!heart.initialized) {
            // Rebuild from the event-maintained index, never from a cube of world blocks.
            heart.infected.clear();
            for (BlockPos p : HiveNetwork.get(level).positions(HiveNetwork.Kind.INFECTION, pos, 32)) heart.infected.add(p.asLong());
            heart.initialized = true;
            heart.setChanged();
        }
        if (!heart.generatedTissue.isEmpty()) {
            int count = Math.min(64, heart.generatedTissue.size());
            List<BlockPos> batch = new ArrayList<>(count);
            for (int i = 0; i < count; i++) batch.add(BlockPos.of(heart.generatedTissue.get(i)));
            HiveNetwork.registerGenerated(level, pos, batch);
            heart.generatedTissue.subList(0, count).clear();
            heart.setChanged();
        }
        if (!InfectionTickQueue.refreshHeartChunk(level, pos)) return;
        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), PULSE_INTERVAL_TICKS), PULSE_INTERVAL_TICKS) == 0)
            heart.pulse(level);
    }
    private void pulse(ServerLevel level) {
        com.carnis.mod.event.AmalgamationHandler.onHighBiomassPulse(level, worldPosition);
        if (sentinel != null && HiveNetwork.get(level).consumeSentinelDeath(sentinel)) { sentinel = null; setChanged(); }
        if (sentinel == null) {
            var area = new net.minecraft.world.phys.AABB(worldPosition).inflate(32);
            for (HiveSentinelEntity guard : level.getEntitiesOfClass(HiveSentinelEntity.class, area,
                    e -> e.isAlive() && e.blockPosition().distSqr(worldPosition) <= 1024)) {
                sentinel = guard.getUUID(); guard.setHeartPos(worldPosition); setChanged(); break;
            }
        }
        int queued = 0;
        for (long packed : infected) {
            BlockPos p = BlockPos.of(packed);
            if (p.distSqr(worldPosition) <= PULSE_RADIUS * PULSE_RADIUS && level.hasChunkAt(p)
                    && InfectionTickQueue.isInfectionSource(level.getBlockState(p))) {
                InfectionTickQueue.enqueueHeartPulse(level, p);
                if (++queued >= 6) break;
            }
        }
        if (!level.getGameRules().getBoolean(net.minecraft.world.level.GameRules.RULE_MOBGRIEFING)) return;
        if (infected.size() >= 25 && !hasOrgan(level, HiveNetwork.Kind.EYE)) morphBlock(level, 0);
        else if (infected.size() >= 50 && sentinel == null) morphBlock(level, 1);
        else if (infected.size() >= 75 && !hasOrgan(level, HiveNetwork.Kind.POOL)) morphBlock(level, 2);
        else if (infected.size() >= 100 && !hasOrgan(level, HiveNetwork.Kind.PILLAR)) morphBlock(level, 3);
        else if (infected.size() >= 100 && sentinel != null && biomass >= 200
                && HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.EYE, worldPosition, 32) != null
                && HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.POOL, worldPosition, 32) != null
                && HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.PILLAR, worldPosition, 32) != null) metamorphose(level);
    }
    private boolean hasOrgan(ServerLevel level, HiveNetwork.Kind kind) {
        for (BlockPos p : HiveNetwork.get(level).positions(kind, worldPosition, 32)) {
            if (!level.hasChunkAt(p)) return true; // Unknown unloaded organ is not duplicated.
            BlockState state = level.getBlockState(p);
            if ((kind == HiveNetwork.Kind.EYE && state.is(ModBlocks.HIVE_EYE.get()))
                    || (kind == HiveNetwork.Kind.POOL && state.is(ModBlocks.STOMACH_POOL.get()))
                    || (kind == HiveNetwork.Kind.PILLAR && state.is(ModBlocks.NERVE_PILLAR.get()))) return true;
        }
        return false;
    }
    private BlockPos pickFlesh(ServerLevel level) {
        BlockPos selected = null; int seen = 0;
        for (long packed : infected) {
            BlockPos p = BlockPos.of(packed); double d = p.distSqr(worldPosition);
            if (d < 64 || d > 576 || !level.hasChunkAt(p) || !level.hasChunkAt(p.below()) || !level.hasChunkAt(p.above())) continue;
            if (!level.getBlockState(p).is(ModBlocks.LIVING_FLESH.get()) || !level.isEmptyBlock(p.above())
                    || !level.getBlockState(p.below()).isFaceSturdy(level, p.below(), Direction.UP)) continue;
            if (level.random.nextInt(++seen) == 0) selected = p;
        }
        return selected;
    }
    private void morphBlock(ServerLevel level, int organ) {
        BlockPos pos = pickFlesh(level);
        if (pos == null) return;
        if (organ == 1) {
            HiveSentinelEntity entity = ModEntities.HIVE_SENTINEL.get().create(level);
            if (entity == null) return;
            entity.moveTo(pos.getX() + .5, pos.getY(), pos.getZ() + .5, 0, 0);
            entity.setHeartPos(worldPosition); entity.setPersistenceRequired();
            BlockState old = level.getBlockState(pos);
            if (!level.removeBlock(pos, false)) return;
            if (!level.addFreshEntity(entity)) { level.setBlockAndUpdate(pos, old); return; }
            sentinel = entity.getUUID(); setChanged();
        } else {
            BlockState replacement = organ == 0 ? ModBlocks.HIVE_EYE.get().defaultBlockState()
                    : organ == 2 ? ModBlocks.STOMACH_POOL.get().defaultBlockState() : ModBlocks.NERVE_PILLAR.get().defaultBlockState();
            if (!level.setBlockAndUpdate(pos, replacement)) return;
        }
        level.playSound(null, pos, ModSounds.PULSING_HEART_BEAT.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
    }
    private void metamorphose(ServerLevel level) {
        Entity entity = level.getEntity(sentinel);
        if (!(entity instanceof HiveSentinelEntity guard) || !guard.isAlive()) return;
        List<BlockPos> satellites = new ArrayList<>();
        for (BlockPos p : HiveNetwork.get(level).positions(HiveNetwork.Kind.INFECTION, worldPosition, 64)) {
            double d = p.distSqr(worldPosition);
            if (d < 48D * 48D || !level.hasChunkAt(p) || !level.getBlockState(p).is(ModBlocks.LIVING_FLESH.get())) continue;
            if (!satellites.isEmpty() && p.distSqr(satellites.get(0)) < 32D * 32D) continue;
            satellites.add(p);
            if (satellites.size() == 2) break;
        }
        if (satellites.size() < 2) return; // No forced chunk loading or partial budding.
        CerebralNexusEntity nexus = ModEntities.CEREBRAL_NEXUS.get().create(level);
        if (nexus == null) return;
        nexus.moveTo(worldPosition.getX() + .5D, worldPosition.getY(), worldPosition.getZ() + .5D, 0, 0);
        nexus.setPersistenceRequired(); nexus.setBiomass(biomass - 200);
        BlockPos first = satellites.get(0), second = satellites.get(1);
        if (!level.setBlockAndUpdate(first, ModBlocks.PULSING_HEART.get().defaultBlockState())) return;
        if (!level.setBlockAndUpdate(second, ModBlocks.PULSING_HEART.get().defaultBlockState())) {
            level.setBlockAndUpdate(first, ModBlocks.LIVING_FLESH.get().defaultBlockState()); return;
        }
        if (!level.addFreshEntity(nexus)) {
            level.setBlockAndUpdate(first, ModBlocks.LIVING_FLESH.get().defaultBlockState());
            level.setBlockAndUpdate(second, ModBlocks.LIVING_FLESH.get().defaultBlockState()); return;
        }
        level.playSound(null, worldPosition, ModSounds.AMALGAM_ROAR.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), worldPosition.getX() + .5, worldPosition.getY() + .7,
                worldPosition.getZ() + .5, 80, .6, .7, .6, .15);
        level.removeBlock(worldPosition, false);
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "pulse_controller", 0, state -> state.setAndContinue(PULSE_ANIMATION)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return animationCache; }
}
