# HOTFIX-002 — полные исходники

Сборка и игровые тесты не выполнялись.

## `src/main/java/com/carnis/mod/entity/BiomassMaggotEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.FleshBulbBlock;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.ForgeEventFactory;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.List;

public final class BiomassMaggotEntity extends Monster implements GeoEntity, HivemindLinkedMob {
    public static final String FED_COUNT = "carnis:fed_count";
    private static final String FLESH_TICKS = "carnis:flesh_ticks";
    private static final TagKey<Block> BURROWABLE = TagKey.create(Registries.BLOCK,
            new ResourceLocation(CarnisMod.MOD_ID, "burrowable"));
    private static final EntityDataAccessor<Integer> ACTION = SynchedEntityData.defineId(
            BiomassMaggotEntity.class, EntityDataSerializers.INT);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.biomass_maggot.idle");
    private static final RawAnimation CRAWL = RawAnimation.begin().thenLoop("animation.biomass_maggot.crawl");
    private static final RawAnimation EAT = RawAnimation.begin().thenLoop("animation.biomass_maggot.eat");
    private static final RawAnimation BURROW = RawAnimation.begin().thenLoop("animation.biomass_maggot.burrow");
    private static final List<BlockPos> SEARCH_OFFSETS = buildOffsets();
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    // The travel goal hands off a reached block to the stationary work goal.
    private BlockPos pendingTarget;
    private WorkType pendingType;

    private enum WorkType { EAT, BURROW }

    public BiomassMaggotEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ACTION, 0);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 10.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.18D);
    }

    @Override protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new WorkGoal());
        goalSelector.addGoal(2, new BurrowGoal());
        goalSelector.addGoal(3, new EatRemainsGoal());
        goalSelector.addGoal(4, new WaterAvoidingRandomStrollGoal(this, 0.8D));
    }

    @Override protected void customServerAiStep() {
        BlockPos belowPos = blockPosition().below();
        int previous = getPersistentData().getInt(FLESH_TICKS);
        int ticks = previous;
        if (previous < 1200 && level().isLoaded(belowPos)) {
            BlockState below = level().getBlockState(belowPos);
            ticks = below.is(ModBlocks.LIVING_FLESH.get()) || below.is(ModBlocks.OSSIFIED_FLESH.get())
                    ? Math.min(1200, previous + 1) : 0;
        }
        getPersistentData().putInt(FLESH_TICKS, Math.min(1200, ticks));
        super.customServerAiStep();
    }

    private boolean readyToBurrow() {
        return getPersistentData().getInt(FED_COUNT) >= 2 || getPersistentData().getInt(FLESH_TICKS) >= 1200;
    }

    private static boolean isSafeBurrowMaterial(BlockState state) {
        return state.is(ModBlocks.LIVING_FLESH.get()) || state.is(ModBlocks.OSSIFIED_FLESH.get())
                || state.is(Blocks.DIRT) || state.is(Blocks.GRASS_BLOCK) || state.is(Blocks.PODZOL)
                || state.is(Blocks.MYCELIUM) || state.is(Blocks.MUD) || state.is(Blocks.SAND)
                || state.is(Blocks.GRAVEL) || state.is(Blocks.MOSS_BLOCK);
    }

    private boolean validTarget(WorkType type, BlockPos pos) {
        if (type == null || pos == null || !(level() instanceof ServerLevel server)
                || server.isOutsideBuildHeight(pos) || !server.hasChunkAt(pos)) return false;
        if (type == WorkType.EAT) {
            return !readyToBurrow() && server.getBlockState(pos).is(ModBlocks.BIOMASS_REMAINS.get());
        }
        BlockPos ground = pos.below();
        if (!readyToBurrow() || server.isOutsideBuildHeight(ground) || !server.hasChunkAt(ground)
                || !server.isEmptyBlock(pos)) return false;
        BlockState floor = server.getBlockState(ground);
        BlockState bulb = ModBlocks.FLESH_BULB.get().defaultBlockState().setValue(FleshBulbBlock.HANGING, false);
        return floor.is(BURROWABLE) && isSafeBurrowMaterial(floor)
                && floor.isFaceSturdy(server, ground, Direction.UP) && bulb.canSurvive(server, pos);
    }

    private boolean mayWork() {
        return isAlive() && level() instanceof ServerLevel server
                && ForgeEventFactory.getMobGriefingEvent(server, this);
    }

    private boolean closeTo(BlockPos pos) {
        return pos != null && distanceToSqr(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D) <= 1.7D;
    }

    private void queueWork(WorkType type, BlockPos pos) {
        pendingType = type;
        pendingTarget = pos.immutable();
    }

    private void clearPendingWork() {
        pendingTarget = null;
        pendingType = null;
    }

    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "locomotion", 2, state -> state.setAndContinue(
                entityData.get(ACTION) == 1 ? EAT : entityData.get(ACTION) == 2 ? BURROW : state.isMoving() ? CRAWL : IDLE)));
    }

    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }

    // Precomputed once. Each search attempt checks at most 256 positions, five ticks apart.
    private static List<BlockPos> buildOffsets() {
        List<BlockPos> offsets = new ArrayList<>();
        for (int x = -16; x <= 16; x++) for (int y = -16; y <= 16; y++) for (int z = -16; z <= 16; z++)
            if (x * x + y * y + z * z <= 256) offsets.add(new BlockPos(x, y, z));
        offsets.sort(Comparator.comparingInt(p -> p.getX() * p.getX() + p.getY() * p.getY() + p.getZ() * p.getZ()));
        return List.copyOf(offsets);
    }

    private abstract class SearchGoal extends Goal {
        private final WorkType type;
        private BlockPos target;
        private BlockPos anchor;
        private int cursor;
        private int searchCooldown;
        private int elapsed;

        SearchGoal(WorkType type) {
            this.type = type;
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        private boolean isValidTarget(BlockPos pos) { return validTarget(type, pos); }
        private boolean allowed() { return type == WorkType.BURROW ? readyToBurrow() : !readyToBurrow(); }

        private BlockPos findTarget(ServerLevel server) {
            if (anchor == null || anchor.distSqr(blockPosition()) > 4) {
                anchor = blockPosition();
                cursor = 0;
            }
            int end = Math.min(cursor + 256, SEARCH_OFFSETS.size());
            while (cursor < end) {
                BlockPos pos = anchor.offset(SEARCH_OFFSETS.get(cursor++));
                if (!server.isOutsideBuildHeight(pos) && server.hasChunkAt(pos) && isValidTarget(pos)) return pos;
            }
            if (cursor >= SEARCH_OFFSETS.size()) { cursor = 0; anchor = blockPosition(); }
            return null;
        }

        @Override public boolean canUse() {
            if (!(level() instanceof ServerLevel server) || pendingTarget != null || !allowed()
                    || tickCount < searchCooldown || !mayWork()) return false;
            searchCooldown = tickCount + 5;
            target = findTarget(server);
            return target != null;
        }

        @Override public boolean canContinueToUse() {
            boolean valid = target != null && level().isLoaded(target) && isValidTarget(target)
                    && allowed() && mayWork() && elapsed < 400;
            // Navigation can finish between AI ticks; transfer a reached target before stopping.
            if (valid && getNavigation().isDone() && closeTo(target)) queueWork(type, target);
            return valid && !getNavigation().isDone();
        }

        @Override public void start() {
            elapsed = 0;
            if (target == null || !level().isLoaded(target) || !isValidTarget(target) || !mayWork()) {
                stop();
                return;
            }
            if (closeTo(target)) {
                queueWork(type, target);
                stop();
            } else {
                getNavigation().moveTo(target.getX() + 0.5D, target.getY(), target.getZ() + 0.5D, 0.8D);
            }
        }

        @Override public void stop() {
            target = null;
            getNavigation().stop();
            entityData.set(ACTION, 0);
            anchor = null;
            cursor = 0;
        }

        @Override public boolean requiresUpdateEveryTick() { return true; }

        private boolean approach() {
            if (this.target == null) return false;
            if (closeTo(target)) return true;
            if (elapsed % 10 == 0)
                getNavigation().moveTo(target.getX() + 0.5D, target.getY(), target.getZ() + 0.5D, 0.8D);
            return false;
        }

        @Override public void tick() {
            if (target == null || !level().isLoaded(target) || !isValidTarget(target) || !mayWork()) {
                stop();
                return;
            }
            elapsed++;
            if (approach()) {
                queueWork(type, target);
                stop();
            }
        }
    }

    private final class EatRemainsGoal extends SearchGoal {
        EatRemainsGoal() { super(WorkType.EAT); }
    }

    private final class BurrowGoal extends SearchGoal {
        BurrowGoal() { super(WorkType.BURROW); }
    }

    /** Work continues while stationary; the search goal never pretends navigation is active. */
    private final class WorkGoal extends Goal {
        private BlockPos target;
        private WorkType type;
        private int workTicks;

        WorkGoal() { setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK)); }

        @Override public boolean canUse() {
            if (pendingTarget == null || pendingType == null) {
                clearPendingWork();
                return false;
            }
            if (!mayWork() || !level().isLoaded(pendingTarget) || !validTarget(pendingType, pendingTarget)
                    || !closeTo(pendingTarget)) {
                clearPendingWork();
                return false;
            }
            return true;
        }

        @Override public void start() {
            target = pendingTarget;
            type = pendingType;
            clearPendingWork();
            workTicks = 0;
            getNavigation().stop();
        }

        @Override public boolean canContinueToUse() {
            return target != null && type != null && level().isLoaded(target) && validTarget(type, target)
                    && closeTo(target) && mayWork();
        }

        @Override public boolean requiresUpdateEveryTick() { return true; }

        @Override public void stop() {
            target = null;
            type = null;
            workTicks = 0;
            getNavigation().stop();
            entityData.set(ACTION, 0);
        }

        @Override public void tick() {
            if (target == null || type == null || !(level() instanceof ServerLevel server)
                    || !server.isLoaded(target) || !validTarget(type, target) || !closeTo(target) || !mayWork()) {
                stop();
                return;
            }
            workTicks++;
            if (type == WorkType.EAT) {
                entityData.set(ACTION, 1);
                if (workTicks % 20 == 0) playSound(SoundEvents.GENERIC_EAT, 0.8F, 0.65F);
                if (workTicks >= 70) {
                    if (server.removeBlock(target, false)) {
                        getPersistentData().putInt(FED_COUNT, getPersistentData().getInt(FED_COUNT) + 1);
                        server.playSound(null, target, SoundEvents.GENERIC_EAT, SoundSource.HOSTILE, 1.0F, 0.7F);
                    }
                    stop();
                }
            } else {
                entityData.set(ACTION, 2);
                if (workTicks % 5 == 0) {
                    server.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, server.getBlockState(target.below())),
                            getX(), getY() + 0.1D, getZ(), 8, 0.15D, 0.05D, 0.15D, 0.03D);
                    server.sendParticles(ModParticles.BIOMASS_SPARK.get(), getX(), getY() + 0.1D, getZ(),
                            3, 0.1D, 0.05D, 0.1D, 0.02D);
                }
                if (workTicks >= 50) {
                    BlockState bulb = ModBlocks.FLESH_BULB.get().defaultBlockState().setValue(FleshBulbBlock.HANGING, false);
                    if (server.setBlockAndUpdate(target, bulb)) discard();
                    stop();
                }
            }
        }
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/CarnisFeedingGoal.java`

```java
package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.AssimilatingMob;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

public final class CarnisFeedingGoal extends Goal {
    public static final String DEADLINE = "carnis:feeding_until";
    public static final String X = "carnis:feeding_x";
    public static final String Y = "carnis:feeding_y";
    public static final String Z = "carnis:feeding_z";
    private static final String TRAVEL = "carnis:feeding_travel";
    private final Mob mob;
    private boolean facingLocked;
    private float feedingYaw;
    private float feedingPitch;

    public CarnisFeedingGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (!mob.isAlive() || !(mob.level() instanceof ServerLevel level)
                || !mob.getPersistentData().contains(DEADLINE)) return false;
        var tag = mob.getPersistentData();
        if (!tag.contains(X) || !tag.contains(Y) || !tag.contains(Z)
                || !Double.isFinite(tag.getDouble(X)) || !Double.isFinite(tag.getDouble(Y))
                || !Double.isFinite(tag.getDouble(Z))) {
            tag.remove(DEADLINE);
            tag.remove(TRAVEL);
            return false;
        }
        BlockPos pos = BlockPos.containing(tag.getDouble(X), tag.getDouble(Y), tag.getDouble(Z));
        return !level.isOutsideBuildHeight(pos) && level.hasChunkAt(pos);
    }

    @Override
    public boolean canContinueToUse() {
        return canUse();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void start() {
        facingLocked = false;
        setAssimilating(false);
        mob.setTarget(null);
    }

    @Override
    public void stop() {
        facingLocked = false;
        setAssimilating(false);
        mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        if (!canUse() || !(mob.level() instanceof ServerLevel level)) {
            stop();
            return;
        }
        var tag = mob.getPersistentData();
        Vec3 corpse = new Vec3(tag.getDouble(X), tag.getDouble(Y), tag.getDouble(Z));
        mob.setTarget(null);
        if (mob.distanceToSqr(corpse) > 4.0D) {
            facingLocked = false;
            setAssimilating(false);
            int travel = tag.getInt(TRAVEL) + 1;
            tag.putInt(TRAVEL, travel);
            tag.putInt(DEADLINE, 0);
            if (travel > 200) {
                tag.remove(DEADLINE);
                tag.remove(TRAVEL);
            } else if (travel % 10 == 1) {
                mob.getNavigation().moveTo(corpse.x, corpse.y, corpse.z, 1.0D);
            }
            return;
        }

        mob.getNavigation().stop();
        if (!facingLocked) {
            net.minecraft.core.BlockPos remains = findRemains(level, corpse);
            if (remains != null) corpse = Vec3.atCenterOf(remains);
            double dx = corpse.x - mob.getX(), dz = corpse.z - mob.getZ();
            double horizontal = Math.sqrt(dx * dx + dz * dz);
            float desiredYaw = horizontal < 1.0E-4D ? mob.getYRot()
                    : (float) Math.toDegrees(Math.atan2(-dx, dz));
            feedingYaw = mob.getYRot() + net.minecraft.util.Mth.wrapDegrees(desiredYaw - mob.getYRot());
            double dy = corpse.y - mob.getEyeY();
            feedingPitch = (float) net.minecraft.util.Mth.clamp(
                    -Math.toDegrees(Math.atan2(dy, Math.max(horizontal, 0.12D))), -70D, 70D);
            facingLocked = true;
        }
        mob.setYRot(feedingYaw);
        mob.setYHeadRot(feedingYaw);
        mob.setYBodyRot(feedingYaw);
        mob.setXRot(feedingPitch);
        setAssimilating(true);

        if (mob.tickCount % 20 == 0) {
            level.playSound(null, mob.blockPosition(), ModSounds.DIGESTOR_CHURN.get(),
                    SoundSource.HOSTILE, 0.8F, 0.7F);
        }
        if (mob.tickCount % 5 == 0) {
            Vec3 destination = mob.position().add(0.0D, mob.getBbHeight() * 0.55D, 0.0D);
            for (int i = 0; i < 2; i++) {
                Vec3 origin = corpse.add((level.random.nextDouble() - 0.5D) * 0.3D,
                        0.15D, (level.random.nextDouble() - 0.5D) * 0.3D);
                Vec3 velocity = destination.subtract(origin).scale(0.12D);
                level.sendParticles(ModParticles.BIOMASS_SPARK.get(), origin.x, origin.y, origin.z, 0,
                        velocity.x, velocity.y, velocity.z, 1.0D);
            }
        }
        if (tag.getInt(DEADLINE) + 1 >= 100) {
            tag.remove(DEADLINE);
            tag.remove(TRAVEL);
            net.minecraft.core.BlockPos remains = findRemains(level, corpse);
            if (remains != null && net.minecraftforge.event.ForgeEventFactory.getMobGriefingEvent(level, mob))
                level.removeBlock(remains, false);
            setAssimilating(false);
            facingLocked = false;
            CarnisWorldData.get(level).addBiomassPoints(50L);
            ModMessages.sendToPlayersInLevel(level);
        } else {
            tag.putInt(DEADLINE, tag.getInt(DEADLINE) + 1);
        }
    }

    private static net.minecraft.core.BlockPos findRemains(ServerLevel level, Vec3 corpse) {
        net.minecraft.core.BlockPos base = net.minecraft.core.BlockPos.containing(corpse);
        for (int dy : new int[]{0, -1, 1}) {
            net.minecraft.core.BlockPos pos = base.offset(0, dy, 0);
            if (level.hasChunkAt(pos) && !level.isOutsideBuildHeight(pos)
                    && level.getBlockState(pos).is(com.carnis.mod.init.ModBlocks.BIOMASS_REMAINS.get())) return pos;
        }
        return null;
    }

    private void setAssimilating(boolean value) {
        if (mob instanceof AssimilatingMob assimilatingMob) {
            assimilatingMob.setAssimilating(value);
        }
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/goal/HiveDefendHeartGoal.java`

```java
package com.carnis.mod.entity.ai.goal;

import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import java.util.EnumSet;

/** A defense order is pushed by an attack event, not discovered by scanning blocks. */
public final class HiveDefendHeartGoal extends Goal {
    private final Mob mob;
    private BlockPos destination;
    private int repath;
    public HiveDefendHeartGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }
    @Override public boolean canUse() {
        if (!(mob.level() instanceof ServerLevel level) || !mob.isAlive()) return false;
        destination = HiveSwarmCoordinator.defensePosition(mob);
        if (destination == null) { HiveSwarmCoordinator.clearDefense(mob); return false; }
        // Once near the threatened location, hand control back to normal combat.
        return level.hasChunkAt(destination) && farFromDefense() && !enemyClose();
    }
    @Override public boolean canContinueToUse() {
        BlockPos current = HiveSwarmCoordinator.defensePosition(mob);
        return mob.isAlive() && mob.level() instanceof ServerLevel level && destination != null
                && current != null && current.equals(destination) && level.hasChunkAt(destination)
                && farFromDefense() && !enemyClose();
    }
    private boolean farFromDefense() {
        return destination != null && mob.distanceToSqr(destination.getX() + .5D, destination.getY() + .5D, destination.getZ() + .5D) > 36.0D;
    }
    private boolean enemyClose() {
        var target = mob.getTarget();
        return target != null && target.isAlive() && target.level() == mob.level()
                && mob.distanceToSqr(target) <= 36.0D;
    }
    @Override public void start() { repath = 0; }
    @Override public void stop() { mob.getNavigation().stop(); destination = null; }
    @Override public void tick() {
        if (destination == null || !(mob.level() instanceof ServerLevel level)
                || !mob.isAlive() || !level.hasChunkAt(destination)) {
            stop();
            return;
        }
        BlockPos current = HiveSwarmCoordinator.defensePosition(mob);
        if (current == null || !current.equals(destination)) {
            stop();
            return;
        }
        if (--repath <= 0) {
            repath = 20;
            // A removed heart is still a useful rally point. No chunk is loaded by this goal.
            if (level.hasChunkAt(destination))
                mob.getNavigation().moveTo(destination.getX() + .5D, destination.getY(), destination.getZ() + .5D, 1.15D);
        }
        var target = mob.getTarget();
        if (target != null && target.isAlive() && target.level() == level)
            mob.getLookControl().setLookAt(target, 30.0F, 30.0F);
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/goal/HiveEscortLeaderGoal.java`

```java
package com.carnis.mod.entity.ai.goal;

import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HiveSentinelEntity;
import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;
import java.util.Comparator;
import java.util.EnumSet;

/** Follows a loaded leader without replacing any active combat target. */
public final class HiveEscortLeaderGoal extends Goal {
    private static final double SEARCH_RADIUS = 24.0D;
    private static final double INNER = 6.0D;
    private static final double OUTER = 14.0D;
    private final Mob mob;
    private Mob leader;
    private int nextSearch;
    private int repath;
    public HiveEscortLeaderGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }
    private boolean available() {
        return mob.isAlive() && mob.getTarget() == null
                && !mob.getPersistentData().contains(CarnisFeedingGoal.DEADLINE)
                && HiveSwarmCoordinator.defensePosition(mob) == null;
    }
    private static boolean isLeader(Mob candidate) {
        return candidate instanceof HiveSentinelEntity || candidate instanceof CerebralNexusEntity
                || candidate instanceof FleshAmalgamEntity;
    }
    @Override public boolean canUse() {
        if (!(mob.level() instanceof ServerLevel level) || !available() || mob.tickCount < nextSearch) return false;
        nextSearch = mob.tickCount + 40;
        leader = level.getEntitiesOfClass(Mob.class, mob.getBoundingBox().inflate(SEARCH_RADIUS),
                candidate -> candidate != mob && candidate.isAlive() && isLeader(candidate)
                        && mob.distanceToSqr(candidate) <= SEARCH_RADIUS * SEARCH_RADIUS)
                .stream().min(Comparator.comparingDouble(mob::distanceToSqr)).orElse(null);
        return leader != null;
    }
    @Override public boolean canContinueToUse() {
        return available() && leader != null && leader.isAlive() && !leader.isRemoved()
                && leader.level() == mob.level() && mob.level().isLoaded(leader.blockPosition())
                && mob.distanceToSqr(leader) <= SEARCH_RADIUS * SEARCH_RADIUS;
    }
    @Override public void start() { repath = 0; }
    @Override public void stop() { mob.getNavigation().stop(); leader = null; }
    @Override public void tick() {
        if (!canContinueToUse()) {
            stop();
            return;
        }
        if (--repath > 0) return;
        repath = 20;
        double distance = mob.distanceToSqr(leader);
        mob.getLookControl().setLookAt(leader, 30.0F, 30.0F);
        if (distance > OUTER * OUTER) {
            mob.getNavigation().moveTo(leader, 1.0D);
        } else if (distance < INNER * INNER) {
            Vec3 away = mob.position().subtract(leader.position()).multiply(1, 0, 1);
            if (away.lengthSqr() < 0.01D) away = new Vec3(1, 0, 0);
            Vec3 destination = leader.position().add(away.normalize().scale(9.0D));
            mob.getNavigation().moveTo(destination.x, destination.y, destination.z, 0.9D);
        } else {
            mob.getNavigation().stop();
        }
    }
}
```
