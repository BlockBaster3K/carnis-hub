package com.carnis.mod.network.packet;

import com.carnis.mod.client.sound.PhantomSoundManager;
import com.carnis.mod.hallucination.HallucinationType;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;

import java.util.Objects;
import java.util.function.Supplier;

/**
 * Carries one purely client-side auditory hallucination. The relative offset
 * uses player-local axes: positive X is right, positive Y is up and positive
 * Z is forward, so a negative Z value is heard behind the player.
 */
public record ClientboundHallucinationPacket(
        HallucinationType type,
        float volumeMultiplier,
        Vec3 relativeOffset
) {
    private static final float MAX_VOLUME_MULTIPLIER = 2.0F;
    private static final double MAX_OFFSET_COMPONENT = 16.0D;

    public ClientboundHallucinationPacket {
        type = Objects.requireNonNull(type, "type");
        relativeOffset = sanitizeOffset(
                Objects.requireNonNull(relativeOffset, "relativeOffset")
        );

        if (Float.isNaN(volumeMultiplier)) {
            volumeMultiplier = 1.0F;
        } else {
            volumeMultiplier = Math.max(
                    0.0F,
                    Math.min(MAX_VOLUME_MULTIPLIER, volumeMultiplier)
            );
        }
    }

    public static void encode(
            ClientboundHallucinationPacket packet,
            FriendlyByteBuf buffer
    ) {
        buffer.writeEnum(packet.type());
        buffer.writeFloat(packet.volumeMultiplier());
        buffer.writeDouble(packet.relativeOffset().x);
        buffer.writeDouble(packet.relativeOffset().y);
        buffer.writeDouble(packet.relativeOffset().z);
    }

    public static ClientboundHallucinationPacket decode(
            FriendlyByteBuf buffer
    ) {
        return new ClientboundHallucinationPacket(
                buffer.readEnum(HallucinationType.class),
                buffer.readFloat(),
                new Vec3(
                        buffer.readDouble(),
                        buffer.readDouble(),
                        buffer.readDouble()
                )
        );
    }

    public static void handle(
            ClientboundHallucinationPacket packet,
            Supplier<NetworkEvent.Context> contextSupplier
    ) {
        NetworkEvent.Context context = contextSupplier.get();

        if (context.getDirection() != NetworkDirection.PLAY_TO_CLIENT) {
            context.setPacketHandled(true);
            return;
        }

        DistExecutor.unsafeRunWhenOn(
                Dist.CLIENT,
                () -> () -> PhantomSoundManager.handle(packet)
        );

        context.setPacketHandled(true);
    }

    private static Vec3 sanitizeOffset(Vec3 offset) {
        return new Vec3(
                sanitizeOffsetComponent(offset.x),
                sanitizeOffsetComponent(offset.y),
                sanitizeOffsetComponent(offset.z)
        );
    }

    private static double sanitizeOffsetComponent(double component) {
        if (!Double.isFinite(component)) {
            return 0.0D;
        }

        return Math.max(
                -MAX_OFFSET_COMPONENT,
                Math.min(MAX_OFFSET_COMPONENT, component)
        );
    }
}
