# Carnis — Шаг 12: полный исходный код

Полные файлы без сокращений. Бинарные ресурсы находятся в проекте.

## `src/main/java/com/carnis/mod/item/BioPurifierItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.FleshIncineration;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.init.ModEffects;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.HashSet;
import java.util.Set;

public final class BioPurifierItem extends Item implements GeoItem {
    public static final int MAX_DURABILITY = 500;
    private static final int DURATION = 72000;
    private static final int SHOCK_TICKS = 60;
    private static final double RANGE = 6.5D;
    // 25 degrees is the cone half-angle, measured from its axis.
    private static final double COS_ANGLE = Math.cos(Math.toRadians(25.0D));
    private static final double TAN_ANGLE = Math.tan(Math.toRadians(25.0D));
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.bio_purifier.idle");
    private static final RawAnimation FIRING = RawAnimation.begin().thenLoop("animation.bio_purifier.firing");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public BioPurifierItem(Properties properties) { super(properties.durability(MAX_DURABILITY)); }

    @Override public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientItemExtensions> consumer) {
        consumer.accept(new net.minecraftforge.client.extensions.common.IClientItemExtensions() {
            private com.carnis.mod.client.renderer.item.BioPurifierRenderer renderer;
            @Override public net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new com.carnis.mod.client.renderer.item.BioPurifierRenderer();
                return renderer;
            }
        });
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "operation", 0, state -> state.setAndContinue(
                com.carnis.mod.client.BioPurifierAnimationState.isFiring(state) ? FIRING : IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
    @Override public int getUseDuration(ItemStack stack) { return DURATION; }
    @Override public UseAnim getUseAnimation(ItemStack stack) { return UseAnim.NONE; }

    @Override public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        player.startUsingItem(hand);
        if (level instanceof ServerLevel server) server.playSound(null, player.blockPosition(), ModSounds.PURIFIER_IGNITE.get(),
                SoundSource.PLAYERS, 0.9F, 1.0F);
        return InteractionResultHolder.consume(stack);
    }

    @Override public void onUseTick(Level level, LivingEntity user, ItemStack stack, int count) {
        if (!(level instanceof ServerLevel server)) return;
        if (stack.isEmpty()) { user.stopUsingItem(); return; }
        int elapsed = DURATION - count;
        if (elapsed % 10 == 0) server.playSound(null, user.blockPosition(), ModSounds.PURIFIER_LOOP.get(),
                SoundSource.PLAYERS, 0.7F, 1.0F);
        if (elapsed % 2 == 0 && (!(user instanceof Player player) || !player.getAbilities().instabuild)) {
            stack.hurtAndBreak(1, user, entity -> entity.broadcastBreakEvent(entity.getUsedItemHand()));
            if (stack.isEmpty()) { user.stopUsingItem(); return; }
        }

        Vec3 forward = user.getLookAngle().normalize();
        double yaw = Math.toRadians(user.getYRot());
        Vec3 right = new Vec3(-Math.cos(yaw), 0.0D, -Math.sin(yaw)).normalize();
        Vec3 up = forward.cross(right).normalize();
        double side = 1.0D;
        if (user instanceof Player player) {
            HumanoidArm arm = user.getUsedItemHand() == InteractionHand.MAIN_HAND
                    ? player.getMainArm() : player.getMainArm().getOpposite();
            side = arm == HumanoidArm.RIGHT ? 1.0D : -1.0D;
        }
        Vec3 eye = user.getEyePosition();
        Vec3 origin = eye.add(right.scale(0.28D * side)).add(0, -0.35D, 0).add(forward.scale(0.85D));
        if (server.clip(new ClipContext(eye, origin, ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE, user)).getType() == HitResult.Type.BLOCK) return;

        emitParticles(server, user, origin, forward, right, up);
        if (elapsed % 4 == 0) {
            damageEntities(server, user, origin, forward);
            burnConeBlocks(server, user, origin, forward, right, up);
        }
    }

    private static boolean insideCone(Vec3 origin, Vec3 forward, Vec3 point) {
        Vec3 delta = point.subtract(origin);
        double distanceSquared = delta.lengthSqr();
        if (distanceSquared < 1.0E-8D || distanceSquared > RANGE * RANGE) return false;
        return delta.dot(forward) / Math.sqrt(distanceSquared) >= COS_ANGLE;
    }

    private static boolean clearRay(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 target) {
        return level.clip(new ClipContext(origin, target, ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE, user)).getType() == HitResult.Type.MISS;
    }

    private static boolean exposedInCone(ServerLevel level, LivingEntity user, LivingEntity target, Vec3 origin, Vec3 forward) {
        AABB b = target.getBoundingBox();
        double x = (b.minX + b.maxX) * .5D, z = (b.minZ + b.maxZ) * .5D;
        double y = (b.minY + b.maxY) * .5D;
        Vec3[] samples = {new Vec3(x, y, z), new Vec3(x, b.minY + .05D, z),
                new Vec3(x, b.maxY - .05D, z), new Vec3(b.minX, y, z), new Vec3(b.maxX, y, z),
                new Vec3(x, y, b.minZ), new Vec3(x, y, b.maxZ)};
        for (Vec3 point : samples) if (insideCone(origin, forward, point) && clearRay(level, user, origin, point)) return true;
        return false;
    }

    private static void damageEntities(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 forward) {
        Vec3 end = origin.add(forward.scale(RANGE));
        AABB bounds = new AABB(origin, end).inflate(RANGE * TAN_ANGLE);
        for (LivingEntity target : level.getEntitiesOfClass(LivingEntity.class, bounds,
                e -> e != user && e.isAlive() && !e.isSpectator())) {
            if (user instanceof Player attacker && target instanceof Player victim && !attacker.canHarmPlayer(victim)) continue;
            if (!exposedInCone(level, user, target, origin, forward)) continue;
            boolean protectedByPillar = HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.PILLAR, target.blockPosition(), 32) != null;
            target.setSecondsOnFire(4);
            if (protectedByPillar) target.setRemainingFireTicks(Math.min(target.getRemainingFireTicks(), 20));
            if (!protectedByPillar && infected(target))
                target.addEffect(new MobEffectInstance(ModEffects.THERMAL_SHOCK.get(), SHOCK_TICKS, 0));
            // Permit the four-tick stream cadence without clearing unrelated immunity afterwards.
            int previous = target.invulnerableTime;
            target.invulnerableTime = 0;
            try { target.hurt(ModDamageTypes.bioPurifierSurface(level, user), 3.0F); }
            finally { target.invulnerableTime = Math.max(previous, target.invulnerableTime); }
        }
    }

    private static boolean infected(LivingEntity target) {
        if (target instanceof HivemindLinkedMob || InfectionHandler.isInfected(target)
                || target.hasEffect(ModEffects.INCUBATING.get())) return true;
        if (target instanceof Player player && PlayerInfectionApi.getInfectionLevel(player) > 0) return true;
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(target.getType());
        return id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }

    private static Vec3 rayDirection(Vec3 forward, Vec3 right, Vec3 up, double fraction, double angle) {
        return forward.add(right.scale(TAN_ANGLE * fraction * Math.cos(angle)))
                .add(up.scale(TAN_ANGLE * fraction * Math.sin(angle))).normalize();
    }

    private static void burnConeBlocks(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 forward, Vec3 right, Vec3 up) {
        Set<BlockPos> hitBlocks = new HashSet<>();
        traceBlock(level, user, origin, forward, hitBlocks);
        for (int ring = 1; ring <= 2; ring++) for (int i = 0; i < 12; i++) {
            double angle = 2.0D * Math.PI * (i + (ring == 1 ? 0.5D : 0.0D)) / 12.0D;
            traceBlock(level, user, origin, rayDirection(forward, right, up, ring / 2.0D, angle), hitBlocks);
        }
        for (BlockPos pos : hitBlocks) burnBlock(level, pos);
    }

    private static void traceBlock(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 direction, Set<BlockPos> found) {
        BlockHitResult hit = level.clip(new ClipContext(origin, origin.add(direction.scale(RANGE)),
                ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, user));
        if (hit.getType() == HitResult.Type.BLOCK) found.add(hit.getBlockPos().immutable());
    }

    private static void burnBlock(ServerLevel level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        if (state.is(ModBlocks.LIVING_FLESH.get()) || state.is(ModBlocks.OSSIFIED_FLESH.get())) {
            FleshIncineration.tryBurn(level, pos, state);
        } else if (state.is(ModBlocks.FLESH_VEINS.get())) {
            BlockState replacement = state.getFluidState().isEmpty() ? Blocks.AIR.defaultBlockState()
                    : state.getFluidState().createLegacyBlock();
            level.setBlockAndUpdate(pos, replacement);
        }
        // FIREPROOF_FLESH is not changed; it also blocks rays like any solid block.
    }

    private static void emitParticles(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 forward, Vec3 right, Vec3 up) {
        for (int i = 0; i < 5; i++) {
            double angle = level.random.nextDouble() * Math.PI * 2.0D;
            double radius = Math.sqrt(level.random.nextDouble());
            Vec3 ray = rayDirection(forward, right, up, radius, angle);
            double distance = 0.4D + level.random.nextDouble() * (RANGE - 0.4D);
            Vec3 intended = origin.add(ray.scale(distance));
            BlockHitResult hit = level.clip(new ClipContext(origin, intended, ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE, user));
            Vec3 point = hit.getType() == HitResult.Type.BLOCK ? hit.getLocation().subtract(ray.scale(.05D)) : intended;
            Vec3 velocity = ray.scale(.06D);
            level.sendParticles(ModParticles.PURIFIER_FLAME.get(), point.x, point.y, point.z, 0,
                    velocity.x, velocity.y, velocity.z, 1.0D);
            level.sendParticles(ParticleTypes.FLAME, point.x, point.y, point.z, 0,
                    velocity.x, velocity.y, velocity.z, 1.0D);
            if (i % 2 == 0) level.sendParticles(ParticleTypes.SMOKE, point.x, point.y, point.z, 0,
                    velocity.x * .5D, velocity.y * .5D + .01D, velocity.z * .5D, 1.0D);
        }
    }
}
```

## `src/main/java/com/carnis/mod/effect/ThermalShockEffect.java`

```java
package com.carnis.mod.effect;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModEffects;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ThermalShockEffect extends MobEffect {
    public ThermalShockEffect() {
        super(MobEffectCategory.HARMFUL, 0x3B6B8C);
        addAttributeModifier(Attributes.MOVEMENT_SPEED, "7e0881ae-07f3-48da-b5ae-17c8da3fe023",
                -0.30D, AttributeModifier.Operation.MULTIPLY_TOTAL);
    }

    /** Applied before ordinary mitigation; no additional damage event is fired. */
    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onHurt(LivingHurtEvent event) {
        if (!event.isCanceled() && event.getAmount() > 0.0F && !event.getEntity().level().isClientSide
                && event.getEntity().hasEffect(ModEffects.THERMAL_SHOCK.get()))
            event.setAmount(event.getAmount() * 1.25F);
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/item/BioPurifierRenderer.java`

```java
package com.carnis.mod.client.renderer.item;

import com.carnis.mod.client.model.BioPurifierModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.item.BioPurifierItem;
import software.bernie.geckolib.renderer.GeoItemRenderer;

public final class BioPurifierRenderer extends GeoItemRenderer<BioPurifierItem> {
    public BioPurifierRenderer() {
        super(new BioPurifierModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
```

## `src/main/java/com/carnis/mod/client/model/BioPurifierModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.item.BioPurifierItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class BioPurifierModel extends GeoModel<BioPurifierItem> {
    @Override public ResourceLocation getModelResource(BioPurifierItem item) {
        return new ResourceLocation("carnis", "geo/item/bio_purifier.geo.json");
    }
    @Override public ResourceLocation getTextureResource(BioPurifierItem item) {
        return new ResourceLocation("carnis", "textures/item/bio_purifier.png");
    }
    @Override public ResourceLocation getAnimationResource(BioPurifierItem item) {
        return new ResourceLocation("carnis", "animations/item/bio_purifier.animation.json");
    }
}
```

## `src/main/java/com/carnis/mod/init/ModEffects.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.effect.ImmunosuppressionMobEffect;
import com.carnis.mod.effect.IncubatingMobEffect;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEffects {
    public static final DeferredRegister<MobEffect> EFFECTS =
            DeferredRegister.create(ForgeRegistries.MOB_EFFECTS, CarnisMod.MOD_ID);
    public static final RegistryObject<MobEffect> INCUBATING = EFFECTS.register("incubating", () ->
            new IncubatingMobEffect());
    public static final RegistryObject<MobEffect> THERMAL_SHOCK = EFFECTS.register("thermal_shock",
            com.carnis.mod.effect.ThermalShockEffect::new);
    public static final RegistryObject<MobEffect> IMMUNOSUPPRESSION = EFFECTS.register(
            "immunosuppression", ImmunosuppressionMobEffect::new);

    private ModEffects() { }
    public static void register(IEventBus bus) { EFFECTS.register(bus); }
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
    }
}
```

## `src/main/java/com/carnis/mod/client/BioPurifierAnimationState.java`

```java
package com.carnis.mod.client;
import com.carnis.mod.item.BioPurifierItem;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animation.AnimationState;

/** Render-side state only; item renderers do not receive an owning entity in GeckoLib 4. */
public final class BioPurifierAnimationState {
    private BioPurifierAnimationState() { }
    public static boolean isFiring(AnimationState<BioPurifierItem> state) {
        ItemDisplayContext context = state.getData(DataTickets.ITEM_RENDER_PERSPECTIVE);
        if (context != ItemDisplayContext.FIRST_PERSON_LEFT_HAND && context != ItemDisplayContext.FIRST_PERSON_RIGHT_HAND
                && context != ItemDisplayContext.THIRD_PERSON_LEFT_HAND && context != ItemDisplayContext.THIRD_PERSON_RIGHT_HAND) return false;
        ItemStack stack = state.getData(DataTickets.ITEMSTACK);
        var level = Minecraft.getInstance().level;
        if (stack == null || level == null) return false;
        for (Player player : level.players()) {
            if (player.isUsingItem() && player.getUseItem() == stack) return true;
        }
        return false;
    }
}
```

## `src/main/resources/assets/carnis/geo/item/bio_purifier.geo.json`

```json
{
  "format_version": "1.12.0",
  "minecraft:geometry": [
    {
      "description": {
        "identifier": "geometry.carnis.bio_purifier",
        "texture_width": 64,
        "texture_height": 64,
        "visible_bounds_width": 4,
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
            8,
            0
          ],
          "cubes": [
            {
              "origin": [
                -5.4,
                3.95,
                -6.75
              ],
              "size": [
                10.8,
                9.45,
                13.5
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    0,
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
                -5.94,
                3.95,
                -5.4
              ],
              "size": [
                0.81,
                9.45,
                10.8
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                5.13,
                3.95,
                -5.4
              ],
              "size": [
                0.81,
                9.45,
                10.8
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                -5.4,
                12.05,
                -5.4
              ],
              "size": [
                10.8,
                1.35,
                10.8
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                -2.7,
                -2.8,
                1.35
              ],
              "size": [
                5.4,
                8.1,
                5.4
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                -2.025,
                -1.45,
                -5.4
              ],
              "size": [
                4.05,
                6.75,
                4.05
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                -4.05,
                13.4,
                -2.7
              ],
              "size": [
                8.1,
                6.75,
                8.1
              ],
              "uv": {
                "north": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    16,
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
                -4.455,
                14.075,
                -3.105
              ],
              "size": [
                8.91,
                1.35,
                8.91
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                -4.455,
                17.72,
                -3.105
              ],
              "size": [
                8.91,
                1.35,
                8.91
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                -1.35,
                20.15,
                0.0
              ],
              "size": [
                2.7,
                2.7,
                2.7
              ],
              "uv": {
                "north": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    16,
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
                -4.05,
                6.65,
                -25.65
              ],
              "size": [
                2.7,
                2.7,
                20.25
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                -4.32,
                6.38,
                -26.19
              ],
              "size": [
                3.24,
                3.24,
                1.62
              ],
              "uv": {
                "north": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    24,
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
                -4.59,
                5.975,
                -20.25
              ],
              "size": [
                3.78,
                4.05,
                0.8775
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                -4.59,
                5.975,
                -16.2
              ],
              "size": [
                3.78,
                4.05,
                0.8775
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                -4.59,
                5.975,
                -12.15
              ],
              "size": [
                3.78,
                4.05,
                0.8775
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                -4.59,
                5.975,
                -8.1
              ],
              "size": [
                3.78,
                4.05,
                0.8775
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                1.35,
                6.65,
                -25.65
              ],
              "size": [
                2.7,
                2.7,
                20.25
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                1.08,
                6.38,
                -26.19
              ],
              "size": [
                3.24,
                3.24,
                1.62
              ],
              "uv": {
                "north": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    24,
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
                0.81,
                5.975,
                -20.25
              ],
              "size": [
                3.78,
                4.05,
                0.8775
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                0.81,
                5.975,
                -16.2
              ],
              "size": [
                3.78,
                4.05,
                0.8775
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                0.81,
                5.975,
                -12.15
              ],
              "size": [
                3.78,
                4.05,
                0.8775
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                0.81,
                5.975,
                -8.1
              ],
              "size": [
                3.78,
                4.05,
                0.8775
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
          "name": "turbine",
          "parent": "root",
          "pivot": [
            6,
            9.5,
            0
          ],
          "cubes": [
            {
              "origin": [
                5.96,
                7.5,
                -2
              ],
              "size": [
                0.8,
                4,
                4
              ],
              "uv": {
                "north": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    8,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    8,
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
                6.77,
                8.8,
                -2.5
              ],
              "size": [
                0.3,
                1.4,
                5
              ],
              "uv": {
                "north": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    16,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    16,
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
          "name": "pilot_light",
          "parent": "root",
          "pivot": [
            5.6,
            11,
            2.5
          ],
          "cubes": [
            {
              "origin": [
                5.45,
                10.3,
                1.8
              ],
              "size": [
                0.75,
                1.4,
                1.4
              ],
              "uv": {
                "north": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    24,
                    0
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    24,
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
          "name": "fuel_feed",
          "parent": "root",
          "pivot": [
            4.5,
            13.0,
            -1.5
          ],
          "cubes": [
            {
              "origin": [
                4.25,
                12.7,
                -3.8
              ],
              "size": [
                1.0,
                1.0,
                5.0
              ],
              "uv": {
                "north": {
                  "uv": [
                    0,
                    8
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "south": {
                  "uv": [
                    0,
                    8
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "east": {
                  "uv": [
                    0,
                    8
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "west": {
                  "uv": [
                    0,
                    8
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "up": {
                  "uv": [
                    0,
                    8
                  ],
                  "uv_size": [
                    8,
                    8
                  ]
                },
                "down": {
                  "uv": [
                    0,
                    8
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

## `src/main/resources/assets/carnis/animations/item/bio_purifier.animation.json`

```json
{
  "format_version": "1.8.0",
  "animations": {
    "animation.bio_purifier.idle": {
      "loop": true,
      "animation_length": 2.0,
      "bones": {
        "root": {
          "rotation": {
            "0.0": [
              2,
              0,
              -3
            ],
            "1.0": [
              3,
              0,
              -4
            ],
            "2.0": [
              2,
              0,
              -3
            ]
          },
          "position": {
            "0.0": [
              0,
              0,
              0
            ],
            "1.0": [
              0,
              0.12,
              0
            ],
            "2.0": [
              0,
              0,
              0
            ]
          }
        },
        "turbine": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.5": [
              90,
              0,
              0
            ],
            "1.0": [
              180,
              0,
              0
            ],
            "1.5": [
              270,
              0,
              0
            ],
            "2.0": [
              360,
              0,
              0
            ]
          }
        },
        "fuel_feed": {
          "position": {
            "0.0": [
              0,
              0,
              0
            ],
            "1.0": [
              0,
              0.12,
              0
            ],
            "2.0": [
              0,
              0,
              0
            ]
          }
        }
      }
    },
    "animation.bio_purifier.firing": {
      "loop": true,
      "animation_length": 0.2,
      "bones": {
        "root": {
          "rotation": {
            "0.0": [
              1,
              0,
              -3
            ],
            "0.05": [
              -6,
              1,
              -5
            ],
            "0.1": [
              3,
              -1,
              -2
            ],
            "0.15": [
              -4,
              2,
              -4
            ],
            "0.2": [
              1,
              0,
              -3
            ]
          },
          "position": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.05": [
              0,
              0,
              1.3
            ],
            "0.1": [
              0.2,
              0,
              -0.3
            ],
            "0.15": [
              -0.2,
              0,
              0.8
            ],
            "0.2": [
              0,
              0,
              0
            ]
          }
        },
        "turbine": {
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.05": [
              90,
              0,
              0
            ],
            "0.1": [
              180,
              0,
              0
            ],
            "0.15": [
              270,
              0,
              0
            ],
            "0.2": [
              360,
              0,
              0
            ]
          }
        },
        "fuel_feed": {
          "position": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.1": [
              0,
              0,
              0.5
            ],
            "0.2": [
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

## `src/main/resources/assets/carnis/models/item/bio_purifier.json`

```json
{
  "parent": "builtin/entity",
  "textures": {
    "particle": "carnis:item/bio_purifier"
  },
  "display": {
    "thirdperson_righthand": {
      "rotation": [
        0,
        90,
        -35
      ],
      "translation": [
        0,
        2,
        1
      ],
      "scale": [
        0.55,
        0.55,
        0.55
      ]
    },
    "firstperson_righthand": {
      "rotation": [
        0,
        90,
        0
      ],
      "translation": [
        1,
        2,
        1
      ],
      "scale": [
        0.7,
        0.7,
        0.7
      ]
    },
    "gui": {
      "rotation": [
        30,
        225,
        0
      ],
      "translation": [
        0,
        0,
        0
      ],
      "scale": [
        0.65,
        0.65,
        0.65
      ]
    },
    "firstperson_lefthand": {
      "rotation": [
        0,
        270,
        0
      ],
      "translation": [
        -1,
        2,
        1
      ],
      "scale": [
        0.7,
        0.7,
        0.7
      ]
    },
    "thirdperson_lefthand": {
      "rotation": [
        0,
        270,
        35
      ],
      "translation": [
        0,
        2,
        1
      ],
      "scale": [
        0.55,
        0.55,
        0.55
      ]
    }
  }
}
```

## `src/main/resources/assets/carnis/particles/purifier_flame.json`

```json
{
  "textures": [
    "carnis:purifier_flame"
  ]
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
  }
}
```

