package com.carnis.mod.block.entity;

import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
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

public final class NervePillarBlockEntity extends BlockEntity implements GeoBlockEntity {
    private static final int AURA_INTERVAL_TICKS = 40;
    private static final int PARTICLE_INTERVAL_TICKS = 20;
    private static final int EFFECT_DURATION_TICKS = 60;
    private static final int EFFECT_REFRESH_THRESHOLD_TICKS = 40;
    private static final RawAnimation IDLE_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.nerve_pillar.idle");

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private long nextDischarge;
    private int tickCounter;

    public NervePillarBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.NERVE_PILLAR.get(), pos, state);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "fibers", 0,
                state -> state.setAndContinue(IDLE_ANIMATION)));
    }

    public void discharge(ServerLevel server) {
        long now = server.getGameTime();
        if (now < nextDischarge) return;
        nextDischarge = now + 10;
        double x = worldPosition.getX() + 0.5D;
        double y = worldPosition.getY() + 0.7D;
        double z = worldPosition.getZ() + 0.5D;
        server.sendParticles(ParticleTypes.ELECTRIC_SPARK, x, y, z, 18, 0.3D, 0.45D, 0.3D, 0.08D);
        for (int i = 0; i < 16; i++) {
            double angle = Math.PI * 2.0D * i / 16.0D;
            double dx = Math.cos(angle);
            double dz = Math.sin(angle);
            server.sendParticles(ModParticles.BIOMASS_SPARK.get(), x + dx * 0.52D, y, z + dz * 0.52D,
                    0, dx * 0.08D, 0.025D, dz * 0.08D, 1.0D);
        }
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, NervePillarBlockEntity blockEntity) {
        if (level.isClientSide) return;

        boolean buffsEnabled = CarnisConfig.SERVER.nervePillarBuffsEnabled.get();
        boolean debuffsEnabled = CarnisConfig.SERVER.nervePillarDebuffsEnabled.get();
        boolean auraEnabled = buffsEnabled || debuffsEnabled;

        blockEntity.tickCounter++;
        if (blockEntity.tickCounter % AURA_INTERVAL_TICKS == 0 && auraEnabled) {
            int radius = CarnisConfig.SERVER.nervePillarAuraRadius.get();
            blockEntity.applyAura(level, pos, radius);
        }

        if (blockEntity.tickCounter % PARTICLE_INTERVAL_TICKS == 0 && auraEnabled) {
            spawnAuraParticles((ServerLevel) level, pos);
        }

        if (blockEntity.tickCounter >= AURA_INTERVAL_TICKS) {
            blockEntity.tickCounter = 0;
        }
    }

    private void applyAura(Level level, BlockPos pos, int radius) {
        boolean buffsEnabled = CarnisConfig.SERVER.nervePillarBuffsEnabled.get();
        boolean debuffsEnabled = CarnisConfig.SERVER.nervePillarDebuffsEnabled.get();
        Vec3 center = Vec3.atCenterOf(pos);
        double radiusSquared = (double) radius * radius;
        AABB area = AABB.ofSize(center, radius * 2.0D, radius * 2.0D, radius * 2.0D);

        for (LivingEntity entity : level.getEntitiesOfClass(LivingEntity.class, area,
                candidate -> candidate.isAlive() && !candidate.isSpectator()
                        && candidate.distanceToSqr(center) <= radiusSquared)) {
            boolean hiveAlly = NeuralMossBlock.isHive(entity)
                    || entity instanceof Mob mob && InfectionHandler.isInfected(mob);
            if (buffsEnabled && hiveAlly && !(entity instanceof Player)) {
                maintainEffect(entity, MobEffects.REGENERATION, 0);
            }

            if (debuffsEnabled && entity instanceof Player player
                    && !NeuralMossBlock.isHive(player)
                    && !PlayerInfectionApi.isAssimilated(player)
                    && !NeuroResonatorHelmetItem.isEquipped(player)) {
                maintainEffect(player, MobEffects.DIG_SLOWDOWN, 0);
            }
        }
    }

    private static void maintainEffect(LivingEntity entity, MobEffect effect, int amplifier) {
        MobEffectInstance existing = entity.getEffect(effect);
        if (existing == null || existing.getAmplifier() < amplifier
                || existing.getAmplifier() == amplifier
                && existing.getDuration() <= EFFECT_REFRESH_THRESHOLD_TICKS) {
            entity.addEffect(new MobEffectInstance(effect, EFFECT_DURATION_TICKS, amplifier, false, true));
        }
    }

    /** Spawns world-space spore particles on a spherical shell around the pillar. */
    private static void spawnAuraParticles(ServerLevel level, BlockPos pos) {
        int particleCount = 3 + level.random.nextInt(3);
        Vec3 center = Vec3.atCenterOf(pos);

        for (int i = 0; i < particleCount; i++) {
            double verticalDirection = level.random.nextDouble() * 2.0D - 1.0D;
            double angle = level.random.nextDouble() * Math.PI * 2.0D;
            double horizontalScale = Math.sqrt(1.0D - verticalDirection * verticalDirection);
            double sphereRadius = 0.5D + level.random.nextDouble();
            double x = center.x + sphereRadius * horizontalScale * Math.cos(angle);
            double y = center.y + sphereRadius * verticalDirection;
            double z = center.z + sphereRadius * horizontalScale * Math.sin(angle);
            level.sendParticles(ParticleTypes.CRIMSON_SPORE, x, y, z, 1,
                    0.0D, 0.0D, 0.0D, 0.002D);
        }
    }
}
