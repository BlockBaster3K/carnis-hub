package com.carnis.mod.client.renderer.layer;

import com.carnis.mod.CarnisMod;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

import java.util.HashMap;
import java.util.Map;

/** Renders a glow pass only when the optional companion texture is available. */
public final class OptionalGlowLayer<T extends GeoAnimatable> extends AutoGlowingGeoLayer<T> {
    private static final Map<ResourceLocation, Boolean> RESOURCE_CACHE = new HashMap<>();
    private static ResourceManager cachedResourceManager;
    private static final Map<ResourceLocation, Long> WARNING_TIMES = new HashMap<>();
    private static final long WARNING_COOLDOWN_MS = 60_000L;

    public OptionalGlowLayer(GeoRenderer<T> renderer) {
        super(renderer);
    }

    @Override
    public void render(PoseStack poseStack, T animatable, BakedGeoModel model, RenderType renderType,
                       MultiBufferSource buffers, VertexConsumer buffer, float partialTick,
                       int packedLight, int packedOverlay) {
        ResourceLocation texture = getTextureResource(animatable);
        String path = texture.getPath();
        if (!path.endsWith(".png")) return;

        ResourceLocation glowmask = new ResourceLocation(texture.getNamespace(),
                path.substring(0, path.length() - 4) + "_glowmask.png");
        ResourceManager manager = Minecraft.getInstance().getResourceManager();
        if (cachedResourceManager != manager) {
            RESOURCE_CACHE.clear();
            WARNING_TIMES.clear();
            cachedResourceManager = manager;
        }
        Boolean present = RESOURCE_CACHE.get(glowmask);
        if (present == null) {
            present = manager.getResource(glowmask).isPresent();
            RESOURCE_CACHE.put(glowmask, present);
        }
        if (!present) {
            long now = Util.getMillis();
            long last = WARNING_TIMES.getOrDefault(glowmask, Long.MIN_VALUE / 2);
            if (now >= last && now - last >= WARNING_COOLDOWN_MS) {
                CarnisMod.LOGGER.warn("Optional glowmask is missing: {}", glowmask);
                WARNING_TIMES.put(glowmask, now);
            }
            return;
        }

        poseStack.pushPose();
        poseStack.scale(1.002F, 1.002F, 1.002F);
        try {
            super.render(poseStack, animatable, model, renderType, buffers, buffer,
                    partialTick, packedLight, packedOverlay);
        } finally {
            poseStack.popPose();
        }
    }
}
