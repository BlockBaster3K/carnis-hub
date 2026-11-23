package com.carnis.mod.client.data;

import com.carnis.mod.CarnisMod;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Клиентская копия персонального счётчика; мировая биомасса хранится отдельно. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ClientPlayerBiomassData {
    private static volatile long biomassPoints;

    private ClientPlayerBiomassData() { }

    public static void apply(long points) {
        biomassPoints = Math.max(0L, points);
    }

    public static long get() {
        return biomassPoints;
    }

    public static void reset() {
        biomassPoints = 0L;
    }

    @SubscribeEvent
    public static void onLogout(ClientPlayerNetworkEvent.LoggingOut event) {
        reset();
    }
}
