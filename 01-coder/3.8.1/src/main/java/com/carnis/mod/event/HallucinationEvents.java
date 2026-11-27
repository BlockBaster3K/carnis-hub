package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.hallucination.HallucinationType;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.item.NeuroWeave;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.network.packet.ClientboundHallucinationPacket;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class HallucinationEvents {
    public static final float INFECTION_THRESHOLD = 60.0F;
    public static final int MIN_DELAY_TICKS = 20 * 20;
    public static final int MAX_DELAY_TICKS = 50 * 20;

    private static final float MIN_VOLUME_MULTIPLIER = 0.85F;
    private static final float MAX_VOLUME_MULTIPLIER = 1.15F;
    private static final String DELAY_TAG =
            CarnisMod.MOD_ID + ":hallucination_delay_ticks";
    private static final HallucinationType[] TYPES =
            HallucinationType.values();

    private HallucinationEvents() {
    }

    // ОТКЛЮЧЕНО: дублирует PlayerHallucinationHandler. Сервер не должен отправлять звуковые пакеты галлюцинаций.
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (
                event.phase != TickEvent.Phase.END
                        || !(event.player instanceof ServerPlayer player)
        ) {
            return;
        }

        CompoundTag persistentData = player.getPersistentData();

        if (
                !player.isAlive()
                        || player.isSpectator()
                        || NeuroResonatorHelmetItem.isEquipped(player)
                        || PlayerInfectionApi.getInfectionLevel(player)
                        < INFECTION_THRESHOLD
        ) {
            resetHallucinationTimer(player);
            return;
        }

        if (!persistentData.contains(DELAY_TAG)) {
            scheduleNextHallucination(persistentData, player.getRandom(), PlayerInfectionApi.getInfectionLevel(player) >= 100.0F);
            return;
        }

        int remainingTicks = persistentData.getInt(DELAY_TAG);

        if (remainingTicks > 1) {
            persistentData.putInt(DELAY_TAG, remainingTicks - 1);
            return;
        }

        RandomSource random = player.getRandom();
        HallucinationType type = TYPES[random.nextInt(TYPES.length)];
        float volumeMultiplier = MIN_VOLUME_MULTIPLIER
                + random.nextFloat()
                * (MAX_VOLUME_MULTIPLIER - MIN_VOLUME_MULTIPLIER);
        volumeMultiplier *= NeuroWeave.infectionMultiplier(player);
        Vec3 relativeOffset = createRelativeOffset(type, random);

        ModMessages.sendHallucination(
                player,
                new ClientboundHallucinationPacket(
                        type,
                        volumeMultiplier,
                        relativeOffset
                )
        );
        scheduleNextHallucination(persistentData, random, PlayerInfectionApi.getInfectionLevel(player) >= 100.0F);
    }

    public static void resetHallucinationTimer(ServerPlayer player) {
        player.getPersistentData().remove(DELAY_TAG);
    }

    private static void scheduleNextHallucination(
            CompoundTag persistentData,
            RandomSource random, boolean critical
    ) {
        persistentData.putInt(
                DELAY_TAG,
                random.nextIntBetweenInclusive(
                        critical ? 100 : MIN_DELAY_TICKS,
                        critical ? 200 : MAX_DELAY_TICKS
                )
        );
    }

    private static Vec3 createRelativeOffset(
            HallucinationType type,
            RandomSource random
    ) {
        return switch (type) {
            case CREEPER_HISS -> new Vec3(
                    0.0D,
                    0.75D,
                    -randomBetween(random, 2.0D, 3.0D)
            );
            case PHANTOM_FOOTSTEPS -> new Vec3(
                    randomBetween(random, -1.25D, 1.25D),
                    -0.15D,
                    -randomBetween(random, 2.0D, 3.5D)
            );
            case WHISPER -> new Vec3(
                    (random.nextBoolean() ? 1.0D : -1.0D)
                            * randomBetween(random, 0.55D, 1.1D),
                    1.25D,
                    -randomBetween(random, 1.0D, 2.0D)
            );
            case FALSE_DAMAGE -> new Vec3(0.0D, 1.0D, 0.0D);
        };
    }

    private static double randomBetween(
            RandomSource random,
            double minimum,
            double maximum
    ) {
        return minimum + random.nextDouble() * (maximum - minimum);
    }
}
