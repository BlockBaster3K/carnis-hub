package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.HiveEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.item.armor.NeuroArmorItem;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NeuroArmorEventHandler {
    private static final EquipmentSlot[] SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
    private static final String PROVOKED_UNTIL = "carnis:neuro_provoked_until";
    private static final String PROVOKED_DIMENSION = "carnis:neuro_provoked_dimension";
    private static final int PROVOCATION_TICKS = 600;
    private NeuroArmorEventHandler() { }

    private static boolean piece(LivingEntity entity, EquipmentSlot slot, ArmorItem.Type expected) {
        ItemStack stack = entity.getItemBySlot(slot);
        return stack.getItem() instanceof NeuroArmorItem armor && armor.getType() == expected;
    }
    public static boolean hasHelmet(LivingEntity entity) { return piece(entity, EquipmentSlot.HEAD, ArmorItem.Type.HELMET); }
    public static boolean hasSymbioticPair(LivingEntity entity) {
        return piece(entity, EquipmentSlot.CHEST, ArmorItem.Type.CHESTPLATE)
                && piece(entity, EquipmentSlot.LEGS, ArmorItem.Type.LEGGINGS);
    }
    public static int pieces(LivingEntity entity) {
        int count = 0;
        for (EquipmentSlot slot : SLOTS) {
            ItemStack stack = entity.getItemBySlot(slot);
            if (stack.getItem() instanceof NeuroArmorItem armor && armor.getEquipmentSlot() == slot) count++;
        }
        return count;
    }
    public static boolean hasFullSet(LivingEntity entity) { return pieces(entity) == 4; }
    public static boolean isHiveEntity(Entity entity) {
        if (!(entity instanceof LivingEntity)) return false;
        if (entity instanceof HiveEntity || entity instanceof HivemindLinkedMob) return true;
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
        return id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }
    public static void provoke(Player player) {
        player.getPersistentData().putLong(PROVOKED_UNTIL, player.level().getGameTime() + PROVOCATION_TICKS);
        player.getPersistentData().putString(PROVOKED_DIMENSION, player.level().dimension().location().toString());
    }
    public static boolean isProvoked(Player player) {
        return player.level().dimension().location().toString().equals(player.getPersistentData().getString(PROVOKED_DIMENSION))
                && player.level().getGameTime() < player.getPersistentData().getLong(PROVOKED_UNTIL);
    }
    /** Eye-like sensors can detect an unprovoked disguised player at four blocks or closer. */
    public static boolean hiddenFromSensor(Player player, double distanceSquared) {
        return hasFullSet(player) && !isProvoked(player) && distanceSquared > 16.0D;
    }
    private static boolean hiddenFromMob(Player player) { return hasFullSet(player) && !isProvoked(player); }

    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onHurt(LivingHurtEvent event) {
        if (event.isCanceled() || event.getEntity().level().isClientSide) return;
        Entity attacker = event.getSource().getEntity();
        if (attacker instanceof Player player && isHiveEntity(event.getEntity()) && event.getAmount() > 0) provoke(player);
        if (event.getEntity() instanceof Player player && isHiveEntity(attacker)) {
            event.setAmount(event.getAmount() * (1.0F - 0.08F * pieces(player)));
        }
    }
    @SubscribeEvent
    public static void onTargetChange(LivingChangeTargetEvent event) {
        if (!event.getEntity().level().isClientSide && isHiveEntity(event.getEntity())
                && event.getNewTarget() instanceof Player player && hiddenFromMob(player)) event.setCanceled(true);
    }
    @SubscribeEvent
    public static void onLivingTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide || !isHiveEntity(mob)) return;
        if (mob.getTarget() instanceof Player player && hiddenFromMob(player)) mob.setTarget(null);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onBreak(BlockEvent.BreakEvent event) {
        if (event.isCanceled() || event.getPlayer().level().isClientSide || !hasFullSet(event.getPlayer())) return;
        BlockState state = event.getState();
        if (!state.is(ModBlocks.LIVING_FLESH.get()) && !state.is(ModBlocks.OSSIFIED_FLESH.get())
                && !state.is(ModBlocks.FIREPROOF_FLESH.get()) && !state.is(ModBlocks.FLESH_VEINS.get())
                && !state.is(ModBlocks.BIOMASS_REMAINS.get())) return;
        Player player = event.getPlayer();
        BlockPos pos = event.getPos();
        var nearby = player.level().getEntitiesOfClass(Mob.class, new AABB(pos).inflate(12.0D),
                mob -> mob.isAlive() && isHiveEntity(mob) && mob.distanceToSqr(pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D) <= 144.0D);
        if (nearby.isEmpty()) return;
        provoke(player);
        for (Mob mob : nearby) if (mob.canAttack(player)) mob.setTarget(player);
    }
    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.player.level().isClientSide) return;
        Player player = event.player;
        if (!player.isAlive() || player.isSpectator() || !player.onGround() || !hasSymbioticPair(player)
                || player.tickCount % 60 != 0 || player.getHealth() >= player.getMaxHealth()) return;
        if (player.getBlockStateOn().is(ModBlocks.LIVING_FLESH.get())) player.heal(1.0F);
    }
}
