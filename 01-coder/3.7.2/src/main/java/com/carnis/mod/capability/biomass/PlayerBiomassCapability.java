package com.carnis.mod.capability.biomass;

import com.carnis.mod.CarnisMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.CapabilityManager;
import net.minecraftforge.common.capabilities.CapabilityToken;
import net.minecraftforge.common.capabilities.RegisterCapabilitiesEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class PlayerBiomassCapability {
    public static final ResourceLocation ID = new ResourceLocation(CarnisMod.MOD_ID, "player_biomass");
    public static final Capability<PlayerBiomassData> PLAYER_BIOMASS =
            CapabilityManager.get(new CapabilityToken<>() { });

    private PlayerBiomassCapability() { }

    @SubscribeEvent
    public static void register(RegisterCapabilitiesEvent event) {
        event.register(PlayerBiomassData.class);
    }
}
