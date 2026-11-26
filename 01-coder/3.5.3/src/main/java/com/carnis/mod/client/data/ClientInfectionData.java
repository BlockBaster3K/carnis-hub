package com.carnis.mod.client.data;

import com.carnis.mod.network.SyncPlayerInfectionPacket;
import net.minecraft.client.Minecraft;

/** Client-side presentation snapshot, replaced only by server packets. */
public final class ClientInfectionData {
    private static int points;
    private static int stage;
    private ClientInfectionData() { }
    public static void apply(SyncPlayerInfectionPacket packet) {
        points = packet.infectionPoints();
        stage = packet.stage();
        var player = Minecraft.getInstance().player;
        if (player != null) {
            player.getPersistentData().putInt("carnis:infection_points", points);
            player.getPersistentData().putFloat("carnis:infection_fraction", 0.0F);
        }
    }
    public static int points() { return points; }
    public static int stage() { return stage; }
    public static void reset() { points = 0; stage = 0; }
}
