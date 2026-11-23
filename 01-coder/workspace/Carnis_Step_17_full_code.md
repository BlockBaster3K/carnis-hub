# Шаг 17 — полный исходный код и ресурсы

## `src/main/java/com/carnis/mod/world/feature/FleshNestFeature.java`

```java
package com.carnis.mod.world.feature;

import com.carnis.mod.block.FleshBulbBlock;
import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.entity.BiomassMaggotEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import java.util.ArrayList;
import java.util.List;

public final class FleshNestFeature extends Feature<NoneFeatureConfiguration> {
    private static final int MIN_Y = -58, MAX_Y = 0;
    public FleshNestFeature() { super(NoneFeatureConfiguration.CODEC); }
    @Override public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        RandomSource random = context.random();
        BlockPos origin = context.origin();
        // The center is fixed inside the placement chunk, leaving a one-block border.
        BlockPos center = new BlockPos((origin.getX() & ~15) + 7, origin.getY(), (origin.getZ() & ~15) + 7);
        int radius = 3 + random.nextInt(4);
        int vertical = Math.max(3, radius - 2);
        if (!preflight(level, center, radius, vertical)) return false;
        if (!level.setBlock(center, ModBlocks.PULSING_HEART.get().defaultBlockState(), 2)) return false;
        List<BlockPos> tissue = new ArrayList<>();
        for (int x = -radius; x <= radius; x++) for (int y = -vertical; y <= vertical; y++)
            for (int z = -radius; z <= radius; z++) {
                double d = ellipsoid(x, y, z, radius, vertical);
                if (d > 1.0D || x == 0 && y == 0 && z == 0) continue;
                BlockPos pos = center.offset(x, y, z);
                if (d >= .50D) {
                    BlockState flesh = random.nextInt(5) == 0 ? ModBlocks.OSSIFIED_FLESH.get().defaultBlockState()
                            : ModBlocks.LIVING_FLESH.get().defaultBlockState();
                    if (level.setBlock(pos, flesh, 2)) tissue.add(pos.immutable());
                } else level.setBlock(pos, Blocks.AIR.defaultBlockState(), 2);
            }
        List<BlockPos> ceiling = new ArrayList<>();
        List<BlockPos> floor = new ArrayList<>();
        for (int x = -radius + 1; x < radius; x++) for (int z = -radius + 1; z < radius; z++) {
            for (int y = 1; y <= vertical; y++) {
                BlockPos pos = center.offset(x, y, z), support = pos.above();
                if (OrganicFeatureUtil.inWindow(center, support) && OrganicFeatureUtil.safeHeight(level, support, MIN_Y, MAX_Y)
                        && level.getBlockState(pos).isAir()
                        && level.getBlockState(support).isFaceSturdy(level, support, Direction.DOWN)) {
                    ceiling.add(pos.immutable()); break;
                }
            }
            for (int y = -vertical + 1; y <= -1; y++) {
                BlockPos pos = center.offset(x, y, z), support = pos.below();
                if (OrganicFeatureUtil.inWindow(center, support) && OrganicFeatureUtil.safeHeight(level, support, MIN_Y, MAX_Y)
                        && level.getBlockState(pos).isAir()
                        && level.getBlockState(support).isFaceSturdy(level, support, Direction.UP)) {
                    floor.add(pos.immutable()); break;
                }
            }
        }
        OrganicFeatureUtil.shuffle(ceiling, random);
        int bulbs = 2 + random.nextInt(3), placedBulbs = 0;
        BlockState hanging = ModBlocks.FLESH_BULB.get().defaultBlockState()
                .setValue(FleshBulbBlock.HANGING, true).setValue(FleshBulbBlock.PULSING, false);
        for (BlockPos pos : ceiling) {
            if (placedBulbs >= bulbs) break;
            if (hanging.canSurvive(level, pos) && level.setBlock(pos, hanging, 2)) placedBulbs++;
        }
        OrganicFeatureUtil.shuffle(floor, random);
        int clusters = 1 + random.nextInt(3);
        List<BlockPos> centers = new ArrayList<>();
        List<BlockPos> spawnSites = new ArrayList<>();
        BlockState remains = ModBlocks.BIOMASS_REMAINS.get().defaultBlockState();
        for (BlockPos pos : floor) {
            if (centers.size() >= clusters) break;
            if (centers.stream().anyMatch(p -> p.distSqr(pos) < 5.0D) || !level.getBlockState(pos).isAir()
                    || !remains.canSurvive(level, pos) || !level.setBlock(pos, remains, 2)) continue;
            centers.add(pos); spawnSites.add(pos);
            for (Direction direction : Direction.Plane.HORIZONTAL) {
                BlockPos next = pos.relative(direction);
                if (!floor.contains(next) || !OrganicFeatureUtil.inWindow(center, next) || random.nextBoolean()
                        || !level.getBlockState(next).isAir() || !remains.canSurvive(level, next)) continue;
                if (level.setBlock(next, remains, 2)) spawnSites.add(next.immutable());
            }
        }
        for (BlockPos pos : floor) {
            if (spawnSites.size() >= 4) break;
            if (!spawnSites.contains(pos) && level.getBlockState(pos).isAir()) spawnSites.add(pos);
        }
        for (int x = -radius + 1; x < radius; x++) for (int y = -vertical + 1; y < vertical; y++)
            for (int z = -radius + 1; z < radius; z++) {
                BlockPos pos = center.offset(x, y, z);
                if (spawnSites.contains(pos) || spawnSites.contains(pos.below())
                        || random.nextInt(3) != 0 || !OrganicFeatureUtil.inWindow(center, pos)) continue;
                if (OrganicFeatureUtil.placeVein(level, center, pos, MIN_Y, MAX_Y)) tissue.add(pos.immutable());
            }
        if (level.getBlockEntity(center) instanceof PulsingHeartBlockEntity heart) heart.seedGeneratedTissue(tissue);
        spawnMaggots(level, random, center, spawnSites, 1 + random.nextInt(2));
        return true;
    }
    private static double ellipsoid(int x, int y, int z, int radius, int vertical) {
        return (x * x + z * z) / (double) (radius * radius) + y * y / (double) (vertical * vertical);
    }
    private static boolean preflight(WorldGenLevel level, BlockPos center, int radius, int vertical) {
        if (!OrganicFeatureUtil.safeHeight(level, center.offset(0, -vertical, 0), MIN_Y, MAX_Y)
                || !OrganicFeatureUtil.safeHeight(level, center.offset(0, vertical, 0), MIN_Y, MAX_Y)) return false;
        int deep = 0;
        int caveAir = 0;
        for (int x = -radius - 1; x <= radius + 1; x++) for (int z = -radius - 1; z <= radius + 1; z++) {
            BlockPos column = center.offset(x, 0, z);
            if (!OrganicFeatureUtil.inWindow(center, column)) continue;
            if (!OrganicFeatureUtil.covered(level, column.above(vertical), 8)) return false;
            for (int y = -vertical - 1; y <= vertical + 1; y++) {
                BlockPos pos = center.offset(x, y, z);
                if (level.isOutsideBuildHeight(pos)) return false;
                BlockState state = level.getBlockState(pos);
                if (!state.getFluidState().isEmpty()) return false;
                if (Math.abs(x) <= radius && Math.abs(z) <= radius && Math.abs(y) <= vertical
                        && ellipsoid(x, y, z, radius, vertical) <= 1.0D) {
                    if (!OrganicFeatureUtil.validNatural(state)) return false;
                    if (state.is(Blocks.DEEPSLATE)) deep++;
                    if (state.isAir() && ellipsoid(x, y, z, radius, vertical) < .50D) caveAir++;
                }
            }
        }
        return deep >= 20 && caveAir >= 4;
    }
    private static void spawnMaggots(WorldGenLevel level, RandomSource random, BlockPos center,
                                     List<BlockPos> sites, int count) {
        OrganicFeatureUtil.shuffle(sites, random);
        int placed = 0;
        for (BlockPos pos : sites) {
            if (placed >= count) break;
            BlockPos above = pos.above();
            if (!OrganicFeatureUtil.inWindow(center, pos) || !OrganicFeatureUtil.safeHeight(level, above, MIN_Y, MAX_Y)
                    || !level.getBlockState(above).isAir()) continue;
            BiomassMaggotEntity maggot = ModEntities.BIOMASS_MAGGOT.get().create(level.getLevel());
            if (maggot == null) continue;
            maggot.moveTo(pos.getX() + .5D, pos.getY(), pos.getZ() + .5D, random.nextFloat() * 360.0F, 0);
            maggot.setPersistenceRequired();
            if (level.addFreshEntity(maggot)) placed++;
        }
    }
}
```

## `src/main/java/com/carnis/mod/world/feature/SporePocketFeature.java`

```java
package com.carnis.mod.world.feature;

import com.carnis.mod.block.FleshBulbBlock;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import java.util.ArrayList;
import java.util.List;

public final class SporePocketFeature extends Feature<NoneFeatureConfiguration> {
    private static final int MIN_Y = -30, MAX_Y = 40;
    public SporePocketFeature() { super(NoneFeatureConfiguration.CODEC); }
    @Override public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        RandomSource random = context.random();
        BlockPos origin = context.origin();
        int radius = 2 + random.nextInt(2);
        // Include a one-cell margin in the same chunk for support and fluid checks.
        if (!OrganicFeatureUtil.inWindow(origin, origin.offset(-radius - 1, 0, -radius - 1))
                || !OrganicFeatureUtil.inWindow(origin, origin.offset(radius + 1, 0, radius + 1))) return false;
        BlockPos floor = null;
        BlockPos ceiling = null;
        for (int dy = -4; dy <= 4 && floor == null; dy++) {
            BlockPos pos = origin.offset(0, dy, 0);
            if (!OrganicFeatureUtil.safeHeight(level, pos, MIN_Y, MAX_Y)
                    || !OrganicFeatureUtil.safeHeight(level, pos.below(), MIN_Y, MAX_Y)
                    || !level.getBlockState(pos).isAir() || !OrganicFeatureUtil.naturalStone(level.getBlockState(pos.below()))
                    || !level.getBlockState(pos.below()).isFaceSturdy(level, pos.below(), Direction.UP)) continue;
            for (int rise = 2; rise <= 7; rise++) {
                BlockPos candidate = pos.above(rise);
                if (!OrganicFeatureUtil.safeHeight(level, candidate.above(), MIN_Y, MAX_Y)) break;
                if (!level.getBlockState(candidate).isAir()) break;
                BlockPos support = candidate.above();
                if (OrganicFeatureUtil.naturalStone(level.getBlockState(support))
                        && level.getBlockState(support).isFaceSturdy(level, support, Direction.DOWN)) {
                    floor = pos.immutable(); ceiling = candidate.immutable(); break;
                }
            }
        }
        if (floor == null || ceiling == null || !OrganicFeatureUtil.covered(level, ceiling.above(), 8)) return false;
        List<BlockPos> patch = new ArrayList<>();
        for (int x = -radius - 1; x <= radius + 1; x++) for (int z = -radius - 1; z <= radius + 1; z++) {
            BlockPos column = floor.offset(x, 0, z);
            if (!OrganicFeatureUtil.inWindow(origin, column) || !OrganicFeatureUtil.covered(level, column.above(7), 4)) return false;
            for (int y = -1; y <= 7; y++) {
                BlockPos pos = column.above(y);
                if (!OrganicFeatureUtil.safeHeight(level, pos, MIN_Y, MAX_Y) || !level.getFluidState(pos).isEmpty()) return false;
            }
            if (x*x + z*z > radius*radius) continue;
            BlockPos ground = column.below();
            BlockState state = level.getBlockState(ground);
            if (OrganicFeatureUtil.naturalStone(state) && !state.hasBlockEntity() && state.getFluidState().isEmpty()
                    && level.getBlockState(column).isAir() && state.isFaceSturdy(level, ground, Direction.UP)) patch.add(ground.immutable());
        }
        if (patch.size() < 4) return false;
        BlockState bulb = ModBlocks.FLESH_BULB.get().defaultBlockState()
                .setValue(FleshBulbBlock.HANGING, true).setValue(FleshBulbBlock.PULSING, false);
        if (!bulb.canSurvive(level, ceiling) || !level.setBlock(ceiling, bulb, 2)) return false;
        for (BlockPos pos : patch) level.setBlock(pos, ModBlocks.LIVING_FLESH.get().defaultBlockState(), 2);
        for (BlockPos ground : patch) {
            BlockPos pos = ground.above();
            if (random.nextInt(3) != 0) OrganicFeatureUtil.placeVein(level, origin, pos, MIN_Y, MAX_Y);
        }
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/world/feature/OrganicFeatureUtil.java`

```java
package com.carnis.mod.world.feature;

import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import java.util.List;

/** All positions, including support reads, are restricted to the central chunk interior. */
public final class OrganicFeatureUtil {
    private OrganicFeatureUtil() { }
    public static boolean inWindow(BlockPos origin, BlockPos pos) {
        int minX = origin.getX() & ~15, minZ = origin.getZ() & ~15;
        int x = pos.getX() - minX, z = pos.getZ() - minZ;
        return x >= 1 && x <= 14 && z >= 1 && z <= 14;
    }
    public static boolean safeHeight(WorldGenLevel level, BlockPos pos, int minY, int maxY) {
        return pos.getY() >= minY && pos.getY() <= maxY && !level.isOutsideBuildHeight(pos);
    }
    public static boolean covered(WorldGenLevel level, BlockPos pos, int clearance) {
        return pos.getY() + clearance < level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, pos.getX(), pos.getZ());
    }
    public static boolean naturalStone(BlockState state) {
        return state.is(Blocks.STONE) || state.is(Blocks.DEEPSLATE) || state.is(Blocks.TUFF)
                || state.is(Blocks.GRANITE) || state.is(Blocks.DIORITE) || state.is(Blocks.ANDESITE);
    }
    public static boolean validNatural(BlockState state) {
        return !state.hasBlockEntity() && state.getFluidState().isEmpty() && (state.isAir() || naturalStone(state));
    }
    public static boolean placeVein(WorldGenLevel level, BlockPos origin, BlockPos pos, int minY, int maxY) {
        if (!inWindow(origin, pos) || !safeHeight(level, pos, minY, maxY)) return false;
        BlockState existing = level.getBlockState(pos);
        if (!existing.isAir() || !existing.getFluidState().isEmpty()) return false;
        BlockState vein = existing;
        for (Direction face : Direction.values()) {
            BlockPos support = pos.relative(face);
            if (!inWindow(origin, support) || !safeHeight(level, support, minY, maxY)) continue;
            if (!level.getBlockState(support).isFaceSturdy(level, support, face.getOpposite())) continue;
            BlockState next = ModBlocks.FLESH_VEINS.get().getStateForPlacement(vein, level, pos, face);
            if (next != null) vein = next;
        }
        return vein.is(ModBlocks.FLESH_VEINS.get()) && level.setBlock(pos, vein, 2);
    }
    public static <T> void shuffle(List<T> list, RandomSource random) {
        for (int i = list.size() - 1; i > 0; i--) {
            int j = random.nextInt(i + 1);
            T previous = list.get(i); list.set(i, list.get(j)); list.set(j, previous);
        }
    }
}
```

## `src/main/java/com/carnis/mod/init/ModFeatures.java`

```java
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
```

## `src/main/java/com/carnis/mod/world/ModConfiguredFeatures.java`

```java
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
```

## `src/main/java/com/carnis/mod/world/ModPlacedFeatures.java`

```java
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
```

## `src/main/java/com/carnis/mod/world/HiveNetwork.java`

```java
package com.carnis.mod.world;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.world.infection.InfectionTickQueue;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

/** Persisted, per-dimension position index. Only known positions are visited; no voxel scans. */
public final class HiveNetwork extends SavedData {
    public enum Kind { INFECTION, EYE, POOL, PILLAR }
    private final EnumMap<Kind, Map<Long, Set<Long>>> byChunk = new EnumMap<>(Kind.class);
    private final Set<UUID> deadSentinels = new HashSet<>();
    public HiveNetwork() { for (Kind k : Kind.values()) byChunk.put(k, new HashMap<>()); }
    public static HiveNetwork get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(HiveNetwork::load, HiveNetwork::new, "carnis_hive_network");
    }
    public static HiveNetwork load(CompoundTag tag) {
        HiveNetwork data = new HiveNetwork();
        for (Kind k : Kind.values()) for (long packed : tag.getLongArray(k.name())) data.put(k, BlockPos.of(packed), true);
        var dead = tag.getList("DeadSentinels", net.minecraft.nbt.Tag.TAG_STRING);
        for (int i = 0; i < dead.size(); i++) {
            try { data.deadSentinels.add(UUID.fromString(dead.getString(i))); } catch (IllegalArgumentException ignored) { }
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag tag) {
        for (Kind k : Kind.values()) {
            List<Long> list = new ArrayList<>();
            byChunk.get(k).values().forEach(list::addAll);
            tag.putLongArray(k.name(), list);
        }
        var dead = new net.minecraft.nbt.ListTag();
        deadSentinels.forEach(id -> dead.add(net.minecraft.nbt.StringTag.valueOf(id.toString())));
        tag.put("DeadSentinels", dead);
        return tag;
    }
    public void noteSentinelDeath(UUID id) { if (deadSentinels.add(id)) setDirty(); }
    public boolean consumeSentinelDeath(UUID id) { boolean found = deadSentinels.remove(id); if (found) setDirty(); return found; }
    private boolean put(Kind kind, BlockPos pos, boolean present) {
        long chunk = new ChunkPos(pos).toLong();
        Map<Long, Set<Long>> map = byChunk.get(kind);
        if (present) return map.computeIfAbsent(chunk, k -> new HashSet<>()).add(pos.asLong());
        Set<Long> entries = map.get(chunk);
        if (entries == null || !entries.remove(pos.asLong())) return false;
        if (entries.isEmpty()) map.remove(chunk);
        return true;
    }
    public static void observe(ServerLevel level, BlockPos pos, BlockState state, boolean present) {
        HiveNetwork index = get(level);
        for (Kind kind : Kind.values()) {
            boolean matches = switch (kind) {
                case INFECTION -> InfectionTickQueue.isInfectionSource(state);
                case EYE -> state.is(ModBlocks.HIVE_EYE.get());
                case POOL -> state.is(ModBlocks.STOMACH_POOL.get());
                case PILLAR -> state.is(ModBlocks.NERVE_PILLAR.get());
            };
            if (matches && index.put(kind, pos, present)) {
                index.setDirty();
                if (kind == Kind.INFECTION) for (PulsingHeartBlockEntity heart : nearbyHearts(level, pos, 32)) heart.observeInfection(pos, present);
            }
        }
    }
    /** Register a bounded batch of world-generated tissue after its chunk is live. */
    public static void registerGenerated(ServerLevel level, BlockPos origin, List<BlockPos> positions) {
        HiveNetwork index = get(level);
        List<PulsingHeartBlockEntity> hearts = nearbyHearts(level, origin, 40);
        boolean changed = false;
        for (BlockPos pos : positions) {
            if (!level.hasChunkAt(pos) || !InfectionTickQueue.isInfectionSource(level.getBlockState(pos))) continue;
            changed |= index.put(Kind.INFECTION, pos, true);
            for (PulsingHeartBlockEntity heart : hearts) heart.observeInfection(pos, true);
        }
        if (changed) index.setDirty();
    }
    public List<BlockPos> positions(Kind kind, BlockPos origin, int radius) {
        List<BlockPos> found = new ArrayList<>();
        int minX = (origin.getX() - radius) >> 4, maxX = (origin.getX() + radius) >> 4;
        int minZ = (origin.getZ() - radius) >> 4, maxZ = (origin.getZ() + radius) >> 4;
        for (int x = minX; x <= maxX; x++) for (int z = minZ; z <= maxZ; z++) {
            Set<Long> set = byChunk.get(kind).get(ChunkPos.asLong(x, z));
            if (set == null) continue;
            for (long packed : set) {
                BlockPos p = BlockPos.of(packed);
                if (p.distSqr(origin) <= (double) radius * radius) found.add(p);
            }
        }
        return found;
    }
    public static List<PulsingHeartBlockEntity> nearbyHearts(ServerLevel level, BlockPos origin, int radius) {
        List<PulsingHeartBlockEntity> result = new ArrayList<>();
        int minX = (origin.getX() - radius) >> 4, maxX = (origin.getX() + radius) >> 4;
        int minZ = (origin.getZ() - radius) >> 4, maxZ = (origin.getZ() + radius) >> 4;
        for (int x = minX; x <= maxX; x++) for (int z = minZ; z <= maxZ; z++) {
            var chunk = level.getChunkSource().getChunkNow(x, z);
            if (chunk == null) continue;
            for (var be : chunk.getBlockEntities().values())
                if (be instanceof PulsingHeartBlockEntity heart && heart.getBlockPos().distSqr(origin) <= (double)radius * radius) result.add(heart);
        }
        return result;
    }
    public static PulsingHeartBlockEntity nearestHeart(ServerLevel level, BlockPos pos, int radius) {
        return nearbyHearts(level, pos, radius).stream().min(Comparator.comparingDouble(h -> h.getBlockPos().distSqr(pos))).orElse(null);
    }
    public static BlockPos nearestLoaded(ServerLevel level, Kind kind, BlockPos pos, int radius) {
        BlockPos best = null; double distance = Double.MAX_VALUE;
        for (BlockPos p : get(level).positions(kind, pos, radius)) {
            if (!level.hasChunkAt(p)) continue;
            BlockState state = level.getBlockState(p);
            boolean valid = switch(kind) {
                case INFECTION -> InfectionTickQueue.isInfectionSource(state);
                case EYE -> state.is(ModBlocks.HIVE_EYE.get());
                case POOL -> state.is(ModBlocks.STOMACH_POOL.get());
                case PILLAR -> state.is(ModBlocks.NERVE_PILLAR.get());
            };
            if (!valid) { get(level).put(kind, p, false); get(level).setDirty(); continue; }
            double d = p.distSqr(pos); if (d < distance) { best = p; distance = d; }
        }
        return best;
    }
    public static boolean shielded(ServerLevel level, BlockPos pos) { return nearestLoaded(level, Kind.PILLAR, pos, 32) != null; }
}
```

## `src/main/java/com/carnis/mod/block/entity/PulsingHeartBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.HiveSentinelEntity;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import com.carnis.mod.world.infection.InfectionTickQueue;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import software.bernie.geckolib.animatable.GeoBlockEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

public final class PulsingHeartBlockEntity extends BlockEntity implements GeoBlockEntity {
    public static final int PULSE_INTERVAL_TICKS = 100;
    public static final int PULSE_RADIUS = 8;
    private static final RawAnimation PULSE_ANIMATION = RawAnimation.begin().thenLoop("animation.pulsing_heart.pulse");
    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private final Set<Long> infected = new HashSet<>();
    private final List<Long> generatedTissue = new ArrayList<>();
    private long biomass;
    private UUID sentinel;
    private boolean initialized;

    public PulsingHeartBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.PULSING_HEART.get(), pos, state); }
    public int getInfectedBlocksCount() { return infected.size(); }
    public void seedGeneratedTissue(List<BlockPos> positions) {
        for (BlockPos pos : positions) generatedTissue.add(pos.asLong());
        setChanged();
    }
    public long getBiomass() { return biomass; }
    public void addBiomass(long value) {
        if (value <= 0) return;
        biomass = biomass > Long.MAX_VALUE - value ? Long.MAX_VALUE : biomass + value;
        setChanged();
    }
    public void observeInfection(BlockPos pos, boolean present) {
        if (pos.distSqr(worldPosition) > 32D * 32D) return;
        if (present ? infected.add(pos.asLong()) : infected.remove(pos.asLong())) setChanged();
    }
    public void sentinelDied(UUID id) {
        if (id.equals(sentinel)) {
            if (level instanceof ServerLevel server) HiveNetwork.get(server).consumeSentinelDeath(id);
            sentinel = null; setChanged();
        }
    }
    @Override protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putLongArray("InfectedPositions", new ArrayList<>(infected));
        tag.putLongArray("GeneratedTissuePending", generatedTissue);
        tag.putInt("infected_blocks_count", infected.size());
        tag.putLong("ClusterBiomass", biomass);
        if (sentinel != null) tag.putUUID("Sentinel", sentinel);
    }
    @Override public void load(CompoundTag tag) {
        super.load(tag); infected.clear();
        for (long p : tag.getLongArray("InfectedPositions")) infected.add(p);
        generatedTissue.clear();
        for (long p : tag.getLongArray("GeneratedTissuePending")) generatedTissue.add(p);
        biomass = Math.max(0, tag.getLong("ClusterBiomass"));
        sentinel = tag.hasUUID("Sentinel") ? tag.getUUID("Sentinel") : null;
        initialized = false;
    }
    public static void serverTick(Level world, BlockPos pos, BlockState state, PulsingHeartBlockEntity heart) {
        if (!(world instanceof ServerLevel level)) return;
        if (!heart.initialized) {
            // Rebuild from the event-maintained index, never from a cube of world blocks.
            heart.infected.clear();
            for (BlockPos p : HiveNetwork.get(level).positions(HiveNetwork.Kind.INFECTION, pos, 32)) heart.infected.add(p.asLong());
            heart.initialized = true;
            heart.setChanged();
        }
        if (!heart.generatedTissue.isEmpty()) {
            int count = Math.min(64, heart.generatedTissue.size());
            List<BlockPos> batch = new ArrayList<>(count);
            for (int i = 0; i < count; i++) batch.add(BlockPos.of(heart.generatedTissue.get(i)));
            HiveNetwork.registerGenerated(level, pos, batch);
            heart.generatedTissue.subList(0, count).clear();
            heart.setChanged();
        }
        if (!InfectionTickQueue.refreshHeartChunk(level, pos)) return;
        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), PULSE_INTERVAL_TICKS), PULSE_INTERVAL_TICKS) == 0)
            heart.pulse(level);
    }
    private void pulse(ServerLevel level) {
        com.carnis.mod.event.AmalgamationHandler.onHighBiomassPulse(level, worldPosition);
        if (sentinel != null && HiveNetwork.get(level).consumeSentinelDeath(sentinel)) { sentinel = null; setChanged(); }
        if (sentinel == null) {
            var area = new net.minecraft.world.phys.AABB(worldPosition).inflate(32);
            for (HiveSentinelEntity guard : level.getEntitiesOfClass(HiveSentinelEntity.class, area,
                    e -> e.isAlive() && e.blockPosition().distSqr(worldPosition) <= 1024)) {
                sentinel = guard.getUUID(); guard.setHeartPos(worldPosition); setChanged(); break;
            }
        }
        int queued = 0;
        for (long packed : infected) {
            BlockPos p = BlockPos.of(packed);
            if (p.distSqr(worldPosition) <= PULSE_RADIUS * PULSE_RADIUS && level.hasChunkAt(p)
                    && InfectionTickQueue.isInfectionSource(level.getBlockState(p))) {
                InfectionTickQueue.enqueueHeartPulse(level, p);
                if (++queued >= 6) break;
            }
        }
        if (!level.getGameRules().getBoolean(net.minecraft.world.level.GameRules.RULE_MOBGRIEFING)) return;
        if (infected.size() >= 25 && !hasOrgan(level, HiveNetwork.Kind.EYE)) morphBlock(level, 0);
        else if (infected.size() >= 50 && sentinel == null) morphBlock(level, 1);
        else if (infected.size() >= 75 && !hasOrgan(level, HiveNetwork.Kind.POOL)) morphBlock(level, 2);
        else if (infected.size() >= 100 && !hasOrgan(level, HiveNetwork.Kind.PILLAR)) morphBlock(level, 3);
        else if (infected.size() >= 100 && sentinel != null && biomass >= 200
                && HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.EYE, worldPosition, 32) != null
                && HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.POOL, worldPosition, 32) != null
                && HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.PILLAR, worldPosition, 32) != null) metamorphose(level);
    }
    private boolean hasOrgan(ServerLevel level, HiveNetwork.Kind kind) {
        for (BlockPos p : HiveNetwork.get(level).positions(kind, worldPosition, 32)) {
            if (!level.hasChunkAt(p)) return true; // Unknown unloaded organ is not duplicated.
            BlockState state = level.getBlockState(p);
            if ((kind == HiveNetwork.Kind.EYE && state.is(ModBlocks.HIVE_EYE.get()))
                    || (kind == HiveNetwork.Kind.POOL && state.is(ModBlocks.STOMACH_POOL.get()))
                    || (kind == HiveNetwork.Kind.PILLAR && state.is(ModBlocks.NERVE_PILLAR.get()))) return true;
        }
        return false;
    }
    private BlockPos pickFlesh(ServerLevel level) {
        BlockPos selected = null; int seen = 0;
        for (long packed : infected) {
            BlockPos p = BlockPos.of(packed); double d = p.distSqr(worldPosition);
            if (d < 64 || d > 576 || !level.hasChunkAt(p) || !level.hasChunkAt(p.below()) || !level.hasChunkAt(p.above())) continue;
            if (!level.getBlockState(p).is(ModBlocks.LIVING_FLESH.get()) || !level.isEmptyBlock(p.above())
                    || !level.getBlockState(p.below()).isFaceSturdy(level, p.below(), Direction.UP)) continue;
            if (level.random.nextInt(++seen) == 0) selected = p;
        }
        return selected;
    }
    private void morphBlock(ServerLevel level, int organ) {
        BlockPos pos = pickFlesh(level);
        if (pos == null) return;
        if (organ == 1) {
            HiveSentinelEntity entity = ModEntities.HIVE_SENTINEL.get().create(level);
            if (entity == null) return;
            entity.moveTo(pos.getX() + .5, pos.getY(), pos.getZ() + .5, 0, 0);
            entity.setHeartPos(worldPosition); entity.setPersistenceRequired();
            BlockState old = level.getBlockState(pos);
            if (!level.removeBlock(pos, false)) return;
            if (!level.addFreshEntity(entity)) { level.setBlockAndUpdate(pos, old); return; }
            sentinel = entity.getUUID(); setChanged();
        } else {
            BlockState replacement = organ == 0 ? ModBlocks.HIVE_EYE.get().defaultBlockState()
                    : organ == 2 ? ModBlocks.STOMACH_POOL.get().defaultBlockState() : ModBlocks.NERVE_PILLAR.get().defaultBlockState();
            if (!level.setBlockAndUpdate(pos, replacement)) return;
        }
        level.playSound(null, pos, ModSounds.PULSING_HEART_BEAT.get(), SoundSource.BLOCKS, 1.0F, .65F);
    }
    private void metamorphose(ServerLevel level) {
        Entity entity = level.getEntity(sentinel);
        if (!(entity instanceof HiveSentinelEntity guard) || !guard.isAlive()) return;
        List<BlockPos> satellites = new ArrayList<>();
        for (BlockPos p : HiveNetwork.get(level).positions(HiveNetwork.Kind.INFECTION, worldPosition, 64)) {
            double d = p.distSqr(worldPosition);
            if (d < 48D * 48D || !level.hasChunkAt(p) || !level.getBlockState(p).is(ModBlocks.LIVING_FLESH.get())) continue;
            if (!satellites.isEmpty() && p.distSqr(satellites.get(0)) < 32D * 32D) continue;
            satellites.add(p);
            if (satellites.size() == 2) break;
        }
        if (satellites.size() < 2) return; // No forced chunk loading or partial budding.
        CerebralNexusEntity nexus = ModEntities.CEREBRAL_NEXUS.get().create(level);
        if (nexus == null) return;
        nexus.moveTo(worldPosition.getX() + .5D, worldPosition.getY(), worldPosition.getZ() + .5D, 0, 0);
        nexus.setPersistenceRequired(); nexus.setBiomass(biomass - 200);
        BlockPos first = satellites.get(0), second = satellites.get(1);
        if (!level.setBlockAndUpdate(first, ModBlocks.PULSING_HEART.get().defaultBlockState())) return;
        if (!level.setBlockAndUpdate(second, ModBlocks.PULSING_HEART.get().defaultBlockState())) {
            level.setBlockAndUpdate(first, ModBlocks.LIVING_FLESH.get().defaultBlockState()); return;
        }
        if (!level.addFreshEntity(nexus)) {
            level.setBlockAndUpdate(first, ModBlocks.LIVING_FLESH.get().defaultBlockState());
            level.setBlockAndUpdate(second, ModBlocks.LIVING_FLESH.get().defaultBlockState()); return;
        }
        level.playSound(null, worldPosition, ModSounds.AMALGAM_ROAR.get(), SoundSource.HOSTILE, 2F, .65F);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), worldPosition.getX() + .5, worldPosition.getY() + .7,
                worldPosition.getZ() + .5, 80, .6, .7, .6, .15);
        level.removeBlock(worldPosition, false);
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "pulse_controller", 0, state -> state.setAndContinue(PULSE_ANIMATION)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return animationCache; }
}
```

## `src/main/resources/data/carnis/worldgen/configured_feature/flesh_nest.json`

```json
{
  "type": "carnis:flesh_nest",
  "config": {}
}
```

## `src/main/resources/data/carnis/worldgen/configured_feature/spore_pocket.json`

```json
{
  "type": "carnis:spore_pocket",
  "config": {}
}
```

## `src/main/resources/data/carnis/worldgen/placed_feature/flesh_nest.json`

```json
{
  "feature": "carnis:flesh_nest",
  "placement": [
    {
      "type": "minecraft:rarity_filter",
      "chance": 32
    },
    {
      "type": "minecraft:in_square"
    },
    {
      "type": "minecraft:height_range",
      "height": {
        "type": "minecraft:uniform",
        "min_inclusive": {
          "absolute": -58
        },
        "max_inclusive": {
          "absolute": -10
        }
      }
    },
    {
      "type": "minecraft:biome"
    }
  ]
}
```

## `src/main/resources/data/carnis/worldgen/placed_feature/spore_pocket.json`

```json
{
  "feature": "carnis:spore_pocket",
  "placement": [
    {
      "type": "minecraft:rarity_filter",
      "chance": 24
    },
    {
      "type": "minecraft:in_square"
    },
    {
      "type": "minecraft:height_range",
      "height": {
        "type": "minecraft:uniform",
        "min_inclusive": {
          "absolute": -30
        },
        "max_inclusive": {
          "absolute": 40
        }
      }
    },
    {
      "type": "minecraft:biome"
    }
  ]
}
```

## `src/main/resources/data/carnis/forge/biome_modifier/add_flesh_nests.json`

```json
{
  "type": "forge:add_features",
  "biomes": "#minecraft:is_overworld",
  "features": "carnis:flesh_nest",
  "step": "underground_decoration"
}
```

## `src/main/resources/data/carnis/forge/biome_modifier/add_spore_pockets.json`

```json
{
  "type": "forge:add_features",
  "biomes": "#minecraft:is_overworld",
  "features": "carnis:spore_pocket",
  "step": "underground_decoration"
}
```
