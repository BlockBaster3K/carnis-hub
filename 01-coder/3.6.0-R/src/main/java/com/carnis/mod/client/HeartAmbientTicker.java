package com.carnis.mod.client;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.init.ModSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

public final class HeartAmbientTicker {
    private static final int HEARTBEAT_INTERVAL_FAR = 46;
    private static final int HEARTBEAT_INTERVAL_NEAR = 34;
    // The repeat interval must exceed this maximum supported sample duration (min interval is 1.7 s).

    private HeartAmbientTicker() { }

    public static void tick(Level level, BlockPos pos, BlockState state, PulsingHeartBlockEntity heart) {
        var player = Minecraft.getInstance().player;
        if (player == null) return;
        double distance = player.position().distanceTo(Vec3.atCenterOf(pos));
        if (distance >= 16.0D) return;
        float proximity = (float) (1.0D - distance / 16.0D);
        int interval = 46 - Math.round(proximity * 12.0F);
        if (Math.floorMod(level.getGameTime() + pos.asLong(), interval) != 0) return;
        level.playLocalSound(pos.getX() + 0.5D, pos.getY() + 0.5D, pos.getZ() + 0.5D,
                ModSounds.HEARTBEAT_LOOP.get(), SoundSource.BLOCKS, 0.2F + proximity * 0.8F,
                1.0F, false);
    }
}
