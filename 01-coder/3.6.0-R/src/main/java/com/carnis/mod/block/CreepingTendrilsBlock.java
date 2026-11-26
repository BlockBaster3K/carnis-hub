package com.carnis.mod.block;

import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import javax.annotation.Nullable;

public final class CreepingTendrilsBlock extends LadderBlock {
    public static final IntegerProperty VARIANT = IntegerProperty.create("variant", 0, 3);
    // Relative weights for variants 0..3 are 4:3:2:1 (40%, 30%, 20%, 10%).
    private static final int[] VARIANT_WEIGHTS = {4, 3, 2, 1};
    private static final int VARIANT_WEIGHT_TOTAL = 10;

    public CreepingTendrilsBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(defaultBlockState().setValue(VARIANT, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        // LadderBlock already contributes FACING; only add our persistent texture variant.
        super.createBlockStateDefinition(builder);
        builder.add(VARIANT);
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
        if (state == null || !canSurvive(state, context.getLevel(), context.getClickedPos())) return null;
        return state.setValue(VARIANT, chooseVariant(context.getLevel().random));
    }

    private static int chooseVariant(RandomSource random) {
        int roll = random.nextInt(VARIANT_WEIGHT_TOTAL);
        for (int variant = 0; variant < VARIANT_WEIGHTS.length; variant++) {
            roll -= VARIANT_WEIGHTS[variant];
            if (roll < 0) return variant;
        }
        throw new IllegalStateException("Invalid creeping tendrils variant weights");
    }
}
