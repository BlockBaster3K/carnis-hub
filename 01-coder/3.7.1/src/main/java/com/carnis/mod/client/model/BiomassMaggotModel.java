package com.carnis.mod.client.model;

import com.carnis.mod.entity.BiomassMaggotEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class BiomassMaggotModel extends GeoModel<BiomassMaggotEntity> {
    @Override public ResourceLocation getModelResource(BiomassMaggotEntity entity) {
        return new ResourceLocation("carnis", "geo/entity/biomass_maggot.geo.json");
    }
    @Override public ResourceLocation getTextureResource(BiomassMaggotEntity entity) {
        return new ResourceLocation("carnis", "textures/entity/biomass_maggot.png");
    }
    @Override public ResourceLocation getAnimationResource(BiomassMaggotEntity entity) {
        return new ResourceLocation("carnis", "animations/entity/biomass_maggot.animation.json");
    }
}
