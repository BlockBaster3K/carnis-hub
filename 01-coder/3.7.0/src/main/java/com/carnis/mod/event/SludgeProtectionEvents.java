package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.item.NeuroWeave;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Neuro protection applies to the mod's sludge acid, not unrelated damage types. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class SludgeProtectionEvents {
    private SludgeProtectionEvents() { }

    @SubscribeEvent
    public static void onAttack(LivingAttackEvent event) {
        if (event.getSource().is(ModDamageTypes.TAINTED_SLUDGE)
                && NeuroWeave.hasSludgeImmuneBoots(event.getEntity())) event.setCanceled(true);
    }

    @SubscribeEvent
    public static void onHurt(LivingHurtEvent event) {
        if (!event.getSource().is(ModDamageTypes.TAINTED_SLUDGE)) return;
        float multiplier = NeuroWeave.infectionMultiplier(event.getEntity());
        if (multiplier <= 0.0F) event.setCanceled(true);
        else event.setAmount(event.getAmount() * multiplier);
    }
}
