package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModItems;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.MissingMappingsEvent;

/** Best-effort block/item ID migration; the retired digestor block entity has no replacement. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class LegacyRegistryMappings {
    private LegacyRegistryMappings() { }

    @SubscribeEvent
    public static void onMissingMappings(MissingMappingsEvent event) {
        for (var mapping : event.getMappings(ForgeRegistries.Keys.BLOCKS, CarnisMod.MOD_ID)) {
            switch (mapping.getKey().getPath()) {
                case "synapse_pillar" -> mapping.remap(ModBlocks.NERVE_PILLAR.get());
                case "digestor_pit" -> mapping.remap(ModBlocks.STOMACH_POOL.get());
                default -> { }
            }
        }
        for (var mapping : event.getMappings(ForgeRegistries.Keys.ITEMS, CarnisMod.MOD_ID)) {
            switch (mapping.getKey().getPath()) {
                case "synapse_pillar" -> mapping.remap(ModItems.NERVE_PILLAR.get());
                case "digestor_pit" -> mapping.remap(ModItems.STOMACH_POOL.get());
                default -> { }
            }
        }
        for (var mapping : event.getMappings(ForgeRegistries.Keys.BLOCK_ENTITY_TYPES, CarnisMod.MOD_ID)) {
            if (mapping.getKey().getPath().equals("digestor_pit")) {
                // Stomach pools are not block entities. Old block-entity NBT cannot be retained.
                mapping.ignore();
                CarnisMod.LOGGER.warn("Legacy digestor_pit block-entity data cannot be migrated to stomach_pool");
            }
        }
    }
}
