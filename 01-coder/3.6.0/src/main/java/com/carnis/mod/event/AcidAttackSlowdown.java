package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.UUID;

/**
 * Owns the short-lived attack-speed penalty inflicted by Amalgam acid.
 *
 * <p>The fixed UUID makes repeated splashes refresh one modifier instead of
 * stacking without bound. The modifier itself is transient; its small timing
 * record lets a reconnect restore the remaining duration, while the attribute
 * modifier is still never serialized as a permanent player statistic.</p>
 */
@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class AcidAttackSlowdown {
    private static final UUID MODIFIER_ID = UUID.fromString(
            "998af1a3-cca9-508b-9a0f-df56cb810b54"
    );
    private static final String MODIFIER_NAME =
            "Carnis Amalgam acid attack slowdown";
    private static final String EXPIRY_TAG =
            CarnisMod.MOD_ID + ":acid_attack_slow_until";
    private static final String AMOUNT_TAG =
            CarnisMod.MOD_ID + ":acid_attack_slow_amount";

    private static final double STANDARD_AMOUNT = -0.25D;
    private static final double EMPOWERED_AMOUNT = -0.40D;

    private AcidAttackSlowdown() {
    }

    public static void apply(
            ServerPlayer player,
            int durationTicks,
            boolean empowered
    ) {
        AttributeInstance attackSpeed = player.getAttribute(
                Attributes.ATTACK_SPEED
        );

        if (attackSpeed == null || durationTicks <= 0) {
            return;
        }

        CompoundTag persistentData = player.getPersistentData();
        long expiryTick = Math.max(
                persistentData.getLong(EXPIRY_TAG),
                player.level().getGameTime() + durationTicks
        );
        double amount = empowered
                ? EMPOWERED_AMOUNT
                : STANDARD_AMOUNT;

        if (persistentData.contains(AMOUNT_TAG)) {
            amount = Math.min(
                    amount,
                    sanitizeAmount(persistentData.getDouble(AMOUNT_TAG))
            );
        }

        persistentData.putLong(EXPIRY_TAG, expiryTick);
        persistentData.putDouble(AMOUNT_TAG, amount);
        replaceModifier(attackSpeed, amount);
    }

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (
                event.phase != TickEvent.Phase.END
                        || !(event.player instanceof ServerPlayer player)
        ) {
            return;
        }

        CompoundTag persistentData = player.getPersistentData();

        if (!persistentData.contains(EXPIRY_TAG)) {
            return;
        }

        AttributeInstance attackSpeed = player.getAttribute(
                Attributes.ATTACK_SPEED
        );

        if (player.level().getGameTime() >= persistentData.getLong(EXPIRY_TAG)) {
            if (attackSpeed != null) {
                attackSpeed.removeModifier(MODIFIER_ID);
            }

            persistentData.remove(EXPIRY_TAG);
            persistentData.remove(AMOUNT_TAG);
            return;
        }

        // Transient modifiers are deliberately absent from saved attributes.
        // Recreate this one if the player reconnects before the timer expires.
        if (
                attackSpeed != null
                        && attackSpeed.getModifier(MODIFIER_ID) == null
        ) {
            replaceModifier(
                    attackSpeed,
                    sanitizeAmount(persistentData.getDouble(AMOUNT_TAG))
            );
        }
    }

    private static double sanitizeAmount(double amount) {
        return Math.max(
                EMPOWERED_AMOUNT,
                Math.min(STANDARD_AMOUNT, amount)
        );
    }

    private static void replaceModifier(
            AttributeInstance attackSpeed,
            double amount
    ) {
        attackSpeed.removeModifier(MODIFIER_ID);
        attackSpeed.addTransientModifier(
                new AttributeModifier(
                        MODIFIER_ID,
                        MODIFIER_NAME,
                        amount,
                        AttributeModifier.Operation.MULTIPLY_TOTAL
                )
        );
    }
}
