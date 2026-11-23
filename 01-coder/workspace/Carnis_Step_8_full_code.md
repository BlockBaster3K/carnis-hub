# Шаг 8 — полный код

## ParasiticTendrilEntity.java

```java
package com.carnis.mod.entity;

import com.carnis.mod.event.IncubationEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class ParasiticTendrilEntity extends Monster implements GeoEntity {
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.parasitic_tendril.idle");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    public ParasiticTendrilEntity(EntityType<? extends Monster> type, Level level) { super(type, level); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 10).add(Attributes.MOVEMENT_SPEED, .27)
                .add(Attributes.FOLLOW_RANGE, 24).add(Attributes.ATTACK_DAMAGE, 1);
    }
    @Override protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.1D, false));
        goalSelector.addGoal(5, new RandomStrollGoal(this, .8D));
        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 10, true, false,
                target -> IncubationEvents.isEligible(target) && !InfectionHandler.isInfected(target)));
    }
    @Override public boolean doHurtTarget(Entity target) {
        if (!(level() instanceof ServerLevel server) || !(target instanceof LivingEntity host)
                || !host.isAlive() || !IncubationEvents.isEligible(host) || InfectionHandler.isInfected(host)) return false;
        boolean hostile = IncubationEvents.isHostileHost(host);
        boolean armored = false;
        for (EquipmentSlot slot : EquipmentSlot.values()) {
            if (slot.isArmor() && !host.getItemBySlot(slot).isEmpty()) { armored = true; break; }
        }
        // Armor subtracts 15 percentage points, not 15 percent of the chance.
        float chance = hostile ? (armored ? 0.30F : 0.45F) : 0.85F;
        boolean success = random.nextFloat() < chance;
        if (success) {
            InfectionHandler.begin(host);
            server.playSound(null, host.blockPosition(), SoundEvents.SLIME_SQUISH,
                    SoundSource.HOSTILE, 0.9F, 0.65F);
            server.sendParticles(ModParticles.BIOMASS_SPARK.get(), host.getX(), host.getY(0.6D), host.getZ(),
                    12, host.getBbWidth() * 0.3D, host.getBbHeight() * 0.2D, host.getBbWidth() * 0.3D, 0.03D);
        } else {
            host.hurt(server.damageSources().mobAttack(this), 1.0F);
            server.playSound(null, blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1.0F, 1.2F);
            server.sendParticles(ParticleTypes.POOF, getX(), getY(0.5D), getZ(), 12, .2D, .25D, .2D, .03D);
            server.sendParticles(ModParticles.BIOMASS_SPARK.get(), getX(), getY(0.5D), getZ(), 10, .2D, .25D, .2D, .08D);
        }
        discard();
        return true;
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "whip", 2, state -> state.setAndContinue(IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
```

## InfectionHandler.java

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModEffects;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.UUID;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class InfectionHandler {
    public static final String STAGE = "carnis:infection_stage";
    public static final String TIMER = "carnis:infection_timer";
    private static final UUID SLOW_ID = UUID.fromString("36782739-7a30-44e0-a1e2-d40ac9fa072c");
    private static final AttributeModifier SLOW = new AttributeModifier(SLOW_ID, "Carnis incubation", -0.20D,
            AttributeModifier.Operation.MULTIPLY_TOTAL);
    private InfectionHandler() { }

    public static boolean isInfected(LivingEntity host) { return host.getPersistentData().getInt(STAGE) > 0; }

    public static void begin(LivingEntity host) {
        if (host.level().isClientSide || isInfected(host)) return;
        host.getPersistentData().putInt(STAGE, 1);
        host.getPersistentData().putInt(TIMER, 0);
        syncMarker(host, 1);
    }

    @SubscribeEvent
    public static void onTick(LivingEvent.LivingTickEvent event) {
        LivingEntity host = event.getEntity();
        if (!(host.level() instanceof ServerLevel level) || !host.isAlive()) return;
        CompoundTag tag = host.getPersistentData();
        int stage = tag.getInt(STAGE);
        if (stage < 1 || stage > 4 || !IncubationEvents.isEligible(host)) return;
        int timer = tag.getInt(TIMER) + 1;
        tag.putInt(TIMER, timer);
        int next = timer >= 600 ? 4 : timer >= 500 ? 3 : timer >= 200 ? 2 : 1;
        if (next != stage) {
            tag.putInt(STAGE, next);
            stage = next;
            if (stage == 3) rupture(level, host);
            if (!host.isAlive()) return;
            if (stage < 4) syncMarker(host, stage);
        }
        applySlow(host, stage >= 2);
        if (stage < 4 && !host.hasEffect(ModEffects.INCUBATING.get())) syncMarker(host, stage);
        if (stage == 1 && timer % 35 == 0) {
            level.sendParticles(ModParticles.BIOMASS_SPARK.get(), host.getX(), host.getEyeY() - 0.1D, host.getZ(),
                    2, host.getBbWidth() * 0.22D, 0.08D, host.getBbWidth() * 0.22D, 0.01D);
        }
        if (stage == 1 && timer % 8 == 0) {
            host.setYHeadRot(host.getYHeadRot() + (level.random.nextBoolean() ? 2.0F : -2.0F));
        }
        if (stage == 4 && timer % 20 == 0) finish(level, host);
    }

    private static void syncMarker(LivingEntity host, int stage) {
        host.removeEffect(ModEffects.INCUBATING.get());
        host.addEffect(new MobEffectInstance(ModEffects.INCUBATING.get(), 700, stage - 1, false, false, false));
    }

    private static void applySlow(LivingEntity host, boolean active) {
        AttributeInstance movement = host.getAttribute(Attributes.MOVEMENT_SPEED);
        if (movement == null) return;
        if (active && !movement.hasModifier(SLOW)) movement.addTransientModifier(SLOW);
        else if (!active && movement.hasModifier(SLOW)) movement.removeModifier(SLOW_ID);
    }

    @SubscribeEvent
    public static void onDeath(LivingDeathEvent event) {
        if (!event.isCanceled() && event.getEntity().level() instanceof ServerLevel) applySlow(event.getEntity(), false);
    }

    private static void rupture(ServerLevel level, LivingEntity host) {
        level.playSound(null, host.blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1.4F, 0.65F);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), host.getX(), host.getY(0.5D), host.getZ(),
                36, host.getBbWidth() * 0.4D, host.getBbHeight() * 0.3D, host.getBbWidth() * 0.4D, 0.10D);
        if (ForgeEventFactory.getMobGriefingEvent(level, host)) seedGround(level, host);
        host.hurt(level.damageSources().magic(), host.getMaxHealth() * 0.30F);
    }

    private static void seedGround(ServerLevel level, LivingEntity host) {
        BlockPos center = host.blockPosition();
        for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) {
            BlockPos ground = center.offset(dx, -1, dz);
            if (ground.distToCenterSqr(host.getX(), ground.getY() + 0.5D, host.getZ()) > 2.25D
                    || !level.hasChunkAt(ground) || level.isOutsideBuildHeight(ground)) continue;
            BlockState old = level.getBlockState(ground);
            if (!old.hasBlockEntity() && old.getFluidState().isEmpty() && old.getDestroySpeed(level, ground) >= 0
                    && old.isFaceSturdy(level, ground, Direction.UP))
                level.setBlockAndUpdate(ground, ModBlocks.LIVING_FLESH.get().defaultBlockState());
        }
        for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) for (int dy = 0; dy <= 1; dy++) {
            BlockPos pos = center.offset(dx, dy, dz);
            if (pos.distToCenterSqr(host.getX(), host.getY() + 0.5D, host.getZ()) > 2.25D
                    || !level.hasChunkAt(pos) || level.isOutsideBuildHeight(pos)) continue;
            BlockState old = level.getBlockState(pos);
            if (!old.isAir() && !old.is(ModBlocks.FLESH_VEINS.get())) continue;
            BlockState result = old.isAir() ? Blocks.AIR.defaultBlockState() : old;
            for (Direction face : Direction.Plane.HORIZONTAL) {
                BlockPos wall = pos.relative(face);
                if (!level.hasChunkAt(wall) || level.isOutsideBuildHeight(wall)
                        || !level.getBlockState(wall).isFaceSturdy(level, wall, face.getOpposite())) continue;
                BlockState next = ModBlocks.FLESH_VEINS.get().getStateForPlacement(result, level, pos, face);
                if (next != null) result = next;
            }
            if (!result.equals(old)) level.setBlockAndUpdate(pos, result);
        }
    }

    private static void finish(ServerLevel level, LivingEntity host) {
        if (!IncubationEvents.isHostileHost(host)) {
            host.hurt(level.damageSources().magic(), Float.MAX_VALUE);
            return;
        }
        EntityType<?> type = host.getType();
        Mob converted = type == EntityType.ZOMBIE ? ModEntities.INFECTED_ZOMBIE.get().create(level)
                : type == EntityType.SKELETON ? ModEntities.INFECTED_SKELETON.get().create(level)
                : type == EntityType.CREEPER ? ModEntities.INFECTED_CREEPER.get().create(level)
                : ModEntities.INFECTED_SPIDER.get().create(level);
        if (converted == null) return;
        converted.moveTo(host.getX(), host.getY(), host.getZ(), host.getYRot(), host.getXRot());
        converted.setHealth(Math.max(0.01F, Math.min(1.0F, host.getHealth() / host.getMaxHealth())) * converted.getMaxHealth());
        converted.setCustomName(host.getCustomName());
        converted.setCustomNameVisible(host.isCustomNameVisible());
        for (EquipmentSlot slot : EquipmentSlot.values()) converted.setItemSlot(slot, host.getItemBySlot(slot).copy());
        if (!level.addFreshEntity(converted)) return;
        applySlow(host, false);
        host.discard();
    }
}
```

