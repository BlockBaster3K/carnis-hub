package com.carnis.mod.block;

import com.carnis.mod.world.infection.VeinMutationEngine;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class FleshBlock extends Block {
    @Override public void onPlace(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState old, boolean moving) {
        super.onPlace(state, level, pos, old, moving);
        if (!old.is(state.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
    }
    @Override public void onRemove(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
        super.onRemove(state, level, pos, next, moving);
    }
    public FleshBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public boolean isFlammable(BlockState state, BlockGetter level, BlockPos pos, Direction face) {
        return state.is(ModBlocks.LIVING_FLESH.get());
    }

    @Override
    public int getFireSpreadSpeed(BlockState state, BlockGetter level, BlockPos pos, Direction face) {
        return state.is(ModBlocks.LIVING_FLESH.get()) ? 30 : 0;
    }

    @Override
    public int getFlammability(BlockState state, BlockGetter level, BlockPos pos, Direction face) {
        return state.is(ModBlocks.LIVING_FLESH.get()) ? 60 : 0;
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        com.carnis.mod.world.HiveNetwork.observe(level, pos, state, true);
        if ((state.is(ModBlocks.LIVING_FLESH.get()) || state.is(ModBlocks.OSSIFIED_FLESH.get()))
                && isExposedToFireOrLava(level, pos) && random.nextFloat() < 0.35F) {
            FleshIncineration.burn(level, pos, state);
            return;
        }
        float floraChance = CarnisConfig.SERVER.floraChancePercent.get().floatValue() / 100.0F;
        if (state.is(ModBlocks.LIVING_FLESH.get()) && random.nextFloat() < floraChance) {
            BlockPos above = pos.above();
            if (!level.isOutsideBuildHeight(above) && level.getBlockState(above).isAir()) {
                int floraCap = CarnisConfig.SERVER.floraLocalCap.get();
                if (countNearbyFlora(level, above, floraCap) < floraCap) {
                    Block flora = switch (random.nextInt(3)) {
                        case 0 -> ModBlocks.SPORE_SPROUT.get();
                        case 1 -> ModBlocks.PUSTULE_CLUSTER.get();
                        default -> ModBlocks.NEURAL_MOSS.get();
                    };
                    BlockState plant = flora.defaultBlockState();
                    if (plant.canSurvive(level, above)) level.setBlockAndUpdate(above, plant);
                }
            }
        }
        if (state.is(ModBlocks.LIVING_FLESH.get())) VeinMutationEngine.tickFlesh(level, pos, random);
        if (state.is(ModBlocks.LIVING_FLESH.get()) && random.nextInt(12) == 0)
            com.carnis.mod.ecology.MaggotForaging.onFleshRandomTick(level, pos);
    }

    private static int countNearbyFlora(ServerLevel level, BlockPos center, int stopAt) {
        int count = 0;
        BlockPos.MutableBlockPos cursor = new BlockPos.MutableBlockPos();
        for (int dx = -3; dx <= 3; dx++) {
            for (int dy = -3; dy <= 3; dy++) {
                for (int dz = -3; dz <= 3; dz++) {
                    cursor.setWithOffset(center, dx, dy, dz);
                    if (level.isOutsideBuildHeight(cursor) || !level.hasChunkAt(cursor)) continue;
                    BlockState nearby = level.getBlockState(cursor);
                    if (nearby.is(ModBlocks.SPORE_SPROUT.get())
                            || nearby.is(ModBlocks.PUSTULE_CLUSTER.get())
                            || nearby.is(ModBlocks.NEURAL_MOSS.get())) {
                        count++;
                        if (count >= stopAt) return count;
                    }
                }
            }
        }
        return count;
    }

    private static boolean isExposedToFireOrLava(ServerLevel level, BlockPos pos) {
        for (Direction direction : Direction.values()) {
            BlockPos adjacent = pos.relative(direction);
            if (!level.isOutsideBuildHeight(adjacent) && level.hasChunkAt(adjacent)
                    && (level.getBlockState(adjacent).is(BlockTags.FIRE)
                    || level.getFluidState(adjacent).is(FluidTags.LAVA))) return true;
        }
        return false;
    }
}
