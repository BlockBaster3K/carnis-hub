package com.carnis.mod.client.data;

import com.carnis.mod.network.packet.SyncCarnisWorldDataPacket;
import com.carnis.mod.world.CarnisWorldData.AdaptationType;

import java.util.Objects;

public final class ClientCarnisWorldData {
    private static volatile Snapshot snapshot = Snapshot.EMPTY;

    private ClientCarnisWorldData() {
    }

    public static void apply(SyncCarnisWorldDataPacket packet) {
        Objects.requireNonNull(packet, "packet");

        snapshot = new Snapshot(
                packet.biomassPoints(),
                packet.fireAdaptation(),
                packet.rangedAdaptation(),
                packet.meleeAdaptation(),
                packet.pillaringAdaptation(),
                packet.explosiveAdaptation(),
                packet.darkAdaptation()
        );
    }

    public static Snapshot getSnapshot() {
        return snapshot;
    }

    public static long getBiomassPoints() {
        return snapshot.biomassPoints();
    }

    public static long getAdaptation(AdaptationType type) {
        Objects.requireNonNull(type, "type");

        return switch (type) {
            case FIRE -> snapshot.fireAdaptation();
            case RANGED -> snapshot.rangedAdaptation();
            case MELEE -> snapshot.meleeAdaptation();
            case PILLARING -> snapshot.pillaringAdaptation();
            case EXPLOSIVE -> snapshot.explosiveAdaptation();
            case DARK -> snapshot.darkAdaptation();
        };
    }

    public static void reset() {
        snapshot = Snapshot.EMPTY;
    }

    public record Snapshot(
            long biomassPoints,
            long fireAdaptation,
            long rangedAdaptation,
            long meleeAdaptation,
            long pillaringAdaptation,
            long explosiveAdaptation,
            long darkAdaptation
    ) {
        private static final Snapshot EMPTY = new Snapshot(
                0L,
                0L,
                0L,
                0L,
                0L,
                0L,
                0L
        );
    }
}
