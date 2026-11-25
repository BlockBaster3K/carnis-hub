package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerInfection;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@OnlyIn(Dist.CLIENT)
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NecroticCameraEffects {
    private NecroticCameraEffects() {
    }

    public static void onCameraAngles(ViewportEvent.ComputeCameraAngles event) {
        LocalPlayer player = Minecraft.getInstance().player;
        if (player == null || !player.isAlive() || player.isSpectator()
                || ClientPlayerInfection.getInfectionLevel() < 100.0F) {
            return;
        }
        double phase = (player.tickCount % 20) + event.getPartialTick();
        if (phase < 4.0D) {
            float roll = (float) (Math.sin(phase * 4.0D) * (1.0D - phase / 4.0D) * 1.5D);
            event.setRoll(event.getRoll() + roll);
        }
    }
}
