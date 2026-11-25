package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.biomass.PlayerBiomassCapability;
import com.carnis.mod.capability.biomass.PlayerBiomassEvents;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.BiomassValued;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.Spider;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.UUID;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisEvents {
    private CarnisEvents() {
    }

    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void protectHiveTissueFromInfectedCreeper(ExplosionEvent.Detonate event) {
        var explosion = event.getExplosion();
        Entity exploder = explosion.getExploder();
        if (exploder == null) exploder = explosion.getIndirectSourceEntity();
        if (!(exploder instanceof InfectedCreeperEntity)) return;
        event.getAffectedBlocks().removeIf(pos -> {
            var state = event.getLevel().getBlockState(pos);
            return state.is(ModBlocks.LIVING_FLESH.get())
                    || state.is(ModBlocks.FLESH_BULB.get())
                    || state.is(ModBlocks.CREEPING_TENDRILS.get())
                    || state.is(ModBlocks.SPORE_SPROUT.get())
                    || state.is(ModBlocks.NEURAL_MOSS.get())
                    || state.is(ModBlocks.PULSING_HEART.get())
                    || state.is(ModBlocks.OSSIFIED_FLESH.get())
                    || state.is(ModBlocks.CHARRED_FLESH.get())
                    || state.is(ModBlocks.FIREPROOF_FLESH.get())
                    || state.is(ModBlocks.FLESH_VEINS.get())
                    || state.is(ModBlocks.STOMACH_POOL.get())
                    || state.is(ModBlocks.NERVE_PILLAR.get())
                    || state.is(ModBlocks.SINEW_SPIKES.get())
                    || state.is(ModBlocks.PUSTULE_CLUSTER.get())
                    || state.is(ModBlocks.HIVE_EYE.get())
                    || state.is(ModBlocks.HIVE_MEMBRANE.get())
                    || state.is(ModBlocks.SYNAPSE_NODE.get())
                    || state.is(ModBlocks.INCUBATION_CYST.get())
                    || state.is(ModBlocks.PURIFIER_LAMP.get());
        });
    }

    @SubscribeEvent(priority = EventPriority.HIGH, receiveCanceled = true)
    public static void onLivingDeath(LivingDeathEvent event) {
        LivingEntity victim = event.getEntity();
        if (!(victim.level() instanceof ServerLevel level)) return;

        Entity killer = event.getSource().getEntity();
        if (event.isCanceled() || victim instanceof Player || killer == null || killer == victim) return;

        if (victim instanceof BiomassValued valuedVictim) {
            if (killer instanceof ServerPlayer player) {
                awardBiomass(player, valuedVictim.getBiomassValue());
            }
            return;
        }

        ServerPlayer recipient = null;
        if (killer instanceof ServerPlayer player) {
            float infection = PlayerInfectionApi.getInfectionLevel(player);
            if (infection <= 0.0F) return;
            recipient = player;
        } else if (killer instanceof HivemindLinkedMob) {
            if (victim instanceof HivemindLinkedMob) return;
            if (killer instanceof TamableAnimal tame && tame.getOwnerUUID() != null) {
                UUID ownerId = tame.getOwnerUUID();
                recipient = level.getServer().getPlayerList().getPlayer(ownerId);
                if (recipient == null) {
                    CarnisMod.LOGGER.warn("Could not award biomass: owner {} is offline", ownerId);
                    return;
                }
            }
        } else {
            return;
        }

        long multiplier = 1L;
        if (victim instanceof Mob mob && DartTreatmentEvents.isMutating(mob)) {
            multiplier *= 3L;
        }
        if (InfectionHandler.isInfected(victim)) {
            multiplier *= 2L;
        }
        long total = basePoints(victim) * multiplier;

        if (recipient != null) {
            awardBiomass(recipient, total);
        } else {
            CarnisWorldData data = CarnisWorldData.get(level);
            data.addBiomassPoints(total);
            ModMessages.sendToPlayersInLevel(level);
        }
    }

    private static void awardBiomass(ServerPlayer player, long amount) {
        if (amount <= 0L) return;
        var biomass = player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS);
        if (!biomass.isPresent()) {
            CarnisMod.LOGGER.warn("Could not award biomass to {}: capability is absent", player.getUUID());
            return;
        }
        biomass.ifPresent(data -> {
            data.addBiomassPoints(amount);
            PlayerBiomassEvents.syncToPlayer(player);
        });
    }

    private static long basePoints(LivingEntity victim) {
        if (victim instanceof Zombie) return 1L;

        EntityType<?> type = victim.getType();
        if (type == EntityType.ALLAY || type == EntityType.VEX || type == EntityType.WARDEN
                || type == EntityType.ELDER_GUARDIAN || type == EntityType.IRON_GOLEM
                || type == EntityType.SNOW_GOLEM || type == EntityType.TRADER_LLAMA) return 25L;
        if (victim instanceof Creeper || victim instanceof Spider) return 5L;
        if (victim instanceof Animal) return 5L;
        if (victim instanceof Monster) return 15L;
        return 5L;
    }
}
