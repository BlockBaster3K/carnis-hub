package com.carnis.mod.world.infection;

import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.MultifaceBlock;
import net.minecraft.world.level.block.state.BlockState;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.WeakHashMap;

/** Bounded, random-tick-driven vein growth and observed-coverage mutation. */
public final class VeinMutationEngine {
    private static final int ANCHOR_RADIUS = 4;
    private static final long MUTATION_TICKS = 200L;
    private static final long BIOMASS_COST = 5L;
    private static final int MAX_TRACKED = 10000;
    private static final Direction[] DIRECTIONS = Direction.values();
    private static final Map<net.minecraft.server.MinecraftServer, LinkedHashMap<Key, Observation>> TRACKED = new WeakHashMap<>();

    private VeinMutationEngine() { }

    private record Key(ResourceKey<Level> dimension, BlockPos pos) { }
    private record Observation(BlockState host, int faces, long since) { }
    private enum Anchor { FOUND, MISSING, UNKNOWN }

    public static void tickVein(ServerLevel level, BlockPos pos, BlockState state, RandomSource random) {
        Anchor anchor = findAnchor(level, pos);
        if (anchor == Anchor.MISSING) {
            level.removeBlock(pos, false);
            return;
        }
        if (anchor != Anchor.FOUND || shocked(level, pos)) return;
        for (Direction direction : DIRECTIONS) {
            if (MultifaceBlock.hasFace(state, direction)) {
                BlockPos host = pos.relative(direction);
                if (loaded(level, host)) observeHost(level, host);
            }
        }
        spread(level, pos, random);
    }

    /** Called by a flesh block's random tick to seed veins on neighboring hosts. */
    public static void tickFlesh(ServerLevel level, BlockPos pos, RandomSource random) {
        if (!shocked(level, pos)) spread(level, pos, random);
    }

    private static void observeHost(ServerLevel level, BlockPos hostPos) {
        var map = TRACKED.computeIfAbsent(level.getServer(), ignored -> new LinkedHashMap<>());
        Key key = new Key(level.dimension(), hostPos.immutable());
        BlockState host = level.getBlockState(hostPos);
        int faces = 0;
        boolean complete = true;
        for (Direction direction : DIRECTIONS) {
            BlockPos outside = hostPos.relative(direction);
            if (!loaded(level, outside)) { complete = false; continue; }
            BlockState vein = level.getBlockState(outside);
            if (vein.is(ModBlocks.FLESH_VEINS.get()) && MultifaceBlock.hasFace(vein, direction.getOpposite()))
                faces |= 1 << direction.ordinal();
        }
        if (!complete || faces == 0 || !eligibleHost(level, hostPos, host) || shocked(level, hostPos)) {
            map.remove(key);
            return;
        }
        long now = level.getGameTime();
        Observation old = map.get(key);
        if (old == null || !old.host().equals(host) || old.faces() != faces || now < old.since()) {
            if (old == null && map.size() >= MAX_TRACKED) map.remove(map.keySet().iterator().next());
            map.put(key, new Observation(host, faces, now));
            return;
        }
        if (now - old.since() < MUTATION_TICKS) return;
        CarnisWorldData data = CarnisWorldData.get(level);
        if (!data.tryConsumeBiomassPoints(BIOMASS_COST)) return;
        BlockState replacement = data.getFireAdaptation() >= 300L
                ? ModBlocks.OSSIFIED_FLESH.get().defaultBlockState()
                : ModBlocks.LIVING_FLESH.get().defaultBlockState();
        if (level.setBlockAndUpdate(hostPos, replacement)) {
            map.remove(key);
            ModMessages.sendToPlayersInLevel(level);
        } else {
            data.addBiomassPoints(BIOMASS_COST);
        }
    }

    private static void spread(ServerLevel level, BlockPos source, RandomSource random) {
        int start = random.nextInt(6);
        for (int i = 0; i < 6; i++) {
            BlockPos hostPos = source.relative(DIRECTIONS[(start + i) % 6]);
            if (!loaded(level, hostPos) || shocked(level, hostPos)) continue;
            BlockState host = level.getBlockState(hostPos);
            if (!eligibleHost(level, hostPos, host)) continue;
            int first = random.nextInt(6);
            for (int j = 0; j < 6; j++) {
                Direction face = DIRECTIONS[(first + j) % 6];
                BlockPos outside = hostPos.relative(face);
                if (!loaded(level, outside) || shocked(level, outside) || findAnchor(level, outside) != Anchor.FOUND) continue;
                BlockState existing = level.getBlockState(outside);
                if (forbidden(existing)) continue;
                boolean vein = existing.is(ModBlocks.FLESH_VEINS.get());
                if (!vein && !existing.isAir() && (existing.isSolidRender(level, outside) || !existing.canBeReplaced())) continue;
                BlockState placementBase = vein ? existing : Blocks.AIR.defaultBlockState();
                BlockState result = ModBlocks.FLESH_VEINS.get().getStateForPlacement(
                        placementBase, level, outside, face.getOpposite());
                if (result != null && !result.equals(existing) && level.setBlockAndUpdate(outside, result)) return;
            }
        }
    }

    private static boolean eligibleHost(ServerLevel level, BlockPos pos, BlockState state) {
        float hardness = state.getDestroySpeed(level, pos);
        return !forbidden(state) && !state.isAir() && !state.hasBlockEntity()
                && !InfectionTickQueue.isInfectionSource(state) && state.isSolidRender(level, pos)
                && hardness >= 0.0F && hardness <= 5.0F;
    }

    private static boolean forbidden(BlockState state) {
        return state.is(BlockTags.FIRE) || state.is(BlockTags.PORTALS)
                || state.getBlock() instanceof LiquidBlock || !state.getFluidState().isEmpty();
    }

    private static boolean loaded(ServerLevel level, BlockPos pos) {
        return !level.isOutsideBuildHeight(pos) && level.hasChunkAt(pos);
    }

    private static boolean shocked(ServerLevel level, BlockPos pos) {
        return CarnisWorldData.get(level).isChunkShocked(new ChunkPos(pos), level.getGameTime());
    }

    private static Anchor findAnchor(ServerLevel level, BlockPos center) {
        boolean unknown = false;
        for (int dx = -ANCHOR_RADIUS; dx <= ANCHOR_RADIUS; dx++) {
            for (int dy = -ANCHOR_RADIUS; dy <= ANCHOR_RADIUS; dy++) {
                for (int dz = -ANCHOR_RADIUS; dz <= ANCHOR_RADIUS; dz++) {
                    if (Math.abs(dx) + Math.abs(dy) + Math.abs(dz) > ANCHOR_RADIUS) continue;
                    BlockPos pos = center.offset(dx, dy, dz);
                    if (level.isOutsideBuildHeight(pos)) continue;
                    if (!level.hasChunkAt(pos)) { unknown = true; continue; }
                    BlockState state = level.getBlockState(pos);
                    if (state.is(ModBlocks.LIVING_FLESH.get()) && state.isSolidRender(level, pos)) return Anchor.FOUND;
                }
            }
        }
        return unknown ? Anchor.UNKNOWN : Anchor.MISSING;
    }
}
