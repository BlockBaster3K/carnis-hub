package com.carnis.mod.block;

import com.carnis.mod.block.entity.StomachPoolBlockEntity;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.BlockPathTypes;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import javax.annotation.Nullable;

public final class StomachPoolBlock extends net.minecraft.world.level.block.BaseEntityBlock {
    private static final String POOL_DISSOLVING = "carnis:pool_dissolving";
    private static final String POOL_DISSOLVING_UNTIL = "carnis:pool_dissolving_until";
    private static final String POOL_BIOMASS_AWARDED = "carnis:pool_biomass_awarded";
    private static final int DISSOLVING_DURATION_TICKS = 100;
    @Override public void onPlace(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState old, boolean moving) {
        super.onPlace(state, level, pos, old, moving);
        if (!old.is(state.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
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
    public StomachPoolBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    private static final VoxelShape OUTLINE_SHAPE = Shapes.block();
    private static final VoxelShape COLLISION_SHAPE = Shapes.box(0.0D, 0.0D, 0.0D, 1.0D, 0.25D, 1.0D);

    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return OUTLINE_SHAPE;
    }

    @Override public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return COLLISION_SHAPE;
    }

    @Nullable
    @Override public BlockPathTypes getBlockPathType(BlockState state, BlockGetter level, BlockPos pos, @Nullable Mob mob) {
        return BlockPathTypes.WALKABLE;
    }
    @Override public net.minecraft.world.level.block.RenderShape getRenderShape(BlockState state) { return net.minecraft.world.level.block.RenderShape.MODEL; }
    @Override public net.minecraft.world.level.block.entity.BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new com.carnis.mod.block.entity.StomachPoolBlockEntity(pos, state); }
    @Override public <T extends net.minecraft.world.level.block.entity.BlockEntity> net.minecraft.world.level.block.entity.BlockEntityTicker<T> getTicker(Level level, BlockState state, net.minecraft.world.level.block.entity.BlockEntityType<T> type) {
        return createTickerHelper(type, com.carnis.mod.init.ModBlockEntities.STOMACH_POOL.get(), com.carnis.mod.block.entity.StomachPoolBlockEntity::tick);
    }
    private static void digest(ServerLevel level, BlockPos pos) {
        if (level.getBlockEntity(pos) instanceof com.carnis.mod.block.entity.StomachPoolBlockEntity pool) pool.markDigesting();
    }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        if (!(level instanceof ServerLevel server)) {
            return;
        }
        if (entity instanceof ItemEntity item && item.isAlive() && !item.getItem().isEmpty()) {
            ItemStack stack = item.getItem();
            FoodProperties food = stack.getFoodProperties(null);
            boolean flesh = stack.is(Items.ROTTEN_FLESH) || stack.is(ModItems.LIVING_FLESH.get())
                    || stack.is(ModItems.OSSIFIED_FLESH.get()) || stack.is(ModItems.FIREPROOF_FLESH.get())
                    || food != null && food.isMeat();
            long value = (long) stack.getCount() * (flesh ? 5L : 1L);
            digest(server, pos);
            item.discard();
            CarnisWorldData.get(server).addBiomassPoints(value);
            ModMessages.sendToPlayersInLevel(server);
            server.playSound(null, pos, SoundEvents.GENERIC_SPLASH, SoundSource.BLOCKS, 0.6F, 1.0F);
            server.sendParticles(ParticleTypes.BUBBLE_POP, item.getX(), item.getY(), item.getZ(),
                    8, 0.2D, 0.2D, 0.2D, 0.02D);
        } else if (entity instanceof LivingEntity living && living.tickCount % 20 == 0) {
            if (NeuralMossBlock.isHive(living)) return;
            var heart = com.carnis.mod.world.HiveNetwork.nearestHeart(server, pos, 32);
            boolean mob = living instanceof net.minecraft.world.entity.Mob;
            if (heart != null && mob) {
                living.getPersistentData().putBoolean(POOL_DISSOLVING, true);
                living.getPersistentData().putLong(POOL_DISSOLVING_UNTIL,
                        server.getGameTime() + DISSOLVING_DURATION_TICKS);
            }
            digest(server, pos);
            living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 0));
            living.hurt(server.damageSources().generic(), 1.0F);
            server.sendParticles(ParticleTypes.ITEM_SLIME, living.getX(), living.getY() + 0.1D, living.getZ(),
                    8, 0.2D, 0.1D, 0.2D, 0.02D);
            server.playSound(null, pos, com.carnis.mod.init.ModSounds.ACID_SPLASH.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
            if (heart != null && mob && living.isDeadOrDying()
                    && !living.getPersistentData().getBoolean(POOL_BIOMASS_AWARDED)) {
                living.getPersistentData().putBoolean(POOL_BIOMASS_AWARDED, true);
                long biomass = living instanceof net.minecraft.world.entity.animal.Cow ? 30L : 20L;
                heart.addBiomass(biomass);
            }
        }
    }
}
