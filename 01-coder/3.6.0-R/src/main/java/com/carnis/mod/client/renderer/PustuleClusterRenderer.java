package com.carnis.mod.client.renderer;

import com.carnis.mod.block.entity.PustuleClusterBlockEntity;
import com.carnis.mod.client.model.PustuleClusterModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import software.bernie.geckolib.renderer.GeoBlockRenderer;

public final class PustuleClusterRenderer extends GeoBlockRenderer<PustuleClusterBlockEntity> {
    public PustuleClusterRenderer(BlockEntityRendererProvider.Context context) {
        super(new PustuleClusterModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
