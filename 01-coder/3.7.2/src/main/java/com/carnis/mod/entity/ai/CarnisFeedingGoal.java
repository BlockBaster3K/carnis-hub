package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.AssimilatingMob;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

public final class CarnisFeedingGoal extends Goal {
    public static final String DEADLINE = "carnis:feeding_until";
    public static final String X = "carnis:feeding_x";
    public static final String Y = "carnis:feeding_y";
    public static final String Z = "carnis:feeding_z";
    private static final String TRAVEL = "carnis:feeding_travel";
    private final Mob mob;
    private boolean facingLocked;
    private float feedingYaw;
    private float feedingPitch;

    public CarnisFeedingGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (!mob.isAlive() || !(mob.level() instanceof ServerLevel level)
                || !mob.getPersistentData().contains(DEADLINE)) return false;
        var tag = mob.getPersistentData();
        if (!tag.contains(X) || !tag.contains(Y) || !tag.contains(Z)
                || !Double.isFinite(tag.getDouble(X)) || !Double.isFinite(tag.getDouble(Y))
                || !Double.isFinite(tag.getDouble(Z))) {
            tag.remove(DEADLINE);
            tag.remove(TRAVEL);
            return false;
        }
        BlockPos pos = BlockPos.containing(tag.getDouble(X), tag.getDouble(Y), tag.getDouble(Z));
        return !level.isOutsideBuildHeight(pos) && level.hasChunkAt(pos);
    }

    @Override
    public boolean canContinueToUse() {
        return canUse();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void start() {
        facingLocked = false;
        setAssimilating(false);
        mob.setTarget(null);
    }

    @Override
    public void stop() {
        facingLocked = false;
        setAssimilating(false);
        mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        if (!canUse() || !(mob.level() instanceof ServerLevel level)) {
            stop();
            return;
        }
        var tag = mob.getPersistentData();
        Vec3 corpse = new Vec3(tag.getDouble(X), tag.getDouble(Y), tag.getDouble(Z));
        mob.setTarget(null);
        if (mob.distanceToSqr(corpse) > 4.0D) {
            facingLocked = false;
            setAssimilating(false);
            int travel = tag.getInt(TRAVEL) + 1;
            tag.putInt(TRAVEL, travel);
            tag.putInt(DEADLINE, 0);
            if (travel > 200) {
                tag.remove(DEADLINE);
                tag.remove(TRAVEL);
            } else if (travel % 10 == 1) {
                mob.getNavigation().moveTo(corpse.x, corpse.y, corpse.z, 1.0D);
            }
            return;
        }

        mob.getNavigation().stop();
        if (!facingLocked) {
            net.minecraft.core.BlockPos remains = findRemains(level, corpse);
            if (remains != null) corpse = Vec3.atCenterOf(remains);
            double dx = corpse.x - mob.getX(), dz = corpse.z - mob.getZ();
            double horizontal = Math.sqrt(dx * dx + dz * dz);
            float desiredYaw = horizontal < 1.0E-4D ? mob.getYRot()
                    : (float) Math.toDegrees(Math.atan2(-dx, dz));
            feedingYaw = mob.getYRot() + net.minecraft.util.Mth.wrapDegrees(desiredYaw - mob.getYRot());
            double dy = corpse.y - mob.getEyeY();
            feedingPitch = (float) net.minecraft.util.Mth.clamp(
                    -Math.toDegrees(Math.atan2(dy, Math.max(horizontal, 0.12D))), -70D, 70D);
            facingLocked = true;
        }
        mob.setYRot(feedingYaw);
        mob.setYHeadRot(feedingYaw);
        mob.setYBodyRot(feedingYaw);
        mob.setXRot(feedingPitch);
        setAssimilating(true);

        if (mob.tickCount % 20 == 0) {
            level.playSound(null, mob.blockPosition(), ModSounds.DIGESTOR_CHURN.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
        if (mob.tickCount % 5 == 0) {
            Vec3 destination = mob.position().add(0.0D, mob.getBbHeight() * 0.55D, 0.0D);
            for (int i = 0; i < 2; i++) {
                Vec3 origin = corpse.add((level.random.nextDouble() - 0.5D) * 0.3D,
                        0.15D, (level.random.nextDouble() - 0.5D) * 0.3D);
                Vec3 velocity = destination.subtract(origin).scale(0.12D);
                level.sendParticles(ModParticles.BIOMASS_SPARK.get(), origin.x, origin.y, origin.z, 0,
                        velocity.x, velocity.y, velocity.z, 1.0D);
            }
        }
        if (tag.getInt(DEADLINE) + 1 >= 100) {
            tag.remove(DEADLINE);
            tag.remove(TRAVEL);
            net.minecraft.core.BlockPos remains = findRemains(level, corpse);
            if (remains != null && net.minecraftforge.event.ForgeEventFactory.getMobGriefingEvent(level, mob))
                level.removeBlock(remains, false);
            setAssimilating(false);
            facingLocked = false;
            CarnisWorldData.get(level).addBiomassPoints(50L);
            ModMessages.sendToPlayersInLevel(level);
        } else {
            tag.putInt(DEADLINE, tag.getInt(DEADLINE) + 1);
        }
    }

    private static net.minecraft.core.BlockPos findRemains(ServerLevel level, Vec3 corpse) {
        net.minecraft.core.BlockPos base = net.minecraft.core.BlockPos.containing(corpse);
        for (int dy : new int[]{0, -1, 1}) {
            net.minecraft.core.BlockPos pos = base.offset(0, dy, 0);
            if (level.hasChunkAt(pos) && !level.isOutsideBuildHeight(pos)
                    && level.getBlockState(pos).is(com.carnis.mod.init.ModBlocks.BIOMASS_REMAINS.get())) return pos;
        }
        return null;
    }

    private void setAssimilating(boolean value) {
        if (mob instanceof AssimilatingMob assimilatingMob) {
            assimilatingMob.setAssimilating(value);
        }
    }
}
