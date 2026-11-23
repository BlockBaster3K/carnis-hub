# Шаг 9 — полный код

## BiomassRemainsBlock.java

```java
package com.carnis.mod.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

public final class BiomassRemainsBlock extends Block {
    private static final VoxelShape SHAPE = Block.box(0, 0, 0, 16, 3, 16);
    public BiomassRemainsBlock(BlockBehaviour.Properties properties) { super(properties); }
    @Override public VoxelShape getShape(BlockState state, BlockGetter world, BlockPos pos, CollisionContext context) { return SHAPE; }
    @Override public boolean canSurvive(BlockState state, LevelReader world, BlockPos pos) {
        return world.getBlockState(pos.below()).isFaceSturdy(world, pos.below(), Direction.UP);
    }
    @Override public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
            LevelAccessor world, BlockPos pos, BlockPos neighborPos) {
        return direction == Direction.DOWN && !state.canSurvive(world, pos) ? Blocks.AIR.defaultBlockState()
                : super.updateShape(state, direction, neighbor, world, pos, neighborPos);
    }
    @Override public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        if (!(entity instanceof LivingEntity living)) return;
        Vec3 velocity = living.getDeltaMovement();
        living.setDeltaMovement(velocity.x * 0.8D, velocity.y, velocity.z * 0.8D);
        if (!level.isClientSide && living.tickCount % 12 == 0 && velocity.horizontalDistanceSqr() > 0.0004D)
            level.playSound(null, pos, SoundEvents.SLIME_SQUISH, SoundSource.BLOCKS, 0.4F, 0.7F);
    }
}
```

## FleshBulbBlockEntity.java

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.block.FleshBulbBlock;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public final class FleshBulbBlockEntity extends BlockEntity {
    private int age;
    private int duration;
    public FleshBulbBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.FLESH_BULB.get(), pos, state); }
    @Override protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putInt("Age", age);
        tag.putInt("Duration", duration);
    }
    @Override public void load(CompoundTag tag) {
        super.load(tag);
        age = Math.max(0, tag.getInt("Age"));
        duration = tag.getInt("Duration");
    }
    public static void serverTick(Level world, BlockPos pos, BlockState state, FleshBulbBlockEntity bulb) {
        if (!(world instanceof ServerLevel level)) return;
        if (bulb.duration < 1200 || bulb.duration > 1800) bulb.duration = 1200 + level.random.nextInt(601);
        bulb.age++;
        bulb.setChanged();
        if (bulb.age >= bulb.duration) {
            level.playSound(null, pos, ModSounds.ACID_SPLASH.get(), SoundSource.BLOCKS, 1.5F, 0.65F);
            level.sendParticles(ModParticles.BIOMASS_SPARK.get(), pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D,
                    48, .35D, .35D, .35D, .16D);
            int count = 1 + level.random.nextInt(2);
            // Remove once before spawning; prevents a saved mature bulb spawning repeatedly.
            level.removeBlock(pos, false);
            for (int i = 0; i < count; i++) {
                ParasiticTendrilEntity tendril = ModEntities.PARASITIC_TENDRIL.get().create(level);
                if (tendril == null) continue;
                tendril.moveTo(pos.getX() + .5D + (i == 0 ? -0.18D : 0.18D), pos.getY(), pos.getZ() + .5D,
                        level.random.nextFloat() * 360.0F, 0.0F);
                tendril.setPersistenceRequired();
                level.addFreshEntity(tendril);
            }
            return;
        }
        int interval = 40 - (int)(30L * bulb.age / bulb.duration);
        int phase = bulb.age % interval;
        if (phase == 0) level.playSound(null, pos, ModSounds.PULSING_HEART_BEAT.get(), SoundSource.BLOCKS,
                0.55F, 0.75F + 0.25F * bulb.age / bulb.duration);
        boolean pulse = phase < 3;
        if (state.getValue(FleshBulbBlock.PULSING) != pulse)
            level.setBlock(pos, state.setValue(FleshBulbBlock.PULSING, pulse), 3);
    }
}
```

## BiomassMaggotEntity.java

```java
package com.carnis.mod.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.FleshBulbBlock;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.ForgeEventFactory;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.List;

public final class BiomassMaggotEntity extends Monster implements GeoEntity, HivemindLinkedMob {
    public static final String FED_COUNT = "carnis:fed_count";
    private static final String FLESH_TICKS = "carnis:flesh_ticks";
    private static final TagKey<Block> BURROWABLE = TagKey.create(Registries.BLOCK, new ResourceLocation(CarnisMod.MOD_ID, "burrowable"));
    private static final EntityDataAccessor<Integer> ACTION = SynchedEntityData.defineId(BiomassMaggotEntity.class, EntityDataSerializers.INT);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.biomass_maggot.idle");
    private static final RawAnimation CRAWL = RawAnimation.begin().thenLoop("animation.biomass_maggot.crawl");
    private static final RawAnimation EAT = RawAnimation.begin().thenLoop("animation.biomass_maggot.eat");
    private static final RawAnimation BURROW = RawAnimation.begin().thenLoop("animation.biomass_maggot.burrow");
    private static final List<BlockPos> SEARCH_OFFSETS = buildOffsets();
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public BiomassMaggotEntity(EntityType<? extends Monster> type, Level level) { super(type, level); }
    @Override protected void defineSynchedData() { super.defineSynchedData(); entityData.define(ACTION, 0); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 10.0D).add(Attributes.MOVEMENT_SPEED, 0.18D);
    }
    @Override protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new BurrowGoal());
        goalSelector.addGoal(2, new EatRemainsGoal());
        goalSelector.addGoal(3, new WaterAvoidingRandomStrollGoal(this, 0.8D));
    }
    @Override protected void customServerAiStep() {
        BlockState below = level().getBlockState(blockPosition().below());
        int previous = getPersistentData().getInt(FLESH_TICKS);
        int ticks = previous >= 1200 ? 1200 : below.is(ModBlocks.LIVING_FLESH.get()) || below.is(ModBlocks.OSSIFIED_FLESH.get())
                ? Math.min(1200, previous + 1) : 0;
        getPersistentData().putInt(FLESH_TICKS, ticks);
        super.customServerAiStep();
    }
    private boolean readyToBurrow() { return getPersistentData().getInt(FED_COUNT) >= 2 || getPersistentData().getInt(FLESH_TICKS) >= 1200; }
    private static boolean isSafeBurrowMaterial(BlockState state) {
        return state.is(ModBlocks.LIVING_FLESH.get()) || state.is(ModBlocks.OSSIFIED_FLESH.get())
                || state.is(net.minecraft.world.level.block.Blocks.DIRT)
                || state.is(net.minecraft.world.level.block.Blocks.GRASS_BLOCK)
                || state.is(net.minecraft.world.level.block.Blocks.PODZOL)
                || state.is(net.minecraft.world.level.block.Blocks.MYCELIUM)
                || state.is(net.minecraft.world.level.block.Blocks.MUD)
                || state.is(net.minecraft.world.level.block.Blocks.SAND)
                || state.is(net.minecraft.world.level.block.Blocks.GRAVEL)
                || state.is(net.minecraft.world.level.block.Blocks.MOSS_BLOCK);
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "locomotion", 2, state -> state.setAndContinue(
                entityData.get(ACTION) == 1 ? EAT : entityData.get(ACTION) == 2 ? BURROW : state.isMoving() ? CRAWL : IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }

    // Precomputed offsets only; each search examines at most 256 loaded positions per attempt.
    private static List<BlockPos> buildOffsets() {
        List<BlockPos> offsets = new ArrayList<>();
        for (int x = -16; x <= 16; x++) for (int y = -16; y <= 16; y++) for (int z = -16; z <= 16; z++)
            if (x*x + y*y + z*z <= 256) offsets.add(new BlockPos(x, y, z));
        offsets.sort(Comparator.comparingInt(p -> p.getX()*p.getX() + p.getY()*p.getY() + p.getZ()*p.getZ()));
        return List.copyOf(offsets);
    }
    private abstract class SearchGoal extends Goal {
        BlockPos target;
        BlockPos anchor;
        int cursor;
        int nextSearch;
        int elapsed;
        SearchGoal() { setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK)); }
        abstract boolean matches(ServerLevel level, BlockPos pos);
        abstract boolean allowed();
        @Override public boolean canUse() {
            if (!(level() instanceof ServerLevel server) || !allowed() || tickCount < nextSearch
                    || !ForgeEventFactory.getMobGriefingEvent(server, BiomassMaggotEntity.this)) return false;
            nextSearch = tickCount + 5;
            if (anchor == null || anchor.distSqr(blockPosition()) > 4) { anchor = blockPosition(); cursor = 0; }
            int end = Math.min(cursor + 256, SEARCH_OFFSETS.size());
            while (cursor < end) {
                BlockPos pos = anchor.offset(SEARCH_OFFSETS.get(cursor++));
                if (!server.isOutsideBuildHeight(pos) && server.hasChunkAt(pos) && matches(server, pos)) { target = pos; return true; }
            }
            if (cursor >= SEARCH_OFFSETS.size()) { cursor = 0; anchor = blockPosition(); }
            return false;
        }
        @Override public boolean canContinueToUse() {
            return target != null && elapsed < 400 && level() instanceof ServerLevel server
                    && server.hasChunkAt(target) && allowed() && matches(server, target)
                    && ForgeEventFactory.getMobGriefingEvent(server, BiomassMaggotEntity.this);
        }
        @Override public void start() { elapsed = 0; }
        @Override public void stop() { getNavigation().stop(); entityData.set(ACTION, 0); target = null; anchor = null; cursor = 0; }
        @Override public boolean requiresUpdateEveryTick() { return true; }
        boolean approach() {
            if (distanceToSqr(target.getX() + .5D, target.getY(), target.getZ() + .5D) <= 1.7D) {
                getNavigation().stop(); return true;
            }
            if (elapsed % 10 == 0) getNavigation().moveTo(target.getX() + .5D, target.getY(), target.getZ() + .5D, 0.8D);
            return false;
        }
    }
    private final class EatRemainsGoal extends SearchGoal {
        private int chewing;
        @Override boolean allowed() { return !readyToBurrow(); }
        @Override boolean matches(ServerLevel level, BlockPos pos) { return level.getBlockState(pos).is(ModBlocks.BIOMASS_REMAINS.get()); }
        @Override public void start() { super.start(); chewing = 0; }
        @Override public void tick() {
            elapsed++;
            if (!approach()) { chewing = 0; entityData.set(ACTION, 0); return; }
            entityData.set(ACTION, 1);
            if (++chewing % 20 == 0) playSound(SoundEvents.GENERIC_EAT, 0.8F, 0.65F);
            if (chewing >= 70 && level() instanceof ServerLevel server && matches(server, target)) {
                if (server.removeBlock(target, false)) {
                    getPersistentData().putInt(FED_COUNT, getPersistentData().getInt(FED_COUNT) + 1);
                    server.playSound(null, target, SoundEvents.GENERIC_EAT, SoundSource.HOSTILE, 1.0F, 0.7F);
                }
                target = null;
            }
        }
    }
    private final class BurrowGoal extends SearchGoal {
        private int burrowTicks;
        @Override boolean allowed() { return readyToBurrow(); }
        @Override boolean matches(ServerLevel level, BlockPos pos) {
            BlockPos ground = pos.below();
            if (!level.hasChunkAt(ground) || level.isOutsideBuildHeight(ground) || !level.isEmptyBlock(pos)) return false;
            BlockState floor = level.getBlockState(ground);
            BlockState bulb = ModBlocks.FLESH_BULB.get().defaultBlockState().setValue(FleshBulbBlock.HANGING, false);
            return floor.is(BURROWABLE) && isSafeBurrowMaterial(floor)
                    && floor.isFaceSturdy(level, ground, Direction.UP) && bulb.canSurvive(level, pos);
        }
        @Override public void start() { super.start(); burrowTicks = 0; }
        @Override public void tick() {
            elapsed++;
            if (!approach()) { burrowTicks = 0; entityData.set(ACTION, 0); return; }
            entityData.set(ACTION, 2);
            if (level() instanceof ServerLevel server && ++burrowTicks % 5 == 0) {
                server.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, server.getBlockState(target.below())),
                        getX(), getY() + 0.1D, getZ(), 8, .15D, .05D, .15D, .03D);
                server.sendParticles(ModParticles.BIOMASS_SPARK.get(), getX(), getY() + .1D, getZ(), 3, .1D, .05D, .1D, .02D);
            }
            if (burrowTicks >= 50 && level() instanceof ServerLevel server && matches(server, target)) {
                BlockState bulb = ModBlocks.FLESH_BULB.get().defaultBlockState().setValue(FleshBulbBlock.HANGING, false);
                if (server.setBlockAndUpdate(target, bulb)) discard();
                target = null;
            }
        }
    }
}
```

## FleshBulbBlock.java

```java
package com.carnis.mod.block;

import com.carnis.mod.block.entity.FleshBulbBlockEntity;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import javax.annotation.Nullable;

public final class FleshBulbBlock extends BaseEntityBlock {
    public static final BooleanProperty HANGING = BooleanProperty.create("hanging");
    public static final BooleanProperty PULSING = BooleanProperty.create("pulsing");
    private static final VoxelShape HANGING_SHAPE = Block.box(3, 3, 3, 13, 16, 13);
    private static final VoxelShape FLOOR_SHAPE = Block.box(2, 0, 3, 14, 14, 13);
    public FleshBulbBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(HANGING, true).setValue(PULSING, false));
    }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) { builder.add(HANGING, PULSING); }
    @Override public RenderShape getRenderShape(BlockState state) { return RenderShape.MODEL; }
    @Nullable @Override public BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new FleshBulbBlockEntity(pos, state); }
    @Nullable @Override public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return level.isClientSide ? null : createTickerHelper(type, ModBlockEntities.FLESH_BULB.get(), FleshBulbBlockEntity::serverTick);
    }
    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return state.getValue(HANGING) ? HANGING_SHAPE : FLOOR_SHAPE;
    }
    @Override public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        Direction direction = state.getValue(HANGING) ? Direction.UP : Direction.DOWN;
        BlockPos support = pos.relative(direction);
        return level.getBlockState(support).isFaceSturdy(level, support, direction.getOpposite());
    }
    @Nullable @Override public BlockState getStateForPlacement(BlockPlaceContext context) {
        boolean preferHanging = context.getClickedFace() == Direction.DOWN;
        BlockState chosen = defaultBlockState().setValue(HANGING, preferHanging);
        if (chosen.canSurvive(context.getLevel(), context.getClickedPos())) return chosen;
        chosen = chosen.setValue(HANGING, !preferHanging);
        return chosen.canSurvive(context.getLevel(), context.getClickedPos()) ? chosen : null;
    }
    @Override public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
            LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        Direction support = state.getValue(HANGING) ? Direction.UP : Direction.DOWN;
        return direction == support && !state.canSurvive(level, pos) ? Blocks.AIR.defaultBlockState()
                : super.updateShape(state, direction, neighbor, level, pos, neighborPos);
    }
    @Override public void onProjectileHit(Level level, BlockState state, BlockHitResult hit, Projectile projectile) {
        if (!level.isClientSide && projectile.mayInteract(level, hit.getBlockPos())) level.destroyBlock(hit.getBlockPos(), true, projectile);
    }
    @Override public void onRemove(BlockState state, Level level, BlockPos pos, BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && !moving && state.getValue(HANGING) && level instanceof ServerLevel server) {
            AABB area = new AABB(pos.getX() - 2, pos.getY() - 8, pos.getZ() - 2, pos.getX() + 3, pos.getY(), pos.getZ() + 3);
            for (Player player : server.getEntitiesOfClass(Player.class, area,
                    p -> p.isAlive() && !p.isSpectator() && p.getY() < pos.getY())) {
                player.hurt(server.damageSources().magic(), 4.0F);
                PlayerInfectionApi.addExposure(player, 10.0F);
            }
            for (int y = 0; y < 8; y++) server.sendParticles(ParticleTypes.CRIMSON_SPORE,
                    pos.getX() + .5, pos.getY() - y + .3, pos.getZ() + .5, 5, 1.2, .15, 1.2, .02);
        }
        super.onRemove(state, level, pos, next, moving);
    }
}
```

## RemainsEvents.java

```java
package com.carnis.mod.ecology;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.AssimilatingMob;
import com.carnis.mod.entity.BiomassMaggotEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.event.IncubationEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class RemainsEvents {
    private RemainsEvents() { }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onDeath(LivingDeathEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof Mob victim)
                || !(victim.level() instanceof ServerLevel level)) return;
        Entity killer = event.getSource().getEntity();
        boolean hiveKill = killer instanceof HivemindLinkedMob || killer instanceof AssimilatingMob;
        boolean decomposition = victim.getPersistentData().getInt(InfectionHandler.STAGE) == 4
                && IncubationEvents.isEligible(victim) && !IncubationEvents.isHostileHost(victim);
        if ((!hiveKill && !decomposition) || !ForgeEventFactory.getMobGriefingEvent(level, victim)) return;
        if (victim.getPersistentData().getBoolean("carnis:remains_created")) return;
        BlockPos base = victim.blockPosition();
        BlockPos placed = null;
        BlockState remains = ModBlocks.BIOMASS_REMAINS.get().defaultBlockState();
        for (int dy : new int[]{0, -1, 1}) {
            BlockPos pos = base.offset(0, dy, 0);
            if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos) || !level.hasChunkAt(pos.below())) continue;
            if (level.isEmptyBlock(pos) && remains.canSurvive(level, pos) && level.setBlockAndUpdate(pos, remains)) {
                placed = pos;
                break;
            }
        }
        if (placed == null) return;
        victim.getPersistentData().putBoolean("carnis:remains_created", true);
        if (!(victim instanceof Enemy)) {
            int count = 2 + level.random.nextInt(2);
            for (int i = 0; i < count; i++) {
                BiomassMaggotEntity maggot = ModEntities.BIOMASS_MAGGOT.get().create(level);
                if (maggot == null) continue;
                double angle = i * Math.PI * 2.0D / count;
                maggot.moveTo(placed.getX() + .5D + Math.cos(angle) * .6D, placed.getY(),
                        placed.getZ() + .5D + Math.sin(angle) * .6D, level.random.nextFloat() * 360F, 0);
                if (level.noCollision(maggot)) {
                    maggot.setPersistenceRequired();
                    level.addFreshEntity(maggot);
                }
            }
        }
    }
}
```

