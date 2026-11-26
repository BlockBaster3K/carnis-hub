package com.carnis.mod.effect;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModEffects;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ThermalShockEffect extends MobEffect {
    public ThermalShockEffect() {
        super(MobEffectCategory.HARMFUL, 0x3B6B8C);
        addAttributeModifier(Attributes.MOVEMENT_SPEED, "7e0881ae-07f3-48da-b5ae-17c8da3fe023",
                -0.30D, AttributeModifier.Operation.MULTIPLY_TOTAL);
    }

    /** Applied before ordinary mitigation; no additional damage event is fired. */
    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onHurt(LivingHurtEvent event) {
        if (!event.isCanceled() && event.getAmount() > 0.0F && !event.getEntity().level().isClientSide
                && event.getEntity().hasEffect(ModEffects.THERMAL_SHOCK.get()))
            event.setAmount(event.getAmount() * 1.25F);
    }
}
