package com.carnis.mod.client.model;
import com.carnis.mod.item.PulsingHeartItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class PulsingHeartItemModel extends GeoModel<PulsingHeartItem> {
    @Override public ResourceLocation getModelResource(PulsingHeartItem item) { return new ResourceLocation("carnis", "geo/block/pulsing_heart.geo.json"); }
    @Override public ResourceLocation getTextureResource(PulsingHeartItem item) { return new ResourceLocation("carnis", "textures/block/pulsing_heart.png"); }
    @Override public ResourceLocation getAnimationResource(PulsingHeartItem item) { return new ResourceLocation("carnis", "animations/block/pulsing_heart.animation.json"); }
}
