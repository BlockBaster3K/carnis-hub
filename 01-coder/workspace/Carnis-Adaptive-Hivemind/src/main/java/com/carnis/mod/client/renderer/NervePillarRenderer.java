package com.carnis.mod.client.renderer;

import com.carnis.mod.block.entity.NervePillarBlockEntity;
import com.carnis.mod.client.model.NervePillarModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import software.bernie.geckolib.renderer.GeoBlockRenderer;

public final class NervePillarRenderer extends GeoBlockRenderer<NervePillarBlockEntity> {
    public NervePillarRenderer(BlockEntityRendererProvider.Context context) {
        super(new NervePillarModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
