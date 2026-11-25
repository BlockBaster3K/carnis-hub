package com.carnis.mod.client.model;

import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import software.bernie.geckolib.model.GeoModel;

@OnlyIn(Dist.CLIENT)
public final class FleshAmalgamModel extends GeoModel<FleshAmalgamEntity> {
    @Override public ResourceLocation getModelResource(FleshAmalgamEntity entity) {
        return new ResourceLocation("carnis", "geo/entity/flesh_amalgam.geo.json");
    }
    @Override public ResourceLocation getTextureResource(FleshAmalgamEntity entity) {
        return new ResourceLocation("carnis", "textures/entity/flesh_amalgam.png");
    }
    @Override public ResourceLocation getAnimationResource(FleshAmalgamEntity entity) {
        return new ResourceLocation("carnis", "animations/entity/flesh_amalgam.animation.json");
    }
}
