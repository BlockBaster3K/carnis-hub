package com.carnis.mod.client.model;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import software.bernie.geckolib.model.DefaultedBlockGeoModel;

@OnlyIn(Dist.CLIENT)
public final class PulsingHeartModel
        extends DefaultedBlockGeoModel<PulsingHeartBlockEntity> {
    public PulsingHeartModel() {
        super(new ResourceLocation(CarnisMod.MOD_ID, "pulsing_heart"));
    }

    @Override
    public RenderType getRenderType(
            PulsingHeartBlockEntity animatable,
            ResourceLocation texture
    ) {
        return RenderType.entityTranslucent(texture);
    }
}
