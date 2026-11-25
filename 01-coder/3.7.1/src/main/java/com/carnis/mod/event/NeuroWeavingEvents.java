package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.item.NeuroWeave;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.AnvilUpdateEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NeuroWeavingEvents {
    private NeuroWeavingEvents() {
    }

    @SubscribeEvent
    public static void onAnvilUpdate(AnvilUpdateEvent event) {
        ItemStack left = event.getLeft();
        if (!(left.getItem() instanceof ArmorItem) || !event.getRight().is(ModItems.NEURAL_BINDING_MATRIX.get())
                || NeuroWeave.isWoven(left)) {
            return;
        }
        ItemStack output = left.copy();
        output.getOrCreateTag().putBoolean(NeuroWeave.TAG, true);
        // Add a no-effect level-zero enchant only to otherwise unenchanted armor.
        // This preserves existing enchantments but HideFlags also hides any later enchantments.
        if (!output.isEnchanted()) {
            output.enchant(net.minecraft.world.item.enchantment.Enchantments.UNBREAKING, 0);
            output.getOrCreateTag().putInt("HideFlags", output.getOrCreateTag().getInt("HideFlags") | 1);
        }
        output.setHoverName(Component.literal("[Neuro-Woven] ").withStyle(ChatFormatting.RED)
                .append(left.getHoverName().copy().withStyle(ChatFormatting.RESET)));
        var display = output.getOrCreateTagElement("display");
        ListTag lore = display.contains("Lore", Tag.TAG_LIST)
                ? display.getList("Lore", Tag.TAG_STRING).copy() : new ListTag();
        Component line = Component.literal("Trait: ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal("Psychic & Biological Shielding").withStyle(ChatFormatting.RED));
        lore.add(StringTag.valueOf(Component.Serializer.toJson(line)));
        display.put("Lore", lore);
        event.setOutput(output);
        event.setCost(5);
        event.setMaterialCost(1);
    }
}
