package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.InfectedZombieGeoModel;
import com.carnis.mod.entity.InfectedZombieEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;

/** The model resolves the geometry, texture, and animation resources. */
public final class InfectedZombieRenderer extends GeoEntityRenderer<InfectedZombieEntity> {
    public InfectedZombieRenderer(EntityRendererProvider.Context context) {
        super(context, new InfectedZombieGeoModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
        this.shadowRadius = 0.45F;
    }
}
