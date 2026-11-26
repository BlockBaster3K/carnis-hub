package com.carnis.mod.entity.ai;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.CarnisWorldData;
import com.carnis.mod.world.SubstratePlacer;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.phys.Vec3;
import java.util.EnumSet;

public final class CarnisGestationGoal extends Goal {
    private final Mob mob;
    private int ticks;
    public CarnisGestationGoal(Mob mob) { this.mob = mob; setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK)); }
    @Override public boolean canUse() {
        if (!(mob.level() instanceof ServerLevel level) || mob.getTarget() != null || !mob.onGround()
                || mob.getPersistentData().contains(CarnisFeedingGoal.DEADLINE) || mob.getRandom().nextInt(100) != 0
                || !level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)
                || CarnisWorldData.get(level).getBiomassPoints() < 200L) return false;
        return safeGround(level) && noHeartInLoadedArea(level);
    }
    @Override public boolean canContinueToUse() {
        return ticks < 60 && mob.isAlive() && mob.level() instanceof ServerLevel level && mob.getTarget() == null
                && !mob.getPersistentData().contains(CarnisFeedingGoal.DEADLINE)
                && level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING) && safeGround(level)
                && CarnisWorldData.get(level).getBiomassPoints() >= 200L;
    }
    @Override public boolean requiresUpdateEveryTick() { return true; }
    @Override public void start() { ticks = 0; mob.getNavigation().stop(); }
    @Override public void tick() {
        if (!(mob.level() instanceof ServerLevel level)) return;
        mob.getNavigation().stop();
        if (++ticks == 1) level.playSound(null, mob.blockPosition(), ModSounds.AMALGAM_ROAR.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
        if (ticks % 5 == 0) level.sendParticles(ParticleTypes.CRIMSON_SPORE, mob.getX(), mob.getY(), mob.getZ(), 12, .35, .2, .35, .03);
        if (ticks >= 60 && level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)
                && safeGround(level) && noHeartInLoadedArea(level)) {
            BlockPos ground = mob.blockPosition().below();
            if (level.setBlockAndUpdate(ground, ModBlocks.PULSING_HEART.get().defaultBlockState())) {
                SubstratePlacer.placePatch(level, ground);
                mob.discard();
            }
        }
    }
    private boolean safeGround(ServerLevel level) {
        BlockPos pos = mob.blockPosition().below();
        if (!level.hasChunkAt(pos) || level.isOutsideBuildHeight(pos)) return false;
        var state = level.getBlockState(pos);
        return !state.isAir() && state.getFluidState().isEmpty() && !state.hasBlockEntity()
                && state.isSolidRender(level, pos) && state.getDestroySpeed(level, pos) >= 0;
    }
    private boolean noHeartInLoadedArea(ServerLevel level) {
        BlockPos origin = mob.blockPosition();
        int minX = (origin.getX() - 48) >> 4, maxX = (origin.getX() + 48) >> 4;
        int minZ = (origin.getZ() - 48) >> 4, maxZ = (origin.getZ() + 48) >> 4;
        Vec3 center = mob.position();
        for (int x = minX; x <= maxX; x++) for (int z = minZ; z <= maxZ; z++) {
            var chunk = level.getChunkSource().getChunkNow(x, z);
            if (chunk == null) return false; // do not create a competing heart near unloaded terrain
            for (var blockEntity : chunk.getBlockEntities().values()) {
                if (blockEntity instanceof PulsingHeartBlockEntity && Vec3.atCenterOf(blockEntity.getBlockPos()).distanceToSqr(center) <= 48D * 48D) return false;
            }
        }
        return true;
    }
}
