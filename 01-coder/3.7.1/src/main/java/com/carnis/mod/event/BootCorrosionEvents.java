package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.item.NeuroWeave;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class BootCorrosionEvents {
    private BootCorrosionEvents() { }

    @SubscribeEvent
    public static void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)
                || !player.isAlive() || player.isSpectator() || !player.onGround()
                || player.tickCount % 60 != 0 || !player.getBlockStateOn().is(ModBlocks.LIVING_FLESH.get())) return;
        ItemStack boots = player.getItemBySlot(EquipmentSlot.FEET);
        if (!boots.isEmpty() && !NeuroWeave.isWoven(boots) && !(boots.getItem() instanceof com.carnis.mod.item.armor.NeuroArmorItem)) {
            boots.hurtAndBreak(1, player, entity -> entity.broadcastBreakEvent(EquipmentSlot.FEET));
        }
    }
}
