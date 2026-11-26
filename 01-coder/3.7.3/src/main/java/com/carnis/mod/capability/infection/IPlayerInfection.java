package com.carnis.mod.capability.infection;

/**
 * Mutable player infection state expressed as a percentage.
 */
public interface IPlayerInfection {
    float MIN_INFECTION = 0.0F;
    float MAX_INFECTION = 100.0F;

    float getInfectionLevel();

    /**
     * Sets the infection percentage after clamping it to the valid range.
     *
     * @return true only when the stored value actually changed
     */
    boolean setInfectionLevel(float infectionLevel);

    /**
     * Adds a signed amount to the infection percentage.
     *
     * @return true only when the stored value actually changed
     */
    boolean addInfection(float amount);

    default boolean isAssimilated() {
        return getInfectionLevel() >= MAX_INFECTION;
    }
}
