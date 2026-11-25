package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerInfection;
import com.carnis.mod.config.CarnisConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.util.Mth;
import net.minecraft.world.level.material.FogType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@OnlyIn(Dist.CLIENT)
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisFogRenderer {
    private static final float FOG_RED = 0.32F;
    private static final float FOG_GREEN = 0.04F;
    private static final float FOG_BLUE = 0.06F;
    private static final float SMOOTHING_PER_TICK = 0.10F;
    private static final float DENSITY_THRESHOLD = 0.50F;
    private static final float FAR_DISTANCE_LOW = 24.0F;
    private static final float FAR_DISTANCE_HIGH = 12.0F;
    private static float previousInfection;
    private static float smoothedInfection;

    private CarnisFogRenderer() {
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.player == null || minecraft.level == null) {
            previousInfection = 0.0F;
            smoothedInfection = 0.0F;
            return;
        }
        if (com.carnis.mod.client.data.ClientInfectionData.stage() < 3) {
            previousInfection = 0.0F;
            smoothedInfection = 0.0F;
            return;
        }
        float infection = ClientPlayerInfection.getInfectionLevel();
        float target = Float.isFinite(infection)
                ? Mth.clamp(infection / 100.0F, 0.0F, 1.0F)
                : 0.0F;
        previousInfection = smoothedInfection;
        smoothedInfection = Mth.lerp(SMOOTHING_PER_TICK, smoothedInfection, target);
    }

    @SubscribeEvent
    public static void onLogout(ClientPlayerNetworkEvent.LoggingOut event) {
        previousInfection = 0.0F;
        smoothedInfection = 0.0F;
        ClientPlayerInfection.reset();
    }

    private static float infectionForFrame(double partialTick) {
        float partial = Mth.clamp((float) partialTick, 0.0F, 1.0F);
        return Mth.lerp(partial, previousInfection, smoothedInfection);
    }

    @SubscribeEvent
    public static void onFogColor(ViewportEvent.ComputeFogColor event) {
        Minecraft minecraft = Minecraft.getInstance();
        if (!CarnisConfig.CLIENT.atmosphericFogEnabled.get()
                || minecraft.player == null || minecraft.level == null
                || event.getCamera().getFluidInCamera() != FogType.NONE) {
            return;
        }
        float strength = infectionForFrame(event.getPartialTick());
        if (strength <= 0.0F) {
            return;
        }
        event.setRed(Mth.lerp(strength, event.getRed(), FOG_RED));
        event.setGreen(Mth.lerp(strength, event.getGreen(), FOG_GREEN));
        event.setBlue(Mth.lerp(strength, event.getBlue(), FOG_BLUE));
    }

    @SubscribeEvent
    public static void onRenderFog(ViewportEvent.RenderFog event) {
        Minecraft minecraft = Minecraft.getInstance();
        if (!CarnisConfig.CLIENT.atmosphericFogEnabled.get()
                || minecraft.player == null || minecraft.level == null
                || event.getType() != FogType.NONE
                || event.getMode() != FogRenderer.FogMode.FOG_TERRAIN) {
            return;
        }
        float infection = infectionForFrame(event.getPartialTick());
        float density = Mth.clamp(
                (infection - DENSITY_THRESHOLD) / (1.0F - DENSITY_THRESHOLD),
                0.0F, 1.0F
        );
        if (density <= 0.0F) {
            return;
        }
        float originalEnd = event.getFarPlaneDistance();
        float originalStart = event.getNearPlaneDistance();
        float desiredEnd = Mth.lerp(density, FAR_DISTANCE_LOW, FAR_DISTANCE_HIGH);
        float end = Mth.lerp(density, originalEnd, Math.min(originalEnd, desiredEnd));
        float start = Mth.lerp(density, originalStart, Math.min(originalStart, end * 0.25F));
        if (end < originalEnd || start < originalStart) {
            event.setFarPlaneDistance(end);
            event.setNearPlaneDistance(Math.min(start, end));
            event.setCanceled(true);
        }
    }
}
