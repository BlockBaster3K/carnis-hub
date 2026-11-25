package com.carnis.mod.entity;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.protocol.Packet;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.network.NetworkHooks;

public final class ViralDartEntity extends AbstractArrow {
    public ViralDartEntity(EntityType<? extends ViralDartEntity> type, Level level) {
        super(type, level);
        pickup = Pickup.DISALLOWED;
    }

    public ViralDartEntity(Level level, LivingEntity owner) {
        super(ModEntities.VIRAL_DART.get(), owner, level);
        pickup = Pickup.DISALLOWED;
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        if (level().isClientSide) {
            return;
        }
        Entity hit = result.getEntity();
        if (hit instanceof ServerPlayer player) {
            if (!(getOwner() instanceof Player attacker) || attacker.canHarmPlayer(player)) {
                PlayerInfectionApi.addExposure(player, 30.0F);
            }
        } else if (hit instanceof LivingEntity living) {
            living.addEffect(new MobEffectInstance(MobEffects.POISON, 200, 1));
            living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 200, 0));
        }
        discard();
    }

    @Override
    protected SoundEvent getDefaultHitGroundSoundEvent() {
        return ModSounds.DART_HIT.get();
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        setSoundEvent(ModSounds.DART_HIT.get());
        super.onHitBlock(result);
    }

    @Override
    protected ItemStack getPickupItem() {
        return ItemStack.EMPTY;
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
