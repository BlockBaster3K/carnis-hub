package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraftforge.event.entity.ProjectileImpactEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class FleshAmalgamCombatEvents {
    private FleshAmalgamCombatEvents() {
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void onProjectileImpact(ProjectileImpactEvent event) {
        Projectile projectile = event.getProjectile();

        if (
                event.isCanceled()
                        || event.getImpactResult()
                        != ProjectileImpactEvent.ImpactResult.DEFAULT
                        || !(projectile.level() instanceof ServerLevel)
                        || !(event.getRayTraceResult()
                        instanceof EntityHitResult entityHitResult)
                        || !(entityHitResult.getEntity()
                        instanceof FleshAmalgamEntity amalgam)
                        || !amalgam.tryDeflectProjectile(projectile)
        ) {
            return;
        }

        // The arrow's velocity has already been redirected at the impact point.
        // Skip this collision so it does not immediately damage the Amalgam.
        event.setImpactResult(
                ProjectileImpactEvent.ImpactResult.SKIP_ENTITY
        );
    }
}
