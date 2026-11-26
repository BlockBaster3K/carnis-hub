package com.carnis.mod.block.entity;

import com.carnis.mod.block.FleshBulbBlock;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public final class FleshBulbBlockEntity extends BlockEntity {
    private int age;
    private int duration;
    private int nextHeartbeatAge;
    private int pulseTicksRemaining;
    private static final int MIN_HEARTBEAT_INTERVAL_TICKS = 13;
    public FleshBulbBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.FLESH_BULB.get(), pos, state); }
    @Override protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putInt("Age", age);
        tag.putInt("Duration", duration);
        tag.putInt("NextHeartbeatAge", nextHeartbeatAge);
        tag.putInt("PulseTicksRemaining", pulseTicksRemaining);
    }
    @Override public void load(CompoundTag tag) {
        super.load(tag);
        age = Math.max(0, tag.getInt("Age"));
        duration = tag.getInt("Duration");
        nextHeartbeatAge = Math.max(0, tag.getInt("NextHeartbeatAge"));
        pulseTicksRemaining = Math.max(0, Math.min(3, tag.getInt("PulseTicksRemaining")));
    }
    public static void serverTick(Level world, BlockPos pos, BlockState state, FleshBulbBlockEntity bulb) {
        if (!(world instanceof ServerLevel level)) return;
        if (bulb.duration < 1200 || bulb.duration > 1800) bulb.duration = 1200 + level.random.nextInt(601);
        bulb.age++;
        bulb.setChanged();
        if (bulb.age >= bulb.duration) {
            level.playSound(null, pos, ModSounds.ACID_SPLASH.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
            level.sendParticles(ModParticles.BIOMASS_SPARK.get(), pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D,
                    48, .35D, .35D, .35D, .16D);
            int count = 1 + level.random.nextInt(2);
            // Remove once before spawning; prevents a saved mature bulb spawning repeatedly.
            level.removeBlock(pos, false);
            for (int i = 0; i < count; i++) {
                ParasiticTendrilEntity tendril = ModEntities.PARASITIC_TENDRIL.get().create(level);
                if (tendril == null) continue;
                tendril.moveTo(pos.getX() + .5D + (i == 0 ? -0.18D : 0.18D), pos.getY(), pos.getZ() + .5D,
                        level.random.nextFloat() * 360.0F, 0.0F);
                tendril.setPersistenceRequired();
                level.addFreshEntity(tendril);
            }
            return;
        }
        // Accumulate the next onset; a changing modulo would collapse real intervals.
        if (bulb.age >= bulb.nextHeartbeatAge) {
            level.playSound(null, pos, ModSounds.PULSING_HEART_BEAT.get(), SoundSource.BLOCKS,
                    1.0F, 1.0F);
            int nominalInterval = 40 - (int)(30L * bulb.age / bulb.duration);
            int interval = Math.max(MIN_HEARTBEAT_INTERVAL_TICKS, nominalInterval);
            bulb.nextHeartbeatAge = bulb.age + interval;
            bulb.pulseTicksRemaining = 3;
        } else if (bulb.pulseTicksRemaining > 0) {
            bulb.pulseTicksRemaining--;
        }
        boolean pulse = bulb.pulseTicksRemaining > 0;
        if (state.getValue(FleshBulbBlock.PULSING) != pulse)
            level.setBlock(pos, state.setValue(FleshBulbBlock.PULSING, pulse), 3);
    }
}
