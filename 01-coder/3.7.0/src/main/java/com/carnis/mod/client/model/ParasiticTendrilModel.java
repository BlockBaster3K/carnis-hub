package com.carnis.mod.client.model;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class ParasiticTendrilModel extends GeoModel<ParasiticTendrilEntity> {
    @Override public ResourceLocation getModelResource(ParasiticTendrilEntity e) { return new ResourceLocation("carnis", "geo/entity/parasitic_tendril.geo.json"); }
    @Override public ResourceLocation getTextureResource(ParasiticTendrilEntity e) { return new ResourceLocation("carnis", "textures/entity/parasitic_tendril.png"); }
    @Override public ResourceLocation getAnimationResource(ParasiticTendrilEntity e) { return new ResourceLocation("carnis", "animations/entity/parasitic_tendril.animation.json"); }
}
