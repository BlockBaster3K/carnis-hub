package com.carnis.mod.client.sound;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModSounds;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import java.util.HashMap;
import java.util.Map;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;


/** Samples loaded Hive blocks only; no chunk loading and a fixed client-tick budget. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class HiveAmbientSoundHandler {
    private static final Map<String, Boolean> AMBIENT_RESOURCE_CACHE = new HashMap<>();
    private static ResourceManager ambientResourceManager;
    private static final Map<String, Long> AMBIENT_WARNING_TIMES = new HashMap<>();
    private static final long AMBIENT_WARNING_COOLDOWN_MS = 60_000L;

    private static final int RADIUS = 16;
    private static final int SIDE = RADIUS * 2 + 1;
    private static final int VOLUME = SIDE * SIDE * SIDE;
    private static final int BUDGET = 2048;
    private static final int CLOSE_STRUCTURE_ENTER = 12;
    private static final int CLOSE_STRUCTURE_EXIT = 8;
    private static final int PULSE_INTERVAL_TICKS = 450; // 22.5 seconds
    private static final int HEARTBEAT_MIN_INTERVAL = 800; // 40 seconds
    private static final int HEARTBEAT_MAX_INTERVAL = 1200; // 60 seconds
    // Sphere radius 16 contains approximately 17,077 sampled positions.
    private static final int DENSITY_SURFACE = 85;
    private static final int DENSITY_CORE = 1366;
    private static final int ZONE_THRESHOLD = 0;
    private static final int ZONE_SURFACE = 1;
    private static final int ZONE_DEEP = 2;
    private static final int ZONE_CORE = 3;
    private static final int STINGER_INTENSIFY = 0;
    private static final int STINGER_RELEASE = 1;
    private static final int STINGER_DEEP = 2;
    private static final long NO_SCHEDULED_TIME = -1L;

    private static Level lastLevel;
    private static boolean playerWasPresent = false;
    private static BlockPos center;
    private static int cursor = VOLUME;
    private static int hiveDensityNearby;
    private static int stableHiveDensity;
    private static boolean zoneScanReady;
    private static int closeHiveBlockCount;
    private static boolean insideStructure;
    private static double nearestHive = Double.POSITIVE_INFINITY;
    private static HiveAmbientSoundInstance sound;
    private static SoundEvent currentLoopEvent;
    private static HiveAmbientSoundInstance closeSound;
    private static long nextPulseAt = NO_SCHEDULED_TIME;
    private static long nextTonalStingerAt = NO_SCHEDULED_TIME;
    private static long nextHeartbeatAt = NO_SCHEDULED_TIME;
    private static boolean nextHiveHeartbeatEvent = true;
    private static SimpleSoundInstance heartbeatSound;
    private static boolean heartbeatPlaying = false;
    private static int currentZone = -1;
    private static int pendingZone = -1;
    private static int pendingZoneTicks = 0;
    private static boolean zoneKnown = false;

    private HiveAmbientSoundHandler() { }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft client = Minecraft.getInstance();
        ClientLevel level = client.level;
        if (level == null) return;
        if (client.player == null) {
            if (playerWasPresent) {
                reset();
                playerWasPresent = false;
            }
            return;
        }
        playerWasPresent = true;
        if (level != lastLevel) {
            reset();
            lastLevel = level;
        }
        if (center == null || cursor >= VOLUME && level.getGameTime() % 40L == 0L) {
            center = client.player.blockPosition().immutable();
            cursor = 0;
            hiveDensityNearby = 0;
            closeHiveBlockCount = 0;
            nearestHive = Double.POSITIVE_INFINITY;
        }
        if (cursor < VOLUME) {
            long scanStartedAt = System.nanoTime();
            int end = Math.min(VOLUME, cursor + BUDGET);
            BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
            while (cursor < end) {
                int index = cursor++;
                int dx = index % SIDE - RADIUS;
                int dy = index / SIDE % SIDE - RADIUS;
                int dz = index / (SIDE * SIDE) - RADIUS;
                int distanceSquared = dx * dx + dy * dy + dz * dz;
                if (distanceSquared > RADIUS * RADIUS) continue;

                pos.set(center.getX() + dx, center.getY() + dy, center.getZ() + dz);
                if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) continue;
                BlockState state = level.getBlockState(pos);
                boolean hiveBlock = state.is(ModBlocks.PULSING_HEART.get())
                        || state.is(ModBlocks.LIVING_FLESH.get())
                        || state.is(ModBlocks.FLESH_VEINS.get());
                if (!hiveBlock) continue;
                hiveDensityNearby++;
                if (distanceSquared <= 16) closeHiveBlockCount++;
                nearestHive = Math.min(nearestHive, Math.sqrt(distanceSquared));
            }
            long elapsed = System.nanoTime() - scanStartedAt;
            if (elapsed > 1_000_000L) {
                CarnisMod.LOGGER.debug("Slow ambient scan batch: {} ms", elapsed / 1_000_000.0D);
            }
            if (cursor < VOLUME) {
                if (zoneScanReady) updateZone(level, client.player);
                return;
            }
            stableHiveDensity = hiveDensityNearby;
            zoneScanReady = true;
        }

        if (zoneScanReady) updateZone(level, client.player);
        updateAmbience(client, level);
    }

    private static void updateAmbience(Minecraft client, ClientLevel level) {
        if (sound != null && sound.isStopped()) {
            sound = null;
            currentLoopEvent = null;
        }
        if (closeSound != null && closeSound.isStopped()) closeSound = null;

        float targetVolume = 0.0F;
        if (Double.isFinite(nearestHive)) {
            targetVolume = 0.45F * (float) (1.0D - nearestHive / (RADIUS + 1.0D));
        }
        targetVolume = Mth.clamp(targetVolume, 0.0F, 0.45F);
        SoundEvent wantedBed = targetVolume > 0.0F ? selectZoneBed() : null;
        if (targetVolume > 0.0F && wantedBed == null) targetVolume = 0.0F;
        if (!insideStructure && closeHiveBlockCount > CLOSE_STRUCTURE_ENTER) {
            insideStructure = true;
        } else if (insideStructure && closeHiveBlockCount < CLOSE_STRUCTURE_EXIT) {
            insideStructure = false;
        }

        if (targetVolume > 0.0F) {
            if (sound != null && currentLoopEvent != wantedBed) {
                sound.setTarget(0.0F);
                sound = null;
                currentLoopEvent = null;
            }
            if (sound == null) {
                sound = new HiveAmbientSoundInstance(level, wantedBed, targetVolume);
                currentLoopEvent = wantedBed;
                client.getSoundManager().play(sound);
            } else {
                sound.setTarget(targetVolume);
            }

            // Keep the existing close ambience as a separate layer over the selected zonal bed.
            if (insideStructure) {
                if (closeSound == null) {
                    closeSound = new HiveAmbientSoundInstance(
                            level, ModSounds.HIVE_AMBIENT_CLOSE.get(), Mth.clamp(targetVolume * 0.55F, 0.0F, 0.25F));
                    client.getSoundManager().play(closeSound);
                } else {
                    closeSound.setTarget(Mth.clamp(targetVolume * 0.55F, 0.0F, 0.25F));
                }
            } else if (closeSound != null) {
                closeSound.setTarget(0.0F);
                closeSound = null;
            }
            playPeriodicEvents(client, level);
        } else {
            if (sound != null) sound.setTarget(0.0F);
            if (closeSound != null) closeSound.setTarget(0.0F);
            nextPulseAt = NO_SCHEDULED_TIME;
            nextTonalStingerAt = NO_SCHEDULED_TIME;
            nextHeartbeatAt = NO_SCHEDULED_TIME;
            nextHiveHeartbeatEvent = true;
            stopHeartbeat(client);
        }
    }

    /** Select an available zonal asset; the established ambient bank is the canonical fallback. */
    private static SoundEvent selectZoneBed() {
        String[] zonePaths = switch (currentZone) {
            case ZONE_SURFACE -> new String[]{"hive/amb_surface"};
            case ZONE_DEEP -> new String[]{"hive/amb_deep"};
            case ZONE_CORE -> new String[]{"hive/amb_core"};
            default -> new String[]{"hive/amb_threshold"};
        };
        if (hasAmbientAssets(zonePaths)) {
            return switch (currentZone) {
                case ZONE_SURFACE -> ModSounds.HIVE_AMB_SURFACE.get();
                case ZONE_DEEP -> ModSounds.HIVE_AMB_DEEP.get();
                case ZONE_CORE -> ModSounds.HIVE_AMB_CORE.get();
                default -> ModSounds.HIVE_AMB_THRESHOLD.get();
            };
        }
        if (hasAmbientAssets("amb/hive_ambient_01", "amb/hive_ambient_02", "amb/hive_ambient_03")) {
            return ModSounds.HIVE_AMBIENT.get();
        }
        return null;
    }

    /** Presence gates playback only; sound registration and sounds.json declarations remain unconditional. */
    private static boolean hasAmbientAssets(String... paths) {
        ResourceManager manager = Minecraft.getInstance().getResourceManager();
        if (ambientResourceManager != manager) {
            AMBIENT_RESOURCE_CACHE.clear();
            AMBIENT_WARNING_TIMES.clear();
            ambientResourceManager = manager;
        }
        boolean complete = true;
        for (String path : paths) {
            Boolean present = AMBIENT_RESOURCE_CACHE.get(path);
            if (present == null) {
                ResourceLocation location = new ResourceLocation("carnis", "sounds/" + path + ".ogg");
                present = manager.getResource(location).isPresent();
                AMBIENT_RESOURCE_CACHE.put(path, present);
            }
            if (!present) {
                complete = false;
                long now = Util.getMillis();
                long last = AMBIENT_WARNING_TIMES.getOrDefault(path, Long.MIN_VALUE / 2);
                if (now >= last && now - last >= AMBIENT_WARNING_COOLDOWN_MS) {
                    CarnisMod.LOGGER.warn("Hive ambience asset is missing: carnis:{}; using canonical fallback when available", path);
                    AMBIENT_WARNING_TIMES.put(path, now);
                }
            }
        }
        return complete;
    }

    /** Update the zone state once per client tick; initialization is intentionally silent. */
    private static void updateZone(ClientLevel level, Player player) {
        int desired = calculateZone(player);
        if (!zoneKnown) {
            currentZone = desired;
            pendingZone = -1;
            pendingZoneTicks = 0;
            zoneKnown = true;
            return;
        }
        if (desired == currentZone) {
            pendingZone = -1;
            pendingZoneTicks = 0;
            return;
        }
        if (desired != pendingZone) {
            pendingZone = desired;
            pendingZoneTicks = 0;
        }
        pendingZoneTicks++;
        if (pendingZoneTicks < 60) return;

        int oldZone = currentZone;
        int newZone = pendingZone;
        currentZone = newZone;
        pendingZone = -1;
        pendingZoneTicks = 0;

        if (newZone > oldZone) {
            if (newZone - oldZone > 1) {
                playZoneStinger(level, player, STINGER_DEEP);
            } else {
                playZoneStinger(level, player, STINGER_INTENSIFY);
            }
        } else if (newZone < oldZone) {
            playZoneStinger(level, player, STINGER_RELEASE);
        }
    }

    private static int calculateZone(Player player) {
        int density = stableHiveDensity;
        int y = player.blockPosition().getY();
        if (density > DENSITY_CORE) return ZONE_CORE;
        if (density > DENSITY_SURFACE) {
            boolean wasDeep = currentZone == ZONE_DEEP;
            if (wasDeep) return (y < 44) ? ZONE_DEEP : ZONE_SURFACE;
            return (y < 36) ? ZONE_DEEP : ZONE_SURFACE;
        }
        return ZONE_THRESHOLD;
    }

    private static void playZoneStinger(Level level, Player player, int stingerType) {
        if (!zoneKnown) return;
        SoundEvent stinger = switch (stingerType) {
            case STINGER_INTENSIFY -> ModSounds.ZONE_STINGER_INTENSIFY.get();
            case STINGER_RELEASE -> ModSounds.ZONE_STINGER_RELEASE.get();
            case STINGER_DEEP -> ModSounds.ZONE_STINGER_DEEP.get();
            default -> null;
        };
        if (stinger == null) return;

        level.playSound(null, player.blockPosition(), stinger, SoundSource.AMBIENT, 1.0F, 1.0F);
    }

    private static void playPeriodicEvents(Minecraft client, ClientLevel level) {
        long now = level.getGameTime();
        if (nextPulseAt == NO_SCHEDULED_TIME) nextPulseAt = now + PULSE_INTERVAL_TICKS;
        if (now >= nextPulseAt) {
            playOneShot(client, ModSounds.HIVE_PULSE.get());
            do {
                nextPulseAt += PULSE_INTERVAL_TICKS;
            } while (nextPulseAt <= now);
        }

        if (nextTonalStingerAt == NO_SCHEDULED_TIME) {
            nextTonalStingerAt = now + 1200L + level.random.nextInt(1201);
        } else if (now >= nextTonalStingerAt) {
            playOneShot(client, ModSounds.HIVE_AMBIENT_TONAL_STINGER.get());
            nextTonalStingerAt = now + 1200L + level.random.nextInt(1201);
        }

        if (insideStructure) {
            if (nextHeartbeatAt == NO_SCHEDULED_TIME) {
                nextHeartbeatAt = now + nextHeartbeatDelay(level);
            } else if (now >= nextHeartbeatAt) {
                // Alternate the separately registered core heartbeat events; they do not replace Hive Pulse.
                SoundEvent heartbeat = nextHiveHeartbeatEvent
                        ? ModSounds.HIVE_HEARTBEAT.get()
                        : ModSounds.HEARTBEAT_LOOP.get();
                if (heartbeat == ModSounds.HEARTBEAT_LOOP.get()) {
                    if (heartbeatPlaying && !client.getSoundManager().isActive(heartbeatSound)) {
                        heartbeatPlaying = false;
                        heartbeatSound = null;
                    }
                    if (!heartbeatPlaying) {
                        heartbeatSound = SimpleSoundInstance.forAmbientAddition(heartbeat);
                        client.getSoundManager().play(heartbeatSound);
                        heartbeatPlaying = true;
                    }
                } else {
                    playOneShot(client, heartbeat);
                }
                nextHiveHeartbeatEvent = !nextHiveHeartbeatEvent;
                nextHeartbeatAt = now + nextHeartbeatDelay(level);
            }
        } else {
            nextHeartbeatAt = NO_SCHEDULED_TIME;
            nextHiveHeartbeatEvent = true;
            stopHeartbeat(client);
        }
    }

    private static int nextHeartbeatDelay(ClientLevel level) {
        return HEARTBEAT_MIN_INTERVAL
                + level.random.nextInt(HEARTBEAT_MAX_INTERVAL - HEARTBEAT_MIN_INTERVAL + 1);
    }

    private static void playOneShot(Minecraft client, SoundEvent event) {
        client.getSoundManager().play(SimpleSoundInstance.forAmbientAddition(event));
    }

    private static void stopHeartbeat(Minecraft client) {
        if (heartbeatSound != null) client.getSoundManager().stop(heartbeatSound);
        heartbeatSound = null;
        heartbeatPlaying = false;
    }

    private static void reset() {
        stopHeartbeat(Minecraft.getInstance());
        if (sound != null) sound.end();
        if (closeSound != null) closeSound.end();
        sound = null;
        currentLoopEvent = null;
        closeSound = null;
        center = null;
        cursor = VOLUME;
        hiveDensityNearby = 0;
        stableHiveDensity = 0;
        zoneScanReady = false;
        closeHiveBlockCount = 0;
        insideStructure = false;
        nearestHive = Double.POSITIVE_INFINITY;
        nextPulseAt = NO_SCHEDULED_TIME;
        nextTonalStingerAt = NO_SCHEDULED_TIME;
        nextHeartbeatAt = NO_SCHEDULED_TIME;
        nextHiveHeartbeatEvent = true;

        currentZone = -1;
        pendingZone = -1;
        pendingZoneTicks = 0;
        heartbeatPlaying = false;
        zoneKnown = false;
    }

}
