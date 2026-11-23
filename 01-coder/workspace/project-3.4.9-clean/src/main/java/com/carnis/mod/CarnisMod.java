package com.carnis.mod;

import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModCreativeTabs;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.network.ModMessages;
import com.mojang.logging.LogUtils;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.server.ServerStartingEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;
import software.bernie.geckolib.GeckoLib;

@Mod(CarnisMod.MOD_ID)
public final class CarnisMod {
    public static final String MOD_ID = "carnis";
    public static final Logger LOGGER = LogUtils.getLogger();

    public CarnisMod() {
        GeckoLib.initialize();

        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();

        com.carnis.mod.init.ModEffects.register(modEventBus);
        com.carnis.mod.init.ModFluids.register(modEventBus);
        ModBlocks.register(modEventBus);
        ModBlockEntities.register(modEventBus);
        ModEntities.register(modEventBus);
        com.carnis.mod.init.ModFeatures.register(modEventBus);
        ModItems.register(modEventBus);
        ModCreativeTabs.register(modEventBus);
        ModSounds.register(modEventBus);
        com.carnis.mod.init.ModParticles.register(modEventBus);

        modEventBus.addListener(this::onCommonSetup);

        ModLoadingContext.get().registerConfig(
                ModConfig.Type.SERVER,
                CarnisConfig.SERVER_SPEC,
                "carnis-server.toml"
        );
        ModLoadingContext.get().registerConfig(
                ModConfig.Type.CLIENT,
                CarnisConfig.CLIENT_SPEC,
                "carnis-client.toml"
        );

        MinecraftForge.EVENT_BUS.register(this);
    }

    private void onCommonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(ModMessages::register);
        LOGGER.info("Initializing {} common systems", MOD_ID);
    }

    @SubscribeEvent
    public void onServerStarting(ServerStartingEvent event) {
        LOGGER.info("{} server systems are ready", MOD_ID);
    }
}
