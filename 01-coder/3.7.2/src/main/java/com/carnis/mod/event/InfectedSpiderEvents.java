package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.InfectedSpiderEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class InfectedSpiderEvents {
    private InfectedSpiderEvents() {
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onHit(LivingHurtEvent event) {
        if (!event.isCanceled() && event.getAmount() > 0.0F
                && event.getEntity().level() instanceof ServerLevel
                && event.getSource().getEntity() instanceof InfectedSpiderEntity spider
                && event.getSource().getDirectEntity() == spider) {
            event.getEntity().addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 1));
        }
    }
}
