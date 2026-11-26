package com.carnis.mod.sound;

import com.carnis.mod.init.ModSounds;
import net.minecraft.world.level.block.SoundType;

/** SoundType factory for the mod's organic blocks. */
public final class CarnisSoundTypes {
    private CarnisSoundTypes() { }

    /**
     * Must be called from a deferred block-registration supplier, after the sound registry objects exist.
     * SoundType argument order: break, step, place, hit, fall.
     */
    public static SoundType membrane() {
        return new SoundType(1.0F, 1.0F,
                ModSounds.HIVE_BLOCK_BREAK.get(),
                ModSounds.HIVE_MEMBRANE_STEP.get(),
                ModSounds.HIVE_MEMBRANE_PLACE.get(),
                ModSounds.COMBAT_FLESH_HIT.get(),
                ModSounds.HIVE_MEMBRANE_STEP.get());
    }

    public static SoundType organic() {
        return new SoundType(
                1.0F,
                1.0F,
                ModSounds.HIVE_BLOCK_BREAK.get(),
                ModSounds.FLESH_BLOCK_STEP.get(),
                ModSounds.HIVE_BLOCK_PLACE.get(),
                ModSounds.COMBAT_FLESH_HIT.get(),
                ModSounds.FLESH_BLOCK_STEP.get()
        );
    }
}
