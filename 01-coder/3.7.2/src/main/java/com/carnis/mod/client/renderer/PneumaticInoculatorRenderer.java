package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.PneumaticInoculatorModel;
import com.carnis.mod.item.PneumaticInoculatorItem;
import software.bernie.geckolib.renderer.GeoItemRenderer;

public final class PneumaticInoculatorRenderer extends GeoItemRenderer<PneumaticInoculatorItem> {
    public PneumaticInoculatorRenderer() {
        super(new PneumaticInoculatorModel());
    }
}
