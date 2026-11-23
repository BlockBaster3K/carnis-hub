package com.carnis.mod.event;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.animal.horse.AbstractHorse;

import java.util.Set;

/** Явный список допустимых ванильных носителей. */
public final class IncubationEvents {
    private static final Set<String> ANIMAL_HOSTS = Set.of(
            "cow", "sheep", "pig", "chicken", "goat", "llama", "trader_llama", "horse",
            "donkey", "mule", "skeleton_horse", "zombie_horse", "fox", "wolf", "cat",
            "ocelot", "parrot", "panda", "polar_bear", "turtle", "frog", "camel", "sniffer",
            "strider", "mooshroom", "rabbit", "bee", "hoglin", "tadpole", "cod", "salmon",
            "pufferfish", "tropical_fish", "squid", "glow_squid", "dolphin", "axolotl"
    );
    private static final Set<String> ORIGINAL_PEACEFUL_HOSTS = Set.of("cow", "sheep", "pig", "chicken", "villager");

    private IncubationEvents() { }

    public static boolean isHostileHost(LivingEntity entity) {
        EntityType<?> type = entity.getType();
        return type == EntityType.ZOMBIE || type == EntityType.SKELETON
                || type == EntityType.CREEPER || type == EntityType.SPIDER || type == EntityType.CAVE_SPIDER;
    }

    /** Тип носителя без проверки текущей стадии: используется при продолжающейся инкубации. */
    public static boolean supportsIncubation(LivingEntity entity) {
        ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType());
        return isHostileHost(entity) || id != null && id.getNamespace().equals("minecraft")
                && (ANIMAL_HOSTS.contains(id.getPath()) || id.getPath().equals("villager"));
    }

    public static boolean hasOwner(LivingEntity entity) {
        return entity instanceof TamableAnimal tame && tame.getOwnerUUID() != null
                || entity instanceof AbstractHorse horse && horse.getOwnerUUID() != null;
    }

    /** Проверка исключительно для начала заражения. */
    public static boolean isEligible(LivingEntity entity) {
        return supportsIncubation(entity) && !hasOwner(entity) && !InfectionHandler.isInfected(entity);
    }

    /** Новые не превращающиеся носители; старые мирные виды сохраняют прежнюю механику. */
    public static boolean isNewAnimalHost(LivingEntity entity) {
        ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType());
        return id != null && id.getNamespace().equals("minecraft")
                && ANIMAL_HOSTS.contains(id.getPath()) && !ORIGINAL_PEACEFUL_HOSTS.contains(id.getPath());
    }
}
