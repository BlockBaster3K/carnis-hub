package com.carnis.mod.client.model;
import com.carnis.mod.entity.HiveSentinelEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class HiveSentinelModel extends GeoModel<HiveSentinelEntity> {
    @Override public ResourceLocation getModelResource(HiveSentinelEntity entity) { return new ResourceLocation("carnis", "geo/entity/hive_sentinel.geo.json"); }
    @Override public ResourceLocation getTextureResource(HiveSentinelEntity entity) { return new ResourceLocation("carnis", "textures/entity/hive_sentinel.png"); }
    @Override public ResourceLocation getAnimationResource(HiveSentinelEntity entity) { return new ResourceLocation("carnis", "animations/entity/hive_sentinel.animation.json"); }
}
