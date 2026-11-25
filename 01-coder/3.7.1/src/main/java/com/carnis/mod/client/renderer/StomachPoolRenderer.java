package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.StomachPoolBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

public final class StomachPoolRenderer implements BlockEntityRenderer<StomachPoolBlockEntity> {
    private static final ResourceLocation ACID = new ResourceLocation(CarnisMod.MOD_ID, "textures/block/stomach_pool.png");
    public StomachPoolRenderer(BlockEntityRendererProvider.Context context) { }
    @Override public void render(StomachPoolBlockEntity pool, float partialTick, PoseStack pose,
                                 MultiBufferSource buffers, int packedLight, int packedOverlay) {
        double time = pool.getLevel() == null ? 0 : pool.getLevel().getGameTime() + partialTick;
        boolean active = pool.isDigesting();
        float y = .65F + (float)Math.sin(time * (active ? .24 : .08)) * (active ? .018F : .008F);
        float alpha = .77F + (float)Math.sin(time * (active ? .19 : .06)) * .09F;
        VertexConsumer vertices = buffers.getBuffer(RenderType.entityTranslucent(ACID));
        Matrix4f matrix = pose.last().pose();
        Matrix3f normal = pose.last().normal();
        vertex(vertices, matrix, normal, .126F, y, .126F, 0, 0, alpha);
        vertex(vertices, matrix, normal, .126F, y, .874F, 0, 1, alpha);
        vertex(vertices, matrix, normal, .874F, y, .874F, 1, 1, alpha);
        vertex(vertices, matrix, normal, .874F, y, .126F, 1, 0, alpha);
    }
    private static void vertex(VertexConsumer out, Matrix4f pose, Matrix3f normal, float x, float y, float z, float u, float v, float alpha) {
        out.vertex(pose, x, y, z).color(.68F, 1F, .36F, alpha).uv(u, v)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(LightTexture.FULL_BRIGHT)
                .normal(normal, 0, 1, 0).endVertex();
    }
}
