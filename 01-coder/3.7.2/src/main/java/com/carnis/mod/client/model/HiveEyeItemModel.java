package com.carnis.mod.client.model;

import com.carnis.mod.item.HiveEyeItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class HiveEyeItemModel extends GeoModel<HiveEyeItem> {
    @Override
    public ResourceLocation getModelResource(HiveEyeItem eye) {
        return new ResourceLocation("carnis", "geo/block/hive_eye.geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(HiveEyeItem eye) {
        return new ResourceLocation("carnis", "textures/block/hive_eye.png");
    }

    @Override
    public ResourceLocation getAnimationResource(HiveEyeItem eye) {
        return new ResourceLocation("carnis", "animations/block/hive_eye.animation.json");
    }
}
