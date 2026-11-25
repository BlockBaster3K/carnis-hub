package com.carnis.mod.ecology;
import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class FeedingEvents {
    private FeedingEvents() { }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onDeath(LivingDeathEvent event) {
        if (event.isCanceled() || !(event.getEntity().level() instanceof ServerLevel level)
                || !(event.getSource().getEntity() instanceof Mob hunter) || !(hunter instanceof HivemindLinkedMob)
                || !(hunter instanceof com.carnis.mod.entity.InfectedZombieEntity || hunter instanceof com.carnis.mod.entity.InfectedSkeletonEntity
                    || hunter instanceof com.carnis.mod.entity.InfectedCreeperEntity || hunter instanceof com.carnis.mod.entity.InfectedSpiderEntity)
                || !hunter.isAlive() || !CarnisHuntPreyGoal.isPrey(event.getEntity())) return;
        // One active feeding at a time; don't overwrite the pending award.
        var tag = hunter.getPersistentData();
        if (tag.contains(CarnisFeedingGoal.DEADLINE)) return;
        tag.putInt(CarnisFeedingGoal.DEADLINE, 0);
        tag.putInt("carnis:feeding_travel", 0);
        tag.putDouble(CarnisFeedingGoal.X, event.getEntity().getX());
        tag.putDouble(CarnisFeedingGoal.Y, event.getEntity().getY());
        tag.putDouble(CarnisFeedingGoal.Z, event.getEntity().getZ());
    }
}
