package com.carnis.mod.client.renderer;
import com.carnis.mod.client.model.CerebralNexusModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.entity.CerebralNexusEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
public final class CerebralNexusRenderer extends GeoEntityRenderer<CerebralNexusEntity> {
    public CerebralNexusRenderer(EntityRendererProvider.Context context) { super(context, new CerebralNexusModel()); addRenderLayer(new OptionalGlowLayer<>(this)); shadowRadius = 0.6F; }
}
