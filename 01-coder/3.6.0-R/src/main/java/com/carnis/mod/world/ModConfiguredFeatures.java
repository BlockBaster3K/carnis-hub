package com.carnis.mod.world;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModFeatures;
import net.minecraft.core.registries.Registries;
import net.minecraft.data.worldgen.BootstapContext;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** Optional data-generation bootstrap; runtime entries are provided by data JSON. */
public final class ModConfiguredFeatures {
    public static final ResourceKey<ConfiguredFeature<?, ?>> FLESH_NEST = key("flesh_nest");
    public static final ResourceKey<ConfiguredFeature<?, ?>> SPORE_POCKET = key("spore_pocket");
    private ModConfiguredFeatures() { }
    private static ResourceKey<ConfiguredFeature<?, ?>> key(String name) {
        return ResourceKey.create(Registries.CONFIGURED_FEATURE, new ResourceLocation(CarnisMod.MOD_ID, name));
    }
    public static void bootstrap(BootstapContext<ConfiguredFeature<?, ?>> context) {
        context.register(FLESH_NEST, new ConfiguredFeature<>(ModFeatures.FLESH_NEST.get(), NoneFeatureConfiguration.INSTANCE));
        context.register(SPORE_POCKET, new ConfiguredFeature<>(ModFeatures.SPORE_POCKET.get(), NoneFeatureConfiguration.INSTANCE));
    }
}
