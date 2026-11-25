package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.TickTask;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class AmalgamationHandler {
    public static final double SEARCH_RADIUS = 12.0D;
    public static final int REQUIRED_MOBS = 3;

    private static final double SEARCH_RADIUS_SQUARED =
            SEARCH_RADIUS * SEARCH_RADIUS;

    private record Fusion(ServerLevel level, net.minecraft.core.BlockPos heart, Vec3 center,
                          List<Mob> mobs, List<Vec3> starts, int elapsed) { }
    private static final java.util.Map<ServerLevel, List<Fusion>> ACTIVE = new java.util.WeakHashMap<>();

    private AmalgamationHandler() {
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onDamage(net.minecraftforge.event.entity.living.LivingHurtEvent event) {
        if (event.isCanceled() || event.getAmount() <= 0.0F
                || !(event.getEntity() instanceof net.minecraft.world.entity.monster.Zombie zombie)
                || !(zombie.level() instanceof ServerLevel level)) return;
        MinecraftServer server = level.getServer();
        server.tell(new TickTask(server.getTickCount(), () -> attemptAmalgamation(level, zombie)));
    }

    /** Called by a heart's existing pulse; biomass is a threshold, not consumed. */
    public static void onHighBiomassPulse(ServerLevel level, net.minecraft.core.BlockPos heartPos) {
        if (com.carnis.mod.world.CarnisWorldData.get(level).getBiomassPoints() < 300L) return;
        Vec3 center = Vec3.atCenterOf(heartPos);
        List<net.minecraft.world.entity.monster.Zombie> zombies = level.getEntitiesOfClass(
                net.minecraft.world.entity.monster.Zombie.class, AABB.ofSize(center, 24, 24, 24),
                mob -> mob.isAlive() && mob.position().distanceToSqr(center) <= SEARCH_RADIUS_SQUARED);
        if (!zombies.isEmpty()) attemptAmalgamation(level, zombies.get(0));
    }

    private static net.minecraft.core.BlockPos findHeart(ServerLevel level, Mob mob) {
        net.minecraft.world.level.ChunkPos start = new net.minecraft.world.level.ChunkPos(mob.blockPosition());
        net.minecraft.core.BlockPos best = null;
        double nearest = SEARCH_RADIUS_SQUARED;
        for (int cx = start.x - 1; cx <= start.x + 1; cx++) {
            for (int cz = start.z - 1; cz <= start.z + 1; cz++) {
                var chunk = level.getChunkSource().getChunkNow(cx, cz);
                if (chunk == null) continue;
                for (var blockEntity : chunk.getBlockEntities().values()) {
                    if (!(blockEntity instanceof com.carnis.mod.block.entity.PulsingHeartBlockEntity)) continue;
                    net.minecraft.core.BlockPos p = blockEntity.getBlockPos();
                    double distance = mob.position().distanceToSqr(Vec3.atCenterOf(p));
                    if (distance <= nearest) { nearest = distance; best = p; }
                }
            }
        }
        return best;
    }

    private static void attemptAmalgamation(
            ServerLevel serverLevel,
            Mob joiningMob
    ) {
        if (
                !joiningMob.isAddedToWorld()
                        || !joiningMob.isAlive()
                        || joiningMob.level() != serverLevel
                        || !isFusionCandidate(joiningMob)
        ) {
            return;
        }

        net.minecraft.core.BlockPos heartPos = findHeart(serverLevel, joiningMob);
        if (heartPos == null || com.carnis.mod.world.CarnisWorldData.get(serverLevel).getBiomassPoints() < 300L) return;
        Vec3 searchCenter = Vec3.atCenterOf(heartPos);
        AABB searchBox = AABB.ofSize(
                searchCenter,
                SEARCH_RADIUS * 2.0D,
                SEARCH_RADIUS * 2.0D,
                SEARCH_RADIUS * 2.0D
        );
        List<Mob> candidates = new ArrayList<>();
        candidates.add(joiningMob);
        candidates.addAll(serverLevel.getEntitiesOfClass(
                Mob.class,
                searchBox,
                candidate -> candidate != joiningMob
                        && isFusionCandidate(candidate)
                        && candidate.position().distanceToSqr(searchCenter)
                        <= SEARCH_RADIUS_SQUARED
        ));

        if (candidates.size() < REQUIRED_MOBS) {
            return;
        }

        candidates.sort(
                Comparator
                        .comparingDouble(
                                (Mob candidate) -> candidate.position()
                                        .distanceToSqr(searchCenter)
                        )
                        .thenComparingInt(Mob::getId)
        );
        List<Mob> selectedMobs = List.copyOf(
                candidates.subList(0, REQUIRED_MOBS)
        );
        Vec3 fusionPoint = averagePosition(selectedMobs);
        List<Vec3> starts = selectedMobs.stream().map(Mob::position).toList();
        ACTIVE.computeIfAbsent(serverLevel, ignored -> new ArrayList<>())
                .add(new Fusion(serverLevel, heartPos.immutable(), fusionPoint, selectedMobs, starts, 0));
    }

    @SubscribeEvent
    public static void onLevelTick(net.minecraftforge.event.TickEvent.LevelTickEvent event) {
        if (event.phase != net.minecraftforge.event.TickEvent.Phase.END || !(event.level instanceof ServerLevel level)) return;
        List<Fusion> fusions = ACTIVE.get(level);
        if (fusions == null) return;
        for (int i = fusions.size() - 1; i >= 0; i--) {
            Fusion f = fusions.get(i);
            if (!level.hasChunkAt(f.heart()) || !(level.getBlockEntity(f.heart()) instanceof com.carnis.mod.block.entity.PulsingHeartBlockEntity)
                    || com.carnis.mod.world.CarnisWorldData.get(level).getBiomassPoints() < 300L
                    || f.mobs().stream().anyMatch(m -> !m.isAlive() || !m.isAddedToWorld() || m.level() != level)) {
                fusions.remove(i);
                continue;
            }
            int tick = f.elapsed() + 1;
            double progress = tick / 30.0D;
            for (int k = 0; k < f.mobs().size(); k++) {
                Mob mob = f.mobs().get(k);
                Vec3 start = f.starts().get(k);
                double angle = tick * .35D + k * Math.PI * 2.0D / 3.0D;
                double radius = (1.0D - progress) * 0.55D;
                double x = start.x * (1.0D - progress) + f.center().x * progress + Math.cos(angle) * radius;
                double z = start.z * (1.0D - progress) + f.center().z * progress + Math.sin(angle) * radius;
                double y = start.y * (1.0D - progress) + f.center().y * progress + 1.5D * progress;
                mob.teleportTo(x, y, z);
                mob.setDeltaMovement(Vec3.ZERO);
                mob.resetFallDistance();
            }
            for (int k = 0; k < 8; k++) {
                double angle = tick * .35D + k * Math.PI / 4.0D;
                double r = 1.8D * (1.0D - progress) + .2D;
                double x = f.center().x + Math.cos(angle) * r;
                double y = f.center().y + .15D + progress * 2.2D;
                double z = f.center().z + Math.sin(angle) * r;
                level.sendParticles(ParticleTypes.CRIMSON_SPORE, x, y, z, 1, 0, 0, 0, 0);
                if (k % 2 == 0) level.sendParticles(ParticleTypes.SQUID_INK, x, y, z, 1, 0, 0, 0, 0);
                if (k == 0) level.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, x, y, z, 1, 0, 0, 0, 0);
            }
            if (tick < 30) { fusions.set(i, new Fusion(level, f.heart(), f.center(), f.mobs(), f.starts(), tick)); continue; }
            FleshAmalgamEntity amalgam = ModEntities.FLESH_AMALGAM.get().create(level);
            if (amalgam != null) {
                amalgam.moveTo(f.center().x, f.center().y, f.center().z, level.random.nextFloat() * 360.0F, 0.0F);
                // Commit only after successful spawn; failed insertions preserve all zombies.
                if (level.addFreshEntity(amalgam)) {
                    for (Mob mob : f.mobs()) mob.discard();
                    playFusionEffects(level, f.center());
                    level.playSound(null, f.center().x, f.center().y, f.center().z, ModSounds.AMALGAM_ROAR.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
                }
            }
            fusions.remove(i);
        }
        if (fusions.isEmpty()) ACTIVE.remove(level);
    }

    @SubscribeEvent
    public static void onLevelUnload(net.minecraftforge.event.level.LevelEvent.Unload event) {
        if (event.getLevel() instanceof ServerLevel level) ACTIVE.remove(level);
    }

    private static boolean isFusionCandidate(Mob mob) {
        if (!(mob instanceof net.minecraft.world.entity.monster.Zombie) || !mob.isAlive()) return false;
        if (!(mob.level() instanceof ServerLevel level)) return false;
        return ACTIVE.getOrDefault(level, List.of()).stream().noneMatch(f -> f.mobs().contains(mob));
    }

    private static Vec3 averagePosition(List<Mob> mobs) {
        double x = 0.0D;
        double y = 0.0D;
        double z = 0.0D;

        for (Mob mob : mobs) {
            x += mob.getX();
            y += mob.getY();
            z += mob.getZ();
        }

        double divisor = mobs.size();
        return new Vec3(x / divisor, y / divisor, z / divisor);
    }

    private static void playFusionEffects(
            ServerLevel serverLevel,
            Vec3 fusionPoint
    ) {
        serverLevel.playSound(
                null,
                fusionPoint.x,
                fusionPoint.y,
                fusionPoint.z,
                ModSounds.AMALGAMATION_FUSE.get(),
                SoundSource.HOSTILE,
                1.0F,
                1.0F
        );

        ItemParticleOption fleshParticles = new ItemParticleOption(
                ParticleTypes.ITEM,
                new ItemStack(ModItems.LIVING_FLESH.get())
        );
        serverLevel.sendParticles(
                fleshParticles,
                fusionPoint.x,
                fusionPoint.y + 1.0D,
                fusionPoint.z,
                80,
                1.25D,
                1.1D,
                1.25D,
                0.16D
        );
        serverLevel.sendParticles(
                ParticleTypes.DRIPPING_HONEY,
                fusionPoint.x,
                fusionPoint.y + 1.1D,
                fusionPoint.z,
                45,
                1.0D,
                1.0D,
                1.0D,
                0.08D
        );
        serverLevel.sendParticles(
                ParticleTypes.DAMAGE_INDICATOR,
                fusionPoint.x,
                fusionPoint.y + 0.9D,
                fusionPoint.z,
                36,
                0.9D,
                0.8D,
                0.9D,
                0.12D
        );
        serverLevel.sendParticles(
                ParticleTypes.POOF,
                fusionPoint.x,
                fusionPoint.y + 0.8D,
                fusionPoint.z,
                28,
                0.8D,
                0.7D,
                0.8D,
                0.08D
        );
    }
}
