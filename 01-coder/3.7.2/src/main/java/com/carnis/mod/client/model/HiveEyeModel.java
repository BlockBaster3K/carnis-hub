package com.carnis.mod.client.model;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.HiveEyeBlockEntity;
import com.carnis.mod.client.renderer.HiveEyeRenderer;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;

public final class HiveEyeModel extends GeoModel<HiveEyeBlockEntity> {
    @Override
    public void setCustomAnimations(HiveEyeBlockEntity eye, long instanceId, AnimationState<HiveEyeBlockEntity> state) {
        super.setCustomAnimations(eye, instanceId, state);
        CoreGeoBone iris = getAnimationProcessor().getBone("iris");
        CoreGeoBone pupil = getAnimationProcessor().getBone("pupil");
        if (iris != null && pupil != null) {
            HiveEyeRenderer.applyEyePose(eye, iris, pupil, (float) state.getPartialTick());
        }
    }

    @Override
    public ResourceLocation getModelResource(HiveEyeBlockEntity object) {
        return new ResourceLocation(CarnisMod.MOD_ID, "geo/block/hive_eye.geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(HiveEyeBlockEntity object) {
        return new ResourceLocation(CarnisMod.MOD_ID, "textures/block/hive_eye.png");
    }

    @Override
    public ResourceLocation getAnimationResource(HiveEyeBlockEntity object) {
        return new ResourceLocation(CarnisMod.MOD_ID, "animations/block/hive_eye.animation.json");
    }
}
