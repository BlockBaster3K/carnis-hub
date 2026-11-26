package com.carnis.mod.item;

import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;

public final class NeuroWeave {
    public static final String TAG = "carnis:neuro_woven";
    private static final EquipmentSlot[] ARMOR_SLOTS = {
            EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET
    };

    private NeuroWeave() { }

    public static boolean isWoven(ItemStack stack) {
        return stack.getItem() instanceof ArmorItem && stack.hasTag() && stack.getTag().getBoolean(TAG);
    }

    public static int protectedPieces(LivingEntity entity) {
        int count = 0;
        for (EquipmentSlot slot : ARMOR_SLOTS) {
            ItemStack stack = entity.getItemBySlot(slot);
            if (isWoven(stack) || stack.getItem() instanceof com.carnis.mod.item.armor.NeuroArmorItem) count++;
        }
        return count;
    }

    public static float infectionMultiplier(LivingEntity entity) {
        return Math.max(0.0F, 1.0F - 0.25F * protectedPieces(entity));
    }

    public static boolean hasSludgeImmuneBoots(LivingEntity entity) {
        ItemStack boots = entity.getItemBySlot(EquipmentSlot.FEET);
        return boots.getItem() instanceof com.carnis.mod.item.armor.NeuroArmorItem armor
                && armor.getType() == ArmorItem.Type.BOOTS;
    }
}
