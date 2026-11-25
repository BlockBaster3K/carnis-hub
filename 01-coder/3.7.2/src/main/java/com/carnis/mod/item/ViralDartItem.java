package com.carnis.mod.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import javax.annotation.Nullable;
import java.util.List;

public final class ViralDartItem extends Item {
    public ViralDartItem(Properties properties) { super(properties); }
    @Override public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.carnis.viral_dart.mechanics").withStyle(ChatFormatting.LIGHT_PURPLE));
        tooltip.add(Component.translatable("tooltip.carnis.viral_dart.protocol").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.carnis.dart.use").withStyle(ChatFormatting.DARK_GRAY));
    }
}
