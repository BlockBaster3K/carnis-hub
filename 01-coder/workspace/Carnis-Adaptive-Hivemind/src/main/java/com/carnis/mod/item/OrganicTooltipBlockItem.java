package com.carnis.mod.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;

import javax.annotation.Nullable;
import java.util.List;

public final class OrganicTooltipBlockItem extends BlockItem {
    private final String tooltipName;

    public OrganicTooltipBlockItem(Block block, Properties properties, String tooltipName) {
        super(block, properties);
        this.tooltipName = tooltipName;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.carnis." + tooltipName + ".mechanics").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.carnis." + tooltipName + ".lore").withStyle(ChatFormatting.DARK_RED));
    }
}
