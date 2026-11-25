package com.carnis.mod.client.renderer;
import com.carnis.mod.client.model.HiveSentinelModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.entity.HiveSentinelEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
public final class HiveSentinelRenderer extends GeoEntityRenderer<HiveSentinelEntity> {
    public HiveSentinelRenderer(EntityRendererProvider.Context context) { super(context, new HiveSentinelModel()); addRenderLayer(new OptionalGlowLayer<>(this)); shadowRadius = 0.6F; }
}
