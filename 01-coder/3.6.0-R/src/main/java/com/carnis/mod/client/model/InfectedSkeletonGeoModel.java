package com.carnis.mod.client.model;

import com.carnis.mod.entity.InfectedSkeletonEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class InfectedSkeletonGeoModel extends GeoModel<InfectedSkeletonEntity> {
    @Override public ResourceLocation getModelResource(InfectedSkeletonEntity entity) { return new ResourceLocation("carnis", "geo/entity/infected_skeleton.geo.json"); }
    @Override public ResourceLocation getTextureResource(InfectedSkeletonEntity entity) { return new ResourceLocation("carnis", "textures/entity/infected_skeleton.png"); }
    @Override public ResourceLocation getAnimationResource(InfectedSkeletonEntity entity) { return new ResourceLocation("carnis", "animations/entity/infected_skeleton.animation.json"); }
}
