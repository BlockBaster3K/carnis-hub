package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.item.ScytheItem;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import javax.annotation.Nullable;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CombatItemEvents {
    private CombatItemEvents() { }

    @SubscribeEvent
    public static void onScytheAttack(AttackEntityEvent event) {
        Player player = event.getEntity();
        if (player.level().isClientSide) return;
        playWorldSwing(player, player.blockPosition());
    }

    @SubscribeEvent
    public static void onScytheBlockSwing(PlayerInteractEvent.LeftClickBlock event) {
        Player player = event.getEntity();
        if (player.level().isClientSide) return;
        playWorldSwing(player, event.getPos());
    }

    @SubscribeEvent
    public static void onScytheAirSwing(PlayerInteractEvent.LeftClickEmpty event) {
        Player player = event.getEntity();
        if (!player.level().isClientSide) return;
        ScytheItem scythe = heldScythe(player);
        if (scythe == null) return;
        player.level().playLocalSound(player.getX(), player.getY(), player.getZ(),
                ModSounds.OSSIFIED_SCYTHE_SWING.get(), SoundSource.PLAYERS,
                scythe.getSoundVolume(), scythe.getSoundPitch(), false);
    }

    private static void playWorldSwing(Player player, net.minecraft.core.BlockPos soundPos) {
        ScytheItem scythe = heldScythe(player);
        if (scythe == null) return;
        player.level().playSound(null, soundPos, ModSounds.OSSIFIED_SCYTHE_SWING.get(),
                SoundSource.PLAYERS, scythe.getSoundVolume(), scythe.getSoundPitch());
    }

    @Nullable
    private static ScytheItem heldScythe(Player player) {
        return player.getMainHandItem().getItem() instanceof ScytheItem scythe ? scythe : null;
    }

    @SubscribeEvent
    public static void onShieldBlock(LivingAttackEvent event) {
        LivingEntity entity = event.getEntity();
        if (!(entity instanceof net.minecraft.server.level.ServerPlayer player) || !player.isBlocking()
                || !player.getUseItem().is(ModItems.SINEW_SHIELD.get())
                || !player.isDamageSourceBlocked(event.getSource())) return;
        player.level().playSound(null, player.blockPosition(), ModSounds.SINEW_SHIELD_BLOCK.get(),
                SoundSource.PLAYERS, 1.0F, 1.0F);
    }
}
