package com.carnis.mod.item;

import com.carnis.mod.init.ModItems;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.ArmorMaterials;
import net.minecraft.world.item.crafting.Ingredient;

public enum NeuroArmorMaterial implements ArmorMaterial {
    INSTANCE;

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> 330;
            case CHESTPLATE -> 480;
            case LEGGINGS -> 450;
            case BOOTS -> 390;
        };
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> 3;
            case CHESTPLATE -> 7;
            case LEGGINGS -> 5;
            case BOOTS -> 2;
        };
    }

    @Override public int getEnchantmentValue() { return 15; }
    @Override public SoundEvent getEquipSound() { return SoundEvents.ARMOR_EQUIP_IRON; }
    @Override public Ingredient getRepairIngredient() { return Ingredient.of(ModItems.LIVING_FLESH.get()); }
    @Override public String getName() { return "carnis:neuro_resonator"; }
    @Override public float getToughness() { return 1.5F; }
    @Override public float getKnockbackResistance() { return 0.025F; }
}
