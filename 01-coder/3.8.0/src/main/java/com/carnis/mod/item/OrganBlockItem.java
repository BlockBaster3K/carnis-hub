package com.carnis.mod.item;

import com.carnis.mod.block.PustuleClusterBlock;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import javax.annotation.Nullable;

public final class OrganBlockItem extends BlockItem {
    public OrganBlockItem(Block block, Properties properties) {
        super(block, properties);
    }

    @Nullable
    @Override
    protected BlockState getPlacementState(BlockPlaceContext context) {
        BlockState state = super.getPlacementState(context);
        if (state != null && state.getBlock() instanceof PustuleClusterBlock
                && (state.getValue(PustuleClusterBlock.BURST)
                || state.getValue(PustuleClusterBlock.AGE) > 0)) {
            return null;
        }
        return state;
    }
}
