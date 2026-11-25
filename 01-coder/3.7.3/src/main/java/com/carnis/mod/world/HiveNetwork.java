package com.carnis.mod.world;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.world.infection.InfectionTickQueue;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

/** Persisted, per-dimension position index. Only known positions are visited; no voxel scans. */
public final class HiveNetwork extends SavedData {
    public enum Kind { INFECTION, EYE, POOL, PILLAR }
    private final EnumMap<Kind, Map<Long, Set<Long>>> byChunk = new EnumMap<>(Kind.class);
    private final Set<UUID> deadSentinels = new HashSet<>();
    public HiveNetwork() { for (Kind k : Kind.values()) byChunk.put(k, new HashMap<>()); }
    public static HiveNetwork get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(HiveNetwork::load, HiveNetwork::new, "carnis_hive_network");
    }
    public static HiveNetwork load(CompoundTag tag) {
        HiveNetwork data = new HiveNetwork();
        for (Kind k : Kind.values()) for (long packed : tag.getLongArray(k.name())) data.put(k, BlockPos.of(packed), true);
        var dead = tag.getList("DeadSentinels", net.minecraft.nbt.Tag.TAG_STRING);
        for (int i = 0; i < dead.size(); i++) {
            try { data.deadSentinels.add(UUID.fromString(dead.getString(i))); } catch (IllegalArgumentException ignored) { }
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag tag) {
        for (Kind k : Kind.values()) {
            List<Long> list = new ArrayList<>();
            byChunk.get(k).values().forEach(list::addAll);
            tag.putLongArray(k.name(), list);
        }
        var dead = new net.minecraft.nbt.ListTag();
        deadSentinels.forEach(id -> dead.add(net.minecraft.nbt.StringTag.valueOf(id.toString())));
        tag.put("DeadSentinels", dead);
        return tag;
    }
    public void noteSentinelDeath(UUID id) { if (deadSentinels.add(id)) setDirty(); }
    public boolean consumeSentinelDeath(UUID id) { boolean found = deadSentinels.remove(id); if (found) setDirty(); return found; }
    private boolean put(Kind kind, BlockPos pos, boolean present) {
        long chunk = new ChunkPos(pos).toLong();
        Map<Long, Set<Long>> map = byChunk.get(kind);
        if (present) return map.computeIfAbsent(chunk, k -> new HashSet<>()).add(pos.asLong());
        Set<Long> entries = map.get(chunk);
        if (entries == null || !entries.remove(pos.asLong())) return false;
        if (entries.isEmpty()) map.remove(chunk);
        return true;
    }
    public static void observe(ServerLevel level, BlockPos pos, BlockState state, boolean present) {
        HiveNetwork index = get(level);
        for (Kind kind : Kind.values()) {
            boolean matches = switch (kind) {
                case INFECTION -> InfectionTickQueue.isInfectionSource(state);
                case EYE -> state.is(ModBlocks.HIVE_EYE.get());
                case POOL -> state.is(ModBlocks.STOMACH_POOL.get());
                case PILLAR -> state.is(ModBlocks.NERVE_PILLAR.get());
            };
            if (matches && index.put(kind, pos, present)) {
                index.setDirty();
                if (kind == Kind.INFECTION) for (PulsingHeartBlockEntity heart : nearbyHearts(level, pos, 32)) heart.observeInfection(pos, present);
            }
        }
    }
    /** Register a bounded batch of world-generated tissue after its chunk is live. */
    public static void registerGenerated(ServerLevel level, BlockPos origin, List<BlockPos> positions) {
        HiveNetwork index = get(level);
        List<PulsingHeartBlockEntity> hearts = nearbyHearts(level, origin, 40);
        boolean changed = false;
        for (BlockPos pos : positions) {
            if (!level.hasChunkAt(pos) || !InfectionTickQueue.isInfectionSource(level.getBlockState(pos))) continue;
            changed |= index.put(Kind.INFECTION, pos, true);
            for (PulsingHeartBlockEntity heart : hearts) heart.observeInfection(pos, true);
        }
        if (changed) index.setDirty();
    }
    public List<BlockPos> positions(Kind kind, BlockPos origin, int radius) {
        List<BlockPos> found = new ArrayList<>();
        int minX = (origin.getX() - radius) >> 4, maxX = (origin.getX() + radius) >> 4;
        int minZ = (origin.getZ() - radius) >> 4, maxZ = (origin.getZ() + radius) >> 4;
        for (int x = minX; x <= maxX; x++) for (int z = minZ; z <= maxZ; z++) {
            Set<Long> set = byChunk.get(kind).get(ChunkPos.asLong(x, z));
            if (set == null) continue;
            for (long packed : set) {
                BlockPos p = BlockPos.of(packed);
                if (p.distSqr(origin) <= (double) radius * radius) found.add(p);
            }
        }
        return found;
    }
    public static List<PulsingHeartBlockEntity> nearbyHearts(ServerLevel level, BlockPos origin, int radius) {
        List<PulsingHeartBlockEntity> result = new ArrayList<>();
        int minX = (origin.getX() - radius) >> 4, maxX = (origin.getX() + radius) >> 4;
        int minZ = (origin.getZ() - radius) >> 4, maxZ = (origin.getZ() + radius) >> 4;
        for (int x = minX; x <= maxX; x++) for (int z = minZ; z <= maxZ; z++) {
            var chunk = level.getChunkSource().getChunkNow(x, z);
            if (chunk == null) continue;
            for (var be : chunk.getBlockEntities().values())
                if (be instanceof PulsingHeartBlockEntity heart && heart.getBlockPos().distSqr(origin) <= (double)radius * radius) result.add(heart);
        }
        return result;
    }
    public static PulsingHeartBlockEntity nearestHeart(ServerLevel level, BlockPos pos, int radius) {
        return nearbyHearts(level, pos, radius).stream().min(Comparator.comparingDouble(h -> h.getBlockPos().distSqr(pos))).orElse(null);
    }
    public static BlockPos nearestLoaded(ServerLevel level, Kind kind, BlockPos pos, int radius) {
        BlockPos best = null; double distance = Double.MAX_VALUE;
        for (BlockPos p : get(level).positions(kind, pos, radius)) {
            if (!level.hasChunkAt(p)) continue;
            BlockState state = level.getBlockState(p);
            boolean valid = switch(kind) {
                case INFECTION -> InfectionTickQueue.isInfectionSource(state);
                case EYE -> state.is(ModBlocks.HIVE_EYE.get());
                case POOL -> state.is(ModBlocks.STOMACH_POOL.get());
                case PILLAR -> state.is(ModBlocks.NERVE_PILLAR.get());
            };
            if (!valid) { get(level).put(kind, p, false); get(level).setDirty(); continue; }
            double d = p.distSqr(pos); if (d < distance) { best = p; distance = d; }
        }
        return best;
    }
    public static boolean shielded(ServerLevel level, BlockPos pos) {
        BlockPos pillar = nearestLoaded(level, Kind.PILLAR, pos, 32);
        if (pillar == null) return false;
        if (level.getBlockEntity(pillar) instanceof com.carnis.mod.block.entity.NervePillarBlockEntity organ) organ.discharge(level);
        return true;
    }
}
