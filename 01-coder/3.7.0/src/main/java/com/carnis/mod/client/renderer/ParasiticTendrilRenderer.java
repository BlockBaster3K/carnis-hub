package com.carnis.mod.client.renderer;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import com.carnis.mod.client.model.ParasiticTendrilModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
public final class ParasiticTendrilRenderer extends GeoEntityRenderer<ParasiticTendrilEntity> {
    public ParasiticTendrilRenderer(EntityRendererProvider.Context context) { super(context, new ParasiticTendrilModel()); shadowRadius = .35F; }
}
