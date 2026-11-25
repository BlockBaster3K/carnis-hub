package com.carnis.mod.client.sound;

import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.hallucination.HallucinationType;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.network.packet.ClientboundHallucinationPacket;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public final class PhantomSoundManager {
    private PhantomSoundManager() {
    }

    public static void handle(ClientboundHallucinationPacket packet) {
        if (!CarnisConfig.CLIENT.hallucinationSoundsEnabled.get()) {
            return;
        }

        Minecraft minecraft = Minecraft.getInstance();
        ClientLevel level = minecraft.level;
        LocalPlayer player = minecraft.player;

        if (level == null || player == null) {
            return;
        }

        if (NeuroResonatorHelmetItem.isEquipped(player)) {
            return;
        }

        float configuredVolume = CarnisConfig.CLIENT
                .hallucinationSoundVolume
                .get()
                .floatValue();
        float volume = Math.max(
                0.0F,
                Math.min(2.0F, packet.volumeMultiplier() * configuredVolume)
        );

        if (volume <= 0.0F) {
            return;
        }

        Vec3 worldOffset = rotateLocalOffset(
                packet.relativeOffset(),
                player.getYRot()
        );
        Vec3 soundPosition = player.position().add(worldOffset);

        level.playLocalSound(
                soundPosition.x,
                soundPosition.y,
                soundPosition.z,
                soundFor(packet.type()),
                sourceFor(packet.type()),
                volume,
                1.0F,
                false
        );
    }

    private static Vec3 rotateLocalOffset(
            Vec3 localOffset,
            float playerYawDegrees
    ) {
        double yawRadians = Math.toRadians(playerYawDegrees);
        Vec3 forward = new Vec3(
                -Math.sin(yawRadians),
                0.0D,
                Math.cos(yawRadians)
        );
        Vec3 right = new Vec3(-forward.z, 0.0D, forward.x);

        return right.scale(localOffset.x)
                .add(0.0D, localOffset.y, 0.0D)
                .add(forward.scale(localOffset.z));
    }

    private static SoundEvent soundFor(HallucinationType type) {
        return switch (type) {
            case CREEPER_HISS -> ModSounds.PHANTOM_CREEPER.get();
            case PHANTOM_FOOTSTEPS -> ModSounds.PHANTOM_FOOTSTEPS.get();
            case WHISPER -> ModSounds.PHANTOM_WHISPER.get();
            case FALSE_DAMAGE -> SoundEvents.PLAYER_HURT;
        };
    }

    private static SoundSource sourceFor(HallucinationType type) {
        return type == HallucinationType.FALSE_DAMAGE
                ? SoundSource.PLAYERS
                : SoundSource.AMBIENT;
    }

}
