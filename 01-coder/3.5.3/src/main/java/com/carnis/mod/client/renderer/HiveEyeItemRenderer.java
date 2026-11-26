package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.HiveEyeItemModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.item.HiveEyeItem;
import software.bernie.geckolib.renderer.GeoItemRenderer;

public final class HiveEyeItemRenderer extends GeoItemRenderer<HiveEyeItem> {
    public HiveEyeItemRenderer() {
        super(new HiveEyeItemModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
