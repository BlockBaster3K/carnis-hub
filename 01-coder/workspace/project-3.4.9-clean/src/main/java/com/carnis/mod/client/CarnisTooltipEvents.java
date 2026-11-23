package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@OnlyIn(Dist.CLIENT)
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisTooltipEvents {
    private CarnisTooltipEvents() {
    }

    @SubscribeEvent
    public static void onTooltip(ItemTooltipEvent event) {
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(event.getItemStack().getItem());
        if (id == null || !CarnisMod.MOD_ID.equals(id.getNamespace())) {
            return;
        }
        if (Screen.hasShiftDown()) {
            event.getToolTip().add(Component.translatable("tooltip.carnis." + id.getPath())
                    .withStyle(ChatFormatting.DARK_RED));
        } else {
            event.getToolTip().add(Component.translatable("tooltip.carnis.hold_shift")
                    .withStyle(ChatFormatting.GRAY));
        }
    }
}
