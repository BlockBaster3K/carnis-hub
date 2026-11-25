package com.carnis.mod.capability.biomass;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.network.packet.SyncPlayerBiomassPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.event.AttachCapabilitiesEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Прикрепление и перенос персональной биомассы на сервере. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerBiomassEvents {
    private PlayerBiomassEvents() { }

    @SubscribeEvent
    public static void attach(AttachCapabilitiesEvent<Entity> event) {
        if (!(event.getObject() instanceof ServerPlayer)) return;
        PlayerBiomassProvider provider = new PlayerBiomassProvider();
        event.addCapability(PlayerBiomassCapability.ID, provider);
        event.addListener(provider::invalidateCaps);
    }

    /** Отправляется после изменений через серверные операции следующих шагов. */
    public static void syncToPlayer(ServerPlayer player) {
        player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS).ifPresent(data ->
                ModMessages.sendToPlayer(new SyncPlayerBiomassPacket(data.getBiomassPoints()), player));
    }

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) syncToPlayer(player);
    }

    @SubscribeEvent
    public static void onDimensionChange(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) syncToPlayer(player);
    }

    @SubscribeEvent
    public static void onPlayerRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) syncToPlayer(player);
    }

    @SubscribeEvent
    public static void clonePlayer(PlayerEvent.Clone event) {
        if (!(event.getEntity() instanceof ServerPlayer)
                || !(event.getOriginal() instanceof ServerPlayer)) return;
        event.getOriginal().reviveCaps();
        try {
            event.getOriginal().getCapability(PlayerBiomassCapability.PLAYER_BIOMASS).ifPresent(oldData ->
                    event.getEntity().getCapability(PlayerBiomassCapability.PLAYER_BIOMASS).ifPresent(newData ->
                            newData.deserializeNBT(oldData.serializeNBT())));
        } finally {
            event.getOriginal().invalidateCaps();
        }
    }
}
