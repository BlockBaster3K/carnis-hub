package com.carnis.mod.client.renderer;

import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.client.model.InfectedCreeperGeoModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class InfectedCreeperRenderer extends GeoEntityRenderer<InfectedCreeperEntity> {
    public InfectedCreeperRenderer(EntityRendererProvider.Context context) {
        super(context, new InfectedCreeperGeoModel());
        addRenderLayer(new com.carnis.mod.client.renderer.layer.OptionalGlowLayer<>(this));
        this.shadowRadius = .45F;
    }
}
