package com.carnis.mod.world;

import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/** Seeds a horizontal, ground-level patch without loading chunks; only selected ground blocks are eligible. */
public final class SubstratePlacer {
    private SubstratePlacer() { }

    /** Returns the number of blocks newly converted. The center is a ground position. */
    public static int placePatch(ServerLevel level, BlockPos center) {
        return placePatch(level, center, 3);
    }

    /** Places an odd-width square, bounded to at most nine blocks per side. */
    public static int placePatch(ServerLevel level, BlockPos center, int width) {
        if (width < 1 || width > 9 || (width & 1) == 0) throw new IllegalArgumentException("width must be odd and between 1 and 9");
        if (!level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)) return 0;
        int placed = 0;
        int radius = width / 2;
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dz = -radius; dz <= radius; dz++) {
                BlockPos pos = center.offset(dx, 0, dz);
                if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) continue;
                BlockState state = level.getBlockState(pos);
                if (state.hasBlockEntity() || !state.getFluidState().isEmpty()
                        || state.getDestroySpeed(level, pos) < 0 || !isNaturalGround(state)) continue;
                if (level.setBlockAndUpdate(pos, ModBlocks.LIVING_FLESH.get().defaultBlockState())) placed++;
            }
        }
        return placed;
    }

    private static boolean isNaturalGround(BlockState state) {
        return state.is(BlockTags.DIRT) || state.is(Blocks.STONE) || state.is(Blocks.DEEPSLATE)
                || state.is(Blocks.SAND) || state.is(Blocks.RED_SAND) || state.is(Blocks.GRAVEL);
    }
}
