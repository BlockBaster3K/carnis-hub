package com.carnis.mod.block;

import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class PurifierLampBlock extends Block {
    private static final int UPDATE_INTERVAL = 20;

    public PurifierLampBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean moving) {
        super.onPlace(state, level, pos, oldState, moving);
        if (!level.isClientSide && !state.is(oldState.getBlock())) {
            level.playSound(null, pos, ModSounds.PURIFIER_LAMP_IGNITE.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
            level.scheduleTick(pos, this, UPDATE_INTERVAL);
        }
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (!level.getBlockState(pos).is(this)) return;
        if (Math.floorMod(level.getGameTime(), 80L) == 0L) {
            level.playSound(null, pos, ModSounds.PURIFIER_LOOP.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        }
        level.sendParticles(ModParticles.PURIFIER_FLAME.get(), pos.getX() + 0.5D, pos.getY() + 0.7D,
                pos.getZ() + 0.5D, 2, 0.15D, 0.2D, 0.15D, 0.01D);
        level.scheduleTick(pos, this, UPDATE_INTERVAL);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(3) == 0) {
            level.addParticle(ModParticles.PURIFIER_FLAME.get(), pos.getX() + 0.25D + random.nextDouble() * 0.5D,
                    pos.getY() + 0.7D, pos.getZ() + 0.25D + random.nextDouble() * 0.5D,
                    0.0D, 0.015D, 0.0D);
        }
    }
}
