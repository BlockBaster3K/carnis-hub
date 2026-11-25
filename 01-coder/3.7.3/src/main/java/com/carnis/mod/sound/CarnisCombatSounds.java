package com.carnis.mod.sound;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.init.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.common.ToolAction;
import net.minecraftforge.common.ToolActions;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.lang.ref.WeakReference;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;

/** Server-side combat sound routing and short delayed dismemberment playback. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisCombatSounds {
    private static final long HEAVY_HIT_COOLDOWN_TICKS = 2L;
    private static final long DISMEMBER_COOLDOWN_TICKS = 20L;

    private static final Map<LivingEntity, Long> LAST_HEAVY_HIT = new WeakHashMap<>();
    private static final Map<LivingEntity, Long> LAST_DISMEMBER = new WeakHashMap<>();
    private static final List<PendingSound> PENDING_DISMEMBER_SOUNDS = new ArrayList<>();

    private CarnisCombatSounds() { }

    /** Plays the regular flesh-hit variation for a server-side target. */
    public static void onHit(LivingEntity target) {
        ServerLevel level = serverLevel(target);
        if (level == null) return;
        playAt(level, target, ModSounds.COMBAT_FLESH_HIT.get(), 1.0F);
    }

    /** Plays a deep hit at most once per target every two game ticks (100 ms). */
    public static void onHeavyHit(LivingEntity target) {
        ServerLevel level = serverLevel(target);
        if (level == null) return;

        long now = level.getGameTime();
        synchronized (LAST_HEAVY_HIT) {
            Long previous = LAST_HEAVY_HIT.get(target);
            if (previous != null && now >= previous && now - previous < HEAVY_HIT_COOLDOWN_TICKS) return;
            LAST_HEAVY_HIT.put(target, now);
        }

        playAt(level, target, ModSounds.COMBAT_FLESH_HIT_DEEP.get(), 1.0F);
    }

    /**
     * Schedules a dismemberment sound 3–5 ticks after the hit, with a one-second per-target cooldown.
     * The caller supplies the current game time so this can be used by existing combat/dismemberment logic.
     */
    public static void onDismember(LivingEntity target, DamageSource src, long now) {
        ServerLevel level = serverLevel(target);
        if (level == null || src == null) return;

        synchronized (LAST_DISMEMBER) {
            Long previous = LAST_DISMEMBER.get(target);
            if (previous != null && now >= previous && now - previous < DISMEMBER_COOLDOWN_TICKS) return;
            LAST_DISMEMBER.put(target, now);
        }

        int delay = 3 + target.getRandom().nextInt(3);
        float volume = 1.0F;
        PendingSound pending = new PendingSound(new WeakReference<>(level),
                level.getGameTime() + delay, target.getX(), target.getY(), target.getZ(),
                ModSounds.COMBAT_DISMEMBER.get(), volume);
        synchronized (PENDING_DISMEMBER_SOUNDS) {
            PENDING_DISMEMBER_SOUNDS.add(pending);
        }
    }

    /** Routes combat sounds for Hive targets and armored non-Hive targets. */
    @SubscribeEvent
    public static void onLivingHurt(LivingHurtEvent event) {
        LivingEntity target = event.getEntity();
        if (event.isCanceled() || !(target.level() instanceof ServerLevel level)
                || event.getAmount() <= 0.0F) return;

        DamageSource source = event.getSource();
        Entity attacker = source.getEntity();
        boolean explosion = source.is(DamageTypeTags.IS_EXPLOSION);
        if (attacker == target || attacker == null && source.getDirectEntity() == null && !explosion) return;

        boolean axeHit = hasToolAction(attacker, ToolActions.AXE_DIG);
        boolean swordHit = hasToolAction(attacker, ToolActions.SWORD_DIG);
        boolean hiveTarget = NeuralMossBlock.isHive(target);

        if (!hiveTarget) {
            if (hasArmorItem(target) && (axeHit || swordHit)) {
                playAt(level, target, ModSounds.COMBAT_ARMOR_DEFLECT.get(), 1.0F);
            }
            if (attacker instanceof Player player
                    && player.getAttackStrengthScale(0.5F) > 0.9F
                    && event.getAmount() > 6.0F) {
                playAt(level, target, ModSounds.COMBAT_BLOCK_STAB.get(), 1.0F);
            }
            return;
        }

        boolean criticalHit = isCriticalHit(attacker);
        boolean highDamage = event.getAmount() > 6.0F && !swordHit;
        if (axeHit || criticalHit || explosion || highDamage) {
            onHeavyHit(target);
        } else {
            onHit(target);
        }
    }

    @SubscribeEvent
    public static void onLivingDeath(LivingDeathEvent event) {
        LivingEntity victim = event.getEntity();
        if (event.isCanceled() || !(victim.level() instanceof ServerLevel level)
                || !NeuralMossBlock.isHive(victim)) return;

        Entity attacker = event.getSource().getEntity();
        boolean eligibleAttacker = attacker instanceof Player
                || attacker instanceof Mob mob && NeuralMossBlock.isHive(mob);
        if (eligibleAttacker) onDismember(victim, event.getSource(), level.getGameTime());
    }

    private static boolean hasToolAction(Entity entity, ToolAction action) {
        if (!(entity instanceof LivingEntity living)) return false;
        return living.getMainHandItem().canPerformAction(action)
                || living.getOffhandItem().canPerformAction(action);
    }

    private static boolean hasArmorItem(LivingEntity entity) {
        for (ItemStack stack : entity.getArmorSlots()) {
            if (!stack.isEmpty() && stack.getItem() instanceof ArmorItem) return true;
        }
        return false;
    }

    private static boolean isCriticalHit(Entity attacker) {
        if (!(attacker instanceof Player player)) return false;
        return player.getAttackStrengthScale(0.5F) > 0.9F
                && player.fallDistance > 0.0F
                && !player.onGround()
                && !player.onClimbable()
                && !player.isInWater()
                && !player.hasEffect(MobEffects.BLINDNESS)
                && !player.isPassenger()
                && !player.isSprinting()
                && !player.isFallFlying();
    }

    @SubscribeEvent
    public static void onLevelTick(TickEvent.LevelTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.level instanceof ServerLevel level)) return;

        List<PendingSound> ready = new ArrayList<>();
        synchronized (PENDING_DISMEMBER_SOUNDS) {
            Iterator<PendingSound> iterator = PENDING_DISMEMBER_SOUNDS.iterator();
            while (iterator.hasNext()) {
                PendingSound pending = iterator.next();
                ServerLevel pendingLevel = pending.level().get();
                if (pendingLevel == null) {
                    iterator.remove();
                } else if (pendingLevel == level && level.getGameTime() >= pending.dueAt()) {
                    ready.add(pending);
                    iterator.remove();
                }
            }
        }

        for (PendingSound pending : ready) {
            level.playSound(null, pending.x(), pending.y(), pending.z(), pending.sound(),
                    SoundSource.HOSTILE, pending.volume(), 1.0F);
        }
    }

    private static ServerLevel serverLevel(LivingEntity target) {
        return target.level() instanceof ServerLevel level ? level : null;
    }

    private static void playAt(ServerLevel level, LivingEntity target, SoundEvent sound, float volume) {
        level.playSound(null, target.getX(), target.getY(), target.getZ(), sound,
                SoundSource.HOSTILE, volume, 1.0F);
    }

    private record PendingSound(WeakReference<ServerLevel> level, long dueAt,
                                double x, double y, double z, SoundEvent sound,
                                float volume) { }
}
