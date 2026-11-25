package com.carnis.mod.client.gui;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientInfectionData;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.item.NeuroWeave;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.List;

/** Локальные кратковременные изображения глаз; не создаёт сущностей в мире. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PhantomEyesOverlay implements IGuiOverlay {
    private static final ResourceLocation TEXTURE = new ResourceLocation(CarnisMod.MOD_ID,
            "textures/hallucination/phantom_eyes.png");
    private static final int TEXTURE_SIZE = 8;
    private static final int FADE_TICKS = 5;
    private static final int MAX_FLASHES = 2;
    private static final List<Flash> FLASHES = new ArrayList<>(MAX_FLASHES);
    private static ClientLevel activeLevel;
    private static LocalPlayer activePlayer;
    private static int delay = -1;
    private static int lastStage;

    private static final class Flash {
        private final float x;
        private final float y;
        private final int duration;
        private int age;

        private Flash(float x, float y, int duration) {
            this.x = x;
            this.y = y;
            this.duration = duration;
        }
    }

    private static boolean eligible(Minecraft mc, LocalPlayer player) {
        return mc.level != null && player != null && player.isAlive() && !player.isSpectator()
                && CarnisConfig.CLIENT.phantomEyesEnabled.get()
                && ClientInfectionData.points() >= 25 && ClientInfectionData.stage() >= 2
                && !NeuroResonatorHelmetItem.isEquipped(player) && NeuroWeave.protectedPieces(player) < 4;
    }

    private static void reset() {
        FLASHES.clear();
        activeLevel = null;
        activePlayer = null;
        delay = -1;
        lastStage = 0;
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (!eligible(mc, player)) {
            reset();
            return;
        }
        if (activeLevel != mc.level || activePlayer != player) {
            reset();
            activeLevel = mc.level;
            activePlayer = player;
        }
        if (mc.isPaused()) return;

        int stage = Mth.clamp(ClientInfectionData.stage(), 2, 4);
        RandomSource random = player.getRandom();
        FLASHES.removeIf(flash -> ++flash.age >= flash.duration);
        if (lastStage != stage) {
            lastStage = stage;
            delay = nextDelay(stage, random);
            return;
        }
        if (--delay > 0) return;
        int count = 1 + random.nextInt(2);
        for (int i = 0; i < count && FLASHES.size() < MAX_FLASHES; i++) {
            FLASHES.add(createFlash(random));
        }
        delay = nextDelay(stage, random);
    }

    private static int nextDelay(int stage, RandomSource random) {
        return switch (stage) {
            case 2 -> random.nextIntBetweenInclusive(600, 1800);
            case 3 -> random.nextIntBetweenInclusive(300, 900);
            default -> random.nextIntBetweenInclusive(100, 300);
        };
    }

    private static Flash createFlash(RandomSource random) {
        float along = random.nextFloat();
        float edge = random.nextFloat() * 0.15F;
        int side = random.nextInt(4);
        float x = side == 0 ? edge : side == 1 ? 1.0F - edge : along;
        float y = side == 2 ? edge : side == 3 ? 1.0F - edge : along;
        return new Flash(x, y, random.nextIntBetweenInclusive(20, 60));
    }

    @Override
    public void render(ForgeGui gui, GuiGraphics graphics, float partialTick, int screenWidth, int screenHeight) {
        Minecraft mc = gui.getMinecraft();
        if (!eligible(mc, mc.player) || activeLevel != mc.level || activePlayer != mc.player
                || mc.options.hideGui || screenWidth <= 0 || screenHeight <= 0 || FLASHES.isEmpty()) return;

        float intensity = CarnisConfig.CLIENT.phantomEyesIntensity.get().floatValue();
        int size = Math.max(1, Math.min(Math.min(screenWidth, screenHeight), Math.round(48.0F * intensity)));
        int stage = Mth.clamp(ClientInfectionData.stage(), 2, 4);
        int color = stage == 2 ? 0x00AA00 : stage == 3 ? 0x00FF44 : 0xFF2200;
        float red = ((color >> 16) & 255) / 255.0F;
        float green = ((color >> 8) & 255) / 255.0F;
        float blue = (color & 255) / 255.0F;

        gui.setupOverlayRenderState(true, false);
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        try {
            for (Flash flash : FLASHES) {
                float elapsed = flash.age + partialTick;
                float fadeIn = Mth.clamp(elapsed / FADE_TICKS, 0.0F, 1.0F);
                float fadeOut = Mth.clamp((flash.duration - elapsed) / FADE_TICKS, 0.0F, 1.0F);
                float alpha = Mth.clamp(0.7F * intensity * Math.min(fadeIn, fadeOut), 0.0F, 1.0F);
                int x = Mth.clamp(Math.round(flash.x * screenWidth - size / 2.0F), 0, screenWidth - size);
                int y = Mth.clamp(Math.round(flash.y * screenHeight - size / 2.0F), 0, screenHeight - size);
                RenderSystem.setShaderColor(red, green, blue, alpha);
                graphics.blit(TEXTURE, x, y, size, size, 0.0F, 0.0F,
                        TEXTURE_SIZE, TEXTURE_SIZE, TEXTURE_SIZE, TEXTURE_SIZE);
            }
        } finally {
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            RenderSystem.defaultBlendFunc();
            RenderSystem.disableBlend();
            RenderSystem.enableDepthTest();
        }
    }
}
