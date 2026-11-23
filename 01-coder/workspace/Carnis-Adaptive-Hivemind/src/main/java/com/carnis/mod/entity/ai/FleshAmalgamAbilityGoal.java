package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.AmalgamBileProjectile;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import java.util.EnumSet;

/** One wind-up at a time; cooldowns belong to the entity and persist across saves. */
public final class FleshAmalgamAbilityGoal extends Goal {
    private static final int SLAM = 1, PULL = 2, BILE = 3;
    private final FleshAmalgamEntity boss;
    private LivingEntity target;
    private int ability, elapsed;
    public FleshAmalgamAbilityGoal(FleshAmalgamEntity boss) {
        this.boss = boss;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }
    @Override public boolean canUse() {
        if (!(boss.level() instanceof ServerLevel) || !boss.isAlive()) return false;
        LivingEntity current = boss.getTarget();
        if (!HiveSwarmCoordinator.validTarget(boss, current) || !boss.hasLineOfSight(current)) return false;
        double distance = boss.distanceToSqr(current);
        if (distance < 25.0D && boss.onGround() && boss.canUseAbility(SLAM)) ability = SLAM;
        else if (distance >= 64.0D && distance <= 484.0D && boss.canUseAbility(PULL)) ability = PULL;
        else if (distance >= 25.0D && distance <= 676.0D && boss.canUseAbility(BILE)) ability = BILE;
        else return false;
        target = current;
        return true;
    }
    @Override public boolean canContinueToUse() {
        return boss.isAlive() && HiveSwarmCoordinator.validTarget(boss, target) && elapsed < 20;
    }
    @Override public boolean requiresUpdateEveryTick() { return true; }
    @Override public void start() {
        elapsed = 0;
        boss.consumeAbilityCooldown(ability);
        boss.getNavigation().stop();
        if (ability == SLAM) boss.triggerSlamAnimation();
    }
    @Override public void tick() {
        if (!(boss.level() instanceof ServerLevel level) || !HiveSwarmCoordinator.validTarget(boss, target)) return;
        boss.getNavigation().stop();
        boss.getLookControl().setLookAt(target, 30.0F, 30.0F);
        elapsed++;
        if (ability == SLAM && elapsed == 12 && boss.onGround()) slam(level);
        if (ability == PULL && elapsed == 8) pull(level);
        if (ability == BILE && elapsed == 8) spit(level);
    }
    @Override public void stop() { target = null; ability = 0; elapsed = 0; }
    private void slam(ServerLevel level) {
        level.playSound(null, boss.blockPosition(), ModSounds.HIVE_AMALGAM_SLAM.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
        for (int i = 0; i < 40; i++) {
            double angle = Math.PI * 2.0D * i / 40.0D;
            double x = boss.getX() + Math.cos(angle) * 6.0D, z = boss.getZ() + Math.sin(angle) * 6.0D;
            level.sendParticles(ModParticles.BIOMASS_SPARK.get(), x, boss.getY() + .15D, z, 1, 0, .05D, 0, 0);
        }
        for (LivingEntity victim : level.getEntitiesOfClass(LivingEntity.class, boss.getBoundingBox().inflate(6.0D),
                e -> e != boss && HiveSwarmCoordinator.validTarget(boss, e)
                        && boss.distanceToSqr(e) <= 36.0D)) {
            if (!victim.hurt(level.damageSources().mobAttack(boss), 10.0F)) continue;
            victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 1));
            Vec3 away = victim.position().subtract(boss.position()).multiply(1, 0, 1);
            if (away.lengthSqr() > 1.0E-6D) away = away.normalize().scale(.30D);
            Vec3 old = victim.getDeltaMovement();
            victim.setDeltaMovement(old.x + away.x, Math.max(.65D, old.y + .65D), old.z + away.z);
            syncVelocity(level, victim);
        }
    }
    private void pull(ServerLevel level) {
        if (!HiveSwarmCoordinator.validTarget(boss, target) || !boss.hasLineOfSight(target)) return;
        double distance = boss.distanceToSqr(target);
        if (distance < 64.0D || distance > 484.0D) return;
        Vec3 delta = boss.position().add(0, .3D, 0).subtract(target.position());
        if (delta.lengthSqr() < 1.0E-6D) return;
        Vec3 motion = delta.normalize().scale(1.35D).add(0, .20D, 0);
        target.setDeltaMovement(motion);
        syncVelocity(level, target);
        level.playSound(null, boss.blockPosition(), ModSounds.ORGANIC_CREAK.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
        for (int i = 1; i <= 10; i++) {
            Vec3 point = boss.getEyePosition().lerp(target.getEyePosition(), i / 11.0D);
            level.sendParticles(ModParticles.BIOMASS_SPARK.get(), point.x, point.y, point.z, 1, 0, 0, 0, 0);
        }
    }
    private void spit(ServerLevel level) {
        if (!HiveSwarmCoordinator.validTarget(boss, target) || !boss.hasLineOfSight(target)
                || boss.distanceToSqr(target) > 676.0D) return;
        Vec3 origin = boss.getEyePosition();
        Vec3 aim = target.getEyePosition().subtract(origin);
        if (aim.lengthSqr() < 1.0E-6D) return;
        for (int degrees : new int[]{-10, 0, 10}) {
            Vec3 direction = aim.yRot((float) Math.toRadians(degrees));
            AmalgamBileProjectile projectile = new AmalgamBileProjectile(level, boss);
            projectile.setPos(origin.x, origin.y, origin.z);
            projectile.shoot(direction.x, direction.y, direction.z, 1.35F, 0.0F);
            level.addFreshEntity(projectile);
        }
        level.playSound(null, boss.blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
    }
    private static void syncVelocity(ServerLevel level, LivingEntity target) {
        ClientboundSetEntityMotionPacket packet = new ClientboundSetEntityMotionPacket(target);
        level.getChunkSource().broadcast(target, packet);
        if (target instanceof ServerPlayer player) player.connection.send(packet);
    }
}
