package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.BiomassMaggotModel;
import com.carnis.mod.entity.BiomassMaggotEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class BiomassMaggotRenderer extends GeoEntityRenderer<BiomassMaggotEntity> {
    public BiomassMaggotRenderer(EntityRendererProvider.Context context) {
        super(context, new BiomassMaggotModel());
        this.shadowRadius = 0.2F;
    }
}
