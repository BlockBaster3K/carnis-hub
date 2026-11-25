package com.carnis.mod.client.renderer;

import com.carnis.mod.entity.InfectedSpiderEntity;
import com.carnis.mod.client.model.InfectedSpiderGeoModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class InfectedSpiderRenderer extends GeoEntityRenderer<InfectedSpiderEntity> {
    public InfectedSpiderRenderer(EntityRendererProvider.Context context) {
        super(context, new InfectedSpiderGeoModel());
        addRenderLayer(new software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer<>(this));
        this.shadowRadius = .65F;
    }
}
