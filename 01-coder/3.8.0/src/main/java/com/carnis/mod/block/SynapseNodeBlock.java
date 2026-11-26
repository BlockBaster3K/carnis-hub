package com.carnis.mod.block;

import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.AABB;

public final class SynapseNodeBlock extends Block {
    public static final IntegerProperty POWER = BlockStateProperties.POWER;
    private static final int SCAN_RADIUS = 8;
    private static final int ACTIVE_SIGNAL = 15;
    private static final int UPDATE_INTERVAL = 10;

    public SynapseNodeBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(defaultBlockState().setValue(POWER, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(POWER);
    }

    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean moving) {
        super.onPlace(state, level, pos, oldState, moving);
        if (!level.isClientSide && !state.is(oldState.getBlock())) {
            level.scheduleTick(pos, this, UPDATE_INTERVAL);
        }
    }

    @Override
    public void neighborChanged(BlockState state, Level level, BlockPos pos, Block block,
                                BlockPos fromPos, boolean moving) {
        super.neighborChanged(state, level, pos, block, fromPos, moving);
        if (!level.isClientSide) level.scheduleTick(pos, this, UPDATE_INTERVAL);
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (!level.getBlockState(pos).is(this)) return;
        double centerX = pos.getX() + 0.5D;
        double centerY = pos.getY() + 0.5D;
        double centerZ = pos.getZ() + 0.5D;
        double radiusSquared = SCAN_RADIUS * SCAN_RADIUS;
        int nearbyTargets = level.getEntitiesOfClass(LivingEntity.class, new AABB(pos).inflate(SCAN_RADIUS),
                entity -> isHiveTarget(entity)
                        && entity.distanceToSqr(centerX, centerY, centerZ) <= radiusSquared).size();
        int nextPower = Math.min(ACTIVE_SIGNAL, nearbyTargets);
        if (state.getValue(POWER) != nextPower) {
            level.setBlock(pos, state.setValue(POWER, nextPower), 3);
            level.updateNeighborsAt(pos, this);
            level.updateNeighbourForOutputSignal(pos, this);
            if (nextPower > 0) {
                level.playSound(null, pos, ModSounds.SYNAPSE_SHOCK.get(),
                        SoundSource.BLOCKS, 0.8F, 1.0F);
            }
        }
        if (nearbyTargets > 0 && Math.floorMod(level.getGameTime(), 40L) == 0L) {
            level.playSound(null, pos, ModSounds.SYNAPSE_NODE_PULSE.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        }
        level.scheduleTick(pos, this, UPDATE_INTERVAL);
    }

    private static boolean isHiveTarget(LivingEntity entity) {
        return entity.isAlive() && (entity instanceof HivemindLinkedMob || entity instanceof FleshAmalgamEntity);
    }

    @Override
    public boolean isSignalSource(BlockState state) {
        return true;
    }

    @Override
    public int getSignal(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return state.getValue(POWER);
    }

    @Override
    public int getDirectSignal(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return state.getValue(POWER);
    }
}
