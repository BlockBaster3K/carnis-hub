package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.InfectedSkeletonGeoModel;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class InfectedSkeletonRenderer extends GeoEntityRenderer<InfectedSkeletonEntity> {
    public InfectedSkeletonRenderer(EntityRendererProvider.Context context) {
        super(context, new InfectedSkeletonGeoModel());
        addRenderLayer(new com.carnis.mod.client.renderer.layer.OptionalGlowLayer<>(this));
        this.shadowRadius = 0.45F;
    }
}
