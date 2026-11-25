package com.carnis.mod.entity.ai;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import java.util.EnumSet;

/** A defense order is pushed by an attack event, not discovered by scanning blocks. */
public final class HiveDefendHeartGoal extends Goal {
    private final Mob mob;
    private BlockPos destination;
    private int repath;
    public HiveDefendHeartGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }
    @Override public boolean canUse() {
        if (!(mob.level() instanceof ServerLevel level) || !mob.isAlive()) return false;
        destination = HiveSwarmCoordinator.defensePosition(mob);
        if (destination == null) { HiveSwarmCoordinator.clearDefense(mob); return false; }
        // Once near the threatened location, hand control back to normal combat.
        return level.hasChunkAt(destination) && farFromDefense() && !enemyClose();
    }
    @Override public boolean canContinueToUse() {
        BlockPos current = HiveSwarmCoordinator.defensePosition(mob);
        return mob.isAlive() && mob.level() instanceof ServerLevel level && destination != null
                && current != null && current.equals(destination) && level.hasChunkAt(destination)
                && farFromDefense() && !enemyClose();
    }
    private boolean farFromDefense() {
        return destination != null && mob.distanceToSqr(destination.getX() + .5D, destination.getY() + .5D, destination.getZ() + .5D) > 36.0D;
    }
    private boolean enemyClose() {
        var target = mob.getTarget();
        return target != null && target.isAlive() && target.level() == mob.level()
                && mob.distanceToSqr(target) <= 36.0D;
    }
    @Override public void start() { repath = 0; }
    @Override public void stop() { mob.getNavigation().stop(); destination = null; }
    @Override public void tick() {
        if (destination == null || !(mob.level() instanceof ServerLevel level)
                || !mob.isAlive() || !level.hasChunkAt(destination)) {
            stop();
            return;
        }
        BlockPos current = HiveSwarmCoordinator.defensePosition(mob);
        if (current == null || !current.equals(destination)) {
            stop();
            return;
        }
        if (--repath <= 0) {
            repath = 20;
            // A removed heart is still a useful rally point. No chunk is loaded by this goal.
            if (level.hasChunkAt(destination))
                mob.getNavigation().moveTo(destination.getX() + .5D, destination.getY(), destination.getZ() + .5D, 1.15D);
        }
        var target = mob.getTarget();
        if (target != null && target.isAlive() && target.level() == level)
            mob.getLookControl().setLookAt(target, 30.0F, 30.0F);
    }
}
