package com.carnis.mod.entity;

import com.carnis.mod.event.IncubationEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class ParasiticTendrilEntity extends Monster implements GeoEntity {
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.parasitic_tendril.idle");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    public ParasiticTendrilEntity(EntityType<? extends Monster> type, Level level) { super(type, level); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 10).add(Attributes.MOVEMENT_SPEED, .27)
                .add(Attributes.FOLLOW_RANGE, 24).add(Attributes.ATTACK_DAMAGE, 1);
    }
    @Override protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.1D, false));
        goalSelector.addGoal(5, new RandomStrollGoal(this, .8D));
        targetSelector.addGoal(2, new HurtByTargetGoal(this));
        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 10, true, false,
                target -> IncubationEvents.isEligible(target) && !InfectionHandler.isInfected(target)));
    }
    @Override public boolean doHurtTarget(Entity target) {
        if (!(level() instanceof ServerLevel server) || !(target instanceof LivingEntity host)
                || !host.isAlive() || !IncubationEvents.isEligible(host) || InfectionHandler.isInfected(host)) return false;
        boolean hostile = IncubationEvents.isHostileHost(host);
        boolean armored = false;
        for (EquipmentSlot slot : EquipmentSlot.values()) {
            if (slot.isArmor() && !host.getItemBySlot(slot).isEmpty()) { armored = true; break; }
        }
        // Armor subtracts 15 percentage points, not 15 percent of the chance.
        float chance = hostile ? (armored ? 0.30F : 0.45F) : 0.85F;
        boolean success = random.nextFloat() < chance;
        if (success) {
            InfectionHandler.begin(host);
            server.playSound(null, host.blockPosition(), SoundEvents.SLIME_SQUISH,
                    SoundSource.HOSTILE, 0.9F, 1.0F);
            server.sendParticles(ModParticles.BIOMASS_SPARK.get(), host.getX(), host.getY(0.6D), host.getZ(),
                    12, host.getBbWidth() * 0.3D, host.getBbHeight() * 0.2D, host.getBbWidth() * 0.3D, 0.03D);
        } else {
            host.hurt(server.damageSources().mobAttack(this), 1.0F);
            server.playSound(null, blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
            server.sendParticles(ParticleTypes.POOF, getX(), getY(0.5D), getZ(), 12, .2D, .25D, .2D, .03D);
            server.sendParticles(ModParticles.BIOMASS_SPARK.get(), getX(), getY(0.5D), getZ(), 10, .2D, .25D, .2D, .08D);
        }
        discard();
        return true;
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "whip", 2, state -> state.setAndContinue(IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
