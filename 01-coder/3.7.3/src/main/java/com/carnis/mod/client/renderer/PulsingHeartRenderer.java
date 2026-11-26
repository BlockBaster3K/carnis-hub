package com.carnis.mod.client.renderer;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.client.model.PulsingHeartModel;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import software.bernie.geckolib.renderer.GeoBlockRenderer;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;

@OnlyIn(Dist.CLIENT)
public final class PulsingHeartRenderer
        extends GeoBlockRenderer<PulsingHeartBlockEntity> {
    public PulsingHeartRenderer(BlockEntityRendererProvider.Context context) {
        super(new PulsingHeartModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
