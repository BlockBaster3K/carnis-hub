package com.carnis.mod.client.renderer;

import com.carnis.mod.block.entity.HiveEyeBlockEntity;
import com.carnis.mod.client.model.HiveEyeModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.renderer.GeoBlockRenderer;

public final class HiveEyeRenderer extends GeoBlockRenderer<HiveEyeBlockEntity> {
    public HiveEyeRenderer(BlockEntityRendererProvider.Context context) {
        super(new HiveEyeModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }

    public static void applyEyePose(HiveEyeBlockEntity eye, CoreGeoBone iris, CoreGeoBone pupil, float partialTick) {
        if (eye == null || iris == null || pupil == null) return;
        float yaw = eye.trackingYaw(partialTick);
        float pitch = eye.trackingPitch(partialTick);
        iris.setRotY(-yaw);
        iris.setRotX(-pitch);
        iris.setScaleX(eye.irisPulseScale(partialTick));
        iris.setScaleY(eye.irisPulseScale(partialTick));
        pupil.setRotY(0.0F);
        pupil.setRotX(0.0F);
        float distanceScale = eye.hasTrackingTarget() ? eye.pupilDistanceScale(partialTick) : 1.0F;
        pupil.setScaleX(distanceScale);
        pupil.setScaleY(distanceScale * eye.pupilScaleY(partialTick));
    }
}
