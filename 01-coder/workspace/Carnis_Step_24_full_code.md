# Шаг 24 — полный код и текстовые ресурсы

## `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoBlockEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
import javax.annotation.Nullable;
import java.lang.ref.WeakReference;

public final class HiveEyeBlockEntity extends BlockEntity implements GeoBlockEntity {
    public static final int SCAN_INTERVAL_TICKS = 20;
    public static final double PLAYER_SCAN_RADIUS = 18D;
    public static final double HIVEMIND_ALERT_RADIUS = 28D;
    private static final java.util.Set<String> AUDIBLE_EVENTS = java.util.Set.of(
            "step", "hit_ground", "projectile_shoot", "projectile_land", "block_destroy",
            "entity_action", "entity_interact", "entity_damage", "entity_roar", "entity_place");
    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private final net.minecraft.world.level.gameevent.GameEventListener vibrationListener = new EyeListener();

    public net.minecraft.world.level.gameevent.GameEventListener getVibrationListener() { return vibrationListener; }

    private final class EyeListener implements net.minecraft.world.level.gameevent.GameEventListener {
        private final net.minecraft.world.level.gameevent.PositionSource source =
                new net.minecraft.world.level.gameevent.BlockPositionSource(worldPosition);
        @Override public net.minecraft.world.level.gameevent.PositionSource getListenerSource() { return source; }
        @Override public int getListenerRadius() { return 16; }
        @Override public boolean handleGameEvent(ServerLevel level, net.minecraft.world.level.gameevent.GameEvent event,
                net.minecraft.world.level.gameevent.GameEvent.Context context, Vec3 position) {
            var id = net.minecraft.core.registries.BuiltInRegistries.GAME_EVENT.getKey(event);
            if (id == null || !id.getNamespace().equals("minecraft") || !AUDIBLE_EVENTS.contains(id.getPath())) return false;
            net.minecraft.world.entity.Entity origin = context.sourceEntity();
            if (origin instanceof net.minecraft.world.entity.projectile.Projectile projectile && projectile.getOwner() != null)
                origin = projectile.getOwner();
            if (!(origin instanceof LivingEntity living) || !isTarget(living)
                    || living instanceof Player player && (player.isSteppingCarefully() || NeuroArmorEventHandler.hasFullSet(player))
                    || position.distanceToSqr(Vec3.atCenterOf(worldPosition)) > 256D) return false;
            hear(level, living);
            return true;
        }
    }
    private WeakReference<LivingEntity> tracked = new WeakReference<>(null);
    private long alertUntil;
    private boolean clientAlert;
    private float yaw, pitch, previousYaw, previousPitch;
    public HiveEyeBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.HIVE_EYE.get(), pos, state); }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return animationCache; }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "blink", 0, state -> state.setAndContinue(RawAnimation.begin()
                .thenLoop(isAlert() ? "animation.hive_eye.alert" : "animation.hive_eye.idle"))));
    }
    public boolean isAlert() { return level != null && (level.isClientSide ? clientAlert : level.getGameTime() < alertUntil); }
    public float trackingYaw(float partial) { return Mth.lerp(partial, previousYaw, yaw); }
    public float trackingPitch(float partial) { return Mth.lerp(partial, previousPitch, pitch); }
    @Override public CompoundTag getUpdateTag() {
        CompoundTag tag = new CompoundTag(); tag.putBoolean("Alert", isAlert()); return tag;
    }
    @Nullable @Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
    @Override public void handleUpdateTag(CompoundTag tag) { clientAlert = tag.getBoolean("Alert"); }
    @Override public void onDataPacket(Connection connection, ClientboundBlockEntityDataPacket packet) {
        if (packet.getTag() != null) handleUpdateTag(packet.getTag());
    }
    public static void serverTick(Level world, BlockPos pos, BlockState state, HiveEyeBlockEntity eye) {
        if (!(world instanceof ServerLevel level)) return;
        if (eye.alertUntil != 0 && level.getGameTime() >= eye.alertUntil) {
            eye.alertUntil = 0;
            level.sendBlockUpdated(pos, state, state, 3);
        }
        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), SCAN_INTERVAL_TICKS), SCAN_INTERVAL_TICKS) == 0) {
            HiveNetwork.observe(level, pos, state, true);
            LivingEntity nearest = eye.findNearest(level);
            if (nearest != null) nearest.addEffect(new MobEffectInstance(MobEffects.GLOWING, 100, 0));
        }
    }
    /** Called when a tracked game event has an eligible living source. */
    public void hear(ServerLevel level, LivingEntity source) {
        if (!isTarget(source) || source.distanceToSqr(Vec3.atCenterOf(worldPosition)) > 144D
                || source instanceof Player player && NeuroArmorEventHandler.hasFullSet(player)) return;
        boolean wasAlert = isAlert();
        alertUntil = level.getGameTime() + 60;
        if (!wasAlert) {
            level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
            level.playSound(null, worldPosition, ModSounds.HIVE_ALARM.get(), SoundSource.BLOCKS, 1.25F, .92F);
            level.sendParticles(ParticleTypes.ELECTRIC_SPARK, worldPosition.getX() + .5D, worldPosition.getY() + .8D,
                    worldPosition.getZ() + .5D, 12, .25D, .2D, .25D, .02D);
        }
        HiveSwarmCoordinator.eyeAlarm(level, worldPosition, source);
    }
    private static boolean isTarget(LivingEntity entity) {
        return entity.isAlive() && !entity.isSpectator() && !NeuralMossBlock.isHive(entity)
                && (!(entity instanceof Player player) || !player.isCreative() && !NeuroArmorEventHandler.hasFullSet(player));
    }
    @Nullable private LivingEntity findNearest(Level level) {
        Vec3 center = Vec3.atCenterOf(worldPosition);
        LivingEntity nearest = null;
        double best = PLAYER_SCAN_RADIUS * PLAYER_SCAN_RADIUS;
        for (LivingEntity candidate : level.getEntitiesOfClass(LivingEntity.class,
                AABB.ofSize(center, 36, 36, 36), HiveEyeBlockEntity::isTarget)) {
            double d = candidate.position().distanceToSqr(center);
            if (d <= best) { best = d; nearest = candidate; }
        }
        return nearest;
    }
    public static void clientTick(Level level, BlockPos pos, BlockState state, HiveEyeBlockEntity eye) {
        eye.previousYaw = eye.yaw;
        eye.previousPitch = eye.pitch;
        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), 10), 10) == 0)
            eye.tracked = new WeakReference<>(eye.findNearest(level));
        LivingEntity target = eye.tracked.get();
        float wantedYaw = 0, wantedPitch = 0;
        if (target != null && isTarget(target) && target.position().distanceToSqr(Vec3.atCenterOf(pos)) <= 324D) {
            Vec3 delta = target.getEyePosition().subtract(pos.getX() + .5D, pos.getY() + .5625D, pos.getZ() + .5D);
            double horizontal = Math.sqrt(delta.x * delta.x + delta.z * delta.z);
            if (horizontal > 1.0E-5D) wantedYaw = (float) Mth.clamp(Math.atan2(delta.x, -delta.z), -.7D, .7D);
            wantedPitch = (float) Mth.clamp(-Math.atan2(delta.y, Math.max(horizontal, .001D)), -.6D, .6D);
        }
        eye.yaw += (wantedYaw - eye.yaw) * .18F;
        eye.pitch += (wantedPitch - eye.pitch) * .18F;
    }
}
```

## `src/main/java/com/carnis/mod/block/HiveEyeBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.block.entity.HiveEyeBlockEntity;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;

public final class HiveEyeBlock extends BaseEntityBlock {
    @Override public void onPlace(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState old, boolean moving) {
        super.onPlace(state, level, pos, old, moving);
        if (!old.is(state.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
    }
    @Override public void onRemove(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
        super.onRemove(state, level, pos, next, moving);
    }
    public HiveEyeBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.ENTITYBLOCK_ANIMATED;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return ModBlockEntities.HIVE_EYE.get().create(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> net.minecraft.world.level.gameevent.GameEventListener getListener(
            net.minecraft.server.level.ServerLevel level, T blockEntity) {
        return blockEntity instanceof HiveEyeBlockEntity eye ? eye.getVibrationListener() : null;
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
            Level level,
            BlockState state,
            BlockEntityType<T> blockEntityType
    ) {
        if (level.isClientSide()) {
            return createTickerHelper(blockEntityType, ModBlockEntities.HIVE_EYE.get(), HiveEyeBlockEntity::clientTick);
        }

        return createTickerHelper(
                blockEntityType,
                ModBlockEntities.HIVE_EYE.get(),
                HiveEyeBlockEntity::serverTick
        );
    }
}
```

## `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundInstance.java`

```java
package com.carnis.mod.client.sound;

import com.carnis.mod.init.ModSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;

/** Non-positional bed controlled by the locally sampled Hive intensity. */
public final class HiveAmbientSoundInstance extends AbstractTickableSoundInstance {
    private final ClientLevel world;
    private float desired;
    public HiveAmbientSoundInstance(ClientLevel world, float target) {
        super(ModSounds.HIVE_AMBIENT_DRONE.get(), SoundSource.AMBIENT, SoundInstance.createUnseededRandom());
        this.world = world;
        this.looping = true;
        this.delay = 0;
        this.relative = true;
        this.attenuation = SoundInstance.Attenuation.NONE;
        this.volume = 0F;
        this.pitch = 1F;
        setTarget(target);
    }
    public void setTarget(float target) { desired = Mth.clamp(target, 0F, .85F); }
    public void end() { stop(); }
    @Override public boolean canStartSilent() { return true; }
    @Override public void tick() {
        Minecraft client = Minecraft.getInstance();
        if (client.level != world || client.player == null) { stop(); return; }
        float difference = desired - volume;
        volume += Mth.clamp(difference, -.025F, .025F);
        if (desired <= 0F && volume <= .001F) stop();
    }
}
```

## `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java`

```java
package com.carnis.mod.client.sound;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** One client sampler, with a fixed per-tick budget and no chunk loading. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class HiveAmbientSoundHandler {
    private static final int RADIUS = 16, SIDE = 33, VOLUME = SIDE * SIDE * SIDE, BUDGET = 2048;
    private static ClientLevel sampledWorld;
    private static BlockPos center;
    private static int cursor, tissue;
    private static double nearestHeart, nearestTissue;
    private static HiveAmbientSoundInstance sound;
    private HiveAmbientSoundHandler() { }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft client = Minecraft.getInstance();
        ClientLevel level = client.level;
        if (level == null || client.player == null || level != sampledWorld) {
            if (sound != null) sound.end();
            sound = null;
            sampledWorld = level;
            center = null;
            cursor = VOLUME;
            if (level == null || client.player == null) return;
        }
        if (center == null || cursor >= VOLUME && level.getGameTime() % 20L == 0L) {
            center = client.player.blockPosition().immutable();
            cursor = 0;
            tissue = 0;
            nearestHeart = Double.POSITIVE_INFINITY;
            nearestTissue = Double.POSITIVE_INFINITY;
        }
        if (cursor >= VOLUME) return;
        int end = Math.min(VOLUME, cursor + BUDGET);
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        while (cursor < end) {
            int index = cursor++;
            int dx = index % SIDE - RADIUS;
            int dy = index / SIDE % SIDE - RADIUS;
            int dz = index / (SIDE * SIDE) - RADIUS;
            int distanceSq = dx * dx + dy * dy + dz * dz;
            if (distanceSq > RADIUS * RADIUS) continue;
            pos.set(center.getX() + dx, center.getY() + dy, center.getZ() + dz);
            if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) continue;
            BlockState state = level.getBlockState(pos);
            if (state.is(ModBlocks.PULSING_HEART.get()) && level.getBlockEntity(pos) instanceof PulsingHeartBlockEntity)
                nearestHeart = Math.min(nearestHeart, Math.sqrt(distanceSq));
            else if (state.is(ModBlocks.LIVING_FLESH.get()) || state.is(ModBlocks.FLESH_VEINS.get())) {
                tissue++;
                nearestTissue = Math.min(nearestTissue, Math.sqrt(distanceSq));
            }
        }
        if (cursor < VOLUME) return;
        float target = 0F;
        if (Double.isFinite(nearestHeart)) target = .85F * (float) (1D - nearestHeart / 17D);
        if (tissue > 10 && Double.isFinite(nearestTissue))
            target = Math.max(target, .55F * (float) (1D - nearestTissue / 17D));
        target = Mth.clamp(target, 0F, .85F);
        if (sound != null && sound.isStopped()) sound = null;
        if (target > 0F && sound == null) {
            sound = new HiveAmbientSoundInstance(level, target);
            client.getSoundManager().play(sound);
        } else if (sound != null) sound.setTarget(target);
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
    public static final RegistryObject<SoundEvent> HIVE_ALARM =
            registerVariableRangeSound("hive_alarm");
    public static final RegistryObject<SoundEvent> HIVE_AMBIENT_DRONE =
            registerVariableRangeSound("hive_ambient_drone");
    public static final RegistryObject<SoundEvent> CREEPER_RUPTURE =
            registerVariableRangeSound("creeper_rupture");

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
        event.registerEntityRenderer(ModEntities.AMALGAM_BILE.get(), net.minecraft.client.renderer.entity.ThrownItemRenderer::new);
        event.registerEntityRenderer(ModEntities.HIVE_SPORE_CLOUD.get(), net.minecraft.client.renderer.entity.NoopRenderer::new);
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
        goalSelector.addGoal(1, new CarnisFeedingGoal(this));
        goalSelector.addGoal(2, new CarnisGestationGoal(this));
        targetSelector.addGoal(3, new CarnisHuntPreyGoal(this));
    }
    public static AttributeSupplier.Builder createAttributes() {
        return Creeper.createAttributes().add(Attributes.MAX_HEALTH, 24.0D);
    }

    private boolean ruptured;

    /** Replaces the canceled vanilla explosion; the event listener guarantees server authority. */
    public void rupture(ServerLevel level) {
        if (ruptured) return;
        ruptured = true;
        double radius = 4.5D;
        level.playSound(null, blockPosition(), ModSounds.CREEPER_RUPTURE.get(), SoundSource.HOSTILE, 2F, .7F);
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
        add("tooltip.carnis.purification_dart.mechanics", "Players: removes 35 infection and clears nausea, blindness and slowness.");
        add("tooltip.carnis.purification_dart.protocol", "Regresses infected humanoids; damages and stuns major Hive organisms.");
        add("tooltip.carnis.viral_dart.mechanics", "Players: adds 25 infection and causes weakness.");
        add("tooltip.carnis.viral_dart.protocol", "Accelerates livestock incubation; mutates zombies, skeletons and creepers.");
        add("tooltip.carnis.dart.use", "Load in the Pneumatic Inoculator and fire at the target.");
        add("subtitles.carnis.hive_alarm", "Hive eye screams");
        add("subtitles.carnis.hive_ambient_drone", "The Hive breathes");
        add("subtitles.carnis.creeper_rupture", "Biological rupture");
        add("entity.carnis.hive_spore_cloud", "Hive Spore Cloud");
        add("tooltip.carnis.purification_serum.mechanics", "Drink to remove 35 infection points.");
        add("tooltip.carnis.purification_serum.use", "Use directly or craft into purification darts.");
        add("entity.carnis.inoculator_dart", "Inoculator Dart");
        add("tooltip.carnis.viral_dart", "Adds 30 infection to players; poisons and slows mobs.");
        add("tooltip.carnis.purification_dart", "Removes 35 infection or damages Carnis mobs for 25.");
        add("tooltip.carnis.hold_shift", "Hold Shift for details");
        add("tooltip.carnis.living_flesh", "Living tissue spreads through nearby terrain.");
        add("tooltip.carnis.charred_flesh", "Burned tissue yields bone meal and charcoal.");
        add("tooltip.carnis.spore_sprout", "An organic sprout releases drifting spores.");
        add("tooltip.carnis.neural_moss", "A fleshy carpet impedes movement.");
        add("tooltip.carnis.neural_moss.mechanics", "Slows outsiders; spreads near water or Hive tissue.");
        add("tooltip.carnis.neural_moss.lore", "A living carpet listens for unfamiliar footsteps.");
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
        add("entity.carnis.assimilated_player", "Assimilated %s");
        add("death.attack.organic_consumption", "%1$s was consumed by the hive");
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
        add("tooltip.carnis.purification_dart.mechanics", "Игрок: −35 заражения; снимает тошноту, слепоту и замедление.");
        add("tooltip.carnis.purification_dart.protocol", "Обращает мутацию гуманоидов; ранит и оглушает крупные организмы Улья.");
        add("tooltip.carnis.viral_dart.mechanics", "Игрок: +25 заражения и слабость.");
        add("tooltip.carnis.viral_dart.protocol", "Ускоряет инкубацию скота; мутирует зомби, скелетов и криперов.");
        add("tooltip.carnis.dart.use", "Зарядите пневматический инокулятор и выстрелите в цель.");
        add("subtitles.carnis.hive_alarm", "Око Улья кричит");
        add("subtitles.carnis.hive_ambient_drone", "Улей дышит");
        add("subtitles.carnis.creeper_rupture", "Биологический разрыв");
        add("entity.carnis.hive_spore_cloud", "Споровое облако Улья");
        add("tooltip.carnis.purification_serum.mechanics", "Выпейте, чтобы снять 35 очков заражения.");
        add("tooltip.carnis.purification_serum.use", "Выпейте напрямую или изготовьте дротики очищения.");
        add("entity.carnis.inoculator_dart", "Дротик инокулятора");
        add("tooltip.carnis.purification_dart", "Снимает 35 заражения или наносит мобам Carnis 25 урона.");
        add("tooltip.carnis.hold_shift", "Удерживайте Shift для подробностей");
        add("tooltip.carnis.living_flesh", "Живая ткань распространяется по окружающим блокам.");
        add("tooltip.carnis.charred_flesh", "Обгоревшая ткань даёт костную муку и уголь.");
        add("tooltip.carnis.spore_sprout", "Органический росток выпускает споры.");
        add("tooltip.carnis.neural_moss", "Мясистый мох замедляет движение.");
        add("tooltip.carnis.neural_moss.mechanics", "Замедляет чужаков; растёт у воды и тканей Улья.");
        add("tooltip.carnis.neural_moss.lore", "Живой ковёр прислушивается к чужим шагам.");
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
        add("entity.carnis.assimilated_player", "Ассимилированный %s");
        add("death.attack.organic_consumption", "%1$s был поглощён Ульем");
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
  },
  "hive_alarm": {
    "subtitle": "subtitles.carnis.hive_alarm",
    "sounds": [
      {
        "name": "carnis:block/hive_eye_screech",
        "volume": 1.0,
        "pitch": 0.9,
        "stream": false
      }
    ]
  },
  "hive_ambient_drone": {
    "subtitle": "subtitles.carnis.hive_ambient_drone",
    "sounds": [
      {
        "name": "carnis:block/hive_ambient_drone",
        "stream": true
      }
    ]
  },
  "creeper_rupture": {
    "subtitle": "subtitles.carnis.creeper_rupture",
    "sounds": [
      {
        "name": "carnis:block/synapse_rupture",
        "pitch": 0.9,
        "volume": 1.0
      }
    ]
  }
}
```

## `src/main/resources/assets/carnis/particles/biomass_spark.json`

```json
{
  "textures": [
    "carnis:biomass_spark"
  ]
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

## `src/generated/resources/assets/carnis/lang/en_us.json`

```json
{
  "block.carnis.charred_flesh": "Charred Flesh",
  "block.carnis.creeping_tendrils": "Creeping Tendrils",
  "block.carnis.fireproof_flesh": "Fireproof Flesh",
  "block.carnis.flesh_bulb": "Flesh Bulb",
  "block.carnis.flesh_veins": "Flesh Veins",
  "block.carnis.hive_eye": "Hive Eye",
  "block.carnis.living_flesh": "Living Flesh",
  "block.carnis.nerve_pillar": "Nerve Pillar",
  "block.carnis.neural_moss": "Neural Moss",
  "block.carnis.ossified_flesh": "Ossified Flesh",
  "block.carnis.pulsing_heart": "Pulsing Heart",
  "block.carnis.pustule_cluster": "Pustule Cluster",
  "block.carnis.sinew_spikes": "Sinew Spikes",
  "block.carnis.spore_sprout": "Spore Sprout",
  "block.carnis.stomach_pool": "Stomach Pool",
  "block.carnis.tainted_sludge": "Tainted Sludge",
  "codex.carnis.body.0": "Veins spread across supported faces; incomplete faces may resist growth. Sludge contaminates players and reacts with water and lava. Infection spreads by a queued process.",
  "codex.carnis.body.1": "FIRE / RANGED / MELEE / EXPLOSIVE use the same logarithmic mitigation curve. Points: 0 / 100 / 300 / 600 / 1000. Reduction: 0% / 25% / 50% / 70% / 80%. Between thresholds: linear interpolation in ln(1+points). Cap 80%.",
  "codex.carnis.body.2": "Hive Eye detects players within 24 blocks and alerts linked mobs within 32. Placing a Nerve Pillar halves remaining chunk shock. Stomach Pool dissolves items: flesh or meat gives 5 biomass each; other items give 1. Living creatures take 4 damage per second.",
  "codex.carnis.body.3": "Serum reduces infection by 35. Antibiotics block positive exposure for 3600 ticks. On an anvil, combine armor and one neural binding matrix for 5 levels. Each woven or resonator armor piece reduces exposure by 25%; four pieces reach 100%.",
  "codex.carnis.body.4": "Zombie: 35 health, 4.5 attack; skeleton: 28 health, 4.5 attack; creeper: 24 health; spider: 20 health, 3 attack. Spat: 2 damage, Slowness II for 100 ticks and +5 exposure on successful damage. Three zombies near a heart at 300 biomass can fuse.",
  "codex.carnis.chapter.0": "Inception & Biomes",
  "codex.carnis.chapter.1": "Adaptive Hivemind",
  "codex.carnis.chapter.2": "Hive Organs & Flora",
  "codex.carnis.chapter.3": "Medical & Armor Weaving",
  "codex.carnis.chapter.4": "Mutants & Amalgamation",
  "death.attack.bio_purifier": "%1$s was incinerated by a bio-purifier",
  "death.attack.bio_purifier.player": "%1$s was incinerated by %2$s's bio-purifier",
  "death.attack.carnis_tainted_sludge": "%1$s dissolved in tainted sludge",
  "death.attack.necrotic_consumption": "%1$s was consumed by the hivemind",
  "death.attack.purification_dart": "%1$s was purified by a dart",
  "death.attack.purification_dart.player": "%1$s was purified by %2$s",
  "effect.carnis.immunosuppression": "Immunosuppression",
  "effect.carnis.incubating": "Incubating",
  "entity.carnis.biomass_maggot": "Biomass Maggot",
  "entity.carnis.flesh_amalgam": "Flesh Amalgam",
  "entity.carnis.flesh_spat": "Flesh Spat",
  "entity.carnis.infected_creeper": "Infected Creeper",
  "entity.carnis.infected_skeleton": "Infected Skeleton",
  "entity.carnis.infected_spider": "Infected Spider",
  "entity.carnis.infected_zombie": "Infected Zombie",
  "entity.carnis.parasitic_tendril": "Parasitic Tendril",
  "entity.carnis.purification_dart": "Purification Dart",
  "entity.carnis.viral_dart": "Viral Dart",
  "fluid_type.carnis.tainted_sludge": "Tainted Sludge",
  "item.carnis.antibiotics": "Antibiotics",
  "item.carnis.bio_purifier": "Bio-Purifier",
  "item.carnis.biomass_maggot_spawn_egg": "Biomass Maggot Spawn Egg",
  "item.carnis.bone_scythe_arm": "Bone Scythe Arm",
  "item.carnis.flesh_amalgam_spawn_egg": "Flesh Amalgam Spawn Egg",
  "item.carnis.flesh_spat": "Flesh Spat",
  "item.carnis.infected_creeper_spawn_egg": "Infected Creeper Spawn Egg",
  "item.carnis.infected_skeleton_spawn_egg": "Infected Skeleton Spawn Egg",
  "item.carnis.infected_spider_spawn_egg": "Infected Spider Spawn Egg",
  "item.carnis.infected_zombie_spawn_egg": "Infected Zombie Spawn Egg",
  "item.carnis.neural_binding_matrix": "Neural Binding Matrix",
  "item.carnis.neuro_resonator_boots": "Neuro-Resonator Boots",
  "item.carnis.neuro_resonator_chestplate": "Neuro-Resonator Chestplate",
  "item.carnis.neuro_resonator_helmet": "Neuro-Resonator Helmet",
  "item.carnis.neuro_resonator_leggings": "Neuro-Resonator Leggings",
  "item.carnis.pneumatic_inoculator": "Pneumatic Inoculator",
  "item.carnis.purification_dart": "Purification Dart",
  "item.carnis.purification_serum": "Purification Serum",
  "item.carnis.research_journal": "Codex Carnis",
  "item.carnis.tainted_sludge_bucket": "Tainted Sludge Bucket",
  "item.carnis.viral_dart": "Viral Dart",
  "itemGroup.carnis": "Carnis: Adaptive Hivemind",
  "subtitles.carnis.acid_splash": "Corrosive acid splashes",
  "subtitles.carnis.amalgam_roar": "Amalgam roars",
  "subtitles.carnis.amalgam_step": "Flesh Amalgam squelches",
  "subtitles.carnis.amalgamation_fuse": "Flesh fuses into an amalgam",
  "subtitles.carnis.bone_deflect": "A projectile ricochets off bone",
  "subtitles.carnis.digestor_churn": "A digestor churns",
  "subtitles.carnis.flamethrower_fire": "Flamethrower roars",
  "subtitles.carnis.flesh_amalgam_ambient": "The Flesh Amalgam groans",
  "subtitles.carnis.flesh_amalgam_death": "The Flesh Amalgam collapses",
  "subtitles.carnis.flesh_amalgam_hurt": "The Flesh Amalgam recoils",
  "subtitles.carnis.heartbeat_loop": "Heart beats",
  "subtitles.carnis.hive_eye_screech": "The hive eye shrieks",
  "subtitles.carnis.phantom_creeper": "Something hisses behind you",
  "subtitles.carnis.phantom_footsteps": "Footsteps squelch through flesh",
  "subtitles.carnis.phantom_whisper": "The hivemind whispers",
  "subtitles.carnis.pulsing_heart_beat": "A biome heart beats",
  "subtitles.carnis.synapse_rupture": "Nerve tissue tears apart",
  "subtitles.carnis.synapse_shock": "A synapse discharges",
  "tooltip.carnis.antibiotics": "Prevents exposure for 3 minutes.",
  "tooltip.carnis.bio_purifier": "Hold use: 6.5-block cone of flame.",
  "tooltip.carnis.bone_scythe_arm": "A jagged bone blade.",
  "tooltip.carnis.charred_flesh": "Burned tissue yields bone meal and charcoal.",
  "tooltip.carnis.creeping_tendrils": "Climb the tendrils attached to solid flesh.",
  "tooltip.carnis.fireproof_flesh": "Adapted tissue resistant to flame.",
  "tooltip.carnis.flesh_amalgam_spawn_egg": "Spawns a Flesh Amalgam.",
  "tooltip.carnis.flesh_spat": "A glob of infectious tissue.",
  "tooltip.carnis.flesh_veins": "Organic growth on exposed surfaces.",
  "tooltip.carnis.hive_eye": "Detects intruders and alerts nearby Amalgams.",
  "tooltip.carnis.hold_shift": "Hold Shift for details",
  "tooltip.carnis.infected_creeper_spawn_egg": "Spawns an infected creeper.",
  "tooltip.carnis.infected_skeleton_spawn_egg": "Spawns an infected skeleton.",
  "tooltip.carnis.infected_spider_spawn_egg": "Spawns an infected spider.",
  "tooltip.carnis.infected_zombie_spawn_egg": "Spawns an infected zombie.",
  "tooltip.carnis.living_flesh": "Living tissue spreads through nearby terrain.",
  "tooltip.carnis.nerve_pillar": "Placement halves remaining shock time in this chunk.",
  "tooltip.carnis.neural_binding_matrix": "Weave into armor at an anvil for five levels.",
  "tooltip.carnis.neural_moss": "A fleshy carpet impedes movement.",
  "tooltip.carnis.neuro_resonator_boots": "Biological boots reduce infection exposure.",
  "tooltip.carnis.neuro_resonator_chestplate": "A biological chestplate reduces infection exposure.",
  "tooltip.carnis.neuro_resonator_helmet": "Dampens hallucinations, reduces exposure by 25% and reveals nearby biomass.",
  "tooltip.carnis.neuro_resonator_leggings": "Biological leggings reduce infection exposure.",
  "tooltip.carnis.ossified_flesh": "Hardened tissue spreads the hive.",
  "tooltip.carnis.pneumatic_inoculator": "Right-click to fire a carried dart; 15-tick cooldown.",
  "tooltip.carnis.pulsing_heart": "The hive heart accelerates nearby infection.",
  "tooltip.carnis.purification_dart": "Removes 35 infection or damages Carnis mobs for 25.",
  "tooltip.carnis.purification_serum": "Drink to remove 35 infection points.",
  "tooltip.carnis.pustule_cluster": "Step on it without sneaking to burst infectious spores.",
  "tooltip.carnis.research_journal": "A field guide to the hive.",
  "tooltip.carnis.spore_sprout": "An organic sprout releases drifting spores.",
  "tooltip.carnis.stomach_pool": "Corrosive tissue dissolves items into biomass.",
  "tooltip.carnis.tainted_sludge_bucket": "A bucket of infectious sludge.",
  "tooltip.carnis.veins": "Living veins carry infection through wood.",
  "tooltip.carnis.viral_dart": "Adds 30 infection to players; poisons and slows mobs.",
  "tooltip.carnis.flesh_bulb.mechanics": "An incubation sac that can attach to ceilings and floors.",
  "tooltip.carnis.flesh_bulb.lore": "The muffled, rapid heartbeat of a maturing brood can be heard inside.",
  "tooltip.carnis.sinew_spikes.mechanics": "Deals piercing damage and slows any creature that steps on it.",
  "tooltip.carnis.sinew_spikes.lore": "Taut sinews respond to the slightest vibration of footsteps.",
  "tooltip.carnis.biomass_maggot.mechanics": "A voracious scavenger. Devours organic remains and pupates in soil.",
  "tooltip.carnis.biomass_maggot.lore": "The first link in the Hive’s parasitic cycle.",
  "subtitles.carnis.inoculator_fire": "Inoculator fires",
  "subtitles.carnis.dart_hit": "Dart hits",
  "block.carnis.biomass_remains": "Biomass Remains",
  "entity.carnis.hive_sentinel": "Hive Sentinel",
  "entity.carnis.cerebral_nexus": "Cerebral Nexus",
  "effect.carnis.thermal_shock": "Thermal Shock",
  "subtitles.carnis.purifier_ignite": "Purifier ignites",
  "subtitles.carnis.purifier_loop": "Purifier fires",
  "item.carnis.amalgam_bile_glob": "Amalgam Bile",
  "entity.carnis.amalgam_bile": "Amalgam Bile",
  "tooltip.carnis.amalgam_bile_glob": "A corrosive organic glob.",
  "subtitles.carnis.amalgam_smash": "Amalgam slams the ground",
  "subtitles.carnis.organic_creak": "Sinew lashes",
  "entity.carnis.assimilated_player": "Assimilated %s",
  "death.attack.organic_consumption": "%1$s was consumed by the hive",
  "tooltip.carnis.neural_moss.mechanics": "Slows outsiders; spreads near water or Hive tissue.",
  "tooltip.carnis.neural_moss.lore": "A living carpet listens for unfamiliar footsteps.",
  "tooltip.carnis.purification_dart.mechanics": "Players: removes 35 infection and clears nausea, blindness and slowness.",
  "tooltip.carnis.purification_dart.protocol": "Regresses infected humanoids; damages and stuns major Hive organisms.",
  "tooltip.carnis.viral_dart.mechanics": "Players: adds 25 infection and causes weakness.",
  "tooltip.carnis.viral_dart.protocol": "Accelerates livestock incubation; mutates zombies, skeletons and creepers.",
  "tooltip.carnis.dart.use": "Load in the Pneumatic Inoculator and fire at the target.",
  "tooltip.carnis.purification_serum.mechanics": "Drink to remove 35 infection points.",
  "tooltip.carnis.purification_serum.use": "Use directly or craft into purification darts.",
  "entity.carnis.inoculator_dart": "Inoculator Dart",
  "subtitles.carnis.hive_alarm": "Hive eye screams",
  "entity.carnis.hive_spore_cloud": "Hive Spore Cloud",
  "subtitles.carnis.hive_ambient_drone": "The Hive breathes",
  "subtitles.carnis.creeper_rupture": "Biological rupture"
}
```

## `src/generated/resources/assets/carnis/lang/ru_ru.json`

```json
{
  "block.carnis.charred_flesh": "Обугленная плоть",
  "block.carnis.creeping_tendrils": "Ползучие щупальца",
  "block.carnis.fireproof_flesh": "Огнеупорная плоть",
  "block.carnis.flesh_bulb": "Мясная луковица",
  "block.carnis.flesh_veins": "Плотяные жилы",
  "block.carnis.hive_eye": "Око разума",
  "block.carnis.living_flesh": "Живая плоть",
  "block.carnis.nerve_pillar": "Нервный столп",
  "block.carnis.neural_moss": "Нервный мох",
  "block.carnis.ossified_flesh": "Окостенелая плоть",
  "block.carnis.pulsing_heart": "Сердце биома",
  "block.carnis.pustule_cluster": "Скопление пустул",
  "block.carnis.sinew_spikes": "Сухожильные шипы",
  "block.carnis.spore_sprout": "Споровый росток",
  "block.carnis.stomach_pool": "Желудочный бассейн",
  "block.carnis.tainted_sludge": "Заражённая слизь",
  "codex.carnis.body.0": "Вены растут по поддерживаемым граням; неполные грани могут мешать росту. Жижа заражает игроков и реагирует с водой и лавой. Распространение обрабатывается очередью.",
  "codex.carnis.body.1": "ОГОНЬ / ДАЛЬНИЙ / БЛИЖНИЙ / ВЗРЫВ: общая логарифмическая кривая. Очки: 0 / 100 / 300 / 600 / 1000. Снижение: 0% / 25% / 50% / 70% / 80%. Между порогами — интерполяция по ln(1+очки). Предел 80%.",
  "codex.carnis.body.2": "Глаз видит игроков в 24 блоках и предупреждает связанных мобов в 32. Установка нервного столба вдвое сокращает оставшийся шок чанка. Желудочный бассейн даёт 5 биомассы за мясо или плоть, 1 за иной предмет; живым наносит 4 урона в секунду.",
  "codex.carnis.body.3": "Сыворотка снижает заражение на 35. Антибиотики блокируют положительную экспозицию на 3600 тиков. На наковальне соедините броню с одной матрицей за 5 уровней. Каждая защищённая часть снижает экспозицию на 25%, четыре — на 100%.",
  "codex.carnis.body.4": "Зомби: 35 здоровья, 4,5 урона; скелет: 28 и 4,5; крипер: 24 здоровья; паук: 20 и 3. Плевок: 2 урона, замедление II на 100 тиков и +5 экспозиции при успешном уроне. Три зомби у сердца при 300 биомассы могут слиться.",
  "codex.carnis.chapter.0": "Истоки и биомы",
  "codex.carnis.chapter.1": "Адаптивный разум",
  "codex.carnis.chapter.2": "Органы и флора улья",
  "codex.carnis.chapter.3": "Медицина и нейроплетение",
  "codex.carnis.chapter.4": "Мутанты и слияние",
  "death.attack.bio_purifier": "%1$s сожжён биоочистителем",
  "death.attack.bio_purifier.player": "%1$s сожжён биоочистителем игрока %2$s",
  "death.attack.carnis_tainted_sludge": "%1$s растворился в заражённой жиже",
  "death.attack.necrotic_consumption": "%1$s поглощён коллективным разумом",
  "death.attack.purification_dart": "%1$s очищен дротиком",
  "death.attack.purification_dart.player": "%1$s очищен игроком %2$s",
  "effect.carnis.immunosuppression": "Иммуносупрессия",
  "effect.carnis.incubating": "Инкубация",
  "entity.carnis.biomass_maggot": "Личинка биомассы",
  "entity.carnis.flesh_amalgam": "Амальгама плоти",
  "entity.carnis.flesh_spat": "Плевок плоти",
  "entity.carnis.infected_creeper": "Заражённый крипер",
  "entity.carnis.infected_skeleton": "Заражённый скелет",
  "entity.carnis.infected_spider": "Заражённый паук",
  "entity.carnis.infected_zombie": "Заражённый зомби",
  "entity.carnis.parasitic_tendril": "Паразитический усик",
  "entity.carnis.purification_dart": "Очищающий дротик",
  "entity.carnis.viral_dart": "Вирусный дротик",
  "fluid_type.carnis.tainted_sludge": "Заражённая слизь",
  "item.carnis.antibiotics": "Антибиотики",
  "item.carnis.bio_purifier": "Очищающий огнемёт",
  "item.carnis.biomass_maggot_spawn_egg": "Яйцо призыва: Личинка биомассы",
  "item.carnis.bone_scythe_arm": "Костяная коса-рука",
  "item.carnis.flesh_amalgam_spawn_egg": "Яйцо призыва амальгамы плоти",
  "item.carnis.flesh_spat": "Плевок плоти",
  "item.carnis.infected_creeper_spawn_egg": "Яйцо призыва: Заражённый крипер",
  "item.carnis.infected_skeleton_spawn_egg": "Яйцо призыва: Заражённый скелет",
  "item.carnis.infected_spider_spawn_egg": "Яйцо призыва: Заражённый паук",
  "item.carnis.infected_zombie_spawn_egg": "Яйцо призыва заражённого зомби",
  "item.carnis.neural_binding_matrix": "Матрица нейронного сплетения",
  "item.carnis.neuro_resonator_boots": "Нейро-резонаторные ботинки",
  "item.carnis.neuro_resonator_chestplate": "Нейро-резонаторный нагрудник",
  "item.carnis.neuro_resonator_helmet": "Нейро-резонаторный шлем",
  "item.carnis.neuro_resonator_leggings": "Нейро-резонаторные поножи",
  "item.carnis.pneumatic_inoculator": "Пневматический инокулятор",
  "item.carnis.purification_dart": "Очищающий дротик",
  "item.carnis.purification_serum": "Очищающая сыворотка",
  "item.carnis.research_journal": "Кодекс Карнис",
  "item.carnis.tainted_sludge_bucket": "Ведро заражённой слизи",
  "item.carnis.viral_dart": "Вирусный дротик",
  "itemGroup.carnis": "Carnis: Адаптивный коллективный разум",
  "subtitles.carnis.acid_splash": "Едкая кислота брызжет",
  "subtitles.carnis.amalgam_roar": "Амальгама ревёт",
  "subtitles.carnis.amalgam_step": "Плотяная амальгама чавкает",
  "subtitles.carnis.amalgamation_fuse": "Плоть сливается в амальгаму",
  "subtitles.carnis.bone_deflect": "Снаряд рикошетит от кости",
  "subtitles.carnis.digestor_churn": "Желудочный пруд бурлит",
  "subtitles.carnis.flamethrower_fire": "Огнемёт ревёт",
  "subtitles.carnis.flesh_amalgam_ambient": "Амальгама плоти стонет",
  "subtitles.carnis.flesh_amalgam_death": "Амальгама плоти обрушивается",
  "subtitles.carnis.flesh_amalgam_hurt": "Амальгама плоти вздрагивает",
  "subtitles.carnis.heartbeat_loop": "Сердце бьётся",
  "subtitles.carnis.hive_eye_screech": "Око разума визжит",
  "subtitles.carnis.phantom_creeper": "Что-то шипит за спиной",
  "subtitles.carnis.phantom_footsteps": "Шаги хлюпают по плоти",
  "subtitles.carnis.phantom_whisper": "Коллективный разум шепчет",
  "subtitles.carnis.pulsing_heart_beat": "Сердце биома бьётся",
  "subtitles.carnis.synapse_rupture": "Нервная ткань разрывается",
  "subtitles.carnis.synapse_shock": "Нервный столб разряжается",
  "tooltip.carnis.antibiotics": "Предотвращает заражение на 3 минуты.",
  "tooltip.carnis.bio_purifier": "Удерживайте: конус пламени на 6,5 блока.",
  "tooltip.carnis.bone_scythe_arm": "Зазубренный костяной клинок.",
  "tooltip.carnis.charred_flesh": "Обгоревшая ткань даёт костную муку и уголь.",
  "tooltip.carnis.creeping_tendrils": "Взбирайтесь по усикам на поверхности плоти.",
  "tooltip.carnis.fireproof_flesh": "Ткань, приспособленная к огню.",
  "tooltip.carnis.flesh_amalgam_spawn_egg": "Призывает амальгаму плоти.",
  "tooltip.carnis.flesh_spat": "Сгусток заражённой ткани.",
  "tooltip.carnis.flesh_veins": "Органические жилы на открытых поверхностях.",
  "tooltip.carnis.hive_eye": "Обнаруживает чужаков и тревожит ближайших амальгам.",
  "tooltip.carnis.hold_shift": "Удерживайте Shift для подробностей",
  "tooltip.carnis.infected_creeper_spawn_egg": "Призывает заражённого крипера.",
  "tooltip.carnis.infected_skeleton_spawn_egg": "Призывает заражённого скелета.",
  "tooltip.carnis.infected_spider_spawn_egg": "Призывает заражённого паука.",
  "tooltip.carnis.infected_zombie_spawn_egg": "Призывает заражённого зомби.",
  "tooltip.carnis.living_flesh": "Живая ткань распространяется по окружающим блокам.",
  "tooltip.carnis.nerve_pillar": "При установке вдвое сокращает оставшийся шок чанка.",
  "tooltip.carnis.neural_binding_matrix": "Вплетите в броню на наковальне за пять уровней.",
  "tooltip.carnis.neural_moss": "Мясистый мох замедляет движение.",
  "tooltip.carnis.neuro_resonator_boots": "Биологические ботинки снижают заражение.",
  "tooltip.carnis.neuro_resonator_chestplate": "Биологический нагрудник снижает заражение.",
  "tooltip.carnis.neuro_resonator_helmet": "Подавляет галлюцинации, снижает экспозицию на 25% и обнаруживает биомассу.",
  "tooltip.carnis.neuro_resonator_leggings": "Биологические поножи снижают заражение.",
  "tooltip.carnis.ossified_flesh": "Окостеневшая ткань распространяет улей.",
  "tooltip.carnis.pneumatic_inoculator": "ПКМ: выстрел дротиком из инвентаря; задержка 15 тиков.",
  "tooltip.carnis.pulsing_heart": "Сердце улья ускоряет заражение поблизости.",
  "tooltip.carnis.purification_dart": "Снимает 35 заражения или наносит мобам Carnis 25 урона.",
  "tooltip.carnis.purification_serum": "Выпейте, чтобы снизить заражение на 35 пунктов.",
  "tooltip.carnis.pustule_cluster": "Наступите без приседания: пустулы лопнут и заразят вас.",
  "tooltip.carnis.research_journal": "Полевой справочник по улью.",
  "tooltip.carnis.spore_sprout": "Органический росток выпускает споры.",
  "tooltip.carnis.stomach_pool": "Едкая ткань растворяет предметы в биомассу.",
  "tooltip.carnis.tainted_sludge_bucket": "Ведро заразной слизи.",
  "tooltip.carnis.veins": "Живые вены несут инфекцию через древесину.",
  "tooltip.carnis.viral_dart": "Добавляет игрокам 30 заражения; травит и замедляет мобов.",
  "tooltip.carnis.flesh_bulb.mechanics": "Инкубационный мешок, способный закрепляться на потолке и полу.",
  "tooltip.carnis.flesh_bulb.lore": "Внутри слышно глухое, частое сердцебиение зреющего выводка.",
  "tooltip.carnis.sinew_spikes.mechanics": "Наносят колющий урон и замедляют любое наступившее существо.",
  "tooltip.carnis.sinew_spikes.lore": "Натянутые жилы реагируют на малейшую вибрацию шагов.",
  "tooltip.carnis.biomass_maggot.mechanics": "Ненасытный трупоед. Пожирает органические останки и окукливается в почве.",
  "tooltip.carnis.biomass_maggot.lore": "Начальное звено паразитического круговорота Улья.",
  "subtitles.carnis.inoculator_fire": "Выстрел инокулятора",
  "subtitles.carnis.dart_hit": "Дротик ударяется",
  "block.carnis.biomass_remains": "Останки биомассы",
  "entity.carnis.hive_sentinel": "Страж Улья",
  "entity.carnis.cerebral_nexus": "Мозговой узел",
  "effect.carnis.thermal_shock": "Термический шок",
  "subtitles.carnis.purifier_ignite": "Очиститель зажигается",
  "subtitles.carnis.purifier_loop": "Очиститель выпускает пламя",
  "item.carnis.amalgam_bile_glob": "Желчь амальгамы",
  "entity.carnis.amalgam_bile": "Желчь амальгамы",
  "tooltip.carnis.amalgam_bile_glob": "Едкий органический сгусток.",
  "subtitles.carnis.amalgam_smash": "Амальгама сотрясает землю",
  "subtitles.carnis.organic_creak": "Сухожилие хлещет",
  "entity.carnis.assimilated_player": "Ассимилированный %s",
  "death.attack.organic_consumption": "%1$s был поглощён Ульем",
  "tooltip.carnis.neural_moss.mechanics": "Замедляет чужаков; растёт у воды и тканей Улья.",
  "tooltip.carnis.neural_moss.lore": "Живой ковёр прислушивается к чужим шагам.",
  "tooltip.carnis.purification_dart.mechanics": "Игрок: −35 заражения; снимает тошноту, слепоту и замедление.",
  "tooltip.carnis.purification_dart.protocol": "Обращает мутацию гуманоидов; ранит и оглушает крупные организмы Улья.",
  "tooltip.carnis.viral_dart.mechanics": "Игрок: +25 заражения и слабость.",
  "tooltip.carnis.viral_dart.protocol": "Ускоряет инкубацию скота; мутирует зомби, скелетов и криперов.",
  "tooltip.carnis.dart.use": "Зарядите пневматический инокулятор и выстрелите в цель.",
  "tooltip.carnis.purification_serum.mechanics": "Выпейте, чтобы снять 35 очков заражения.",
  "tooltip.carnis.purification_serum.use": "Выпейте напрямую или изготовьте дротики очищения.",
  "entity.carnis.inoculator_dart": "Дротик инокулятора",
  "subtitles.carnis.hive_alarm": "Око Улья кричит",
  "entity.carnis.hive_spore_cloud": "Споровое облако Улья",
  "subtitles.carnis.hive_ambient_drone": "Улей дышит",
  "subtitles.carnis.creeper_rupture": "Биологический разрыв"
}
```
