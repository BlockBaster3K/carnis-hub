package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.HiveDefendHeartGoal;
import com.carnis.mod.entity.ai.HiveEscortLeaderGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedSkeletonEntity extends HiveEntity implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final long BIOMASS_VALUE = 5L;
    private static final int WHIP_ANIMATION_TICKS = 9;
    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedSkeletonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> WHIP_ANIM_TICKS =
            SynchedEntityData.defineId(InfectedSkeletonEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> BONE_RATTLE_ACTIVE =
            SynchedEntityData.defineId(InfectedSkeletonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_skeleton.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_skeleton.walk");
    private static final RawAnimation ASSIMILATE = RawAnimation.begin().thenLoop("animation.infected_skeleton.assimilate");
    private static final RawAnimation BONE_RATTLE = RawAnimation.begin().thenLoop("animation.infected_skeleton.bone_rattle");
    private static final RawAnimation BLADE_ATTACK = RawAnimation.begin().thenPlay("animation.infected_skeleton.attack_scythe");
    private static final RawAnimation WHIP_ATTACK = RawAnimation.begin().thenPlay("animation.infected_skeleton.attack_whip");
    private static final RawAnimation HURT = RawAnimation.begin().thenPlay("animation.infected_skeleton.hurt");
    private static final RawAnimation DEATH = RawAnimation.begin().thenPlay("animation.infected_skeleton.death");
    private static final int BONE_RATTLE_DURATION_TICKS = 40;
    private int idleTicks;
    private int boneRattleTicks;
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedSkeletonEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
        entityData.define(WHIP_ANIM_TICKS, 0);
        entityData.define(BONE_RATTLE_ACTIVE, false);
    }

    @Override
    public boolean isAssimilating() {
        return entityData.get(ASSIMILATING);
    }

    @Override
    public void setAssimilating(boolean assimilating) {
        boolean changed = entityData.get(ASSIMILATING) != assimilating;
        entityData.set(ASSIMILATING, assimilating);
        if (changed && assimilating && !level().isClientSide) {
            triggerAnim("movement", "assimilate");
        }
    }

    public boolean isWhipping() {
        return entityData.get(WHIP_ANIM_TICKS) > 0;
    }

    public void beginWhipAnimation() {
        entityData.set(WHIP_ANIM_TICKS, WHIP_ANIMATION_TICKS);
    }

    private void cancelWhipAnimation() {
        entityData.set(WHIP_ANIM_TICKS, 0);
    }

    private boolean isBoneRattleActive() {
        return entityData.get(BONE_RATTLE_ACTIVE);
    }

    private void tickIdleBoneRattle() {
        boolean idle = getTarget() == null && !isAssimilating() && !swinging && !isWhipping()
                && getDeltaMovement().horizontalDistanceSqr() < 0.0025D;
        if (!idle) {
            idleTicks = 0;
            boneRattleTicks = 0;
            entityData.set(BONE_RATTLE_ACTIVE, false);
            return;
        }

        if (boneRattleTicks > 0) {
            boneRattleTicks--;
            if (boneRattleTicks == 0) entityData.set(BONE_RATTLE_ACTIVE, false);
            return;
        }

        idleTicks++;
        if (idleTicks > 200 && tickCount % 20 == 0 && random.nextFloat() < 0.05F) {
            boneRattleTicks = BONE_RATTLE_DURATION_TICKS;
            idleTicks = 0;
            entityData.set(BONE_RATTLE_ACTIVE, true);
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_SKELETON_BONECRACK.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
    }

    @Override
    public void tick() {
        if (!level().isClientSide) {
            int whipAnimTicks = entityData.get(WHIP_ANIM_TICKS);
            if (whipAnimTicks > 0) entityData.set(WHIP_ANIM_TICKS, whipAnimTicks - 1);
            tickIdleBoneRattle();
        }
        super.tick();
    }

    @Override
    public boolean hurt(net.minecraft.world.damagesource.DamageSource source, float amount) {
        boolean damaged = super.hurt(source, amount);
        if (damaged && isAlive() && !level().isClientSide) triggerAnim("action", "hurt");
        return damaged;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HIVE_SPAWN_HURT.get();
    }

    @Override
    public void die(net.minecraft.world.damagesource.DamageSource source) {
        if (!level().isClientSide) {
            cancelWhipAnimation();
            entityData.set(BONE_RATTLE_ACTIVE, false);
            triggerAnim("action", "death");
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_DEATH.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
        super.die(source);
    }

    @Override
    protected SoundEvent getDeathSound() {
        // die() emits the explicit death sound once, alongside the GeckoLib death animation.
        return null;
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 25.0D)
                .add(Attributes.ATTACK_DAMAGE, 3.5D)
                .add(Attributes.MOVEMENT_SPEED, 0.27D)
                .add(Attributes.FOLLOW_RANGE, 20.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.2D)
                .add(Attributes.ARMOR, 1.0D);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 2, state -> {
            if (isAssimilating()) return state.setAndContinue(ASSIMILATE);
            return state.setAndContinue(isBoneRattleActive() ? BONE_RATTLE : state.isMoving() ? WALK : IDLE);
        }).triggerableAnim("assimilate", ASSIMILATE));
        controllers.add(new AnimationController<>(this, "action", 0, state -> {
            if (isWhipping()) return state.setAndContinue(WHIP_ATTACK);
            if (!isAssimilating() && swinging) return state.setAndContinue(BLADE_ATTACK);
            state.getController().forceAnimationReset();
            return PlayState.STOP;
        }).triggerableAnim("hurt", HURT).triggerableAnim("death", DEATH));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new InfectedSkeletonAttackGoal(this, 1.15D));
        goalSelector.addGoal(2, new MoveTowardsRestrictionGoal(this, 0.9D));
        goalSelector.addGoal(3, new WaterAvoidingRandomStrollGoal(this, 0.9D));
        goalSelector.addGoal(4, new LookAtPlayerGoal(this, Player.class, 10.0F));
        goalSelector.addGoal(5, new RandomLookAroundGoal(this));
        goalSelector.addGoal(6, new HiveDefendHeartGoal(this));
        goalSelector.addGoal(7, new HiveEscortLeaderGoal(this));
        goalSelector.addGoal(8, new CarnisFeedingGoal(this));
        goalSelector.addGoal(9, new CarnisGestationGoal(this));

        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                target -> HiveSwarmCoordinator.validTarget(this, target)));
        targetSelector.addGoal(2, new HurtByTargetGoal(this));
    }

    /** Immediate-hit checks are separate from target eligibility so out-of-range targets can be pursued. */
    private boolean canAttackNow(LivingEntity target) {
        if (!HiveSwarmCoordinator.validTarget(this, target)) return false;
        Vec3 offset = target.position().subtract(position());
        Vec3 horizontal = new Vec3(offset.x, 0.0D, offset.z);
        if (offset.lengthSqr() > 9.0D || !hasLineOfSight(target)) return false;
        if (horizontal.lengthSqr() < 1.0E-8D) return true;

        Vec3 look = getLookAngle();
        Vec3 forward = new Vec3(look.x, 0.0D, look.z);
        if (forward.lengthSqr() < 1.0E-8D) {
            double yaw = Math.toRadians(getYRot());
            forward = new Vec3(-Math.sin(yaw), 0.0D, Math.cos(yaw));
        } else {
            forward = forward.normalize();
        }
        return forward.dot(horizontal.normalize()) >= -0.15D;
    }

    @Override
    public void setTarget(LivingEntity target) {
        if (target != null && !HiveSwarmCoordinator.validTarget(this, target)) return;
        super.setTarget(target);
    }

    @Override
    public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
        if (!(target instanceof LivingEntity livingTarget) || !canAttackNow(livingTarget)) return false;
        boolean hit = super.doHurtTarget(target);
        if (hit && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_SKELETON_BLADE.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
        return hit;
    }

    /** Resolve the wide 3-block lash; damage is lower than the close-range blade strike. */
    public void performWhipAttack() {
        if (!(level() instanceof ServerLevel server)) return;
        Vec3 look = getLookAngle();
        Vec3 forward = new Vec3(look.x, 0.0D, look.z);
        if (forward.lengthSqr() < 1.0E-8D) {
            double yaw = Math.toRadians(getYRot());
            forward = new Vec3(-Math.sin(yaw), 0.0D, Math.cos(yaw));
        } else {
            forward = forward.normalize();
        }

        AABB reach = getBoundingBox().inflate(3.0D, 1.0D, 3.0D);
        for (LivingEntity target : server.getEntitiesOfClass(LivingEntity.class, reach,
                candidate -> candidate != this && HiveSwarmCoordinator.validTarget(this, candidate))) {
            Vec3 offset = target.position().subtract(position());
            Vec3 horizontal = new Vec3(offset.x, 0.0D, offset.z);
            if (offset.lengthSqr() > 9.0D || horizontal.lengthSqr() < 1.0E-8D
                    || forward.dot(horizontal.normalize()) < -0.15D || !hasLineOfSight(target)) continue;
            if (target.hurt(server.damageSources().mobAttack(this), 2.5F)) {
                target.knockback(0.3D, getX() - target.getX(), getZ() - target.getZ());
            }
        }
        server.sendParticles(ParticleTypes.SWEEP_ATTACK, getX() + forward.x, getY(0.5D),
                getZ() + forward.z, 1, 0.0D, 0.0D, 0.0D, 0.0D);
        server.playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_SKELETON_WHIP.get(),
                SoundSource.HOSTILE, 1.0F, 1.0F);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_SPAWN_SKELETON_BONECRACK.get();
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        level().playSound(null, pos, ModSounds.FLESH_BLOCK_STEP.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
    }

    /** One melee goal handles both close blade strikes and the mid-range whip. */
    private static final class InfectedSkeletonAttackGoal extends MeleeAttackGoal {
        private static final int WHIP_IMPACT_TICK = 4;
        private static final int WHIP_COOLDOWN_TICKS = 30;
        private final InfectedSkeletonEntity skeleton;
        private LivingEntity whipTarget;
        private int whipWindup;
        private int nextWhipTick;

        private InfectedSkeletonAttackGoal(InfectedSkeletonEntity skeleton, double speed) {
            super(skeleton, speed, false);
            this.skeleton = skeleton;
        }

        @Override
        public void stop() {
            super.stop();
            whipTarget = null;
            whipWindup = 0;
            skeleton.cancelWhipAnimation();
        }

        @Override
        protected void checkAndPerformAttack(LivingEntity target, double distanceToTargetSqr) {
            // A direct target assigned by HurtByTargetGoal may bypass target-selection predicates.
            // Do not clear it: movement/navigation may still bring a valid target into range.
            if (!skeleton.canAttackNow(target)) return;
            boolean inWhipBand = distanceToTargetSqr >= 2.25D && distanceToTargetSqr <= 9.0D;
            if (whipTarget != null) {
                if (target != whipTarget || !inWhipBand || !skeleton.canAttackNow(target)) {
                    whipTarget = null;
                    whipWindup = 0;
                } else if (--whipWindup <= 0) {
                    skeleton.performWhipAttack();
                    nextWhipTick = skeleton.tickCount + WHIP_COOLDOWN_TICKS;
                    whipTarget = null;
                }
                return;
            }
            if (inWhipBand) {
                if (skeleton.tickCount >= nextWhipTick && skeleton.canAttackNow(target)) {
                    whipTarget = target;
                    whipWindup = WHIP_IMPACT_TICK;
                    skeleton.beginWhipAnimation();
                }
                return;
            }
            if (distanceToTargetSqr < 2.25D) super.checkAndPerformAttack(target, distanceToTargetSqr);
        }
    }
}
