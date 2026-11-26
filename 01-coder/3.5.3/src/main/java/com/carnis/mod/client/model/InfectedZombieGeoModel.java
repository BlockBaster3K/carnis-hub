package com.carnis.mod.client.model;

import com.carnis.mod.entity.InfectedZombieEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class InfectedZombieGeoModel extends GeoModel<InfectedZombieEntity> {
    @Override public ResourceLocation getModelResource(InfectedZombieEntity entity) { return new ResourceLocation("carnis", "geo/entity/infected_zombie.geo.json"); }
    @Override public ResourceLocation getTextureResource(InfectedZombieEntity entity) { return new ResourceLocation("carnis", "textures/entity/infected_zombie.png"); }
    @Override public ResourceLocation getAnimationResource(InfectedZombieEntity entity) { return new ResourceLocation("carnis", "animations/entity/infected_zombie.animation.json"); }
}
