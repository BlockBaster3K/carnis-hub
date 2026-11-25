package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HiveSentinelEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;
import java.util.Comparator;
import java.util.EnumSet;

/** Follows a loaded leader without replacing any active combat target. */
public final class HiveEscortLeaderGoal extends Goal {
    private static final double SEARCH_RADIUS = 24.0D;
    private static final double INNER = 6.0D;
    private static final double OUTER = 14.0D;
    private final Mob mob;
    private Mob leader;
    private int nextSearch;
    private int repath;
    public HiveEscortLeaderGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }
    private boolean available() {
        return mob.isAlive() && mob.getTarget() == null
                && !mob.getPersistentData().contains(CarnisFeedingGoal.DEADLINE)
                && HiveSwarmCoordinator.defensePosition(mob) == null;
    }
    private static boolean isLeader(Mob candidate) {
        return candidate instanceof HiveSentinelEntity || candidate instanceof CerebralNexusEntity
                || candidate instanceof FleshAmalgamEntity;
    }
    @Override public boolean canUse() {
        if (!(mob.level() instanceof ServerLevel level) || !available() || mob.tickCount < nextSearch) return false;
        nextSearch = mob.tickCount + 40;
        leader = level.getEntitiesOfClass(Mob.class, mob.getBoundingBox().inflate(SEARCH_RADIUS),
                candidate -> candidate != mob && candidate.isAlive() && isLeader(candidate)
                        && mob.distanceToSqr(candidate) <= SEARCH_RADIUS * SEARCH_RADIUS)
                .stream().min(Comparator.comparingDouble(mob::distanceToSqr)).orElse(null);
        return leader != null;
    }
    @Override public boolean canContinueToUse() {
        return available() && leader != null && leader.isAlive() && !leader.isRemoved()
                && leader.level() == mob.level() && mob.level().isLoaded(leader.blockPosition())
                && mob.distanceToSqr(leader) <= SEARCH_RADIUS * SEARCH_RADIUS;
    }
    @Override public void start() { repath = 0; }
    @Override public void stop() { mob.getNavigation().stop(); leader = null; }
    @Override public void tick() {
        if (!canContinueToUse()) {
            stop();
            return;
        }
        if (--repath > 0) return;
        repath = 20;
        double distance = mob.distanceToSqr(leader);
        mob.getLookControl().setLookAt(leader, 30.0F, 30.0F);
        if (distance > OUTER * OUTER) {
            mob.getNavigation().moveTo(leader, 1.0D);
        } else if (distance < INNER * INNER) {
            Vec3 away = mob.position().subtract(leader.position()).multiply(1, 0, 1);
            if (away.lengthSqr() < 0.01D) away = new Vec3(1, 0, 0);
            Vec3 destination = leader.position().add(away.normalize().scale(9.0D));
            mob.getNavigation().moveTo(destination.x, destination.y, destination.z, 0.9D);
        } else {
            mob.getNavigation().stop();
        }
    }
}
