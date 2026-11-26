package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent.ServerTickEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.level.ChunkEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.WeakHashMap;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ChunkInfectionEvents {
    private static final int MAX_CHUNKS_PER_TICK = 1;
    private static final long CACHE_TTL_TICKS = 20L;

    // Weak level keys, with values that contain only positions (no strong level reference).
    private static final Map<ServerLevel, Map<Long, CachedBlockScan>> BLOCK_SCAN_CACHE = new WeakHashMap<>();
    private static final Map<ServerLevel, Map<Long, CachedEntities>> ENTITY_CACHE = new WeakHashMap<>();
    private static final Map<ServerLevel, LinkedHashSet<ChunkPos>> pendingChunks = new WeakHashMap<>();

    private ChunkInfectionEvents() { }

    private static final class CachedBlockScan {
        private final long expiresAt;
        private final boolean infected;

        private CachedBlockScan(long expiresAt, boolean infected) {
            this.expiresAt = expiresAt;
            this.infected = infected;
        }
    }

    private static final class CachedEntities {
        private final long expiresAt;
        private final boolean hasCarnisEntity;

        private CachedEntities(long expiresAt, boolean hasCarnisEntity) {
            this.expiresAt = expiresAt;
            this.hasCarnisEntity = hasCarnisEntity;
        }
    }

    private record QueuedChunk(ServerLevel level, ChunkPos pos) { }

    private static boolean isCarnisBlock(BlockState state) {
        ResourceLocation id = ForgeRegistries.BLOCKS.getKey(state.getBlock());
        return id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }

    private static AABB chunkBounds(ServerLevel level, ChunkPos pos) {
        return new AABB(pos.getMinBlockX(), level.getMinBuildHeight(), pos.getMinBlockZ(),
                pos.getMinBlockX() + 16, level.getMaxBuildHeight(), pos.getMinBlockZ() + 16);
    }

    private static boolean containsCarnisBlock(ServerLevel level, LevelChunk chunk) {
        long now = level.getGameTime();
        long key = chunk.getPos().toLong();
        synchronized (BLOCK_SCAN_CACHE) {
            Map<Long, CachedBlockScan> levelCache = BLOCK_SCAN_CACHE.computeIfAbsent(level, ignored -> new HashMap<>());
            CachedBlockScan cached = levelCache.get(key);
            if (cached != null && now < cached.expiresAt) return cached.infected;

            boolean found = false;
            for (LevelChunkSection section : chunk.getSections()) {
                if (section == null || section.hasOnlyAir()
                        || !section.maybeHas(ChunkInfectionEvents::isCarnisBlock)) continue;
                // maybeHas can match an unused palette entry, so confirm actual block cells.
                for (int x = 0; x < 16 && !found; x++) {
                    for (int y = 0; y < 16 && !found; y++) {
                        for (int z = 0; z < 16; z++) {
                            if (isCarnisBlock(section.getBlockState(x, y, z))) {
                                found = true;
                                break;
                            }
                        }
                    }
                }
                if (found) break;
            }

            levelCache.entrySet().removeIf(entry -> entry.getValue().expiresAt <= now);
            levelCache.put(key, new CachedBlockScan(now + CACHE_TTL_TICKS, found));
            return found;
        }
    }

    private static boolean hasCarnisEntity(ServerLevel level, ChunkPos pos, AABB box) {
        long now = level.getGameTime();
        long key = pos.toLong();
        synchronized (ENTITY_CACHE) {
            Map<Long, CachedEntities> levelCache = ENTITY_CACHE.computeIfAbsent(level, ignored -> new HashMap<>());
            CachedEntities cached = levelCache.get(key);
            if (cached != null && now < cached.expiresAt) return cached.hasCarnisEntity;

            boolean found = !level.getEntitiesOfClass(LivingEntity.class, box, entity -> {
                ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
                return entity instanceof HivemindLinkedMob
                        || (id != null && CarnisMod.MOD_ID.equals(id.getNamespace()));
            }).isEmpty();

            levelCache.entrySet().removeIf(entry -> entry.getValue().expiresAt <= now);
            levelCache.put(key, new CachedEntities(now + CACHE_TTL_TICKS, found));
            return found;
        }
    }

    private static void queueChunk(ServerLevel level, ChunkPos pos) {
        synchronized (pendingChunks) {
            pendingChunks.computeIfAbsent(level, ignored -> new LinkedHashSet<>())
                    .add(new ChunkPos(pos.x, pos.z));
        }
    }

    @SubscribeEvent
    public static void onChunkLoad(ChunkEvent.Load event) {
        if (!(event.getLevel() instanceof ServerLevel level)) return;
        queueChunk(level, event.getChunk().getPos());
    }

    @SubscribeEvent
    public static void onServerTick(ServerTickEvent event) {
        if (event.phase == net.minecraftforge.event.TickEvent.Phase.END) processPendingChunks();
    }

    /** Prewarm no more than MAX_CHUNKS_PER_TICK queued chunks; direct cache misses remain synchronous. */
    private static void processPendingChunks() {
        for (int processed = 0; processed < MAX_CHUNKS_PER_TICK; processed++) {
            QueuedChunk queued = pollPendingChunk();
            if (queued == null) return;

            ServerLevel level = queued.level();
            ChunkPos pos = queued.pos();
            long startedAt = System.nanoTime();
            LevelChunk chunk = level.getChunkSource().getChunkNow(pos.x, pos.z);
            if (chunk == null) {
                logIfSlow("chunk prewarm lookup", startedAt);
                continue;
            }

            // maybeHas skips empty/non-hive sections before any 4096-cell verification pass.
            hasCarnisEntity(level, pos, chunkBounds(level, pos));
            containsCarnisBlock(level, chunk);
            logIfSlow("chunk prewarm", startedAt);
        }
    }

    private static QueuedChunk pollPendingChunk() {
        synchronized (pendingChunks) {
            var levels = pendingChunks.entrySet().iterator();
            while (levels.hasNext()) {
                Map.Entry<ServerLevel, LinkedHashSet<ChunkPos>> entry = levels.next();
                if (entry.getValue().isEmpty()) {
                    levels.remove();
                    continue;
                }
                ServerLevel level = entry.getKey();
                var positions = entry.getValue().iterator();
                ChunkPos pos = positions.next();
                positions.remove();
                if (entry.getValue().isEmpty()) levels.remove();
                return new QueuedChunk(level, pos);
            }
            return null;
        }
    }

    public static boolean infectedChunk(ServerLevel level, ChunkPos pos) {
        long startedAt = System.nanoTime();
        LevelChunk chunk = level.getChunkSource().getChunkNow(pos.x, pos.z);
        if (chunk == null) {
            logIfSlow("infectedChunk lookup", startedAt);
            return false;
        }
        boolean hasEntity = hasCarnisEntity(level, pos, chunkBounds(level, pos));
        boolean infected = hasEntity || containsCarnisBlock(level, chunk);
        logIfSlow("infectedChunk lookup", startedAt);
        return infected;
    }

    private static void logIfSlow(String operation, long startedAt) {
        long elapsed = System.nanoTime() - startedAt;
        if (elapsed > 1_000_000L) {
            CarnisMod.LOGGER.debug("Slow chunk op: {} took {} ms", operation, elapsed / 1_000_000.0D);
        }
    }

    @SubscribeEvent
    public static void onDetonate(ExplosionEvent.Detonate event) {
        if (!(event.getLevel() instanceof ServerLevel level)) return;
        BlockPos center = BlockPos.containing(event.getExplosion().getPosition());
        ChunkPos chunk = new ChunkPos(center);
        if (!infectedChunk(level, chunk)) return;
        CarnisWorldData data = CarnisWorldData.get(level);
        data.shockChunkFor(chunk, level.getGameTime(), 600L);
        data.addAdaptation(CarnisWorldData.AdaptationType.EXPLOSIVE, 35L);
        ModMessages.sendToPlayersInLevel(level);
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onDeath(LivingDeathEvent event) {
        if (event.isCanceled() || !(event.getEntity().level() instanceof ServerLevel level)) return;
        LivingEntity entity = event.getEntity();
        if (entity.getPersistentData().getBoolean("carnis:pool_dissolving")
                && entity.getPersistentData().getLong("carnis:pool_dissolving_until") >= level.getGameTime()) return;
        BlockPos pos = entity.blockPosition();
        if (!level.getBlockState(pos).is(ModBlocks.STOMACH_POOL.get())
                && !infectedChunk(level, new ChunkPos(pos))) return;
        CarnisWorldData.get(level).addBiomassPoints(entity instanceof Player ? 100L : 20L);
        ModMessages.sendToPlayersInLevel(level);
    }
}
