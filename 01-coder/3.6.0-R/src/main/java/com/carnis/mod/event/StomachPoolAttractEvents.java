package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.entity.ai.StomachPoolAttractGoal;
import com.carnis.mod.entity.ai.GoalPriorityUtil;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class StomachPoolAttractEvents {
    private StomachPoolAttractEvents() { }

    public static boolean isAllowedType(EntityType<?> type) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(type);
        if (id == null) return false;

        // Third-party mobs: allow land/passive categories, but not foreign MONSTER bosses.
        if (!id.getNamespace().equals("minecraft")) {
            return type.getCategory() == MobCategory.CREATURE
                    || type.getCategory() == MobCategory.AMBIENT;
        }

        // Vanilla MISC-category hosts that should still be attracted.
        if (type == EntityType.VILLAGER
                || type == EntityType.WANDERING_TRADER
                || type == EntityType.IRON_GOLEM
                || type == EntityType.SNOW_GOLEM
                || type == EntityType.TRADER_LLAMA) {
            return true;
        }

        MobCategory category = type.getCategory();
        if (category == MobCategory.CREATURE || category == MobCategory.AMBIENT) return true;
        if (category == MobCategory.MONSTER) {
            return type != EntityType.ENDER_DRAGON
                    && type != EntityType.WITHER
                    && type != EntityType.ELDER_GUARDIAN
                    && type != EntityType.WARDEN;
        }
        return false;
    }

    @SubscribeEvent
    public static void onEntityJoin(EntityJoinLevelEvent event) {
        if (!(event.getLevel() instanceof ServerLevel) || !(event.getEntity() instanceof Mob mob)
                || !isAllowedType(mob.getType()) || NeuralMossBlock.isHive(mob)) return;

        for (var wrapped : mob.goalSelector.getAvailableGoals()) {
            if (wrapped.getGoal() instanceof StomachPoolAttractGoal) return;
        }

        StomachPoolAttractGoal attraction = new StomachPoolAttractGoal(mob);
        mob.goalSelector.addGoal(GoalPriorityUtil.firstUnused(mob.goalSelector), attraction.createHoldGoal());
        mob.goalSelector.addGoal(GoalPriorityUtil.firstUnused(mob.goalSelector), attraction);
    }
}
