package com.carnis.mod.entity.ai;

import com.carnis.mod.CarnisMod;
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
        return mob != null && target != null && target != mob && target.isAlive()
                && target.level() == mob.level() && !target.isSpectator()
                && (!(target instanceof Player player) || !player.isCreative())
                && !(target instanceof HivemindLinkedMob)
                && !NeuroArmorEventHandler.isHiveEntity(target)
                && mob.canAttack(target);
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
        if (mob.getTarget() != null && !validTarget(mob, mob.getTarget())) mob.setTarget(null);
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
        if (event.isCanceled() || !(event.getEntity() instanceof Mob mob)
                || !(mob instanceof HivemindLinkedMob) || !(mob.level() instanceof ServerLevel level)) return;
        LivingEntity candidate = event.getNewTarget();
        if (candidate != null && !validTarget(mob, candidate)) {
            event.setCanceled(true);
            return;
        }
        if (BROADCASTING.get() || candidate == null) return;
        broadcast(level, mob.position(), 20.0D, candidate, false, false, null);
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
        level.playSound(null, pos, ModSounds.PHANTOM_WHISPER.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
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
