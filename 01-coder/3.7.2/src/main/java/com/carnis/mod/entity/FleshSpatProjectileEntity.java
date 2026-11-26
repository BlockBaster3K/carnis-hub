package com.carnis.mod.entity;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModItems;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.network.NetworkHooks;

public final class FleshSpatProjectileEntity extends ThrowableItemProjectile {
    public FleshSpatProjectileEntity(EntityType<? extends FleshSpatProjectileEntity> type, Level level) {
        super(type, level);
    }

    public FleshSpatProjectileEntity(Level level, LivingEntity owner) {
        super(ModEntities.FLESH_SPAT.get(), owner, level);
    }

    @Override protected Item getDefaultItem() { return ModItems.FLESH_SPAT.get(); }

    @Override public void tick() {
        super.tick();
        if (level().isClientSide && !isRemoved()) {
            level().addParticle(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), 0, 0.01D, 0);
        }
        if (!level().isClientSide && tickCount > 200) discard();
    }

    @Override protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        if (level().isClientSide || !(result.getEntity() instanceof LivingEntity target)) return;
        if (target.hurt(damageSources().thrown(this, getOwner()), 2.0F)) {
            target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 1));
            if (target instanceof ServerPlayer player) PlayerInfectionApi.addExposure(player, 5.0F);
        }
    }

    @Override protected void onHit(HitResult result) {
        super.onHit(result);
        if (level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), 14, .2, .2, .2, .03);
            discard();
        }
    }

    @Override public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
