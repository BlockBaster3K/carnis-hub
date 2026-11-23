# Carnis 3.4.6 — полный текст затронутых файлов

> Сгенерировано из актуальных файлов проекта после реализации требований 3.4.6.
> Новые события используют только OGG, фактически существующие в assets; для отдельных wave events использованы валидные повторно задействованные samples, так как выделенные wave OGG отсутствуют.


## `src/main/java/com/carnis/mod/entity/AssimilatingMob.java`

```java
package com.carnis.mod.entity;

/** Network-synchronised visual state and final biomass value for assimilating mobs. */
public interface AssimilatingMob extends BiomassValued {
    boolean isAssimilating();
    void setAssimilating(boolean assimilating);
}
```


## `src/main/java/com/carnis/mod/entity/BiomassValued.java`

```java
package com.carnis.mod.entity;

/** Exposes an entity's explicit biomass value where the caller needs one. */
public interface BiomassValued {
    long getBiomassValue();
}
```


## `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.ForgeEventFactory;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedCreeperEntity extends Creeper implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final long BIOMASS_VALUE = 8L;
    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedCreeperEntity.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_creeper.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_creeper.walk");
    private static final RawAnimation FUSE = RawAnimation.begin().thenLoop("animation.infected_creeper.fuse");
    private static final RawAnimation ASSIMILATE = RawAnimation.begin().thenLoop("animation.infected_creeper.assimilate");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedCreeperEntity(EntityType<? extends Creeper> type, Level level) { super(type, level); }

    @Override protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
    }
    @Override public long getBiomassValue() { return BIOMASS_VALUE; }
    @Override public boolean isAssimilating() { return entityData.get(ASSIMILATING); }
    @Override public void setAssimilating(boolean value) { entityData.set(ASSIMILATING, value); }

    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 2, state ->
                state.setAndContinue(getSwellDir() > 0 || isIgnited() ? FUSE
                        : isAssimilating() ? ASSIMILATE : state.isMoving() ? WALK : IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return geoCache; }

    @Override protected void registerGoals() {
        super.registerGoals();
        goalSelector.addGoal(7, new CarnisFeedingGoal(this));
        goalSelector.addGoal(8, new CarnisGestationGoal(this));
        targetSelector.addGoal(3, new CarnisHuntPreyGoal(this));
    }
    public static AttributeSupplier.Builder createAttributes() {
        return Creeper.createAttributes().add(Attributes.MAX_HEALTH, 24.0D);
    }

    private boolean ruptured;
    private boolean rupturePending;

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_SPAWN_CREEPER_SAC.get();
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        level().playSound(null, pos, ModSounds.HIVE_SPAWN_CREEPER_CRAWL.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
    }

    /** Marks one fuse warning; the event handler applies damage five ticks later. */
    public boolean beginRuptureCountdown() {
        if (ruptured || rupturePending) return false;
        rupturePending = true;
        return true;
    }

    /** Applies the canceled vanilla explosion after the synchronized five-tick warning lead. */
    public void rupture(ServerLevel level) {
        if (ruptured) return;
        rupturePending = false;
        ruptured = true;
        double radius = 4.5D;
        level.playSound(null, blockPosition(), ModSounds.CREEPER_RUPTURE.get(), SoundSource.HOSTILE, 2F, 1.0F);
        level.sendParticles(ParticleTypes.SNEEZE, getX(), getY() + .7D, getZ(), 100, .7D, .6D, .7D, .16D);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), getX(), getY() + .7D, getZ(), 90, .7D, .6D, .7D, .18D);
        level.sendParticles(ParticleTypes.CRIMSON_SPORE, getX(), getY() + .8D, getZ(), 70, .9D, .6D, .9D, .1D);
        for (LivingEntity target : level.getEntitiesOfClass(LivingEntity.class,
                getBoundingBox().inflate(radius), e -> e != this && e.isAlive() && !e.isSpectator()
                        && e.distanceToSqr(this) <= radius * radius)) {
            target.hurt(level.damageSources().mobAttack(this), 12F);
            if (target.isAlive()) target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 2));
        }
        HiveSporeCloudEntity cloud = com.carnis.mod.init.ModEntities.HIVE_SPORE_CLOUD.get().create(level);
        if (cloud != null) {
            cloud.setPos(getX(), getY(), getZ());
            cloud.setOwner(this);
            cloud.setRadius(3.0F);
            cloud.setWaitTime(0);
            cloud.setDuration(160);
            cloud.setRadiusPerTick(0F);
            cloud.setRadiusOnUse(0F);
            cloud.setDurationOnUse(0);
            cloud.setParticle(ParticleTypes.SNEEZE);
            cloud.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
            cloud.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 100, 0));
            level.addFreshEntity(cloud);
        }
        if (!ForgeEventFactory.getMobGriefingEvent(level, this)) return;
        BlockPos center = blockPosition();
        for (BlockPos mutable : BlockPos.betweenClosed(center.offset(-3, -3, -3), center.offset(3, 3, 3))) {
            BlockPos pos = mutable.immutable();
            if (!level.hasChunkAt(pos) || level.isOutsideBuildHeight(pos)
                    || pos.distToCenterSqr(getX(), getY(), getZ()) > 9D) continue;
            BlockState existing = level.getBlockState(pos);
            boolean vein = existing.is(ModBlocks.FLESH_VEINS.get());
            if ((!vein && !existing.isAir()) || !existing.getFluidState().isEmpty()) continue;
            BlockState result = vein ? existing : Blocks.AIR.defaultBlockState();
            for (Direction face : Direction.values()) {
                BlockPos support = pos.relative(face);
                if (!level.hasChunkAt(support) || level.isOutsideBuildHeight(support)
                        || !level.getBlockState(support).isFaceSturdy(level, support, face.getOpposite())) continue;
                BlockState next = ModBlocks.FLESH_VEINS.get().getStateForPlacement(result, level, pos, face);
                if (next != null) result = next;
            }
            if (!result.equals(existing)) level.setBlockAndUpdate(pos, result);
        }
        if (level.random.nextFloat() >= .4F) return;
        for (BlockPos pos : new BlockPos[]{center, center.above(), center.below(), center.north(), center.south(), center.east(), center.west()}) {
            if (!level.hasChunkAt(pos) || !level.hasChunkAt(pos.below()) || level.isOutsideBuildHeight(pos)) continue;
            BlockState existing = level.getBlockState(pos);
            if (!existing.isAir() && !existing.is(ModBlocks.FLESH_VEINS.get())) continue;
            if (!existing.getFluidState().isEmpty()) continue;
            BlockState growth = (level.random.nextBoolean() ? ModBlocks.PUSTULE_CLUSTER.get() : ModBlocks.BIOMASS_REMAINS.get()).defaultBlockState();
            if (growth.canSurvive(level, pos) && level.setBlockAndUpdate(pos, growth)) break;
        }
    }
}
```


## `src/main/java/com/carnis/mod/entity/InfectedSpiderEntity.java`

```java
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
        goalSelector.addGoal(7, new com.carnis.mod.entity.ai.CarnisFeedingGoal(this));
        goalSelector.addGoal(8, new com.carnis.mod.entity.ai.CarnisGestationGoal(this));
        targetSelector.addGoal(3, new com.carnis.mod.entity.ai.CarnisHuntPreyGoal(this));
        goalSelector.addGoal(9, new com.carnis.mod.entity.ai.InfectedSpiderRangedSpatGoal(this));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Spider.createAttributes().add(Attributes.MAX_HEALTH, 20.0D)
                .add(Attributes.ATTACK_DAMAGE, 3.0D);
    }
}
```


## `src/main/java/com/carnis/mod/entity/InfectedZombieEntity.java`

```java
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
        boolean success = super.doHurtTarget(target);
        if (success && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_ATTACK.get(),
                    SoundSource.HOSTILE, 0.9F, 0.9F + random.nextFloat() * 0.2F);
        }
        return success;
    }

    @Override
    public void setTarget(LivingEntity target) {
        if (target != null && (target instanceof HiveEntity || target instanceof HivemindLinkedMob)) return;
        boolean wasUntargeted = getTarget() == null;
        super.setTarget(target);
        if (wasUntargeted && target != null && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_ALERT.get(),
                    SoundSource.HOSTILE, 0.9F, 0.95F + random.nextFloat() * 0.1F);
        }
    }
}
```


## `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java`

```java
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
        entityData.set(ASSIMILATING, assimilating);
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
                    SoundSource.HOSTILE, 0.65F, 1.0F);
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
            return state.setAndContinue(isBoneRattleActive() ? BONE_RATTLE : state.isMoving() ? WALK : IDLE);
        }));
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

    @Override
    public boolean canAttack(LivingEntity target) {
        // This argument may be a candidate target not yet installed as getTarget().
        // Keep the eligibility check independent of range so target acquisition can start pursuit.
        return target != null && !target.isDeadOrDying()
                && !(target instanceof HiveEntity || target instanceof HivemindLinkedMob)
                && super.canAttack(target);
    }

    /** Immediate-hit checks are separate from target eligibility so out-of-range targets can be pursued. */
    private boolean canAttackNow(LivingEntity target) {
        if (!canAttack(target)) return false;
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
        if (target != null && (target instanceof HiveEntity || target instanceof HivemindLinkedMob)) return;
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
        level().playSound(null, pos, ModSounds.FLESH_BLOCK_STEP.get(), SoundSource.HOSTILE, 0.15F, 1.0F);
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
```


## `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.ai.FleshAmalgamChargeGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.event.AcidAttackSlowdown;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.CarnisWorldData;
import com.carnis.mod.world.CarnisWorldData.AdaptationType;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class FleshAmalgamEntity extends HiveEntity
        implements GeoEntity, HivemindLinkedMob {
    private static final byte ROAR_ANIMATION_EVENT = 60;
    private static final byte SLAM_ANIMATION_EVENT = 61;

    @Override
    protected void playStepSound(net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState state) {
        level().playSound(null, getX(), getY(), getZ(), ModSounds.AMALGAM_STEP.get(),
                SoundSource.HOSTILE, 0.9F, 1.0F);
        if (tickCount % 4 == 0) {
            level().playSound(null, getX(), getY(), getZ(), ModSounds.HIVE_AMALGAM_SHUFFLE.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
    }

    /** Sends a compact vanilla entity event so GeckoLib is triggered on the rendering client. */
    public void triggerRoarAnimation() {
        if (level().isClientSide) triggerAnim("roar_controller", "roar");
        else level().broadcastEntityEvent(this, ROAR_ANIMATION_EVENT);
    }

    public void triggerSlamAnimation() {
        if (level().isClientSide) triggerAnim("slam_controller", "slam");
        else level().broadcastEntityEvent(this, SLAM_ANIMATION_EVENT);
    }

    @Override
    public void handleEntityEvent(byte id) {
        if (level().isClientSide && id == ROAR_ANIMATION_EVENT) {
            triggerAnim("roar_controller", "roar");
        } else if (level().isClientSide && id == SLAM_ANIMATION_EVENT) {
            triggerAnim("slam_controller", "slam");
        } else {
            super.handleEntityEvent(id);
        }
    }

    private static final long BIOMASS_VALUE = 25L;

    public static final double MAX_HEALTH = 240.0D;
    public static final double KNOCKBACK_RESISTANCE = 1.0D;
    public static final double ATTACK_DAMAGE = 14.0D;
    public static final double MOVEMENT_SPEED = 0.22D;
    public static final double FOLLOW_RANGE = 32.0D;
    public static final double ARMOR = 12.0D;
    public static final double ARMOR_TOUGHNESS = 4.0D;

    public static final double CHARGE_TRIGGER_DISTANCE = 12.0D;

    private static final String REFLECTED_PROJECTILE_TAG =
            CarnisMod.MOD_ID + ":amalgam_reflected";

    private static final double PROJECTILE_REFLECTION_BASE_CHANCE = 0.06D;
    private static final double PROJECTILE_REFLECTION_CHANCE_PER_LEVEL = 0.0075D;
    private static final double PROJECTILE_REFLECTION_MAX_CHANCE = 0.45D;

    private static final double ACID_BASE_CHANCE = 0.08D;
    private static final double ACID_CHANCE_PER_LEVEL = 0.007D;
    private static final double ACID_MAX_CHANCE = 0.50D;
    private static final int ACID_BASE_ARMOR_DAMAGE = 2;
    private static final int ACID_MAX_ARMOR_DAMAGE = 6;
    private static final long ACID_LEVELS_PER_ARMOR_DAMAGE = 15L;
    private static final int ACID_BASE_DURATION_TICKS = 40;
    private static final int ACID_MAX_DURATION_TICKS = 100;
    private static final long ACID_EMPOWERED_SLOW_LEVEL = 50L;

    private static final double THORN_BASE_CHANCE = 0.08D;
    private static final double THORN_CHANCE_PER_LEVEL = 0.008D;
    private static final double THORN_MAX_CHANCE = 0.55D;
    private static final float THORN_BASE_DAMAGE = 1.5F;
    private static final float THORN_DAMAGE_PER_LEVEL = 0.05F;
    private static final float THORN_MAX_DAMAGE = 5.0F;

    private static final RawAnimation IDLE_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.flesh_amalgam.idle");
    private static final RawAnimation WALK_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.flesh_amalgam.walk");
    private static final RawAnimation ATTACK_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.attack");
    private static final RawAnimation SLAM_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.slam");
    private static final RawAnimation ROAR_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.roar");

    private final net.minecraft.server.level.ServerBossEvent bossBar = new net.minecraft.server.level.ServerBossEvent(
            getDisplayName(), net.minecraft.world.BossEvent.BossBarColor.RED,
            net.minecraft.world.BossEvent.BossBarOverlay.NOTCHED_10);
    private final com.carnis.mod.entity.ai.AmalgamBiomassFeast biomassFeast =
            new com.carnis.mod.entity.ai.AmalgamBiomassFeast(this);
    private long slamReady;
    private long pullReady;
    private long bileReady;
    private long feastReady;

    private final AnimatableInstanceCache animationCache =
            GeckoLibUtil.createInstanceCache(this);

    public FleshAmalgamEntity(
            EntityType<? extends FleshAmalgamEntity> entityType,
            Level level
    ) {
        super(entityType, level);
        this.xpReward = 18;
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, MAX_HEALTH)
                .add(Attributes.KNOCKBACK_RESISTANCE, KNOCKBACK_RESISTANCE)
                .add(Attributes.ATTACK_DAMAGE, ATTACK_DAMAGE)
                .add(Attributes.MOVEMENT_SPEED, MOVEMENT_SPEED)
                .add(Attributes.FOLLOW_RANGE, FOLLOW_RANGE)
                .add(Attributes.ARMOR, ARMOR)
                .add(Attributes.ARMOR_TOUGHNESS, ARMOR_TOUGHNESS);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new com.carnis.mod.entity.ai.FleshAmalgamAbilityGoal(this));
        goalSelector.addGoal(2, new FleshAmalgamChargeGoal(this));
        goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.0D, false));
        goalSelector.addGoal(
                5,
                new WaterAvoidingRandomStrollGoal(this, 0.8D)
        );
        goalSelector.addGoal(
                6,
                new LookAtPlayerGoal(this, Player.class, 10.0F)
        );
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));

        targetSelector.addGoal(
                1,
                new NearestAttackableTargetGoal<>(
                        this,
                        Player.class,
                        true,
                        target -> target instanceof Player player
                                && PlayerInfectionApi.isHostileTarget(player)
                                && HiveSwarmCoordinator.validTarget(this, target)
                )
        );
        targetSelector.addGoal(
                2,
                new HurtByTargetGoal(this).setAlertOthers()
        );
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (target instanceof Player player && PlayerInfectionApi.isAssimilated(player)) return false;
        return super.canAttack(target);
    }

    @Override
    public void setTarget(LivingEntity target) {
        if (target != null && !HiveSwarmCoordinator.validTarget(this, target)) return;
        super.setTarget(target);
    }

    public boolean canUseAbility(int ability) {
        long now = level().getGameTime();
        return switch (ability) {
            case 1 -> now >= slamReady;
            case 2 -> now >= pullReady;
            case 3 -> now >= bileReady;
            default -> false;
        };
    }

    public void consumeAbilityCooldown(int ability) {
        long now = level().getGameTime();
        switch (ability) {
            case 1 -> slamReady = now + 160L;
            case 2 -> pullReady = now + 240L;
            case 3 -> bileReady = now + 200L;
            default -> throw new IllegalArgumentException("Unknown ability: " + ability);
        }
    }

    public long getFeastReady() { return feastReady; }
    public void setFeastReady(long tick) { feastReady = tick; }

    @Override
    public void tick() {
        super.tick();
        if (!(level() instanceof ServerLevel server)) return;
        if (!isAlive()) { bossBar.removeAllPlayers(); return; }
        bossBar.setProgress(net.minecraft.util.Mth.clamp(getHealth() / getMaxHealth(), 0.0F, 1.0F));
        bossBar.setName(getDisplayName());
        if (tickCount % 10 == 0) {
            for (ServerPlayer player : new java.util.ArrayList<>(bossBar.getPlayers())) {
                if (player.serverLevel() != server || !server.players().contains(player)
                        || !player.isAlive() || player.distanceToSqr(this) > 32.0D * 32.0D) bossBar.removePlayer(player);
            }
            for (ServerPlayer player : server.players()) {
                if (player.isAlive() && player.distanceToSqr(this) <= 32.0D * 32.0D) bossBar.addPlayer(player);
                else bossBar.removePlayer(player);
            }
        }
        if (!isNoAi()) biomassFeast.tick(server);
    }

    @Override
    public void remove(Entity.RemovalReason reason) {
        bossBar.removeAllPlayers();
        super.remove(reason);
    }

    @Override
    public void addAdditionalSaveData(net.minecraft.nbt.CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putLong("CarnisSlamReady", slamReady);
        tag.putLong("CarnisPullReady", pullReady);
        tag.putLong("CarnisBileReady", bileReady);
        tag.putLong("CarnisFeastReady", feastReady);
    }

    @Override
    public void readAdditionalSaveData(net.minecraft.nbt.CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        slamReady = tag.getLong("CarnisSlamReady");
        pullReady = tag.getLong("CarnisPullReady");
        bileReady = tag.getLong("CarnisBileReady");
        feastReady = tag.getLong("CarnisFeastReady");
    }

    @Override
    protected void customServerAiStep() {
        LivingEntity target = getTarget();

        if (
                target instanceof Player player
                        && PlayerInfectionApi.isAssimilated(player)
        ) {
            setTarget(null);
        }

        super.customServerAiStep();
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (!(level() instanceof ServerLevel serverLevel)) {
            return super.hurt(source, amount);
        }

        LivingEntity meleeAttacker = getDirectMeleeAttacker(source);
        boolean hurt = super.hurt(source, amount);

        if (hurt && meleeAttacker != null) {
            trySpikedRetaliation(serverLevel, meleeAttacker);
        }

        return hurt;
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);

        if (
                hit
                        && target instanceof ServerPlayer player
                        && level() instanceof ServerLevel serverLevel
        ) {
            tryAcidSplash(serverLevel, player);
        }

        return hit;
    }

    /**
     * Called from the Forge projectile-impact hook before vanilla processes
     * the collision. Returning true means the event must skip that impact.
     */
    public boolean tryDeflectProjectile(Projectile projectile) {
        if (
                !(level() instanceof ServerLevel serverLevel)
                        || projectile.isRemoved()
                        || !(projectile instanceof AbstractArrow)
                        || projectile.getOwner() == this
                        || projectile.getPersistentData().getBoolean(
                                REFLECTED_PROJECTILE_TAG
                        )
        ) {
            return false;
        }

        long rangedLevel = getAdaptationLevel(AdaptationType.RANGED);
        double reflectionChance = scaledChance(
                rangedLevel,
                PROJECTILE_REFLECTION_BASE_CHANCE,
                PROJECTILE_REFLECTION_CHANCE_PER_LEVEL,
                PROJECTILE_REFLECTION_MAX_CHANCE
        );

        if (
                reflectionChance <= 0.0D
                        || getRandom().nextDouble() >= reflectionChance
        ) {
            return false;
        }

        Vec3 incomingMovement = projectile.getDeltaMovement();
        Vec3 reflected = incomingMovement.scale(-0.4D).add(
                (getRandom().nextDouble() - 0.5D) * 0.2D,
                0.1D,
                (getRandom().nextDouble() - 0.5D) * 0.2D
        );
        projectile.getPersistentData().putBoolean(REFLECTED_PROJECTILE_TAG, true);
        projectile.setDeltaMovement(reflected);
        serverLevel.getChunkSource().broadcast(
                projectile, new ClientboundSetEntityMotionPacket(projectile)
        );
        Vec3 impactPosition = projectile.position();
        serverLevel.playSound(null, impactPosition.x, impactPosition.y, impactPosition.z,
                SoundEvents.SHIELD_BLOCK, SoundSource.HOSTILE, 1.0F, 1.0F);
        playBoneDeflectEffects(serverLevel, impactPosition);
        return true;
    }

    public long getRangedAdaptationLevel() {
        return getAdaptationLevel(AdaptationType.RANGED);
    }

    private void tryAcidSplash(
            ServerLevel serverLevel,
            ServerPlayer player
    ) {
        long meleeLevel = getAdaptationLevel(AdaptationType.MELEE);
        double acidChance = scaledChance(
                meleeLevel,
                ACID_BASE_CHANCE,
                ACID_CHANCE_PER_LEVEL,
                ACID_MAX_CHANCE
        );

        if (
                acidChance <= 0.0D
                        || getRandom().nextDouble() >= acidChance
        ) {
            return;
        }

        int armorDamageBonus = (int) Math.min(
                ACID_MAX_ARMOR_DAMAGE - ACID_BASE_ARMOR_DAMAGE,
                meleeLevel / ACID_LEVELS_PER_ARMOR_DAMAGE
        );
        int armorDamage = ACID_BASE_ARMOR_DAMAGE + armorDamageBonus;

        for (EquipmentSlot slot : EquipmentSlot.values()) {
            if (!slot.isArmor()) {
                continue;
            }

            ItemStack armorStack = player.getItemBySlot(slot);

            if (!armorStack.isEmpty() && armorStack.isDamageableItem()) {
                armorStack.hurtAndBreak(
                        armorDamage,
                        player,
                        wearer -> wearer.broadcastBreakEvent(slot)
                );
            }
        }

        int duration = ACID_BASE_DURATION_TICKS + (int) Math.min(
                ACID_MAX_DURATION_TICKS - ACID_BASE_DURATION_TICKS,
                meleeLevel
        );
        AcidAttackSlowdown.apply(
                player,
                duration,
                meleeLevel >= ACID_EMPOWERED_SLOW_LEVEL
        );

        playAcidSplashEffects(serverLevel, player);
    }

    private void trySpikedRetaliation(
            ServerLevel serverLevel,
            LivingEntity attacker
    ) {
        if (!attacker.isAlive() || attacker == this) {
            return;
        }

        long meleeLevel = getAdaptationLevel(AdaptationType.MELEE);
        double thornChance = scaledChance(
                meleeLevel,
                THORN_BASE_CHANCE,
                THORN_CHANCE_PER_LEVEL,
                THORN_MAX_CHANCE
        );

        if (
                thornChance <= 0.0D
                        || getRandom().nextDouble() >= thornChance
        ) {
            return;
        }

        float thornDamage = (float) Math.min(
                THORN_MAX_DAMAGE,
                THORN_BASE_DAMAGE + meleeLevel * THORN_DAMAGE_PER_LEVEL
        );

        if (attacker.hurt(serverLevel.damageSources().thorns(this), thornDamage)) {
            serverLevel.sendParticles(
                    ParticleTypes.CRIT,
                    attacker.getX(),
                    attacker.getY() + attacker.getBbHeight() * 0.6D,
                    attacker.getZ(),
                    18,
                    0.45D,
                    0.55D,
                    0.45D,
                    0.18D
            );
        }
    }

    private LivingEntity getDirectMeleeAttacker(DamageSource source) {
        if (
                source.is(DamageTypeTags.IS_FIRE)
                        || source.is(DamageTypeTags.IS_PROJECTILE)
                        || source.is(DamageTypeTags.IS_EXPLOSION)
                        || source.is(DamageTypes.THORNS)
                        || !(source.getEntity() instanceof LivingEntity attacker)
                        || source.getDirectEntity() != attacker
        ) {
            return null;
        }

        return attacker;
    }

    private void playBoneDeflectEffects(
            ServerLevel serverLevel,
            Vec3 impactPosition
    ) {
        serverLevel.playSound(
                null,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                ModSounds.BONE_DEFLECT.get(),
                SoundSource.HOSTILE,
                1.1F,
                1.0F
        );

        ItemParticleOption boneParticle = new ItemParticleOption(
                ParticleTypes.ITEM,
                new ItemStack(Items.BONE)
        );
        serverLevel.sendParticles(
                boneParticle,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                24,
                0.55D,
                0.65D,
                0.55D,
                0.16D
        );
        serverLevel.sendParticles(
                ParticleTypes.ELECTRIC_SPARK,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                18,
                0.48D,
                0.52D,
                0.48D,
                0.20D
        );
        serverLevel.sendParticles(
                ParticleTypes.CRIT,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                12,
                0.42D,
                0.48D,
                0.42D,
                0.14D
        );
    }

    private void playAcidSplashEffects(
            ServerLevel serverLevel,
            ServerPlayer player
    ) {
        double effectY = player.getY() + player.getBbHeight() * 0.6D;
        serverLevel.playSound(
                null,
                player.getX(),
                effectY,
                player.getZ(),
                ModSounds.ACID_SPLASH.get(),
                SoundSource.HOSTILE,
                1.0F,
                1.0F
        );
        serverLevel.sendParticles(
                ParticleTypes.ITEM_SLIME,
                player.getX(),
                effectY,
                player.getZ(),
                32,
                0.55D,
                0.65D,
                0.55D,
                0.14D
        );
        serverLevel.sendParticles(
                ParticleTypes.SPIT,
                player.getX(),
                effectY,
                player.getZ(),
                20,
                0.5D,
                0.6D,
                0.5D,
                0.12D
        );
        serverLevel.sendParticles(
                ParticleTypes.SPLASH,
                player.getX(),
                effectY,
                player.getZ(),
                16,
                0.6D,
                0.55D,
                0.6D,
                0.10D
        );
    }

    private long getAdaptationLevel(AdaptationType type) {
        if (!(level() instanceof ServerLevel serverLevel)) {
            return 0L;
        }

        return CarnisWorldData.get(serverLevel).getAdaptation(type);
    }

    private static double scaledChance(
            long level,
            double baseChance,
            double chancePerLevel,
            double maximumChance
    ) {
        if (level <= 0L) {
            return 0.0D;
        }

        return Math.min(
                maximumChance,
                baseChance + level * chancePerLevel
        );
    }

    @Override
    public void playAmbientSound() {
        super.playAmbientSound();
        triggerRoarAnimation();
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_AMALGAM_BREATH.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource damageSource) {
        return ModSounds.FLESH_AMALGAM_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.FLESH_AMALGAM_DEATH.get();
    }

    @Override
    public void registerControllers(
            AnimatableManager.ControllerRegistrar controllers
    ) {
        controllers.add(
                new AnimationController<>(
                        this,
                        "locomotion_controller",
                        5,
                        state -> state.setAndContinue(
                                state.isMoving()
                                        ? WALK_ANIMATION
                                        : IDLE_ANIMATION
                        )
                ),
                new AnimationController<>(
                        this,
                        "attack_controller",
                        2,
                        state -> {
                            if (swinging) {
                                return state.setAndContinue(ATTACK_ANIMATION);
                            }

                            state.getController().forceAnimationReset();
                            return PlayState.STOP;
                        }
                ),
                new AnimationController<>(this, "roar_controller", 2,
                        state -> PlayState.STOP).triggerableAnim("roar", ROAR_ANIMATION),
                new AnimationController<>(this, "slam_controller", 1,
                        state -> PlayState.STOP).triggerableAnim("slam", SLAM_ANIMATION)
        );
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }
}
```


## `src/main/java/com/carnis/mod/entity/ai/FleshAmalgamAbilityGoal.java`

```java
package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.AmalgamBileProjectile;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import java.util.EnumSet;

/** One wind-up at a time; cooldowns belong to the entity and persist across saves. */
public final class FleshAmalgamAbilityGoal extends Goal {
    private static final int SLAM = 1, PULL = 2, BILE = 3;
    private final FleshAmalgamEntity boss;
    private LivingEntity target;
    private int ability, elapsed;
    public FleshAmalgamAbilityGoal(FleshAmalgamEntity boss) {
        this.boss = boss;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }
    @Override public boolean canUse() {
        if (!(boss.level() instanceof ServerLevel) || !boss.isAlive()) return false;
        LivingEntity current = boss.getTarget();
        if (!HiveSwarmCoordinator.validTarget(boss, current) || !boss.hasLineOfSight(current)) return false;
        double distance = boss.distanceToSqr(current);
        if (distance < 25.0D && boss.onGround() && boss.canUseAbility(SLAM)) ability = SLAM;
        else if (distance >= 64.0D && distance <= 484.0D && boss.canUseAbility(PULL)) ability = PULL;
        else if (distance >= 25.0D && distance <= 676.0D && boss.canUseAbility(BILE)) ability = BILE;
        else return false;
        target = current;
        return true;
    }
    @Override public boolean canContinueToUse() {
        return boss.isAlive() && target != null && target.isAlive() && target.level() == boss.level() && elapsed < 20;
    }
    @Override public boolean requiresUpdateEveryTick() { return true; }
    @Override public void start() {
        elapsed = 0;
        boss.consumeAbilityCooldown(ability);
        boss.getNavigation().stop();
        if (ability == SLAM) boss.triggerSlamAnimation();
    }
    @Override public void tick() {
        if (!(boss.level() instanceof ServerLevel level) || target == null) return;
        boss.getNavigation().stop();
        boss.getLookControl().setLookAt(target, 30.0F, 30.0F);
        elapsed++;
        if (ability == SLAM && elapsed == 12 && boss.onGround()) slam(level);
        if (ability == PULL && elapsed == 8) pull(level);
        if (ability == BILE && elapsed == 8) spit(level);
    }
    @Override public void stop() { target = null; ability = 0; elapsed = 0; }
    private void slam(ServerLevel level) {
        level.playSound(null, boss.blockPosition(), ModSounds.HIVE_AMALGAM_SLAM.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
        for (int i = 0; i < 40; i++) {
            double angle = Math.PI * 2.0D * i / 40.0D;
            double x = boss.getX() + Math.cos(angle) * 6.0D, z = boss.getZ() + Math.sin(angle) * 6.0D;
            level.sendParticles(ModParticles.BIOMASS_SPARK.get(), x, boss.getY() + .15D, z, 1, 0, .05D, 0, 0);
        }
        for (LivingEntity victim : level.getEntitiesOfClass(LivingEntity.class, boss.getBoundingBox().inflate(6.0D),
                e -> e != boss && e.isAlive() && !e.isSpectator() && boss.distanceToSqr(e) <= 36.0D
                        && !NeuroArmorEventHandler.isHiveEntity(e) && boss.canAttack(e)
                        && (!(e instanceof Player player) || !player.isCreative()))) {
            if (!victim.hurt(level.damageSources().mobAttack(boss), 10.0F)) continue;
            victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 1));
            Vec3 away = victim.position().subtract(boss.position()).multiply(1, 0, 1);
            if (away.lengthSqr() > 1.0E-6D) away = away.normalize().scale(.30D);
            Vec3 old = victim.getDeltaMovement();
            victim.setDeltaMovement(old.x + away.x, Math.max(.65D, old.y + .65D), old.z + away.z);
            syncVelocity(level, victim);
        }
    }
    private void pull(ServerLevel level) {
        if (!HiveSwarmCoordinator.validTarget(boss, target) || !boss.hasLineOfSight(target)) return;
        double distance = boss.distanceToSqr(target);
        if (distance < 64.0D || distance > 484.0D) return;
        Vec3 delta = boss.position().add(0, .3D, 0).subtract(target.position());
        if (delta.lengthSqr() < 1.0E-6D) return;
        Vec3 motion = delta.normalize().scale(1.35D).add(0, .20D, 0);
        target.setDeltaMovement(motion);
        syncVelocity(level, target);
        level.playSound(null, boss.blockPosition(), ModSounds.ORGANIC_CREAK.get(), SoundSource.HOSTILE, 1.5F, 1.0F);
        for (int i = 1; i <= 10; i++) {
            Vec3 point = boss.getEyePosition().lerp(target.getEyePosition(), i / 11.0D);
            level.sendParticles(ModParticles.BIOMASS_SPARK.get(), point.x, point.y, point.z, 1, 0, 0, 0, 0);
        }
    }
    private void spit(ServerLevel level) {
        if (!HiveSwarmCoordinator.validTarget(boss, target) || !boss.hasLineOfSight(target)
                || boss.distanceToSqr(target) > 676.0D) return;
        Vec3 origin = boss.getEyePosition();
        Vec3 aim = target.getEyePosition().subtract(origin);
        if (aim.lengthSqr() < 1.0E-6D) return;
        for (int degrees : new int[]{-10, 0, 10}) {
            Vec3 direction = aim.yRot((float) Math.toRadians(degrees));
            AmalgamBileProjectile projectile = new AmalgamBileProjectile(level, boss);
            projectile.setPos(origin.x, origin.y, origin.z);
            projectile.shoot(direction.x, direction.y, direction.z, 1.35F, 0.0F);
            level.addFreshEntity(projectile);
        }
        level.playSound(null, boss.blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1.25F, 1.0F);
    }
    private static void syncVelocity(ServerLevel level, LivingEntity target) {
        ClientboundSetEntityMotionPacket packet = new ClientboundSetEntityMotionPacket(target);
        level.getChunkSource().broadcast(target, packet);
        if (target instanceof ServerPlayer player) player.connection.send(packet);
    }
}
```


## `src/main/java/com/carnis/mod/entity/ai/AmalgamBiomassFeast.java`

```java
package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.BiomassMaggotEntity;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.ForgeEventFactory;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/** Bounded incremental search: never load chunks or scan an entire cube in one tick. */
public final class AmalgamBiomassFeast {
    private static final int RADIUS = 8;
    private static final int BUDGET = 256;
    private static final List<BlockPos> OFFSETS = offsets();
    private final FleshAmalgamEntity boss;
    private BlockPos anchor;
    private int cursor;
    public AmalgamBiomassFeast(FleshAmalgamEntity boss) { this.boss = boss; }
    private static List<BlockPos> offsets() {
        List<BlockPos> result = new ArrayList<>();
        for (int x = -RADIUS; x <= RADIUS; x++) for (int y = -RADIUS; y <= RADIUS; y++)
            for (int z = -RADIUS; z <= RADIUS; z++) if (x*x + y*y + z*z <= RADIUS * RADIUS)
                result.add(new BlockPos(x, y, z));
        result.sort(Comparator.comparingInt(p -> p.getX()*p.getX() + p.getY()*p.getY() + p.getZ()*p.getZ()));
        return List.copyOf(result);
    }
    public void tick(ServerLevel level) {
        if (!boss.isAlive() || boss.getHealth() >= boss.getMaxHealth() * .4F || boss.getTarget() == null
                || !boss.getTarget().isAlive() || level.getGameTime() < boss.getFeastReady()
                || boss.tickCount % 10 != 0 || !ForgeEventFactory.getMobGriefingEvent(level, boss)) return;
        LivingEntity prey = level.getEntitiesOfClass(LivingEntity.class, boss.getBoundingBox().inflate(RADIUS),
                e -> e.isAlive() && (e instanceof BiomassMaggotEntity || e instanceof ParasiticTendrilEntity)
                        && boss.distanceToSqr(e) <= RADIUS * RADIUS).stream()
                .min(Comparator.comparingDouble(boss::distanceToSqr)).orElse(null);
        if (prey != null) {
            Vec3 location = prey.position();
            prey.discard();
            feed(level, location);
            return;
        }
        if (anchor == null || anchor.distSqr(boss.blockPosition()) > RADIUS * RADIUS) {
            anchor = boss.blockPosition().immutable();
            cursor = 0;
        }
        int end = Math.min(cursor + BUDGET, OFFSETS.size());
        while (cursor < end) {
            BlockPos pos = anchor.offset(OFFSETS.get(cursor++));
            if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)
                    || boss.position().distanceToSqr(Vec3.atCenterOf(pos)) > RADIUS * RADIUS
                    || !level.getBlockState(pos).is(ModBlocks.BIOMASS_REMAINS.get())) continue;
            if (level.setBlockAndUpdate(pos, Blocks.AIR.defaultBlockState())) {
                feed(level, Vec3.atCenterOf(pos));
                return;
            }
        }
        if (cursor >= OFFSETS.size()) { anchor = null; cursor = 0; }
    }
    private void feed(ServerLevel level, Vec3 from) {
        boss.setFeastReady(level.getGameTime() + 100L);
        anchor = null;
        cursor = 0;
        boss.heal(25.0F);
        boss.triggerRoarAnimation();
        level.playSound(null, boss.blockPosition(), ModSounds.AMALGAM_ROAR.get(), SoundSource.HOSTILE, 1.5F, 1.0F);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), from.x, from.y + .2D, from.z, 20, .35D, .35D, .35D, .04D);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), boss.getX(), boss.getY(.6D), boss.getZ(),
                30, boss.getBbWidth() * .35D, boss.getBbHeight() * .3D, boss.getBbWidth() * .35D, .06D);
    }
}
```


## `src/main/java/com/carnis/mod/event/CarnisEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.biomass.PlayerBiomassCapability;
import com.carnis.mod.capability.biomass.PlayerBiomassEvents;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.AssimilatingMob;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.entity.HiveEntity;
import com.carnis.mod.entity.BiomassValued;
import com.carnis.mod.entity.HiveSentinelEntity;
import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.UUID;

/** Мгновенная награда за убийство; питание остаётся отдельной механикой. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisEvents {
    private CarnisEvents() { }

    @SubscribeEvent(priority = EventPriority.HIGH, receiveCanceled = true)
    public static void onLivingDeath(LivingDeathEvent event) {
        LivingEntity victim = event.getEntity();
        if (!(victim.level() instanceof ServerLevel level)) return;

        Entity killer = event.getSource().getEntity();
        if (event.isCanceled() || victim instanceof Player || killer == null || killer == victim) return;

        if (victim instanceof BiomassValued hiveVictim
                && (victim instanceof HiveEntity || victim instanceof HiveSentinelEntity
                || victim instanceof CerebralNexusEntity)) {
            // Explicit Hive values are awarded only to player killers; no generic multipliers.
            if (killer instanceof ServerPlayer player) awardBiomass(player, hiveVictim.getBiomassValue());
            return;
        }

        if (victim instanceof AssimilatingMob assimilator) {
            // This entity value is final too: award directly, bypassing vanilla multipliers.
            if (killer instanceof ServerPlayer player) awardBiomass(player, assimilator.getBiomassValue());
            return;
        }

        ServerPlayer recipient = null;
        if (killer instanceof ServerPlayer player) {
            // PersistentData является источником истины; API учитывает также дробную долю.
            float infection = PlayerInfectionApi.getInfectionLevel(player);
            if (infection <= 0.0F) return;
            recipient = player;
        } else if (killer instanceof HivemindLinkedMob) {
            if (victim instanceof HivemindLinkedMob) {
                return;
            }
            if (killer instanceof TamableAnimal tame && tame.getOwnerUUID() != null) {
                UUID ownerId = tame.getOwnerUUID();
                recipient = level.getServer().getPlayerList().getPlayer(ownerId);
                if (recipient == null) {
                    // Известный владелец не в сети: не приписываем его награду дикому Улью.
                    CarnisMod.LOGGER.warn("Не удалось начислить биомассу: владелец {} не в сети", ownerId);
                    return;
                }
            }
        } else {
            return;
        }

        long total;
        if (victim instanceof BiomassValued valuedVictim) {
            total = valuedVictim.getBiomassValue();
        } else {
            // Generic vanilla mobs have no explicit final biomass value.
            long multiplier = 3L;
            if (InfectionHandler.isInfected(victim)) multiplier *= 2L;
            total = basePoints(victim) * multiplier;
        }

        if (recipient != null) {
            ServerPlayer player = recipient;
            awardBiomass(player, total);
        } else {
            CarnisWorldData data = CarnisWorldData.get(level);
            data.addBiomassPoints(total);
            ModMessages.sendToPlayersInLevel(level);
        }
    }

    private static void awardBiomass(ServerPlayer player, long amount) {
        if (amount <= 0L) return;
        var biomass = player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS);
        if (!biomass.isPresent()) {
            CarnisMod.LOGGER.warn("Не удалось начислить биомассу игроку {}: Capability отсутствует", player.getUUID());
            return;
        }
        biomass.ifPresent(data -> {
            data.addBiomassPoints(amount);
            PlayerBiomassEvents.syncToPlayer(player);
        });
    }

    private static long basePoints(LivingEntity victim) {
        // Vanilla zombie baseline is deliberately small; generic mutation/hunger multipliers follow.
        EntityType<?> type = victim.getType();
        if (type == EntityType.ZOMBIE) return 1L;
        if (type == EntityType.CREEPER || type == EntityType.SPIDER) return 5L;
        // Редкие проверяются раньше Animal/Monster: торговая лама и виз входят в эти группы.
        if (type == EntityType.ALLAY || type == EntityType.VEX || type == EntityType.WARDEN
                || type == EntityType.ELDER_GUARDIAN || type == EntityType.IRON_GOLEM
                || type == EntityType.SNOW_GOLEM || type == EntityType.TRADER_LLAMA) return 25L;
        if (victim instanceof Animal) return 5L;
        if (victim instanceof Monster) return 15L;
        return 5L;
    }
}
```


## `src/main/java/com/carnis/mod/event/InfectedCreeperEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.init.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class InfectedCreeperEvents {
    private static final int DETONATE_LEAD_TICKS = 5; // 250 ms at 20 TPS
    private static final List<PendingRupture> PENDING_RUPTURES = new ArrayList<>();

    private InfectedCreeperEvents() { }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void onExplosionStart(ExplosionEvent.Start event) {
        if (event.getLevel() instanceof ServerLevel level
                && event.getExplosion().getDirectSourceEntity() instanceof InfectedCreeperEntity creeper) {
            event.setCanceled(true);
            if (!creeper.beginRuptureCountdown()) return;

            level.playSound(null, creeper.blockPosition(), ModSounds.HIVE_SPAWN_CREEPER_DETONATE.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
            PENDING_RUPTURES.add(new PendingRupture(level, creeper,
                    level.getGameTime() + DETONATE_LEAD_TICKS));
        }
    }

    @SubscribeEvent
    public static void onLevelTick(TickEvent.LevelTickEvent event) {
        if (!(event.level instanceof ServerLevel level) || event.phase != TickEvent.Phase.END) return;
        Iterator<PendingRupture> iterator = PENDING_RUPTURES.iterator();
        while (iterator.hasNext()) {
            PendingRupture pending = iterator.next();
            if (pending.level() != level || level.getGameTime() < pending.detonateAt()) continue;
            iterator.remove();
            pending.creeper().rupture(level);
        }
    }

    private record PendingRupture(ServerLevel level, InfectedCreeperEntity creeper, long detonateAt) { }
}
```


## `src/main/java/com/carnis/mod/init/ModSounds.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUND_EVENTS =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, CarnisMod.MOD_ID);

    public static final RegistryObject<SoundEvent> INOCULATOR_FIRE =
            registerVariableRangeSound("item.inoculator.fire");
    public static final RegistryObject<SoundEvent> DART_HIT =
            registerVariableRangeSound("entity.dart.hit");

    public static final RegistryObject<SoundEvent> PURIFIER_IGNITE = registerVariableRangeSound("item.purifier.ignite");
    public static final RegistryObject<SoundEvent> PURIFIER_LOOP = registerVariableRangeSound("item.purifier.loop");
    public static final RegistryObject<SoundEvent> FLAMETHROWER_FIRE = registerVariableRangeSound("flamethrower_fire");
    public static final RegistryObject<SoundEvent> AMALGAM_SMASH = registerVariableRangeSound("amalgam_smash");
    public static final RegistryObject<SoundEvent> ORGANIC_CREAK = registerVariableRangeSound("organic_creak");
    public static final RegistryObject<SoundEvent> AMALGAM_ROAR = registerVariableRangeSound("amalgam_roar");

    public static final RegistryObject<SoundEvent> HEARTBEAT_LOOP = registerVariableRangeSound("heartbeat_loop");
    public static final RegistryObject<SoundEvent> HIVE_HEARTBEAT = registerVariableRangeSound("hive_heartbeat");

    public static final RegistryObject<SoundEvent> AMALGAM_STEP = registerVariableRangeSound("amalgam_step");

    public static final RegistryObject<SoundEvent> PHANTOM_CREEPER =
            registerVariableRangeSound("phantom_creeper");

    public static final RegistryObject<SoundEvent> PHANTOM_FOOTSTEPS =
            registerVariableRangeSound("phantom_footsteps");

    public static final RegistryObject<SoundEvent> PHANTOM_WHISPER =
            registerVariableRangeSound("phantom_whisper");

    public static final RegistryObject<SoundEvent> PULSING_HEART_BEAT =
            registerVariableRangeSound("pulsing_heart_beat");

    public static final RegistryObject<SoundEvent> SYNAPSE_SHOCK =
            registerVariableRangeSound("synapse_shock");

    public static final RegistryObject<SoundEvent> SYNAPSE_RUPTURE =
            registerVariableRangeSound("synapse_rupture");

    public static final RegistryObject<SoundEvent> DIGESTOR_CHURN =
            registerVariableRangeSound("digestor_churn");

    public static final RegistryObject<SoundEvent> HIVE_EYE_SCREECH =
            registerVariableRangeSound("hive_eye_screech");
    public static final RegistryObject<SoundEvent> HIVE_ALARM =
            registerVariableRangeSound("hive_alarm");
    public static final RegistryObject<SoundEvent> HIVE_AMBIENT =
            registerVariableRangeSound("hive_ambient");
    public static final RegistryObject<SoundEvent> HIVE_AMBIENT_CLOSE =
            registerVariableRangeSound("hive_ambient_close");
    public static final RegistryObject<SoundEvent> HIVE_PULSE =
            registerVariableRangeSound("hive_pulse");
    public static final RegistryObject<SoundEvent> HIVE_AMBIENT_TONAL_STINGER =
            registerVariableRangeSound("hive_ambient_tonal_stinger");

    public static final RegistryObject<SoundEvent> HIVE_AMB_SURFACE =
            registerVariableRangeSound("ambient.hive.surface");
    public static final RegistryObject<SoundEvent> HIVE_AMB_DEEP =
            registerVariableRangeSound("ambient.hive.deep");
    public static final RegistryObject<SoundEvent> HIVE_AMB_CORE =
            registerVariableRangeSound("ambient.hive.core");
    public static final RegistryObject<SoundEvent> HIVE_AMB_THRESHOLD =
            registerVariableRangeSound("ambient.hive.threshold");

    public static final RegistryObject<SoundEvent> ZONE_STINGER_INTENSIFY =
            registerVariableRangeSound("zone.stinger.intensify");
    public static final RegistryObject<SoundEvent> ZONE_STINGER_RELEASE =
            registerVariableRangeSound("zone.stinger.release");
    public static final RegistryObject<SoundEvent> ZONE_STINGER_DEEP =
            registerVariableRangeSound("zone.stinger.deep");

    public static final RegistryObject<SoundEvent> FLESH_BLOCK_STEP =
            registerVariableRangeSound("flesh_block_step");
    public static final RegistryObject<SoundEvent> HIVE_BLOCK_PLACE =
            registerVariableRangeSound("hive.block.place");
    public static final RegistryObject<SoundEvent> HIVE_BLOCK_BREAK =
            registerVariableRangeSound("hive.block.break");
    public static final RegistryObject<SoundEvent> HIVE_SPREAD =
            registerVariableRangeSound("hive.spread");
    public static final RegistryObject<SoundEvent> COMBAT_FLESH_HIT =
            registerVariableRangeSound("combat.flesh_hit");
    public static final RegistryObject<SoundEvent> COMBAT_FLESH_HIT_DEEP =
            registerVariableRangeSound("combat.flesh_hit_deep");
    public static final RegistryObject<SoundEvent> COMBAT_DISMEMBER =
            registerVariableRangeSound("combat.dismember");
    public static final RegistryObject<SoundEvent> COMBAT_ARMOR_DEFLECT =
            registerVariableRangeSound("combat.armor_deflect");
    public static final RegistryObject<SoundEvent> COMBAT_BLOCK_STAB =
            registerVariableRangeSound("combat.block_stab");

    public static final RegistryObject<SoundEvent> HIVE_DETAIL_FLOW =
            registerVariableRangeSound("hive.detail.flow");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_MEMBRANE =
            registerVariableRangeSound("hive.detail.membrane");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_BUBBLES =
            registerVariableRangeSound("hive.detail.bubbles");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_CREAK =
            registerVariableRangeSound("hive.detail.creak");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_SCUTTLE =
            registerVariableRangeSound("hive.detail.scuttle");

    public static final RegistryObject<SoundEvent> HIVE_SPAWN_ALERT =
            registerVariableRangeSound("hive.spawn.alert");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_ATTACK =
            registerVariableRangeSound("hive.spawn.attack");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_IDLE =
            registerVariableRangeSound("hive.spawn.idle");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_HURT =
            registerVariableRangeSound("hive.spawn.hurt");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_HURT_CRITICAL =
            registerVariableRangeSound("hive.spawn.hurt_critical");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_SKELETON_WHIP =
            registerVariableRangeSound("hive.spawn.skeleton_whip");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_SKELETON_BLADE =
            registerVariableRangeSound("hive.spawn.skeleton_blade");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_SKELETON_BONECRACK =
            registerVariableRangeSound("hive.spawn.skeleton_bonecrack");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_CREEPER_SAC =
            registerVariableRangeSound("hive.spawn_creeper_sac");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_CREEPER_CRAWL =
            registerVariableRangeSound("hive.spawn_creeper_crawl");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_CREEPER_DETONATE =
            registerVariableRangeSound("hive.spawn_creeper_detonate");
    public static final RegistryObject<SoundEvent> HIVE_AMALGAM_SHUFFLE =
            registerVariableRangeSound("hive.amalgam_shuffle");
    public static final RegistryObject<SoundEvent> HIVE_AMALGAM_BREATH =
            registerVariableRangeSound("hive.amalgam_breath");
    public static final RegistryObject<SoundEvent> HIVE_AMALGAM_SLAM =
            registerVariableRangeSound("hive.amalgam_slam");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_DEATH =
            registerVariableRangeSound("hive.spawn.death");

    public static final RegistryObject<SoundEvent> CREEPER_RUPTURE =
            registerVariableRangeSound("creeper_rupture");

    public static final RegistryObject<SoundEvent> AMALGAMATION_FUSE =
            registerVariableRangeSound("amalgamation_fuse");

    public static final RegistryObject<SoundEvent> BONE_DEFLECT =
            registerVariableRangeSound("bone_deflect");

    public static final RegistryObject<SoundEvent> ACID_SPLASH =
            registerVariableRangeSound("acid_splash");

    public static final RegistryObject<SoundEvent> PUSTULE_BURST =
            registerVariableRangeSound("pustule_burst");

    public static final RegistryObject<SoundEvent> FLESH_AMALGAM_AMBIENT =
            registerVariableRangeSound("flesh_amalgam_ambient");

    public static final RegistryObject<SoundEvent> FLESH_AMALGAM_HURT =
            registerVariableRangeSound("flesh_amalgam_hurt");

    public static final RegistryObject<SoundEvent> FLESH_AMALGAM_DEATH =
            registerVariableRangeSound("flesh_amalgam_death");

    private ModSounds() {
    }

    private static RegistryObject<SoundEvent> registerVariableRangeSound(String name) {
        ResourceLocation soundId = new ResourceLocation(CarnisMod.MOD_ID, name);
        return SOUND_EVENTS.register(
                name,
                () -> SoundEvent.createVariableRangeEvent(soundId)
        );
    }

    public static void register(IEventBus modEventBus) {
        SOUND_EVENTS.register(modEventBus);
    }
}
```


## `src/main/resources/assets/carnis/sounds.json`

```json
{
  "item.inoculator.fire": {
    "subtitle": "carnis.subtitle.inoculator_fire",
    "sounds": [
      {
        "name": "carnis:item/inoculator_fire",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "entity.dart.hit": {
    "subtitle": "carnis.subtitle.dart_hit",
    "sounds": [
      {
        "name": "carnis:item/dart_hit",
        "volume": 0.8,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "item.purifier.ignite": {
    "subtitle": "carnis.subtitle.purifier_ignite",
    "sounds": [
      {
        "name": "carnis:item/purifier_ignite",
        "volume": 1.0,
        "pitch": 1.0
      }
    ]
  },
  "item.purifier.loop": {
    "subtitle": "carnis.subtitle.purifier_loop",
    "sounds": [
      {
        "name": "carnis:item/purifier_loop",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": true
      }
    ]
  },
  "flamethrower_fire": {
    "subtitle": "carnis.subtitle.flamethrower_fire",
    "sounds": [
      {
        "name": "carnis:entity/flamethrower_fire",
        "stream": false
      }
    ]
  },
  "amalgam_smash": {
    "subtitle": "carnis.subtitle.amalgam_smash",
    "sounds": [
      "carnis:entity/amalgam_smash"
    ]
  },
  "organic_creak": {
    "subtitle": "carnis.subtitle.organic_creak",
    "sounds": [
      {
        "name": "carnis:entity/organic_creak"
      }
    ]
  },
  "amalgam_roar": {
    "subtitle": "carnis.subtitle.amalgam_roar",
    "sounds": [
      {
        "name": "carnis:entity/amalgam_roar",
        "volume": 1.0,
        "pitch": 0.75
      }
    ]
  },
  "heartbeat_loop": {
    "subtitle": "carnis.subtitle.heartbeat_loop",
    "sounds": [
      {
        "name": "carnis:block/heartbeat_loop",
        "stream": true
      }
    ]
  },
  "hive_heartbeat": {
    "subtitle": "carnis.subtitle.hive_heartbeat",
    "sounds": [
      {
        "name": "carnis:block/hive_heartbeat"
      }
    ]
  },
  "amalgam_step": {
    "subtitle": "carnis.subtitle.amalgam_step",
    "sounds": [
      {
        "name": "carnis:entity/amalgam_smash",
        "volume": 0.38,
        "pitch": 0.68,
        "weight": 1
      },
      {
        "name": "carnis:block/digestor_churn",
        "volume": 0.38,
        "pitch": 0.74,
        "weight": 1
      },
      {
        "name": "carnis:entity/flesh_amalgam_ambient",
        "volume": 0.38,
        "pitch": 0.8,
        "weight": 1
      }
    ]
  },
  "phantom_creeper": {
    "subtitle": "carnis.subtitle.phantom_creeper",
    "sounds": [
      {
        "name": "carnis:hallucination/phantom_creeper",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "phantom_footsteps": {
    "subtitle": "carnis.subtitle.phantom_footsteps",
    "sounds": [
      {
        "name": "carnis:hallucination/phantom_footsteps"
      }
    ]
  },
  "phantom_whisper": {
    "subtitle": "carnis.subtitle.phantom_whisper",
    "sounds": [
      {
        "name": "carnis:hallucination/phantom_whisper",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "pulsing_heart_beat": {
    "subtitle": "carnis.subtitle.pulsing_heart_beat",
    "sounds": [
      "carnis:block/heart_pulse"
    ]
  },
  "synapse_shock": {
    "subtitle": "carnis.subtitle.synapse_shock",
    "sounds": [
      {
        "name": "carnis:block/nervous_twitch",
        "pitch": 1.2
      }
    ]
  },
  "synapse_rupture": {
    "subtitle": "carnis.subtitle.synapse_rupture",
    "sounds": [
      {
        "name": "carnis:block/synapse_rupture",
        "pitch": 1.0
      }
    ]
  },
  "digestor_churn": {
    "subtitle": "carnis.subtitle.digestor_churn",
    "sounds": [
      {
        "name": "carnis:block/digestor_churn",
        "volume": 0.9,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "hive_eye_screech": {
    "subtitle": "carnis.subtitle.hive_eye_screech",
    "sounds": [
      {
        "name": "carnis:block/hive_eye_screech",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "hive_alarm": {
    "subtitle": "carnis.subtitle.hive_alarm",
    "sounds": [
      {
        "name": "carnis:block/hive_alarm",
        "volume": 1.0,
        "pitch": 0.9,
        "stream": false
      }
    ]
  },
  "hive_ambient": {
    "subtitle": "carnis.subtitle.hive_ambient",
    "sounds": [
      {
        "name": "carnis:amb/hive_ambient_01",
        "stream": true,
        "pitch": 0.9
      },
      {
        "name": "carnis:amb/hive_ambient_02",
        "stream": true,
        "pitch": 1.0
      },
      {
        "name": "carnis:amb/hive_ambient_03",
        "stream": true,
        "pitch": 1.1
      }
    ]
  },
  "hive_ambient_close": {
    "subtitle": "carnis.subtitle.hive_ambient_close",
    "sounds": [
      {
        "name": "carnis:amb/hive_ambient_close_01",
        "stream": true,
        "pitch": 0.95
      },
      {
        "name": "carnis:amb/hive_ambient_close_02",
        "stream": true,
        "pitch": 1.05
      }
    ]
  },
  "hive_pulse": {
    "subtitle": "carnis.subtitle.hive_pulse",
    "sounds": [
      {
        "name": "carnis:amb/hive_pulse_01",
        "stream": false,
        "pitch": 0.9
      },
      {
        "name": "carnis:amb/hive_pulse_02",
        "stream": false,
        "pitch": 1.0
      },
      {
        "name": "carnis:amb/hive_pulse_03",
        "stream": false,
        "pitch": 1.1
      }
    ]
  },
  "hive_ambient_tonal_stinger": {
    "subtitle": "carnis.subtitle.hive_ambient_tonal_stinger",
    "sounds": [
      {
        "name": "carnis:amb/hive_ambient_tonal_stinger",
        "stream": false
      }
    ]
  },
  "flesh_block_step": {
    "subtitle": "carnis.subtitle.flesh_block_step",
    "sounds": [
      {
        "name": "carnis:flesh/flesh_block_step_01",
        "pitch": 0.9
      },
      {
        "name": "carnis:flesh/flesh_block_step_02",
        "pitch": 1.0
      },
      {
        "name": "carnis:flesh/flesh_block_step_03",
        "pitch": 1.1
      }
    ]
  },
  "hive.block.place": {
    "subtitle": "carnis.subtitle.hive_block_place",
    "sounds": [
      {
        "name": "carnis:block/hive_block_place_01_soft",
        "pitch": 0.9
      },
      {
        "name": "carnis:block/hive_block_place_02_dense",
        "pitch": 1.0
      },
      {
        "name": "carnis:block/hive_block_place_03_wet",
        "pitch": 1.1
      }
    ]
  },
  "hive.block.break": {
    "subtitle": "carnis.subtitle.hive_block_break",
    "sounds": [
      {
        "name": "carnis:block/hive_block_break_01_tear",
        "pitch": 0.9
      },
      {
        "name": "carnis:block/hive_block_break_02_pop",
        "pitch": 1.0
      },
      {
        "name": "carnis:block/hive_block_break_03_crunch",
        "pitch": 1.1
      }
    ]
  },
  "hive.spread": {
    "subtitle": "carnis.subtitle.hive_spread",
    "sounds": [
      {
        "name": "carnis:hive/hive_spread_01_creep",
        "pitch": 0.9
      },
      {
        "name": "carnis:hive/hive_spread_02_pulse",
        "pitch": 1.0
      },
      {
        "name": "carnis:hive/hive_spread_03_swell",
        "pitch": 1.1
      }
    ]
  },
  "combat.flesh_hit": {
    "subtitle": "carnis.subtitle.combat_flesh_hit",
    "sounds": [
      {
        "name": "carnis:combat/combat_flesh_hit_01",
        "pitch": 0.9,
        "weight": 1
      },
      {
        "name": "carnis:combat/combat_flesh_hit_02",
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:combat/combat_flesh_hit_03",
        "pitch": 1.1,
        "weight": 1
      }
    ]
  },
  "combat.flesh_hit_deep": {
    "subtitle": "carnis.subtitle.combat_flesh_hit_deep",
    "sounds": [
      {
        "name": "carnis:combat/combat_flesh_hit_deep_01_axe",
        "pitch": 0.9,
        "weight": 1
      },
      {
        "name": "carnis:combat/combat_flesh_hit_deep_02_crit",
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:combat/combat_flesh_hit_deep_03_blast",
        "pitch": 1.1,
        "weight": 1
      }
    ]
  },
  "combat.dismember": {
    "subtitle": "carnis.subtitle.combat_dismember",
    "sounds": [
      {
        "name": "carnis:combat/dismember_01",
        "pitch": 0.85,
        "weight": 1
      },
      {
        "name": "carnis:combat/dismember_02",
        "pitch": 0.92,
        "weight": 1
      },
      {
        "name": "carnis:combat/dismember_03",
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:combat/dismember_04",
        "pitch": 1.08,
        "weight": 1
      },
      {
        "name": "carnis:combat/dismember_05",
        "pitch": 1.15,
        "weight": 1
      }
    ]
  },
  "combat.armor_deflect": {
    "subtitle": "carnis.subtitle.combat_armor_deflect",
    "sounds": [
      {
        "name": "carnis:combat/combat_deflect_01_chitin",
        "pitch": 0.85,
        "weight": 1
      },
      {
        "name": "carnis:combat/combat_deflect_02_bone",
        "pitch": 0.92,
        "weight": 1
      },
      {
        "name": "carnis:combat/combat_deflect_03_metal",
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:combat/combat_deflect_04_glance",
        "pitch": 1.08,
        "weight": 1
      },
      {
        "name": "carnis:combat/combat_deflect_05_parry",
        "pitch": 1.15,
        "weight": 1
      }
    ]
  },
  "combat.block_stab": {
    "subtitle": "carnis.subtitle.combat_block_stab",
    "sounds": [
      {
        "name": "carnis:combat/combat_stab_01_bone",
        "pitch": 0.9,
        "weight": 1
      },
      {
        "name": "carnis:combat/combat_stab_02_chitin",
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:combat/combat_stab_03_shield",
        "pitch": 1.1,
        "weight": 1
      }
    ]
  },
  "hive.detail.flow": {
    "subtitle": "carnis.subtitle.hive_detail_flow",
    "sounds": [
      {
        "name": "carnis:hive/detail_flow_01",
        "pitch": 0.95
      },
      {
        "name": "carnis:hive/detail_flow_02",
        "pitch": 1.05
      }
    ]
  },
  "hive.detail.membrane": {
    "subtitle": "carnis.subtitle.hive_detail_membrane",
    "sounds": [
      {
        "name": "carnis:hive/detail_membrane_01"
      }
    ]
  },
  "hive.detail.bubbles": {
    "subtitle": "carnis.subtitle.hive_detail_bubbles",
    "sounds": [
      {
        "name": "carnis:hive/detail_bubbles_01"
      }
    ]
  },
  "hive.detail.creak": {
    "subtitle": "carnis.subtitle.hive_detail_creak",
    "sounds": [
      {
        "name": "carnis:hive/detail_creak_01"
      }
    ]
  },
  "hive.detail.scuttle": {
    "subtitle": "carnis.subtitle.hive_detail_scuttle",
    "sounds": [
      {
        "name": "carnis:hive/detail_scuttle_01"
      }
    ]
  },
  "hive.spawn.alert": {
    "subtitle": "carnis.subtitle.hive_spawn_alert",
    "sounds": [
      {
        "name": "carnis:block/hive_alarm",
        "volume": 0.6,
        "pitch": 0.96,
        "weight": 1
      },
      {
        "name": "carnis:block/hive_eye_screech",
        "volume": 0.6,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:block/heartbeat_loop",
        "volume": 0.6,
        "pitch": 1.04,
        "weight": 1
      }
    ]
  },
  "hive.spawn.attack": {
    "subtitle": "carnis.subtitle.hive_spawn_attack",
    "sounds": [
      {
        "name": "carnis:entity/amalgam_smash",
        "volume": 0.7,
        "pitch": 0.94,
        "weight": 1
      },
      {
        "name": "carnis:block/synapse_rupture",
        "volume": 0.7,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:entity/acid_splash",
        "volume": 0.7,
        "pitch": 1.06,
        "weight": 1
      }
    ]
  },
  "hive.spawn.idle": {
    "subtitle": "carnis.subtitle.hive_spawn_idle",
    "sounds": [
      {
        "name": "carnis:block/heartbeat_loop",
        "volume": 0.35,
        "pitch": 0.96,
        "weight": 1
      },
      {
        "name": "carnis:entity/flesh_amalgam_ambient",
        "volume": 0.35,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:block/digestor_churn",
        "volume": 0.35,
        "pitch": 1.04,
        "weight": 1
      }
    ]
  },
  "hive.spawn.hurt": {
    "subtitle": "carnis.subtitle.hive_spawn_hurt",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_hurt",
        "volume": 0.65,
        "pitch": 0.94,
        "weight": 1
      },
      {
        "name": "carnis:entity/acid_splash",
        "volume": 0.65,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:block/nervous_twitch",
        "volume": 0.65,
        "pitch": 1.06,
        "weight": 1
      }
    ]
  },
  "hive.spawn.hurt_critical": {
    "subtitle": "carnis.subtitle.hive_spawn_hurt_critical",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_hurt",
        "volume": 0.8,
        "pitch": 0.92,
        "weight": 1
      },
      {
        "name": "carnis:block/synapse_rupture",
        "volume": 0.8,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:block/pustule_burst",
        "volume": 0.8,
        "pitch": 1.08,
        "weight": 1
      }
    ]
  },
  "hive.spawn.death": {
    "subtitle": "carnis.subtitle.hive_spawn_death",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_death",
        "volume": 0.9,
        "pitch": 0.92,
        "weight": 1
      },
      {
        "name": "carnis:block/creeper_rupture",
        "volume": 0.9,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:block/synapse_rupture",
        "volume": 0.9,
        "pitch": 1.08,
        "weight": 1
      }
    ]
  },
  "hive.spawn.skeleton_whip": {
    "subtitle": "carnis.subtitle.hive_spawn_skeleton_whip",
    "sounds": [
      {
        "name": "carnis:entity/flamethrower_fire",
        "volume": 0.65,
        "pitch": 0.94,
        "weight": 1
      },
      {
        "name": "carnis:block/nervous_twitch",
        "volume": 0.65,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:entity/amalgamation_fuse",
        "volume": 0.65,
        "pitch": 1.06,
        "weight": 1
      }
    ]
  },
  "hive.spawn.skeleton_blade": {
    "subtitle": "carnis.subtitle.hive_spawn_skeleton_blade",
    "sounds": [
      {
        "name": "carnis:entity/amalgam_smash",
        "volume": 0.7,
        "pitch": 0.94,
        "weight": 1
      },
      {
        "name": "carnis:block/synapse_rupture",
        "volume": 0.7,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:block/creeper_rupture",
        "volume": 0.7,
        "pitch": 1.06,
        "weight": 1
      }
    ]
  },
  "hive.spawn.skeleton_bonecrack": {
    "subtitle": "carnis.subtitle.hive_spawn_skeleton_bonecrack",
    "sounds": [
      {
        "name": "carnis:block/digestor_churn",
        "volume": 0.55,
        "pitch": 0.94,
        "weight": 1
      },
      {
        "name": "carnis:block/pustule_burst",
        "volume": 0.55,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:block/nervous_twitch",
        "volume": 0.55,
        "pitch": 1.06,
        "weight": 1
      }
    ]
  },
  "creeper_rupture": {
    "subtitle": "carnis.subtitle.creeper_rupture",
    "sounds": [
      {
        "name": "carnis:block/creeper_rupture",
        "pitch": 0.9,
        "volume": 1.0
      }
    ]
  },
  "amalgamation_fuse": {
    "subtitle": "carnis.subtitle.amalgamation_fuse",
    "sounds": [
      {
        "name": "carnis:entity/amalgamation_fuse",
        "volume": 1.1,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "bone_deflect": {
    "subtitle": "carnis.subtitle.bone_deflect",
    "sounds": [
      {
        "name": "carnis:block/bone_deflect"
      }
    ]
  },
  "acid_splash": {
    "subtitle": "carnis.subtitle.acid_splash",
    "sounds": [
      {
        "name": "carnis:entity/acid_splash",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "pustule_burst": {
    "subtitle": "carnis.subtitle.pustule_burst",
    "sounds": [
      "carnis:block/pustule_burst"
    ]
  },
  "flesh_amalgam_ambient": {
    "subtitle": "carnis.subtitle.flesh_amalgam_ambient",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_ambient",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "flesh_amalgam_hurt": {
    "subtitle": "carnis.subtitle.flesh_amalgam_hurt",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_hurt",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "flesh_amalgam_death": {
    "subtitle": "carnis.subtitle.flesh_amalgam_death",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_death",
        "volume": 1.1,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "ambient.hive.surface": {
    "subtitle": "carnis.subtitle.amb_hive_surface",
    "sounds": [
      {
        "name": "carnis:hive/amb_surface",
        "stream": true
      }
    ]
  },
  "ambient.hive.deep": {
    "subtitle": "carnis.subtitle.amb_hive_deep",
    "sounds": [
      {
        "name": "carnis:hive/amb_deep",
        "stream": true
      }
    ]
  },
  "ambient.hive.core": {
    "subtitle": "carnis.subtitle.amb_hive_core",
    "sounds": [
      {
        "name": "carnis:hive/amb_core",
        "stream": true
      }
    ]
  },
  "ambient.hive.threshold": {
    "subtitle": "carnis.subtitle.amb_hive_threshold",
    "sounds": [
      {
        "name": "carnis:hive/amb_threshold",
        "stream": true
      }
    ]
  },
  "zone.stinger.intensify": {
    "subtitle": "carnis.subtitle.zone_stinger_intensify",
    "sounds": [
      {
        "name": "carnis:hive/zone_stinger_intensify",
        "volume": 0.65,
        "pitch": 1.0
      }
    ]
  },
  "zone.stinger.release": {
    "subtitle": "carnis.subtitle.zone_stinger_release",
    "sounds": [
      {
        "name": "carnis:hive/zone_stinger_release",
        "volume": 0.65,
        "pitch": 1.0
      }
    ]
  },
  "zone.stinger.deep": {
    "subtitle": "carnis.subtitle.zone_stinger_deep",
    "sounds": [
      {
        "name": "carnis:hive/zone_stinger_deep",
        "volume": 0.65,
        "pitch": 1.0
      }
    ]
  },
  "hive.spawn_creeper_sac": {
    "subtitle": "carnis.subtitle.hive_spawn_creeper_sac",
    "sounds": [
      {
        "name": "carnis:block/pustule_burst",
        "volume": 0.32,
        "pitch": 0.94,
        "weight": 1
      },
      {
        "name": "carnis:block/heartbeat_loop",
        "volume": 0.32,
        "pitch": 1.04,
        "weight": 1
      },
      {
        "name": "carnis:entity/amalgamation_fuse",
        "volume": 0.32,
        "pitch": 1.0,
        "weight": 1
      }
    ]
  },
  "hive.spawn_creeper_crawl": {
    "subtitle": "carnis.subtitle.hive_spawn_creeper_crawl",
    "sounds": [
      {
        "name": "carnis:block/nervous_twitch",
        "volume": 0.3,
        "pitch": 0.94,
        "weight": 1
      },
      {
        "name": "carnis:block/digestor_churn",
        "volume": 0.3,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:block/heartbeat_loop",
        "volume": 0.3,
        "pitch": 1.06,
        "weight": 1
      }
    ]
  },
  "hive.spawn_creeper_detonate": {
    "subtitle": "carnis.subtitle.hive_spawn_creeper_detonate",
    "sounds": [
      {
        "name": "carnis:block/creeper_rupture",
        "volume": 0.4,
        "pitch": 0.92,
        "weight": 1
      },
      {
        "name": "carnis:block/synapse_rupture",
        "volume": 0.4,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:block/pustule_burst",
        "volume": 0.4,
        "pitch": 1.06,
        "weight": 1
      }
    ]
  },
  "hive.amalgam_shuffle": {
    "subtitle": "carnis.subtitle.hive_amalgam_shuffle",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_ambient",
        "volume": 0.35,
        "pitch": 0.94,
        "weight": 1
      },
      {
        "name": "carnis:block/digestor_churn",
        "volume": 0.35,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:entity/amalgamation_fuse",
        "volume": 0.35,
        "pitch": 1.06,
        "weight": 1
      }
    ]
  },
  "hive.amalgam_breath": {
    "subtitle": "carnis.subtitle.hive_amalgam_breath",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_ambient",
        "volume": 0.25,
        "pitch": 0.94,
        "weight": 1
      },
      {
        "name": "carnis:entity/amalgam_roar",
        "volume": 0.25,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:entity/flesh_amalgam_ambient",
        "volume": 0.25,
        "pitch": 1.06,
        "weight": 1
      }
    ]
  },
  "hive.amalgam_slam": {
    "subtitle": "carnis.subtitle.hive_amalgam_slam",
    "sounds": [
      {
        "name": "carnis:entity/amalgam_smash",
        "volume": 0.55,
        "pitch": 0.92,
        "weight": 1
      },
      {
        "name": "carnis:block/synapse_rupture",
        "volume": 0.55,
        "pitch": 1.0,
        "weight": 1
      },
      {
        "name": "carnis:block/creeper_rupture",
        "volume": 0.55,
        "pitch": 1.06,
        "weight": 1
      }
    ]
  }
}
```


## `src/main/resources/assets/carnis/lang/en_us.json`

```json
{
  "carnis.subtitle.pustule_burst": "Pustule bursts",
  "carnis.subtitle.hive_eye_screech": "Hive eye screeches",
  "carnis.subtitle.hive_alarm": "Hive alarm",
  "carnis.subtitle.acid_splash": "Acid splashes",
  "carnis.subtitle.amalgamation_fuse": "Amalgamation begins",
  "carnis.subtitle.digestor_churn": "Digestor churns",
  "carnis.subtitle.flesh_amalgam_ambient": "Flesh amalgam groans",
  "carnis.subtitle.flesh_amalgam_death": "Flesh amalgam dies",
  "carnis.subtitle.flesh_amalgam_hurt": "Flesh amalgam hurt",
  "carnis.subtitle.phantom_creeper": "Phantom creeper hisses",
  "carnis.subtitle.phantom_whisper": "A phantom whispers",
  "carnis.subtitle.synapse_rupture": "Synapse ruptures",
  "carnis.subtitle.heartbeat_loop": "Heartbeat",
  "carnis.subtitle.amalgam_roar": "Amalgam roars",
  "carnis.subtitle.flamethrower_fire": "Flamethrower fires",
  "carnis.subtitle.synapse_shock": "Synapse shocks",
  "carnis.subtitle.pulsing_heart_beat": "Pulsing heart beats",
  "carnis.subtitle.inoculator_fire": "Inoculator fires",
  "carnis.subtitle.dart_hit": "Dart hits",
  "carnis.subtitle.purifier_ignite": "Purifier ignites",
  "carnis.subtitle.purifier_loop": "Purifier runs",
  "carnis.subtitle.amalgam_smash": "Amalgam smashes",
  "carnis.subtitle.creeper_rupture": "Creeper ruptures",
  "carnis.subtitle.organic_creak": "Organic mass creaks",
  "carnis.subtitle.hive_heartbeat": "The Hive heartbeat",
  "carnis.subtitle.amalgam_step": "Heavy amalgam step",
  "carnis.subtitle.phantom_footsteps": "Phantom footsteps",
  "carnis.subtitle.hive_ambient": "The Hive breathes",
  "carnis.subtitle.hive_ambient_close": "The Hive stirs nearby",
  "carnis.subtitle.hive_pulse": "The Hive pulses",
  "carnis.subtitle.hive_ambient_tonal_stinger": "A Hive tone rings out",
  "carnis.subtitle.flesh_block_step": "Footsteps squelch through flesh",
  "carnis.subtitle.hive_block_place": "Hive tissue grows",
  "carnis.subtitle.hive_block_break": "Hive tissue tears",
  "carnis.subtitle.hive_spread": "The Hive spreads",
  "carnis.subtitle.combat_flesh_hit": "Flesh is struck",
  "carnis.subtitle.combat_flesh_hit_deep": "A deep blow lands",
  "carnis.subtitle.combat_dismember": "A body part is severed",
  "carnis.subtitle.hive_detail_flow": "Fluid flows through the Hive",
  "carnis.subtitle.hive_detail_membrane": "A membrane flexes",
  "carnis.subtitle.hive_detail_bubbles": "Bubbles rise in the Hive",
  "carnis.subtitle.hive_detail_creak": "Organic tissue creaks",
  "carnis.subtitle.hive_detail_scuttle": "Something scuttles within the Hive",
  "carnis.subtitle.hive_spawn_alert": "A Hive creature alerts",
  "carnis.subtitle.hive_spawn_attack": "A Hive creature attacks",
  "carnis.subtitle.hive_spawn_idle": "A Hive creature stirs",
  "carnis.subtitle.hive_spawn_hurt": "A Hive creature is hurt",
  "carnis.subtitle.hive_spawn_hurt_critical": "A Hive creature suffers a critical wound",
  "carnis.subtitle.hive_spawn_skeleton_whip": "Infected Skeleton lashes",
  "carnis.subtitle.hive_spawn_skeleton_blade": "Infected Skeleton strikes",
  "carnis.subtitle.hive_spawn_skeleton_bonecrack": "Bones crack",
  "carnis.subtitle.hive_spawn_death": "A Hive creature dies",
  "carnis.subtitle.bone_deflect": "Bone deflects the blow",
  "carnis.subtitle.combat_armor_deflect": "Armor deflects the blow",
  "carnis.subtitle.combat_block_stab": "A weapon strikes the shield",
  "carnis.subtitle.amb_hive_surface": "Hive hums (surface)",
  "carnis.subtitle.amb_hive_deep": "Hive groans (deep)",
  "carnis.subtitle.amb_hive_core": "Hive pulses (core)",
  "carnis.subtitle.amb_hive_threshold": "Hive breathes (threshold)",
  "carnis.subtitle.zone_stinger_intensify": "Hive membrane tightens",
  "carnis.subtitle.zone_stinger_release": "Hive membrane relaxes",
  "carnis.subtitle.zone_stinger_deep": "Descending into the hive",
  "carnis.subtitle.hive_spawn_creeper_sac": "An infected creeper sac pulses",
  "carnis.subtitle.hive_spawn_creeper_crawl": "An infected creeper crawls",
  "carnis.subtitle.hive_spawn_creeper_detonate": "An infected creeper detonates",
  "carnis.subtitle.hive_amalgam_shuffle": "The amalgam shuffles",
  "carnis.subtitle.hive_amalgam_breath": "The amalgam breathes",
  "carnis.subtitle.hive_amalgam_slam": "The amalgam slams down"
}
```


## `src/main/resources/assets/carnis/lang/ru_ru.json`

```json
{
  "carnis.subtitle.pustule_burst": "Пустула лопнула",
  "carnis.subtitle.hive_eye_screech": "Улей-глаз визжит",
  "carnis.subtitle.hive_alarm": "Тревога улья",
  "carnis.subtitle.acid_splash": "Кислота шипит",
  "carnis.subtitle.amalgamation_fuse": "Слияние начинается",
  "carnis.subtitle.digestor_churn": "Перевариватель урчит",
  "carnis.subtitle.flesh_amalgam_ambient": "Плотский амальгам стонет",
  "carnis.subtitle.flesh_amalgam_death": "Плотский амальгам погибает",
  "carnis.subtitle.flesh_amalgam_hurt": "Плотский амальгам ранен",
  "carnis.subtitle.phantom_creeper": "Фантомный крипер шипит",
  "carnis.subtitle.phantom_whisper": "Фантом шепчет",
  "carnis.subtitle.synapse_rupture": "Синапс разрывается",
  "carnis.subtitle.heartbeat_loop": "Сердцебиение",
  "carnis.subtitle.amalgam_roar": "Амальгам рычит",
  "carnis.subtitle.flamethrower_fire": "Огнемёт стреляет",
  "carnis.subtitle.synapse_shock": "Разряд синапса",
  "carnis.subtitle.pulsing_heart_beat": "Пульсирующее сердце бьётся",
  "carnis.subtitle.inoculator_fire": "Инокулятор стреляет",
  "carnis.subtitle.dart_hit": "Дротик попал",
  "carnis.subtitle.purifier_ignite": "Очиститель зажёгся",
  "carnis.subtitle.purifier_loop": "Очиститель работает",
  "carnis.subtitle.amalgam_smash": "Амальгам бьёт",
  "carnis.subtitle.creeper_rupture": "Крипер разрывается",
  "carnis.subtitle.organic_creak": "Органическая масса скрипит",
  "carnis.subtitle.hive_heartbeat": "Сердцебиение Улья",
  "carnis.subtitle.amalgam_step": "Тяжёлый шаг амальгамы",
  "carnis.subtitle.phantom_footsteps": "Призрачные шаги",
  "carnis.subtitle.hive_ambient": "Улей дышит",
  "carnis.subtitle.hive_ambient_close": "Улей шевелится рядом",
  "carnis.subtitle.hive_pulse": "Улей пульсирует",
  "carnis.subtitle.hive_ambient_tonal_stinger": "Звучит тон Улья",
  "carnis.subtitle.flesh_block_step": "Шаги хлюпают по плоти",
  "carnis.subtitle.hive_block_place": "Ткань Улья разрастается",
  "carnis.subtitle.hive_block_break": "Ткань Улья разрывается",
  "carnis.subtitle.hive_spread": "Улей распространяется",
  "carnis.subtitle.combat_flesh_hit": "Удар по плоти",
  "carnis.subtitle.combat_flesh_hit_deep": "Тяжёлый удар",
  "carnis.subtitle.combat_dismember": "Часть тела отсечена",
  "carnis.subtitle.hive_detail_flow": "Жидкость течёт внутри Улья",
  "carnis.subtitle.hive_detail_membrane": "Мембрана натягивается",
  "carnis.subtitle.hive_detail_bubbles": "В Улье поднимаются пузыри",
  "carnis.subtitle.hive_detail_creak": "Органическая ткань скрипит",
  "carnis.subtitle.hive_detail_scuttle": "В Улье кто-то шуршит",
  "carnis.subtitle.hive_spawn_alert": "Существо Улья подаёт сигнал",
  "carnis.subtitle.hive_spawn_attack": "Существо Улья атакует",
  "carnis.subtitle.hive_spawn_idle": "Существо Улья шевелится",
  "carnis.subtitle.hive_spawn_hurt": "Существо Улья ранено",
  "carnis.subtitle.hive_spawn_hurt_critical": "Существо Улья получает критическое ранение",
  "carnis.subtitle.hive_spawn_skeleton_whip": "Заражённый скелет щёлкает жгутиком",
  "carnis.subtitle.hive_spawn_skeleton_blade": "Заражённый скелет бьёт клинком",
  "carnis.subtitle.hive_spawn_skeleton_bonecrack": "Кости хрустят",
  "carnis.subtitle.hive_spawn_death": "Существо Улья погибает",
  "carnis.subtitle.bone_deflect": "Кость отражает удар",
  "carnis.subtitle.combat_armor_deflect": "Броня отражает удар",
  "carnis.subtitle.combat_block_stab": "Оружие ударяет по щиту",
  "carnis.subtitle.amb_hive_surface": "Улей гудит (поверхность)",
  "carnis.subtitle.amb_hive_deep": "Улей стонет (глубина)",
  "carnis.subtitle.amb_hive_core": "Улей пульсирует (ядро)",
  "carnis.subtitle.amb_hive_threshold": "Улей дышит (порог)",
  "carnis.subtitle.zone_stinger_intensify": "Мембрана улья натягивается",
  "carnis.subtitle.zone_stinger_release": "Мембрана улья ослабевает",
  "carnis.subtitle.zone_stinger_deep": "Погружение в улей",
  "carnis.subtitle.hive_spawn_creeper_sac": "Мешок заражённого крипера пульсирует",
  "carnis.subtitle.hive_spawn_creeper_crawl": "Заражённый крипер ползёт",
  "carnis.subtitle.hive_spawn_creeper_detonate": "Заражённый крипер взрывается",
  "carnis.subtitle.hive_amalgam_shuffle": "Амальгам шаркает",
  "carnis.subtitle.hive_amalgam_breath": "Амальгам дышит",
  "carnis.subtitle.hive_amalgam_slam": "Амальгам обрушивает удар"
}
```


## `gradle.properties`

```properties
# Gradle settings
org.gradle.jvmargs=-Xmx3G -Dfile.encoding=UTF-8
org.gradle.daemon=false
org.gradle.parallel=false
org.gradle.workers.max=2
org.gradle.caching=true
org.gradle.configuration-cache=false
org.gradle.warning.mode=all

# Project properties
mod_id=carnis
mod_name=Carnis: Adaptive Hivemind
mod_license=MIT
mod_version=3.4.6
mod_author=BlockBaster3K
mod_description=The Living Swarm Update: Hive evolution, four parasitic stages, organogenesis, the Flesh Amalgam, Neuro-Resonator armor, the Bio-Purifier and Codex Carnis.

# Versions
minecraft_version=1.20.1
minecraft_version_range=[1.20.1]
forge_version=47.4.28
forge_version_range=[47.1.0,)
loader_version_range=[47,)
geckolib_version=4.4.4
mapping_channel=official
mapping_version=1.20.1
```


## `build.gradle`

```groovy
plugins {
    id 'eclipse'
    id 'maven-publish'
    id 'net.minecraftforge.gradle'
}

version = project.mod_version
group = "com.carnis.mod"
archivesBaseName = "${mod_id}"

java.toolchain.languageVersion = JavaLanguageVersion.of(17)

minecraft {
    mappings channel: 'official', version: "${minecraft_version}"
    copyIdeResources = true

    runs {
        configureEach {
            workingDirectory project.file('run')
            property 'forge.logging.markers', 'REGISTRIES'
            property 'forge.logging.console.level', 'debug'
            mods {
                "${mod_id}" {
                    source sourceSets.main
                }
            }
        }

        client {
            property 'forge.enabledGameTestNamespaces', mod_id
        }

        server {
            property 'forge.enabledGameTestNamespaces', mod_id
            args '--nogui'
        }

        data {
            workingDirectory project.file('run')
            args '--mod', mod_id, '--all',
                 '--output', file('src/generated/resources/'),
                 '--existing', file('src/main/resources/')
        }
    }
}

sourceSets.main.resources {
    srcDir 'src/generated/resources'
}

repositories {
    mavenCentral()
    maven {
        name = 'GeckoLib'
        url = 'https://dl.cloudsmith.io/public/geckolib3/geckolib/maven/'
    }
}

dependencies {
    minecraft "net.minecraftforge:forge:${minecraft_version}-${forge_version}"
    implementation fg.deobf("software.bernie.geckolib:geckolib-forge-${minecraft_version}:${geckolib_version}")
}

tasks.named('processResources', ProcessResources).configure {
    var replaceProperties = [
            minecraft_version      : minecraft_version,
            minecraft_version_range: minecraft_version_range,
            forge_version          : forge_version,
            forge_version_range    : forge_version_range,
            loader_version_range   : loader_version_range,
            mod_id                 : mod_id,
            mod_name               : mod_name,
            mod_license            : mod_license,
            mod_version            : mod_version,
            mod_author             : mod_author,
            mod_description        : mod_description
    ]
    inputs.properties replaceProperties

    filesMatching(['META-INF/mods.toml', 'pack.mcmeta']) {
        expand replaceProperties + [project: project]
    }

    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}

tasks.named('jar', Jar).configure {
    manifest {
        attributes([
                'Specification-Title'     : mod_id,
                'Specification-Vendor'    : mod_author,
                'Specification-Version'   : '1',
                'Implementation-Title'    : project.name,
                'Implementation-Version'  : project.jar.archiveVersion,
                'Implementation-Vendor'   : mod_author,
                'Implementation-Timestamp': new Date().format("yyyy-MM-dd'T'HH:mm:ssZ")
        ])
    }
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
    finalizedBy 'reobfJar'
}

tasks.withType(JavaCompile).configureEach {
    options.encoding = 'UTF-8'
}
```


## `src/main/resources/META-INF/mods.toml`

```toml
modLoader="javafml"
loaderVersion="[47,)"
license="MIT"

[[mods]]
modId="carnis"
version="${mod_version}"
displayName="Carnis: Adaptive Hivemind"
displayVersion="${mod_version}"
authors="BlockBaster3K"
description='''The Living Swarm Update. An adaptive organic Hive evolves through four stages of parasitism, spreading living tissue and developing macroscopic organs. Explore the Pulsing Heart and its network, confront the Flesh Amalgam, and survive the Swarm with Neuro-Resonator armor, the Bio-Purifier, the Pneumatic Inoculator and the Codex Carnis.'''

[[dependencies.carnis]]
modId="forge"
mandatory=true
versionRange="[47.1.0,)"
ordering="NONE"
side="BOTH"

[[dependencies.carnis]]
modId="minecraft"
mandatory=true
versionRange="[1.20.1]"
ordering="NONE"
side="BOTH"

[[dependencies.carnis]]
modId="geckolib"
mandatory=true
versionRange="[4.4.4,)"
ordering="AFTER"
side="BOTH"
```
