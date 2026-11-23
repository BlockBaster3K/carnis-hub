package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
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
        // Neural moss uses a hand-authored carpet model.
        // Pustule state is rendered by its block entity.

        // Sprout open and closed states use hand-authored models.
        // Flesh bulb and biomass remains use hand-authored state and composite models in main resources.
        // Sinew spikes use a hand-authored 3D panel model.

        geoBlock(ModBlocks.CREEPING_TENDRILS, "creeping_tendrils");
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
