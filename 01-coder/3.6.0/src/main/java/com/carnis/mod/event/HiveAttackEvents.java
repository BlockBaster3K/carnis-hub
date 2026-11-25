package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlockTags;
import com.carnis.mod.block.entity.HiveEyeBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HiveAttackEvents {
    private HiveAttackEvents() {
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onBlockBreak(BlockEvent.BreakEvent event) {
        if (event.isCanceled() || !(event.getLevel() instanceof ServerLevel level)) return;
        Player attacker = event.getPlayer();
        if (!attacker.isAlive() || !event.getState().is(ModBlockTags.HIVE_BLOCKS)) return;

        BlockPos brokenPos = event.getPos();
        Vec3 brokenCenter = Vec3.atCenterOf(brokenPos);
        double radiusSquared = HiveEyeBlockEntity.HIVEMIND_ALERT_RADIUS
                * HiveEyeBlockEntity.HIVEMIND_ALERT_RADIUS;
        int radius = (int) Math.ceil(HiveEyeBlockEntity.HIVEMIND_ALERT_RADIUS);
        int minChunkX = (brokenPos.getX() - radius) >> 4;
        int maxChunkX = (brokenPos.getX() + radius) >> 4;
        int minChunkZ = (brokenPos.getZ() - radius) >> 4;
        int maxChunkZ = (brokenPos.getZ() + radius) >> 4;

        for (int chunkX = minChunkX; chunkX <= maxChunkX; chunkX++) {
            for (int chunkZ = minChunkZ; chunkZ <= maxChunkZ; chunkZ++) {
                var chunk = level.getChunkSource().getChunkNow(chunkX, chunkZ);
                if (chunk == null) continue;

                for (BlockEntity blockEntity : chunk.getBlockEntities().values()) {
                    if (blockEntity instanceof HiveEyeBlockEntity eye
                            && !eye.isRemoved()
                            && Vec3.atCenterOf(eye.getBlockPos()).distanceToSqr(brokenCenter) <= radiusSquared) {
                        eye.onHiveAttacked(level, attacker);
                    }
                }
            }
        }
    }
}
