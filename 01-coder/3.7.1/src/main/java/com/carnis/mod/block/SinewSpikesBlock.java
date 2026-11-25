package com.carnis.mod.block;

import com.carnis.mod.init.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import javax.annotation.Nullable;

public final class SinewSpikesBlock extends Block {
    private static final VoxelShape SHAPE = Shapes.block();
    private static final String NEXT_HIT = "carnis:sinew_spikes_next_hit";
    private static final long HIT_COOLDOWN_TICKS = 10L;
    private static final float HIT_DAMAGE = 2.0F;
    public SinewSpikesBlock(BlockBehaviour.Properties properties) { super(properties); }
    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) { return SHAPE; }
    @Override public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) { return Shapes.empty(); }
    @Override public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        BlockPos below = pos.below();
        return level.getBlockState(below).isFaceSturdy(level, below, Direction.UP);
    }
    @Nullable @Override public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState state = defaultBlockState();
        return state.canSurvive(context.getLevel(), context.getClickedPos()) ? state : null;
    }
    @Override public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
                                            LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        if (direction == Direction.DOWN && !state.canSurvive(level, pos)) return Blocks.AIR.defaultBlockState();
        return super.updateShape(state, direction, neighbor, level, pos, neighborPos);
    }
    @Override public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        super.stepOn(level, pos, state, entity);
        hurtAtFeet(level, pos, entity);
    }
    @Override public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        hurtAtFeet(level, pos, entity);
    }
    private static void hurtAtFeet(Level level, BlockPos pos, Entity entity) {
        if (level.isClientSide || !(entity instanceof LivingEntity living) || !living.isAlive()
                || living.isSpectator() || NeuralMossBlock.isHive(living)) return;
        if (living instanceof Player player && player.getItemBySlot(EquipmentSlot.FEET).is(ModItems.NEURO_RESONATOR_BOOTS.get())) return;
        if (living.getBoundingBox().minY > pos.getY() + 7.0D / 16.0D + .05D
                || living.getBoundingBox().maxY < pos.getY()) return;
        long now = level.getGameTime();
        var data = living.getPersistentData();
        if (data.contains(NEXT_HIT) && data.getLong(NEXT_HIT) > now) return;
        // Shared on entity NBT: adjacent spike blocks cannot multiply hits.
        data.putLong(NEXT_HIT, now + HIT_COOLDOWN_TICKS);
        living.hurt(level.damageSources().generic(), HIT_DAMAGE);
        level.playSound(null, pos, SoundEvents.WOOL_PLACE, SoundSource.BLOCKS,
                0.6F, 1.0F);
        if (level instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(ParticleTypes.ITEM_SLIME,
                    living.getX(), living.getY() + 0.5D, living.getZ(),
                    5, 0.3D, 0.3D, 0.3D, 0.0D);
        }
    }
}
