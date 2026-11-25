package com.carnis.mod.infection;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfection;
import com.carnis.mod.capability.infection.PlayerInfectionCapability;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModDamageSources;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.item.NeuroWeave;
import com.carnis.mod.network.ModMessages;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.UUID;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerInfectionManager {
    public static final String POINTS = "carnis:infection_points";
    public static final String METAMORPHOSED = "carnis:human_metamorphosed";
    private static final String FRACTION = "carnis:infection_fraction";
    private static final String AGONY = "carnis:infection_agony_remaining";
    private static final String TERMINAL_ATTEMPT = "carnis:terminal_attempt";
    private static final String DEATH_OBSERVED = "carnis:terminal_death_observed";
    private static final UUID SLOW_ID = UUID.fromString("048ac83b-cbb9-4f41-96c8-9f62a6db0200");
    private static final AttributeModifier SLOW = new AttributeModifier(SLOW_ID, "Carnis infection", -.10D,
            AttributeModifier.Operation.MULTIPLY_TOTAL);
    private PlayerInfectionManager() { }

    /** The integer NBT value is authoritative; fractional exposure is retained separately. */
    public static float getPoints(Player player) {
        CompoundTag data = player.getPersistentData();
        if (!data.contains(POINTS)) {
            float legacy = player.getCapability(PlayerInfectionCapability.PLAYER_INFECTION)
                    .resolve().map(cap -> cap.getInfectionLevel()).orElse(0.0F);
            writeRaw(player, legacy);
        }
        int whole = Math.max(0, Math.min(100, data.getInt(POINTS)));
        float fraction = data.getFloat(FRACTION);
        if (!Float.isFinite(fraction) || fraction < 0 || fraction >= 1 || whole == 100) fraction = 0;
        return whole + fraction;
    }
    public static int stage(float points) {
        if (points <= 0) return 0;
        if (points < 25) return 1;
        if (points < 50) return 2;
        if (points < 90) return 3;
        return 4;
    }
    public static int displayPoints(Player player) { return (int) Math.floor(getPoints(player)); }
    private static void writeRaw(Player player, float value) {
        if (!Float.isFinite(value)) value = 0;
        value = Math.max(0, Math.min(100, value));
        int whole = (int) Math.floor(value);
        player.getPersistentData().putInt(POINTS, whole);
        player.getPersistentData().putFloat(FRACTION, whole == 100 ? 0 : value - whole);
        float mirror = value;
        player.getCapability(PlayerInfectionCapability.PLAYER_INFECTION).ifPresent(cap -> {
            if (cap instanceof PlayerInfection legacy) legacy.setInfectionLevelSilently(mirror);
        });
    }
    public static boolean setPoints(Player player, float value) {
        float before = getPoints(player);
        if (!Float.isFinite(value)) return false;
        value = Math.max(0, Math.min(100, value));
        if (Float.compare(before, value) == 0) return false;
        writeRaw(player, value);
        if (value < 100) player.getPersistentData().remove(AGONY);
        if (!player.level().isClientSide) {
            updateSlow(player, stage(value) >= 2);
            if (player instanceof ServerPlayer server && ((int) Math.floor(before) != (int) Math.floor(value)
                    || stage(before) != stage(value))) ModMessages.sendPlayerInfection(server);
        }
        return true;
    }
    public static void copyToClone(Player original, Player replacement, boolean death) {
        float points = getPoints(original);
        writeRaw(replacement, points);
        replacement.getPersistentData().remove(METAMORPHOSED);
        if (!death && original.getPersistentData().contains(AGONY))
            replacement.getPersistentData().putInt(AGONY, original.getPersistentData().getInt(AGONY));
        else replacement.getPersistentData().remove(AGONY);
    }
    private static void updateSlow(Player player, boolean active) {
        AttributeInstance speed = player.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed == null) return;
        boolean present = speed.getModifier(SLOW_ID) != null;
        if (active && !present) speed.addTransientModifier(SLOW);
        else if (!active && present) speed.removeModifier(SLOW_ID);
    }
    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)) return;
        float points = getPoints(player);
        int stage = stage(points);
        updateSlow(player, player.isAlive() && stage >= 2);
        if (player.tickCount % 20 == 0) {
            ModMessages.sendPlayerInfection(player);
            if (player.isAlive() && !player.isSpectator() && stage >= 1) player.causeFoodExhaustion(.02F);
        }
        if (!player.isAlive() || player.isSpectator() || player.isCreative() || points < 100) {
            if (points < 100) player.getPersistentData().remove(AGONY);
            return;
        }
        CompoundTag data = player.getPersistentData();
        if (!data.contains(AGONY)) { data.putInt(AGONY, 100); return; }
        int remaining = data.getInt(AGONY) - 1;
        data.putInt(AGONY, remaining);
        if (remaining <= 0) metamorphose(player);
    }
    @SubscribeEvent(priority = EventPriority.NORMAL)
    public static void onHurt(LivingHurtEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof ServerPlayer player) || stage(getPoints(player)) < 3) return;
        if (NeuroArmorEventHandler.isHiveEntity(event.getSource().getEntity())) event.setAmount(event.getAmount() * .8F);
        if (event.getSource().is(DamageTypeTags.IS_FIRE)) event.setAmount(event.getAmount() * 1.5F);
    }
    private static boolean neutralAtDistance(Mob mob, Player player) {
        return stage(getPoints(player)) >= 2 && mob.distanceToSqr(player) > 144.0D;
    }
    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onTargetChange(LivingChangeTargetEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide
                || !NeuroArmorEventHandler.isHiveEntity(mob) || !(event.getNewTarget() instanceof Player player)) return;
        if (neutralAtDistance(mob, player)) event.setCanceled(true);
    }
    @SubscribeEvent
    public static void onLivingTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide
                || !NeuroArmorEventHandler.isHiveEntity(mob) || !(mob.getTarget() instanceof Player player)) return;
        if (neutralAtDistance(mob, player)) mob.setTarget(null);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onTerminalDeath(LivingDeathEvent event) {
        if (!event.isCanceled() && event.getEntity() instanceof ServerPlayer player
                && player.getPersistentData().getBoolean(TERMINAL_ATTEMPT)
                && event.getSource().is(ModDamageSources.ORGANIC_CONSUMPTION))
            player.getPersistentData().putBoolean(DEATH_OBSERVED, true);
    }
    private static void metamorphose(ServerPlayer player) {
        ServerLevel level = player.serverLevel();
        // Do not transfer equipment if vanilla keepInventory protects the player's inventory.
        boolean transfer = !level.getGameRules().getBoolean(GameRules.RULE_KEEPINVENTORY);
        ItemStack weapon = ItemStack.EMPTY, helmet = ItemStack.EMPTY;
        if (transfer) {
            ItemStack held = player.getMainHandItem();
            if (held.getItem() instanceof net.minecraft.world.item.SwordItem
                    || held.getItem() instanceof net.minecraft.world.item.AxeItem
                    || held.getItem() instanceof net.minecraft.world.item.BowItem
                    || held.getItem() instanceof net.minecraft.world.item.CrossbowItem
                    || held.getItem() instanceof net.minecraft.world.item.TridentItem) {
                weapon = held.copy();
                player.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
            }
            helmet = player.getItemBySlot(EquipmentSlot.HEAD).copy();
            player.setItemSlot(EquipmentSlot.HEAD, ItemStack.EMPTY);
        }
        CompoundTag data = player.getPersistentData();
        data.remove(DEATH_OBSERVED);
        data.putBoolean(TERMINAL_ATTEMPT, true);
        try { player.hurt(ModDamageSources.organicConsumption(level), 10000.0F); }
        finally { data.remove(TERMINAL_ATTEMPT); }
        boolean deathObserved = data.getBoolean(DEATH_OBSERVED);
        data.remove(DEATH_OBSERVED);
        if (!deathObserved || player.isAlive()) {
            restore(player, EquipmentSlot.MAINHAND, weapon);
            restore(player, EquipmentSlot.HEAD, helmet);
            player.getPersistentData().putInt(AGONY, 20);
            return;
        }
        player.getPersistentData().putBoolean(METAMORPHOSED, true);
        setPoints(player, 0);
        player.getPersistentData().remove(AGONY);
        InfectedZombieEntity clone = ModEntities.INFECTED_ZOMBIE.get().create(level);
        boolean spawned = false;
        if (clone != null) {
            clone.moveTo(player.getX(), player.getY(), player.getZ(), player.getYRot(), 0);
            clone.setPersistenceRequired();
            clone.setItemSlot(EquipmentSlot.MAINHAND, weapon);
            clone.setItemSlot(EquipmentSlot.HEAD, helmet);
            clone.setDropChance(EquipmentSlot.MAINHAND, 1.0F);
            clone.setDropChance(EquipmentSlot.HEAD, 1.0F);
            for (int[] offset : new int[][]{{0,0,0},{1,0,0},{-1,0,0},{0,0,1},{0,0,-1},{0,1,0}}) {
                BlockPos spot = player.blockPosition().offset(offset[0], offset[1], offset[2]);
                if (!level.hasChunkAt(spot) || level.isOutsideBuildHeight(spot)) continue;
                clone.moveTo(spot.getX() + .5D, spot.getY(), spot.getZ() + .5D, player.getYRot(), 0);
                if (!level.noCollision(clone)) continue;
                spawned = level.addFreshEntity(clone);
                break;
            }
        }
        if (!spawned) {
            dropAt(level, player, weapon);
            dropAt(level, player, helmet);
        }
        if (level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)) seedTissue(level, player.blockPosition());
    }
    private static void restore(ServerPlayer player, EquipmentSlot slot, ItemStack stack) {
        if (stack.isEmpty()) return;
        if (player.getItemBySlot(slot).isEmpty()) player.setItemSlot(slot, stack);
        else if (!player.getInventory().add(stack)) player.drop(stack, false);
    }
    private static void dropAt(ServerLevel level, Player player, ItemStack stack) {
        if (!stack.isEmpty()) level.addFreshEntity(new ItemEntity(level, player.getX(), player.getY(), player.getZ(), stack));
    }
    private static void seedTissue(ServerLevel level, BlockPos center) {
        BlockState remains = ModBlocks.BIOMASS_REMAINS.get().defaultBlockState();
        for (BlockPos pos : BlockPos.betweenClosed(center.offset(-1, -1, -1), center.offset(1, 1, 1))) {
            if (!level.hasChunkAt(pos) || level.isOutsideBuildHeight(pos) || !level.isEmptyBlock(pos)) continue;
            if (remains.canSurvive(level, pos) && level.setBlockAndUpdate(pos, remains)) break;
        }
        for (BlockPos pos : BlockPos.betweenClosed(center.offset(-3, -3, -3), center.offset(3, 3, 3))) {
            if (pos.distSqr(center) > 9 || level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) continue;
            BlockState state = level.getBlockState(pos);
            if (!state.isAir() || !state.getFluidState().isEmpty()) continue;
            BlockState vein = Blocks.AIR.defaultBlockState();
            for (Direction face : Direction.values()) {
                BlockPos support = pos.relative(face);
                if (!level.hasChunkAt(support) || level.isOutsideBuildHeight(support)
                        || !level.getBlockState(support).isFaceSturdy(level, support, face.getOpposite())) continue;
                BlockState next = ModBlocks.FLESH_VEINS.get().getStateForPlacement(vein, level, pos, face);
                if (next != null) vein = next;
            }
            if (vein.is(ModBlocks.FLESH_VEINS.get())) level.setBlockAndUpdate(pos, vein);
        }
    }
}
