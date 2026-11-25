package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.BiomassMaggotEntity;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.ForgeEventFactory;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/** Bounded incremental search: never load chunks or scan an entire cube in one tick. */
public final class AmalgamBiomassFeast {
    private static final int RADIUS = 8;
    private static final int BUDGET = 256;
    private static final List<BlockPos> OFFSETS = offsets();
    private final FleshAmalgamEntity boss;
    private BlockPos anchor;
    private int cursor;
    public AmalgamBiomassFeast(FleshAmalgamEntity boss) { this.boss = boss; }
    private static List<BlockPos> offsets() {
        List<BlockPos> result = new ArrayList<>();
        for (int x = -RADIUS; x <= RADIUS; x++) for (int y = -RADIUS; y <= RADIUS; y++)
            for (int z = -RADIUS; z <= RADIUS; z++) if (x*x + y*y + z*z <= RADIUS * RADIUS)
                result.add(new BlockPos(x, y, z));
        result.sort(Comparator.comparingInt(p -> p.getX()*p.getX() + p.getY()*p.getY() + p.getZ()*p.getZ()));
        return List.copyOf(result);
    }
    public void tick(ServerLevel level) {
        if (!boss.isAlive() || boss.getHealth() >= boss.getMaxHealth() * .4F || !HiveSwarmCoordinator.validTarget(boss, boss.getTarget()) || level.getGameTime() < boss.getFeastReady()
                || boss.tickCount % 10 != 0 || !ForgeEventFactory.getMobGriefingEvent(level, boss)) return;
        LivingEntity prey = level.getEntitiesOfClass(LivingEntity.class, boss.getBoundingBox().inflate(RADIUS),
                e -> e.isAlive() && (e instanceof BiomassMaggotEntity || e instanceof ParasiticTendrilEntity)
                        && boss.distanceToSqr(e) <= RADIUS * RADIUS).stream()
                .min(Comparator.comparingDouble(boss::distanceToSqr)).orElse(null);
        if (prey != null) {
            Vec3 location = prey.position();
            prey.discard();
            feed(level, location);
            return;
        }
        if (anchor == null || anchor.distSqr(boss.blockPosition()) > RADIUS * RADIUS) {
            anchor = boss.blockPosition().immutable();
            cursor = 0;
        }
        int end = Math.min(cursor + BUDGET, OFFSETS.size());
        while (cursor < end) {
            BlockPos pos = anchor.offset(OFFSETS.get(cursor++));
            if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)
                    || boss.position().distanceToSqr(Vec3.atCenterOf(pos)) > RADIUS * RADIUS
                    || !level.getBlockState(pos).is(ModBlocks.BIOMASS_REMAINS.get())) continue;
            if (level.setBlockAndUpdate(pos, Blocks.AIR.defaultBlockState())) {
                feed(level, Vec3.atCenterOf(pos));
                return;
            }
        }
        if (cursor >= OFFSETS.size()) { anchor = null; cursor = 0; }
    }
    private void feed(ServerLevel level, Vec3 from) {
        boss.setFeastReady(level.getGameTime() + 100L);
        anchor = null;
        cursor = 0;
        boss.heal(25.0F);
        boss.triggerRoarAnimation();
        level.playSound(null, boss.blockPosition(), ModSounds.AMALGAM_ROAR.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), from.x, from.y + .2D, from.z, 20, .35D, .35D, .35D, .04D);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), boss.getX(), boss.getY(.6D), boss.getZ(),
                30, boss.getBbWidth() * .35D, boss.getBbHeight() * .3D, boss.getBbWidth() * .35D, .06D);
    }
}
