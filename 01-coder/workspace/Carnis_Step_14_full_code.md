# Шаг 14 — полные исходные файлы

Запрошенные четыре класса и связанные классы представлены целиком.

## `src/main/java/com/carnis/mod/entity/HivemindLinkedMob.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;

/** Shared server-side swarm contract for entities that are also vanilla mobs. */
public interface HivemindLinkedMob {
    default void alertTarget(LivingEntity target) {
        if (this instanceof Mob mob) HiveSwarmCoordinator.alertTarget(mob, target);
    }
    default void triggerFrenzy(int durationTicks) {
        if (this instanceof Mob mob) HiveSwarmCoordinator.triggerFrenzy(mob, durationTicks);
    }
    default boolean isFrenzied() {
        return this instanceof Mob mob && HiveSwarmCoordinator.isFrenzied(mob);
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/HiveSwarmCoordinator.java`

```java
package com.carnis.mod.entity.ai;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.AssimilatingMob;
import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.UUID;

/** Server-authoritative coordination. Broadcasts never recursively relay themselves. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HiveSwarmCoordinator {
    public static final String DEFENSE_POS = "carnis:swarm_defense_pos";
    public static final String DEFENSE_UNTIL = "carnis:swarm_defense_until";
    public static final String DEFENSE_DIM = "carnis:swarm_defense_dim";
    private static final String FRENZY_UNTIL = "carnis:frenzy_until";
    private static final String FRENZY_DIM = "carnis:frenzy_dim";
    private static final String LAST_ALARM_POS = "carnis:last_hive_alarm_pos";
    private static final String LAST_ALARM_TICK = "carnis:last_hive_alarm_tick";
    private static final String LAST_ALARM_DIM = "carnis:last_hive_alarm_dim";
    private static final UUID SPEED_ID = UUID.fromString("322fcbde-4022-41f2-ae54-5f416537a4db");
    private static final AttributeModifier SPEED = new AttributeModifier(SPEED_ID, "Carnis swarm frenzy", 0.20D,
            AttributeModifier.Operation.MULTIPLY_TOTAL);
    private static final ThreadLocal<Boolean> BROADCASTING = ThreadLocal.withInitial(() -> false);
    private HiveSwarmCoordinator() { }

    private static String dimension(ServerLevel level) { return level.dimension().location().toString(); }
    public static boolean validTarget(Mob mob, LivingEntity target) {
        if (target == null || target == mob || !target.isAlive() || target.isSpectator()
                || target.level() != mob.level() || target instanceof HivemindLinkedMob
                || NeuroArmorEventHandler.isHiveEntity(target)) return false;
        if (target instanceof Player player && (player.isCreative() || PlayerInfectionApi.isAssimilated(player)
                || NeuroArmorEventHandler.hasFullSet(player) && !NeuroArmorEventHandler.isProvoked(player))) return false;
        return mob.canAttack(target);
    }

    public static void alertTarget(Mob mob, LivingEntity target) {
        if (!(mob.level() instanceof ServerLevel) || !mob.isAlive() || !validTarget(mob, target)) return;
        if (mob.getTarget() == target) return;
        // Interrupt feeding so it cannot clear the alarm target on its next tick.
        mob.getPersistentData().remove(CarnisFeedingGoal.DEADLINE);
        mob.getPersistentData().remove("carnis:feeding_travel");
        if (mob instanceof AssimilatingMob assimilating) assimilating.setAssimilating(false);
        mob.setTarget(target);
    }
    public static void triggerFrenzy(Mob mob, int durationTicks) {
        if (!(mob.level() instanceof ServerLevel level) || !mob.isAlive() || durationTicks <= 0) return;
        CompoundTag tag = mob.getPersistentData();
        long until = level.getGameTime() + (long) durationTicks;
        if (dimension(level).equals(tag.getString(FRENZY_DIM))) until = Math.max(until, tag.getLong(FRENZY_UNTIL));
        tag.putLong(FRENZY_UNTIL, until);
        tag.putString(FRENZY_DIM, dimension(level));
        updateSpeed(mob, true);
    }
    public static boolean isFrenzied(Mob mob) {
        if (!(mob.level() instanceof ServerLevel level)) return false;
        CompoundTag tag = mob.getPersistentData();
        return dimension(level).equals(tag.getString(FRENZY_DIM)) && tag.getLong(FRENZY_UNTIL) > level.getGameTime();
    }
    private static void updateSpeed(Mob mob, boolean active) {
        AttributeInstance speed = mob.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed == null) return;
        boolean present = speed.getModifier(SPEED_ID) != null;
        if (active && !present) speed.addTransientModifier(SPEED);
        else if (!active && present) speed.removeModifier(SPEED_ID);
    }
    @SubscribeEvent
    public static void onLivingTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || !(mob instanceof HivemindLinkedMob)
                || !(mob.level() instanceof ServerLevel level)) return;
        boolean active = mob.isAlive() && isFrenzied(mob);
        updateSpeed(mob, active);
        if (!active) {
            mob.getPersistentData().remove(FRENZY_UNTIL);
            mob.getPersistentData().remove(FRENZY_DIM);
        } else if (mob.tickCount % 10 == 0) {
            level.sendParticles(ModParticles.BIOMASS_SPARK.get(), mob.getX(), mob.getY(0.55D), mob.getZ(),
                    3, mob.getBbWidth() * .35D, mob.getBbHeight() * .3D, mob.getBbWidth() * .35D, .01D);
        }
    }
    private static void issueDefense(Mob mob, ServerLevel level, BlockPos pos) {
        CompoundTag tag = mob.getPersistentData();
        tag.putLong(DEFENSE_POS, pos.asLong());
        tag.putLong(DEFENSE_UNTIL, level.getGameTime() + 400L);
        tag.putString(DEFENSE_DIM, dimension(level));
    }
    public static BlockPos defensePosition(Mob mob) {
        if (!(mob.level() instanceof ServerLevel level)) return null;
        CompoundTag tag = mob.getPersistentData();
        if (!tag.contains(DEFENSE_POS) || !dimension(level).equals(tag.getString(DEFENSE_DIM))
                || tag.getLong(DEFENSE_UNTIL) <= level.getGameTime()) return null;
        return BlockPos.of(tag.getLong(DEFENSE_POS));
    }
    public static void clearDefense(Mob mob) {
        mob.getPersistentData().remove(DEFENSE_POS);
        mob.getPersistentData().remove(DEFENSE_UNTIL);
        mob.getPersistentData().remove(DEFENSE_DIM);
    }
    private static void broadcast(ServerLevel level, Vec3 center, double radius, LivingEntity target,
                                  boolean onlyFree, boolean frenzy, BlockPos defense) {
        if (BROADCASTING.get()) return;
        BROADCASTING.set(true);
        try {
            AABB area = AABB.ofSize(center, radius * 2, radius * 2, radius * 2);
            for (Mob mob : level.getEntitiesOfClass(Mob.class, area,
                    m -> m instanceof HivemindLinkedMob && m.isAlive()
                            && m.position().distanceToSqr(center) <= radius * radius)) {
                HivemindLinkedMob linked = (HivemindLinkedMob) mob;
                if (frenzy) linked.triggerFrenzy(400);
                if (defense != null) issueDefense(mob, level, defense);
                boolean occupied = mob.getTarget() != null && mob.getTarget().isAlive()
                        || mob.getPersistentData().contains(CarnisFeedingGoal.DEADLINE);
                if (!onlyFree || !occupied) linked.alertTarget(target);
            }
        } finally { BROADCASTING.remove(); }
    }
    public static void eyeAlarm(ServerLevel level, BlockPos eye, LivingEntity intruder) {
        broadcast(level, Vec3.atCenterOf(eye), 28.0D, intruder, true, false, null);
    }
    private static void defend(ServerLevel level, Vec3 center, BlockPos pos, LivingEntity intruder, boolean frenzy) {
        broadcast(level, center, 36.0D, intruder, false, frenzy, pos);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onHurt(LivingHurtEvent event) {
        if (event.isCanceled() || event.getAmount() <= 0 || !(event.getEntity().level() instanceof ServerLevel level)) return;
        Entity source = event.getSource().getEntity();
        if (event.getEntity() instanceof CerebralNexusEntity nexus && source instanceof LivingEntity attacker
                && validTarget(nexus, attacker)) {
            defend(level, nexus.position(), nexus.blockPosition(), attacker, false);
            return;
        }
        if (event.getEntity() instanceof Mob victim && victim instanceof HivemindLinkedMob
                && source instanceof LivingEntity attacker && validTarget(victim, attacker)) {
            broadcast(level, victim.position(), 20.0D, attacker, false, false, null);
        } else if (source instanceof Mob attacker && attacker instanceof HivemindLinkedMob
                && validTarget(attacker, event.getEntity())) {
            broadcast(level, attacker.position(), 20.0D, event.getEntity(), false, false, null);
        }
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onTargetChange(LivingChangeTargetEvent event) {
        if (event.isCanceled() || BROADCASTING.get() || !(event.getEntity() instanceof Mob mob)
                || !(mob instanceof HivemindLinkedMob) || !(mob.level() instanceof ServerLevel level)
                || event.getNewTarget() == null || !validTarget(mob, event.getNewTarget())) return;
        broadcast(level, mob.position(), 20.0D, event.getNewTarget(), false, false, null);
    }
    private static boolean keyOrgan(BlockState state) {
        return state.is(ModBlocks.PULSING_HEART.get()) || state.is(ModBlocks.HIVE_EYE.get())
                || state.is(ModBlocks.STOMACH_POOL.get()) || state.is(ModBlocks.NERVE_PILLAR.get());
    }
    private static void organAttacked(ServerLevel level, BlockPos pos, Player player) {
        if (!player.isAlive() || player.isSpectator() || player.isCreative()) return;
        CompoundTag tag = player.getPersistentData();
        long now = level.getGameTime();
        boolean duplicate = tag.contains(LAST_ALARM_TICK) && tag.getLong(LAST_ALARM_POS) == pos.asLong()
                && dimension(level).equals(tag.getString(LAST_ALARM_DIM))
                && now >= tag.getLong(LAST_ALARM_TICK) && now - tag.getLong(LAST_ALARM_TICK) < 8;
        NeuroArmorEventHandler.provoke(player);
        if (duplicate) return;
        tag.putLong(LAST_ALARM_POS, pos.asLong());
        tag.putLong(LAST_ALARM_TICK, now);
        tag.putString(LAST_ALARM_DIM, dimension(level));
        BlockPos rally = level.getBlockState(pos).is(ModBlocks.PULSING_HEART.get()) ? pos : null;
        defend(level, Vec3.atCenterOf(pos), rally, player, true);
        level.playSound(null, pos, ModSounds.PHANTOM_WHISPER.get(), SoundSource.HOSTILE, 2.0F, .6F);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onStartBreaking(PlayerInteractEvent.LeftClickBlock event) {
        if (event.isCanceled() || event.getAction() != PlayerInteractEvent.LeftClickBlock.Action.START
                || !(event.getLevel() instanceof ServerLevel level) || !keyOrgan(level.getBlockState(event.getPos()))) return;
        organAttacked(level, event.getPos(), event.getEntity());
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onBreak(BlockEvent.BreakEvent event) {
        if (event.isCanceled() || !(event.getLevel() instanceof ServerLevel level) || !keyOrgan(event.getState())) return;
        organAttacked(level, event.getPos(), event.getPlayer());
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
        if (!(mob.level() instanceof ServerLevel) || !mob.isAlive()) return false;
        destination = HiveSwarmCoordinator.defensePosition(mob);
        if (destination == null) { HiveSwarmCoordinator.clearDefense(mob); return false; }
        // Once near the threatened location, hand control back to normal combat.
        return farFromDefense() && !enemyClose();
    }
    @Override public boolean canContinueToUse() {
        BlockPos current = HiveSwarmCoordinator.defensePosition(mob);
        return mob.isAlive() && current != null && current.equals(destination)
                && farFromDefense() && !enemyClose();
    }
    private boolean farFromDefense() {
        return mob.distanceToSqr(destination.getX() + .5D, destination.getY() + .5D, destination.getZ() + .5D) > 36.0D;
    }
    private boolean enemyClose() {
        return mob.getTarget() != null && mob.getTarget().isAlive() && mob.distanceToSqr(mob.getTarget()) <= 36.0D;
    }
    @Override public void start() { repath = 0; }
    @Override public void stop() { mob.getNavigation().stop(); destination = null; }
    @Override public void tick() {
        if (destination == null || !(mob.level() instanceof ServerLevel level)) return;
        if (--repath <= 0) {
            repath = 20;
            // A removed heart is still a useful rally point. No chunk is loaded by this goal.
            if (level.hasChunkAt(destination))
                mob.getNavigation().moveTo(destination.getX() + .5D, destination.getY(), destination.getZ() + .5D, 1.15D);
        }
        if (mob.getTarget() != null) mob.getLookControl().setLookAt(mob.getTarget(), 30.0F, 30.0F);
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
        return available() && leader != null && leader.isAlive() && leader.level() == mob.level()
                && mob.distanceToSqr(leader) <= SEARCH_RADIUS * SEARCH_RADIUS;
    }
    @Override public void start() { repath = 0; }
    @Override public void stop() { mob.getNavigation().stop(); leader = null; }
    @Override public void tick() {
        if (leader == null || --repath > 0) return;
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

## `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

import java.lang.ref.WeakReference;

public final class HiveEyeBlockEntity extends BlockEntity implements software.bernie.geckolib.animatable.GeoBlockEntity {
    private final software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache animationCache =
            software.bernie.geckolib.util.GeckoLibUtil.createInstanceCache(this);

    @Override
    public software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }

    @Override
    public void registerControllers(software.bernie.geckolib.core.animation.AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this, "idle", 0,
                state -> state.setAndContinue(software.bernie.geckolib.core.animation.RawAnimation.begin()
                        .thenLoop("animation.hive_eye.idle"))));
    }

    public static final int SCAN_INTERVAL_TICKS = 20;
    public static final double PLAYER_SCAN_RADIUS = 24.0D;
    public static final double HIVEMIND_ALERT_RADIUS = 28.0D;
    private WeakReference<LivingEntity> lastDetectedTarget = new WeakReference<>(null);

    public HiveEyeBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.HIVE_EYE.get(), pos, state);
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, HiveEyeBlockEntity eye) {
        if (level instanceof ServerLevel serverLevel
                && Math.floorMod(serverLevel.getGameTime() + Math.floorMod(pos.asLong(), SCAN_INTERVAL_TICKS),
                        SCAN_INTERVAL_TICKS) == 0L) {
            eye.scan(serverLevel);
        }
    }

    private void scan(ServerLevel level) {
        com.carnis.mod.world.HiveNetwork.observe(level, worldPosition, getBlockState(), true);
        Vec3 center = Vec3.atCenterOf(worldPosition);
        AABB search = AABB.ofSize(center, PLAYER_SCAN_RADIUS * 2.0D,
                PLAYER_SCAN_RADIUS * 2.0D, PLAYER_SCAN_RADIUS * 2.0D);
        LivingEntity nearest = null;
        double closest = PLAYER_SCAN_RADIUS * PLAYER_SCAN_RADIUS;
        for (LivingEntity candidate : level.getEntitiesOfClass(LivingEntity.class, search, HiveEyeBlockEntity::isTarget)) {
            double distance = candidate.position().distanceToSqr(center);
            if (candidate instanceof Player player
                    && com.carnis.mod.event.NeuroArmorEventHandler.hiddenFromSensor(player, distance)) continue;
            if (distance <= closest) {
                nearest = candidate;
                closest = distance;
            }
        }
        if (nearest == null) {
            lastDetectedTarget.clear();
            return;
        }
        if (nearest != lastDetectedTarget.get()) {
            level.playSound(null, worldPosition, ModSounds.HIVE_EYE_SCREECH.get(),
                    SoundSource.BLOCKS, 1.25F, 0.92F);
            level.sendParticles(ParticleTypes.ELECTRIC_SPARK, center.x, center.y + 0.5D, center.z,
                    12, 0.25D, 0.2D, 0.25D, 0.02D);
            lastDetectedTarget = new WeakReference<>(nearest);
        }
        nearest.addEffect(new MobEffectInstance(MobEffects.GLOWING, 100, 0));
        com.carnis.mod.entity.ai.HiveSwarmCoordinator.eyeAlarm(level, worldPosition, nearest);
    }

    private static boolean isTarget(LivingEntity entity) {
        if (!entity.isAlive() || entity.isSpectator() || entity instanceof HivemindLinkedMob) {
            return false;
        }
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
        if (id != null && CarnisMod.MOD_ID.equals(id.getNamespace())) {
            return false;
        }
        if (entity instanceof Player player) {
            return !player.isCreative() && PlayerInfectionApi.getInfectionLevel(player) <= 0.0F;
        }
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/entity/InfectedZombieEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedZombieEntity extends Zombie implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedZombieEntity.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_zombie.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_zombie.walk");
    private static final RawAnimation ASSIMILATE = RawAnimation.begin().thenLoop("animation.infected_zombie.assimilate");
    private static final RawAnimation PULSE = RawAnimation.begin().thenLoop("animation.infected_zombie.pulsing");
    private static final RawAnimation ATTACK = RawAnimation.begin().thenPlay("animation.infected_zombie.attack");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedZombieEntity(EntityType<? extends Zombie> type, Level level) {
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
        super.registerGoals();
        goalSelector.addGoal(0, new com.carnis.mod.entity.ai.goal.HiveDefendHeartGoal(this));
        goalSelector.addGoal(4, new com.carnis.mod.entity.ai.goal.HiveEscortLeaderGoal(this));
        goalSelector.addGoal(1, new CarnisFeedingGoal(this));
        goalSelector.addGoal(2, new CarnisGestationGoal(this));
        targetSelector.addGoal(3, new CarnisHuntPreyGoal(this));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Zombie.createAttributes().add(Attributes.MAX_HEALTH, 35.0D)
                .add(Attributes.ATTACK_DAMAGE, 4.5D);
    }

    @Override
    protected boolean isSunSensitive() {
        return false;
    }

    @Override
    protected boolean convertsInWater() {
        return false;
    }
}
```

## `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.monster.AbstractSkeleton;
import net.minecraft.world.entity.monster.Skeleton;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedSkeletonEntity extends Skeleton implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_skeleton.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_skeleton.walk");
    private static final RawAnimation HEARTBEAT = RawAnimation.begin().thenLoop("animation.infected_skeleton.heartbeat");
    private static final RawAnimation WHIRLWIND = RawAnimation.begin().thenPlay("animation.infected_skeleton.attack_whirlwind");
    private static final net.minecraft.network.syncher.EntityDataAccessor<Boolean> ASSIMILATING =
            net.minecraft.network.syncher.SynchedEntityData.defineId(InfectedSkeletonEntity.class,
                    net.minecraft.network.syncher.EntityDataSerializers.BOOLEAN);

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
    }

    @Override
    public boolean isAssimilating() { return entityData.get(ASSIMILATING); }

    @Override
    public void setAssimilating(boolean assimilating) { entityData.set(ASSIMILATING, assimilating); }

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedSkeletonEntity(EntityType<? extends Skeleton> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return AbstractSkeleton.createAttributes().add(Attributes.MAX_HEALTH, 28.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.33D).add(Attributes.ATTACK_DAMAGE, 4.5D);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 2,
                state -> state.setAndContinue(isAssimilating()
                        ? RawAnimation.begin().thenLoop("animation.infected_skeleton.assimilate")
                        : state.isMoving() ? WALK : IDLE)));
        controllers.add(new AnimationController<>(this, "heartbeat", 0,
                state -> isAssimilating() ? PlayState.STOP : state.setAndContinue(HEARTBEAT)));
        controllers.add(new AnimationController<>(this, "action", 0, state -> {
            if (!isAssimilating() && swinging) return state.setAndContinue(WHIRLWIND);
            state.getController().forceAnimationReset();
            return PlayState.STOP;
        }));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() { return geoCache; }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        goalSelector.addGoal(0, new com.carnis.mod.entity.ai.goal.HiveDefendHeartGoal(this));
        goalSelector.addGoal(4, new com.carnis.mod.entity.ai.goal.HiveEscortLeaderGoal(this));
        goalSelector.addGoal(1, new CarnisFeedingGoal(this));
        goalSelector.addGoal(2, new CarnisGestationGoal(this));
        goalSelector.addGoal(4, new MeleeAttackGoal(this, 1.2D, false));
        targetSelector.addGoal(3, new CarnisHuntPreyGoal(this));
    }

    @Override
    public void reassessWeaponGoal() {
        // Suppress vanilla bow and weapon-based attack goals, including on equipment changes.
    }

    @Override
    protected void populateDefaultEquipmentSlots(RandomSource random, DifficultyInstance difficulty) {
        // The scythe is part of the arm geometry; do not equip a separate weapon or bow.
    }

    @Override
    public boolean doHurtTarget(Entity primary) {
        boolean hit = super.doHurtTarget(primary);
        if (!hit || !(level() instanceof ServerLevel server) || !(primary instanceof LivingEntity)) return hit;
        Vec3 forward = primary.position().subtract(position()).multiply(1, 0, 1);
        if (forward.lengthSqr() < 1.0E-6D) return hit;
        forward = forward.normalize();
        for (LivingEntity other : server.getEntitiesOfClass(LivingEntity.class,
                getBoundingBox().inflate(3.5D, 1.5D, 3.5D),
                target -> target != this && target != primary && target.isAlive() && !target.isSpectator()
                        && !(target instanceof HivemindLinkedMob)
                        && (!(target instanceof Player player) || !PlayerInfectionApi.isAssimilated(player))
                        && canAttack(target))) {
            Vec3 delta = other.position().subtract(position()).multiply(1, 0, 1);
            if (delta.lengthSqr() <= 12.25D && delta.lengthSqr() > 1.0E-6D
                    && forward.dot(delta.normalize()) >= 0.5D && hasLineOfSight(other)) {
                other.hurt(server.damageSources().mobAttack(this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE));
            }
        }
        return hit;
    }
}
```

## `src/main/java/com/carnis/mod/event/NeuroArmorEventHandler.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.item.armor.NeuroArmorItem;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NeuroArmorEventHandler {
    private static final EquipmentSlot[] SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
    private static final String PROVOKED_UNTIL = "carnis:neuro_provoked_until";
    private static final String PROVOKED_DIMENSION = "carnis:neuro_provoked_dimension";
    private static final int PROVOCATION_TICKS = 600;
    private NeuroArmorEventHandler() { }

    private static boolean piece(LivingEntity entity, EquipmentSlot slot, ArmorItem.Type expected) {
        ItemStack stack = entity.getItemBySlot(slot);
        return stack.getItem() instanceof NeuroArmorItem armor && armor.getType() == expected;
    }
    public static boolean hasHelmet(LivingEntity entity) { return piece(entity, EquipmentSlot.HEAD, ArmorItem.Type.HELMET); }
    public static boolean hasSymbioticPair(LivingEntity entity) {
        return piece(entity, EquipmentSlot.CHEST, ArmorItem.Type.CHESTPLATE)
                && piece(entity, EquipmentSlot.LEGS, ArmorItem.Type.LEGGINGS);
    }
    public static int pieces(LivingEntity entity) {
        int count = 0;
        for (EquipmentSlot slot : SLOTS) {
            ItemStack stack = entity.getItemBySlot(slot);
            if (stack.getItem() instanceof NeuroArmorItem armor && armor.getEquipmentSlot() == slot) count++;
        }
        return count;
    }
    public static boolean hasFullSet(LivingEntity entity) { return pieces(entity) == 4; }
    public static boolean isHiveEntity(Entity entity) {
        if (!(entity instanceof LivingEntity)) return false;
        if (entity instanceof HivemindLinkedMob) return true;
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
        return id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }
    public static void provoke(Player player) {
        player.getPersistentData().putLong(PROVOKED_UNTIL, player.level().getGameTime() + PROVOCATION_TICKS);
        player.getPersistentData().putString(PROVOKED_DIMENSION, player.level().dimension().location().toString());
    }
    public static boolean isProvoked(Player player) {
        return player.level().dimension().location().toString().equals(player.getPersistentData().getString(PROVOKED_DIMENSION))
                && player.level().getGameTime() < player.getPersistentData().getLong(PROVOKED_UNTIL);
    }
    /** Eye-like sensors can detect an unprovoked disguised player at four blocks or closer. */
    public static boolean hiddenFromSensor(Player player, double distanceSquared) {
        return hasFullSet(player) && !isProvoked(player) && distanceSquared > 16.0D;
    }
    private static boolean hiddenFromMob(Player player) { return hasFullSet(player) && !isProvoked(player); }

    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onHurt(LivingHurtEvent event) {
        if (event.isCanceled() || event.getEntity().level().isClientSide) return;
        Entity attacker = event.getSource().getEntity();
        if (attacker instanceof Player player && isHiveEntity(event.getEntity()) && event.getAmount() > 0) provoke(player);
        if (event.getEntity() instanceof Player player && isHiveEntity(attacker)) {
            event.setAmount(event.getAmount() * (1.0F - 0.08F * pieces(player)));
        }
    }
    @SubscribeEvent
    public static void onTargetChange(LivingChangeTargetEvent event) {
        if (!event.getEntity().level().isClientSide && isHiveEntity(event.getEntity())
                && event.getNewTarget() instanceof Player player && hiddenFromMob(player)) event.setCanceled(true);
    }
    @SubscribeEvent
    public static void onLivingTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide || !isHiveEntity(mob)) return;
        if (mob.getTarget() instanceof Player player && hiddenFromMob(player)) mob.setTarget(null);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onBreak(BlockEvent.BreakEvent event) {
        if (event.isCanceled() || event.getPlayer().level().isClientSide || !hasFullSet(event.getPlayer())) return;
        BlockState state = event.getState();
        if (!state.is(ModBlocks.LIVING_FLESH.get()) && !state.is(ModBlocks.OSSIFIED_FLESH.get())
                && !state.is(ModBlocks.FIREPROOF_FLESH.get()) && !state.is(ModBlocks.FLESH_VEINS.get())
                && !state.is(ModBlocks.BIOMASS_REMAINS.get())) return;
        Player player = event.getPlayer();
        BlockPos pos = event.getPos();
        var nearby = player.level().getEntitiesOfClass(Mob.class, new AABB(pos).inflate(12.0D),
                mob -> mob.isAlive() && isHiveEntity(mob) && mob.distanceToSqr(pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D) <= 144.0D);
        if (nearby.isEmpty()) return;
        provoke(player);
        for (Mob mob : nearby) if (mob.canAttack(player)) mob.setTarget(player);
    }
    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.player.level().isClientSide) return;
        Player player = event.player;
        if (!player.isAlive() || player.isSpectator() || !player.onGround() || !hasSymbioticPair(player)
                || player.tickCount % 60 != 0 || player.getHealth() >= player.getMaxHealth()) return;
        if (player.getBlockStateOn().is(ModBlocks.LIVING_FLESH.get())) player.heal(1.0F);
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

    public CarnisFeedingGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        return mob.isAlive() && mob.level() instanceof ServerLevel
                && mob.getPersistentData().contains(DEADLINE);
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
        if (!(mob.level() instanceof ServerLevel level)) return;
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
            feedingYaw = mob.getYRot();
            facingLocked = true;
        }
        mob.setYRot(feedingYaw);
        mob.setYHeadRot(feedingYaw);
        mob.setYBodyRot(feedingYaw);
        mob.setXRot(0.0F);
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
            setAssimilating(false);
            facingLocked = false;
            CarnisWorldData.get(level).addBiomassPoints(50L);
            ModMessages.sendToPlayersInLevel(level);
        } else {
            tag.putInt(DEADLINE, tag.getInt(DEADLINE) + 1);
        }
    }

    private void setAssimilating(boolean value) {
        if (mob instanceof AssimilatingMob assimilatingMob) {
            assimilatingMob.setAssimilating(value);
        }
    }
}
```

## `src/main/java/com/carnis/mod/entity/HiveSentinelEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.event.HypnosisEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.animal.Pig;
import net.minecraft.world.entity.animal.Sheep;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class HiveSentinelEntity extends Monster implements GeoEntity, HivemindLinkedMob {
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.hive_sentinel.idle");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private BlockPos heartPos;
    public HiveSentinelEntity(EntityType<? extends Monster> type, Level level) { super(type, level); setNoGravity(true); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 60.0D)
                .add(Attributes.ARMOR, 8.0D).add(Attributes.KNOCKBACK_RESISTANCE, 1.0D).add(Attributes.MOVEMENT_SPEED, 0.0D);
    }
    public void setHeartPos(BlockPos pos) { heartPos = pos.immutable(); }
    @Override public boolean isPushable() { return false; }
    @Override public void push(double x, double y, double z) { }
    @Override protected void registerGoals() { }
    @Override public void tick() {
        super.tick();
        setDeltaMovement(0, 0, 0);
        if (!(level() instanceof ServerLevel server) || !isAlive() || tickCount % 20 != 0) return;
        if (tickCount % 100 == 0) server.playSound(null, blockPosition(), ModSounds.PHANTOM_WHISPER.get(), SoundSource.HOSTILE, 0.9F, .65F);
        BlockPos pool = heartPos == null ? null : HiveNetwork.nearestLoaded(server, HiveNetwork.Kind.POOL, heartPos, 32);
        AABB area = getBoundingBox().inflate(16.0D);
        for (var animal : server.getEntitiesOfClass(net.minecraft.world.entity.animal.Animal.class, area,
                a -> (a instanceof Cow || a instanceof Sheep || a instanceof Pig) && a.isAlive()
                        && a.distanceToSqr(this) <= 256.0D && !InfectionHandler.isInfected(a))) {
            HypnosisEvents.apply(animal, server, pool);
        }
    }
    @Override public void die(net.minecraft.world.damagesource.DamageSource source) {
        if (level() instanceof ServerLevel server && heartPos != null) {
            HiveNetwork.get(server).noteSentinelDeath(getUUID());
            if (server.hasChunkAt(heartPos) && server.getBlockEntity(heartPos) instanceof PulsingHeartBlockEntity heart)
                heart.sentinelDied(getUUID());
        }
        super.die(source);
    }
    @Override public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag); if (heartPos != null) tag.putLong("HiveHeart", heartPos.asLong());
    }
    @Override public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag); if (tag.contains("HiveHeart")) heartPos = BlockPos.of(tag.getLong("HiveHeart"));
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "idle", 0, state -> state.setAndContinue(IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
```

## `src/main/java/com/carnis/mod/entity/CerebralNexusEntity.java`

```java
package com.carnis.mod.entity;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/** Tier-two command node; later tier mechanics are intentionally not defined here. */
public final class CerebralNexusEntity extends Monster implements GeoEntity, HivemindLinkedMob {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private long biomass;
    public CerebralNexusEntity(EntityType<? extends Monster> type, Level level) { super(type, level); setNoGravity(true); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 120D).add(Attributes.ARMOR, 10D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1D).add(Attributes.MOVEMENT_SPEED, 0D);
    }
    public void setBiomass(long value) { biomass = Math.max(0L, value); }
    @Override public boolean isPushable() { return false; }
    @Override public void push(double x, double y, double z) { }
    @Override protected void registerGoals() { }
    @Override public void tick() { super.tick(); setDeltaMovement(0, 0, 0); }
    @Override public void addAdditionalSaveData(CompoundTag tag) { super.addAdditionalSaveData(tag); tag.putLong("Biomass", biomass); }
    @Override public void readAdditionalSaveData(CompoundTag tag) { super.readAdditionalSaveData(tag); biomass = Math.max(0, tag.getLong("Biomass")); }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "idle", 0, state -> state.setAndContinue(RawAnimation.begin().thenLoop("animation.cerebral_nexus.idle"))));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
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

## `src/main/java/com/carnis/mod/init/ModParticles.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES =
            DeferredRegister.create(ForgeRegistries.PARTICLE_TYPES, CarnisMod.MOD_ID);
    public static final RegistryObject<SimpleParticleType> BIOMASS_SPARK =
            PARTICLES.register("biomass_spark", () -> new SimpleParticleType(false));

    public static final RegistryObject<SimpleParticleType> PURIFIER_FLAME =
            PARTICLES.register("purifier_flame", () -> new SimpleParticleType(false));

    private ModParticles() { }

    public static void register(IEventBus bus) {
        PARTICLES.register(bus);
    }
}
```

