package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModItems;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.client.model.generators.ItemModelProvider;
import net.minecraftforge.common.data.ExistingFileHelper;
import net.minecraftforge.registries.RegistryObject;

public final class ModItemModelProvider extends ItemModelProvider {
    public ModItemModelProvider(PackOutput output, ExistingFileHelper existingFileHelper) {
        super(output, CarnisMod.MOD_ID, existingFileHelper);
    }

    @Override
    protected void registerModels() {
        withExistingParent("stomach_pool", new ResourceLocation(CarnisMod.MOD_ID, "block/stomach_pool"));
        withExistingParent("nerve_pillar", new ResourceLocation(CarnisMod.MOD_ID, "block/nerve_pillar"));
        // Standard cube block items
        blockItem(ModBlocks.LIVING_FLESH);
        blockItem(ModBlocks.OSSIFIED_FLESH);
        blockItem(ModBlocks.CHARRED_FLESH);
        blockItem(ModBlocks.FIREPROOF_FLESH);
        withExistingParent("pustule_cluster", new ResourceLocation(CarnisMod.MOD_ID, "block/pustule_cluster"));

        // 2D flat item representation for Geo & organic hazard block items
        flatBlockItem(ModBlocks.SPORE_SPROUT);
        // Flesh bulb, moss, spikes, and remains item models are hand-authored in main resources.
        flatBlockItem(ModBlocks.CREEPING_TENDRILS);
        flatBlockItem(ModBlocks.FLESH_VEINS);

        blockItem(ModBlocks.HIVE_MEMBRANE);
        blockItem(ModBlocks.SYNAPSE_NODE);
        blockItem(ModBlocks.INCUBATION_CYST);
        blockItem(ModBlocks.PURIFIER_LAMP);
        // Standard flat items
        flatItem(ModItems.VIRAL_DART);
        flatItem(ModItems.PURIFICATION_DART);
        flatItem(ModItems.PURIFICATION_SERUM);
        flatItem(ModItems.NEURAL_BINDING_MATRIX);
        flatItem(ModItems.TAINTED_SLUDGE_BUCKET);
        flatItem(ModItems.FLESH_AMALGAM_SPAWN_EGG);
        flatItem(ModItems.SINEW_SHIELD);
        flatItem(ModItems.BONE_SCYTHE);
        flatItem(ModItems.OSSIFIED_SCYTHE);
        flatItem(ModItems.PUSTULE_GRENADE);
        flatItem(ModItems.PURIFICATION_VIAL);
    }

    private void blockItem(RegistryObject<? extends Block> block) {
        withExistingParent(block.getId().getPath(),
                new ResourceLocation(CarnisMod.MOD_ID, "block/" + block.getId().getPath()));
    }

    private void flatBlockItem(RegistryObject<? extends Block> block) {
        singleTexture(block.getId().getPath(),
                new ResourceLocation("minecraft", "item/generated"),
                "layer0",
                new ResourceLocation(CarnisMod.MOD_ID, "block/" + block.getId().getPath()));
    }

    private void flatItem(RegistryObject<? extends Item> item) {
        singleTexture(item.getId().getPath(),
                new ResourceLocation("minecraft", "item/generated"),
                "layer0",
                new ResourceLocation(CarnisMod.MOD_ID, "item/" + item.getId().getPath()));
    }
}
