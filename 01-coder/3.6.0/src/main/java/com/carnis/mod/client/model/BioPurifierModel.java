package com.carnis.mod.client.model;

import com.carnis.mod.item.BioPurifierItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class BioPurifierModel extends GeoModel<BioPurifierItem> {
    @Override public ResourceLocation getModelResource(BioPurifierItem item) {
        return new ResourceLocation("carnis", "geo/item/bio_purifier.geo.json");
    }
    @Override public ResourceLocation getTextureResource(BioPurifierItem item) {
        return new ResourceLocation("carnis", "textures/item/bio_purifier.png");
    }
    @Override public ResourceLocation getAnimationResource(BioPurifierItem item) {
        return new ResourceLocation("carnis", "animations/item/bio_purifier.animation.json");
    }
}
