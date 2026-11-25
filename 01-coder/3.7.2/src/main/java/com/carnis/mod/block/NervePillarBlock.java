package com.carnis.mod.block;

import com.carnis.mod.block.entity.NervePillarBlockEntity;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;

public final class NervePillarBlock extends net.minecraft.world.level.block.BaseEntityBlock {
    private static final net.minecraft.world.phys.shapes.VoxelShape SHAPE = box(3, 0, 3, 13, 16, 13);
    @Override public net.minecraft.world.phys.shapes.VoxelShape getShape(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos, net.minecraft.world.phys.shapes.CollisionContext context) { return SHAPE; }
    @Override public net.minecraft.world.phys.shapes.VoxelShape getCollisionShape(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos, net.minecraft.world.phys.shapes.CollisionContext context) { return SHAPE; }
    @Override public net.minecraft.world.level.block.RenderShape getRenderShape(BlockState state) { return net.minecraft.world.level.block.RenderShape.ENTITYBLOCK_ANIMATED; }
    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new NervePillarBlockEntity(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
            Level level,
            BlockState state,
            BlockEntityType<T> type
    ) {
        if (level.isClientSide) return null;
        return createTickerHelper(type, ModBlockEntities.NERVE_PILLAR.get(), NervePillarBlockEntity::serverTick);
    }
    @Override public void onRemove(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
        super.onRemove(state, level, pos, next, moving);
    }
    @Override public void randomTick(net.minecraft.world.level.block.state.BlockState state, net.minecraft.server.level.ServerLevel level,
            net.minecraft.core.BlockPos pos, net.minecraft.util.RandomSource random) {
        com.carnis.mod.world.HiveNetwork.observe(level, pos, state, true);
    }
    public NervePillarBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean moving) {
        super.onPlace(state, level, pos, oldState, moving);
        if (!oldState.is(state.getBlock()) && level instanceof ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
        if (!oldState.is(state.getBlock()) && level instanceof ServerLevel server
                && CarnisWorldData.get(server).halveRemainingShock(new ChunkPos(pos), server.getGameTime())) {
            ModMessages.sendToPlayersInLevel(server);
        }
    }

    @Override
    public void playerWillDestroy(
            Level level,
            BlockPos pos,
            BlockState state,
            net.minecraft.world.entity.player.Player player
    ) {
        if (level instanceof ServerLevel serverLevel) {
            CarnisWorldData.get(serverLevel).shockSynapseArea(
                    new ChunkPos(pos),
                    serverLevel.getGameTime()
            );

            serverLevel.playSound(
                    null,
                    pos,
                    com.carnis.mod.init.ModSounds.SYNAPSE_RUPTURE.get(),
                    net.minecraft.sounds.SoundSource.BLOCKS,
                    1.0F,
                    1.0F
            );

            serverLevel.sendParticles(
                    ParticleTypes.ELECTRIC_SPARK,
                    pos.getX() + 0.5D,
                    pos.getY() + 0.8D,
                    pos.getZ() + 0.5D,
                    36,
                    0.55D,
                    0.8D,
                    0.55D,
                    0.08D
            );
            serverLevel.sendParticles(
                    ParticleTypes.POOF,
                    pos.getX() + 0.5D,
                    pos.getY() + 0.6D,
                    pos.getZ() + 0.5D,
                    18,
                    0.4D,
                    0.55D,
                    0.4D,
                    0.035D
            );
        }

        super.playerWillDestroy(level, pos, state, player);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(8) == 0) {
            level.addParticle(ParticleTypes.CRIMSON_SPORE, pos.getX() + random.nextDouble(),
                    pos.getY() + random.nextDouble(), pos.getZ() + random.nextDouble(), 0.0D, 0.02D, 0.0D);
        }
    }
}
