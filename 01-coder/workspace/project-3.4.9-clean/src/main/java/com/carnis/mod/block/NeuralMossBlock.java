package com.carnis.mod.block;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.HiveEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.FluidTags;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.CarpetBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/** A floor carpet: unlike a multiface block it can only grow on upward-facing supports. */
public final class NeuralMossBlock extends CarpetBlock {
    public static final TagKey<EntityType<?>> HIVE_MEMBERS = TagKey.create(Registries.ENTITY_TYPE,
            new ResourceLocation(CarnisMod.MOD_ID, "hive_members"));
    private static final String LAST_SLOW_TICK = "carnis:neural_moss_slow_tick";
    public NeuralMossBlock(BlockBehaviour.Properties properties) { super(properties); }

    @Override public boolean canSurvive(BlockState state, net.minecraft.world.level.LevelReader level, BlockPos pos) {
        BlockPos below = pos.below();
        return level.getBlockState(below).isFaceSturdy(level, below, Direction.UP);
    }

    @Override public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (random.nextFloat() >= .15F || !hasSuitableEnvironment(level, pos)) return;
        Direction direction = Direction.Plane.HORIZONTAL.getRandomDirection(random);
        BlockPos target = pos.relative(direction).offset(0, random.nextInt(3) - 1, 0);
        if (!level.hasChunkAt(target) || !level.hasChunkAt(target.below()) || level.isOutsideBuildHeight(target)) return;
        BlockState old = level.getBlockState(target);
        if (!old.isAir() || !old.getFluidState().isEmpty()) return;
        BlockState moss = defaultBlockState();
        if (moss.canSurvive(level, target)) level.setBlockAndUpdate(target, moss);
    }

    private static boolean hasSuitableEnvironment(ServerLevel level, BlockPos pos) {
        for (Direction direction : Direction.values()) {
            BlockPos neighbor = pos.relative(direction);
            if (!level.hasChunkAt(neighbor) || level.isOutsideBuildHeight(neighbor)) continue;
            BlockState state = level.getBlockState(neighbor);
            if (state.getFluidState().is(FluidTags.WATER) || state.is(ModBlocks.LIVING_FLESH.get())
                    || state.is(ModBlocks.OSSIFIED_FLESH.get()) || state.is(ModBlocks.FIREPROOF_FLESH.get())
                    || state.is(ModBlocks.FLESH_VEINS.get())) return true;
        }
        return false;
    }

    public static boolean isHive(Entity entity) {
        return entity instanceof HiveEntity || entity instanceof HivemindLinkedMob || entity.getType().is(HIVE_MEMBERS);
    }
    private static boolean protectedPlayer(Entity entity) {
        if (!(entity instanceof Player player)) return false;
        return player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.NEURO_RESONATOR_HELMET.get())
                && player.getItemBySlot(EquipmentSlot.CHEST).is(ModItems.NEURO_RESONATOR_CHESTPLATE.get())
                && player.getItemBySlot(EquipmentSlot.LEGS).is(ModItems.NEURO_RESONATOR_LEGGINGS.get())
                && player.getItemBySlot(EquipmentSlot.FEET).is(ModItems.NEURO_RESONATOR_BOOTS.get());
    }
    private static void slow(Level level, Entity entity) {
        if (!(entity instanceof LivingEntity living) || !living.isAlive() || living.isSpectator()
                || isHive(entity) || protectedPlayer(entity)) return;
        long now = level.getGameTime();
        var data = entity.getPersistentData();
        if (data.contains(LAST_SLOW_TICK) && data.getLong(LAST_SLOW_TICK) == now) return;
        data.putLong(LAST_SLOW_TICK, now);
        Vec3 velocity = entity.getDeltaMovement();
        entity.setDeltaMovement(velocity.x * .8D, velocity.y, velocity.z * .8D);
    }
    @Override public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        super.stepOn(level, pos, state, entity);
        slow(level, entity);
    }
    @Override public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        slow(level, entity);
    }
    @Override public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(12) != 0) return;
        double x = pos.getX() + random.nextDouble(), z = pos.getZ() + random.nextDouble();
        level.addParticle(random.nextInt(4) == 0 ? ModParticles.BIOMASS_SPARK.get() : ParticleTypes.CRIMSON_SPORE,
                x, pos.getY() + .1D, z, 0, .012D, 0);
    }
}
