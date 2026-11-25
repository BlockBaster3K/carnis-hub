package com.carnis.mod.client.model;
import com.carnis.mod.item.armor.NeuroArmorItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class NeuroArmorModel extends GeoModel<NeuroArmorItem> {
    @Override public ResourceLocation getModelResource(NeuroArmorItem item) { return new ResourceLocation("carnis", "geo/item/neuro_armor.geo.json"); }
    @Override public ResourceLocation getTextureResource(NeuroArmorItem item) { return new ResourceLocation("carnis", "textures/armor/neuro_armor.png"); }
    @Override public ResourceLocation getAnimationResource(NeuroArmorItem item) { return new ResourceLocation("carnis", "animations/armor/neuro_armor.animation.json"); }
}
