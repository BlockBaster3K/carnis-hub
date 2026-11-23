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
        if (type != EntityType.ZOMBIE && type != EntityType.SKELETON && type != EntityType.CREEPER
                && type != EntityType.SPIDER && type != EntityType.CAVE_SPIDER) return;
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
        } else if (!purify && (source.getType() == EntityType.SPIDER
                || source.getType() == EntityType.CAVE_SPIDER)) {
            result = ModEntities.INFECTED_SPIDER.get().create(level);
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
            level.playSound(null, result.blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1F, 1.0F);
        }
        return true;
    }
}
