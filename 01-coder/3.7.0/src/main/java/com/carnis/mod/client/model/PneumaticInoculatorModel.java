package com.carnis.mod.client.model;
import com.carnis.mod.item.PneumaticInoculatorItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class PneumaticInoculatorModel extends GeoModel<PneumaticInoculatorItem> {
 @Override public ResourceLocation getModelResource(PneumaticInoculatorItem a) { return new ResourceLocation("carnis", "geo/item/pneumatic_inoculator.geo.json"); }
 @Override public ResourceLocation getTextureResource(PneumaticInoculatorItem a) { return new ResourceLocation("carnis", "textures/item/pneumatic_inoculator_geo.png"); }
 @Override public ResourceLocation getAnimationResource(PneumaticInoculatorItem a) { return new ResourceLocation("carnis", "animations/item/pneumatic_inoculator.animation.json"); }
}
