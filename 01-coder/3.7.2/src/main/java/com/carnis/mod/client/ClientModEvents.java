package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.gui.InfectionVeinsOverlay;
import com.carnis.mod.client.gui.PhantomEyesOverlay;
import com.carnis.mod.client.hud.BiomassHudOverlay;
import com.carnis.mod.client.renderer.FleshAmalgamRenderer;
import com.carnis.mod.client.renderer.DartRenderer;
import com.carnis.mod.client.renderer.PulsingHeartRenderer;
import com.carnis.mod.client.renderer.HiveEyeRenderer;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModEntities;
import net.minecraft.client.renderer.entity.ZombieRenderer;
import net.minecraft.client.renderer.entity.SkeletonRenderer;
import net.minecraft.client.renderer.entity.CreeperRenderer;
import net.minecraft.client.renderer.entity.SpiderRenderer;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.MOD,
        value = Dist.CLIENT
)
public final class ClientModEvents {
    private ClientModEvents() {
    }

    @SubscribeEvent
    public static void onRegisterRenderers(
            EntityRenderersEvent.RegisterRenderers event
    ) {
        event.registerEntityRenderer(ModEntities.HIVE_SENTINEL.get(), com.carnis.mod.client.renderer.HiveSentinelRenderer::new);
        event.registerEntityRenderer(ModEntities.CEREBRAL_NEXUS.get(), com.carnis.mod.client.renderer.CerebralNexusRenderer::new);
        event.registerEntityRenderer(ModEntities.BIOMASS_MAGGOT.get(), com.carnis.mod.client.renderer.BiomassMaggotRenderer::new);
        event.registerEntityRenderer(ModEntities.PARASITIC_TENDRIL.get(), com.carnis.mod.client.renderer.ParasiticTendrilRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_ZOMBIE.get(), com.carnis.mod.client.renderer.InfectedZombieRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_SKELETON.get(), com.carnis.mod.client.renderer.InfectedSkeletonRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_CREEPER.get(), com.carnis.mod.client.renderer.InfectedCreeperRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_SPIDER.get(), com.carnis.mod.client.renderer.InfectedSpiderRenderer::new);

        event.registerEntityRenderer(ModEntities.FLESH_SPAT.get(), net.minecraft.client.renderer.entity.ThrownItemRenderer::new);
        event.registerEntityRenderer(ModEntities.AMALGAM_BILE.get(), net.minecraft.client.renderer.entity.ThrownItemRenderer::new);
        event.registerEntityRenderer(ModEntities.HIVE_SPORE_CLOUD.get(), net.minecraft.client.renderer.entity.NoopRenderer::new);
        event.registerEntityRenderer(ModEntities.INOCULATOR_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.VIRAL_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.PURIFICATION_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.PUSTULE_GRENADE.get(), net.minecraft.client.renderer.entity.ThrownItemRenderer::new);
        event.registerBlockEntityRenderer(
                ModBlockEntities.PULSING_HEART.get(),
                PulsingHeartRenderer::new
        );
        event.registerBlockEntityRenderer(ModBlockEntities.HIVE_EYE.get(), HiveEyeRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.STOMACH_POOL.get(), com.carnis.mod.client.renderer.StomachPoolRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.NERVE_PILLAR.get(), com.carnis.mod.client.renderer.NervePillarRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.PUSTULE_CLUSTER.get(), com.carnis.mod.client.renderer.PustuleClusterRenderer::new);
        event.registerEntityRenderer(
                ModEntities.FLESH_AMALGAM.get(),
                FleshAmalgamRenderer::new
        );
    }

    @SubscribeEvent
    public static void onRegisterParticles(net.minecraftforge.client.event.RegisterParticleProvidersEvent event) {
        event.registerSpriteSet(com.carnis.mod.init.ModParticles.BIOMASS_SPARK.get(),
                com.carnis.mod.client.particle.BiomassSparkParticle.Provider::new);
        event.registerSpriteSet(com.carnis.mod.init.ModParticles.PURIFIER_FLAME.get(),
                com.carnis.mod.client.particle.BiomassSparkParticle.Provider::new);
    }

    @SubscribeEvent
    public static void onClientSetup(net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            net.minecraft.client.renderer.ItemBlockRenderTypes.setRenderLayer(
                    com.carnis.mod.init.ModFluids.SLUDGE_SOURCE.get(), net.minecraft.client.renderer.RenderType.translucent());
            net.minecraft.client.renderer.ItemBlockRenderTypes.setRenderLayer(
                    com.carnis.mod.init.ModFluids.SLUDGE_FLOWING.get(), net.minecraft.client.renderer.RenderType.translucent());
        });
    }

    @SubscribeEvent
    public static void onRegisterGuiOverlays(
            RegisterGuiOverlaysEvent event
    ) {
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "veins_overlay", new InfectionVeinsOverlay());
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "phantom_eyes", new PhantomEyesOverlay());
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "neuro_resonance", new com.carnis.mod.client.gui.overlay.NeuroResonanceOverlay());
        event.registerAboveAll("biomass_counter", new BiomassHudOverlay());
    }
}
