package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.block.CreepingTendrilsBlock;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraftforge.client.model.generators.BlockModelBuilder;
import net.minecraftforge.client.model.generators.BlockStateProvider;
import net.minecraftforge.client.model.generators.ConfiguredModel;
import net.minecraftforge.common.data.ExistingFileHelper;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;

public final class ModBlockStateProvider extends BlockStateProvider {
    public ModBlockStateProvider(PackOutput output, ExistingFileHelper exFileHelper) {
        super(output, CarnisMod.MOD_ID, exFileHelper);
    }

    @Override
    protected void registerStatesAndModels() {
        fleshVariants(ModBlocks.LIVING_FLESH);
        fleshVariants(ModBlocks.OSSIFIED_FLESH);
        fleshVariants(ModBlocks.CHARRED_FLESH);
        fleshVariants(ModBlocks.FIREPROOF_FLESH);
        simpleBlock(ModBlocks.HIVE_MEMBRANE.get(), models().cubeAll("hive_membrane",
                new ResourceLocation(CarnisMod.MOD_ID, "block/hive_membrane")));
        BlockModelBuilder synapse = models().cubeAll("synapse_node",
                new ResourceLocation(CarnisMod.MOD_ID, "block/synapse_node"));
        getVariantBuilder(ModBlocks.SYNAPSE_NODE.get()).forAllStates(state ->
                ConfiguredModel.builder().modelFile(synapse).build());
        simpleBlock(ModBlocks.INCUBATION_CYST.get(), models().cubeAll("incubation_cyst",
                new ResourceLocation(CarnisMod.MOD_ID, "block/incubation_cyst")));
        simpleBlock(ModBlocks.PURIFIER_LAMP.get(), models().cubeAll("purifier_lamp",
                new ResourceLocation(CarnisMod.MOD_ID, "block/purifier_lamp")));
        // Neural moss uses a hand-authored carpet model.
        // Pustule state is rendered by its block entity.

        // Sprout open and closed states use hand-authored models.
        // Flesh bulb and biomass remains use hand-authored state and composite models in main resources.
        // Sinew spikes use a hand-authored 3D panel model.

        creepingTendrils();
    }

    private void creepingTendrils() {
        BlockModelBuilder[] variantModels = new BlockModelBuilder[4];
        for (int variant = 0; variant < variantModels.length; variant++) {
            String name = "creeping_tendrils_" + variant;
            variantModels[variant] = models().withExistingParent(name, "minecraft:block/ladder")
                    .texture("texture", new ResourceLocation(CarnisMod.MOD_ID, "block/" + name))
                    .renderType("minecraft:cutout");
        }
        getVariantBuilder(ModBlocks.CREEPING_TENDRILS.get()).forAllStates(state -> {
            Direction facing = state.getValue(LadderBlock.FACING);
            int rotation = switch (facing) {
                case NORTH -> 0;
                case EAST -> 90;
                case SOUTH -> 180;
                case WEST -> 270;
                default -> throw new IllegalStateException("Non-horizontal tendril facing: " + facing);
            };
            return ConfiguredModel.builder()
                    .modelFile(variantModels[state.getValue(CreepingTendrilsBlock.VARIANT)])
                    .rotationY(rotation)
                    .build();
        });
    }

    private void fleshVariants(RegistryObject<? extends Block> block) {
        String name = block.getId().getPath();
        List<ConfiguredModel> variants = new ArrayList<>();
        for (int variant = 0; variant < 4; variant++) {
            String variantName = name + "_" + variant;
            BlockModelBuilder model = models().cubeAll(variantName,
                    new ResourceLocation(CarnisMod.MOD_ID, "block/" + variantName));
            for (int x = 0; x < 360; x += 90) {
                for (int y = 0; y < 360; y += 90) {
                    variants.add(ConfiguredModel.builder().modelFile(model)
                            .rotationX(x).rotationY(y).build()[0]);
                }
            }
        }
        getVariantBuilder(block.get()).partialState().setModels(variants.toArray(new ConfiguredModel[0]));
        models().cubeAll(name, new ResourceLocation(CarnisMod.MOD_ID, "block/" + name + "_0"));
    }

    private void simpleCube(RegistryObject<? extends Block> block, String texture) {
        simpleBlock(block.get(), models().cubeAll(block.getId().getPath(),
                new ResourceLocation(CarnisMod.MOD_ID, "block/" + texture)));
    }

    private void crossBlock(RegistryObject<? extends Block> block, String texture) {
        simpleBlock(block.get(), models().cross(block.getId().getPath(),
                new ResourceLocation(CarnisMod.MOD_ID, "block/" + texture)).renderType("cutout"));
    }

    private void geoBlock(RegistryObject<? extends Block> block, String particleTexture) {
        simpleBlock(block.get(), models().getBuilder(block.getId().getPath())
                .texture("particle", new ResourceLocation(CarnisMod.MOD_ID, "block/" + particleTexture)));
    }
}
