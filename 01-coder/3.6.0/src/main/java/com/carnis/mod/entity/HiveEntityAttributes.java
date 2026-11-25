package com.carnis.mod.entity;

import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;

/**
 * Базовые атрибуты для сущностей улья.
 * Каждая конкретная сущность создаёт СВОЙ createAttributes(),
 * НЕ вызывая этот метод напрямую для registration.
 */
public final class HiveEntityAttributes {
    private HiveEntityAttributes() { }

    public static AttributeSupplier.Builder create() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 20.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.23D)
                .add(Attributes.ATTACK_DAMAGE, 3.0D)
                .add(Attributes.FOLLOW_RANGE, 32.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.05D);
    }
}
