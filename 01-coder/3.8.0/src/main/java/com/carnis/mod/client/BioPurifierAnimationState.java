package com.carnis.mod.client;
import com.carnis.mod.item.BioPurifierItem;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animation.AnimationState;

/** Render-side state only; item renderers do not receive an owning entity in GeckoLib 4. */
public final class BioPurifierAnimationState {
    private BioPurifierAnimationState() { }
    public static boolean isFiring(AnimationState<BioPurifierItem> state) {
        ItemDisplayContext context = state.getData(DataTickets.ITEM_RENDER_PERSPECTIVE);
        if (context != ItemDisplayContext.FIRST_PERSON_LEFT_HAND && context != ItemDisplayContext.FIRST_PERSON_RIGHT_HAND
                && context != ItemDisplayContext.THIRD_PERSON_LEFT_HAND && context != ItemDisplayContext.THIRD_PERSON_RIGHT_HAND) return false;
        ItemStack stack = state.getData(DataTickets.ITEMSTACK);
        var level = Minecraft.getInstance().level;
        if (stack == null || level == null) return false;
        for (Player player : level.players()) {
            if (player.isUsingItem() && player.getUseItem() == stack) return true;
        }
        return false;
    }
}
