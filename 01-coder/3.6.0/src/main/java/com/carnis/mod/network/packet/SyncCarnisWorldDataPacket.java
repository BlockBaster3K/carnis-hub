package com.carnis.mod.network.packet;

import com.carnis.mod.client.data.ClientCarnisWorldData;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;

import java.util.Objects;
import java.util.function.Supplier;

public record SyncCarnisWorldDataPacket(
        long biomassPoints,
        long fireAdaptation,
        long rangedAdaptation,
        long meleeAdaptation,
        long pillaringAdaptation,
        long explosiveAdaptation,
        long darkAdaptation
) {
    public SyncCarnisWorldDataPacket {
        biomassPoints = nonNegative(biomassPoints);
        fireAdaptation = nonNegative(fireAdaptation);
        rangedAdaptation = nonNegative(rangedAdaptation);
        meleeAdaptation = nonNegative(meleeAdaptation);
        pillaringAdaptation = nonNegative(pillaringAdaptation);
        explosiveAdaptation = nonNegative(explosiveAdaptation);
        darkAdaptation = nonNegative(darkAdaptation);
    }

    public static SyncCarnisWorldDataPacket from(CarnisWorldData worldData) {
        Objects.requireNonNull(worldData, "worldData");

        return new SyncCarnisWorldDataPacket(
                worldData.getBiomassPoints(),
                worldData.getFireAdaptation(),
                worldData.getRangedAdaptation(),
                worldData.getMeleeAdaptation(),
                worldData.getPillaringAdaptation(),
                worldData.getExplosiveAdaptation(),
                worldData.getDarkAdaptation()
        );
    }

    public static void encode(
            SyncCarnisWorldDataPacket packet,
            FriendlyByteBuf buffer
    ) {
        buffer.writeLong(packet.biomassPoints());
        buffer.writeLong(packet.fireAdaptation());
        buffer.writeLong(packet.rangedAdaptation());
        buffer.writeLong(packet.meleeAdaptation());
        buffer.writeLong(packet.pillaringAdaptation());
        buffer.writeLong(packet.explosiveAdaptation());
        buffer.writeLong(packet.darkAdaptation());
    }

    public static SyncCarnisWorldDataPacket decode(FriendlyByteBuf buffer) {
        return new SyncCarnisWorldDataPacket(
                buffer.readLong(),
                buffer.readLong(),
                buffer.readLong(),
                buffer.readLong(),
                buffer.readLong(),
                buffer.readLong(),
                buffer.readLong()
        );
    }

    public static void handle(
            SyncCarnisWorldDataPacket packet,
            Supplier<NetworkEvent.Context> contextSupplier
    ) {
        NetworkEvent.Context context = contextSupplier.get();

        if (context.getDirection() != NetworkDirection.PLAY_TO_CLIENT) {
            context.setPacketHandled(true);
            return;
        }

        DistExecutor.unsafeRunWhenOn(
                Dist.CLIENT,
                () -> () -> ClientCarnisWorldData.apply(packet)
        );

        context.setPacketHandled(true);
    }

    private static long nonNegative(long value) {
        return Math.max(0L, value);
    }
}
