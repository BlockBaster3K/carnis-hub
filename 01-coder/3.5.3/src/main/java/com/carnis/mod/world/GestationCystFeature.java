package com.carnis.mod.world;

import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

public final class GestationCystFeature extends Feature<NoneFeatureConfiguration> {
    private static final int RADIUS = 6;
    private static final int INNER_RADIUS = 4;

    public GestationCystFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos center = context.origin();
        if (center.getY() < -50 || center.getY() > 0
                || !level.getBlockState(center).is(Blocks.DEEPSLATE)) {
            return false;
        }
        // Reject fluids adjacent to the shell as well as inside it.
        for (int x = -RADIUS - 1; x <= RADIUS + 1; x++) {
            for (int y = -RADIUS - 1; y <= RADIUS + 1; y++) {
                for (int z = -RADIUS - 1; z <= RADIUS + 1; z++) {
                    if (x * x + y * y + z * z > (RADIUS + 1) * (RADIUS + 1)) continue;
                    BlockPos p = center.offset(x, y, z);
                    if (level.isOutsideBuildHeight(p) || !level.getFluidState(p).isEmpty()) return false;
                }
            }
        }
        // Validate the complete footprint before writing: never erase block entities,
        // fluids, bedrock, or existing structures with non-natural blocks.
        for (int x = -RADIUS; x <= RADIUS; x++) {
            for (int y = -RADIUS; y <= RADIUS; y++) {
                for (int z = -RADIUS; z <= RADIUS; z++) {
                    if (x * x + y * y + z * z > RADIUS * RADIUS) continue;
                    BlockPos p = center.offset(x, y, z);
                    BlockState state = level.getBlockState(p);
                    if (state.hasBlockEntity() || !state.getFluidState().isEmpty()
                            || !(state.isAir() || state.is(Blocks.DEEPSLATE) || state.is(Blocks.TUFF))) {
                        return false;
                    }
                }
            }
        }
        for (int x = -RADIUS; x <= RADIUS; x++) {
            for (int y = -RADIUS; y <= RADIUS; y++) {
                for (int z = -RADIUS; z <= RADIUS; z++) {
                    int distance = x * x + y * y + z * z;
                    if (distance > RADIUS * RADIUS) continue;
                    BlockState replacement = distance >= INNER_RADIUS * INNER_RADIUS
                            ? ModBlocks.OSSIFIED_FLESH.get().defaultBlockState()
                            : Blocks.AIR.defaultBlockState();
                    level.setBlock(center.offset(x, y, z), replacement, 2);
                }
            }
        }
        level.setBlock(center, ModBlocks.PULSING_HEART.get().defaultBlockState(), 2);
        level.setBlock(center.offset(2, 0, 0), ModBlocks.HIVE_EYE.get().defaultBlockState(), 2);
        level.setBlock(center.offset(-2, 0, 0), ModBlocks.HIVE_EYE.get().defaultBlockState(), 2);
        level.setBlock(center.offset(0, -2, 0), ModBlocks.NERVE_PILLAR.get().defaultBlockState(), 2);
        BlockPos moss = center.offset(2, -2, 0);
        BlockPos sprout = center.offset(-2, -2, 0);
        level.setBlock(moss.below(), ModBlocks.LIVING_FLESH.get().defaultBlockState(), 2);
        level.setBlock(sprout.below(), ModBlocks.LIVING_FLESH.get().defaultBlockState(), 2);
        if (ModBlocks.NEURAL_MOSS.get().defaultBlockState().canSurvive(level, moss))
            level.setBlock(moss, ModBlocks.NEURAL_MOSS.get().defaultBlockState(), 2);
        if (ModBlocks.SPORE_SPROUT.get().defaultBlockState().canSurvive(level, sprout))
            level.setBlock(sprout, ModBlocks.SPORE_SPROUT.get().defaultBlockState(), 2);
        return true;
    }
}
