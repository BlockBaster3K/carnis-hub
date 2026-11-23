package com.carnis.mod.entity;

import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.network.NetworkHooks;

public final class AmalgamBileProjectile extends ThrowableItemProjectile {
    public AmalgamBileProjectile(EntityType<? extends AmalgamBileProjectile> type, Level level) { super(type, level); }
    public AmalgamBileProjectile(Level level, LivingEntity owner) { super(ModEntities.AMALGAM_BILE.get(), owner, level); }
    @Override protected Item getDefaultItem() { return ModItems.AMALGAM_BILE_GLOB.get(); }
    @Override protected boolean canHitEntity(Entity entity) {
        return super.canHitEntity(entity) && !NeuroArmorEventHandler.isHiveEntity(entity)
                && (!(entity instanceof Player player) || !player.isCreative() && !player.isSpectator());
    }
    @Override public void tick() {
        super.tick();
        if (level().isClientSide && !isRemoved()) level().addParticle(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), 0, .01D, 0);
        if (!level().isClientSide && tickCount > 120) discard();
    }
    @Override protected void onHitEntity(EntityHitResult hit) {
        super.onHitEntity(hit);
        if (!(level() instanceof ServerLevel level) || !(hit.getEntity() instanceof LivingEntity target)) return;
        if (target.hurt(level.damageSources().thrown(this, getOwner()), 5.0F))
            target.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 0));
    }
    @Override protected void onHit(HitResult hit) {
        super.onHit(hit);
        if (level() instanceof ServerLevel level) {
            level.playSound(null, blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
            level.sendParticles(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), 14, .2D, .2D, .2D, .04D);
            discard();
        }
    }
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket() { return NetworkHooks.getEntitySpawningPacket(this); }
}
