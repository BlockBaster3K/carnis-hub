package com.carnis.mod.capability.infection;

import java.util.Objects;

/**
 * Clamped data implementation for the player infection capability.
 */
public final class PlayerInfection implements IPlayerInfection {
    private static final Runnable NO_CHANGE_LISTENER = () -> {
    };

    private final Runnable changeListener;
    private float infectionLevel;

    public PlayerInfection() {
        this(NO_CHANGE_LISTENER);
    }

    public PlayerInfection(Runnable changeListener) {
        this.changeListener = Objects.requireNonNull(
                changeListener,
                "changeListener"
        );
    }

    @Override
    public float getInfectionLevel() {
        return infectionLevel;
    }

    @Override
    public boolean setInfectionLevel(float infectionLevel) {
        float sanitizedLevel = sanitize(infectionLevel);

        if (Float.compare(this.infectionLevel, sanitizedLevel) == 0) {
            return false;
        }

        this.infectionLevel = sanitizedLevel;
        changeListener.run();
        return true;
    }

    @Override
    public boolean addInfection(float amount) {
        if (Float.isNaN(amount) || amount == 0.0F) {
            return false;
        }

        return setInfectionLevel(infectionLevel + amount);
    }

    static float sanitize(float infectionLevel) {
        if (Float.isNaN(infectionLevel)) {
            return MIN_INFECTION;
        }

        return Math.max(
                MIN_INFECTION,
                Math.min(MAX_INFECTION, infectionLevel)
        );
    }

    public void setInfectionLevelSilently(float infectionLevel) {
        this.infectionLevel = sanitize(infectionLevel);
    }
}
