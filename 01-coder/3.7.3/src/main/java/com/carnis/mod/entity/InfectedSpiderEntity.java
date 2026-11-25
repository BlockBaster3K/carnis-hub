package com.carnis.mod.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Spider;
import net.minecraft.world.level.Level;

public final class InfectedSpiderEntity extends Spider implements HivemindLinkedMob, AssimilatingMob, software.bernie.geckolib.animatable.GeoEntity {
    private static final net.minecraft.network.syncher.EntityDataAccessor<Boolean> ASSIMILATING =
            net.minecraft.network.syncher.SynchedEntityData.defineId(InfectedSpiderEntity.class,
                    net.minecraft.network.syncher.EntityDataSerializers.BOOLEAN);

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
    }

    @Override
    public long getBiomassValue() { return 5L; }

    @Override
    public boolean isAssimilating() { return entityData.get(ASSIMILATING); }

    @Override
    public void setAssimilating(boolean assimilating) { entityData.set(ASSIMILATING, assimilating); }

    private final software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache geoCache =
            software.bernie.geckolib.util.GeckoLibUtil.createInstanceCache(this);

    @Override
    public void registerControllers(software.bernie.geckolib.core.animation.AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this, "movement", 3,
                state -> state.setAndContinue(software.bernie.geckolib.core.animation.RawAnimation.begin()
                        .thenLoop("animation.infected_spider." + (isAssimilating() ? "assimilate" : state.isMoving() ? "walk" : "idle")))));
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this, "action", 1, state -> {
            if (!isAssimilating() && swinging) return state.setAndContinue(software.bernie.geckolib.core.animation.RawAnimation.begin()
                    .thenPlay("animation.infected_spider.attack"));
            state.getController().forceAnimationReset();
            return software.bernie.geckolib.core.object.PlayState.STOP;
        }));
    }

    @Override
    public software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    public InfectedSpiderEntity(EntityType<? extends Spider> type, Level level) {
        super(type, level);
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        moveRandomLookGoalToPriority(7);
        goalSelector.addGoal(8, new com.carnis.mod.entity.ai.CarnisFeedingGoal(this));
        goalSelector.addGoal(9, new com.carnis.mod.entity.ai.CarnisGestationGoal(this));
        goalSelector.addGoal(10, new com.carnis.mod.entity.ai.InfectedSpiderRangedSpatGoal(this));
        targetSelector.addGoal(4, new com.carnis.mod.entity.ai.CarnisHuntPreyGoal(this));
    }

    private void moveRandomLookGoalToPriority(int priority) {
        for (var wrappedGoal : goalSelector.getAvailableGoals()) {
            if (wrappedGoal.getGoal() instanceof net.minecraft.world.entity.ai.goal.RandomLookAroundGoal) {
                goalSelector.removeGoal(wrappedGoal.getGoal());
                goalSelector.addGoal(priority, new net.minecraft.world.entity.ai.goal.RandomLookAroundGoal(this));
                return;
            }
        }
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Spider.createAttributes().add(Attributes.MAX_HEALTH, 20.0D)
                .add(Attributes.ATTACK_DAMAGE, 3.0D);
    }
}
