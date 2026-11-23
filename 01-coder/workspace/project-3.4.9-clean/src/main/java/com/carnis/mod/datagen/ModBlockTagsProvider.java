package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlockTags;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.common.data.BlockTagsProvider;
import net.minecraftforge.common.data.ExistingFileHelper;

import java.util.concurrent.CompletableFuture;

public final class ModBlockTagsProvider extends BlockTagsProvider {
    public ModBlockTagsProvider(
            PackOutput output,
            CompletableFuture<HolderLookup.Provider> lookupProvider,
            ExistingFileHelper existingFileHelper
    ) {
        super(
                output,
                lookupProvider,
                CarnisMod.MOD_ID,
                existingFileHelper
        );
    }

    @Override
    protected void addTags(HolderLookup.Provider provider) {
        tag(ModBlockTags.INFECTIOUS_SURFACES)
                .add(
                        ModBlocks.LIVING_FLESH.get(),
                        ModBlocks.OSSIFIED_FLESH.get(),
                        ModBlocks.FIREPROOF_FLESH.get(),
                        ModBlocks.FLESH_VEINS.get(),
                        ModBlocks.PULSING_HEART.get(),
                        ModBlocks.NERVE_PILLAR.get(),
                        ModBlocks.STOMACH_POOL.get(),
                        ModBlocks.HIVE_EYE.get()
                );

        tag(BlockTags.MINEABLE_WITH_HOE).add(ModBlocks.LIVING_FLESH.get(),
                ModBlocks.PUSTULE_CLUSTER.get(), ModBlocks.NEURAL_MOSS.get(), ModBlocks.STOMACH_POOL.get(),
                ModBlocks.FLESH_BULB.get(), ModBlocks.PULSING_HEART.get(), ModBlocks.HIVE_EYE.get());
        tag(BlockTags.MINEABLE_WITH_AXE).add(ModBlocks.FLESH_VEINS.get(), ModBlocks.NERVE_PILLAR.get());
        tag(BlockTags.MINEABLE_WITH_PICKAXE).add(ModBlocks.OSSIFIED_FLESH.get(),
                ModBlocks.FIREPROOF_FLESH.get(), ModBlocks.CHARRED_FLESH.get(), ModBlocks.SINEW_SPIKES.get());
        TagKey<Block> carnisBlocks = TagKey.create(Registries.BLOCK, new ResourceLocation(CarnisMod.MOD_ID, "carnis_blocks"));
        tag(carnisBlocks).add(ModBlocks.TAINTED_SLUDGE.get(), ModBlocks.FLESH_VEINS.get(),
                ModBlocks.FLESH_BULB.get(), ModBlocks.SINEW_SPIKES.get(), ModBlocks.NERVE_PILLAR.get(),
                ModBlocks.CREEPING_TENDRILS.get(), ModBlocks.PUSTULE_CLUSTER.get(), ModBlocks.STOMACH_POOL.get(),
                ModBlocks.SPORE_SPROUT.get(), ModBlocks.NEURAL_MOSS.get(), ModBlocks.CHARRED_FLESH.get(),
                ModBlocks.LIVING_FLESH.get(), ModBlocks.OSSIFIED_FLESH.get(), ModBlocks.FIREPROOF_FLESH.get(),
                ModBlocks.PULSING_HEART.get(), ModBlocks.HIVE_EYE.get());

        tag(BlockTags.NEEDS_STONE_TOOL)
                .add(ModBlocks.OSSIFIED_FLESH.get());

        tag(BlockTags.NEEDS_IRON_TOOL)
                .add(ModBlocks.FIREPROOF_FLESH.get());
    }
}
