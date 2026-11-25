package com.carnis.mod.client.renderer.layer;

import com.carnis.mod.init.ModEffects;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;

public final class IncubatingEntityLayer<T extends LivingEntity, M extends EntityModel<T>> extends RenderLayer<T, M> {
    private static final ResourceLocation VEINS = new ResourceLocation("carnis", "textures/entity/incubation_overlay.png");
    private static final ResourceLocation PUSTULE = new ResourceLocation("carnis", "textures/entity/incubation_pustule.png");
    private final ModelPart growth;

    public IncubatingEntityLayer(RenderLayerParent<T, M> parent) {
        super(parent);
        MeshDefinition mesh = new MeshDefinition();
        mesh.getRoot().addOrReplaceChild("growth", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-1.5F, -1.5F, -1.5F, 3, 3, 3), PartPose.ZERO);
        growth = LayerDefinition.create(mesh, 16, 16).bakeRoot().getChild("growth");
    }

    @Override
    public void render(PoseStack pose, MultiBufferSource buffers, int light, T entity,
            float limbSwing, float limbSwingAmount, float partialTick, float age,
            float netHeadYaw, float headPitch) {
        MobEffectInstance effect = entity.getEffect(ModEffects.INCUBATING.get());
        if (effect == null || effect.getAmplifier() < 1 || entity.isInvisible()) return;
        float pulse = 0.5F + 0.5F * Mth.sin(age * 0.22F);
        float alpha = 0.4F + 0.25F * pulse;
        pose.pushPose();
        try {
            pose.scale(1.012F, 1.012F, 1.012F);
            VertexConsumer veins = buffers.getBuffer(RenderType.entityTranslucent(VEINS));
            getParentModel().renderToBuffer(pose, veins, light,
                    LivingEntityRenderer.getOverlayCoords(entity, 0), 1, 1, 1, alpha);
        } finally { pose.popPose(); }
        VertexConsumer vertices = buffers.getBuffer(RenderType.entityCutoutNoCull(PUSTULE));
        if (getParentModel() instanceof HumanoidModel<?> humanoid) {
            attach(pose, vertices, humanoid.head, -0.18F, -0.25F, -0.24F, pulse, light);
            attach(pose, vertices, humanoid.body, 0.15F, 0.32F, -0.14F, pulse, light);
            attach(pose, vertices, humanoid.leftArm, 0.06F, 0.30F, -0.12F, pulse, light);
            attach(pose, vertices, humanoid.rightArm, -0.06F, 0.40F, -0.12F, pulse, light);
            attach(pose, vertices, humanoid.leftLeg, 0.05F, 0.34F, -0.12F, pulse, light);
            attach(pose, vertices, humanoid.rightLeg, -0.05F, 0.40F, -0.12F, pulse, light);
        } else {
            // Non-humanoid vanilla models have different inaccessible part layouts.
            // These two growths follow the rendered body transform, not individual limbs.
            attach(pose, vertices, null, -0.12F, 0.65F, -0.22F, pulse, light);
            attach(pose, vertices, null, 0.15F, 0.85F, 0.16F, pulse, light);
        }
    }

    private void attach(PoseStack pose, VertexConsumer vertices, ModelPart part,
                        float x, float y, float z, float pulse, int light) {
        pose.pushPose();
        try {
            if (part != null) part.translateAndRotate(pose);
            pose.translate(x, y, z);
            float scale = 0.8F + pulse * 0.20F;
            pose.scale(scale, scale, scale);
            growth.render(pose, vertices, light, net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY);
        } finally { pose.popPose(); }
    }
}
