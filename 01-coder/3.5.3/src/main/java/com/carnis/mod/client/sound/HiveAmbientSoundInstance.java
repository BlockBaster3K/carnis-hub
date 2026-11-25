package com.carnis.mod.client.sound;

import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;

/** Streamed non-positional Hive bed with a forty-tick fade in/out. */
public final class HiveAmbientSoundInstance extends AbstractTickableSoundInstance {
    private static final float MAX_VOLUME = 0.85F;
    private static final float FADE_PER_TICK = MAX_VOLUME / 40.0F;
    private final ClientLevel world;
    private float desired;
    private float fadeOutStartVolume;
    private int fadeOutTicksRemaining;

    public HiveAmbientSoundInstance(ClientLevel world, SoundEvent event, float target) {
        super(event, SoundSource.AMBIENT, SoundInstance.createUnseededRandom());
        this.world = world;
        this.looping = true;
        this.delay = 0;
        this.relative = true;
        this.attenuation = SoundInstance.Attenuation.NONE;
        this.volume = 0.0F;
        this.pitch = 1.0F;
        setTarget(target);
    }

    public void setTarget(float target) {
        float next = Mth.clamp(target, 0.0F, MAX_VOLUME);
        if (next <= 0.0F && desired > 0.0F) {
            fadeOutStartVolume = volume;
            fadeOutTicksRemaining = 40;
        } else if (next > 0.0F) {
            fadeOutTicksRemaining = 0;
        }
        desired = next;
    }

    public void end() {
        stop();
    }

    @Override
    public boolean canStartSilent() {
        return true;
    }

    @Override
    public void tick() {
        Minecraft client = Minecraft.getInstance();
        if (client.level != world || client.player == null) {
            stop();
            return;
        }

        if (desired <= 0.0F) {
            if (fadeOutTicksRemaining > 0) {
                fadeOutTicksRemaining--;
                volume = fadeOutStartVolume * fadeOutTicksRemaining / 40.0F;
            } else {
                volume = 0.0F;
                stop();
            }
            return;
        }

        float difference = desired - volume;
        volume += Mth.clamp(difference, -FADE_PER_TICK, FADE_PER_TICK);
    }
}
