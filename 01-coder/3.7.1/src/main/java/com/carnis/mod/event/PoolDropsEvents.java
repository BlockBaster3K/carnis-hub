package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PoolDropsEvents {
    private PoolDropsEvents() { }
    @SubscribeEvent public static void onDrops(LivingDropsEvent event) {
        var entity = event.getEntity();
        var data = entity.getPersistentData();
        if (data.getBoolean("carnis:pool_dissolving")
                && data.getLong("carnis:pool_dissolving_until") >= entity.level().getGameTime()) {
            event.setCanceled(true);
        }
    }
}
