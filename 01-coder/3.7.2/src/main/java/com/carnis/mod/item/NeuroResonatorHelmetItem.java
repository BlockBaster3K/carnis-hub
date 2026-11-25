package com.carnis.mod.item;

import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;

import java.util.Objects;

public final class NeuroResonatorHelmetItem extends NeuroResonatorArmorItem {
    public NeuroResonatorHelmetItem(Properties properties) {
        super(Type.HELMET, properties);
    }

    public static boolean isEquipped(LivingEntity entity) {
        Objects.requireNonNull(entity, "entity");

        return entity.getItemBySlot(EquipmentSlot.HEAD).getItem()
                instanceof NeuroResonatorHelmetItem;
    }
}
