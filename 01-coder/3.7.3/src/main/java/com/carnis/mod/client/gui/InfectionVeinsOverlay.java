package com.carnis.mod.client.gui;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerInfection;
import com.carnis.mod.config.CarnisConfig;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

@OnlyIn(Dist.CLIENT)
public final class InfectionVeinsOverlay implements IGuiOverlay {
    private static final ResourceLocation VEINS_TEXTURE = new ResourceLocation(
            CarnisMod.MOD_ID,
            "textures/misc/vein_overlay.png"
    );

    private static final int TEXTURE_SIZE = 256;
    private static final float HIGH_INFECTION_THRESHOLD = 70.0F;
    private static final double MIN_PULSE_SPEED = 0.055D;
    private static final double MAX_PULSE_SPEED = 0.180D;

    @Override
    public void render(
            ForgeGui gui,
            GuiGraphics guiGraphics,
            float partialTick,
            int screenWidth,
            int screenHeight
    ) {
        if (!CarnisConfig.CLIENT.veinOverlayEnabled.get()) {
            return;
        }

        float infectionLevel = ClientPlayerInfection.getInfectionLevel();

        if (com.carnis.mod.client.data.ClientInfectionData.stage() < 2) {
            return;
        }

        ClientLevel level = gui.getMinecraft().level;

        if (level == null || screenWidth <= 0 || screenHeight <= 0) {
            return;
        }

        float configuredIntensity = CarnisConfig.CLIENT
                .veinOverlayIntensity
                .get()
                .floatValue();

        if (configuredIntensity <= 0.0F) {
            return;
        }

        float normalizedInfection = Mth.clamp(
                infectionLevel / 100.0F,
                0.0F,
                1.0F
        );
        float baseAlpha = normalizedInfection;
        double speed = Mth.lerp(
                normalizedInfection,
                MIN_PULSE_SPEED,
                MAX_PULSE_SPEED
        );
        double gameTime = level.getGameTime() + partialTick;
        float pulse = 0.72F + 0.28F * (float) (
                (Math.sin(gameTime * speed) + 1.0D) * 0.5D
        );
        float overlayAlpha = Mth.clamp(
                baseAlpha * pulse * configuredIntensity,
                0.0F,
                1.0F
        );

        gui.setupOverlayRenderState(true, false);
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();

        try {
            RenderSystem.setShaderColor(
                    1.0F,
                    0.52F,
                    0.60F,
                    overlayAlpha
            );
            blitFullScreen(guiGraphics, screenWidth, screenHeight);

            if (infectionLevel >= HIGH_INFECTION_THRESHOLD) {
                float severeInfection = Mth.clamp(
                        (infectionLevel - HIGH_INFECTION_THRESHOLD)
                                / (100.0F - HIGH_INFECTION_THRESHOLD),
                        0.0F,
                        1.0F
                );
                float darkeningAlpha = Mth.clamp(
                        configuredIntensity
                                * pulse
                                * (0.08F + 0.42F * severeInfection),
                        0.0F,
                        1.0F
                );

                RenderSystem.setShaderColor(
                        0.28F,
                        0.018F,
                        0.032F,
                        darkeningAlpha
                );
                blitFullScreen(guiGraphics, screenWidth, screenHeight);
            }
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            int stage = com.carnis.mod.client.data.ClientInfectionData.stage();
            if (stage >= 3 && Math.floorMod(level.getGameTime(), 120L) < 5L) {
                int alpha = (int) (configuredIntensity * 24.0F);
                guiGraphics.fill(0, 0, screenWidth, screenHeight, (alpha << 24) | 0x356D42);
            }
            if (infectionLevel >= 100.0F) {
                int alpha = (int) (configuredIntensity * 45.0F * pulse);
                guiGraphics.fill(0, 0, screenWidth, screenHeight, (alpha << 24) | 0x110408);
            }
        } finally {
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            RenderSystem.defaultBlendFunc();
            RenderSystem.disableBlend();
            RenderSystem.enableDepthTest();
        }
    }

    private static void blitFullScreen(
            GuiGraphics guiGraphics,
            int screenWidth,
            int screenHeight
    ) {
        guiGraphics.blit(
                VEINS_TEXTURE,
                0,
                0,
                screenWidth,
                screenHeight,
                0.0F,
                0.0F,
                TEXTURE_SIZE,
                TEXTURE_SIZE,
                TEXTURE_SIZE,
                TEXTURE_SIZE
        );
    }
}
