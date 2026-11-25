package com.carnis.mod.block;

import com.carnis.mod.block.entity.FleshBulbBlockEntity;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import javax.annotation.Nullable;

public final class FleshBulbBlock extends BaseEntityBlock {
    public static final BooleanProperty HANGING = BooleanProperty.create("hanging");
    public static final BooleanProperty PULSING = BooleanProperty.create("pulsing");
    private static final VoxelShape HANGING_SHAPE = Block.box(3, 3, 3, 13, 16, 13);
    private static final VoxelShape FLOOR_SHAPE = Block.box(2, 0, 3, 14, 14, 13);
    public FleshBulbBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(HANGING, true).setValue(PULSING, false));
    }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) { builder.add(HANGING, PULSING); }
    @Override public RenderShape getRenderShape(BlockState state) { return RenderShape.MODEL; }
    @Nullable @Override public BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new FleshBulbBlockEntity(pos, state); }
    @Nullable @Override public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return level.isClientSide ? null : createTickerHelper(type, ModBlockEntities.FLESH_BULB.get(), FleshBulbBlockEntity::serverTick);
    }
    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return state.getValue(HANGING) ? HANGING_SHAPE : FLOOR_SHAPE;
    }
    @Override public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        Direction direction = state.getValue(HANGING) ? Direction.UP : Direction.DOWN;
        BlockPos support = pos.relative(direction);
        return level.getBlockState(support).isFaceSturdy(level, support, direction.getOpposite());
    }
    @Nullable @Override public BlockState getStateForPlacement(BlockPlaceContext context) {
        boolean preferHanging = context.getClickedFace() == Direction.DOWN;
        BlockState chosen = defaultBlockState().setValue(HANGING, preferHanging);
        if (chosen.canSurvive(context.getLevel(), context.getClickedPos())) return chosen;
        chosen = chosen.setValue(HANGING, !preferHanging);
        return chosen.canSurvive(context.getLevel(), context.getClickedPos()) ? chosen : null;
    }
    @Override public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
            LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        Direction support = state.getValue(HANGING) ? Direction.UP : Direction.DOWN;
        return direction == support && !state.canSurvive(level, pos) ? Blocks.AIR.defaultBlockState()
                : super.updateShape(state, direction, neighbor, level, pos, neighborPos);
    }
    @Override public void onProjectileHit(Level level, BlockState state, BlockHitResult hit, Projectile projectile) {
        if (!level.isClientSide && projectile.mayInteract(level, hit.getBlockPos())) level.destroyBlock(hit.getBlockPos(), true, projectile);
    }
    @Override public void onRemove(BlockState state, Level level, BlockPos pos, BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && !moving && state.getValue(HANGING) && level instanceof ServerLevel server) {
            AABB area = new AABB(pos.getX() - 2, pos.getY() - 8, pos.getZ() - 2, pos.getX() + 3, pos.getY(), pos.getZ() + 3);
            for (Player player : server.getEntitiesOfClass(Player.class, area,
                    p -> p.isAlive() && !p.isSpectator() && p.getY() < pos.getY())) {
                player.hurt(server.damageSources().magic(), 4.0F);
                PlayerInfectionApi.addExposure(player, 10.0F);
            }
            for (int y = 0; y < 8; y++) server.sendParticles(ParticleTypes.CRIMSON_SPORE,
                    pos.getX() + .5, pos.getY() - y + .3, pos.getZ() + .5, 5, 1.2, .15, 1.2, .02);
        }
        super.onRemove(state, level, pos, next, moving);
    }
}
