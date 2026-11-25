package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.Block;

public final class ModBlockTags {
    public static final TagKey<Block> HIVE_BLOCKS = TagKey.create(
            Registries.BLOCK,
            new ResourceLocation(CarnisMod.MOD_ID, "hive_blocks")
    );

    public static final TagKey<Block> INFECTIOUS_SURFACES = TagKey.create(
            Registries.BLOCK,
            new ResourceLocation(CarnisMod.MOD_ID, "infectious_surfaces")
    );

    private ModBlockTags() {
    }
}
