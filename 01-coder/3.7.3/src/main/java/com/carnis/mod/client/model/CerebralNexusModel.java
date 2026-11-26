package com.carnis.mod.client.model;
import com.carnis.mod.entity.CerebralNexusEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class CerebralNexusModel extends GeoModel<CerebralNexusEntity> {
    @Override public ResourceLocation getModelResource(CerebralNexusEntity entity) { return new ResourceLocation("carnis", "geo/entity/cerebral_nexus.geo.json"); }
    @Override public ResourceLocation getTextureResource(CerebralNexusEntity entity) { return new ResourceLocation("carnis", "textures/entity/cerebral_nexus.png"); }
    @Override public ResourceLocation getAnimationResource(CerebralNexusEntity entity) { return new ResourceLocation("carnis", "animations/entity/cerebral_nexus.animation.json"); }
}
