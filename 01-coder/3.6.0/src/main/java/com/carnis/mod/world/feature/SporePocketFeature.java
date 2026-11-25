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
