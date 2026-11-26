package com.carnis.mod.block;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import javax.annotation.Nullable;

public final class PulsingHeartBlock extends BaseEntityBlock {
    private static final VoxelShape SHAPE = box(
            2.0D,
            0.0D,
            2.0D,
            14.0D,
            15.0D,
            14.0D
    );

    public PulsingHeartBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.ENTITYBLOCK_ANIMATED;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return ModBlockEntities.PULSING_HEART.get().create(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
            Level level,
            BlockState state,
            BlockEntityType<T> blockEntityType
    ) {
        if (level.isClientSide()) {
            return createTickerHelper(blockEntityType, ModBlockEntities.PULSING_HEART.get(),
                    com.carnis.mod.client.HeartAmbientTicker::tick);
        }

        return createTickerHelper(
                blockEntityType,
                ModBlockEntities.PULSING_HEART.get(),
                PulsingHeartBlockEntity::serverTick
        );
    }

    @Override
    public VoxelShape getShape(
            BlockState state,
            BlockGetter level,
            BlockPos pos,
            CollisionContext context
    ) {
        return SHAPE;
    }
}
