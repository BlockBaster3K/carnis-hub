package com.carnis.mod.capability.biomass;

import net.minecraft.nbt.CompoundTag;

/** Персональные очки биомассы без привязки к игроку или миру. */
public final class PlayerBiomassData {
    private static final String BIOMASS_POINTS = "BiomassPoints";
    private long biomassPoints = 0L;

    public long getBiomassPoints() {
        return biomassPoints;
    }

    public void setBiomassPoints(long amount) {
        if (amount < 0L) {
            throw new IllegalArgumentException("amount must not be negative");
        }
        biomassPoints = amount;
    }

    public void addBiomassPoints(long amount) {
        if (amount < 0L) {
            throw new IllegalArgumentException("amount must not be negative");
        }
        biomassPoints = amount > Long.MAX_VALUE - biomassPoints
                ? Long.MAX_VALUE : biomassPoints + amount;
    }

    public CompoundTag serializeNBT() {
        CompoundTag tag = new CompoundTag();
        tag.putLong(BIOMASS_POINTS, biomassPoints);
        return tag;
    }

    public void deserializeNBT(CompoundTag nbt) {
        biomassPoints = Math.max(0L, nbt.getLong(BIOMASS_POINTS));
    }
}
