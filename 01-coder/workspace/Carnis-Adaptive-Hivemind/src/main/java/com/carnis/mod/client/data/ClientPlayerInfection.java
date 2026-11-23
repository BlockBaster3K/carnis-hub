package com.carnis.mod.client.data;

/** Compatibility facade for earlier overlays and fog renderers. */
public final class ClientPlayerInfection {
    private ClientPlayerInfection() { }
    public static float getInfectionLevel() { return ClientInfectionData.points(); }
    public static boolean isAssimilated() { return ClientInfectionData.points() >= 100; }
    public static void reset() { ClientInfectionData.reset(); }
}
