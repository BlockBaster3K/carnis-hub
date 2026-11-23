# Шаг 22 — полный код и текстовые ресурсы

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

## `src/main/java/com/carnis/mod/client/renderer/InfectedZombieRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.InfectedZombieGeoModel;
import com.carnis.mod.entity.InfectedZombieEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;

/** The model resolves the geometry, texture, and animation resources. */
public final class InfectedZombieRenderer extends GeoEntityRenderer<InfectedZombieEntity> {
    public InfectedZombieRenderer(EntityRendererProvider.Context context) {
        super(context, new InfectedZombieGeoModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
        this.shadowRadius = 0.45F;
    }
}
```

## `src/main/java/com/carnis/mod/client/model/InfectedZombieGeoModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.entity.InfectedZombieEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class InfectedZombieGeoModel extends GeoModel<InfectedZombieEntity> {
    @Override public ResourceLocation getModelResource(InfectedZombieEntity entity) { return new ResourceLocation("carnis", "geo/entity/infected_zombie.geo.json"); }
    @Override public ResourceLocation getTextureResource(InfectedZombieEntity entity) { return new ResourceLocation("carnis", "textures/entity/infected_zombie.png"); }
    @Override public ResourceLocation getAnimationResource(InfectedZombieEntity entity) { return new ResourceLocation("carnis", "animations/entity/infected_zombie.animation.json"); }
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
    private static final RawAnimation SCYTHE_ATTACK = RawAnimation.begin().thenPlay("animation.infected_skeleton.attack_scythe");
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
            if (!isAssimilating() && swinging) return state.setAndContinue(SCYTHE_ATTACK);
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
        Vec3 look = getLookAngle();
        Vec3 forward = new Vec3(look.x, 0, look.z);
        if (forward.lengthSqr() < 1.0E-8D) {
            double yaw = Math.toRadians(getYRot());
            forward = new Vec3(-Math.sin(yaw), 0, Math.cos(yaw));
        } else forward = forward.normalize();
        float damage = (float) (getAttributeValue(Attributes.ATTACK_DAMAGE) * .75D);
        for (LivingEntity other : server.getEntitiesOfClass(LivingEntity.class,
                getBoundingBox().inflate(2.5D), target -> target != primary && target != this
                        && com.carnis.mod.entity.ai.HiveSwarmCoordinator.validTarget(this, target))) {
            Vec3 offset = other.position().subtract(position());
            Vec3 horizontal = new Vec3(offset.x, 0, offset.z);
            if (offset.lengthSqr() > 6.25D || horizontal.lengthSqr() < 1.0E-8D
                    || forward.dot(horizontal.normalize()) < 0.8660254037844386D || !hasLineOfSight(other)) continue;
            if (other.hurt(server.damageSources().mobAttack(this), damage))
                other.knockback(.4D, getX() - other.getX(), getZ() - other.getZ());
        }
        server.sendParticles(net.minecraft.core.particles.ParticleTypes.SWEEP_ATTACK,
                getX() + forward.x, getY(.5D), getZ() + forward.z, 1, 0, 0, 0, 0);
        server.playSound(null, blockPosition(), net.minecraft.sounds.SoundEvents.PLAYER_ATTACK_SWEEP,
                net.minecraft.sounds.SoundSource.HOSTILE, 1F, .85F + server.random.nextFloat() * .2F);
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/InfectedSkeletonRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.InfectedSkeletonGeoModel;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class InfectedSkeletonRenderer extends GeoEntityRenderer<InfectedSkeletonEntity> {
    public InfectedSkeletonRenderer(EntityRendererProvider.Context context) {
        super(context, new InfectedSkeletonGeoModel());
        addRenderLayer(new com.carnis.mod.client.renderer.layer.OptionalGlowLayer<>(this));
        this.shadowRadius = 0.45F;
    }
}
```

## `src/main/java/com/carnis/mod/client/model/InfectedSkeletonGeoModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.entity.InfectedSkeletonEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class InfectedSkeletonGeoModel extends GeoModel<InfectedSkeletonEntity> {
    @Override public ResourceLocation getModelResource(InfectedSkeletonEntity entity) { return new ResourceLocation("carnis", "geo/entity/infected_skeleton.geo.json"); }
    @Override public ResourceLocation getTextureResource(InfectedSkeletonEntity entity) { return new ResourceLocation("carnis", "textures/entity/infected_skeleton.png"); }
    @Override public ResourceLocation getAnimationResource(InfectedSkeletonEntity entity) { return new ResourceLocation("carnis", "animations/entity/infected_skeleton.animation.json"); }
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
    private float feedingPitch;

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
            net.minecraft.core.BlockPos remains = findRemains(level, corpse);
            if (remains != null) corpse = Vec3.atCenterOf(remains);
            double dx = corpse.x - mob.getX(), dz = corpse.z - mob.getZ();
            double horizontal = Math.sqrt(dx * dx + dz * dz);
            float desiredYaw = horizontal < 1.0E-4D ? mob.getYRot()
                    : (float) Math.toDegrees(Math.atan2(-dx, dz));
            feedingYaw = mob.getYRot() + net.minecraft.util.Mth.wrapDegrees(desiredYaw - mob.getYRot());
            double dy = corpse.y - mob.getEyeY();
            feedingPitch = (float) net.minecraft.util.Mth.clamp(
                    -Math.toDegrees(Math.atan2(dy, Math.max(horizontal, 0.12D))), -70D, 70D);
            facingLocked = true;
        }
        mob.setYRot(feedingYaw);
        mob.setYHeadRot(feedingYaw);
        mob.setYBodyRot(feedingYaw);
        mob.setXRot(feedingPitch);
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
            net.minecraft.core.BlockPos remains = findRemains(level, corpse);
            if (remains != null && net.minecraftforge.event.ForgeEventFactory.getMobGriefingEvent(level, mob))
                level.removeBlock(remains, false);
            setAssimilating(false);
            facingLocked = false;
            CarnisWorldData.get(level).addBiomassPoints(50L);
            ModMessages.sendToPlayersInLevel(level);
        } else {
            tag.putInt(DEADLINE, tag.getInt(DEADLINE) + 1);
        }
    }

    private static net.minecraft.core.BlockPos findRemains(ServerLevel level, Vec3 corpse) {
        net.minecraft.core.BlockPos base = net.minecraft.core.BlockPos.containing(corpse);
        for (int dy : new int[]{0, -1, 1}) {
            net.minecraft.core.BlockPos pos = base.offset(0, dy, 0);
            if (level.hasChunkAt(pos) && !level.isOutsideBuildHeight(pos)
                    && level.getBlockState(pos).is(com.carnis.mod.init.ModBlocks.BIOMASS_REMAINS.get())) return pos;
        }
        return null;
    }

    private void setAssimilating(boolean value) {
        if (mob instanceof AssimilatingMob assimilatingMob) {
            assimilatingMob.setAssimilating(value);
        }
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
        event.registerEntityRenderer(ModEntities.INOCULATOR_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.VIRAL_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.PURIFICATION_DART.get(), DartRenderer::new);
        event.registerBlockEntityRenderer(
                ModBlockEntities.PULSING_HEART.get(),
                PulsingHeartRenderer::new
        );
        event.registerBlockEntityRenderer(ModBlockEntities.HIVE_EYE.get(), HiveEyeRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.STOMACH_POOL.get(), com.carnis.mod.client.renderer.StomachPoolRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.NERVE_PILLAR.get(), com.carnis.mod.client.renderer.NervePillarRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.PUSTULE_CLUSTER.get(), com.carnis.mod.client.renderer.PustuleClusterRenderer::new);
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

## `src/main/resources/assets/carnis/geo/entity/infected_zombie.geo.json`

```json
{
  "format_version": "1.12.0",
  "minecraft:geometry": [
    {
      "description": {
        "identifier": "geometry.carnis.infected_zombie",
        "texture_width": 64,
        "texture_height": 64,
        "visible_bounds_width": 3,
        "visible_bounds_height": 3,
        "visible_bounds_offset": [
          0,
          1,
          0
        ]
      },
      "bones": [
        {
          "name": "root",
          "pivot": [
            0,
            0,
            0
          ]
        },
        {
          "name": "body",
          "pivot": [
            0,
            12,
            0
          ],
          "parent": "root",
          "cubes": [
            {
              "origin": [
                -4,
                12,
                -2
              ],
              "size": [
                8,
                12,
                4
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -3.6,
                14,
                -2.25
              ],
              "size": [
                7.2,
                8,
                0.5
              ],
              "uv": {
                "north": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "head",
          "pivot": [
            0,
            24,
            0
          ],
          "parent": "body",
          "cubes": [
            {
              "origin": [
                -4,
                24,
                -4
              ],
              "size": [
                8,
                8,
                8
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                0.5,
                27.6,
                -4.35
              ],
              "size": [
                3,
                2.7,
                0.6
              ],
              "uv": {
                "north": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -3.3,
                28,
                -4.32
              ],
              "size": [
                2.6,
                2.6,
                0.5
              ],
              "uv": {
                "north": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -2.8,
                28.5,
                -4.65
              ],
              "size": [
                1.2,
                1.2,
                0.4
              ],
              "uv": {
                "north": {
                  "uv": [
                    32,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    32,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    32,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    32,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    32,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    32,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "jaw",
          "pivot": [
            -3,
            25,
            -3
          ],
          "parent": "head",
          "cubes": [
            {
              "origin": [
                -3.4,
                23.2,
                -4.8
              ],
              "size": [
                6.8,
                2.5,
                3
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              },
              "rotation": [
                0,
                0,
                -12
              ],
              "pivot": [
                -3,
                25,
                -3
              ]
            },
            {
              "origin": [
                -3,
                25,
                -5
              ],
              "size": [
                6,
                0.7,
                0.7
              ],
              "uv": {
                "north": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              },
              "rotation": [
                0,
                0,
                -12
              ],
              "pivot": [
                -3,
                25,
                -3
              ]
            }
          ]
        },
        {
          "name": "tendril_left",
          "pivot": [
            -1.8,
            23.5,
            -4.7
          ],
          "parent": "jaw",
          "cubes": [
            {
              "origin": [
                -2.2,
                19.5,
                -5
              ],
              "size": [
                0.7,
                4.5,
                0.7
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "tendril_mid",
          "pivot": [
            0,
            23.3,
            -4.7
          ],
          "parent": "jaw",
          "cubes": [
            {
              "origin": [
                -0.35,
                18.8,
                -5.1
              ],
              "size": [
                0.7,
                5,
                0.7
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "tendril_right",
          "pivot": [
            1.8,
            23.5,
            -4.7
          ],
          "parent": "jaw",
          "cubes": [
            {
              "origin": [
                1.45,
                20,
                -5
              ],
              "size": [
                0.7,
                3.8,
                0.7
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "right_arm",
          "pivot": [
            0,
            24,
            0
          ],
          "parent": "body",
          "cubes": [
            {
              "origin": [
                -10.6,
                15,
                -2.8
              ],
              "size": [
                5.6,
                7.5,
                5.6
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -10.7,
                16,
                -3
              ],
              "size": [
                5.8,
                2,
                0.4
              ],
              "uv": {
                "north": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "right_forearm",
          "pivot": [
            -7.8,
            16,
            0
          ],
          "parent": "right_arm",
          "cubes": [
            {
              "origin": [
                -10.6,
                8,
                -2.8
              ],
              "size": [
                5.6,
                8,
                5.6
              ],
              "uv": {
                "north": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -10.8,
                10,
                -3
              ],
              "size": [
                0.5,
                5,
                0.4
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -8.2,
                9,
                -3.05
              ],
              "size": [
                0.55,
                6,
                0.45
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -5.7,
                10,
                -3
              ],
              "size": [
                0.45,
                4,
                0.4
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "bone_blade",
          "pivot": [
            -7.8,
            9,
            0
          ],
          "parent": "right_forearm",
          "cubes": [
            {
              "origin": [
                -10.6,
                3,
                -2.8
              ],
              "size": [
                5.6,
                6,
                5.6
              ],
              "uv": {
                "north": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -9,
                0,
                -1.2
              ],
              "size": [
                2.5,
                4,
                2.4
              ],
              "uv": {
                "north": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -8.25,
                -2,
                -0.65
              ],
              "size": [
                1,
                3,
                1.3
              ],
              "uv": {
                "north": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    48,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "left_arm",
          "pivot": [
            0,
            24,
            0
          ],
          "parent": "body",
          "cubes": [
            {
              "origin": [
                5.2,
                14,
                -1.5
              ],
              "size": [
                2.9,
                8,
                3
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "left_forearm",
          "pivot": [
            6.5,
            15,
            0
          ],
          "parent": "left_arm",
          "cubes": [
            {
              "origin": [
                5.4,
                8,
                -1.2
              ],
              "size": [
                2.5,
                7,
                2.4
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "left_claws",
          "pivot": [
            6.5,
            9,
            0
          ],
          "parent": "left_forearm",
          "cubes": [
            {
              "origin": [
                5.1,
                3.5,
                -1.7
              ],
              "size": [
                0.7,
                5.1,
                0.7
              ],
              "uv": {
                "north": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              },
              "rotation": [
                0,
                0,
                -10
              ],
              "pivot": [
                5.45,
                8,
                -1.35
              ]
            },
            {
              "origin": [
                6.15,
                2.8,
                -1.7
              ],
              "size": [
                0.7,
                5.7,
                0.7
              ],
              "uv": {
                "north": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                7.2,
                3.5,
                -1.7
              ],
              "size": [
                0.7,
                5.1,
                0.7
              ],
              "uv": {
                "north": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              },
              "rotation": [
                0,
                0,
                10
              ],
              "pivot": [
                7.55,
                8,
                -1.35
              ]
            }
          ]
        },
        {
          "name": "right_leg",
          "pivot": [
            -2,
            12,
            0
          ],
          "parent": "root",
          "cubes": [
            {
              "origin": [
                -4.1,
                0,
                -2.1
              ],
              "size": [
                4.1,
                12,
                4.2
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -4.15,
                5,
                -2.3
              ],
              "size": [
                4.2,
                2,
                0.35
              ],
              "uv": {
                "north": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "left_leg",
          "pivot": [
            2,
            12,
            0
          ],
          "parent": "root",
          "cubes": [
            {
              "origin": [
                0,
                0,
                -2.1
              ],
              "size": [
                4.1,
                12,
                4.2
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                0,
                7,
                -2.3
              ],
              "size": [
                4.1,
                1,
                0.35
              ],
              "uv": {
                "north": {
                  "uv": [
                    16,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    16,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    16,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    16,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    16,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    16,
                    32
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "ribs",
          "pivot": [
            0,
            18,
            -2
          ],
          "parent": "body",
          "cubes": [
            {
              "origin": [
                -3.2,
                20,
                -3
              ],
              "size": [
                6.4,
                0.65,
                0.8
              ],
              "uv": {
                "north": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -3.4,
                18.5,
                -3
              ],
              "size": [
                6.8,
                0.65,
                0.8
              ],
              "uv": {
                "north": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -3.25,
                17,
                -3
              ],
              "size": [
                6.5,
                0.65,
                0.8
              ],
              "uv": {
                "north": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                -3,
                15.5,
                -3
              ],
              "size": [
                6,
                0.65,
                0.8
              ],
              "uv": {
                "north": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "core",
          "pivot": [
            0,
            18,
            -2.8
          ],
          "parent": "body",
          "cubes": [
            {
              "origin": [
                -1.3,
                16.5,
                -3.3
              ],
              "size": [
                2.6,
                2.6,
                0.65
              ],
              "uv": {
                "north": {
                  "uv": [
                    16,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    16,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    16,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    16,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    16,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    16,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "back_veins",
          "pivot": [
            0,
            18,
            2
          ],
          "parent": "body",
          "cubes": [
            {
              "origin": [
                -2.7,
                13,
                2
              ],
              "size": [
                0.7,
                10,
                0.45
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            },
            {
              "origin": [
                1.3,
                15,
                2
              ],
              "size": [
                0.7,
                8,
                0.45
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    16
                  ],
                  "uv_size": [
                    16,
                    16
                  ]
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## `src/main/resources/assets/carnis/animations/entity/infected_zombie.animation.json`

```json
{
  "format_version": "1.8.0",
  "animations": {
    "animation.infected_zombie.idle": {
      "loop": true,
      "animation_length": 2,
      "bones": {
        "body": {
          "rotation": {
            "0": [
              2,
              0,
              -4
            ],
            "0.55": [
              3,
              0,
              -5
            ],
            "0.7": [
              1,
              0,
              -4
            ],
            "1.3": [
              2,
              0,
              -5
            ],
            "2": [
              2,
              0,
              -4
            ]
          },
          "scale": {
            "0": [
              1,
              1,
              1
            ],
            "0.55": [
              1.025,
              1.012,
              1.025
            ],
            "0.7": [
              1,
              1,
              1
            ],
            "1.3": [
              1.018,
              1.008,
              1.018
            ],
            "2": [
              1,
              1,
              1
            ]
          }
        },
        "jaw": {
          "rotation": {
            "0": [
              2,
              0,
              -6
            ],
            "1": [
              5,
              0,
              -7
            ],
            "2": [
              2,
              0,
              -6
            ]
          }
        },
        "tendril_left": {
          "rotation": {
            "0": [
              5,
              0,
              -7
            ],
            "0.8": [
              -6,
              0,
              5
            ],
            "2": [
              5,
              0,
              -7
            ]
          }
        },
        "tendril_mid": {
          "rotation": {
            "0": [
              -4,
              0,
              2
            ],
            "1": [
              7,
              0,
              -3
            ],
            "2": [
              -4,
              0,
              2
            ]
          }
        },
        "tendril_right": {
          "rotation": {
            "0": [
              3,
              0,
              5
            ],
            "1.1": [
              -5,
              0,
              -6
            ],
            "2": [
              3,
              0,
              5
            ]
          }
        }
      }
    },
    "animation.infected_zombie.walk": {
      "loop": true,
      "animation_length": 1.2,
      "bones": {
        "body": {
          "rotation": {
            "0": [
              7,
              1,
              -8
            ],
            "0.25": [
              8,
              -1,
              -10
            ],
            "0.45": [
              6,
              2,
              -7
            ],
            "0.6": [
              9,
              0,
              -9
            ],
            "0.9": [
              6,
              -2,
              -6
            ],
            "1.2": [
              7,
              1,
              -8
            ]
          }
        },
        "right_leg": {
          "rotation": {
            "0": [
              -18,
              0,
              0
            ],
            "0.3": [
              12,
              0,
              0
            ],
            "0.6": [
              19,
              0,
              0
            ],
            "0.9": [
              -12,
              0,
              0
            ],
            "1.2": [
              -18,
              0,
              0
            ]
          }
        },
        "left_leg": {
          "rotation": {
            "0": [
              28,
              0,
              0
            ],
            "0.3": [
              8,
              0,
              0
            ],
            "0.6": [
              -24,
              0,
              0
            ],
            "0.9": [
              -8,
              0,
              0
            ],
            "1.2": [
              28,
              0,
              0
            ]
          }
        },
        "right_arm": {
          "rotation": {
            "0": [
              16,
              0,
              -8
            ],
            "0.3": [
              9,
              1,
              -10
            ],
            "0.6": [
              -12,
              0,
              -8
            ],
            "0.64": [
              -9,
              2,
              -10
            ],
            "1.2": [
              16,
              0,
              -8
            ]
          }
        },
        "left_arm": {
          "rotation": {
            "0": [
              -17,
              0,
              5
            ],
            "0.3": [
              -4,
              0,
              7
            ],
            "0.6": [
              19,
              0,
              4
            ],
            "0.9": [
              2,
              -2,
              5
            ],
            "1.2": [
              -17,
              0,
              5
            ]
          }
        },
        "right_forearm": {
          "rotation": {
            "0": [
              3,
              0,
              2
            ],
            "0.58": [
              8,
              0,
              4
            ],
            "0.63": [
              3,
              0,
              1
            ],
            "1.2": [
              3,
              0,
              2
            ]
          }
        }
      }
    },
    "animation.infected_zombie.attack": {
      "loop": false,
      "animation_length": 0.7,
      "bones": {
        "body": {
          "rotation": {
            "0": [
              3,
              0,
              -5
            ],
            "0.2": [
              -8,
              -28,
              -8
            ],
            "0.38": [
              18,
              20,
              -7
            ],
            "0.7": [
              3,
              0,
              -5
            ]
          }
        },
        "right_arm": {
          "rotation": {
            "0": [
              0,
              0,
              -7
            ],
            "0.2": [
              -145,
              -18,
              -20
            ],
            "0.38": [
              65,
              8,
              14
            ],
            "0.7": [
              0,
              0,
              -7
            ]
          }
        },
        "right_forearm": {
          "rotation": {
            "0": [
              0,
              0,
              0
            ],
            "0.2": [
              -30,
              0,
              0
            ],
            "0.38": [
              30,
              0,
              0
            ],
            "0.7": [
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
              4
            ],
            "0.2": [
              -35,
              0,
              18
            ],
            "0.38": [
              -20,
              0,
              5
            ],
            "0.7": [
              0,
              0,
              4
            ]
          }
        }
      }
    },
    "animation.infected_zombie.pulsing": {
      "loop": true,
      "animation_length": 72,
      "bones": {
        "core": {
          "scale": [
            "1.0 + Math.sin(query.anim_time * 5.0) * 0.15",
            "1.0 + Math.sin(query.anim_time * 5.0) * 0.25",
            "1.0 + Math.sin(query.anim_time * 5.0) * 0.15"
          ]
        }
      }
    },
    "animation.infected_zombie.assimilate": {
      "loop": true,
      "animation_length": 1.2,
      "bones": {
        "body": {
          "position": {
            "0.0": [
              0,
              -2.5,
              0
            ],
            "0.6": [
              0,
              -2.7,
              0
            ],
            "1.2": [
              0,
              -2.5,
              0
            ]
          },
          "rotation": [
            28,
            0,
            -6
          ]
        },
        "head": {
          "rotation": [
            22,
            0,
            4
          ]
        },
        "right_arm": {
          "rotation": [
            35,
            0,
            -14
          ]
        },
        "right_forearm": {
          "rotation": [
            -20,
            0,
            0
          ]
        },
        "left_arm": {
          "rotation": [
            35,
            0,
            9
          ]
        },
        "right_leg": {
          "rotation": [
            -38,
            0,
            3
          ]
        },
        "left_leg": {
          "rotation": [
            28,
            0,
            -4
          ]
        },
        "core": {
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.3": [
              1.14,
              1.18,
              1.1
            ],
            "0.6": [
              1,
              1,
              1
            ],
            "0.9": [
              1.1,
              1.12,
              1.08
            ],
            "1.2": [
              1,
              1,
              1
            ]
          }
        },
        "jaw": {
          "rotation": {
            "0.0": [
              12,
              0,
              -8
            ],
            "0.6": [
              19,
              0,
              -8
            ],
            "1.2": [
              12,
              0,
              -8
            ]
          }
        },
        "tendril_left": {
          "rotation": {
            "0.0": [
              25,
              0,
              -6
            ],
            "0.6": [
              45,
              0,
              5
            ],
            "1.2": [
              25,
              0,
              -6
            ]
          }
        },
        "tendril_mid": {
          "rotation": {
            "0.0": [
              45,
              0,
              0
            ],
            "0.6": [
              25,
              0,
              0
            ],
            "1.2": [
              45,
              0,
              0
            ]
          }
        },
        "tendril_right": {
          "rotation": {
            "0.0": [
              30,
              0,
              5
            ],
            "0.6": [
              46,
              0,
              -6
            ],
            "1.2": [
              30,
              0,
              5
            ]
          }
        }
      }
    }
  }
}
```

## `src/main/resources/assets/carnis/geo/entity/infected_skeleton.geo.json`

```json
{
  "format_version": "1.12.0",
  "minecraft:geometry": [
    {
      "description": {
        "identifier": "geometry.carnis.infected_skeleton",
        "texture_width": 64,
        "texture_height": 32,
        "visible_bounds_width": 5,
        "visible_bounds_height": 4,
        "visible_bounds_offset": [
          0,
          1,
          0
        ]
      },
      "bones": [
        {
          "name": "root",
          "pivot": [
            0,
            0,
            0
          ]
        },
        {
          "name": "body",
          "parent": "root",
          "pivot": [
            0,
            12,
            0
          ],
          "cubes": [
            {
              "origin": [
                -3,
                11,
                -1
              ],
              "size": [
                6,
                2,
                2
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                23,
                -1
              ],
              "size": [
                8,
                1,
                2
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -0.5,
                13,
                -2.5
              ],
              "size": [
                1,
                10,
                1
              ],
              "uv": [
                0,
                0
              ]
            }
          ]
        },
        {
          "name": "spine",
          "parent": "body",
          "pivot": [
            0,
            12,
            1.5
          ],
          "cubes": [
            {
              "origin": [
                -1,
                12,
                1
              ],
              "size": [
                2,
                2,
                2
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -1,
                15,
                1
              ],
              "size": [
                2,
                2,
                2
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -1,
                18,
                1
              ],
              "size": [
                2,
                2,
                2
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -1,
                21,
                1
              ],
              "size": [
                2,
                2,
                2
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -0.5,
                12,
                1.5
              ],
              "size": [
                1,
                11,
                1
              ],
              "uv": [
                0,
                0
              ]
            }
          ]
        },
        {
          "name": "ribs",
          "parent": "body",
          "pivot": [
            0,
            18,
            0
          ],
          "cubes": [
            {
              "origin": [
                -4,
                14,
                -2
              ],
              "size": [
                1,
                1,
                4
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                17,
                -2
              ],
              "size": [
                1,
                1,
                4
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                20,
                -2
              ],
              "size": [
                1,
                1,
                4
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                23,
                -2
              ],
              "size": [
                1,
                1,
                4
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                3,
                14,
                -2
              ],
              "size": [
                1,
                1,
                4
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                3,
                17,
                -2
              ],
              "size": [
                1,
                1,
                4
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                3,
                20,
                -2
              ],
              "size": [
                1,
                1,
                4
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                3,
                23,
                -2
              ],
              "size": [
                1,
                1,
                4
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                14,
                1
              ],
              "size": [
                8,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                17,
                1
              ],
              "size": [
                8,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                20,
                1
              ],
              "size": [
                8,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                23,
                1
              ],
              "size": [
                8,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                14,
                -2
              ],
              "size": [
                2,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                17,
                -2
              ],
              "size": [
                2,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                20,
                -2
              ],
              "size": [
                2,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                23,
                -2
              ],
              "size": [
                2,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                2,
                14,
                -2
              ],
              "size": [
                2,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                2,
                17,
                -2
              ],
              "size": [
                2,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                2,
                20,
                -2
              ],
              "size": [
                2,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                2,
                23,
                -2
              ],
              "size": [
                2,
                1,
                1
              ],
              "uv": [
                0,
                0
              ]
            }
          ]
        },
        {
          "name": "heart",
          "parent": "body",
          "pivot": [
            0,
            18,
            -0.1
          ],
          "cubes": [
            {
              "origin": [
                -1.5,
                16,
                -1.2
              ],
              "size": [
                3,
                4,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -1,
                19,
                -1
              ],
              "size": [
                2,
                2,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "head",
          "parent": "body",
          "pivot": [
            0,
            24,
            0
          ],
          "cubes": [
            {
              "origin": [
                -4,
                24,
                -4
              ],
              "size": [
                8,
                8,
                8
              ],
              "uv": {
                "north": {
                  "uv": [
                    40,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    32,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -3,
                27,
                -4.4
              ],
              "size": [
                1,
                3,
                0.5
              ],
              "uv": {
                "north": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -3.8,
                29,
                -4.5
              ],
              "size": [
                2,
                0.5,
                0.5
              ],
              "uv": {
                "north": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    48,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            }
          ]
        },
        {
          "name": "left_arm",
          "parent": "body",
          "pivot": [
            5,
            23,
            0
          ],
          "cubes": [
            {
              "origin": [
                4,
                18,
                -1
              ],
              "size": [
                2,
                5,
                2
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                4.1,
                11,
                -1.2
              ],
              "size": [
                0.8,
                7,
                0.8
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                5.3,
                11,
                0.2
              ],
              "size": [
                0.8,
                7,
                0.8
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                4,
                10,
                -1
              ],
              "size": [
                2,
                1,
                2
              ],
              "uv": [
                0,
                0
              ]
            }
          ]
        },
        {
          "name": "right_arm",
          "parent": "body",
          "pivot": [
            -5,
            23,
            0
          ],
          "cubes": [
            {
              "origin": [
                -6,
                18,
                -1
              ],
              "size": [
                2,
                5,
                2
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -6,
                10,
                -1.2
              ],
              "size": [
                0.8,
                8,
                0.8
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4.8,
                10,
                0.2
              ],
              "size": [
                0.8,
                8,
                0.8
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -6,
                9,
                -1.4
              ],
              "size": [
                2,
                2,
                2.4
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -6,
                6,
                -1.2
              ],
              "size": [
                2,
                4,
                2
              ],
              "uv": [
                0,
                0
              ]
            }
          ]
        },
        {
          "name": "scythe",
          "parent": "right_arm",
          "pivot": [
            -5,
            9,
            0
          ],
          "cubes": [
            {
              "origin": [
                -6,
                3,
                -1
              ],
              "size": [
                2,
                4,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -9,
                3,
                -1
              ],
              "size": [
                4,
                2,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -12,
                4,
                -1
              ],
              "size": [
                4,
                2,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -15,
                5,
                -1
              ],
              "size": [
                4,
                2,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -17,
                6,
                -1
              ],
              "size": [
                3,
                2,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -19,
                7,
                -1
              ],
              "size": [
                3,
                2,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -20,
                8,
                -1
              ],
              "size": [
                2,
                3,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -11,
                2,
                -1
              ],
              "size": [
                1,
                2,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -14,
                3,
                -1
              ],
              "size": [
                1,
                2,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -17,
                4,
                -1
              ],
              "size": [
                1,
                2,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                -19,
                5,
                -1
              ],
              "size": [
                1,
                2,
                2
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    16
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            }
          ],
          "rotation": [
            0,
            -55,
            -8
          ]
        },
        {
          "name": "left_leg",
          "parent": "root",
          "pivot": [
            2,
            12,
            0
          ],
          "cubes": [
            {
              "origin": [
                1,
                6,
                -1
              ],
              "size": [
                2,
                6,
                2
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                1,
                1,
                -1
              ],
              "size": [
                0.8,
                5,
                0.8
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                2.2,
                1,
                0.2
              ],
              "size": [
                0.8,
                5,
                0.8
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                1,
                0,
                -3
              ],
              "size": [
                2,
                1,
                4
              ],
              "uv": [
                0,
                0
              ]
            }
          ]
        },
        {
          "name": "right_leg",
          "parent": "root",
          "pivot": [
            -2,
            12,
            0
          ],
          "cubes": [
            {
              "origin": [
                -3,
                6,
                -1
              ],
              "size": [
                2,
                6,
                2
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -3,
                1,
                -1
              ],
              "size": [
                0.8,
                5,
                0.8
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -1.8,
                1,
                0.2
              ],
              "size": [
                0.8,
                5,
                0.8
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -3,
                0,
                -3
              ],
              "size": [
                2,
                1,
                4
              ],
              "uv": [
                0,
                0
              ]
            }
          ]
        },
        {
          "name": "neural_filaments",
          "parent": "head",
          "pivot": [
            2.5,
            29,
            -4.2
          ],
          "cubes": [
            {
              "origin": [
                2.4,
                29,
                -4.7
              ],
              "size": [
                0.6,
                5,
                0.6
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                1.8,
                31,
                -4.7
              ],
              "size": [
                0.5,
                4,
                0.5
              ],
              "pivot": [
                2,
                31,
                -4.5
              ],
              "rotation": [
                0,
                0,
                18
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            },
            {
              "origin": [
                2.2,
                27.2,
                -4.65
              ],
              "size": [
                0.55,
                3,
                0.55
              ],
              "pivot": [
                2.5,
                29,
                -4.4
              ],
              "rotation": [
                8,
                0,
                -20
              ],
              "uv": {
                "north": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    56,
                    24
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## `src/main/resources/assets/carnis/animations/entity/infected_skeleton.animation.json`

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
    }
  }
}
```
