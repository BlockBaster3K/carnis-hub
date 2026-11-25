package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.world.GestationCystFeature;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModFeatures {
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(Registries.FEATURE, CarnisMod.MOD_ID);
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> GESTATION_CYST =
            FEATURES.register("gestation_cyst", GestationCystFeature::new);
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> FLESH_NEST =
            FEATURES.register("flesh_nest", com.carnis.mod.world.feature.FleshNestFeature::new);
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> SPORE_POCKET =
            FEATURES.register("spore_pocket", com.carnis.mod.world.feature.SporePocketFeature::new);

    private ModFeatures() {
    }

    public static void register(IEventBus bus) {
        FEATURES.register(bus);
    }
}
