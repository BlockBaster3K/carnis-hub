package com.carnis.mod.entity;

import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.init.ModItems;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraftforge.network.NetworkHooks;

public final class PustuleGrenadeEntity extends ThrowableItemProjectile {
    public PustuleGrenadeEntity(EntityType<? extends PustuleGrenadeEntity> type, Level level) {
        super(type, level);
    }

    public PustuleGrenadeEntity(Level level, LivingEntity owner) {
        super(ModEntities.PUSTULE_GRENADE.get(), owner, level);
    }

    @Override
    protected Item getDefaultItem() {
        return ModItems.PUSTULE_GRENADE.get();
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        if (!level().isClientSide) {
            if (result.getEntity() instanceof LivingEntity target) {
                target.addEffect(new MobEffectInstance(MobEffects.POISON, 60, 3), getOwner());
            }
            burst();
        }
        discard();
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        super.onHitBlock(result);
        if (!level().isClientSide) burst();
        discard();
    }

    private void burst() {
        level().playSound(null, getX(), getY(), getZ(), ModSounds.PUSTULE_GRENADE_IMPACT.get(),
                SoundSource.PLAYERS, 1.0F, 1.0F);
        if (level() instanceof ServerLevel server) {
            server.sendParticles(ModParticles.BIOMASS_SPARK.get(), getX(), getY(), getZ(),
                    20, 0.4D, 0.35D, 0.4D, 0.08D);
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
