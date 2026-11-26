package com.carnis.mod.network;

import com.carnis.mod.infection.PlayerInfectionManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

public record SyncPlayerInfectionPacket(int infectionPoints, int stage) {
    public SyncPlayerInfectionPacket {
        infectionPoints = Math.max(0, Math.min(100, infectionPoints));
        stage = Math.max(0, Math.min(4, stage));
    }
    public static SyncPlayerInfectionPacket from(Player player) {
        return new SyncPlayerInfectionPacket(PlayerInfectionManager.displayPoints(player),
                PlayerInfectionManager.stage(PlayerInfectionManager.getPoints(player)));
    }
    public static void encode(SyncPlayerInfectionPacket packet, FriendlyByteBuf buffer) {
        buffer.writeVarInt(packet.infectionPoints());
        buffer.writeVarInt(packet.stage());
    }
    public static SyncPlayerInfectionPacket decode(FriendlyByteBuf buffer) {
        return new SyncPlayerInfectionPacket(buffer.readVarInt(), buffer.readVarInt());
    }
    public static void handle(SyncPlayerInfectionPacket packet, Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        if (context.getDirection() == NetworkDirection.PLAY_TO_CLIENT)
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> com.carnis.mod.client.data.ClientInfectionData.apply(packet));
        context.setPacketHandled(true);
    }
}
