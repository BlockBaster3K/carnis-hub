package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModItems;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ProgressionEvents {
    private static final ResourceLocation JOURNAL_ADVANCEMENT = new ResourceLocation(CarnisMod.MOD_ID, "read_research_journal");
    private static final ResourceLocation ARMOR_ADVANCEMENT = new ResourceLocation(CarnisMod.MOD_ID, "neuro_resonator_set");

    private ProgressionEvents() { }

    @SubscribeEvent
    public static void onReadJournal(PlayerInteractEvent.RightClickItem event) {
        if (!(event.getEntity() instanceof ServerPlayer player)
                || !event.getItemStack().is(ModItems.RESEARCH_JOURNAL.get())) return;
        award(player, JOURNAL_ADVANCEMENT, "read_journal");
    }

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)) return;
        if (wearingFullResonatorSet(player)) award(player, ARMOR_ADVANCEMENT, "full_set");
    }

    private static boolean wearingFullResonatorSet(Player player) {
        return player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.NEURO_RESONATOR_HELMET.get())
                && player.getItemBySlot(EquipmentSlot.CHEST).is(ModItems.NEURO_RESONATOR_CHESTPLATE.get())
                && player.getItemBySlot(EquipmentSlot.LEGS).is(ModItems.NEURO_RESONATOR_LEGGINGS.get())
                && player.getItemBySlot(EquipmentSlot.FEET).is(ModItems.NEURO_RESONATOR_BOOTS.get());
    }

    private static void award(ServerPlayer player, ResourceLocation id, String criterion) {
        var server = player.getServer();
        if (server == null) return;
        var advancement = server.getAdvancements().getAdvancement(id);
        if (advancement != null) player.getAdvancements().award(advancement, criterion);
    }
}
