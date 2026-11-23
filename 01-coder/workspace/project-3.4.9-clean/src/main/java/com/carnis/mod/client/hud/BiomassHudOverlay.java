package com.carnis.mod.client.hud;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerBiomassData;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.CustomizeGuiOverlayEvent;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Персональный счётчик биомассы, независимый от мирового счётчика Улья. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class BiomassHudOverlay implements IGuiOverlay {
    private static final ResourceLocation ICON = new ResourceLocation(CarnisMod.MOD_ID, "textures/gui/biomass_icon.png");
    private static final int ICON_SIZE = 16;
    private static final int TOP_MARGIN = 8;
    private static int bossBottom = TOP_MARGIN;

    /** Начало отрисовки шкал сбрасывает измерение для текущего кадра. */
    @SubscribeEvent(priority = EventPriority.LOWEST, receiveCanceled = true)
    public static void onBossOverlayPre(RenderGuiOverlayEvent.Pre event) {
        if (event.getOverlay().id().equals(VanillaGuiOverlay.BOSS_EVENT_PROGRESS.id())) {
            bossBottom = TOP_MARGIN;
        }
    }

    /** Учитываем положение и интервал каждой реально обрабатываемой шкалы. */
    @SubscribeEvent(priority = EventPriority.LOWEST, receiveCanceled = true)
    public static void onBossBar(CustomizeGuiOverlayEvent.BossEventProgress event) {
        if (!event.isCanceled()) {
            bossBottom = Math.max(bossBottom, event.getY() + event.getIncrement());
        }
    }

    @Override
    public void render(ForgeGui gui, GuiGraphics graphics, float partialTick, int screenWidth, int screenHeight) {
        Minecraft minecraft = gui.getMinecraft();
        if (minecraft.player == null || minecraft.level == null || minecraft.options.hideGui) return;

        String label = "§c❤ Биомасса: §f" + ClientPlayerBiomassData.get();
        int textWidth = minecraft.font.width(label);
        int contentWidth = ICON_SIZE + 4 + textWidth;
        int x = Math.max(0, Math.min(screenWidth - 120, screenWidth - contentWidth - 4));
        int y = Math.max(TOP_MARGIN, bossBottom);

        gui.setupOverlayRenderState(true, false);
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        try {
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            graphics.blit(ICON, x, y, 0, 0, ICON_SIZE, ICON_SIZE, ICON_SIZE, ICON_SIZE);
            graphics.drawString(minecraft.font, label, x + ICON_SIZE + 4, y + 4, 0xFFFFFFFF, true);
        } finally {
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            RenderSystem.defaultBlendFunc();
            RenderSystem.disableBlend();
            RenderSystem.enableDepthTest();
        }
    }
}
