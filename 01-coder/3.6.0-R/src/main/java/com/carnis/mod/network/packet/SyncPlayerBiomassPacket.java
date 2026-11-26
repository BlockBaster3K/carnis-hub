package com.carnis.mod.network.packet;

import com.carnis.mod.client.data.ClientPlayerBiomassData;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Серверное значение персональной биомассы для одного игрока. */
public final class SyncPlayerBiomassPacket {
    private final long biomassPoints;

    public SyncPlayerBiomassPacket(long biomassPoints) {
        this.biomassPoints = Math.max(0L, biomassPoints);
    }

    public static void encode(SyncPlayerBiomassPacket packet, FriendlyByteBuf buffer) {
        buffer.writeLong(packet.biomassPoints);
    }

    public static SyncPlayerBiomassPacket decode(FriendlyByteBuf buffer) {
        return new SyncPlayerBiomassPacket(buffer.readLong());
    }

    public static void handle(SyncPlayerBiomassPacket packet, Supplier<NetworkEvent.Context> contextSupplier) {
        NetworkEvent.Context context = contextSupplier.get();
        if (context.getDirection() == NetworkDirection.PLAY_TO_CLIENT) {
            context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                    () -> () -> ClientPlayerBiomassData.apply(packet.biomassPoints)));
        }
        context.setPacketHandled(true);
    }
}
