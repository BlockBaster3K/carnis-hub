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
