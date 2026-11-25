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
