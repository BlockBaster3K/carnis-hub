package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, CarnisMod.MOD_ID);
    public static final RegistryObject<CreativeModeTab> CARNIS_TAB = CREATIVE_TABS.register("carnis", () ->
            CreativeModeTab.builder().title(Component.translatable("carnis.tab"))
                    .icon(() -> ModItems.PULSING_HEART.get().getDefaultInstance())
                    .displayItems((parameters, output) -> {
                        // Organs and cores
                        output.accept(ModItems.PULSING_HEART.get());
                        output.accept(ModItems.HIVE_EYE.get());
                        output.accept(ModItems.STOMACH_POOL.get());
                        output.accept(ModItems.NERVE_PILLAR.get());
                        // Tissues and flora
                        output.accept(ModItems.LIVING_FLESH.get());
                        output.accept(ModItems.OSSIFIED_FLESH.get());
                        output.accept(ModItems.CHARRED_FLESH.get());
                        output.accept(ModItems.FIREPROOF_FLESH.get());
                        output.accept(ModItems.FLESH_VEINS.get());
                        output.accept(ModItems.NEURAL_MOSS.get());
                        output.accept(ModItems.SINEW_SPIKES.get());
                        output.accept(ModItems.PUSTULE_CLUSTER.get());
                        output.accept(ModItems.SPORE_SPROUT.get());
                        output.accept(ModItems.FLESH_BULB.get());
                        output.accept(ModItems.BIOMASS_REMAINS.get());
                        // Field equipment
                        output.accept(ModItems.RESEARCH_JOURNAL.get());
                        output.accept(ModItems.BIO_PURIFIER.get());
                        output.accept(ModItems.PNEUMATIC_INOCULATOR.get());
                        output.accept(ModItems.PURIFICATION_SERUM.get());
                        output.accept(ModItems.PURIFICATION_DART.get());
                        output.accept(ModItems.VIRAL_DART.get());
                        output.accept(ModItems.NEURAL_BINDING_MATRIX.get());
                        // Neuro-resonator armor
                        output.accept(ModItems.NEURO_RESONATOR_HELMET.get());
                        output.accept(ModItems.NEURO_RESONATOR_CHESTPLATE.get());
                        output.accept(ModItems.NEURO_RESONATOR_LEGGINGS.get());
                        output.accept(ModItems.NEURO_RESONATOR_BOOTS.get());
                        // Materials
                        output.accept(ModItems.CREEPING_TENDRILS.get());
                        output.accept(ModItems.TAINTED_SLUDGE_BUCKET.get());
                        // Spawn eggs
                        output.accept(ModItems.INFECTED_ZOMBIE_SPAWN_EGG.get());
                        output.accept(ModItems.INFECTED_SKELETON_SPAWN_EGG.get());
                        output.accept(ModItems.INFECTED_CREEPER_SPAWN_EGG.get());
                        output.accept(ModItems.BIOMASS_MAGGOT_SPAWN_EGG.get());
                        output.accept(ModItems.PARASITIC_TENDRIL_SPAWN_EGG.get());
                        output.accept(ModItems.FLESH_AMALGAM_SPAWN_EGG.get());
                        output.accept(ModItems.HIVE_SENTINEL_SPAWN_EGG.get());
                        output.accept(ModItems.CEREBRAL_NEXUS_SPAWN_EGG.get());
                        // Existing additional items remain accessible.
                        output.accept(ModItems.INFECTED_SPIDER_SPAWN_EGG.get());
                        output.accept(ModItems.ANTIBIOTICS.get());
                        output.accept(ModItems.BONE_SCYTHE_ARM.get());
                        output.accept(ModItems.FLESH_SPAT.get());
                        output.accept(ModItems.AMALGAM_BILE_GLOB.get());
                    }).build());
    private ModCreativeTabs() { }
    public static void register(IEventBus modEventBus) { CREATIVE_TABS.register(modEventBus); }
}
