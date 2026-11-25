package com.carnis.mod.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraftforge.common.ForgeSpawnEggItem;

import javax.annotation.Nullable;
import java.util.List;
import java.util.function.Supplier;

public final class MaggotSpawnEggItem extends ForgeSpawnEggItem {
    public MaggotSpawnEggItem(Supplier<? extends EntityType<? extends Mob>> entityType,
                              int backgroundColor, int highlightColor, Properties properties) {
        super(entityType, backgroundColor, highlightColor, properties);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.carnis.biomass_maggot.mechanics").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.carnis.biomass_maggot.lore").withStyle(ChatFormatting.DARK_RED));
    }
}
