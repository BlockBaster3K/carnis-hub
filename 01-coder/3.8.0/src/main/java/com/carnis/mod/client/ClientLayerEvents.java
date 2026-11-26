package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.renderer.layer.IncubatingEntityLayer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ClientLayerEvents {
    private ClientLayerEvents() {
    }

    @SubscribeEvent
    public static void onAddLayers(EntityRenderersEvent.AddLayers event) {
        for (String skin : event.getSkins()) {
            LivingEntityRenderer<AbstractClientPlayer, PlayerModel<AbstractClientPlayer>> renderer = event.getSkin(skin);
            if (renderer != null) {
                renderer.addLayer(new IncubatingEntityLayer<>(renderer));
            }
        }

        addLayerTo(event, EntityType.ZOMBIE);
        addLayerTo(event, EntityType.SKELETON);
        addLayerTo(event, EntityType.HUSK);
        addLayerTo(event, EntityType.DROWNED);
        addLayerTo(event, EntityType.STRAY);
        addLayerTo(event, EntityType.WITHER_SKELETON);
        addLayerTo(event, EntityType.VILLAGER);
        addLayerTo(event, EntityType.WANDERING_TRADER);
        addLayerTo(event, EntityType.PIGLIN);
        addLayerTo(event, EntityType.PIGLIN_BRUTE);
        addLayerTo(event, EntityType.ZOMBIFIED_PIGLIN);
        addLayerTo(event, EntityType.PIG);
        addLayerTo(event, EntityType.COW);
        addLayerTo(event, EntityType.SHEEP);
        addLayerTo(event, EntityType.CHICKEN);
        addLayerTo(event, EntityType.SPIDER);
        addLayerTo(event, EntityType.HORSE);
        addLayerTo(event, EntityType.CREEPER);
        addLayerTo(event, EntityType.IRON_GOLEM);

        // Эти идентификаторы соответствуют ванильным живым носителям Minecraft 1.20.1.
        for (String id : new String[]{"goat", "llama", "trader_llama", "donkey", "mule",
                "skeleton_horse", "zombie_horse", "fox", "wolf", "cat", "ocelot", "parrot",
                "panda", "polar_bear", "turtle", "frog", "camel", "sniffer", "strider",
                "mooshroom", "rabbit", "bee", "hoglin", "tadpole", "cod", "salmon",
                "pufferfish", "tropical_fish", "squid", "glow_squid", "dolphin", "axolotl", "cave_spider"}) {
            addVanillaLivingLayer(event, id);
        }
    }

    @SuppressWarnings("unchecked")
    private static void addVanillaLivingLayer(EntityRenderersEvent.AddLayers event, String path) {
        EntityType<?> type = net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES
                .getValue(new net.minecraft.resources.ResourceLocation("minecraft", path));
        if (type != null) addLayerTo(event, (EntityType<? extends LivingEntity>) type);
    }

    private static <T extends LivingEntity, M extends EntityModel<T>> void addLayerTo(
            EntityRenderersEvent.AddLayers event,
            EntityType<T> entityType
    ) {
        LivingEntityRenderer<T, M> renderer = event.getRenderer(entityType);
        if (renderer != null) {
            renderer.addLayer(new IncubatingEntityLayer<>(renderer));
        }
    }
}
