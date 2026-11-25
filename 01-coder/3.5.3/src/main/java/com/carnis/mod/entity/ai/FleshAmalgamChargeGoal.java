package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * RANGED adaptation countermeasure: when its target keeps distance, the
 * Amalgam abandons ordinary pathing for one bounded ballistic charge.
 */
public final class FleshAmalgamChargeGoal extends Goal {
    private static final double TRIGGER_DISTANCE_SQUARED =
            FleshAmalgamEntity.CHARGE_TRIGGER_DISTANCE
                    * FleshAmalgamEntity.CHARGE_TRIGGER_DISTANCE;
    private static final double MIN_HORIZONTAL_VECTOR_SQUARED = 1.0E-6D;

    private static final double BASE_HORIZONTAL_SPEED = 1.15D;
    private static final double SPEED_PER_ADAPTATION_LEVEL = 0.008D;
    private static final double MAX_HORIZONTAL_SPEED = 1.55D;
    private static final double VERTICAL_SPEED = 0.52D;

    private static final int BASE_COOLDOWN_TICKS = 90;
    private static final int MIN_COOLDOWN_TICKS = 35;
    private static final int MAX_AIRBORNE_TICKS = 20;

    private final FleshAmalgamEntity amalgam;

    private LivingEntity target;
    private long nextAllowedChargeTick;
    private int airborneTicks;

    public FleshAmalgamChargeGoal(FleshAmalgamEntity amalgam) {
        this.amalgam = amalgam;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (
                amalgam.level().getGameTime() < nextAllowedChargeTick
                        || !amalgam.onGround()
                        || amalgam.getRangedAdaptationLevel() <= 0L
        ) {
            return false;
        }

        LivingEntity currentTarget = amalgam.getTarget();

        if (
                !HiveSwarmCoordinator.validTarget(amalgam, currentTarget)
        ) {
            return false;
        }

        double offsetX = currentTarget.getX() - amalgam.getX();
        double offsetZ = currentTarget.getZ() - amalgam.getZ();
        double horizontalDistanceSquared = offsetX * offsetX
                + offsetZ * offsetZ;

        if (
                amalgam.distanceToSqr(currentTarget)
                        <= TRIGGER_DISTANCE_SQUARED
                        || horizontalDistanceSquared
                        < MIN_HORIZONTAL_VECTOR_SQUARED
        ) {
            return false;
        }

        target = currentTarget;
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        return HiveSwarmCoordinator.validTarget(amalgam, target)
                && airborneTicks < MAX_AIRBORNE_TICKS
                && (!amalgam.onGround() || airborneTicks == 0);
    }

    @Override
    public void start() {
        if (target == null) {
            return;
        }

        Vec3 horizontalDirection = new Vec3(
                target.getX() - amalgam.getX(),
                0.0D,
                target.getZ() - amalgam.getZ()
        );

        if (
                horizontalDirection.lengthSqr()
                        < MIN_HORIZONTAL_VECTOR_SQUARED
        ) {
            target = null;
            return;
        }

        long rangedLevel = amalgam.getRangedAdaptationLevel();
        double horizontalSpeed = Math.min(
                MAX_HORIZONTAL_SPEED,
                BASE_HORIZONTAL_SPEED
                        + rangedLevel * SPEED_PER_ADAPTATION_LEVEL
        );
        int cooldownReduction = (int) Math.min(
                BASE_COOLDOWN_TICKS - MIN_COOLDOWN_TICKS,
                rangedLevel
        );

        horizontalDirection = horizontalDirection.normalize();
        amalgam.getNavigation().stop();
        amalgam.getLookControl().setLookAt(target, 30.0F, 30.0F);
        amalgam.setDeltaMovement(
                horizontalDirection.x * horizontalSpeed,
                Math.max(
                        VERTICAL_SPEED,
                        amalgam.getDeltaMovement().y
                ),
                horizontalDirection.z * horizontalSpeed
        );
        amalgam.setSprinting(true);

        nextAllowedChargeTick = amalgam.level().getGameTime()
                + BASE_COOLDOWN_TICKS
                - cooldownReduction;
        airborneTicks = 0;
    }

    @Override
    public void tick() {
        airborneTicks++;

        if (HiveSwarmCoordinator.validTarget(amalgam, target)) {
            amalgam.getLookControl().setLookAt(target, 30.0F, 30.0F);
        }
    }

    @Override
    public void stop() {
        amalgam.setSprinting(false);
        target = null;
        airborneTicks = 0;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }
}
