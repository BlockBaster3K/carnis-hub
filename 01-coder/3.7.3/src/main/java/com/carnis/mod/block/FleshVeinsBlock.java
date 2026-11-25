package com.carnis.mod.block;

import com.carnis.mod.world.infection.VeinMutationEngine;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.MultifaceBlock;
import net.minecraft.world.level.block.MultifaceSpreader;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

public final class FleshVeinsBlock extends MultifaceBlock {
    private static final VoxelShape[] SHAPES_BY_FACES = createShapes();
    private final MultifaceSpreader spreader = new MultifaceSpreader(this);

    private static VoxelShape[] createShapes() {
        VoxelShape[] perFace = new VoxelShape[Direction.values().length];
        for (Direction direction : Direction.values()) {
            perFace[direction.ordinal()] = faceShape(direction);
        }

        VoxelShape[] result = new VoxelShape[1 << Direction.values().length];
        for (int mask = 0; mask < result.length; mask++) {
            VoxelShape combined = Shapes.empty();
            for (Direction direction : Direction.values()) {
                if ((mask & (1 << direction.ordinal())) != 0) {
                    combined = Shapes.or(combined, perFace[direction.ordinal()]);
                }
            }
            result[mask] = combined;
        }
        return result;
    }

    private static VoxelShape faceShape(Direction face) {
        return switch (face) {
            case DOWN -> Block.box(0.0D, 0.0D, 0.0D, 16.0D, 1.0D, 16.0D);
            case UP -> Block.box(0.0D, 15.0D, 0.0D, 16.0D, 16.0D, 16.0D);
            case NORTH -> Block.box(0.0D, 0.0D, 0.0D, 16.0D, 16.0D, 1.0D);
            case SOUTH -> Block.box(0.0D, 0.0D, 15.0D, 16.0D, 16.0D, 16.0D);
            case WEST -> Block.box(0.0D, 0.0D, 0.0D, 1.0D, 16.0D, 16.0D);
            case EAST -> Block.box(15.0D, 0.0D, 0.0D, 16.0D, 16.0D, 16.0D);
        };
    }

    private static boolean hasSupport(BlockGetter level, BlockPos pos, Direction face) {
        BlockPos supportPos = pos.relative(face);
        BlockState support = level.getBlockState(supportPos);
        return !support.isAir() && (support.isFaceSturdy(level, supportPos, face.getOpposite())
                || support.isSolidRender(level, supportPos));
    }

    private static VoxelShape outline(BlockState state, BlockGetter level, BlockPos pos) {
        int mask = 0;
        for (Direction direction : Direction.values()) {
            if (MultifaceBlock.hasFace(state, direction) && hasSupport(level, pos, direction)) {
                mask |= 1 << direction.ordinal();
            }
        }
        return SHAPES_BY_FACES[mask];
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return outline(state, level, pos);
    }

    @Override
    public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return Shapes.empty();
    }

    @Override
    public VoxelShape getVisualShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return outline(state, level, pos);
    }

    @Override
    public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        for (Direction face : Direction.values()) {
            if (MultifaceBlock.hasFace(state, face) && hasSupport(level, pos, face)) return true;
        }
        return false;
    }

    @Override
    public void onPlace(BlockState state, net.minecraft.world.level.Level level,
                        BlockPos pos, BlockState old, boolean moving) {
        super.onPlace(state, level, pos, old, moving);
        if (!old.is(state.getBlock()) && level instanceof ServerLevel server) {
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
        }
    }

    @Override
    public void onRemove(BlockState state, net.minecraft.world.level.Level level,
                         BlockPos pos, BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof ServerLevel server) {
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
        }
        super.onRemove(state, level, pos, next, moving);
    }

    public FleshVeinsBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public MultifaceSpreader getSpreader() {
        return spreader;
    }

    @Override
    public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
                                  LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        BlockState updated = super.updateShape(state, direction, neighbor, level, pos, neighborPos);
        if (!updated.is(this)) return updated;

        for (Direction face : Direction.values()) {
            if (MultifaceBlock.hasFace(updated, face) && !hasSupport(level, pos, face)) {
                updated = updated.setValue(MultifaceBlock.getFaceProperty(face), false);
            }
        }

        for (Direction face : Direction.values()) {
            if (MultifaceBlock.hasFace(updated, face)) return updated;
        }
        return Blocks.AIR.defaultBlockState();
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        com.carnis.mod.world.HiveNetwork.observe(level, pos, state, true);
        VeinMutationEngine.tickVein(level, pos, state, random);
    }
}
