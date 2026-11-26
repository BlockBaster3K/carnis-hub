package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;

/** Shared server-side swarm contract for entities that are also vanilla mobs. */
public interface HivemindLinkedMob {
    default void alertTarget(LivingEntity target) {
        if (this instanceof Mob mob) HiveSwarmCoordinator.alertTarget(mob, target);
    }
    default void triggerFrenzy(int durationTicks) {
        if (this instanceof Mob mob) HiveSwarmCoordinator.triggerFrenzy(mob, durationTicks);
    }
    default boolean isFrenzied() {
        return this instanceof Mob mob && HiveSwarmCoordinator.isFrenzied(mob);
    }
}
