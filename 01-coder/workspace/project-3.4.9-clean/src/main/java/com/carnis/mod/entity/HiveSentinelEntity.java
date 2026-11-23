package com.carnis.mod.entity;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.event.HypnosisEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.animal.Pig;
import net.minecraft.world.entity.animal.Sheep;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class HiveSentinelEntity extends Monster implements GeoEntity, HivemindLinkedMob, BiomassValued {
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.hive_sentinel.idle");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private BlockPos heartPos;
    public HiveSentinelEntity(EntityType<? extends Monster> type, Level level) { super(type, level); setNoGravity(true); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 60.0D)
                .add(Attributes.ARMOR, 8.0D).add(Attributes.KNOCKBACK_RESISTANCE, 1.0D).add(Attributes.MOVEMENT_SPEED, 0.0D);
    }
    @Override public long getBiomassValue() { return 40L; }
    public void setHeartPos(BlockPos pos) { heartPos = pos.immutable(); }
    @Override public boolean isPushable() { return false; }
    @Override public void push(double x, double y, double z) { }
    @Override protected void registerGoals() { }
    @Override public void tick() {
        super.tick();
        setDeltaMovement(0, 0, 0);
        if (!(level() instanceof ServerLevel server) || !isAlive() || tickCount % 20 != 0) return;
        if (tickCount % 100 == 0) server.playSound(null, blockPosition(), ModSounds.PHANTOM_WHISPER.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
        BlockPos pool = heartPos == null ? null : HiveNetwork.nearestLoaded(server, HiveNetwork.Kind.POOL, heartPos, 32);
        AABB area = getBoundingBox().inflate(16.0D);
        for (var animal : server.getEntitiesOfClass(net.minecraft.world.entity.animal.Animal.class, area,
                a -> (a instanceof Cow || a instanceof Sheep || a instanceof Pig) && a.isAlive()
                        && a.distanceToSqr(this) <= 256.0D && !InfectionHandler.isInfected(a))) {
            HypnosisEvents.apply(animal, server, pool);
        }
    }
    @Override public void die(net.minecraft.world.damagesource.DamageSource source) {
        if (level() instanceof ServerLevel server && heartPos != null) {
            HiveNetwork.get(server).noteSentinelDeath(getUUID());
            if (server.hasChunkAt(heartPos) && server.getBlockEntity(heartPos) instanceof PulsingHeartBlockEntity heart)
                heart.sentinelDied(getUUID());
        }
        super.die(source);
    }
    @Override public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag); if (heartPos != null) tag.putLong("HiveHeart", heartPos.asLong());
    }
    @Override public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag); if (tag.contains("HiveHeart")) heartPos = BlockPos.of(tag.getLong("HiveHeart"));
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "idle", 0, state -> state.setAndContinue(IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
