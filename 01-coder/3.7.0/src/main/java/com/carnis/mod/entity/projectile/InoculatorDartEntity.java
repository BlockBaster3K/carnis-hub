package com.carnis.mod.entity.projectile;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HiveSentinelEntity;
import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.event.DartTreatmentEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.event.IncubationEvents;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.network.NetworkHooks;

public final class InoculatorDartEntity extends AbstractArrow {
    public enum DartType { PURIFICATION, VIRAL }
    private static final EntityDataAccessor<Integer> CONTENT = SynchedEntityData.defineId(InoculatorDartEntity.class, EntityDataSerializers.INT);
    public InoculatorDartEntity(EntityType<? extends InoculatorDartEntity> type, Level level) {
        super(type, level); pickup = Pickup.DISALLOWED;
    }
    public InoculatorDartEntity(Level level, LivingEntity owner, DartType contents) {
        super(ModEntities.INOCULATOR_DART.get(), owner, level);
        pickup = Pickup.DISALLOWED;
        setDartType(contents);
    }
    @Override protected void defineSynchedData() { super.defineSynchedData(); entityData.define(CONTENT, 0); }
    public DartType getDartType() { return entityData.get(CONTENT) == 1 ? DartType.VIRAL : DartType.PURIFICATION; }
    public void setDartType(DartType type) { entityData.set(CONTENT, type == DartType.VIRAL ? 1 : 0); }
    @Override public void addAdditionalSaveData(CompoundTag tag) { super.addAdditionalSaveData(tag); tag.putString("DartType", getDartType().name()); }
    @Override public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        setDartType("VIRAL".equals(tag.getString("DartType")) ? DartType.VIRAL : DartType.PURIFICATION);
    }
    @Override public void tick() {
        super.tick();
        if (isRemoved() || inGround || isNoGravity()) return;
        // AbstractArrow applies 0.05 blocks/tick². Counter 0.04 after its normal flight tick.
        setDeltaMovement(getDeltaMovement().add(0, .04D, 0));
        if (level().isClientSide) {
            boolean clean = getDartType() == DartType.PURIFICATION;
            level().addParticle(clean ? ModParticles.PURIFIER_FLAME.get() : ModParticles.BIOMASS_SPARK.get(),
                    getX(), getY(), getZ(), 0, 0, 0);
            if (tickCount % 3 == 0) level().addParticle(clean ? ParticleTypes.COMPOSTER : ParticleTypes.CRIMSON_SPORE,
                    getX(), getY(), getZ(), 0, .005D, 0);
        }
    }
    @Override protected void onHitEntity(EntityHitResult result) {
        if (!(level() instanceof ServerLevel server)) return;
        Entity hit = result.getEntity();
        if (hit instanceof LivingEntity living) {
            if (getDartType() == DartType.PURIFICATION) purify(server, living);
            else infect(server, living);
        }
        discard();
    }
    private void purify(ServerLevel level, LivingEntity target) {
        if (target instanceof Player player) {
            PlayerInfectionApi.addInfection(player, -35F);
            player.removeEffect(MobEffects.CONFUSION);
            player.removeEffect(MobEffects.BLINDNESS);
            player.removeEffect(MobEffects.MOVEMENT_SLOWDOWN);
        } else if (target instanceof InfectedZombieEntity || target instanceof InfectedSkeletonEntity) {
            DartTreatmentEvents.startRegression((Mob) target);
        } else if (target instanceof FleshAmalgamEntity || target instanceof HiveSentinelEntity || target instanceof CerebralNexusEntity) {
            target.hurt(level.damageSources().magic(), 25F);
            if (target.isAlive()) DartTreatmentEvents.stun((Mob) target, 60);
        }
    }
    private void infect(ServerLevel level, LivingEntity target) {
        if (target instanceof Player player) {
            if (getOwner() instanceof Player shooter && !shooter.canHarmPlayer(player)) return;
            PlayerInfectionApi.addInfection(player, 25F);
            player.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 120, 0));
            return;
        }
        if (!IncubationEvents.isEligible(target)) return;
        EntityType<?> type = target.getType();
        if (type == EntityType.ZOMBIE || type == EntityType.SKELETON || type == EntityType.CREEPER
                || type == EntityType.SPIDER || type == EntityType.CAVE_SPIDER) {
            DartTreatmentEvents.startMutation((Mob) target);
        } else {
            InfectionHandler.beginAccelerated(target);
        }
    }
    @Override protected void onHitBlock(BlockHitResult hit) { setSoundEvent(ModSounds.DART_HIT.get()); super.onHitBlock(hit); }
    @Override protected SoundEvent getDefaultHitGroundSoundEvent() { return ModSounds.DART_HIT.get(); }
    @Override protected ItemStack getPickupItem() { return ItemStack.EMPTY; }
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket() { return NetworkHooks.getEntitySpawningPacket(this); }
}
