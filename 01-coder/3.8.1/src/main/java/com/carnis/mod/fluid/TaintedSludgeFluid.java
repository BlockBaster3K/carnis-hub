package com.carnis.mod.fluid;

import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModFluids;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;
import net.minecraftforge.fluids.ForgeFlowingFluid;

public final class TaintedSludgeFluid {
    private TaintedSludgeFluid() { }

    private static boolean interact(Level level, BlockPos pos) {
        if (!(level instanceof ServerLevel server) || !level.getBlockState(pos).is(ModBlocks.TAINTED_SLUDGE.get())) return false;
        for (Direction dir : Direction.values()) {
            BlockPos other = pos.relative(dir);
            if (level.isOutsideBuildHeight(other) || !level.hasChunkAt(other)) continue;
            if (level.getBlockState(other).is(Blocks.LAVA)) {
                level.setBlockAndUpdate(pos, ModBlocks.CHARRED_FLESH.get().defaultBlockState());
                server.sendParticles(ParticleTypes.CLOUD, pos.getX() + .5, pos.getY() + .5, pos.getZ() + .5,
                        18, .35, .35, .35, .03);
                level.playSound(null, pos, SoundEvents.FIRE_EXTINGUISH, SoundSource.BLOCKS, 0.8F, 1.0F);
                return true;
            }
        }
        // One randomized neighbor at most per scheduled tick; never replace waterlogged hosts.
        if (level.random.nextInt(8) == 0) {
            Direction dir = Direction.values()[level.random.nextInt(6)];
            BlockPos other = pos.relative(dir);
            if (!level.isOutsideBuildHeight(other) && level.hasChunkAt(other)
                    && level.getBlockState(other).is(Blocks.WATER)
                    && level.getFluidState(other).isSource()
                    && level.getFluidState(other).getType() == Fluids.WATER) {
                level.setBlockAndUpdate(other, ModBlocks.TAINTED_SLUDGE.get().defaultBlockState());
            }
        }
        return false;
    }

    private static void reschedule(Level level, BlockPos pos) {
        FluidState current = level.getFluidState(pos);
        if (current.getType().isSame(ModFluids.SLUDGE_SOURCE.get())) {
            level.scheduleTick(pos, current.getType(), 20);
        }
    }

    public static final class Source extends ForgeFlowingFluid.Source {
        public Source() { super(ModFluids.properties()); }
        @Override public void tick(Level level, BlockPos pos, FluidState state) {
            if (interact(level, pos)) return;
            super.tick(level, pos, state);
            reschedule(level, pos);
        }
    }

    public static final class Flowing extends ForgeFlowingFluid.Flowing {
        public Flowing() { super(ModFluids.properties()); }
        @Override public void tick(Level level, BlockPos pos, FluidState state) {
            if (interact(level, pos)) return;
            super.tick(level, pos, state);
            reschedule(level, pos);
        }
    }
}
