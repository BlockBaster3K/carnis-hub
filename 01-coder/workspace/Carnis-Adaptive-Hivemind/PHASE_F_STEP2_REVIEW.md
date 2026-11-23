# Carnis 3.4.4 — Фаза F, шаг 2: полный текст для ревизора

> Включены все запрошенные полные файлы и дополнительные изменённые исходники, относящиеся к whiplash-анимации, AI-цели и регистрации атрибутов. В `sounds.json` прежние записи сохранены; добавлены три skeleton-события.

## `InfectedSkeletonEntity.java` — `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java`

```java

package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.HiveDefendHeartGoal;
import com.carnis.mod.entity.ai.HiveEscortLeaderGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.entity.ai.InfectedSkeletonWhipGoal;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
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
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;

public final class InfectedSkeletonEntity extends HiveEntity implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final long BIOMASS_VALUE = 5L;
    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedSkeletonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> WHIPPING =
            SynchedEntityData.defineId(InfectedSkeletonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_skeleton.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_skeleton.walk");
    private static final RawAnimation HEARTBEAT = RawAnimation.begin().thenLoop("animation.infected_skeleton.heartbeat");
    private static final RawAnimation BLADE_ATTACK = RawAnimation.begin().thenPlay("animation.infected_skeleton.attack_scythe");
    private static final RawAnimation WHIP_ATTACK = RawAnimation.begin().thenPlay("animation.infected_skeleton.attack_whip");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedSkeletonEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
        entityData.define(WHIPPING, false);
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
        return entityData.get(WHIPPING);
    }

    public void setWhipping(boolean whipping) {
        entityData.set(WHIPPING, whipping);
    }

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
            if (isAssimilating()) return state.setAndContinue(
                    RawAnimation.begin().thenLoop("animation.infected_skeleton.assimilate"));
            return state.setAndContinue(state.isMoving() ? WALK : IDLE);
        }));
        controllers.add(new AnimationController<>(this, "heartbeat", 0,
                state -> isAssimilating() ? PlayState.STOP : state.setAndContinue(HEARTBEAT)));
        controllers.add(new AnimationController<>(this, "action", 0, state -> {
            if (isWhipping()) return state.setAndContinue(WHIP_ATTACK);
            if (!isAssimilating() && swinging) return state.setAndContinue(BLADE_ATTACK);
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
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(0, new HiveDefendHeartGoal(this));
        goalSelector.addGoal(1, new InfectedSkeletonWhipGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.15D, false));
        goalSelector.addGoal(3, new CarnisFeedingGoal(this));
        goalSelector.addGoal(4, new CarnisGestationGoal(this));
        goalSelector.addGoal(5, new MoveTowardsRestrictionGoal(this, 0.9D));
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.9D));
        goalSelector.addGoal(7, new HiveEscortLeaderGoal(this));
        goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 10.0F));
        goalSelector.addGoal(9, new RandomLookAroundGoal(this));

        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                target -> HiveSwarmCoordinator.validTarget(this, target)));
        targetSelector.addGoal(2, new HurtByTargetGoal(this));
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        return !(target instanceof HiveEntity || target instanceof HivemindLinkedMob) && super.canAttack(target);
    }

    @Override
    public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
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
}

```

## `InfectedSkeletonWhipGoal.java` — `src/main/java/com/carnis/mod/entity/ai/InfectedSkeletonWhipGoal.java`

```java

package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.InfectedSkeletonEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import java.util.EnumSet;

/** Whip strike used only while a valid target is between 1.5 and 3 blocks away. */
public final class InfectedSkeletonWhipGoal extends Goal {
    private final InfectedSkeletonEntity mob;
    private LivingEntity target;
    private int windupTicks;
    private int nextAttackTick;
    private boolean completed;

    public InfectedSkeletonWhipGoal(InfectedSkeletonEntity mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private boolean inWhipRange(LivingEntity candidate) {
        if (candidate == null || !candidate.isAlive() || candidate.level() != mob.level()) return false;
        double distance = mob.distanceToSqr(candidate);
        return distance >= 2.25D && distance <= 9.0D;
    }

    @Override
    public boolean canUse() {
        target = mob.getTarget();
        return mob.tickCount >= nextAttackTick && inWhipRange(target) && mob.canAttack(target);
    }

    @Override
    public boolean canContinueToUse() {
        return !completed && inWhipRange(target) && mob.getTarget() == target && mob.canAttack(target);
    }

    @Override
    public void start() {
        completed = false;
        windupTicks = 4;
        mob.setWhipping(true);
        mob.getNavigation().stop();
    }

    @Override
    public void stop() {
        mob.setWhipping(false);
        if (!completed) mob.getNavigation().stop();
        target = null;
    }

    @Override
    public void tick() {
        if (target == null || !target.isAlive()) return;
        mob.getLookControl().setLookAt(target, 30.0F, 30.0F);
        mob.getNavigation().stop();
        if (--windupTicks <= 0) {
            mob.performWhipAttack();
            nextAttackTick = mob.tickCount + 30;
            completed = true;
            mob.setWhipping(false);
        }
    }
}

```

## `InfectedZombieEntity.java` — `src/main/java/com/carnis/mod/entity/InfectedZombieEntity.java`

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
        goalSelector.addGoal(0, new MeleeAttackGoal(this, 1.0D, false));
        goalSelector.addGoal(0, new HiveDefendHeartGoal(this));
        goalSelector.addGoal(1, new CarnisFeedingGoal(this));
        goalSelector.addGoal(2, new CarnisGestationGoal(this));
        goalSelector.addGoal(3, new RandomStrollGoal(this, 0.8D));
        goalSelector.addGoal(4, new HiveEscortLeaderGoal(this));
        goalSelector.addGoal(5, new LookAtPlayerGoal(this, Player.class, 8.0F));
        goalSelector.addGoal(6, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                target -> HiveSwarmCoordinator.validTarget(this, target)));
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
        boolean wasUntargeted = getTarget() == null;
        super.setTarget(target);
        if (wasUntargeted && target != null && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_ALERT.get(),
                    SoundSource.HOSTILE, 0.9F, 0.95F + random.nextFloat() * 0.1F);
        }
    }
}

```

## `CarnisEvents.java` — `src/main/java/com/carnis/mod/event/CarnisEvents.java`

```java

package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.biomass.PlayerBiomassCapability;
import com.carnis.mod.capability.biomass.PlayerBiomassEvents;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.AssimilatingMob;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.entity.HiveEntity;
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

        if (victim instanceof HiveEntity hiveVictim) {
            // Explicit HiveEntity values are awarded only to player killers; no generic multipliers.
            if (killer instanceof ServerPlayer player) awardBiomass(player, hiveVictim.getBiomassValue());
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

        long multiplier = 1L;
        if (InfectionHandler.isInfected(victim)) multiplier *= 2L;
        if (victim instanceof AssimilatingMob) multiplier *= 3L;
        long total = basePoints(victim) * multiplier;

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
        if (victim instanceof FleshAmalgamEntity) return 500L;
        // Редкие проверяются раньше Animal/Monster: торговая лама и виз входят в эти группы.
        EntityType<?> type = victim.getType();
        if (type == EntityType.ALLAY || type == EntityType.VEX || type == EntityType.WARDEN
                || type == EntityType.ELDER_GUARDIAN || type == EntityType.IRON_GOLEM
                || type == EntityType.SNOW_GOLEM || type == EntityType.TRADER_LLAMA) return 25L;
        if (victim instanceof Animal) return 5L;
        if (victim instanceof Monster) return 15L;
        return 5L;
    }
}

```

## `HiveEntity.java` — `src/main/java/com/carnis/mod/entity/HiveEntity.java`

```java

package com.carnis.mod.entity;

import com.carnis.mod.init.ModSounds;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/** Common base for living hive monsters; keeps shared sound and critical-wound behavior centralized. */
public abstract class HiveEntity extends Monster {
    private static final String CRITICAL_HURT_COOLDOWN = "carnis:hive_critical_hurt_ms";
    private static final long CRITICAL_HURT_COOLDOWN_MS = 120L;

    protected HiveEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    public static net.minecraft.world.entity.ai.attributes.AttributeSupplier.Builder createAttributes() {
        return HiveEntityAttributes.create();
    }

    // Явное значение биомассы. Множители НЕ применяются.
    public long getBiomassValue() {
        return 0L;
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
        boolean hurt = super.hurt(source, amount);
        if (hurt && !level().isClientSide && isAlive() && getMaxHealth() > 0.0F
                && getHealth() / getMaxHealth() < 0.25F) {
            long now = System.currentTimeMillis();
            long last = getPersistentData().getLong(CRITICAL_HURT_COOLDOWN);
            if (now - last >= CRITICAL_HURT_COOLDOWN_MS) {
                getPersistentData().putLong(CRITICAL_HURT_COOLDOWN, now);
                level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_HURT_CRITICAL.get(),
                        SoundSource.HOSTILE, 1.0F, 1.0F);
            }
        }
        return hurt;
    }
}

```

## `ModSounds.java` — `src/main/java/com/carnis/mod/init/ModSounds.java`

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

## `sounds.json` — `src/main/resources/assets/carnis/sounds.json`

```json

{
  "item.inoculator.fire": {"subtitle": "carnis.subtitle.inoculator_fire", "sounds": [{"name": "carnis:item/inoculator_fire", "volume": 1.0, "pitch": 1.0, "stream": false}]},
  "entity.dart.hit": {"subtitle": "carnis.subtitle.dart_hit", "sounds": [{"name": "carnis:item/dart_hit", "volume": 0.8, "pitch": 1.0, "stream": false}]},
  "item.purifier.ignite": {"subtitle": "carnis.subtitle.purifier_ignite", "sounds": [{"name": "carnis:item/purifier_ignite", "volume": 1.0, "pitch": 1.0}]},
  "item.purifier.loop": {"subtitle": "carnis.subtitle.purifier_loop", "sounds": [{"name": "carnis:item/purifier_loop", "volume": 1.0, "pitch": 1.0, "stream": true}]},
  "flamethrower_fire": {"subtitle": "carnis.subtitle.flamethrower_fire", "sounds": [{"name": "carnis:entity/flamethrower_fire", "stream": false}]},
  "amalgam_smash": {"subtitle": "carnis.subtitle.amalgam_smash", "sounds": ["carnis:entity/amalgam_smash"]},
  "organic_creak": {"subtitle": "carnis.subtitle.organic_creak", "sounds": [{"name": "carnis:entity/organic_creak"}]},
  "amalgam_roar": {"subtitle": "carnis.subtitle.amalgam_roar", "sounds": [{"name": "carnis:entity/amalgam_roar", "volume": 1.0, "pitch": 0.75}]},
  "heartbeat_loop": {"subtitle": "carnis.subtitle.heartbeat_loop", "sounds": [{"name": "carnis:block/heartbeat_loop", "stream": true}]},
  "hive_heartbeat": {"subtitle": "carnis.subtitle.hive_heartbeat", "sounds": [{"name": "carnis:block/hive_heartbeat"}]},
  "amalgam_step": {"subtitle": "carnis.subtitle.amalgam_step", "sounds": [{"name": "carnis:entity/amalgam_step"}]},
  "phantom_creeper": {"subtitle": "carnis.subtitle.phantom_creeper", "sounds": [{"name": "carnis:hallucination/phantom_creeper", "volume": 1.0, "pitch": 1.0, "stream": false}]},
  "phantom_footsteps": {"subtitle": "carnis.subtitle.phantom_footsteps", "sounds": [{"name": "carnis:hallucination/phantom_footsteps"}]},
  "phantom_whisper": {"subtitle": "carnis.subtitle.phantom_whisper", "sounds": [{"name": "carnis:hallucination/phantom_whisper", "volume": 1.0, "pitch": 1.0, "stream": false}]},
  "pulsing_heart_beat": {"subtitle": "carnis.subtitle.pulsing_heart_beat", "sounds": ["carnis:block/heart_pulse"]},
  "synapse_shock": {"subtitle": "carnis.subtitle.synapse_shock", "sounds": [{"name": "carnis:block/nervous_twitch", "pitch": 1.2}]},
  "synapse_rupture": {"subtitle": "carnis.subtitle.synapse_rupture", "sounds": [{"name": "carnis:block/synapse_rupture", "pitch": 1.0}]},
  "digestor_churn": {"subtitle": "carnis.subtitle.digestor_churn", "sounds": [{"name": "carnis:block/digestor_churn", "volume": 0.9, "pitch": 1.0, "stream": false}]},
  "hive_eye_screech": {"subtitle": "carnis.subtitle.hive_eye_screech", "sounds": [{"name": "carnis:block/hive_eye_screech", "volume": 1.0, "pitch": 1.0, "stream": false}]},
  "hive_alarm": {"subtitle": "carnis.subtitle.hive_alarm", "sounds": [{"name": "carnis:block/hive_alarm", "volume": 1.0, "pitch": 0.9, "stream": false}]},
  "hive_ambient": {"subtitle": "carnis.subtitle.hive_ambient", "sounds": [{"name": "carnis:amb/hive_ambient_01", "stream": true, "pitch": 0.9}, {"name": "carnis:amb/hive_ambient_02", "stream": true, "pitch": 1.0}, {"name": "carnis:amb/hive_ambient_03", "stream": true, "pitch": 1.1}]},
  "hive_ambient_close": {"subtitle": "carnis.subtitle.hive_ambient_close", "sounds": [{"name": "carnis:amb/hive_ambient_close_01", "stream": true, "pitch": 0.95}, {"name": "carnis:amb/hive_ambient_close_02", "stream": true, "pitch": 1.05}]},
  "hive_pulse": {"subtitle": "carnis.subtitle.hive_pulse", "sounds": [{"name": "carnis:amb/hive_pulse_01", "stream": false, "pitch": 0.9}, {"name": "carnis:amb/hive_pulse_02", "stream": false, "pitch": 1.0}, {"name": "carnis:amb/hive_pulse_03", "stream": false, "pitch": 1.1}]},
  "hive_ambient_tonal_stinger": {"subtitle": "carnis.subtitle.hive_ambient_tonal_stinger", "sounds": [{"name": "carnis:amb/hive_ambient_tonal_stinger", "stream": false}]},
  "flesh_block_step": {"subtitle": "carnis.subtitle.flesh_block_step", "sounds": [{"name": "carnis:flesh/flesh_block_step_01", "pitch": 0.9}, {"name": "carnis:flesh/flesh_block_step_02", "pitch": 1.0}, {"name": "carnis:flesh/flesh_block_step_03", "pitch": 1.1}]},
  "hive.block.place": {"subtitle": "carnis.subtitle.hive_block_place", "sounds": [{"name": "carnis:block/hive_block_place_01_soft", "pitch": 0.9}, {"name": "carnis:block/hive_block_place_02_dense", "pitch": 1.0}, {"name": "carnis:block/hive_block_place_03_wet", "pitch": 1.1}]},
  "hive.block.break": {"subtitle": "carnis.subtitle.hive_block_break", "sounds": [{"name": "carnis:block/hive_block_break_01_tear", "pitch": 0.9}, {"name": "carnis:block/hive_block_break_02_pop", "pitch": 1.0}, {"name": "carnis:block/hive_block_break_03_crunch", "pitch": 1.1}]},
  "hive.spread": {"subtitle": "carnis.subtitle.hive_spread", "sounds": [{"name": "carnis:hive/hive_spread_01_creep", "pitch": 0.9}, {"name": "carnis:hive/hive_spread_02_pulse", "pitch": 1.0}, {"name": "carnis:hive/hive_spread_03_swell", "pitch": 1.1}]},
  "combat.flesh_hit": {"subtitle": "carnis.subtitle.combat_flesh_hit", "sounds": [{"name": "carnis:combat/combat_flesh_hit_01", "pitch": 0.9, "weight": 1}, {"name": "carnis:combat/combat_flesh_hit_02", "pitch": 1.0, "weight": 1}, {"name": "carnis:combat/combat_flesh_hit_03", "pitch": 1.1, "weight": 1}]},
  "combat.flesh_hit_deep": {"subtitle": "carnis.subtitle.combat_flesh_hit_deep", "sounds": [{"name": "carnis:combat/combat_flesh_hit_deep_01_axe", "pitch": 0.9, "weight": 1}, {"name": "carnis:combat/combat_flesh_hit_deep_02_crit", "pitch": 1.0, "weight": 1}, {"name": "carnis:combat/combat_flesh_hit_deep_03_blast", "pitch": 1.1, "weight": 1}]},
  "combat.dismember": {"subtitle": "carnis.subtitle.combat_dismember", "sounds": [{"name": "carnis:combat/dismember_01", "pitch": 0.85, "weight": 1}, {"name": "carnis:combat/dismember_02", "pitch": 0.92, "weight": 1}, {"name": "carnis:combat/dismember_03", "pitch": 1.0, "weight": 1}, {"name": "carnis:combat/dismember_04", "pitch": 1.08, "weight": 1}, {"name": "carnis:combat/dismember_05", "pitch": 1.15, "weight": 1}]},
  "combat.armor_deflect": {"subtitle": "carnis.subtitle.combat_armor_deflect", "sounds": [{"name": "carnis:combat/combat_deflect_01_chitin", "pitch": 0.85, "weight": 1}, {"name": "carnis:combat/combat_deflect_02_bone", "pitch": 0.92, "weight": 1}, {"name": "carnis:combat/combat_deflect_03_metal", "pitch": 1.0, "weight": 1}, {"name": "carnis:combat/combat_deflect_04_glance", "pitch": 1.08, "weight": 1}, {"name": "carnis:combat/combat_deflect_05_parry", "pitch": 1.15, "weight": 1}]},
  "combat.block_stab": {"subtitle": "carnis.subtitle.combat_block_stab", "sounds": [{"name": "carnis:combat/combat_stab_01_bone", "pitch": 0.9, "weight": 1}, {"name": "carnis:combat/combat_stab_02_chitin", "pitch": 1.0, "weight": 1}, {"name": "carnis:combat/combat_stab_03_shield", "pitch": 1.1, "weight": 1}]},
  "hive.detail.flow": {"subtitle": "carnis.subtitle.hive_detail_flow", "sounds": [{"name": "carnis:hive/detail_flow_01", "pitch": 0.95}, {"name": "carnis:hive/detail_flow_02", "pitch": 1.05}]},
  "hive.detail.membrane": {"subtitle": "carnis.subtitle.hive_detail_membrane", "sounds": [{"name": "carnis:hive/detail_membrane_01"}]},
  "hive.detail.bubbles": {"subtitle": "carnis.subtitle.hive_detail_bubbles", "sounds": [{"name": "carnis:hive/detail_bubbles_01"}]},
  "hive.detail.creak": {"subtitle": "carnis.subtitle.hive_detail_creak", "sounds": [{"name": "carnis:hive/detail_creak_01"}]},
  "hive.detail.scuttle": {"subtitle": "carnis.subtitle.hive_detail_scuttle", "sounds": [{"name": "carnis:hive/detail_scuttle_01"}]},
  "hive.spawn.alert": {"subtitle": "carnis.subtitle.hive_spawn_alert", "sounds": [{"name": "carnis:hive/hive_spawn_alert_01", "pitch": 0.88}, {"name": "carnis:hive/hive_spawn_alert_02", "pitch": 0.96}, {"name": "carnis:hive/hive_spawn_alert_03", "pitch": 1.04}, {"name": "carnis:hive/hive_spawn_alert_04", "pitch": 1.12}]},
  "hive.spawn.attack": {"subtitle": "carnis.subtitle.hive_spawn_attack", "sounds": [{"name": "carnis:hive/hive_spawn_attack_01", "pitch": 0.88}, {"name": "carnis:hive/hive_spawn_attack_02", "pitch": 0.96}, {"name": "carnis:hive/hive_spawn_attack_03", "pitch": 1.04}, {"name": "carnis:hive/hive_spawn_attack_04", "pitch": 1.12}]},
  "hive.spawn.idle": {"subtitle": "carnis.subtitle.hive_spawn_idle", "sounds": [{"name": "carnis:hive/hive_spawn_idle_01", "pitch": 0.88}, {"name": "carnis:hive/hive_spawn_idle_02", "pitch": 0.96}, {"name": "carnis:hive/hive_spawn_idle_03", "pitch": 1.04}, {"name": "carnis:hive/hive_spawn_idle_04", "pitch": 1.12}]},
  "hive.spawn.hurt": {"subtitle": "carnis.subtitle.hive_spawn_hurt", "sounds": [{"name": "carnis:hive/hive_spawn_hurt_01", "pitch": 0.88}, {"name": "carnis:hive/hive_spawn_hurt_02", "pitch": 0.96}, {"name": "carnis:hive/hive_spawn_hurt_03", "pitch": 1.04}, {"name": "carnis:hive/hive_spawn_hurt_04", "pitch": 1.12}]},
  "hive.spawn.hurt_critical": {"subtitle": "carnis.subtitle.hive_spawn_hurt_critical", "sounds": [{"name": "carnis:hive/hive_spawn_hurt_critical_01", "pitch": 0.90}, {"name": "carnis:hive/hive_spawn_hurt_critical_02", "pitch": 0.95}, {"name": "carnis:hive/hive_spawn_hurt_critical_03", "pitch": 1.00}, {"name": "carnis:hive/hive_spawn_hurt_critical_04", "pitch": 1.05}]},
  "hive.spawn.death": {"subtitle": "carnis.subtitle.hive_spawn_death", "sounds": [{"name": "carnis:hive/hive_spawn_death_01", "pitch": 0.88}, {"name": "carnis:hive/hive_spawn_death_02", "pitch": 0.96}, {"name": "carnis:hive/hive_spawn_death_03", "pitch": 1.04}, {"name": "carnis:hive/hive_spawn_death_04", "pitch": 1.12}]},
  "hive.spawn.skeleton_whip": {"subtitle": "carnis.subtitle.hive_spawn_skeleton_whip", "sounds": [{"name": "carnis:hive/spawn_skeleton_whip_01", "pitch": 0.92, "weight": 1}, {"name": "carnis:hive/spawn_skeleton_whip_02", "pitch": 1.0, "weight": 1}, {"name": "carnis:hive/spawn_skeleton_whip_03", "pitch": 1.08, "weight": 1}]},
  "hive.spawn.skeleton_blade": {"subtitle": "carnis.subtitle.hive_spawn_skeleton_blade", "sounds": [{"name": "carnis:hive/spawn_skeleton_blade_01", "pitch": 0.92, "weight": 1}, {"name": "carnis:hive/spawn_skeleton_blade_02", "pitch": 1.0, "weight": 1}, {"name": "carnis:hive/spawn_skeleton_blade_03", "pitch": 1.08, "weight": 1}]},
  "hive.spawn.skeleton_bonecrack": {"subtitle": "carnis.subtitle.hive_spawn_skeleton_bonecrack", "sounds": [{"name": "carnis:hive/spawn_skeleton_bonecrack_01", "pitch": 0.95, "weight": 1}, {"name": "carnis:hive/spawn_skeleton_bonecrack_02", "pitch": 1.05, "weight": 1}]},
  "creeper_rupture": {"subtitle": "carnis.subtitle.creeper_rupture", "sounds": [{"name": "carnis:block/creeper_rupture", "pitch": 0.9, "volume": 1.0}]},
  "amalgamation_fuse": {"subtitle": "carnis.subtitle.amalgamation_fuse", "sounds": [{"name": "carnis:entity/amalgamation_fuse", "volume": 1.1, "pitch": 1.0, "stream": false}]},
  "bone_deflect": {"subtitle": "carnis.subtitle.bone_deflect", "sounds": [{"name": "carnis:block/bone_deflect"}]},
  "acid_splash": {"subtitle": "carnis.subtitle.acid_splash", "sounds": [{"name": "carnis:entity/acid_splash", "volume": 1.0, "pitch": 1.0, "stream": false}]},
  "pustule_burst": {"subtitle": "carnis.subtitle.pustule_burst", "sounds": ["carnis:block/pustule_burst"]},
  "flesh_amalgam_ambient": {"subtitle": "carnis.subtitle.flesh_amalgam_ambient", "sounds": [{"name": "carnis:entity/flesh_amalgam_ambient", "volume": 1.0, "pitch": 1.0, "stream": false}]},
  "flesh_amalgam_hurt": {"subtitle": "carnis.subtitle.flesh_amalgam_hurt", "sounds": [{"name": "carnis:entity/flesh_amalgam_hurt", "volume": 1.0, "pitch": 1.0, "stream": false}]},
  "flesh_amalgam_death": {"subtitle": "carnis.subtitle.flesh_amalgam_death", "sounds": [{"name": "carnis:entity/flesh_amalgam_death", "volume": 1.1, "pitch": 1.0, "stream": false}]},
  "ambient.hive.surface": {"subtitle": "carnis.subtitle.amb_hive_surface", "sounds": [{"name": "carnis:hive/amb_surface", "stream": true}]},
  "ambient.hive.deep": {"subtitle": "carnis.subtitle.amb_hive_deep", "sounds": [{"name": "carnis:hive/amb_deep", "stream": true}]},
  "ambient.hive.core": {"subtitle": "carnis.subtitle.amb_hive_core", "sounds": [{"name": "carnis:hive/amb_core", "stream": true}]},
  "ambient.hive.threshold": {"subtitle": "carnis.subtitle.amb_hive_threshold", "sounds": [{"name": "carnis:hive/amb_threshold", "stream": true}]},
  "zone.stinger.intensify": {"subtitle": "carnis.subtitle.zone_stinger_intensify", "sounds": [{"name": "carnis:hive/zone_stinger_intensify", "volume": 0.65, "pitch": 1.0}]},
  "zone.stinger.release": {"subtitle": "carnis.subtitle.zone_stinger_release", "sounds": [{"name": "carnis:hive/zone_stinger_release", "volume": 0.65, "pitch": 1.0}]},
  "zone.stinger.deep": {"subtitle": "carnis.subtitle.zone_stinger_deep", "sounds": [{"name": "carnis:hive/zone_stinger_deep", "volume": 0.65, "pitch": 1.0}]}
}

```

## `en_us.json` — `src/main/resources/assets/carnis/lang/en_us.json`

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
  "carnis.subtitle.zone_stinger_deep": "Descending into the hive"
}

```

## `ru_ru.json` — `src/main/resources/assets/carnis/lang/ru_ru.json`

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
  "carnis.subtitle.zone_stinger_deep": "Погружение в улей"
}

```

## `ModEntities.java` — `src/main/java/com/carnis/mod/init/ModEntities.java`

```java

package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;

import com.carnis.mod.entity.ViralDartEntity;
import com.carnis.mod.entity.PurificationDartEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, CarnisMod.MOD_ID);

    public static final RegistryObject<EntityType<com.carnis.mod.entity.HiveSentinelEntity>> HIVE_SENTINEL = ENTITY_TYPES.register(
            "hive_sentinel", () -> EntityType.Builder.<com.carnis.mod.entity.HiveSentinelEntity>of(
                    com.carnis.mod.entity.HiveSentinelEntity::new, MobCategory.MONSTER)
                    .sized(0.9F, 1.8F).clientTrackingRange(8).build("carnis:hive_sentinel"));
    public static final RegistryObject<EntityType<com.carnis.mod.entity.CerebralNexusEntity>> CEREBRAL_NEXUS = ENTITY_TYPES.register(
            "cerebral_nexus", () -> EntityType.Builder.<com.carnis.mod.entity.CerebralNexusEntity>of(
                    com.carnis.mod.entity.CerebralNexusEntity::new, MobCategory.MONSTER)
                    .sized(1.3F, 2.2F).clientTrackingRange(10).build("carnis:cerebral_nexus"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.ParasiticTendrilEntity>> PARASITIC_TENDRIL = ENTITY_TYPES.register(
            "parasitic_tendril", () -> EntityType.Builder.<com.carnis.mod.entity.ParasiticTendrilEntity>of(
                    com.carnis.mod.entity.ParasiticTendrilEntity::new, MobCategory.MONSTER)
                    .sized(0.5F, 1.2F).clientTrackingRange(8).build("carnis:parasitic_tendril"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.BiomassMaggotEntity>> BIOMASS_MAGGOT =
            ENTITY_TYPES.register("biomass_maggot", () -> EntityType.Builder
                    .<com.carnis.mod.entity.BiomassMaggotEntity>of(com.carnis.mod.entity.BiomassMaggotEntity::new, MobCategory.MONSTER)
                    .sized(0.55F, 0.35F).clientTrackingRange(8).build("carnis:biomass_maggot"));

    public static final RegistryObject<EntityType<InfectedZombieEntity>> INFECTED_ZOMBIE = ENTITY_TYPES.register(
            "infected_zombie", () -> EntityType.Builder.<InfectedZombieEntity>of(InfectedZombieEntity::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.95F).clientTrackingRange(8).build("carnis:infected_zombie"));

    public static final RegistryObject<EntityType<InfectedSkeletonEntity>> INFECTED_SKELETON = ENTITY_TYPES.register(
            "infected_skeleton", () -> EntityType.Builder.<InfectedSkeletonEntity>of(InfectedSkeletonEntity::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.99F).clientTrackingRange(8).build("carnis:infected_skeleton"));
    public static final RegistryObject<EntityType<InfectedCreeperEntity>> INFECTED_CREEPER = ENTITY_TYPES.register(
            "infected_creeper", () -> EntityType.Builder.<InfectedCreeperEntity>of(InfectedCreeperEntity::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.7F).clientTrackingRange(8).build("carnis:infected_creeper"));
    public static final RegistryObject<EntityType<InfectedSpiderEntity>> INFECTED_SPIDER = ENTITY_TYPES.register(
            "infected_spider", () -> EntityType.Builder.<InfectedSpiderEntity>of(InfectedSpiderEntity::new, MobCategory.MONSTER)
                    .sized(1.4F, 0.9F).clientTrackingRange(8).build("carnis:infected_spider"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.FleshSpatProjectileEntity>> FLESH_SPAT = ENTITY_TYPES.register(
            "flesh_spat", () -> EntityType.Builder.<com.carnis.mod.entity.FleshSpatProjectileEntity>of(
                    com.carnis.mod.entity.FleshSpatProjectileEntity::new, MobCategory.MISC)
                    .sized(0.25F, 0.25F).clientTrackingRange(4).updateInterval(1).build("carnis:flesh_spat"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.AmalgamBileProjectile>> AMALGAM_BILE = ENTITY_TYPES.register(
            "amalgam_bile", () -> EntityType.Builder.<com.carnis.mod.entity.AmalgamBileProjectile>of(
                    com.carnis.mod.entity.AmalgamBileProjectile::new, MobCategory.MISC)
                    .sized(0.25F, 0.25F).clientTrackingRange(8).updateInterval(1).build("carnis:amalgam_bile"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.HiveSporeCloudEntity>> HIVE_SPORE_CLOUD = ENTITY_TYPES.register(
            "hive_spore_cloud", () -> EntityType.Builder.<com.carnis.mod.entity.HiveSporeCloudEntity>of(
                    com.carnis.mod.entity.HiveSporeCloudEntity::new, MobCategory.MISC)
                    .sized(6F, 0.5F).clientTrackingRange(10).updateInterval(10).build("carnis:hive_spore_cloud"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.projectile.InoculatorDartEntity>> INOCULATOR_DART = ENTITY_TYPES.register(
            "inoculator_dart", () -> EntityType.Builder.<com.carnis.mod.entity.projectile.InoculatorDartEntity>of(
                    com.carnis.mod.entity.projectile.InoculatorDartEntity::new, MobCategory.MISC)
                    .sized(0.5F, 0.5F).clientTrackingRange(8).updateInterval(1).build("carnis:inoculator_dart"));

    public static final RegistryObject<EntityType<ViralDartEntity>> VIRAL_DART = ENTITY_TYPES.register(
            "viral_dart", () -> EntityType.Builder.<ViralDartEntity>of(ViralDartEntity::new, MobCategory.MISC)
                    .sized(0.5F, 0.5F).clientTrackingRange(4).updateInterval(1).build("carnis:viral_dart"));
    public static final RegistryObject<EntityType<PurificationDartEntity>> PURIFICATION_DART = ENTITY_TYPES.register(
            "purification_dart", () -> EntityType.Builder.<PurificationDartEntity>of(PurificationDartEntity::new, MobCategory.MISC)
                    .sized(0.5F, 0.5F).clientTrackingRange(4).updateInterval(1).build("carnis:purification_dart"));

    public static final RegistryObject<EntityType<FleshAmalgamEntity>>
            FLESH_AMALGAM = ENTITY_TYPES.register(
                    "flesh_amalgam",
                    () -> EntityType.Builder.of(
                                    FleshAmalgamEntity::new,
                                    MobCategory.MONSTER
                            )
                            .sized(1.4F, 2.75F)
                            .clientTrackingRange(10)
                            .updateInterval(3)
                            .build(new ResourceLocation(
                                    CarnisMod.MOD_ID,
                                    "flesh_amalgam"
                            ).toString())
            );

    /** Register this method from the existing MOD-bus ModEntityEvents subscriber. */
    public static void registerSpawnPlacements(SpawnPlacementRegisterEvent event) {
        event.register(PARASITIC_TENDRIL.get(), SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, ModEntities::canSpawnTendril,
                SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(INFECTED_ZOMBIE.get(), SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, ModEntities::canSpawnInfectedZombie,
                SpawnPlacementRegisterEvent.Operation.REPLACE);
    }

    public static boolean canSpawnTendril(
            EntityType<com.carnis.mod.entity.ParasiticTendrilEntity> type,
            ServerLevelAccessor level, MobSpawnType reason, BlockPos pos, RandomSource random) {
        long dayTime = Math.floorMod(level.getLevel().getDayTime(), 24000L);
        return dayTime >= 13000L && dayTime < 23000L
                && level.getMaxLocalRawBrightness(pos) <= 7
                && level.getBlockState(pos.below()).is(BlockTags.ANIMALS_SPAWNABLE_ON);
    }

    public static boolean canSpawnInfectedZombie(
            EntityType<com.carnis.mod.entity.InfectedZombieEntity> type,
            ServerLevelAccessor level, MobSpawnType reason, BlockPos pos, RandomSource random) {
        if (level.getMaxLocalRawBrightness(pos) > 7) return false;
        if (!level.getBlockState(pos.below()).isSolidRender(level, pos.below())) return false;
        return com.carnis.mod.event.ChunkInfectionEvents.infectedChunk(
                level.getLevel(), new net.minecraft.world.level.ChunkPos(pos));
    }

    private ModEntities() {
    }

    public static void register(IEventBus modEventBus) {
        ENTITY_TYPES.register(modEventBus);
    }
}

```

## `ModEntityEvents.java` — `src/main/java/com/carnis/mod/event/ModEntityEvents.java`

```java

package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;

import com.carnis.mod.init.ModEntities;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.MOD
)
public final class ModEntityEvents {
    private ModEntityEvents() {
    }

    @SubscribeEvent
    public static void onSpawnPlacements(net.minecraftforge.event.entity.SpawnPlacementRegisterEvent event) {
        ModEntities.registerSpawnPlacements(event);
    }

    @SubscribeEvent
    public static void onCreateEntityAttributes(
            EntityAttributeCreationEvent event
    ) {
        event.put(ModEntities.HIVE_SENTINEL.get(), com.carnis.mod.entity.HiveSentinelEntity.createAttributes().build());
        event.put(ModEntities.CEREBRAL_NEXUS.get(), com.carnis.mod.entity.CerebralNexusEntity.createAttributes().build());
        event.put(ModEntities.BIOMASS_MAGGOT.get(), com.carnis.mod.entity.BiomassMaggotEntity.createAttributes().build());
        event.put(ModEntities.PARASITIC_TENDRIL.get(), com.carnis.mod.entity.ParasiticTendrilEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_ZOMBIE.get(), InfectedZombieEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_SKELETON.get(), InfectedSkeletonEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_CREEPER.get(), InfectedCreeperEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_SPIDER.get(), InfectedSpiderEntity.createAttributes().build());

        event.put(
                ModEntities.FLESH_AMALGAM.get(),
                FleshAmalgamEntity.createAttributes().build()
        );
    }
}

```

## `infected_skeleton.animation.json` — `src/main/resources/assets/carnis/animations/entity/infected_skeleton.animation.json`

```json

{
  "format_version": "1.8.0",
  "animations": {
    "animation.infected_skeleton.idle": {
      "loop": true,
      "animation_length": 0.8,
      "bones": {
        "ribs": {
          "rotation": {
            "0.0": [
              0,
              0,
              -1
            ],
            "0.2": [
              1,
              0,
              1
            ],
            "0.4": [
              0,
              0,
              -1
            ],
            "0.6": [
              -1,
              0,
              1
            ],
            "0.8": [
              0,
              0,
              -1
            ]
          }
        },
        "head": {
          "rotation": {
            "0.0": [
              0,
              0,
              1
            ],
            "0.4": [
              0,
              0,
              -1
            ],
            "0.8": [
              0,
              0,
              1
            ]
          }
        },
        "neural_filaments": {
          "rotation": {
            "0.0": [
              0,
              0,
              -3
            ],
            "0.4": [
              4,
              0,
              4
            ],
            "0.8": [
              0,
              0,
              -3
            ]
          }
        }
      }
    },
    "animation.infected_skeleton.walk": {
      "loop": true,
      "animation_length": 0.4,
      "bones": {
        "body": {
          "rotation": {
            "0.0": [
              8,
              0,
              -4
            ],
            "0.1": [
              10,
              0,
              2
            ],
            "0.2": [
              8,
              0,
              4
            ],
            "0.3": [
              10,
              0,
              -2
            ],
            "0.4": [
              8,
              0,
              -4
            ]
          }
        },
        "head": {
          "rotation": {
            "0.0": [
              -3,
              0,
              3
            ],
            "0.2": [
              -3,
              0,
              -3
            ],
            "0.4": [
              -3,
              0,
              3
            ]
          }
        },
        "left_leg": {
          "rotation": {
            "0.0": [
              40,
              0,
              0
            ],
            "0.2": [
              -40,
              0,
              0
            ],
            "0.4": [
              40,
              0,
              0
            ]
          }
        },
        "right_leg": {
          "rotation": {
            "0.0": [
              -40,
              0,
              0
            ],
            "0.2": [
              40,
              0,
              0
            ],
            "0.4": [
              -40,
              0,
              0
            ]
          }
        },
        "left_arm": {
          "rotation": {
            "0.0": [
              -25,
              0,
              0
            ],
            "0.2": [
              25,
              0,
              0
            ],
            "0.4": [
              -25,
              0,
              0
            ]
          }
        },
        "right_arm": {
          "rotation": {
            "0.0": [
              25,
              0,
              0
            ],
            "0.2": [
              -25,
              0,
              0
            ],
            "0.4": [
              25,
              0,
              0
            ]
          }
        }
      }
    },
    "animation.infected_skeleton.heartbeat": {
      "loop": true,
      "animation_length": 0.8,
      "bones": {
        "heart": {
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.1": [
              1.2,
              1.25,
              1.2
            ],
            "0.2": [
              1,
              1,
              1
            ],
            "0.32": [
              1.13,
              1.16,
              1.13
            ],
            "0.44": [
              1,
              1,
              1
            ],
            "0.8": [
              1,
              1,
              1
            ]
          }
        }
      }
    },
    "animation.infected_skeleton.attack_whirlwind": {
      "loop": false,
      "animation_length": 0.25,
      "bones": {
        "body": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.0625": [
              0,
              90,
              0
            ],
            "0.125": [
              0,
              180,
              0
            ],
            "0.1875": [
              0,
              270,
              0
            ],
            "0.25": [
              0,
              360,
              0
            ]
          }
        },
        "right_arm": {
          "rotation": {
            "0.0": [
              -30,
              0,
              -55
            ],
            "0.0625": [
              -55,
              0,
              -75
            ],
            "0.1875": [
              -55,
              0,
              -75
            ],
            "0.25": [
              0,
              0,
              0
            ]
          }
        }
      }
    },
    "animation.infected_skeleton.assimilate": {
      "loop": true,
      "animation_length": 0.6,
      "bones": {
        "body": {
          "rotation": [
            16,
            0,
            -3
          ]
        },
        "heart": {
          "scale": {
            "0": [
              1,
              1,
              1
            ],
            "0.15": [
              1.2,
              1.2,
              1.2
            ],
            "0.3": [
              1,
              1,
              1
            ],
            "0.6": [
              1,
              1,
              1
            ]
          }
        },
        "right_arm": {
          "rotation": [
            20,
            0,
            5
          ]
        },
        "left_arm": {
          "rotation": [
            20,
            0,
            -5
          ]
        },
        "right_leg": {
          "rotation": [
            0,
            0,
            0
          ]
        },
        "left_leg": {
          "rotation": [
            0,
            0,
            0
          ]
        }
      }
    },
    "animation.infected_skeleton.attack_scythe": {
      "loop": false,
      "animation_length": 0.65,
      "bones": {
        "body": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            ".18": [
              0,
              -24,
              -6
            ],
            ".38": [
              0,
              28,
              5
            ],
            ".65": [
              0,
              0,
              0
            ]
          }
        },
        "right_arm": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            ".18": [
              -70,
              -30,
              -35
            ],
            ".38": [
              20,
              45,
              25
            ],
            ".65": [
              0,
              0,
              0
            ]
          }
        }
      }
       ,"animation.infected_skeleton.attack_whip": {
        "loop": false,
        "animation_length": 0.45,
        "bones": {
          "body": {
            "rotation": {
              "0.0": [0, 0, 0],
              "0.1": [0, -12, -4],
              "0.22": [0, 16, 4],
              "0.45": [0, 0, 0]
            }
          },
          "right_arm": {
            "rotation": {
              "0.0": [0, 0, 0],
              "0.1": [-35, 0, -15],
              "0.22": [-15, 0, -35],
              "0.45": [0, 0, 0]
            },
            "scale": {
              "0.0": [1, 1, 1],
              "0.1": [1, 1.2, 1],
              "0.22": [1, 2.8, 1],
              "0.3": [1, 1.4, 1],
              "0.45": [1, 1, 1]
            }
          }
        }
      }
    }
  }
}

```

## `gradle.properties` — `gradle.properties`

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
mod_version=3.4.4
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
