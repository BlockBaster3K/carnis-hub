package com.carnis.mod.capability.infection;

import com.carnis.mod.infection.PlayerInfectionManager;
import com.carnis.mod.item.NeuroWeave;
import net.minecraft.world.entity.player.Player;

/** Compatibility facade. Persistent player data is the authoritative store. */
public final class PlayerInfectionApi {
    private PlayerInfectionApi() { }
    public static float getInfectionLevel(Player player) { return PlayerInfectionManager.getPoints(player); }
    public static boolean setInfectionLevel(Player player, float value) {
        if (value > getInfectionLevel(player) && player.hasEffect(com.carnis.mod.init.ModEffects.IMMUNOSUPPRESSION.get())) return false;
        return PlayerInfectionManager.setPoints(player, value);
    }
    public static boolean addInfection(Player player, float amount) {
        if (Float.isNaN(amount) || amount == 0) return false;
        return setInfectionLevel(player, getInfectionLevel(player) + amount);
    }
    public static boolean addExposure(Player player, float amount) {
        if (amount > 0 && player.hasEffect(com.carnis.mod.init.ModEffects.IMMUNOSUPPRESSION.get())) return false;
        return addInfection(player, amount > 0 ? amount * NeuroWeave.infectionMultiplier(player) : amount);
    }
    /** A living carrier has not yet been assimilated into a clone. */
    public static boolean isAssimilated(Player player) {
        return player.getPersistentData().getBoolean(PlayerInfectionManager.METAMORPHOSED);
    }
    public static boolean isHostileTarget(Player player) {
        return player.isAlive() && !player.isSpectator() && !player.isCreative();
    }
    public static void copy(Player source, Player target) {
        PlayerInfectionManager.copyToClone(source, target, false);
    }
}
