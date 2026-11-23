package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientInfectionData;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Presentation only: camera changes do not alter server-side aim or motion. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerHallucinationHandler {
    private static int soundDelay;
    private static int whisperDelay = -1;
    private static int spasm;
    private static int agonyTicks;
    private PlayerHallucinationHandler() { }
    @SubscribeEvent public static void onTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        int stage = ClientInfectionData.stage();
        if (mc.level == null || player == null || !player.isAlive() || player.isSpectator() || stage == 0) {
            soundDelay = 0; whisperDelay = -1; spasm = 0; agonyTicks = 0; return;
        }
        if (ClientInfectionData.points() >= 100) {
            if (agonyTicks == 0) soundDelay = 0;
            agonyTicks = Math.min(100, agonyTicks + 1);
        } else agonyTicks = 0;
        if (spasm > 0) spasm--;
        if (NeuroResonatorHelmetItem.isEquipped(player)) { soundDelay = 0; whisperDelay = -1; spasm = 0; return; }
        if (stage >= 3 && player.getRandom().nextInt(180) == 0) spasm = 8;
        if (!CarnisConfig.CLIENT.hallucinationSoundsEnabled.get()) { whisperDelay = -1; return; }
        tickWhisper(mc, player);
        if (soundDelay > 0) { soundDelay--; return; }
        float volume = CarnisConfig.CLIENT.hallucinationSoundVolume.get().floatValue();
        volume *= com.carnis.mod.item.NeuroWeave.infectionMultiplier(player);
        if (volume > 0) {
            SoundEvent sound;
            Vec3 pos;
            if (agonyTicks > 0) {
                sound = agonyTicks == 1 ? ModSounds.AMALGAM_ROAR.get() : ModSounds.HEARTBEAT_LOOP.get();
                pos = player.position().add(0, 1, 0);
                volume *= .4F + .6F * agonyTicks / 100.0F;
                soundDelay = Math.max(8, 24 - agonyTicks / 7);
            } else {
                boolean whisper = stage == 1 || player.getRandom().nextBoolean();
                sound = whisper ? null : ModSounds.PHANTOM_FOOTSTEPS.get();
                if (stage == 1 && player.getRandom().nextBoolean()) sound = ModSounds.HEARTBEAT_LOOP.get();
                Vec3 behind = player.getLookAngle().multiply(1, 0, 1).normalize().scale(-2.5D);
                pos = player.position().add(behind).add(0, .6D, 0);
                soundDelay = stage == 1 ? 400 + player.getRandom().nextInt(601)
                        : 200 + player.getRandom().nextInt(501);
            }
            if (sound != null) mc.level.playLocalSound(pos.x, pos.y, pos.z, sound, SoundSource.AMBIENT, volume, 1.0F, false);
        } else soundDelay = 200;
    }

    private static void tickWhisper(Minecraft mc, LocalPlayer player) {
        float infection = Mth.clamp((float) ClientInfectionData.points(), 0.0F, 100.0F);
        float protection = com.carnis.mod.item.NeuroWeave.infectionMultiplier(player);
        float configuredVolume = CarnisConfig.CLIENT.hallucinationSoundVolume.get().floatValue();
        if (infection <= 10.0F || protection <= 0.0F || configuredVolume <= 0.0F) {
            whisperDelay = -1;
            return;
        }
        if (whisperDelay < 0) {
            whisperDelay = nextWhisperDelay(infection, player.getRandom());
            return;
        }
        if (--whisperDelay > 0) return;

        float volume = whisperVolume(infection) * configuredVolume * protection;
        Vec3 behind = player.getLookAngle().multiply(1, 0, 1).normalize().scale(-2.5D);
        Vec3 pos = player.position().add(behind).add(0, .6D, 0);
        mc.level.playLocalSound(pos.x, pos.y, pos.z, ModSounds.PHANTOM_WHISPER.get(),
                SoundSource.AMBIENT, volume, 1.0F, false);
        whisperDelay = nextWhisperDelay(infection, player.getRandom());
    }

    private static float whisperVolume(float infection) {
        if (infection <= 10.0F) return 0.0F;
        if (infection <= 25.0F) return Mth.lerp((infection - 10.0F) / 15.0F, 0.1F, 0.3F);
        if (infection <= 50.0F) return Mth.lerp((infection - 25.0F) / 25.0F, 0.3F, 0.6F);
        if (infection <= 75.0F) return Mth.lerp((infection - 50.0F) / 25.0F, 0.6F, 0.85F);
        return Mth.lerp((infection - 75.0F) / 25.0F, 0.85F, 1.0F);
    }

    private static int nextWhisperDelay(float infection, RandomSource random) {
        float lower;
        float upper;
        if (infection <= 25.0F) {
            float t = (infection - 10.0F) / 15.0F;
            lower = Mth.lerp(t, 400.0F, 300.0F);
            upper = Mth.lerp(t, 1000.0F, 800.0F);
        } else if (infection <= 50.0F) {
            float t = (infection - 25.0F) / 25.0F;
            lower = Mth.lerp(t, 300.0F, 200.0F);
            upper = Mth.lerp(t, 800.0F, 600.0F);
        } else if (infection <= 75.0F) {
            float t = (infection - 50.0F) / 25.0F;
            lower = Mth.lerp(t, 200.0F, 150.0F);
            upper = Mth.lerp(t, 600.0F, 400.0F);
        } else {
            float t = (infection - 75.0F) / 25.0F;
            lower = Mth.lerp(t, 150.0F, 100.0F);
            upper = Mth.lerp(t, 400.0F, 250.0F);
        }
        int min = Math.round(lower);
        int max = Math.round(upper);
        return random.nextIntBetweenInclusive(min, max);
    }

    @SubscribeEvent public static void onCamera(ViewportEvent.ComputeCameraAngles event) {
        LocalPlayer player = Minecraft.getInstance().player;
        if (player == null || !player.isAlive() || player.isSpectator() || event.getCamera().getEntity() != player
                || NeuroResonatorHelmetItem.isEquipped(player) || ClientInfectionData.stage() < 3) return;
        double t = player.tickCount + event.getPartialTick();
        float strength = spasm > 0 ? .8F * spasm / 8.0F : 0;
        if (agonyTicks > 0) strength += .35F * agonyTicks / 100.0F;
        event.setYaw(event.getYaw() + (float) Math.sin(t * 2.4D) * strength);
        event.setPitch(event.getPitch() + (float) Math.cos(t * 1.7D) * strength * .7F);
        event.setRoll(event.getRoll() + (float) Math.sin(t * 1.2D) * strength * .6F);
    }
}
