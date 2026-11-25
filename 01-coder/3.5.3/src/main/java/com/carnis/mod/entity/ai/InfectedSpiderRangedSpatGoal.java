package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.FleshSpatProjectileEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import java.util.EnumSet;

public final class InfectedSpiderRangedSpatGoal extends Goal {
    private final InfectedSpiderEntity spider;
    private long nextShot;

    public InfectedSpiderRangedSpatGoal(InfectedSpiderEntity spider) {
        this.spider = spider;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override public boolean canUse() {
        LivingEntity target = spider.getTarget();
        if (!HiveSwarmCoordinator.validTarget(spider, target) || !spider.hasLineOfSight(target)) return false;
        double distance = spider.distanceToSqr(target);
        return distance >= 16.0D && distance <= 144.0D;
    }

    @Override public boolean canContinueToUse() { return canUse(); }
    @Override public boolean requiresUpdateEveryTick() { return true; }

    @Override public void tick() {
        LivingEntity target = spider.getTarget();
        if (!HiveSwarmCoordinator.validTarget(spider, target)) return;
        spider.getNavigation().stop();
        spider.getLookControl().setLookAt(target, 30.0F, 30.0F);
        long now = spider.level().getGameTime();
        if (now < nextShot) return;
        FleshSpatProjectileEntity spat = new FleshSpatProjectileEntity(spider.level(), spider);
        double x = target.getX() - spat.getX();
        double z = target.getZ() - spat.getZ();
        double y = target.getY(0.45D) - spat.getY() + Math.sqrt(x * x + z * z) * 0.05D;
        spat.shoot(x, y, z, 1.2F, 1.0F);
        if (spider.level().addFreshEntity(spat)) nextShot = now + 60L;
    }
}
