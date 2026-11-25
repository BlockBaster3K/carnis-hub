package com.carnis.mod.entity.ai;

import java.util.HashSet;
import java.util.Set;
import net.minecraft.world.entity.ai.goal.GoalSelector;
import net.minecraft.world.entity.ai.goal.WrappedGoal;

/** Assigns the first unused selector priority when goals are registered dynamically. */
public final class GoalPriorityUtil {
    private GoalPriorityUtil() { }

    public static int firstUnused(GoalSelector selector) {
        Set<Integer> used = new HashSet<>();
        for (WrappedGoal goal : selector.getAvailableGoals()) used.add(goal.getPriority());
        int priority = 0;
        while (used.contains(priority)) priority++;
        return priority;
    }
}
