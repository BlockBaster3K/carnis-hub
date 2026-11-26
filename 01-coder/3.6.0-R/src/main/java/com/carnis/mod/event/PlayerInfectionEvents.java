package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.capability.infection.PlayerInfectionCapability;
import com.carnis.mod.capability.infection.PlayerInfectionProvider;
import com.carnis.mod.entity.FleshSpatProjectileEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;
import com.carnis.mod.infection.PlayerInfectionManager;
import com.carnis.mod.init.ModBlockTags;
import com.carnis.mod.network.ModMessages;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.AttachCapabilitiesEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerInfectionEvents {
    public static final float SURFACE_INFECTION_PER_TICK = .05F;
    public static final float MOB_HIT_BASE_INFECTION = 1.0F;
    public static final float MOB_HIT_INFECTION_PER_DAMAGE = .5F;
    private PlayerInfectionEvents() { }
    @SubscribeEvent public static void onAttachCapabilities(AttachCapabilitiesEvent<Entity> event) {
        if (!(event.getObject() instanceof Player player)) return;
        PlayerInfectionProvider provider = new PlayerInfectionProvider(player);
        event.addCapability(PlayerInfectionCapability.ID, provider);
        event.addListener(provider::invalidate);
    }
    @SubscribeEvent public static void onPlayerClone(PlayerEvent.Clone event) {
        Player old = event.getOriginal();
        old.reviveCaps();
        try { PlayerInfectionManager.copyToClone(old, event.getEntity(), event.isWasDeath()); }
        finally { old.invalidateCaps(); }
    }
    @SubscribeEvent public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) { sync(event.getEntity()); }
    @SubscribeEvent public static void onRespawn(PlayerEvent.PlayerRespawnEvent event) { sync(event.getEntity()); }
    @SubscribeEvent public static void onDimension(PlayerEvent.PlayerChangedDimensionEvent event) { sync(event.getEntity()); }
    private static void sync(Player player) { if (player instanceof ServerPlayer server) ModMessages.sendPlayerInfection(server); }
    @SubscribeEvent public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)
                || !player.isAlive() || player.isSpectator() || !player.onGround()
                || !player.getBlockStateOn().is(ModBlockTags.INFECTIOUS_SURFACES)) return;
        PlayerInfectionApi.addExposure(player, SURFACE_INFECTION_PER_TICK);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onLivingHurt(LivingHurtEvent event) {
        if (event.isCanceled() || event.getAmount() <= 0 || !(event.getEntity() instanceof ServerPlayer player)
                || event.getSource().getDirectEntity() instanceof FleshSpatProjectileEntity
                || !NeuroArmorEventHandler.isHiveEntity(event.getSource().getEntity())) return;
        Entity attacker = event.getSource().getEntity();
        boolean direct = event.getSource().getDirectEntity() == attacker;
        if (direct && attacker instanceof InfectedZombieEntity) {
            final String cooldownKey = "carnis:infected_zombie_infection_next_tick";
            long now = player.level().getGameTime();
            if (now >= player.getPersistentData().getLong(cooldownKey)) {
                player.getPersistentData().putLong(cooldownKey, now + 40L);
                if (player.getRandom().nextFloat() < 0.02F) PlayerInfectionApi.addExposure(player, 2.0F);
            }
            return;
        }
        float amount = direct && attacker instanceof InfectedSkeletonEntity ? 10.0F
                : direct && attacker instanceof InfectedSpiderEntity ? 5.0F
                : MOB_HIT_BASE_INFECTION + event.getAmount() * MOB_HIT_INFECTION_PER_DAMAGE;
        PlayerInfectionApi.addExposure(player, amount);
    }
}
