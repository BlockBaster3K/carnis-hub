package com.carnis.mod.block.entity;

import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.network.protocol.Packet;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public final class StomachPoolBlockEntity extends BlockEntity {
    private static final int MAX_ATTRACTED = 8;
    private static final int RESERVATION_TTL_TICKS = 600;
    private static final double RESERVATION_EXPIRY_DISTANCE_SQUARED = 16.0D;
    private static final double MAX_RESERVATION_DISTANCE_SQUARED = 256.0D;

    private long activeUntil;
    // UUID -> game time at reservation; transient, as reservations only cover loaded mobs.
    private final Map<UUID, Long> attracted = new HashMap<>();
    // Separate digestion progress, so reservation timestamps remain stable for TTL expiry.
    private final Map<UUID, Integer> insideTicks = new HashMap<>();

    public StomachPoolBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.STOMACH_POOL.get(), pos, state);
    }

    private void pruneAttracted(ServerLevel server) {
        long now = server.getGameTime();
        attracted.entrySet().removeIf(entry -> {
            UUID id = entry.getKey();
            Entity entity = server.getEntity(id);
            if (!(entity instanceof Mob mob) || !mob.isAlive() || mob.isRemoved()
                    || NeuralMossBlock.isHive(mob)) {
                insideTicks.remove(id);
                return true;
            }

            double distanceSquared = mob.distanceToSqr(
                    worldPosition.getX() + 0.5D,
                    worldPosition.getY() + 0.5D,
                    worldPosition.getZ() + 0.5D);
            boolean timedOutBeforeArrival = now - entry.getValue() > RESERVATION_TTL_TICKS
                    && distanceSquared > RESERVATION_EXPIRY_DISTANCE_SQUARED;
            boolean outOfRange = distanceSquared > MAX_RESERVATION_DISTANCE_SQUARED;
            if (timedOutBeforeArrival || outOfRange) insideTicks.remove(id);
            return timedOutBeforeArrival || outOfRange;
        });
        insideTicks.keySet().removeIf(id -> !attracted.containsKey(id));
    }

    public boolean reserve(Mob mob) {
        if (!(level instanceof ServerLevel server) || isRemoved() || !mob.isAlive() || mob.level() != level
                || NeuralMossBlock.isHive(mob)) return false;
        pruneAttracted(server);
        UUID id = mob.getUUID();
        if (attracted.containsKey(id)) return true;
        if (attracted.size() >= MAX_ATTRACTED) return false;
        attracted.put(id, server.getGameTime());
        insideTicks.put(id, 0);
        return true;
    }

    public boolean hasReservation(Mob mob) {
        return !NeuralMossBlock.isHive(mob) && attracted.containsKey(mob.getUUID());
    }

    public void release(Mob mob) {
        UUID id = mob.getUUID();
        attracted.remove(id);
        insideTicks.remove(id);
    }

    /** Вызывается целью удержания один раз за серверный тик внутри бассейна. */
    public boolean countInsideTick(Mob mob) {
        UUID id = mob.getUUID();
        if (NeuralMossBlock.isHive(mob) || !mob.isAlive() || mob.isRemoved()) {
            release(mob);
            return false;
        }
        if (!attracted.containsKey(id)) return false;

        int ticks = insideTicks.getOrDefault(id, 0) + 1;
        if (ticks >= 200) {
            release(mob);
            // Go through the normal damage/death pipeline so death events and loot can run.
            mob.hurt(mob.damageSources().generic(), Float.MAX_VALUE);
            if (mob.isAlive()) mob.kill();
            if (mob.isAlive()) mob.discard();
            return true;
        }
        insideTicks.put(id, ticks);
        return false;
    }

    public boolean isDigesting() {
        return level != null && level.getGameTime() < activeUntil;
    }

    public void markDigesting() {
        if (!(level instanceof ServerLevel server)) return;
        if (activeUntil - server.getGameTime() > 20) return;
        activeUntil = server.getGameTime() + 40;
        setChanged();
        server.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
    }

    public static void tick(Level level, BlockPos pos, BlockState state, StomachPoolBlockEntity pool) {
        if (!level.isClientSide) return;
        boolean active = pool.isDigesting();
        if (level.random.nextInt(active ? 3 : 20) != 0) return;
        double x = pos.getX() + .18 + level.random.nextDouble() * .64;
        double z = pos.getZ() + .18 + level.random.nextDouble() * .64;
        level.addParticle(active && level.random.nextBoolean()
                        ? ModParticles.BIOMASS_SPARK.get() : ParticleTypes.BUBBLE_POP,
                x, pos.getY() + .66, z, 0, .025, 0);
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putLong("ActiveUntil", activeUntil);
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        activeUntil = tag.getLong("ActiveUntil");
    }

    @Override
    public CompoundTag getUpdateTag() {
        return saveWithoutMetadata();
    }

    @Nullable
    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    @Override
    public void onDataPacket(Connection connection, ClientboundBlockEntityDataPacket packet) {
        CompoundTag tag = packet.getTag();
        if (tag != null) load(tag);
    }
}
