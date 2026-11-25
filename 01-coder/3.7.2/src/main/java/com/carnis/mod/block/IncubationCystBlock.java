package com.carnis.mod.block;

import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.sounds.SoundSource;
import com.carnis.mod.event.InfectionHandler;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

public final class IncubationCystBlock extends Block {
    private static final int UPDATE_INTERVAL = 20;

    public IncubationCystBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean moving) {
        super.onPlace(state, level, pos, oldState, moving);
        if (!level.isClientSide && !state.is(oldState.getBlock())) level.scheduleTick(pos, this, UPDATE_INTERVAL);
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (!level.getBlockState(pos).is(this)) return;
        AABB area = new AABB(pos).inflate(1.0D);
        double centerX = pos.getX() + 0.5D;
        double centerY = pos.getY() + 0.5D;
        double centerZ = pos.getZ() + 0.5D;
        for (LivingEntity target : level.getEntitiesOfClass(LivingEntity.class, area,
                entity -> entity.isAlive() && entity.distanceToSqr(centerX, centerY, centerZ) <= 1.0D
                        && !(entity instanceof HivemindLinkedMob) && !InfectionHandler.isInfected(entity))) {
            target.hurt(level.damageSources().magic(), 1.0F);
        }
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), pos.getX() + 0.5D, pos.getY() + 0.6D,
                pos.getZ() + 0.5D, 2, 0.25D, 0.2D, 0.25D, 0.01D);
        if (Math.floorMod(level.getGameTime(), 100L) == 0L) {
            level.playSound(null, pos, ModSounds.INCUBATION_CYST_AMBIENT.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        }
        level.scheduleTick(pos, this, UPDATE_INTERVAL);
    }

    @Override
    public void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moving) {
        if (!level.isClientSide && !moving && !state.is(newState.getBlock())) {
            level.playSound(null, pos, ModSounds.INCUBATION_CYST_RUPTURE.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        }
        super.onRemove(state, level, pos, newState, moving);
    }

    @Override
    public int getFlammability(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return 12;
    }

    @Override
    public int getFireSpreadSpeed(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return 4;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(5) == 0) {
            level.addParticle(random.nextBoolean() ? ParticleTypes.CRIMSON_SPORE : ModParticles.BIOMASS_SPARK.get(),
                    pos.getX() + random.nextDouble(), pos.getY() + 0.6D + random.nextDouble() * 0.3D,
                    pos.getZ() + random.nextDouble(), 0.0D, 0.01D, 0.0D);
        }
    }
}
