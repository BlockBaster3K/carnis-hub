package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.HivemindLinkedMob;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.registries.ForgeRegistries;

/** Vanilla mobs are prey; players and allied Carnis are handled by other goals. */
public final class CarnisHuntPreyGoal extends NearestAttackableTargetGoal<LivingEntity> {
    public CarnisHuntPreyGoal(Mob hunter) {
        super(hunter, LivingEntity.class, 20, true, false,
                target -> isPrey(target) && hunter.distanceToSqr(target) <= 256.0D
                        && hunter.hasLineOfSight(target) && HiveSwarmCoordinator.validTarget(hunter, target));
    }
    public static boolean isPrey(LivingEntity target) {
        if (!(target instanceof Mob) || target instanceof HivemindLinkedMob || target instanceof Player) return false;
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(target.getType());
        return id != null && "minecraft".equals(id.getNamespace());
    }
}
