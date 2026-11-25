package com.carnis.mod.client.model;

import com.carnis.mod.entity.InfectedCreeperEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class InfectedCreeperGeoModel extends GeoModel<InfectedCreeperEntity> {
    @Override public ResourceLocation getModelResource(InfectedCreeperEntity entity) { return new ResourceLocation("carnis", "geo/entity/infected_creeper.geo.json"); }
    @Override public ResourceLocation getTextureResource(InfectedCreeperEntity entity) { return new ResourceLocation("carnis", "textures/entity/infected_creeper.png"); }
    @Override public ResourceLocation getAnimationResource(InfectedCreeperEntity entity) { return new ResourceLocation("carnis", "animations/entity/infected_creeper.animation.json"); }
}
