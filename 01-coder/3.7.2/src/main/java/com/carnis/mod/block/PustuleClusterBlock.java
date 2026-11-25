package com.carnis.mod.block;

import com.carnis.mod.block.entity.PustuleClusterBlockEntity;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
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
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import javax.annotation.Nullable;

public final class PustuleClusterBlock extends BaseEntityBlock {
    public static final IntegerProperty AGE = BlockStateProperties.AGE_3;
    public static final BooleanProperty BURST = BooleanProperty.create("burst");
    private static final float REMAINS_CONVERSION_CHANCE = 0.5F;
    private static final String PUSTULE_INFECTION_COOLDOWN = "carnis:pustule_cd";
    private static final VoxelShape SHAPE = Block.box(2, 0, 2, 14, 10, 14);
    private static final VoxelShape EMPTY_SHAPE = Block.box(2, 0, 2, 14, 3, 14);
    public PustuleClusterBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(AGE, 0).setValue(BURST, false));
    }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) { builder.add(AGE, BURST); }
    @Override public RenderShape getRenderShape(BlockState state) { return RenderShape.ENTITYBLOCK_ANIMATED; }
    @Nullable @Override public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return ModBlockEntities.PUSTULE_CLUSTER.get().create(pos, state);
    }
    @Nullable @Override public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
            Level level, BlockState state, BlockEntityType<T> type) {
        return level.isClientSide ? null
                : createTickerHelper(type, ModBlockEntities.PUSTULE_CLUSTER.get(), PustuleClusterBlockEntity::serverTick);
    }
    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return state.getValue(BURST) ? EMPTY_SHAPE : SHAPE;
    }
    @Override public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return getShape(state, level, pos, context);
    }
    @Override public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        BlockPos below = pos.below();
        return level.getBlockState(below).isFaceSturdy(level, below, Direction.UP);
    }
    @Override public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor, LevelAccessor level,
                                            BlockPos pos, BlockPos neighborPos) {
        return direction == Direction.DOWN && !state.canSurvive(level, pos) ? Blocks.AIR.defaultBlockState()
                : super.updateShape(state, direction, neighbor, level, pos, neighborPos);
    }
    @Override public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (!state.getValue(BURST) && state.getValue(AGE) < 3 && random.nextInt(3) == 0)
            level.setBlock(pos, state.setValue(AGE, state.getValue(AGE) + 1), 3);
    }
    public static boolean ready(BlockState state) {
        return state.getBlock() instanceof PustuleClusterBlock && !state.getValue(BURST) && state.getValue(AGE) >= 2;
    }
    private static void contact(BlockState state, Level level, BlockPos pos, Entity entity) {
        if (!(level instanceof ServerLevel server) || !(entity instanceof LivingEntity living) || !living.isAlive()
                || living.isSpectator() || NeuralMossBlock.isHive(living) || NeuroArmorEventHandler.hasFullSet(living)) return;
        if (!state.getShape(level, pos, CollisionContext.empty()).bounds().intersects(entity.getBoundingBox())) return;
        if (living.getBoundingBox().minY > pos.getY() + 10.0D / 16.0D + .05D) return;
        burst(server, pos);
    }
    @Override public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        super.stepOn(level, pos, state, entity); contact(state, level, pos, entity);
    }
    @Override public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity); contact(state, level, pos, entity);
    }
    @Override public void onProjectileHit(Level level, BlockState state, BlockHitResult hit, Projectile projectile) {
        if (level instanceof ServerLevel server && projectile.mayInteract(level, hit.getBlockPos())) burst(server, hit.getBlockPos());
    }
    public static boolean burst(ServerLevel level, BlockPos pos) {
        BlockState current = level.getBlockState(pos);
        if (!ready(current)) return false;
        BlockState remains = ModBlocks.BIOMASS_REMAINS.get().defaultBlockState();
        BlockState after = level.random.nextFloat() < REMAINS_CONVERSION_CHANCE && remains.canSurvive(level, pos)
                ? remains : current.setValue(BURST, true);
        // Commit the inert state first to prevent re-entrant detonations.
        if (!level.setBlock(pos, after, 3)) return false;
        double x = pos.getX() + .5D, y = pos.getY() + .5D, z = pos.getZ() + .5D;
        level.playSound(null, pos, ModSounds.PUSTULE_BURST.get(), SoundSource.BLOCKS, 1F, 1.0F);
        level.sendParticles(ParticleTypes.SNEEZE, x, y, z, 45, .8, .55, .8, .12);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), x, y, z, 35, .8, .55, .8, .12);
        level.sendParticles(ParticleTypes.ENTITY_EFFECT, x, y, z, 25, .7, .5, .7, .06);
        for (LivingEntity living : level.getEntitiesOfClass(LivingEntity.class, new AABB(x - 3, y - 3, z - 3, x + 3, y + 3, z + 3),
                e -> e.isAlive() && !e.isSpectator()
                        && !NeuralMossBlock.isHive(e)
                        && !NeuroArmorEventHandler.hasFullSet(e)
                        && e.distanceToSqr(x, y, z) <= 9.0D)) {
            if (living instanceof Player player && player.isCreative()) continue;
            if (living instanceof Player player) {
                var data = player.getPersistentData();
                long gameTime = level.getGameTime();
                if (data.getLong(PUSTULE_INFECTION_COOLDOWN) > gameTime) continue;
                data.putLong(PUSTULE_INFECTION_COOLDOWN, gameTime + 20L);
            }
            if (!living.hurt(level.damageSources().magic(), 6F)) {
                if (living instanceof Player player && !player.isCreative()) {
                    PlayerInfectionApi.addInfection(player, 15F);
                }
                continue;
            }
            if (!living.isAlive()) continue;
            living.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 0));
            if (living instanceof Player player) PlayerInfectionApi.addInfection(player, 15F);
        }
        return true;
    }
}
