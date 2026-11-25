package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.util.HiveGrowthSuppression;
import org.joml.Vector3f;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.BonemealEvent;
import net.minecraftforge.event.level.BlockEvent.CropGrowEvent;
import net.minecraftforge.event.level.SaplingGrowTreeEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.HashSet;
import java.util.Set;

/** Серверные события подавления роста естественной флоры и прорастания от костной муки. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HiveGrowthSuppressionEvents {
    private static final DustParticleOptions SUPPRESSION_DUST =
            new DustParticleOptions(new Vector3f(0.3F, 0.15F, 0.1F), 1.0F);

    private HiveGrowthSuppressionEvents() {
    }

    @SubscribeEvent
    public static void onCropGrow(CropGrowEvent.Pre event) {
        ServerLevel level = getServerLevel(event.getLevel());
        if (level == null) {
            return;
        }
        BlockPos pos = event.getPos();
        if (shouldSuppress(level, pos)) {
            event.setResult(Event.Result.DENY);
            spawnSuppressionParticles(level, pos, 4, 1.0D, 0.3D);
        }
    }

    @SubscribeEvent
    public static void onSaplingGrow(SaplingGrowTreeEvent event) {
        ServerLevel level = getServerLevel(event.getLevel());
        if (level == null) {
            return;
        }
        BlockPos pos = event.getPos();
        if (shouldSuppress(level, pos)) {
            event.setCanceled(true);
            spawnSuppressionParticles(level, pos, 4, 1.0D, 0.3D);
        }
    }

    @SubscribeEvent
    public static void onBonemeal(BonemealEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer)) {
            return;
        }
        ServerLevel level = getServerLevel(event.getLevel());
        if (level == null) {
            return;
        }

        int strength = CarnisConfig.SERVER.growthSuppressionStrength.get();
        BlockPos pos = event.getPos();
        if (strength <= 0 || !HiveGrowthSuppression.isNearHive(
                level,
                pos,
                CarnisConfig.SERVER.growthSuppressionRadius.get()
        )) {
            return;
        }

        if (level.random.nextFloat() < strength / 100.0F) {
            event.setCanceled(true);
            spawnSuppressionParticles(level, pos, 4, 1.0D, 0.3D);
        }
    }

    /** Кэш поиска очищается каждые 100 серверных тиков. */
    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase == TickEvent.Phase.END && event.getServer().getTickCount() % 100 == 0) {
            HiveGrowthSuppression.clearCache();
        }
    }

    /** Периодически увядает трава и микелий внутри активной зоны Улья. */
    @SubscribeEvent
    public static void onServerTickGrassWither(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.getServer().getTickCount() % 200 != 0) {
            return;
        }

        int strength = CarnisConfig.SERVER.growthSuppressionStrength.get();
        if (strength <= 0) {
            return;
        }

        int radius = CarnisConfig.SERVER.growthSuppressionRadius.get();
        int scanRadius = radius * 2;
        float suppressionChance = strength / 100.0F;
        int changes = 0;
        BlockState dirt = Blocks.DIRT.defaultBlockState();

        scan:
        for (ServerLevel level : event.getServer().getAllLevels()) {
            Set<Long> testedPositions = new HashSet<>();
            for (ServerPlayer player : level.players()) {
                BlockPos center = player.blockPosition();
                int minX = center.getX() - scanRadius;
                int maxX = center.getX() + scanRadius;
                int minZ = center.getZ() - scanRadius;
                int maxZ = center.getZ() + scanRadius;
                int minY = Math.max(level.getMinBuildHeight(), center.getY() - scanRadius);
                int maxY = Math.min(level.getMaxBuildHeight() - 1, center.getY() + scanRadius);
                BlockPos.MutableBlockPos cursor = new BlockPos.MutableBlockPos();

                for (int x = minX; x <= maxX; x++) {
                    for (int y = minY; y <= maxY; y++) {
                        for (int z = minZ; z <= maxZ; z++) {
                            cursor.set(x, y, z);
                            if (!level.hasChunkAt(cursor)) {
                                continue;
                            }

                            BlockState state = level.getBlockState(cursor);
                            if (!state.is(Blocks.GRASS_BLOCK) && !state.is(Blocks.MYCELIUM)) {
                                continue;
                            }

                            long packedPos = cursor.asLong();
                            if (!testedPositions.add(packedPos)
                                    || !HiveGrowthSuppression.isNearHive(level, cursor, radius)
                                    || level.random.nextFloat() >= suppressionChance) {
                                continue;
                            }

                            BlockPos targetPos = cursor.immutable();
                            if (level.setBlockAndUpdate(targetPos, dirt)) {
                                spawnSuppressionParticles(level, targetPos, 3, 1.0D, 0.3D);
                                level.playSound(null, targetPos, SoundEvents.GRASS_BREAK,
                                        SoundSource.BLOCKS, 0.3F, 1.0F);
                                changes++;
                                if (changes >= 32) {
                                    break scan;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    private static boolean shouldSuppress(ServerLevel level, BlockPos pos) {
        int strength = CarnisConfig.SERVER.growthSuppressionStrength.get();
        if (strength <= 0) {
            return false;
        }

        float factor = HiveGrowthSuppression.getSuppressionFactor(
                level,
                pos,
                CarnisConfig.SERVER.growthSuppressionRadius.get(),
                strength
        );
        if (factor >= 1.0F) {
            return false;
        }
        if (factor <= 0.0F) {
            return true;
        }
        return level.random.nextFloat() > factor;
    }

    private static void spawnSuppressionParticles(
            ServerLevel level,
            BlockPos pos,
            int count,
            double yOffset,
            double spread
    ) {
        level.sendParticles(
                SUPPRESSION_DUST,
                pos.getX() + 0.5D,
                pos.getY() + yOffset,
                pos.getZ() + 0.5D,
                count,
                spread,
                spread,
                spread,
                0.0D
        );
    }

    private static ServerLevel getServerLevel(LevelAccessor levelAccessor) {
        if (levelAccessor.isClientSide() || !(levelAccessor instanceof ServerLevel serverLevel)) {
            return null;
        }
        return serverLevel;
    }
}
