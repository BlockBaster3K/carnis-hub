package com.carnis.mod.client.model;

import com.carnis.mod.entity.InfectedSpiderEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class InfectedSpiderGeoModel extends GeoModel<InfectedSpiderEntity> {
    @Override public ResourceLocation getModelResource(InfectedSpiderEntity entity) { return new ResourceLocation("carnis", "geo/entity/infected_spider.geo.json"); }
    @Override public ResourceLocation getTextureResource(InfectedSpiderEntity entity) { return new ResourceLocation("carnis", "textures/entity/infected_spider.png"); }
    @Override public ResourceLocation getAnimationResource(InfectedSpiderEntity entity) { return new ResourceLocation("carnis", "animations/entity/infected_spider.animation.json"); }
}
