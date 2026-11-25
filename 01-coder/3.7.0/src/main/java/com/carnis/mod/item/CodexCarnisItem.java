package com.carnis.mod.item;

import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.Level;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;

/** Keeps the original carnis:research_journal registry identity. */
public final class CodexCarnisItem extends Item {
    public CodexCarnisItem(Properties properties) {
        super(properties.stacksTo(1).rarity(Rarity.UNCOMMON));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide) {
            DistExecutor.safeRunWhenOn(Dist.CLIENT,
                    () -> com.carnis.mod.client.gui.CodexCarnisScreen::open);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }
}
