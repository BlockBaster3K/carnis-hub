package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;

import com.carnis.mod.init.ModEntities;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.MOD
)
public final class ModEntityEvents {
    private ModEntityEvents() {
    }

    @SubscribeEvent
    public static void onSpawnPlacements(net.minecraftforge.event.entity.SpawnPlacementRegisterEvent event) {
        ModEntities.registerSpawnPlacements(event);
    }

    @SubscribeEvent
    public static void onCreateEntityAttributes(
            EntityAttributeCreationEvent event
    ) {
        event.put(ModEntities.HIVE_SENTINEL.get(), com.carnis.mod.entity.HiveSentinelEntity.createAttributes().build());
        event.put(ModEntities.CEREBRAL_NEXUS.get(), com.carnis.mod.entity.CerebralNexusEntity.createAttributes().build());
        event.put(ModEntities.BIOMASS_MAGGOT.get(), com.carnis.mod.entity.BiomassMaggotEntity.createAttributes().build());
        event.put(ModEntities.PARASITIC_TENDRIL.get(), com.carnis.mod.entity.ParasiticTendrilEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_ZOMBIE.get(), InfectedZombieEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_SKELETON.get(), InfectedSkeletonEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_CREEPER.get(), InfectedCreeperEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_SPIDER.get(), InfectedSpiderEntity.createAttributes().build());

        event.put(
                ModEntities.FLESH_AMALGAM.get(),
                FleshAmalgamEntity.createAttributes().build()
        );
    }
}
