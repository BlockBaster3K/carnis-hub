package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.FleshAmalgamModel;
import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;

@OnlyIn(Dist.CLIENT)
public final class FleshAmalgamRenderer
        extends GeoEntityRenderer<FleshAmalgamEntity> {
    public FleshAmalgamRenderer(EntityRendererProvider.Context context) {
        super(context, new FleshAmalgamModel());
        this.shadowRadius = 0.85F;
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
