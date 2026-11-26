package com.carnis.mod.block;

import com.carnis.mod.block.entity.SporeSproutBlockEntity;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModBlockTags;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.BushBlock;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import javax.annotation.Nullable;

public final class SporeSproutBlock extends BushBlock implements EntityBlock {
    public static final BooleanProperty CLOSED = BooleanProperty.create("closed");
    private static final int MIN_COOLDOWN_TICKS = 250;
    private static final int MAX_COOLDOWN_TICKS = 350;
    private static final VoxelShape SHAPE = Block.box(4, 0, 4, 12, 14, 12);

    public SporeSproutBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(CLOSED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<net.minecraft.world.level.block.Block, BlockState> builder) {
        builder.add(CLOSED);
    }

    @Override
    protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
        return state.is(ModBlockTags.INFECTIOUS_SURFACES) || super.mayPlaceOn(state, level, pos);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new SporeSproutBlockEntity(pos, state);
    }

    @Nullable
    @Override
    @SuppressWarnings("unchecked")
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
            Level level,
            BlockState state,
            BlockEntityType<T> blockEntityType
    ) {
        if (level.isClientSide || blockEntityType != ModBlockEntities.SPORE_SPROUT.get()) return null;
        return (BlockEntityTicker<T>) (BlockEntityTicker<SporeSproutBlockEntity>) SporeSproutBlockEntity::serverTick;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(5) == 0) {
            level.addParticle(ParticleTypes.CRIMSON_SPORE,
                    pos.getX() + random.nextDouble(), pos.getY() + .4D, pos.getZ() + random.nextDouble(), 0, .01D, 0);
        }
    }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        if (!(level instanceof ServerLevel server) || !(entity instanceof Player player) || !player.isAlive()
                || player.isSpectator() || NeuroArmorEventHandler.hasFullSet(player) || state.getValue(CLOSED)) return;
        if (!(server.getBlockEntity(pos) instanceof SporeSproutBlockEntity sprout)
                || sprout.getCooldownTicks() > 0) return;
        if (!server.setBlock(pos, state.setValue(CLOSED, true), 3)) return;

        sprout.startCooldown(MIN_COOLDOWN_TICKS + server.random.nextInt(MAX_COOLDOWN_TICKS - MIN_COOLDOWN_TICKS + 1));
        server.playSound(null, pos, ModSounds.ORGANIC_CREAK.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        server.sendParticles(ParticleTypes.SNEEZE, pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D,
                25, .35D, .35D, .35D, .06D);
        server.sendParticles(ModParticles.BIOMASS_SPARK.get(), pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D,
                10, .2D, .3D, .2D, .04D);
        player.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 80, 0));
        PlayerInfectionApi.addExposure(player, 5F);
    }
}
