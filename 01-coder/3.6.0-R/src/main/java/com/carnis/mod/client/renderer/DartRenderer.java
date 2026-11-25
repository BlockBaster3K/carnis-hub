package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.PurificationDartEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public final class DartRenderer<T extends AbstractArrow> extends EntityRenderer<T> {
    private static final ResourceLocation TEXTURE =
            new ResourceLocation(CarnisMod.MOD_ID, "textures/entity/dart.png");
    private static final int STEEL = 0;
    private static final int DARK_STEEL = 1;
    private static final int BRASS = 2;
    private static final int VIRAL = 3;
    private static final int VIRAL_ACCENT = 4;
    private static final int SERUM = 5;
    private static final int GLASS = 6;
    private static final int GLASS_RIM = 7;

    public DartRenderer(EntityRendererProvider.Context context) {
        super(context);
        shadowRadius = 0.0F;
    }

    @Override
    public void render(T dart, float entityYaw, float partialTick, PoseStack poseStack,
                       MultiBufferSource buffers, int packedLight) {
        poseStack.pushPose();
        poseStack.mulPose(Axis.YP.rotationDegrees(Mth.rotLerp(partialTick, dart.yRotO, dart.getYRot()) - 90.0F));
        poseStack.mulPose(Axis.ZP.rotationDegrees(Mth.lerp(partialTick, dart.xRotO, dart.getXRot())));

        VertexConsumer vertices = buffers.getBuffer(RenderType.entityCutoutNoCull(TEXTURE));
        boolean purification = dart instanceof PurificationDartEntity
                || dart instanceof com.carnis.mod.entity.projectile.InoculatorDartEntity inoculator
                && inoculator.getDartType() == com.carnis.mod.entity.projectile.InoculatorDartEntity.DartType.PURIFICATION;
        int fluid = purification ? SERUM : VIRAL;

        // The model's positive X axis points toward the needle tip.
        box(poseStack, vertices, packedLight, -0.34F, -0.018F, -0.018F, 0.34F, 0.018F, 0.018F, STEEL);
        box(poseStack, vertices, packedLight, 0.32F, -0.010F, -0.010F, 0.52F, 0.010F, 0.010F, GLASS);
        box(poseStack, vertices, packedLight, -0.15F, -0.056F, -0.056F, 0.10F, 0.056F, 0.056F, fluid);
        box(poseStack, vertices, packedLight, -0.15F, -0.064F, -0.064F, 0.10F, -0.054F, -0.054F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.15F, 0.054F, -0.064F, 0.10F, 0.064F, -0.054F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.15F, -0.064F, 0.054F, 0.10F, -0.054F, 0.064F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.15F, 0.054F, 0.054F, 0.10F, 0.064F, 0.064F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.14F, 0.057F, -0.038F, 0.08F, 0.061F, -0.023F, GLASS);
        if (!purification) {
            box(poseStack, vertices, packedLight, -0.09F, 0.057F, 0.015F, 0.03F, 0.061F, 0.033F, VIRAL_ACCENT);
        }
        box(poseStack, vertices, packedLight, -0.19F, -0.072F, -0.072F, -0.15F, 0.072F, 0.072F, BRASS);
        box(poseStack, vertices, packedLight, 0.10F, -0.072F, -0.072F, 0.14F, 0.072F, 0.072F, BRASS);
        box(poseStack, vertices, packedLight, -0.43F, -0.025F, -0.025F, -0.30F, 0.025F, 0.025F, DARK_STEEL);
        box(poseStack, vertices, packedLight, -0.42F, -0.125F, -0.012F, -0.29F, 0.125F, 0.012F, BRASS);
        box(poseStack, vertices, packedLight, -0.42F, -0.012F, -0.125F, -0.29F, 0.012F, 0.125F, BRASS);

        poseStack.popPose();
        super.render(dart, entityYaw, partialTick, poseStack, buffers, packedLight);
    }

    private static void box(PoseStack stack, VertexConsumer out, int light,
                            float x0, float y0, float z0, float x1, float y1, float z1, int swatch) {
        float u = (swatch * 4.0F + 2.0F) / 32.0F;
        float v = 0.5F;
        face(stack, out, light, u, v, -1, 0, 0, x0,y0,z0, x0,y0,z1, x0,y1,z1, x0,y1,z0);
        face(stack, out, light, u, v,  1, 0, 0, x1,y0,z1, x1,y0,z0, x1,y1,z0, x1,y1,z1);
        face(stack, out, light, u, v, 0, -1, 0, x0,y0,z1, x0,y0,z0, x1,y0,z0, x1,y0,z1);
        face(stack, out, light, u, v, 0,  1, 0, x0,y1,z0, x0,y1,z1, x1,y1,z1, x1,y1,z0);
        face(stack, out, light, u, v, 0, 0, -1, x1,y0,z0, x0,y0,z0, x0,y1,z0, x1,y1,z0);
        face(stack, out, light, u, v, 0, 0,  1, x0,y0,z1, x1,y0,z1, x1,y1,z1, x0,y1,z1);
    }

    private static void face(PoseStack stack, VertexConsumer out, int light, float u, float v,
                             float nx, float ny, float nz,
                             float ax, float ay, float az, float bx, float by, float bz,
                             float cx, float cy, float cz, float dx, float dy, float dz) {
        PoseStack.Pose pose = stack.last();
        vertex(pose, out, light, u, v, nx, ny, nz, ax, ay, az);
        vertex(pose, out, light, u, v, nx, ny, nz, bx, by, bz);
        vertex(pose, out, light, u, v, nx, ny, nz, cx, cy, cz);
        vertex(pose, out, light, u, v, nx, ny, nz, dx, dy, dz);
    }

    private static void vertex(PoseStack.Pose pose, VertexConsumer out, int light, float u, float v,
                               float nx, float ny, float nz, float x, float y, float z) {
        out.vertex(pose.pose(), x, y, z).color(255, 255, 255, 255).uv(u, v)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light)
                .normal(pose.normal(), nx, ny, nz).endVertex();
    }

    @Override
    public ResourceLocation getTextureLocation(T dart) {
        return TEXTURE;
    }
}
