package com.carnis.mod.item;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.event.HallucinationEvents;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;

public final class PurificationSerumItem extends Item {
    public static final float INFECTION_REDUCTION = 35.0F;
    private static final int DRINK_DURATION_TICKS = 32;

    public PurificationSerumItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(
            Level level,
            Player player,
            InteractionHand hand
    ) {
        ItemStack stack = player.getItemInHand(hand);
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public ItemStack finishUsingItem(
            ItemStack stack,
            Level level,
            LivingEntity user
    ) {
        if (!level.isClientSide() && user instanceof ServerPlayer player) {
            float infectionLevel = PlayerInfectionApi.getInfectionLevel(player);
            PlayerInfectionApi.setInfectionLevel(
                    player,
                    Math.max(0.0F, infectionLevel - INFECTION_REDUCTION)
            );
            HallucinationEvents.resetHallucinationTimer(player);
        }

        if (user instanceof Player player
                && player.getAbilities().instabuild) {
            return stack;
        }

        stack.shrink(1);
        ItemStack emptyBottle = new ItemStack(Items.GLASS_BOTTLE);

        if (stack.isEmpty()) {
            return emptyBottle;
        }

        if (user instanceof Player player
                && !player.getInventory().add(emptyBottle)) {
            player.drop(emptyBottle, false);
        }

        return stack;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.DRINK;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return DRINK_DURATION_TICKS;
    }

    @Override
    public void appendHoverText(ItemStack stack, @javax.annotation.Nullable Level level,
                                java.util.List<net.minecraft.network.chat.Component> tooltip,
                                net.minecraft.world.item.TooltipFlag flag) {
        tooltip.add(net.minecraft.network.chat.Component.translatable("tooltip.carnis.purification_serum.mechanics")
                .withStyle(net.minecraft.ChatFormatting.AQUA));
        tooltip.add(net.minecraft.network.chat.Component.translatable("tooltip.carnis.purification_serum.use")
                .withStyle(net.minecraft.ChatFormatting.GRAY));
    }

    @Override
    public SoundEvent getDrinkingSound() {
        return SoundEvents.GENERIC_DRINK;
    }
}
