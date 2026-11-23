package com.carnis.mod.world;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.data.worldgen.BootstapContext;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.VerticalAnchor;
import net.minecraft.world.level.levelgen.placement.BiomeFilter;
import net.minecraft.world.level.levelgen.placement.HeightRangePlacement;
import net.minecraft.world.level.levelgen.placement.InSquarePlacement;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;
import net.minecraft.world.level.levelgen.placement.RarityFilter;
import java.util.List;

/** Optional data-generation bootstrap; matching JSON supplies the runtime registry. */
public final class ModPlacedFeatures {
    public static final ResourceKey<PlacedFeature> FLESH_NEST = key("flesh_nest");
    public static final ResourceKey<PlacedFeature> SPORE_POCKET = key("spore_pocket");
    private ModPlacedFeatures() { }
    private static ResourceKey<PlacedFeature> key(String name) {
        return ResourceKey.create(Registries.PLACED_FEATURE, new ResourceLocation(CarnisMod.MOD_ID, name));
    }
    public static void bootstrap(BootstapContext<PlacedFeature> context) {
        var configured = context.lookup(Registries.CONFIGURED_FEATURE);
        context.register(FLESH_NEST, new PlacedFeature(configured.getOrThrow(ModConfiguredFeatures.FLESH_NEST), List.of(
                RarityFilter.onAverageOnceEvery(32), InSquarePlacement.spread(),
                HeightRangePlacement.uniform(VerticalAnchor.absolute(-58), VerticalAnchor.absolute(-10)), BiomeFilter.biome())));
        context.register(SPORE_POCKET, new PlacedFeature(configured.getOrThrow(ModConfiguredFeatures.SPORE_POCKET), List.of(
                RarityFilter.onAverageOnceEvery(24), InSquarePlacement.spread(),
                HeightRangePlacement.uniform(VerticalAnchor.absolute(-30), VerticalAnchor.absolute(40)), BiomeFilter.biome())));
    }
}
