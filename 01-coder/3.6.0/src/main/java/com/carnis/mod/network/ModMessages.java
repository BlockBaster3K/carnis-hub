package com.carnis.mod.network;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.network.packet.ClientboundHallucinationPacket;
import com.carnis.mod.network.packet.SyncCarnisWorldDataPacket;
import com.carnis.mod.network.packet.SyncPlayerBiomassPacket;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

import java.util.Objects;

public final class ModMessages {
    private static final String PROTOCOL_VERSION = "3";

    private static final SimpleChannel CHANNEL =
            NetworkRegistry.ChannelBuilder
                    .named(new ResourceLocation(CarnisMod.MOD_ID, "messages"))
                    .networkProtocolVersion(() -> PROTOCOL_VERSION)
                    .clientAcceptedVersions(PROTOCOL_VERSION::equals)
                    .serverAcceptedVersions(PROTOCOL_VERSION::equals)
                    .simpleChannel();

    private static int nextPacketId;
    private static volatile boolean registered;

    private ModMessages() {
    }

    public static synchronized void register() {
        if (registered) {
            throw new IllegalStateException("Carnis network packets are already registered");
        }

        CHANNEL.messageBuilder(
                        SyncCarnisWorldDataPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(SyncCarnisWorldDataPacket::encode)
                .decoder(SyncCarnisWorldDataPacket::decode)
                .consumerMainThread(SyncCarnisWorldDataPacket::handle)
                .add();

        CHANNEL.messageBuilder(
                        SyncPlayerInfectionPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(SyncPlayerInfectionPacket::encode)
                .decoder(SyncPlayerInfectionPacket::decode)
                .consumerMainThread(SyncPlayerInfectionPacket::handle)
                .add();

        CHANNEL.messageBuilder(
                        ClientboundHallucinationPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(ClientboundHallucinationPacket::encode)
                .decoder(ClientboundHallucinationPacket::decode)
                .consumerMainThread(ClientboundHallucinationPacket::handle)
                .add();

        CHANNEL.messageBuilder(
                        SyncPlayerBiomassPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(SyncPlayerBiomassPacket::encode)
                .decoder(SyncPlayerBiomassPacket::decode)
                .consumerMainThread(SyncPlayerBiomassPacket::handle)
                .add();

        registered = true;
    }

    public static void sendToPlayer(SyncPlayerBiomassPacket packet, ServerPlayer player) {
        Objects.requireNonNull(packet, "packet");
        Objects.requireNonNull(player, "player");
        ensureRegistered();
        CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), packet);
    }

    public static void sendToPlayer(ServerPlayer player) {
        Objects.requireNonNull(player, "player");
        ensureRegistered();

        CarnisWorldData worldData = CarnisWorldData.get(player.serverLevel());
        sendToPlayer(player, SyncCarnisWorldDataPacket.from(worldData));
    }

    public static void sendPlayerInfection(ServerPlayer player) {
        Objects.requireNonNull(player, "player");
        ensureRegistered();

        sendToPlayer(player, SyncPlayerInfectionPacket.from(player));
    }

    public static void sendHallucination(
            ServerPlayer player,
            ClientboundHallucinationPacket packet
    ) {
        Objects.requireNonNull(player, "player");
        Objects.requireNonNull(packet, "packet");
        ensureRegistered();

        sendToPlayer(player, packet);
    }

    public static void sendToPlayersInLevel(ServerLevel level) {
        Objects.requireNonNull(level, "level");
        ensureRegistered();

        SyncCarnisWorldDataPacket packet = SyncCarnisWorldDataPacket.from(
                CarnisWorldData.get(level)
        );

        for (ServerPlayer player : level.players()) {
            sendToPlayer(player, packet);
        }
    }

    public static void sendToAllPlayers(MinecraftServer server) {
        Objects.requireNonNull(server, "server");
        ensureRegistered();

        for (ServerLevel level : server.getAllLevels()) {
            sendToPlayersInLevel(level);
        }
    }

    private static void sendToPlayer(
            ServerPlayer player,
            SyncCarnisWorldDataPacket packet
    ) {
        CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                packet
        );
    }

    private static void sendToPlayer(
            ServerPlayer player,
            SyncPlayerInfectionPacket packet
    ) {
        CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                packet
        );
    }

    private static void sendToPlayer(
            ServerPlayer player,
            ClientboundHallucinationPacket packet
    ) {
        CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                packet
        );
    }

    private static int nextPacketId() {
        return nextPacketId++;
    }

    private static void ensureRegistered() {
        if (!registered) {
            throw new IllegalStateException(
                    "Carnis network packets have not been registered yet"
            );
        }
    }
}
