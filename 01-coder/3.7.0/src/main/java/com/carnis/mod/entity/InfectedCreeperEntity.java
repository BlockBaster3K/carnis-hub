package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.init.ModSounds;
import net.minecraft.Util;
import net.minecraft.core.BlockPos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.SwellGoal;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

import java.util.Comparator;
import java.util.EnumSet;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedCreeperEntity extends Creeper
        implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final long BIOMASS_VALUE = 8L;
    private static final int SCALE_DIVISOR = 28;
    private static final int FUSE_LENGTH = 30;
    private static final long CRAWL_SOUND_COOLDOWN_MS = 3_000L;

    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedCreeperEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> SAC_CHARGING =
            SynchedEntityData.defineId(InfectedCreeperEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> CRAWLING =
            SynchedEntityData.defineId(InfectedCreeperEntity.class, EntityDataSerializers.BOOLEAN);

    private static final RawAnimation IDLE = RawAnimation.begin()
            .thenLoop("animation.infected_creeper.idle");
    private static final RawAnimation WALK = RawAnimation.begin()
            .thenLoop("animation.infected_creeper.walk");
    private static final RawAnimation FUSE = RawAnimation.begin()
            .thenLoop("animation.infected_creeper.fuse");
    private static final RawAnimation CRAWL = RawAnimation.begin()
            .thenLoop("animation.infected_creeper.crawl");
    private static final RawAnimation ASSIMILATE = RawAnimation.begin()
            .thenLoop("animation.infected_creeper.assimilate");
    private static final RawAnimation SAC_CHARGE = RawAnimation.begin()
            .thenPlay("animation.infected_creeper.sac_charge");
    private static final RawAnimation DETONATE = RawAnimation.begin()
            .thenPlay("animation.infected_creeper.detonate");
    private static final RawAnimation HURT = RawAnimation.begin()
            .thenPlay("animation.infected_creeper.hurt");
    private static final RawAnimation DEATH = RawAnimation.begin()
            .thenPlay("animation.infected_creeper.death");

    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private boolean detonateWarningPlayed;
    private Pose poseBeforeCrawl = Pose.STANDING;
    private long lastCrawlSoundMs = -CRAWL_SOUND_COOLDOWN_MS;

    public InfectedCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
        entityData.define(SAC_CHARGING, false);
        entityData.define(CRAWLING, false);
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    @Override
    public boolean isAssimilating() {
        return entityData.get(ASSIMILATING);
    }

    @Override
    public void setAssimilating(boolean assimilating) {
        entityData.set(ASSIMILATING, assimilating);
    }

    public boolean isSacCharging() {
        return entityData.get(SAC_CHARGING);
    }

    public boolean isCrawling() {
        return entityData.get(CRAWLING);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(
                new AnimationController<>(this, "movement", 2, state -> {
                    if (isSacCharging()) return state.setAndContinue(FUSE);
                    if (isCrawling()) return state.setAndContinue(CRAWL);
                    if (isAssimilating()) return state.setAndContinue(ASSIMILATE);
                    return state.setAndContinue(state.isMoving() ? WALK : IDLE);
                }),
                new AnimationController<>(this, "action", 0, state -> PlayState.STOP)
                        .triggerableAnim("sac_charge", SAC_CHARGE)
                        .triggerableAnim("detonate", DETONATE)
                        .triggerableAnim("hurt", HURT)
                        .triggerableAnim("death", DEATH)
        );
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        goalSelector.removeAllGoals(goal -> goal instanceof SwellGoal);
        goalSelector.addGoal(2, new PlayerOnlySwellGoal(this));
        moveRandomLookGoalToPriority(7);
        goalSelector.addGoal(8, new CarnisFeedingGoal(this));
        goalSelector.addGoal(9, new CarnisGestationGoal(this));
        targetSelector.removeAllGoals(goal -> goal instanceof net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal<?>);
        targetSelector.addGoal(1, new NearestLivePlayerTargetGoal(this));
        targetSelector.addGoal(3, new CarnisHuntPreyGoal(this));
    }


    private static final class NearestLivePlayerTargetGoal extends Goal {
        private final InfectedCreeperEntity creeper;
        private Player candidate;

        private NearestLivePlayerTargetGoal(InfectedCreeperEntity creeper) {
            this.creeper = creeper;
            setFlags(EnumSet.of(Flag.TARGET));
        }

        @Override
        public boolean canUse() {
            double range = creeper.getAttributeValue(Attributes.FOLLOW_RANGE);
            AABB searchArea = creeper.getBoundingBox().inflate(range);
            candidate = creeper.level().getEntitiesOfClass(Player.class, searchArea,
                            player -> HiveSwarmCoordinator.validTarget(creeper, player))
                    .stream()
                    .filter(player -> creeper.distanceToSqr(player) <= range * range
                            && creeper.hasLineOfSight(player))
                    .min(Comparator.comparingDouble(player -> creeper.distanceToSqr(player)))
                    .orElse(null);
            return candidate != null;
        }

        @Override
        public boolean canContinueToUse() {
            return candidate != null && HiveSwarmCoordinator.validTarget(creeper, candidate)
                    && creeper.distanceToSqr(candidate)
                    <= creeper.getAttributeValue(Attributes.FOLLOW_RANGE)
                    * creeper.getAttributeValue(Attributes.FOLLOW_RANGE);
        }

        @Override
        public void start() {
            if (candidate != null) creeper.setTarget(candidate);
        }

        @Override
        public void stop() {
            if (creeper.getTarget() == candidate) creeper.setTarget(null);
            candidate = null;
        }
    }

    private void moveRandomLookGoalToPriority(int priority) {
        for (var wrappedGoal : goalSelector.getAvailableGoals()) {
            if (wrappedGoal.getGoal() instanceof net.minecraft.world.entity.ai.goal.RandomLookAroundGoal) {
                goalSelector.removeGoal(wrappedGoal.getGoal());
                goalSelector.addGoal(priority,
                        new net.minecraft.world.entity.ai.goal.RandomLookAroundGoal(this));
                return;
            }
        }
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Creeper.createAttributes().add(Attributes.MAX_HEALTH, 24.0D);
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (target instanceof HivemindLinkedMob || com.carnis.mod.event.NeuroArmorEventHandler.isHiveEntity(target)) {
            return false;
        }
        return super.canAttack(target);
    }

    @Override
    public void setTarget(LivingEntity target) {
        if (target != null && !HiveSwarmCoordinator.validTarget(this, target)) return;
        super.setTarget(target);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) return;

        updateCrawlState();
        boolean charging = getSwellDir() > 0 || isIgnited();
        boolean wasCharging = entityData.get(SAC_CHARGING);
        if (charging != wasCharging) {
            entityData.set(SAC_CHARGING, charging);
            if (charging) {
                level().playSound(null, getX(), getY(), getZ(), ModSounds.HIVE_SPAWN_CREEPER_SAC.get(),
                        SoundSource.HOSTILE, 1.0F, 1.0F);
                triggerAnimation("sac_charge");
            } else {
                detonateWarningPlayed = false;
            }
        }

        if (charging && getFuse() == 5 && !detonateWarningPlayed) {
            detonateWarningPlayed = true;
            level().playSound(null, getX(), getY(), getZ(), ModSounds.HIVE_SPAWN_CREEPER_DETONATE.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
            triggerAnimation("detonate");
        }
    }

    private void updateCrawlState() {
        LivingEntity target = getTarget();
        boolean shouldCrawl = target != null && target.isAlive()
                && distanceToSqr(target) <= 100.0D && !hasLineOfSight(target);
        boolean wasCrawling = entityData.get(CRAWLING);
        if (shouldCrawl == wasCrawling) return;

        entityData.set(CRAWLING, shouldCrawl);
        if (shouldCrawl) {
            poseBeforeCrawl = getPose();
            setPose(Pose.SWIMMING);
            playCrawlSound();
        } else if (getPose() == Pose.SWIMMING) {
            setPose(poseBeforeCrawl);
        }
    }

    private int getFuse() {
        int elapsedScaleTicks = Math.round(getSwelling(1.0F) * SCALE_DIVISOR);
        return Math.max(0, FUSE_LENGTH - elapsedScaleTicks);
    }

    private static final class PlayerOnlySwellGoal extends SwellGoal {
        private final InfectedCreeperEntity creeper;

        private PlayerOnlySwellGoal(InfectedCreeperEntity creeper) {
            super(creeper);
            this.creeper = creeper;
        }

        @Override
        public boolean canUse() {
            return super.canUse() && HiveSwarmCoordinator.validTarget(creeper, creeper.getTarget())
                    && creeper.getTarget() instanceof Player;
        }

        @Override
        public boolean canContinueToUse() {
            return super.canContinueToUse() && HiveSwarmCoordinator.validTarget(creeper, creeper.getTarget())
                    && creeper.getTarget() instanceof Player;
        }
    }

    private void triggerAnimation(String animation) {
        if (!level().isClientSide) triggerAnim("action", animation);
    }

    private void playCrawlSound() {
        long now = Util.getMillis();
        long elapsed = now - lastCrawlSoundMs;
        if (elapsed < 0L) return;
        if (elapsed >= 0L && elapsed < CRAWL_SOUND_COOLDOWN_MS) return;
        lastCrawlSoundMs = now;
        level().playSound(null, getX(), getY(), getZ(), ModSounds.HIVE_SPAWN_CREEPER_CRAWL.get(),
                SoundSource.HOSTILE, 1.0F, 1.0F);
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        if (isCrawling()) playCrawlSound();
        else super.playStepSound(pos, state);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_SPAWN_IDLE.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HIVE_SPAWN_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.HIVE_SPAWN_DEATH.get();
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean damaged = super.hurt(source, amount);
        if (damaged && isAlive() && !level().isClientSide) triggerAnimation("hurt");
        return damaged;
    }

    @Override
    public void die(DamageSource source) {
        if (!level().isClientSide) triggerAnimation("death");
        super.die(source);
    }
}
