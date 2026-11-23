package com.carnis.mod.block;

import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import javax.annotation.Nullable;

public final class CreepingTendrilsBlock extends LadderBlock {
    public CreepingTendrilsBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientBlockExtensions> consumer) {
        consumer.accept(new net.minecraftforge.client.extensions.common.IClientBlockExtensions() {
            @Override public boolean addDestroyEffects(BlockState state, net.minecraft.world.level.Level level,
                    BlockPos pos, net.minecraft.client.particle.ParticleEngine manager) {
                var particles = new net.minecraft.core.particles.BlockParticleOption(net.minecraft.core.particles.ParticleTypes.BLOCK,
                        ModBlocks.LIVING_FLESH.get().defaultBlockState());
                for (int i = 0; i < 24; i++) {
                    double x = level.random.nextDouble(), y = level.random.nextDouble(), z = level.random.nextDouble();
                    level.addParticle(particles, pos.getX() + x, pos.getY() + y, pos.getZ() + z,
                            (x - .5D) * .15D, (y - .5D) * .15D, (z - .5D) * .15D);
                }
                return true;
            }
        });
    }

    @Override
    public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        BlockState support = level.getBlockState(pos.relative(state.getValue(FACING).getOpposite()));
        return (support.is(ModBlocks.LIVING_FLESH.get()) || support.is(ModBlocks.OSSIFIED_FLESH.get())
                || support.is(ModBlocks.FIREPROOF_FLESH.get())) && super.canSurvive(state, level, pos);
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState state = super.getStateForPlacement(context);
        return state != null && canSurvive(state, context.getLevel(), context.getClickedPos()) ? state : null;
    }
}
