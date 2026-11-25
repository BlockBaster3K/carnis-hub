package com.carnis.mod.block.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.item.NeuroWeave;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.tags.ItemTags;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TridentItem;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.gameevent.GameEventListener;
import net.minecraftforge.common.ToolActions;
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
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import javax.annotation.Nullable;
import java.util.Set;
import java.util.UUID;

public final class HiveEyeBlockEntity extends BlockEntity implements GeoBlockEntity, GameEventListener.Holder<GameEventListener> {
    public static final int SCAN_INTERVAL_TICKS = 20;
    public static final double PLAYER_SCAN_RADIUS = 18D;
    public static final double LOOK_RADIUS = 16D;
    public static final double THREAT_RADIUS = 16D;
    public static final double HIVEMIND_ALERT_RADIUS = 28D;
    private static final int SYNCHRONIZED_ALERT_RADIUS = 32;
    private static final int SYNCHRONIZED_ALERT_DURATION_TICKS = 100;
    private static final int SWARM_ALARM_COOLDOWN_TICKS = 20;
    public static final int CALM_STATE = 0;
    public static final int WATCHING_STATE = 1;
    public static final int SOFT_ALERT_STATE = 2;
    public static final int ALERT_STATE = SOFT_ALERT_STATE;
    public static final int FULL_ALERT_STATE = 3;

    private static final int PLAYER_STATE_SCAN_INTERVAL = 5;
    private static final int AURA_INTERVAL_TICKS = 40;
    private static final int AURA_EFFECT_DURATION_TICKS = 60;
    private static final int AURA_REFRESH_THRESHOLD_TICKS = 40;
    private static final int BLINK_DURATION_TICKS = 10;
    private static final int BLINK_MIN_TICKS = 80;
    private static final int BLINK_MAX_TICKS = 300;
    private static final int SCREECH_COOLDOWN_TICKS = 200;
    private static final int ARMED_WARNING_RADIUS = 8;
    private static final int ARMED_WARNING_TICKS = 40;
    private static final float MAX_LOOK_YAW = (float) Math.toRadians(20.0D);
    private static final float MAX_LOOK_PITCH = (float) Math.toRadians(15.0D);
    private static final float CLIENT_LERP_SPEED = 0.15F;
    private static final float STATE_LERP_STEP = 1.0F / 30.0F;
    private static final Set<String> AUDIBLE_EVENTS = Set.of(
            "step", "hit_ground", "projectile_shoot", "projectile_land", "block_destroy",
            "entity_action", "entity_interact", "entity_damage", "entity_roar", "entity_place");

    private static final RawAnimation IDLE_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.hive_eye.idle");
    private static final RawAnimation WATCHING_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.hive_eye.watching");
    private static final RawAnimation ALERT_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.hive_eye.alert");
    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private final net.minecraft.world.level.gameevent.GameEventListener vibrationListener = new EyeListener();

    private long alertUntil;
    private long hiveAttackUntil;
    private long lastSwarmAlarmTick = Long.MIN_VALUE;
    private int reinforcementCooldown;
    private int blinkCooldown;
    private int blinkTicksRemaining;
    private int alertLevel;
    private int screechCooldown;
    private int armedApproachTicks;
    private boolean blinking;
    private boolean blinkTimerInitialized;
    private boolean clientAlert;
    private boolean clientBlinking;
    private boolean targetPlayerPresent;
    private boolean armedScreechPending;
    private boolean reinforcementsCalled;
    @Nullable
    private LivingEntity pendingVibrationSource;
    private long clientBlinkStartedAt = Long.MIN_VALUE;
    private double previousArmedDistance = Double.MAX_VALUE;
    @Nullable
    private UUID armedTargetId;
    private float targetYaw;
    private float targetPitch;
    private float lastSyncedTargetYaw;
    private float lastSyncedTargetPitch;
    private float targetPlayerDistance;
    private float lastSyncedPlayerDistance = -1.0F;
    private float playerDistance;
    private float previousPlayerDistance;
    private float yaw;
    private float pitch;
    private float previousYaw;
    private float previousPitch;
    private float alertBlend;
    private float previousAlertBlend;
    private float fullAlertBlend;
    private float previousFullAlertBlend;

    public HiveEyeBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.HIVE_EYE.get(), pos, state);
    }

    @Override
    public GameEventListener getListener() {
        return vibrationListener;
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "eye_state", 30, state -> {
            if (isAlert()) return state.setAndContinue(ALERT_ANIMATION);
            if (alertLevel >= WATCHING_STATE) return state.setAndContinue(WATCHING_ANIMATION);
            return state.setAndContinue(IDLE_ANIMATION);
        }));
    }

    public boolean isAlert() {
        if (level == null) return false;
        return level.isClientSide
                ? clientAlert || alertLevel >= SOFT_ALERT_STATE
                : level.getGameTime() < alertUntil || alertLevel >= SOFT_ALERT_STATE;
    }

    public float trackingYaw(float partialTick) {
        return Mth.lerp(partialTick, previousYaw, yaw);
    }

    public float trackingPitch(float partialTick) {
        return Mth.lerp(partialTick, previousPitch, pitch);
    }

    public float alertBlend(float partialTick) {
        return Mth.lerp(partialTick, previousAlertBlend, alertBlend);
    }

    private float fullAlertBlend(float partialTick) {
        return Mth.lerp(partialTick, previousFullAlertBlend, fullAlertBlend);
    }

    public float irisPulseScale(float partialTick) {
        if (level == null) return 1.0F;
        double time = level.getGameTime() + partialTick;
        float wave = (float) ((Math.sin(time * (Math.PI * 2.0D / 10.0D)) + 1.0D) * 0.5D);
        float amplitude = 0.05F * alertBlend(partialTick) + 0.05F * fullAlertBlend(partialTick);
        return 1.0F + amplitude * wave;
    }

    public boolean hasTrackingTarget() {
        return targetPlayerPresent;
    }

    public float pupilDistanceScale(float partialTick) {
        float distance = Mth.lerp(partialTick, previousPlayerDistance, playerDistance);
        if (distance <= 2.0F) return 1.0F;
        float progress = Mth.clamp((float) ((distance - 2.0) / (LOOK_RADIUS - 2.0)), 0.0F, 1.0F);
        return targetPlayerPresent ? 1.0F - 0.45F * progress : 1.0F;
    }

    public float pupilScaleY(float partialTick) {
        float squeeze = 0.3F * alertBlend(partialTick) + 0.2F * fullAlertBlend(partialTick);
        return (1.0F - squeeze) * blinkScale(partialTick);
    }

    public boolean consumeReinforcementsCalled() {
        boolean wasCalled = reinforcementsCalled;
        reinforcementsCalled = false;
        return wasCalled;
    }

    private float blinkScale(float partialTick) {
        if (level == null || clientBlinkStartedAt == Long.MIN_VALUE) return 1.0F;
        float elapsed = (float) (level.getGameTime() - clientBlinkStartedAt) + partialTick;
        if (elapsed < 0.0F || elapsed >= BLINK_DURATION_TICKS) return 1.0F;
        if (elapsed <= BLINK_DURATION_TICKS * 0.5F) {
            return 1.0F - elapsed / (BLINK_DURATION_TICKS * 0.5F);
        }
        return (elapsed - BLINK_DURATION_TICKS * 0.5F) / (BLINK_DURATION_TICKS * 0.5F);
    }

    @Override
    public CompoundTag getUpdateTag() {
        CompoundTag tag = new CompoundTag();
        tag.putBoolean("Alert", isAlert());
        tag.putInt("BlinkCooldown", blinkCooldown);
        tag.putBoolean("Blinking", blinking);
        tag.putFloat("TargetYaw", targetYaw);
        tag.putFloat("TargetPitch", targetPitch);
        tag.putFloat("TargetPlayerDistance", targetPlayerDistance);
        tag.putBoolean("TargetPlayerPresent", targetPlayerPresent);
        tag.putInt("AlertLevel", alertLevel);
        tag.putBoolean("ReinforcementsCalled", reinforcementsCalled);
        return tag;
    }

    @Nullable
    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    @Override
    public void handleUpdateTag(CompoundTag tag) {
        clientAlert = tag.getBoolean("Alert");
        blinkCooldown = Mth.clamp(tag.getInt("BlinkCooldown"), 0, BLINK_MAX_TICKS);
        targetYaw = Mth.clamp(tag.getFloat("TargetYaw"), -MAX_LOOK_YAW, MAX_LOOK_YAW);
        targetPitch = Mth.clamp(tag.getFloat("TargetPitch"), -MAX_LOOK_PITCH, MAX_LOOK_PITCH);
        targetPlayerDistance = Mth.clamp(tag.getFloat("TargetPlayerDistance"), 0.0F, (float) LOOK_RADIUS);
        targetPlayerPresent = tag.getBoolean("TargetPlayerPresent");
        alertLevel = Mth.clamp(tag.getInt("AlertLevel"), CALM_STATE, FULL_ALERT_STATE);

        boolean newBlinking = tag.getBoolean("Blinking");
        if (newBlinking && !clientBlinking) {
            clientBlinkStartedAt = level == null ? 0L : level.getGameTime();
        }
        clientBlinking = newBlinking;
    }

    @Override
    public void onDataPacket(Connection connection, ClientboundBlockEntityDataPacket packet) {
        if (packet.getTag() != null) handleUpdateTag(packet.getTag());
    }

    private void applyAura(ServerLevel level) {
        if (alertLevel == CALM_STATE) return;

        boolean buffsEnabled = CarnisConfig.SERVER.hiveEyeBuffsEnabled.get();
        boolean debuffsEnabled = CarnisConfig.SERVER.hiveEyeDebuffsEnabled.get();
        if (!buffsEnabled && !debuffsEnabled) return;

        int radius = CarnisConfig.SERVER.hiveEyeAuraRadius.get();
        double radiusSquared = (double) radius * radius;
        Vec3 center = Vec3.atCenterOf(worldPosition);
        AABB area = AABB.ofSize(center, radius * 2.0D, radius * 2.0D, radius * 2.0D);

        for (LivingEntity entity : level.getEntitiesOfClass(LivingEntity.class, area,
                candidate -> candidate.isAlive() && !candidate.isSpectator())) {
            if (entity.position().distanceToSqr(center) > radiusSquared) continue;

            if (buffsEnabled && NeuralMossBlock.isHive(entity)) {
                applyHiveBuffs(entity);
            } else if (debuffsEnabled && entity instanceof Player player) {
                applyThreatDebuffs(player);
            }
        }
    }

    private void applyHiveBuffs(LivingEntity entity) {
        switch (alertLevel) {
            case WATCHING_STATE -> maintainAuraEffect(entity, MobEffects.MOVEMENT_SPEED, 0);
            case SOFT_ALERT_STATE -> {
                maintainAuraEffect(entity, MobEffects.MOVEMENT_SPEED, 0);
                maintainAuraEffect(entity, MobEffects.DAMAGE_BOOST, 0);
            }
            case FULL_ALERT_STATE -> {
                maintainAuraEffect(entity, MobEffects.MOVEMENT_SPEED, 1);
                maintainAuraEffect(entity, MobEffects.DAMAGE_BOOST, 1);
                maintainAuraEffect(entity, MobEffects.DAMAGE_RESISTANCE, 0);
            }
            default -> {
            }
        }
    }

    private void applyThreatDebuffs(Player player) {
        int playerThreatLevel = threatLevel(player);
        if (playerThreatLevel < SOFT_ALERT_STATE) return;
        if (alertLevel == SOFT_ALERT_STATE) {
            maintainAuraEffect(player, MobEffects.WEAKNESS, 0);
        } else if (alertLevel >= FULL_ALERT_STATE) {
            maintainAuraEffect(player, MobEffects.WEAKNESS, 1);
            maintainAuraEffect(player, MobEffects.MOVEMENT_SLOWDOWN, 0);
        }
    }

    private static void maintainAuraEffect(LivingEntity entity, MobEffect effect, int amplifier) {
        MobEffectInstance existing = entity.getEffect(effect);
        if (existing == null || existing.getAmplifier() < amplifier
                || existing.getAmplifier() == amplifier
                && existing.getDuration() <= AURA_REFRESH_THRESHOLD_TICKS) {
            entity.addEffect(new MobEffectInstance(effect, AURA_EFFECT_DURATION_TICKS, amplifier));
        }
    }

    private void spawnAuraBoundaryParticles(ServerLevel level) {
        int radius = CarnisConfig.SERVER.hiveEyeAuraRadius.get();
        int particleCount = 1 + level.random.nextInt(2);
        for (int i = 0; i < particleCount; i++) {
            double angle = level.random.nextDouble() * Math.PI * 2.0D;
            double distance = radius - 2.0D + level.random.nextDouble() * 4.0D;
            double x = worldPosition.getX() + 0.5D + Math.cos(angle) * distance;
            double y = worldPosition.getY() + 0.5D + level.random.nextDouble() * 4.0D - 2.0D;
            double z = worldPosition.getZ() + 0.5D + Math.sin(angle) * distance;
            level.sendParticles(ParticleTypes.CRIMSON_SPORE, x, y, z, 1, 0.0D, 0.0D, 0.0D, 0.0D);
        }
    }

    public static void serverTick(Level world, BlockPos pos, BlockState state, HiveEyeBlockEntity eye) {
        if (!(world instanceof ServerLevel level)) return;
        boolean syncAnimation = false;

        if (eye.alertUntil != 0 && level.getGameTime() >= eye.alertUntil) {
            eye.alertUntil = 0;
            syncAnimation = true;
        }
        if (eye.hiveAttackUntil != 0 && level.getGameTime() >= eye.hiveAttackUntil) {
            eye.hiveAttackUntil = 0;
            syncAnimation = true;
        }

        if (eye.pendingVibrationSource != null) {
            LivingEntity source = eye.pendingVibrationSource;
            eye.pendingVibrationSource = null;
            boolean wasEventAlert = level.getGameTime() < eye.alertUntil;
            eye.alertUntil = level.getGameTime() + 60L;
            if (!wasEventAlert) {
                syncAnimation = true;
                level.playSound(null, pos, ModSounds.HIVE_ALARM.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
                level.sendParticles(ParticleTypes.ELECTRIC_SPARK, pos.getX() + .5D, pos.getY() + .8D,
                        pos.getZ() + .5D, 12, .25D, .2D, .25D, .02D);
            }
            eye.notifySwarmAlarm(level, source);
        }

        if (!eye.blinkTimerInitialized) {
            eye.blinkCooldown = eye.nextBlinkDelay(level);
            eye.blinkTimerInitialized = true;
            syncAnimation = true;
        } else {
            eye.blinkCooldown--;
            if (eye.blinking) {
                eye.blinkTicksRemaining--;
                if (eye.blinkTicksRemaining <= 0) {
                    eye.blinkTicksRemaining = 0;
                    eye.blinking = false;
                    syncAnimation = true;
                }
            } else if (eye.blinkCooldown <= 0) {
                eye.blinking = true;
                eye.blinkTicksRemaining = BLINK_DURATION_TICKS;
                eye.blinkCooldown = eye.nextBlinkDelay(level);
                syncAnimation = true;
            }
        }

        if (eye.screechCooldown > 0) eye.screechCooldown--;
        if (eye.reinforcementCooldown > 0) eye.reinforcementCooldown--;

        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), PLAYER_STATE_SCAN_INTERVAL),
                PLAYER_STATE_SCAN_INTERVAL) == 0) {
            int previousLevel = eye.alertLevel;
            boolean previousTargetPlayerPresent = eye.targetPlayerPresent;
            eye.updatePlayerState(level);

            if (previousLevel != eye.alertLevel) {
                eye.blinkCooldown = eye.nextBlinkDelay(level);
                syncAnimation = true;
                HiveNetwork.observe(level, pos, state, true);
                if (eye.alertLevel == FULL_ALERT_STATE) {
                    eye.propagateAlert(level, pos);
                }
            }
            if (Math.abs(eye.lastSyncedTargetYaw - eye.targetYaw) > 0.01F
                    || Math.abs(eye.lastSyncedTargetPitch - eye.targetPitch) > 0.01F
                    || previousTargetPlayerPresent != eye.targetPlayerPresent
                    || Math.abs(eye.lastSyncedPlayerDistance - eye.targetPlayerDistance) > 0.05F) {
                syncAnimation = true;
            }
        }

        if (eye.consumeReinforcementsCalled()) {
            eye.spawnReinforcements(level, pos);
        }

        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), SCAN_INTERVAL_TICKS),
                SCAN_INTERVAL_TICKS) == 0) {
            HiveNetwork.observe(level, pos, state, true);
            LivingEntity nearest = eye.findNearestLiving(level);
            if (nearest != null) nearest.addEffect(new MobEffectInstance(MobEffects.GLOWING, 100, 0));
        }

        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), AURA_INTERVAL_TICKS),
                AURA_INTERVAL_TICKS) == 0) {
            eye.applyAura(level);
        }
        if (eye.alertLevel >= SOFT_ALERT_STATE
                && Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), 20), 20) == 0) {
            eye.spawnAuraBoundaryParticles(level);
        }

        if (syncAnimation) {
            eye.lastSyncedPlayerDistance = eye.targetPlayerDistance;
            eye.syncAnimationData(level);
        }
    }

    private void spawnReinforcements(ServerLevel level, BlockPos pos) {
        if (reinforcementCooldown > 0) return;
        reinforcementCooldown = 300;

        int nearbyCount = countNearbyHiveMobs(level, pos, 32);
        if (nearbyCount >= 8) return;

        int requestedCount = 2 + level.random.nextInt(3);
        int spawnedCount = 0;
        for (int i = 0; i < requestedCount && nearbyCount < 8; i++) {
            Mob reinforcement = createRandomReinforcement(level);
            if (reinforcement == null) continue;

            BlockPos spawnPos = findReinforcementSpawnPos(level, pos, reinforcement);
            if (spawnPos == null) {
                reinforcement.discard();
                continue;
            }

            reinforcement.finalizeSpawn(level, level.getCurrentDifficultyAt(spawnPos), MobSpawnType.EVENT, null, null);
            if (!level.noCollision(reinforcement) || !level.addFreshEntity(reinforcement)) {
                reinforcement.discard();
                continue;
            }

            Player target = findNearestThreat(level, pos, 32);
            if (target != null) reinforcement.setTarget(target);
            nearbyCount++;
            spawnedCount++;
        }

        if (spawnedCount == 0) return;

        level.playSound(null, pos, ModSounds.AMALGAM_ROAR.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        level.sendParticles(ParticleTypes.CRIMSON_SPORE,
                pos.getX() + 0.5D, pos.getY() + 1.0D, pos.getZ() + 0.5D,
                20, 0.8D, 0.6D, 0.8D, 0.02D);
        level.sendParticles(ParticleTypes.ELECTRIC_SPARK,
                pos.getX() + 0.5D, pos.getY() + 0.8D, pos.getZ() + 0.5D,
                12, 0.25D, 0.2D, 0.25D, 0.02D);
    }

    private static Mob createRandomReinforcement(ServerLevel level) {
        int roll = level.random.nextInt(100);
        if (roll < 50) return ModEntities.INFECTED_ZOMBIE.get().create(level);
        if (roll < 75) return ModEntities.INFECTED_SPIDER.get().create(level);
        if (roll < 90) return ModEntities.INFECTED_SKELETON.get().create(level);
        return ModEntities.FLESH_AMALGAM.get().create(level);
    }

    private static int countNearbyHiveMobs(ServerLevel level, BlockPos pos, int radius) {
        Vec3 center = Vec3.atCenterOf(pos);
        double radiusSquared = (double) radius * radius;
        AABB area = AABB.ofSize(center, radius * 2.0D, radius * 2.0D, radius * 2.0D);
        int count = 0;
        for (Mob mob : level.getEntitiesOfClass(Mob.class, area,
                candidate -> candidate.isAlive() && NeuralMossBlock.isHive(candidate))) {
            if (mob.position().distanceToSqr(center) <= radiusSquared) count++;
        }
        return count;
    }

    @Nullable
    private static BlockPos findReinforcementSpawnPos(ServerLevel level, BlockPos eyePos, Mob mob) {
        for (int ring = 0; ring <= 3; ring++) {
            for (int dx = -ring; dx <= ring; dx++) {
                for (int dy = -ring; dy <= ring; dy++) {
                    for (int dz = -ring; dz <= ring; dz++) {
                        if (Math.max(Math.max(Math.abs(dx), Math.abs(dy)), Math.abs(dz)) != ring) continue;
                        BlockPos candidate = eyePos.above().offset(dx, dy, dz);
                        if (candidate.distSqr(eyePos) > 16.0D) continue;
                        BlockPos support = candidate.below();
                        BlockPos head = candidate.above();
                        if (!level.hasChunkAt(support) || !level.hasChunkAt(candidate) || !level.hasChunkAt(head)) continue;

                        BlockState feetState = level.getBlockState(candidate);
                        BlockState headState = level.getBlockState(head);
                        if (!(feetState.isAir() || feetState.canBeReplaced())
                                || !(headState.isAir() || headState.canBeReplaced())
                                || !level.getFluidState(candidate).isEmpty()
                                || !level.getBlockState(support).isFaceSturdy(level, support, Direction.UP)) continue;

                        mob.moveTo(candidate.getX() + 0.5D, candidate.getY(), candidate.getZ() + 0.5D,
                                level.random.nextFloat() * 360.0F, 0.0F);
                        if (level.noCollision(mob)) return candidate;
                    }
                }
            }
        }
        return null;
    }

    @Nullable
    private static Player findNearestThreat(ServerLevel level, BlockPos pos, int radius) {
        Vec3 center = Vec3.atCenterOf(pos);
        double radiusSquared = (double) radius * radius;
        double nearestDistance = radiusSquared;
        Player nearest = null;
        AABB area = AABB.ofSize(center, radius * 2.0D, radius * 2.0D, radius * 2.0D);
        for (Player player : level.getEntitiesOfClass(Player.class, area,
                candidate -> candidate.isAlive() && !candidate.isSpectator())) {
            double distance = player.position().distanceToSqr(center);
            if (distance > nearestDistance || threatLevel(player) == CALM_STATE) continue;
            nearestDistance = distance;
            nearest = player;
        }
        return nearest;
    }

    private void propagateAlert(ServerLevel level, BlockPos sourcePos) {
        long operationStartedAt = System.nanoTime();
        long alertUntilTick = level.getGameTime() + SYNCHRONIZED_ALERT_DURATION_TICKS;
        hiveAttackUntil = Math.max(hiveAttackUntil, alertUntilTick);
        alertLevel = FULL_ALERT_STATE;
        HiveNetwork.observe(level, sourcePos, level.getBlockState(sourcePos), true);

        int minChunkX = (sourcePos.getX() - SYNCHRONIZED_ALERT_RADIUS) >> 4;
        int maxChunkX = (sourcePos.getX() + SYNCHRONIZED_ALERT_RADIUS) >> 4;
        int minChunkZ = (sourcePos.getZ() - SYNCHRONIZED_ALERT_RADIUS) >> 4;
        int maxChunkZ = (sourcePos.getZ() + SYNCHRONIZED_ALERT_RADIUS) >> 4;
        double radiusSquared = (double) SYNCHRONIZED_ALERT_RADIUS * SYNCHRONIZED_ALERT_RADIUS;
        Vec3 sourceCenter = Vec3.atCenterOf(sourcePos);

        int loadedChunksScanned = 0;
        for (int chunkX = minChunkX; chunkX <= maxChunkX; chunkX++) {
            for (int chunkZ = minChunkZ; chunkZ <= maxChunkZ; chunkZ++) {
                var chunk = level.getChunkSource().getChunkNow(chunkX, chunkZ);
                if (chunk == null) continue;
                loadedChunksScanned++;

                for (BlockEntity blockEntity : chunk.getBlockEntities().values()) {
                    if (!(blockEntity instanceof HiveEyeBlockEntity other) || other == this || other.isRemoved()) continue;
                    if (Vec3.atCenterOf(other.getBlockPos()).distanceToSqr(sourceCenter) > radiusSquared) continue;

                    other.alertLevel = FULL_ALERT_STATE;
                    other.hiveAttackUntil = Math.max(other.hiveAttackUntil, alertUntilTick);
                    other.alertUntil = Math.max(other.alertUntil, alertUntilTick);
                    other.syncAnimationData(level);
                    HiveNetwork.observe(level, other.getBlockPos(), other.getBlockState(), true);
                }
            }
        }
        long elapsed = System.nanoTime() - operationStartedAt;
        if (elapsed > 1_000_000L) {
            CarnisMod.LOGGER.debug("Slow hive alert propagation: {} ms across {} loaded chunks",
                    elapsed / 1_000_000.0D, loadedChunksScanned);
        }
    }

    private void notifySwarmAlarm(ServerLevel level, LivingEntity intruder) {
        long now = level.getGameTime();
        if (lastSwarmAlarmTick != Long.MIN_VALUE && now >= lastSwarmAlarmTick
                && now - lastSwarmAlarmTick < SWARM_ALARM_COOLDOWN_TICKS) return;
        lastSwarmAlarmTick = now;
        HiveSwarmCoordinator.eyeAlarm(level, worldPosition, intruder);
    }

    private int nextBlinkDelay(ServerLevel level) {
        return BLINK_MIN_TICKS + level.random.nextInt(BLINK_MAX_TICKS - BLINK_MIN_TICKS + 1);
    }

    private void updatePlayerState(ServerLevel level) {
        Vec3 center = Vec3.atCenterOf(worldPosition);
        double lookRadiusSquared = LOOK_RADIUS * LOOK_RADIUS;
        double threatRadiusSquared = THREAT_RADIUS * THREAT_RADIUS;
        double armedRadiusSquared = (double) ARMED_WARNING_RADIUS * ARMED_WARNING_RADIUS;
        Player nearestPlayer = null;
        Player nearestArmedPlayer = null;
        double nearestPlayerDistance = lookRadiusSquared;
        double nearestArmedDistanceSquared = armedRadiusSquared;
        int maxThreatLevel = CALM_STATE;
        AABB scanArea = AABB.ofSize(center, LOOK_RADIUS * 2.0D, LOOK_RADIUS * 2.0D, LOOK_RADIUS * 2.0D);

        for (Player player : level.getEntitiesOfClass(Player.class, scanArea,
                candidate -> candidate.isAlive() && !candidate.isSpectator())) {
            double distanceSquared = player.position().distanceToSqr(center);
            if (distanceSquared > lookRadiusSquared) continue;

            if (nearestPlayer == null || distanceSquared < nearestPlayerDistance) {
                nearestPlayerDistance = distanceSquared;
                nearestPlayer = player;
            }

            int playerThreatLevel = threatLevel(player);
            if (playerThreatLevel != CALM_STATE && distanceSquared <= threatRadiusSquared) {
                maxThreatLevel = Math.max(maxThreatLevel, playerThreatLevel);
            }

            if (distanceSquared <= armedRadiusSquared && isArmed(player)
                    && (nearestArmedPlayer == null || distanceSquared < nearestArmedDistanceSquared)) {
                nearestArmedDistanceSquared = distanceSquared;
                nearestArmedPlayer = player;
            }
        }

        targetPlayerPresent = nearestPlayer != null;
        if (nearestPlayer == null) {
            targetYaw = 0.0F;
            targetPitch = 0.0F;
            targetPlayerDistance = 0.0F;
        } else {
            setTargetAngles(nearestPlayer);
            targetPlayerDistance = (float) Math.sqrt(nearestPlayerDistance);
        }

        updateArmedApproach(level, nearestArmedPlayer,
                nearestArmedPlayer == null ? Double.MAX_VALUE : Math.sqrt(nearestArmedDistanceSquared));

        int nextAlertLevel;
        if (maxThreatLevel >= FULL_ALERT_STATE) {
            nextAlertLevel = FULL_ALERT_STATE;
        } else if (maxThreatLevel == SOFT_ALERT_STATE) {
            nextAlertLevel = SOFT_ALERT_STATE;
        } else if (maxThreatLevel >= WATCHING_STATE) {
            nextAlertLevel = WATCHING_STATE;
        } else {
            nextAlertLevel = CALM_STATE;
        }

        if (nearestArmedPlayer != null || level.getGameTime() < hiveAttackUntil) {
            nextAlertLevel = FULL_ALERT_STATE;
        }
        alertLevel = nextAlertLevel;
    }

    private void setTargetAngles(Player player) {
        Vec3 delta = player.getEyePosition().subtract(
                worldPosition.getX() + 0.5D,
                worldPosition.getY() + 0.5625D,
                worldPosition.getZ() + 0.5D);
        double horizontal = Math.sqrt(delta.x * delta.x + delta.z * delta.z);
        targetYaw = horizontal > 1.0E-5D
                ? Mth.clamp((float) Math.atan2(delta.x, -delta.z), -MAX_LOOK_YAW, MAX_LOOK_YAW)
                : 0.0F;
        targetPitch = Mth.clamp((float) -Math.atan2(delta.y, Math.max(horizontal, 1.0E-5D)),
                -MAX_LOOK_PITCH, MAX_LOOK_PITCH);
    }

    private void updateArmedApproach(ServerLevel level, @Nullable Player armedPlayer, double distance) {
        if (armedPlayer == null) {
            armedTargetId = null;
            previousArmedDistance = Double.MAX_VALUE;
            armedApproachTicks = 0;
            armedScreechPending = false;
            return;
        }

        UUID currentId = armedPlayer.getUUID();
        if (!currentId.equals(armedTargetId)) {
            armedTargetId = currentId;
            previousArmedDistance = distance;
            armedApproachTicks = 0;
            armedScreechPending = true;
        } else if (distance < previousArmedDistance - 0.01D) {
            armedApproachTicks += PLAYER_STATE_SCAN_INTERVAL;
        } else if (distance > previousArmedDistance + 0.01D) {
            armedApproachTicks = 0;
        }
        previousArmedDistance = distance;

        if (armedScreechPending && armedApproachTicks >= ARMED_WARNING_TICKS && screechCooldown <= 0) {
            playScreech(level, armedPlayer);
            armedScreechPending = false;
        }
    }

    private static int threatLevel(Player player) {
        if (!player.isAlive() || player.isSpectator() || player.isCreative()) return CALM_STATE;
        if (NeuroArmorEventHandler.hasFullSet(player)
                || NeuroWeave.protectedPieces(player) >= 4
                || NeuroResonatorHelmetItem.isEquipped(player)) return CALM_STATE;
        if (PlayerInfectionApi.isAssimilated(player)) return CALM_STATE;

        float infection = PlayerInfectionApi.getInfectionLevel(player);
        if (infection >= 100.0F) return CALM_STATE;
        if (infection >= 75.0F) return WATCHING_STATE;
        if (infection >= 1.0F) return SOFT_ALERT_STATE;
        return FULL_ALERT_STATE;
    }

    private static boolean isArmed(Player player) {
        ItemStack held = player.getMainHandItem();
        return held.canPerformAction(ToolActions.SWORD_DIG)
                || held.canPerformAction(ToolActions.AXE_DIG)
                || held.is(ItemTags.SWORDS)
                || held.is(ItemTags.AXES)
                || held.getItem() instanceof BowItem
                || held.getItem() instanceof CrossbowItem
                || held.getItem() instanceof TridentItem;
    }

    private void playScreech(ServerLevel level, Player armedPlayer) {
        if (!isArmed(armedPlayer) || screechCooldown > 0) return;
        level.playSound(null, worldPosition, ModSounds.HIVE_EYE_SCREECH.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        screechCooldown = SCREECH_COOLDOWN_TICKS;
    }

    public void onHiveAttacked(ServerLevel level, Player attacker) {
        if (!attacker.isAlive()) return;
        long now = level.getGameTime();
        alertUntil = now + 200L;
        hiveAttackUntil = alertUntil;
        alertLevel = FULL_ALERT_STATE;
        armedTargetId = null;
        armedApproachTicks = 0;
        armedScreechPending = false;
        reinforcementsCalled = true;
        setTargetAngles(attacker);
        targetPlayerPresent = true;
        targetPlayerDistance = Mth.clamp((float) attacker.position().distanceTo(Vec3.atCenterOf(worldPosition)),
                0.0F, (float) LOOK_RADIUS);

        if (isArmed(attacker)) playScreech(level, attacker);
        level.playSound(null, worldPosition, ModSounds.HIVE_ALARM.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        level.sendParticles(ParticleTypes.ELECTRIC_SPARK, worldPosition.getX() + .5D, worldPosition.getY() + .8D,
                worldPosition.getZ() + .5D, 12, .25D, .2D, .25D, .02D);
        notifySwarmAlarm(level, attacker);
        propagateAlert(level, worldPosition);
        HiveNetwork.observe(level, worldPosition, getBlockState(), true);
        syncAnimationData(level);
    }

    private void syncAnimationData(ServerLevel level) {
        lastSyncedTargetYaw = targetYaw;
        lastSyncedTargetPitch = targetPitch;
        lastSyncedPlayerDistance = targetPlayerDistance;
        setChanged();
        BlockState state = getBlockState();
        level.sendBlockUpdated(worldPosition, state, state, Block.UPDATE_CLIENTS);
    }

    private void recordVibration(LivingEntity source) {
        if (isTarget(source)) pendingVibrationSource = source;
    }

    private static boolean isTarget(LivingEntity entity) {
        if (!entity.isAlive() || entity.isSpectator() || NeuralMossBlock.isHive(entity)) return false;
        return !(entity instanceof Player player) || threatLevel(player) > CALM_STATE;
    }

    @Nullable
    private LivingEntity findNearestLiving(Level level) {
        Vec3 center = Vec3.atCenterOf(worldPosition);
        LivingEntity nearest = null;
        double best = PLAYER_SCAN_RADIUS * PLAYER_SCAN_RADIUS;
        for (LivingEntity candidate : level.getEntitiesOfClass(LivingEntity.class,
                AABB.ofSize(center, 36, 36, 36), HiveEyeBlockEntity::isTarget)) {
            double distance = candidate.position().distanceToSqr(center);
            if (distance <= best) {
                best = distance;
                nearest = candidate;
            }
        }
        return nearest;
    }

    public static void clientTick(Level level, BlockPos pos, BlockState state, HiveEyeBlockEntity eye) {
        eye.previousYaw = eye.yaw;
        eye.previousPitch = eye.pitch;
        eye.yaw += (eye.targetYaw - eye.yaw) * CLIENT_LERP_SPEED;
        eye.pitch += (eye.targetPitch - eye.pitch) * CLIENT_LERP_SPEED;

        eye.previousPlayerDistance = eye.playerDistance;
        eye.playerDistance += (eye.targetPlayerDistance - eye.playerDistance) * CLIENT_LERP_SPEED;

        eye.previousAlertBlend = eye.alertBlend;
        eye.previousFullAlertBlend = eye.fullAlertBlend;
        float wantedAlertBlend = eye.alertLevel >= SOFT_ALERT_STATE ? 1.0F : 0.0F;
        float wantedFullAlertBlend = eye.alertLevel >= FULL_ALERT_STATE ? 1.0F : 0.0F;
        eye.alertBlend = approach(eye.alertBlend, wantedAlertBlend, STATE_LERP_STEP);
        eye.fullAlertBlend = approach(eye.fullAlertBlend, wantedFullAlertBlend, STATE_LERP_STEP);
    }

    private static float approach(float current, float target, float step) {
        if (current < target) return Math.min(current + step, target);
        return Math.max(current - step, target);
    }

    private final class EyeListener implements net.minecraft.world.level.gameevent.GameEventListener {
        private final net.minecraft.world.level.gameevent.PositionSource source =
                new net.minecraft.world.level.gameevent.BlockPositionSource(worldPosition);

        @Override
        public net.minecraft.world.level.gameevent.PositionSource getListenerSource() {
            return source;
        }

        @Override
        public int getListenerRadius() {
            return 16;
        }

        @Override
        public boolean handleGameEvent(ServerLevel level, net.minecraft.world.level.gameevent.GameEvent event,
                                       net.minecraft.world.level.gameevent.GameEvent.Context context, Vec3 position) {
            var id = net.minecraft.core.registries.BuiltInRegistries.GAME_EVENT.getKey(event);
            if (id == null || !id.getNamespace().equals("minecraft") || !AUDIBLE_EVENTS.contains(id.getPath())) {
                return false;
            }
            net.minecraft.world.entity.Entity origin = context.sourceEntity();
            if (origin instanceof net.minecraft.world.entity.projectile.Projectile projectile && projectile.getOwner() != null) {
                origin = projectile.getOwner();
            }
            if (!(origin instanceof LivingEntity living) || !isTarget(living)
                    || living instanceof Player player
                    && (player.isSteppingCarefully() || NeuroArmorEventHandler.hasFullSet(player))
                    || position.distanceToSqr(Vec3.atCenterOf(worldPosition)) > 256D) {
                return false;
            }
            recordVibration(living);
            return true;
        }
    }
}
