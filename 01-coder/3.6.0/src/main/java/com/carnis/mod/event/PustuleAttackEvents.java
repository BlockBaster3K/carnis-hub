package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.PustuleClusterBlock;
import net.minecraft.server.level.ServerLevel;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PustuleAttackEvents {
    private PustuleAttackEvents() { }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onAttack(PlayerInteractEvent.LeftClickBlock event) {
        if (event.isCanceled() || event.getAction() != PlayerInteractEvent.LeftClickBlock.Action.START) return;
        var level = event.getLevel();
        if (!PustuleClusterBlock.ready(level.getBlockState(event.getPos()))) return;
        if (level instanceof ServerLevel server) {
            if (PustuleClusterBlock.burst(server, event.getPos())) event.setCanceled(true);
        }
    }
}
