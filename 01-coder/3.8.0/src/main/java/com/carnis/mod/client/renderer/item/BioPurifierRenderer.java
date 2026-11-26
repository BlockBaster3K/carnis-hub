package com.carnis.mod.client.renderer.item;

import com.carnis.mod.client.model.BioPurifierModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.item.BioPurifierItem;
import software.bernie.geckolib.renderer.GeoItemRenderer;

public final class BioPurifierRenderer extends GeoItemRenderer<BioPurifierItem> {
    public BioPurifierRenderer() {
        super(new BioPurifierModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
