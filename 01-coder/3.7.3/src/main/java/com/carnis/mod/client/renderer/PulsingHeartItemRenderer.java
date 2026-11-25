package com.carnis.mod.client.renderer;
import com.carnis.mod.client.model.PulsingHeartItemModel;
import com.carnis.mod.item.PulsingHeartItem;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
public final class PulsingHeartItemRenderer extends GeoItemRenderer<PulsingHeartItem> {
    public PulsingHeartItemRenderer() { super(new PulsingHeartItemModel()); addRenderLayer(new OptionalGlowLayer<>(this)); }
}
