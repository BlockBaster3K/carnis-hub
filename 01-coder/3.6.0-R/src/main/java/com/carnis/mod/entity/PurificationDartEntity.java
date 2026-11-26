package com.carnis.mod.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.protocol.Packet;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.network.NetworkHooks;
import net.minecraftforge.registries.ForgeRegistries;

public final class PurificationDartEntity extends AbstractArrow {
    public PurificationDartEntity(EntityType<? extends PurificationDartEntity> type, Level level) {
        super(type, level);
        pickup = Pickup.DISALLOWED;
    }

    public PurificationDartEntity(Level level, LivingEntity owner) {
        super(ModEntities.PURIFICATION_DART.get(), owner, level);
        pickup = Pickup.DISALLOWED;
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        if (level().isClientSide) {
            return;
        }
        Entity hit = result.getEntity();
        if (hit instanceof ServerPlayer player) {
            PlayerInfectionApi.addInfection(player, -35.0F);
        } else if (hit instanceof LivingEntity living && isCarnis(living)) {
            living.hurt(ModDamageTypes.purificationDart(level(), this, getOwner()), 25.0F);
        }
        discard();
    }

    private static boolean isCarnis(LivingEntity target) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(target.getType());
        return target instanceof HivemindLinkedMob || id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
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
