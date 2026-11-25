package com.carnis.mod.entity.ai;

import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.block.entity.StomachPoolBlockEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.event.StomachPoolAttractEvents;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.animal.Wolf;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.List;

/** Цель движения к бассейну для разрешённых типов мобов. */
public final class StomachPoolAttractGoal extends Goal {
    private static final double SEARCH_RADIUS = 24.0D;
    private static final double RADIUS_SQUARED = SEARCH_RADIUS * SEARCH_RADIUS;
    private static final int SEARCH_INTERVAL = 20;
    private static final int REPATH_INTERVAL = 10;
    private static final int TRAVEL_LIMIT = 600;
    private static final int TELEPORT_FALLBACK_TICK = 300;
    private static final double PATH_SPEED = 1.25D;

    private final Mob mob;
    private StomachPoolBlockEntity pool;
    private long nextSearch;
    private int travelTicks;
    private int nextRepath;
    private boolean teleportFallbackAttempted;
    private double destinationX;
    private double destinationZ;

    public StomachPoolAttractGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    /** Внутренняя цель удержания разделяет резервирование с целью подхода. */
    public Goal createHoldGoal() {
        return new HoldGoal();
    }

    private boolean eligible() {
        // Мобы с InfectionHandler stage тоже разрешены; собственные существа Улья исключены.
        return mob.isAlive() && !mob.isRemoved() && !NeuralMossBlock.isHive(mob)
                && !(mob instanceof HivemindLinkedMob)
                && (!(mob instanceof Wolf wolf) || !wolf.isTame())
                && StomachPoolAttractEvents.isAllowedType(mob.getType());
    }

    private boolean hasCombatTarget() {
        return mob.getTarget() != null;
    }

    private static double distanceSquared(Mob mob, BlockPos pos) {
        return mob.distanceToSqr(pos.getX() + 0.5D, pos.getY() + 0.5D, pos.getZ() + 0.5D);
    }

    private boolean validPool() {
        if (pool == null || pool.isRemoved() || !(mob.level() instanceof ServerLevel server)) return false;
        BlockPos pos = pool.getBlockPos();
        return server.hasChunkAt(pos) && server.getBlockState(pos).is(ModBlocks.STOMACH_POOL.get())
                && server.getBlockEntity(pos) == pool && pool.hasReservation(mob)
                && distanceSquared(mob, pos) <= RADIUS_SQUARED;
    }

    private boolean insidePool() {
        if (pool == null) return false;
        BlockPos pos = pool.getBlockPos();
        return distanceSquared(mob, pos) <= 1.0D && mob.getBoundingBox().intersects(new AABB(pos));
    }

    private void releasePool() {
        if (pool != null) pool.release(mob);
        pool = null;
        teleportFallbackAttempted = false;
    }

    /** Поиск только по блок-сущностям загруженных чанков. */
    private StomachPoolBlockEntity findAndReserve(ServerLevel level) {
        BlockPos origin = mob.blockPosition();
        int minX = (origin.getX() - (int) SEARCH_RADIUS) >> 4;
        int maxX = (origin.getX() + (int) SEARCH_RADIUS) >> 4;
        int minZ = (origin.getZ() - (int) SEARCH_RADIUS) >> 4;
        int maxZ = (origin.getZ() + (int) SEARCH_RADIUS) >> 4;
        List<StomachPoolBlockEntity> candidates = new ArrayList<>();

        for (int x = minX; x <= maxX; x++) {
            for (int z = minZ; z <= maxZ; z++) {
                var chunk = level.getChunkSource().getChunkNow(x, z);
                if (chunk == null) continue;
                for (BlockEntity blockEntity : chunk.getBlockEntities().values()) {
                    if (blockEntity instanceof StomachPoolBlockEntity candidate && !candidate.isRemoved()
                            && distanceSquared(mob, candidate.getBlockPos()) <= RADIUS_SQUARED
                            && level.getBlockState(candidate.getBlockPos()).is(ModBlocks.STOMACH_POOL.get())) {
                        candidates.add(candidate);
                    }
                }
            }
        }

        candidates.sort(Comparator.comparingDouble(candidate -> distanceSquared(mob, candidate.getBlockPos())));
        for (StomachPoolBlockEntity candidate : candidates) {
            if (candidate.reserve(mob)) return candidate;
        }
        return null;
    }

    @Override
    public boolean canUse() {
        if (pool != null) {
            if (!eligible() || hasCombatTarget() || !validPool() || !insidePool()) releasePool();
            else return false;
        }
        // Combat temporarily wins; when it ends, the selector evaluates this goal again.
        if (!(mob.level() instanceof ServerLevel level) || !eligible() || hasCombatTarget()
                || level.getGameTime() < nextSearch) return false;
        nextSearch = level.getGameTime() + SEARCH_INTERVAL;
        pool = findAndReserve(level);
        return pool != null;
    }

    @Override
    public boolean canContinueToUse() {
        return eligible() && !hasCombatTarget() && validPool() && !insidePool() && travelTicks < TRAVEL_LIMIT;
    }

    @Override
    public void start() {
        travelTicks = 0;
        nextRepath = 0;
        if (!validPool()) {
            releasePool();
            return;
        }
        BlockPos pos = pool.getBlockPos();
        destinationX = pos.getX() + 0.25D + mob.getRandom().nextDouble() * 0.5D;
        destinationZ = pos.getZ() + 0.25D + mob.getRandom().nextDouble() * 0.5D;
    }

    @Override
    public void tick() {
        if (!eligible() || hasCombatTarget() || !validPool()) {
            releasePool();
            mob.getNavigation().stop();
            return;
        }
        travelTicks++;
        if (insidePool()) {
            mob.getNavigation().stop();
            return;
        }

        if (!teleportFallbackAttempted && travelTicks >= TELEPORT_FALLBACK_TICK) {
            teleportFallbackAttempted = true;
            if (tryTeleportCloserToPool()) {
                teleportFallbackAttempted = false;
                travelTicks = 0;
                nextRepath = 0;
                return;
            }
        }

        if (--nextRepath <= 0) {
            nextRepath = REPATH_INTERVAL;
            mob.getNavigation().moveTo(destinationX, pool.getBlockPos().getY() + 0.25D,
                    destinationZ, PATH_SPEED);
        }
    }

    private static boolean hasLineOfSight(Level level, Mob mob, BlockPos target) {
        Vec3 to = Vec3.atCenterOf(target);

        Vec3 fromEye = mob.getEyePosition();
        ClipContext eyeContext = new ClipContext(fromEye, to,
                ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, mob);
        if (level.clip(eyeContext).getType() != HitResult.Type.MISS) return false;

        Vec3 fromFeet = mob.position().add(0.0D, 0.1D, 0.0D);
        ClipContext feetContext = new ClipContext(fromFeet, to,
                ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, mob);
        return level.clip(feetContext).getType() == HitResult.Type.MISS;
    }

    /** One safe, short random relocation toward the pool if normal navigation has stalled. */
    private boolean tryTeleportCloserToPool() {
        if (pool == null || !(mob.level() instanceof ServerLevel level)) return false;
        BlockPos poolPos = pool.getBlockPos();
        double targetX = poolPos.getX() + 0.5D;
        double targetZ = poolPos.getZ() + 0.5D;
        double dx = targetX - mob.getX();
        double dz = targetZ - mob.getZ();
        double horizontalDistance = Math.sqrt(dx * dx + dz * dz);
        if (horizontalDistance <= 2.25D) return false;

        double oldX = mob.getX();
        double oldY = mob.getY();
        double oldZ = mob.getZ();
        float oldYaw = mob.getYRot();
        float oldPitch = mob.getXRot();
        double oldPoolDistance = mob.distanceToSqr(targetX, poolPos.getY() + 0.5D, targetZ);
        int baseY = mob.blockPosition().getY();

        for (int attempt = 0; attempt < 8; attempt++) {
            double step = Math.min(2.0D + mob.getRandom().nextDouble(), horizontalDistance - 1.25D);
            double candidateX = oldX + dx / horizontalDistance * step;
            double candidateZ = oldZ + dz / horizontalDistance * step;
            BlockPos base = BlockPos.containing(candidateX, oldY, candidateZ);

            for (int yOffset : new int[]{0, -1, 1}) {
                BlockPos candidate = new BlockPos(base.getX(), baseY + yOffset, base.getZ());
                BlockPos head = candidate.above();
                BlockPos support = candidate.below();
                if (!level.hasChunkAt(support) || !level.hasChunkAt(candidate) || !level.hasChunkAt(head)) continue;

                var feetState = level.getBlockState(candidate);
                var headState = level.getBlockState(head);
                if (!(feetState.isAir() || feetState.canBeReplaced())
                        || !(headState.isAir() || headState.canBeReplaced())
                        || !level.getFluidState(candidate).isEmpty()
                        || !level.getBlockState(support).isFaceSturdy(level, support, net.minecraft.core.Direction.UP)
                        || !hasLineOfSight(level, mob, candidate)) {
                    continue;
                }

                double x = candidate.getX() + 0.5D;
                double y = candidate.getY();
                double z = candidate.getZ() + 0.5D;
                double movedSqr = mob.distanceToSqr(x, oldY, z);
                double newPoolDistance = mob.distanceToSqr(x, poolPos.getY() + 0.5D, z);
                if (movedSqr < 1.5D * 1.5D || movedSqr > 4.0D * 4.0D
                        || newPoolDistance >= oldPoolDistance) continue;

                mob.moveTo(x, y, z, oldYaw, oldPitch);
                if (level.noCollision(mob)) return true;
                mob.moveTo(oldX, oldY, oldZ, oldYaw, oldPitch);
            }
        }
        return false;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void stop() {
        mob.getNavigation().stop();
        // Если моб уже внутри, резервирование передаётся цели удержания.
        if (!eligible() || hasCombatTarget() || !validPool() || !insidePool()) releasePool();
    }

    /** В бассейне удерживаем движение, но не отменяем и не очищаем цель атаки. */
    private final class HoldGoal extends Goal {
        HoldGoal() {
            setFlags(EnumSet.of(Flag.MOVE));
        }

        @Override
        public boolean canUse() {
            return eligible() && !hasCombatTarget() && validPool() && insidePool();
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
        public boolean isInterruptable() {
            return false;
        }

        @Override
        public void start() {
            mob.getNavigation().stop();
        }

        @Override
        public void tick() {
            if (!canUse()) {
                mob.getNavigation().stop();
                releasePool();
                return;
            }
            mob.getNavigation().stop();
            mob.setDeltaMovement(0.0D, mob.getDeltaMovement().y, 0.0D);
            if (pool.countInsideTick(mob)) releasePool();
        }

        @Override
        public void stop() {
            mob.getNavigation().stop();
            releasePool();
        }
    }
}
