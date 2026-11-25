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
                if (workTicks % 20 == 0) playSound(SoundEvents.GENERIC_EAT, 0.8F, 1.0F);
                if (workTicks >= 70) {
                    if (server.removeBlock(target, false)) {
                        getPersistentData().putInt(FED_COUNT, getPersistentData().getInt(FED_COUNT) + 1);
                        server.playSound(null, target, SoundEvents.GENERIC_EAT, SoundSource.HOSTILE, 1.0F, 1.0F);
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
