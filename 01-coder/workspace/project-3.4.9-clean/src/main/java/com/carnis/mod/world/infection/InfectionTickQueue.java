package com.carnis.mod.world.infection;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.MultifaceBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class InfectionTickQueue {
    public static final int MAX_QUEUE_SIZE = 10000;
    public static final int HEART_CHUNK_PRIORITY_BUDGET = 4;

    private static final long HEART_ACTIVITY_LEASE_TICKS = 2L;
    private static final long FIREPROOF_ADAPTATION_THRESHOLD = 25L;
    private static final double FIREPROOF_BASE_CHANCE = 0.10D;
    private static final double FIREPROOF_CHANCE_PER_LEVEL = 0.01D;
    private static final double FIREPROOF_MAX_CHANCE = 0.75D;

    private static final Direction[] SPREAD_DIRECTIONS = Direction.values();

    private static final Map<MinecraftServer, InfectionTickQueue> INSTANCES =
            new WeakHashMap<>();

    private final Map<ResourceKey<Level>, LinkedHashSet<BlockPos>>
            queuedPositions = new LinkedHashMap<>();

    private final Map<ResourceKey<Level>, LinkedHashMap<Long, Long>>
            activeHeartChunks = new LinkedHashMap<>();

    private final LinkedHashSet<QueuedPosition> heartPriorityPositions =
            new LinkedHashSet<>();

    private int queuedPositionCount;

    private InfectionTickQueue() {
    }

    public static boolean enqueue(ServerLevel serverLevel, BlockPos pos) {
        if (!serverLevel.hasChunkAt(pos)) {
            return false;
        }

        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);
        ChunkPos chunkPos = new ChunkPos(pos);

        if (
                worldData.isChunkShocked(
                        chunkPos,
                        serverLevel.getGameTime()
                )
        ) {
            return false;
        }

        InfectionTickQueue manager = getOrCreate(serverLevel.getServer());
        return manager.enqueueInternal(
                serverLevel.dimension(),
                pos.immutable(),
                serverLevel.getGameTime()
        );
    }

    public static boolean refreshHeartChunk(
            ServerLevel serverLevel,
            BlockPos heartPos
    ) {
        if (!serverLevel.hasChunkAt(heartPos)) {
            return false;
        }

        ChunkPos heartChunk = new ChunkPos(heartPos);
        long currentGameTime = serverLevel.getGameTime();
        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);

        if (worldData.isChunkShocked(heartChunk, currentGameTime)) {
            InfectionTickQueue existingManager = getExisting(
                    serverLevel.getServer()
            );

            if (existingManager != null) {
                existingManager.deactivateHeartChunk(
                        serverLevel.dimension(),
                        heartChunk.toLong()
                );
            }

            return false;
        }

        InfectionTickQueue manager = getOrCreate(serverLevel.getServer());
        manager.refreshHeartChunkInternal(
                serverLevel.dimension(),
                heartChunk.toLong(),
                currentGameTime
        );
        return true;
    }

    public static int enqueueHeartPulse(
            ServerLevel serverLevel,
            BlockPos selectedFleshPos
    ) {
        if (
                !serverLevel.hasChunkAt(selectedFleshPos)
                        || !isInfectionSource(
                                serverLevel.getBlockState(selectedFleshPos)
                        )
        ) {
            return 0;
        }

        int enqueuedPositions = enqueue(
                serverLevel,
                selectedFleshPos
        ) ? 1 : 0;

        for (Direction direction : SPREAD_DIRECTIONS) {
            BlockPos adjacentPos = selectedFleshPos.relative(direction);

            if (
                    !serverLevel.isOutsideBuildHeight(adjacentPos)
                            && serverLevel.hasChunkAt(adjacentPos)
                            && isInfectionSource(
                                    serverLevel.getBlockState(adjacentPos)
                            )
                            && enqueue(serverLevel, adjacentPos)
            ) {
                enqueuedPositions++;
            }
        }

        return enqueuedPositions;
    }

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }

        InfectionTickQueue manager = getExisting(event.getServer());

        if (manager == null) {
            return;
        }

        manager.processQueuedPositions(
                event.getServer(),
                CarnisConfig.SERVER.infectionBlocksPerTick.get()
        );
    }

    @SubscribeEvent
    public static void onServerStopped(ServerStoppedEvent event) {
        synchronized (INSTANCES) {
            INSTANCES.remove(event.getServer());
        }
    }

    private static InfectionTickQueue getOrCreate(MinecraftServer server) {
        synchronized (INSTANCES) {
            return INSTANCES.computeIfAbsent(
                    server,
                    ignored -> new InfectionTickQueue()
            );
        }
    }

    private static InfectionTickQueue getExisting(MinecraftServer server) {
        synchronized (INSTANCES) {
            return INSTANCES.get(server);
        }
    }

    private boolean enqueueInternal(
            ResourceKey<Level> dimension,
            BlockPos pos,
            long currentGameTime
    ) {
        LinkedHashSet<BlockPos> dimensionQueue = queuedPositions.get(
                dimension
        );
        QueuedPosition queuedPosition = new QueuedPosition(dimension, pos);

        if (dimensionQueue != null && dimensionQueue.contains(pos)) {
            prioritizeIfHeartActive(queuedPosition, currentGameTime);
            return false;
        }

        if (queuedPositionCount >= MAX_QUEUE_SIZE) {
            return false;
        }

        if (dimensionQueue == null) {
            dimensionQueue = new LinkedHashSet<>();
            queuedPositions.put(dimension, dimensionQueue);
        }

        if (!dimensionQueue.add(pos)) {
            return false;
        }

        queuedPositionCount++;
        prioritizeIfHeartActive(queuedPosition, currentGameTime);
        return true;
    }

    private void refreshHeartChunkInternal(
            ResourceKey<Level> dimension,
            long chunkKey,
            long currentGameTime
    ) {
        LinkedHashMap<Long, Long> dimensionHeartChunks =
                activeHeartChunks.computeIfAbsent(
                        dimension,
                        ignored -> new LinkedHashMap<>()
                );
        Long previousExpiration = dimensionHeartChunks.put(
                chunkKey,
                currentGameTime + HEART_ACTIVITY_LEASE_TICKS
        );

        if (
                previousExpiration != null
                        && previousExpiration >= currentGameTime
        ) {
            return;
        }

        LinkedHashSet<BlockPos> dimensionQueue = queuedPositions.get(
                dimension
        );

        if (dimensionQueue == null) {
            return;
        }

        for (BlockPos queuedPos : dimensionQueue) {
            if (new ChunkPos(queuedPos).toLong() == chunkKey) {
                heartPriorityPositions.add(
                        new QueuedPosition(dimension, queuedPos)
                );
            }
        }
    }

    private void deactivateHeartChunk(
            ResourceKey<Level> dimension,
            long chunkKey
    ) {
        LinkedHashMap<Long, Long> dimensionHeartChunks =
                activeHeartChunks.get(dimension);

        if (
                dimensionHeartChunks == null
                        || dimensionHeartChunks.remove(chunkKey) == null
        ) {
            return;
        }

        if (dimensionHeartChunks.isEmpty()) {
            activeHeartChunks.remove(dimension);
        }

        removeHeartPrioritiesForChunk(dimension, chunkKey);
    }

    private void prioritizeIfHeartActive(
            QueuedPosition queuedPosition,
            long currentGameTime
    ) {
        long chunkKey = new ChunkPos(queuedPosition.pos()).toLong();

        if (
                isHeartChunkActive(
                        queuedPosition.dimension(),
                        chunkKey,
                        currentGameTime
                )
        ) {
            heartPriorityPositions.add(queuedPosition);
        }
    }

    private boolean isHeartChunkActive(
            ResourceKey<Level> dimension,
            long chunkKey,
            long currentGameTime
    ) {
        Map<Long, Long> dimensionHeartChunks = activeHeartChunks.get(
                dimension
        );

        if (dimensionHeartChunks == null) {
            return false;
        }

        Long expirationGameTime = dimensionHeartChunks.get(chunkKey);
        return expirationGameTime != null
                && expirationGameTime >= currentGameTime;
    }

    private void expireInactiveHeartChunks(MinecraftServer server) {
        Iterator<Map.Entry<ResourceKey<Level>, LinkedHashMap<Long, Long>>>
                dimensionIterator = activeHeartChunks.entrySet().iterator();

        while (dimensionIterator.hasNext()) {
            Map.Entry<ResourceKey<Level>, LinkedHashMap<Long, Long>> entry =
                    dimensionIterator.next();
            ServerLevel serverLevel = server.getLevel(entry.getKey());

            if (serverLevel == null) {
                ResourceKey<Level> missingDimension = entry.getKey();
                dimensionIterator.remove();
                heartPriorityPositions.removeIf(
                        queuedPosition -> queuedPosition.dimension().equals(
                                missingDimension
                        )
                );
                continue;
            }

            long currentGameTime = serverLevel.getGameTime();
            Iterator<Map.Entry<Long, Long>> chunkIterator =
                    entry.getValue().entrySet().iterator();

            while (chunkIterator.hasNext()) {
                Map.Entry<Long, Long> chunkEntry = chunkIterator.next();

                if (chunkEntry.getValue() < currentGameTime) {
                    long expiredChunkKey = chunkEntry.getKey();
                    chunkIterator.remove();
                    removeHeartPrioritiesForChunk(
                            entry.getKey(),
                            expiredChunkKey
                    );
                }
            }

            if (entry.getValue().isEmpty()) {
                dimensionIterator.remove();
            }
        }
    }

    private void removeHeartPrioritiesForChunk(
            ResourceKey<Level> dimension,
            long chunkKey
    ) {
        heartPriorityPositions.removeIf(
                queuedPosition -> queuedPosition.dimension().equals(dimension)
                        && new ChunkPos(queuedPosition.pos()).toLong()
                        == chunkKey
        );
    }

    private void processQueuedPositions(
            MinecraftServer server,
            int maxPositions
    ) {
        expireInactiveHeartChunks(server);

        if (maxPositions <= 0 || queuedPositionCount == 0) {
            return;
        }

        List<QueuedPosition> batch = drainBatch(server, maxPositions);

        for (QueuedPosition queuedPosition : batch) {
            ServerLevel serverLevel = server.getLevel(
                    queuedPosition.dimension()
            );

            if (serverLevel != null) {
                processPosition(serverLevel, queuedPosition.pos());
            }
        }
    }

    private List<QueuedPosition> drainBatch(
            MinecraftServer server,
            int maxPositions
    ) {
        List<QueuedPosition> batch = new ArrayList<>(
                Math.min(maxPositions, queuedPositionCount)
        );

        drainHeartPriorityPositions(
                server,
                batch,
                Math.min(HEART_CHUNK_PRIORITY_BUDGET, maxPositions)
        );

        while (
                batch.size() < maxPositions
                        && queuedPositionCount > 0
                        && !queuedPositions.isEmpty()
        ) {
            boolean removedPositionThisPass = false;
            Iterator<Map.Entry<ResourceKey<Level>, LinkedHashSet<BlockPos>>>
                    dimensionIterator = queuedPositions.entrySet().iterator();

            while (
                    dimensionIterator.hasNext()
                            && batch.size() < maxPositions
            ) {
                Map.Entry<ResourceKey<Level>, LinkedHashSet<BlockPos>> entry =
                        dimensionIterator.next();
                LinkedHashSet<BlockPos> dimensionQueue = entry.getValue();

                if (server.getLevel(entry.getKey()) == null) {
                    ResourceKey<Level> missingDimension = entry.getKey();
                    queuedPositionCount -= dimensionQueue.size();
                    dimensionIterator.remove();
                    heartPriorityPositions.removeIf(
                            queuedPosition -> queuedPosition.dimension().equals(
                                    missingDimension
                            )
                    );
                    continue;
                }

                Iterator<BlockPos> positionIterator =
                        dimensionQueue.iterator();

                if (positionIterator.hasNext()) {
                    BlockPos pos = positionIterator.next();
                    QueuedPosition queuedPosition = new QueuedPosition(
                            entry.getKey(),
                            pos
                    );
                    positionIterator.remove();
                    heartPriorityPositions.remove(queuedPosition);
                    queuedPositionCount--;
                    removedPositionThisPass = true;
                    batch.add(queuedPosition);
                }

                if (dimensionQueue.isEmpty()) {
                    dimensionIterator.remove();
                }
            }

            if (!removedPositionThisPass) {
                break;
            }
        }

        return batch;
    }

    private void drainHeartPriorityPositions(
            MinecraftServer server,
            List<QueuedPosition> batch,
            int priorityBudget
    ) {
        Iterator<QueuedPosition> priorityIterator =
                heartPriorityPositions.iterator();

        while (
                priorityIterator.hasNext()
                        && batch.size() < priorityBudget
        ) {
            QueuedPosition queuedPosition = priorityIterator.next();
            ServerLevel serverLevel = server.getLevel(
                    queuedPosition.dimension()
            );
            LinkedHashSet<BlockPos> dimensionQueue = queuedPositions.get(
                    queuedPosition.dimension()
            );
            long chunkKey = new ChunkPos(queuedPosition.pos()).toLong();

            if (
                    serverLevel == null
                            || dimensionQueue == null
                            || !isHeartChunkActive(
                                    queuedPosition.dimension(),
                                    chunkKey,
                                    serverLevel.getGameTime()
                            )
                            || !dimensionQueue.remove(queuedPosition.pos())
            ) {
                priorityIterator.remove();
                continue;
            }

            priorityIterator.remove();
            queuedPositionCount--;
            batch.add(queuedPosition);

            if (dimensionQueue.isEmpty()) {
                queuedPositions.remove(queuedPosition.dimension());
            }
        }
    }

    // Vein propagation and mutation are exclusively driven by block random ticks.
    private void processPosition(ServerLevel serverLevel, BlockPos sourcePos) {
    }

    public static boolean isInfectionSource(BlockState state) {
        return state.is(ModBlocks.LIVING_FLESH.get())
                || state.is(ModBlocks.OSSIFIED_FLESH.get())
                || state.is(ModBlocks.FIREPROOF_FLESH.get())
                || state.is(ModBlocks.FLESH_VEINS.get());
    }

    private static BlockState getInfectedState(
            ServerLevel serverLevel,
            CarnisWorldData worldData,
            BlockState targetState
    ) {
        if (targetState.is(Blocks.GRASS_BLOCK)
                || targetState.is(Blocks.DIRT)
                || targetState.is(Blocks.STONE)
                || targetState.is(Blocks.DEEPSLATE)) {
            return selectFleshState(serverLevel, worldData);
        }

        if (targetState.is(BlockTags.LOGS)) {
            return null;
        }

        if (targetState.canBeReplaced() && targetState.getFluidState().isEmpty()) {
            return ModBlocks.LIVING_FLESH.get().defaultBlockState();
        }

        return null;
    }

    private static BlockState selectFleshState(
            ServerLevel serverLevel,
            CarnisWorldData worldData
    ) {
        long fireAdaptation = worldData.getFireAdaptation();

        if (fireAdaptation < FIREPROOF_ADAPTATION_THRESHOLD) {
            return ModBlocks.LIVING_FLESH.get().defaultBlockState();
        }

        double fireproofChance = Math.min(
                FIREPROOF_MAX_CHANCE,
                FIREPROOF_BASE_CHANCE
                        + (fireAdaptation - FIREPROOF_ADAPTATION_THRESHOLD)
                        * FIREPROOF_CHANCE_PER_LEVEL
        );

        if (serverLevel.getRandom().nextDouble() < fireproofChance) {
            return ModBlocks.FIREPROOF_FLESH.get().defaultBlockState();
        }

        return ModBlocks.LIVING_FLESH.get().defaultBlockState();
    }

    private record QueuedPosition(
            ResourceKey<Level> dimension,
            BlockPos pos
    ) {
    }
}
