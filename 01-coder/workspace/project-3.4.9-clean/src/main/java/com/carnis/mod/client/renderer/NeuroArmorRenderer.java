package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.NeuroArmorModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.item.armor.NeuroArmorItem;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoArmorRenderer;

import javax.annotation.Nullable;

public final class NeuroArmorRenderer extends GeoArmorRenderer<NeuroArmorItem> {
    public NeuroArmorRenderer() {
        super(new NeuroArmorModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }

    @Nullable @Override public GeoBone getHeadBone() { return getGeoModel().getBone("head").orElse(null); }
    @Nullable @Override public GeoBone getBodyBone() { return getGeoModel().getBone("body").orElse(null); }
    @Nullable @Override public GeoBone getRightArmBone() { return getGeoModel().getBone("right_arm").orElse(null); }
    @Nullable @Override public GeoBone getLeftArmBone() { return getGeoModel().getBone("left_arm").orElse(null); }
    @Nullable @Override public GeoBone getRightLegBone() { return getGeoModel().getBone("right_leg").orElse(null); }
    @Nullable @Override public GeoBone getLeftLegBone() { return getGeoModel().getBone("left_leg").orElse(null); }
    @Nullable @Override public GeoBone getRightBootBone() { return getGeoModel().getBone("right_boot").orElse(null); }
    @Nullable @Override public GeoBone getLeftBootBone() { return getGeoModel().getBone("left_boot").orElse(null); }
}
