package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import com.carnis.mod.entity.ai.HiveDefendHeartGoal;
import com.carnis.mod.entity.ai.HiveEscortLeaderGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedZombieEntity extends HiveEntity implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final long BIOMASS_VALUE = 3L;
    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedZombieEntity.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_zombie.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_zombie.walk");
    private static final RawAnimation ASSIMILATE = RawAnimation.begin().thenLoop("animation.infected_zombie.assimilate");
    private static final RawAnimation PULSE = RawAnimation.begin().thenLoop("animation.infected_zombie.pulsing");
    private static final RawAnimation ATTACK = RawAnimation.begin().thenPlay("animation.infected_zombie.attack");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedZombieEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
    }

    @Override
    public boolean isAssimilating() {
        return entityData.get(ASSIMILATING);
    }

    @Override
    public void setAssimilating(boolean assimilating) {
        entityData.set(ASSIMILATING, assimilating);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 3, state -> {
            if (isAssimilating()) return state.setAndContinue(ASSIMILATE);
            return state.setAndContinue(state.isMoving() ? WALK : IDLE);
        }));
        controllers.add(new AnimationController<>(this, "pulsing", 0, state -> {
            if (isAssimilating()) return PlayState.STOP;
            return state.setAndContinue(PULSE);
        }));
        controllers.add(new AnimationController<>(this, "action", 1, state -> {
            if (!isAssimilating() && swinging) return state.setAndContinue(ATTACK);
            state.getController().forceAnimationReset();
            return PlayState.STOP;
        }));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new HiveDefendHeartGoal(this));
        goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.0D, false));
        goalSelector.addGoal(2, new CarnisFeedingGoal(this));
        goalSelector.addGoal(3, new CarnisGestationGoal(this));
        goalSelector.addGoal(4, new RandomStrollGoal(this, 0.8D));
        goalSelector.addGoal(5, new HiveEscortLeaderGoal(this));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0F));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                target -> HiveSwarmCoordinator.validTarget(this, target)));
        targetSelector.addGoal(2, new HurtByTargetGoal(this));
        targetSelector.addGoal(3, new CarnisHuntPreyGoal(this));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 35.0D)
                .add(Attributes.ATTACK_DAMAGE, 4.5D)
                .add(Attributes.MOVEMENT_SPEED, 0.25D)
                .add(Attributes.FOLLOW_RANGE, 16.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.3D)
                .add(Attributes.ARMOR, 2.0D);
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_SPAWN_IDLE.get();
    }

    @Override
    public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
        if (!(target instanceof LivingEntity livingTarget)
                || !HiveSwarmCoordinator.validTarget(this, livingTarget)) return false;
        boolean success = super.doHurtTarget(target);
        if (success && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_ATTACK.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
        return success;
    }

    @Override
    public void setTarget(LivingEntity target) {
        if (target != null && !HiveSwarmCoordinator.validTarget(this, target)) return;
        boolean wasUntargeted = getTarget() == null;
        super.setTarget(target);
        if (wasUntargeted && target != null && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_ALERT.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
    }
}
