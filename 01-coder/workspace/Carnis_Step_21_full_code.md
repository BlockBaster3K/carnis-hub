# Шаг 21 — полный код и ресурсы

## `src/main/java/com/carnis/mod/entity/projectile/InoculatorDartEntity.java`

```java
package com.carnis.mod.entity.projectile;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HiveSentinelEntity;
import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.event.DartTreatmentEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.network.NetworkHooks;

public final class InoculatorDartEntity extends AbstractArrow {
    public enum DartType { PURIFICATION, VIRAL }
    private static final EntityDataAccessor<Integer> CONTENT = SynchedEntityData.defineId(InoculatorDartEntity.class, EntityDataSerializers.INT);
    public InoculatorDartEntity(EntityType<? extends InoculatorDartEntity> type, Level level) {
        super(type, level); pickup = Pickup.DISALLOWED;
    }
    public InoculatorDartEntity(Level level, LivingEntity owner, DartType contents) {
        super(ModEntities.INOCULATOR_DART.get(), owner, level);
        pickup = Pickup.DISALLOWED;
        setDartType(contents);
    }
    @Override protected void defineSynchedData() { super.defineSynchedData(); entityData.define(CONTENT, 0); }
    public DartType getDartType() { return entityData.get(CONTENT) == 1 ? DartType.VIRAL : DartType.PURIFICATION; }
    public void setDartType(DartType type) { entityData.set(CONTENT, type == DartType.VIRAL ? 1 : 0); }
    @Override public void addAdditionalSaveData(CompoundTag tag) { super.addAdditionalSaveData(tag); tag.putString("DartType", getDartType().name()); }
    @Override public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        setDartType("VIRAL".equals(tag.getString("DartType")) ? DartType.VIRAL : DartType.PURIFICATION);
    }
    @Override public void tick() {
        super.tick();
        if (isRemoved() || inGround || isNoGravity()) return;
        // AbstractArrow applies 0.05 blocks/tick². Counter 0.04 after its normal flight tick.
        setDeltaMovement(getDeltaMovement().add(0, .04D, 0));
        if (level().isClientSide) {
            boolean clean = getDartType() == DartType.PURIFICATION;
            level().addParticle(clean ? ModParticles.PURIFIER_FLAME.get() : ModParticles.BIOMASS_SPARK.get(),
                    getX(), getY(), getZ(), 0, 0, 0);
            if (tickCount % 3 == 0) level().addParticle(clean ? ParticleTypes.COMPOSTER : ParticleTypes.CRIMSON_SPORE,
                    getX(), getY(), getZ(), 0, .005D, 0);
        }
    }
    @Override protected void onHitEntity(EntityHitResult result) {
        if (!(level() instanceof ServerLevel server)) return;
        Entity hit = result.getEntity();
        if (hit instanceof LivingEntity living) {
            if (getDartType() == DartType.PURIFICATION) purify(server, living);
            else infect(server, living);
        }
        discard();
    }
    private void purify(ServerLevel level, LivingEntity target) {
        if (target instanceof Player player) {
            PlayerInfectionApi.addInfection(player, -35F);
            player.removeEffect(MobEffects.CONFUSION);
            player.removeEffect(MobEffects.BLINDNESS);
            player.removeEffect(MobEffects.MOVEMENT_SLOWDOWN);
        } else if (target instanceof InfectedZombieEntity || target instanceof InfectedSkeletonEntity) {
            DartTreatmentEvents.startRegression((Mob) target);
        } else if (target instanceof FleshAmalgamEntity || target instanceof HiveSentinelEntity || target instanceof CerebralNexusEntity) {
            target.hurt(level.damageSources().magic(), 25F);
            if (target.isAlive()) DartTreatmentEvents.stun((Mob) target, 60);
        }
    }
    private void infect(ServerLevel level, LivingEntity target) {
        if (target instanceof Player player) {
            if (getOwner() instanceof Player shooter && !shooter.canHarmPlayer(player)) return;
            PlayerInfectionApi.addInfection(player, 25F);
            player.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 120, 0));
            return;
        }
        EntityType<?> type = target.getType();
        if (type == EntityType.COW || type == EntityType.SHEEP || type == EntityType.PIG) {
            InfectionHandler.beginAccelerated(target);
        } else if (type == EntityType.ZOMBIE || type == EntityType.SKELETON || type == EntityType.CREEPER) {
            DartTreatmentEvents.startMutation((Mob) target);
        }
    }
    @Override protected void onHitBlock(BlockHitResult hit) { setSoundEvent(ModSounds.DART_HIT.get()); super.onHitBlock(hit); }
    @Override protected SoundEvent getDefaultHitGroundSoundEvent() { return ModSounds.DART_HIT.get(); }
    @Override protected ItemStack getPickupItem() { return ItemStack.EMPTY; }
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket() { return NetworkHooks.getEntitySpawningPacket(this); }
}
```

## `src/main/java/com/carnis/mod/item/PurificationDartItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import javax.annotation.Nullable;
import java.util.List;

public final class PurificationDartItem extends Item {
    public PurificationDartItem(Properties properties) { super(properties); }
    @Override public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.carnis.purification_dart.mechanics").withStyle(ChatFormatting.AQUA));
        tooltip.add(Component.translatable("tooltip.carnis.purification_dart.protocol").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.carnis.dart.use").withStyle(ChatFormatting.DARK_GRAY));
    }
}
```

## `src/main/java/com/carnis/mod/item/ViralDartItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import javax.annotation.Nullable;
import java.util.List;

public final class ViralDartItem extends Item {
    public ViralDartItem(Properties properties) { super(properties); }
    @Override public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.carnis.viral_dart.mechanics").withStyle(ChatFormatting.LIGHT_PURPLE));
        tooltip.add(Component.translatable("tooltip.carnis.viral_dart.protocol").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.carnis.dart.use").withStyle(ChatFormatting.DARK_GRAY));
    }
}
```

## `src/main/java/com/carnis/mod/item/PurificationSerumItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.event.HallucinationEvents;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;

public final class PurificationSerumItem extends Item {
    public static final float INFECTION_REDUCTION = 35.0F;
    private static final int DRINK_DURATION_TICKS = 32;

    public PurificationSerumItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(
            Level level,
            Player player,
            InteractionHand hand
    ) {
        ItemStack stack = player.getItemInHand(hand);
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public ItemStack finishUsingItem(
            ItemStack stack,
            Level level,
            LivingEntity user
    ) {
        if (!level.isClientSide() && user instanceof ServerPlayer player) {
            float infectionLevel = PlayerInfectionApi.getInfectionLevel(player);
            PlayerInfectionApi.setInfectionLevel(
                    player,
                    Math.max(0.0F, infectionLevel - INFECTION_REDUCTION)
            );
            HallucinationEvents.resetHallucinationTimer(player);
        }

        if (user instanceof Player player
                && player.getAbilities().instabuild) {
            return stack;
        }

        stack.shrink(1);
        ItemStack emptyBottle = new ItemStack(Items.GLASS_BOTTLE);

        if (stack.isEmpty()) {
            return emptyBottle;
        }

        if (user instanceof Player player
                && !player.getInventory().add(emptyBottle)) {
            player.drop(emptyBottle, false);
        }

        return stack;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.DRINK;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return DRINK_DURATION_TICKS;
    }

    @Override
    public void appendHoverText(ItemStack stack, @javax.annotation.Nullable Level level,
                                java.util.List<net.minecraft.network.chat.Component> tooltip,
                                net.minecraft.world.item.TooltipFlag flag) {
        tooltip.add(net.minecraft.network.chat.Component.translatable("tooltip.carnis.purification_serum.mechanics")
                .withStyle(net.minecraft.ChatFormatting.AQUA));
        tooltip.add(net.minecraft.network.chat.Component.translatable("tooltip.carnis.purification_serum.use")
                .withStyle(net.minecraft.ChatFormatting.GRAY));
    }

    @Override
    public SoundEvent getDrinkingSound() {
        return SoundEvents.GENERIC_DRINK;
    }
}
```

## `src/main/java/com/carnis/mod/event/DartTreatmentEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Persistent loaded-tick treatments; no world scans or background threads. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class DartTreatmentEvents {
    private static final String REGRESSION = "carnis:dart_regression_ticks";
    private static final String MUTATION = "carnis:dart_mutation_ticks";
    private static final String STUN = "carnis:dart_stun_ticks";
    private static final String PRIOR_NO_AI = "carnis:dart_previous_no_ai";
    private DartTreatmentEvents() { }
    public static boolean isMutating(Mob mob) { return mob.getPersistentData().contains(MUTATION); }
    public static boolean isStunned(Mob mob) { return mob.getPersistentData().getInt(STUN) > 0; }
    private static void lock(Mob mob) {
        CompoundTag tag = mob.getPersistentData();
        if (!tag.contains(PRIOR_NO_AI)) tag.putBoolean(PRIOR_NO_AI, mob.isNoAi());
        mob.getNavigation().stop();
        mob.setTarget(null);
        mob.setNoAi(true);
    }
    private static void unlock(Mob mob) {
        CompoundTag tag = mob.getPersistentData();
        if (!tag.contains(PRIOR_NO_AI)) return;
        mob.setNoAi(tag.getBoolean(PRIOR_NO_AI));
        tag.remove(PRIOR_NO_AI);
    }
    public static void startRegression(Mob mob) {
        if (!(mob.level() instanceof ServerLevel) || !mob.isAlive()) return;
        if (!(mob instanceof InfectedZombieEntity) && !(mob instanceof InfectedSkeletonEntity)) return;
        if (mob.getPersistentData().contains(REGRESSION)) return;
        mob.getPersistentData().putInt(REGRESSION, 100);
        HiveSwarmCoordinator.clearFrenzy(mob);
        lock(mob);
    }
    public static void startMutation(Mob mob) {
        if (!(mob.level() instanceof ServerLevel) || !mob.isAlive()) return;
        EntityType<?> type = mob.getType();
        if (type != EntityType.ZOMBIE && type != EntityType.SKELETON && type != EntityType.CREEPER) return;
        if (!mob.getPersistentData().contains(MUTATION)) mob.getPersistentData().putInt(MUTATION, 60);
    }
    public static void stun(Mob mob, int ticks) {
        if (!(mob.level() instanceof ServerLevel) || !mob.isAlive() || ticks <= 0) return;
        CompoundTag tag = mob.getPersistentData();
        tag.putInt(STUN, Math.max(tag.getInt(STUN), ticks));
        HiveSwarmCoordinator.clearFrenzy(mob);
        lock(mob);
    }
    @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || !(mob.level() instanceof ServerLevel level) || !mob.isAlive()) return;
        CompoundTag tag = mob.getPersistentData();
        if (tag.contains(REGRESSION)) {
            lock(mob);
            Vec3 motion = mob.getDeltaMovement();
            mob.setDeltaMovement(0, motion.y, 0);
            if (mob.tickCount % 3 == 0) {
                mob.setYHeadRot(mob.getYRot() + (level.random.nextBoolean() ? 15F : -15F));
                level.sendParticles(ModParticles.PURIFIER_FLAME.get(), mob.getX(), mob.getY(.5D), mob.getZ(),
                        5, mob.getBbWidth() * .35D, mob.getBbHeight() * .35D, mob.getBbWidth() * .35D, .02D);
            }
            int remaining = tag.getInt(REGRESSION) - 1;
            if (remaining <= 0) {
                if (!convert(level, mob, true)) tag.putInt(REGRESSION, 20);
                return;
            }
            tag.putInt(REGRESSION, remaining);
        }
        if (tag.contains(MUTATION)) {
            int remaining = tag.getInt(MUTATION) - 1;
            if (remaining <= 0) {
                if (!convert(level, mob, false)) tag.putInt(MUTATION, 20);
                return;
            }
            tag.putInt(MUTATION, remaining);
        }
        if (tag.getInt(STUN) > 0) {
            lock(mob);
            Vec3 motion = mob.getDeltaMovement();
            mob.setDeltaMovement(0, motion.y, 0);
            int remaining = tag.getInt(STUN) - 1;
            if (remaining == 0) {
                tag.remove(STUN);
                if (!tag.contains(REGRESSION)) unlock(mob);
            } else tag.putInt(STUN, remaining);
        }
    }
    private static boolean convert(ServerLevel level, Mob source, boolean purify) {
        Mob result;
        if (purify && source instanceof InfectedZombieEntity) {
            result = level.random.nextFloat() < .30F ? EntityType.VILLAGER.create(level) : EntityType.ZOMBIE.create(level);
        } else if (purify && source instanceof InfectedSkeletonEntity) {
            result = EntityType.SKELETON.create(level);
        } else if (!purify && source.getType() == EntityType.ZOMBIE) {
            result = ModEntities.INFECTED_ZOMBIE.get().create(level);
        } else if (!purify && source.getType() == EntityType.SKELETON) {
            result = ModEntities.INFECTED_SKELETON.get().create(level);
        } else if (!purify && source.getType() == EntityType.CREEPER) {
            result = ModEntities.INFECTED_CREEPER.get().create(level);
        } else return false;
        if (result == null) return false;
        result.moveTo(source.getX(), source.getY(), source.getZ(), source.getYRot(), source.getXRot());
        result.setCustomName(source.getCustomName());
        result.setCustomNameVisible(source.isCustomNameVisible());
        result.setHealth(Math.max(.01F, Math.min(1F, source.getHealth() / source.getMaxHealth())) * result.getMaxHealth());
        if (source.isPersistenceRequired()) result.setPersistenceRequired();
        for (EquipmentSlot slot : EquipmentSlot.values()) result.setItemSlot(slot, source.getItemBySlot(slot).copy());
        if (!level.addFreshEntity(result)) return false;
        source.discard();
        if (purify) {
            result.spawnAtLocation(new ItemStack(ModItems.BIOMASS_REMAINS.get(), 1 + level.random.nextInt(2)));
            level.playSound(null, result.blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1F, .8F);
        }
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/event/InfectionHandler.java`

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

    /** Viral dart starts stage two and advances incubation three ticks per loaded tick. */
    public static void beginAccelerated(LivingEntity host) {
        if (!(host.level() instanceof ServerLevel) || !IncubationEvents.isEligible(host)) return;
        CompoundTag tag = host.getPersistentData();
        if (tag.getInt(STAGE) < 2) {
            tag.putInt(STAGE, 2);
            tag.putInt(TIMER, 200);
            syncMarker(host, 2);
        }
        tag.putBoolean("carnis:accelerated_incubation", true);
    }

    @SubscribeEvent
    public static void onTick(LivingEvent.LivingTickEvent event) {
        LivingEntity host = event.getEntity();
        if (!(host.level() instanceof ServerLevel level) || !host.isAlive()) return;
        if (host instanceof Mob mob && DartTreatmentEvents.isMutating(mob)) return;
        CompoundTag tag = host.getPersistentData();
        int stage = tag.getInt(STAGE);
        if (stage < 1 || stage > 4 || !IncubationEvents.isEligible(host)) return;
        int timer = tag.getInt(TIMER) + (tag.getBoolean("carnis:accelerated_incubation") ? 3 : 1);
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
        if (!(mob.level() instanceof ServerLevel level) || !mob.isAlive() || durationTicks <= 0
                || com.carnis.mod.event.DartTreatmentEvents.isStunned(mob)) return;
        CompoundTag tag = mob.getPersistentData();
        long until = level.getGameTime() + (long) durationTicks;
        if (dimension(level).equals(tag.getString(FRENZY_DIM))) until = Math.max(until, tag.getLong(FRENZY_UNTIL));
        tag.putLong(FRENZY_UNTIL, until);
        tag.putString(FRENZY_DIM, dimension(level));
        updateSpeed(mob, true);
    }
    public static void clearFrenzy(Mob mob) {
        mob.getPersistentData().remove(FRENZY_UNTIL);
        mob.getPersistentData().remove(FRENZY_DIM);
        updateSpeed(mob, false);
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
        if (!isNoAi()) biomassFeast.tick(server);
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

## `src/main/java/com/carnis/mod/item/PneumaticInoculatorItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.client.renderer.PneumaticInoculatorRenderer;
import com.carnis.mod.entity.PurificationDartEntity;
import com.carnis.mod.entity.ViralDartEntity;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.SingletonGeoAnimatable;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.function.Consumer;

public final class PneumaticInoculatorItem extends Item implements GeoItem {
    private static final int COOLDOWN_TICKS = 15;
    private static final RawAnimation FIRE = RawAnimation.begin().thenPlay("animation.pneumatic_inoculator.fire");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public PneumaticInoculatorItem(Properties properties) {
        super(properties);
        SingletonGeoAnimatable.registerSyncedAnimatable(this);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() { return geoCache; }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<PneumaticInoculatorItem>(this, "action", 0,
                state -> PlayState.STOP).triggerableAnim("fire", FIRE));
    }

    @Override
    public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new IClientItemExtensions() {
            private PneumaticInoculatorRenderer renderer;
            @Override
            public BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new PneumaticInoculatorRenderer();
                return renderer;
            }
        });
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack weapon = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(this)) return InteractionResultHolder.fail(weapon);
        ItemStack ammo = findAmmo(player);
        if (ammo.isEmpty()) return InteractionResultHolder.fail(weapon);

        if (level instanceof ServerLevel server) {
            com.carnis.mod.entity.projectile.InoculatorDartEntity dart = new com.carnis.mod.entity.projectile.InoculatorDartEntity(
                    level, player, ammo.is(ModItems.VIRAL_DART.get())
                    ? com.carnis.mod.entity.projectile.InoculatorDartEntity.DartType.VIRAL
                    : com.carnis.mod.entity.projectile.InoculatorDartEntity.DartType.PURIFICATION);
            dart.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 2.8F, 1.0F);
            if (!server.addFreshEntity(dart)) return InteractionResultHolder.fail(weapon);
            if (!player.getAbilities().instabuild) ammo.shrink(1);
            player.getCooldowns().addCooldown(this, COOLDOWN_TICKS);
            triggerAnim(player, GeoItem.getOrAssignId(weapon, server), "action", "fire");

            Vec3 forward = player.getLookAngle().normalize();
            Vec3 horizontal = new Vec3(forward.x, 0.0D, forward.z);
            if (horizontal.lengthSqr() < 1.0E-8D) {
                float yaw = player.getYRot() * ((float) Math.PI / 180.0F);
                horizontal = new Vec3(-Math.sin(yaw), 0.0D, Math.cos(yaw));
            } else {
                horizontal = horizontal.normalize();
            }
            Vec3 right = new Vec3(-horizontal.z, 0.0D, horizontal.x);
            HumanoidArm heldArm = hand == InteractionHand.MAIN_HAND
                    ? player.getMainArm() : player.getMainArm().getOpposite();
            double side = heldArm == HumanoidArm.RIGHT ? 1.0D : -1.0D;
            Vec3 eye = player.getEyePosition();
            Vec3 muzzle = eye.add(right.scale(0.24D * side)).add(0.0D, -0.24D, 0.0D)
                    .add(forward.scale(0.65D));
            var obstruction = server.clip(new ClipContext(eye, muzzle, ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE, player));
            if (obstruction.getType() != HitResult.Type.MISS) {
                muzzle = obstruction.getLocation().add(eye.subtract(obstruction.getLocation()).normalize().scale(0.02D));
            }
            server.sendParticles(ParticleTypes.POOF, muzzle.x, muzzle.y, muzzle.z,
                    3, 0.025D, 0.025D, 0.025D, 0.01D);
            for (int i = 0; i < 5; i++) {
                double lateral = (i - 2) * 0.045D;
                Vec3 velocity = forward.scale(0.12D).add(right.scale(lateral * 0.12D));
                server.sendParticles(ParticleTypes.CLOUD, muzzle.x, muzzle.y, muzzle.z, 0,
                        velocity.x, velocity.y, velocity.z, 1.0D);
            }
            server.playSound(null, player.blockPosition(), ModSounds.INOCULATOR_FIRE.get(),
                    SoundSource.PLAYERS, 0.9F, 1.0F);
        }
        return InteractionResultHolder.sidedSuccess(weapon, level.isClientSide);
    }

    private static ItemStack findAmmo(Player player) {
        ItemStack selected = player.getMainHandItem();
        if (isAmmo(selected)) return selected;
        ItemStack offhand = player.getOffhandItem();
        if (isAmmo(offhand)) return offhand;
        for (int slot = 0; slot < player.getInventory().getContainerSize(); slot++) {
            ItemStack stack = player.getInventory().getItem(slot);
            if (isAmmo(stack)) return stack;
        }
        return ItemStack.EMPTY;
    }

    private static boolean isAmmo(ItemStack stack) {
        return stack.is(ModItems.VIRAL_DART.get()) || stack.is(ModItems.PURIFICATION_DART.get());
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
            () -> new com.carnis.mod.item.OrganBlockItem(ModBlocks.NERVE_PILLAR.get(), new Item.Properties()));
    public static final RegistryObject<Item> VIRAL_DART = ITEMS.register("viral_dart",
            () -> new com.carnis.mod.item.ViralDartItem(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<Item> PURIFICATION_DART = ITEMS.register("purification_dart",
            () -> new com.carnis.mod.item.PurificationDartItem(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<PneumaticInoculatorItem> PNEUMATIC_INOCULATOR = ITEMS.register(
            "pneumatic_inoculator", () -> new PneumaticInoculatorItem(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> CREEPING_TENDRILS = ITEMS.register(
            "creeping_tendrils", () -> new BlockItem(ModBlocks.CREEPING_TENDRILS.get(), new Item.Properties()));
    public static final RegistryObject<Item> PUSTULE_CLUSTER = ITEMS.register(
            "pustule_cluster", () -> new com.carnis.mod.item.OrganBlockItem(ModBlocks.PUSTULE_CLUSTER.get(), new Item.Properties()));
    public static final RegistryObject<Item> STOMACH_POOL = ITEMS.register(
            "stomach_pool", () -> new com.carnis.mod.item.OrganBlockItem(ModBlocks.STOMACH_POOL.get(), new Item.Properties()));

    public static final RegistryObject<Item> SPORE_SPROUT = ITEMS.register(
            "spore_sprout", () -> new BlockItem(ModBlocks.SPORE_SPROUT.get(), new Item.Properties()));
    public static final RegistryObject<Item> NEURAL_MOSS = ITEMS.register(
            "neural_moss", () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.NEURAL_MOSS.get(), new Item.Properties(), "neural_moss"));

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

## `src/main/java/com/carnis/mod/client/renderer/DartRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.PurificationDartEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public final class DartRenderer<T extends AbstractArrow> extends EntityRenderer<T> {
    private static final ResourceLocation TEXTURE =
            new ResourceLocation(CarnisMod.MOD_ID, "textures/entity/dart.png");
    private static final int STEEL = 0;
    private static final int DARK_STEEL = 1;
    private static final int BRASS = 2;
    private static final int VIRAL = 3;
    private static final int VIRAL_ACCENT = 4;
    private static final int SERUM = 5;
    private static final int GLASS = 6;
    private static final int GLASS_RIM = 7;

    public DartRenderer(EntityRendererProvider.Context context) {
        super(context);
        shadowRadius = 0.0F;
    }

    @Override
    public void render(T dart, float entityYaw, float partialTick, PoseStack poseStack,
                       MultiBufferSource buffers, int packedLight) {
        poseStack.pushPose();
        poseStack.mulPose(Axis.YP.rotationDegrees(Mth.rotLerp(partialTick, dart.yRotO, dart.getYRot()) - 90.0F));
        poseStack.mulPose(Axis.ZP.rotationDegrees(Mth.lerp(partialTick, dart.xRotO, dart.getXRot())));

        VertexConsumer vertices = buffers.getBuffer(RenderType.entityCutoutNoCull(TEXTURE));
        boolean purification = dart instanceof PurificationDartEntity
                || dart instanceof com.carnis.mod.entity.projectile.InoculatorDartEntity inoculator
                && inoculator.getDartType() == com.carnis.mod.entity.projectile.InoculatorDartEntity.DartType.PURIFICATION;
        int fluid = purification ? SERUM : VIRAL;

        // The model's positive X axis points toward the needle tip.
        box(poseStack, vertices, packedLight, -0.34F, -0.018F, -0.018F, 0.34F, 0.018F, 0.018F, STEEL);
        box(poseStack, vertices, packedLight, 0.32F, -0.010F, -0.010F, 0.52F, 0.010F, 0.010F, GLASS);
        box(poseStack, vertices, packedLight, -0.15F, -0.056F, -0.056F, 0.10F, 0.056F, 0.056F, fluid);
        box(poseStack, vertices, packedLight, -0.15F, -0.064F, -0.064F, 0.10F, -0.054F, -0.054F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.15F, 0.054F, -0.064F, 0.10F, 0.064F, -0.054F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.15F, -0.064F, 0.054F, 0.10F, -0.054F, 0.064F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.15F, 0.054F, 0.054F, 0.10F, 0.064F, 0.064F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.14F, 0.057F, -0.038F, 0.08F, 0.061F, -0.023F, GLASS);
        if (!purification) {
            box(poseStack, vertices, packedLight, -0.09F, 0.057F, 0.015F, 0.03F, 0.061F, 0.033F, VIRAL_ACCENT);
        }
        box(poseStack, vertices, packedLight, -0.19F, -0.072F, -0.072F, -0.15F, 0.072F, 0.072F, BRASS);
        box(poseStack, vertices, packedLight, 0.10F, -0.072F, -0.072F, 0.14F, 0.072F, 0.072F, BRASS);
        box(poseStack, vertices, packedLight, -0.43F, -0.025F, -0.025F, -0.30F, 0.025F, 0.025F, DARK_STEEL);
        box(poseStack, vertices, packedLight, -0.42F, -0.125F, -0.012F, -0.29F, 0.125F, 0.012F, BRASS);
        box(poseStack, vertices, packedLight, -0.42F, -0.012F, -0.125F, -0.29F, 0.012F, 0.125F, BRASS);

        poseStack.popPose();
        super.render(dart, entityYaw, partialTick, poseStack, buffers, packedLight);
    }

    private static void box(PoseStack stack, VertexConsumer out, int light,
                            float x0, float y0, float z0, float x1, float y1, float z1, int swatch) {
        float u = (swatch * 4.0F + 2.0F) / 32.0F;
        float v = 0.5F;
        face(stack, out, light, u, v, -1, 0, 0, x0,y0,z0, x0,y0,z1, x0,y1,z1, x0,y1,z0);
        face(stack, out, light, u, v,  1, 0, 0, x1,y0,z1, x1,y0,z0, x1,y1,z0, x1,y1,z1);
        face(stack, out, light, u, v, 0, -1, 0, x0,y0,z1, x0,y0,z0, x1,y0,z0, x1,y0,z1);
        face(stack, out, light, u, v, 0,  1, 0, x0,y1,z0, x0,y1,z1, x1,y1,z1, x1,y1,z0);
        face(stack, out, light, u, v, 0, 0, -1, x1,y0,z0, x0,y0,z0, x0,y1,z0, x1,y1,z0);
        face(stack, out, light, u, v, 0, 0,  1, x0,y0,z1, x1,y0,z1, x1,y1,z1, x0,y1,z1);
    }

    private static void face(PoseStack stack, VertexConsumer out, int light, float u, float v,
                             float nx, float ny, float nz,
                             float ax, float ay, float az, float bx, float by, float bz,
                             float cx, float cy, float cz, float dx, float dy, float dz) {
        PoseStack.Pose pose = stack.last();
        vertex(pose, out, light, u, v, nx, ny, nz, ax, ay, az);
        vertex(pose, out, light, u, v, nx, ny, nz, bx, by, bz);
        vertex(pose, out, light, u, v, nx, ny, nz, cx, cy, cz);
        vertex(pose, out, light, u, v, nx, ny, nz, dx, dy, dz);
    }

    private static void vertex(PoseStack.Pose pose, VertexConsumer out, int light, float u, float v,
                               float nx, float ny, float nz, float x, float y, float z) {
        out.vertex(pose.pose(), x, y, z).color(255, 255, 255, 255).uv(u, v)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light)
                .normal(pose.normal(), nx, ny, nz).endVertex();
    }

    @Override
    public ResourceLocation getTextureLocation(T dart) {
        return TEXTURE;
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

## `src/main/resources/data/carnis/recipes/purification_serum.json`

```json
{
  "type": "minecraft:crafting_shapeless",
  "ingredients": [
    {
      "item": "minecraft:milk_bucket"
    },
    {
      "item": "minecraft:honey_bottle"
    },
    {
      "item": "carnis:creeping_tendrils"
    },
    {
      "item": "minecraft:glass_bottle"
    }
  ],
  "result": {
    "item": "carnis:purification_serum",
    "count": 1
  }
}
```

## `src/main/resources/data/carnis/recipes/purification_dart.json`

```json
{
  "type": "minecraft:crafting_shaped",
  "pattern": [
    " I ",
    " S ",
    " F "
  ],
  "key": {
    "I": {
      "item": "minecraft:iron_nugget"
    },
    "S": {
      "item": "carnis:purification_serum"
    },
    "F": {
      "item": "minecraft:feather"
    }
  },
  "result": {
    "item": "carnis:purification_dart",
    "count": 4
  }
}
```

## `src/main/resources/data/carnis/recipes/viral_dart.json`

```json
{
  "type": "minecraft:crafting_shaped",
  "pattern": [
    " I ",
    " S ",
    " F "
  ],
  "key": {
    "I": {
      "item": "minecraft:iron_nugget"
    },
    "S": {
      "item": "carnis:living_flesh"
    },
    "F": {
      "item": "minecraft:feather"
    }
  },
  "result": {
    "item": "carnis:viral_dart",
    "count": 4
  }
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
  "entity.carnis.inoculator_dart": "Inoculator Dart"
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
  "entity.carnis.inoculator_dart": "Дротик инокулятора"
}
```
