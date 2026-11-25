package com.carnis.mod.capability.infection;

import com.carnis.mod.CarnisMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.CapabilityManager;
import net.minecraftforge.common.capabilities.CapabilityToken;
import net.minecraftforge.common.capabilities.RegisterCapabilitiesEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.MOD
)
public final class PlayerInfectionCapability {
    public static final ResourceLocation ID = new ResourceLocation(
            CarnisMod.MOD_ID,
            "player_infection"
    );

    public static final Capability<IPlayerInfection> PLAYER_INFECTION =
            CapabilityManager.get(new CapabilityToken<>() {
            });

    private PlayerInfectionCapability() {
    }

    @SubscribeEvent
    public static void registerCapabilities(RegisterCapabilitiesEvent event) {
        event.register(IPlayerInfection.class);
    }
}
