package com.carnis.mod.world;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public final class CarnisWorldData extends SavedData {
    public static final String DATA_NAME = "carnis_world_data";

    public static final long SYNAPSE_SHOCK_DURATION_TICKS = 180L * 20L;
    public static final int SYNAPSE_SHOCK_RADIUS_CHUNKS = 1;

    private static final int DATA_VERSION = 1;

    private static final String TAG_DATA_VERSION = "DataVersion";
    private static final String TAG_BIOMASS_POINTS = "BiomassPoints";
    private static final String TAG_ADAPTATION = "Adaptation";
    private static final String TAG_FIRE = "Fire";
    private static final String TAG_RANGED = "Ranged";
    private static final String TAG_MELEE = "Melee";
    private static final String TAG_PILLARING = "Pillaring";
    private static final String TAG_EXPLOSIVE = "Explosive";
    private static final String TAG_DARK = "Dark";
    private static final String TAG_SHOCKED_CHUNKS = "ShockedChunks";
    private static final String TAG_CHUNK_X = "ChunkX";
    private static final String TAG_CHUNK_Z = "ChunkZ";
    private static final String TAG_EXPIRES_AT = "ExpiresAt";

    private long biomassPoints;

    private long fireAdaptation;
    private long rangedAdaptation;
    private long meleeAdaptation;
    private long pillaringAdaptation;
    private long explosiveAdaptation;
    private long darkAdaptation;

    private final Map<ChunkPos, Long> shockedChunks = new HashMap<>();
    // Ephemeral per-dimension cooldowns. Expired entries are pruned on use;
    // no world chunks are loaded or kept alive by this map.
    private final Map<AdaptationCooldownKey, Long> adaptationCooldowns = new HashMap<>();

    private record AdaptationCooldownKey(ChunkPos chunk, AdaptationType type) {
    }

    public boolean tryAwardDamageAdaptation(ChunkPos chunk, AdaptationType type, long tick) {
        Objects.requireNonNull(chunk, "chunk");
        Objects.requireNonNull(type, "type");
        adaptationCooldowns.entrySet().removeIf(entry -> tick < entry.getValue()
                || tick - entry.getValue() >= 10L);
        AdaptationCooldownKey key = new AdaptationCooldownKey(chunk, type);
        if (adaptationCooldowns.containsKey(key)) {
            return false;
        }
        adaptationCooldowns.put(key, tick);
        incrementAdaptation(type);
        return true;
    }

    public void decayAdaptation(AdaptationType type, long amount) {
        requireNonNegative(amount, "amount");
        long value = getAdaptation(type);
        setAdaptation(type, value - Math.min(value, amount));
    }

    /** Log-interpolated between the specified resistance milestones. */
    public static float damageMitigation(long points) {
        long[] thresholds = {0L, 100L, 300L, 600L, 1000L};
        double[] resistance = {0.0D, 0.25D, 0.50D, 0.70D, 0.80D};
        double p = Math.max(0L, points);
        if (p >= 1000.0D) {
            return 0.80F;
        }
        for (int i = 1; i < thresholds.length; i++) {
            if (p <= thresholds[i]) {
                double start = Math.log1p(thresholds[i - 1]);
                double end = Math.log1p(thresholds[i]);
                double fraction = (Math.log1p(p) - start) / (end - start);
                return (float) Math.min(0.80D, Math.max(0.0D,
                        resistance[i - 1] + fraction * (resistance[i] - resistance[i - 1])));
            }
        }
        return 0.80F;
    }

    public CarnisWorldData() {
    }

    public static CarnisWorldData get(ServerLevel level) {
        Objects.requireNonNull(level, "level");
        return level.getDataStorage().computeIfAbsent(
                CarnisWorldData::load,
                CarnisWorldData::new,
                DATA_NAME
        );
    }

    public static CarnisWorldData load(CompoundTag rootTag) {
        CarnisWorldData data = new CarnisWorldData();

        data.biomassPoints = nonNegative(rootTag.getLong(TAG_BIOMASS_POINTS));

        if (rootTag.contains(TAG_ADAPTATION, Tag.TAG_COMPOUND)) {
            CompoundTag adaptationTag = rootTag.getCompound(TAG_ADAPTATION);
            data.fireAdaptation = nonNegative(adaptationTag.getLong(TAG_FIRE));
            data.rangedAdaptation = nonNegative(adaptationTag.getLong(TAG_RANGED));
            data.meleeAdaptation = nonNegative(adaptationTag.getLong(TAG_MELEE));
            data.pillaringAdaptation = nonNegative(adaptationTag.getLong(TAG_PILLARING));
            data.explosiveAdaptation = nonNegative(adaptationTag.getLong(TAG_EXPLOSIVE));
            data.darkAdaptation = nonNegative(adaptationTag.getLong(TAG_DARK));
        }

        ListTag shockedChunksTag = rootTag.getList(
                TAG_SHOCKED_CHUNKS,
                Tag.TAG_COMPOUND
        );

        for (int index = 0; index < shockedChunksTag.size(); index++) {
            CompoundTag chunkTag = shockedChunksTag.getCompound(index);
            long expiresAt = chunkTag.getLong(TAG_EXPIRES_AT);

            if (expiresAt <= 0L) {
                continue;
            }

            ChunkPos chunkPos = new ChunkPos(
                    chunkTag.getInt(TAG_CHUNK_X),
                    chunkTag.getInt(TAG_CHUNK_Z)
            );

            data.shockedChunks.merge(chunkPos, expiresAt, Math::max);
        }

        return data;
    }

    @Override
    public CompoundTag save(CompoundTag rootTag) {
        rootTag.putInt(TAG_DATA_VERSION, DATA_VERSION);
        rootTag.putLong(TAG_BIOMASS_POINTS, biomassPoints);

        CompoundTag adaptationTag = new CompoundTag();
        adaptationTag.putLong(TAG_FIRE, fireAdaptation);
        adaptationTag.putLong(TAG_RANGED, rangedAdaptation);
        adaptationTag.putLong(TAG_MELEE, meleeAdaptation);
        adaptationTag.putLong(TAG_PILLARING, pillaringAdaptation);
        adaptationTag.putLong(TAG_EXPLOSIVE, explosiveAdaptation);
        adaptationTag.putLong(TAG_DARK, darkAdaptation);
        rootTag.put(TAG_ADAPTATION, adaptationTag);

        ListTag shockedChunksTag = new ListTag();
        shockedChunks.entrySet().stream()
                .sorted(
                        Comparator
                                .comparingInt(
                                        (Map.Entry<ChunkPos, Long> entry) ->
                                                entry.getKey().x
                                )
                                .thenComparingInt(entry -> entry.getKey().z)
                )
                .forEach(entry -> {
                    CompoundTag chunkTag = new CompoundTag();
                    chunkTag.putInt(TAG_CHUNK_X, entry.getKey().x);
                    chunkTag.putInt(TAG_CHUNK_Z, entry.getKey().z);
                    chunkTag.putLong(TAG_EXPIRES_AT, entry.getValue());
                    shockedChunksTag.add(chunkTag);
                });
        rootTag.put(TAG_SHOCKED_CHUNKS, shockedChunksTag);

        return rootTag;
    }

    public long getBiomassPoints() {
        return biomassPoints;
    }

    public void setBiomassPoints(long points) {
        requireNonNegative(points, "points");

        if (biomassPoints != points) {
            biomassPoints = points;
            setDirty();
        }
    }

    public long addBiomassPoints(long points) {
        requireNonNegative(points, "points");
        long updatedPoints = saturatingAdd(biomassPoints, points);

        if (updatedPoints != biomassPoints) {
            biomassPoints = updatedPoints;
            setDirty();
        }

        return biomassPoints;
    }

    public boolean tryConsumeBiomassPoints(long points) {
        requireNonNegative(points, "points");

        if (biomassPoints < points) {
            return false;
        }

        if (points > 0L) {
            biomassPoints -= points;
            setDirty();
        }

        return true;
    }

    public long getAdaptation(AdaptationType type) {
        Objects.requireNonNull(type, "type");

        return switch (type) {
            case FIRE -> fireAdaptation;
            case RANGED -> rangedAdaptation;
            case MELEE -> meleeAdaptation;
            case PILLARING -> pillaringAdaptation;
            case EXPLOSIVE -> explosiveAdaptation;
            case DARK -> darkAdaptation;
        };
    }

    public long setAdaptation(AdaptationType type, long value) {
        Objects.requireNonNull(type, "type");
        requireNonNegative(value, "value");

        if (getAdaptation(type) != value) {
            setAdaptationValue(type, value);
            setDirty();
        }

        return getAdaptation(type);
    }

    public long addAdaptation(AdaptationType type, long amount) {
        Objects.requireNonNull(type, "type");
        requireNonNegative(amount, "amount");

        long currentValue = getAdaptation(type);
        long updatedValue = saturatingAdd(currentValue, amount);

        if (updatedValue != currentValue) {
            setAdaptationValue(type, updatedValue);
            setDirty();
        }

        return updatedValue;
    }

    public long incrementAdaptation(AdaptationType type) {
        return addAdaptation(type, 1L);
    }

    public void resetAdaptations() {
        boolean changed = fireAdaptation != 0L
                || rangedAdaptation != 0L
                || meleeAdaptation != 0L
                || pillaringAdaptation != 0L
                || explosiveAdaptation != 0L
                || darkAdaptation != 0L;

        if (!changed) {
            return;
        }

        fireAdaptation = 0L;
        rangedAdaptation = 0L;
        meleeAdaptation = 0L;
        pillaringAdaptation = 0L;
        explosiveAdaptation = 0L;
        darkAdaptation = 0L;
        setDirty();
    }

    public long getFireAdaptation() {
        return fireAdaptation;
    }

    public long getRangedAdaptation() {
        return rangedAdaptation;
    }

    public long getMeleeAdaptation() {
        return meleeAdaptation;
    }

    public long getPillaringAdaptation() {
        return pillaringAdaptation;
    }

    public long getExplosiveAdaptation() {
        return explosiveAdaptation;
    }

    public long getDarkAdaptation() {
        return darkAdaptation;
    }

    public Map<ChunkPos, Long> getShockedChunks() {
        return Collections.unmodifiableMap(shockedChunks);
    }

    /**
     * Shocks the center chunk and every horizontal neighbor at Chebyshev
     * distance one: an inclusive 3-by-3 square of nine whole chunks. The
     * expiry is extended to exactly 3,600 ticks (180 seconds) from the
     * supplied game time.
     */
    public void shockSynapseArea(ChunkPos center, long currentGameTime) {
        shockChunkArea(
                center,
                SYNAPSE_SHOCK_RADIUS_CHUNKS,
                currentGameTime
        );
    }

    public int shockChunkArea(
            ChunkPos center,
            int radiusChunks,
            long currentGameTime
    ) {
        Objects.requireNonNull(center, "center");
        requireNonNegative(currentGameTime, "currentGameTime");

        if (radiusChunks < 0) {
            throw new IllegalArgumentException(
                    "radiusChunks must not be negative"
            );
        }

        long expiresAt = saturatingAdd(
                currentGameTime,
                SYNAPSE_SHOCK_DURATION_TICKS
        );
        int changedChunks = 0;

        for (
                int offsetX = -radiusChunks;
                offsetX <= radiusChunks;
                offsetX++
        ) {
            for (
                    int offsetZ = -radiusChunks;
                    offsetZ <= radiusChunks;
                    offsetZ++
            ) {
                ChunkPos affectedChunk = new ChunkPos(
                        center.x + offsetX,
                        center.z + offsetZ
                );
                Long previousExpiration = shockedChunks.get(affectedChunk);

                if (
                        previousExpiration == null
                                || previousExpiration < expiresAt
                ) {
                    shockedChunks.put(affectedChunk, expiresAt);
                    changedChunks++;
                }
            }
        }

        if (changedChunks > 0) {
            setDirty();
        }

        return changedChunks;
    }

    /** Extends, but never shortens, an existing shock. */
    public boolean shockChunkFor(ChunkPos chunk, long currentGameTime, long durationTicks) {
        Objects.requireNonNull(chunk, "chunk");
        requireNonNegative(currentGameTime, "currentGameTime");
        requireNonNegative(durationTicks, "durationTicks");
        long expiry = saturatingAdd(currentGameTime, durationTicks);
        Long old = shockedChunks.get(chunk);
        if (old != null && old >= expiry) return false;
        shockedChunks.put(chunk, expiry);
        setDirty();
        return true;
    }

    /** Add shock duration without discarding the remaining active duration. */
    public void extendChunkShock(ChunkPos chunk, long now, long extraTicks) {
        Objects.requireNonNull(chunk, "chunk");
        requireNonNegative(now, "now");
        requireNonNegative(extraTicks, "extraTicks");
        long old = shockedChunks.getOrDefault(chunk, now);
        shockedChunks.put(chunk, saturatingAdd(Math.max(now, old), extraTicks));
        setDirty();
    }

    public boolean isChunkShocked(
            ChunkPos chunkPos,
            long currentGameTime
    ) {
        Objects.requireNonNull(chunkPos, "chunkPos");
        requireNonNegative(currentGameTime, "currentGameTime");

        Long expiresAt = shockedChunks.get(chunkPos);

        if (expiresAt == null) {
            return false;
        }

        if (expiresAt > currentGameTime) {
            return true;
        }

        if (shockedChunks.remove(chunkPos, expiresAt)) {
            setDirty();
        }

        return false;
    }

    public boolean halveRemainingShock(ChunkPos chunkPos, long currentGameTime) {
        Objects.requireNonNull(chunkPos, "chunkPos");
        requireNonNegative(currentGameTime, "currentGameTime");
        Long expiry = shockedChunks.get(chunkPos);
        if (expiry == null || expiry <= currentGameTime) {
            return false;
        }
        long remaining = expiry - currentGameTime;
        long shortened = currentGameTime + remaining / 2L;
        if (shortened <= currentGameTime) {
            shockedChunks.remove(chunkPos);
        } else {
            shockedChunks.put(chunkPos, shortened);
        }
        setDirty();
        return true;
    }

    public long getRemainingShockTicks(
            ChunkPos chunkPos,
            long currentGameTime
    ) {
        Objects.requireNonNull(chunkPos, "chunkPos");
        requireNonNegative(currentGameTime, "currentGameTime");

        Long expiresAt = shockedChunks.get(chunkPos);

        if (expiresAt == null || expiresAt <= currentGameTime) {
            if (expiresAt != null && shockedChunks.remove(chunkPos, expiresAt)) {
                setDirty();
            }
            return 0L;
        }

        return expiresAt - currentGameTime;
    }

    public int purgeExpiredShockedChunks(long currentGameTime) {
        requireNonNegative(currentGameTime, "currentGameTime");

        int previousSize = shockedChunks.size();
        shockedChunks.entrySet().removeIf(
                entry -> entry.getValue() <= currentGameTime
        );
        int removedCount = previousSize - shockedChunks.size();

        if (removedCount > 0) {
            setDirty();
        }

        return removedCount;
    }

    public void clearShockedChunks() {
        if (!shockedChunks.isEmpty()) {
            shockedChunks.clear();
            setDirty();
        }
    }

    private void setAdaptationValue(AdaptationType type, long value) {
        switch (type) {
            case FIRE -> fireAdaptation = value;
            case RANGED -> rangedAdaptation = value;
            case MELEE -> meleeAdaptation = value;
            case PILLARING -> pillaringAdaptation = value;
            case EXPLOSIVE -> explosiveAdaptation = value;
            case DARK -> darkAdaptation = value;
        }
    }

    private static long nonNegative(long value) {
        return Math.max(0L, value);
    }

    private static void requireNonNegative(long value, String name) {
        if (value < 0L) {
            throw new IllegalArgumentException(name + " must not be negative");
        }
    }

    private static long saturatingAdd(long current, long amount) {
        if (amount > Long.MAX_VALUE - current) {
            return Long.MAX_VALUE;
        }
        return current + amount;
    }

    public enum AdaptationType {
        FIRE,
        RANGED,
        MELEE,
        PILLARING,
        EXPLOSIVE,
        DARK
    }
}
