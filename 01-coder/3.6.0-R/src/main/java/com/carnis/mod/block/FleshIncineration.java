package com.carnis.mod.block;

import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.state.BlockState;

public final class FleshIncineration {
    private FleshIncineration() { }

    public static void burn(ServerLevel level, BlockPos pos, BlockState state) {
        tryBurn(level, pos, state);
    }

    /** Returns false if the supplied state is not burnable or replacement fails. */
    public static boolean tryBurn(ServerLevel level, BlockPos pos, BlockState state) {
        if (!state.is(ModBlocks.LIVING_FLESH.get()) && !state.is(ModBlocks.OSSIFIED_FLESH.get())) return false;
        if (!level.getBlockState(pos).equals(state)) return false;
        if (!level.setBlockAndUpdate(pos, ModBlocks.CHARRED_FLESH.get().defaultBlockState())) return false;
        CarnisWorldData data = CarnisWorldData.get(level);
        data.addAdaptation(CarnisWorldData.AdaptationType.FIRE, 5L);
        if (!com.carnis.mod.world.HiveNetwork.shielded(level, pos))
            data.extendChunkShock(new ChunkPos(pos), level.getGameTime(), 20L);
        ModMessages.sendToPlayersInLevel(level);
        level.sendParticles(ParticleTypes.SMOKE, pos.getX() + 0.5D, pos.getY() + 0.5D,
                pos.getZ() + 0.5D, 16, 0.35D, 0.35D, 0.35D, 0.02D);
        level.sendParticles(ParticleTypes.FLAME, pos.getX() + 0.5D, pos.getY() + 0.5D,
                pos.getZ() + 0.5D, 8, 0.3D, 0.3D, 0.3D, 0.02D);
        return true;
    }
}
