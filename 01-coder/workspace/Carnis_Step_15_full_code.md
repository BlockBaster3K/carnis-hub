# Шаг 15 — полный код Амальгамы и интеграция

Файлы целиком, без сокращений; PNG и OGG хранятся в проекте.

## `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.ai.FleshAmalgamChargeGoal;
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

public final class FleshAmalgamEntity extends Monster
        implements GeoEntity, HivemindLinkedMob {
    @Override
    protected void playStepSound(net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState state) {
        playSound(ModSounds.AMALGAM_STEP.get(), 0.9F, 0.85F + getRandom().nextFloat() * 0.2F);
    }

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
                new HurtByTargetGoal(this).setAlertOthers()
        );
        targetSelector.addGoal(
                2,
                new NearestAttackableTargetGoal<>(
                        this,
                        Player.class,
                        true,
                        target -> target instanceof Player player
                                && PlayerInfectionApi.isHostileTarget(player)
                )
        );
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (
                target instanceof Player player
                        && PlayerInfectionApi.isAssimilated(player)
        ) {
            return false;
        }

        return super.canAttack(target);
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
        biomassFeast.tick(server);
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
                SoundEvents.SHIELD_BLOCK, SoundSource.HOSTILE, 1.0F, 0.9F);
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
                0.9F + getRandom().nextFloat() * 0.2F
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
                0.92F + getRandom().nextFloat() * 0.16F
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
        if (!level().isClientSide) triggerAnim("roar_controller", "roar");
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.FLESH_AMALGAM_AMBIENT.get();
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
        if (ability == SLAM) boss.triggerAnim("slam_controller", "slam");
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
        level.playSound(null, boss.blockPosition(), ModSounds.AMALGAM_SMASH.get(), SoundSource.HOSTILE, 2.0F, 0.85F);
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
        level.playSound(null, boss.blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1.25F, .72F);
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
        boss.triggerAnim("roar_controller", "roar");
        level.playSound(null, boss.blockPosition(), ModSounds.AMALGAM_ROAR.get(), SoundSource.HOSTILE, 1.5F, .7F);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), from.x, from.y + .2D, from.z, 20, .35D, .35D, .35D, .04D);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), boss.getX(), boss.getY(.6D), boss.getZ(),
                30, boss.getBbWidth() * .35D, boss.getBbHeight() * .3D, boss.getBbWidth() * .35D, .06D);
    }
}
```

## `src/main/java/com/carnis/mod/entity/AmalgamBileProjectile.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.network.NetworkHooks;

public final class AmalgamBileProjectile extends ThrowableItemProjectile {
    public AmalgamBileProjectile(EntityType<? extends AmalgamBileProjectile> type, Level level) { super(type, level); }
    public AmalgamBileProjectile(Level level, LivingEntity owner) { super(ModEntities.AMALGAM_BILE.get(), owner, level); }
    @Override protected Item getDefaultItem() { return ModItems.AMALGAM_BILE_GLOB.get(); }
    @Override protected boolean canHitEntity(Entity entity) {
        return super.canHitEntity(entity) && !NeuroArmorEventHandler.isHiveEntity(entity)
                && (!(entity instanceof Player player) || !player.isCreative() && !player.isSpectator());
    }
    @Override public void tick() {
        super.tick();
        if (level().isClientSide && !isRemoved()) level().addParticle(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), 0, .01D, 0);
        if (!level().isClientSide && tickCount > 120) discard();
    }
    @Override protected void onHitEntity(EntityHitResult hit) {
        super.onHitEntity(hit);
        if (!(level() instanceof ServerLevel level) || !(hit.getEntity() instanceof LivingEntity target)) return;
        if (target.hurt(level.damageSources().thrown(this, getOwner()), 5.0F))
            target.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 0));
    }
    @Override protected void onHit(HitResult hit) {
        super.onHit(hit);
        if (level() instanceof ServerLevel level) {
            level.playSound(null, blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, .6F, 1.1F);
            level.sendParticles(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), 14, .2D, .2D, .2D, .04D);
            discard();
        }
    }
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket() { return NetworkHooks.getEntitySpawningPacket(this); }
}
```

## `src/main/java/com/carnis/mod/client/model/FleshAmalgamModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import software.bernie.geckolib.model.GeoModel;

@OnlyIn(Dist.CLIENT)
public final class FleshAmalgamModel extends GeoModel<FleshAmalgamEntity> {
    @Override public ResourceLocation getModelResource(FleshAmalgamEntity entity) {
        return new ResourceLocation("carnis", "geo/entity/flesh_amalgam.geo.json");
    }
    @Override public ResourceLocation getTextureResource(FleshAmalgamEntity entity) {
        return new ResourceLocation("carnis", "textures/entity/flesh_amalgam.png");
    }
    @Override public ResourceLocation getAnimationResource(FleshAmalgamEntity entity) {
        return new ResourceLocation("carnis", "animations/entity/flesh_amalgam.animation.json");
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/FleshAmalgamRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.FleshAmalgamModel;
import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;

@OnlyIn(Dist.CLIENT)
public final class FleshAmalgamRenderer
        extends GeoEntityRenderer<FleshAmalgamEntity> {
    public FleshAmalgamRenderer(EntityRendererProvider.Context context) {
        super(context, new FleshAmalgamModel());
        this.shadowRadius = 0.85F;
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/FleshAmalgamChargeGoal.java`

```java
package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * RANGED adaptation countermeasure: when its target keeps distance, the
 * Amalgam abandons ordinary pathing for one bounded ballistic charge.
 */
public final class FleshAmalgamChargeGoal extends Goal {
    private static final double TRIGGER_DISTANCE_SQUARED =
            FleshAmalgamEntity.CHARGE_TRIGGER_DISTANCE
                    * FleshAmalgamEntity.CHARGE_TRIGGER_DISTANCE;
    private static final double MIN_HORIZONTAL_VECTOR_SQUARED = 1.0E-6D;

    private static final double BASE_HORIZONTAL_SPEED = 1.15D;
    private static final double SPEED_PER_ADAPTATION_LEVEL = 0.008D;
    private static final double MAX_HORIZONTAL_SPEED = 1.55D;
    private static final double VERTICAL_SPEED = 0.52D;

    private static final int BASE_COOLDOWN_TICKS = 90;
    private static final int MIN_COOLDOWN_TICKS = 35;
    private static final int MAX_AIRBORNE_TICKS = 20;

    private final FleshAmalgamEntity amalgam;

    private LivingEntity target;
    private long nextAllowedChargeTick;
    private int airborneTicks;

    public FleshAmalgamChargeGoal(FleshAmalgamEntity amalgam) {
        this.amalgam = amalgam;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (
                amalgam.level().getGameTime() < nextAllowedChargeTick
                        || !amalgam.onGround()
                        || amalgam.getRangedAdaptationLevel() <= 0L
        ) {
            return false;
        }

        LivingEntity currentTarget = amalgam.getTarget();

        if (
                currentTarget == null
                        || !currentTarget.isAlive()
        ) {
            return false;
        }

        double offsetX = currentTarget.getX() - amalgam.getX();
        double offsetZ = currentTarget.getZ() - amalgam.getZ();
        double horizontalDistanceSquared = offsetX * offsetX
                + offsetZ * offsetZ;

        if (
                amalgam.distanceToSqr(currentTarget)
                        <= TRIGGER_DISTANCE_SQUARED
                        || horizontalDistanceSquared
                        < MIN_HORIZONTAL_VECTOR_SQUARED
        ) {
            return false;
        }

        target = currentTarget;
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        return target != null
                && target.isAlive()
                && airborneTicks < MAX_AIRBORNE_TICKS
                && (!amalgam.onGround() || airborneTicks == 0);
    }

    @Override
    public void start() {
        if (target == null) {
            return;
        }

        Vec3 horizontalDirection = new Vec3(
                target.getX() - amalgam.getX(),
                0.0D,
                target.getZ() - amalgam.getZ()
        );

        if (
                horizontalDirection.lengthSqr()
                        < MIN_HORIZONTAL_VECTOR_SQUARED
        ) {
            target = null;
            return;
        }

        long rangedLevel = amalgam.getRangedAdaptationLevel();
        double horizontalSpeed = Math.min(
                MAX_HORIZONTAL_SPEED,
                BASE_HORIZONTAL_SPEED
                        + rangedLevel * SPEED_PER_ADAPTATION_LEVEL
        );
        int cooldownReduction = (int) Math.min(
                BASE_COOLDOWN_TICKS - MIN_COOLDOWN_TICKS,
                rangedLevel
        );

        horizontalDirection = horizontalDirection.normalize();
        amalgam.getNavigation().stop();
        amalgam.getLookControl().setLookAt(target, 30.0F, 30.0F);
        amalgam.setDeltaMovement(
                horizontalDirection.x * horizontalSpeed,
                Math.max(
                        VERTICAL_SPEED,
                        amalgam.getDeltaMovement().y
                ),
                horizontalDirection.z * horizontalSpeed
        );
        amalgam.setSprinting(true);

        nextAllowedChargeTick = amalgam.level().getGameTime()
                + BASE_COOLDOWN_TICKS
                - cooldownReduction;
        airborneTicks = 0;
    }

    @Override
    public void tick() {
        airborneTicks++;

        if (target != null) {
            amalgam.getLookControl().setLookAt(target, 30.0F, 30.0F);
        }
    }

    @Override
    public void stop() {
        amalgam.setSprinting(false);
        target = null;
        airborneTicks = 0;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/init/ModEntities.java`

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
    }

    public static boolean canSpawnTendril(
            EntityType<com.carnis.mod.entity.ParasiticTendrilEntity> type,
            ServerLevelAccessor level, MobSpawnType reason, BlockPos pos, RandomSource random) {
        long dayTime = Math.floorMod(level.getLevel().getDayTime(), 24000L);
        return dayTime >= 13000L && dayTime < 23000L
                && level.getMaxLocalRawBrightness(pos) <= 7
                && level.getBlockState(pos.below()).is(BlockTags.ANIMALS_SPAWNABLE_ON);
    }

    private ModEntities() {
    }

    public static void register(IEventBus modEventBus) {
        ENTITY_TYPES.register(modEventBus);
    }
}
```

## `src/main/java/com/carnis/mod/init/ModItems.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.item.BioPurifierItem;
import com.carnis.mod.item.NeuroResonatorArmorItem;
import net.minecraft.world.item.ArmorItem;
import com.carnis.mod.item.PneumaticInoculatorItem;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.item.PurificationSerumItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, CarnisMod.MOD_ID);

    public static final RegistryObject<Item> BIOMASS_REMAINS = ITEMS.register("biomass_remains",
            () -> new BlockItem(ModBlocks.BIOMASS_REMAINS.get(), new Item.Properties()));

    public static final RegistryObject<Item> FLESH_BULB = ITEMS.register("flesh_bulb",
            () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.FLESH_BULB.get(), new Item.Properties(), "flesh_bulb"));
    public static final RegistryObject<Item> SINEW_SPIKES = ITEMS.register("sinew_spikes",
            () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.SINEW_SPIKES.get(), new Item.Properties(), "sinew_spikes"));
    public static final RegistryObject<ForgeSpawnEggItem> BIOMASS_MAGGOT_SPAWN_EGG = ITEMS.register(
            "biomass_maggot_spawn_egg", () -> new com.carnis.mod.item.MaggotSpawnEggItem(ModEntities.BIOMASS_MAGGOT,
                    0x60202c, 0xc99d79, new Item.Properties()));

    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_ZOMBIE_SPAWN_EGG = ITEMS.register(
            "infected_zombie_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_ZOMBIE,
                    0x552d31, 0x8c9c54, new Item.Properties()));

    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_SKELETON_SPAWN_EGG = ITEMS.register(
            "infected_skeleton_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_SKELETON, 0x552d31, 0xc7b9a6, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_CREEPER_SPAWN_EGG = ITEMS.register(
            "infected_creeper_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_CREEPER, 0x552d31, 0x668b45, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_SPIDER_SPAWN_EGG = ITEMS.register(
            "infected_spider_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_SPIDER, 0x552d31, 0x654643, new Item.Properties()));

    public static final RegistryObject<net.minecraft.world.item.BucketItem> TAINTED_SLUDGE_BUCKET = ITEMS.register(
            "tainted_sludge_bucket", () -> new net.minecraft.world.item.BucketItem(ModFluids.SLUDGE_SOURCE,
                    new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1)));
    public static final RegistryObject<com.carnis.mod.item.CodexCarnisItem> RESEARCH_JOURNAL = ITEMS.register(
            "research_journal", () -> new com.carnis.mod.item.CodexCarnisItem(new Item.Properties()));
    public static final RegistryObject<Item> AMALGAM_BILE_GLOB = ITEMS.register("amalgam_bile_glob", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> FLESH_SPAT = ITEMS.register("flesh_spat", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> BONE_SCYTHE_ARM = ITEMS.register("bone_scythe_arm",
            () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> FLESH_VEINS = ITEMS.register("flesh_veins",
            () -> new BlockItem(ModBlocks.FLESH_VEINS.get(), new Item.Properties()));

    public static final RegistryObject<com.carnis.mod.item.AntibioticsItem> ANTIBIOTICS = ITEMS.register("antibiotics",
            () -> new com.carnis.mod.item.AntibioticsItem(new Item.Properties().stacksTo(16)));

    public static final RegistryObject<Item> NEURAL_BINDING_MATRIX = ITEMS.register(
            "neural_binding_matrix", () -> new Item(new Item.Properties()));
    public static final RegistryObject<NeuroResonatorArmorItem> NEURO_RESONATOR_CHESTPLATE = ITEMS.register(
            "neuro_resonator_chestplate", () -> new NeuroResonatorArmorItem(ArmorItem.Type.CHESTPLATE, new Item.Properties()));
    public static final RegistryObject<NeuroResonatorArmorItem> NEURO_RESONATOR_LEGGINGS = ITEMS.register(
            "neuro_resonator_leggings", () -> new NeuroResonatorArmorItem(ArmorItem.Type.LEGGINGS, new Item.Properties()));
    public static final RegistryObject<NeuroResonatorArmorItem> NEURO_RESONATOR_BOOTS = ITEMS.register(
            "neuro_resonator_boots", () -> new NeuroResonatorArmorItem(ArmorItem.Type.BOOTS, new Item.Properties()));

    public static final RegistryObject<Item> NERVE_PILLAR = ITEMS.register("nerve_pillar",
            () -> new BlockItem(ModBlocks.NERVE_PILLAR.get(), new Item.Properties()));
    public static final RegistryObject<Item> VIRAL_DART = ITEMS.register("viral_dart",
            () -> new Item(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<Item> PURIFICATION_DART = ITEMS.register("purification_dart",
            () -> new Item(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<PneumaticInoculatorItem> PNEUMATIC_INOCULATOR = ITEMS.register(
            "pneumatic_inoculator", () -> new PneumaticInoculatorItem(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> CREEPING_TENDRILS = ITEMS.register(
            "creeping_tendrils", () -> new BlockItem(ModBlocks.CREEPING_TENDRILS.get(), new Item.Properties()));
    public static final RegistryObject<Item> PUSTULE_CLUSTER = ITEMS.register(
            "pustule_cluster", () -> new BlockItem(ModBlocks.PUSTULE_CLUSTER.get(), new Item.Properties()));
    public static final RegistryObject<Item> STOMACH_POOL = ITEMS.register(
            "stomach_pool", () -> new BlockItem(ModBlocks.STOMACH_POOL.get(), new Item.Properties()));

    public static final RegistryObject<Item> SPORE_SPROUT = ITEMS.register(
            "spore_sprout", () -> new BlockItem(ModBlocks.SPORE_SPROUT.get(), new Item.Properties()));
    public static final RegistryObject<Item> NEURAL_MOSS = ITEMS.register(
            "neural_moss", () -> new BlockItem(ModBlocks.NEURAL_MOSS.get(), new Item.Properties()));

    public static final RegistryObject<Item> CHARRED_FLESH = ITEMS.register(
            "charred_flesh",
            () -> new BlockItem(ModBlocks.CHARRED_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> LIVING_FLESH = ITEMS.register(
            "living_flesh",
            () -> new BlockItem(ModBlocks.LIVING_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> OSSIFIED_FLESH = ITEMS.register(
            "ossified_flesh",
            () -> new BlockItem(ModBlocks.OSSIFIED_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> FIREPROOF_FLESH = ITEMS.register(
            "fireproof_flesh",
            () -> new BlockItem(ModBlocks.FIREPROOF_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> PULSING_HEART = ITEMS.register(
            "pulsing_heart",
            () -> new com.carnis.mod.item.PulsingHeartItem(
                    ModBlocks.PULSING_HEART.get(),
                    new Item.Properties()
            )
    );

    public static final RegistryObject<Item> HIVE_EYE = ITEMS.register(
            "hive_eye",
            () -> new com.carnis.mod.item.HiveEyeItem(
                    ModBlocks.HIVE_EYE.get(),
                    new Item.Properties()
            )
    );

    public static final RegistryObject<ForgeSpawnEggItem>
            FLESH_AMALGAM_SPAWN_EGG = ITEMS.register(
                    "flesh_amalgam_spawn_egg",
                    () -> new ForgeSpawnEggItem(
                            ModEntities.FLESH_AMALGAM,
                            0x6F1B31,
                            0xD98B76,
                            new Item.Properties()
                    )
            );

    public static final RegistryObject<PurificationSerumItem>
            PURIFICATION_SERUM = ITEMS.register(
                    "purification_serum",
                    () -> new PurificationSerumItem(
                            new Item.Properties()
                                    .stacksTo(16)
                                    .craftRemainder(Items.GLASS_BOTTLE)
                                    .rarity(Rarity.UNCOMMON)
                    )
            );

    public static final RegistryObject<BioPurifierItem>
            BIO_PURIFIER = ITEMS.register(
                    "bio_purifier",
                    () -> new BioPurifierItem(
                            new Item.Properties()
                                    .durability(BioPurifierItem.MAX_DURABILITY)
                                    .rarity(Rarity.RARE)
                    )
            );

    public static final RegistryObject<NeuroResonatorHelmetItem>
            NEURO_RESONATOR_HELMET = ITEMS.register(
                    "neuro_resonator_helmet",
                    () -> new NeuroResonatorHelmetItem(
                            new Item.Properties()
                                    .rarity(Rarity.UNCOMMON)
                    )
            );

    private ModItems() {
    }

    public static void register(IEventBus modEventBus) {
        ITEMS.register(modEventBus);
    }
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

    public static final RegistryObject<SoundEvent> AMALGAMATION_FUSE =
            registerVariableRangeSound("amalgamation_fuse");

    public static final RegistryObject<SoundEvent> BONE_DEFLECT =
            registerVariableRangeSound("bone_deflect");

    public static final RegistryObject<SoundEvent> ACID_SPLASH =
            registerVariableRangeSound("acid_splash");

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

## `src/main/java/com/carnis/mod/client/ClientModEvents.java`

```java
package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.gui.InfectionVeinsOverlay;
import com.carnis.mod.client.renderer.FleshAmalgamRenderer;
import com.carnis.mod.client.renderer.DartRenderer;
import com.carnis.mod.client.renderer.PulsingHeartRenderer;
import com.carnis.mod.client.renderer.HiveEyeRenderer;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModEntities;
import net.minecraft.client.renderer.entity.ZombieRenderer;
import net.minecraft.client.renderer.entity.SkeletonRenderer;
import net.minecraft.client.renderer.entity.CreeperRenderer;
import net.minecraft.client.renderer.entity.SpiderRenderer;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.MOD,
        value = Dist.CLIENT
)
public final class ClientModEvents {
    private ClientModEvents() {
    }

    @SubscribeEvent
    public static void onRegisterRenderers(
            EntityRenderersEvent.RegisterRenderers event
    ) {
        event.registerEntityRenderer(ModEntities.HIVE_SENTINEL.get(), com.carnis.mod.client.renderer.HiveSentinelRenderer::new);
        event.registerEntityRenderer(ModEntities.CEREBRAL_NEXUS.get(), com.carnis.mod.client.renderer.CerebralNexusRenderer::new);
        event.registerEntityRenderer(ModEntities.BIOMASS_MAGGOT.get(), com.carnis.mod.client.renderer.BiomassMaggotRenderer::new);
        event.registerEntityRenderer(ModEntities.PARASITIC_TENDRIL.get(), com.carnis.mod.client.renderer.ParasiticTendrilRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_ZOMBIE.get(), com.carnis.mod.client.renderer.InfectedZombieRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_SKELETON.get(), com.carnis.mod.client.renderer.InfectedSkeletonRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_CREEPER.get(), com.carnis.mod.client.renderer.InfectedCreeperRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_SPIDER.get(), com.carnis.mod.client.renderer.InfectedSpiderRenderer::new);

        event.registerEntityRenderer(ModEntities.FLESH_SPAT.get(), net.minecraft.client.renderer.entity.ThrownItemRenderer::new);
        event.registerEntityRenderer(ModEntities.AMALGAM_BILE.get(), net.minecraft.client.renderer.entity.ThrownItemRenderer::new);
        event.registerEntityRenderer(ModEntities.VIRAL_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.PURIFICATION_DART.get(), DartRenderer::new);
        event.registerBlockEntityRenderer(
                ModBlockEntities.PULSING_HEART.get(),
                PulsingHeartRenderer::new
        );
        event.registerBlockEntityRenderer(ModBlockEntities.HIVE_EYE.get(), HiveEyeRenderer::new);
        event.registerEntityRenderer(
                ModEntities.FLESH_AMALGAM.get(),
                FleshAmalgamRenderer::new
        );
    }

    @SubscribeEvent
    public static void onRegisterParticles(net.minecraftforge.client.event.RegisterParticleProvidersEvent event) {
        event.registerSpriteSet(com.carnis.mod.init.ModParticles.BIOMASS_SPARK.get(),
                com.carnis.mod.client.particle.BiomassSparkParticle.Provider::new);
        event.registerSpriteSet(com.carnis.mod.init.ModParticles.PURIFIER_FLAME.get(),
                com.carnis.mod.client.particle.BiomassSparkParticle.Provider::new);
    }

    @SubscribeEvent
    public static void onClientSetup(net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            net.minecraft.client.renderer.ItemBlockRenderTypes.setRenderLayer(
                    com.carnis.mod.init.ModFluids.SLUDGE_SOURCE.get(), net.minecraft.client.renderer.RenderType.translucent());
            net.minecraft.client.renderer.ItemBlockRenderTypes.setRenderLayer(
                    com.carnis.mod.init.ModFluids.SLUDGE_FLOWING.get(), net.minecraft.client.renderer.RenderType.translucent());
        });
    }

    @SubscribeEvent
    public static void onRegisterGuiOverlays(
            RegisterGuiOverlaysEvent event
    ) {
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "veins_overlay", new InfectionVeinsOverlay());
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "neuro_resonance", new com.carnis.mod.client.gui.overlay.NeuroResonanceOverlay());
    }
}
```

## `src/main/java/com/carnis/mod/client/gui/CodexContent.java`

```java
package com.carnis.mod.client.gui;

import java.util.List;

/** Field notes are intentionally Russian; each entry is paginated by the active game font. */
public final class CodexContent {
    public record Page(String title, String body, String note) { }
    public record Chapter(String title, List<Page> pages) { }

    public static final List<Chapter> CHAPTERS = List.of(
        new Chapter("Органогенез", List.of(
            new Page("Пульсирующее сердце",
                "Центр колонии пульсирует каждые 100 тиков. Известная ему плоть и жилы дают меру роста в радиусе 32 блоков; сам импульс охватывает 8.",
                "Сердце считает лишь обнаруженную ткань."),
            new Page("Порядок органов",
                "На 25, 50, 75 и 100 заражённых блоках улей закладывает око, стража, бассейн и столп. Для роста требуется живая плоть в 8–24 блоках.",
                "Орган растёт там, где клетка считает место пригодным."),
            new Page("Око Улья",
                "Сенсор замечает чужаков в пределах 24 блоков и передаёт тревогу свободным мобам Улья в радиусе 28 блоков.",
                "Вопль слышен раньше, чем видно зрачок."),
            new Page("Желудочный бассейн",
                "Кислота разлагает предметы и живую ткань. Погибший в ней скот отдаёт ближайшему сердцу 20 единиц биомассы, корова — 30.",
                "Пять единиц урона в секунду — достаточно, чтобы не входить."),
            new Page("Нервный столп",
                "Столп рассеивает новый термический шок в радиусе 32 блоков. Щит сокращает поджог форм Улья, но не делает плоть несгораемой.",
                "Сначала разрушить якорь. Затем очистить очаг."),
            new Page("Страж и Нексус",
                "Пси-якорь вводит скот в транс и ведёт его к бассейну. При четырёх органах и 200 единицах сердце может стать Мозговым Нексусом.",
                "Два дочерних сердца возникают на известной плоти в 48–64 блоках."))),
        new Chapter("Биоценоз", List.of(
            new Page("Остатки биомассы",
                "На твёрдом полу гибель хозяина оставляет рыхлые останки. Они замедляют и чужаков, и существ Улья; близ падали появляются личинки.",
                "В воде и без опоры образец получить не удалось."),
            new Page("Личинка биомассы",
                "Личинка ищет останки в радиусе 16 блоков. Два приёма пищи пробуждают инстинкт зарывания; час на плоти не требуется — достаточно минуты.",
                "Она выбирает рыхлую землю или плоть, но не камень."),
            new Page("Кокон созревания",
                "Мясная луковица держится на потолке или на полу. Через 60–90 секунд её сердцебиение учащается, мешок лопается и выпускает щупальца.",
                "Счёт идёт только в загруженной области."),
            new Page("Щупальце: внедрение",
                "При контакте вероятность заражения мирного хозяина — 85%, монстра — 45%; броня снижает шанс монстра до 30%. Паразит исчезает после броска.",
                "Провал сопровождается шипением и слабым ранением."),
            new Page("Четыре стадии",
                "До 10 секунд — инкубация; до 25 — вены и опухоли; до 30 — разрыв и заражение почвы. Затем монстр мутирует, а мирный хозяин разлагается.",
                "На третьей стадии рана способна убить до превращения."))),
        new Chapter("Аберрации", List.of(
            new Page("Заражённый зомби",
                "Правая рука разрослась в костяной клинок; жгутики обрамляют разорванную голову. У останков он замирает и поглощает биомассу.",
                "Во время питания его взгляд удерживается на одном направлении."),
            new Page("Заражённый скелет",
                "Костяной серп заменяет оружие. Проросший нерв и ядро в рёбрах излучают красный свет; удар лезвием может задеть соседние цели.",
                "Не принимать пустую глазницу за отсутствие зрения."),
            new Page("Заражённый крипер",
                "Раздутые мешки колышутся до разрыва. Вместо обычного взрыва он выбрасывает споры, травит живых и оставляет жилы на прочных гранях.",
                "Признак детонации — бешеное дрожание нервных усиков."),
            new Page("Амальгама плоти",
                "Титанический симбиот возникает из слияния заражённых форм у сердца. Костяные пластины и кислота меняются вместе с адаптацией Улья.",
                "Ослабленная амальгама поглощает останки и малые формы; берегитесь ударной волны и едкой желчи."))),
        new Chapter("Биотехнологии", List.of(
            new Page("Пневмоинокулятор",
                "Дротик несёт вирусный штамм или очищающий состав. На расстоянии учитывайте падение снаряда и укрытия; магазин расходует подходящие дротики.",
                "Очищающий состав снижает заражение игрока на 35."),
            new Page("Био-очиститель",
                "Поток огня стерилизует живую и окостеневшую плоть, оставляя обугленную ткань. Термический удар обычно вызывает шок заражённого участка.",
                "Действующий нервный столп блокирует новый термошок."),
            new Page("Нейро-броня",
                "Вплетённые сухожилия связывают доспех с нервной системой носителя. Каждая защищённая часть уменьшает заражающую экспозицию на четверть.",
                "Полный комплект скрывает носителя от Ока, но не обещает невидимости всем.")))
    );
    private CodexContent() { }
}
```

## `src/main/java/com/carnis/mod/datagen/ModLanguageProvider.java`

```java
package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModItems;
import net.minecraft.data.PackOutput;
import net.minecraftforge.common.data.LanguageProvider;

public final class ModLanguageProvider extends LanguageProvider {
    private static final String EN_US = "en_us";
    private static final String RU_RU = "ru_ru";

    private final String locale;

    public ModLanguageProvider(PackOutput output, String locale) {
        super(output, CarnisMod.MOD_ID, locale);
        this.locale = locale;
    }

    @Override
    protected void addTranslations() {
        switch (locale) {
            case EN_US -> addEnglishTranslations();
            case RU_RU -> addRussianTranslations();
            default -> throw new IllegalStateException(
                    "Unsupported Carnis language provider locale: " + locale
            );
        }
    }

    private void addEnglishTranslations() {
        add("subtitles.carnis.inoculator_fire", "Inoculator fires");
        add("subtitles.carnis.dart_hit", "Dart hits");
        add("tooltip.carnis.flesh_bulb.mechanics", "An incubation sac that can attach to ceilings and floors.");
        add("tooltip.carnis.flesh_bulb.lore", "The muffled, rapid heartbeat of a maturing brood can be heard inside.");
        add("tooltip.carnis.sinew_spikes.mechanics", "Deals piercing damage and slows any creature that steps on it.");
        add("tooltip.carnis.sinew_spikes.lore", "Taut sinews respond to the slightest vibration of footsteps.");
        add("tooltip.carnis.biomass_maggot.mechanics", "A voracious scavenger. Devours organic remains and pupates in soil.");
        add("tooltip.carnis.biomass_maggot.lore", "The first link in the Hive’s parasitic cycle.");
        add("item.carnis.infected_zombie_spawn_egg", "Infected Zombie Spawn Egg");
        add("entity.carnis.infected_zombie", "Infected Zombie");
        add("tooltip.carnis.infected_zombie_spawn_egg", "Spawns an infected zombie.");
        add("item.carnis.antibiotics", "Antibiotics");
        add("effect.carnis.immunosuppression", "Immunosuppression");
        add("tooltip.carnis.antibiotics", "Prevents exposure for 3 minutes.");
        add("entity.carnis.parasitic_tendril", "Parasitic Tendril");
        add("entity.carnis.hive_sentinel", "Hive Sentinel");
        add("entity.carnis.cerebral_nexus", "Cerebral Nexus");
        add("effect.carnis.incubating", "Incubating");
        add("subtitles.carnis.flamethrower_fire", "Flamethrower roars");
        add("subtitles.carnis.amalgam_roar", "Amalgam roars");
        add("codex.carnis.chapter.0", "Inception & Biomes");
        add("codex.carnis.body.0", "Veins spread across supported faces; incomplete faces may resist growth. Sludge contaminates players and reacts with water and lava. Infection spreads by a queued process.");
        add("codex.carnis.chapter.1", "Adaptive Hivemind");
        add("codex.carnis.body.1", "FIRE / RANGED / MELEE / EXPLOSIVE use the same logarithmic mitigation curve. Points: 0 / 100 / 300 / 600 / 1000. Reduction: 0% / 25% / 50% / 70% / 80%. Between thresholds: linear interpolation in ln(1+points). Cap 80%.");
        add("codex.carnis.chapter.2", "Hive Organs & Flora");
        add("codex.carnis.body.2", "Hive Eye detects players within 24 blocks and alerts linked mobs within 32. Placing a Nerve Pillar halves remaining chunk shock. Stomach Pool dissolves items: flesh or meat gives 5 biomass each; other items give 1. Living creatures take 4 damage per second.");
        add("codex.carnis.chapter.3", "Medical & Armor Weaving");
        add("codex.carnis.body.3", "Serum reduces infection by 35. Antibiotics block positive exposure for 3600 ticks. On an anvil, combine armor and one neural binding matrix for 5 levels. Each woven or resonator armor piece reduces exposure by 25%; four pieces reach 100%.");
        add("codex.carnis.chapter.4", "Mutants & Amalgamation");
        add("codex.carnis.body.4", "Zombie: 35 health, 4.5 attack; skeleton: 28 health, 4.5 attack; creeper: 24 health; spider: 20 health, 3 attack. Spat: 2 damage, Slowness II for 100 ticks and +5 exposure on successful damage. Three zombies near a heart at 300 biomass can fuse.");
        add("entity.carnis.flesh_spat", "Flesh Spat");
        add("item.carnis.flesh_spat", "Flesh Spat");
        add("tooltip.carnis.flesh_spat", "A glob of infectious tissue.");
        add("subtitles.carnis.heartbeat_loop", "Heart beats");
        add("item.carnis.research_journal", "Codex Carnis");
        add("tooltip.carnis.research_journal", "A field guide to the hive.");
        add("item.carnis.tainted_sludge_bucket", "Tainted Sludge Bucket");
        add("item.carnis.bone_scythe_arm", "Bone Scythe Arm");
        add("block.carnis.tainted_sludge", "Tainted Sludge");
        add("fluid_type.carnis.tainted_sludge", "Tainted Sludge");
        add("tooltip.carnis.tainted_sludge_bucket", "A bucket of infectious sludge.");
        add("tooltip.carnis.bone_scythe_arm", "A jagged bone blade.");
        add("subtitles.carnis.amalgam_step", "Flesh Amalgam squelches");
        add("block.carnis.flesh_veins", "Flesh Veins");
        add("tooltip.carnis.flesh_veins", "Organic growth on exposed surfaces.");

        add("entity.carnis.infected_skeleton", "Infected Skeleton");
        add("item.carnis.infected_skeleton_spawn_egg", "Infected Skeleton Spawn Egg");
        add("tooltip.carnis.infected_skeleton_spawn_egg", "Spawns an infected skeleton.");
        add("entity.carnis.infected_creeper", "Infected Creeper");
        add("item.carnis.infected_creeper_spawn_egg", "Infected Creeper Spawn Egg");
        add("tooltip.carnis.infected_creeper_spawn_egg", "Spawns an infected creeper.");
        add("entity.carnis.infected_spider", "Infected Spider");
        add("item.carnis.infected_spider_spawn_egg", "Infected Spider Spawn Egg");
        add("tooltip.carnis.infected_spider_spawn_egg", "Spawns an infected spider.");
        add("item.carnis.neuro_resonator_chestplate", "Neuro-Resonator Chestplate");
        add("item.carnis.neuro_resonator_leggings", "Neuro-Resonator Leggings");
        add("item.carnis.neuro_resonator_boots", "Neuro-Resonator Boots");
        add("block.carnis.flesh_bulb", "Flesh Bulb");
        add("block.carnis.biomass_remains", "Biomass Remains");
        add("block.carnis.sinew_spikes", "Sinew Spikes");
        add("entity.carnis.biomass_maggot", "Biomass Maggot");
        add("item.carnis.biomass_maggot_spawn_egg", "Biomass Maggot Spawn Egg");
        add("item.carnis.neural_binding_matrix", "Neural Binding Matrix");
        add("tooltip.carnis.neuro_resonator_chestplate", "A biological chestplate reduces infection exposure.");
        add("tooltip.carnis.neuro_resonator_leggings", "Biological leggings reduce infection exposure.");
        add("tooltip.carnis.neuro_resonator_boots", "Biological boots reduce infection exposure.");
        add("tooltip.carnis.neural_binding_matrix", "Weave into armor at an anvil for five levels.");
        add("block.carnis.nerve_pillar", "Nerve Pillar");
        add("item.carnis.pneumatic_inoculator", "Pneumatic Inoculator");
        add("item.carnis.viral_dart", "Viral Dart");
        add("item.carnis.purification_dart", "Purification Dart");
        add("entity.carnis.viral_dart", "Viral Dart");
        add("entity.carnis.purification_dart", "Purification Dart");
        add("death.attack.carnis_tainted_sludge", "%1$s dissolved in tainted sludge");
        add("death.attack.purification_dart", "%1$s was purified by a dart");
        add("death.attack.purification_dart.player", "%1$s was purified by %2$s");
        add("tooltip.carnis.nerve_pillar", "Placement halves remaining shock time in this chunk.");
        add("tooltip.carnis.pneumatic_inoculator", "Right-click to fire a carried dart; 15-tick cooldown.");
        add("tooltip.carnis.viral_dart", "Adds 30 infection to players; poisons and slows mobs.");
        add("tooltip.carnis.purification_dart", "Removes 35 infection or damages Carnis mobs for 25.");
        add("tooltip.carnis.hold_shift", "Hold Shift for details");
        add("tooltip.carnis.living_flesh", "Living tissue spreads through nearby terrain.");
        add("tooltip.carnis.charred_flesh", "Burned tissue yields bone meal and charcoal.");
        add("tooltip.carnis.spore_sprout", "An organic sprout releases drifting spores.");
        add("tooltip.carnis.neural_moss", "A fleshy carpet impedes movement.");
        add("tooltip.carnis.creeping_tendrils", "Climb the tendrils attached to solid flesh.");
        add("tooltip.carnis.pustule_cluster", "Step on it without sneaking to burst infectious spores.");
        add("tooltip.carnis.stomach_pool", "Corrosive tissue dissolves items into biomass.");
        add("tooltip.carnis.ossified_flesh", "Hardened tissue spreads the hive.");
        add("tooltip.carnis.fireproof_flesh", "Adapted tissue resistant to flame.");
        add("tooltip.carnis.veins", "Living veins carry infection through wood.");
        add("tooltip.carnis.pulsing_heart", "The hive heart accelerates nearby infection.");
        add("tooltip.carnis.hive_eye", "Detects intruders and alerts nearby Amalgams.");
        add("tooltip.carnis.flesh_amalgam_spawn_egg", "Spawns a Flesh Amalgam.");
        add("tooltip.carnis.purification_serum", "Drink to remove 35 infection points.");
        add("effect.carnis.thermal_shock", "Thermal Shock");
        add("subtitles.carnis.purifier_ignite", "Purifier ignites");
        add("subtitles.carnis.purifier_loop", "Purifier fires");
        add("tooltip.carnis.bio_purifier", "Hold use: 6.5-block cone of flame.");
        add("tooltip.carnis.neuro_resonator_helmet", "Dampens hallucinations, reduces exposure by 25% and reveals nearby biomass.");
        add("itemGroup.carnis", "Carnis: Adaptive Hivemind");

        add("death.attack.necrotic_consumption", "%1$s was consumed by the hivemind");
        add(ModBlocks.CREEPING_TENDRILS.get(), "Creeping Tendrils");
        add(ModBlocks.PUSTULE_CLUSTER.get(), "Pustule Cluster");
        add(ModBlocks.STOMACH_POOL.get(), "Stomach Pool");
        add(ModBlocks.SPORE_SPROUT.get(), "Spore Sprout");
        add(ModBlocks.NEURAL_MOSS.get(), "Neural Moss");
        add(ModBlocks.CHARRED_FLESH.get(), "Charred Flesh");
        add(ModBlocks.LIVING_FLESH.get(), "Living Flesh");
        add(ModBlocks.OSSIFIED_FLESH.get(), "Ossified Flesh");
        add(ModBlocks.FIREPROOF_FLESH.get(), "Fireproof Flesh");
        add(ModBlocks.PULSING_HEART.get(), "Pulsing Heart");
        add(ModBlocks.HIVE_EYE.get(), "Hive Eye");
        add("entity.carnis.flesh_amalgam", "Flesh Amalgam");
        add("item.carnis.amalgam_bile_glob", "Amalgam Bile");
        add("entity.carnis.amalgam_bile", "Amalgam Bile");
        add("tooltip.carnis.amalgam_bile_glob", "A corrosive organic glob.");
        add("subtitles.carnis.amalgam_smash", "Amalgam slams the ground");
        add("subtitles.carnis.organic_creak", "Sinew lashes");
        add(
                "item.carnis.flesh_amalgam_spawn_egg",
                "Flesh Amalgam Spawn Egg"
        );
        add(ModItems.PURIFICATION_SERUM.get(), "Purification Serum");
        add(ModItems.BIO_PURIFIER.get(), "Bio-Purifier");
        add(
                ModItems.NEURO_RESONATOR_HELMET.get(),
                "Neuro-Resonator Helmet"
        );
        add(
                "death.attack.bio_purifier",
                "%1$s was incinerated by a bio-purifier"
        );
        add(
                "death.attack.bio_purifier.player",
                "%1$s was incinerated by %2$s's bio-purifier"
        );

        add("subtitles.carnis.phantom_creeper", "Something hisses behind you");
        add("subtitles.carnis.phantom_footsteps", "Footsteps squelch through flesh");
        add("subtitles.carnis.phantom_whisper", "The hivemind whispers");
        add("subtitles.carnis.pulsing_heart_beat", "A biome heart beats");
        add("subtitles.carnis.synapse_shock", "A synapse discharges");
        add("subtitles.carnis.synapse_rupture", "Nerve tissue tears apart");
        add("subtitles.carnis.digestor_churn", "A digestor churns");
        add("subtitles.carnis.hive_eye_screech", "The hive eye shrieks");
        add(
                "subtitles.carnis.amalgamation_fuse",
                "Flesh fuses into an amalgam"
        );
        add(
                "subtitles.carnis.bone_deflect",
                "A projectile ricochets off bone"
        );
        add(
                "subtitles.carnis.acid_splash",
                "Corrosive acid splashes"
        );
        add(
                "subtitles.carnis.flesh_amalgam_ambient",
                "The Flesh Amalgam groans"
        );
        add(
                "subtitles.carnis.flesh_amalgam_hurt",
                "The Flesh Amalgam recoils"
        );
        add(
                "subtitles.carnis.flesh_amalgam_death",
                "The Flesh Amalgam collapses"
        );
    }

    private void addRussianTranslations() {
        add("entity.carnis.hive_sentinel", "Страж Улья");
        add("entity.carnis.cerebral_nexus", "Мозговой узел");
        add("subtitles.carnis.inoculator_fire", "Выстрел инокулятора");
        add("subtitles.carnis.dart_hit", "Дротик ударяется");
        add("tooltip.carnis.flesh_bulb.mechanics", "Инкубационный мешок, способный закрепляться на потолке и полу.");
        add("tooltip.carnis.flesh_bulb.lore", "Внутри слышно глухое, частое сердцебиение зреющего выводка.");
        add("tooltip.carnis.sinew_spikes.mechanics", "Наносят колющий урон и замедляют любое наступившее существо.");
        add("tooltip.carnis.sinew_spikes.lore", "Натянутые жилы реагируют на малейшую вибрацию шагов.");
        add("tooltip.carnis.biomass_maggot.mechanics", "Ненасытный трупоед. Пожирает органические останки и окукливается в почве.");
        add("tooltip.carnis.biomass_maggot.lore", "Начальное звено паразитического круговорота Улья.");
        add("item.carnis.infected_zombie_spawn_egg", "Яйцо призыва заражённого зомби");
        add("entity.carnis.infected_zombie", "Заражённый зомби");
        add("tooltip.carnis.infected_zombie_spawn_egg", "Призывает заражённого зомби.");
        add("item.carnis.antibiotics", "Антибиотики");
        add("effect.carnis.immunosuppression", "Иммуносупрессия");
        add("tooltip.carnis.antibiotics", "Предотвращает заражение на 3 минуты.");
        add("entity.carnis.parasitic_tendril", "Паразитический усик");
        add("effect.carnis.incubating", "Инкубация");
        add("subtitles.carnis.flamethrower_fire", "Огнемёт ревёт");
        add("subtitles.carnis.amalgam_roar", "Амальгама ревёт");
        add("codex.carnis.chapter.0", "Истоки и биомы");
        add("codex.carnis.body.0", "Вены растут по поддерживаемым граням; неполные грани могут мешать росту. Жижа заражает игроков и реагирует с водой и лавой. Распространение обрабатывается очередью.");
        add("codex.carnis.chapter.1", "Адаптивный разум");
        add("codex.carnis.body.1", "ОГОНЬ / ДАЛЬНИЙ / БЛИЖНИЙ / ВЗРЫВ: общая логарифмическая кривая. Очки: 0 / 100 / 300 / 600 / 1000. Снижение: 0% / 25% / 50% / 70% / 80%. Между порогами — интерполяция по ln(1+очки). Предел 80%.");
        add("codex.carnis.chapter.2", "Органы и флора улья");
        add("codex.carnis.body.2", "Глаз видит игроков в 24 блоках и предупреждает связанных мобов в 32. Установка нервного столба вдвое сокращает оставшийся шок чанка. Желудочный бассейн даёт 5 биомассы за мясо или плоть, 1 за иной предмет; живым наносит 4 урона в секунду.");
        add("codex.carnis.chapter.3", "Медицина и нейроплетение");
        add("codex.carnis.body.3", "Сыворотка снижает заражение на 35. Антибиотики блокируют положительную экспозицию на 3600 тиков. На наковальне соедините броню с одной матрицей за 5 уровней. Каждая защищённая часть снижает экспозицию на 25%, четыре — на 100%.");
        add("codex.carnis.chapter.4", "Мутанты и слияние");
        add("codex.carnis.body.4", "Зомби: 35 здоровья, 4,5 урона; скелет: 28 и 4,5; крипер: 24 здоровья; паук: 20 и 3. Плевок: 2 урона, замедление II на 100 тиков и +5 экспозиции при успешном уроне. Три зомби у сердца при 300 биомассы могут слиться.");
        add("entity.carnis.flesh_spat", "Плевок плоти");
        add("item.carnis.flesh_spat", "Плевок плоти");
        add("tooltip.carnis.flesh_spat", "Сгусток заражённой ткани.");
        add("subtitles.carnis.heartbeat_loop", "Сердце бьётся");
        add("item.carnis.research_journal", "Кодекс Карнис");
        add("tooltip.carnis.research_journal", "Полевой справочник по улью.");
        add("item.carnis.tainted_sludge_bucket", "Ведро заражённой слизи");
        add("item.carnis.bone_scythe_arm", "Костяная коса-рука");
        add("block.carnis.tainted_sludge", "Заражённая слизь");
        add("fluid_type.carnis.tainted_sludge", "Заражённая слизь");
        add("tooltip.carnis.tainted_sludge_bucket", "Ведро заразной слизи.");
        add("tooltip.carnis.bone_scythe_arm", "Зазубренный костяной клинок.");
        add("subtitles.carnis.amalgam_step", "Плотяная амальгама чавкает");
        add("block.carnis.flesh_veins", "Плотяные жилы");
        add("tooltip.carnis.flesh_veins", "Органические жилы на открытых поверхностях.");

        add("entity.carnis.infected_skeleton", "Заражённый скелет");
        add("item.carnis.infected_skeleton_spawn_egg", "Яйцо призыва: Заражённый скелет");
        add("tooltip.carnis.infected_skeleton_spawn_egg", "Призывает заражённого скелета.");
        add("entity.carnis.infected_creeper", "Заражённый крипер");
        add("item.carnis.infected_creeper_spawn_egg", "Яйцо призыва: Заражённый крипер");
        add("tooltip.carnis.infected_creeper_spawn_egg", "Призывает заражённого крипера.");
        add("entity.carnis.infected_spider", "Заражённый паук");
        add("item.carnis.infected_spider_spawn_egg", "Яйцо призыва: Заражённый паук");
        add("tooltip.carnis.infected_spider_spawn_egg", "Призывает заражённого паука.");
        add("item.carnis.neuro_resonator_chestplate", "Нейро-резонаторный нагрудник");
        add("item.carnis.neuro_resonator_leggings", "Нейро-резонаторные поножи");
        add("item.carnis.neuro_resonator_boots", "Нейро-резонаторные ботинки");
        add("block.carnis.flesh_bulb", "Мясная луковица");
        add("block.carnis.biomass_remains", "Останки биомассы");
        add("block.carnis.sinew_spikes", "Сухожильные шипы");
        add("entity.carnis.biomass_maggot", "Личинка биомассы");
        add("item.carnis.biomass_maggot_spawn_egg", "Яйцо призыва: Личинка биомассы");
        add("item.carnis.neural_binding_matrix", "Матрица нейронного сплетения");
        add("tooltip.carnis.neuro_resonator_chestplate", "Биологический нагрудник снижает заражение.");
        add("tooltip.carnis.neuro_resonator_leggings", "Биологические поножи снижают заражение.");
        add("tooltip.carnis.neuro_resonator_boots", "Биологические ботинки снижают заражение.");
        add("tooltip.carnis.neural_binding_matrix", "Вплетите в броню на наковальне за пять уровней.");
        add("block.carnis.nerve_pillar", "Нервный столп");
        add("item.carnis.pneumatic_inoculator", "Пневматический инокулятор");
        add("item.carnis.viral_dart", "Вирусный дротик");
        add("item.carnis.purification_dart", "Очищающий дротик");
        add("entity.carnis.viral_dart", "Вирусный дротик");
        add("entity.carnis.purification_dart", "Очищающий дротик");
        add("death.attack.carnis_tainted_sludge", "%1$s растворился в заражённой жиже");
        add("death.attack.purification_dart", "%1$s очищен дротиком");
        add("death.attack.purification_dart.player", "%1$s очищен игроком %2$s");
        add("tooltip.carnis.nerve_pillar", "При установке вдвое сокращает оставшийся шок чанка.");
        add("tooltip.carnis.pneumatic_inoculator", "ПКМ: выстрел дротиком из инвентаря; задержка 15 тиков.");
        add("tooltip.carnis.viral_dart", "Добавляет игрокам 30 заражения; травит и замедляет мобов.");
        add("tooltip.carnis.purification_dart", "Снимает 35 заражения или наносит мобам Carnis 25 урона.");
        add("tooltip.carnis.hold_shift", "Удерживайте Shift для подробностей");
        add("tooltip.carnis.living_flesh", "Живая ткань распространяется по окружающим блокам.");
        add("tooltip.carnis.charred_flesh", "Обгоревшая ткань даёт костную муку и уголь.");
        add("tooltip.carnis.spore_sprout", "Органический росток выпускает споры.");
        add("tooltip.carnis.neural_moss", "Мясистый мох замедляет движение.");
        add("tooltip.carnis.creeping_tendrils", "Взбирайтесь по усикам на поверхности плоти.");
        add("tooltip.carnis.pustule_cluster", "Наступите без приседания: пустулы лопнут и заразят вас.");
        add("tooltip.carnis.stomach_pool", "Едкая ткань растворяет предметы в биомассу.");
        add("tooltip.carnis.ossified_flesh", "Окостеневшая ткань распространяет улей.");
        add("tooltip.carnis.fireproof_flesh", "Ткань, приспособленная к огню.");
        add("tooltip.carnis.veins", "Живые вены несут инфекцию через древесину.");
        add("tooltip.carnis.pulsing_heart", "Сердце улья ускоряет заражение поблизости.");
        add("tooltip.carnis.hive_eye", "Обнаруживает чужаков и тревожит ближайших амальгам.");
        add("tooltip.carnis.flesh_amalgam_spawn_egg", "Призывает амальгаму плоти.");
        add("tooltip.carnis.purification_serum", "Выпейте, чтобы снизить заражение на 35 пунктов.");
        add("effect.carnis.thermal_shock", "Термический шок");
        add("subtitles.carnis.purifier_ignite", "Очиститель зажигается");
        add("subtitles.carnis.purifier_loop", "Очиститель выпускает пламя");
        add("tooltip.carnis.bio_purifier", "Удерживайте: конус пламени на 6,5 блока.");
        add("tooltip.carnis.neuro_resonator_helmet", "Подавляет галлюцинации, снижает экспозицию на 25% и обнаруживает биомассу.");
        add("itemGroup.carnis", "Carnis: Адаптивный коллективный разум");

        add("death.attack.necrotic_consumption", "%1$s поглощён коллективным разумом");
        add(ModBlocks.CREEPING_TENDRILS.get(), "Ползучие щупальца");
        add(ModBlocks.PUSTULE_CLUSTER.get(), "Скопление пустул");
        add(ModBlocks.STOMACH_POOL.get(), "Желудочный бассейн");
        add(ModBlocks.SPORE_SPROUT.get(), "Споровый росток");
        add(ModBlocks.NEURAL_MOSS.get(), "Нервный мох");
        add(ModBlocks.CHARRED_FLESH.get(), "Обугленная плоть");
        add(ModBlocks.LIVING_FLESH.get(), "Живая плоть");
        add(ModBlocks.OSSIFIED_FLESH.get(), "Окостенелая плоть");
        add(ModBlocks.FIREPROOF_FLESH.get(), "Огнеупорная плоть");
        add(ModBlocks.PULSING_HEART.get(), "Сердце биома");
        add(ModBlocks.HIVE_EYE.get(), "Око разума");
        add("entity.carnis.flesh_amalgam", "Амальгама плоти");
        add("item.carnis.amalgam_bile_glob", "Желчь амальгамы");
        add("entity.carnis.amalgam_bile", "Желчь амальгамы");
        add("tooltip.carnis.amalgam_bile_glob", "Едкий органический сгусток.");
        add("subtitles.carnis.amalgam_smash", "Амальгама сотрясает землю");
        add("subtitles.carnis.organic_creak", "Сухожилие хлещет");
        add(
                "item.carnis.flesh_amalgam_spawn_egg",
                "Яйцо призыва амальгамы плоти"
        );
        add(ModItems.PURIFICATION_SERUM.get(), "Очищающая сыворотка");
        add(ModItems.BIO_PURIFIER.get(), "Очищающий огнемёт");
        add(
                ModItems.NEURO_RESONATOR_HELMET.get(),
                "Нейро-резонаторный шлем"
        );
        add(
                "death.attack.bio_purifier",
                "%1$s сожжён биоочистителем"
        );
        add(
                "death.attack.bio_purifier.player",
                "%1$s сожжён биоочистителем игрока %2$s"
        );

        add("subtitles.carnis.phantom_creeper", "Что-то шипит за спиной");
        add("subtitles.carnis.phantom_footsteps", "Шаги хлюпают по плоти");
        add("subtitles.carnis.phantom_whisper", "Коллективный разум шепчет");
        add("subtitles.carnis.pulsing_heart_beat", "Сердце биома бьётся");
        add("subtitles.carnis.synapse_shock", "Нервный столб разряжается");
        add("subtitles.carnis.synapse_rupture", "Нервная ткань разрывается");
        add("subtitles.carnis.digestor_churn", "Желудочный пруд бурлит");
        add("subtitles.carnis.hive_eye_screech", "Око разума визжит");
        add(
                "subtitles.carnis.amalgamation_fuse",
                "Плоть сливается в амальгаму"
        );
        add(
                "subtitles.carnis.bone_deflect",
                "Снаряд рикошетит от кости"
        );
        add(
                "subtitles.carnis.acid_splash",
                "Едкая кислота брызжет"
        );
        add(
                "subtitles.carnis.flesh_amalgam_ambient",
                "Амальгама плоти стонет"
        );
        add(
                "subtitles.carnis.flesh_amalgam_hurt",
                "Амальгама плоти вздрагивает"
        );
        add(
                "subtitles.carnis.flesh_amalgam_death",
                "Амальгама плоти обрушивается"
        );
    }
}
```

## `src/main/resources/assets/carnis/animations/entity/flesh_amalgam.animation.json`

```json
{
  "format_version": "1.8.0",
  "animations": {
    "animation.flesh_amalgam.idle": {
      "loop": true,
      "animation_length": 3.0,
      "bones": {
        "pelvis": {
          "position": {
            "0.0": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            },
            "1.5": {
              "vector": [
                0.0,
                0.35,
                0.0
              ],
              "easing": "easeInOutSine"
            },
            "3.0": {
              "vector": [
                0.0,
                0.0,
                0.0
              ],
              "easing": "easeInOutSine"
            }
          }
        },
        "body": {
          "rotation": {
            "0.0": {
              "vector": [
                0.0,
                0.0,
                -1.5
              ]
            },
            "1.5": {
              "vector": [
                2.0,
                1.5,
                1.5
              ],
              "easing": "easeInOutSine"
            },
            "3.0": {
              "vector": [
                0.0,
                0.0,
                -1.5
              ],
              "easing": "easeInOutSine"
            }
          },
          "scale": {
            "0.0": {
              "vector": [
                1.0,
                1.0,
                1.0
              ]
            },
            "1.5": {
              "vector": [
                1.025,
                1.04,
                1.025
              ],
              "easing": "easeInOutSine"
            },
            "3.0": {
              "vector": [
                1.0,
                1.0,
                1.0
              ],
              "easing": "easeInOutSine"
            }
          }
        },
        "head": {
          "rotation": {
            "0.0": {
              "vector": [
                -2.0,
                -3.0,
                0.0
              ]
            },
            "1.5": {
              "vector": [
                3.0,
                3.0,
                1.5
              ],
              "easing": "easeInOutSine"
            },
            "3.0": {
              "vector": [
                -2.0,
                -3.0,
                0.0
              ],
              "easing": "easeInOutSine"
            }
          }
        },
        "left_arm": {
          "rotation": {
            "0.0": {
              "vector": [
                3.0,
                0.0,
                0.0
              ]
            },
            "1.5": {
              "vector": [
                -3.0,
                0.0,
                -3.0
              ],
              "easing": "easeInOutSine"
            },
            "3.0": {
              "vector": [
                3.0,
                0.0,
                0.0
              ],
              "easing": "easeInOutSine"
            }
          }
        },
        "right_arm": {
          "rotation": {
            "0.0": {
              "vector": [
                -2.0,
                0.0,
                0.0
              ]
            },
            "1.5": {
              "vector": [
                4.0,
                0.0,
                3.0
              ],
              "easing": "easeInOutSine"
            },
            "3.0": {
              "vector": [
                -2.0,
                0.0,
                0.0
              ],
              "easing": "easeInOutSine"
            }
          }
        },
        "left_tendril": {
          "rotation": {
            "0.0": {
              "vector": [
                0.0,
                -3.0,
                0.0
              ]
            },
            "1.5": {
              "vector": [
                5.0,
                4.0,
                4.0
              ],
              "easing": "easeInOutSine"
            },
            "3.0": {
              "vector": [
                0.0,
                -3.0,
                0.0
              ],
              "easing": "easeInOutSine"
            }
          }
        },
        "right_tendril": {
          "rotation": {
            "0.0": {
              "vector": [
                0.0,
                3.0,
                0.0
              ]
            },
            "1.5": {
              "vector": [
                5.0,
                -4.0,
                -5.0
              ],
              "easing": "easeInOutSine"
            },
            "3.0": {
              "vector": [
                0.0,
                3.0,
                0.0
              ],
              "easing": "easeInOutSine"
            }
          }
        },
        "chest_eye": {
          "scale": {
            "0.0": {
              "vector": [
                1.0,
                1.0,
                1.0
              ]
            },
            "1.42": {
              "vector": [
                1.0,
                1.0,
                1.0
              ]
            },
            "1.5": {
              "vector": [
                1.0,
                0.12,
                1.0
              ]
            },
            "1.62": {
              "vector": [
                1.0,
                1.0,
                1.0
              ]
            },
            "3.0": {
              "vector": [
                1.0,
                1.0,
                1.0
              ]
            }
          }
        }
      }
    },
    "animation.flesh_amalgam.walk": {
      "loop": true,
      "animation_length": 1.0,
      "bones": {
        "pelvis": {
          "position": {
            "0.0": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            },
            "0.25": {
              "vector": [
                0.0,
                0.7,
                0.0
              ]
            },
            "0.5": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            },
            "0.75": {
              "vector": [
                0.0,
                0.7,
                0.0
              ]
            },
            "1.0": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            }
          }
        },
        "body": {
          "rotation": {
            "0.0": {
              "vector": [
                4.0,
                -4.0,
                -2.0
              ]
            },
            "0.5": {
              "vector": [
                4.0,
                4.0,
                2.0
              ]
            },
            "1.0": {
              "vector": [
                4.0,
                -4.0,
                -2.0
              ]
            }
          }
        },
        "head": {
          "rotation": {
            "0.0": {
              "vector": [
                -5.0,
                4.0,
                0.0
              ]
            },
            "0.5": {
              "vector": [
                1.0,
                -4.0,
                0.0
              ]
            },
            "1.0": {
              "vector": [
                -5.0,
                4.0,
                0.0
              ]
            }
          }
        },
        "left_leg": {
          "rotation": {
            "0.0": {
              "vector": [
                32.0,
                0.0,
                0.0
              ]
            },
            "0.5": {
              "vector": [
                -32.0,
                0.0,
                0.0
              ]
            },
            "1.0": {
              "vector": [
                32.0,
                0.0,
                0.0
              ]
            }
          }
        },
        "right_leg": {
          "rotation": {
            "0.0": {
              "vector": [
                -32.0,
                0.0,
                0.0
              ]
            },
            "0.5": {
              "vector": [
                32.0,
                0.0,
                0.0
              ]
            },
            "1.0": {
              "vector": [
                -32.0,
                0.0,
                0.0
              ]
            }
          }
        },
        "left_arm": {
          "rotation": {
            "0.0": {
              "vector": [
                -24.0,
                0.0,
                0.0
              ]
            },
            "0.5": {
              "vector": [
                24.0,
                0.0,
                0.0
              ]
            },
            "1.0": {
              "vector": [
                -24.0,
                0.0,
                0.0
              ]
            }
          }
        },
        "right_arm": {
          "rotation": {
            "0.0": {
              "vector": [
                24.0,
                0.0,
                0.0
              ]
            },
            "0.5": {
              "vector": [
                -24.0,
                0.0,
                0.0
              ]
            },
            "1.0": {
              "vector": [
                24.0,
                0.0,
                0.0
              ]
            }
          }
        },
        "left_tendril": {
          "rotation": {
            "0.0": {
              "vector": [
                -8.0,
                0.0,
                -6.0
              ]
            },
            "0.5": {
              "vector": [
                10.0,
                0.0,
                6.0
              ]
            },
            "1.0": {
              "vector": [
                -8.0,
                0.0,
                -6.0
              ]
            }
          }
        },
        "right_tendril": {
          "rotation": {
            "0.0": {
              "vector": [
                12.0,
                0.0,
                -7.0
              ]
            },
            "0.5": {
              "vector": [
                -7.0,
                0.0,
                5.0
              ]
            },
            "1.0": {
              "vector": [
                12.0,
                0.0,
                -7.0
              ]
            }
          }
        }
      }
    },
    "animation.flesh_amalgam.attack": {
      "loop": false,
      "animation_length": 0.3,
      "bones": {
        "pelvis": {
          "position": {
            "0.0": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            },
            "0.1": {
              "vector": [
                0.0,
                -0.6,
                1.0
              ]
            },
            "0.2": {
              "vector": [
                0.0,
                0.4,
                -1.2
              ],
              "easing": "easeOutBack"
            },
            "0.3": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            }
          }
        },
        "body": {
          "rotation": {
            "0.0": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            },
            "0.1": {
              "vector": [
                -14.0,
                0.0,
                0.0
              ]
            },
            "0.2": {
              "vector": [
                19.0,
                0.0,
                0.0
              ],
              "easing": "easeOutQuad"
            },
            "0.3": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            }
          }
        },
        "head": {
          "rotation": {
            "0.0": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            },
            "0.1": {
              "vector": [
                -18.0,
                0.0,
                0.0
              ]
            },
            "0.2": {
              "vector": [
                12.0,
                0.0,
                0.0
              ]
            },
            "0.3": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            }
          }
        },
        "left_arm": {
          "rotation": {
            "0.0": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            },
            "0.1": {
              "vector": [
                -115.0,
                -10.0,
                -10.0
              ]
            },
            "0.2": {
              "vector": [
                62.0,
                12.0,
                4.0
              ],
              "easing": "easeOutExpo"
            },
            "0.3": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            }
          }
        },
        "right_arm": {
          "rotation": {
            "0.0": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            },
            "0.1": {
              "vector": [
                -105.0,
                10.0,
                9.0
              ]
            },
            "0.2": {
              "vector": [
                55.0,
                -12.0,
                -6.0
              ],
              "easing": "easeOutExpo"
            },
            "0.3": {
              "vector": [
                0.0,
                0.0,
                0.0
              ]
            }
          }
        },
        "chest_eye": {
          "scale": {
            "0.0": {
              "vector": [
                1.0,
                1.0,
                1.0
              ]
            },
            "0.1": {
              "vector": [
                1.35,
                1.35,
                1.35
              ]
            },
            "0.2": {
              "vector": [
                1.1,
                1.1,
                1.1
              ]
            },
            "0.3": {
              "vector": [
                1.0,
                1.0,
                1.0
              ]
            }
          }
        }
      }
    },
    "animation.flesh_amalgam.roar": {
      "loop": false,
      "animation_length": 1.1,
      "bones": {
        "body": {
          "rotation": {
            "0": [
              0,
              0,
              0
            ],
            "0.3": [
              -12,
              0,
              0
            ],
            "0.8": [
              -8,
              0,
              0
            ],
            "1.1": [
              0,
              0,
              0
            ]
          }
        },
        "head": {
          "rotation": {
            "0": [
              0,
              0,
              0
            ],
            "0.3": [
              -20,
              0,
              0
            ],
            "0.8": [
              -14,
              0,
              0
            ],
            "1.1": [
              0,
              0,
              0
            ]
          }
        },
        "left_arm": {
          "rotation": {
            "0": [
              0,
              0,
              0
            ],
            "0.4": [
              -20,
              0,
              -18
            ],
            "1.1": [
              0,
              0,
              0
            ]
          }
        },
        "right_arm": {
          "rotation": {
            "0": [
              0,
              0,
              0
            ],
            "0.4": [
              -20,
              0,
              18
            ],
            "1.1": [
              0,
              0,
              0
            ]
          }
        }
      }
    },
    "animation.flesh_amalgam.slam": {
      "loop": false,
      "animation_length": 1.0,
      "bones": {
        "body": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.35": [
              -20,
              0,
              0
            ],
            "0.6": [
              35,
              0,
              0
            ],
            "0.8": [
              15,
              0,
              0
            ],
            "1.0": [
              0,
              0,
              0
            ]
          }
        },
        "left_arm": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.35": [
              -150,
              0,
              -12
            ],
            "0.6": [
              65,
              0,
              -8
            ],
            "0.8": [
              45,
              0,
              -8
            ],
            "1.0": [
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
            "0.35": [
              -150,
              0,
              12
            ],
            "0.6": [
              65,
              0,
              8
            ],
            "0.8": [
              45,
              0,
              8
            ],
            "1.0": [
              0,
              0,
              0
            ]
          }
        },
        "head": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.35": [
              -12,
              0,
              0
            ],
            "0.6": [
              22,
              0,
              0
            ],
            "1.0": [
              0,
              0,
              0
            ]
          }
        },
        "pelvis": {
          "position": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.35": [
              0,
              1,
              0
            ],
            "0.6": [
              0,
              -1.5,
              0
            ],
            "1.0": [
              0,
              0,
              0
            ]
          }
        }
      }
    }
  },
  "geckolib_format_version": 2
}
```

## `src/main/resources/assets/carnis/models/item/amalgam_bile_glob.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "carnis:item/amalgam_bile_glob"
  }
}
```

## `src/main/resources/assets/carnis/sounds.json`

```json
{
  "acid_splash": {
    "subtitle": "subtitles.carnis.acid_splash",
    "sounds": [
      {
        "name": "carnis:entity/acid_splash",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "amalgamation_fuse": {
    "subtitle": "subtitles.carnis.amalgamation_fuse",
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
    "subtitle": "subtitles.carnis.bone_deflect",
    "sounds": [
      {
        "name": "carnis:entity/bone_deflect",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "digestor_churn": {
    "subtitle": "subtitles.carnis.digestor_churn",
    "sounds": [
      {
        "name": "carnis:block/digestor_churn",
        "volume": 0.9,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "flesh_amalgam_ambient": {
    "subtitle": "subtitles.carnis.flesh_amalgam_ambient",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_ambient",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "flesh_amalgam_death": {
    "subtitle": "subtitles.carnis.flesh_amalgam_death",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_death",
        "volume": 1.1,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "flesh_amalgam_hurt": {
    "subtitle": "subtitles.carnis.flesh_amalgam_hurt",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_hurt",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "hive_eye_screech": {
    "subtitle": "subtitles.carnis.hive_eye_screech",
    "sounds": [
      {
        "name": "carnis:block/hive_eye_screech",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "phantom_creeper": {
    "subtitle": "subtitles.carnis.phantom_creeper",
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
    "subtitle": "subtitles.carnis.phantom_footsteps",
    "sounds": [
      {
        "name": "carnis:hallucination/phantom_footsteps",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "phantom_whisper": {
    "subtitle": "subtitles.carnis.phantom_whisper",
    "sounds": [
      {
        "name": "carnis:hallucination/phantom_whisper",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "synapse_rupture": {
    "subtitle": "subtitles.carnis.synapse_rupture",
    "sounds": [
      {
        "name": "carnis:block/synapse_rupture",
        "volume": 1.0,
        "pitch": 1.0,
        "stream": false
      }
    ]
  },
  "amalgam_step": {
    "subtitle": "subtitles.carnis.amalgam_step",
    "sounds": [
      "carnis:entity/amalgam_step"
    ]
  },
  "heartbeat_loop": {
    "subtitle": "subtitles.carnis.heartbeat_loop",
    "sounds": [
      "carnis:block/heartbeat_loop"
    ]
  },
  "amalgam_roar": {
    "subtitle": "subtitles.carnis.amalgam_roar",
    "sounds": [
      {
        "name": "carnis:entity/flesh_amalgam_death",
        "volume": 1.0,
        "pitch": 0.75
      }
    ]
  },
  "flamethrower_fire": {
    "subtitle": "subtitles.carnis.flamethrower_fire",
    "sounds": [
      {
        "name": "carnis:entity/flamethrower_fire",
        "stream": false
      }
    ]
  },
  "synapse_shock": {
    "subtitle": "subtitles.carnis.synapse_shock",
    "sounds": [
      {
        "name": "carnis:block/synapse_rupture",
        "pitch": 1.2
      }
    ]
  },
  "pulsing_heart_beat": {
    "subtitle": "subtitles.carnis.pulsing_heart_beat",
    "sounds": [
      "carnis:block/heartbeat_loop"
    ]
  },
  "item.inoculator.fire": {
    "subtitle": "subtitles.carnis.inoculator_fire",
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
    "subtitle": "subtitles.carnis.dart_hit",
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
    "subtitle": "subtitles.carnis.purifier_ignite",
    "sounds": [
      {
        "name": "carnis:item/purifier_ignite",
        "volume": 1.0,
        "pitch": 1.0
      }
    ]
  },
  "item.purifier.loop": {
    "subtitle": "subtitles.carnis.purifier_loop",
    "sounds": [
      {
        "name": "carnis:item/purifier_loop",
        "volume": 1.0,
        "pitch": 1.0
      }
    ]
  },
  "amalgam_smash": {
    "subtitle": "subtitles.carnis.amalgam_smash",
    "sounds": [
      "carnis:entity/amalgam_smash"
    ]
  },
  "organic_creak": {
    "subtitle": "subtitles.carnis.organic_creak",
    "sounds": [
      "carnis:entity/organic_creak"
    ]
  }
}
```

## `src/main/resources/data/carnis/loot_tables/entities/flesh_amalgam.json`

```json
{
  "type": "minecraft:entity",
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "carnis:living_flesh",
          "functions": [
            {
              "function": "minecraft:set_count",
              "count": {
                "type": "minecraft:uniform",
                "min": 8,
                "max": 16
              }
            }
          ]
        }
      ]
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "carnis:ossified_flesh",
          "functions": [
            {
              "function": "minecraft:set_count",
              "count": {
                "type": "minecraft:uniform",
                "min": 4,
                "max": 8
              }
            }
          ]
        }
      ]
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "carnis:biomass_remains",
          "functions": [
            {
              "function": "minecraft:set_count",
              "count": {
                "type": "minecraft:uniform",
                "min": 4,
                "max": 8
              }
            }
          ]
        }
      ]
    }
  ]
}
```

