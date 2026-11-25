package com.carnis.mod.client.model;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.NervePillarBlockEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.DefaultedBlockGeoModel;

public final class NervePillarModel extends DefaultedBlockGeoModel<NervePillarBlockEntity> {
    public NervePillarModel() { super(new ResourceLocation(CarnisMod.MOD_ID, "nerve_pillar")); }
}
