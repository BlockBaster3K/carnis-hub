# Carnis 3.4.2 — ревизия

> Актуальные исходники после фиксов атрибутов, точной награды биомассой, распознавания улья и переноса AI goals в единый пакет `com.carnis.mod.entity.ai`. `sounds.json` не изменялся.

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

    /** Base biomass value; CarnisEvents applies the fixed hive assimilation multiplier. */
    public long getBiomassValue() {
        return 1L;
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

## `src/main/java/com/carnis/mod/event/CarnisEvents.java`

```java

package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.biomass.PlayerBiomassCapability;
import com.carnis.mod.capability.biomass.PlayerBiomassEvents;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.AssimilatingMob;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
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
        if (victim instanceof InfectedZombieEntity infectedZombie) {
            // Hive zombies have a fixed three-point reward: base value 1 × hive multiplier 3.
            // Their built-in hive status does not receive the unrelated infection-stage bonus.
            total = infectedZombie.getBiomassValue() * 3L;
        } else {
            long multiplier = 1L;
            if (InfectionHandler.isInfected(victim)) multiplier *= 2L;
            if (victim instanceof AssimilatingMob) multiplier *= 3L;
            total = basePoints(victim) * multiplier;
        }

        if (recipient != null) {
            ServerPlayer player = recipient;
            var biomass = player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS);
            if (!biomass.isPresent()) {
                CarnisMod.LOGGER.warn("Не удалось начислить биомассу игроку {}: Capability отсутствует", player.getUUID());
                return;
            }
            biomass.ifPresent(data -> {
                data.addBiomassPoints(total);
                PlayerBiomassEvents.syncToPlayer(player);
            });
        } else {
            CarnisWorldData data = CarnisWorldData.get(level);
            data.addBiomassPoints(total);
            ModMessages.sendToPlayersInLevel(level);
        }
    }

    private static long basePoints(LivingEntity victim) {
        if (victim instanceof InfectedZombieEntity infectedZombie) return infectedZombie.getBiomassValue();
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

## `src/main/java/com/carnis/mod/event/ModEntityEvents.java`

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

## `src/main/java/com/carnis/mod/entity/HiveEntityAttributes.java`

```java

package com.carnis.mod.entity;

import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;

/**
 * Базовые атрибуты для сущностей улья.
 * Каждая конкретная сущность создаёт СВОЙ createAttributes(),
 * НЕ вызывая этот метод напрямую для registration.
 */
public final class HiveEntityAttributes {
    private HiveEntityAttributes() { }

    public static AttributeSupplier.Builder create() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 20.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.23D)
                .add(Attributes.ATTACK_DAMAGE, 3.0D)
                .add(Attributes.FOLLOW_RANGE, 32.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.05D);
    }
}


```

## `src/main/java/com/carnis/mod/entity/ai/HiveDefendHeartGoal.java`

```java

package com.carnis.mod.entity.ai;

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

## `src/main/java/com/carnis/mod/entity/ai/HiveEscortLeaderGoal.java`

```java

package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HiveSentinelEntity;
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
mod_version=3.4.2
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

## `src/main/java/com/carnis/mod/block/NeuralMossBlock.java` — hive-check method

```java

    public static boolean isHive(Entity entity) {
        return entity instanceof HiveEntity || entity instanceof HivemindLinkedMob || entity.getType().is(HIVE_MEMBERS);
    }

```

## `src/main/java/com/carnis/mod/event/NeuroArmorEventHandler.java` — hive-check method

```java

    public static boolean isHiveEntity(Entity entity) {
        if (!(entity instanceof LivingEntity)) return false;
        if (entity instanceof HiveEntity || entity instanceof HivemindLinkedMob) return true;
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
        return id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }

```
