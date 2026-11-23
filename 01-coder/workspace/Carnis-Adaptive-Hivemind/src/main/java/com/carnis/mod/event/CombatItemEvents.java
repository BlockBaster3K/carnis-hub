package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CombatItemEvents {
    private CombatItemEvents() { }

    @SubscribeEvent
    public static void onScytheAttack(AttackEntityEvent event) {
        Player player = event.getEntity();
        if (player.getMainHandItem().is(ModItems.OSSIFIED_SCYTHE.get())) {
            player.level().playSound(null, player.blockPosition(), ModSounds.OSSIFIED_SCYTHE_SWING.get(),
                    SoundSource.PLAYERS, 1.0F, 1.0F);
        }
    }

    @SubscribeEvent
    public static void onScytheBlockSwing(PlayerInteractEvent.LeftClickBlock event) {
        Player player = event.getEntity();
        if (player.getMainHandItem().is(ModItems.OSSIFIED_SCYTHE.get())) {
            player.level().playSound(null, event.getPos(), ModSounds.OSSIFIED_SCYTHE_SWING.get(),
                    SoundSource.PLAYERS, 1.0F, 1.0F);
        }
    }

    @SubscribeEvent
    public static void onShieldBlock(LivingAttackEvent event) {
        LivingEntity entity = event.getEntity();
        if (!(entity instanceof ServerPlayer player) || !player.isBlocking()
                || !player.getUseItem().is(ModItems.SINEW_SHIELD.get())
                || !player.isDamageSourceBlocked(event.getSource())) return;
        player.level().playSound(null, player.blockPosition(), ModSounds.SINEW_SHIELD_BLOCK.get(),
                SoundSource.PLAYERS, 1.0F, 1.0F);
    }
}
