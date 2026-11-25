package com.carnis.mod.client.model;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.PustuleClusterBlockEntity;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.DefaultedBlockGeoModel;

public final class PustuleClusterModel extends DefaultedBlockGeoModel<PustuleClusterBlockEntity> {
    public PustuleClusterModel() { super(new ResourceLocation(CarnisMod.MOD_ID, "pustule_cluster")); }
    @Override public RenderType getRenderType(PustuleClusterBlockEntity entity, ResourceLocation texture) {
        return RenderType.entityTranslucent(texture);
    }
}
