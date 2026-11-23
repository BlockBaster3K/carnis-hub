# Шаг 10 — полный код

## HiveSentinelEntity.java

```java
package com.carnis.mod.entity;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.event.HypnosisEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.animal.Pig;
import net.minecraft.world.entity.animal.Sheep;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class HiveSentinelEntity extends Monster implements GeoEntity, HivemindLinkedMob {
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.hive_sentinel.idle");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private BlockPos heartPos;
    public HiveSentinelEntity(EntityType<? extends Monster> type, Level level) { super(type, level); setNoGravity(true); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 60.0D)
                .add(Attributes.ARMOR, 8.0D).add(Attributes.KNOCKBACK_RESISTANCE, 1.0D).add(Attributes.MOVEMENT_SPEED, 0.0D);
    }
    public void setHeartPos(BlockPos pos) { heartPos = pos.immutable(); }
    @Override public boolean isPushable() { return false; }
    @Override public void push(double x, double y, double z) { }
    @Override protected void registerGoals() { }
    @Override public void tick() {
        super.tick();
        setDeltaMovement(0, 0, 0);
        if (!(level() instanceof ServerLevel server) || !isAlive() || tickCount % 20 != 0) return;
        if (tickCount % 100 == 0) server.playSound(null, blockPosition(), ModSounds.PHANTOM_WHISPER.get(), SoundSource.HOSTILE, 0.9F, .65F);
        BlockPos pool = heartPos == null ? null : HiveNetwork.nearestLoaded(server, HiveNetwork.Kind.POOL, heartPos, 32);
        AABB area = getBoundingBox().inflate(16.0D);
        for (var animal : server.getEntitiesOfClass(net.minecraft.world.entity.animal.Animal.class, area,
                a -> (a instanceof Cow || a instanceof Sheep || a instanceof Pig) && a.isAlive()
                        && a.distanceToSqr(this) <= 256.0D && !InfectionHandler.isInfected(a))) {
            HypnosisEvents.apply(animal, server, pool);
        }
    }
    @Override public void die(net.minecraft.world.damagesource.DamageSource source) {
        if (level() instanceof ServerLevel server && heartPos != null) {
            HiveNetwork.get(server).noteSentinelDeath(getUUID());
            if (server.hasChunkAt(heartPos) && server.getBlockEntity(heartPos) instanceof PulsingHeartBlockEntity heart)
                heart.sentinelDied(getUUID());
        }
        super.die(source);
    }
    @Override public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag); if (heartPos != null) tag.putLong("HiveHeart", heartPos.asLong());
    }
    @Override public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag); if (tag.contains("HiveHeart")) heartPos = BlockPos.of(tag.getLong("HiveHeart"));
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "idle", 0, state -> state.setAndContinue(IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
```

## PulsingHeartBlockEntity.java

```java
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
    private long biomass;
    private UUID sentinel;
    private boolean initialized;

    public PulsingHeartBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.PULSING_HEART.get(), pos, state); }
    public int getInfectedBlocksCount() { return infected.size(); }
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
        tag.putInt("infected_blocks_count", infected.size());
        tag.putLong("ClusterBiomass", biomass);
        if (sentinel != null) tag.putUUID("Sentinel", sentinel);
    }
    @Override public void load(CompoundTag tag) {
        super.load(tag); infected.clear();
        for (long p : tag.getLongArray("InfectedPositions")) infected.add(p);
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
        level.playSound(null, pos, ModSounds.PULSING_HEART_BEAT.get(), SoundSource.BLOCKS, 1.0F, .65F);
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
        level.playSound(null, worldPosition, ModSounds.AMALGAM_ROAR.get(), SoundSource.HOSTILE, 2F, .65F);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), worldPosition.getX() + .5, worldPosition.getY() + .7,
                worldPosition.getZ() + .5, 80, .6, .7, .6, .15);
        level.removeBlock(worldPosition, false);
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "pulse_controller", 0, state -> state.setAndContinue(PULSE_ANIMATION)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return animationCache; }
}
```

## StomachPoolBlock.java

```java
package com.carnis.mod.block;

import com.carnis.mod.init.ModItems;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class StomachPoolBlock extends Block {
    @Override public void onPlace(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState old, boolean moving) {
        super.onPlace(state, level, pos, old, moving);
        if (!old.is(state.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
    }
    @Override public void onRemove(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
        super.onRemove(state, level, pos, next, moving);
    }
    @Override public void randomTick(net.minecraft.world.level.block.state.BlockState state, net.minecraft.server.level.ServerLevel level,
            net.minecraft.core.BlockPos pos, net.minecraft.util.RandomSource random) {
        com.carnis.mod.world.HiveNetwork.observe(level, pos, state, true);
    }
    public StomachPoolBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        if (!(level instanceof ServerLevel server)) {
            return;
        }
        if (entity instanceof ItemEntity item && item.isAlive() && !item.getItem().isEmpty()) {
            ItemStack stack = item.getItem();
            FoodProperties food = stack.getFoodProperties(null);
            boolean flesh = stack.is(Items.ROTTEN_FLESH) || stack.is(ModItems.LIVING_FLESH.get())
                    || stack.is(ModItems.OSSIFIED_FLESH.get()) || stack.is(ModItems.FIREPROOF_FLESH.get())
                    || food != null && food.isMeat();
            long value = (long) stack.getCount() * (flesh ? 5L : 1L);
            item.discard();
            CarnisWorldData.get(server).addBiomassPoints(value);
            ModMessages.sendToPlayersInLevel(server);
            server.playSound(null, pos, SoundEvents.GENERIC_SPLASH, SoundSource.BLOCKS, 0.6F, 0.8F);
            server.sendParticles(ParticleTypes.BUBBLE_POP, item.getX(), item.getY(), item.getZ(),
                    8, 0.2D, 0.2D, 0.2D, 0.02D);
        } else if (entity instanceof LivingEntity living && living.tickCount % 20 == 0) {
            var heart = com.carnis.mod.world.HiveNetwork.nearestHeart(server, pos, 32);
            boolean mob = living instanceof net.minecraft.world.entity.Mob;
            if (heart != null && mob) living.getPersistentData().putBoolean("carnis:pool_dissolving", true);
            living.hurt(server.damageSources().generic(), 5.0F);
            server.playSound(null, pos, com.carnis.mod.init.ModSounds.ACID_SPLASH.get(), SoundSource.BLOCKS, .7F, .85F);
            if (heart != null && mob && living.isDeadOrDying()) {
                long biomass = living instanceof net.minecraft.world.entity.animal.Cow ? 30L : 20L;
                heart.addBiomass(biomass);
            }
            living.getPersistentData().remove("carnis:pool_dissolving");
        }
    }
}
```

## HiveNetwork.java

```java
package com.carnis.mod.world;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.world.infection.InfectionTickQueue;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

/** Persisted, per-dimension position index. Only known positions are visited; no voxel scans. */
public final class HiveNetwork extends SavedData {
    public enum Kind { INFECTION, EYE, POOL, PILLAR }
    private final EnumMap<Kind, Map<Long, Set<Long>>> byChunk = new EnumMap<>(Kind.class);
    private final Set<UUID> deadSentinels = new HashSet<>();
    public HiveNetwork() { for (Kind k : Kind.values()) byChunk.put(k, new HashMap<>()); }
    public static HiveNetwork get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(HiveNetwork::load, HiveNetwork::new, "carnis_hive_network");
    }
    public static HiveNetwork load(CompoundTag tag) {
        HiveNetwork data = new HiveNetwork();
        for (Kind k : Kind.values()) for (long packed : tag.getLongArray(k.name())) data.put(k, BlockPos.of(packed), true);
        var dead = tag.getList("DeadSentinels", net.minecraft.nbt.Tag.TAG_STRING);
        for (int i = 0; i < dead.size(); i++) {
            try { data.deadSentinels.add(UUID.fromString(dead.getString(i))); } catch (IllegalArgumentException ignored) { }
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag tag) {
        for (Kind k : Kind.values()) {
            List<Long> list = new ArrayList<>();
            byChunk.get(k).values().forEach(list::addAll);
            tag.putLongArray(k.name(), list);
        }
        var dead = new net.minecraft.nbt.ListTag();
        deadSentinels.forEach(id -> dead.add(net.minecraft.nbt.StringTag.valueOf(id.toString())));
        tag.put("DeadSentinels", dead);
        return tag;
    }
    public void noteSentinelDeath(UUID id) { if (deadSentinels.add(id)) setDirty(); }
    public boolean consumeSentinelDeath(UUID id) { boolean found = deadSentinels.remove(id); if (found) setDirty(); return found; }
    private boolean put(Kind kind, BlockPos pos, boolean present) {
        long chunk = new ChunkPos(pos).toLong();
        Map<Long, Set<Long>> map = byChunk.get(kind);
        if (present) return map.computeIfAbsent(chunk, k -> new HashSet<>()).add(pos.asLong());
        Set<Long> entries = map.get(chunk);
        if (entries == null || !entries.remove(pos.asLong())) return false;
        if (entries.isEmpty()) map.remove(chunk);
        return true;
    }
    public static void observe(ServerLevel level, BlockPos pos, BlockState state, boolean present) {
        HiveNetwork index = get(level);
        for (Kind kind : Kind.values()) {
            boolean matches = switch (kind) {
                case INFECTION -> InfectionTickQueue.isInfectionSource(state);
                case EYE -> state.is(ModBlocks.HIVE_EYE.get());
                case POOL -> state.is(ModBlocks.STOMACH_POOL.get());
                case PILLAR -> state.is(ModBlocks.NERVE_PILLAR.get());
            };
            if (matches && index.put(kind, pos, present)) {
                index.setDirty();
                if (kind == Kind.INFECTION) for (PulsingHeartBlockEntity heart : nearbyHearts(level, pos, 32)) heart.observeInfection(pos, present);
            }
        }
    }
    public List<BlockPos> positions(Kind kind, BlockPos origin, int radius) {
        List<BlockPos> found = new ArrayList<>();
        int minX = (origin.getX() - radius) >> 4, maxX = (origin.getX() + radius) >> 4;
        int minZ = (origin.getZ() - radius) >> 4, maxZ = (origin.getZ() + radius) >> 4;
        for (int x = minX; x <= maxX; x++) for (int z = minZ; z <= maxZ; z++) {
            Set<Long> set = byChunk.get(kind).get(ChunkPos.asLong(x, z));
            if (set == null) continue;
            for (long packed : set) {
                BlockPos p = BlockPos.of(packed);
                if (p.distSqr(origin) <= (double) radius * radius) found.add(p);
            }
        }
        return found;
    }
    public static List<PulsingHeartBlockEntity> nearbyHearts(ServerLevel level, BlockPos origin, int radius) {
        List<PulsingHeartBlockEntity> result = new ArrayList<>();
        int minX = (origin.getX() - radius) >> 4, maxX = (origin.getX() + radius) >> 4;
        int minZ = (origin.getZ() - radius) >> 4, maxZ = (origin.getZ() + radius) >> 4;
        for (int x = minX; x <= maxX; x++) for (int z = minZ; z <= maxZ; z++) {
            var chunk = level.getChunkSource().getChunkNow(x, z);
            if (chunk == null) continue;
            for (var be : chunk.getBlockEntities().values())
                if (be instanceof PulsingHeartBlockEntity heart && heart.getBlockPos().distSqr(origin) <= (double)radius * radius) result.add(heart);
        }
        return result;
    }
    public static PulsingHeartBlockEntity nearestHeart(ServerLevel level, BlockPos pos, int radius) {
        return nearbyHearts(level, pos, radius).stream().min(Comparator.comparingDouble(h -> h.getBlockPos().distSqr(pos))).orElse(null);
    }
    public static BlockPos nearestLoaded(ServerLevel level, Kind kind, BlockPos pos, int radius) {
        BlockPos best = null; double distance = Double.MAX_VALUE;
        for (BlockPos p : get(level).positions(kind, pos, radius)) {
            if (!level.hasChunkAt(p)) continue;
            BlockState state = level.getBlockState(p);
            boolean valid = switch(kind) {
                case INFECTION -> InfectionTickQueue.isInfectionSource(state);
                case EYE -> state.is(ModBlocks.HIVE_EYE.get());
                case POOL -> state.is(ModBlocks.STOMACH_POOL.get());
                case PILLAR -> state.is(ModBlocks.NERVE_PILLAR.get());
            };
            if (!valid) { get(level).put(kind, p, false); get(level).setDirty(); continue; }
            double d = p.distSqr(pos); if (d < distance) { best = p; distance = d; }
        }
        return best;
    }
    public static boolean shielded(ServerLevel level, BlockPos pos) { return nearestLoaded(level, Kind.PILLAR, pos, 32) != null; }
}
```

## HypnosisEvents.java

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.EnumSet;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HypnosisEvents {
    private static final String UNTIL = "carnis:trance_until", POOL = "carnis:trance_pool";
    private HypnosisEvents() { }
    public static void apply(Mob mob, ServerLevel level, BlockPos pool) {
        mob.getPersistentData().putLong(UNTIL, level.getGameTime() + 60);
        if (pool == null) mob.getPersistentData().remove(POOL); else mob.getPersistentData().putLong(POOL, pool.asLong());
    }
    @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || !(mob.level() instanceof ServerLevel level)) return;
        if (mob.tickCount % 10 != 0) return;
        boolean active = mob.getPersistentData().getLong(UNTIL) > level.getGameTime();
        TranceGoal found = null;
        for (var wrapped : mob.goalSelector.getAvailableGoals())
            if (wrapped.getGoal() instanceof TranceGoal g) { found = g; break; }
        if (active && found == null) mob.goalSelector.addGoal(0, new TranceGoal(mob));
        else if (!active && found != null) {
            mob.goalSelector.removeGoal(found);
            mob.getPersistentData().remove(UNTIL);
            mob.getPersistentData().remove(POOL);
        }
    }
    private static final class TranceGoal extends Goal {
        private final Mob mob;
        TranceGoal(Mob mob) { this.mob = mob; setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK)); }
        @Override public boolean canUse() { return mob.level() instanceof ServerLevel l && mob.getPersistentData().getLong(UNTIL) > l.getGameTime(); }
        @Override public boolean canContinueToUse() { return canUse(); }
        @Override public void start() { mob.getNavigation().stop(); }
        @Override public void stop() { mob.getNavigation().stop(); }
        @Override public void tick() {
            if (!(mob.level() instanceof ServerLevel level)) return;
            if (!mob.getPersistentData().contains(POOL)) { mob.getNavigation().stop(); return; }
            BlockPos pool = BlockPos.of(mob.getPersistentData().getLong(POOL));
            if (!level.hasChunkAt(pool) || !level.getBlockState(pool).is(ModBlocks.STOMACH_POOL.get())) {
                mob.getNavigation().stop(); return;
            }
            if (mob.tickCount % 10 == 0) mob.getNavigation().moveTo(pool.getX() + .5D, pool.getY(), pool.getZ() + .5D, 0.9D);
        }
        @Override public boolean requiresUpdateEveryTick() { return true; }
    }
}
```

## CerebralNexusEntity.java

```java
package com.carnis.mod.entity;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/** Tier-two command node; later tier mechanics are intentionally not defined here. */
public final class CerebralNexusEntity extends Monster implements GeoEntity, HivemindLinkedMob {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private long biomass;
    public CerebralNexusEntity(EntityType<? extends Monster> type, Level level) { super(type, level); setNoGravity(true); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 120D).add(Attributes.ARMOR, 10D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1D).add(Attributes.MOVEMENT_SPEED, 0D);
    }
    public void setBiomass(long value) { biomass = Math.max(0L, value); }
    @Override public boolean isPushable() { return false; }
    @Override public void push(double x, double y, double z) { }
    @Override protected void registerGoals() { }
    @Override public void tick() { super.tick(); setDeltaMovement(0, 0, 0); }
    @Override public void addAdditionalSaveData(CompoundTag tag) { super.addAdditionalSaveData(tag); tag.putLong("Biomass", biomass); }
    @Override public void readAdditionalSaveData(CompoundTag tag) { super.readAdditionalSaveData(tag); biomass = Math.max(0, tag.getLong("Biomass")); }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "idle", 0, state -> state.setAndContinue(RawAnimation.begin().thenLoop("animation.cerebral_nexus.idle"))));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
```

