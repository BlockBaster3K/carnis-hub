package com.carnis.mod.ecology;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.AssimilatingMob;
import com.carnis.mod.entity.BiomassMaggotEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.event.IncubationEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class RemainsEvents {
    private RemainsEvents() { }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onDeath(LivingDeathEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof Mob victim)
                || !(victim.level() instanceof ServerLevel level)) return;
        Entity killer = event.getSource().getEntity();
        boolean hiveKill = killer instanceof HivemindLinkedMob || killer instanceof AssimilatingMob;
        boolean decomposition = victim.getPersistentData().getInt(InfectionHandler.STAGE) == 4
                && IncubationEvents.supportsIncubation(victim) && !IncubationEvents.hasOwner(victim)
                && !IncubationEvents.isHostileHost(victim);
        if ((!hiveKill && !decomposition) || !ForgeEventFactory.getMobGriefingEvent(level, victim)) return;
        if (decomposition && !hiveKill && IncubationEvents.isNewAnimalHost(victim)
                && level.random.nextFloat() >= 0.4F) return;
        if (victim.getPersistentData().getBoolean("carnis:remains_created")) return;
        BlockPos base = victim.blockPosition();
        BlockPos placed = null;
        BlockState remains = ModBlocks.BIOMASS_REMAINS.get().defaultBlockState();
        for (int dy : new int[]{0, -1, 1}) {
            BlockPos pos = base.offset(0, dy, 0);
            if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos) || !level.hasChunkAt(pos.below())) continue;
            if (level.isEmptyBlock(pos) && remains.canSurvive(level, pos) && level.setBlockAndUpdate(pos, remains)) {
                placed = pos;
                break;
            }
        }
        if (placed == null) return;
        victim.getPersistentData().putBoolean("carnis:remains_created", true);
        if (!(victim instanceof Enemy)) {
            int count = 2 + level.random.nextInt(2);
            for (int i = 0; i < count; i++) {
                BiomassMaggotEntity maggot = ModEntities.BIOMASS_MAGGOT.get().create(level);
                if (maggot == null) continue;
                double angle = i * Math.PI * 2.0D / count;
                maggot.moveTo(placed.getX() + .5D + Math.cos(angle) * .6D, placed.getY(),
                        placed.getZ() + .5D + Math.sin(angle) * .6D, level.random.nextFloat() * 360F, 0);
                if (level.noCollision(maggot)) {
                    maggot.setPersistenceRequired();
                    level.addFreshEntity(maggot);
                }
            }
        }
    }
}
