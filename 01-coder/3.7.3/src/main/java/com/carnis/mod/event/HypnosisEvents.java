package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.entity.ai.GoalPriorityUtil;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.EnumSet;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HypnosisEvents {
    private static final String UNTIL = "carnis:trance_until", POOL = "carnis:trance_pool";
    private HypnosisEvents() { }
    public static void apply(Mob mob, ServerLevel level, BlockPos pool) {
        mob.getPersistentData().putLong(UNTIL, level.getGameTime() + 60);
        if (pool == null) mob.getPersistentData().remove(POOL); else mob.getPersistentData().putLong(POOL, pool.asLong());
    }
    @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || !(mob.level() instanceof ServerLevel level)) return;
        if (mob.tickCount % 10 != 0) return;
        boolean active = mob.getPersistentData().getLong(UNTIL) > level.getGameTime();
        TranceGoal found = null;
        for (var wrapped : mob.goalSelector.getAvailableGoals())
            if (wrapped.getGoal() instanceof TranceGoal g) { found = g; break; }
        if (active && found == null) mob.goalSelector.addGoal(GoalPriorityUtil.firstUnused(mob.goalSelector), new TranceGoal(mob));
        else if (!active && found != null) {
            mob.goalSelector.removeGoal(found);
            mob.getPersistentData().remove(UNTIL);
            mob.getPersistentData().remove(POOL);
        }
    }
    private static final class TranceGoal extends Goal {
        private final Mob mob;
        TranceGoal(Mob mob) { this.mob = mob; setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK)); }
        @Override public boolean canUse() { return mob.level() instanceof ServerLevel l && mob.getPersistentData().getLong(UNTIL) > l.getGameTime(); }
        @Override public boolean canContinueToUse() { return canUse(); }
        @Override public void start() { mob.getNavigation().stop(); }
        @Override public void stop() { mob.getNavigation().stop(); }
        @Override public void tick() {
            if (!(mob.level() instanceof ServerLevel level)) return;
            if (!mob.getPersistentData().contains(POOL)) { mob.getNavigation().stop(); return; }
            BlockPos pool = BlockPos.of(mob.getPersistentData().getLong(POOL));
            if (!level.hasChunkAt(pool) || !level.getBlockState(pool).is(ModBlocks.STOMACH_POOL.get())) {
                mob.getNavigation().stop(); return;
            }
            if (mob.tickCount % 10 == 0) mob.getNavigation().moveTo(pool.getX() + .5D, pool.getY(), pool.getZ() + .5D, 0.9D);
        }
        @Override public boolean requiresUpdateEveryTick() { return true; }
    }
}
