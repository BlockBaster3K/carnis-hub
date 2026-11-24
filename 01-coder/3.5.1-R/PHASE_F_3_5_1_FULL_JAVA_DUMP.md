# Carnis 3.5.1 — полный Java dump

> Дамп построен из актуального чистого дерева: 228 Java-файла, один заголовок на файл; дублей и удалённых секций нет.

## `src/main/java/com/carnis/mod/CarnisMod.java`

```java
package com.carnis.mod;

import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModCreativeTabs;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.network.ModMessages;
import com.mojang.logging.LogUtils;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.server.ServerStartingEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;
import software.bernie.geckolib.GeckoLib;

@Mod(CarnisMod.MOD_ID)
public final class CarnisMod {
    public static final String MOD_ID = "carnis";
    public static final Logger LOGGER = LogUtils.getLogger();

    public CarnisMod() {
        GeckoLib.initialize();

        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();

        com.carnis.mod.init.ModEffects.register(modEventBus);
        com.carnis.mod.init.ModFluids.register(modEventBus);
        ModBlocks.register(modEventBus);
        ModBlockEntities.register(modEventBus);
        ModEntities.register(modEventBus);
        com.carnis.mod.init.ModFeatures.register(modEventBus);
        ModItems.register(modEventBus);
        ModCreativeTabs.register(modEventBus);
        ModSounds.register(modEventBus);
        com.carnis.mod.init.ModParticles.register(modEventBus);

        modEventBus.addListener(this::onCommonSetup);

        ModLoadingContext.get().registerConfig(
                ModConfig.Type.SERVER,
                CarnisConfig.SERVER_SPEC,
                "carnis-server.toml"
        );
        ModLoadingContext.get().registerConfig(
                ModConfig.Type.CLIENT,
                CarnisConfig.CLIENT_SPEC,
                "carnis-client.toml"
        );

        MinecraftForge.EVENT_BUS.register(this);
    }

    private void onCommonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(ModMessages::register);
        LOGGER.info("Initializing {} common systems", MOD_ID);
    }

    @SubscribeEvent
    public void onServerStarting(ServerStartingEvent event) {
        LOGGER.info("{} server systems are ready", MOD_ID);
    }
}
```

## `src/main/java/com/carnis/mod/block/BiomassRemainsBlock.java`

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
        if (!(living instanceof net.minecraft.world.entity.player.Player player)
                || !com.carnis.mod.event.NeuroArmorEventHandler.hasSymbioticPair(player))
            living.setDeltaMovement(velocity.x * 0.8D, velocity.y, velocity.z * 0.8D);
        if (!level.isClientSide && living.tickCount % 12 == 0 && velocity.horizontalDistanceSqr() > 0.0004D)
            level.playSound(null, pos, SoundEvents.SLIME_SQUISH, SoundSource.BLOCKS, 0.4F, 1.0F);
    }
}
```

## `src/main/java/com/carnis/mod/block/CreepingTendrilsBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import javax.annotation.Nullable;

public final class CreepingTendrilsBlock extends LadderBlock {
    public CreepingTendrilsBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientBlockExtensions> consumer) {
        consumer.accept(new net.minecraftforge.client.extensions.common.IClientBlockExtensions() {
            @Override public boolean addDestroyEffects(BlockState state, net.minecraft.world.level.Level level,
                    BlockPos pos, net.minecraft.client.particle.ParticleEngine manager) {
                var particles = new net.minecraft.core.particles.BlockParticleOption(net.minecraft.core.particles.ParticleTypes.BLOCK,
                        ModBlocks.LIVING_FLESH.get().defaultBlockState());
                for (int i = 0; i < 24; i++) {
                    double x = level.random.nextDouble(), y = level.random.nextDouble(), z = level.random.nextDouble();
                    level.addParticle(particles, pos.getX() + x, pos.getY() + y, pos.getZ() + z,
                            (x - .5D) * .15D, (y - .5D) * .15D, (z - .5D) * .15D);
                }
                return true;
            }
        });
    }

    @Override
    public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        BlockState support = level.getBlockState(pos.relative(state.getValue(FACING).getOpposite()));
        return (support.is(ModBlocks.LIVING_FLESH.get()) || support.is(ModBlocks.OSSIFIED_FLESH.get())
                || support.is(ModBlocks.FIREPROOF_FLESH.get())) && super.canSurvive(state, level, pos);
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState state = super.getStateForPlacement(context);
        return state != null && canSurvive(state, context.getLevel(), context.getClickedPos()) ? state : null;
    }
}
```

## `src/main/java/com/carnis/mod/block/FleshBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.world.infection.VeinMutationEngine;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class FleshBlock extends Block {
    @Override public void onPlace(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState old, boolean moving) {
        super.onPlace(state, level, pos, old, moving);
        if (!old.is(state.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
    }
    @Override public void onRemove(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
        super.onRemove(state, level, pos, next, moving);
    }
    public FleshBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public boolean isFlammable(BlockState state, BlockGetter level, BlockPos pos, Direction face) {
        return state.is(ModBlocks.LIVING_FLESH.get());
    }

    @Override
    public int getFireSpreadSpeed(BlockState state, BlockGetter level, BlockPos pos, Direction face) {
        return state.is(ModBlocks.LIVING_FLESH.get()) ? 30 : 0;
    }

    @Override
    public int getFlammability(BlockState state, BlockGetter level, BlockPos pos, Direction face) {
        return state.is(ModBlocks.LIVING_FLESH.get()) ? 60 : 0;
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        com.carnis.mod.world.HiveNetwork.observe(level, pos, state, true);
        if ((state.is(ModBlocks.LIVING_FLESH.get()) || state.is(ModBlocks.OSSIFIED_FLESH.get()))
                && isExposedToFireOrLava(level, pos) && random.nextFloat() < 0.35F) {
            FleshIncineration.burn(level, pos, state);
            return;
        }
        if (state.is(ModBlocks.LIVING_FLESH.get()) && random.nextFloat() < 0.05F) {
            BlockPos above = pos.above();
            if (!level.isOutsideBuildHeight(above) && level.getBlockState(above).isAir()) {
                Block flora = switch (random.nextInt(3)) {
                    case 0 -> ModBlocks.SPORE_SPROUT.get();
                    case 1 -> ModBlocks.PUSTULE_CLUSTER.get();
                    default -> ModBlocks.NEURAL_MOSS.get();
                };
                BlockState plant = flora.defaultBlockState();
                if (plant.canSurvive(level, above)) level.setBlockAndUpdate(above, plant);
            }
        }
        if (state.is(ModBlocks.LIVING_FLESH.get())) VeinMutationEngine.tickFlesh(level, pos, random);
        if (state.is(ModBlocks.LIVING_FLESH.get()) && random.nextInt(12) == 0)
            com.carnis.mod.ecology.MaggotForaging.onFleshRandomTick(level, pos);
    }

    private static boolean isExposedToFireOrLava(ServerLevel level, BlockPos pos) {
        for (Direction direction : Direction.values()) {
            BlockPos adjacent = pos.relative(direction);
            if (!level.isOutsideBuildHeight(adjacent) && level.hasChunkAt(adjacent)
                    && (level.getBlockState(adjacent).is(BlockTags.FIRE)
                    || level.getFluidState(adjacent).is(FluidTags.LAVA))) return true;
        }
        return false;
    }
}
```

## `src/main/java/com/carnis/mod/block/FleshBulbBlock.java`

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

## `src/main/java/com/carnis/mod/block/FleshIncineration.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.state.BlockState;

public final class FleshIncineration {
    private FleshIncineration() { }

    public static void burn(ServerLevel level, BlockPos pos, BlockState state) {
        tryBurn(level, pos, state);
    }

    /** Returns false if the supplied state is not burnable or replacement fails. */
    public static boolean tryBurn(ServerLevel level, BlockPos pos, BlockState state) {
        if (!state.is(ModBlocks.LIVING_FLESH.get()) && !state.is(ModBlocks.OSSIFIED_FLESH.get())) return false;
        if (!level.getBlockState(pos).equals(state)) return false;
        if (!level.setBlockAndUpdate(pos, ModBlocks.CHARRED_FLESH.get().defaultBlockState())) return false;
        CarnisWorldData data = CarnisWorldData.get(level);
        data.addAdaptation(CarnisWorldData.AdaptationType.FIRE, 5L);
        if (!com.carnis.mod.world.HiveNetwork.shielded(level, pos))
            data.extendChunkShock(new ChunkPos(pos), level.getGameTime(), 20L);
        ModMessages.sendToPlayersInLevel(level);
        level.sendParticles(ParticleTypes.SMOKE, pos.getX() + 0.5D, pos.getY() + 0.5D,
                pos.getZ() + 0.5D, 16, 0.35D, 0.35D, 0.35D, 0.02D);
        level.sendParticles(ParticleTypes.FLAME, pos.getX() + 0.5D, pos.getY() + 0.5D,
                pos.getZ() + 0.5D, 8, 0.3D, 0.3D, 0.3D, 0.02D);
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/block/FleshVeinsBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.world.infection.VeinMutationEngine;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.MultifaceBlock;
import net.minecraft.world.level.block.MultifaceSpreader;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

public final class FleshVeinsBlock extends MultifaceBlock {
    private static final VoxelShape[] SHAPES_BY_FACES = createShapes();
    private final MultifaceSpreader spreader = new MultifaceSpreader(this);

    private static VoxelShape[] createShapes() {
        VoxelShape[] perFace = new VoxelShape[Direction.values().length];
        for (Direction direction : Direction.values()) {
            perFace[direction.ordinal()] = faceShape(direction);
        }

        VoxelShape[] result = new VoxelShape[1 << Direction.values().length];
        for (int mask = 0; mask < result.length; mask++) {
            VoxelShape combined = Shapes.empty();
            for (Direction direction : Direction.values()) {
                if ((mask & (1 << direction.ordinal())) != 0) {
                    combined = Shapes.or(combined, perFace[direction.ordinal()]);
                }
            }
            result[mask] = combined;
        }
        return result;
    }

    private static VoxelShape faceShape(Direction face) {
        return switch (face) {
            case DOWN -> Block.box(0.0D, 0.0D, 0.0D, 16.0D, 1.0D, 16.0D);
            case UP -> Block.box(0.0D, 15.0D, 0.0D, 16.0D, 16.0D, 16.0D);
            case NORTH -> Block.box(0.0D, 0.0D, 0.0D, 16.0D, 16.0D, 1.0D);
            case SOUTH -> Block.box(0.0D, 0.0D, 15.0D, 16.0D, 16.0D, 16.0D);
            case WEST -> Block.box(0.0D, 0.0D, 0.0D, 1.0D, 16.0D, 16.0D);
            case EAST -> Block.box(15.0D, 0.0D, 0.0D, 16.0D, 16.0D, 16.0D);
        };
    }

    private static boolean hasSupport(BlockGetter level, BlockPos pos, Direction face) {
        BlockPos supportPos = pos.relative(face);
        BlockState support = level.getBlockState(supportPos);
        return !support.isAir() && (support.isFaceSturdy(level, supportPos, face.getOpposite())
                || support.isSolidRender(level, supportPos));
    }

    private static VoxelShape outline(BlockState state, BlockGetter level, BlockPos pos) {
        int mask = 0;
        for (Direction direction : Direction.values()) {
            if (MultifaceBlock.hasFace(state, direction) && hasSupport(level, pos, direction)) {
                mask |= 1 << direction.ordinal();
            }
        }
        return SHAPES_BY_FACES[mask];
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return outline(state, level, pos);
    }

    @Override
    public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return Shapes.empty();
    }

    @Override
    public VoxelShape getVisualShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return outline(state, level, pos);
    }

    @Override
    public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        for (Direction face : Direction.values()) {
            if (MultifaceBlock.hasFace(state, face) && hasSupport(level, pos, face)) return true;
        }
        return false;
    }

    @Override
    public void onPlace(BlockState state, net.minecraft.world.level.Level level,
                        BlockPos pos, BlockState old, boolean moving) {
        super.onPlace(state, level, pos, old, moving);
        if (!old.is(state.getBlock()) && level instanceof ServerLevel server) {
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
        }
    }

    @Override
    public void onRemove(BlockState state, net.minecraft.world.level.Level level,
                         BlockPos pos, BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof ServerLevel server) {
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
        }
        super.onRemove(state, level, pos, next, moving);
    }

    public FleshVeinsBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public MultifaceSpreader getSpreader() {
        return spreader;
    }

    @Override
    public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
                                  LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        BlockState updated = super.updateShape(state, direction, neighbor, level, pos, neighborPos);
        if (!updated.is(this)) return updated;

        for (Direction face : Direction.values()) {
            if (MultifaceBlock.hasFace(updated, face) && !hasSupport(level, pos, face)) {
                updated = updated.setValue(MultifaceBlock.getFaceProperty(face), false);
            }
        }

        for (Direction face : Direction.values()) {
            if (MultifaceBlock.hasFace(updated, face)) return updated;
        }
        return Blocks.AIR.defaultBlockState();
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        com.carnis.mod.world.HiveNetwork.observe(level, pos, state, true);
        VeinMutationEngine.tickVein(level, pos, state, random);
    }
}
```

## `src/main/java/com/carnis/mod/block/HiveEyeBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.block.entity.HiveEyeBlockEntity;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;

public final class HiveEyeBlock extends BaseEntityBlock {
    @Override public void onPlace(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState old, boolean moving) {
        super.onPlace(state, level, pos, old, moving);
        if (!old.is(state.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
    }
    @Override public void onRemove(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
        super.onRemove(state, level, pos, next, moving);
    }
    public HiveEyeBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.ENTITYBLOCK_ANIMATED;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return ModBlockEntities.HIVE_EYE.get().create(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
            Level level,
            BlockState state,
            BlockEntityType<T> blockEntityType
    ) {
        if (level.isClientSide()) {
            return createTickerHelper(blockEntityType, ModBlockEntities.HIVE_EYE.get(), HiveEyeBlockEntity::clientTick);
        }

        return createTickerHelper(
                blockEntityType,
                ModBlockEntities.HIVE_EYE.get(),
                HiveEyeBlockEntity::serverTick
        );
    }
}
```

## `src/main/java/com/carnis/mod/block/HiveMembraneBlock.java`

```java
package com.carnis.mod.block;

import net.minecraft.world.level.block.Block;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class HiveMembraneBlock extends Block {
    public HiveMembraneBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public int getFlammability(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return 24;
    }

    @Override
    public int getFireSpreadSpeed(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return 8;
    }
}
```

## `src/main/java/com/carnis/mod/block/IncubationCystBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.sounds.SoundSource;
import com.carnis.mod.event.InfectionHandler;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

public final class IncubationCystBlock extends Block {
    private static final int UPDATE_INTERVAL = 20;

    public IncubationCystBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean moving) {
        super.onPlace(state, level, pos, oldState, moving);
        if (!level.isClientSide && !state.is(oldState.getBlock())) level.scheduleTick(pos, this, UPDATE_INTERVAL);
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (!level.getBlockState(pos).is(this)) return;
        AABB area = new AABB(pos).inflate(1.0D);
        double centerX = pos.getX() + 0.5D;
        double centerY = pos.getY() + 0.5D;
        double centerZ = pos.getZ() + 0.5D;
        for (LivingEntity target : level.getEntitiesOfClass(LivingEntity.class, area,
                entity -> entity.isAlive() && entity.distanceToSqr(centerX, centerY, centerZ) <= 1.0D
                        && !(entity instanceof HivemindLinkedMob) && !InfectionHandler.isInfected(entity))) {
            target.hurt(level.damageSources().magic(), 1.0F);
        }
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), pos.getX() + 0.5D, pos.getY() + 0.6D,
                pos.getZ() + 0.5D, 2, 0.25D, 0.2D, 0.25D, 0.01D);
        if (Math.floorMod(level.getGameTime(), 100L) == 0L) {
            level.playSound(null, pos, ModSounds.INCUBATION_CYST_AMBIENT.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        }
        level.scheduleTick(pos, this, UPDATE_INTERVAL);
    }

    @Override
    public void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moving) {
        if (!level.isClientSide && !moving && !state.is(newState.getBlock())) {
            level.playSound(null, pos, ModSounds.INCUBATION_CYST_RUPTURE.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        }
        super.onRemove(state, level, pos, newState, moving);
    }

    @Override
    public int getFlammability(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return 12;
    }

    @Override
    public int getFireSpreadSpeed(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return 4;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(5) == 0) {
            level.addParticle(random.nextBoolean() ? ParticleTypes.CRIMSON_SPORE : ModParticles.BIOMASS_SPARK.get(),
                    pos.getX() + random.nextDouble(), pos.getY() + 0.6D + random.nextDouble() * 0.3D,
                    pos.getZ() + random.nextDouble(), 0.0D, 0.01D, 0.0D);
        }
    }
}
```

## `src/main/java/com/carnis/mod/block/NervePillarBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.block.entity.NervePillarBlockEntity;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;

public final class NervePillarBlock extends net.minecraft.world.level.block.BaseEntityBlock {
    private static final net.minecraft.world.phys.shapes.VoxelShape SHAPE = box(3, 0, 3, 13, 16, 13);
    @Override public net.minecraft.world.phys.shapes.VoxelShape getShape(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos, net.minecraft.world.phys.shapes.CollisionContext context) { return SHAPE; }
    @Override public net.minecraft.world.phys.shapes.VoxelShape getCollisionShape(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos, net.minecraft.world.phys.shapes.CollisionContext context) { return SHAPE; }
    @Override public net.minecraft.world.level.block.RenderShape getRenderShape(BlockState state) { return net.minecraft.world.level.block.RenderShape.ENTITYBLOCK_ANIMATED; }
    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new NervePillarBlockEntity(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
            Level level,
            BlockState state,
            BlockEntityType<T> type
    ) {
        if (level.isClientSide) return null;
        return createTickerHelper(type, ModBlockEntities.NERVE_PILLAR.get(), NervePillarBlockEntity::serverTick);
    }
    @Override public void onRemove(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
        super.onRemove(state, level, pos, next, moving);
    }
    @Override public void randomTick(net.minecraft.world.level.block.state.BlockState state, net.minecraft.server.level.ServerLevel level,
            net.minecraft.core.BlockPos pos, net.minecraft.util.RandomSource random) {
        com.carnis.mod.world.HiveNetwork.observe(level, pos, state, true);
    }
    public NervePillarBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean moving) {
        super.onPlace(state, level, pos, oldState, moving);
        if (!oldState.is(state.getBlock()) && level instanceof ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
        if (!oldState.is(state.getBlock()) && level instanceof ServerLevel server
                && CarnisWorldData.get(server).halveRemainingShock(new ChunkPos(pos), server.getGameTime())) {
            ModMessages.sendToPlayersInLevel(server);
        }
    }

    @Override
    public void playerWillDestroy(
            Level level,
            BlockPos pos,
            BlockState state,
            net.minecraft.world.entity.player.Player player
    ) {
        if (level instanceof ServerLevel serverLevel) {
            CarnisWorldData.get(serverLevel).shockSynapseArea(
                    new ChunkPos(pos),
                    serverLevel.getGameTime()
            );

            serverLevel.playSound(
                    null,
                    pos,
                    com.carnis.mod.init.ModSounds.SYNAPSE_RUPTURE.get(),
                    net.minecraft.sounds.SoundSource.BLOCKS,
                    1.0F,
                    1.0F
            );

            serverLevel.sendParticles(
                    ParticleTypes.ELECTRIC_SPARK,
                    pos.getX() + 0.5D,
                    pos.getY() + 0.8D,
                    pos.getZ() + 0.5D,
                    36,
                    0.55D,
                    0.8D,
                    0.55D,
                    0.08D
            );
            serverLevel.sendParticles(
                    ParticleTypes.POOF,
                    pos.getX() + 0.5D,
                    pos.getY() + 0.6D,
                    pos.getZ() + 0.5D,
                    18,
                    0.4D,
                    0.55D,
                    0.4D,
                    0.035D
            );
        }

        super.playerWillDestroy(level, pos, state, player);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(8) == 0) {
            level.addParticle(ParticleTypes.CRIMSON_SPORE, pos.getX() + random.nextDouble(),
                    pos.getY() + random.nextDouble(), pos.getZ() + random.nextDouble(), 0.0D, 0.02D, 0.0D);
        }
    }
}
```

## `src/main/java/com/carnis/mod/block/NeuralMossBlock.java`

```java
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
```

## `src/main/java/com/carnis/mod/block/PulsingHeartBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import javax.annotation.Nullable;

public final class PulsingHeartBlock extends BaseEntityBlock {
    private static final VoxelShape SHAPE = box(
            2.0D,
            0.0D,
            2.0D,
            14.0D,
            15.0D,
            14.0D
    );

    public PulsingHeartBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.ENTITYBLOCK_ANIMATED;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return ModBlockEntities.PULSING_HEART.get().create(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
            Level level,
            BlockState state,
            BlockEntityType<T> blockEntityType
    ) {
        if (level.isClientSide()) {
            return createTickerHelper(blockEntityType, ModBlockEntities.PULSING_HEART.get(),
                    com.carnis.mod.client.HeartAmbientTicker::tick);
        }

        return createTickerHelper(
                blockEntityType,
                ModBlockEntities.PULSING_HEART.get(),
                PulsingHeartBlockEntity::serverTick
        );
    }

    @Override
    public VoxelShape getShape(
            BlockState state,
            BlockGetter level,
            BlockPos pos,
            CollisionContext context
    ) {
        return SHAPE;
    }
}
```

## `src/main/java/com/carnis/mod/block/PurifierLampBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class PurifierLampBlock extends Block {
    private static final int UPDATE_INTERVAL = 20;

    public PurifierLampBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean moving) {
        super.onPlace(state, level, pos, oldState, moving);
        if (!level.isClientSide && !state.is(oldState.getBlock())) {
            level.playSound(null, pos, ModSounds.PURIFIER_LAMP_IGNITE.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
            level.scheduleTick(pos, this, UPDATE_INTERVAL);
        }
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (!level.getBlockState(pos).is(this)) return;
        if (Math.floorMod(level.getGameTime(), 80L) == 0L) {
            level.playSound(null, pos, ModSounds.PURIFIER_LOOP.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        }
        level.sendParticles(ModParticles.PURIFIER_FLAME.get(), pos.getX() + 0.5D, pos.getY() + 0.7D,
                pos.getZ() + 0.5D, 2, 0.15D, 0.2D, 0.15D, 0.01D);
        level.scheduleTick(pos, this, UPDATE_INTERVAL);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(3) == 0) {
            level.addParticle(ModParticles.PURIFIER_FLAME.get(), pos.getX() + 0.25D + random.nextDouble() * 0.5D,
                    pos.getY() + 0.7D, pos.getZ() + 0.25D + random.nextDouble() * 0.5D,
                    0.0D, 0.015D, 0.0D);
        }
    }
}
```

## `src/main/java/com/carnis/mod/block/PustuleClusterBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.block.entity.PustuleClusterBlockEntity;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
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
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import javax.annotation.Nullable;

public final class PustuleClusterBlock extends BaseEntityBlock {
    public static final IntegerProperty AGE = BlockStateProperties.AGE_3;
    public static final BooleanProperty BURST = BooleanProperty.create("burst");
    private static final float REMAINS_CONVERSION_CHANCE = 0.5F;
    private static final String PUSTULE_INFECTION_COOLDOWN = "carnis:pustule_cd";
    private static final VoxelShape SHAPE = Block.box(2, 0, 2, 14, 10, 14);
    private static final VoxelShape EMPTY_SHAPE = Block.box(2, 0, 2, 14, 3, 14);
    public PustuleClusterBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(AGE, 0).setValue(BURST, false));
    }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) { builder.add(AGE, BURST); }
    @Override public RenderShape getRenderShape(BlockState state) { return RenderShape.ENTITYBLOCK_ANIMATED; }
    @Nullable @Override public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return ModBlockEntities.PUSTULE_CLUSTER.get().create(pos, state);
    }
    @Nullable @Override public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
            Level level, BlockState state, BlockEntityType<T> type) {
        return level.isClientSide ? null
                : createTickerHelper(type, ModBlockEntities.PUSTULE_CLUSTER.get(), PustuleClusterBlockEntity::serverTick);
    }
    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return state.getValue(BURST) ? EMPTY_SHAPE : SHAPE;
    }
    @Override public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return getShape(state, level, pos, context);
    }
    @Override public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        BlockPos below = pos.below();
        return level.getBlockState(below).isFaceSturdy(level, below, Direction.UP);
    }
    @Override public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor, LevelAccessor level,
                                            BlockPos pos, BlockPos neighborPos) {
        return direction == Direction.DOWN && !state.canSurvive(level, pos) ? Blocks.AIR.defaultBlockState()
                : super.updateShape(state, direction, neighbor, level, pos, neighborPos);
    }
    @Override public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (!state.getValue(BURST) && state.getValue(AGE) < 3 && random.nextInt(3) == 0)
            level.setBlock(pos, state.setValue(AGE, state.getValue(AGE) + 1), 3);
    }
    public static boolean ready(BlockState state) {
        return state.getBlock() instanceof PustuleClusterBlock && !state.getValue(BURST) && state.getValue(AGE) >= 2;
    }
    private static void contact(BlockState state, Level level, BlockPos pos, Entity entity) {
        if (!(level instanceof ServerLevel server) || !(entity instanceof LivingEntity living) || !living.isAlive()
                || living.isSpectator() || NeuralMossBlock.isHive(living) || NeuroArmorEventHandler.hasFullSet(living)) return;
        if (!state.getShape(level, pos, CollisionContext.empty()).bounds().intersects(entity.getBoundingBox())) return;
        if (living.getBoundingBox().minY > pos.getY() + 10.0D / 16.0D + .05D) return;
        burst(server, pos);
    }
    @Override public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        super.stepOn(level, pos, state, entity); contact(state, level, pos, entity);
    }
    @Override public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity); contact(state, level, pos, entity);
    }
    @Override public void onProjectileHit(Level level, BlockState state, BlockHitResult hit, Projectile projectile) {
        if (level instanceof ServerLevel server && projectile.mayInteract(level, hit.getBlockPos())) burst(server, hit.getBlockPos());
    }
    public static boolean burst(ServerLevel level, BlockPos pos) {
        BlockState current = level.getBlockState(pos);
        if (!ready(current)) return false;
        BlockState remains = ModBlocks.BIOMASS_REMAINS.get().defaultBlockState();
        BlockState after = level.random.nextFloat() < REMAINS_CONVERSION_CHANCE && remains.canSurvive(level, pos)
                ? remains : current.setValue(BURST, true);
        // Commit the inert state first to prevent re-entrant detonations.
        if (!level.setBlock(pos, after, 3)) return false;
        double x = pos.getX() + .5D, y = pos.getY() + .5D, z = pos.getZ() + .5D;
        level.playSound(null, pos, ModSounds.PUSTULE_BURST.get(), SoundSource.BLOCKS, 1F, 1.0F);
        level.sendParticles(ParticleTypes.SNEEZE, x, y, z, 45, .8, .55, .8, .12);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), x, y, z, 35, .8, .55, .8, .12);
        level.sendParticles(ParticleTypes.ENTITY_EFFECT, x, y, z, 25, .7, .5, .7, .06);
        for (LivingEntity living : level.getEntitiesOfClass(LivingEntity.class, new AABB(x - 3, y - 3, z - 3, x + 3, y + 3, z + 3),
                e -> e.isAlive() && !e.isSpectator()
                        && !NeuralMossBlock.isHive(e)
                        && !NeuroArmorEventHandler.hasFullSet(e)
                        && e.distanceToSqr(x, y, z) <= 9.0D)) {
            if (living instanceof Player player && player.isCreative()) continue;
            if (living instanceof Player player) {
                var data = player.getPersistentData();
                long gameTime = level.getGameTime();
                if (data.getLong(PUSTULE_INFECTION_COOLDOWN) > gameTime) continue;
                data.putLong(PUSTULE_INFECTION_COOLDOWN, gameTime + 20L);
            }
            if (!living.hurt(level.damageSources().magic(), 6F)) {
                if (living instanceof Player player && !player.isCreative()) {
                    PlayerInfectionApi.addInfection(player, 15F);
                }
                continue;
            }
            if (!living.isAlive()) continue;
            living.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 0));
            if (living instanceof Player player) PlayerInfectionApi.addInfection(player, 15F);
        }
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/block/SinewSpikesBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.init.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import javax.annotation.Nullable;

public final class SinewSpikesBlock extends Block {
    private static final VoxelShape SHAPE = Shapes.block();
    private static final String NEXT_HIT = "carnis:sinew_spikes_next_hit";
    private static final long HIT_COOLDOWN_TICKS = 10L;
    private static final float HIT_DAMAGE = 2.0F;
    public SinewSpikesBlock(BlockBehaviour.Properties properties) { super(properties); }
    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) { return SHAPE; }
    @Override public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) { return Shapes.empty(); }
    @Override public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        BlockPos below = pos.below();
        return level.getBlockState(below).isFaceSturdy(level, below, Direction.UP);
    }
    @Nullable @Override public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState state = defaultBlockState();
        return state.canSurvive(context.getLevel(), context.getClickedPos()) ? state : null;
    }
    @Override public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
                                            LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        if (direction == Direction.DOWN && !state.canSurvive(level, pos)) return Blocks.AIR.defaultBlockState();
        return super.updateShape(state, direction, neighbor, level, pos, neighborPos);
    }
    @Override public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        super.stepOn(level, pos, state, entity);
        hurtAtFeet(level, pos, entity);
    }
    @Override public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        hurtAtFeet(level, pos, entity);
    }
    private static void hurtAtFeet(Level level, BlockPos pos, Entity entity) {
        if (level.isClientSide || !(entity instanceof LivingEntity living) || !living.isAlive()
                || living.isSpectator() || NeuralMossBlock.isHive(living)) return;
        if (living instanceof Player player && player.getItemBySlot(EquipmentSlot.FEET).is(ModItems.NEURO_RESONATOR_BOOTS.get())) return;
        if (living.getBoundingBox().minY > pos.getY() + 7.0D / 16.0D + .05D
                || living.getBoundingBox().maxY < pos.getY()) return;
        long now = level.getGameTime();
        var data = living.getPersistentData();
        if (data.contains(NEXT_HIT) && data.getLong(NEXT_HIT) > now) return;
        // Shared on entity NBT: adjacent spike blocks cannot multiply hits.
        data.putLong(NEXT_HIT, now + HIT_COOLDOWN_TICKS);
        living.hurt(level.damageSources().generic(), HIT_DAMAGE);
        level.playSound(null, pos, SoundEvents.WOOL_PLACE, SoundSource.BLOCKS,
                0.6F, 1.0F);
        if (level instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(ParticleTypes.ITEM_SLIME,
                    living.getX(), living.getY() + 0.5D, living.getZ(),
                    5, 0.3D, 0.3D, 0.3D, 0.0D);
        }
    }
}
```

## `src/main/java/com/carnis/mod/block/SporeSproutBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.block.entity.SporeSproutBlockEntity;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModBlockTags;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.BushBlock;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import javax.annotation.Nullable;

public final class SporeSproutBlock extends BushBlock implements EntityBlock {
    public static final BooleanProperty CLOSED = BooleanProperty.create("closed");
    private static final int MIN_COOLDOWN_TICKS = 250;
    private static final int MAX_COOLDOWN_TICKS = 350;
    private static final VoxelShape SHAPE = Block.box(4, 0, 4, 12, 14, 12);

    public SporeSproutBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(CLOSED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<net.minecraft.world.level.block.Block, BlockState> builder) {
        builder.add(CLOSED);
    }

    @Override
    protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
        return state.is(ModBlockTags.INFECTIOUS_SURFACES) || super.mayPlaceOn(state, level, pos);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new SporeSproutBlockEntity(pos, state);
    }

    @Nullable
    @Override
    @SuppressWarnings("unchecked")
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
            Level level,
            BlockState state,
            BlockEntityType<T> blockEntityType
    ) {
        if (level.isClientSide || blockEntityType != ModBlockEntities.SPORE_SPROUT.get()) return null;
        return (BlockEntityTicker<T>) (BlockEntityTicker<SporeSproutBlockEntity>) SporeSproutBlockEntity::serverTick;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(5) == 0) {
            level.addParticle(ParticleTypes.CRIMSON_SPORE,
                    pos.getX() + random.nextDouble(), pos.getY() + .4D, pos.getZ() + random.nextDouble(), 0, .01D, 0);
        }
    }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        if (!(level instanceof ServerLevel server) || !(entity instanceof Player player) || !player.isAlive()
                || player.isSpectator() || NeuroArmorEventHandler.hasFullSet(player) || state.getValue(CLOSED)) return;
        if (!(server.getBlockEntity(pos) instanceof SporeSproutBlockEntity sprout)
                || sprout.getCooldownTicks() > 0) return;
        if (!server.setBlock(pos, state.setValue(CLOSED, true), 3)) return;

        sprout.startCooldown(MIN_COOLDOWN_TICKS + server.random.nextInt(MAX_COOLDOWN_TICKS - MIN_COOLDOWN_TICKS + 1));
        server.playSound(null, pos, ModSounds.ORGANIC_CREAK.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        server.sendParticles(ParticleTypes.SNEEZE, pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D,
                25, .35D, .35D, .35D, .06D);
        server.sendParticles(ModParticles.BIOMASS_SPARK.get(), pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D,
                10, .2D, .3D, .2D, .04D);
        player.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 80, 0));
        PlayerInfectionApi.addExposure(player, 5F);
    }
}
```

## `src/main/java/com/carnis/mod/block/StomachPoolBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.block.entity.StomachPoolBlockEntity;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.BlockPathTypes;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import javax.annotation.Nullable;

public final class StomachPoolBlock extends net.minecraft.world.level.block.BaseEntityBlock {
    private static final String POOL_DISSOLVING = "carnis:pool_dissolving";
    private static final String POOL_DISSOLVING_UNTIL = "carnis:pool_dissolving_until";
    private static final String POOL_BIOMASS_AWARDED = "carnis:pool_biomass_awarded";
    private static final int DISSOLVING_DURATION_TICKS = 100;
    @Override public void onPlace(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState old, boolean moving) {
        super.onPlace(state, level, pos, old, moving);
        if (!old.is(state.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, true);
    }
    @Override public void onRemove(net.minecraft.world.level.block.state.BlockState state, net.minecraft.world.level.Level level,
            net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState next, boolean moving) {
        if (!state.is(next.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel server)
            com.carnis.mod.world.HiveNetwork.observe(server, pos, state, false);
        super.onRemove(state, level, pos, next, moving);
    }
    @Override public void randomTick(net.minecraft.world.level.block.state.BlockState state, net.minecraft.server.level.ServerLevel level,
            net.minecraft.core.BlockPos pos, net.minecraft.util.RandomSource random) {
        com.carnis.mod.world.HiveNetwork.observe(level, pos, state, true);
    }
    public StomachPoolBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    private static final VoxelShape OUTLINE_SHAPE = Shapes.block();
    private static final VoxelShape COLLISION_SHAPE = Shapes.box(0.0D, 0.0D, 0.0D, 1.0D, 0.25D, 1.0D);

    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return OUTLINE_SHAPE;
    }

    @Override public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return COLLISION_SHAPE;
    }

    @Nullable
    @Override public BlockPathTypes getBlockPathType(BlockState state, BlockGetter level, BlockPos pos, @Nullable Mob mob) {
        return BlockPathTypes.WALKABLE;
    }
    @Override public net.minecraft.world.level.block.RenderShape getRenderShape(BlockState state) { return net.minecraft.world.level.block.RenderShape.MODEL; }
    @Override public net.minecraft.world.level.block.entity.BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new com.carnis.mod.block.entity.StomachPoolBlockEntity(pos, state); }
    @Override public <T extends net.minecraft.world.level.block.entity.BlockEntity> net.minecraft.world.level.block.entity.BlockEntityTicker<T> getTicker(Level level, BlockState state, net.minecraft.world.level.block.entity.BlockEntityType<T> type) {
        return createTickerHelper(type, com.carnis.mod.init.ModBlockEntities.STOMACH_POOL.get(), com.carnis.mod.block.entity.StomachPoolBlockEntity::tick);
    }
    private static void digest(ServerLevel level, BlockPos pos) {
        if (level.getBlockEntity(pos) instanceof com.carnis.mod.block.entity.StomachPoolBlockEntity pool) pool.markDigesting();
    }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        if (!(level instanceof ServerLevel server)) {
            return;
        }
        if (entity instanceof ItemEntity item && item.isAlive() && !item.getItem().isEmpty()) {
            ItemStack stack = item.getItem();
            FoodProperties food = stack.getFoodProperties(null);
            boolean flesh = stack.is(Items.ROTTEN_FLESH) || stack.is(ModItems.LIVING_FLESH.get())
                    || stack.is(ModItems.OSSIFIED_FLESH.get()) || stack.is(ModItems.FIREPROOF_FLESH.get())
                    || food != null && food.isMeat();
            long value = (long) stack.getCount() * (flesh ? 5L : 1L);
            digest(server, pos);
            item.discard();
            CarnisWorldData.get(server).addBiomassPoints(value);
            ModMessages.sendToPlayersInLevel(server);
            server.playSound(null, pos, SoundEvents.GENERIC_SPLASH, SoundSource.BLOCKS, 0.6F, 1.0F);
            server.sendParticles(ParticleTypes.BUBBLE_POP, item.getX(), item.getY(), item.getZ(),
                    8, 0.2D, 0.2D, 0.2D, 0.02D);
        } else if (entity instanceof LivingEntity living && living.tickCount % 20 == 0) {
            if (NeuralMossBlock.isHive(living)) return;
            var heart = com.carnis.mod.world.HiveNetwork.nearestHeart(server, pos, 32);
            boolean mob = living instanceof net.minecraft.world.entity.Mob;
            if (heart != null && mob) {
                living.getPersistentData().putBoolean(POOL_DISSOLVING, true);
                living.getPersistentData().putLong(POOL_DISSOLVING_UNTIL,
                        server.getGameTime() + DISSOLVING_DURATION_TICKS);
            }
            digest(server, pos);
            living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 0));
            living.hurt(server.damageSources().generic(), 1.0F);
            server.sendParticles(ParticleTypes.ITEM_SLIME, living.getX(), living.getY() + 0.1D, living.getZ(),
                    8, 0.2D, 0.1D, 0.2D, 0.02D);
            server.playSound(null, pos, com.carnis.mod.init.ModSounds.ACID_SPLASH.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
            if (heart != null && mob && living.isDeadOrDying()
                    && !living.getPersistentData().getBoolean(POOL_BIOMASS_AWARDED)) {
                living.getPersistentData().putBoolean(POOL_BIOMASS_AWARDED, true);
                long biomass = living instanceof net.minecraft.world.entity.animal.Cow ? 30L : 20L;
                heart.addBiomass(biomass);
            }
        }
    }
}
```

## `src/main/java/com/carnis/mod/block/SynapseNodeBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.AABB;

public final class SynapseNodeBlock extends Block {
    public static final IntegerProperty POWER = BlockStateProperties.POWER;
    private static final int SCAN_RADIUS = 8;
    private static final int ACTIVE_SIGNAL = 15;
    private static final int UPDATE_INTERVAL = 10;

    public SynapseNodeBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(defaultBlockState().setValue(POWER, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(POWER);
    }

    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean moving) {
        super.onPlace(state, level, pos, oldState, moving);
        if (!level.isClientSide && !state.is(oldState.getBlock())) {
            level.scheduleTick(pos, this, UPDATE_INTERVAL);
        }
    }

    @Override
    public void neighborChanged(BlockState state, Level level, BlockPos pos, Block block,
                                BlockPos fromPos, boolean moving) {
        super.neighborChanged(state, level, pos, block, fromPos, moving);
        if (!level.isClientSide) level.scheduleTick(pos, this, UPDATE_INTERVAL);
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (!level.getBlockState(pos).is(this)) return;
        double centerX = pos.getX() + 0.5D;
        double centerY = pos.getY() + 0.5D;
        double centerZ = pos.getZ() + 0.5D;
        double radiusSquared = SCAN_RADIUS * SCAN_RADIUS;
        int nearbyTargets = level.getEntitiesOfClass(LivingEntity.class, new AABB(pos).inflate(SCAN_RADIUS),
                entity -> isHiveTarget(entity)
                        && entity.distanceToSqr(centerX, centerY, centerZ) <= radiusSquared).size();
        int nextPower = Math.min(ACTIVE_SIGNAL, nearbyTargets);
        if (state.getValue(POWER) != nextPower) {
            level.setBlock(pos, state.setValue(POWER, nextPower), 3);
            level.updateNeighborsAt(pos, this);
            level.updateNeighbourForOutputSignal(pos, this);
        }
        if (nearbyTargets > 0 && Math.floorMod(level.getGameTime(), 40L) == 0L) {
            level.playSound(null, pos, ModSounds.SYNAPSE_NODE_PULSE.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        }
        level.scheduleTick(pos, this, UPDATE_INTERVAL);
    }

    private static boolean isHiveTarget(LivingEntity entity) {
        return entity.isAlive() && (entity instanceof HivemindLinkedMob || entity instanceof FleshAmalgamEntity);
    }

    @Override
    public boolean isSignalSource(BlockState state) {
        return true;
    }

    @Override
    public int getSignal(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return state.getValue(POWER);
    }

    @Override
    public int getDirectSignal(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return state.getValue(POWER);
    }
}
```

## `src/main/java/com/carnis/mod/block/entity/FleshBulbBlockEntity.java`

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
            level.playSound(null, pos, ModSounds.ACID_SPLASH.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
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
                1.0F, 1.0F);
        boolean pulse = phase < 3;
        if (state.getValue(FleshBulbBlock.PULSING) != pulse)
            level.setBlock(pos, state.setValue(FleshBulbBlock.PULSING, pulse), 3);
    }
}
```

## `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.item.NeuroWeave;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.tags.ItemTags;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TridentItem;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.gameevent.GameEventListener;
import net.minecraftforge.common.ToolActions;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoBlockEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import javax.annotation.Nullable;
import java.util.Set;
import java.util.UUID;

public final class HiveEyeBlockEntity extends BlockEntity implements GeoBlockEntity, GameEventListener.Holder<GameEventListener> {
    public static final int SCAN_INTERVAL_TICKS = 20;
    public static final double PLAYER_SCAN_RADIUS = 18D;
    public static final double LOOK_RADIUS = 16D;
    public static final double THREAT_RADIUS = 16D;
    public static final double HIVEMIND_ALERT_RADIUS = 28D;
    private static final int SYNCHRONIZED_ALERT_RADIUS = 32;
    private static final int SYNCHRONIZED_ALERT_DURATION_TICKS = 100;
    private static final int SWARM_ALARM_COOLDOWN_TICKS = 20;
    public static final int CALM_STATE = 0;
    public static final int WATCHING_STATE = 1;
    public static final int SOFT_ALERT_STATE = 2;
    public static final int ALERT_STATE = SOFT_ALERT_STATE;
    public static final int FULL_ALERT_STATE = 3;

    private static final int PLAYER_STATE_SCAN_INTERVAL = 5;
    private static final int AURA_INTERVAL_TICKS = 40;
    private static final int AURA_EFFECT_DURATION_TICKS = 60;
    private static final int AURA_REFRESH_THRESHOLD_TICKS = 40;
    private static final int BLINK_DURATION_TICKS = 10;
    private static final int BLINK_MIN_TICKS = 80;
    private static final int BLINK_MAX_TICKS = 300;
    private static final int SCREECH_COOLDOWN_TICKS = 200;
    private static final int ARMED_WARNING_RADIUS = 8;
    private static final int ARMED_WARNING_TICKS = 40;
    private static final float MAX_LOOK_YAW = (float) Math.toRadians(20.0D);
    private static final float MAX_LOOK_PITCH = (float) Math.toRadians(15.0D);
    private static final float CLIENT_LERP_SPEED = 0.15F;
    private static final float STATE_LERP_STEP = 1.0F / 30.0F;
    private static final Set<String> AUDIBLE_EVENTS = Set.of(
            "step", "hit_ground", "projectile_shoot", "projectile_land", "block_destroy",
            "entity_action", "entity_interact", "entity_damage", "entity_roar", "entity_place");

    private static final RawAnimation IDLE_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.hive_eye.idle");
    private static final RawAnimation WATCHING_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.hive_eye.watching");
    private static final RawAnimation ALERT_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.hive_eye.alert");
    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private final net.minecraft.world.level.gameevent.GameEventListener vibrationListener = new EyeListener();

    private long alertUntil;
    private long hiveAttackUntil;
    private long lastSwarmAlarmTick = Long.MIN_VALUE;
    private int reinforcementCooldown;
    private int blinkCooldown;
    private int blinkTicksRemaining;
    private int alertLevel;
    private int screechCooldown;
    private int armedApproachTicks;
    private boolean blinking;
    private boolean blinkTimerInitialized;
    private boolean clientAlert;
    private boolean clientBlinking;
    private boolean targetPlayerPresent;
    private boolean armedScreechPending;
    private boolean reinforcementsCalled;
    @Nullable
    private LivingEntity pendingVibrationSource;
    private long clientBlinkStartedAt = Long.MIN_VALUE;
    private double previousArmedDistance = Double.MAX_VALUE;
    @Nullable
    private UUID armedTargetId;
    private float targetYaw;
    private float targetPitch;
    private float lastSyncedTargetYaw;
    private float lastSyncedTargetPitch;
    private float targetPlayerDistance;
    private float lastSyncedPlayerDistance = -1.0F;
    private float playerDistance;
    private float previousPlayerDistance;
    private float yaw;
    private float pitch;
    private float previousYaw;
    private float previousPitch;
    private float alertBlend;
    private float previousAlertBlend;
    private float fullAlertBlend;
    private float previousFullAlertBlend;

    public HiveEyeBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.HIVE_EYE.get(), pos, state);
    }

    @Override
    public GameEventListener getListener() {
        return vibrationListener;
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "eye_state", 30, state -> {
            if (isAlert()) return state.setAndContinue(ALERT_ANIMATION);
            if (alertLevel >= WATCHING_STATE) return state.setAndContinue(WATCHING_ANIMATION);
            return state.setAndContinue(IDLE_ANIMATION);
        }));
    }

    public boolean isAlert() {
        if (level == null) return false;
        return level.isClientSide
                ? clientAlert || alertLevel >= SOFT_ALERT_STATE
                : level.getGameTime() < alertUntil || alertLevel >= SOFT_ALERT_STATE;
    }

    public float trackingYaw(float partialTick) {
        return Mth.lerp(partialTick, previousYaw, yaw);
    }

    public float trackingPitch(float partialTick) {
        return Mth.lerp(partialTick, previousPitch, pitch);
    }

    public float alertBlend(float partialTick) {
        return Mth.lerp(partialTick, previousAlertBlend, alertBlend);
    }

    private float fullAlertBlend(float partialTick) {
        return Mth.lerp(partialTick, previousFullAlertBlend, fullAlertBlend);
    }

    public float irisPulseScale(float partialTick) {
        if (level == null) return 1.0F;
        double time = level.getGameTime() + partialTick;
        float wave = (float) ((Math.sin(time * (Math.PI * 2.0D / 10.0D)) + 1.0D) * 0.5D);
        float amplitude = 0.05F * alertBlend(partialTick) + 0.05F * fullAlertBlend(partialTick);
        return 1.0F + amplitude * wave;
    }

    public boolean hasTrackingTarget() {
        return targetPlayerPresent;
    }

    public float pupilDistanceScale(float partialTick) {
        float distance = Mth.lerp(partialTick, previousPlayerDistance, playerDistance);
        if (distance <= 2.0F) return 1.0F;
        float progress = Mth.clamp((float) ((distance - 2.0) / (LOOK_RADIUS - 2.0)), 0.0F, 1.0F);
        return targetPlayerPresent ? 1.0F - 0.45F * progress : 1.0F;
    }

    public float pupilScaleY(float partialTick) {
        float squeeze = 0.3F * alertBlend(partialTick) + 0.2F * fullAlertBlend(partialTick);
        return (1.0F - squeeze) * blinkScale(partialTick);
    }

    public boolean consumeReinforcementsCalled() {
        boolean wasCalled = reinforcementsCalled;
        reinforcementsCalled = false;
        return wasCalled;
    }

    private float blinkScale(float partialTick) {
        if (level == null || clientBlinkStartedAt == Long.MIN_VALUE) return 1.0F;
        float elapsed = (float) (level.getGameTime() - clientBlinkStartedAt) + partialTick;
        if (elapsed < 0.0F || elapsed >= BLINK_DURATION_TICKS) return 1.0F;
        if (elapsed <= BLINK_DURATION_TICKS * 0.5F) {
            return 1.0F - elapsed / (BLINK_DURATION_TICKS * 0.5F);
        }
        return (elapsed - BLINK_DURATION_TICKS * 0.5F) / (BLINK_DURATION_TICKS * 0.5F);
    }

    @Override
    public CompoundTag getUpdateTag() {
        CompoundTag tag = new CompoundTag();
        tag.putBoolean("Alert", isAlert());
        tag.putInt("BlinkCooldown", blinkCooldown);
        tag.putBoolean("Blinking", blinking);
        tag.putFloat("TargetYaw", targetYaw);
        tag.putFloat("TargetPitch", targetPitch);
        tag.putFloat("TargetPlayerDistance", targetPlayerDistance);
        tag.putBoolean("TargetPlayerPresent", targetPlayerPresent);
        tag.putInt("AlertLevel", alertLevel);
        tag.putBoolean("ReinforcementsCalled", reinforcementsCalled);
        return tag;
    }

    @Nullable
    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    @Override
    public void handleUpdateTag(CompoundTag tag) {
        clientAlert = tag.getBoolean("Alert");
        blinkCooldown = Mth.clamp(tag.getInt("BlinkCooldown"), 0, BLINK_MAX_TICKS);
        targetYaw = Mth.clamp(tag.getFloat("TargetYaw"), -MAX_LOOK_YAW, MAX_LOOK_YAW);
        targetPitch = Mth.clamp(tag.getFloat("TargetPitch"), -MAX_LOOK_PITCH, MAX_LOOK_PITCH);
        targetPlayerDistance = Mth.clamp(tag.getFloat("TargetPlayerDistance"), 0.0F, (float) LOOK_RADIUS);
        targetPlayerPresent = tag.getBoolean("TargetPlayerPresent");
        alertLevel = Mth.clamp(tag.getInt("AlertLevel"), CALM_STATE, FULL_ALERT_STATE);

        boolean newBlinking = tag.getBoolean("Blinking");
        if (newBlinking && !clientBlinking) {
            clientBlinkStartedAt = level == null ? 0L : level.getGameTime();
        }
        clientBlinking = newBlinking;
    }

    @Override
    public void onDataPacket(Connection connection, ClientboundBlockEntityDataPacket packet) {
        if (packet.getTag() != null) handleUpdateTag(packet.getTag());
    }

    private void applyAura(ServerLevel level) {
        if (alertLevel == CALM_STATE) return;

        boolean buffsEnabled = CarnisConfig.SERVER.hiveEyeBuffsEnabled.get();
        boolean debuffsEnabled = CarnisConfig.SERVER.hiveEyeDebuffsEnabled.get();
        if (!buffsEnabled && !debuffsEnabled) return;

        int radius = CarnisConfig.SERVER.hiveEyeAuraRadius.get();
        double radiusSquared = (double) radius * radius;
        Vec3 center = Vec3.atCenterOf(worldPosition);
        AABB area = AABB.ofSize(center, radius * 2.0D, radius * 2.0D, radius * 2.0D);

        for (LivingEntity entity : level.getEntitiesOfClass(LivingEntity.class, area,
                candidate -> candidate.isAlive() && !candidate.isSpectator())) {
            if (entity.position().distanceToSqr(center) > radiusSquared) continue;

            if (buffsEnabled && NeuralMossBlock.isHive(entity)) {
                applyHiveBuffs(entity);
            } else if (debuffsEnabled && entity instanceof Player player) {
                applyThreatDebuffs(player);
            }
        }
    }

    private void applyHiveBuffs(LivingEntity entity) {
        switch (alertLevel) {
            case WATCHING_STATE -> maintainAuraEffect(entity, MobEffects.MOVEMENT_SPEED, 0);
            case SOFT_ALERT_STATE -> {
                maintainAuraEffect(entity, MobEffects.MOVEMENT_SPEED, 0);
                maintainAuraEffect(entity, MobEffects.DAMAGE_BOOST, 0);
            }
            case FULL_ALERT_STATE -> {
                maintainAuraEffect(entity, MobEffects.MOVEMENT_SPEED, 1);
                maintainAuraEffect(entity, MobEffects.DAMAGE_BOOST, 1);
                maintainAuraEffect(entity, MobEffects.DAMAGE_RESISTANCE, 0);
            }
            default -> {
            }
        }
    }

    private void applyThreatDebuffs(Player player) {
        int playerThreatLevel = threatLevel(player);
        if (playerThreatLevel < SOFT_ALERT_STATE) return;
        if (alertLevel == SOFT_ALERT_STATE) {
            maintainAuraEffect(player, MobEffects.WEAKNESS, 0);
        } else if (alertLevel >= FULL_ALERT_STATE) {
            maintainAuraEffect(player, MobEffects.WEAKNESS, 1);
            maintainAuraEffect(player, MobEffects.MOVEMENT_SLOWDOWN, 0);
        }
    }

    private static void maintainAuraEffect(LivingEntity entity, MobEffect effect, int amplifier) {
        MobEffectInstance existing = entity.getEffect(effect);
        if (existing == null || existing.getAmplifier() < amplifier
                || existing.getAmplifier() == amplifier
                && existing.getDuration() <= AURA_REFRESH_THRESHOLD_TICKS) {
            entity.addEffect(new MobEffectInstance(effect, AURA_EFFECT_DURATION_TICKS, amplifier));
        }
    }

    private void spawnAuraBoundaryParticles(ServerLevel level) {
        int radius = CarnisConfig.SERVER.hiveEyeAuraRadius.get();
        int particleCount = 1 + level.random.nextInt(2);
        for (int i = 0; i < particleCount; i++) {
            double angle = level.random.nextDouble() * Math.PI * 2.0D;
            double distance = radius - 2.0D + level.random.nextDouble() * 4.0D;
            double x = worldPosition.getX() + 0.5D + Math.cos(angle) * distance;
            double y = worldPosition.getY() + 0.5D + level.random.nextDouble() * 4.0D - 2.0D;
            double z = worldPosition.getZ() + 0.5D + Math.sin(angle) * distance;
            level.sendParticles(ParticleTypes.CRIMSON_SPORE, x, y, z, 1, 0.0D, 0.0D, 0.0D, 0.0D);
        }
    }

    public static void serverTick(Level world, BlockPos pos, BlockState state, HiveEyeBlockEntity eye) {
        if (!(world instanceof ServerLevel level)) return;
        boolean syncAnimation = false;

        if (eye.alertUntil != 0 && level.getGameTime() >= eye.alertUntil) {
            eye.alertUntil = 0;
            syncAnimation = true;
        }
        if (eye.hiveAttackUntil != 0 && level.getGameTime() >= eye.hiveAttackUntil) {
            eye.hiveAttackUntil = 0;
            syncAnimation = true;
        }

        if (eye.pendingVibrationSource != null) {
            LivingEntity source = eye.pendingVibrationSource;
            eye.pendingVibrationSource = null;
            boolean wasEventAlert = level.getGameTime() < eye.alertUntil;
            eye.alertUntil = level.getGameTime() + 60L;
            if (!wasEventAlert) {
                syncAnimation = true;
                level.playSound(null, pos, ModSounds.HIVE_ALARM.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
                level.sendParticles(ParticleTypes.ELECTRIC_SPARK, pos.getX() + .5D, pos.getY() + .8D,
                        pos.getZ() + .5D, 12, .25D, .2D, .25D, .02D);
            }
            eye.notifySwarmAlarm(level, source);
        }

        if (!eye.blinkTimerInitialized) {
            eye.blinkCooldown = eye.nextBlinkDelay(level);
            eye.blinkTimerInitialized = true;
            syncAnimation = true;
        } else {
            eye.blinkCooldown--;
            if (eye.blinking) {
                eye.blinkTicksRemaining--;
                if (eye.blinkTicksRemaining <= 0) {
                    eye.blinkTicksRemaining = 0;
                    eye.blinking = false;
                    syncAnimation = true;
                }
            } else if (eye.blinkCooldown <= 0) {
                eye.blinking = true;
                eye.blinkTicksRemaining = BLINK_DURATION_TICKS;
                eye.blinkCooldown = eye.nextBlinkDelay(level);
                syncAnimation = true;
            }
        }

        if (eye.screechCooldown > 0) eye.screechCooldown--;
        if (eye.reinforcementCooldown > 0) eye.reinforcementCooldown--;

        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), PLAYER_STATE_SCAN_INTERVAL),
                PLAYER_STATE_SCAN_INTERVAL) == 0) {
            int previousLevel = eye.alertLevel;
            boolean previousTargetPlayerPresent = eye.targetPlayerPresent;
            eye.updatePlayerState(level);

            if (previousLevel != eye.alertLevel) {
                eye.blinkCooldown = eye.nextBlinkDelay(level);
                syncAnimation = true;
                HiveNetwork.observe(level, pos, state, true);
                if (eye.alertLevel == FULL_ALERT_STATE) {
                    eye.propagateAlert(level, pos);
                }
            }
            if (Math.abs(eye.lastSyncedTargetYaw - eye.targetYaw) > 0.01F
                    || Math.abs(eye.lastSyncedTargetPitch - eye.targetPitch) > 0.01F
                    || previousTargetPlayerPresent != eye.targetPlayerPresent
                    || Math.abs(eye.lastSyncedPlayerDistance - eye.targetPlayerDistance) > 0.05F) {
                syncAnimation = true;
            }
        }

        if (eye.consumeReinforcementsCalled()) {
            eye.spawnReinforcements(level, pos);
        }

        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), SCAN_INTERVAL_TICKS),
                SCAN_INTERVAL_TICKS) == 0) {
            HiveNetwork.observe(level, pos, state, true);
            LivingEntity nearest = eye.findNearestLiving(level);
            if (nearest != null) nearest.addEffect(new MobEffectInstance(MobEffects.GLOWING, 100, 0));
        }

        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), AURA_INTERVAL_TICKS),
                AURA_INTERVAL_TICKS) == 0) {
            eye.applyAura(level);
        }
        if (eye.alertLevel >= SOFT_ALERT_STATE
                && Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), 20), 20) == 0) {
            eye.spawnAuraBoundaryParticles(level);
        }

        if (syncAnimation) {
            eye.lastSyncedPlayerDistance = eye.targetPlayerDistance;
            eye.syncAnimationData(level);
        }
    }

    private void spawnReinforcements(ServerLevel level, BlockPos pos) {
        if (reinforcementCooldown > 0) return;
        reinforcementCooldown = 300;

        int nearbyCount = countNearbyHiveMobs(level, pos, 32);
        if (nearbyCount >= 8) return;

        int requestedCount = 2 + level.random.nextInt(3);
        int spawnedCount = 0;
        for (int i = 0; i < requestedCount && nearbyCount < 8; i++) {
            Mob reinforcement = createRandomReinforcement(level);
            if (reinforcement == null) continue;

            BlockPos spawnPos = findReinforcementSpawnPos(level, pos, reinforcement);
            if (spawnPos == null) {
                reinforcement.discard();
                continue;
            }

            reinforcement.finalizeSpawn(level, level.getCurrentDifficultyAt(spawnPos), MobSpawnType.EVENT, null, null);
            if (!level.noCollision(reinforcement) || !level.addFreshEntity(reinforcement)) {
                reinforcement.discard();
                continue;
            }

            Player target = findNearestThreat(level, pos, 32);
            if (target != null) reinforcement.setTarget(target);
            nearbyCount++;
            spawnedCount++;
        }

        if (spawnedCount == 0) return;

        level.playSound(null, pos, ModSounds.AMALGAM_ROAR.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        level.sendParticles(ParticleTypes.CRIMSON_SPORE,
                pos.getX() + 0.5D, pos.getY() + 1.0D, pos.getZ() + 0.5D,
                20, 0.8D, 0.6D, 0.8D, 0.02D);
        level.sendParticles(ParticleTypes.ELECTRIC_SPARK,
                pos.getX() + 0.5D, pos.getY() + 0.8D, pos.getZ() + 0.5D,
                12, 0.25D, 0.2D, 0.25D, 0.02D);
    }

    private static Mob createRandomReinforcement(ServerLevel level) {
        int roll = level.random.nextInt(100);
        if (roll < 50) return ModEntities.INFECTED_ZOMBIE.get().create(level);
        if (roll < 75) return ModEntities.INFECTED_SPIDER.get().create(level);
        if (roll < 90) return ModEntities.INFECTED_SKELETON.get().create(level);
        return ModEntities.FLESH_AMALGAM.get().create(level);
    }

    private static int countNearbyHiveMobs(ServerLevel level, BlockPos pos, int radius) {
        Vec3 center = Vec3.atCenterOf(pos);
        double radiusSquared = (double) radius * radius;
        AABB area = AABB.ofSize(center, radius * 2.0D, radius * 2.0D, radius * 2.0D);
        int count = 0;
        for (Mob mob : level.getEntitiesOfClass(Mob.class, area,
                candidate -> candidate.isAlive() && NeuralMossBlock.isHive(candidate))) {
            if (mob.position().distanceToSqr(center) <= radiusSquared) count++;
        }
        return count;
    }

    @Nullable
    private static BlockPos findReinforcementSpawnPos(ServerLevel level, BlockPos eyePos, Mob mob) {
        for (int ring = 0; ring <= 3; ring++) {
            for (int dx = -ring; dx <= ring; dx++) {
                for (int dy = -ring; dy <= ring; dy++) {
                    for (int dz = -ring; dz <= ring; dz++) {
                        if (Math.max(Math.max(Math.abs(dx), Math.abs(dy)), Math.abs(dz)) != ring) continue;
                        BlockPos candidate = eyePos.above().offset(dx, dy, dz);
                        if (candidate.distSqr(eyePos) > 16.0D) continue;
                        BlockPos support = candidate.below();
                        BlockPos head = candidate.above();
                        if (!level.hasChunkAt(support) || !level.hasChunkAt(candidate) || !level.hasChunkAt(head)) continue;

                        BlockState feetState = level.getBlockState(candidate);
                        BlockState headState = level.getBlockState(head);
                        if (!(feetState.isAir() || feetState.canBeReplaced())
                                || !(headState.isAir() || headState.canBeReplaced())
                                || !level.getFluidState(candidate).isEmpty()
                                || !level.getBlockState(support).isFaceSturdy(level, support, Direction.UP)) continue;

                        mob.moveTo(candidate.getX() + 0.5D, candidate.getY(), candidate.getZ() + 0.5D,
                                level.random.nextFloat() * 360.0F, 0.0F);
                        if (level.noCollision(mob)) return candidate;
                    }
                }
            }
        }
        return null;
    }

    @Nullable
    private static Player findNearestThreat(ServerLevel level, BlockPos pos, int radius) {
        Vec3 center = Vec3.atCenterOf(pos);
        double radiusSquared = (double) radius * radius;
        double nearestDistance = radiusSquared;
        Player nearest = null;
        AABB area = AABB.ofSize(center, radius * 2.0D, radius * 2.0D, radius * 2.0D);
        for (Player player : level.getEntitiesOfClass(Player.class, area,
                candidate -> candidate.isAlive() && !candidate.isSpectator())) {
            double distance = player.position().distanceToSqr(center);
            if (distance > nearestDistance || threatLevel(player) == CALM_STATE) continue;
            nearestDistance = distance;
            nearest = player;
        }
        return nearest;
    }

    private void propagateAlert(ServerLevel level, BlockPos sourcePos) {
        long operationStartedAt = System.nanoTime();
        long alertUntilTick = level.getGameTime() + SYNCHRONIZED_ALERT_DURATION_TICKS;
        hiveAttackUntil = Math.max(hiveAttackUntil, alertUntilTick);
        alertLevel = FULL_ALERT_STATE;
        HiveNetwork.observe(level, sourcePos, level.getBlockState(sourcePos), true);

        int minChunkX = (sourcePos.getX() - SYNCHRONIZED_ALERT_RADIUS) >> 4;
        int maxChunkX = (sourcePos.getX() + SYNCHRONIZED_ALERT_RADIUS) >> 4;
        int minChunkZ = (sourcePos.getZ() - SYNCHRONIZED_ALERT_RADIUS) >> 4;
        int maxChunkZ = (sourcePos.getZ() + SYNCHRONIZED_ALERT_RADIUS) >> 4;
        double radiusSquared = (double) SYNCHRONIZED_ALERT_RADIUS * SYNCHRONIZED_ALERT_RADIUS;
        Vec3 sourceCenter = Vec3.atCenterOf(sourcePos);

        int loadedChunksScanned = 0;
        for (int chunkX = minChunkX; chunkX <= maxChunkX; chunkX++) {
            for (int chunkZ = minChunkZ; chunkZ <= maxChunkZ; chunkZ++) {
                var chunk = level.getChunkSource().getChunkNow(chunkX, chunkZ);
                if (chunk == null) continue;
                loadedChunksScanned++;

                for (BlockEntity blockEntity : chunk.getBlockEntities().values()) {
                    if (!(blockEntity instanceof HiveEyeBlockEntity other) || other == this || other.isRemoved()) continue;
                    if (Vec3.atCenterOf(other.getBlockPos()).distanceToSqr(sourceCenter) > radiusSquared) continue;

                    other.alertLevel = FULL_ALERT_STATE;
                    other.hiveAttackUntil = Math.max(other.hiveAttackUntil, alertUntilTick);
                    other.alertUntil = Math.max(other.alertUntil, alertUntilTick);
                    other.syncAnimationData(level);
                    HiveNetwork.observe(level, other.getBlockPos(), other.getBlockState(), true);
                }
            }
        }
        long elapsed = System.nanoTime() - operationStartedAt;
        if (elapsed > 1_000_000L) {
            CarnisMod.LOGGER.debug("Slow hive alert propagation: {} ms across {} loaded chunks",
                    elapsed / 1_000_000.0D, loadedChunksScanned);
        }
    }

    private void notifySwarmAlarm(ServerLevel level, LivingEntity intruder) {
        long now = level.getGameTime();
        if (lastSwarmAlarmTick != Long.MIN_VALUE && now >= lastSwarmAlarmTick
                && now - lastSwarmAlarmTick < SWARM_ALARM_COOLDOWN_TICKS) return;
        lastSwarmAlarmTick = now;
        HiveSwarmCoordinator.eyeAlarm(level, worldPosition, intruder);
    }

    private int nextBlinkDelay(ServerLevel level) {
        return BLINK_MIN_TICKS + level.random.nextInt(BLINK_MAX_TICKS - BLINK_MIN_TICKS + 1);
    }

    private void updatePlayerState(ServerLevel level) {
        Vec3 center = Vec3.atCenterOf(worldPosition);
        double lookRadiusSquared = LOOK_RADIUS * LOOK_RADIUS;
        double threatRadiusSquared = THREAT_RADIUS * THREAT_RADIUS;
        double armedRadiusSquared = (double) ARMED_WARNING_RADIUS * ARMED_WARNING_RADIUS;
        Player nearestPlayer = null;
        Player nearestArmedPlayer = null;
        double nearestPlayerDistance = lookRadiusSquared;
        double nearestArmedDistanceSquared = armedRadiusSquared;
        int maxThreatLevel = CALM_STATE;
        AABB scanArea = AABB.ofSize(center, LOOK_RADIUS * 2.0D, LOOK_RADIUS * 2.0D, LOOK_RADIUS * 2.0D);

        for (Player player : level.getEntitiesOfClass(Player.class, scanArea,
                candidate -> candidate.isAlive() && !candidate.isSpectator())) {
            double distanceSquared = player.position().distanceToSqr(center);
            if (distanceSquared > lookRadiusSquared) continue;

            if (nearestPlayer == null || distanceSquared < nearestPlayerDistance) {
                nearestPlayerDistance = distanceSquared;
                nearestPlayer = player;
            }

            int playerThreatLevel = threatLevel(player);
            if (playerThreatLevel != CALM_STATE && distanceSquared <= threatRadiusSquared) {
                maxThreatLevel = Math.max(maxThreatLevel, playerThreatLevel);
            }

            if (distanceSquared <= armedRadiusSquared && isArmed(player)
                    && (nearestArmedPlayer == null || distanceSquared < nearestArmedDistanceSquared)) {
                nearestArmedDistanceSquared = distanceSquared;
                nearestArmedPlayer = player;
            }
        }

        targetPlayerPresent = nearestPlayer != null;
        if (nearestPlayer == null) {
            targetYaw = 0.0F;
            targetPitch = 0.0F;
            targetPlayerDistance = 0.0F;
        } else {
            setTargetAngles(nearestPlayer);
            targetPlayerDistance = (float) Math.sqrt(nearestPlayerDistance);
        }

        updateArmedApproach(level, nearestArmedPlayer,
                nearestArmedPlayer == null ? Double.MAX_VALUE : Math.sqrt(nearestArmedDistanceSquared));

        int nextAlertLevel;
        if (maxThreatLevel >= FULL_ALERT_STATE) {
            nextAlertLevel = FULL_ALERT_STATE;
        } else if (maxThreatLevel == SOFT_ALERT_STATE) {
            nextAlertLevel = SOFT_ALERT_STATE;
        } else if (maxThreatLevel >= WATCHING_STATE) {
            nextAlertLevel = WATCHING_STATE;
        } else {
            nextAlertLevel = CALM_STATE;
        }

        if (nearestArmedPlayer != null || level.getGameTime() < hiveAttackUntil) {
            nextAlertLevel = FULL_ALERT_STATE;
        }
        alertLevel = nextAlertLevel;
    }

    private void setTargetAngles(Player player) {
        Vec3 delta = player.getEyePosition().subtract(
                worldPosition.getX() + 0.5D,
                worldPosition.getY() + 0.5625D,
                worldPosition.getZ() + 0.5D);
        double horizontal = Math.sqrt(delta.x * delta.x + delta.z * delta.z);
        targetYaw = horizontal > 1.0E-5D
                ? Mth.clamp((float) Math.atan2(delta.x, -delta.z), -MAX_LOOK_YAW, MAX_LOOK_YAW)
                : 0.0F;
        targetPitch = Mth.clamp((float) -Math.atan2(delta.y, Math.max(horizontal, 1.0E-5D)),
                -MAX_LOOK_PITCH, MAX_LOOK_PITCH);
    }

    private void updateArmedApproach(ServerLevel level, @Nullable Player armedPlayer, double distance) {
        if (armedPlayer == null) {
            armedTargetId = null;
            previousArmedDistance = Double.MAX_VALUE;
            armedApproachTicks = 0;
            armedScreechPending = false;
            return;
        }

        UUID currentId = armedPlayer.getUUID();
        if (!currentId.equals(armedTargetId)) {
            armedTargetId = currentId;
            previousArmedDistance = distance;
            armedApproachTicks = 0;
            armedScreechPending = true;
        } else if (distance < previousArmedDistance - 0.01D) {
            armedApproachTicks += PLAYER_STATE_SCAN_INTERVAL;
        } else if (distance > previousArmedDistance + 0.01D) {
            armedApproachTicks = 0;
        }
        previousArmedDistance = distance;

        if (armedScreechPending && armedApproachTicks >= ARMED_WARNING_TICKS && screechCooldown <= 0) {
            playScreech(level, armedPlayer);
            armedScreechPending = false;
        }
    }

    private static int threatLevel(Player player) {
        if (!player.isAlive() || player.isSpectator() || player.isCreative()) return CALM_STATE;
        if (NeuroArmorEventHandler.hasFullSet(player)
                || NeuroWeave.protectedPieces(player) >= 4
                || NeuroResonatorHelmetItem.isEquipped(player)) return CALM_STATE;
        if (PlayerInfectionApi.isAssimilated(player)) return CALM_STATE;

        float infection = PlayerInfectionApi.getInfectionLevel(player);
        if (infection >= 100.0F) return CALM_STATE;
        if (infection >= 75.0F) return WATCHING_STATE;
        if (infection >= 1.0F) return SOFT_ALERT_STATE;
        return FULL_ALERT_STATE;
    }

    private static boolean isArmed(Player player) {
        ItemStack held = player.getMainHandItem();
        return held.canPerformAction(ToolActions.SWORD_DIG)
                || held.canPerformAction(ToolActions.AXE_DIG)
                || held.is(ItemTags.SWORDS)
                || held.is(ItemTags.AXES)
                || held.getItem() instanceof BowItem
                || held.getItem() instanceof CrossbowItem
                || held.getItem() instanceof TridentItem;
    }

    private void playScreech(ServerLevel level, Player armedPlayer) {
        if (!isArmed(armedPlayer) || screechCooldown > 0) return;
        level.playSound(null, worldPosition, ModSounds.HIVE_EYE_SCREECH.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        screechCooldown = SCREECH_COOLDOWN_TICKS;
    }

    public void onHiveAttacked(ServerLevel level, Player attacker) {
        if (!attacker.isAlive()) return;
        long now = level.getGameTime();
        alertUntil = now + 200L;
        hiveAttackUntil = alertUntil;
        alertLevel = FULL_ALERT_STATE;
        armedTargetId = null;
        armedApproachTicks = 0;
        armedScreechPending = false;
        reinforcementsCalled = true;
        setTargetAngles(attacker);
        targetPlayerPresent = true;
        targetPlayerDistance = Mth.clamp((float) attacker.position().distanceTo(Vec3.atCenterOf(worldPosition)),
                0.0F, (float) LOOK_RADIUS);

        if (isArmed(attacker)) playScreech(level, attacker);
        level.playSound(null, worldPosition, ModSounds.HIVE_ALARM.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        level.sendParticles(ParticleTypes.ELECTRIC_SPARK, worldPosition.getX() + .5D, worldPosition.getY() + .8D,
                worldPosition.getZ() + .5D, 12, .25D, .2D, .25D, .02D);
        notifySwarmAlarm(level, attacker);
        propagateAlert(level, worldPosition);
        HiveNetwork.observe(level, worldPosition, getBlockState(), true);
        syncAnimationData(level);
    }

    private void syncAnimationData(ServerLevel level) {
        lastSyncedTargetYaw = targetYaw;
        lastSyncedTargetPitch = targetPitch;
        lastSyncedPlayerDistance = targetPlayerDistance;
        setChanged();
        BlockState state = getBlockState();
        level.sendBlockUpdated(worldPosition, state, state, Block.UPDATE_CLIENTS);
    }

    private void recordVibration(LivingEntity source) {
        if (isTarget(source)) pendingVibrationSource = source;
    }

    private static boolean isTarget(LivingEntity entity) {
        if (!entity.isAlive() || entity.isSpectator() || NeuralMossBlock.isHive(entity)) return false;
        return !(entity instanceof Player player) || threatLevel(player) > CALM_STATE;
    }

    @Nullable
    private LivingEntity findNearestLiving(Level level) {
        Vec3 center = Vec3.atCenterOf(worldPosition);
        LivingEntity nearest = null;
        double best = PLAYER_SCAN_RADIUS * PLAYER_SCAN_RADIUS;
        for (LivingEntity candidate : level.getEntitiesOfClass(LivingEntity.class,
                AABB.ofSize(center, 36, 36, 36), HiveEyeBlockEntity::isTarget)) {
            double distance = candidate.position().distanceToSqr(center);
            if (distance <= best) {
                best = distance;
                nearest = candidate;
            }
        }
        return nearest;
    }

    public static void clientTick(Level level, BlockPos pos, BlockState state, HiveEyeBlockEntity eye) {
        eye.previousYaw = eye.yaw;
        eye.previousPitch = eye.pitch;
        eye.yaw += (eye.targetYaw - eye.yaw) * CLIENT_LERP_SPEED;
        eye.pitch += (eye.targetPitch - eye.pitch) * CLIENT_LERP_SPEED;

        eye.previousPlayerDistance = eye.playerDistance;
        eye.playerDistance += (eye.targetPlayerDistance - eye.playerDistance) * CLIENT_LERP_SPEED;

        eye.previousAlertBlend = eye.alertBlend;
        eye.previousFullAlertBlend = eye.fullAlertBlend;
        float wantedAlertBlend = eye.alertLevel >= SOFT_ALERT_STATE ? 1.0F : 0.0F;
        float wantedFullAlertBlend = eye.alertLevel >= FULL_ALERT_STATE ? 1.0F : 0.0F;
        eye.alertBlend = approach(eye.alertBlend, wantedAlertBlend, STATE_LERP_STEP);
        eye.fullAlertBlend = approach(eye.fullAlertBlend, wantedFullAlertBlend, STATE_LERP_STEP);
    }

    private static float approach(float current, float target, float step) {
        if (current < target) return Math.min(current + step, target);
        return Math.max(current - step, target);
    }

    private final class EyeListener implements net.minecraft.world.level.gameevent.GameEventListener {
        private final net.minecraft.world.level.gameevent.PositionSource source =
                new net.minecraft.world.level.gameevent.BlockPositionSource(worldPosition);

        @Override
        public net.minecraft.world.level.gameevent.PositionSource getListenerSource() {
            return source;
        }

        @Override
        public int getListenerRadius() {
            return 16;
        }

        @Override
        public boolean handleGameEvent(ServerLevel level, net.minecraft.world.level.gameevent.GameEvent event,
                                       net.minecraft.world.level.gameevent.GameEvent.Context context, Vec3 position) {
            var id = net.minecraft.core.registries.BuiltInRegistries.GAME_EVENT.getKey(event);
            if (id == null || !id.getNamespace().equals("minecraft") || !AUDIBLE_EVENTS.contains(id.getPath())) {
                return false;
            }
            net.minecraft.world.entity.Entity origin = context.sourceEntity();
            if (origin instanceof net.minecraft.world.entity.projectile.Projectile projectile && projectile.getOwner() != null) {
                origin = projectile.getOwner();
            }
            if (!(origin instanceof LivingEntity living) || !isTarget(living)
                    || living instanceof Player player
                    && (player.isSteppingCarefully() || NeuroArmorEventHandler.hasFullSet(player))
                    || position.distanceToSqr(Vec3.atCenterOf(worldPosition)) > 256D) {
                return false;
            }
            recordVibration(living);
            return true;
        }
    }
}
```

## `src/main/java/com/carnis/mod/block/entity/NervePillarBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoBlockEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class NervePillarBlockEntity extends BlockEntity implements GeoBlockEntity {
    private static final int AURA_INTERVAL_TICKS = 40;
    private static final int PARTICLE_INTERVAL_TICKS = 20;
    private static final int EFFECT_DURATION_TICKS = 60;
    private static final int EFFECT_REFRESH_THRESHOLD_TICKS = 40;
    private static final RawAnimation IDLE_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.nerve_pillar.idle");

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private long nextDischarge;
    private int tickCounter;

    public NervePillarBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.NERVE_PILLAR.get(), pos, state);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "fibers", 0,
                state -> state.setAndContinue(IDLE_ANIMATION)));
    }

    public void discharge(ServerLevel server) {
        long now = server.getGameTime();
        if (now < nextDischarge) return;
        nextDischarge = now + 10;
        double x = worldPosition.getX() + 0.5D;
        double y = worldPosition.getY() + 0.7D;
        double z = worldPosition.getZ() + 0.5D;
        server.sendParticles(ParticleTypes.ELECTRIC_SPARK, x, y, z, 18, 0.3D, 0.45D, 0.3D, 0.08D);
        for (int i = 0; i < 16; i++) {
            double angle = Math.PI * 2.0D * i / 16.0D;
            double dx = Math.cos(angle);
            double dz = Math.sin(angle);
            server.sendParticles(ModParticles.BIOMASS_SPARK.get(), x + dx * 0.52D, y, z + dz * 0.52D,
                    0, dx * 0.08D, 0.025D, dz * 0.08D, 1.0D);
        }
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, NervePillarBlockEntity blockEntity) {
        if (level.isClientSide) return;

        boolean buffsEnabled = CarnisConfig.SERVER.nervePillarBuffsEnabled.get();
        boolean debuffsEnabled = CarnisConfig.SERVER.nervePillarDebuffsEnabled.get();
        boolean auraEnabled = buffsEnabled || debuffsEnabled;

        blockEntity.tickCounter++;
        if (blockEntity.tickCounter % AURA_INTERVAL_TICKS == 0 && auraEnabled) {
            int radius = CarnisConfig.SERVER.nervePillarAuraRadius.get();
            blockEntity.applyAura(level, pos, radius);
        }

        if (blockEntity.tickCounter % PARTICLE_INTERVAL_TICKS == 0 && auraEnabled) {
            spawnAuraParticles((ServerLevel) level, pos);
        }

        if (blockEntity.tickCounter >= AURA_INTERVAL_TICKS) {
            blockEntity.tickCounter = 0;
        }
    }

    private void applyAura(Level level, BlockPos pos, int radius) {
        boolean buffsEnabled = CarnisConfig.SERVER.nervePillarBuffsEnabled.get();
        boolean debuffsEnabled = CarnisConfig.SERVER.nervePillarDebuffsEnabled.get();
        Vec3 center = Vec3.atCenterOf(pos);
        double radiusSquared = (double) radius * radius;
        AABB area = AABB.ofSize(center, radius * 2.0D, radius * 2.0D, radius * 2.0D);

        for (LivingEntity entity : level.getEntitiesOfClass(LivingEntity.class, area,
                candidate -> candidate.isAlive() && !candidate.isSpectator()
                        && candidate.distanceToSqr(center) <= radiusSquared)) {
            boolean hiveAlly = NeuralMossBlock.isHive(entity)
                    || entity instanceof Mob mob && InfectionHandler.isInfected(mob);
            if (buffsEnabled && hiveAlly && !(entity instanceof Player)) {
                maintainEffect(entity, MobEffects.REGENERATION, 0);
            }

            if (debuffsEnabled && entity instanceof Player player
                    && !NeuralMossBlock.isHive(player)
                    && !PlayerInfectionApi.isAssimilated(player)
                    && !NeuroResonatorHelmetItem.isEquipped(player)) {
                maintainEffect(player, MobEffects.DIG_SLOWDOWN, 0);
            }
        }
    }

    private static void maintainEffect(LivingEntity entity, MobEffect effect, int amplifier) {
        MobEffectInstance existing = entity.getEffect(effect);
        if (existing == null || existing.getAmplifier() < amplifier
                || existing.getAmplifier() == amplifier
                && existing.getDuration() <= EFFECT_REFRESH_THRESHOLD_TICKS) {
            entity.addEffect(new MobEffectInstance(effect, EFFECT_DURATION_TICKS, amplifier, false, true));
        }
    }

    /** Spawns world-space spore particles on a spherical shell around the pillar. */
    private static void spawnAuraParticles(ServerLevel level, BlockPos pos) {
        int particleCount = 3 + level.random.nextInt(3);
        Vec3 center = Vec3.atCenterOf(pos);

        for (int i = 0; i < particleCount; i++) {
            double verticalDirection = level.random.nextDouble() * 2.0D - 1.0D;
            double angle = level.random.nextDouble() * Math.PI * 2.0D;
            double horizontalScale = Math.sqrt(1.0D - verticalDirection * verticalDirection);
            double sphereRadius = 0.5D + level.random.nextDouble();
            double x = center.x + sphereRadius * horizontalScale * Math.cos(angle);
            double y = center.y + sphereRadius * verticalDirection;
            double z = center.z + sphereRadius * horizontalScale * Math.sin(angle);
            level.sendParticles(ParticleTypes.CRIMSON_SPORE, x, y, z, 1,
                    0.0D, 0.0D, 0.0D, 0.002D);
        }
    }
}
```

## `src/main/java/com/carnis/mod/block/entity/PulsingHeartBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.HiveSentinelEntity;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import com.carnis.mod.world.infection.InfectionTickQueue;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import software.bernie.geckolib.animatable.GeoBlockEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

public final class PulsingHeartBlockEntity extends BlockEntity implements GeoBlockEntity {
    public static final int PULSE_INTERVAL_TICKS = 100;
    public static final int PULSE_RADIUS = 8;
    private static final RawAnimation PULSE_ANIMATION = RawAnimation.begin().thenLoop("animation.pulsing_heart.pulse");
    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private final Set<Long> infected = new HashSet<>();
    private final List<Long> generatedTissue = new ArrayList<>();
    private long biomass;
    private UUID sentinel;
    private boolean initialized;

    public PulsingHeartBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.PULSING_HEART.get(), pos, state); }
    public int getInfectedBlocksCount() { return infected.size(); }
    public void seedGeneratedTissue(List<BlockPos> positions) {
        for (BlockPos pos : positions) generatedTissue.add(pos.asLong());
        setChanged();
    }
    public long getBiomass() { return biomass; }
    public void addBiomass(long value) {
        if (value <= 0) return;
        biomass = biomass > Long.MAX_VALUE - value ? Long.MAX_VALUE : biomass + value;
        setChanged();
    }
    public void observeInfection(BlockPos pos, boolean present) {
        if (pos.distSqr(worldPosition) > 32D * 32D) return;
        if (present ? infected.add(pos.asLong()) : infected.remove(pos.asLong())) setChanged();
    }
    public void sentinelDied(UUID id) {
        if (id.equals(sentinel)) {
            if (level instanceof ServerLevel server) HiveNetwork.get(server).consumeSentinelDeath(id);
            sentinel = null; setChanged();
        }
    }
    @Override protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putLongArray("InfectedPositions", new ArrayList<>(infected));
        tag.putLongArray("GeneratedTissuePending", generatedTissue);
        tag.putInt("infected_blocks_count", infected.size());
        tag.putLong("ClusterBiomass", biomass);
        if (sentinel != null) tag.putUUID("Sentinel", sentinel);
    }
    @Override public void load(CompoundTag tag) {
        super.load(tag); infected.clear();
        for (long p : tag.getLongArray("InfectedPositions")) infected.add(p);
        generatedTissue.clear();
        for (long p : tag.getLongArray("GeneratedTissuePending")) generatedTissue.add(p);
        biomass = Math.max(0, tag.getLong("ClusterBiomass"));
        sentinel = tag.hasUUID("Sentinel") ? tag.getUUID("Sentinel") : null;
        initialized = false;
    }
    public static void serverTick(Level world, BlockPos pos, BlockState state, PulsingHeartBlockEntity heart) {
        if (!(world instanceof ServerLevel level)) return;
        if (!heart.initialized) {
            // Rebuild from the event-maintained index, never from a cube of world blocks.
            heart.infected.clear();
            for (BlockPos p : HiveNetwork.get(level).positions(HiveNetwork.Kind.INFECTION, pos, 32)) heart.infected.add(p.asLong());
            heart.initialized = true;
            heart.setChanged();
        }
        if (!heart.generatedTissue.isEmpty()) {
            int count = Math.min(64, heart.generatedTissue.size());
            List<BlockPos> batch = new ArrayList<>(count);
            for (int i = 0; i < count; i++) batch.add(BlockPos.of(heart.generatedTissue.get(i)));
            HiveNetwork.registerGenerated(level, pos, batch);
            heart.generatedTissue.subList(0, count).clear();
            heart.setChanged();
        }
        if (!InfectionTickQueue.refreshHeartChunk(level, pos)) return;
        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), PULSE_INTERVAL_TICKS), PULSE_INTERVAL_TICKS) == 0)
            heart.pulse(level);
    }
    private void pulse(ServerLevel level) {
        com.carnis.mod.event.AmalgamationHandler.onHighBiomassPulse(level, worldPosition);
        if (sentinel != null && HiveNetwork.get(level).consumeSentinelDeath(sentinel)) { sentinel = null; setChanged(); }
        if (sentinel == null) {
            var area = new net.minecraft.world.phys.AABB(worldPosition).inflate(32);
            for (HiveSentinelEntity guard : level.getEntitiesOfClass(HiveSentinelEntity.class, area,
                    e -> e.isAlive() && e.blockPosition().distSqr(worldPosition) <= 1024)) {
                sentinel = guard.getUUID(); guard.setHeartPos(worldPosition); setChanged(); break;
            }
        }
        int queued = 0;
        for (long packed : infected) {
            BlockPos p = BlockPos.of(packed);
            if (p.distSqr(worldPosition) <= PULSE_RADIUS * PULSE_RADIUS && level.hasChunkAt(p)
                    && InfectionTickQueue.isInfectionSource(level.getBlockState(p))) {
                InfectionTickQueue.enqueueHeartPulse(level, p);
                if (++queued >= 6) break;
            }
        }
        if (!level.getGameRules().getBoolean(net.minecraft.world.level.GameRules.RULE_MOBGRIEFING)) return;
        if (infected.size() >= 25 && !hasOrgan(level, HiveNetwork.Kind.EYE)) morphBlock(level, 0);
        else if (infected.size() >= 50 && sentinel == null) morphBlock(level, 1);
        else if (infected.size() >= 75 && !hasOrgan(level, HiveNetwork.Kind.POOL)) morphBlock(level, 2);
        else if (infected.size() >= 100 && !hasOrgan(level, HiveNetwork.Kind.PILLAR)) morphBlock(level, 3);
        else if (infected.size() >= 100 && sentinel != null && biomass >= 200
                && HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.EYE, worldPosition, 32) != null
                && HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.POOL, worldPosition, 32) != null
                && HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.PILLAR, worldPosition, 32) != null) metamorphose(level);
    }
    private boolean hasOrgan(ServerLevel level, HiveNetwork.Kind kind) {
        for (BlockPos p : HiveNetwork.get(level).positions(kind, worldPosition, 32)) {
            if (!level.hasChunkAt(p)) return true; // Unknown unloaded organ is not duplicated.
            BlockState state = level.getBlockState(p);
            if ((kind == HiveNetwork.Kind.EYE && state.is(ModBlocks.HIVE_EYE.get()))
                    || (kind == HiveNetwork.Kind.POOL && state.is(ModBlocks.STOMACH_POOL.get()))
                    || (kind == HiveNetwork.Kind.PILLAR && state.is(ModBlocks.NERVE_PILLAR.get()))) return true;
        }
        return false;
    }
    private BlockPos pickFlesh(ServerLevel level) {
        BlockPos selected = null; int seen = 0;
        for (long packed : infected) {
            BlockPos p = BlockPos.of(packed); double d = p.distSqr(worldPosition);
            if (d < 64 || d > 576 || !level.hasChunkAt(p) || !level.hasChunkAt(p.below()) || !level.hasChunkAt(p.above())) continue;
            if (!level.getBlockState(p).is(ModBlocks.LIVING_FLESH.get()) || !level.isEmptyBlock(p.above())
                    || !level.getBlockState(p.below()).isFaceSturdy(level, p.below(), Direction.UP)) continue;
            if (level.random.nextInt(++seen) == 0) selected = p;
        }
        return selected;
    }
    private void morphBlock(ServerLevel level, int organ) {
        BlockPos pos = pickFlesh(level);
        if (pos == null) return;
        if (organ == 1) {
            HiveSentinelEntity entity = ModEntities.HIVE_SENTINEL.get().create(level);
            if (entity == null) return;
            entity.moveTo(pos.getX() + .5, pos.getY(), pos.getZ() + .5, 0, 0);
            entity.setHeartPos(worldPosition); entity.setPersistenceRequired();
            BlockState old = level.getBlockState(pos);
            if (!level.removeBlock(pos, false)) return;
            if (!level.addFreshEntity(entity)) { level.setBlockAndUpdate(pos, old); return; }
            sentinel = entity.getUUID(); setChanged();
        } else {
            BlockState replacement = organ == 0 ? ModBlocks.HIVE_EYE.get().defaultBlockState()
                    : organ == 2 ? ModBlocks.STOMACH_POOL.get().defaultBlockState() : ModBlocks.NERVE_PILLAR.get().defaultBlockState();
            if (!level.setBlockAndUpdate(pos, replacement)) return;
        }
        level.playSound(null, pos, ModSounds.PULSING_HEART_BEAT.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
    }
    private void metamorphose(ServerLevel level) {
        Entity entity = level.getEntity(sentinel);
        if (!(entity instanceof HiveSentinelEntity guard) || !guard.isAlive()) return;
        List<BlockPos> satellites = new ArrayList<>();
        for (BlockPos p : HiveNetwork.get(level).positions(HiveNetwork.Kind.INFECTION, worldPosition, 64)) {
            double d = p.distSqr(worldPosition);
            if (d < 48D * 48D || !level.hasChunkAt(p) || !level.getBlockState(p).is(ModBlocks.LIVING_FLESH.get())) continue;
            if (!satellites.isEmpty() && p.distSqr(satellites.get(0)) < 32D * 32D) continue;
            satellites.add(p);
            if (satellites.size() == 2) break;
        }
        if (satellites.size() < 2) return; // No forced chunk loading or partial budding.
        CerebralNexusEntity nexus = ModEntities.CEREBRAL_NEXUS.get().create(level);
        if (nexus == null) return;
        nexus.moveTo(worldPosition.getX() + .5D, worldPosition.getY(), worldPosition.getZ() + .5D, 0, 0);
        nexus.setPersistenceRequired(); nexus.setBiomass(biomass - 200);
        BlockPos first = satellites.get(0), second = satellites.get(1);
        if (!level.setBlockAndUpdate(first, ModBlocks.PULSING_HEART.get().defaultBlockState())) return;
        if (!level.setBlockAndUpdate(second, ModBlocks.PULSING_HEART.get().defaultBlockState())) {
            level.setBlockAndUpdate(first, ModBlocks.LIVING_FLESH.get().defaultBlockState()); return;
        }
        if (!level.addFreshEntity(nexus)) {
            level.setBlockAndUpdate(first, ModBlocks.LIVING_FLESH.get().defaultBlockState());
            level.setBlockAndUpdate(second, ModBlocks.LIVING_FLESH.get().defaultBlockState()); return;
        }
        level.playSound(null, worldPosition, ModSounds.AMALGAM_ROAR.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), worldPosition.getX() + .5, worldPosition.getY() + .7,
                worldPosition.getZ() + .5, 80, .6, .7, .6, .15);
        level.removeBlock(worldPosition, false);
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "pulse_controller", 0, state -> state.setAndContinue(PULSE_ANIMATION)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return animationCache; }
}
```

## `src/main/java/com/carnis/mod/block/entity/PustuleClusterBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.block.PustuleClusterBlock;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import software.bernie.geckolib.animatable.GeoBlockEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class PustuleClusterBlockEntity extends BlockEntity implements GeoBlockEntity {
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.pustule_cluster.idle");
    private static final RawAnimation PULSE = RawAnimation.begin().thenLoop("animation.pustule_cluster.pulse");
    private static final RawAnimation EMPTY = RawAnimation.begin().thenPlayAndHold("animation.pustule_cluster.burst");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private int ambientTicks;
    private int ambientAge = -1;

    public PustuleClusterBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.PUSTULE_CLUSTER.get(), pos, state); }

    public static void serverTick(Level level, BlockPos pos, BlockState state, PustuleClusterBlockEntity entity) {
        if (!state.hasProperty(PustuleClusterBlock.AGE) || !state.hasProperty(PustuleClusterBlock.BURST)) return;
        int age = state.getValue(PustuleClusterBlock.AGE);
        if (state.getValue(PustuleClusterBlock.BURST) || age < 2) {
            entity.ambientTicks = 0;
            entity.ambientAge = -1;
            return;
        }
        if (entity.ambientAge != age) {
            entity.ambientAge = age;
            entity.ambientTicks = 0;
        }
        int interval = age == 2 ? 60 : 40;
        if (++entity.ambientTicks >= interval) {
            entity.ambientTicks = 0;
            float volume = age == 2 ? 0.4F : 0.5F;
            level.playSound(null, pos, SoundEvents.SLIME_BLOCK_STEP, SoundSource.BLOCKS, volume, 1.0F);
        }
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "pustules", 0, animation -> {
            BlockState state = getBlockState();
            if (!state.hasProperty(PustuleClusterBlock.BURST)) return animation.setAndContinue(IDLE);
            if (state.getValue(PustuleClusterBlock.BURST)) return animation.setAndContinue(EMPTY);
            return animation.setAndContinue(state.getValue(PustuleClusterBlock.AGE) == 3 ? PULSE : IDLE);
        }));
    }
}
```

## `src/main/java/com/carnis/mod/block/entity/SporeSproutBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.block.SporeSproutBlock;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public final class SporeSproutBlockEntity extends BlockEntity {
    private static final int MAX_COOLDOWN_TICKS = 350;
    private static final String COOLDOWN_TAG = "CooldownTicks";

    private int cooldownTicks;

    public SporeSproutBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.SPORE_SPROUT.get(), pos, state);
    }

    public int getCooldownTicks() {
        return cooldownTicks;
    }

    public void startCooldown(int ticks) {
        cooldownTicks = Math.max(0, Math.min(MAX_COOLDOWN_TICKS, ticks));
        setChanged();
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putInt(COOLDOWN_TAG, cooldownTicks);
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        cooldownTicks = Math.max(0, Math.min(MAX_COOLDOWN_TICKS, tag.getInt(COOLDOWN_TAG)));
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, SporeSproutBlockEntity sprout) {
        if (!(level instanceof ServerLevel)) return;

        if (sprout.cooldownTicks > 0) {
            sprout.cooldownTicks--;
            sprout.setChanged();
        }

        if (state.hasProperty(SporeSproutBlock.CLOSED)) {
            boolean shouldBeClosed = sprout.cooldownTicks > 0;
            if (state.getValue(SporeSproutBlock.CLOSED) != shouldBeClosed) {
                level.setBlock(pos, state.setValue(SporeSproutBlock.CLOSED, shouldBeClosed), 3);
            }
        }
    }
}
```

## `src/main/java/com/carnis/mod/block/entity/StomachPoolBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.network.protocol.Packet;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public final class StomachPoolBlockEntity extends BlockEntity {
    private static final int MAX_ATTRACTED = 8;
    private static final int RESERVATION_TTL_TICKS = 600;
    private static final double RESERVATION_EXPIRY_DISTANCE_SQUARED = 16.0D;
    private static final double MAX_RESERVATION_DISTANCE_SQUARED = 256.0D;

    private long activeUntil;
    // UUID -> game time at reservation; transient, as reservations only cover loaded mobs.
    private final Map<UUID, Long> attracted = new HashMap<>();
    // Separate digestion progress, so reservation timestamps remain stable for TTL expiry.
    private final Map<UUID, Integer> insideTicks = new HashMap<>();

    public StomachPoolBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.STOMACH_POOL.get(), pos, state);
    }

    private void pruneAttracted(ServerLevel server) {
        long now = server.getGameTime();
        attracted.entrySet().removeIf(entry -> {
            UUID id = entry.getKey();
            Entity entity = server.getEntity(id);
            if (!(entity instanceof Mob mob) || !mob.isAlive() || mob.isRemoved()
                    || NeuralMossBlock.isHive(mob)) {
                insideTicks.remove(id);
                return true;
            }

            double distanceSquared = mob.distanceToSqr(
                    worldPosition.getX() + 0.5D,
                    worldPosition.getY() + 0.5D,
                    worldPosition.getZ() + 0.5D);
            boolean timedOutBeforeArrival = now - entry.getValue() > RESERVATION_TTL_TICKS
                    && distanceSquared > RESERVATION_EXPIRY_DISTANCE_SQUARED;
            boolean outOfRange = distanceSquared > MAX_RESERVATION_DISTANCE_SQUARED;
            if (timedOutBeforeArrival || outOfRange) insideTicks.remove(id);
            return timedOutBeforeArrival || outOfRange;
        });
        insideTicks.keySet().removeIf(id -> !attracted.containsKey(id));
    }

    public boolean reserve(Mob mob) {
        if (!(level instanceof ServerLevel server) || isRemoved() || !mob.isAlive() || mob.level() != level
                || NeuralMossBlock.isHive(mob)) return false;
        pruneAttracted(server);
        UUID id = mob.getUUID();
        if (attracted.containsKey(id)) return true;
        if (attracted.size() >= MAX_ATTRACTED) return false;
        attracted.put(id, server.getGameTime());
        insideTicks.put(id, 0);
        return true;
    }

    public boolean hasReservation(Mob mob) {
        return !NeuralMossBlock.isHive(mob) && attracted.containsKey(mob.getUUID());
    }

    public void release(Mob mob) {
        UUID id = mob.getUUID();
        attracted.remove(id);
        insideTicks.remove(id);
    }

    /** Вызывается целью удержания один раз за серверный тик внутри бассейна. */
    public boolean countInsideTick(Mob mob) {
        UUID id = mob.getUUID();
        if (NeuralMossBlock.isHive(mob) || !mob.isAlive() || mob.isRemoved()) {
            release(mob);
            return false;
        }
        if (!attracted.containsKey(id)) return false;

        int ticks = insideTicks.getOrDefault(id, 0) + 1;
        if (ticks >= 200) {
            release(mob);
            // Go through the normal damage/death pipeline so death events and loot can run.
            mob.hurt(mob.damageSources().generic(), Float.MAX_VALUE);
            if (mob.isAlive()) mob.kill();
            if (mob.isAlive()) mob.discard();
            return true;
        }
        insideTicks.put(id, ticks);
        return false;
    }

    public boolean isDigesting() {
        return level != null && level.getGameTime() < activeUntil;
    }

    public void markDigesting() {
        if (!(level instanceof ServerLevel server)) return;
        if (activeUntil - server.getGameTime() > 20) return;
        activeUntil = server.getGameTime() + 40;
        setChanged();
        server.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
    }

    public static void tick(Level level, BlockPos pos, BlockState state, StomachPoolBlockEntity pool) {
        if (!level.isClientSide) return;
        boolean active = pool.isDigesting();
        if (level.random.nextInt(active ? 3 : 20) != 0) return;
        double x = pos.getX() + .18 + level.random.nextDouble() * .64;
        double z = pos.getZ() + .18 + level.random.nextDouble() * .64;
        level.addParticle(active && level.random.nextBoolean()
                        ? ModParticles.BIOMASS_SPARK.get() : ParticleTypes.BUBBLE_POP,
                x, pos.getY() + .66, z, 0, .025, 0);
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putLong("ActiveUntil", activeUntil);
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        activeUntil = tag.getLong("ActiveUntil");
    }

    @Override
    public CompoundTag getUpdateTag() {
        return saveWithoutMetadata();
    }

    @Nullable
    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    @Override
    public void onDataPacket(Connection connection, ClientboundBlockEntityDataPacket packet) {
        CompoundTag tag = packet.getTag();
        if (tag != null) load(tag);
    }
}
```

## `src/main/java/com/carnis/mod/capability/biomass/PlayerBiomassCapability.java`

```java
package com.carnis.mod.capability.biomass;

import com.carnis.mod.CarnisMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.CapabilityManager;
import net.minecraftforge.common.capabilities.CapabilityToken;
import net.minecraftforge.common.capabilities.RegisterCapabilitiesEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class PlayerBiomassCapability {
    public static final ResourceLocation ID = new ResourceLocation(CarnisMod.MOD_ID, "player_biomass");
    public static final Capability<PlayerBiomassData> PLAYER_BIOMASS =
            CapabilityManager.get(new CapabilityToken<>() { });

    private PlayerBiomassCapability() { }

    @SubscribeEvent
    public static void register(RegisterCapabilitiesEvent event) {
        event.register(PlayerBiomassData.class);
    }
}
```

## `src/main/java/com/carnis/mod/capability/biomass/PlayerBiomassData.java`

```java
package com.carnis.mod.capability.biomass;

import net.minecraft.nbt.CompoundTag;

/** Персональные очки биомассы без привязки к игроку или миру. */
public final class PlayerBiomassData {
    private static final String BIOMASS_POINTS = "BiomassPoints";
    private long biomassPoints = 0L;

    public long getBiomassPoints() {
        return biomassPoints;
    }

    public void setBiomassPoints(long amount) {
        if (amount < 0L) {
            throw new IllegalArgumentException("amount must not be negative");
        }
        biomassPoints = amount;
    }

    public void addBiomassPoints(long amount) {
        if (amount < 0L) {
            throw new IllegalArgumentException("amount must not be negative");
        }
        biomassPoints = amount > Long.MAX_VALUE - biomassPoints
                ? Long.MAX_VALUE : biomassPoints + amount;
    }

    public CompoundTag serializeNBT() {
        CompoundTag tag = new CompoundTag();
        tag.putLong(BIOMASS_POINTS, biomassPoints);
        return tag;
    }

    public void deserializeNBT(CompoundTag nbt) {
        biomassPoints = Math.max(0L, nbt.getLong(BIOMASS_POINTS));
    }
}
```

## `src/main/java/com/carnis/mod/capability/biomass/PlayerBiomassEvents.java`

```java
package com.carnis.mod.capability.biomass;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.network.packet.SyncPlayerBiomassPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.event.AttachCapabilitiesEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Прикрепление и перенос персональной биомассы на сервере. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerBiomassEvents {
    private PlayerBiomassEvents() { }

    @SubscribeEvent
    public static void attach(AttachCapabilitiesEvent<Entity> event) {
        if (!(event.getObject() instanceof ServerPlayer)) return;
        PlayerBiomassProvider provider = new PlayerBiomassProvider();
        event.addCapability(PlayerBiomassCapability.ID, provider);
        event.addListener(provider::invalidateCaps);
    }

    /** Отправляется после изменений через серверные операции следующих шагов. */
    public static void syncToPlayer(ServerPlayer player) {
        player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS).ifPresent(data ->
                ModMessages.sendToPlayer(new SyncPlayerBiomassPacket(data.getBiomassPoints()), player));
    }

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) syncToPlayer(player);
    }

    @SubscribeEvent
    public static void onDimensionChange(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) syncToPlayer(player);
    }

    @SubscribeEvent
    public static void onPlayerRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) syncToPlayer(player);
    }

    @SubscribeEvent
    public static void clonePlayer(PlayerEvent.Clone event) {
        if (!(event.getEntity() instanceof ServerPlayer)
                || !(event.getOriginal() instanceof ServerPlayer)) return;
        event.getOriginal().reviveCaps();
        try {
            event.getOriginal().getCapability(PlayerBiomassCapability.PLAYER_BIOMASS).ifPresent(oldData ->
                    event.getEntity().getCapability(PlayerBiomassCapability.PLAYER_BIOMASS).ifPresent(newData ->
                            newData.deserializeNBT(oldData.serializeNBT())));
        } finally {
            event.getOriginal().invalidateCaps();
        }
    }
}
```

## `src/main/java/com/carnis/mod/capability/biomass/PlayerBiomassProvider.java`

```java
package com.carnis.mod.capability.biomass;

import javax.annotation.Nullable;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ICapabilitySerializable;
import net.minecraftforge.common.util.LazyOptional;

/** Владеет одним экземпляром данных на время жизни прикрепления. */
public final class PlayerBiomassProvider implements ICapabilitySerializable<CompoundTag> {
    private final PlayerBiomassData instance = new PlayerBiomassData();
    private LazyOptional<PlayerBiomassData> holder = LazyOptional.of(() -> instance);

    @Override
    public <T> LazyOptional<T> getCapability(Capability<T> capability, @Nullable Direction side) {
        if (capability == PlayerBiomassCapability.PLAYER_BIOMASS) {
            // После reviveCaps прежний LazyOptional может быть инвалидирован.
            if (!holder.isPresent()) holder = LazyOptional.of(() -> instance);
            return holder.cast();
        }
        return LazyOptional.empty();
    }

    @Override
    public CompoundTag serializeNBT() {
        return instance.serializeNBT();
    }

    @Override
    public void deserializeNBT(CompoundTag nbt) {
        instance.deserializeNBT(nbt);
    }

    public void invalidateCaps() {
        holder.invalidate();
    }
}
```

## `src/main/java/com/carnis/mod/capability/infection/IPlayerInfection.java`

```java
package com.carnis.mod.capability.infection;

/**
 * Mutable player infection state expressed as a percentage.
 */
public interface IPlayerInfection {
    float MIN_INFECTION = 0.0F;
    float MAX_INFECTION = 100.0F;

    float getInfectionLevel();

    /**
     * Sets the infection percentage after clamping it to the valid range.
     *
     * @return true only when the stored value actually changed
     */
    boolean setInfectionLevel(float infectionLevel);

    /**
     * Adds a signed amount to the infection percentage.
     *
     * @return true only when the stored value actually changed
     */
    boolean addInfection(float amount);

    default boolean isAssimilated() {
        return getInfectionLevel() >= MAX_INFECTION;
    }
}
```

## `src/main/java/com/carnis/mod/capability/infection/PlayerInfection.java`

```java
package com.carnis.mod.capability.infection;

import java.util.Objects;

/**
 * Clamped data implementation for the player infection capability.
 */
public final class PlayerInfection implements IPlayerInfection {
    private static final Runnable NO_CHANGE_LISTENER = () -> {
    };

    private final Runnable changeListener;
    private float infectionLevel;

    public PlayerInfection() {
        this(NO_CHANGE_LISTENER);
    }

    public PlayerInfection(Runnable changeListener) {
        this.changeListener = Objects.requireNonNull(
                changeListener,
                "changeListener"
        );
    }

    @Override
    public float getInfectionLevel() {
        return infectionLevel;
    }

    @Override
    public boolean setInfectionLevel(float infectionLevel) {
        float sanitizedLevel = sanitize(infectionLevel);

        if (Float.compare(this.infectionLevel, sanitizedLevel) == 0) {
            return false;
        }

        this.infectionLevel = sanitizedLevel;
        changeListener.run();
        return true;
    }

    @Override
    public boolean addInfection(float amount) {
        if (Float.isNaN(amount) || amount == 0.0F) {
            return false;
        }

        return setInfectionLevel(infectionLevel + amount);
    }

    static float sanitize(float infectionLevel) {
        if (Float.isNaN(infectionLevel)) {
            return MIN_INFECTION;
        }

        return Math.max(
                MIN_INFECTION,
                Math.min(MAX_INFECTION, infectionLevel)
        );
    }

    public void setInfectionLevelSilently(float infectionLevel) {
        this.infectionLevel = sanitize(infectionLevel);
    }
}
```

## `src/main/java/com/carnis/mod/capability/infection/PlayerInfectionApi.java`

```java
package com.carnis.mod.capability.infection;

import com.carnis.mod.infection.PlayerInfectionManager;
import com.carnis.mod.item.NeuroWeave;
import net.minecraft.world.entity.player.Player;

/** Compatibility facade. Persistent player data is the authoritative store. */
public final class PlayerInfectionApi {
    private PlayerInfectionApi() { }
    public static float getInfectionLevel(Player player) { return PlayerInfectionManager.getPoints(player); }
    public static boolean setInfectionLevel(Player player, float value) {
        if (value > getInfectionLevel(player) && player.hasEffect(com.carnis.mod.init.ModEffects.IMMUNOSUPPRESSION.get())) return false;
        return PlayerInfectionManager.setPoints(player, value);
    }
    public static boolean addInfection(Player player, float amount) {
        if (Float.isNaN(amount) || amount == 0) return false;
        return setInfectionLevel(player, getInfectionLevel(player) + amount);
    }
    public static boolean addExposure(Player player, float amount) {
        if (amount > 0 && player.hasEffect(com.carnis.mod.init.ModEffects.IMMUNOSUPPRESSION.get())) return false;
        return addInfection(player, amount > 0 ? amount * NeuroWeave.infectionMultiplier(player) : amount);
    }
    /** A living carrier has not yet been assimilated into a clone. */
    public static boolean isAssimilated(Player player) {
        return player.getPersistentData().getBoolean(PlayerInfectionManager.METAMORPHOSED);
    }
    public static boolean isHostileTarget(Player player) {
        return player.isAlive() && !player.isSpectator() && !player.isCreative();
    }
    public static void copy(Player source, Player target) {
        PlayerInfectionManager.copyToClone(source, target, false);
    }
}
```

## `src/main/java/com/carnis/mod/capability/infection/PlayerInfectionCapability.java`

```java
package com.carnis.mod.capability.infection;

import com.carnis.mod.CarnisMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.CapabilityManager;
import net.minecraftforge.common.capabilities.CapabilityToken;
import net.minecraftforge.common.capabilities.RegisterCapabilitiesEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.MOD
)
public final class PlayerInfectionCapability {
    public static final ResourceLocation ID = new ResourceLocation(
            CarnisMod.MOD_ID,
            "player_infection"
    );

    public static final Capability<IPlayerInfection> PLAYER_INFECTION =
            CapabilityManager.get(new CapabilityToken<>() {
            });

    private PlayerInfectionCapability() {
    }

    @SubscribeEvent
    public static void registerCapabilities(RegisterCapabilitiesEvent event) {
        event.register(IPlayerInfection.class);
    }
}
```

## `src/main/java/com/carnis/mod/capability/infection/PlayerInfectionProvider.java`

```java
package com.carnis.mod.capability.infection;

import com.carnis.mod.network.ModMessages;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ICapabilitySerializable;
import net.minecraftforge.common.util.LazyOptional;

import java.util.Objects;

public final class PlayerInfectionProvider
        implements ICapabilitySerializable<CompoundTag> {
    private static final String INFECTION_LEVEL_TAG = "infection_level";

    private final PlayerInfection infection;
    private final LazyOptional<IPlayerInfection> holder;

    public PlayerInfectionProvider(Player owner) {
        Objects.requireNonNull(owner, "owner");

        infection = new PlayerInfection(() -> onLegacyChange(owner));
        holder = LazyOptional.of(() -> infection);
    }

    private void onLegacyChange(Player owner) {
        if (!owner.level().isClientSide)
            com.carnis.mod.infection.PlayerInfectionManager.setPoints(owner, infection.getInfectionLevel());
    }

    @Override
    public <T> LazyOptional<T> getCapability(
            Capability<T> capability,
            Direction side
    ) {
        if (capability == PlayerInfectionCapability.PLAYER_INFECTION) {
            return holder.cast();
        }

        return LazyOptional.empty();
    }

    @Override
    public CompoundTag serializeNBT() {
        return serializeInfection(infection);
    }

    @Override
    public void deserializeNBT(CompoundTag tag) {
        deserializeInfection(infection, tag);
    }

    public static CompoundTag serializeInfection(IPlayerInfection infection) {
        CompoundTag tag = new CompoundTag();
        tag.putFloat(INFECTION_LEVEL_TAG, infection.getInfectionLevel());
        return tag;
    }

    public static void deserializeInfection(IPlayerInfection infection, CompoundTag tag) {
        float level = tag.getFloat(INFECTION_LEVEL_TAG);
        if (infection instanceof PlayerInfection data) {
            data.setInfectionLevelSilently(level);
        } else {
            infection.setInfectionLevel(level);
        }
    }

    public void invalidate() {
        holder.invalidate();
    }
}
```

## `src/main/java/com/carnis/mod/client/BioPurifierAnimationState.java`

```java
package com.carnis.mod.client;
import com.carnis.mod.item.BioPurifierItem;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animation.AnimationState;

/** Render-side state only; item renderers do not receive an owning entity in GeckoLib 4. */
public final class BioPurifierAnimationState {
    private BioPurifierAnimationState() { }
    public static boolean isFiring(AnimationState<BioPurifierItem> state) {
        ItemDisplayContext context = state.getData(DataTickets.ITEM_RENDER_PERSPECTIVE);
        if (context != ItemDisplayContext.FIRST_PERSON_LEFT_HAND && context != ItemDisplayContext.FIRST_PERSON_RIGHT_HAND
                && context != ItemDisplayContext.THIRD_PERSON_LEFT_HAND && context != ItemDisplayContext.THIRD_PERSON_RIGHT_HAND) return false;
        ItemStack stack = state.getData(DataTickets.ITEMSTACK);
        var level = Minecraft.getInstance().level;
        if (stack == null || level == null) return false;
        for (Player player : level.players()) {
            if (player.isUsingItem() && player.getUseItem() == stack) return true;
        }
        return false;
    }
}
```

## `src/main/java/com/carnis/mod/client/CarnisTooltipEvents.java`

```java
package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@OnlyIn(Dist.CLIENT)
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisTooltipEvents {
    private CarnisTooltipEvents() {
    }

    @SubscribeEvent
    public static void onTooltip(ItemTooltipEvent event) {
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(event.getItemStack().getItem());
        if (id == null || !CarnisMod.MOD_ID.equals(id.getNamespace())) {
            return;
        }
        if (Screen.hasShiftDown()) {
            event.getToolTip().add(Component.translatable("tooltip.carnis." + id.getPath())
                    .withStyle(ChatFormatting.DARK_RED));
        } else {
            event.getToolTip().add(Component.translatable("tooltip.carnis.hold_shift")
                    .withStyle(ChatFormatting.GRAY));
        }
    }
}
```

## `src/main/java/com/carnis/mod/client/ClientLayerEvents.java`

```java
package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.renderer.layer.IncubatingEntityLayer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ClientLayerEvents {
    private ClientLayerEvents() {
    }

    @SubscribeEvent
    public static void onAddLayers(EntityRenderersEvent.AddLayers event) {
        for (String skin : event.getSkins()) {
            LivingEntityRenderer<AbstractClientPlayer, PlayerModel<AbstractClientPlayer>> renderer = event.getSkin(skin);
            if (renderer != null) {
                renderer.addLayer(new IncubatingEntityLayer<>(renderer));
            }
        }

        addLayerTo(event, EntityType.ZOMBIE);
        addLayerTo(event, EntityType.SKELETON);
        addLayerTo(event, EntityType.HUSK);
        addLayerTo(event, EntityType.DROWNED);
        addLayerTo(event, EntityType.STRAY);
        addLayerTo(event, EntityType.WITHER_SKELETON);
        addLayerTo(event, EntityType.VILLAGER);
        addLayerTo(event, EntityType.WANDERING_TRADER);
        addLayerTo(event, EntityType.PIGLIN);
        addLayerTo(event, EntityType.PIGLIN_BRUTE);
        addLayerTo(event, EntityType.ZOMBIFIED_PIGLIN);
        addLayerTo(event, EntityType.PIG);
        addLayerTo(event, EntityType.COW);
        addLayerTo(event, EntityType.SHEEP);
        addLayerTo(event, EntityType.CHICKEN);
        addLayerTo(event, EntityType.SPIDER);
        addLayerTo(event, EntityType.HORSE);
        addLayerTo(event, EntityType.CREEPER);
        addLayerTo(event, EntityType.IRON_GOLEM);

        // Эти идентификаторы соответствуют ванильным живым носителям Minecraft 1.20.1.
        for (String id : new String[]{"goat", "llama", "trader_llama", "donkey", "mule",
                "skeleton_horse", "zombie_horse", "fox", "wolf", "cat", "ocelot", "parrot",
                "panda", "polar_bear", "turtle", "frog", "camel", "sniffer", "strider",
                "mooshroom", "rabbit", "bee", "hoglin", "tadpole", "cod", "salmon",
                "pufferfish", "tropical_fish", "squid", "glow_squid", "dolphin", "axolotl", "cave_spider"}) {
            addVanillaLivingLayer(event, id);
        }
    }

    @SuppressWarnings("unchecked")
    private static void addVanillaLivingLayer(EntityRenderersEvent.AddLayers event, String path) {
        EntityType<?> type = net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES
                .getValue(new net.minecraft.resources.ResourceLocation("minecraft", path));
        if (type != null) addLayerTo(event, (EntityType<? extends LivingEntity>) type);
    }

    private static <T extends LivingEntity, M extends EntityModel<T>> void addLayerTo(
            EntityRenderersEvent.AddLayers event,
            EntityType<T> entityType
    ) {
        LivingEntityRenderer<T, M> renderer = event.getRenderer(entityType);
        if (renderer != null) {
            renderer.addLayer(new IncubatingEntityLayer<>(renderer));
        }
    }
}
```

## `src/main/java/com/carnis/mod/client/ClientModEvents.java`

```java
package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.gui.InfectionVeinsOverlay;
import com.carnis.mod.client.gui.PhantomEyesOverlay;
import com.carnis.mod.client.hud.BiomassHudOverlay;
import com.carnis.mod.client.renderer.FleshAmalgamRenderer;
import com.carnis.mod.client.renderer.DartRenderer;
import com.carnis.mod.client.renderer.PulsingHeartRenderer;
import com.carnis.mod.client.renderer.HiveEyeRenderer;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModEntities;
import net.minecraft.client.renderer.entity.ZombieRenderer;
import net.minecraft.client.renderer.entity.SkeletonRenderer;
import net.minecraft.client.renderer.entity.CreeperRenderer;
import net.minecraft.client.renderer.entity.SpiderRenderer;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.MOD,
        value = Dist.CLIENT
)
public final class ClientModEvents {
    private ClientModEvents() {
    }

    @SubscribeEvent
    public static void onRegisterRenderers(
            EntityRenderersEvent.RegisterRenderers event
    ) {
        event.registerEntityRenderer(ModEntities.HIVE_SENTINEL.get(), com.carnis.mod.client.renderer.HiveSentinelRenderer::new);
        event.registerEntityRenderer(ModEntities.CEREBRAL_NEXUS.get(), com.carnis.mod.client.renderer.CerebralNexusRenderer::new);
        event.registerEntityRenderer(ModEntities.BIOMASS_MAGGOT.get(), com.carnis.mod.client.renderer.BiomassMaggotRenderer::new);
        event.registerEntityRenderer(ModEntities.PARASITIC_TENDRIL.get(), com.carnis.mod.client.renderer.ParasiticTendrilRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_ZOMBIE.get(), com.carnis.mod.client.renderer.InfectedZombieRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_SKELETON.get(), com.carnis.mod.client.renderer.InfectedSkeletonRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_CREEPER.get(), com.carnis.mod.client.renderer.InfectedCreeperRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_SPIDER.get(), com.carnis.mod.client.renderer.InfectedSpiderRenderer::new);

        event.registerEntityRenderer(ModEntities.FLESH_SPAT.get(), net.minecraft.client.renderer.entity.ThrownItemRenderer::new);
        event.registerEntityRenderer(ModEntities.AMALGAM_BILE.get(), net.minecraft.client.renderer.entity.ThrownItemRenderer::new);
        event.registerEntityRenderer(ModEntities.HIVE_SPORE_CLOUD.get(), net.minecraft.client.renderer.entity.NoopRenderer::new);
        event.registerEntityRenderer(ModEntities.INOCULATOR_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.VIRAL_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.PURIFICATION_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.PUSTULE_GRENADE.get(), net.minecraft.client.renderer.entity.ThrownItemRenderer::new);
        event.registerBlockEntityRenderer(
                ModBlockEntities.PULSING_HEART.get(),
                PulsingHeartRenderer::new
        );
        event.registerBlockEntityRenderer(ModBlockEntities.HIVE_EYE.get(), HiveEyeRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.STOMACH_POOL.get(), com.carnis.mod.client.renderer.StomachPoolRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.NERVE_PILLAR.get(), com.carnis.mod.client.renderer.NervePillarRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.PUSTULE_CLUSTER.get(), com.carnis.mod.client.renderer.PustuleClusterRenderer::new);
        event.registerEntityRenderer(
                ModEntities.FLESH_AMALGAM.get(),
                FleshAmalgamRenderer::new
        );
    }

    @SubscribeEvent
    public static void onRegisterParticles(net.minecraftforge.client.event.RegisterParticleProvidersEvent event) {
        event.registerSpriteSet(com.carnis.mod.init.ModParticles.BIOMASS_SPARK.get(),
                com.carnis.mod.client.particle.BiomassSparkParticle.Provider::new);
        event.registerSpriteSet(com.carnis.mod.init.ModParticles.PURIFIER_FLAME.get(),
                com.carnis.mod.client.particle.BiomassSparkParticle.Provider::new);
    }

    @SubscribeEvent
    public static void onClientSetup(net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            net.minecraft.client.renderer.ItemBlockRenderTypes.setRenderLayer(
                    com.carnis.mod.init.ModFluids.SLUDGE_SOURCE.get(), net.minecraft.client.renderer.RenderType.translucent());
            net.minecraft.client.renderer.ItemBlockRenderTypes.setRenderLayer(
                    com.carnis.mod.init.ModFluids.SLUDGE_FLOWING.get(), net.minecraft.client.renderer.RenderType.translucent());
        });
    }

    @SubscribeEvent
    public static void onRegisterGuiOverlays(
            RegisterGuiOverlaysEvent event
    ) {
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "veins_overlay", new InfectionVeinsOverlay());
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "phantom_eyes", new PhantomEyesOverlay());
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "neuro_resonance", new com.carnis.mod.client.gui.overlay.NeuroResonanceOverlay());
        event.registerAboveAll("biomass_counter", new BiomassHudOverlay());
    }
}
```

## `src/main/java/com/carnis/mod/client/HeartAmbientTicker.java`

```java
package com.carnis.mod.client;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.init.ModSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

public final class HeartAmbientTicker {
    private HeartAmbientTicker() { }

    public static void tick(Level level, BlockPos pos, BlockState state, PulsingHeartBlockEntity heart) {
        var player = Minecraft.getInstance().player;
        if (player == null) return;
        double distance = player.position().distanceTo(Vec3.atCenterOf(pos));
        if (distance >= 16.0D) return;
        float proximity = (float) (1.0D - distance / 16.0D);
        int interval = 30 - Math.round(proximity * 12.0F);
        if (Math.floorMod(level.getGameTime() + pos.asLong(), interval) != 0) return;
        level.playLocalSound(pos.getX() + 0.5D, pos.getY() + 0.5D, pos.getZ() + 0.5D,
                ModSounds.HEARTBEAT_LOOP.get(), SoundSource.BLOCKS, 0.2F + proximity * 0.8F,
                1.0F, false);
    }
}
```

## `src/main/java/com/carnis/mod/client/PlayerHallucinationHandler.java`

```java
package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientInfectionData;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Presentation only: camera changes do not alter server-side aim or motion. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerHallucinationHandler {
    private static int soundDelay;
    private static int whisperDelay = -1;
    private static int spasm;
    private static int agonyTicks;
    private PlayerHallucinationHandler() { }
    @SubscribeEvent public static void onTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        int stage = ClientInfectionData.stage();
        if (mc.level == null || player == null || !player.isAlive() || player.isSpectator() || stage == 0) {
            soundDelay = 0; whisperDelay = -1; spasm = 0; agonyTicks = 0; return;
        }
        if (ClientInfectionData.points() >= 100) {
            if (agonyTicks == 0) soundDelay = 0;
            agonyTicks = Math.min(100, agonyTicks + 1);
        } else agonyTicks = 0;
        if (spasm > 0) spasm--;
        if (NeuroResonatorHelmetItem.isEquipped(player)) { soundDelay = 0; whisperDelay = -1; spasm = 0; return; }
        if (stage >= 3 && player.getRandom().nextInt(180) == 0) spasm = 8;
        if (!CarnisConfig.CLIENT.hallucinationSoundsEnabled.get()) { whisperDelay = -1; return; }
        tickWhisper(mc, player);
        if (soundDelay > 0) { soundDelay--; return; }
        float volume = CarnisConfig.CLIENT.hallucinationSoundVolume.get().floatValue();
        volume *= com.carnis.mod.item.NeuroWeave.infectionMultiplier(player);
        if (volume > 0) {
            SoundEvent sound;
            Vec3 pos;
            if (agonyTicks > 0) {
                sound = agonyTicks == 1 ? ModSounds.AMALGAM_ROAR.get() : ModSounds.HEARTBEAT_LOOP.get();
                pos = player.position().add(0, 1, 0);
                volume *= .4F + .6F * agonyTicks / 100.0F;
                soundDelay = Math.max(8, 24 - agonyTicks / 7);
            } else {
                boolean whisper = stage == 1 || player.getRandom().nextBoolean();
                sound = whisper ? null : ModSounds.PHANTOM_FOOTSTEPS.get();
                if (stage == 1 && player.getRandom().nextBoolean()) sound = ModSounds.HEARTBEAT_LOOP.get();
                Vec3 behind = player.getLookAngle().multiply(1, 0, 1).normalize().scale(-2.5D);
                pos = player.position().add(behind).add(0, .6D, 0);
                soundDelay = stage == 1 ? 400 + player.getRandom().nextInt(601)
                        : 200 + player.getRandom().nextInt(501);
            }
            if (sound != null) mc.level.playLocalSound(pos.x, pos.y, pos.z, sound, SoundSource.AMBIENT, volume, 1.0F, false);
        } else soundDelay = 200;
    }

    private static void tickWhisper(Minecraft mc, LocalPlayer player) {
        float infection = Mth.clamp((float) ClientInfectionData.points(), 0.0F, 100.0F);
        float protection = com.carnis.mod.item.NeuroWeave.infectionMultiplier(player);
        float configuredVolume = CarnisConfig.CLIENT.hallucinationSoundVolume.get().floatValue();
        if (infection <= 10.0F || protection <= 0.0F || configuredVolume <= 0.0F) {
            whisperDelay = -1;
            return;
        }
        if (whisperDelay < 0) {
            whisperDelay = nextWhisperDelay(infection, player.getRandom());
            return;
        }
        if (--whisperDelay > 0) return;

        float volume = whisperVolume(infection) * configuredVolume * protection;
        Vec3 behind = player.getLookAngle().multiply(1, 0, 1).normalize().scale(-2.5D);
        Vec3 pos = player.position().add(behind).add(0, .6D, 0);
        mc.level.playLocalSound(pos.x, pos.y, pos.z, ModSounds.PHANTOM_WHISPER.get(),
                SoundSource.AMBIENT, volume, 1.0F, false);
        whisperDelay = nextWhisperDelay(infection, player.getRandom());
    }

    private static float whisperVolume(float infection) {
        if (infection <= 10.0F) return 0.0F;
        if (infection <= 25.0F) return Mth.lerp((infection - 10.0F) / 15.0F, 0.1F, 0.3F);
        if (infection <= 50.0F) return Mth.lerp((infection - 25.0F) / 25.0F, 0.3F, 0.6F);
        if (infection <= 75.0F) return Mth.lerp((infection - 50.0F) / 25.0F, 0.6F, 0.85F);
        return Mth.lerp((infection - 75.0F) / 25.0F, 0.85F, 1.0F);
    }

    private static int nextWhisperDelay(float infection, RandomSource random) {
        float lower;
        float upper;
        if (infection <= 25.0F) {
            float t = (infection - 10.0F) / 15.0F;
            lower = Mth.lerp(t, 400.0F, 300.0F);
            upper = Mth.lerp(t, 1000.0F, 800.0F);
        } else if (infection <= 50.0F) {
            float t = (infection - 25.0F) / 25.0F;
            lower = Mth.lerp(t, 300.0F, 200.0F);
            upper = Mth.lerp(t, 800.0F, 600.0F);
        } else if (infection <= 75.0F) {
            float t = (infection - 50.0F) / 25.0F;
            lower = Mth.lerp(t, 200.0F, 150.0F);
            upper = Mth.lerp(t, 600.0F, 400.0F);
        } else {
            float t = (infection - 75.0F) / 25.0F;
            lower = Mth.lerp(t, 150.0F, 100.0F);
            upper = Mth.lerp(t, 400.0F, 250.0F);
        }
        int min = Math.round(lower);
        int max = Math.round(upper);
        return random.nextIntBetweenInclusive(min, max);
    }

    @SubscribeEvent public static void onCamera(ViewportEvent.ComputeCameraAngles event) {
        LocalPlayer player = Minecraft.getInstance().player;
        if (player == null || !player.isAlive() || player.isSpectator() || event.getCamera().getEntity() != player
                || NeuroResonatorHelmetItem.isEquipped(player) || ClientInfectionData.stage() < 3) return;
        double t = player.tickCount + event.getPartialTick();
        float strength = spasm > 0 ? .8F * spasm / 8.0F : 0;
        if (agonyTicks > 0) strength += .35F * agonyTicks / 100.0F;
        event.setYaw(event.getYaw() + (float) Math.sin(t * 2.4D) * strength);
        event.setPitch(event.getPitch() + (float) Math.cos(t * 1.7D) * strength * .7F);
        event.setRoll(event.getRoll() + (float) Math.sin(t * 1.2D) * strength * .6F);
    }
}
```

## `src/main/java/com/carnis/mod/client/data/ClientCarnisWorldData.java`

```java
package com.carnis.mod.client.data;

import com.carnis.mod.network.packet.SyncCarnisWorldDataPacket;
import com.carnis.mod.world.CarnisWorldData.AdaptationType;

import java.util.Objects;

public final class ClientCarnisWorldData {
    private static volatile Snapshot snapshot = Snapshot.EMPTY;

    private ClientCarnisWorldData() {
    }

    public static void apply(SyncCarnisWorldDataPacket packet) {
        Objects.requireNonNull(packet, "packet");

        snapshot = new Snapshot(
                packet.biomassPoints(),
                packet.fireAdaptation(),
                packet.rangedAdaptation(),
                packet.meleeAdaptation(),
                packet.pillaringAdaptation(),
                packet.explosiveAdaptation(),
                packet.darkAdaptation()
        );
    }

    public static Snapshot getSnapshot() {
        return snapshot;
    }

    public static long getBiomassPoints() {
        return snapshot.biomassPoints();
    }

    public static long getAdaptation(AdaptationType type) {
        Objects.requireNonNull(type, "type");

        return switch (type) {
            case FIRE -> snapshot.fireAdaptation();
            case RANGED -> snapshot.rangedAdaptation();
            case MELEE -> snapshot.meleeAdaptation();
            case PILLARING -> snapshot.pillaringAdaptation();
            case EXPLOSIVE -> snapshot.explosiveAdaptation();
            case DARK -> snapshot.darkAdaptation();
        };
    }

    public static void reset() {
        snapshot = Snapshot.EMPTY;
    }

    public record Snapshot(
            long biomassPoints,
            long fireAdaptation,
            long rangedAdaptation,
            long meleeAdaptation,
            long pillaringAdaptation,
            long explosiveAdaptation,
            long darkAdaptation
    ) {
        private static final Snapshot EMPTY = new Snapshot(
                0L,
                0L,
                0L,
                0L,
                0L,
                0L,
                0L
        );
    }
}
```

## `src/main/java/com/carnis/mod/client/data/ClientInfectionData.java`

```java
package com.carnis.mod.client.data;

import com.carnis.mod.network.SyncPlayerInfectionPacket;
import net.minecraft.client.Minecraft;

/** Client-side presentation snapshot, replaced only by server packets. */
public final class ClientInfectionData {
    private static int points;
    private static int stage;
    private ClientInfectionData() { }
    public static void apply(SyncPlayerInfectionPacket packet) {
        points = packet.infectionPoints();
        stage = packet.stage();
        var player = Minecraft.getInstance().player;
        if (player != null) {
            player.getPersistentData().putInt("carnis:infection_points", points);
            player.getPersistentData().putFloat("carnis:infection_fraction", 0.0F);
        }
    }
    public static int points() { return points; }
    public static int stage() { return stage; }
    public static void reset() { points = 0; stage = 0; }
}
```

## `src/main/java/com/carnis/mod/client/data/ClientPlayerBiomassData.java`

```java
package com.carnis.mod.client.data;

import com.carnis.mod.CarnisMod;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Клиентская копия персонального счётчика; мировая биомасса хранится отдельно. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ClientPlayerBiomassData {
    private static volatile long biomassPoints;

    private ClientPlayerBiomassData() { }

    public static void apply(long points) {
        biomassPoints = Math.max(0L, points);
    }

    public static long get() {
        return biomassPoints;
    }

    public static void reset() {
        biomassPoints = 0L;
    }

    @SubscribeEvent
    public static void onLogout(ClientPlayerNetworkEvent.LoggingOut event) {
        reset();
    }
}
```

## `src/main/java/com/carnis/mod/client/data/ClientPlayerInfection.java`

```java
package com.carnis.mod.client.data;

/** Compatibility facade for earlier overlays and fog renderers. */
public final class ClientPlayerInfection {
    private ClientPlayerInfection() { }
    public static float getInfectionLevel() { return ClientInfectionData.points(); }
    public static boolean isAssimilated() { return ClientInfectionData.points() >= 100; }
    public static void reset() { ClientInfectionData.reset(); }
}
```

## `src/main/java/com/carnis/mod/client/gui/CodexCarnisScreen.java`

```java
package com.carnis.mod.client.gui;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.FormattedCharSequence;
import org.lwjgl.glfw.GLFW;
import java.util.ArrayList;
import java.util.List;

public final class CodexCarnisScreen extends Screen {
    private static final ResourceLocation TEXTURE = new ResourceLocation("carnis", "textures/gui/codex_carnis_gui.png");
    private static final int BOOK_WIDTH = 256, BOOK_HEIGHT = 180, TAB_WIDTH = 18;
    private static final int PAGE_WIDTH = 100, LINES_PER_PAGE = 13, LINE_HEIGHT = 10;
    private static final int TITLE_COLOR = 0x6B1D1D, TEXT_COLOR = 0x2B261F, NOTE_COLOR = 0x7A4B2A;
    private static final String[] NUMERALS = {"I", "II", "III", "IV"};
    private record Line(FormattedCharSequence text, int color) { }
    private record Leaf(List<Line> lines) { }

    private final List<List<Leaf>> chapters = new ArrayList<>();
    private int chapter;
    private int spread;
    private float scale;
    private float left;
    private float top;

    public CodexCarnisScreen() { super(Component.translatable("item.carnis.research_journal")); }

    public static void open() {
        Minecraft client = Minecraft.getInstance();
        if (client.player != null && client.level != null) {
            client.level.playLocalSound(client.player.getX(), client.player.getY(), client.player.getZ(),
                    SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 0.8F, 1.0F, false);
        }
        client.setScreen(new CodexCarnisScreen());
    }

    @Override protected void init() {
        scale = Math.min(1.0F, Math.min((width - 8.0F) / (BOOK_WIDTH + TAB_WIDTH), (height - 8.0F) / BOOK_HEIGHT));
        scale = Math.max(0.05F, scale);
        left = (width - (BOOK_WIDTH + TAB_WIDTH) * scale) / 2.0F;
        top = (height - BOOK_HEIGHT * scale) / 2.0F;
        chapters.clear();
        for (CodexContent.Chapter section : CodexContent.CHAPTERS) {
            List<Leaf> leaves = new ArrayList<>();
            for (CodexContent.Page page : section.pages()) paginate(page, leaves);
            if ((leaves.size() & 1) != 0) leaves.add(new Leaf(List.of()));
            chapters.add(List.copyOf(leaves));
        }
        chapter = Math.min(chapter, chapters.size() - 1);
        spread = Math.min(spread, spreadCount() - 1);
    }

    private void paginate(CodexContent.Page page, List<Leaf> leaves) {
        List<Line> lines = new ArrayList<>();
        addLines(lines, Component.translatable(page.title()).withStyle(ChatFormatting.BOLD), TITLE_COLOR);
        lines.add(new Line(FormattedCharSequence.EMPTY, TEXT_COLOR));
        addLines(lines, Component.translatable(page.body()), TEXT_COLOR);
        lines.add(new Line(FormattedCharSequence.EMPTY, TEXT_COLOR));
        addLines(lines, Component.translatable(page.note()).withStyle(ChatFormatting.ITALIC), NOTE_COLOR);
        for (int i = 0; i < lines.size(); i += LINES_PER_PAGE) {
            leaves.add(new Leaf(List.copyOf(lines.subList(i, Math.min(lines.size(), i + LINES_PER_PAGE)))));
        }
    }

    private void addLines(List<Line> target, Component text, int color) {
        for (FormattedCharSequence line : font.split(text, PAGE_WIDTH)) target.add(new Line(line, color));
    }

    private int spreadCount() { return Math.max(1, (chapters.get(chapter).size() + 1) / 2); }
    private void pageSound() {
        Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1.0F));
    }
    private void turn(int amount) {
        int next = Math.max(0, Math.min(spreadCount() - 1, spread + amount));
        if (next != spread) { spread = next; pageSound(); }
    }
    private void selectChapter(int index) {
        if (index != chapter || spread != 0) { chapter = index; spread = 0; pageSound(); }
    }

    @Override public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        float localX = (mouseX - left) / scale, localY = (mouseY - top) / scale;
        graphics.pose().pushPose();
        try {
            graphics.pose().translate(left, top, 0);
            graphics.pose().scale(scale, scale, 1.0F);
            graphics.blit(TEXTURE, 0, 0, 0, 0, BOOK_WIDTH, BOOK_HEIGHT, 256, 256);
            List<Leaf> leaves = chapters.get(chapter);
            drawLeaf(graphics, leaves, spread * 2, 18);
            drawLeaf(graphics, leaves, spread * 2 + 1, 138);
            drawTurn(graphics, 18, Component.translatable("codex.carnis.previous").getString(), spread > 0, inside(localX, localY, 18, 156, 64, 174));
            drawTurn(graphics, 192, Component.translatable("codex.carnis.next").getString(), spread + 1 < spreadCount(), inside(localX, localY, 192, 156, 238, 174));
            graphics.drawCenteredString(font, (spread + 1) + " / " + spreadCount(), 128, 159, 0x5E4935);
            for (int i = 0; i < CodexContent.CHAPTERS.size(); i++) drawTab(graphics, i, localX, localY);
        } finally { graphics.pose().popPose(); }
        int hovered = hoveredTab(localX, localY);
        if (hovered >= 0) graphics.renderTooltip(font,
                Component.literal(NUMERALS[hovered] + ". ").append(Component.translatable("codex.carnis.tab." + hovered)), mouseX, mouseY);
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    private void drawLeaf(GuiGraphics graphics, List<Leaf> leaves, int index, int x) {
        if (index >= leaves.size()) return;
        int y = 16;
        for (Line line : leaves.get(index).lines()) {
            graphics.drawString(font, line.text(), x, y, line.color(), false);
            y += LINE_HEIGHT;
        }
    }

    private void drawTurn(GuiGraphics graphics, int x, String label, boolean enabled, boolean hovered) {
        graphics.fill(x, 156, x + 46, 174, enabled ? (hovered ? 0xBBA76543 : 0x886E4D38) : 0x553A3026);
        graphics.drawCenteredString(font, label, x + 23, 161, enabled ? 0xFFF1DCB3 : 0xFF918577);
    }

    private void drawTab(GuiGraphics graphics, int index, float mouseX, float mouseY) {
        int y = 16 + index * 34;
        boolean hover = inside(mouseX, mouseY, 256, y, 274, y + 28);
        int color = index == chapter ? 0xFF98423E : hover ? 0xFF704337 : 0xFF50352B;
        graphics.fill(256, y, 274, y + 28, 0xFF352219);
        graphics.fill(257, y + 1, 273, y + 27, color);
        // Each icon is drawn inside its tab: heart, cocoon, blade, injector.
        int ink = 0xFFE8CC94;
        switch (index) {
            case 0 -> { graphics.fill(261, y + 7, 264, y + 10, ink); graphics.fill(266, y + 7, 269, y + 10, ink); graphics.fill(261, y + 10, 269, y + 13, ink); graphics.fill(263, y + 13, 267, y + 16, ink); }
            case 1 -> { graphics.fill(262, y + 7, 268, y + 16, ink); graphics.fill(261, y + 9, 269, y + 14, ink); graphics.fill(263, y + 10, 267, y + 11, color); }
            case 2 -> { graphics.fill(267, y + 6, 269, y + 12, ink); graphics.fill(265, y + 10, 267, y + 15, ink); graphics.fill(262, y + 14, 266, y + 16, ink); }
            case 3 -> { graphics.fill(262, y + 8, 268, y + 12, ink); graphics.fill(268, y + 9, 271, y + 10, ink); graphics.fill(260, y + 7, 262, y + 13, ink); graphics.fill(264, y + 12, 266, y + 16, ink); }
        }
        graphics.drawCenteredString(font, NUMERALS[index], 265, y + 18, 0xFFE6CBA3);
    }

    private int hoveredTab(float x, float y) {
        for (int i = 0; i < CodexContent.CHAPTERS.size(); i++)
            if (inside(x, y, 256, 16 + i * 34, 274, 44 + i * 34)) return i;
        return -1;
    }
    private static boolean inside(float x, float y, int x0, int y0, int x1, int y1) {
        return x >= x0 && x < x1 && y >= y0 && y < y1;
    }

    @Override public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (button != 0) return super.mouseClicked(mouseX, mouseY, button);
        float x = (float)((mouseX - left) / scale), y = (float)((mouseY - top) / scale);
        int tab = hoveredTab(x, y);
        if (tab >= 0) { selectChapter(tab); return true; }
        if (inside(x, y, 18, 156, 64, 174)) { turn(-1); return true; }
        if (inside(x, y, 192, 156, 238, 174)) { turn(1); return true; }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode == GLFW.GLFW_KEY_LEFT || keyCode == GLFW.GLFW_KEY_PAGE_UP) { turn(-1); return true; }
        if (keyCode == GLFW.GLFW_KEY_RIGHT || keyCode == GLFW.GLFW_KEY_PAGE_DOWN) { turn(1); return true; }
        if (keyCode >= GLFW.GLFW_KEY_1 && keyCode <= GLFW.GLFW_KEY_4) { selectChapter(keyCode - GLFW.GLFW_KEY_1); return true; }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }
    @Override public boolean isPauseScreen() { return false; }
}
```

## `src/main/java/com/carnis/mod/client/gui/CodexContent.java`

```java
package com.carnis.mod.client.gui;

import java.util.List;

/** Field notes use translation keys; each entry is paginated by the active game font. */
public final class CodexContent {
    public record Page(String title, String body, String note) { }
    public record Chapter(String title, List<Page> pages) { }

    public static final List<Chapter> CHAPTERS = List.of(
        new Chapter("codex.carnis.tab.0", List.of(
            new Page("codex.carnis.entry.0.title", "codex.carnis.entry.0.body", "codex.carnis.entry.0.note"),
            new Page("codex.carnis.entry.1.title", "codex.carnis.entry.1.body", "codex.carnis.entry.1.note"),
            new Page("codex.carnis.entry.2.title", "codex.carnis.entry.2.body", "codex.carnis.entry.2.note"),
            new Page("codex.carnis.entry.3.title", "codex.carnis.entry.3.body", "codex.carnis.entry.3.note"),
            new Page("codex.carnis.entry.4.title", "codex.carnis.entry.4.body", "codex.carnis.entry.4.note"),
            new Page("codex.carnis.entry.5.title", "codex.carnis.entry.5.body", "codex.carnis.entry.5.note"))),
        new Chapter("codex.carnis.tab.1", List.of(
            new Page("codex.carnis.entry.6.title", "codex.carnis.entry.6.body", "codex.carnis.entry.6.note"),
            new Page("codex.carnis.entry.7.title", "codex.carnis.entry.7.body", "codex.carnis.entry.7.note"),
            new Page("codex.carnis.entry.8.title", "codex.carnis.entry.8.body", "codex.carnis.entry.8.note"),
            new Page("codex.carnis.entry.9.title", "codex.carnis.entry.9.body", "codex.carnis.entry.9.note"),
            new Page("codex.carnis.entry.10.title", "codex.carnis.entry.10.body", "codex.carnis.entry.10.note"))),
        new Chapter("codex.carnis.tab.2", List.of(
            new Page("codex.carnis.entry.11.title", "codex.carnis.entry.11.body", "codex.carnis.entry.11.note"),
            new Page("codex.carnis.entry.12.title", "codex.carnis.entry.12.body", "codex.carnis.entry.12.note"),
            new Page("codex.carnis.entry.13.title", "codex.carnis.entry.13.body", "codex.carnis.entry.13.note"),
            new Page("codex.carnis.entry.14.title", "codex.carnis.entry.14.body", "codex.carnis.entry.14.note"))),
        new Chapter("codex.carnis.tab.3", List.of(
            new Page("codex.carnis.entry.15.title", "codex.carnis.entry.15.body", "codex.carnis.entry.15.note"),
            new Page("codex.carnis.entry.16.title", "codex.carnis.entry.16.body", "codex.carnis.entry.16.note"),
            new Page("codex.carnis.entry.17.title", "codex.carnis.entry.17.body", "codex.carnis.entry.17.note"),
            new Page("codex.carnis.entry.18.title", "codex.carnis.entry.18.body", "codex.carnis.entry.18.note"),
            new Page("codex.carnis.entry.19.title", "codex.carnis.entry.19.body", "codex.carnis.entry.19.note")))
    );
    private CodexContent() { }
}
```

## `src/main/java/com/carnis/mod/client/gui/InfectionVeinsOverlay.java`

```java
package com.carnis.mod.client.gui;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerInfection;
import com.carnis.mod.config.CarnisConfig;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

@OnlyIn(Dist.CLIENT)
public final class InfectionVeinsOverlay implements IGuiOverlay {
    private static final ResourceLocation VEINS_TEXTURE = new ResourceLocation(
            CarnisMod.MOD_ID,
            "textures/misc/vein_overlay.png"
    );

    private static final int TEXTURE_SIZE = 256;
    private static final float HIGH_INFECTION_THRESHOLD = 70.0F;
    private static final double MIN_PULSE_SPEED = 0.055D;
    private static final double MAX_PULSE_SPEED = 0.180D;

    @Override
    public void render(
            ForgeGui gui,
            GuiGraphics guiGraphics,
            float partialTick,
            int screenWidth,
            int screenHeight
    ) {
        if (!CarnisConfig.CLIENT.veinOverlayEnabled.get()) {
            return;
        }

        float infectionLevel = ClientPlayerInfection.getInfectionLevel();

        if (com.carnis.mod.client.data.ClientInfectionData.stage() < 2) {
            return;
        }

        ClientLevel level = gui.getMinecraft().level;

        if (level == null || screenWidth <= 0 || screenHeight <= 0) {
            return;
        }

        float configuredIntensity = CarnisConfig.CLIENT
                .veinOverlayIntensity
                .get()
                .floatValue();

        if (configuredIntensity <= 0.0F) {
            return;
        }

        float normalizedInfection = Mth.clamp(
                infectionLevel / 100.0F,
                0.0F,
                1.0F
        );
        float baseAlpha = normalizedInfection;
        double speed = Mth.lerp(
                normalizedInfection,
                MIN_PULSE_SPEED,
                MAX_PULSE_SPEED
        );
        double gameTime = level.getGameTime() + partialTick;
        float pulse = 0.72F + 0.28F * (float) (
                (Math.sin(gameTime * speed) + 1.0D) * 0.5D
        );
        float overlayAlpha = Mth.clamp(
                baseAlpha * pulse * configuredIntensity,
                0.0F,
                1.0F
        );

        gui.setupOverlayRenderState(true, false);
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();

        try {
            RenderSystem.setShaderColor(
                    1.0F,
                    0.52F,
                    0.60F,
                    overlayAlpha
            );
            blitFullScreen(guiGraphics, screenWidth, screenHeight);

            if (infectionLevel >= HIGH_INFECTION_THRESHOLD) {
                float severeInfection = Mth.clamp(
                        (infectionLevel - HIGH_INFECTION_THRESHOLD)
                                / (100.0F - HIGH_INFECTION_THRESHOLD),
                        0.0F,
                        1.0F
                );
                float darkeningAlpha = Mth.clamp(
                        configuredIntensity
                                * pulse
                                * (0.08F + 0.42F * severeInfection),
                        0.0F,
                        1.0F
                );

                RenderSystem.setShaderColor(
                        0.28F,
                        0.018F,
                        0.032F,
                        darkeningAlpha
                );
                blitFullScreen(guiGraphics, screenWidth, screenHeight);
            }
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            int stage = com.carnis.mod.client.data.ClientInfectionData.stage();
            if (stage >= 3 && Math.floorMod(level.getGameTime(), 120L) < 5L) {
                int alpha = (int) (configuredIntensity * 24.0F);
                guiGraphics.fill(0, 0, screenWidth, screenHeight, (alpha << 24) | 0x356D42);
            }
            if (infectionLevel >= 100.0F) {
                int alpha = (int) (configuredIntensity * 45.0F * pulse);
                guiGraphics.fill(0, 0, screenWidth, screenHeight, (alpha << 24) | 0x110408);
            }
        } finally {
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            RenderSystem.defaultBlendFunc();
            RenderSystem.disableBlend();
            RenderSystem.enableDepthTest();
        }
    }

    private static void blitFullScreen(
            GuiGraphics guiGraphics,
            int screenWidth,
            int screenHeight
    ) {
        guiGraphics.blit(
                VEINS_TEXTURE,
                0,
                0,
                screenWidth,
                screenHeight,
                0.0F,
                0.0F,
                TEXTURE_SIZE,
                TEXTURE_SIZE,
                TEXTURE_SIZE,
                TEXTURE_SIZE
        );
    }
}
```

## `src/main/java/com/carnis/mod/client/gui/PhantomEyesOverlay.java`

```java
package com.carnis.mod.client.gui;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientInfectionData;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.item.NeuroWeave;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.List;

/** Локальные кратковременные изображения глаз; не создаёт сущностей в мире. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PhantomEyesOverlay implements IGuiOverlay {
    private static final ResourceLocation TEXTURE = new ResourceLocation(CarnisMod.MOD_ID,
            "textures/hallucination/phantom_eyes.png");
    private static final int TEXTURE_SIZE = 8;
    private static final int FADE_TICKS = 5;
    private static final int MAX_FLASHES = 2;
    private static final List<Flash> FLASHES = new ArrayList<>(MAX_FLASHES);
    private static ClientLevel activeLevel;
    private static LocalPlayer activePlayer;
    private static int delay = -1;
    private static int lastStage;

    private static final class Flash {
        private final float x;
        private final float y;
        private final int duration;
        private int age;

        private Flash(float x, float y, int duration) {
            this.x = x;
            this.y = y;
            this.duration = duration;
        }
    }

    private static boolean eligible(Minecraft mc, LocalPlayer player) {
        return mc.level != null && player != null && player.isAlive() && !player.isSpectator()
                && CarnisConfig.CLIENT.phantomEyesEnabled.get()
                && ClientInfectionData.points() >= 25 && ClientInfectionData.stage() >= 2
                && !NeuroResonatorHelmetItem.isEquipped(player) && NeuroWeave.protectedPieces(player) < 4;
    }

    private static void reset() {
        FLASHES.clear();
        activeLevel = null;
        activePlayer = null;
        delay = -1;
        lastStage = 0;
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (!eligible(mc, player)) {
            reset();
            return;
        }
        if (activeLevel != mc.level || activePlayer != player) {
            reset();
            activeLevel = mc.level;
            activePlayer = player;
        }
        if (mc.isPaused()) return;

        int stage = Mth.clamp(ClientInfectionData.stage(), 2, 4);
        RandomSource random = player.getRandom();
        FLASHES.removeIf(flash -> ++flash.age >= flash.duration);
        if (lastStage != stage) {
            lastStage = stage;
            delay = nextDelay(stage, random);
            return;
        }
        if (--delay > 0) return;
        int count = 1 + random.nextInt(2);
        for (int i = 0; i < count && FLASHES.size() < MAX_FLASHES; i++) {
            FLASHES.add(createFlash(random));
        }
        delay = nextDelay(stage, random);
    }

    private static int nextDelay(int stage, RandomSource random) {
        return switch (stage) {
            case 2 -> random.nextIntBetweenInclusive(600, 1800);
            case 3 -> random.nextIntBetweenInclusive(300, 900);
            default -> random.nextIntBetweenInclusive(100, 300);
        };
    }

    private static Flash createFlash(RandomSource random) {
        float along = random.nextFloat();
        float edge = random.nextFloat() * 0.15F;
        int side = random.nextInt(4);
        float x = side == 0 ? edge : side == 1 ? 1.0F - edge : along;
        float y = side == 2 ? edge : side == 3 ? 1.0F - edge : along;
        return new Flash(x, y, random.nextIntBetweenInclusive(20, 60));
    }

    @Override
    public void render(ForgeGui gui, GuiGraphics graphics, float partialTick, int screenWidth, int screenHeight) {
        Minecraft mc = gui.getMinecraft();
        if (!eligible(mc, mc.player) || activeLevel != mc.level || activePlayer != mc.player
                || mc.options.hideGui || screenWidth <= 0 || screenHeight <= 0 || FLASHES.isEmpty()) return;

        float intensity = CarnisConfig.CLIENT.phantomEyesIntensity.get().floatValue();
        int size = Math.max(1, Math.min(Math.min(screenWidth, screenHeight), Math.round(48.0F * intensity)));
        int stage = Mth.clamp(ClientInfectionData.stage(), 2, 4);
        int color = stage == 2 ? 0x00AA00 : stage == 3 ? 0x00FF44 : 0xFF2200;
        float red = ((color >> 16) & 255) / 255.0F;
        float green = ((color >> 8) & 255) / 255.0F;
        float blue = (color & 255) / 255.0F;

        gui.setupOverlayRenderState(true, false);
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        try {
            for (Flash flash : FLASHES) {
                float elapsed = flash.age + partialTick;
                float fadeIn = Mth.clamp(elapsed / FADE_TICKS, 0.0F, 1.0F);
                float fadeOut = Mth.clamp((flash.duration - elapsed) / FADE_TICKS, 0.0F, 1.0F);
                float alpha = Mth.clamp(0.7F * intensity * Math.min(fadeIn, fadeOut), 0.0F, 1.0F);
                int x = Mth.clamp(Math.round(flash.x * screenWidth - size / 2.0F), 0, screenWidth - size);
                int y = Mth.clamp(Math.round(flash.y * screenHeight - size / 2.0F), 0, screenHeight - size);
                RenderSystem.setShaderColor(red, green, blue, alpha);
                graphics.blit(TEXTURE, x, y, size, size, 0.0F, 0.0F,
                        TEXTURE_SIZE, TEXTURE_SIZE, TEXTURE_SIZE, TEXTURE_SIZE);
            }
        } finally {
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            RenderSystem.defaultBlendFunc();
            RenderSystem.disableBlend();
            RenderSystem.enableDepthTest();
        }
    }
}
```

## `src/main/java/com/carnis/mod/client/gui/overlay/NeuroResonanceOverlay.java`

```java
package com.carnis.mod.client.gui.overlay;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Incremental, client-only scan of loaded blocks. A completed sweep is atomically published. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NeuroResonanceOverlay implements IGuiOverlay {
    private static final int RADIUS = 24;
    private static final int SIDE = RADIUS * 2 + 1;
    private static final int TOTAL = SIDE * SIDE * SIDE;
    private static final int SCAN_BUDGET = 1024;
    private static ClientLevel scanLevel;
    private static BlockPos anchor;
    private static int cursor;
    private static BlockPos candidateTarget, candidateHeart, target, heart;
    private static double targetDistance, heartDistance;

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        ClientLevel level = mc.level;
        Player player = mc.player;
        if (level == null || player == null || !player.isAlive() || !NeuroArmorEventHandler.hasHelmet(player)) {
            reset();
            return;
        }
        if (scanLevel != level || anchor == null) {
            reset();
            scanLevel = level;
            beginSweep(player);
        }
        for (int n = 0; n < SCAN_BUDGET && cursor < TOTAL; n++, cursor++) {
            int dx = cursor % SIDE - RADIUS;
            int dz = cursor / SIDE % SIDE - RADIUS;
            int dy = cursor / (SIDE * SIDE) - RADIUS;
            if (dx * dx + dy * dy + dz * dz > RADIUS * RADIUS) continue;
            BlockPos pos = anchor.offset(dx, dy, dz);
            if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) continue;
            BlockState state = level.getBlockState(pos);
            boolean isHeart = state.is(ModBlocks.PULSING_HEART.get());
            boolean isPool = state.is(ModBlocks.STOMACH_POOL.get());
            boolean isCluster = state.is(ModBlocks.BIOMASS_REMAINS.get()) && isCluster(level, pos);
            if (!isHeart && !isPool && !isCluster) continue;
            double distance = player.distanceToSqr(Vec3.atCenterOf(pos));
            if (distance > RADIUS * RADIUS) continue;
            if (distance < targetDistance) { targetDistance = distance; candidateTarget = pos; }
            if (isHeart && distance < heartDistance) { heartDistance = distance; candidateHeart = pos; }
        }
        if (cursor == TOTAL) {
            target = candidateTarget;
            heart = candidateHeart;
            beginSweep(player);
        }
    }
    private static boolean isCluster(ClientLevel level, BlockPos pos) {
        int count = 1;
        for (Direction direction : Direction.values()) {
            BlockPos next = pos.relative(direction);
            if (level.hasChunkAt(next) && level.getBlockState(next).is(ModBlocks.BIOMASS_REMAINS.get())) count++;
        }
        return count >= 3;
    }
    private static void beginSweep(Player player) {
        anchor = player.blockPosition().immutable();
        cursor = 0;
        candidateTarget = null;
        candidateHeart = null;
        targetDistance = Double.MAX_VALUE;
        heartDistance = Double.MAX_VALUE;
    }
    private static void reset() {
        scanLevel = null;
        anchor = null;
        cursor = 0;
        candidateTarget = null;
        candidateHeart = null;
        target = null;
        heart = null;
    }
    private static boolean validTarget(ClientLevel level, Player player, BlockPos pos, boolean heartOnly) {
        if (pos == null || !level.hasChunkAt(pos) || player.distanceToSqr(Vec3.atCenterOf(pos)) > RADIUS * RADIUS) return false;
        BlockState state = level.getBlockState(pos);
        if (state.is(ModBlocks.PULSING_HEART.get())) return true;
        return !heartOnly && (state.is(ModBlocks.STOMACH_POOL.get())
                || state.is(ModBlocks.BIOMASS_REMAINS.get()) && isCluster(level, pos));
    }
    private static int color(float alpha) {
        return (Mth.clamp(Math.round(alpha * 255.0F), 0, 255) << 24) | 0x38E094;
    }
    @Override
    public void render(ForgeGui gui, GuiGraphics graphics, float partialTick, int width, int height) {
        Minecraft mc = gui.getMinecraft();
        ClientLevel level = mc.level;
        Player player = mc.player;
        if (level == null || player == null || mc.options.hideGui || !NeuroArmorEventHandler.hasHelmet(player)
                || scanLevel != level) return;
        float opacity = CarnisConfig.CLIENT.neuroSonarOpacity.get().floatValue();
        if (opacity <= 0.0F) return;
        boolean hasHeart = validTarget(level, player, heart, true);
        double time = level.getGameTime() + partialTick;
        double phase = hasHeart
                ? (time + Math.floorMod(heart.asLong(), PulsingHeartBlockEntity.PULSE_INTERVAL_TICKS))
                    / PulsingHeartBlockEntity.PULSE_INTERVAL_TICKS
                : time / 100.0D;
        float pulse = (float) (0.55D + 0.45D * (0.5D + 0.5D * Math.cos(phase * Math.PI * 2.0D)));
        int border = color(opacity * .30F);
        int signal = color(opacity * pulse);
        int cx = width / 2, cy = height / 2;
        graphics.fill(5, 5, 6, Math.min(height - 5, 29), border);
        graphics.fill(5, 5, 29, 6, border);
        graphics.fill(width - 6, 5, width - 5, Math.min(height - 5, 29), border);
        graphics.fill(width - 29, 5, width - 5, 6, border);
        graphics.fill(cx - 2, cy + 24, cx + 3, cy + 29, signal);
        graphics.fill(cx - 5, cy + 26, cx + 6, cy + 27, signal);
        if (!validTarget(level, player, target, false)) return;
        Vec3 delta = Vec3.atCenterOf(target).subtract(player.position());
        double yaw = Math.toRadians(player.getYRot());
        double right = delta.x * -Math.cos(yaw) + delta.z * -Math.sin(yaw);
        double forward = delta.x * -Math.sin(yaw) + delta.z * Math.cos(yaw);
        double length = Math.sqrt(right * right + forward * forward);
        if (length < 1.0E-5D) { right = 0.0D; forward = 1.0D; length = 1.0D; }
        double ux = right / length, uy = -forward / length;
        int x = cx + (int) Math.round(ux * 36), y = cy + (int) Math.round(uy * 36);
        for (int i = -5; i <= 5; i++) {
            int px = x + (int) Math.round(ux * i), py = y + (int) Math.round(uy * i);
            graphics.fill(px, py, px + 2, py + 2, signal);
        }
        for (int i = 0; i <= 4; i++) {
            int bx = x + (int) Math.round(ux * (5 - i));
            int by = y + (int) Math.round(uy * (5 - i));
            int lx = bx + (int) Math.round(-uy * i), ly = by + (int) Math.round(ux * i);
            int rx = bx - (int) Math.round(-uy * i), ry = by - (int) Math.round(ux * i);
            graphics.fill(lx, ly, lx + 2, ly + 2, signal);
            graphics.fill(rx, ry, rx + 2, ry + 2, signal);
        }
        String distance = String.format(java.util.Locale.ROOT, "%.0f m", delta.length());
        graphics.drawCenteredString(mc.font, distance, cx, cy + 34, signal);
    }
}
```

## `src/main/java/com/carnis/mod/client/hud/BiomassHudOverlay.java`

```java
package com.carnis.mod.client.hud;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerBiomassData;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.CustomizeGuiOverlayEvent;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Персональный счётчик биомассы, независимый от мирового счётчика Улья. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class BiomassHudOverlay implements IGuiOverlay {
    private static final ResourceLocation ICON = new ResourceLocation(CarnisMod.MOD_ID, "textures/gui/biomass_icon.png");
    private static final int ICON_SIZE = 16;
    private static final int TOP_MARGIN = 8;
    private static int bossBottom = TOP_MARGIN;

    /** Начало отрисовки шкал сбрасывает измерение для текущего кадра. */
    @SubscribeEvent(priority = EventPriority.LOWEST, receiveCanceled = true)
    public static void onBossOverlayPre(RenderGuiOverlayEvent.Pre event) {
        if (event.getOverlay().id().equals(VanillaGuiOverlay.BOSS_EVENT_PROGRESS.id())) {
            bossBottom = TOP_MARGIN;
        }
    }

    /** Учитываем положение и интервал каждой реально обрабатываемой шкалы. */
    @SubscribeEvent(priority = EventPriority.LOWEST, receiveCanceled = true)
    public static void onBossBar(CustomizeGuiOverlayEvent.BossEventProgress event) {
        if (!event.isCanceled()) {
            bossBottom = Math.max(bossBottom, event.getY() + event.getIncrement());
        }
    }

    @Override
    public void render(ForgeGui gui, GuiGraphics graphics, float partialTick, int screenWidth, int screenHeight) {
        Minecraft minecraft = gui.getMinecraft();
        if (minecraft.player == null || minecraft.level == null || minecraft.options.hideGui) return;

        String label = "§c❤ Биомасса: §f" + ClientPlayerBiomassData.get();
        int textWidth = minecraft.font.width(label);
        int contentWidth = ICON_SIZE + 4 + textWidth;
        int x = Math.max(0, Math.min(screenWidth - 120, screenWidth - contentWidth - 4));
        int y = Math.max(TOP_MARGIN, bossBottom);

        gui.setupOverlayRenderState(true, false);
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        try {
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            graphics.blit(ICON, x, y, 0, 0, ICON_SIZE, ICON_SIZE, ICON_SIZE, ICON_SIZE);
            graphics.drawString(minecraft.font, label, x + ICON_SIZE + 4, y + 4, 0xFFFFFFFF, true);
        } finally {
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            RenderSystem.defaultBlendFunc();
            RenderSystem.disableBlend();
            RenderSystem.enableDepthTest();
        }
    }
}
```

## `src/main/java/com/carnis/mod/client/model/BioPurifierModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.item.BioPurifierItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class BioPurifierModel extends GeoModel<BioPurifierItem> {
    @Override public ResourceLocation getModelResource(BioPurifierItem item) {
        return new ResourceLocation("carnis", "geo/item/bio_purifier.geo.json");
    }
    @Override public ResourceLocation getTextureResource(BioPurifierItem item) {
        return new ResourceLocation("carnis", "textures/item/bio_purifier.png");
    }
    @Override public ResourceLocation getAnimationResource(BioPurifierItem item) {
        return new ResourceLocation("carnis", "animations/item/bio_purifier.animation.json");
    }
}
```

## `src/main/java/com/carnis/mod/client/model/BiomassMaggotModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.entity.BiomassMaggotEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class BiomassMaggotModel extends GeoModel<BiomassMaggotEntity> {
    @Override public ResourceLocation getModelResource(BiomassMaggotEntity entity) {
        return new ResourceLocation("carnis", "geo/entity/biomass_maggot.geo.json");
    }
    @Override public ResourceLocation getTextureResource(BiomassMaggotEntity entity) {
        return new ResourceLocation("carnis", "textures/entity/biomass_maggot.png");
    }
    @Override public ResourceLocation getAnimationResource(BiomassMaggotEntity entity) {
        return new ResourceLocation("carnis", "animations/entity/biomass_maggot.animation.json");
    }
}
```

## `src/main/java/com/carnis/mod/client/model/CerebralNexusModel.java`

```java
package com.carnis.mod.client.model;
import com.carnis.mod.entity.CerebralNexusEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class CerebralNexusModel extends GeoModel<CerebralNexusEntity> {
    @Override public ResourceLocation getModelResource(CerebralNexusEntity entity) { return new ResourceLocation("carnis", "geo/entity/cerebral_nexus.geo.json"); }
    @Override public ResourceLocation getTextureResource(CerebralNexusEntity entity) { return new ResourceLocation("carnis", "textures/entity/cerebral_nexus.png"); }
    @Override public ResourceLocation getAnimationResource(CerebralNexusEntity entity) { return new ResourceLocation("carnis", "animations/entity/cerebral_nexus.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/client/model/FleshAmalgamModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import software.bernie.geckolib.model.GeoModel;

@OnlyIn(Dist.CLIENT)
public final class FleshAmalgamModel extends GeoModel<FleshAmalgamEntity> {
    @Override public ResourceLocation getModelResource(FleshAmalgamEntity entity) {
        return new ResourceLocation("carnis", "geo/entity/flesh_amalgam.geo.json");
    }
    @Override public ResourceLocation getTextureResource(FleshAmalgamEntity entity) {
        return new ResourceLocation("carnis", "textures/entity/flesh_amalgam.png");
    }
    @Override public ResourceLocation getAnimationResource(FleshAmalgamEntity entity) {
        return new ResourceLocation("carnis", "animations/entity/flesh_amalgam.animation.json");
    }
}
```

## `src/main/java/com/carnis/mod/client/model/HiveEyeItemModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.item.HiveEyeItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class HiveEyeItemModel extends GeoModel<HiveEyeItem> {
    @Override
    public ResourceLocation getModelResource(HiveEyeItem eye) {
        return new ResourceLocation("carnis", "geo/block/hive_eye.geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(HiveEyeItem eye) {
        return new ResourceLocation("carnis", "textures/block/hive_eye.png");
    }

    @Override
    public ResourceLocation getAnimationResource(HiveEyeItem eye) {
        return new ResourceLocation("carnis", "animations/block/hive_eye.animation.json");
    }
}
```

## `src/main/java/com/carnis/mod/client/model/HiveEyeModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.HiveEyeBlockEntity;
import com.carnis.mod.client.renderer.HiveEyeRenderer;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;

public final class HiveEyeModel extends GeoModel<HiveEyeBlockEntity> {
    @Override
    public void setCustomAnimations(HiveEyeBlockEntity eye, long instanceId, AnimationState<HiveEyeBlockEntity> state) {
        super.setCustomAnimations(eye, instanceId, state);
        CoreGeoBone iris = getAnimationProcessor().getBone("iris");
        CoreGeoBone pupil = getAnimationProcessor().getBone("pupil");
        if (iris != null && pupil != null) {
            HiveEyeRenderer.applyEyePose(eye, iris, pupil, (float) state.getPartialTick());
        }
    }

    @Override
    public ResourceLocation getModelResource(HiveEyeBlockEntity object) {
        return new ResourceLocation(CarnisMod.MOD_ID, "geo/block/hive_eye.geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(HiveEyeBlockEntity object) {
        return new ResourceLocation(CarnisMod.MOD_ID, "textures/block/hive_eye.png");
    }

    @Override
    public ResourceLocation getAnimationResource(HiveEyeBlockEntity object) {
        return new ResourceLocation(CarnisMod.MOD_ID, "animations/block/hive_eye.animation.json");
    }
}
```

## `src/main/java/com/carnis/mod/client/model/HiveSentinelModel.java`

```java
package com.carnis.mod.client.model;
import com.carnis.mod.entity.HiveSentinelEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class HiveSentinelModel extends GeoModel<HiveSentinelEntity> {
    @Override public ResourceLocation getModelResource(HiveSentinelEntity entity) { return new ResourceLocation("carnis", "geo/entity/hive_sentinel.geo.json"); }
    @Override public ResourceLocation getTextureResource(HiveSentinelEntity entity) { return new ResourceLocation("carnis", "textures/entity/hive_sentinel.png"); }
    @Override public ResourceLocation getAnimationResource(HiveSentinelEntity entity) { return new ResourceLocation("carnis", "animations/entity/hive_sentinel.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/client/model/InfectedCreeperGeoModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.entity.InfectedCreeperEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class InfectedCreeperGeoModel extends GeoModel<InfectedCreeperEntity> {
    @Override public ResourceLocation getModelResource(InfectedCreeperEntity entity) { return new ResourceLocation("carnis", "geo/entity/infected_creeper.geo.json"); }
    @Override public ResourceLocation getTextureResource(InfectedCreeperEntity entity) { return new ResourceLocation("carnis", "textures/entity/infected_creeper.png"); }
    @Override public ResourceLocation getAnimationResource(InfectedCreeperEntity entity) { return new ResourceLocation("carnis", "animations/entity/infected_creeper.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/client/model/InfectedSkeletonGeoModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.entity.InfectedSkeletonEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class InfectedSkeletonGeoModel extends GeoModel<InfectedSkeletonEntity> {
    @Override public ResourceLocation getModelResource(InfectedSkeletonEntity entity) { return new ResourceLocation("carnis", "geo/entity/infected_skeleton.geo.json"); }
    @Override public ResourceLocation getTextureResource(InfectedSkeletonEntity entity) { return new ResourceLocation("carnis", "textures/entity/infected_skeleton.png"); }
    @Override public ResourceLocation getAnimationResource(InfectedSkeletonEntity entity) { return new ResourceLocation("carnis", "animations/entity/infected_skeleton.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/client/model/InfectedSpiderGeoModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.entity.InfectedSpiderEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class InfectedSpiderGeoModel extends GeoModel<InfectedSpiderEntity> {
    @Override public ResourceLocation getModelResource(InfectedSpiderEntity entity) { return new ResourceLocation("carnis", "geo/entity/infected_spider.geo.json"); }
    @Override public ResourceLocation getTextureResource(InfectedSpiderEntity entity) { return new ResourceLocation("carnis", "textures/entity/infected_spider.png"); }
    @Override public ResourceLocation getAnimationResource(InfectedSpiderEntity entity) { return new ResourceLocation("carnis", "animations/entity/infected_spider.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/client/model/InfectedZombieGeoModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.entity.InfectedZombieEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public final class InfectedZombieGeoModel extends GeoModel<InfectedZombieEntity> {
    @Override public ResourceLocation getModelResource(InfectedZombieEntity entity) { return new ResourceLocation("carnis", "geo/entity/infected_zombie.geo.json"); }
    @Override public ResourceLocation getTextureResource(InfectedZombieEntity entity) { return new ResourceLocation("carnis", "textures/entity/infected_zombie.png"); }
    @Override public ResourceLocation getAnimationResource(InfectedZombieEntity entity) { return new ResourceLocation("carnis", "animations/entity/infected_zombie.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/client/model/NervePillarModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.NervePillarBlockEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.DefaultedBlockGeoModel;

public final class NervePillarModel extends DefaultedBlockGeoModel<NervePillarBlockEntity> {
    public NervePillarModel() { super(new ResourceLocation(CarnisMod.MOD_ID, "nerve_pillar")); }
}
```

## `src/main/java/com/carnis/mod/client/model/NeuroArmorModel.java`

```java
package com.carnis.mod.client.model;
import com.carnis.mod.item.armor.NeuroArmorItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class NeuroArmorModel extends GeoModel<NeuroArmorItem> {
    @Override public ResourceLocation getModelResource(NeuroArmorItem item) { return new ResourceLocation("carnis", "geo/item/neuro_armor.geo.json"); }
    @Override public ResourceLocation getTextureResource(NeuroArmorItem item) { return new ResourceLocation("carnis", "textures/armor/neuro_armor.png"); }
    @Override public ResourceLocation getAnimationResource(NeuroArmorItem item) { return new ResourceLocation("carnis", "animations/armor/neuro_armor.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/client/model/ParasiticTendrilModel.java`

```java
package com.carnis.mod.client.model;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class ParasiticTendrilModel extends GeoModel<ParasiticTendrilEntity> {
    @Override public ResourceLocation getModelResource(ParasiticTendrilEntity e) { return new ResourceLocation("carnis", "geo/entity/parasitic_tendril.geo.json"); }
    @Override public ResourceLocation getTextureResource(ParasiticTendrilEntity e) { return new ResourceLocation("carnis", "textures/entity/parasitic_tendril.png"); }
    @Override public ResourceLocation getAnimationResource(ParasiticTendrilEntity e) { return new ResourceLocation("carnis", "animations/entity/parasitic_tendril.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/client/model/PneumaticInoculatorModel.java`

```java
package com.carnis.mod.client.model;
import com.carnis.mod.item.PneumaticInoculatorItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class PneumaticInoculatorModel extends GeoModel<PneumaticInoculatorItem> {
 @Override public ResourceLocation getModelResource(PneumaticInoculatorItem a) { return new ResourceLocation("carnis", "geo/item/pneumatic_inoculator.geo.json"); }
 @Override public ResourceLocation getTextureResource(PneumaticInoculatorItem a) { return new ResourceLocation("carnis", "textures/item/pneumatic_inoculator_geo.png"); }
 @Override public ResourceLocation getAnimationResource(PneumaticInoculatorItem a) { return new ResourceLocation("carnis", "animations/item/pneumatic_inoculator.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/client/model/PulsingHeartItemModel.java`

```java
package com.carnis.mod.client.model;
import com.carnis.mod.item.PulsingHeartItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class PulsingHeartItemModel extends GeoModel<PulsingHeartItem> {
    @Override public ResourceLocation getModelResource(PulsingHeartItem item) { return new ResourceLocation("carnis", "geo/block/pulsing_heart.geo.json"); }
    @Override public ResourceLocation getTextureResource(PulsingHeartItem item) { return new ResourceLocation("carnis", "textures/block/pulsing_heart.png"); }
    @Override public ResourceLocation getAnimationResource(PulsingHeartItem item) { return new ResourceLocation("carnis", "animations/block/pulsing_heart.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/client/model/PulsingHeartModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import software.bernie.geckolib.model.DefaultedBlockGeoModel;

@OnlyIn(Dist.CLIENT)
public final class PulsingHeartModel
        extends DefaultedBlockGeoModel<PulsingHeartBlockEntity> {
    public PulsingHeartModel() {
        super(new ResourceLocation(CarnisMod.MOD_ID, "pulsing_heart"));
    }

    @Override
    public RenderType getRenderType(
            PulsingHeartBlockEntity animatable,
            ResourceLocation texture
    ) {
        return RenderType.entityTranslucent(texture);
    }
}
```

## `src/main/java/com/carnis/mod/client/model/PustuleClusterModel.java`

```java
package com.carnis.mod.client.model;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.PustuleClusterBlockEntity;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.DefaultedBlockGeoModel;

public final class PustuleClusterModel extends DefaultedBlockGeoModel<PustuleClusterBlockEntity> {
    public PustuleClusterModel() { super(new ResourceLocation(CarnisMod.MOD_ID, "pustule_cluster")); }
    @Override public RenderType getRenderType(PustuleClusterBlockEntity entity, ResourceLocation texture) {
        return RenderType.entityTranslucent(texture);
    }
}
```

## `src/main/java/com/carnis/mod/client/particle/BiomassSparkParticle.java`

```java
package com.carnis.mod.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.core.particles.SimpleParticleType;

public final class BiomassSparkParticle extends TextureSheetParticle {
    private BiomassSparkParticle(ClientLevel level, double x, double y, double z,
                                 double vx, double vy, double vz, SpriteSet sprites) {
        super(level, x, y, z);
        this.xd = vx;
        this.yd = vy;
        this.zd = vz;
        this.gravity = 0.0F;
        this.friction = 1.0F;
        this.hasPhysics = false;
        this.lifetime = 8;
        this.quadSize = 0.065F;
        pickSprite(sprites);
    }

    @Override
    public int getLightColor(float partialTick) {
        return 0xF000F0;
    }

    @Override
    public ParticleRenderType getRenderType() {
        return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
    }

    public static final class Provider implements ParticleProvider<SimpleParticleType> {
        private final SpriteSet sprites;

        public Provider(SpriteSet sprites) {
            this.sprites = sprites;
        }

        @Override
        public Particle createParticle(SimpleParticleType type, ClientLevel level,
                                       double x, double y, double z, double vx, double vy, double vz) {
            return new BiomassSparkParticle(level, x, y, z, vx, vy, vz, sprites);
        }
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/BiomassMaggotRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.BiomassMaggotModel;
import com.carnis.mod.entity.BiomassMaggotEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class BiomassMaggotRenderer extends GeoEntityRenderer<BiomassMaggotEntity> {
    public BiomassMaggotRenderer(EntityRendererProvider.Context context) {
        super(context, new BiomassMaggotModel());
        this.shadowRadius = 0.2F;
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/CarnisFogRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerInfection;
import com.carnis.mod.config.CarnisConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.util.Mth;
import net.minecraft.world.level.material.FogType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@OnlyIn(Dist.CLIENT)
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisFogRenderer {
    private static final float FOG_RED = 0.32F;
    private static final float FOG_GREEN = 0.04F;
    private static final float FOG_BLUE = 0.06F;
    private static final float SMOOTHING_PER_TICK = 0.10F;
    private static final float DENSITY_THRESHOLD = 0.50F;
    private static final float FAR_DISTANCE_LOW = 24.0F;
    private static final float FAR_DISTANCE_HIGH = 12.0F;
    private static float previousInfection;
    private static float smoothedInfection;

    private CarnisFogRenderer() {
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.player == null || minecraft.level == null) {
            previousInfection = 0.0F;
            smoothedInfection = 0.0F;
            return;
        }
        if (com.carnis.mod.client.data.ClientInfectionData.stage() < 3) {
            previousInfection = 0.0F;
            smoothedInfection = 0.0F;
            return;
        }
        float infection = ClientPlayerInfection.getInfectionLevel();
        float target = Float.isFinite(infection)
                ? Mth.clamp(infection / 100.0F, 0.0F, 1.0F)
                : 0.0F;
        previousInfection = smoothedInfection;
        smoothedInfection = Mth.lerp(SMOOTHING_PER_TICK, smoothedInfection, target);
    }

    @SubscribeEvent
    public static void onLogout(ClientPlayerNetworkEvent.LoggingOut event) {
        previousInfection = 0.0F;
        smoothedInfection = 0.0F;
        ClientPlayerInfection.reset();
    }

    private static float infectionForFrame(double partialTick) {
        float partial = Mth.clamp((float) partialTick, 0.0F, 1.0F);
        return Mth.lerp(partial, previousInfection, smoothedInfection);
    }

    @SubscribeEvent
    public static void onFogColor(ViewportEvent.ComputeFogColor event) {
        Minecraft minecraft = Minecraft.getInstance();
        if (!CarnisConfig.CLIENT.atmosphericFogEnabled.get()
                || minecraft.player == null || minecraft.level == null
                || event.getCamera().getFluidInCamera() != FogType.NONE) {
            return;
        }
        float strength = infectionForFrame(event.getPartialTick());
        if (strength <= 0.0F) {
            return;
        }
        event.setRed(Mth.lerp(strength, event.getRed(), FOG_RED));
        event.setGreen(Mth.lerp(strength, event.getGreen(), FOG_GREEN));
        event.setBlue(Mth.lerp(strength, event.getBlue(), FOG_BLUE));
    }

    @SubscribeEvent
    public static void onRenderFog(ViewportEvent.RenderFog event) {
        Minecraft minecraft = Minecraft.getInstance();
        if (!CarnisConfig.CLIENT.atmosphericFogEnabled.get()
                || minecraft.player == null || minecraft.level == null
                || event.getType() != FogType.NONE
                || event.getMode() != FogRenderer.FogMode.FOG_TERRAIN) {
            return;
        }
        float infection = infectionForFrame(event.getPartialTick());
        float density = Mth.clamp(
                (infection - DENSITY_THRESHOLD) / (1.0F - DENSITY_THRESHOLD),
                0.0F, 1.0F
        );
        if (density <= 0.0F) {
            return;
        }
        float originalEnd = event.getFarPlaneDistance();
        float originalStart = event.getNearPlaneDistance();
        float desiredEnd = Mth.lerp(density, FAR_DISTANCE_LOW, FAR_DISTANCE_HIGH);
        float end = Mth.lerp(density, originalEnd, Math.min(originalEnd, desiredEnd));
        float start = Mth.lerp(density, originalStart, Math.min(originalStart, end * 0.25F));
        if (end < originalEnd || start < originalStart) {
            event.setFarPlaneDistance(end);
            event.setNearPlaneDistance(Math.min(start, end));
            event.setCanceled(true);
        }
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/CerebralNexusRenderer.java`

```java
package com.carnis.mod.client.renderer;
import com.carnis.mod.client.model.CerebralNexusModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.entity.CerebralNexusEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
public final class CerebralNexusRenderer extends GeoEntityRenderer<CerebralNexusEntity> {
    public CerebralNexusRenderer(EntityRendererProvider.Context context) { super(context, new CerebralNexusModel()); addRenderLayer(new OptionalGlowLayer<>(this)); shadowRadius = 0.6F; }
}
```

## `src/main/java/com/carnis/mod/client/renderer/DartRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.PurificationDartEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public final class DartRenderer<T extends AbstractArrow> extends EntityRenderer<T> {
    private static final ResourceLocation TEXTURE =
            new ResourceLocation(CarnisMod.MOD_ID, "textures/entity/dart.png");
    private static final int STEEL = 0;
    private static final int DARK_STEEL = 1;
    private static final int BRASS = 2;
    private static final int VIRAL = 3;
    private static final int VIRAL_ACCENT = 4;
    private static final int SERUM = 5;
    private static final int GLASS = 6;
    private static final int GLASS_RIM = 7;

    public DartRenderer(EntityRendererProvider.Context context) {
        super(context);
        shadowRadius = 0.0F;
    }

    @Override
    public void render(T dart, float entityYaw, float partialTick, PoseStack poseStack,
                       MultiBufferSource buffers, int packedLight) {
        poseStack.pushPose();
        poseStack.mulPose(Axis.YP.rotationDegrees(Mth.rotLerp(partialTick, dart.yRotO, dart.getYRot()) - 90.0F));
        poseStack.mulPose(Axis.ZP.rotationDegrees(Mth.lerp(partialTick, dart.xRotO, dart.getXRot())));

        VertexConsumer vertices = buffers.getBuffer(RenderType.entityCutoutNoCull(TEXTURE));
        boolean purification = dart instanceof PurificationDartEntity
                || dart instanceof com.carnis.mod.entity.projectile.InoculatorDartEntity inoculator
                && inoculator.getDartType() == com.carnis.mod.entity.projectile.InoculatorDartEntity.DartType.PURIFICATION;
        int fluid = purification ? SERUM : VIRAL;

        // The model's positive X axis points toward the needle tip.
        box(poseStack, vertices, packedLight, -0.34F, -0.018F, -0.018F, 0.34F, 0.018F, 0.018F, STEEL);
        box(poseStack, vertices, packedLight, 0.32F, -0.010F, -0.010F, 0.52F, 0.010F, 0.010F, GLASS);
        box(poseStack, vertices, packedLight, -0.15F, -0.056F, -0.056F, 0.10F, 0.056F, 0.056F, fluid);
        box(poseStack, vertices, packedLight, -0.15F, -0.064F, -0.064F, 0.10F, -0.054F, -0.054F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.15F, 0.054F, -0.064F, 0.10F, 0.064F, -0.054F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.15F, -0.064F, 0.054F, 0.10F, -0.054F, 0.064F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.15F, 0.054F, 0.054F, 0.10F, 0.064F, 0.064F, GLASS_RIM);
        box(poseStack, vertices, packedLight, -0.14F, 0.057F, -0.038F, 0.08F, 0.061F, -0.023F, GLASS);
        if (!purification) {
            box(poseStack, vertices, packedLight, -0.09F, 0.057F, 0.015F, 0.03F, 0.061F, 0.033F, VIRAL_ACCENT);
        }
        box(poseStack, vertices, packedLight, -0.19F, -0.072F, -0.072F, -0.15F, 0.072F, 0.072F, BRASS);
        box(poseStack, vertices, packedLight, 0.10F, -0.072F, -0.072F, 0.14F, 0.072F, 0.072F, BRASS);
        box(poseStack, vertices, packedLight, -0.43F, -0.025F, -0.025F, -0.30F, 0.025F, 0.025F, DARK_STEEL);
        box(poseStack, vertices, packedLight, -0.42F, -0.125F, -0.012F, -0.29F, 0.125F, 0.012F, BRASS);
        box(poseStack, vertices, packedLight, -0.42F, -0.012F, -0.125F, -0.29F, 0.012F, 0.125F, BRASS);

        poseStack.popPose();
        super.render(dart, entityYaw, partialTick, poseStack, buffers, packedLight);
    }

    private static void box(PoseStack stack, VertexConsumer out, int light,
                            float x0, float y0, float z0, float x1, float y1, float z1, int swatch) {
        float u = (swatch * 4.0F + 2.0F) / 32.0F;
        float v = 0.5F;
        face(stack, out, light, u, v, -1, 0, 0, x0,y0,z0, x0,y0,z1, x0,y1,z1, x0,y1,z0);
        face(stack, out, light, u, v,  1, 0, 0, x1,y0,z1, x1,y0,z0, x1,y1,z0, x1,y1,z1);
        face(stack, out, light, u, v, 0, -1, 0, x0,y0,z1, x0,y0,z0, x1,y0,z0, x1,y0,z1);
        face(stack, out, light, u, v, 0,  1, 0, x0,y1,z0, x0,y1,z1, x1,y1,z1, x1,y1,z0);
        face(stack, out, light, u, v, 0, 0, -1, x1,y0,z0, x0,y0,z0, x0,y1,z0, x1,y1,z0);
        face(stack, out, light, u, v, 0, 0,  1, x0,y0,z1, x1,y0,z1, x1,y1,z1, x0,y1,z1);
    }

    private static void face(PoseStack stack, VertexConsumer out, int light, float u, float v,
                             float nx, float ny, float nz,
                             float ax, float ay, float az, float bx, float by, float bz,
                             float cx, float cy, float cz, float dx, float dy, float dz) {
        PoseStack.Pose pose = stack.last();
        vertex(pose, out, light, u, v, nx, ny, nz, ax, ay, az);
        vertex(pose, out, light, u, v, nx, ny, nz, bx, by, bz);
        vertex(pose, out, light, u, v, nx, ny, nz, cx, cy, cz);
        vertex(pose, out, light, u, v, nx, ny, nz, dx, dy, dz);
    }

    private static void vertex(PoseStack.Pose pose, VertexConsumer out, int light, float u, float v,
                               float nx, float ny, float nz, float x, float y, float z) {
        out.vertex(pose.pose(), x, y, z).color(255, 255, 255, 255).uv(u, v)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light)
                .normal(pose.normal(), nx, ny, nz).endVertex();
    }

    @Override
    public ResourceLocation getTextureLocation(T dart) {
        return TEXTURE;
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/FleshAmalgamRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.FleshAmalgamModel;
import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;

@OnlyIn(Dist.CLIENT)
public final class FleshAmalgamRenderer
        extends GeoEntityRenderer<FleshAmalgamEntity> {
    public FleshAmalgamRenderer(EntityRendererProvider.Context context) {
        super(context, new FleshAmalgamModel());
        this.shadowRadius = 0.85F;
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/HiveEyeItemRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.HiveEyeItemModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.item.HiveEyeItem;
import software.bernie.geckolib.renderer.GeoItemRenderer;

public final class HiveEyeItemRenderer extends GeoItemRenderer<HiveEyeItem> {
    public HiveEyeItemRenderer() {
        super(new HiveEyeItemModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/HiveEyeRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.block.entity.HiveEyeBlockEntity;
import com.carnis.mod.client.model.HiveEyeModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.renderer.GeoBlockRenderer;

public final class HiveEyeRenderer extends GeoBlockRenderer<HiveEyeBlockEntity> {
    public HiveEyeRenderer(BlockEntityRendererProvider.Context context) {
        super(new HiveEyeModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }

    public static void applyEyePose(HiveEyeBlockEntity eye, CoreGeoBone iris, CoreGeoBone pupil, float partialTick) {
        if (eye == null || iris == null || pupil == null) return;
        float yaw = eye.trackingYaw(partialTick);
        float pitch = eye.trackingPitch(partialTick);
        iris.setRotY(-yaw);
        iris.setRotX(-pitch);
        iris.setScaleX(eye.irisPulseScale(partialTick));
        iris.setScaleY(eye.irisPulseScale(partialTick));
        pupil.setRotY(0.0F);
        pupil.setRotX(0.0F);
        float distanceScale = eye.hasTrackingTarget() ? eye.pupilDistanceScale(partialTick) : 1.0F;
        pupil.setScaleX(distanceScale);
        pupil.setScaleY(distanceScale * eye.pupilScaleY(partialTick));
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/HiveSentinelRenderer.java`

```java
package com.carnis.mod.client.renderer;
import com.carnis.mod.client.model.HiveSentinelModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.entity.HiveSentinelEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
public final class HiveSentinelRenderer extends GeoEntityRenderer<HiveSentinelEntity> {
    public HiveSentinelRenderer(EntityRendererProvider.Context context) { super(context, new HiveSentinelModel()); addRenderLayer(new OptionalGlowLayer<>(this)); shadowRadius = 0.6F; }
}
```

## `src/main/java/com/carnis/mod/client/renderer/InfectedCreeperRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.client.model.InfectedCreeperGeoModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class InfectedCreeperRenderer extends GeoEntityRenderer<InfectedCreeperEntity> {
    public InfectedCreeperRenderer(EntityRendererProvider.Context context) {
        super(context, new InfectedCreeperGeoModel());
        addRenderLayer(new com.carnis.mod.client.renderer.layer.OptionalGlowLayer<>(this));
        this.shadowRadius = .45F;
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/InfectedSkeletonRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.InfectedSkeletonGeoModel;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class InfectedSkeletonRenderer extends GeoEntityRenderer<InfectedSkeletonEntity> {
    public InfectedSkeletonRenderer(EntityRendererProvider.Context context) {
        super(context, new InfectedSkeletonGeoModel());
        addRenderLayer(new com.carnis.mod.client.renderer.layer.OptionalGlowLayer<>(this));
        this.shadowRadius = 0.45F;
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/InfectedSpiderRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.entity.InfectedSpiderEntity;
import com.carnis.mod.client.model.InfectedSpiderGeoModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class InfectedSpiderRenderer extends GeoEntityRenderer<InfectedSpiderEntity> {
    public InfectedSpiderRenderer(EntityRendererProvider.Context context) {
        super(context, new InfectedSpiderGeoModel());
        addRenderLayer(new software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer<>(this));
        this.shadowRadius = .65F;
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/InfectedZombieRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.InfectedZombieGeoModel;
import com.carnis.mod.entity.InfectedZombieEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;

/** The model resolves the geometry, texture, and animation resources. */
public final class InfectedZombieRenderer extends GeoEntityRenderer<InfectedZombieEntity> {
    public InfectedZombieRenderer(EntityRendererProvider.Context context) {
        super(context, new InfectedZombieGeoModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
        this.shadowRadius = 0.45F;
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/NecroticCameraEffects.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerInfection;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@OnlyIn(Dist.CLIENT)
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NecroticCameraEffects {
    private NecroticCameraEffects() {
    }

    public static void onCameraAngles(ViewportEvent.ComputeCameraAngles event) {
        LocalPlayer player = Minecraft.getInstance().player;
        if (player == null || !player.isAlive() || player.isSpectator()
                || ClientPlayerInfection.getInfectionLevel() < 100.0F) {
            return;
        }
        double phase = (player.tickCount % 20) + event.getPartialTick();
        if (phase < 4.0D) {
            float roll = (float) (Math.sin(phase * 4.0D) * (1.0D - phase / 4.0D) * 1.5D);
            event.setRoll(event.getRoll() + roll);
        }
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/NervePillarRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.block.entity.NervePillarBlockEntity;
import com.carnis.mod.client.model.NervePillarModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import software.bernie.geckolib.renderer.GeoBlockRenderer;

public final class NervePillarRenderer extends GeoBlockRenderer<NervePillarBlockEntity> {
    public NervePillarRenderer(BlockEntityRendererProvider.Context context) {
        super(new NervePillarModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/NeuroArmorRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.NeuroArmorModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.item.armor.NeuroArmorItem;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoArmorRenderer;

import javax.annotation.Nullable;

public final class NeuroArmorRenderer extends GeoArmorRenderer<NeuroArmorItem> {
    public NeuroArmorRenderer() {
        super(new NeuroArmorModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }

    @Nullable @Override public GeoBone getHeadBone() { return getGeoModel().getBone("head").orElse(null); }
    @Nullable @Override public GeoBone getBodyBone() { return getGeoModel().getBone("body").orElse(null); }
    @Nullable @Override public GeoBone getRightArmBone() { return getGeoModel().getBone("right_arm").orElse(null); }
    @Nullable @Override public GeoBone getLeftArmBone() { return getGeoModel().getBone("left_arm").orElse(null); }
    @Nullable @Override public GeoBone getRightLegBone() { return getGeoModel().getBone("right_leg").orElse(null); }
    @Nullable @Override public GeoBone getLeftLegBone() { return getGeoModel().getBone("left_leg").orElse(null); }
    @Nullable @Override public GeoBone getRightBootBone() { return getGeoModel().getBone("right_boot").orElse(null); }
    @Nullable @Override public GeoBone getLeftBootBone() { return getGeoModel().getBone("left_boot").orElse(null); }
}
```

## `src/main/java/com/carnis/mod/client/renderer/ParasiticTendrilRenderer.java`

```java
package com.carnis.mod.client.renderer;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import com.carnis.mod.client.model.ParasiticTendrilModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
public final class ParasiticTendrilRenderer extends GeoEntityRenderer<ParasiticTendrilEntity> {
    public ParasiticTendrilRenderer(EntityRendererProvider.Context context) { super(context, new ParasiticTendrilModel()); shadowRadius = .35F; }
}
```

## `src/main/java/com/carnis/mod/client/renderer/PneumaticInoculatorRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.PneumaticInoculatorModel;
import com.carnis.mod.item.PneumaticInoculatorItem;
import software.bernie.geckolib.renderer.GeoItemRenderer;

public final class PneumaticInoculatorRenderer extends GeoItemRenderer<PneumaticInoculatorItem> {
    public PneumaticInoculatorRenderer() {
        super(new PneumaticInoculatorModel());
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/PulsingHeartItemRenderer.java`

```java
package com.carnis.mod.client.renderer;
import com.carnis.mod.client.model.PulsingHeartItemModel;
import com.carnis.mod.item.PulsingHeartItem;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
public final class PulsingHeartItemRenderer extends GeoItemRenderer<PulsingHeartItem> {
    public PulsingHeartItemRenderer() { super(new PulsingHeartItemModel()); addRenderLayer(new OptionalGlowLayer<>(this)); }
}
```

## `src/main/java/com/carnis/mod/client/renderer/PulsingHeartRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.client.model.PulsingHeartModel;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import software.bernie.geckolib.renderer.GeoBlockRenderer;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;

@OnlyIn(Dist.CLIENT)
public final class PulsingHeartRenderer
        extends GeoBlockRenderer<PulsingHeartBlockEntity> {
    public PulsingHeartRenderer(BlockEntityRendererProvider.Context context) {
        super(new PulsingHeartModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/PustuleClusterRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.block.entity.PustuleClusterBlockEntity;
import com.carnis.mod.client.model.PustuleClusterModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import software.bernie.geckolib.renderer.GeoBlockRenderer;

public final class PustuleClusterRenderer extends GeoBlockRenderer<PustuleClusterBlockEntity> {
    public PustuleClusterRenderer(BlockEntityRendererProvider.Context context) {
        super(new PustuleClusterModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/StomachPoolRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.StomachPoolBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

public final class StomachPoolRenderer implements BlockEntityRenderer<StomachPoolBlockEntity> {
    private static final ResourceLocation ACID = new ResourceLocation(CarnisMod.MOD_ID, "textures/block/stomach_pool.png");
    public StomachPoolRenderer(BlockEntityRendererProvider.Context context) { }
    @Override public void render(StomachPoolBlockEntity pool, float partialTick, PoseStack pose,
                                 MultiBufferSource buffers, int packedLight, int packedOverlay) {
        double time = pool.getLevel() == null ? 0 : pool.getLevel().getGameTime() + partialTick;
        boolean active = pool.isDigesting();
        float y = .65F + (float)Math.sin(time * (active ? .24 : .08)) * (active ? .018F : .008F);
        float alpha = .77F + (float)Math.sin(time * (active ? .19 : .06)) * .09F;
        VertexConsumer vertices = buffers.getBuffer(RenderType.entityTranslucent(ACID));
        Matrix4f matrix = pose.last().pose();
        Matrix3f normal = pose.last().normal();
        vertex(vertices, matrix, normal, .126F, y, .126F, 0, 0, alpha);
        vertex(vertices, matrix, normal, .126F, y, .874F, 0, 1, alpha);
        vertex(vertices, matrix, normal, .874F, y, .874F, 1, 1, alpha);
        vertex(vertices, matrix, normal, .874F, y, .126F, 1, 0, alpha);
    }
    private static void vertex(VertexConsumer out, Matrix4f pose, Matrix3f normal, float x, float y, float z, float u, float v, float alpha) {
        out.vertex(pose, x, y, z).color(.68F, 1F, .36F, alpha).uv(u, v)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(LightTexture.FULL_BRIGHT)
                .normal(normal, 0, 1, 0).endVertex();
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/item/BioPurifierRenderer.java`

```java
package com.carnis.mod.client.renderer.item;

import com.carnis.mod.client.model.BioPurifierModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.item.BioPurifierItem;
import software.bernie.geckolib.renderer.GeoItemRenderer;

public final class BioPurifierRenderer extends GeoItemRenderer<BioPurifierItem> {
    public BioPurifierRenderer() {
        super(new BioPurifierModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/layer/IncubatingEntityLayer.java`

```java
package com.carnis.mod.client.renderer.layer;

import com.carnis.mod.init.ModEffects;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;

public final class IncubatingEntityLayer<T extends LivingEntity, M extends EntityModel<T>> extends RenderLayer<T, M> {
    private static final ResourceLocation VEINS = new ResourceLocation("carnis", "textures/entity/incubation_overlay.png");
    private static final ResourceLocation PUSTULE = new ResourceLocation("carnis", "textures/entity/incubation_pustule.png");
    private final ModelPart growth;

    public IncubatingEntityLayer(RenderLayerParent<T, M> parent) {
        super(parent);
        MeshDefinition mesh = new MeshDefinition();
        mesh.getRoot().addOrReplaceChild("growth", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-1.5F, -1.5F, -1.5F, 3, 3, 3), PartPose.ZERO);
        growth = LayerDefinition.create(mesh, 16, 16).bakeRoot().getChild("growth");
    }

    @Override
    public void render(PoseStack pose, MultiBufferSource buffers, int light, T entity,
            float limbSwing, float limbSwingAmount, float partialTick, float age,
            float netHeadYaw, float headPitch) {
        MobEffectInstance effect = entity.getEffect(ModEffects.INCUBATING.get());
        if (effect == null || effect.getAmplifier() < 1 || entity.isInvisible()) return;
        float pulse = 0.5F + 0.5F * Mth.sin(age * 0.22F);
        float alpha = 0.4F + 0.25F * pulse;
        pose.pushPose();
        try {
            pose.scale(1.012F, 1.012F, 1.012F);
            VertexConsumer veins = buffers.getBuffer(RenderType.entityTranslucent(VEINS));
            getParentModel().renderToBuffer(pose, veins, light,
                    LivingEntityRenderer.getOverlayCoords(entity, 0), 1, 1, 1, alpha);
        } finally { pose.popPose(); }
        VertexConsumer vertices = buffers.getBuffer(RenderType.entityCutoutNoCull(PUSTULE));
        if (getParentModel() instanceof HumanoidModel<?> humanoid) {
            attach(pose, vertices, humanoid.head, -0.18F, -0.25F, -0.24F, pulse, light);
            attach(pose, vertices, humanoid.body, 0.15F, 0.32F, -0.14F, pulse, light);
            attach(pose, vertices, humanoid.leftArm, 0.06F, 0.30F, -0.12F, pulse, light);
            attach(pose, vertices, humanoid.rightArm, -0.06F, 0.40F, -0.12F, pulse, light);
            attach(pose, vertices, humanoid.leftLeg, 0.05F, 0.34F, -0.12F, pulse, light);
            attach(pose, vertices, humanoid.rightLeg, -0.05F, 0.40F, -0.12F, pulse, light);
        } else {
            // Non-humanoid vanilla models have different inaccessible part layouts.
            // These two growths follow the rendered body transform, not individual limbs.
            attach(pose, vertices, null, -0.12F, 0.65F, -0.22F, pulse, light);
            attach(pose, vertices, null, 0.15F, 0.85F, 0.16F, pulse, light);
        }
    }

    private void attach(PoseStack pose, VertexConsumer vertices, ModelPart part,
                        float x, float y, float z, float pulse, int light) {
        pose.pushPose();
        try {
            if (part != null) part.translateAndRotate(pose);
            pose.translate(x, y, z);
            float scale = 0.8F + pulse * 0.20F;
            pose.scale(scale, scale, scale);
            growth.render(pose, vertices, light, net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY);
        } finally { pose.popPose(); }
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/layer/OptionalGlowLayer.java`

```java
package com.carnis.mod.client.renderer.layer;

import com.carnis.mod.CarnisMod;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

import java.util.HashMap;
import java.util.Map;

/** Renders a glow pass only when the optional companion texture is available. */
public final class OptionalGlowLayer<T extends GeoAnimatable> extends AutoGlowingGeoLayer<T> {
    private static final Map<ResourceLocation, Boolean> RESOURCE_CACHE = new HashMap<>();
    private static ResourceManager cachedResourceManager;
    private static final Map<ResourceLocation, Long> WARNING_TIMES = new HashMap<>();
    private static final long WARNING_COOLDOWN_MS = 60_000L;

    public OptionalGlowLayer(GeoRenderer<T> renderer) {
        super(renderer);
    }

    @Override
    public void render(PoseStack poseStack, T animatable, BakedGeoModel model, RenderType renderType,
                       MultiBufferSource buffers, VertexConsumer buffer, float partialTick,
                       int packedLight, int packedOverlay) {
        ResourceLocation texture = getTextureResource(animatable);
        String path = texture.getPath();
        if (!path.endsWith(".png")) return;

        ResourceLocation glowmask = new ResourceLocation(texture.getNamespace(),
                path.substring(0, path.length() - 4) + "_glowmask.png");
        ResourceManager manager = Minecraft.getInstance().getResourceManager();
        if (cachedResourceManager != manager) {
            RESOURCE_CACHE.clear();
            WARNING_TIMES.clear();
            cachedResourceManager = manager;
        }
        Boolean present = RESOURCE_CACHE.get(glowmask);
        if (present == null) {
            present = manager.getResource(glowmask).isPresent();
            RESOURCE_CACHE.put(glowmask, present);
        }
        if (!present) {
            long now = Util.getMillis();
            long last = WARNING_TIMES.getOrDefault(glowmask, Long.MIN_VALUE / 2);
            if (now >= last && now - last >= WARNING_COOLDOWN_MS) {
                CarnisMod.LOGGER.warn("Optional glowmask is missing: {}", glowmask);
                WARNING_TIMES.put(glowmask, now);
            }
            return;
        }

        super.render(poseStack, animatable, model, renderType, buffers, buffer,
                partialTick, packedLight, packedOverlay);
    }
}
```

## `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java`

```java
package com.carnis.mod.client.sound;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModSounds;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import java.util.HashMap;
import java.util.Map;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;


/** Samples loaded Hive blocks only; no chunk loading and a fixed client-tick budget. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class HiveAmbientSoundHandler {
    private static final Map<String, Boolean> AMBIENT_RESOURCE_CACHE = new HashMap<>();
    private static ResourceManager ambientResourceManager;
    private static final Map<String, Long> AMBIENT_WARNING_TIMES = new HashMap<>();
    private static final long AMBIENT_WARNING_COOLDOWN_MS = 60_000L;

    private static final int RADIUS = 16;
    private static final int SIDE = RADIUS * 2 + 1;
    private static final int VOLUME = SIDE * SIDE * SIDE;
    private static final int BUDGET = 2048;
    private static final int CLOSE_STRUCTURE_ENTER = 12;
    private static final int CLOSE_STRUCTURE_EXIT = 8;
    private static final int PULSE_INTERVAL_TICKS = 268; // 13.4 seconds
    private static final int HEARTBEAT_MIN_INTERVAL = 800; // 40 seconds
    private static final int HEARTBEAT_MAX_INTERVAL = 1200; // 60 seconds
    // Sphere radius 16 contains approximately 17,077 sampled positions.
    private static final int DENSITY_SURFACE = 85;
    private static final int DENSITY_CORE = 1366;
    private static final int ZONE_THRESHOLD = 0;
    private static final int ZONE_SURFACE = 1;
    private static final int ZONE_DEEP = 2;
    private static final int ZONE_CORE = 3;
    private static final int STINGER_INTENSIFY = 0;
    private static final int STINGER_RELEASE = 1;
    private static final int STINGER_DEEP = 2;
    private static final long NO_SCHEDULED_TIME = -1L;

    private static Level lastLevel;
    private static boolean playerWasPresent = false;
    private static BlockPos center;
    private static int cursor = VOLUME;
    private static int hiveDensityNearby;
    private static int stableHiveDensity;
    private static boolean zoneScanReady;
    private static int closeHiveBlockCount;
    private static boolean insideStructure;
    private static double nearestHive = Double.POSITIVE_INFINITY;
    private static HiveAmbientSoundInstance sound;
    private static SoundEvent currentLoopEvent;
    private static HiveAmbientSoundInstance closeSound;
    private static long nextPulseAt = NO_SCHEDULED_TIME;
    private static long nextTonalStingerAt = NO_SCHEDULED_TIME;
    private static long nextHeartbeatAt = NO_SCHEDULED_TIME;
    private static boolean nextHiveHeartbeatEvent = true;
    private static SimpleSoundInstance heartbeatSound;
    private static boolean heartbeatPlaying = false;
    private static int currentZone = -1;
    private static int pendingZone = -1;
    private static int pendingZoneTicks = 0;
    private static boolean zoneKnown = false;

    private HiveAmbientSoundHandler() { }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft client = Minecraft.getInstance();
        ClientLevel level = client.level;
        if (level == null) return;
        if (client.player == null) {
            if (playerWasPresent) {
                reset();
                playerWasPresent = false;
            }
            return;
        }
        playerWasPresent = true;
        if (level != lastLevel) {
            reset();
            lastLevel = level;
        }
        if (center == null || cursor >= VOLUME && level.getGameTime() % 40L == 0L) {
            center = client.player.blockPosition().immutable();
            cursor = 0;
            hiveDensityNearby = 0;
            closeHiveBlockCount = 0;
            nearestHive = Double.POSITIVE_INFINITY;
        }
        if (cursor < VOLUME) {
            long scanStartedAt = System.nanoTime();
            int end = Math.min(VOLUME, cursor + BUDGET);
            BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
            while (cursor < end) {
                int index = cursor++;
                int dx = index % SIDE - RADIUS;
                int dy = index / SIDE % SIDE - RADIUS;
                int dz = index / (SIDE * SIDE) - RADIUS;
                int distanceSquared = dx * dx + dy * dy + dz * dz;
                if (distanceSquared > RADIUS * RADIUS) continue;

                pos.set(center.getX() + dx, center.getY() + dy, center.getZ() + dz);
                if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) continue;
                BlockState state = level.getBlockState(pos);
                boolean hiveBlock = state.is(ModBlocks.PULSING_HEART.get())
                        || state.is(ModBlocks.LIVING_FLESH.get())
                        || state.is(ModBlocks.FLESH_VEINS.get());
                if (!hiveBlock) continue;
                hiveDensityNearby++;
                if (distanceSquared <= 16) closeHiveBlockCount++;
                nearestHive = Math.min(nearestHive, Math.sqrt(distanceSquared));
            }
            long elapsed = System.nanoTime() - scanStartedAt;
            if (elapsed > 1_000_000L) {
                CarnisMod.LOGGER.debug("Slow ambient scan batch: {} ms", elapsed / 1_000_000.0D);
            }
            if (cursor < VOLUME) {
                if (zoneScanReady) updateZone(level, client.player);
                return;
            }
            stableHiveDensity = hiveDensityNearby;
            zoneScanReady = true;
        }

        if (zoneScanReady) updateZone(level, client.player);
        updateAmbience(client, level);
    }

    private static void updateAmbience(Minecraft client, ClientLevel level) {
        if (sound != null && sound.isStopped()) {
            sound = null;
            currentLoopEvent = null;
        }
        if (closeSound != null && closeSound.isStopped()) closeSound = null;

        float targetVolume = 0.0F;
        if (Double.isFinite(nearestHive)) {
            targetVolume = 0.85F * (float) (1.0D - nearestHive / (RADIUS + 1.0D));
        }
        targetVolume = Mth.clamp(targetVolume, 0.0F, 0.85F);
        SoundEvent wantedBed = targetVolume > 0.0F ? selectZoneBed() : null;
        if (targetVolume > 0.0F && wantedBed == null) targetVolume = 0.0F;
        if (!insideStructure && closeHiveBlockCount > CLOSE_STRUCTURE_ENTER) {
            insideStructure = true;
        } else if (insideStructure && closeHiveBlockCount < CLOSE_STRUCTURE_EXIT) {
            insideStructure = false;
        }

        if (targetVolume > 0.0F) {
            if (sound != null && currentLoopEvent != wantedBed) {
                sound.setTarget(0.0F);
                sound = null;
                currentLoopEvent = null;
            }
            if (sound == null) {
                sound = new HiveAmbientSoundInstance(level, wantedBed, targetVolume);
                currentLoopEvent = wantedBed;
                client.getSoundManager().play(sound);
            } else {
                sound.setTarget(targetVolume);
            }

            // Keep the existing close ambience as a separate layer over the selected zonal bed.
            if (insideStructure) {
                if (closeSound == null) {
                    closeSound = new HiveAmbientSoundInstance(
                            level, ModSounds.HIVE_AMBIENT_CLOSE.get(), targetVolume * 0.6F);
                    client.getSoundManager().play(closeSound);
                } else {
                    closeSound.setTarget(targetVolume * 0.6F);
                }
            } else if (closeSound != null) {
                closeSound.setTarget(0.0F);
                closeSound = null;
            }
            playPeriodicEvents(client, level);
        } else {
            if (sound != null) sound.setTarget(0.0F);
            if (closeSound != null) closeSound.setTarget(0.0F);
            nextPulseAt = NO_SCHEDULED_TIME;
            nextTonalStingerAt = NO_SCHEDULED_TIME;
            nextHeartbeatAt = NO_SCHEDULED_TIME;
            nextHiveHeartbeatEvent = true;
            stopHeartbeat(client);
        }
    }

    /** Select an available zonal asset; the established ambient bank is the canonical fallback. */
    private static SoundEvent selectZoneBed() {
        String[] zonePaths = switch (currentZone) {
            case ZONE_SURFACE -> new String[]{"hive/amb_surface"};
            case ZONE_DEEP -> new String[]{"hive/amb_deep"};
            case ZONE_CORE -> new String[]{"hive/amb_core"};
            default -> new String[]{"hive/amb_threshold"};
        };
        if (hasAmbientAssets(zonePaths)) {
            return switch (currentZone) {
                case ZONE_SURFACE -> ModSounds.HIVE_AMB_SURFACE.get();
                case ZONE_DEEP -> ModSounds.HIVE_AMB_DEEP.get();
                case ZONE_CORE -> ModSounds.HIVE_AMB_CORE.get();
                default -> ModSounds.HIVE_AMB_THRESHOLD.get();
            };
        }
        if (hasAmbientAssets("amb/hive_ambient_01", "amb/hive_ambient_02", "amb/hive_ambient_03")) {
            return ModSounds.HIVE_AMBIENT.get();
        }
        return null;
    }

    /** Presence gates playback only; sound registration and sounds.json declarations remain unconditional. */
    private static boolean hasAmbientAssets(String... paths) {
        ResourceManager manager = Minecraft.getInstance().getResourceManager();
        if (ambientResourceManager != manager) {
            AMBIENT_RESOURCE_CACHE.clear();
            AMBIENT_WARNING_TIMES.clear();
            ambientResourceManager = manager;
        }
        boolean complete = true;
        for (String path : paths) {
            Boolean present = AMBIENT_RESOURCE_CACHE.get(path);
            if (present == null) {
                ResourceLocation location = new ResourceLocation("carnis", "sounds/" + path + ".ogg");
                present = manager.getResource(location).isPresent();
                AMBIENT_RESOURCE_CACHE.put(path, present);
            }
            if (!present) {
                complete = false;
                long now = Util.getMillis();
                long last = AMBIENT_WARNING_TIMES.getOrDefault(path, Long.MIN_VALUE / 2);
                if (now >= last && now - last >= AMBIENT_WARNING_COOLDOWN_MS) {
                    CarnisMod.LOGGER.warn("Hive ambience asset is missing: carnis:{}; using canonical fallback when available", path);
                    AMBIENT_WARNING_TIMES.put(path, now);
                }
            }
        }
        return complete;
    }

    /** Update the zone state once per client tick; initialization is intentionally silent. */
    private static void updateZone(ClientLevel level, Player player) {
        int desired = calculateZone(player);
        if (!zoneKnown) {
            currentZone = desired;
            pendingZone = -1;
            pendingZoneTicks = 0;
            zoneKnown = true;
            return;
        }
        if (desired == currentZone) {
            pendingZone = -1;
            pendingZoneTicks = 0;
            return;
        }
        if (desired != pendingZone) {
            pendingZone = desired;
            pendingZoneTicks = 0;
        }
        pendingZoneTicks++;
        if (pendingZoneTicks < 60) return;

        int oldZone = currentZone;
        int newZone = pendingZone;
        currentZone = newZone;
        pendingZone = -1;
        pendingZoneTicks = 0;

        if (newZone > oldZone) {
            if (newZone - oldZone > 1) {
                playZoneStinger(level, player, STINGER_DEEP);
            } else {
                playZoneStinger(level, player, STINGER_INTENSIFY);
            }
        } else if (newZone < oldZone) {
            playZoneStinger(level, player, STINGER_RELEASE);
        }
    }

    private static int calculateZone(Player player) {
        int density = stableHiveDensity;
        int y = player.blockPosition().getY();
        if (density > DENSITY_CORE) return ZONE_CORE;
        if (density > DENSITY_SURFACE) {
            boolean wasDeep = currentZone == ZONE_DEEP;
            if (wasDeep) return (y < 44) ? ZONE_DEEP : ZONE_SURFACE;
            return (y < 36) ? ZONE_DEEP : ZONE_SURFACE;
        }
        return ZONE_THRESHOLD;
    }

    private static void playZoneStinger(Level level, Player player, int stingerType) {
        if (!zoneKnown) return;
        SoundEvent stinger = switch (stingerType) {
            case STINGER_INTENSIFY -> ModSounds.ZONE_STINGER_INTENSIFY.get();
            case STINGER_RELEASE -> ModSounds.ZONE_STINGER_RELEASE.get();
            case STINGER_DEEP -> ModSounds.ZONE_STINGER_DEEP.get();
            default -> null;
        };
        if (stinger == null) return;

        level.playSound(null, player.blockPosition(), stinger, SoundSource.AMBIENT, 1.0F, 1.0F);
    }

    private static void playPeriodicEvents(Minecraft client, ClientLevel level) {
        long now = level.getGameTime();
        if (nextPulseAt == NO_SCHEDULED_TIME) nextPulseAt = now + PULSE_INTERVAL_TICKS;
        if (now >= nextPulseAt) {
            playOneShot(client, ModSounds.HIVE_PULSE.get());
            do {
                nextPulseAt += PULSE_INTERVAL_TICKS;
            } while (nextPulseAt <= now);
        }

        if (nextTonalStingerAt == NO_SCHEDULED_TIME) {
            nextTonalStingerAt = now + 1200L + level.random.nextInt(1201);
        } else if (now >= nextTonalStingerAt) {
            playOneShot(client, ModSounds.HIVE_AMBIENT_TONAL_STINGER.get());
            nextTonalStingerAt = now + 1200L + level.random.nextInt(1201);
        }

        if (insideStructure) {
            if (nextHeartbeatAt == NO_SCHEDULED_TIME) {
                nextHeartbeatAt = now + nextHeartbeatDelay(level);
            } else if (now >= nextHeartbeatAt) {
                // Alternate the separately registered core heartbeat events; they do not replace Hive Pulse.
                SoundEvent heartbeat = nextHiveHeartbeatEvent
                        ? ModSounds.HIVE_HEARTBEAT.get()
                        : ModSounds.HEARTBEAT_LOOP.get();
                if (heartbeat == ModSounds.HEARTBEAT_LOOP.get()) {
                    if (heartbeatPlaying && !client.getSoundManager().isActive(heartbeatSound)) {
                        heartbeatPlaying = false;
                        heartbeatSound = null;
                    }
                    if (!heartbeatPlaying) {
                        heartbeatSound = SimpleSoundInstance.forAmbientAddition(heartbeat);
                        client.getSoundManager().play(heartbeatSound);
                        heartbeatPlaying = true;
                    }
                } else {
                    playOneShot(client, heartbeat);
                }
                nextHiveHeartbeatEvent = !nextHiveHeartbeatEvent;
                nextHeartbeatAt = now + nextHeartbeatDelay(level);
            }
        } else {
            nextHeartbeatAt = NO_SCHEDULED_TIME;
            nextHiveHeartbeatEvent = true;
            stopHeartbeat(client);
        }
    }

    private static int nextHeartbeatDelay(ClientLevel level) {
        return HEARTBEAT_MIN_INTERVAL
                + level.random.nextInt(HEARTBEAT_MAX_INTERVAL - HEARTBEAT_MIN_INTERVAL + 1);
    }

    private static void playOneShot(Minecraft client, SoundEvent event) {
        client.getSoundManager().play(SimpleSoundInstance.forAmbientAddition(event));
    }

    private static void stopHeartbeat(Minecraft client) {
        if (heartbeatSound != null) client.getSoundManager().stop(heartbeatSound);
        heartbeatSound = null;
        heartbeatPlaying = false;
    }

    private static void reset() {
        stopHeartbeat(Minecraft.getInstance());
        if (sound != null) sound.end();
        if (closeSound != null) closeSound.end();
        sound = null;
        currentLoopEvent = null;
        closeSound = null;
        center = null;
        cursor = VOLUME;
        hiveDensityNearby = 0;
        stableHiveDensity = 0;
        zoneScanReady = false;
        closeHiveBlockCount = 0;
        insideStructure = false;
        nearestHive = Double.POSITIVE_INFINITY;
        nextPulseAt = NO_SCHEDULED_TIME;
        nextTonalStingerAt = NO_SCHEDULED_TIME;
        nextHeartbeatAt = NO_SCHEDULED_TIME;
        nextHiveHeartbeatEvent = true;

        currentZone = -1;
        pendingZone = -1;
        pendingZoneTicks = 0;
        heartbeatPlaying = false;
        zoneKnown = false;
    }

}
```

## `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundInstance.java`

```java
package com.carnis.mod.client.sound;

import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;

/** Streamed non-positional Hive bed with a forty-tick fade in/out. */
public final class HiveAmbientSoundInstance extends AbstractTickableSoundInstance {
    private static final float MAX_VOLUME = 0.85F;
    private static final float FADE_PER_TICK = MAX_VOLUME / 40.0F;
    private final ClientLevel world;
    private float desired;
    private float fadeOutStartVolume;
    private int fadeOutTicksRemaining;

    public HiveAmbientSoundInstance(ClientLevel world, SoundEvent event, float target) {
        super(event, SoundSource.AMBIENT, SoundInstance.createUnseededRandom());
        this.world = world;
        this.looping = true;
        this.delay = 0;
        this.relative = true;
        this.attenuation = SoundInstance.Attenuation.NONE;
        this.volume = 0.0F;
        this.pitch = 1.0F;
        setTarget(target);
    }

    public void setTarget(float target) {
        float next = Mth.clamp(target, 0.0F, MAX_VOLUME);
        if (next <= 0.0F && desired > 0.0F) {
            fadeOutStartVolume = volume;
            fadeOutTicksRemaining = 40;
        } else if (next > 0.0F) {
            fadeOutTicksRemaining = 0;
        }
        desired = next;
    }

    public void end() {
        stop();
    }

    @Override
    public boolean canStartSilent() {
        return true;
    }

    @Override
    public void tick() {
        Minecraft client = Minecraft.getInstance();
        if (client.level != world || client.player == null) {
            stop();
            return;
        }

        if (desired <= 0.0F) {
            if (fadeOutTicksRemaining > 0) {
                fadeOutTicksRemaining--;
                volume = fadeOutStartVolume * fadeOutTicksRemaining / 40.0F;
            } else {
                volume = 0.0F;
                stop();
            }
            return;
        }

        float difference = desired - volume;
        volume += Mth.clamp(difference, -FADE_PER_TICK, FADE_PER_TICK);
    }
}
```

## `src/main/java/com/carnis/mod/client/sound/PhantomSoundManager.java`

```java
package com.carnis.mod.client.sound;

import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.hallucination.HallucinationType;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.network.packet.ClientboundHallucinationPacket;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public final class PhantomSoundManager {
    private PhantomSoundManager() {
    }

    public static void handle(ClientboundHallucinationPacket packet) {
        if (!CarnisConfig.CLIENT.hallucinationSoundsEnabled.get()) {
            return;
        }

        Minecraft minecraft = Minecraft.getInstance();
        ClientLevel level = minecraft.level;
        LocalPlayer player = minecraft.player;

        if (level == null || player == null) {
            return;
        }

        if (NeuroResonatorHelmetItem.isEquipped(player)) {
            return;
        }

        float configuredVolume = CarnisConfig.CLIENT
                .hallucinationSoundVolume
                .get()
                .floatValue();
        float volume = Math.max(
                0.0F,
                Math.min(2.0F, packet.volumeMultiplier() * configuredVolume)
        );

        if (volume <= 0.0F) {
            return;
        }

        Vec3 worldOffset = rotateLocalOffset(
                packet.relativeOffset(),
                player.getYRot()
        );
        Vec3 soundPosition = player.position().add(worldOffset);

        level.playLocalSound(
                soundPosition.x,
                soundPosition.y,
                soundPosition.z,
                soundFor(packet.type()),
                sourceFor(packet.type()),
                volume,
                1.0F,
                false
        );
    }

    private static Vec3 rotateLocalOffset(
            Vec3 localOffset,
            float playerYawDegrees
    ) {
        double yawRadians = Math.toRadians(playerYawDegrees);
        Vec3 forward = new Vec3(
                -Math.sin(yawRadians),
                0.0D,
                Math.cos(yawRadians)
        );
        Vec3 right = new Vec3(-forward.z, 0.0D, forward.x);

        return right.scale(localOffset.x)
                .add(0.0D, localOffset.y, 0.0D)
                .add(forward.scale(localOffset.z));
    }

    private static SoundEvent soundFor(HallucinationType type) {
        return switch (type) {
            case CREEPER_HISS -> ModSounds.PHANTOM_CREEPER.get();
            case PHANTOM_FOOTSTEPS -> ModSounds.PHANTOM_FOOTSTEPS.get();
            case WHISPER -> ModSounds.PHANTOM_WHISPER.get();
            case FALSE_DAMAGE -> SoundEvents.PLAYER_HURT;
        };
    }

    private static SoundSource sourceFor(HallucinationType type) {
        return type == HallucinationType.FALSE_DAMAGE
                ? SoundSource.PLAYERS
                : SoundSource.AMBIENT;
    }

}
```

## `src/main/java/com/carnis/mod/command/CarnisCommands.java`

```java
package com.carnis.mod.command;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.biomass.PlayerBiomassCapability;
import com.carnis.mod.capability.biomass.PlayerBiomassEvents;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import com.carnis.mod.world.CarnisWorldData.AdaptationType;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.LongArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.mojang.brigadier.exceptions.DynamicCommandExceptionType;
import com.mojang.brigadier.suggestion.Suggestions;
import com.mojang.brigadier.suggestion.SuggestionsBuilder;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.ChunkPos;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Locale;
import java.util.concurrent.CompletableFuture;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class CarnisCommands {
    private static final int REQUIRED_PERMISSION_LEVEL = 2;
    private static final int DEFAULT_SHOCK_RADIUS_CHUNKS =
            CarnisWorldData.SYNAPSE_SHOCK_RADIUS_CHUNKS;
    private static final int MAX_SHOCK_RADIUS_CHUNKS = 16;

    private static final String VALID_ADAPTATION_TYPES =
            "FIRE, RANGED, MELEE, PILLARING, EXPLOSIVE, DARK";

    private static final DynamicCommandExceptionType
            INVALID_ADAPTATION_TYPE = new DynamicCommandExceptionType(
                    value -> Component.literal(
                            "Неизвестный тип адаптации '"
                                    + value
                                    + "'. Допустимые значения: "
                                    + VALID_ADAPTATION_TYPES
                    )
            );

    private CarnisCommands() {
    }

    @SubscribeEvent
    public static void onRegisterCommands(RegisterCommandsEvent event) {
        register(event.getDispatcher());
    }

    private static void register(
            CommandDispatcher<CommandSourceStack> dispatcher
    ) {
        dispatcher.register(
                Commands.literal("carnis")
                        .requires(
                                source -> source.hasPermission(
                                        REQUIRED_PERMISSION_LEVEL
                                )
                        )
                        .then(
                                Commands.literal("infection")
                                        .then(Commands.argument("targets", EntityArgument.players())
                                                .then(Commands.literal("get")
                                                        .executes(context -> infection(context, "get")))
                                                .then(Commands.literal("set")
                                                        .then(Commands.argument("value", FloatArgumentType.floatArg(0.0F, 100.0F))
                                                                .executes(context -> infection(context, "set"))))
                                                .then(Commands.literal("add")
                                                        .then(Commands.argument("value", FloatArgumentType.floatArg())
                                                                .executes(context -> infection(context, "add")))))
                        )
                        .then(
                                Commands.literal("info")
                                        .executes(CarnisCommands::showInfo)
                        )
                        .then(
                                Commands.literal("add_points")
                                        .then(
                                                Commands.argument(
                                                                "amount",
                                                                LongArgumentType.longArg(1L, 1000000L)
                                                        )
                                                        .executes(
                                                                CarnisCommands::addPoints
                                                        )
                                        )
                        )
                        .then(
                                Commands.literal("set_points")
                                        .then(
                                                Commands.argument(
                                                                "amount",
                                                                LongArgumentType.longArg(0L, 1000000L)
                                                        )
                                                        .executes(CarnisCommands::setPoints)
                                        )
                        )
                        .then(
                                Commands.literal("set_adaptation")
                                        .then(
                                                Commands.argument(
                                                                "type",
                                                                StringArgumentType.word()
                                                        )
                                                        .suggests(
                                                                CarnisCommands::suggestAdaptationTypes
                                                        )
                                                        .then(
                                                                Commands.argument(
                                                                                "level",
                                                                                LongArgumentType.longArg(
                                                                                        0L
                                                                                )
                                                                        )
                                                                        .executes(
                                                                                CarnisCommands::setAdaptation
                                                                        )
                                                        )
                                        )
                        )
                        .then(
                                Commands.literal("shock_chunk")
                                        .executes(
                                                context -> shockChunk(
                                                        context,
                                                        DEFAULT_SHOCK_RADIUS_CHUNKS
                                                )
                                        )
                                        .then(
                                                Commands.argument(
                                                                "radius",
                                                                IntegerArgumentType.integer(
                                                                        0,
                                                                        MAX_SHOCK_RADIUS_CHUNKS
                                                                )
                                                        )
                                                        .executes(
                                                                context -> shockChunk(
                                                                        context,
                                                                        IntegerArgumentType.getInteger(
                                                                                context,
                                                                                "radius"
                                                                        )
                                                                )
                                                        )
                                        )
                        )
        );
    }

    private static int infection(CommandContext<CommandSourceStack> context, String action)
            throws CommandSyntaxException {
        var players = EntityArgument.getPlayers(context, "targets");
        float amount = action.equals("get") ? 0.0F : FloatArgumentType.getFloat(context, "value");
        for (ServerPlayer player : players) {
            if (action.equals("set")) {
                PlayerInfectionApi.setInfectionLevel(player, amount);
            } else if (action.equals("add")) {
                PlayerInfectionApi.addInfection(player, amount);
            }
            float current = PlayerInfectionApi.getInfectionLevel(player);
            context.getSource().sendSuccess(
                    () -> Component.literal(player.getGameProfile().getName() + ": " + current + "%"),
                    !action.equals("get")
            );
        }
        return players.size();
    }

    private static int showInfo(
            CommandContext<CommandSourceStack> context
    ) {
        CommandSourceStack source = context.getSource();
        ServerLevel serverLevel = source.getLevel();
        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);
        ChunkPos chunkPos = getSourceChunk(source);
        long currentGameTime = serverLevel.getGameTime();
        Long expiresAt = worldData.getShockedChunks().get(chunkPos);
        long remainingShockTicks = expiresAt == null
                || expiresAt <= currentGameTime
                ? 0L
                : expiresAt - currentGameTime;
        long remainingShockSeconds = remainingShockTicks / 20L;

        if (remainingShockTicks % 20L != 0L) {
            remainingShockSeconds++;
        }

        source.sendSuccess(
                () -> Component.literal(
                                "=== Carnis: Adaptive Hivemind ==="
                        )
                        .withStyle(ChatFormatting.DARK_RED),
                false
        );
        source.sendSuccess(
                () -> Component.literal(
                        "Измерение: "
                                + serverLevel.dimension().location()
                ),
                false
        );
        source.sendSuccess(
                () -> Component.literal(
                                "Очки биомассы: "
                                        + worldData.getBiomassPoints()
                        )
                        .withStyle(ChatFormatting.GOLD),
                false
        );

        if (remainingShockTicks > 0L) {
            long displayedSeconds = remainingShockSeconds;
            source.sendSuccess(
                    () -> Component.literal(
                                    "Чанк ["
                                            + chunkPos.x
                                            + ", "
                                            + chunkPos.z
                                            + "]: ШОК АКТИВЕН, осталось "
                                            + displayedSeconds
                                            + " с ("
                                            + remainingShockTicks
                                            + " тиков)"
                            )
                            .withStyle(ChatFormatting.AQUA),
                    false
            );
        } else {
            source.sendSuccess(
                    () -> Component.literal(
                                    "Чанк ["
                                            + chunkPos.x
                                            + ", "
                                            + chunkPos.z
                                            + "]: шок неактивен"
                            )
                            .withStyle(ChatFormatting.GRAY),
                    false
            );
        }

        source.sendSuccess(
                () -> Component.literal("Матрица адаптации:")
                        .withStyle(ChatFormatting.DARK_AQUA),
                false
        );

        for (AdaptationType type : AdaptationType.values()) {
            long adaptationLevel = worldData.getAdaptation(type);
            source.sendSuccess(
                    () -> Component.literal(
                            "  " + type.name() + ": " + adaptationLevel
                    ),
                    false
            );
        }

        return 1;
    }

    private static int addPoints(
            CommandContext<CommandSourceStack> context
    ) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        long amount = LongArgumentType.getLong(context, "amount");
        var biomass = player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS);
        if (!biomass.isPresent()) {
            player.sendSystemMessage(Component.literal(
                    "§c[Carnis] Ошибка: данные биомассы не найдены"));
            return 0;
        }
        biomass.ifPresent(data -> {
            data.addBiomassPoints(amount);
            PlayerBiomassEvents.syncToPlayer(player);
            player.sendSystemMessage(Component.literal(
                    "§a[Carnis] Добавлено " + amount + " биомассы. Итого: "
                            + data.getBiomassPoints()));
        });
        return 1;
    }

    private static int setPoints(
            CommandContext<CommandSourceStack> context
    ) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        long amount = LongArgumentType.getLong(context, "amount");
        var biomass = player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS);
        if (!biomass.isPresent()) {
            player.sendSystemMessage(Component.literal(
                    "§c[Carnis] Ошибка: данные биомассы не найдены"));
            return 0;
        }
        biomass.ifPresent(data -> {
            data.setBiomassPoints(amount);
            PlayerBiomassEvents.syncToPlayer(player);
            player.sendSystemMessage(Component.literal(
                    "§a[Carnis] Биомасса установлена: " + amount));
        });
        return amount > 0L ? 1 : 0;
    }

    private static int setAdaptation(
            CommandContext<CommandSourceStack> context
    ) throws CommandSyntaxException {
        CommandSourceStack source = context.getSource();
        ServerLevel serverLevel = source.getLevel();
        String rawType = StringArgumentType.getString(context, "type");
        AdaptationType type = parseAdaptationType(rawType);
        long requestedLevel = LongArgumentType.getLong(context, "level");
        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);
        long previousLevel = worldData.getAdaptation(type);
        long updatedLevel = worldData.setAdaptation(type, requestedLevel);
        boolean changed = updatedLevel != previousLevel;

        if (changed) {
            ModMessages.sendToPlayersInLevel(serverLevel);
        }

        ChatFormatting color = changed
                ? ChatFormatting.GREEN
                : ChatFormatting.YELLOW;
        source.sendSuccess(
                () -> Component.literal(
                                "Адаптация "
                                        + type.name()
                                        + ": "
                                        + previousLevel
                                        + " -> "
                                        + updatedLevel
                        )
                        .withStyle(color),
                changed
        );

        return 1;
    }

    private static int shockChunk(
            CommandContext<CommandSourceStack> context,
            int radiusChunks
    ) {
        CommandSourceStack source = context.getSource();
        ServerLevel serverLevel = source.getLevel();
        ChunkPos centerChunk = getSourceChunk(source);
        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);
        int changedChunks = worldData.shockChunkArea(
                centerChunk,
                radiusChunks,
                serverLevel.getGameTime()
        );
        boolean changed = changedChunks > 0;

        if (changed) {
            ModMessages.sendToPlayersInLevel(serverLevel);
        }

        int diameterChunks = radiusChunks * 2 + 1;
        long durationSeconds =
                CarnisWorldData.SYNAPSE_SHOCK_DURATION_TICKS / 20L;
        ChatFormatting color = changed
                ? ChatFormatting.AQUA
                : ChatFormatting.YELLOW;

        source.sendSuccess(
                () -> Component.literal(
                                "Шок чанков: центр ["
                                        + centerChunk.x
                                        + ", "
                                        + centerChunk.z
                                        + "], радиус "
                                        + radiusChunks
                                        + ", область "
                                        + diameterChunks
                                        + "x"
                                        + diameterChunks
                                        + ", длительность "
                                        + durationSeconds
                                        + " с, обновлено чанков: "
                                        + changedChunks
                        )
                        .withStyle(color),
                changed
        );

        return 1;
    }

    private static AdaptationType parseAdaptationType(String rawType)
            throws CommandSyntaxException {
        try {
            return AdaptationType.valueOf(
                    rawType.toUpperCase(Locale.ROOT)
            );
        } catch (IllegalArgumentException exception) {
            throw INVALID_ADAPTATION_TYPE.create(rawType);
        }
    }

    private static CompletableFuture<Suggestions> suggestAdaptationTypes(
            CommandContext<CommandSourceStack> context,
            SuggestionsBuilder builder
    ) {
        String remaining = builder.getRemaining().toUpperCase(Locale.ROOT);

        for (AdaptationType type : AdaptationType.values()) {
            if (type.name().startsWith(remaining)) {
                builder.suggest(type.name());
            }
        }

        return builder.buildFuture();
    }

    private static ChunkPos getSourceChunk(CommandSourceStack source) {
        return new ChunkPos(BlockPos.containing(source.getPosition()));
    }
}
```

## `src/main/java/com/carnis/mod/config/CarnisConfig.java`

```java
package com.carnis.mod.config;

import net.minecraftforge.common.ForgeConfigSpec;

public final class CarnisConfig {
    public static final Server SERVER;
    public static final ForgeConfigSpec SERVER_SPEC;

    public static final Client CLIENT;
    public static final ForgeConfigSpec CLIENT_SPEC;

    static {
        ForgeConfigSpec.Builder serverBuilder = new ForgeConfigSpec.Builder();
        SERVER = new Server(serverBuilder);
        SERVER_SPEC = serverBuilder.build();

        ForgeConfigSpec.Builder clientBuilder = new ForgeConfigSpec.Builder();
        CLIENT = new Client(clientBuilder);
        CLIENT_SPEC = clientBuilder.build();
    }

    private CarnisConfig() {
    }

    public static final class Server {
        public final ForgeConfigSpec.IntValue infectionBlocksPerTick;
        public final ForgeConfigSpec.IntValue pulsingHeartQueueBonus;
        public final ForgeConfigSpec.IntValue digestorMaxItemsPerCycle;
        public final ForgeConfigSpec.BooleanValue debugLogging;
        public final ForgeConfigSpec.IntValue growthSuppressionRadius;
        public final ForgeConfigSpec.IntValue growthSuppressionStrength;
        public final ForgeConfigSpec.IntValue hiveEyeAuraRadius;
        public final ForgeConfigSpec.BooleanValue hiveEyeBuffsEnabled;
        public final ForgeConfigSpec.BooleanValue hiveEyeDebuffsEnabled;
        public final ForgeConfigSpec.IntValue nervePillarAuraRadius;
        public final ForgeConfigSpec.BooleanValue nervePillarBuffsEnabled;
        public final ForgeConfigSpec.BooleanValue nervePillarDebuffsEnabled;

        private Server(ForgeConfigSpec.Builder builder) {
            builder.comment("Server-side gameplay and performance settings.")
                    .push("server");

            builder.comment("Optimized infection queue settings.")
                    .push("infection_queue");

            infectionBlocksPerTick = builder
                    .comment("Maximum number of queued infection positions processed per server tick.")
                    .defineInRange("blocks_per_tick", 64, 1, 4096);

            pulsingHeartQueueBonus = builder
                    .comment("Additional queued positions a nearby Pulsing Heart may process per server tick.")
                    .defineInRange("pulsing_heart_bonus", 32, 0, 1024);

            builder.pop();

            builder.comment("Living organ settings.")
                    .push("organs");

            digestorMaxItemsPerCycle = builder
                    .comment("Maximum number of item entities a Digestor Pit may consume during one cycle.")
                    .defineInRange("digestor_max_items_per_cycle", 16, 1, 256);

            builder.pop();

            debugLogging = builder
                    .comment("Writes additional Carnis diagnostics to the server log.")
                    .define("debug_logging", false);

            growthSuppressionRadius = builder
                    .comment("Радиус кубической зоны подавления роста флоры вокруг блоков Улья.")
                    .defineInRange("growth_suppression_radius", 8, 1, 32);

            growthSuppressionStrength = builder
                    .comment("Сила подавления роста флоры: от 0 (отключено) до 100 (полное подавление).")
                    .defineInRange("growth_suppression_strength", 80, 0, 100);

            hiveEyeAuraRadius = builder
                    .comment("Радиус действия ауры Ока Улья в блоках.")
                    .defineInRange("hive_eye_aura_radius", 16, 4, 48);

            hiveEyeBuffsEnabled = builder
                    .comment("Включает баффы существ Улья в ауре Ока.")
                    .define("hive_eye_buffs_enabled", true);

            hiveEyeDebuffsEnabled = builder
                    .comment("Включает дебаффы игроков-угроз в ауре Ока.")
                    .define("hive_eye_debuffs_enabled", true);

            nervePillarAuraRadius = builder
                    .comment("Радиус действия ауры Нервного Столба в блоках.")
                    .defineInRange("nerve_pillar_aura_radius", 8, 2, 32);

            nervePillarBuffsEnabled = builder
                    .comment("Включает регенерацию союзников Улья в ауре Нервного Столба.")
                    .define("nerve_pillar_buffs_enabled", true);

            nervePillarDebuffsEnabled = builder
                    .comment("Включает эффект утомления игроков в ауре Нервного Столба.")
                    .define("nerve_pillar_debuffs_enabled", true);

            builder.pop();
        }
    }

    public static final class Client {
        public final ForgeConfigSpec.BooleanValue veinOverlayEnabled;
        public final ForgeConfigSpec.DoubleValue veinOverlayIntensity;
        public final ForgeConfigSpec.BooleanValue phantomEyesEnabled;
        public final ForgeConfigSpec.DoubleValue phantomEyesIntensity;
        public final ForgeConfigSpec.BooleanValue hallucinationSoundsEnabled;
        public final ForgeConfigSpec.DoubleValue hallucinationSoundVolume;
        public final ForgeConfigSpec.BooleanValue atmosphericFogEnabled;
        public final ForgeConfigSpec.DoubleValue neuroSonarOpacity;

        private Client(ForgeConfigSpec.Builder builder) {
            builder.comment("Client-only presentation settings. No gameplay logic is stored here.")
                    .push("client");

            builder.comment("Procedural hallucination overlay settings.")
                    .push("hallucinations");

            veinOverlayEnabled = builder
                    .comment("Enables the procedural pulsing-vein screen overlay.")
                    .define("vein_overlay_enabled", true);

            veinOverlayIntensity = builder
                    .comment("Opacity multiplier for the procedural vein overlay.")
                    .defineInRange("vein_overlay_intensity", 1.0D, 0.0D, 1.0D);

            phantomEyesEnabled = builder
                    .comment("Enables phantom eyes at the edge of the screen.")
                    .define("phantom_eyes_enabled", true);

            phantomEyesIntensity = builder
                    .comment("Size and opacity multiplier for phantom eyes.")
                    .defineInRange("phantom_eyes_intensity", 1.0D, 0.5D, 2.0D);

            hallucinationSoundsEnabled = builder
                    .comment("Enables client-side phantom sounds triggered by server packets.")
                    .define("hallucination_sounds_enabled", true);

            hallucinationSoundVolume = builder
                    .comment("Volume multiplier for phantom hallucination sounds.")
                    .defineInRange("hallucination_sound_volume", 0.75D, 0.0D, 1.0D);

            builder.pop();

            neuroSonarOpacity = builder.comment("Neuro-resonance visor and sonar opacity, 0 to 1.")
                    .defineInRange("neuro_sonar_opacity", 0.65D, 0.0D, 1.0D);

            builder.comment("Infection atmosphere settings.")
                    .push("atmosphere");

            atmosphericFogEnabled = builder
                    .comment("Enables infection-driven atmospheric fog color and distance.")
                    .define("atmospheric_fog_enabled", true);

            builder.pop();
            builder.pop();
        }
    }
}
```

## `src/main/java/com/carnis/mod/datagen/DataGenerators.java`

```java
package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import net.minecraft.data.DataGenerator;
import net.minecraft.data.PackOutput;
import net.minecraftforge.common.data.ExistingFileHelper;
import net.minecraftforge.data.event.GatherDataEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class DataGenerators {
    private DataGenerators() { }

    @SubscribeEvent
    public static void gatherData(GatherDataEvent event) {
        DataGenerator generator = event.getGenerator();
        PackOutput output = generator.getPackOutput();
        ExistingFileHelper existingFileHelper = event.getExistingFileHelper();

        // Client assets
        generator.addProvider(event.includeClient(), new ModBlockStateProvider(output, existingFileHelper));
        generator.addProvider(event.includeClient(), new ModItemModelProvider(output, existingFileHelper));

        // Server data
        generator.addProvider(event.includeServer(),
                new ModBlockTagsProvider(output, event.getLookupProvider(), existingFileHelper));
    }
}
```

## `src/main/java/com/carnis/mod/datagen/ModBlockStateProvider.java`

```java
package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.client.model.generators.BlockModelBuilder;
import net.minecraftforge.client.model.generators.BlockStateProvider;
import net.minecraftforge.client.model.generators.ConfiguredModel;
import net.minecraftforge.common.data.ExistingFileHelper;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;

public final class ModBlockStateProvider extends BlockStateProvider {
    public ModBlockStateProvider(PackOutput output, ExistingFileHelper exFileHelper) {
        super(output, CarnisMod.MOD_ID, exFileHelper);
    }

    @Override
    protected void registerStatesAndModels() {
        fleshVariants(ModBlocks.LIVING_FLESH);
        fleshVariants(ModBlocks.OSSIFIED_FLESH);
        fleshVariants(ModBlocks.CHARRED_FLESH);
        fleshVariants(ModBlocks.FIREPROOF_FLESH);
        simpleBlock(ModBlocks.HIVE_MEMBRANE.get(), models().cubeAll("hive_membrane",
                new ResourceLocation(CarnisMod.MOD_ID, "block/hive_membrane")));
        BlockModelBuilder synapse = models().cubeAll("synapse_node",
                new ResourceLocation(CarnisMod.MOD_ID, "block/synapse_node"));
        getVariantBuilder(ModBlocks.SYNAPSE_NODE.get()).forAllStates(state ->
                ConfiguredModel.builder().modelFile(synapse).build());
        simpleBlock(ModBlocks.INCUBATION_CYST.get(), models().cubeAll("incubation_cyst",
                new ResourceLocation(CarnisMod.MOD_ID, "block/incubation_cyst")));
        simpleBlock(ModBlocks.PURIFIER_LAMP.get(), models().cubeAll("purifier_lamp",
                new ResourceLocation(CarnisMod.MOD_ID, "block/purifier_lamp")));
        // Neural moss uses a hand-authored carpet model.
        // Pustule state is rendered by its block entity.

        // Sprout open and closed states use hand-authored models.
        // Flesh bulb and biomass remains use hand-authored state and composite models in main resources.
        // Sinew spikes use a hand-authored 3D panel model.

        geoBlock(ModBlocks.CREEPING_TENDRILS, "creeping_tendrils");
    }

    private void fleshVariants(RegistryObject<? extends Block> block) {
        String name = block.getId().getPath();
        List<ConfiguredModel> variants = new ArrayList<>();
        for (int variant = 0; variant < 4; variant++) {
            String variantName = name + "_" + variant;
            BlockModelBuilder model = models().cubeAll(variantName,
                    new ResourceLocation(CarnisMod.MOD_ID, "block/" + variantName));
            for (int x = 0; x < 360; x += 90) {
                for (int y = 0; y < 360; y += 90) {
                    variants.add(ConfiguredModel.builder().modelFile(model)
                            .rotationX(x).rotationY(y).build()[0]);
                }
            }
        }
        getVariantBuilder(block.get()).partialState().setModels(variants.toArray(new ConfiguredModel[0]));
        models().cubeAll(name, new ResourceLocation(CarnisMod.MOD_ID, "block/" + name + "_0"));
    }

    private void simpleCube(RegistryObject<? extends Block> block, String texture) {
        simpleBlock(block.get(), models().cubeAll(block.getId().getPath(),
                new ResourceLocation(CarnisMod.MOD_ID, "block/" + texture)));
    }

    private void crossBlock(RegistryObject<? extends Block> block, String texture) {
        simpleBlock(block.get(), models().cross(block.getId().getPath(),
                new ResourceLocation(CarnisMod.MOD_ID, "block/" + texture)).renderType("cutout"));
    }

    private void geoBlock(RegistryObject<? extends Block> block, String particleTexture) {
        simpleBlock(block.get(), models().getBuilder(block.getId().getPath())
                .texture("particle", new ResourceLocation(CarnisMod.MOD_ID, "block/" + particleTexture)));
    }
}
```

## `src/main/java/com/carnis/mod/datagen/ModBlockTagsProvider.java`

```java
package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlockTags;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.common.data.BlockTagsProvider;
import net.minecraftforge.common.data.ExistingFileHelper;

import java.util.concurrent.CompletableFuture;

public final class ModBlockTagsProvider extends BlockTagsProvider {
    public ModBlockTagsProvider(
            PackOutput output,
            CompletableFuture<HolderLookup.Provider> lookupProvider,
            ExistingFileHelper existingFileHelper
    ) {
        super(
                output,
                lookupProvider,
                CarnisMod.MOD_ID,
                existingFileHelper
        );
    }

    @Override
    protected void addTags(HolderLookup.Provider provider) {
        tag(ModBlockTags.HIVE_BLOCKS).add(
                ModBlocks.BIOMASS_REMAINS.get(), ModBlocks.CHARRED_FLESH.get(), ModBlocks.CREEPING_TENDRILS.get(),
                ModBlocks.FIREPROOF_FLESH.get(), ModBlocks.FLESH_BULB.get(), ModBlocks.FLESH_VEINS.get(),
                ModBlocks.HIVE_EYE.get(), ModBlocks.LIVING_FLESH.get(), ModBlocks.NEURAL_MOSS.get(),
                ModBlocks.NERVE_PILLAR.get(), ModBlocks.OSSIFIED_FLESH.get(), ModBlocks.PULSING_HEART.get(),
                ModBlocks.PUSTULE_CLUSTER.get(), ModBlocks.SINEW_SPIKES.get(), ModBlocks.SPORE_SPROUT.get(),
                ModBlocks.STOMACH_POOL.get(), ModBlocks.TAINTED_SLUDGE.get(), ModBlocks.HIVE_MEMBRANE.get(),
                ModBlocks.SYNAPSE_NODE.get(), ModBlocks.INCUBATION_CYST.get(), ModBlocks.PURIFIER_LAMP.get()
        );

        tag(ModBlockTags.INFECTIOUS_SURFACES)
                .add(
                        ModBlocks.LIVING_FLESH.get(),
                        ModBlocks.OSSIFIED_FLESH.get(),
                        ModBlocks.FIREPROOF_FLESH.get(),
                        ModBlocks.FLESH_VEINS.get(),
                        ModBlocks.PULSING_HEART.get(),
                        ModBlocks.NERVE_PILLAR.get(),
                        ModBlocks.STOMACH_POOL.get(),
                        ModBlocks.HIVE_EYE.get(),
                        ModBlocks.HIVE_MEMBRANE.get(),
                        ModBlocks.SYNAPSE_NODE.get(),
                        ModBlocks.INCUBATION_CYST.get()
                );

        tag(BlockTags.MINEABLE_WITH_HOE).add(ModBlocks.LIVING_FLESH.get(),
                ModBlocks.PUSTULE_CLUSTER.get(), ModBlocks.NEURAL_MOSS.get(), ModBlocks.STOMACH_POOL.get(),
                ModBlocks.FLESH_BULB.get(), ModBlocks.PULSING_HEART.get(), ModBlocks.HIVE_EYE.get(),
                ModBlocks.INCUBATION_CYST.get());
        tag(BlockTags.MINEABLE_WITH_AXE).add(ModBlocks.FLESH_VEINS.get(), ModBlocks.NERVE_PILLAR.get());
        tag(BlockTags.MINEABLE_WITH_PICKAXE).add(ModBlocks.OSSIFIED_FLESH.get(),
                ModBlocks.FIREPROOF_FLESH.get(), ModBlocks.CHARRED_FLESH.get(), ModBlocks.SINEW_SPIKES.get(),
                ModBlocks.HIVE_MEMBRANE.get(), ModBlocks.SYNAPSE_NODE.get(), ModBlocks.PURIFIER_LAMP.get());
        TagKey<Block> carnisBlocks = TagKey.create(Registries.BLOCK, new ResourceLocation(CarnisMod.MOD_ID, "carnis_blocks"));
        tag(carnisBlocks).add(ModBlocks.TAINTED_SLUDGE.get(), ModBlocks.FLESH_VEINS.get(),
                ModBlocks.FLESH_BULB.get(), ModBlocks.SINEW_SPIKES.get(), ModBlocks.NERVE_PILLAR.get(),
                ModBlocks.CREEPING_TENDRILS.get(), ModBlocks.PUSTULE_CLUSTER.get(), ModBlocks.STOMACH_POOL.get(),
                ModBlocks.SPORE_SPROUT.get(), ModBlocks.NEURAL_MOSS.get(), ModBlocks.CHARRED_FLESH.get(),
                ModBlocks.LIVING_FLESH.get(), ModBlocks.OSSIFIED_FLESH.get(), ModBlocks.FIREPROOF_FLESH.get(),
                ModBlocks.PULSING_HEART.get(), ModBlocks.HIVE_EYE.get(), ModBlocks.HIVE_MEMBRANE.get(),
                ModBlocks.SYNAPSE_NODE.get(), ModBlocks.INCUBATION_CYST.get(), ModBlocks.PURIFIER_LAMP.get());

        tag(BlockTags.NEEDS_STONE_TOOL)
                .add(ModBlocks.OSSIFIED_FLESH.get());

        tag(BlockTags.NEEDS_IRON_TOOL)
                .add(ModBlocks.FIREPROOF_FLESH.get());
    }
}
```

## `src/main/java/com/carnis/mod/datagen/ModItemModelProvider.java`

```java
package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModItems;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.client.model.generators.ItemModelProvider;
import net.minecraftforge.common.data.ExistingFileHelper;
import net.minecraftforge.registries.RegistryObject;

public final class ModItemModelProvider extends ItemModelProvider {
    public ModItemModelProvider(PackOutput output, ExistingFileHelper existingFileHelper) {
        super(output, CarnisMod.MOD_ID, existingFileHelper);
    }

    @Override
    protected void registerModels() {
        withExistingParent("stomach_pool", new ResourceLocation(CarnisMod.MOD_ID, "block/stomach_pool"));
        withExistingParent("nerve_pillar", new ResourceLocation(CarnisMod.MOD_ID, "block/nerve_pillar"));
        // Standard cube block items
        blockItem(ModBlocks.LIVING_FLESH);
        blockItem(ModBlocks.OSSIFIED_FLESH);
        blockItem(ModBlocks.CHARRED_FLESH);
        blockItem(ModBlocks.FIREPROOF_FLESH);
        withExistingParent("pustule_cluster", new ResourceLocation(CarnisMod.MOD_ID, "block/pustule_cluster"));

        // 2D flat item representation for Geo & organic hazard block items
        flatBlockItem(ModBlocks.SPORE_SPROUT);
        // Flesh bulb, moss, spikes, and remains item models are hand-authored in main resources.
        flatBlockItem(ModBlocks.CREEPING_TENDRILS);
        flatBlockItem(ModBlocks.FLESH_VEINS);

        blockItem(ModBlocks.HIVE_MEMBRANE);
        blockItem(ModBlocks.SYNAPSE_NODE);
        blockItem(ModBlocks.INCUBATION_CYST);
        blockItem(ModBlocks.PURIFIER_LAMP);
        // Standard flat items
        flatItem(ModItems.VIRAL_DART);
        flatItem(ModItems.PURIFICATION_DART);
        flatItem(ModItems.PURIFICATION_SERUM);
        flatItem(ModItems.NEURAL_BINDING_MATRIX);
        flatItem(ModItems.TAINTED_SLUDGE_BUCKET);
        flatItem(ModItems.FLESH_AMALGAM_SPAWN_EGG);
        flatItem(ModItems.SINEW_SHIELD);
        flatItem(ModItems.BONE_SCYTHE);
        flatItem(ModItems.OSSIFIED_SCYTHE);
        flatItem(ModItems.PUSTULE_GRENADE);
        flatItem(ModItems.PURIFICATION_VIAL);
    }

    private void blockItem(RegistryObject<? extends Block> block) {
        withExistingParent(block.getId().getPath(),
                new ResourceLocation(CarnisMod.MOD_ID, "block/" + block.getId().getPath()));
    }

    private void flatBlockItem(RegistryObject<? extends Block> block) {
        singleTexture(block.getId().getPath(),
                new ResourceLocation("minecraft", "item/generated"),
                "layer0",
                new ResourceLocation(CarnisMod.MOD_ID, "block/" + block.getId().getPath()));
    }

    private void flatItem(RegistryObject<? extends Item> item) {
        singleTexture(item.getId().getPath(),
                new ResourceLocation("minecraft", "item/generated"),
                "layer0",
                new ResourceLocation(CarnisMod.MOD_ID, "item/" + item.getId().getPath()));
    }
}
```

## `src/main/java/com/carnis/mod/ecology/FeedingEvents.java`

```java
package com.carnis.mod.ecology;
import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class FeedingEvents {
    private FeedingEvents() { }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onDeath(LivingDeathEvent event) {
        if (event.isCanceled() || !(event.getEntity().level() instanceof ServerLevel level)
                || !(event.getSource().getEntity() instanceof Mob hunter) || !(hunter instanceof HivemindLinkedMob)
                || !(hunter instanceof com.carnis.mod.entity.InfectedZombieEntity || hunter instanceof com.carnis.mod.entity.InfectedSkeletonEntity
                    || hunter instanceof com.carnis.mod.entity.InfectedCreeperEntity || hunter instanceof com.carnis.mod.entity.InfectedSpiderEntity)
                || !hunter.isAlive() || !CarnisHuntPreyGoal.isPrey(event.getEntity())) return;
        // One active feeding at a time; don't overwrite the pending award.
        var tag = hunter.getPersistentData();
        if (tag.contains(CarnisFeedingGoal.DEADLINE)) return;
        tag.putInt(CarnisFeedingGoal.DEADLINE, 0);
        tag.putInt("carnis:feeding_travel", 0);
        tag.putDouble(CarnisFeedingGoal.X, event.getEntity().getX());
        tag.putDouble(CarnisFeedingGoal.Y, event.getEntity().getY());
        tag.putDouble(CarnisFeedingGoal.Z, event.getEntity().getZ());
    }
}
```

## `src/main/java/com/carnis/mod/ecology/MaggotForaging.java`

```java
package com.carnis.mod.ecology;

import com.carnis.mod.entity.BiomassMaggotEntity;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.AABB;

import java.util.Set;

/** Invoked only from a flesh block's random tick; no world or block scan. */
public final class MaggotForaging {
    private static final Set<Item> MEAT = Set.of(Items.BEEF, Items.COOKED_BEEF, Items.PORKCHOP,
            Items.COOKED_PORKCHOP, Items.CHICKEN, Items.COOKED_CHICKEN, Items.MUTTON,
            Items.COOKED_MUTTON, Items.RABBIT, Items.COOKED_RABBIT, Items.ROTTEN_FLESH);
    private MaggotForaging() { }

    public static void onFleshRandomTick(ServerLevel level, BlockPos pos) {
        AABB local = new AABB(pos).inflate(4.0D, 2.0D, 4.0D);
        for (BiomassMaggotEntity maggot : level.getEntitiesOfClass(BiomassMaggotEntity.class, local, e -> e.isAlive())) {
            AABB reach = maggot.getBoundingBox().inflate(1.0D, 0.5D, 1.0D);
            for (ItemEntity item : level.getEntitiesOfClass(ItemEntity.class, reach,
                    e -> e.isAlive() && e.onGround() && MEAT.contains(e.getItem().getItem()))) {
                ItemStack stack = item.getItem();
                if (stack.isEmpty()) continue;
                stack.shrink(1);
                if (stack.isEmpty()) item.discard(); else item.setItem(stack);
                CarnisWorldData.get(level).addBiomassPoints(5L);
                ModMessages.sendToPlayersInLevel(level);
                return; // At most one item per invocation.
            }
        }
    }
}
```

## `src/main/java/com/carnis/mod/ecology/RemainsEvents.java`

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
                && IncubationEvents.supportsIncubation(victim) && !IncubationEvents.hasOwner(victim)
                && !IncubationEvents.isHostileHost(victim);
        if ((!hiveKill && !decomposition) || !ForgeEventFactory.getMobGriefingEvent(level, victim)) return;
        if (decomposition && !hiveKill && IncubationEvents.isNewAnimalHost(victim)
                && level.random.nextFloat() >= 0.4F) return;
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

## `src/main/java/com/carnis/mod/effect/ImmunosuppressionMobEffect.java`

```java
package com.carnis.mod.effect;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;

/** Positive infection changes are blocked by PlayerInfectionApi while this effect is active. */
public final class ImmunosuppressionMobEffect extends MobEffect {
    public ImmunosuppressionMobEffect() { super(MobEffectCategory.BENEFICIAL, 0x4A85A0); }
}
```

## `src/main/java/com/carnis/mod/effect/IncubatingMobEffect.java`

```java
package com.carnis.mod.effect;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;

/** Client-synchronized visual marker. Lifecycle is owned by InfectionHandler. */
public final class IncubatingMobEffect extends MobEffect {
    public IncubatingMobEffect() { super(MobEffectCategory.HARMFUL, 0x881B2B); }
}
```

## `src/main/java/com/carnis/mod/effect/ThermalShockEffect.java`

```java
package com.carnis.mod.effect;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModEffects;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ThermalShockEffect extends MobEffect {
    public ThermalShockEffect() {
        super(MobEffectCategory.HARMFUL, 0x3B6B8C);
        addAttributeModifier(Attributes.MOVEMENT_SPEED, "7e0881ae-07f3-48da-b5ae-17c8da3fe023",
                -0.30D, AttributeModifier.Operation.MULTIPLY_TOTAL);
    }

    /** Applied before ordinary mitigation; no additional damage event is fired. */
    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onHurt(LivingHurtEvent event) {
        if (!event.isCanceled() && event.getAmount() > 0.0F && !event.getEntity().level().isClientSide
                && event.getEntity().hasEffect(ModEffects.THERMAL_SHOCK.get()))
            event.setAmount(event.getAmount() * 1.25F);
    }
}
```

## `src/main/java/com/carnis/mod/entity/AmalgamBileProjectile.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.network.NetworkHooks;

public final class AmalgamBileProjectile extends ThrowableItemProjectile {
    public AmalgamBileProjectile(EntityType<? extends AmalgamBileProjectile> type, Level level) { super(type, level); }
    public AmalgamBileProjectile(Level level, LivingEntity owner) { super(ModEntities.AMALGAM_BILE.get(), owner, level); }
    @Override protected Item getDefaultItem() { return ModItems.AMALGAM_BILE_GLOB.get(); }
    @Override protected boolean canHitEntity(Entity entity) {
        return super.canHitEntity(entity) && !NeuroArmorEventHandler.isHiveEntity(entity)
                && (!(entity instanceof Player player) || !player.isCreative() && !player.isSpectator());
    }
    @Override public void tick() {
        super.tick();
        if (level().isClientSide && !isRemoved()) level().addParticle(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), 0, .01D, 0);
        if (!level().isClientSide && tickCount > 120) discard();
    }
    @Override protected void onHitEntity(EntityHitResult hit) {
        super.onHitEntity(hit);
        if (!(level() instanceof ServerLevel level) || !(hit.getEntity() instanceof LivingEntity target)) return;
        if (target.hurt(level.damageSources().thrown(this, getOwner()), 5.0F))
            target.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 0));
    }
    @Override protected void onHit(HitResult hit) {
        super.onHit(hit);
        if (level() instanceof ServerLevel level) {
            level.playSound(null, blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
            level.sendParticles(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), 14, .2D, .2D, .2D, .04D);
            discard();
        }
    }
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket() { return NetworkHooks.getEntitySpawningPacket(this); }
}
```

## `src/main/java/com/carnis/mod/entity/AssimilatingMob.java`

```java
package com.carnis.mod.entity;

/** Network-synchronised visual state and final biomass value for assimilating mobs. */
public interface AssimilatingMob extends BiomassValued {
    boolean isAssimilating();
    void setAssimilating(boolean assimilating);
}
```

## `src/main/java/com/carnis/mod/entity/BiomassMaggotEntity.java`

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
import net.minecraft.core.registries.Registries;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
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
    private static final TagKey<Block> BURROWABLE = TagKey.create(Registries.BLOCK,
            new ResourceLocation(CarnisMod.MOD_ID, "burrowable"));
    private static final EntityDataAccessor<Integer> ACTION = SynchedEntityData.defineId(
            BiomassMaggotEntity.class, EntityDataSerializers.INT);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.biomass_maggot.idle");
    private static final RawAnimation CRAWL = RawAnimation.begin().thenLoop("animation.biomass_maggot.crawl");
    private static final RawAnimation EAT = RawAnimation.begin().thenLoop("animation.biomass_maggot.eat");
    private static final RawAnimation BURROW = RawAnimation.begin().thenLoop("animation.biomass_maggot.burrow");
    private static final List<BlockPos> SEARCH_OFFSETS = buildOffsets();
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    // The travel goal hands off a reached block to the stationary work goal.
    private BlockPos pendingTarget;
    private WorkType pendingType;

    private enum WorkType { EAT, BURROW }

    public BiomassMaggotEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ACTION, 0);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 10.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.18D);
    }

    @Override protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new WorkGoal());
        goalSelector.addGoal(2, new BurrowGoal());
        goalSelector.addGoal(3, new EatRemainsGoal());
        goalSelector.addGoal(4, new WaterAvoidingRandomStrollGoal(this, 0.8D));
    }

    @Override protected void customServerAiStep() {
        BlockPos belowPos = blockPosition().below();
        int previous = getPersistentData().getInt(FLESH_TICKS);
        int ticks = previous;
        if (previous < 1200 && level().isLoaded(belowPos)) {
            BlockState below = level().getBlockState(belowPos);
            ticks = below.is(ModBlocks.LIVING_FLESH.get()) || below.is(ModBlocks.OSSIFIED_FLESH.get())
                    ? Math.min(1200, previous + 1) : 0;
        }
        getPersistentData().putInt(FLESH_TICKS, Math.min(1200, ticks));
        super.customServerAiStep();
    }

    private boolean readyToBurrow() {
        return getPersistentData().getInt(FED_COUNT) >= 2 || getPersistentData().getInt(FLESH_TICKS) >= 1200;
    }

    private static boolean isSafeBurrowMaterial(BlockState state) {
        return state.is(ModBlocks.LIVING_FLESH.get()) || state.is(ModBlocks.OSSIFIED_FLESH.get())
                || state.is(Blocks.DIRT) || state.is(Blocks.GRASS_BLOCK) || state.is(Blocks.PODZOL)
                || state.is(Blocks.MYCELIUM) || state.is(Blocks.MUD) || state.is(Blocks.SAND)
                || state.is(Blocks.GRAVEL) || state.is(Blocks.MOSS_BLOCK);
    }

    private boolean validTarget(WorkType type, BlockPos pos) {
        if (type == null || pos == null || !(level() instanceof ServerLevel server)
                || server.isOutsideBuildHeight(pos) || !server.hasChunkAt(pos)) return false;
        if (type == WorkType.EAT) {
            return !readyToBurrow() && server.getBlockState(pos).is(ModBlocks.BIOMASS_REMAINS.get());
        }
        BlockPos ground = pos.below();
        if (!readyToBurrow() || server.isOutsideBuildHeight(ground) || !server.hasChunkAt(ground)
                || !server.isEmptyBlock(pos)) return false;
        BlockState floor = server.getBlockState(ground);
        BlockState bulb = ModBlocks.FLESH_BULB.get().defaultBlockState().setValue(FleshBulbBlock.HANGING, false);
        return floor.is(BURROWABLE) && isSafeBurrowMaterial(floor)
                && floor.isFaceSturdy(server, ground, Direction.UP) && bulb.canSurvive(server, pos);
    }

    private boolean mayWork() {
        return isAlive() && level() instanceof ServerLevel server
                && ForgeEventFactory.getMobGriefingEvent(server, this);
    }

    private boolean closeTo(BlockPos pos) {
        return pos != null && distanceToSqr(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D) <= 1.7D;
    }

    private void queueWork(WorkType type, BlockPos pos) {
        pendingType = type;
        pendingTarget = pos.immutable();
    }

    private void clearPendingWork() {
        pendingTarget = null;
        pendingType = null;
    }

    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "locomotion", 2, state -> state.setAndContinue(
                entityData.get(ACTION) == 1 ? EAT : entityData.get(ACTION) == 2 ? BURROW : state.isMoving() ? CRAWL : IDLE)));
    }

    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }

    // Precomputed once. Each search attempt checks at most 256 positions, five ticks apart.
    private static List<BlockPos> buildOffsets() {
        List<BlockPos> offsets = new ArrayList<>();
        for (int x = -16; x <= 16; x++) for (int y = -16; y <= 16; y++) for (int z = -16; z <= 16; z++)
            if (x * x + y * y + z * z <= 256) offsets.add(new BlockPos(x, y, z));
        offsets.sort(Comparator.comparingInt(p -> p.getX() * p.getX() + p.getY() * p.getY() + p.getZ() * p.getZ()));
        return List.copyOf(offsets);
    }

    private abstract class SearchGoal extends Goal {
        private final WorkType type;
        private BlockPos target;
        private BlockPos anchor;
        private int cursor;
        private int searchCooldown;
        private int elapsed;

        SearchGoal(WorkType type) {
            this.type = type;
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        private boolean isValidTarget(BlockPos pos) { return validTarget(type, pos); }
        private boolean allowed() { return type == WorkType.BURROW ? readyToBurrow() : !readyToBurrow(); }

        private BlockPos findTarget(ServerLevel server) {
            if (anchor == null || anchor.distSqr(blockPosition()) > 4) {
                anchor = blockPosition();
                cursor = 0;
            }
            int end = Math.min(cursor + 256, SEARCH_OFFSETS.size());
            while (cursor < end) {
                BlockPos pos = anchor.offset(SEARCH_OFFSETS.get(cursor++));
                if (!server.isOutsideBuildHeight(pos) && server.hasChunkAt(pos) && isValidTarget(pos)) return pos;
            }
            if (cursor >= SEARCH_OFFSETS.size()) { cursor = 0; anchor = blockPosition(); }
            return null;
        }

        @Override public boolean canUse() {
            if (!(level() instanceof ServerLevel server) || pendingTarget != null || !allowed()
                    || tickCount < searchCooldown || !mayWork()) return false;
            searchCooldown = tickCount + 5;
            target = findTarget(server);
            return target != null;
        }

        @Override public boolean canContinueToUse() {
            boolean valid = target != null && level().isLoaded(target) && isValidTarget(target)
                    && allowed() && mayWork() && elapsed < 400;
            // Navigation can finish between AI ticks; transfer a reached target before stopping.
            if (valid && getNavigation().isDone() && closeTo(target)) queueWork(type, target);
            return valid && !getNavigation().isDone();
        }

        @Override public void start() {
            elapsed = 0;
            if (target == null || !level().isLoaded(target) || !isValidTarget(target) || !mayWork()) {
                stop();
                return;
            }
            if (closeTo(target)) {
                queueWork(type, target);
                stop();
            } else {
                getNavigation().moveTo(target.getX() + 0.5D, target.getY(), target.getZ() + 0.5D, 0.8D);
            }
        }

        @Override public void stop() {
            target = null;
            getNavigation().stop();
            entityData.set(ACTION, 0);
            anchor = null;
            cursor = 0;
        }

        @Override public boolean requiresUpdateEveryTick() { return true; }

        private boolean approach() {
            if (this.target == null) return false;
            if (closeTo(target)) return true;
            if (elapsed % 10 == 0)
                getNavigation().moveTo(target.getX() + 0.5D, target.getY(), target.getZ() + 0.5D, 0.8D);
            return false;
        }

        @Override public void tick() {
            if (target == null || !level().isLoaded(target) || !isValidTarget(target) || !mayWork()) {
                stop();
                return;
            }
            elapsed++;
            if (approach()) {
                queueWork(type, target);
                stop();
            }
        }
    }

    private final class EatRemainsGoal extends SearchGoal {
        EatRemainsGoal() { super(WorkType.EAT); }
    }

    private final class BurrowGoal extends SearchGoal {
        BurrowGoal() { super(WorkType.BURROW); }
    }

    /** Work continues while stationary; the search goal never pretends navigation is active. */
    private final class WorkGoal extends Goal {
        private BlockPos target;
        private WorkType type;
        private int workTicks;

        WorkGoal() { setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK)); }

        @Override public boolean canUse() {
            if (pendingTarget == null || pendingType == null) {
                clearPendingWork();
                return false;
            }
            if (!mayWork() || !level().isLoaded(pendingTarget) || !validTarget(pendingType, pendingTarget)
                    || !closeTo(pendingTarget)) {
                clearPendingWork();
                return false;
            }
            return true;
        }

        @Override public void start() {
            target = pendingTarget;
            type = pendingType;
            clearPendingWork();
            workTicks = 0;
            getNavigation().stop();
        }

        @Override public boolean canContinueToUse() {
            return target != null && type != null && level().isLoaded(target) && validTarget(type, target)
                    && closeTo(target) && mayWork();
        }

        @Override public boolean requiresUpdateEveryTick() { return true; }

        @Override public void stop() {
            target = null;
            type = null;
            workTicks = 0;
            getNavigation().stop();
            entityData.set(ACTION, 0);
        }

        @Override public void tick() {
            if (target == null || type == null || !(level() instanceof ServerLevel server)
                    || !server.isLoaded(target) || !validTarget(type, target) || !closeTo(target) || !mayWork()) {
                stop();
                return;
            }
            workTicks++;
            if (type == WorkType.EAT) {
                entityData.set(ACTION, 1);
                if (workTicks % 20 == 0) playSound(SoundEvents.GENERIC_EAT, 0.8F, 1.0F);
                if (workTicks >= 70) {
                    if (server.removeBlock(target, false)) {
                        getPersistentData().putInt(FED_COUNT, getPersistentData().getInt(FED_COUNT) + 1);
                        server.playSound(null, target, SoundEvents.GENERIC_EAT, SoundSource.HOSTILE, 1.0F, 1.0F);
                    }
                    stop();
                }
            } else {
                entityData.set(ACTION, 2);
                if (workTicks % 5 == 0) {
                    server.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, server.getBlockState(target.below())),
                            getX(), getY() + 0.1D, getZ(), 8, 0.15D, 0.05D, 0.15D, 0.03D);
                    server.sendParticles(ModParticles.BIOMASS_SPARK.get(), getX(), getY() + 0.1D, getZ(),
                            3, 0.1D, 0.05D, 0.1D, 0.02D);
                }
                if (workTicks >= 50) {
                    BlockState bulb = ModBlocks.FLESH_BULB.get().defaultBlockState().setValue(FleshBulbBlock.HANGING, false);
                    if (server.setBlockAndUpdate(target, bulb)) discard();
                    stop();
                }
            }
        }
    }
}
```

## `src/main/java/com/carnis/mod/entity/BiomassValued.java`

```java
package com.carnis.mod.entity;

/** Exposes an entity's explicit biomass value where the caller needs one. */
public interface BiomassValued {
    long getBiomassValue();
}
```

## `src/main/java/com/carnis/mod/entity/CerebralNexusEntity.java`

```java
package com.carnis.mod.entity;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/** Tier-two command node; later tier mechanics are intentionally not defined here. */
public final class CerebralNexusEntity extends Monster implements GeoEntity, HivemindLinkedMob, BiomassValued {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private long biomass;
    public CerebralNexusEntity(EntityType<? extends Monster> type, Level level) { super(type, level); setNoGravity(true); }
    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 120D).add(Attributes.ARMOR, 10D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1D).add(Attributes.MOVEMENT_SPEED, 0D);
    }
    @Override public long getBiomassValue() { return 100L; }
    public void setBiomass(long value) { biomass = Math.max(0L, value); }
    @Override public boolean isPushable() { return false; }
    @Override public void push(double x, double y, double z) { }
    @Override protected void registerGoals() { }
    @Override public void tick() { super.tick(); setDeltaMovement(0, 0, 0); }
    @Override public void addAdditionalSaveData(CompoundTag tag) { super.addAdditionalSaveData(tag); tag.putLong("Biomass", biomass); }
    @Override public void readAdditionalSaveData(CompoundTag tag) { super.readAdditionalSaveData(tag); biomass = Math.max(0, tag.getLong("Biomass")); }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "idle", 0, state -> state.setAndContinue(RawAnimation.begin().thenLoop("animation.cerebral_nexus.idle"))));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
```

## `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.ai.FleshAmalgamChargeGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.event.AcidAttackSlowdown;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.CarnisWorldData;
import com.carnis.mod.world.CarnisWorldData.AdaptationType;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class FleshAmalgamEntity extends HiveEntity
        implements GeoEntity, HivemindLinkedMob {
    private static final RawAnimation HURT_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.hurt");
    private static final RawAnimation DEATH_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.death");

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        level().playSound(null, getX(), getY(), getZ(), ModSounds.AMALGAM_STEP.get(),
                SoundSource.HOSTILE, 1.0F, 1.0F);
        if (tickCount % 4 == 0) {
            level().playSound(null, getX(), getY(), getZ(), ModSounds.HIVE_AMALGAM_SHUFFLE.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
    }

    public void triggerRoarAnimation() {
        if (!level().isClientSide) triggerAnim("roar_controller", "roar");
    }

    public void triggerSlamAnimation() {
        if (!level().isClientSide) triggerAnim("slam_controller", "slam");
    }

    private static final long BIOMASS_VALUE = 25L;

    public static final double MAX_HEALTH = 240.0D;
    public static final double KNOCKBACK_RESISTANCE = 1.0D;
    public static final double ATTACK_DAMAGE = 14.0D;
    public static final double MOVEMENT_SPEED = 0.22D;
    public static final double FOLLOW_RANGE = 32.0D;
    public static final double ARMOR = 12.0D;
    public static final double ARMOR_TOUGHNESS = 4.0D;

    public static final double CHARGE_TRIGGER_DISTANCE = 12.0D;

    private static final String REFLECTED_PROJECTILE_TAG =
            CarnisMod.MOD_ID + ":amalgam_reflected";

    private static final double PROJECTILE_REFLECTION_BASE_CHANCE = 0.06D;
    private static final double PROJECTILE_REFLECTION_CHANCE_PER_LEVEL = 0.0075D;
    private static final double PROJECTILE_REFLECTION_MAX_CHANCE = 0.45D;

    private static final double ACID_BASE_CHANCE = 0.08D;
    private static final double ACID_CHANCE_PER_LEVEL = 0.007D;
    private static final double ACID_MAX_CHANCE = 0.50D;
    private static final int ACID_BASE_ARMOR_DAMAGE = 2;
    private static final int ACID_MAX_ARMOR_DAMAGE = 6;
    private static final long ACID_LEVELS_PER_ARMOR_DAMAGE = 15L;
    private static final int ACID_BASE_DURATION_TICKS = 40;
    private static final int ACID_MAX_DURATION_TICKS = 100;
    private static final long ACID_EMPOWERED_SLOW_LEVEL = 50L;

    private static final double THORN_BASE_CHANCE = 0.08D;
    private static final double THORN_CHANCE_PER_LEVEL = 0.008D;
    private static final double THORN_MAX_CHANCE = 0.55D;
    private static final float THORN_BASE_DAMAGE = 1.5F;
    private static final float THORN_DAMAGE_PER_LEVEL = 0.05F;
    private static final float THORN_MAX_DAMAGE = 5.0F;

    private static final RawAnimation IDLE_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.flesh_amalgam.idle");
    private static final RawAnimation WALK_ANIMATION = RawAnimation.begin()
            .thenLoop("animation.flesh_amalgam.walk");
    private static final RawAnimation ATTACK_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.attack");
    private static final RawAnimation SLAM_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.slam");
    private static final RawAnimation ROAR_ANIMATION = RawAnimation.begin()
            .thenPlay("animation.flesh_amalgam.roar");

    private final net.minecraft.server.level.ServerBossEvent bossBar = new net.minecraft.server.level.ServerBossEvent(
            getDisplayName(), net.minecraft.world.BossEvent.BossBarColor.RED,
            net.minecraft.world.BossEvent.BossBarOverlay.NOTCHED_10);
    private final com.carnis.mod.entity.ai.AmalgamBiomassFeast biomassFeast =
            new com.carnis.mod.entity.ai.AmalgamBiomassFeast(this);
    private long slamReady;
    private long pullReady;
    private long bileReady;
    private long feastReady;

    private final AnimatableInstanceCache animationCache =
            GeckoLibUtil.createInstanceCache(this);

    public FleshAmalgamEntity(
            EntityType<? extends FleshAmalgamEntity> entityType,
            Level level
    ) {
        super(entityType, level);
        this.xpReward = 18;
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, MAX_HEALTH)
                .add(Attributes.KNOCKBACK_RESISTANCE, KNOCKBACK_RESISTANCE)
                .add(Attributes.ATTACK_DAMAGE, ATTACK_DAMAGE)
                .add(Attributes.MOVEMENT_SPEED, MOVEMENT_SPEED)
                .add(Attributes.FOLLOW_RANGE, FOLLOW_RANGE)
                .add(Attributes.ARMOR, ARMOR)
                .add(Attributes.ARMOR_TOUGHNESS, ARMOR_TOUGHNESS);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new com.carnis.mod.entity.ai.FleshAmalgamAbilityGoal(this));
        goalSelector.addGoal(2, new FleshAmalgamChargeGoal(this));
        goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.0D, false));
        goalSelector.addGoal(
                5,
                new WaterAvoidingRandomStrollGoal(this, 0.8D)
        );
        goalSelector.addGoal(
                6,
                new LookAtPlayerGoal(this, Player.class, 10.0F)
        );
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));

        targetSelector.addGoal(
                1,
                new NearestAttackableTargetGoal<>(
                        this,
                        Player.class,
                        true,
                        target -> target instanceof Player
                                && HiveSwarmCoordinator.validTarget(this, target)
                )
        );
        targetSelector.addGoal(
                2,
                new HurtByTargetGoal(this).setAlertOthers()
        );
    }


    @Override
    public void setTarget(LivingEntity target) {
        if (target != null && !HiveSwarmCoordinator.validTarget(this, target)) return;
        super.setTarget(target);
    }

    public boolean canUseAbility(int ability) {
        long now = level().getGameTime();
        return switch (ability) {
            case 1 -> now >= slamReady;
            case 2 -> now >= pullReady;
            case 3 -> now >= bileReady;
            default -> false;
        };
    }

    public void consumeAbilityCooldown(int ability) {
        long now = level().getGameTime();
        switch (ability) {
            case 1 -> slamReady = now + 160L;
            case 2 -> pullReady = now + 240L;
            case 3 -> bileReady = now + 200L;
            default -> throw new IllegalArgumentException("Unknown ability: " + ability);
        }
    }

    public long getFeastReady() { return feastReady; }
    public void setFeastReady(long tick) { feastReady = tick; }

    @Override
    public void tick() {
        super.tick();
        if (!(level() instanceof ServerLevel server)) return;
        if (!isAlive()) { bossBar.removeAllPlayers(); return; }
        bossBar.setProgress(net.minecraft.util.Mth.clamp(getHealth() / getMaxHealth(), 0.0F, 1.0F));
        bossBar.setName(getDisplayName());
        if (tickCount % 10 == 0) {
            for (ServerPlayer player : new java.util.ArrayList<>(bossBar.getPlayers())) {
                if (player.serverLevel() != server || !server.players().contains(player)
                        || !player.isAlive() || player.distanceToSqr(this) > 32.0D * 32.0D) bossBar.removePlayer(player);
            }
            for (ServerPlayer player : server.players()) {
                if (player.isAlive() && player.distanceToSqr(this) <= 32.0D * 32.0D) bossBar.addPlayer(player);
                else bossBar.removePlayer(player);
            }
        }
        if (!isNoAi()) biomassFeast.tick(server);
    }

    @Override
    public void remove(Entity.RemovalReason reason) {
        bossBar.removeAllPlayers();
        super.remove(reason);
    }

    @Override
    public void addAdditionalSaveData(net.minecraft.nbt.CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putLong("CarnisSlamReady", slamReady);
        tag.putLong("CarnisPullReady", pullReady);
        tag.putLong("CarnisBileReady", bileReady);
        tag.putLong("CarnisFeastReady", feastReady);
    }

    @Override
    public void readAdditionalSaveData(net.minecraft.nbt.CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        slamReady = tag.getLong("CarnisSlamReady");
        pullReady = tag.getLong("CarnisPullReady");
        bileReady = tag.getLong("CarnisBileReady");
        feastReady = tag.getLong("CarnisFeastReady");
    }

    @Override
    protected void customServerAiStep() {
        LivingEntity target = getTarget();
        if (target != null && !HiveSwarmCoordinator.validTarget(this, target)) setTarget(null);
        super.customServerAiStep();
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (!(level() instanceof ServerLevel serverLevel)) {
            return super.hurt(source, amount);
        }

        LivingEntity meleeAttacker = getDirectMeleeAttacker(source);
        boolean hurt = super.hurt(source, amount);
        if (hurt && isAlive() && !level().isClientSide) triggerAnim("damage_controller", "hurt");

        if (hurt && meleeAttacker != null) {
            trySpikedRetaliation(serverLevel, meleeAttacker);
        }

        return hurt;
    }

    @Override
    public void die(DamageSource source) {
        if (!level().isClientSide) triggerAnim("damage_controller", "death");
        super.die(source);
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);

        if (
                hit
                        && target instanceof ServerPlayer player
                        && level() instanceof ServerLevel serverLevel
        ) {
            tryAcidSplash(serverLevel, player);
        }

        return hit;
    }

    /**
     * Called from the Forge projectile-impact hook before vanilla processes
     * the collision. Returning true means the event must skip that impact.
     */
    public boolean tryDeflectProjectile(Projectile projectile) {
        if (
                !(level() instanceof ServerLevel serverLevel)
                        || projectile.isRemoved()
                        || !(projectile instanceof AbstractArrow)
                        || projectile.getOwner() == this
                        || projectile.getPersistentData().getBoolean(
                                REFLECTED_PROJECTILE_TAG
                        )
        ) {
            return false;
        }

        long rangedLevel = getAdaptationLevel(AdaptationType.RANGED);
        double reflectionChance = scaledChance(
                rangedLevel,
                PROJECTILE_REFLECTION_BASE_CHANCE,
                PROJECTILE_REFLECTION_CHANCE_PER_LEVEL,
                PROJECTILE_REFLECTION_MAX_CHANCE
        );

        if (
                reflectionChance <= 0.0D
                        || getRandom().nextDouble() >= reflectionChance
        ) {
            return false;
        }

        Vec3 incomingMovement = projectile.getDeltaMovement();
        Vec3 reflected = incomingMovement.scale(-0.4D).add(
                (getRandom().nextDouble() - 0.5D) * 0.2D,
                0.1D,
                (getRandom().nextDouble() - 0.5D) * 0.2D
        );
        projectile.getPersistentData().putBoolean(REFLECTED_PROJECTILE_TAG, true);
        projectile.setDeltaMovement(reflected);
        serverLevel.getChunkSource().broadcast(
                projectile, new ClientboundSetEntityMotionPacket(projectile)
        );
        Vec3 impactPosition = projectile.position();
        serverLevel.playSound(null, impactPosition.x, impactPosition.y, impactPosition.z,
                SoundEvents.SHIELD_BLOCK, SoundSource.HOSTILE, 1.0F, 1.0F);
        playBoneDeflectEffects(serverLevel, impactPosition);
        return true;
    }

    public long getRangedAdaptationLevel() {
        return getAdaptationLevel(AdaptationType.RANGED);
    }

    private void tryAcidSplash(
            ServerLevel serverLevel,
            ServerPlayer player
    ) {
        long meleeLevel = getAdaptationLevel(AdaptationType.MELEE);
        double acidChance = scaledChance(
                meleeLevel,
                ACID_BASE_CHANCE,
                ACID_CHANCE_PER_LEVEL,
                ACID_MAX_CHANCE
        );

        if (
                acidChance <= 0.0D
                        || getRandom().nextDouble() >= acidChance
        ) {
            return;
        }

        int armorDamageBonus = (int) Math.min(
                ACID_MAX_ARMOR_DAMAGE - ACID_BASE_ARMOR_DAMAGE,
                meleeLevel / ACID_LEVELS_PER_ARMOR_DAMAGE
        );
        int armorDamage = ACID_BASE_ARMOR_DAMAGE + armorDamageBonus;

        for (EquipmentSlot slot : EquipmentSlot.values()) {
            if (!slot.isArmor()) {
                continue;
            }

            ItemStack armorStack = player.getItemBySlot(slot);

            if (!armorStack.isEmpty() && armorStack.isDamageableItem()) {
                armorStack.hurtAndBreak(
                        armorDamage,
                        player,
                        wearer -> wearer.broadcastBreakEvent(slot)
                );
            }
        }

        int duration = ACID_BASE_DURATION_TICKS + (int) Math.min(
                ACID_MAX_DURATION_TICKS - ACID_BASE_DURATION_TICKS,
                meleeLevel
        );
        AcidAttackSlowdown.apply(
                player,
                duration,
                meleeLevel >= ACID_EMPOWERED_SLOW_LEVEL
        );

        playAcidSplashEffects(serverLevel, player);
    }

    private void trySpikedRetaliation(
            ServerLevel serverLevel,
            LivingEntity attacker
    ) {
        if (!attacker.isAlive() || attacker == this) {
            return;
        }

        long meleeLevel = getAdaptationLevel(AdaptationType.MELEE);
        double thornChance = scaledChance(
                meleeLevel,
                THORN_BASE_CHANCE,
                THORN_CHANCE_PER_LEVEL,
                THORN_MAX_CHANCE
        );

        if (
                thornChance <= 0.0D
                        || getRandom().nextDouble() >= thornChance
        ) {
            return;
        }

        float thornDamage = (float) Math.min(
                THORN_MAX_DAMAGE,
                THORN_BASE_DAMAGE + meleeLevel * THORN_DAMAGE_PER_LEVEL
        );

        if (attacker.hurt(serverLevel.damageSources().thorns(this), thornDamage)) {
            serverLevel.sendParticles(
                    ParticleTypes.CRIT,
                    attacker.getX(),
                    attacker.getY() + attacker.getBbHeight() * 0.6D,
                    attacker.getZ(),
                    18,
                    0.45D,
                    0.55D,
                    0.45D,
                    0.18D
            );
        }
    }

    private LivingEntity getDirectMeleeAttacker(DamageSource source) {
        if (
                source.is(DamageTypeTags.IS_FIRE)
                        || source.is(DamageTypeTags.IS_PROJECTILE)
                        || source.is(DamageTypeTags.IS_EXPLOSION)
                        || source.is(DamageTypes.THORNS)
                        || !(source.getEntity() instanceof LivingEntity attacker)
                        || source.getDirectEntity() != attacker
        ) {
            return null;
        }

        return attacker;
    }

    private void playBoneDeflectEffects(
            ServerLevel serverLevel,
            Vec3 impactPosition
    ) {
        serverLevel.playSound(
                null,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                ModSounds.BONE_DEFLECT.get(),
                SoundSource.HOSTILE,
                1.0F,
                1.0F
        );

        ItemParticleOption boneParticle = new ItemParticleOption(
                ParticleTypes.ITEM,
                new ItemStack(Items.BONE)
        );
        serverLevel.sendParticles(
                boneParticle,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                24,
                0.55D,
                0.65D,
                0.55D,
                0.16D
        );
        serverLevel.sendParticles(
                ParticleTypes.ELECTRIC_SPARK,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                18,
                0.48D,
                0.52D,
                0.48D,
                0.20D
        );
        serverLevel.sendParticles(
                ParticleTypes.CRIT,
                impactPosition.x,
                impactPosition.y,
                impactPosition.z,
                12,
                0.42D,
                0.48D,
                0.42D,
                0.14D
        );
    }

    private void playAcidSplashEffects(
            ServerLevel serverLevel,
            ServerPlayer player
    ) {
        double effectY = player.getY() + player.getBbHeight() * 0.6D;
        serverLevel.playSound(
                null,
                player.getX(),
                effectY,
                player.getZ(),
                ModSounds.ACID_SPLASH.get(),
                SoundSource.HOSTILE,
                1.0F,
                1.0F
        );
        serverLevel.sendParticles(
                ParticleTypes.ITEM_SLIME,
                player.getX(),
                effectY,
                player.getZ(),
                32,
                0.55D,
                0.65D,
                0.55D,
                0.14D
        );
        serverLevel.sendParticles(
                ParticleTypes.SPIT,
                player.getX(),
                effectY,
                player.getZ(),
                20,
                0.5D,
                0.6D,
                0.5D,
                0.12D
        );
        serverLevel.sendParticles(
                ParticleTypes.SPLASH,
                player.getX(),
                effectY,
                player.getZ(),
                16,
                0.6D,
                0.55D,
                0.6D,
                0.10D
        );
    }

    private long getAdaptationLevel(AdaptationType type) {
        if (!(level() instanceof ServerLevel serverLevel)) {
            return 0L;
        }

        return CarnisWorldData.get(serverLevel).getAdaptation(type);
    }

    private static double scaledChance(
            long level,
            double baseChance,
            double chancePerLevel,
            double maximumChance
    ) {
        if (level <= 0L) {
            return 0.0D;
        }

        return Math.min(
                maximumChance,
                baseChance + level * chancePerLevel
        );
    }

    @Override
    public void playAmbientSound() {
        super.playAmbientSound();
        if (!level().isClientSide) triggerAnim("roar_controller", "roar");
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_AMALGAM_BREATH.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource damageSource) {
        return ModSounds.FLESH_AMALGAM_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.FLESH_AMALGAM_DEATH.get();
    }

    @Override
    public void registerControllers(
            AnimatableManager.ControllerRegistrar controllers
    ) {
        controllers.add(
                new AnimationController<>(
                        this,
                        "locomotion_controller",
                        5,
                        state -> state.setAndContinue(
                                state.isMoving()
                                        ? WALK_ANIMATION
                                        : IDLE_ANIMATION
                        )
                ),
                new AnimationController<>(
                        this,
                        "attack_controller",
                        2,
                        state -> {
                            if (swinging) {
                                return state.setAndContinue(ATTACK_ANIMATION);
                            }

                            state.getController().forceAnimationReset();
                            return PlayState.STOP;
                        }
                ),
                new AnimationController<>(this, "roar_controller", 2,
                        state -> PlayState.STOP).triggerableAnim("roar", ROAR_ANIMATION),
                new AnimationController<>(this, "slam_controller", 1,
                        state -> PlayState.STOP).triggerableAnim("slam", SLAM_ANIMATION),
                new AnimationController<>(this, "damage_controller", 0,
                        state -> PlayState.STOP)
                        .triggerableAnim("hurt", HURT_ANIMATION)
                        .triggerableAnim("death", DEATH_ANIMATION)
        );
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }
}
```

## `src/main/java/com/carnis/mod/entity/FleshSpatProjectileEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModItems;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.network.NetworkHooks;

public final class FleshSpatProjectileEntity extends ThrowableItemProjectile {
    public FleshSpatProjectileEntity(EntityType<? extends FleshSpatProjectileEntity> type, Level level) {
        super(type, level);
    }

    public FleshSpatProjectileEntity(Level level, LivingEntity owner) {
        super(ModEntities.FLESH_SPAT.get(), owner, level);
    }

    @Override protected Item getDefaultItem() { return ModItems.FLESH_SPAT.get(); }

    @Override public void tick() {
        super.tick();
        if (level().isClientSide && !isRemoved()) {
            level().addParticle(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), 0, 0.01D, 0);
        }
        if (!level().isClientSide && tickCount > 200) discard();
    }

    @Override protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        if (level().isClientSide || !(result.getEntity() instanceof LivingEntity target)) return;
        if (target.hurt(damageSources().thrown(this, getOwner()), 2.0F)) {
            target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 1));
            if (target instanceof ServerPlayer player) PlayerInfectionApi.addExposure(player, 5.0F);
        }
    }

    @Override protected void onHit(HitResult result) {
        super.onHit(result);
        if (level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), 14, .2, .2, .2, .03);
            discard();
        }
    }

    @Override public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
```

## `src/main/java/com/carnis/mod/entity/HiveEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.init.ModSounds;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/** Common base for living hive monsters; keeps shared sound and critical-wound behavior centralized. */
public abstract class HiveEntity extends Monster implements BiomassValued {
    private static final String CRITICAL_HURT_COOLDOWN = "carnis:hive_critical_hurt_ms";
    private static final long CRITICAL_HURT_COOLDOWN_MS = 120L;

    protected HiveEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    public static net.minecraft.world.entity.ai.attributes.AttributeSupplier.Builder createAttributes() {
        return HiveEntityAttributes.create();
    }

    // Явное значение биомассы. Множители НЕ применяются.
    @Override
    public long getBiomassValue() {
        return 0L;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HIVE_SPAWN_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.HIVE_SPAWN_DEATH.get();
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !level().isClientSide && isAlive() && getMaxHealth() > 0.0F
                && getHealth() / getMaxHealth() < 0.25F) {
            long now = System.currentTimeMillis();
            long last = getPersistentData().getLong(CRITICAL_HURT_COOLDOWN);
            if (now - last >= CRITICAL_HURT_COOLDOWN_MS) {
                getPersistentData().putLong(CRITICAL_HURT_COOLDOWN, now);
                level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_HURT_CRITICAL.get(),
                        SoundSource.HOSTILE, 1.0F, 1.0F);
            }
        }
        return hurt;
    }
}
```

## `src/main/java/com/carnis/mod/entity/HiveEntityAttributes.java`

```java
package com.carnis.mod.entity;

import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;

/**
 * Базовые атрибуты для сущностей улья.
 * Каждая конкретная сущность создаёт СВОЙ createAttributes(),
 * НЕ вызывая этот метод напрямую для registration.
 */
public final class HiveEntityAttributes {
    private HiveEntityAttributes() { }

    public static AttributeSupplier.Builder create() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 20.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.23D)
                .add(Attributes.ATTACK_DAMAGE, 3.0D)
                .add(Attributes.FOLLOW_RANGE, 32.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.05D);
    }
}
```

## `src/main/java/com/carnis/mod/entity/HiveSentinelEntity.java`

```java
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
```

## `src/main/java/com/carnis/mod/entity/HiveSporeCloudEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** Entry exposure is per cloud and player, not a repeated dose every tick. */
public final class HiveSporeCloudEntity extends AreaEffectCloud {
    private final Set<UUID> inside = new HashSet<>();
    public HiveSporeCloudEntity(EntityType<? extends AreaEffectCloud> type, Level level) { super(type, level); }
    @Override public void tick() {
        super.tick();
        if (!(level() instanceof ServerLevel server) || isRemoved() || tickCount % 5 != 0) return;
        Set<UUID> current = new HashSet<>();
        double radius = getRadius();
        for (ServerPlayer player : server.getEntitiesOfClass(ServerPlayer.class, getBoundingBox(),
                p -> p.isAlive() && !p.isSpectator() && !p.isCreative())) {
            double dx = player.getX() - getX(), dz = player.getZ() - getZ();
            if (dx * dx + dz * dz > radius * radius) continue;
            current.add(player.getUUID());
            if (!inside.contains(player.getUUID())) PlayerInfectionApi.addInfection(player, 20F);
        }
        inside.retainAll(current);
        inside.addAll(current);
    }
}
```

## `src/main/java/com/carnis/mod/entity/HivemindLinkedMob.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;

/** Shared server-side swarm contract for entities that are also vanilla mobs. */
public interface HivemindLinkedMob {
    default void alertTarget(LivingEntity target) {
        if (this instanceof Mob mob) HiveSwarmCoordinator.alertTarget(mob, target);
    }
    default void triggerFrenzy(int durationTicks) {
        if (this instanceof Mob mob) HiveSwarmCoordinator.triggerFrenzy(mob, durationTicks);
    }
    default boolean isFrenzied() {
        return this instanceof Mob mob && HiveSwarmCoordinator.isFrenzied(mob);
    }
}
```

## `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.init.ModSounds;
import net.minecraft.Util;
import net.minecraft.core.BlockPos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.SwellGoal;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

import java.util.Comparator;
import java.util.EnumSet;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedCreeperEntity extends Creeper
        implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final long BIOMASS_VALUE = 8L;
    private static final int SCALE_DIVISOR = 28;
    private static final int FUSE_LENGTH = 30;
    private static final long CRAWL_SOUND_COOLDOWN_MS = 3_000L;

    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedCreeperEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> SAC_CHARGING =
            SynchedEntityData.defineId(InfectedCreeperEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> CRAWLING =
            SynchedEntityData.defineId(InfectedCreeperEntity.class, EntityDataSerializers.BOOLEAN);

    private static final RawAnimation IDLE = RawAnimation.begin()
            .thenLoop("animation.infected_creeper.idle");
    private static final RawAnimation WALK = RawAnimation.begin()
            .thenLoop("animation.infected_creeper.walk");
    private static final RawAnimation FUSE = RawAnimation.begin()
            .thenLoop("animation.infected_creeper.fuse");
    private static final RawAnimation CRAWL = RawAnimation.begin()
            .thenLoop("animation.infected_creeper.crawl");
    private static final RawAnimation ASSIMILATE = RawAnimation.begin()
            .thenLoop("animation.infected_creeper.assimilate");
    private static final RawAnimation SAC_CHARGE = RawAnimation.begin()
            .thenPlay("animation.infected_creeper.sac_charge");
    private static final RawAnimation DETONATE = RawAnimation.begin()
            .thenPlay("animation.infected_creeper.detonate");
    private static final RawAnimation HURT = RawAnimation.begin()
            .thenPlay("animation.infected_creeper.hurt");
    private static final RawAnimation DEATH = RawAnimation.begin()
            .thenPlay("animation.infected_creeper.death");

    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private boolean detonateWarningPlayed;
    private Pose poseBeforeCrawl = Pose.STANDING;
    private long lastCrawlSoundMs = -CRAWL_SOUND_COOLDOWN_MS;

    public InfectedCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
        entityData.define(SAC_CHARGING, false);
        entityData.define(CRAWLING, false);
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    @Override
    public boolean isAssimilating() {
        return entityData.get(ASSIMILATING);
    }

    @Override
    public void setAssimilating(boolean assimilating) {
        entityData.set(ASSIMILATING, assimilating);
    }

    public boolean isSacCharging() {
        return entityData.get(SAC_CHARGING);
    }

    public boolean isCrawling() {
        return entityData.get(CRAWLING);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(
                new AnimationController<>(this, "movement", 2, state -> {
                    if (isSacCharging()) return state.setAndContinue(FUSE);
                    if (isCrawling()) return state.setAndContinue(CRAWL);
                    if (isAssimilating()) return state.setAndContinue(ASSIMILATE);
                    return state.setAndContinue(state.isMoving() ? WALK : IDLE);
                }),
                new AnimationController<>(this, "action", 0, state -> PlayState.STOP)
                        .triggerableAnim("sac_charge", SAC_CHARGE)
                        .triggerableAnim("detonate", DETONATE)
                        .triggerableAnim("hurt", HURT)
                        .triggerableAnim("death", DEATH)
        );
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        goalSelector.removeAllGoals(goal -> goal instanceof SwellGoal);
        goalSelector.addGoal(2, new PlayerOnlySwellGoal(this));
        moveRandomLookGoalToPriority(7);
        goalSelector.addGoal(8, new CarnisFeedingGoal(this));
        goalSelector.addGoal(9, new CarnisGestationGoal(this));
        targetSelector.removeAllGoals(goal -> goal instanceof net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal<?>);
        targetSelector.addGoal(1, new NearestLivePlayerTargetGoal(this));
        targetSelector.addGoal(3, new CarnisHuntPreyGoal(this));
    }


    private static final class NearestLivePlayerTargetGoal extends Goal {
        private final InfectedCreeperEntity creeper;
        private Player candidate;

        private NearestLivePlayerTargetGoal(InfectedCreeperEntity creeper) {
            this.creeper = creeper;
            setFlags(EnumSet.of(Flag.TARGET));
        }

        @Override
        public boolean canUse() {
            double range = creeper.getAttributeValue(Attributes.FOLLOW_RANGE);
            AABB searchArea = creeper.getBoundingBox().inflate(range);
            candidate = creeper.level().getEntitiesOfClass(Player.class, searchArea,
                            player -> HiveSwarmCoordinator.validTarget(creeper, player))
                    .stream()
                    .filter(player -> creeper.distanceToSqr(player) <= range * range
                            && creeper.hasLineOfSight(player))
                    .min(Comparator.comparingDouble(player -> creeper.distanceToSqr(player)))
                    .orElse(null);
            return candidate != null;
        }

        @Override
        public boolean canContinueToUse() {
            return candidate != null && HiveSwarmCoordinator.validTarget(creeper, candidate)
                    && creeper.distanceToSqr(candidate)
                    <= creeper.getAttributeValue(Attributes.FOLLOW_RANGE)
                    * creeper.getAttributeValue(Attributes.FOLLOW_RANGE);
        }

        @Override
        public void start() {
            if (candidate != null) creeper.setTarget(candidate);
        }

        @Override
        public void stop() {
            if (creeper.getTarget() == candidate) creeper.setTarget(null);
            candidate = null;
        }
    }

    private void moveRandomLookGoalToPriority(int priority) {
        for (var wrappedGoal : goalSelector.getAvailableGoals()) {
            if (wrappedGoal.getGoal() instanceof net.minecraft.world.entity.ai.goal.RandomLookAroundGoal) {
                goalSelector.removeGoal(wrappedGoal.getGoal());
                goalSelector.addGoal(priority,
                        new net.minecraft.world.entity.ai.goal.RandomLookAroundGoal(this));
                return;
            }
        }
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Creeper.createAttributes().add(Attributes.MAX_HEALTH, 24.0D);
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (target instanceof HivemindLinkedMob || com.carnis.mod.event.NeuroArmorEventHandler.isHiveEntity(target)) {
            return false;
        }
        return super.canAttack(target);
    }

    @Override
    public void setTarget(LivingEntity target) {
        if (target != null && !HiveSwarmCoordinator.validTarget(this, target)) return;
        super.setTarget(target);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) return;

        updateCrawlState();
        boolean charging = getSwellDir() > 0 || isIgnited();
        boolean wasCharging = entityData.get(SAC_CHARGING);
        if (charging != wasCharging) {
            entityData.set(SAC_CHARGING, charging);
            if (charging) {
                level().playSound(null, getX(), getY(), getZ(), ModSounds.HIVE_SPAWN_CREEPER_SAC.get(),
                        SoundSource.HOSTILE, 1.0F, 1.0F);
                triggerAnimation("sac_charge");
            } else {
                detonateWarningPlayed = false;
            }
        }

        if (charging && getFuse() == 5 && !detonateWarningPlayed) {
            detonateWarningPlayed = true;
            level().playSound(null, getX(), getY(), getZ(), ModSounds.HIVE_SPAWN_CREEPER_DETONATE.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
            triggerAnimation("detonate");
        }
    }

    private void updateCrawlState() {
        LivingEntity target = getTarget();
        boolean shouldCrawl = target != null && target.isAlive()
                && distanceToSqr(target) <= 100.0D && !hasLineOfSight(target);
        boolean wasCrawling = entityData.get(CRAWLING);
        if (shouldCrawl == wasCrawling) return;

        entityData.set(CRAWLING, shouldCrawl);
        if (shouldCrawl) {
            poseBeforeCrawl = getPose();
            setPose(Pose.SWIMMING);
            playCrawlSound();
        } else if (getPose() == Pose.SWIMMING) {
            setPose(poseBeforeCrawl);
        }
    }

    private int getFuse() {
        int elapsedScaleTicks = Math.round(getSwelling(1.0F) * SCALE_DIVISOR);
        return Math.max(0, FUSE_LENGTH - elapsedScaleTicks);
    }

    private static final class PlayerOnlySwellGoal extends SwellGoal {
        private final InfectedCreeperEntity creeper;

        private PlayerOnlySwellGoal(InfectedCreeperEntity creeper) {
            super(creeper);
            this.creeper = creeper;
        }

        @Override
        public boolean canUse() {
            return super.canUse() && HiveSwarmCoordinator.validTarget(creeper, creeper.getTarget())
                    && creeper.getTarget() instanceof Player;
        }

        @Override
        public boolean canContinueToUse() {
            return super.canContinueToUse() && HiveSwarmCoordinator.validTarget(creeper, creeper.getTarget())
                    && creeper.getTarget() instanceof Player;
        }
    }

    private void triggerAnimation(String animation) {
        if (!level().isClientSide) triggerAnim("action", animation);
    }

    private void playCrawlSound() {
        long now = Util.getMillis();
        long elapsed = now - lastCrawlSoundMs;
        if (elapsed < 0L) return;
        if (elapsed >= 0L && elapsed < CRAWL_SOUND_COOLDOWN_MS) return;
        lastCrawlSoundMs = now;
        level().playSound(null, getX(), getY(), getZ(), ModSounds.HIVE_SPAWN_CREEPER_CRAWL.get(),
                SoundSource.HOSTILE, 1.0F, 1.0F);
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        if (isCrawling()) playCrawlSound();
        else super.playStepSound(pos, state);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_SPAWN_IDLE.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HIVE_SPAWN_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.HIVE_SPAWN_DEATH.get();
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean damaged = super.hurt(source, amount);
        if (damaged && isAlive() && !level().isClientSide) triggerAnimation("hurt");
        return damaged;
    }

    @Override
    public void die(DamageSource source) {
        if (!level().isClientSide) triggerAnimation("death");
        super.die(source);
    }
}
```

## `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.HiveDefendHeartGoal;
import com.carnis.mod.entity.ai.HiveEscortLeaderGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedSkeletonEntity extends HiveEntity implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final long BIOMASS_VALUE = 5L;
    private static final int WHIP_ANIMATION_TICKS = 9;
    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedSkeletonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> WHIP_ANIM_TICKS =
            SynchedEntityData.defineId(InfectedSkeletonEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> BONE_RATTLE_ACTIVE =
            SynchedEntityData.defineId(InfectedSkeletonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_skeleton.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_skeleton.walk");
    private static final RawAnimation ASSIMILATE = RawAnimation.begin().thenLoop("animation.infected_skeleton.assimilate");
    private static final RawAnimation BONE_RATTLE = RawAnimation.begin().thenLoop("animation.infected_skeleton.bone_rattle");
    private static final RawAnimation BLADE_ATTACK = RawAnimation.begin().thenPlay("animation.infected_skeleton.attack_scythe");
    private static final RawAnimation WHIP_ATTACK = RawAnimation.begin().thenPlay("animation.infected_skeleton.attack_whip");
    private static final RawAnimation HURT = RawAnimation.begin().thenPlay("animation.infected_skeleton.hurt");
    private static final RawAnimation DEATH = RawAnimation.begin().thenPlay("animation.infected_skeleton.death");
    private static final int BONE_RATTLE_DURATION_TICKS = 40;
    private int idleTicks;
    private int boneRattleTicks;
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedSkeletonEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
        entityData.define(WHIP_ANIM_TICKS, 0);
        entityData.define(BONE_RATTLE_ACTIVE, false);
    }

    @Override
    public boolean isAssimilating() {
        return entityData.get(ASSIMILATING);
    }

    @Override
    public void setAssimilating(boolean assimilating) {
        boolean changed = entityData.get(ASSIMILATING) != assimilating;
        entityData.set(ASSIMILATING, assimilating);
        if (changed && assimilating && !level().isClientSide) {
            triggerAnim("movement", "assimilate");
        }
    }

    public boolean isWhipping() {
        return entityData.get(WHIP_ANIM_TICKS) > 0;
    }

    public void beginWhipAnimation() {
        entityData.set(WHIP_ANIM_TICKS, WHIP_ANIMATION_TICKS);
    }

    private void cancelWhipAnimation() {
        entityData.set(WHIP_ANIM_TICKS, 0);
    }

    private boolean isBoneRattleActive() {
        return entityData.get(BONE_RATTLE_ACTIVE);
    }

    private void tickIdleBoneRattle() {
        boolean idle = getTarget() == null && !isAssimilating() && !swinging && !isWhipping()
                && getDeltaMovement().horizontalDistanceSqr() < 0.0025D;
        if (!idle) {
            idleTicks = 0;
            boneRattleTicks = 0;
            entityData.set(BONE_RATTLE_ACTIVE, false);
            return;
        }

        if (boneRattleTicks > 0) {
            boneRattleTicks--;
            if (boneRattleTicks == 0) entityData.set(BONE_RATTLE_ACTIVE, false);
            return;
        }

        idleTicks++;
        if (idleTicks > 200 && tickCount % 20 == 0 && random.nextFloat() < 0.05F) {
            boneRattleTicks = BONE_RATTLE_DURATION_TICKS;
            idleTicks = 0;
            entityData.set(BONE_RATTLE_ACTIVE, true);
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_SKELETON_BONECRACK.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
    }

    @Override
    public void tick() {
        if (!level().isClientSide) {
            int whipAnimTicks = entityData.get(WHIP_ANIM_TICKS);
            if (whipAnimTicks > 0) entityData.set(WHIP_ANIM_TICKS, whipAnimTicks - 1);
            tickIdleBoneRattle();
        }
        super.tick();
    }

    @Override
    public boolean hurt(net.minecraft.world.damagesource.DamageSource source, float amount) {
        boolean damaged = super.hurt(source, amount);
        if (damaged && isAlive() && !level().isClientSide) triggerAnim("action", "hurt");
        return damaged;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HIVE_SPAWN_HURT.get();
    }

    @Override
    public void die(net.minecraft.world.damagesource.DamageSource source) {
        if (!level().isClientSide) {
            cancelWhipAnimation();
            entityData.set(BONE_RATTLE_ACTIVE, false);
            triggerAnim("action", "death");
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_DEATH.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
        super.die(source);
    }

    @Override
    protected SoundEvent getDeathSound() {
        // die() emits the explicit death sound once, alongside the GeckoLib death animation.
        return null;
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 25.0D)
                .add(Attributes.ATTACK_DAMAGE, 3.5D)
                .add(Attributes.MOVEMENT_SPEED, 0.27D)
                .add(Attributes.FOLLOW_RANGE, 20.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.2D)
                .add(Attributes.ARMOR, 1.0D);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 2, state -> {
            if (isAssimilating()) return state.setAndContinue(ASSIMILATE);
            return state.setAndContinue(isBoneRattleActive() ? BONE_RATTLE : state.isMoving() ? WALK : IDLE);
        }).triggerableAnim("assimilate", ASSIMILATE));
        controllers.add(new AnimationController<>(this, "action", 0, state -> {
            if (isWhipping()) return state.setAndContinue(WHIP_ATTACK);
            if (!isAssimilating() && swinging) return state.setAndContinue(BLADE_ATTACK);
            state.getController().forceAnimationReset();
            return PlayState.STOP;
        }).triggerableAnim("hurt", HURT).triggerableAnim("death", DEATH));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new InfectedSkeletonAttackGoal(this, 1.15D));
        goalSelector.addGoal(2, new MoveTowardsRestrictionGoal(this, 0.9D));
        goalSelector.addGoal(3, new WaterAvoidingRandomStrollGoal(this, 0.9D));
        goalSelector.addGoal(4, new LookAtPlayerGoal(this, Player.class, 10.0F));
        goalSelector.addGoal(5, new RandomLookAroundGoal(this));
        goalSelector.addGoal(6, new HiveDefendHeartGoal(this));
        goalSelector.addGoal(7, new HiveEscortLeaderGoal(this));
        goalSelector.addGoal(8, new CarnisFeedingGoal(this));
        goalSelector.addGoal(9, new CarnisGestationGoal(this));

        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                target -> HiveSwarmCoordinator.validTarget(this, target)));
        targetSelector.addGoal(2, new HurtByTargetGoal(this));
    }

    /** Immediate-hit checks are separate from target eligibility so out-of-range targets can be pursued. */
    private boolean canAttackNow(LivingEntity target) {
        if (!HiveSwarmCoordinator.validTarget(this, target)) return false;
        Vec3 offset = target.position().subtract(position());
        Vec3 horizontal = new Vec3(offset.x, 0.0D, offset.z);
        if (offset.lengthSqr() > 9.0D || !hasLineOfSight(target)) return false;
        if (horizontal.lengthSqr() < 1.0E-8D) return true;

        Vec3 look = getLookAngle();
        Vec3 forward = new Vec3(look.x, 0.0D, look.z);
        if (forward.lengthSqr() < 1.0E-8D) {
            double yaw = Math.toRadians(getYRot());
            forward = new Vec3(-Math.sin(yaw), 0.0D, Math.cos(yaw));
        } else {
            forward = forward.normalize();
        }
        return forward.dot(horizontal.normalize()) >= -0.15D;
    }

    @Override
    public void setTarget(LivingEntity target) {
        if (target != null && !HiveSwarmCoordinator.validTarget(this, target)) return;
        super.setTarget(target);
    }

    @Override
    public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
        if (!(target instanceof LivingEntity livingTarget) || !canAttackNow(livingTarget)) return false;
        boolean hit = super.doHurtTarget(target);
        if (hit && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_SKELETON_BLADE.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
        return hit;
    }

    /** Resolve the wide 3-block lash; damage is lower than the close-range blade strike. */
    public void performWhipAttack() {
        if (!(level() instanceof ServerLevel server)) return;
        Vec3 look = getLookAngle();
        Vec3 forward = new Vec3(look.x, 0.0D, look.z);
        if (forward.lengthSqr() < 1.0E-8D) {
            double yaw = Math.toRadians(getYRot());
            forward = new Vec3(-Math.sin(yaw), 0.0D, Math.cos(yaw));
        } else {
            forward = forward.normalize();
        }

        AABB reach = getBoundingBox().inflate(3.0D, 1.0D, 3.0D);
        for (LivingEntity target : server.getEntitiesOfClass(LivingEntity.class, reach,
                candidate -> candidate != this && HiveSwarmCoordinator.validTarget(this, candidate))) {
            Vec3 offset = target.position().subtract(position());
            Vec3 horizontal = new Vec3(offset.x, 0.0D, offset.z);
            if (offset.lengthSqr() > 9.0D || horizontal.lengthSqr() < 1.0E-8D
                    || forward.dot(horizontal.normalize()) < -0.15D || !hasLineOfSight(target)) continue;
            if (target.hurt(server.damageSources().mobAttack(this), 2.5F)) {
                target.knockback(0.3D, getX() - target.getX(), getZ() - target.getZ());
            }
        }
        server.sendParticles(ParticleTypes.SWEEP_ATTACK, getX() + forward.x, getY(0.5D),
                getZ() + forward.z, 1, 0.0D, 0.0D, 0.0D, 0.0D);
        server.playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_SKELETON_WHIP.get(),
                SoundSource.HOSTILE, 1.0F, 1.0F);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_SPAWN_SKELETON_BONECRACK.get();
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        level().playSound(null, pos, ModSounds.FLESH_BLOCK_STEP.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
    }

    /** One melee goal handles both close blade strikes and the mid-range whip. */
    private static final class InfectedSkeletonAttackGoal extends MeleeAttackGoal {
        private static final int WHIP_IMPACT_TICK = 4;
        private static final int WHIP_COOLDOWN_TICKS = 30;
        private final InfectedSkeletonEntity skeleton;
        private LivingEntity whipTarget;
        private int whipWindup;
        private int nextWhipTick;

        private InfectedSkeletonAttackGoal(InfectedSkeletonEntity skeleton, double speed) {
            super(skeleton, speed, false);
            this.skeleton = skeleton;
        }

        @Override
        public void stop() {
            super.stop();
            whipTarget = null;
            whipWindup = 0;
            skeleton.cancelWhipAnimation();
        }

        @Override
        protected void checkAndPerformAttack(LivingEntity target, double distanceToTargetSqr) {
            // A direct target assigned by HurtByTargetGoal may bypass target-selection predicates.
            // Do not clear it: movement/navigation may still bring a valid target into range.
            if (!skeleton.canAttackNow(target)) return;
            boolean inWhipBand = distanceToTargetSqr >= 2.25D && distanceToTargetSqr <= 9.0D;
            if (whipTarget != null) {
                if (target != whipTarget || !inWhipBand || !skeleton.canAttackNow(target)) {
                    whipTarget = null;
                    whipWindup = 0;
                } else if (--whipWindup <= 0) {
                    skeleton.performWhipAttack();
                    nextWhipTick = skeleton.tickCount + WHIP_COOLDOWN_TICKS;
                    whipTarget = null;
                }
                return;
            }
            if (inWhipBand) {
                if (skeleton.tickCount >= nextWhipTick && skeleton.canAttackNow(target)) {
                    whipTarget = target;
                    whipWindup = WHIP_IMPACT_TICK;
                    skeleton.beginWhipAnimation();
                }
                return;
            }
            if (distanceToTargetSqr < 2.25D) super.checkAndPerformAttack(target, distanceToTargetSqr);
        }
    }
}
```

## `src/main/java/com/carnis/mod/entity/InfectedSpiderEntity.java`

```java
package com.carnis.mod.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Spider;
import net.minecraft.world.level.Level;

public final class InfectedSpiderEntity extends Spider implements HivemindLinkedMob, AssimilatingMob, software.bernie.geckolib.animatable.GeoEntity {
    private static final net.minecraft.network.syncher.EntityDataAccessor<Boolean> ASSIMILATING =
            net.minecraft.network.syncher.SynchedEntityData.defineId(InfectedSpiderEntity.class,
                    net.minecraft.network.syncher.EntityDataSerializers.BOOLEAN);

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
    }

    @Override
    public long getBiomassValue() { return 5L; }

    @Override
    public boolean isAssimilating() { return entityData.get(ASSIMILATING); }

    @Override
    public void setAssimilating(boolean assimilating) { entityData.set(ASSIMILATING, assimilating); }

    private final software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache geoCache =
            software.bernie.geckolib.util.GeckoLibUtil.createInstanceCache(this);

    @Override
    public void registerControllers(software.bernie.geckolib.core.animation.AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this, "movement", 3,
                state -> state.setAndContinue(software.bernie.geckolib.core.animation.RawAnimation.begin()
                        .thenLoop("animation.infected_spider." + (isAssimilating() ? "assimilate" : state.isMoving() ? "walk" : "idle")))));
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this, "action", 1, state -> {
            if (!isAssimilating() && swinging) return state.setAndContinue(software.bernie.geckolib.core.animation.RawAnimation.begin()
                    .thenPlay("animation.infected_spider.attack"));
            state.getController().forceAnimationReset();
            return software.bernie.geckolib.core.object.PlayState.STOP;
        }));
    }

    @Override
    public software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    public InfectedSpiderEntity(EntityType<? extends Spider> type, Level level) {
        super(type, level);
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        moveRandomLookGoalToPriority(7);
        goalSelector.addGoal(8, new com.carnis.mod.entity.ai.CarnisFeedingGoal(this));
        goalSelector.addGoal(9, new com.carnis.mod.entity.ai.CarnisGestationGoal(this));
        goalSelector.addGoal(10, new com.carnis.mod.entity.ai.InfectedSpiderRangedSpatGoal(this));
        targetSelector.addGoal(4, new com.carnis.mod.entity.ai.CarnisHuntPreyGoal(this));
    }

    private void moveRandomLookGoalToPriority(int priority) {
        for (var wrappedGoal : goalSelector.getAvailableGoals()) {
            if (wrappedGoal.getGoal() instanceof net.minecraft.world.entity.ai.goal.RandomLookAroundGoal) {
                goalSelector.removeGoal(wrappedGoal.getGoal());
                goalSelector.addGoal(priority, new net.minecraft.world.entity.ai.goal.RandomLookAroundGoal(this));
                return;
            }
        }
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Spider.createAttributes().add(Attributes.MAX_HEALTH, 20.0D)
                .add(Attributes.ATTACK_DAMAGE, 3.0D);
    }
}
```

## `src/main/java/com/carnis/mod/entity/InfectedZombieEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.entity.ai.CarnisFeedingGoal;
import com.carnis.mod.entity.ai.CarnisGestationGoal;
import com.carnis.mod.entity.ai.CarnisHuntPreyGoal;
import com.carnis.mod.entity.ai.HiveDefendHeartGoal;
import com.carnis.mod.entity.ai.HiveEscortLeaderGoal;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class InfectedZombieEntity extends HiveEntity implements HivemindLinkedMob, AssimilatingMob, GeoEntity {
    private static final long BIOMASS_VALUE = 3L;
    private static final EntityDataAccessor<Boolean> ASSIMILATING =
            SynchedEntityData.defineId(InfectedZombieEntity.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.infected_zombie.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.infected_zombie.walk");
    private static final RawAnimation ASSIMILATE = RawAnimation.begin().thenLoop("animation.infected_zombie.assimilate");
    private static final RawAnimation PULSE = RawAnimation.begin().thenLoop("animation.infected_zombie.pulsing");
    private static final RawAnimation ATTACK = RawAnimation.begin().thenPlay("animation.infected_zombie.attack");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfectedZombieEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ASSIMILATING, false);
    }

    @Override
    public boolean isAssimilating() {
        return entityData.get(ASSIMILATING);
    }

    @Override
    public void setAssimilating(boolean assimilating) {
        entityData.set(ASSIMILATING, assimilating);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 3, state -> {
            if (isAssimilating()) return state.setAndContinue(ASSIMILATE);
            return state.setAndContinue(state.isMoving() ? WALK : IDLE);
        }));
        controllers.add(new AnimationController<>(this, "pulsing", 0, state -> {
            if (isAssimilating()) return PlayState.STOP;
            return state.setAndContinue(PULSE);
        }));
        controllers.add(new AnimationController<>(this, "action", 1, state -> {
            if (!isAssimilating() && swinging) return state.setAndContinue(ATTACK);
            state.getController().forceAnimationReset();
            return PlayState.STOP;
        }));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new HiveDefendHeartGoal(this));
        goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.0D, false));
        goalSelector.addGoal(2, new CarnisFeedingGoal(this));
        goalSelector.addGoal(3, new CarnisGestationGoal(this));
        goalSelector.addGoal(4, new RandomStrollGoal(this, 0.8D));
        goalSelector.addGoal(5, new HiveEscortLeaderGoal(this));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0F));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                target -> HiveSwarmCoordinator.validTarget(this, target)));
        targetSelector.addGoal(2, new HurtByTargetGoal(this));
        targetSelector.addGoal(3, new CarnisHuntPreyGoal(this));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 35.0D)
                .add(Attributes.ATTACK_DAMAGE, 4.5D)
                .add(Attributes.MOVEMENT_SPEED, 0.25D)
                .add(Attributes.FOLLOW_RANGE, 16.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.3D)
                .add(Attributes.ARMOR, 2.0D);
    }

    @Override
    public long getBiomassValue() {
        return BIOMASS_VALUE;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HIVE_SPAWN_IDLE.get();
    }

    @Override
    public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
        if (!(target instanceof LivingEntity livingTarget)
                || !HiveSwarmCoordinator.validTarget(this, livingTarget)) return false;
        boolean success = super.doHurtTarget(target);
        if (success && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_ATTACK.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
        return success;
    }

    @Override
    public void setTarget(LivingEntity target) {
        if (target != null && !HiveSwarmCoordinator.validTarget(this, target)) return;
        boolean wasUntargeted = getTarget() == null;
        super.setTarget(target);
        if (wasUntargeted && target != null && !level().isClientSide) {
            level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_ALERT.get(),
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
    }
}
```

## `src/main/java/com/carnis/mod/entity/ParasiticTendrilEntity.java`

```java
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
```

## `src/main/java/com/carnis/mod/entity/PurificationDartEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.protocol.Packet;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.network.NetworkHooks;
import net.minecraftforge.registries.ForgeRegistries;

public final class PurificationDartEntity extends AbstractArrow {
    public PurificationDartEntity(EntityType<? extends PurificationDartEntity> type, Level level) {
        super(type, level);
        pickup = Pickup.DISALLOWED;
    }

    public PurificationDartEntity(Level level, LivingEntity owner) {
        super(ModEntities.PURIFICATION_DART.get(), owner, level);
        pickup = Pickup.DISALLOWED;
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        if (level().isClientSide) {
            return;
        }
        Entity hit = result.getEntity();
        if (hit instanceof ServerPlayer player) {
            PlayerInfectionApi.addInfection(player, -35.0F);
        } else if (hit instanceof LivingEntity living && isCarnis(living)) {
            living.hurt(ModDamageTypes.purificationDart(level(), this, getOwner()), 25.0F);
        }
        discard();
    }

    private static boolean isCarnis(LivingEntity target) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(target.getType());
        return target instanceof HivemindLinkedMob || id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }

    @Override
    protected SoundEvent getDefaultHitGroundSoundEvent() {
        return ModSounds.DART_HIT.get();
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        setSoundEvent(ModSounds.DART_HIT.get());
        super.onHitBlock(result);
    }

    @Override
    protected ItemStack getPickupItem() {
        return ItemStack.EMPTY;
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
```

## `src/main/java/com/carnis/mod/entity/PustuleGrenadeEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.init.ModItems;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraftforge.network.NetworkHooks;

public final class PustuleGrenadeEntity extends ThrowableItemProjectile {
    public PustuleGrenadeEntity(EntityType<? extends PustuleGrenadeEntity> type, Level level) {
        super(type, level);
    }

    public PustuleGrenadeEntity(Level level, LivingEntity owner) {
        super(ModEntities.PUSTULE_GRENADE.get(), owner, level);
    }

    @Override
    protected Item getDefaultItem() {
        return ModItems.PUSTULE_GRENADE.get();
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        if (!level().isClientSide) {
            if (result.getEntity() instanceof LivingEntity target) {
                target.addEffect(new MobEffectInstance(MobEffects.POISON, 60, 3), getOwner());
            }
            burst();
        }
        discard();
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        super.onHitBlock(result);
        if (!level().isClientSide) burst();
        discard();
    }

    private void burst() {
        level().playSound(null, getX(), getY(), getZ(), ModSounds.PUSTULE_GRENADE_IMPACT.get(),
                SoundSource.PLAYERS, 1.0F, 1.0F);
        if (level() instanceof ServerLevel server) {
            server.sendParticles(ModParticles.BIOMASS_SPARK.get(), getX(), getY(), getZ(),
                    20, 0.4D, 0.35D, 0.4D, 0.08D);
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
```

## `src/main/java/com/carnis/mod/entity/ViralDartEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.protocol.Packet;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.network.NetworkHooks;

public final class ViralDartEntity extends AbstractArrow {
    public ViralDartEntity(EntityType<? extends ViralDartEntity> type, Level level) {
        super(type, level);
        pickup = Pickup.DISALLOWED;
    }

    public ViralDartEntity(Level level, LivingEntity owner) {
        super(ModEntities.VIRAL_DART.get(), owner, level);
        pickup = Pickup.DISALLOWED;
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        if (level().isClientSide) {
            return;
        }
        Entity hit = result.getEntity();
        if (hit instanceof ServerPlayer player) {
            if (!(getOwner() instanceof Player attacker) || attacker.canHarmPlayer(player)) {
                PlayerInfectionApi.addExposure(player, 30.0F);
            }
        } else if (hit instanceof LivingEntity living) {
            living.addEffect(new MobEffectInstance(MobEffects.POISON, 200, 1));
            living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 200, 0));
        }
        discard();
    }

    @Override
    protected SoundEvent getDefaultHitGroundSoundEvent() {
        return ModSounds.DART_HIT.get();
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        setSoundEvent(ModSounds.DART_HIT.get());
        super.onHitBlock(result);
    }

    @Override
    protected ItemStack getPickupItem() {
        return ItemStack.EMPTY;
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/AmalgamBiomassFeast.java`

```java
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
```

## `src/main/java/com/carnis/mod/entity/ai/CarnisFeedingGoal.java`

```java
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
```

## `src/main/java/com/carnis/mod/entity/ai/CarnisGestationGoal.java`

```java
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
```

## `src/main/java/com/carnis/mod/entity/ai/CarnisHuntPreyGoal.java`

```java
package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.HivemindLinkedMob;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.registries.ForgeRegistries;

/** Vanilla mobs are prey; players and allied Carnis are handled by other goals. */
public final class CarnisHuntPreyGoal extends NearestAttackableTargetGoal<LivingEntity> {
    public CarnisHuntPreyGoal(Mob hunter) {
        super(hunter, LivingEntity.class, 20, true, false,
                target -> isPrey(target) && hunter.distanceToSqr(target) <= 256.0D
                        && hunter.hasLineOfSight(target) && HiveSwarmCoordinator.validTarget(hunter, target));
    }
    public static boolean isPrey(LivingEntity target) {
        if (!(target instanceof Mob) || target instanceof HivemindLinkedMob || target instanceof Player) return false;
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(target.getType());
        return id != null && "minecraft".equals(id.getNamespace());
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/FleshAmalgamAbilityGoal.java`

```java
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
```

## `src/main/java/com/carnis/mod/entity/ai/FleshAmalgamChargeGoal.java`

```java
package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * RANGED adaptation countermeasure: when its target keeps distance, the
 * Amalgam abandons ordinary pathing for one bounded ballistic charge.
 */
public final class FleshAmalgamChargeGoal extends Goal {
    private static final double TRIGGER_DISTANCE_SQUARED =
            FleshAmalgamEntity.CHARGE_TRIGGER_DISTANCE
                    * FleshAmalgamEntity.CHARGE_TRIGGER_DISTANCE;
    private static final double MIN_HORIZONTAL_VECTOR_SQUARED = 1.0E-6D;

    private static final double BASE_HORIZONTAL_SPEED = 1.15D;
    private static final double SPEED_PER_ADAPTATION_LEVEL = 0.008D;
    private static final double MAX_HORIZONTAL_SPEED = 1.55D;
    private static final double VERTICAL_SPEED = 0.52D;

    private static final int BASE_COOLDOWN_TICKS = 90;
    private static final int MIN_COOLDOWN_TICKS = 35;
    private static final int MAX_AIRBORNE_TICKS = 20;

    private final FleshAmalgamEntity amalgam;

    private LivingEntity target;
    private long nextAllowedChargeTick;
    private int airborneTicks;

    public FleshAmalgamChargeGoal(FleshAmalgamEntity amalgam) {
        this.amalgam = amalgam;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (
                amalgam.level().getGameTime() < nextAllowedChargeTick
                        || !amalgam.onGround()
                        || amalgam.getRangedAdaptationLevel() <= 0L
        ) {
            return false;
        }

        LivingEntity currentTarget = amalgam.getTarget();

        if (
                !HiveSwarmCoordinator.validTarget(amalgam, currentTarget)
        ) {
            return false;
        }

        double offsetX = currentTarget.getX() - amalgam.getX();
        double offsetZ = currentTarget.getZ() - amalgam.getZ();
        double horizontalDistanceSquared = offsetX * offsetX
                + offsetZ * offsetZ;

        if (
                amalgam.distanceToSqr(currentTarget)
                        <= TRIGGER_DISTANCE_SQUARED
                        || horizontalDistanceSquared
                        < MIN_HORIZONTAL_VECTOR_SQUARED
        ) {
            return false;
        }

        target = currentTarget;
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        return HiveSwarmCoordinator.validTarget(amalgam, target)
                && airborneTicks < MAX_AIRBORNE_TICKS
                && (!amalgam.onGround() || airborneTicks == 0);
    }

    @Override
    public void start() {
        if (target == null) {
            return;
        }

        Vec3 horizontalDirection = new Vec3(
                target.getX() - amalgam.getX(),
                0.0D,
                target.getZ() - amalgam.getZ()
        );

        if (
                horizontalDirection.lengthSqr()
                        < MIN_HORIZONTAL_VECTOR_SQUARED
        ) {
            target = null;
            return;
        }

        long rangedLevel = amalgam.getRangedAdaptationLevel();
        double horizontalSpeed = Math.min(
                MAX_HORIZONTAL_SPEED,
                BASE_HORIZONTAL_SPEED
                        + rangedLevel * SPEED_PER_ADAPTATION_LEVEL
        );
        int cooldownReduction = (int) Math.min(
                BASE_COOLDOWN_TICKS - MIN_COOLDOWN_TICKS,
                rangedLevel
        );

        horizontalDirection = horizontalDirection.normalize();
        amalgam.getNavigation().stop();
        amalgam.getLookControl().setLookAt(target, 30.0F, 30.0F);
        amalgam.setDeltaMovement(
                horizontalDirection.x * horizontalSpeed,
                Math.max(
                        VERTICAL_SPEED,
                        amalgam.getDeltaMovement().y
                ),
                horizontalDirection.z * horizontalSpeed
        );
        amalgam.setSprinting(true);

        nextAllowedChargeTick = amalgam.level().getGameTime()
                + BASE_COOLDOWN_TICKS
                - cooldownReduction;
        airborneTicks = 0;
    }

    @Override
    public void tick() {
        airborneTicks++;

        if (HiveSwarmCoordinator.validTarget(amalgam, target)) {
            amalgam.getLookControl().setLookAt(target, 30.0F, 30.0F);
        }
    }

    @Override
    public void stop() {
        amalgam.setSprinting(false);
        target = null;
        airborneTicks = 0;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/GoalPriorityUtil.java`

```java
package com.carnis.mod.entity.ai;

import java.util.HashSet;
import java.util.Set;
import net.minecraft.world.entity.ai.goal.GoalSelector;
import net.minecraft.world.entity.ai.goal.WrappedGoal;

/** Assigns the first unused selector priority when goals are registered dynamically. */
public final class GoalPriorityUtil {
    private GoalPriorityUtil() { }

    public static int firstUnused(GoalSelector selector) {
        Set<Integer> used = new HashSet<>();
        for (WrappedGoal goal : selector.getAvailableGoals()) used.add(goal.getPriority());
        int priority = 0;
        while (used.contains(priority)) priority++;
        return priority;
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/HiveDefendHeartGoal.java`

```java
package com.carnis.mod.entity.ai;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import java.util.EnumSet;

/** A defense order is pushed by an attack event, not discovered by scanning blocks. */
public final class HiveDefendHeartGoal extends Goal {
    private final Mob mob;
    private BlockPos destination;
    private int repath;
    public HiveDefendHeartGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }
    @Override public boolean canUse() {
        if (!(mob.level() instanceof ServerLevel level) || !mob.isAlive()) return false;
        destination = HiveSwarmCoordinator.defensePosition(mob);
        if (destination == null) { HiveSwarmCoordinator.clearDefense(mob); return false; }
        // Once near the threatened location, hand control back to normal combat.
        return level.hasChunkAt(destination) && farFromDefense() && !enemyClose();
    }
    @Override public boolean canContinueToUse() {
        BlockPos current = HiveSwarmCoordinator.defensePosition(mob);
        return mob.isAlive() && mob.level() instanceof ServerLevel level && destination != null
                && current != null && current.equals(destination) && level.hasChunkAt(destination)
                && farFromDefense() && !enemyClose();
    }
    private boolean farFromDefense() {
        return destination != null && mob.distanceToSqr(destination.getX() + .5D, destination.getY() + .5D, destination.getZ() + .5D) > 36.0D;
    }
    private boolean enemyClose() {
        var target = mob.getTarget();
        return target != null && target.isAlive() && target.level() == mob.level()
                && mob.distanceToSqr(target) <= 36.0D;
    }
    @Override public void start() { repath = 0; }
    @Override public void stop() { mob.getNavigation().stop(); destination = null; }
    @Override public void tick() {
        if (destination == null || !(mob.level() instanceof ServerLevel level)
                || !mob.isAlive() || !level.hasChunkAt(destination)) {
            stop();
            return;
        }
        BlockPos current = HiveSwarmCoordinator.defensePosition(mob);
        if (current == null || !current.equals(destination)) {
            stop();
            return;
        }
        if (--repath <= 0) {
            repath = 20;
            // A removed heart is still a useful rally point. No chunk is loaded by this goal.
            if (level.hasChunkAt(destination))
                mob.getNavigation().moveTo(destination.getX() + .5D, destination.getY(), destination.getZ() + .5D, 1.15D);
        }
        var target = mob.getTarget();
        if (target != null && target.isAlive() && target.level() == level)
            mob.getLookControl().setLookAt(target, 30.0F, 30.0F);
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/HiveEscortLeaderGoal.java`

```java
package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HiveSentinelEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;
import java.util.Comparator;
import java.util.EnumSet;

/** Follows a loaded leader without replacing any active combat target. */
public final class HiveEscortLeaderGoal extends Goal {
    private static final double SEARCH_RADIUS = 24.0D;
    private static final double INNER = 6.0D;
    private static final double OUTER = 14.0D;
    private final Mob mob;
    private Mob leader;
    private int nextSearch;
    private int repath;
    public HiveEscortLeaderGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }
    private boolean available() {
        return mob.isAlive() && mob.getTarget() == null
                && !mob.getPersistentData().contains(CarnisFeedingGoal.DEADLINE)
                && HiveSwarmCoordinator.defensePosition(mob) == null;
    }
    private static boolean isLeader(Mob candidate) {
        return candidate instanceof HiveSentinelEntity || candidate instanceof CerebralNexusEntity
                || candidate instanceof FleshAmalgamEntity;
    }
    @Override public boolean canUse() {
        if (!(mob.level() instanceof ServerLevel level) || !available() || mob.tickCount < nextSearch) return false;
        nextSearch = mob.tickCount + 40;
        leader = level.getEntitiesOfClass(Mob.class, mob.getBoundingBox().inflate(SEARCH_RADIUS),
                candidate -> candidate != mob && candidate.isAlive() && isLeader(candidate)
                        && mob.distanceToSqr(candidate) <= SEARCH_RADIUS * SEARCH_RADIUS)
                .stream().min(Comparator.comparingDouble(mob::distanceToSqr)).orElse(null);
        return leader != null;
    }
    @Override public boolean canContinueToUse() {
        return available() && leader != null && leader.isAlive() && !leader.isRemoved()
                && leader.level() == mob.level() && mob.level().isLoaded(leader.blockPosition())
                && mob.distanceToSqr(leader) <= SEARCH_RADIUS * SEARCH_RADIUS;
    }
    @Override public void start() { repath = 0; }
    @Override public void stop() { mob.getNavigation().stop(); leader = null; }
    @Override public void tick() {
        if (!canContinueToUse()) {
            stop();
            return;
        }
        if (--repath > 0) return;
        repath = 20;
        double distance = mob.distanceToSqr(leader);
        mob.getLookControl().setLookAt(leader, 30.0F, 30.0F);
        if (distance > OUTER * OUTER) {
            mob.getNavigation().moveTo(leader, 1.0D);
        } else if (distance < INNER * INNER) {
            Vec3 away = mob.position().subtract(leader.position()).multiply(1, 0, 1);
            if (away.lengthSqr() < 0.01D) away = new Vec3(1, 0, 0);
            Vec3 destination = leader.position().add(away.normalize().scale(9.0D));
            mob.getNavigation().moveTo(destination.x, destination.y, destination.z, 0.9D);
        } else {
            mob.getNavigation().stop();
        }
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/HiveSwarmCoordinator.java`

```java
package com.carnis.mod.entity.ai;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.AssimilatingMob;
import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.UUID;

/** Server-authoritative coordination. Broadcasts never recursively relay themselves. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HiveSwarmCoordinator {
    public static final String DEFENSE_POS = "carnis:swarm_defense_pos";
    public static final String DEFENSE_UNTIL = "carnis:swarm_defense_until";
    public static final String DEFENSE_DIM = "carnis:swarm_defense_dim";
    private static final String FRENZY_UNTIL = "carnis:frenzy_until";
    private static final String FRENZY_DIM = "carnis:frenzy_dim";
    private static final String LAST_ALARM_POS = "carnis:last_hive_alarm_pos";
    private static final String LAST_ALARM_TICK = "carnis:last_hive_alarm_tick";
    private static final String LAST_ALARM_DIM = "carnis:last_hive_alarm_dim";
    private static final UUID SPEED_ID = UUID.fromString("322fcbde-4022-41f2-ae54-5f416537a4db");
    private static final AttributeModifier SPEED = new AttributeModifier(SPEED_ID, "Carnis swarm frenzy", 0.20D,
            AttributeModifier.Operation.MULTIPLY_TOTAL);
    private static final ThreadLocal<Boolean> BROADCASTING = ThreadLocal.withInitial(() -> false);
    private HiveSwarmCoordinator() { }

    private static String dimension(ServerLevel level) { return level.dimension().location().toString(); }
    public static boolean validTarget(Mob mob, LivingEntity target) {
        return mob != null && target != null && target != mob && target.isAlive()
                && target.level() == mob.level() && !target.isSpectator()
                && (!(target instanceof Player player) || !player.isCreative())
                && !(target instanceof HivemindLinkedMob)
                && !NeuroArmorEventHandler.isHiveEntity(target)
                && mob.canAttack(target);
    }

    public static void alertTarget(Mob mob, LivingEntity target) {
        if (!(mob.level() instanceof ServerLevel) || !mob.isAlive() || !validTarget(mob, target)) return;
        if (mob.getTarget() == target) return;
        // Interrupt feeding so it cannot clear the alarm target on its next tick.
        mob.getPersistentData().remove(CarnisFeedingGoal.DEADLINE);
        mob.getPersistentData().remove("carnis:feeding_travel");
        if (mob instanceof AssimilatingMob assimilating) assimilating.setAssimilating(false);
        mob.setTarget(target);
    }
    public static void triggerFrenzy(Mob mob, int durationTicks) {
        if (!(mob.level() instanceof ServerLevel level) || !mob.isAlive() || durationTicks <= 0
                || com.carnis.mod.event.DartTreatmentEvents.isStunned(mob)) return;
        CompoundTag tag = mob.getPersistentData();
        long until = level.getGameTime() + (long) durationTicks;
        if (dimension(level).equals(tag.getString(FRENZY_DIM))) until = Math.max(until, tag.getLong(FRENZY_UNTIL));
        tag.putLong(FRENZY_UNTIL, until);
        tag.putString(FRENZY_DIM, dimension(level));
        updateSpeed(mob, true);
    }
    public static void clearFrenzy(Mob mob) {
        mob.getPersistentData().remove(FRENZY_UNTIL);
        mob.getPersistentData().remove(FRENZY_DIM);
        updateSpeed(mob, false);
    }
    public static boolean isFrenzied(Mob mob) {
        if (!(mob.level() instanceof ServerLevel level)) return false;
        CompoundTag tag = mob.getPersistentData();
        return dimension(level).equals(tag.getString(FRENZY_DIM)) && tag.getLong(FRENZY_UNTIL) > level.getGameTime();
    }
    private static void updateSpeed(Mob mob, boolean active) {
        AttributeInstance speed = mob.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed == null) return;
        boolean present = speed.getModifier(SPEED_ID) != null;
        if (active && !present) speed.addTransientModifier(SPEED);
        else if (!active && present) speed.removeModifier(SPEED_ID);
    }
    @SubscribeEvent
    public static void onLivingTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || !(mob instanceof HivemindLinkedMob)
                || !(mob.level() instanceof ServerLevel level)) return;
        boolean active = mob.isAlive() && isFrenzied(mob);
        updateSpeed(mob, active);
        if (!active) {
            mob.getPersistentData().remove(FRENZY_UNTIL);
            mob.getPersistentData().remove(FRENZY_DIM);
        } else if (mob.tickCount % 10 == 0) {
            level.sendParticles(ModParticles.BIOMASS_SPARK.get(), mob.getX(), mob.getY(0.55D), mob.getZ(),
                    3, mob.getBbWidth() * .35D, mob.getBbHeight() * .3D, mob.getBbWidth() * .35D, .01D);
        }
        if (mob.getTarget() != null && !validTarget(mob, mob.getTarget())) mob.setTarget(null);
    }
    private static void issueDefense(Mob mob, ServerLevel level, BlockPos pos) {
        CompoundTag tag = mob.getPersistentData();
        tag.putLong(DEFENSE_POS, pos.asLong());
        tag.putLong(DEFENSE_UNTIL, level.getGameTime() + 400L);
        tag.putString(DEFENSE_DIM, dimension(level));
    }
    public static BlockPos defensePosition(Mob mob) {
        if (!(mob.level() instanceof ServerLevel level)) return null;
        CompoundTag tag = mob.getPersistentData();
        if (!tag.contains(DEFENSE_POS) || !dimension(level).equals(tag.getString(DEFENSE_DIM))
                || tag.getLong(DEFENSE_UNTIL) <= level.getGameTime()) return null;
        return BlockPos.of(tag.getLong(DEFENSE_POS));
    }
    public static void clearDefense(Mob mob) {
        mob.getPersistentData().remove(DEFENSE_POS);
        mob.getPersistentData().remove(DEFENSE_UNTIL);
        mob.getPersistentData().remove(DEFENSE_DIM);
    }
    private static void broadcast(ServerLevel level, Vec3 center, double radius, LivingEntity target,
                                  boolean onlyFree, boolean frenzy, BlockPos defense) {
        if (BROADCASTING.get()) return;
        BROADCASTING.set(true);
        try {
            AABB area = AABB.ofSize(center, radius * 2, radius * 2, radius * 2);
            for (Mob mob : level.getEntitiesOfClass(Mob.class, area,
                    m -> m instanceof HivemindLinkedMob && m.isAlive()
                            && m.position().distanceToSqr(center) <= radius * radius)) {
                HivemindLinkedMob linked = (HivemindLinkedMob) mob;
                if (frenzy) linked.triggerFrenzy(400);
                if (defense != null) issueDefense(mob, level, defense);
                boolean occupied = mob.getTarget() != null && mob.getTarget().isAlive()
                        || mob.getPersistentData().contains(CarnisFeedingGoal.DEADLINE);
                if (!onlyFree || !occupied) linked.alertTarget(target);
            }
        } finally { BROADCASTING.remove(); }
    }
    public static void eyeAlarm(ServerLevel level, BlockPos eye, LivingEntity intruder) {
        broadcast(level, Vec3.atCenterOf(eye), 28.0D, intruder, true, false, null);
    }
    private static void defend(ServerLevel level, Vec3 center, BlockPos pos, LivingEntity intruder, boolean frenzy) {
        broadcast(level, center, 36.0D, intruder, false, frenzy, pos);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onHurt(LivingHurtEvent event) {
        if (event.isCanceled() || event.getAmount() <= 0 || !(event.getEntity().level() instanceof ServerLevel level)) return;
        Entity source = event.getSource().getEntity();
        if (event.getEntity() instanceof CerebralNexusEntity nexus && source instanceof LivingEntity attacker
                && validTarget(nexus, attacker)) {
            defend(level, nexus.position(), nexus.blockPosition(), attacker, false);
            return;
        }
        if (event.getEntity() instanceof Mob victim && victim instanceof HivemindLinkedMob
                && source instanceof LivingEntity attacker && validTarget(victim, attacker)) {
            broadcast(level, victim.position(), 20.0D, attacker, false, false, null);
        } else if (source instanceof Mob attacker && attacker instanceof HivemindLinkedMob
                && validTarget(attacker, event.getEntity())) {
            broadcast(level, attacker.position(), 20.0D, event.getEntity(), false, false, null);
        }
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onTargetChange(LivingChangeTargetEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof Mob mob)
                || !(mob instanceof HivemindLinkedMob) || !(mob.level() instanceof ServerLevel level)) return;
        LivingEntity candidate = event.getNewTarget();
        if (candidate != null && !validTarget(mob, candidate)) {
            event.setCanceled(true);
            return;
        }
        if (BROADCASTING.get() || candidate == null) return;
        broadcast(level, mob.position(), 20.0D, candidate, false, false, null);
    }
    private static boolean keyOrgan(BlockState state) {
        return state.is(ModBlocks.PULSING_HEART.get()) || state.is(ModBlocks.HIVE_EYE.get())
                || state.is(ModBlocks.STOMACH_POOL.get()) || state.is(ModBlocks.NERVE_PILLAR.get());
    }
    private static void organAttacked(ServerLevel level, BlockPos pos, Player player) {
        if (!player.isAlive() || player.isSpectator() || player.isCreative()) return;
        CompoundTag tag = player.getPersistentData();
        long now = level.getGameTime();
        boolean duplicate = tag.contains(LAST_ALARM_TICK) && tag.getLong(LAST_ALARM_POS) == pos.asLong()
                && dimension(level).equals(tag.getString(LAST_ALARM_DIM))
                && now >= tag.getLong(LAST_ALARM_TICK) && now - tag.getLong(LAST_ALARM_TICK) < 8;
        NeuroArmorEventHandler.provoke(player);
        if (duplicate) return;
        tag.putLong(LAST_ALARM_POS, pos.asLong());
        tag.putLong(LAST_ALARM_TICK, now);
        tag.putString(LAST_ALARM_DIM, dimension(level));
        BlockPos rally = level.getBlockState(pos).is(ModBlocks.PULSING_HEART.get()) ? pos : null;
        defend(level, Vec3.atCenterOf(pos), rally, player, true);
        level.playSound(null, pos, ModSounds.PHANTOM_WHISPER.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onStartBreaking(PlayerInteractEvent.LeftClickBlock event) {
        if (event.isCanceled() || event.getAction() != PlayerInteractEvent.LeftClickBlock.Action.START
                || !(event.getLevel() instanceof ServerLevel level) || !keyOrgan(level.getBlockState(event.getPos()))) return;
        organAttacked(level, event.getPos(), event.getEntity());
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onBreak(BlockEvent.BreakEvent event) {
        if (event.isCanceled() || !(event.getLevel() instanceof ServerLevel level) || !keyOrgan(event.getState())) return;
        organAttacked(level, event.getPos(), event.getPlayer());
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/InfectedSpiderRangedSpatGoal.java`

```java
package com.carnis.mod.entity.ai;

import com.carnis.mod.entity.FleshSpatProjectileEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import java.util.EnumSet;

public final class InfectedSpiderRangedSpatGoal extends Goal {
    private final InfectedSpiderEntity spider;
    private long nextShot;

    public InfectedSpiderRangedSpatGoal(InfectedSpiderEntity spider) {
        this.spider = spider;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override public boolean canUse() {
        LivingEntity target = spider.getTarget();
        if (!HiveSwarmCoordinator.validTarget(spider, target) || !spider.hasLineOfSight(target)) return false;
        double distance = spider.distanceToSqr(target);
        return distance >= 16.0D && distance <= 144.0D;
    }

    @Override public boolean canContinueToUse() { return canUse(); }
    @Override public boolean requiresUpdateEveryTick() { return true; }

    @Override public void tick() {
        LivingEntity target = spider.getTarget();
        if (!HiveSwarmCoordinator.validTarget(spider, target)) return;
        spider.getNavigation().stop();
        spider.getLookControl().setLookAt(target, 30.0F, 30.0F);
        long now = spider.level().getGameTime();
        if (now < nextShot) return;
        FleshSpatProjectileEntity spat = new FleshSpatProjectileEntity(spider.level(), spider);
        double x = target.getX() - spat.getX();
        double z = target.getZ() - spat.getZ();
        double y = target.getY(0.45D) - spat.getY() + Math.sqrt(x * x + z * z) * 0.05D;
        spat.shoot(x, y, z, 1.2F, 1.0F);
        if (spider.level().addFreshEntity(spat)) nextShot = now + 60L;
    }
}
```

## `src/main/java/com/carnis/mod/entity/ai/StomachPoolAttractGoal.java`

```java
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
```

## `src/main/java/com/carnis/mod/entity/projectile/InoculatorDartEntity.java`

```java
package com.carnis.mod.entity.projectile;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HiveSentinelEntity;
import com.carnis.mod.entity.CerebralNexusEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.event.DartTreatmentEvents;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.event.IncubationEvents;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.network.NetworkHooks;

public final class InoculatorDartEntity extends AbstractArrow {
    public enum DartType { PURIFICATION, VIRAL }
    private static final EntityDataAccessor<Integer> CONTENT = SynchedEntityData.defineId(InoculatorDartEntity.class, EntityDataSerializers.INT);
    public InoculatorDartEntity(EntityType<? extends InoculatorDartEntity> type, Level level) {
        super(type, level); pickup = Pickup.DISALLOWED;
    }
    public InoculatorDartEntity(Level level, LivingEntity owner, DartType contents) {
        super(ModEntities.INOCULATOR_DART.get(), owner, level);
        pickup = Pickup.DISALLOWED;
        setDartType(contents);
    }
    @Override protected void defineSynchedData() { super.defineSynchedData(); entityData.define(CONTENT, 0); }
    public DartType getDartType() { return entityData.get(CONTENT) == 1 ? DartType.VIRAL : DartType.PURIFICATION; }
    public void setDartType(DartType type) { entityData.set(CONTENT, type == DartType.VIRAL ? 1 : 0); }
    @Override public void addAdditionalSaveData(CompoundTag tag) { super.addAdditionalSaveData(tag); tag.putString("DartType", getDartType().name()); }
    @Override public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        setDartType("VIRAL".equals(tag.getString("DartType")) ? DartType.VIRAL : DartType.PURIFICATION);
    }
    @Override public void tick() {
        super.tick();
        if (isRemoved() || inGround || isNoGravity()) return;
        // AbstractArrow applies 0.05 blocks/tick². Counter 0.04 after its normal flight tick.
        setDeltaMovement(getDeltaMovement().add(0, .04D, 0));
        if (level().isClientSide) {
            boolean clean = getDartType() == DartType.PURIFICATION;
            level().addParticle(clean ? ModParticles.PURIFIER_FLAME.get() : ModParticles.BIOMASS_SPARK.get(),
                    getX(), getY(), getZ(), 0, 0, 0);
            if (tickCount % 3 == 0) level().addParticle(clean ? ParticleTypes.COMPOSTER : ParticleTypes.CRIMSON_SPORE,
                    getX(), getY(), getZ(), 0, .005D, 0);
        }
    }
    @Override protected void onHitEntity(EntityHitResult result) {
        if (!(level() instanceof ServerLevel server)) return;
        Entity hit = result.getEntity();
        if (hit instanceof LivingEntity living) {
            if (getDartType() == DartType.PURIFICATION) purify(server, living);
            else infect(server, living);
        }
        discard();
    }
    private void purify(ServerLevel level, LivingEntity target) {
        if (target instanceof Player player) {
            PlayerInfectionApi.addInfection(player, -35F);
            player.removeEffect(MobEffects.CONFUSION);
            player.removeEffect(MobEffects.BLINDNESS);
            player.removeEffect(MobEffects.MOVEMENT_SLOWDOWN);
        } else if (target instanceof InfectedZombieEntity || target instanceof InfectedSkeletonEntity) {
            DartTreatmentEvents.startRegression((Mob) target);
        } else if (target instanceof FleshAmalgamEntity || target instanceof HiveSentinelEntity || target instanceof CerebralNexusEntity) {
            target.hurt(level.damageSources().magic(), 25F);
            if (target.isAlive()) DartTreatmentEvents.stun((Mob) target, 60);
        }
    }
    private void infect(ServerLevel level, LivingEntity target) {
        if (target instanceof Player player) {
            if (getOwner() instanceof Player shooter && !shooter.canHarmPlayer(player)) return;
            PlayerInfectionApi.addInfection(player, 25F);
            player.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 120, 0));
            return;
        }
        if (!IncubationEvents.isEligible(target)) return;
        EntityType<?> type = target.getType();
        if (type == EntityType.ZOMBIE || type == EntityType.SKELETON || type == EntityType.CREEPER
                || type == EntityType.SPIDER || type == EntityType.CAVE_SPIDER) {
            DartTreatmentEvents.startMutation((Mob) target);
        } else {
            InfectionHandler.beginAccelerated(target);
        }
    }
    @Override protected void onHitBlock(BlockHitResult hit) { setSoundEvent(ModSounds.DART_HIT.get()); super.onHitBlock(hit); }
    @Override protected SoundEvent getDefaultHitGroundSoundEvent() { return ModSounds.DART_HIT.get(); }
    @Override protected ItemStack getPickupItem() { return ItemStack.EMPTY; }
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket() { return NetworkHooks.getEntitySpawningPacket(this); }
}
```

## `src/main/java/com/carnis/mod/event/AcidAttackSlowdown.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.UUID;

/**
 * Owns the short-lived attack-speed penalty inflicted by Amalgam acid.
 *
 * <p>The fixed UUID makes repeated splashes refresh one modifier instead of
 * stacking without bound. The modifier itself is transient; its small timing
 * record lets a reconnect restore the remaining duration, while the attribute
 * modifier is still never serialized as a permanent player statistic.</p>
 */
@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class AcidAttackSlowdown {
    private static final UUID MODIFIER_ID = UUID.fromString(
            "998af1a3-cca9-508b-9a0f-df56cb810b54"
    );
    private static final String MODIFIER_NAME =
            "Carnis Amalgam acid attack slowdown";
    private static final String EXPIRY_TAG =
            CarnisMod.MOD_ID + ":acid_attack_slow_until";
    private static final String AMOUNT_TAG =
            CarnisMod.MOD_ID + ":acid_attack_slow_amount";

    private static final double STANDARD_AMOUNT = -0.25D;
    private static final double EMPOWERED_AMOUNT = -0.40D;

    private AcidAttackSlowdown() {
    }

    public static void apply(
            ServerPlayer player,
            int durationTicks,
            boolean empowered
    ) {
        AttributeInstance attackSpeed = player.getAttribute(
                Attributes.ATTACK_SPEED
        );

        if (attackSpeed == null || durationTicks <= 0) {
            return;
        }

        CompoundTag persistentData = player.getPersistentData();
        long expiryTick = Math.max(
                persistentData.getLong(EXPIRY_TAG),
                player.level().getGameTime() + durationTicks
        );
        double amount = empowered
                ? EMPOWERED_AMOUNT
                : STANDARD_AMOUNT;

        if (persistentData.contains(AMOUNT_TAG)) {
            amount = Math.min(
                    amount,
                    sanitizeAmount(persistentData.getDouble(AMOUNT_TAG))
            );
        }

        persistentData.putLong(EXPIRY_TAG, expiryTick);
        persistentData.putDouble(AMOUNT_TAG, amount);
        replaceModifier(attackSpeed, amount);
    }

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (
                event.phase != TickEvent.Phase.END
                        || !(event.player instanceof ServerPlayer player)
        ) {
            return;
        }

        CompoundTag persistentData = player.getPersistentData();

        if (!persistentData.contains(EXPIRY_TAG)) {
            return;
        }

        AttributeInstance attackSpeed = player.getAttribute(
                Attributes.ATTACK_SPEED
        );

        if (player.level().getGameTime() >= persistentData.getLong(EXPIRY_TAG)) {
            if (attackSpeed != null) {
                attackSpeed.removeModifier(MODIFIER_ID);
            }

            persistentData.remove(EXPIRY_TAG);
            persistentData.remove(AMOUNT_TAG);
            return;
        }

        // Transient modifiers are deliberately absent from saved attributes.
        // Recreate this one if the player reconnects before the timer expires.
        if (
                attackSpeed != null
                        && attackSpeed.getModifier(MODIFIER_ID) == null
        ) {
            replaceModifier(
                    attackSpeed,
                    sanitizeAmount(persistentData.getDouble(AMOUNT_TAG))
            );
        }
    }

    private static double sanitizeAmount(double amount) {
        return Math.max(
                EMPOWERED_AMOUNT,
                Math.min(STANDARD_AMOUNT, amount)
        );
    }

    private static void replaceModifier(
            AttributeInstance attackSpeed,
            double amount
    ) {
        attackSpeed.removeModifier(MODIFIER_ID);
        attackSpeed.addTransientModifier(
                new AttributeModifier(
                        MODIFIER_ID,
                        MODIFIER_NAME,
                        amount,
                        AttributeModifier.Operation.MULTIPLY_TOTAL
                )
        );
    }
}
```

## `src/main/java/com/carnis/mod/event/AdaptationEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import com.carnis.mod.world.CarnisWorldData.AdaptationType;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.AbstractArrow;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.event.entity.ProjectileImpactEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class AdaptationEvents {
    private static final String RANGED_COUNTED_TAG =
            CarnisMod.MOD_ID + ":ranged_adaptation_counted";

    private static final int NEARBY_CARNIS_BLOCK_RADIUS = 1;

    private static final double RETALIATION_BASE_CHANCE = 0.05D;
    private static final double RETALIATION_CHANCE_PER_LEVEL = 0.005D;
    private static final double RETALIATION_MAX_CHANCE = 0.45D;
    private static final float RETALIATION_BASE_DAMAGE = 1.0F;
    private static final float RETALIATION_DAMAGE_PER_LEVEL = 0.04F;
    private static final float RETALIATION_MAX_DAMAGE = 4.0F;

    private static final double EXPLOSION_ABSORPTION_BASE_CHANCE = 0.10D;
    private static final double EXPLOSION_ABSORPTION_CHANCE_PER_LEVEL = 0.0075D;
    private static final double EXPLOSION_ABSORPTION_MAX_CHANCE = 0.60D;

    private static final ThreadLocal<Boolean> APPLYING_RETALIATION =
            ThreadLocal.withInitial(() -> false);

    private AdaptationEvents() {
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onLivingHurt(LivingHurtEvent event) {
        if (
                event.isCanceled()
                        || event.getAmount() <= 0.0F
                        || APPLYING_RETALIATION.get()
        ) {
            return;
        }

        LivingEntity target = event.getEntity();

        if (
                !(target.level() instanceof ServerLevel serverLevel)
                        || !isCarnisEntity(target)
        ) {
            return;
        }

        DamageSource source = event.getSource();

        if (source.is(DamageTypes.THORNS)) {
            return;
        }

        CarnisWorldData data = CarnisWorldData.get(serverLevel);
        AdaptationType damageType = source.is(DamageTypeTags.IS_FIRE)
                ? AdaptationType.FIRE
                : source.is(DamageTypeTags.IS_PROJECTILE)
                ? AdaptationType.RANGED
                : source.is(DamageTypeTags.IS_EXPLOSION)
                ? AdaptationType.EXPLOSIVE
                : source.getEntity() instanceof LivingEntity
                && source.getDirectEntity() == source.getEntity()
                ? AdaptationType.MELEE : null;
        if (damageType == null) {
            return;
        }
        float mitigation = CarnisWorldData.damageMitigation(data.getAdaptation(damageType));
        event.setAmount(event.getAmount() * (1.0F - mitigation));

        if (damageType == AdaptationType.MELEE) {
            data.decayAdaptation(AdaptationType.FIRE, 2L);
            data.decayAdaptation(AdaptationType.RANGED, 2L);
        }
        boolean count = damageType != AdaptationType.RANGED
                || (source.getDirectEntity() instanceof AbstractArrow
                    && markProjectileAttackAsCounted(source.getDirectEntity()));
        if (count) {
            data.tryAwardDamageAdaptation(new ChunkPos(target.blockPosition()),
                    damageType, serverLevel.getGameTime());
        }
        if (count || damageType == AdaptationType.MELEE) {
            ModMessages.sendToPlayersInLevel(serverLevel);
        }
        ServerPlayer meleeAttacker = getMeleeAttacker(source);
        if (meleeAttacker == null) {
            return;
        }
        long meleeLevel = data.getAdaptation(AdaptationType.MELEE);

        // Flesh Amalgams own their stronger adaptive thorn response. Keeping
        // the generic retaliation here as well would roll and apply it twice.
        if (!(target instanceof FleshAmalgamEntity)) {
            tryRetaliate(serverLevel, target, meleeAttacker, meleeLevel);
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onProjectileImpact(ProjectileImpactEvent event) {
        Projectile projectile = event.getProjectile();

        if (
                event.isCanceled()
                        || !(projectile.level() instanceof ServerLevel serverLevel)
                        || !(projectile instanceof AbstractArrow)
                        || isIgnoredEntityImpact(event)
                        || !hitsCarnisTarget(
                                serverLevel,
                                event.getRayTraceResult()
                        )
                        || !markProjectileAttackAsCounted(projectile)
        ) {
            return;
        }

        CarnisWorldData data = CarnisWorldData.get(serverLevel);
        BlockPos hitPos = BlockPos.containing(event.getRayTraceResult().getLocation());
        if (data.tryAwardDamageAdaptation(new ChunkPos(hitPos), AdaptationType.RANGED,
                serverLevel.getGameTime())) {
            ModMessages.sendToPlayersInLevel(serverLevel);
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onExplosionDetonate(ExplosionEvent.Detonate event) {
        if (!(event.getLevel() instanceof ServerLevel serverLevel)) {
            return;
        }

        List<BlockPos> affectedBlocks = event.getAffectedBlocks();
        List<Entity> affectedEntities = event.getAffectedEntities();

        boolean threatensCarnis = affectedBlocks.stream().anyMatch(
                pos -> isCarnisBlock(serverLevel.getBlockState(pos))
        ) || affectedEntities.stream().anyMatch(
                AdaptationEvents::isCarnisEntity
        );

        if (!threatensCarnis) {
            return;
        }

        long explosiveLevel = CarnisWorldData.get(serverLevel)
                .getAdaptation(AdaptationType.EXPLOSIVE);
        double absorptionChance = calculateExplosionAbsorptionChance(
                explosiveLevel
        );

        affectedBlocks.removeIf(
                pos -> isCarnisBlock(serverLevel.getBlockState(pos))
                        && serverLevel.getRandom().nextDouble()
                        < absorptionChance
        );
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onBlockPlaced(BlockEvent.EntityPlaceEvent event) {
        if (
                event.isCanceled()
                        || !(event.getLevel() instanceof ServerLevel serverLevel)
                        || !(event.getEntity() instanceof ServerPlayer player)
        ) {
            return;
        }

        BlockPos placedPos = event.getPos();

        if (
                event.getPlacedBlock()
                        .getCollisionShape(serverLevel, placedPos)
                        .isEmpty()
                        || !isPillaring(player, placedPos)
                        || !hasActiveCarnisPresence(serverLevel, placedPos)
        ) {
            return;
        }

        incrementAndSync(serverLevel, AdaptationType.PILLARING);
    }

    private static ServerPlayer getMeleeAttacker(DamageSource source) {
        if (
                source.is(DamageTypeTags.IS_FIRE)
                        || source.is(DamageTypeTags.IS_PROJECTILE)
                        || source.is(DamageTypeTags.IS_EXPLOSION)
                        || !(source.getEntity() instanceof ServerPlayer attacker)
                        || source.getDirectEntity() != attacker
        ) {
            return null;
        }

        return attacker;
    }

    private static void tryRetaliate(
            ServerLevel serverLevel,
            LivingEntity target,
            ServerPlayer attacker,
            long meleeLevel
    ) {
        double chance = Math.min(
                RETALIATION_MAX_CHANCE,
                RETALIATION_BASE_CHANCE
                        + meleeLevel * RETALIATION_CHANCE_PER_LEVEL
        );

        if (serverLevel.getRandom().nextDouble() >= chance) {
            return;
        }

        float damage = Math.min(
                RETALIATION_MAX_DAMAGE,
                RETALIATION_BASE_DAMAGE
                        + meleeLevel * RETALIATION_DAMAGE_PER_LEVEL
        );

        APPLYING_RETALIATION.set(true);

        try {
            attacker.hurt(
                    serverLevel.damageSources().thorns(target),
                    damage
            );
        } finally {
            APPLYING_RETALIATION.remove();
        }
    }

    private static boolean isIgnoredEntityImpact(
            ProjectileImpactEvent event
    ) {
        return event.getImpactResult()
                == ProjectileImpactEvent.ImpactResult.SKIP_ENTITY
                || event.getImpactResult()
                == ProjectileImpactEvent.ImpactResult.STOP_AT_CURRENT_NO_DAMAGE;
    }

    private static boolean hitsCarnisTarget(
            ServerLevel serverLevel,
            HitResult hitResult
    ) {
        if (hitResult instanceof EntityHitResult entityHitResult) {
            return entityHitResult.getEntity() instanceof LivingEntity living
                    && living.isAlive() && isCarnisEntity(living);
        }

        if (hitResult instanceof BlockHitResult blockHitResult) {
            BlockState state = serverLevel.getBlockState(blockHitResult.getBlockPos());
            return state.is(ModBlocks.PULSING_HEART.get()) || state.is(ModBlocks.HIVE_EYE.get())
                    || state.is(ModBlocks.NERVE_PILLAR.get()) || state.is(ModBlocks.STOMACH_POOL.get());
        }

        return false;
    }

    private static boolean markProjectileAttackAsCounted(Entity directEntity) {
        if (!(directEntity instanceof Projectile projectile)) {
            return true;
        }

        if (projectile.getPersistentData().getBoolean(RANGED_COUNTED_TAG)) {
            return false;
        }

        projectile.getPersistentData().putBoolean(RANGED_COUNTED_TAG, true);
        return true;
    }

    private static boolean isPillaring(
            ServerPlayer player,
            BlockPos placedPos
    ) {
        BlockPos blockBelowPlayer = player.blockPosition().below();
        return placedPos.equals(blockBelowPlayer)
                && player.getY() >= placedPos.getY() + 1.0D;
    }

    private static boolean hasActiveCarnisPresence(
            ServerLevel serverLevel,
            BlockPos center
    ) {
        if (CarnisWorldData.get(serverLevel).getBiomassPoints() > 0L) {
            return true;
        }

        BlockPos.MutableBlockPos cursor = new BlockPos.MutableBlockPos();

        for (
                int offsetX = -NEARBY_CARNIS_BLOCK_RADIUS;
                offsetX <= NEARBY_CARNIS_BLOCK_RADIUS;
                offsetX++
        ) {
            for (
                    int offsetY = -NEARBY_CARNIS_BLOCK_RADIUS;
                    offsetY <= NEARBY_CARNIS_BLOCK_RADIUS;
                    offsetY++
            ) {
                int y = center.getY() + offsetY;

                if (
                        y < serverLevel.getMinBuildHeight()
                                || y >= serverLevel.getMaxBuildHeight()
                ) {
                    continue;
                }

                for (
                        int offsetZ = -NEARBY_CARNIS_BLOCK_RADIUS;
                        offsetZ <= NEARBY_CARNIS_BLOCK_RADIUS;
                        offsetZ++
                ) {
                    cursor.set(
                            center.getX() + offsetX,
                            y,
                            center.getZ() + offsetZ
                    );

                    if (
                            serverLevel.hasChunkAt(cursor)
                                    && isCarnisBlock(
                                            serverLevel.getBlockState(cursor)
                                    )
                    ) {
                        return true;
                    }
                }
            }
        }

        return false;
    }

    private static boolean isCarnisEntity(Entity entity) {
        ResourceLocation registryName = ForgeRegistries.ENTITY_TYPES.getKey(
                entity.getType()
        );
        return registryName != null
                && CarnisMod.MOD_ID.equals(registryName.getNamespace());
    }

    private static boolean isCarnisBlock(BlockState state) {
        ResourceLocation registryName = ForgeRegistries.BLOCKS.getKey(
                state.getBlock()
        );
        return registryName != null
                && CarnisMod.MOD_ID.equals(registryName.getNamespace());
    }

    private static double calculateExplosionAbsorptionChance(long level) {
        return Math.min(
                EXPLOSION_ABSORPTION_MAX_CHANCE,
                EXPLOSION_ABSORPTION_BASE_CHANCE
                        + level * EXPLOSION_ABSORPTION_CHANCE_PER_LEVEL
        );
    }

    private static long incrementAndSync(
            ServerLevel serverLevel,
            AdaptationType type
    ) {
        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);
        long previousValue = worldData.getAdaptation(type);
        long updatedValue = worldData.incrementAdaptation(type);

        if (updatedValue != previousValue) {
            ModMessages.sendToPlayersInLevel(serverLevel);
        }

        return updatedValue;
    }
}
```

## `src/main/java/com/carnis/mod/event/AmalgamationHandler.java`

```java
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
```

## `src/main/java/com/carnis/mod/event/BootCorrosionEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.item.NeuroWeave;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class BootCorrosionEvents {
    private BootCorrosionEvents() { }

    @SubscribeEvent
    public static void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)
                || !player.isAlive() || player.isSpectator() || !player.onGround()
                || player.tickCount % 60 != 0 || !player.getBlockStateOn().is(ModBlocks.LIVING_FLESH.get())) return;
        ItemStack boots = player.getItemBySlot(EquipmentSlot.FEET);
        if (!boots.isEmpty() && !NeuroWeave.isWoven(boots) && !(boots.getItem() instanceof com.carnis.mod.item.armor.NeuroArmorItem)) {
            boots.hurtAndBreak(1, player, entity -> entity.broadcastBreakEvent(EquipmentSlot.FEET));
        }
    }
}
```

## `src/main/java/com/carnis/mod/event/CarnisEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.biomass.PlayerBiomassCapability;
import com.carnis.mod.capability.biomass.PlayerBiomassEvents;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.BiomassValued;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.Spider;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.UUID;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisEvents {
    private CarnisEvents() {
    }

    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void protectHiveTissueFromInfectedCreeper(ExplosionEvent.Detonate event) {
        var explosion = event.getExplosion();
        Entity exploder = explosion.getExploder();
        if (exploder == null) exploder = explosion.getIndirectSourceEntity();
        if (!(exploder instanceof InfectedCreeperEntity)) return;
        event.getAffectedBlocks().removeIf(pos -> {
            var state = event.getLevel().getBlockState(pos);
            return state.is(ModBlocks.LIVING_FLESH.get())
                    || state.is(ModBlocks.FLESH_BULB.get())
                    || state.is(ModBlocks.CREEPING_TENDRILS.get())
                    || state.is(ModBlocks.SPORE_SPROUT.get())
                    || state.is(ModBlocks.NEURAL_MOSS.get())
                    || state.is(ModBlocks.PULSING_HEART.get())
                    || state.is(ModBlocks.OSSIFIED_FLESH.get())
                    || state.is(ModBlocks.CHARRED_FLESH.get())
                    || state.is(ModBlocks.FIREPROOF_FLESH.get())
                    || state.is(ModBlocks.FLESH_VEINS.get())
                    || state.is(ModBlocks.STOMACH_POOL.get())
                    || state.is(ModBlocks.NERVE_PILLAR.get())
                    || state.is(ModBlocks.SINEW_SPIKES.get())
                    || state.is(ModBlocks.PUSTULE_CLUSTER.get())
                    || state.is(ModBlocks.HIVE_EYE.get())
                    || state.is(ModBlocks.HIVE_MEMBRANE.get())
                    || state.is(ModBlocks.SYNAPSE_NODE.get())
                    || state.is(ModBlocks.INCUBATION_CYST.get())
                    || state.is(ModBlocks.PURIFIER_LAMP.get());
        });
    }

    @SubscribeEvent(priority = EventPriority.HIGH, receiveCanceled = true)
    public static void onLivingDeath(LivingDeathEvent event) {
        LivingEntity victim = event.getEntity();
        if (!(victim.level() instanceof ServerLevel level)) return;

        Entity killer = event.getSource().getEntity();
        if (event.isCanceled() || victim instanceof Player || killer == null || killer == victim) return;

        if (victim instanceof BiomassValued valuedVictim) {
            if (killer instanceof ServerPlayer player) {
                awardBiomass(player, valuedVictim.getBiomassValue());
            }
            return;
        }

        ServerPlayer recipient = null;
        if (killer instanceof ServerPlayer player) {
            float infection = PlayerInfectionApi.getInfectionLevel(player);
            if (infection <= 0.0F) return;
            recipient = player;
        } else if (killer instanceof HivemindLinkedMob) {
            if (victim instanceof HivemindLinkedMob) return;
            if (killer instanceof TamableAnimal tame && tame.getOwnerUUID() != null) {
                UUID ownerId = tame.getOwnerUUID();
                recipient = level.getServer().getPlayerList().getPlayer(ownerId);
                if (recipient == null) {
                    CarnisMod.LOGGER.warn("Could not award biomass: owner {} is offline", ownerId);
                    return;
                }
            }
        } else {
            return;
        }

        long multiplier = 1L;
        if (victim instanceof Mob mob && DartTreatmentEvents.isMutating(mob)) {
            multiplier *= 3L;
        }
        if (InfectionHandler.isInfected(victim)) {
            multiplier *= 2L;
        }
        long total = basePoints(victim) * multiplier;

        if (recipient != null) {
            awardBiomass(recipient, total);
        } else {
            CarnisWorldData data = CarnisWorldData.get(level);
            data.addBiomassPoints(total);
            ModMessages.sendToPlayersInLevel(level);
        }
    }

    private static void awardBiomass(ServerPlayer player, long amount) {
        if (amount <= 0L) return;
        var biomass = player.getCapability(PlayerBiomassCapability.PLAYER_BIOMASS);
        if (!biomass.isPresent()) {
            CarnisMod.LOGGER.warn("Could not award biomass to {}: capability is absent", player.getUUID());
            return;
        }
        biomass.ifPresent(data -> {
            data.addBiomassPoints(amount);
            PlayerBiomassEvents.syncToPlayer(player);
        });
    }

    private static long basePoints(LivingEntity victim) {
        if (victim instanceof Zombie) return 1L;

        EntityType<?> type = victim.getType();
        if (type == EntityType.ALLAY || type == EntityType.VEX || type == EntityType.WARDEN
                || type == EntityType.ELDER_GUARDIAN || type == EntityType.IRON_GOLEM
                || type == EntityType.SNOW_GOLEM || type == EntityType.TRADER_LLAMA) return 25L;
        if (victim instanceof Creeper || victim instanceof Spider) return 5L;
        if (victim instanceof Animal) return 5L;
        if (victim instanceof Monster) return 15L;
        return 5L;
    }
}
```

## `src/main/java/com/carnis/mod/event/ChunkInfectionEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent.ServerTickEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.level.ChunkEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.WeakHashMap;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ChunkInfectionEvents {
    private static final int MAX_CHUNKS_PER_TICK = 1;
    private static final long CACHE_TTL_TICKS = 20L;

    // Weak level keys, with values that contain only positions (no strong level reference).
    private static final Map<ServerLevel, Map<Long, CachedBlockScan>> BLOCK_SCAN_CACHE = new WeakHashMap<>();
    private static final Map<ServerLevel, Map<Long, CachedEntities>> ENTITY_CACHE = new WeakHashMap<>();
    private static final Map<ServerLevel, LinkedHashSet<ChunkPos>> pendingChunks = new WeakHashMap<>();

    private ChunkInfectionEvents() { }

    private static final class CachedBlockScan {
        private final long expiresAt;
        private final boolean infected;

        private CachedBlockScan(long expiresAt, boolean infected) {
            this.expiresAt = expiresAt;
            this.infected = infected;
        }
    }

    private static final class CachedEntities {
        private final long expiresAt;
        private final boolean hasCarnisEntity;

        private CachedEntities(long expiresAt, boolean hasCarnisEntity) {
            this.expiresAt = expiresAt;
            this.hasCarnisEntity = hasCarnisEntity;
        }
    }

    private record QueuedChunk(ServerLevel level, ChunkPos pos) { }

    private static boolean isCarnisBlock(BlockState state) {
        ResourceLocation id = ForgeRegistries.BLOCKS.getKey(state.getBlock());
        return id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }

    private static AABB chunkBounds(ServerLevel level, ChunkPos pos) {
        return new AABB(pos.getMinBlockX(), level.getMinBuildHeight(), pos.getMinBlockZ(),
                pos.getMinBlockX() + 16, level.getMaxBuildHeight(), pos.getMinBlockZ() + 16);
    }

    private static boolean containsCarnisBlock(ServerLevel level, LevelChunk chunk) {
        long now = level.getGameTime();
        long key = chunk.getPos().toLong();
        synchronized (BLOCK_SCAN_CACHE) {
            Map<Long, CachedBlockScan> levelCache = BLOCK_SCAN_CACHE.computeIfAbsent(level, ignored -> new HashMap<>());
            CachedBlockScan cached = levelCache.get(key);
            if (cached != null && now < cached.expiresAt) return cached.infected;

            boolean found = false;
            for (LevelChunkSection section : chunk.getSections()) {
                if (section == null || section.hasOnlyAir()
                        || !section.maybeHas(ChunkInfectionEvents::isCarnisBlock)) continue;
                // maybeHas can match an unused palette entry, so confirm actual block cells.
                for (int x = 0; x < 16 && !found; x++) {
                    for (int y = 0; y < 16 && !found; y++) {
                        for (int z = 0; z < 16; z++) {
                            if (isCarnisBlock(section.getBlockState(x, y, z))) {
                                found = true;
                                break;
                            }
                        }
                    }
                }
                if (found) break;
            }

            levelCache.entrySet().removeIf(entry -> entry.getValue().expiresAt <= now);
            levelCache.put(key, new CachedBlockScan(now + CACHE_TTL_TICKS, found));
            return found;
        }
    }

    private static boolean hasCarnisEntity(ServerLevel level, ChunkPos pos, AABB box) {
        long now = level.getGameTime();
        long key = pos.toLong();
        synchronized (ENTITY_CACHE) {
            Map<Long, CachedEntities> levelCache = ENTITY_CACHE.computeIfAbsent(level, ignored -> new HashMap<>());
            CachedEntities cached = levelCache.get(key);
            if (cached != null && now < cached.expiresAt) return cached.hasCarnisEntity;

            boolean found = !level.getEntitiesOfClass(LivingEntity.class, box, entity -> {
                ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
                return entity instanceof HivemindLinkedMob
                        || (id != null && CarnisMod.MOD_ID.equals(id.getNamespace()));
            }).isEmpty();

            levelCache.entrySet().removeIf(entry -> entry.getValue().expiresAt <= now);
            levelCache.put(key, new CachedEntities(now + CACHE_TTL_TICKS, found));
            return found;
        }
    }

    private static void queueChunk(ServerLevel level, ChunkPos pos) {
        synchronized (pendingChunks) {
            pendingChunks.computeIfAbsent(level, ignored -> new LinkedHashSet<>())
                    .add(new ChunkPos(pos.x, pos.z));
        }
    }

    @SubscribeEvent
    public static void onChunkLoad(ChunkEvent.Load event) {
        if (!(event.getLevel() instanceof ServerLevel level)) return;
        queueChunk(level, event.getChunk().getPos());
    }

    @SubscribeEvent
    public static void onServerTick(ServerTickEvent event) {
        if (event.phase == net.minecraftforge.event.TickEvent.Phase.END) processPendingChunks();
    }

    /** Prewarm no more than MAX_CHUNKS_PER_TICK queued chunks; direct cache misses remain synchronous. */
    private static void processPendingChunks() {
        for (int processed = 0; processed < MAX_CHUNKS_PER_TICK; processed++) {
            QueuedChunk queued = pollPendingChunk();
            if (queued == null) return;

            ServerLevel level = queued.level();
            ChunkPos pos = queued.pos();
            long startedAt = System.nanoTime();
            LevelChunk chunk = level.getChunkSource().getChunkNow(pos.x, pos.z);
            if (chunk == null) {
                logIfSlow("chunk prewarm lookup", startedAt);
                continue;
            }

            // maybeHas skips empty/non-hive sections before any 4096-cell verification pass.
            hasCarnisEntity(level, pos, chunkBounds(level, pos));
            containsCarnisBlock(level, chunk);
            logIfSlow("chunk prewarm", startedAt);
        }
    }

    private static QueuedChunk pollPendingChunk() {
        synchronized (pendingChunks) {
            var levels = pendingChunks.entrySet().iterator();
            while (levels.hasNext()) {
                Map.Entry<ServerLevel, LinkedHashSet<ChunkPos>> entry = levels.next();
                if (entry.getValue().isEmpty()) {
                    levels.remove();
                    continue;
                }
                ServerLevel level = entry.getKey();
                var positions = entry.getValue().iterator();
                ChunkPos pos = positions.next();
                positions.remove();
                if (entry.getValue().isEmpty()) levels.remove();
                return new QueuedChunk(level, pos);
            }
            return null;
        }
    }

    public static boolean infectedChunk(ServerLevel level, ChunkPos pos) {
        long startedAt = System.nanoTime();
        LevelChunk chunk = level.getChunkSource().getChunkNow(pos.x, pos.z);
        if (chunk == null) {
            logIfSlow("infectedChunk lookup", startedAt);
            return false;
        }
        boolean hasEntity = hasCarnisEntity(level, pos, chunkBounds(level, pos));
        boolean infected = hasEntity || containsCarnisBlock(level, chunk);
        logIfSlow("infectedChunk lookup", startedAt);
        return infected;
    }

    private static void logIfSlow(String operation, long startedAt) {
        long elapsed = System.nanoTime() - startedAt;
        if (elapsed > 1_000_000L) {
            CarnisMod.LOGGER.debug("Slow chunk op: {} took {} ms", operation, elapsed / 1_000_000.0D);
        }
    }

    @SubscribeEvent
    public static void onDetonate(ExplosionEvent.Detonate event) {
        if (!(event.getLevel() instanceof ServerLevel level)) return;
        BlockPos center = BlockPos.containing(event.getExplosion().getPosition());
        ChunkPos chunk = new ChunkPos(center);
        if (!infectedChunk(level, chunk)) return;
        CarnisWorldData data = CarnisWorldData.get(level);
        data.shockChunkFor(chunk, level.getGameTime(), 600L);
        data.addAdaptation(CarnisWorldData.AdaptationType.EXPLOSIVE, 35L);
        ModMessages.sendToPlayersInLevel(level);
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onDeath(LivingDeathEvent event) {
        if (event.isCanceled() || !(event.getEntity().level() instanceof ServerLevel level)) return;
        LivingEntity entity = event.getEntity();
        if (entity.getPersistentData().getBoolean("carnis:pool_dissolving")
                && entity.getPersistentData().getLong("carnis:pool_dissolving_until") >= level.getGameTime()) return;
        BlockPos pos = entity.blockPosition();
        if (!level.getBlockState(pos).is(ModBlocks.STOMACH_POOL.get())
                && !infectedChunk(level, new ChunkPos(pos))) return;
        CarnisWorldData.get(level).addBiomassPoints(entity instanceof Player ? 100L : 20L);
        ModMessages.sendToPlayersInLevel(level);
    }
}
```

## `src/main/java/com/carnis/mod/event/CombatItemEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CombatItemEvents {
    private CombatItemEvents() { }

    @SubscribeEvent
    public static void onScytheAttack(AttackEntityEvent event) {
        Player player = event.getEntity();
        if (player.getMainHandItem().is(ModItems.OSSIFIED_SCYTHE.get())) {
            player.level().playSound(null, player.blockPosition(), ModSounds.OSSIFIED_SCYTHE_SWING.get(),
                    SoundSource.PLAYERS, 1.0F, 1.0F);
        }
    }

    @SubscribeEvent
    public static void onScytheBlockSwing(PlayerInteractEvent.LeftClickBlock event) {
        Player player = event.getEntity();
        if (player.getMainHandItem().is(ModItems.OSSIFIED_SCYTHE.get())) {
            player.level().playSound(null, event.getPos(), ModSounds.OSSIFIED_SCYTHE_SWING.get(),
                    SoundSource.PLAYERS, 1.0F, 1.0F);
        }
    }

    @SubscribeEvent
    public static void onShieldBlock(LivingAttackEvent event) {
        LivingEntity entity = event.getEntity();
        if (!(entity instanceof ServerPlayer player) || !player.isBlocking()
                || !player.getUseItem().is(ModItems.SINEW_SHIELD.get())
                || !player.isDamageSourceBlocked(event.getSource())) return;
        player.level().playSound(null, player.blockPosition(), ModSounds.SINEW_SHIELD_BLOCK.get(),
                SoundSource.PLAYERS, 1.0F, 1.0F);
    }
}
```

## `src/main/java/com/carnis/mod/event/DartTreatmentEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Persistent loaded-tick treatments; no world scans or background threads. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class DartTreatmentEvents {
    private static final String REGRESSION = "carnis:dart_regression_ticks";
    private static final String MUTATION = "carnis:dart_mutation_ticks";
    private static final String STUN = "carnis:dart_stun_ticks";
    private static final String PRIOR_NO_AI = "carnis:dart_previous_no_ai";
    private DartTreatmentEvents() { }
    public static boolean isMutating(Mob mob) { return mob.getPersistentData().contains(MUTATION); }
    public static boolean isStunned(Mob mob) { return mob.getPersistentData().getInt(STUN) > 0; }
    private static void lock(Mob mob) {
        CompoundTag tag = mob.getPersistentData();
        if (!tag.contains(PRIOR_NO_AI)) tag.putBoolean(PRIOR_NO_AI, mob.isNoAi());
        mob.getNavigation().stop();
        mob.setTarget(null);
        mob.setNoAi(true);
    }
    private static void unlock(Mob mob) {
        CompoundTag tag = mob.getPersistentData();
        if (!tag.contains(PRIOR_NO_AI)) return;
        mob.setNoAi(tag.getBoolean(PRIOR_NO_AI));
        tag.remove(PRIOR_NO_AI);
    }
    public static void startRegression(Mob mob) {
        if (!(mob.level() instanceof ServerLevel) || !mob.isAlive()) return;
        if (!(mob instanceof InfectedZombieEntity) && !(mob instanceof InfectedSkeletonEntity)) return;
        if (mob.getPersistentData().contains(REGRESSION)) return;
        mob.getPersistentData().putInt(REGRESSION, 100);
        HiveSwarmCoordinator.clearFrenzy(mob);
        lock(mob);
    }
    public static void startMutation(Mob mob) {
        if (!(mob.level() instanceof ServerLevel) || !mob.isAlive()) return;
        EntityType<?> type = mob.getType();
        if (type != EntityType.ZOMBIE && type != EntityType.SKELETON && type != EntityType.CREEPER
                && type != EntityType.SPIDER && type != EntityType.CAVE_SPIDER) return;
        if (!mob.getPersistentData().contains(MUTATION)) mob.getPersistentData().putInt(MUTATION, 60);
    }
    public static void stun(Mob mob, int ticks) {
        if (!(mob.level() instanceof ServerLevel) || !mob.isAlive() || ticks <= 0) return;
        CompoundTag tag = mob.getPersistentData();
        tag.putInt(STUN, Math.max(tag.getInt(STUN), ticks));
        HiveSwarmCoordinator.clearFrenzy(mob);
        lock(mob);
    }
    @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || !(mob.level() instanceof ServerLevel level) || !mob.isAlive()) return;
        CompoundTag tag = mob.getPersistentData();
        if (tag.contains(REGRESSION)) {
            lock(mob);
            Vec3 motion = mob.getDeltaMovement();
            mob.setDeltaMovement(0, motion.y, 0);
            if (mob.tickCount % 3 == 0) {
                mob.setYHeadRot(mob.getYRot() + (level.random.nextBoolean() ? 15F : -15F));
                level.sendParticles(ModParticles.PURIFIER_FLAME.get(), mob.getX(), mob.getY(.5D), mob.getZ(),
                        5, mob.getBbWidth() * .35D, mob.getBbHeight() * .35D, mob.getBbWidth() * .35D, .02D);
            }
            int remaining = tag.getInt(REGRESSION) - 1;
            if (remaining <= 0) {
                if (!convert(level, mob, true)) tag.putInt(REGRESSION, 20);
                return;
            }
            tag.putInt(REGRESSION, remaining);
        }
        if (tag.contains(MUTATION)) {
            int remaining = tag.getInt(MUTATION) - 1;
            if (remaining <= 0) {
                if (!convert(level, mob, false)) tag.putInt(MUTATION, 20);
                return;
            }
            tag.putInt(MUTATION, remaining);
        }
        if (tag.getInt(STUN) > 0) {
            lock(mob);
            Vec3 motion = mob.getDeltaMovement();
            mob.setDeltaMovement(0, motion.y, 0);
            int remaining = tag.getInt(STUN) - 1;
            if (remaining == 0) {
                tag.remove(STUN);
                if (!tag.contains(REGRESSION)) unlock(mob);
            } else tag.putInt(STUN, remaining);
        }
    }
    private static boolean convert(ServerLevel level, Mob source, boolean purify) {
        Mob result;
        if (purify && source instanceof InfectedZombieEntity) {
            result = level.random.nextFloat() < .30F ? EntityType.VILLAGER.create(level) : EntityType.ZOMBIE.create(level);
        } else if (purify && source instanceof InfectedSkeletonEntity) {
            result = EntityType.SKELETON.create(level);
        } else if (!purify && source.getType() == EntityType.ZOMBIE) {
            result = ModEntities.INFECTED_ZOMBIE.get().create(level);
        } else if (!purify && source.getType() == EntityType.SKELETON) {
            result = ModEntities.INFECTED_SKELETON.get().create(level);
        } else if (!purify && source.getType() == EntityType.CREEPER) {
            result = ModEntities.INFECTED_CREEPER.get().create(level);
        } else if (!purify && (source.getType() == EntityType.SPIDER
                || source.getType() == EntityType.CAVE_SPIDER)) {
            result = ModEntities.INFECTED_SPIDER.get().create(level);
        } else return false;
        if (result == null) return false;
        result.moveTo(source.getX(), source.getY(), source.getZ(), source.getYRot(), source.getXRot());
        result.setCustomName(source.getCustomName());
        result.setCustomNameVisible(source.isCustomNameVisible());
        result.setHealth(Math.max(.01F, Math.min(1F, source.getHealth() / source.getMaxHealth())) * result.getMaxHealth());
        if (source.isPersistenceRequired()) result.setPersistenceRequired();
        for (EquipmentSlot slot : EquipmentSlot.values()) result.setItemSlot(slot, source.getItemBySlot(slot).copy());
        if (!level.addFreshEntity(result)) return false;
        source.discard();
        if (purify) {
            result.spawnAtLocation(new ItemStack(ModItems.BIOMASS_REMAINS.get(), 1 + level.random.nextInt(2)));
            level.playSound(null, result.blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1F, 1.0F);
        }
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/event/FleshAmalgamCombatEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.FleshAmalgamEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraftforge.event.entity.ProjectileImpactEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class FleshAmalgamCombatEvents {
    private FleshAmalgamCombatEvents() {
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void onProjectileImpact(ProjectileImpactEvent event) {
        Projectile projectile = event.getProjectile();

        if (
                event.isCanceled()
                        || event.getImpactResult()
                        != ProjectileImpactEvent.ImpactResult.DEFAULT
                        || !(projectile.level() instanceof ServerLevel)
                        || !(event.getRayTraceResult()
                        instanceof EntityHitResult entityHitResult)
                        || !(entityHitResult.getEntity()
                        instanceof FleshAmalgamEntity amalgam)
                        || !amalgam.tryDeflectProjectile(projectile)
        ) {
            return;
        }

        // The arrow's velocity has already been redirected at the impact point.
        // Skip this collision so it does not immediately damage the Amalgam.
        event.setImpactResult(
                ProjectileImpactEvent.ImpactResult.SKIP_ENTITY
        );
    }
}
```

## `src/main/java/com/carnis/mod/event/HallucinationEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.hallucination.HallucinationType;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.item.NeuroWeave;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.network.packet.ClientboundHallucinationPacket;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class HallucinationEvents {
    public static final float INFECTION_THRESHOLD = 60.0F;
    public static final int MIN_DELAY_TICKS = 20 * 20;
    public static final int MAX_DELAY_TICKS = 50 * 20;

    private static final float MIN_VOLUME_MULTIPLIER = 0.85F;
    private static final float MAX_VOLUME_MULTIPLIER = 1.15F;
    private static final String DELAY_TAG =
            CarnisMod.MOD_ID + ":hallucination_delay_ticks";
    private static final HallucinationType[] TYPES =
            HallucinationType.values();

    private HallucinationEvents() {
    }

    // ОТКЛЮЧЕНО: дублирует PlayerHallucinationHandler. Сервер не должен отправлять звуковые пакеты галлюцинаций.
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (
                event.phase != TickEvent.Phase.END
                        || !(event.player instanceof ServerPlayer player)
        ) {
            return;
        }

        CompoundTag persistentData = player.getPersistentData();

        if (
                !player.isAlive()
                        || player.isSpectator()
                        || NeuroResonatorHelmetItem.isEquipped(player)
                        || PlayerInfectionApi.getInfectionLevel(player)
                        < INFECTION_THRESHOLD
        ) {
            resetHallucinationTimer(player);
            return;
        }

        if (!persistentData.contains(DELAY_TAG)) {
            scheduleNextHallucination(persistentData, player.getRandom(), PlayerInfectionApi.getInfectionLevel(player) >= 100.0F);
            return;
        }

        int remainingTicks = persistentData.getInt(DELAY_TAG);

        if (remainingTicks > 1) {
            persistentData.putInt(DELAY_TAG, remainingTicks - 1);
            return;
        }

        RandomSource random = player.getRandom();
        HallucinationType type = TYPES[random.nextInt(TYPES.length)];
        float volumeMultiplier = MIN_VOLUME_MULTIPLIER
                + random.nextFloat()
                * (MAX_VOLUME_MULTIPLIER - MIN_VOLUME_MULTIPLIER);
        volumeMultiplier *= NeuroWeave.infectionMultiplier(player);
        Vec3 relativeOffset = createRelativeOffset(type, random);

        ModMessages.sendHallucination(
                player,
                new ClientboundHallucinationPacket(
                        type,
                        volumeMultiplier,
                        relativeOffset
                )
        );
        scheduleNextHallucination(persistentData, random, PlayerInfectionApi.getInfectionLevel(player) >= 100.0F);
    }

    public static void resetHallucinationTimer(ServerPlayer player) {
        player.getPersistentData().remove(DELAY_TAG);
    }

    private static void scheduleNextHallucination(
            CompoundTag persistentData,
            RandomSource random, boolean critical
    ) {
        persistentData.putInt(
                DELAY_TAG,
                random.nextIntBetweenInclusive(
                        critical ? 100 : MIN_DELAY_TICKS,
                        critical ? 200 : MAX_DELAY_TICKS
                )
        );
    }

    private static Vec3 createRelativeOffset(
            HallucinationType type,
            RandomSource random
    ) {
        return switch (type) {
            case CREEPER_HISS -> new Vec3(
                    0.0D,
                    0.75D,
                    -randomBetween(random, 2.0D, 3.0D)
            );
            case PHANTOM_FOOTSTEPS -> new Vec3(
                    randomBetween(random, -1.25D, 1.25D),
                    -0.15D,
                    -randomBetween(random, 2.0D, 3.5D)
            );
            case WHISPER -> new Vec3(
                    (random.nextBoolean() ? 1.0D : -1.0D)
                            * randomBetween(random, 0.55D, 1.1D),
                    1.25D,
                    -randomBetween(random, 1.0D, 2.0D)
            );
            case FALSE_DAMAGE -> new Vec3(0.0D, 1.0D, 0.0D);
        };
    }

    private static double randomBetween(
            RandomSource random,
            double minimum,
            double maximum
    ) {
        return minimum + random.nextDouble() * (maximum - minimum);
    }
}
```

## `src/main/java/com/carnis/mod/event/HiveAttackEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.HiveEyeBlockEntity;
import com.carnis.mod.util.HiveGrowthSuppression;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HiveAttackEvents {
    private HiveAttackEvents() {
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onBlockBreak(BlockEvent.BreakEvent event) {
        if (event.isCanceled() || !(event.getLevel() instanceof ServerLevel level)) return;
        Player attacker = event.getPlayer();
        if (!attacker.isAlive() || !event.getState().is(HiveGrowthSuppression.HIVE_BLOCKS)) return;

        BlockPos brokenPos = event.getPos();
        Vec3 brokenCenter = Vec3.atCenterOf(brokenPos);
        double radiusSquared = HiveEyeBlockEntity.HIVEMIND_ALERT_RADIUS
                * HiveEyeBlockEntity.HIVEMIND_ALERT_RADIUS;
        int radius = (int) Math.ceil(HiveEyeBlockEntity.HIVEMIND_ALERT_RADIUS);
        int minChunkX = (brokenPos.getX() - radius) >> 4;
        int maxChunkX = (brokenPos.getX() + radius) >> 4;
        int minChunkZ = (brokenPos.getZ() - radius) >> 4;
        int maxChunkZ = (brokenPos.getZ() + radius) >> 4;

        for (int chunkX = minChunkX; chunkX <= maxChunkX; chunkX++) {
            for (int chunkZ = minChunkZ; chunkZ <= maxChunkZ; chunkZ++) {
                var chunk = level.getChunkSource().getChunkNow(chunkX, chunkZ);
                if (chunk == null) continue;

                for (BlockEntity blockEntity : chunk.getBlockEntities().values()) {
                    if (blockEntity instanceof HiveEyeBlockEntity eye
                            && !eye.isRemoved()
                            && Vec3.atCenterOf(eye.getBlockPos()).distanceToSqr(brokenCenter) <= radiusSquared) {
                        eye.onHiveAttacked(level, attacker);
                    }
                }
            }
        }
    }
}
```

## `src/main/java/com/carnis/mod/event/HiveGrowthSuppressionEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.util.HiveGrowthSuppression;
import org.joml.Vector3f;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.BonemealEvent;
import net.minecraftforge.event.level.BlockEvent.CropGrowEvent;
import net.minecraftforge.event.level.SaplingGrowTreeEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.HashSet;
import java.util.Set;

/** Серверные события подавления роста естественной флоры и прорастания от костной муки. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HiveGrowthSuppressionEvents {
    private static final DustParticleOptions SUPPRESSION_DUST =
            new DustParticleOptions(new Vector3f(0.3F, 0.15F, 0.1F), 1.0F);

    private HiveGrowthSuppressionEvents() {
    }

    @SubscribeEvent
    public static void onCropGrow(CropGrowEvent.Pre event) {
        ServerLevel level = getServerLevel(event.getLevel());
        if (level == null) {
            return;
        }
        BlockPos pos = event.getPos();
        if (shouldSuppress(level, pos)) {
            event.setResult(Event.Result.DENY);
            spawnSuppressionParticles(level, pos, 4, 1.0D, 0.3D);
        }
    }

    @SubscribeEvent
    public static void onSaplingGrow(SaplingGrowTreeEvent event) {
        ServerLevel level = getServerLevel(event.getLevel());
        if (level == null) {
            return;
        }
        BlockPos pos = event.getPos();
        if (shouldSuppress(level, pos)) {
            event.setCanceled(true);
            spawnSuppressionParticles(level, pos, 4, 1.0D, 0.3D);
        }
    }

    @SubscribeEvent
    public static void onBonemeal(BonemealEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer)) {
            return;
        }
        ServerLevel level = getServerLevel(event.getLevel());
        if (level == null) {
            return;
        }

        int strength = CarnisConfig.SERVER.growthSuppressionStrength.get();
        BlockPos pos = event.getPos();
        if (strength <= 0 || !HiveGrowthSuppression.isNearHive(
                level,
                pos,
                CarnisConfig.SERVER.growthSuppressionRadius.get()
        )) {
            return;
        }

        if (level.random.nextFloat() < strength / 100.0F) {
            event.setCanceled(true);
            spawnSuppressionParticles(level, pos, 4, 1.0D, 0.3D);
        }
    }

    /** Кэш поиска очищается каждые 100 серверных тиков. */
    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase == TickEvent.Phase.END && event.getServer().getTickCount() % 100 == 0) {
            HiveGrowthSuppression.clearCache();
        }
    }

    /** Периодически увядает трава и микелий внутри активной зоны Улья. */
    @SubscribeEvent
    public static void onServerTickGrassWither(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.getServer().getTickCount() % 200 != 0) {
            return;
        }

        int strength = CarnisConfig.SERVER.growthSuppressionStrength.get();
        if (strength <= 0) {
            return;
        }

        int radius = CarnisConfig.SERVER.growthSuppressionRadius.get();
        int scanRadius = radius * 2;
        float suppressionChance = strength / 100.0F;
        int changes = 0;
        BlockState dirt = Blocks.DIRT.defaultBlockState();

        scan:
        for (ServerLevel level : event.getServer().getAllLevels()) {
            Set<Long> testedPositions = new HashSet<>();
            for (ServerPlayer player : level.players()) {
                BlockPos center = player.blockPosition();
                int minX = center.getX() - scanRadius;
                int maxX = center.getX() + scanRadius;
                int minZ = center.getZ() - scanRadius;
                int maxZ = center.getZ() + scanRadius;
                int minY = Math.max(level.getMinBuildHeight(), center.getY() - scanRadius);
                int maxY = Math.min(level.getMaxBuildHeight() - 1, center.getY() + scanRadius);
                BlockPos.MutableBlockPos cursor = new BlockPos.MutableBlockPos();

                for (int x = minX; x <= maxX; x++) {
                    for (int y = minY; y <= maxY; y++) {
                        for (int z = minZ; z <= maxZ; z++) {
                            cursor.set(x, y, z);
                            if (!level.hasChunkAt(cursor)) {
                                continue;
                            }

                            BlockState state = level.getBlockState(cursor);
                            if (!state.is(Blocks.GRASS_BLOCK) && !state.is(Blocks.MYCELIUM)) {
                                continue;
                            }

                            long packedPos = cursor.asLong();
                            if (!testedPositions.add(packedPos)
                                    || !HiveGrowthSuppression.isNearHive(level, cursor, radius)
                                    || level.random.nextFloat() >= suppressionChance) {
                                continue;
                            }

                            BlockPos targetPos = cursor.immutable();
                            if (level.setBlockAndUpdate(targetPos, dirt)) {
                                spawnSuppressionParticles(level, targetPos, 3, 1.0D, 0.3D);
                                level.playSound(null, targetPos, SoundEvents.GRASS_BREAK,
                                        SoundSource.BLOCKS, 0.3F, 1.0F);
                                changes++;
                                if (changes >= 32) {
                                    break scan;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    private static boolean shouldSuppress(ServerLevel level, BlockPos pos) {
        int strength = CarnisConfig.SERVER.growthSuppressionStrength.get();
        if (strength <= 0) {
            return false;
        }

        float factor = HiveGrowthSuppression.getSuppressionFactor(
                level,
                pos,
                CarnisConfig.SERVER.growthSuppressionRadius.get(),
                strength
        );
        if (factor >= 1.0F) {
            return false;
        }
        if (factor <= 0.0F) {
            return true;
        }
        return level.random.nextFloat() > factor;
    }

    private static void spawnSuppressionParticles(
            ServerLevel level,
            BlockPos pos,
            int count,
            double yOffset,
            double spread
    ) {
        level.sendParticles(
                SUPPRESSION_DUST,
                pos.getX() + 0.5D,
                pos.getY() + yOffset,
                pos.getZ() + 0.5D,
                count,
                spread,
                spread,
                spread,
                0.0D
        );
    }

    private static ServerLevel getServerLevel(LevelAccessor levelAccessor) {
        if (levelAccessor.isClientSide() || !(levelAccessor instanceof ServerLevel serverLevel)) {
            return null;
        }
        return serverLevel;
    }
}
```

## `src/main/java/com/carnis/mod/event/HypnosisEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.entity.ai.GoalPriorityUtil;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.EnumSet;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HypnosisEvents {
    private static final String UNTIL = "carnis:trance_until", POOL = "carnis:trance_pool";
    private HypnosisEvents() { }
    public static void apply(Mob mob, ServerLevel level, BlockPos pool) {
        mob.getPersistentData().putLong(UNTIL, level.getGameTime() + 60);
        if (pool == null) mob.getPersistentData().remove(POOL); else mob.getPersistentData().putLong(POOL, pool.asLong());
    }
    @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || !(mob.level() instanceof ServerLevel level)) return;
        if (mob.tickCount % 10 != 0) return;
        boolean active = mob.getPersistentData().getLong(UNTIL) > level.getGameTime();
        TranceGoal found = null;
        for (var wrapped : mob.goalSelector.getAvailableGoals())
            if (wrapped.getGoal() instanceof TranceGoal g) { found = g; break; }
        if (active && found == null) mob.goalSelector.addGoal(GoalPriorityUtil.firstUnused(mob.goalSelector), new TranceGoal(mob));
        else if (!active && found != null) {
            mob.goalSelector.removeGoal(found);
            mob.getPersistentData().remove(UNTIL);
            mob.getPersistentData().remove(POOL);
        }
    }
    private static final class TranceGoal extends Goal {
        private final Mob mob;
        TranceGoal(Mob mob) { this.mob = mob; setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK)); }
        @Override public boolean canUse() { return mob.level() instanceof ServerLevel l && mob.getPersistentData().getLong(UNTIL) > l.getGameTime(); }
        @Override public boolean canContinueToUse() { return canUse(); }
        @Override public void start() { mob.getNavigation().stop(); }
        @Override public void stop() { mob.getNavigation().stop(); }
        @Override public void tick() {
            if (!(mob.level() instanceof ServerLevel level)) return;
            if (!mob.getPersistentData().contains(POOL)) { mob.getNavigation().stop(); return; }
            BlockPos pool = BlockPos.of(mob.getPersistentData().getLong(POOL));
            if (!level.hasChunkAt(pool) || !level.getBlockState(pool).is(ModBlocks.STOMACH_POOL.get())) {
                mob.getNavigation().stop(); return;
            }
            if (mob.tickCount % 10 == 0) mob.getNavigation().moveTo(pool.getX() + .5D, pool.getY(), pool.getZ() + .5D, 0.9D);
        }
        @Override public boolean requiresUpdateEveryTick() { return true; }
    }
}
```

## `src/main/java/com/carnis/mod/event/IncubationEvents.java`

```java
package com.carnis.mod.event;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.animal.horse.AbstractHorse;

import java.util.Set;

/** Явный список допустимых ванильных носителей. */
public final class IncubationEvents {
    private static final Set<String> ANIMAL_HOSTS = Set.of(
            "cow", "sheep", "pig", "chicken", "goat", "llama", "trader_llama", "horse",
            "donkey", "mule", "skeleton_horse", "zombie_horse", "fox", "wolf", "cat",
            "ocelot", "parrot", "panda", "polar_bear", "turtle", "frog", "camel", "sniffer",
            "strider", "mooshroom", "rabbit", "bee", "hoglin", "tadpole", "cod", "salmon",
            "pufferfish", "tropical_fish", "squid", "glow_squid", "dolphin", "axolotl"
    );
    private static final Set<String> ORIGINAL_PEACEFUL_HOSTS = Set.of("cow", "sheep", "pig", "chicken", "villager");

    private IncubationEvents() { }

    public static boolean isHostileHost(LivingEntity entity) {
        EntityType<?> type = entity.getType();
        return type == EntityType.ZOMBIE || type == EntityType.SKELETON
                || type == EntityType.CREEPER || type == EntityType.SPIDER || type == EntityType.CAVE_SPIDER;
    }

    /** Тип носителя без проверки текущей стадии: используется при продолжающейся инкубации. */
    public static boolean supportsIncubation(LivingEntity entity) {
        ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType());
        return isHostileHost(entity) || id != null && id.getNamespace().equals("minecraft")
                && (ANIMAL_HOSTS.contains(id.getPath()) || id.getPath().equals("villager"));
    }

    public static boolean hasOwner(LivingEntity entity) {
        return entity instanceof TamableAnimal tame && tame.getOwnerUUID() != null
                || entity instanceof AbstractHorse horse && horse.getOwnerUUID() != null;
    }

    /** Проверка исключительно для начала заражения. */
    public static boolean isEligible(LivingEntity entity) {
        return supportsIncubation(entity) && !hasOwner(entity) && !InfectionHandler.isInfected(entity);
    }

    /** Новые не превращающиеся носители; старые мирные виды сохраняют прежнюю механику. */
    public static boolean isNewAnimalHost(LivingEntity entity) {
        ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType());
        return id != null && id.getNamespace().equals("minecraft")
                && ANIMAL_HOSTS.contains(id.getPath()) && !ORIGINAL_PEACEFUL_HOSTS.contains(id.getPath());
    }
}
```

## `src/main/java/com/carnis/mod/event/InfectedSpiderEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.InfectedSpiderEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class InfectedSpiderEvents {
    private InfectedSpiderEvents() {
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onHit(LivingHurtEvent event) {
        if (!event.isCanceled() && event.getAmount() > 0.0F
                && event.getEntity().level() instanceof ServerLevel
                && event.getSource().getEntity() instanceof InfectedSpiderEntity spider
                && event.getSource().getDirectEntity() == spider) {
            event.getEntity().addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 1));
        }
    }
}
```

## `src/main/java/com/carnis/mod/event/InfectionEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.ParasiticTendrilEntity;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** A bounded night-time incursion attempt once per level every 600 ticks. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class InfectionEvents {
    private static final long INTERVAL_TICKS = 600L;
    private static final long BIOMASS_LIMIT = 200L;
    private static final int ATTEMPTS = 12;
    private static final int RADIUS = 16;

    private InfectionEvents() { }

    @SubscribeEvent
    public static void onLevelTick(TickEvent.LevelTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.level instanceof ServerLevel level)
                || level.getGameTime() % INTERVAL_TICKS != 0
                || !level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)
                || level.getDifficulty() == Difficulty.PEACEFUL
                || !level.dimensionType().hasSkyLight()
                || CarnisWorldData.get(level).getBiomassPoints() >= BIOMASS_LIMIT) return;

        long dayTime = Math.floorMod(level.getDayTime(), 24000L);
        if (dayTime < 13000L || dayTime >= 23000L) return;

        // Reservoir sampling chooses uniformly without allocating a full candidate list.
        // This traverses loaded entities only once per interval, never loads chunks.
        Animal chosen = null;
        int seen = 0;
        for (Entity entity : level.getAllEntities()) {
            if (!(entity instanceof Animal animal) || !animal.isAlive()
                    || !"minecraft".equals(BuiltInRegistries.ENTITY_TYPE.getKey(animal.getType()).getNamespace())) continue;
            if (level.random.nextInt(++seen) == 0) chosen = animal;
        }
        if (chosen == null || !level.hasChunkAt(chosen.blockPosition())
                || containsTendril(level, new ChunkPos(chosen.blockPosition()))) return;

        for (int i = 0; i < ATTEMPTS; i++) {
            int dx = level.random.nextInt(RADIUS * 2 + 1) - RADIUS;
            int dz = level.random.nextInt(RADIUS * 2 + 1) - RADIUS;
            if (dx * dx + dz * dz > RADIUS * RADIUS) continue;
            BlockPos column = chosen.blockPosition().offset(dx, 0, dz);
            if (!level.hasChunkAt(column)) continue;
            BlockPos pos = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, column);
            if (!level.hasChunkAt(pos) || level.isOutsideBuildHeight(pos)
                    || !level.getBiome(pos).is(BiomeTags.IS_OVERWORLD)
                    || Vec3.atBottomCenterOf(pos).distanceToSqr(chosen.position()) > RADIUS * RADIUS
                    || containsTendril(level, new ChunkPos(pos))
                    || !ModEntities.canSpawnTendril(ModEntities.PARASITIC_TENDRIL.get(), level,
                            MobSpawnType.NATURAL, pos, level.random)) continue;
            AABB bounds = ModEntities.PARASITIC_TENDRIL.get().getDimensions()
                    .makeBoundingBox(pos.getX() + .5D, pos.getY(), pos.getZ() + .5D);
            if (!level.noCollision(bounds) || !level.getFluidState(pos).isEmpty()) continue;
            // EntityType.spawn performs normal entity initialization and insertion.
            ModEntities.PARASITIC_TENDRIL.get().spawn(level, pos, MobSpawnType.NATURAL);
            return;
        }
    }

    private static boolean containsTendril(ServerLevel level, ChunkPos chunk) {
        AABB bounds = new AABB(chunk.getMinBlockX(), level.getMinBuildHeight(), chunk.getMinBlockZ(),
                chunk.getMinBlockX() + 16, level.getMaxBuildHeight(), chunk.getMinBlockZ() + 16);
        return !level.getEntitiesOfClass(ParasiticTendrilEntity.class, bounds, Entity::isAlive).isEmpty();
    }
}
```

## `src/main/java/com/carnis/mod/event/InfectionHandler.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModEffects;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.UUID;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class InfectionHandler {
    public static final String STAGE = "carnis:infection_stage";
    public static final String TIMER = "carnis:infection_timer";
    private static final UUID SLOW_ID = UUID.fromString("36782739-7a30-44e0-a1e2-d40ac9fa072c");
    private static final AttributeModifier SLOW = new AttributeModifier(SLOW_ID, "Carnis incubation", -0.20D,
            AttributeModifier.Operation.MULTIPLY_TOTAL);
    private InfectionHandler() { }

    public static boolean isInfected(LivingEntity host) { return host.getPersistentData().getInt(STAGE) > 0; }

    public static void begin(LivingEntity host) {
        if (host.level().isClientSide || !IncubationEvents.isEligible(host)) return;
        host.getPersistentData().putInt(STAGE, 1);
        host.getPersistentData().putInt(TIMER, 0);
        syncMarker(host, 1);
    }

    /** Viral dart starts stage two and advances incubation three ticks per loaded tick. */
    public static void beginAccelerated(LivingEntity host) {
        if (!(host.level() instanceof ServerLevel) || !IncubationEvents.supportsIncubation(host)
                || IncubationEvents.hasOwner(host)) return;
        CompoundTag tag = host.getPersistentData();
        if (tag.getInt(STAGE) < 2) {
            tag.putInt(STAGE, 2);
            tag.putInt(TIMER, 200);
            syncMarker(host, 2);
        }
        tag.putBoolean("carnis:accelerated_incubation", true);
    }

    @SubscribeEvent
    public static void onTick(LivingEvent.LivingTickEvent event) {
        LivingEntity host = event.getEntity();
        if (!(host.level() instanceof ServerLevel level) || !host.isAlive()) return;
        if (host instanceof Mob mob && DartTreatmentEvents.isMutating(mob)) return;
        CompoundTag tag = host.getPersistentData();
        int stage = tag.getInt(STAGE);
        if (stage < 1 || stage > 4 || !IncubationEvents.supportsIncubation(host)) return;
        if (IncubationEvents.hasOwner(host)) {
            tag.remove(STAGE);
            tag.remove(TIMER);
            tag.remove("carnis:accelerated_incubation");
            host.removeEffect(ModEffects.INCUBATING.get());
            applySlow(host, false);
            return;
        }
        int timer = tag.getInt(TIMER) + (tag.getBoolean("carnis:accelerated_incubation") ? 3 : 1);
        tag.putInt(TIMER, timer);
        int next = timer >= 600 ? 4 : timer >= 500 ? 3 : timer >= 200 ? 2 : 1;
        if (next != stage) {
            tag.putInt(STAGE, next);
            stage = next;
            if (stage == 3) rupture(level, host);
            if (!host.isAlive()) return;
            if (stage < 4) syncMarker(host, stage);
        }
        applySlow(host, stage >= 2);
        if (stage < 4 && !host.hasEffect(ModEffects.INCUBATING.get())) syncMarker(host, stage);
        if (stage == 1 && timer % 35 == 0) {
            level.sendParticles(ModParticles.BIOMASS_SPARK.get(), host.getX(), host.getEyeY() - 0.1D, host.getZ(),
                    2, host.getBbWidth() * 0.22D, 0.08D, host.getBbWidth() * 0.22D, 0.01D);
        }
        if (stage == 1 && timer % 8 == 0) {
            host.setYHeadRot(host.getYHeadRot() + (level.random.nextBoolean() ? 2.0F : -2.0F));
        }
        if (stage == 4 && timer % 20 == 0) finish(level, host);
    }

    private static void syncMarker(LivingEntity host, int stage) {
        host.removeEffect(ModEffects.INCUBATING.get());
        host.addEffect(new MobEffectInstance(ModEffects.INCUBATING.get(), 700, stage - 1, false, false, false));
    }

    private static void applySlow(LivingEntity host, boolean active) {
        AttributeInstance movement = host.getAttribute(Attributes.MOVEMENT_SPEED);
        if (movement == null) return;
        if (active && !movement.hasModifier(SLOW)) movement.addTransientModifier(SLOW);
        else if (!active && movement.hasModifier(SLOW)) movement.removeModifier(SLOW_ID);
    }

    @SubscribeEvent
    public static void onDeath(LivingDeathEvent event) {
        if (!event.isCanceled() && event.getEntity().level() instanceof ServerLevel) applySlow(event.getEntity(), false);
    }

    private static void rupture(ServerLevel level, LivingEntity host) {
        level.playSound(null, host.blockPosition(), ModSounds.ACID_SPLASH.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), host.getX(), host.getY(0.5D), host.getZ(),
                36, host.getBbWidth() * 0.4D, host.getBbHeight() * 0.3D, host.getBbWidth() * 0.4D, 0.10D);
        if (ForgeEventFactory.getMobGriefingEvent(level, host)) seedGround(level, host);
        host.hurt(level.damageSources().magic(), host.getMaxHealth() * 0.30F);
    }

    private static void seedGround(ServerLevel level, LivingEntity host) {
        BlockPos center = host.blockPosition();
        for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) {
            BlockPos ground = center.offset(dx, -1, dz);
            if (ground.distToCenterSqr(host.getX(), ground.getY() + 0.5D, host.getZ()) > 2.25D
                    || !level.hasChunkAt(ground) || level.isOutsideBuildHeight(ground)) continue;
            BlockState old = level.getBlockState(ground);
            if (!old.hasBlockEntity() && old.getFluidState().isEmpty() && old.getDestroySpeed(level, ground) >= 0
                    && old.isFaceSturdy(level, ground, Direction.UP))
                level.setBlockAndUpdate(ground, ModBlocks.LIVING_FLESH.get().defaultBlockState());
        }
        for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) for (int dy = 0; dy <= 1; dy++) {
            BlockPos pos = center.offset(dx, dy, dz);
            if (pos.distToCenterSqr(host.getX(), host.getY() + 0.5D, host.getZ()) > 2.25D
                    || !level.hasChunkAt(pos) || level.isOutsideBuildHeight(pos)) continue;
            BlockState old = level.getBlockState(pos);
            if (!old.isAir() && !old.is(ModBlocks.FLESH_VEINS.get())) continue;
            BlockState result = old.isAir() ? Blocks.AIR.defaultBlockState() : old;
            for (Direction face : Direction.Plane.HORIZONTAL) {
                BlockPos wall = pos.relative(face);
                if (!level.hasChunkAt(wall) || level.isOutsideBuildHeight(wall)
                        || !level.getBlockState(wall).isFaceSturdy(level, wall, face.getOpposite())) continue;
                BlockState next = ModBlocks.FLESH_VEINS.get().getStateForPlacement(result, level, pos, face);
                if (next != null) result = next;
            }
            if (!result.equals(old)) level.setBlockAndUpdate(pos, result);
        }
    }

    private static void finish(ServerLevel level, LivingEntity host) {
        if (!IncubationEvents.isHostileHost(host)) {
            if (IncubationEvents.isNewAnimalHost(host)) {
                level.sendParticles(ParticleTypes.ITEM_SLIME, host.getX(), host.getY(0.5D), host.getZ(),
                        20, host.getBbWidth() * 0.3D, host.getBbHeight() * 0.25D, host.getBbWidth() * 0.3D, 0.08D);
                host.hurt(level.damageSources().magic(), 1000.0F);
            } else {
                host.hurt(level.damageSources().magic(), Float.MAX_VALUE);
            }
            return;
        }
        EntityType<?> type = host.getType();
        Mob converted = type == EntityType.ZOMBIE ? ModEntities.INFECTED_ZOMBIE.get().create(level)
                : type == EntityType.SKELETON ? ModEntities.INFECTED_SKELETON.get().create(level)
                : type == EntityType.CREEPER ? ModEntities.INFECTED_CREEPER.get().create(level)
                : ModEntities.INFECTED_SPIDER.get().create(level);
        if (converted == null) return;
        converted.moveTo(host.getX(), host.getY(), host.getZ(), host.getYRot(), host.getXRot());
        converted.setHealth(Math.max(0.01F, Math.min(1.0F, host.getHealth() / host.getMaxHealth())) * converted.getMaxHealth());
        converted.setCustomName(host.getCustomName());
        converted.setCustomNameVisible(host.isCustomNameVisible());
        for (EquipmentSlot slot : EquipmentSlot.values()) converted.setItemSlot(slot, host.getItemBySlot(slot).copy());
        if (!level.addFreshEntity(converted)) return;
        applySlow(host, false);
        host.discard();
    }
}
```

## `src/main/java/com/carnis/mod/event/LegacyRegistryMappings.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModItems;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.MissingMappingsEvent;

/** Best-effort block/item ID migration; the retired digestor block entity has no replacement. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class LegacyRegistryMappings {
    private LegacyRegistryMappings() { }

    @SubscribeEvent
    public static void onMissingMappings(MissingMappingsEvent event) {
        for (var mapping : event.getMappings(ForgeRegistries.Keys.BLOCKS, CarnisMod.MOD_ID)) {
            switch (mapping.getKey().getPath()) {
                case "synapse_pillar" -> mapping.remap(ModBlocks.NERVE_PILLAR.get());
                case "digestor_pit" -> mapping.remap(ModBlocks.STOMACH_POOL.get());
                default -> { }
            }
        }
        for (var mapping : event.getMappings(ForgeRegistries.Keys.ITEMS, CarnisMod.MOD_ID)) {
            switch (mapping.getKey().getPath()) {
                case "synapse_pillar" -> mapping.remap(ModItems.NERVE_PILLAR.get());
                case "digestor_pit" -> mapping.remap(ModItems.STOMACH_POOL.get());
                default -> { }
            }
        }
        for (var mapping : event.getMappings(ForgeRegistries.Keys.BLOCK_ENTITY_TYPES, CarnisMod.MOD_ID)) {
            if (mapping.getKey().getPath().equals("digestor_pit")) {
                // Stomach pools are not block entities. Old block-entity NBT cannot be retained.
                mapping.ignore();
                CarnisMod.LOGGER.warn("Legacy digestor_pit block-entity data cannot be migrated to stomach_pool");
            }
        }
    }
}
```

## `src/main/java/com/carnis/mod/event/ModEntityEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;

import com.carnis.mod.init.ModEntities;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.MOD
)
public final class ModEntityEvents {
    private ModEntityEvents() {
    }

    @SubscribeEvent
    public static void onSpawnPlacements(net.minecraftforge.event.entity.SpawnPlacementRegisterEvent event) {
        ModEntities.registerSpawnPlacements(event);
    }

    @SubscribeEvent
    public static void onCreateEntityAttributes(
            EntityAttributeCreationEvent event
    ) {
        event.put(ModEntities.HIVE_SENTINEL.get(), com.carnis.mod.entity.HiveSentinelEntity.createAttributes().build());
        event.put(ModEntities.CEREBRAL_NEXUS.get(), com.carnis.mod.entity.CerebralNexusEntity.createAttributes().build());
        event.put(ModEntities.BIOMASS_MAGGOT.get(), com.carnis.mod.entity.BiomassMaggotEntity.createAttributes().build());
        event.put(ModEntities.PARASITIC_TENDRIL.get(), com.carnis.mod.entity.ParasiticTendrilEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_ZOMBIE.get(), InfectedZombieEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_SKELETON.get(), InfectedSkeletonEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_CREEPER.get(), InfectedCreeperEntity.createAttributes().build());
        event.put(ModEntities.INFECTED_SPIDER.get(), InfectedSpiderEntity.createAttributes().build());

        event.put(
                ModEntities.FLESH_AMALGAM.get(),
                FleshAmalgamEntity.createAttributes().build()
        );
    }
}
```

## `src/main/java/com/carnis/mod/event/NeuroArmorEventHandler.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.HiveEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.item.armor.NeuroArmorItem;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NeuroArmorEventHandler {
    private static final EquipmentSlot[] SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
    private static final String PROVOKED_UNTIL = "carnis:neuro_provoked_until";
    private static final String PROVOKED_DIMENSION = "carnis:neuro_provoked_dimension";
    private static final int PROVOCATION_TICKS = 600;
    private NeuroArmorEventHandler() { }

    private static boolean piece(LivingEntity entity, EquipmentSlot slot, ArmorItem.Type expected) {
        ItemStack stack = entity.getItemBySlot(slot);
        return stack.getItem() instanceof NeuroArmorItem armor && armor.getType() == expected;
    }
    public static boolean hasHelmet(LivingEntity entity) { return piece(entity, EquipmentSlot.HEAD, ArmorItem.Type.HELMET); }
    public static boolean hasSymbioticPair(LivingEntity entity) {
        return piece(entity, EquipmentSlot.CHEST, ArmorItem.Type.CHESTPLATE)
                && piece(entity, EquipmentSlot.LEGS, ArmorItem.Type.LEGGINGS);
    }
    public static int pieces(LivingEntity entity) {
        int count = 0;
        for (EquipmentSlot slot : SLOTS) {
            ItemStack stack = entity.getItemBySlot(slot);
            if (stack.getItem() instanceof NeuroArmorItem armor && armor.getEquipmentSlot() == slot) count++;
        }
        return count;
    }
    public static boolean hasFullSet(LivingEntity entity) { return pieces(entity) == 4; }
    public static boolean isHiveEntity(Entity entity) {
        if (!(entity instanceof LivingEntity)) return false;
        if (entity instanceof HiveEntity || entity instanceof HivemindLinkedMob) return true;
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
        return id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }
    public static void provoke(Player player) {
        player.getPersistentData().putLong(PROVOKED_UNTIL, player.level().getGameTime() + PROVOCATION_TICKS);
        player.getPersistentData().putString(PROVOKED_DIMENSION, player.level().dimension().location().toString());
    }
    public static boolean isProvoked(Player player) {
        return player.level().dimension().location().toString().equals(player.getPersistentData().getString(PROVOKED_DIMENSION))
                && player.level().getGameTime() < player.getPersistentData().getLong(PROVOKED_UNTIL);
    }
    /** Eye-like sensors can detect an unprovoked disguised player at four blocks or closer. */
    public static boolean hiddenFromSensor(Player player, double distanceSquared) {
        return hasFullSet(player) && !isProvoked(player) && distanceSquared > 16.0D;
    }
    private static boolean hiddenFromMob(Player player) { return hasFullSet(player) && !isProvoked(player); }

    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onHurt(LivingHurtEvent event) {
        if (event.isCanceled() || event.getEntity().level().isClientSide) return;
        Entity attacker = event.getSource().getEntity();
        if (attacker instanceof Player player && isHiveEntity(event.getEntity()) && event.getAmount() > 0) provoke(player);
        if (event.getEntity() instanceof Player player && isHiveEntity(attacker)) {
            event.setAmount(event.getAmount() * (1.0F - 0.08F * pieces(player)));
        }
    }
    @SubscribeEvent
    public static void onTargetChange(LivingChangeTargetEvent event) {
        if (!event.getEntity().level().isClientSide && isHiveEntity(event.getEntity())
                && event.getNewTarget() instanceof Player player && hiddenFromMob(player)) event.setCanceled(true);
    }
    @SubscribeEvent
    public static void onLivingTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide || !isHiveEntity(mob)) return;
        if (mob.getTarget() instanceof Player player && hiddenFromMob(player)) mob.setTarget(null);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onBreak(BlockEvent.BreakEvent event) {
        if (event.isCanceled() || event.getPlayer().level().isClientSide || !hasFullSet(event.getPlayer())) return;
        BlockState state = event.getState();
        if (!state.is(ModBlocks.LIVING_FLESH.get()) && !state.is(ModBlocks.OSSIFIED_FLESH.get())
                && !state.is(ModBlocks.FIREPROOF_FLESH.get()) && !state.is(ModBlocks.FLESH_VEINS.get())
                && !state.is(ModBlocks.BIOMASS_REMAINS.get())) return;
        Player player = event.getPlayer();
        BlockPos pos = event.getPos();
        var nearby = player.level().getEntitiesOfClass(Mob.class, new AABB(pos).inflate(12.0D),
                mob -> mob.isAlive() && isHiveEntity(mob) && mob.distanceToSqr(pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D) <= 144.0D);
        if (nearby.isEmpty()) return;
        provoke(player);
        for (Mob mob : nearby) if (mob.canAttack(player)) mob.setTarget(player);
    }
    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.player.level().isClientSide) return;
        Player player = event.player;
        if (!player.isAlive() || player.isSpectator() || !player.onGround() || !hasSymbioticPair(player)
                || player.tickCount % 60 != 0 || player.getHealth() >= player.getMaxHealth()) return;
        if (player.getBlockStateOn().is(ModBlocks.LIVING_FLESH.get())) player.heal(1.0F);
    }
}
```

## `src/main/java/com/carnis/mod/event/NeuroWeavingEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.item.NeuroWeave;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.AnvilUpdateEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NeuroWeavingEvents {
    private NeuroWeavingEvents() {
    }

    @SubscribeEvent
    public static void onAnvilUpdate(AnvilUpdateEvent event) {
        ItemStack left = event.getLeft();
        if (!(left.getItem() instanceof ArmorItem) || !event.getRight().is(ModItems.NEURAL_BINDING_MATRIX.get())
                || NeuroWeave.isWoven(left)) {
            return;
        }
        ItemStack output = left.copy();
        output.getOrCreateTag().putBoolean(NeuroWeave.TAG, true);
        // Add a no-effect level-zero enchant only to otherwise unenchanted armor.
        // This preserves existing enchantments but HideFlags also hides any later enchantments.
        if (!output.isEnchanted()) {
            output.enchant(net.minecraft.world.item.enchantment.Enchantments.UNBREAKING, 0);
            output.getOrCreateTag().putInt("HideFlags", output.getOrCreateTag().getInt("HideFlags") | 1);
        }
        output.setHoverName(Component.literal("[Neuro-Woven] ").withStyle(ChatFormatting.RED)
                .append(left.getHoverName().copy().withStyle(ChatFormatting.RESET)));
        var display = output.getOrCreateTagElement("display");
        ListTag lore = display.contains("Lore", Tag.TAG_LIST)
                ? display.getList("Lore", Tag.TAG_STRING).copy() : new ListTag();
        Component line = Component.literal("Trait: ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal("Psychic & Biological Shielding").withStyle(ChatFormatting.RED));
        lore.add(StringTag.valueOf(Component.Serializer.toJson(line)));
        display.put("Lore", lore);
        event.setOutput(output);
        event.setCost(5);
        event.setMaterialCost(1);
    }
}
```

## `src/main/java/com/carnis/mod/event/PlayerInfectionEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.capability.infection.PlayerInfectionCapability;
import com.carnis.mod.capability.infection.PlayerInfectionProvider;
import com.carnis.mod.entity.FleshSpatProjectileEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;
import com.carnis.mod.infection.PlayerInfectionManager;
import com.carnis.mod.init.ModBlockTags;
import com.carnis.mod.network.ModMessages;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.AttachCapabilitiesEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerInfectionEvents {
    public static final float SURFACE_INFECTION_PER_TICK = .05F;
    public static final float MOB_HIT_BASE_INFECTION = 1.0F;
    public static final float MOB_HIT_INFECTION_PER_DAMAGE = .5F;
    private PlayerInfectionEvents() { }
    @SubscribeEvent public static void onAttachCapabilities(AttachCapabilitiesEvent<Entity> event) {
        if (!(event.getObject() instanceof Player player)) return;
        PlayerInfectionProvider provider = new PlayerInfectionProvider(player);
        event.addCapability(PlayerInfectionCapability.ID, provider);
        event.addListener(provider::invalidate);
    }
    @SubscribeEvent public static void onPlayerClone(PlayerEvent.Clone event) {
        Player old = event.getOriginal();
        old.reviveCaps();
        try { PlayerInfectionManager.copyToClone(old, event.getEntity(), event.isWasDeath()); }
        finally { old.invalidateCaps(); }
    }
    @SubscribeEvent public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) { sync(event.getEntity()); }
    @SubscribeEvent public static void onRespawn(PlayerEvent.PlayerRespawnEvent event) { sync(event.getEntity()); }
    @SubscribeEvent public static void onDimension(PlayerEvent.PlayerChangedDimensionEvent event) { sync(event.getEntity()); }
    private static void sync(Player player) { if (player instanceof ServerPlayer server) ModMessages.sendPlayerInfection(server); }
    @SubscribeEvent public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)
                || !player.isAlive() || player.isSpectator() || !player.onGround()
                || !player.getBlockStateOn().is(ModBlockTags.INFECTIOUS_SURFACES)) return;
        PlayerInfectionApi.addExposure(player, SURFACE_INFECTION_PER_TICK);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onLivingHurt(LivingHurtEvent event) {
        if (event.isCanceled() || event.getAmount() <= 0 || !(event.getEntity() instanceof ServerPlayer player)
                || event.getSource().getDirectEntity() instanceof FleshSpatProjectileEntity
                || !NeuroArmorEventHandler.isHiveEntity(event.getSource().getEntity())) return;
        Entity attacker = event.getSource().getEntity();
        boolean direct = event.getSource().getDirectEntity() == attacker;
        if (direct && attacker instanceof InfectedZombieEntity) {
            final String cooldownKey = "carnis:infected_zombie_infection_next_tick";
            long now = player.level().getGameTime();
            if (now >= player.getPersistentData().getLong(cooldownKey)) {
                player.getPersistentData().putLong(cooldownKey, now + 40L);
                if (player.getRandom().nextFloat() < 0.02F) PlayerInfectionApi.addExposure(player, 2.0F);
            }
            return;
        }
        float amount = direct && attacker instanceof InfectedSkeletonEntity ? 10.0F
                : direct && attacker instanceof InfectedSpiderEntity ? 5.0F
                : MOB_HIT_BASE_INFECTION + event.getAmount() * MOB_HIT_INFECTION_PER_DAMAGE;
        PlayerInfectionApi.addExposure(player, amount);
    }
}
```

## `src/main/java/com/carnis/mod/event/PoolDropsEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PoolDropsEvents {
    private PoolDropsEvents() { }
    @SubscribeEvent public static void onDrops(LivingDropsEvent event) {
        var entity = event.getEntity();
        var data = entity.getPersistentData();
        if (data.getBoolean("carnis:pool_dissolving")
                && data.getLong("carnis:pool_dissolving_until") >= entity.level().getGameTime()) {
            event.setCanceled(true);
        }
    }
}
```

## `src/main/java/com/carnis/mod/event/ProgressionEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModItems;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ProgressionEvents {
    private static final ResourceLocation JOURNAL_ADVANCEMENT = new ResourceLocation(CarnisMod.MOD_ID, "read_research_journal");
    private static final ResourceLocation ARMOR_ADVANCEMENT = new ResourceLocation(CarnisMod.MOD_ID, "neuro_resonator_set");

    private ProgressionEvents() { }

    @SubscribeEvent
    public static void onReadJournal(PlayerInteractEvent.RightClickItem event) {
        if (!(event.getEntity() instanceof ServerPlayer player)
                || !event.getItemStack().is(ModItems.RESEARCH_JOURNAL.get())) return;
        award(player, JOURNAL_ADVANCEMENT, "read_journal");
    }

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)) return;
        if (wearingFullResonatorSet(player)) award(player, ARMOR_ADVANCEMENT, "full_set");
    }

    private static boolean wearingFullResonatorSet(Player player) {
        return player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.NEURO_RESONATOR_HELMET.get())
                && player.getItemBySlot(EquipmentSlot.CHEST).is(ModItems.NEURO_RESONATOR_CHESTPLATE.get())
                && player.getItemBySlot(EquipmentSlot.LEGS).is(ModItems.NEURO_RESONATOR_LEGGINGS.get())
                && player.getItemBySlot(EquipmentSlot.FEET).is(ModItems.NEURO_RESONATOR_BOOTS.get());
    }

    private static void award(ServerPlayer player, ResourceLocation id, String criterion) {
        var server = player.getServer();
        if (server == null) return;
        var advancement = server.getAdvancements().getAdvancement(id);
        if (advancement != null) player.getAdvancements().award(advancement, criterion);
    }
}
```

## `src/main/java/com/carnis/mod/event/PustuleAttackEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.PustuleClusterBlock;
import net.minecraft.server.level.ServerLevel;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PustuleAttackEvents {
    private PustuleAttackEvents() { }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onAttack(PlayerInteractEvent.LeftClickBlock event) {
        if (event.isCanceled() || event.getAction() != PlayerInteractEvent.LeftClickBlock.Action.START) return;
        var level = event.getLevel();
        if (!PustuleClusterBlock.ready(level.getBlockState(event.getPos()))) return;
        if (level instanceof ServerLevel server) {
            if (PustuleClusterBlock.burst(server, event.getPos())) event.setCanceled(true);
        }
    }
}
```

## `src/main/java/com/carnis/mod/event/SludgeProtectionEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.item.NeuroWeave;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Neuro protection applies to the mod's sludge acid, not unrelated damage types. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class SludgeProtectionEvents {
    private SludgeProtectionEvents() { }

    @SubscribeEvent
    public static void onAttack(LivingAttackEvent event) {
        if (event.getSource().is(ModDamageTypes.TAINTED_SLUDGE)
                && NeuroWeave.hasSludgeImmuneBoots(event.getEntity())) event.setCanceled(true);
    }

    @SubscribeEvent
    public static void onHurt(LivingHurtEvent event) {
        if (!event.getSource().is(ModDamageTypes.TAINTED_SLUDGE)) return;
        float multiplier = NeuroWeave.infectionMultiplier(event.getEntity());
        if (multiplier <= 0.0F) event.setCanceled(true);
        else event.setAmount(event.getAmount() * multiplier);
    }
}
```

## `src/main/java/com/carnis/mod/event/StomachPoolAttractEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.entity.ai.StomachPoolAttractGoal;
import com.carnis.mod.entity.ai.GoalPriorityUtil;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class StomachPoolAttractEvents {
    private StomachPoolAttractEvents() { }

    public static boolean isAllowedType(EntityType<?> type) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(type);
        if (id == null) return false;

        // Third-party mobs: allow land/passive categories, but not foreign MONSTER bosses.
        if (!id.getNamespace().equals("minecraft")) {
            return type.getCategory() == MobCategory.CREATURE
                    || type.getCategory() == MobCategory.AMBIENT;
        }

        // Vanilla MISC-category hosts that should still be attracted.
        if (type == EntityType.VILLAGER
                || type == EntityType.WANDERING_TRADER
                || type == EntityType.IRON_GOLEM
                || type == EntityType.SNOW_GOLEM
                || type == EntityType.TRADER_LLAMA) {
            return true;
        }

        MobCategory category = type.getCategory();
        if (category == MobCategory.CREATURE || category == MobCategory.AMBIENT) return true;
        if (category == MobCategory.MONSTER) {
            return type != EntityType.ENDER_DRAGON
                    && type != EntityType.WITHER
                    && type != EntityType.ELDER_GUARDIAN
                    && type != EntityType.WARDEN;
        }
        return false;
    }

    @SubscribeEvent
    public static void onEntityJoin(EntityJoinLevelEvent event) {
        if (!(event.getLevel() instanceof ServerLevel) || !(event.getEntity() instanceof Mob mob)
                || !isAllowedType(mob.getType()) || NeuralMossBlock.isHive(mob)) return;

        for (var wrapped : mob.goalSelector.getAvailableGoals()) {
            if (wrapped.getGoal() instanceof StomachPoolAttractGoal) return;
        }

        StomachPoolAttractGoal attraction = new StomachPoolAttractGoal(mob);
        mob.goalSelector.addGoal(GoalPriorityUtil.firstUnused(mob.goalSelector), attraction.createHoldGoal());
        mob.goalSelector.addGoal(GoalPriorityUtil.firstUnused(mob.goalSelector), attraction);
    }
}
```

## `src/main/java/com/carnis/mod/fluid/TaintedSludgeBlock.java`

```java
package com.carnis.mod.fluid;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModFluids;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.item.NeuroWeave;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import java.util.Map;
import java.util.WeakHashMap;

public final class TaintedSludgeBlock extends LiquidBlock {
    private static final Map<LivingEntity, Long> LAST_EXPOSURE = new WeakHashMap<>();
    public TaintedSludgeBlock(BlockBehaviour.Properties properties) { super(ModFluids.SLUDGE_SOURCE, properties); }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        if (!(level instanceof ServerLevel server) || !(entity instanceof LivingEntity living)
                || !living.isAlive() || living.isSpectator() || living.tickCount % 20 != 0) return;
        long time = server.getGameTime();
        Long last = LAST_EXPOSURE.put(living, time);
        if (last != null && last == time) return;
        if (living instanceof Player player) PlayerInfectionApi.addExposure(player, 5.0F);
        living.hurt(ModDamageTypes.taintedSludge(server), 1.0F);
        if (!NeuroWeave.hasSludgeImmuneBoots(living)) {
            living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 0));
        }
        living.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 60, 0));
    }
}
```

## `src/main/java/com/carnis/mod/fluid/TaintedSludgeFluid.java`

```java
package com.carnis.mod.fluid;

import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModFluids;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;
import net.minecraftforge.fluids.ForgeFlowingFluid;

public final class TaintedSludgeFluid {
    private TaintedSludgeFluid() { }

    private static boolean interact(Level level, BlockPos pos) {
        if (!(level instanceof ServerLevel server) || !level.getBlockState(pos).is(ModBlocks.TAINTED_SLUDGE.get())) return false;
        for (Direction dir : Direction.values()) {
            BlockPos other = pos.relative(dir);
            if (level.isOutsideBuildHeight(other) || !level.hasChunkAt(other)) continue;
            if (level.getBlockState(other).is(Blocks.LAVA)) {
                level.setBlockAndUpdate(pos, ModBlocks.CHARRED_FLESH.get().defaultBlockState());
                server.sendParticles(ParticleTypes.CLOUD, pos.getX() + .5, pos.getY() + .5, pos.getZ() + .5,
                        18, .35, .35, .35, .03);
                level.playSound(null, pos, SoundEvents.FIRE_EXTINGUISH, SoundSource.BLOCKS, 0.8F, 1.0F);
                return true;
            }
        }
        // One randomized neighbor at most per scheduled tick; never replace waterlogged hosts.
        if (level.random.nextInt(8) == 0) {
            Direction dir = Direction.values()[level.random.nextInt(6)];
            BlockPos other = pos.relative(dir);
            if (!level.isOutsideBuildHeight(other) && level.hasChunkAt(other)
                    && level.getBlockState(other).is(Blocks.WATER)
                    && level.getFluidState(other).isSource()
                    && level.getFluidState(other).getType() == Fluids.WATER) {
                level.setBlockAndUpdate(other, ModBlocks.TAINTED_SLUDGE.get().defaultBlockState());
            }
        }
        return false;
    }

    private static void reschedule(Level level, BlockPos pos) {
        FluidState current = level.getFluidState(pos);
        if (current.getType().isSame(ModFluids.SLUDGE_SOURCE.get())) {
            level.scheduleTick(pos, current.getType(), 20);
        }
    }

    public static final class Source extends ForgeFlowingFluid.Source {
        public Source() { super(ModFluids.properties()); }
        @Override public void tick(Level level, BlockPos pos, FluidState state) {
            if (interact(level, pos)) return;
            super.tick(level, pos, state);
            reschedule(level, pos);
        }
    }

    public static final class Flowing extends ForgeFlowingFluid.Flowing {
        public Flowing() { super(ModFluids.properties()); }
        @Override public void tick(Level level, BlockPos pos, FluidState state) {
            if (interact(level, pos)) return;
            super.tick(level, pos, state);
            reschedule(level, pos);
        }
    }
}
```

## `src/main/java/com/carnis/mod/fluid/TaintedSludgeType.java`

```java
package com.carnis.mod.fluid;

import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.client.extensions.common.IClientFluidTypeExtensions;
import net.minecraftforge.fluids.FluidType;
import java.util.function.Consumer;

public final class TaintedSludgeType extends FluidType {
    public TaintedSludgeType() {
        super(FluidType.Properties.create().density(1600).viscosity(2400));
    }

    @Override
    public void initializeClient(Consumer<IClientFluidTypeExtensions> consumer) {
        consumer.accept(new IClientFluidTypeExtensions() {
            @Override public ResourceLocation getStillTexture() { return new ResourceLocation("carnis", "block/tainted_sludge_still"); }
            @Override public ResourceLocation getFlowingTexture() { return new ResourceLocation("carnis", "block/tainted_sludge_flow"); }
            @Override public int getTintColor() { return 0xFF8A1A22; }
        });
    }
}
```

## `src/main/java/com/carnis/mod/hallucination/HallucinationType.java`

```java
package com.carnis.mod.hallucination;

public enum HallucinationType {
    CREEPER_HISS,
    PHANTOM_FOOTSTEPS,
    WHISPER,
    FALSE_DAMAGE
}
```

## `src/main/java/com/carnis/mod/infection/PlayerInfectionManager.java`

```java
package com.carnis.mod.infection;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfection;
import com.carnis.mod.capability.infection.PlayerInfectionCapability;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModDamageSources;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.item.NeuroWeave;
import com.carnis.mod.network.ModMessages;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.UUID;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerInfectionManager {
    public static final String POINTS = "carnis:infection_points";
    public static final String METAMORPHOSED = "carnis:human_metamorphosed";
    private static final String FRACTION = "carnis:infection_fraction";
    private static final String AGONY = "carnis:infection_agony_remaining";
    private static final String TERMINAL_ATTEMPT = "carnis:terminal_attempt";
    private static final String DEATH_OBSERVED = "carnis:terminal_death_observed";
    private static final UUID SLOW_ID = UUID.fromString("048ac83b-cbb9-4f41-96c8-9f62a6db0200");
    private static final AttributeModifier SLOW = new AttributeModifier(SLOW_ID, "Carnis infection", -.10D,
            AttributeModifier.Operation.MULTIPLY_TOTAL);
    private PlayerInfectionManager() { }

    /** The integer NBT value is authoritative; fractional exposure is retained separately. */
    public static float getPoints(Player player) {
        CompoundTag data = player.getPersistentData();
        if (!data.contains(POINTS)) {
            float legacy = player.getCapability(PlayerInfectionCapability.PLAYER_INFECTION)
                    .resolve().map(cap -> cap.getInfectionLevel()).orElse(0.0F);
            writeRaw(player, legacy);
        }
        int whole = Math.max(0, Math.min(100, data.getInt(POINTS)));
        float fraction = data.getFloat(FRACTION);
        if (!Float.isFinite(fraction) || fraction < 0 || fraction >= 1 || whole == 100) fraction = 0;
        return whole + fraction;
    }
    public static int stage(float points) {
        if (points <= 0) return 0;
        if (points < 25) return 1;
        if (points < 50) return 2;
        if (points < 90) return 3;
        return 4;
    }
    public static int displayPoints(Player player) { return (int) Math.floor(getPoints(player)); }
    private static void writeRaw(Player player, float value) {
        if (!Float.isFinite(value)) value = 0;
        value = Math.max(0, Math.min(100, value));
        int whole = (int) Math.floor(value);
        player.getPersistentData().putInt(POINTS, whole);
        player.getPersistentData().putFloat(FRACTION, whole == 100 ? 0 : value - whole);
        float mirror = value;
        player.getCapability(PlayerInfectionCapability.PLAYER_INFECTION).ifPresent(cap -> {
            if (cap instanceof PlayerInfection legacy) legacy.setInfectionLevelSilently(mirror);
        });
    }
    public static boolean setPoints(Player player, float value) {
        float before = getPoints(player);
        if (!Float.isFinite(value)) return false;
        value = Math.max(0, Math.min(100, value));
        if (Float.compare(before, value) == 0) return false;
        writeRaw(player, value);
        if (value < 100) player.getPersistentData().remove(AGONY);
        if (!player.level().isClientSide) {
            updateSlow(player, stage(value) >= 2);
            if (player instanceof ServerPlayer server && ((int) Math.floor(before) != (int) Math.floor(value)
                    || stage(before) != stage(value))) ModMessages.sendPlayerInfection(server);
        }
        return true;
    }
    public static void copyToClone(Player original, Player replacement, boolean death) {
        float points = getPoints(original);
        writeRaw(replacement, points);
        replacement.getPersistentData().remove(METAMORPHOSED);
        if (!death && original.getPersistentData().contains(AGONY))
            replacement.getPersistentData().putInt(AGONY, original.getPersistentData().getInt(AGONY));
        else replacement.getPersistentData().remove(AGONY);
    }
    private static void updateSlow(Player player, boolean active) {
        AttributeInstance speed = player.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed == null) return;
        boolean present = speed.getModifier(SLOW_ID) != null;
        if (active && !present) speed.addTransientModifier(SLOW);
        else if (!active && present) speed.removeModifier(SLOW_ID);
    }
    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)) return;
        float points = getPoints(player);
        int stage = stage(points);
        updateSlow(player, player.isAlive() && stage >= 2);
        if (player.tickCount % 20 == 0) {
            ModMessages.sendPlayerInfection(player);
            if (player.isAlive() && !player.isSpectator() && stage >= 1) player.causeFoodExhaustion(.02F);
        }
        if (!player.isAlive() || player.isSpectator() || player.isCreative() || points < 100) {
            if (points < 100) player.getPersistentData().remove(AGONY);
            return;
        }
        CompoundTag data = player.getPersistentData();
        if (!data.contains(AGONY)) { data.putInt(AGONY, 100); return; }
        int remaining = data.getInt(AGONY) - 1;
        data.putInt(AGONY, remaining);
        if (remaining <= 0) metamorphose(player);
    }
    @SubscribeEvent(priority = EventPriority.NORMAL)
    public static void onHurt(LivingHurtEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof ServerPlayer player) || stage(getPoints(player)) < 3) return;
        if (NeuroArmorEventHandler.isHiveEntity(event.getSource().getEntity())) event.setAmount(event.getAmount() * .8F);
        if (event.getSource().is(DamageTypeTags.IS_FIRE)) event.setAmount(event.getAmount() * 1.5F);
    }
    private static boolean neutralAtDistance(Mob mob, Player player) {
        return stage(getPoints(player)) >= 2 && mob.distanceToSqr(player) > 144.0D;
    }
    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onTargetChange(LivingChangeTargetEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide
                || !NeuroArmorEventHandler.isHiveEntity(mob) || !(event.getNewTarget() instanceof Player player)) return;
        if (neutralAtDistance(mob, player)) event.setCanceled(true);
    }
    @SubscribeEvent
    public static void onLivingTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide
                || !NeuroArmorEventHandler.isHiveEntity(mob) || !(mob.getTarget() instanceof Player player)) return;
        if (neutralAtDistance(mob, player)) mob.setTarget(null);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onTerminalDeath(LivingDeathEvent event) {
        if (!event.isCanceled() && event.getEntity() instanceof ServerPlayer player
                && player.getPersistentData().getBoolean(TERMINAL_ATTEMPT)
                && event.getSource().is(ModDamageSources.ORGANIC_CONSUMPTION))
            player.getPersistentData().putBoolean(DEATH_OBSERVED, true);
    }
    private static void metamorphose(ServerPlayer player) {
        ServerLevel level = player.serverLevel();
        // Do not transfer equipment if vanilla keepInventory protects the player's inventory.
        boolean transfer = !level.getGameRules().getBoolean(GameRules.RULE_KEEPINVENTORY);
        ItemStack weapon = ItemStack.EMPTY, helmet = ItemStack.EMPTY;
        if (transfer) {
            ItemStack held = player.getMainHandItem();
            if (held.getItem() instanceof net.minecraft.world.item.SwordItem
                    || held.getItem() instanceof net.minecraft.world.item.AxeItem
                    || held.getItem() instanceof net.minecraft.world.item.BowItem
                    || held.getItem() instanceof net.minecraft.world.item.CrossbowItem
                    || held.getItem() instanceof net.minecraft.world.item.TridentItem) {
                weapon = held.copy();
                player.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
            }
            helmet = player.getItemBySlot(EquipmentSlot.HEAD).copy();
            player.setItemSlot(EquipmentSlot.HEAD, ItemStack.EMPTY);
        }
        CompoundTag data = player.getPersistentData();
        data.remove(DEATH_OBSERVED);
        data.putBoolean(TERMINAL_ATTEMPT, true);
        try { player.hurt(ModDamageSources.organicConsumption(level), 10000.0F); }
        finally { data.remove(TERMINAL_ATTEMPT); }
        boolean deathObserved = data.getBoolean(DEATH_OBSERVED);
        data.remove(DEATH_OBSERVED);
        if (!deathObserved || player.isAlive()) {
            restore(player, EquipmentSlot.MAINHAND, weapon);
            restore(player, EquipmentSlot.HEAD, helmet);
            player.getPersistentData().putInt(AGONY, 20);
            return;
        }
        player.getPersistentData().putBoolean(METAMORPHOSED, true);
        setPoints(player, 0);
        player.getPersistentData().remove(AGONY);
        InfectedZombieEntity clone = ModEntities.INFECTED_ZOMBIE.get().create(level);
        boolean spawned = false;
        if (clone != null) {
            clone.moveTo(player.getX(), player.getY(), player.getZ(), player.getYRot(), 0);
            clone.setPersistenceRequired();
            clone.setItemSlot(EquipmentSlot.MAINHAND, weapon);
            clone.setItemSlot(EquipmentSlot.HEAD, helmet);
            clone.setDropChance(EquipmentSlot.MAINHAND, 1.0F);
            clone.setDropChance(EquipmentSlot.HEAD, 1.0F);
            for (int[] offset : new int[][]{{0,0,0},{1,0,0},{-1,0,0},{0,0,1},{0,0,-1},{0,1,0}}) {
                BlockPos spot = player.blockPosition().offset(offset[0], offset[1], offset[2]);
                if (!level.hasChunkAt(spot) || level.isOutsideBuildHeight(spot)) continue;
                clone.moveTo(spot.getX() + .5D, spot.getY(), spot.getZ() + .5D, player.getYRot(), 0);
                if (!level.noCollision(clone)) continue;
                spawned = level.addFreshEntity(clone);
                break;
            }
        }
        if (!spawned) {
            dropAt(level, player, weapon);
            dropAt(level, player, helmet);
        }
        if (level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)) seedTissue(level, player.blockPosition());
    }
    private static void restore(ServerPlayer player, EquipmentSlot slot, ItemStack stack) {
        if (stack.isEmpty()) return;
        if (player.getItemBySlot(slot).isEmpty()) player.setItemSlot(slot, stack);
        else if (!player.getInventory().add(stack)) player.drop(stack, false);
    }
    private static void dropAt(ServerLevel level, Player player, ItemStack stack) {
        if (!stack.isEmpty()) level.addFreshEntity(new ItemEntity(level, player.getX(), player.getY(), player.getZ(), stack));
    }
    private static void seedTissue(ServerLevel level, BlockPos center) {
        BlockState remains = ModBlocks.BIOMASS_REMAINS.get().defaultBlockState();
        for (BlockPos pos : BlockPos.betweenClosed(center.offset(-1, -1, -1), center.offset(1, 1, 1))) {
            if (!level.hasChunkAt(pos) || level.isOutsideBuildHeight(pos) || !level.isEmptyBlock(pos)) continue;
            if (remains.canSurvive(level, pos) && level.setBlockAndUpdate(pos, remains)) break;
        }
        for (BlockPos pos : BlockPos.betweenClosed(center.offset(-3, -3, -3), center.offset(3, 3, 3))) {
            if (pos.distSqr(center) > 9 || level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) continue;
            BlockState state = level.getBlockState(pos);
            if (!state.isAir() || !state.getFluidState().isEmpty()) continue;
            BlockState vein = Blocks.AIR.defaultBlockState();
            for (Direction face : Direction.values()) {
                BlockPos support = pos.relative(face);
                if (!level.hasChunkAt(support) || level.isOutsideBuildHeight(support)
                        || !level.getBlockState(support).isFaceSturdy(level, support, face.getOpposite())) continue;
                BlockState next = ModBlocks.FLESH_VEINS.get().getStateForPlacement(vein, level, pos, face);
                if (next != null) vein = next;
            }
            if (vein.is(ModBlocks.FLESH_VEINS.get())) level.setBlockAndUpdate(pos, vein);
        }
    }
}
```

## `src/main/java/com/carnis/mod/init/ModArmorMaterials.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.item.NeuroArmorMaterial;
import net.minecraft.world.item.ArmorMaterial;

public final class ModArmorMaterials {
    public static final ArmorMaterial NEURO_RESONATOR = NeuroArmorMaterial.INSTANCE;
    private ModArmorMaterials() { }
}
```

## `src/main/java/com/carnis/mod/init/ModBlockEntities.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.HiveEyeBlockEntity;
import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.block.entity.SporeSproutBlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITY_TYPES =
            DeferredRegister.create(
                    ForgeRegistries.BLOCK_ENTITY_TYPES,
                    CarnisMod.MOD_ID
            );

    public static final RegistryObject<BlockEntityType<PulsingHeartBlockEntity>>
            PULSING_HEART = BLOCK_ENTITY_TYPES.register(
                    "pulsing_heart",
                    () -> BlockEntityType.Builder.of(
                            PulsingHeartBlockEntity::new,
                            ModBlocks.PULSING_HEART.get()
                    ).build(null)
            );

    public static final RegistryObject<BlockEntityType<HiveEyeBlockEntity>>
            HIVE_EYE = BLOCK_ENTITY_TYPES.register(
                    "hive_eye",
                    () -> BlockEntityType.Builder.of(
                            HiveEyeBlockEntity::new,
                            ModBlocks.HIVE_EYE.get()
                    ).build(null)
            );

    public static final RegistryObject<BlockEntityType<com.carnis.mod.block.entity.FleshBulbBlockEntity>> FLESH_BULB =
            BLOCK_ENTITY_TYPES.register("flesh_bulb", () -> BlockEntityType.Builder.of(
                    com.carnis.mod.block.entity.FleshBulbBlockEntity::new, ModBlocks.FLESH_BULB.get()).build(null));

    public static final RegistryObject<BlockEntityType<com.carnis.mod.block.entity.StomachPoolBlockEntity>> STOMACH_POOL =
            BLOCK_ENTITY_TYPES.register("stomach_pool", () -> BlockEntityType.Builder.of(com.carnis.mod.block.entity.StomachPoolBlockEntity::new, ModBlocks.STOMACH_POOL.get()).build(null));
    public static final RegistryObject<BlockEntityType<com.carnis.mod.block.entity.NervePillarBlockEntity>> NERVE_PILLAR =
            BLOCK_ENTITY_TYPES.register("nerve_pillar", () -> BlockEntityType.Builder.of(com.carnis.mod.block.entity.NervePillarBlockEntity::new, ModBlocks.NERVE_PILLAR.get()).build(null));

    public static final RegistryObject<BlockEntityType<com.carnis.mod.block.entity.PustuleClusterBlockEntity>> PUSTULE_CLUSTER =
            BLOCK_ENTITY_TYPES.register("pustule_cluster", () -> BlockEntityType.Builder.of(com.carnis.mod.block.entity.PustuleClusterBlockEntity::new, ModBlocks.PUSTULE_CLUSTER.get()).build(null));

    public static final RegistryObject<BlockEntityType<SporeSproutBlockEntity>> SPORE_SPROUT =
            BLOCK_ENTITY_TYPES.register("spore_sprout", () -> BlockEntityType.Builder.of(
                    SporeSproutBlockEntity::new, ModBlocks.SPORE_SPROUT.get()).build(null));

    private ModBlockEntities() {
    }

    public static void register(IEventBus modEventBus) {
        BLOCK_ENTITY_TYPES.register(modEventBus);
    }
}
```

## `src/main/java/com/carnis/mod/init/ModBlockTags.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.Block;

public final class ModBlockTags {
    public static final TagKey<Block> HIVE_BLOCKS = TagKey.create(
            Registries.BLOCK,
            new ResourceLocation(CarnisMod.MOD_ID, "hive_blocks")
    );

    public static final TagKey<Block> INFECTIOUS_SURFACES = TagKey.create(
            Registries.BLOCK,
            new ResourceLocation(CarnisMod.MOD_ID, "infectious_surfaces")
    );

    private ModBlockTags() {
    }
}
```

## `src/main/java/com/carnis/mod/init/ModBlocks.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.FleshBlock;
import com.carnis.mod.block.NervePillarBlock;
import com.carnis.mod.block.CreepingTendrilsBlock;
import com.carnis.mod.block.PustuleClusterBlock;
import com.carnis.mod.block.StomachPoolBlock;
import com.carnis.mod.block.SporeSproutBlock;
import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.block.HiveEyeBlock;
import com.carnis.mod.block.PulsingHeartBlock;
import com.carnis.mod.block.HiveMembraneBlock;
import com.carnis.mod.block.SynapseNodeBlock;
import com.carnis.mod.block.IncubationCystBlock;
import com.carnis.mod.block.PurifierLampBlock;
import com.carnis.mod.sound.CarnisSoundTypes;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, CarnisMod.MOD_ID);

    public static final RegistryObject<com.carnis.mod.fluid.TaintedSludgeBlock> TAINTED_SLUDGE = BLOCKS.register(
            "tainted_sludge", () -> new com.carnis.mod.fluid.TaintedSludgeBlock(
                    BlockBehaviour.Properties.copy(Blocks.WATER).noLootTable()
                            .sound(CarnisSoundTypes.organic())));

    public static final RegistryObject<com.carnis.mod.block.FleshVeinsBlock> FLESH_VEINS = BLOCKS.register(
            "flesh_veins", () -> new com.carnis.mod.block.FleshVeinsBlock(
                    BlockBehaviour.Properties.copy(Blocks.GLOW_LICHEN).randomTicks()
                            .sound(CarnisSoundTypes.organic())));

    public static final RegistryObject<Block> BIOMASS_REMAINS = BLOCKS.register("biomass_remains",
            () -> new com.carnis.mod.block.BiomassRemainsBlock(BlockBehaviour.Properties.of()
                    .noCollission().noOcclusion().strength(0.2F).sound(CarnisSoundTypes.organic())));

    public static final RegistryObject<Block> FLESH_BULB = BLOCKS.register("flesh_bulb",
            () -> new com.carnis.mod.block.FleshBulbBlock(BlockBehaviour.Properties.copy(Blocks.CRIMSON_ROOTS)
                    .noCollission().noOcclusion().sound(CarnisSoundTypes.organic())));
    public static final RegistryObject<Block> SINEW_SPIKES = BLOCKS.register("sinew_spikes",
            () -> new com.carnis.mod.block.SinewSpikesBlock(BlockBehaviour.Properties.copy(Blocks.STONE)
                    .noOcclusion().strength(0.5F).sound(CarnisSoundTypes.organic())));

    public static final RegistryObject<Block> NERVE_PILLAR = BLOCKS.register(
            "nerve_pillar", () -> new NervePillarBlock(BlockBehaviour.Properties.of()
                    .noOcclusion().strength(2.0F).sound(CarnisSoundTypes.organic()).randomTicks()));

    public static final RegistryObject<Block> CREEPING_TENDRILS = BLOCKS.register(
            "creeping_tendrils", () -> new CreepingTendrilsBlock(
                    BlockBehaviour.Properties.copy(Blocks.LADDER).sound(CarnisSoundTypes.organic())));
    public static final RegistryObject<Block> PUSTULE_CLUSTER = BLOCKS.register(
            "pustule_cluster", () -> new PustuleClusterBlock(BlockBehaviour.Properties.of()
                    .noOcclusion().strength(0.5F).sound(CarnisSoundTypes.organic()).randomTicks()
                    .lightLevel(state -> !state.getValue(PustuleClusterBlock.BURST)
                            && state.getValue(PustuleClusterBlock.AGE) == 3 ? 5 : 0)));
    public static final RegistryObject<Block> STOMACH_POOL = BLOCKS.register(
            "stomach_pool", () -> new StomachPoolBlock(BlockBehaviour.Properties.of()
                    .noOcclusion().strength(0.5F).sound(CarnisSoundTypes.organic()).randomTicks()));

    public static final RegistryObject<Block> SPORE_SPROUT = BLOCKS.register(
            "spore_sprout", () -> new SporeSproutBlock(
                    BlockBehaviour.Properties.copy(Blocks.STONE).noOcclusion().strength(0.2F)
                            .sound(CarnisSoundTypes.organic())));
    public static final RegistryObject<Block> NEURAL_MOSS = BLOCKS.register(
            "neural_moss", () -> new NeuralMossBlock(
                    BlockBehaviour.Properties.copy(Blocks.MOSS_CARPET).randomTicks()
                            .sound(CarnisSoundTypes.organic())));

    public static final RegistryObject<Block> CHARRED_FLESH = BLOCKS.register(
            "charred_flesh",
            () -> new Block(BlockBehaviour.Properties.copy(Blocks.BASALT).strength(1.5F)
                    .sound(CarnisSoundTypes.organic()))
    );

    public static final RegistryObject<Block> LIVING_FLESH = BLOCKS.register(
            "living_flesh",
            () -> new FleshBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_RED)
                    .strength(0.8F, 1.5F)
                    .sound(CarnisSoundTypes.organic())
                    .randomTicks())
    );

    public static final RegistryObject<Block> OSSIFIED_FLESH = BLOCKS.register(
            "ossified_flesh",
            () -> new FleshBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.SAND)
                    .strength(3.0F, 6.0F)
                    .sound(CarnisSoundTypes.organic())
                    .requiresCorrectToolForDrops()
                    .randomTicks())
    );

    public static final RegistryObject<Block> FIREPROOF_FLESH = BLOCKS.register(
            "fireproof_flesh",
            () -> new FleshBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_BLACK)
                    .strength(4.0F, 12.0F)
                    .sound(CarnisSoundTypes.organic())
                    .requiresCorrectToolForDrops()
                    .randomTicks())
    );

    public static final RegistryObject<Block> PULSING_HEART = BLOCKS.register(
            "pulsing_heart",
            () -> new PulsingHeartBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_RED)
                    .strength(2.5F, 6.0F)
                    .sound(CarnisSoundTypes.organic())
                    .lightLevel(state -> 9)
                    .noOcclusion())
    );

    public static final RegistryObject<Block> HIVE_EYE = BLOCKS.register(
            "hive_eye",
            () -> new HiveEyeBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_RED)
                    .strength(1.6F, 3.0F)
                    .sound(CarnisSoundTypes.organic())
                    .lightLevel(state -> 6))
    );


    public static final RegistryObject<Block> HIVE_MEMBRANE = BLOCKS.register("hive_membrane",
            () -> new HiveMembraneBlock(BlockBehaviour.Properties.copy(Blocks.RED_WOOL)
                    .strength(1.2F).sound(CarnisSoundTypes.membrane())));
    public static final RegistryObject<Block> SYNAPSE_NODE = BLOCKS.register("synapse_node",
            () -> new SynapseNodeBlock(BlockBehaviour.Properties.copy(Blocks.REDSTONE_LAMP)
                    .strength(1.5F).sound(CarnisSoundTypes.organic())));
    public static final RegistryObject<Block> INCUBATION_CYST = BLOCKS.register("incubation_cyst",
            () -> new IncubationCystBlock(BlockBehaviour.Properties.copy(Blocks.NETHER_WART_BLOCK)
                    .strength(0.6F).noOcclusion().sound(CarnisSoundTypes.organic()).lightLevel(state -> 2)));
    public static final RegistryObject<Block> PURIFIER_LAMP = BLOCKS.register("purifier_lamp",
            () -> new PurifierLampBlock(BlockBehaviour.Properties.copy(Blocks.LANTERN)
                    .strength(1.5F).lightLevel(state -> 15).sound(net.minecraft.world.level.block.SoundType.LANTERN)));

    private ModBlocks() {
    }

    public static void register(IEventBus modEventBus) {
        BLOCKS.register(modEventBus);
    }
}
```

## `src/main/java/com/carnis/mod/init/ModCreativeTabs.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, CarnisMod.MOD_ID);
    public static final RegistryObject<CreativeModeTab> CARNIS_TAB = CREATIVE_TABS.register("carnis", () ->
            CreativeModeTab.builder().title(Component.translatable("carnis.tab"))
                    .icon(() -> ModItems.PULSING_HEART.get().getDefaultInstance())
                    .displayItems((parameters, output) -> {
                        output.accept(ModItems.HIVE_MEMBRANE.get());
                        output.accept(ModItems.SYNAPSE_NODE.get());
                        output.accept(ModItems.INCUBATION_CYST.get());
                        output.accept(ModItems.PURIFIER_LAMP.get());
                        output.accept(ModItems.SINEW_SHIELD.get());
                        output.accept(ModItems.BONE_SCYTHE.get());
                        output.accept(ModItems.OSSIFIED_SCYTHE.get());
                        output.accept(ModItems.PUSTULE_GRENADE.get());
                        output.accept(ModItems.PURIFICATION_VIAL.get());
                        // Organs and cores
                        output.accept(ModItems.PULSING_HEART.get());
                        output.accept(ModItems.HIVE_EYE.get());
                        output.accept(ModItems.STOMACH_POOL.get());
                        output.accept(ModItems.NERVE_PILLAR.get());
                        // Tissues and flora
                        output.accept(ModItems.LIVING_FLESH.get());
                        output.accept(ModItems.OSSIFIED_FLESH.get());
                        output.accept(ModItems.CHARRED_FLESH.get());
                        output.accept(ModItems.FIREPROOF_FLESH.get());
                        output.accept(ModItems.FLESH_VEINS.get());
                        output.accept(ModItems.NEURAL_MOSS.get());
                        output.accept(ModItems.SINEW_SPIKES.get());
                        output.accept(ModItems.PUSTULE_CLUSTER.get());
                        output.accept(ModItems.SPORE_SPROUT.get());
                        output.accept(ModItems.FLESH_BULB.get());
                        output.accept(ModItems.BIOMASS_REMAINS.get());
                        // Field equipment
                        output.accept(ModItems.RESEARCH_JOURNAL.get());
                        output.accept(ModItems.BIO_PURIFIER.get());
                        output.accept(ModItems.PNEUMATIC_INOCULATOR.get());
                        output.accept(ModItems.PURIFICATION_SERUM.get());
                        output.accept(ModItems.PURIFICATION_DART.get());
                        output.accept(ModItems.VIRAL_DART.get());
                        output.accept(ModItems.NEURAL_BINDING_MATRIX.get());
                        // Neuro-resonator armor
                        output.accept(ModItems.NEURO_RESONATOR_HELMET.get());
                        output.accept(ModItems.NEURO_RESONATOR_CHESTPLATE.get());
                        output.accept(ModItems.NEURO_RESONATOR_LEGGINGS.get());
                        output.accept(ModItems.NEURO_RESONATOR_BOOTS.get());
                        // Materials
                        output.accept(ModItems.CREEPING_TENDRILS.get());
                        output.accept(ModItems.TAINTED_SLUDGE_BUCKET.get());
                        // Spawn eggs
                        output.accept(ModItems.INFECTED_ZOMBIE_SPAWN_EGG.get());
                        output.accept(ModItems.INFECTED_SKELETON_SPAWN_EGG.get());
                        output.accept(ModItems.INFECTED_CREEPER_SPAWN_EGG.get());
                        output.accept(ModItems.BIOMASS_MAGGOT_SPAWN_EGG.get());
                        output.accept(ModItems.PARASITIC_TENDRIL_SPAWN_EGG.get());
                        output.accept(ModItems.FLESH_AMALGAM_SPAWN_EGG.get());
                        output.accept(ModItems.HIVE_SENTINEL_SPAWN_EGG.get());
                        output.accept(ModItems.CEREBRAL_NEXUS_SPAWN_EGG.get());
                        // Existing additional items remain accessible.
                        output.accept(ModItems.INFECTED_SPIDER_SPAWN_EGG.get());
                        output.accept(ModItems.ANTIBIOTICS.get());
                        output.accept(ModItems.BONE_SCYTHE_ARM.get());
                        output.accept(ModItems.FLESH_SPAT.get());
                        output.accept(ModItems.AMALGAM_BILE_GLOB.get());
                    }).build());
    private ModCreativeTabs() { }
    public static void register(IEventBus modEventBus) { CREATIVE_TABS.register(modEventBus); }
}
```

## `src/main/java/com/carnis/mod/init/ModDamageSources.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.level.Level;

public final class ModDamageSources {
    public static final ResourceKey<DamageType> ORGANIC_CONSUMPTION = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "organic_consumption"));
    private ModDamageSources() { }
    public static DamageSource organicConsumption(Level level) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(ORGANIC_CONSUMPTION));
    }
}
```

## `src/main/java/com/carnis/mod/init/ModDamageTypes.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;

import java.util.Objects;

public final class ModDamageTypes {
    public static final ResourceKey<DamageType> BIO_PURIFIER =
            ResourceKey.create(
                    Registries.DAMAGE_TYPE,
                    new ResourceLocation(CarnisMod.MOD_ID, "bio_purifier")
            );

    public static final ResourceKey<DamageType> BIO_PURIFIER_SURFACE = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "bio_purifier_surface"));

    public static DamageSource bioPurifierSurface(Level level, Entity wielder) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(BIO_PURIFIER_SURFACE), wielder, wielder);
    }

    public static final ResourceKey<DamageType> NECROTIC_CONSUMPTION = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "necrotic_consumption"));

    public static DamageSource necroticConsumption(Level level) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(NECROTIC_CONSUMPTION));
    }

    public static final ResourceKey<DamageType> TAINTED_SLUDGE = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "tainted_sludge"));

    public static DamageSource taintedSludge(Level level) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(TAINTED_SLUDGE));
    }

    public static final ResourceKey<DamageType> PURIFICATION_DART = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "purification_dart"));

    public static DamageSource purificationDart(Level level, Entity projectile, Entity shooter) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(PURIFICATION_DART), projectile, shooter);
    }

    private ModDamageTypes() {
    }

    public static DamageSource bioPurifier(Level level, Entity wielder) {
        Objects.requireNonNull(level, "level");
        Objects.requireNonNull(wielder, "wielder");

        Registry<DamageType> damageTypes = level.registryAccess()
                .registryOrThrow(Registries.DAMAGE_TYPE);

        return new DamageSource(
                damageTypes.getHolderOrThrow(BIO_PURIFIER),
                wielder,
                wielder
        );
    }
}
```

## `src/main/java/com/carnis/mod/init/ModEffects.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.effect.ImmunosuppressionMobEffect;
import com.carnis.mod.effect.IncubatingMobEffect;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEffects {
    public static final DeferredRegister<MobEffect> EFFECTS =
            DeferredRegister.create(ForgeRegistries.MOB_EFFECTS, CarnisMod.MOD_ID);
    public static final RegistryObject<MobEffect> INCUBATING = EFFECTS.register("incubating", () ->
            new IncubatingMobEffect());
    public static final RegistryObject<MobEffect> THERMAL_SHOCK = EFFECTS.register("thermal_shock",
            com.carnis.mod.effect.ThermalShockEffect::new);
    public static final RegistryObject<MobEffect> IMMUNOSUPPRESSION = EFFECTS.register(
            "immunosuppression", ImmunosuppressionMobEffect::new);

    private ModEffects() { }
    public static void register(IEventBus bus) { EFFECTS.register(bus); }
}
```

## `src/main/java/com/carnis/mod/init/ModEntities.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedCreeperEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;

import com.carnis.mod.entity.ViralDartEntity;
import com.carnis.mod.entity.PurificationDartEntity;
import com.carnis.mod.entity.PustuleGrenadeEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, CarnisMod.MOD_ID);

    public static final RegistryObject<EntityType<com.carnis.mod.entity.HiveSentinelEntity>> HIVE_SENTINEL = ENTITY_TYPES.register(
            "hive_sentinel", () -> EntityType.Builder.<com.carnis.mod.entity.HiveSentinelEntity>of(
                    com.carnis.mod.entity.HiveSentinelEntity::new, MobCategory.MONSTER)
                    .sized(0.9F, 1.8F).clientTrackingRange(8).build("carnis:hive_sentinel"));
    public static final RegistryObject<EntityType<com.carnis.mod.entity.CerebralNexusEntity>> CEREBRAL_NEXUS = ENTITY_TYPES.register(
            "cerebral_nexus", () -> EntityType.Builder.<com.carnis.mod.entity.CerebralNexusEntity>of(
                    com.carnis.mod.entity.CerebralNexusEntity::new, MobCategory.MONSTER)
                    .sized(1.3F, 2.2F).clientTrackingRange(10).build("carnis:cerebral_nexus"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.ParasiticTendrilEntity>> PARASITIC_TENDRIL = ENTITY_TYPES.register(
            "parasitic_tendril", () -> EntityType.Builder.<com.carnis.mod.entity.ParasiticTendrilEntity>of(
                    com.carnis.mod.entity.ParasiticTendrilEntity::new, MobCategory.MONSTER)
                    .sized(0.5F, 1.2F).clientTrackingRange(8).build("carnis:parasitic_tendril"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.BiomassMaggotEntity>> BIOMASS_MAGGOT =
            ENTITY_TYPES.register("biomass_maggot", () -> EntityType.Builder
                    .<com.carnis.mod.entity.BiomassMaggotEntity>of(com.carnis.mod.entity.BiomassMaggotEntity::new, MobCategory.MONSTER)
                    .sized(0.55F, 0.35F).clientTrackingRange(8).build("carnis:biomass_maggot"));

    public static final RegistryObject<EntityType<InfectedZombieEntity>> INFECTED_ZOMBIE = ENTITY_TYPES.register(
            "infected_zombie", () -> EntityType.Builder.<InfectedZombieEntity>of(InfectedZombieEntity::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.95F).clientTrackingRange(8).build("carnis:infected_zombie"));

    public static final RegistryObject<EntityType<InfectedSkeletonEntity>> INFECTED_SKELETON = ENTITY_TYPES.register(
            "infected_skeleton", () -> EntityType.Builder.<InfectedSkeletonEntity>of(InfectedSkeletonEntity::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.99F).clientTrackingRange(8).build("carnis:infected_skeleton"));
    public static final RegistryObject<EntityType<InfectedCreeperEntity>> INFECTED_CREEPER = ENTITY_TYPES.register(
            "infected_creeper", () -> EntityType.Builder.<InfectedCreeperEntity>of(InfectedCreeperEntity::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.7F).clientTrackingRange(8).build("carnis:infected_creeper"));
    public static final RegistryObject<EntityType<InfectedSpiderEntity>> INFECTED_SPIDER = ENTITY_TYPES.register(
            "infected_spider", () -> EntityType.Builder.<InfectedSpiderEntity>of(InfectedSpiderEntity::new, MobCategory.MONSTER)
                    .sized(1.4F, 0.9F).clientTrackingRange(8).build("carnis:infected_spider"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.FleshSpatProjectileEntity>> FLESH_SPAT = ENTITY_TYPES.register(
            "flesh_spat", () -> EntityType.Builder.<com.carnis.mod.entity.FleshSpatProjectileEntity>of(
                    com.carnis.mod.entity.FleshSpatProjectileEntity::new, MobCategory.MISC)
                    .sized(0.25F, 0.25F).clientTrackingRange(4).updateInterval(1).build("carnis:flesh_spat"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.AmalgamBileProjectile>> AMALGAM_BILE = ENTITY_TYPES.register(
            "amalgam_bile", () -> EntityType.Builder.<com.carnis.mod.entity.AmalgamBileProjectile>of(
                    com.carnis.mod.entity.AmalgamBileProjectile::new, MobCategory.MISC)
                    .sized(0.25F, 0.25F).clientTrackingRange(8).updateInterval(1).build("carnis:amalgam_bile"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.HiveSporeCloudEntity>> HIVE_SPORE_CLOUD = ENTITY_TYPES.register(
            "hive_spore_cloud", () -> EntityType.Builder.<com.carnis.mod.entity.HiveSporeCloudEntity>of(
                    com.carnis.mod.entity.HiveSporeCloudEntity::new, MobCategory.MISC)
                    .sized(6F, 0.5F).clientTrackingRange(10).updateInterval(10).build("carnis:hive_spore_cloud"));

    public static final RegistryObject<EntityType<com.carnis.mod.entity.projectile.InoculatorDartEntity>> INOCULATOR_DART = ENTITY_TYPES.register(
            "inoculator_dart", () -> EntityType.Builder.<com.carnis.mod.entity.projectile.InoculatorDartEntity>of(
                    com.carnis.mod.entity.projectile.InoculatorDartEntity::new, MobCategory.MISC)
                    .sized(0.5F, 0.5F).clientTrackingRange(8).updateInterval(1).build("carnis:inoculator_dart"));

    public static final RegistryObject<EntityType<ViralDartEntity>> VIRAL_DART = ENTITY_TYPES.register(
            "viral_dart", () -> EntityType.Builder.<ViralDartEntity>of(ViralDartEntity::new, MobCategory.MISC)
                    .sized(0.5F, 0.5F).clientTrackingRange(4).updateInterval(1).build("carnis:viral_dart"));
    public static final RegistryObject<EntityType<PurificationDartEntity>> PURIFICATION_DART = ENTITY_TYPES.register(
            "purification_dart", () -> EntityType.Builder.<PurificationDartEntity>of(PurificationDartEntity::new, MobCategory.MISC)
                    .sized(0.5F, 0.5F).clientTrackingRange(4).updateInterval(1).build("carnis:purification_dart"));


    public static final RegistryObject<EntityType<PustuleGrenadeEntity>> PUSTULE_GRENADE = ENTITY_TYPES.register(
            "pustule_grenade", () -> EntityType.Builder.<PustuleGrenadeEntity>of(
                    PustuleGrenadeEntity::new, MobCategory.MISC)
                    .sized(0.25F, 0.25F).clientTrackingRange(4).updateInterval(10)
                    .build("carnis:pustule_grenade"));

    public static final RegistryObject<EntityType<FleshAmalgamEntity>>
            FLESH_AMALGAM = ENTITY_TYPES.register(
                    "flesh_amalgam",
                    () -> EntityType.Builder.of(
                                    FleshAmalgamEntity::new,
                                    MobCategory.MONSTER
                            )
                            .sized(1.4F, 2.75F)
                            .clientTrackingRange(10)
                            .updateInterval(3)
                            .build(new ResourceLocation(
                                    CarnisMod.MOD_ID,
                                    "flesh_amalgam"
                            ).toString())
            );

    /** Register this method from the existing MOD-bus ModEntityEvents subscriber. */
    public static void registerSpawnPlacements(SpawnPlacementRegisterEvent event) {
        event.register(PARASITIC_TENDRIL.get(), SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, ModEntities::canSpawnTendril,
                SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(INFECTED_ZOMBIE.get(), SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, ModEntities::canSpawnInfectedZombie,
                SpawnPlacementRegisterEvent.Operation.REPLACE);
    }

    public static boolean canSpawnTendril(
            EntityType<com.carnis.mod.entity.ParasiticTendrilEntity> type,
            ServerLevelAccessor level, MobSpawnType reason, BlockPos pos, RandomSource random) {
        long dayTime = Math.floorMod(level.getLevel().getDayTime(), 24000L);
        return dayTime >= 13000L && dayTime < 23000L
                && level.getMaxLocalRawBrightness(pos) <= 7
                && level.getBlockState(pos.below()).is(BlockTags.ANIMALS_SPAWNABLE_ON);
    }

    public static boolean canSpawnInfectedZombie(
            EntityType<com.carnis.mod.entity.InfectedZombieEntity> type,
            ServerLevelAccessor level, MobSpawnType reason, BlockPos pos, RandomSource random) {
        if (level.getMaxLocalRawBrightness(pos) > 7) return false;
        if (!level.getBlockState(pos.below()).isSolidRender(level, pos.below())) return false;
        return com.carnis.mod.event.ChunkInfectionEvents.infectedChunk(
                level.getLevel(), new net.minecraft.world.level.ChunkPos(pos));
    }

    private ModEntities() {
    }

    public static void register(IEventBus modEventBus) {
        ENTITY_TYPES.register(modEventBus);
    }
}
```

## `src/main/java/com/carnis/mod/init/ModFeatures.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.world.GestationCystFeature;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModFeatures {
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(Registries.FEATURE, CarnisMod.MOD_ID);
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> GESTATION_CYST =
            FEATURES.register("gestation_cyst", GestationCystFeature::new);
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> FLESH_NEST =
            FEATURES.register("flesh_nest", com.carnis.mod.world.feature.FleshNestFeature::new);
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> SPORE_POCKET =
            FEATURES.register("spore_pocket", com.carnis.mod.world.feature.SporePocketFeature::new);

    private ModFeatures() {
    }

    public static void register(IEventBus bus) {
        FEATURES.register(bus);
    }
}
```

## `src/main/java/com/carnis/mod/init/ModFluids.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.fluid.TaintedSludgeFluid;
import com.carnis.mod.fluid.TaintedSludgeType;
import net.minecraft.world.level.material.Fluid;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fluids.FluidType;
import net.minecraftforge.fluids.ForgeFlowingFluid;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModFluids {
    public static final DeferredRegister<FluidType> TYPES = DeferredRegister.create(ForgeRegistries.Keys.FLUID_TYPES, CarnisMod.MOD_ID);
    public static final DeferredRegister<Fluid> FLUIDS = DeferredRegister.create(ForgeRegistries.FLUIDS, CarnisMod.MOD_ID);
    public static final RegistryObject<FluidType> SLUDGE_TYPE = TYPES.register("tainted_sludge", TaintedSludgeType::new);
    public static final RegistryObject<ForgeFlowingFluid> SLUDGE_SOURCE = FLUIDS.register("tainted_sludge", TaintedSludgeFluid.Source::new);
    public static final RegistryObject<ForgeFlowingFluid> SLUDGE_FLOWING = FLUIDS.register("flowing_tainted_sludge", TaintedSludgeFluid.Flowing::new);

    public static ForgeFlowingFluid.Properties properties() {
        return new ForgeFlowingFluid.Properties(SLUDGE_TYPE, SLUDGE_SOURCE, SLUDGE_FLOWING)
                .block(ModBlocks.TAINTED_SLUDGE).bucket(ModItems.TAINTED_SLUDGE_BUCKET)
                .tickRate(20).slopeFindDistance(3).levelDecreasePerBlock(2);
    }
    private ModFluids() { }
    public static void register(IEventBus bus) { TYPES.register(bus); FLUIDS.register(bus); }
}
```

## `src/main/java/com/carnis/mod/init/ModItems.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.item.BioPurifierItem;
import com.carnis.mod.item.NeuroResonatorArmorItem;
import net.minecraft.world.item.ArmorItem;
import com.carnis.mod.item.PneumaticInoculatorItem;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.item.PurificationSerumItem;
import com.carnis.mod.item.SinewShieldItem;
import com.carnis.mod.item.OssifiedScytheItem;
import com.carnis.mod.item.PustuleGrenadeItem;
import com.carnis.mod.item.PurificationVialItem;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, CarnisMod.MOD_ID);

    public static final RegistryObject<Item> BIOMASS_REMAINS = ITEMS.register("biomass_remains",
            () -> new BlockItem(ModBlocks.BIOMASS_REMAINS.get(), new Item.Properties()));

    public static final RegistryObject<Item> FLESH_BULB = ITEMS.register("flesh_bulb",
            () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.FLESH_BULB.get(), new Item.Properties(), "flesh_bulb"));
    public static final RegistryObject<Item> SINEW_SPIKES = ITEMS.register("sinew_spikes",
            () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.SINEW_SPIKES.get(), new Item.Properties(), "sinew_spikes"));
    public static final RegistryObject<ForgeSpawnEggItem> PARASITIC_TENDRIL_SPAWN_EGG = ITEMS.register(
            "parasitic_tendril_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.PARASITIC_TENDRIL,
                    0xFFFFFF, 0xd8a178, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> HIVE_SENTINEL_SPAWN_EGG = ITEMS.register(
            "hive_sentinel_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.HIVE_SENTINEL,
                    0xFFFFFF, 0x99ca75, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> CEREBRAL_NEXUS_SPAWN_EGG = ITEMS.register(
            "cerebral_nexus_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.CEREBRAL_NEXUS,
                    0xFFFFFF, 0xd78c7b, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> BIOMASS_MAGGOT_SPAWN_EGG = ITEMS.register(
            "biomass_maggot_spawn_egg", () -> new com.carnis.mod.item.MaggotSpawnEggItem(ModEntities.BIOMASS_MAGGOT,
                    0x60202c, 0xc99d79, new Item.Properties()));

    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_ZOMBIE_SPAWN_EGG = ITEMS.register(
            "infected_zombie_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_ZOMBIE,
                    0x552d31, 0x8c9c54, new Item.Properties()));

    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_SKELETON_SPAWN_EGG = ITEMS.register(
            "infected_skeleton_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_SKELETON, 0x552d31, 0xc7b9a6, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_CREEPER_SPAWN_EGG = ITEMS.register(
            "infected_creeper_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_CREEPER, 0x552d31, 0x668b45, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_SPIDER_SPAWN_EGG = ITEMS.register(
            "infected_spider_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_SPIDER, 0x552d31, 0x654643, new Item.Properties()));

    public static final RegistryObject<net.minecraft.world.item.BucketItem> TAINTED_SLUDGE_BUCKET = ITEMS.register(
            "tainted_sludge_bucket", () -> new net.minecraft.world.item.BucketItem(ModFluids.SLUDGE_SOURCE,
                    new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1)));
    public static final RegistryObject<com.carnis.mod.item.CodexCarnisItem> RESEARCH_JOURNAL = ITEMS.register(
            "research_journal", () -> new com.carnis.mod.item.CodexCarnisItem(new Item.Properties()));
    public static final RegistryObject<Item> AMALGAM_BILE_GLOB = ITEMS.register("amalgam_bile_glob", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> FLESH_SPAT = ITEMS.register("flesh_spat", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> BONE_SCYTHE_ARM = ITEMS.register("bone_scythe_arm",
            () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> FLESH_VEINS = ITEMS.register("flesh_veins",
            () -> new BlockItem(ModBlocks.FLESH_VEINS.get(), new Item.Properties()));

    public static final RegistryObject<com.carnis.mod.item.AntibioticsItem> ANTIBIOTICS = ITEMS.register("antibiotics",
            () -> new com.carnis.mod.item.AntibioticsItem(new Item.Properties().stacksTo(16)));

    public static final RegistryObject<Item> NEURAL_BINDING_MATRIX = ITEMS.register(
            "neural_binding_matrix", () -> new Item(new Item.Properties()));
    public static final RegistryObject<NeuroResonatorArmorItem> NEURO_RESONATOR_CHESTPLATE = ITEMS.register(
            "neuro_resonator_chestplate", () -> new NeuroResonatorArmorItem(ArmorItem.Type.CHESTPLATE, new Item.Properties()));
    public static final RegistryObject<NeuroResonatorArmorItem> NEURO_RESONATOR_LEGGINGS = ITEMS.register(
            "neuro_resonator_leggings", () -> new NeuroResonatorArmorItem(ArmorItem.Type.LEGGINGS, new Item.Properties()));
    public static final RegistryObject<NeuroResonatorArmorItem> NEURO_RESONATOR_BOOTS = ITEMS.register(
            "neuro_resonator_boots", () -> new NeuroResonatorArmorItem(ArmorItem.Type.BOOTS, new Item.Properties()));

    public static final RegistryObject<Item> NERVE_PILLAR = ITEMS.register("nerve_pillar",
            () -> new com.carnis.mod.item.OrganBlockItem(ModBlocks.NERVE_PILLAR.get(), new Item.Properties()));
    public static final RegistryObject<Item> VIRAL_DART = ITEMS.register("viral_dart",
            () -> new com.carnis.mod.item.ViralDartItem(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<Item> PURIFICATION_DART = ITEMS.register("purification_dart",
            () -> new com.carnis.mod.item.PurificationDartItem(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<PneumaticInoculatorItem> PNEUMATIC_INOCULATOR = ITEMS.register(
            "pneumatic_inoculator", () -> new PneumaticInoculatorItem(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> CREEPING_TENDRILS = ITEMS.register(
            "creeping_tendrils", () -> new BlockItem(ModBlocks.CREEPING_TENDRILS.get(), new Item.Properties()));
    public static final RegistryObject<Item> PUSTULE_CLUSTER = ITEMS.register(
            "pustule_cluster", () -> new com.carnis.mod.item.OrganBlockItem(ModBlocks.PUSTULE_CLUSTER.get(), new Item.Properties()));
    public static final RegistryObject<Item> STOMACH_POOL = ITEMS.register(
            "stomach_pool", () -> new com.carnis.mod.item.OrganBlockItem(ModBlocks.STOMACH_POOL.get(), new Item.Properties()));

    public static final RegistryObject<Item> SPORE_SPROUT = ITEMS.register(
            "spore_sprout", () -> new BlockItem(ModBlocks.SPORE_SPROUT.get(), new Item.Properties()));
    public static final RegistryObject<Item> NEURAL_MOSS = ITEMS.register(
            "neural_moss", () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.NEURAL_MOSS.get(), new Item.Properties(), "neural_moss"));

    public static final RegistryObject<Item> CHARRED_FLESH = ITEMS.register(
            "charred_flesh",
            () -> new BlockItem(ModBlocks.CHARRED_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> LIVING_FLESH = ITEMS.register(
            "living_flesh",
            () -> new BlockItem(ModBlocks.LIVING_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> OSSIFIED_FLESH = ITEMS.register(
            "ossified_flesh",
            () -> new BlockItem(ModBlocks.OSSIFIED_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> FIREPROOF_FLESH = ITEMS.register(
            "fireproof_flesh",
            () -> new BlockItem(ModBlocks.FIREPROOF_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> PULSING_HEART = ITEMS.register(
            "pulsing_heart",
            () -> new com.carnis.mod.item.PulsingHeartItem(
                    ModBlocks.PULSING_HEART.get(),
                    new Item.Properties()
            )
    );

    public static final RegistryObject<Item> HIVE_EYE = ITEMS.register(
            "hive_eye",
            () -> new com.carnis.mod.item.HiveEyeItem(
                    ModBlocks.HIVE_EYE.get(),
                    new Item.Properties()
            )
    );


    public static final RegistryObject<Item> HIVE_MEMBRANE = ITEMS.register("hive_membrane",
            () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.HIVE_MEMBRANE.get(), new Item.Properties(), "hive_membrane"));
    public static final RegistryObject<Item> SYNAPSE_NODE = ITEMS.register("synapse_node",
            () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.SYNAPSE_NODE.get(), new Item.Properties(), "synapse_node"));
    public static final RegistryObject<Item> INCUBATION_CYST = ITEMS.register("incubation_cyst",
            () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.INCUBATION_CYST.get(), new Item.Properties(), "incubation_cyst"));
    public static final RegistryObject<Item> PURIFIER_LAMP = ITEMS.register("purifier_lamp",
            () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.PURIFIER_LAMP.get(), new Item.Properties(), "purifier_lamp"));
    public static final RegistryObject<Item> SINEW_SHIELD = ITEMS.register("sinew_shield",
            () -> new SinewShieldItem(new Item.Properties().durability(336)));
    public static final RegistryObject<Item> BONE_SCYTHE = ITEMS.register("bone_scythe",
            () -> new net.minecraft.world.item.SwordItem(Tiers.STONE, 2, -2.4F,
                    new Item.Properties().durability(180)));
    public static final RegistryObject<Item> OSSIFIED_SCYTHE = ITEMS.register("ossified_scythe",
            () -> new OssifiedScytheItem(Tiers.IRON, 5, -2.4F,
                    new Item.Properties().durability(650)));
    public static final RegistryObject<Item> PUSTULE_GRENADE = ITEMS.register("pustule_grenade",
            () -> new PustuleGrenadeItem(new Item.Properties().stacksTo(16)));
    public static final RegistryObject<Item> PURIFICATION_VIAL = ITEMS.register("purification_vial",
            () -> new PurificationVialItem(new Item.Properties().stacksTo(16)));

    public static final RegistryObject<ForgeSpawnEggItem>
            FLESH_AMALGAM_SPAWN_EGG = ITEMS.register(
                    "flesh_amalgam_spawn_egg",
                    () -> new ForgeSpawnEggItem(
                            ModEntities.FLESH_AMALGAM,
                            0x6F1B31,
                            0xD98B76,
                            new Item.Properties()
                    )
            );

    public static final RegistryObject<PurificationSerumItem>
            PURIFICATION_SERUM = ITEMS.register(
                    "purification_serum",
                    () -> new PurificationSerumItem(
                            new Item.Properties()
                                    .stacksTo(16)
                                    .craftRemainder(Items.GLASS_BOTTLE)
                                    .rarity(Rarity.UNCOMMON)
                    )
            );

    public static final RegistryObject<BioPurifierItem>
            BIO_PURIFIER = ITEMS.register(
                    "bio_purifier",
                    () -> new BioPurifierItem(
                            new Item.Properties()
                                    .durability(BioPurifierItem.MAX_DURABILITY)
                                    .rarity(Rarity.RARE)
                    )
            );

    public static final RegistryObject<NeuroResonatorHelmetItem>
            NEURO_RESONATOR_HELMET = ITEMS.register(
                    "neuro_resonator_helmet",
                    () -> new NeuroResonatorHelmetItem(
                            new Item.Properties()
                                    .rarity(Rarity.UNCOMMON)
                    )
            );

    private ModItems() {
    }

    public static void register(IEventBus modEventBus) {
        ITEMS.register(modEventBus);
    }
}
```

## `src/main/java/com/carnis/mod/init/ModParticles.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES =
            DeferredRegister.create(ForgeRegistries.PARTICLE_TYPES, CarnisMod.MOD_ID);
    public static final RegistryObject<SimpleParticleType> BIOMASS_SPARK =
            PARTICLES.register("biomass_spark", () -> new SimpleParticleType(false));

    public static final RegistryObject<SimpleParticleType> PURIFIER_FLAME =
            PARTICLES.register("purifier_flame", () -> new SimpleParticleType(false));

    private ModParticles() { }

    public static void register(IEventBus bus) {
        PARTICLES.register(bus);
    }
}
```

## `src/main/java/com/carnis/mod/init/ModSounds.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUND_EVENTS =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, CarnisMod.MOD_ID);

    public static final RegistryObject<SoundEvent> INOCULATOR_FIRE =
            registerVariableRangeSound("item.inoculator.fire");
    public static final RegistryObject<SoundEvent> DART_HIT =
            registerVariableRangeSound("entity.dart.hit");

    public static final RegistryObject<SoundEvent> PURIFIER_IGNITE = registerVariableRangeSound("item.purifier.ignite");
    public static final RegistryObject<SoundEvent> PURIFIER_LOOP = registerVariableRangeSound("item.purifier.loop");
    public static final RegistryObject<SoundEvent> FLAMETHROWER_FIRE = registerVariableRangeSound("flamethrower_fire");
    public static final RegistryObject<SoundEvent> AMALGAM_SMASH = registerVariableRangeSound("amalgam_smash");
    public static final RegistryObject<SoundEvent> ORGANIC_CREAK = registerVariableRangeSound("organic_creak");
    public static final RegistryObject<SoundEvent> AMALGAM_ROAR = registerVariableRangeSound("amalgam_roar");

    public static final RegistryObject<SoundEvent> HEARTBEAT_LOOP = registerVariableRangeSound("heartbeat_loop");
    public static final RegistryObject<SoundEvent> HIVE_HEARTBEAT = registerVariableRangeSound("hive.heartbeat");

    public static final RegistryObject<SoundEvent> AMALGAM_STEP = registerVariableRangeSound("amalgam_step");

    public static final RegistryObject<SoundEvent> PHANTOM_CREEPER =
            registerVariableRangeSound("phantom_creeper");

    public static final RegistryObject<SoundEvent> PHANTOM_FOOTSTEPS =
            registerVariableRangeSound("phantom_footsteps");

    public static final RegistryObject<SoundEvent> PHANTOM_WHISPER =
            registerVariableRangeSound("phantom_whisper");

    public static final RegistryObject<SoundEvent> PULSING_HEART_BEAT =
            registerVariableRangeSound("pulsing_heart_beat");

    public static final RegistryObject<SoundEvent> SYNAPSE_SHOCK =
            registerVariableRangeSound("synapse_shock");

    public static final RegistryObject<SoundEvent> SYNAPSE_RUPTURE =
            registerVariableRangeSound("synapse_rupture");

    public static final RegistryObject<SoundEvent> DIGESTOR_CHURN =
            registerVariableRangeSound("digestor_churn");

    public static final RegistryObject<SoundEvent> HIVE_EYE_SCREECH =
            registerVariableRangeSound("hive.eye_screech");
    public static final RegistryObject<SoundEvent> HIVE_ALARM =
            registerVariableRangeSound("hive.alarm");
    public static final RegistryObject<SoundEvent> HIVE_AMBIENT =
            registerVariableRangeSound("hive.ambient");
    public static final RegistryObject<SoundEvent> HIVE_AMBIENT_CLOSE =
            registerVariableRangeSound("hive.ambient_close");
    public static final RegistryObject<SoundEvent> HIVE_PULSE =
            registerVariableRangeSound("hive.pulse");
    public static final RegistryObject<SoundEvent> HIVE_AMBIENT_TONAL_STINGER =
            registerVariableRangeSound("hive.ambient_tonal_stinger");

    public static final RegistryObject<SoundEvent> HIVE_AMB_SURFACE =
            registerVariableRangeSound("hive.ambient_surface");
    public static final RegistryObject<SoundEvent> HIVE_AMB_DEEP =
            registerVariableRangeSound("hive.ambient_deep");
    public static final RegistryObject<SoundEvent> HIVE_AMB_CORE =
            registerVariableRangeSound("hive.ambient_core");
    public static final RegistryObject<SoundEvent> HIVE_AMB_THRESHOLD =
            registerVariableRangeSound("hive.ambient_threshold");

    public static final RegistryObject<SoundEvent> ZONE_STINGER_INTENSIFY =
            registerVariableRangeSound("hive.zone_stinger_intensify");
    public static final RegistryObject<SoundEvent> ZONE_STINGER_RELEASE =
            registerVariableRangeSound("hive.zone_stinger_release");
    public static final RegistryObject<SoundEvent> ZONE_STINGER_DEEP =
            registerVariableRangeSound("hive.zone_stinger_deep");

    public static final RegistryObject<SoundEvent> FLESH_BLOCK_STEP =
            registerVariableRangeSound("flesh_block_step");
    public static final RegistryObject<SoundEvent> HIVE_BLOCK_PLACE =
            registerVariableRangeSound("hive.block_place");
    public static final RegistryObject<SoundEvent> HIVE_BLOCK_BREAK =
            registerVariableRangeSound("hive.block_break");
    public static final RegistryObject<SoundEvent> HIVE_SPREAD =
            registerVariableRangeSound("hive.spread");
    public static final RegistryObject<SoundEvent> COMBAT_FLESH_HIT =
            registerVariableRangeSound("combat.flesh_hit");
    public static final RegistryObject<SoundEvent> COMBAT_FLESH_HIT_DEEP =
            registerVariableRangeSound("combat.flesh_hit_deep");
    public static final RegistryObject<SoundEvent> COMBAT_DISMEMBER =
            registerVariableRangeSound("combat.dismember");
    public static final RegistryObject<SoundEvent> COMBAT_ARMOR_DEFLECT =
            registerVariableRangeSound("combat.armor_deflect");
    public static final RegistryObject<SoundEvent> COMBAT_BLOCK_STAB =
            registerVariableRangeSound("combat.block_stab");

    public static final RegistryObject<SoundEvent> HIVE_DETAIL_FLOW =
            registerVariableRangeSound("hive.detail_flow");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_MEMBRANE =
            registerVariableRangeSound("hive.detail_membrane");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_BUBBLES =
            registerVariableRangeSound("hive.detail_bubbles");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_CREAK =
            registerVariableRangeSound("hive.detail_creak");
    public static final RegistryObject<SoundEvent> HIVE_DETAIL_SCUTTLE =
            registerVariableRangeSound("hive.detail_scuttle");

    public static final RegistryObject<SoundEvent> HIVE_SPAWN_ALERT =
            registerVariableRangeSound("hive.spawn_alert");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_ATTACK =
            registerVariableRangeSound("hive.spawn_attack");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_IDLE =
            registerVariableRangeSound("hive.spawn_idle");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_HURT =
            registerVariableRangeSound("hive.spawn_hurt");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_HURT_CRITICAL =
            registerVariableRangeSound("hive.spawn_hurt_critical");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_SKELETON_WHIP =
            registerVariableRangeSound("hive.spawn_skeleton_whip");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_SKELETON_BLADE =
            registerVariableRangeSound("hive.spawn_skeleton_blade");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_SKELETON_BONECRACK =
            registerVariableRangeSound("hive.spawn_skeleton_bonecrack");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_CREEPER_SAC =
            registerVariableRangeSound("hive.spawn_creeper_sac");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_CREEPER_CRAWL =
            registerVariableRangeSound("hive.spawn_creeper_crawl");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_CREEPER_DETONATE =
            registerVariableRangeSound("hive.spawn_creeper_detonate");
    public static final RegistryObject<SoundEvent> HIVE_AMALGAM_SHUFFLE =
            registerVariableRangeSound("hive.amalgam_shuffle");
    public static final RegistryObject<SoundEvent> HIVE_AMALGAM_BREATH =
            registerVariableRangeSound("hive.amalgam_breath");
    public static final RegistryObject<SoundEvent> HIVE_AMALGAM_SLAM =
            registerVariableRangeSound("hive.amalgam_slam");
    public static final RegistryObject<SoundEvent> HIVE_SPAWN_DEATH =
            registerVariableRangeSound("hive.spawn_death");

    public static final RegistryObject<SoundEvent> CREEPER_RUPTURE =
            registerVariableRangeSound("creeper_rupture");

    public static final RegistryObject<SoundEvent> AMALGAMATION_FUSE =
            registerVariableRangeSound("amalgamation_fuse");

    public static final RegistryObject<SoundEvent> BONE_DEFLECT =
            registerVariableRangeSound("bone_deflect");

    public static final RegistryObject<SoundEvent> ACID_SPLASH =
            registerVariableRangeSound("acid_splash");

    public static final RegistryObject<SoundEvent> PUSTULE_BURST =
            registerVariableRangeSound("pustule_burst");

    public static final RegistryObject<SoundEvent> FLESH_AMALGAM_AMBIENT =
            registerVariableRangeSound("flesh_amalgam_ambient");

    public static final RegistryObject<SoundEvent> FLESH_AMALGAM_HURT =
            registerVariableRangeSound("flesh_amalgam_hurt");

    public static final RegistryObject<SoundEvent> FLESH_AMALGAM_DEATH =
            registerVariableRangeSound("flesh_amalgam_death");


    public static final RegistryObject<SoundEvent> HIVE_MEMBRANE_PLACE = registerVariableRangeSound("block.hive_membrane.place");
    public static final RegistryObject<SoundEvent> HIVE_MEMBRANE_STEP = registerVariableRangeSound("block.hive_membrane.step");
    public static final RegistryObject<SoundEvent> SYNAPSE_NODE_PULSE = registerVariableRangeSound("block.synapse_node.pulse");
    public static final RegistryObject<SoundEvent> INCUBATION_CYST_RUPTURE = registerVariableRangeSound("entity.incubation_cyst.rupture");
    public static final RegistryObject<SoundEvent> INCUBATION_CYST_AMBIENT = registerVariableRangeSound("entity.incubation_cyst.ambient");
    public static final RegistryObject<SoundEvent> SINEW_SHIELD_BLOCK = registerVariableRangeSound("entity.sinew_shield.block");
    public static final RegistryObject<SoundEvent> OSSIFIED_SCYTHE_SWING = registerVariableRangeSound("item.ossified_scythe.swing");
    public static final RegistryObject<SoundEvent> OSSIFIED_SCYTHE_HIT = registerVariableRangeSound("item.ossified_scythe.hit");
    public static final RegistryObject<SoundEvent> PUSTULE_GRENADE_IMPACT = registerVariableRangeSound("entity.pustule_grenade.impact");
    public static final RegistryObject<SoundEvent> PUSTULE_GRENADE_THROW = registerVariableRangeSound("entity.pustule_grenade.throw");
    public static final RegistryObject<SoundEvent> PURIFIER_LAMP_IGNITE = registerVariableRangeSound("block.purifier_lamp.ignite");
    public static final RegistryObject<SoundEvent> PURIFICATION_VIAL_BREAK = registerVariableRangeSound("item.purification_vial.break");


    private ModSounds() {
    }

    private static RegistryObject<SoundEvent> registerVariableRangeSound(String name) {
        ResourceLocation soundId = new ResourceLocation(CarnisMod.MOD_ID, name);
        return SOUND_EVENTS.register(
                name,
                () -> SoundEvent.createVariableRangeEvent(soundId)
        );
    }

    public static void register(IEventBus modEventBus) {
        SOUND_EVENTS.register(modEventBus);
    }
}
```

## `src/main/java/com/carnis/mod/item/AntibioticsItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.init.ModEffects;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;

public final class AntibioticsItem extends Item {
    public AntibioticsItem(Properties properties) { super(properties); }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(player.getItemInHand(hand));
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity user) {
        if (!level.isClientSide) {
            user.addEffect(new MobEffectInstance(ModEffects.IMMUNOSUPPRESSION.get(), 3600, 0));
        }
        if (!(user instanceof Player player) || !player.getAbilities().instabuild) stack.shrink(1);
        return stack;
    }

    @Override
    public int getUseDuration(ItemStack stack) { return 16; }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) { return UseAnim.EAT; }
}
```

## `src/main/java/com/carnis/mod/item/BioPurifierItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.FleshIncineration;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.init.ModEffects;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.HashSet;
import java.util.Set;

public final class BioPurifierItem extends Item implements GeoItem {
    public static final int MAX_DURABILITY = 500;
    private static final int DURATION = 72000;
    private static final int SHOCK_TICKS = 60;
    private static final double RANGE = 6.5D;
    // 25 degrees is the cone half-angle, measured from its axis.
    private static final double COS_ANGLE = Math.cos(Math.toRadians(25.0D));
    private static final double TAN_ANGLE = Math.tan(Math.toRadians(25.0D));
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.bio_purifier.idle");
    private static final RawAnimation FIRING = RawAnimation.begin().thenLoop("animation.bio_purifier.firing");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public BioPurifierItem(Properties properties) { super(properties.durability(MAX_DURABILITY)); }

    @Override public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientItemExtensions> consumer) {
        consumer.accept(new net.minecraftforge.client.extensions.common.IClientItemExtensions() {
            private com.carnis.mod.client.renderer.item.BioPurifierRenderer renderer;
            @Override public net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new com.carnis.mod.client.renderer.item.BioPurifierRenderer();
                return renderer;
            }
        });
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "operation", 0, state -> state.setAndContinue(
                com.carnis.mod.client.BioPurifierAnimationState.isFiring(state) ? FIRING : IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
    @Override public int getUseDuration(ItemStack stack) { return DURATION; }
    @Override public UseAnim getUseAnimation(ItemStack stack) { return UseAnim.NONE; }

    @Override public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        player.startUsingItem(hand);
        if (level instanceof ServerLevel server) server.playSound(null, player.blockPosition(), ModSounds.PURIFIER_IGNITE.get(),
                SoundSource.PLAYERS, 1.0F, 1.0F);
        return InteractionResultHolder.consume(stack);
    }

    @Override public void onUseTick(Level level, LivingEntity user, ItemStack stack, int count) {
        if (!(level instanceof ServerLevel server)) return;
        if (stack.isEmpty()) { user.stopUsingItem(); return; }
        int elapsed = DURATION - count;
        if (elapsed % 10 == 0) server.playSound(null, user.blockPosition(), ModSounds.PURIFIER_LOOP.get(),
                SoundSource.PLAYERS, 1.0F, 1.0F);
        if (elapsed % 2 == 0 && (!(user instanceof Player player) || !player.getAbilities().instabuild)) {
            stack.hurtAndBreak(1, user, entity -> entity.broadcastBreakEvent(entity.getUsedItemHand()));
            if (stack.isEmpty()) { user.stopUsingItem(); return; }
        }

        Vec3 forward = user.getLookAngle().normalize();
        double yaw = Math.toRadians(user.getYRot());
        Vec3 right = new Vec3(-Math.cos(yaw), 0.0D, -Math.sin(yaw)).normalize();
        Vec3 up = forward.cross(right).normalize();
        double side = 1.0D;
        if (user instanceof Player player) {
            HumanoidArm arm = user.getUsedItemHand() == InteractionHand.MAIN_HAND
                    ? player.getMainArm() : player.getMainArm().getOpposite();
            side = arm == HumanoidArm.RIGHT ? 1.0D : -1.0D;
        }
        Vec3 eye = user.getEyePosition();
        Vec3 origin = eye.add(right.scale(0.28D * side)).add(0, -0.35D, 0).add(forward.scale(0.85D));
        if (server.clip(new ClipContext(eye, origin, ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE, user)).getType() == HitResult.Type.BLOCK) return;

        emitParticles(server, user, origin, forward, right, up);
        damageEntities(server, user, origin, forward, elapsed % 4 == 0);
        if (elapsed % 4 == 0) burnConeBlocks(server, user, origin, forward, right, up);
    }

    private static boolean insideCone(Vec3 origin, Vec3 forward, Vec3 point) {
        Vec3 delta = point.subtract(origin);
        double distanceSquared = delta.lengthSqr();
        if (distanceSquared < 1.0E-8D || distanceSquared > RANGE * RANGE) return false;
        return delta.dot(forward) / Math.sqrt(distanceSquared) >= COS_ANGLE;
    }

    private static boolean clearRay(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 target) {
        return level.clip(new ClipContext(origin, target, ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE, user)).getType() == HitResult.Type.MISS;
    }

    private static boolean exposedInCone(ServerLevel level, LivingEntity user, LivingEntity target, Vec3 origin, Vec3 forward) {
        AABB b = target.getBoundingBox();
        double x = (b.minX + b.maxX) * .5D, z = (b.minZ + b.maxZ) * .5D;
        double y = (b.minY + b.maxY) * .5D;
        Vec3[] samples = {new Vec3(x, y, z), new Vec3(x, b.minY + .05D, z),
                new Vec3(x, b.maxY - .05D, z), new Vec3(b.minX, y, z), new Vec3(b.maxX, y, z),
                new Vec3(x, y, b.minZ), new Vec3(x, y, b.maxZ)};
        for (Vec3 point : samples) if (insideCone(origin, forward, point) && clearRay(level, user, origin, point)) return true;
        return false;
    }

    private static void damageEntities(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 forward, boolean damageTick) {
        Vec3 end = origin.add(forward.scale(RANGE));
        AABB bounds = new AABB(origin, end).inflate(RANGE * TAN_ANGLE);
        for (LivingEntity target : level.getEntitiesOfClass(LivingEntity.class, bounds,
                e -> e != user && e.isAlive() && !e.isSpectator())) {
            if (user instanceof Player attacker && target instanceof Player victim && !attacker.canHarmPlayer(victim)) continue;
            if (!exposedInCone(level, user, target, origin, forward)) continue;
            if (!damageTick) {
                if (target instanceof Player player) PlayerInfectionApi.addInfection(player, -5.0F);
                continue;
            }
            boolean protectedByPillar = HiveNetwork.shielded(level, target.blockPosition());
            target.setSecondsOnFire(4);
            if (protectedByPillar) target.setRemainingFireTicks(Math.min(target.getRemainingFireTicks(), 20));
            if (!protectedByPillar && infected(target))
                target.addEffect(new MobEffectInstance(ModEffects.THERMAL_SHOCK.get(), SHOCK_TICKS, 0));
            // Permit the four-tick stream cadence without clearing unrelated immunity afterwards.
            int previous = target.invulnerableTime;
            target.invulnerableTime = 0;
            try { target.hurt(ModDamageTypes.bioPurifierSurface(level, user), 3.0F); }
            finally { target.invulnerableTime = Math.max(previous, target.invulnerableTime); }
            if (target instanceof Player player && player.isAlive()) PlayerInfectionApi.addInfection(player, -5.0F);
        }
    }

    private static boolean infected(LivingEntity target) {
        if (target instanceof HivemindLinkedMob || InfectionHandler.isInfected(target)
                || target.hasEffect(ModEffects.INCUBATING.get())) return true;
        if (target instanceof Player player && PlayerInfectionApi.getInfectionLevel(player) > 0) return true;
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(target.getType());
        return id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }

    private static Vec3 rayDirection(Vec3 forward, Vec3 right, Vec3 up, double fraction, double angle) {
        return forward.add(right.scale(TAN_ANGLE * fraction * Math.cos(angle)))
                .add(up.scale(TAN_ANGLE * fraction * Math.sin(angle))).normalize();
    }

    private static void burnConeBlocks(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 forward, Vec3 right, Vec3 up) {
        Set<BlockPos> hitBlocks = new HashSet<>();
        traceBlock(level, user, origin, forward, hitBlocks);
        for (int ring = 1; ring <= 2; ring++) for (int i = 0; i < 12; i++) {
            double angle = 2.0D * Math.PI * (i + (ring == 1 ? 0.5D : 0.0D)) / 12.0D;
            traceBlock(level, user, origin, rayDirection(forward, right, up, ring / 2.0D, angle), hitBlocks);
        }
        for (BlockPos pos : hitBlocks) burnBlock(level, pos);
    }

    private static void traceBlock(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 direction, Set<BlockPos> found) {
        BlockHitResult hit = level.clip(new ClipContext(origin, origin.add(direction.scale(RANGE)),
                ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, user));
        if (hit.getType() == HitResult.Type.BLOCK) found.add(hit.getBlockPos().immutable());
    }

    private static void burnBlock(ServerLevel level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        if (state.is(ModBlocks.LIVING_FLESH.get()) || state.is(ModBlocks.OSSIFIED_FLESH.get())) {
            FleshIncineration.tryBurn(level, pos, state);
        } else if (state.is(ModBlocks.FLESH_VEINS.get())) {
            BlockState replacement = state.getFluidState().isEmpty() ? Blocks.AIR.defaultBlockState()
                    : state.getFluidState().createLegacyBlock();
            level.setBlockAndUpdate(pos, replacement);
        }
        // FIREPROOF_FLESH is not changed; it also blocks rays like any solid block.
    }

    private static void emitParticles(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 forward, Vec3 right, Vec3 up) {
        for (int i = 0; i < 5; i++) {
            double angle = level.random.nextDouble() * Math.PI * 2.0D;
            double radius = Math.sqrt(level.random.nextDouble());
            Vec3 ray = rayDirection(forward, right, up, radius, angle);
            double distance = 0.4D + level.random.nextDouble() * (RANGE - 0.4D);
            Vec3 intended = origin.add(ray.scale(distance));
            BlockHitResult hit = level.clip(new ClipContext(origin, intended, ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE, user));
            Vec3 point = hit.getType() == HitResult.Type.BLOCK ? hit.getLocation().subtract(ray.scale(.05D)) : intended;
            Vec3 velocity = ray.scale(.06D);
            level.sendParticles(ModParticles.PURIFIER_FLAME.get(), point.x, point.y, point.z, 0,
                    velocity.x, velocity.y, velocity.z, 1.0D);
            level.sendParticles(ParticleTypes.FLAME, point.x, point.y, point.z, 0,
                    velocity.x, velocity.y, velocity.z, 1.0D);
            if (i % 2 == 0) level.sendParticles(ParticleTypes.SMOKE, point.x, point.y, point.z, 0,
                    velocity.x * .5D, velocity.y * .5D + .01D, velocity.z * .5D, 1.0D);
        }
    }
}
```

## `src/main/java/com/carnis/mod/item/CodexCarnisItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.Level;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;

/** Keeps the original carnis:research_journal registry identity. */
public final class CodexCarnisItem extends Item {
    public CodexCarnisItem(Properties properties) {
        super(properties.stacksTo(1).rarity(Rarity.UNCOMMON));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide) {
            DistExecutor.safeRunWhenOn(Dist.CLIENT,
                    () -> com.carnis.mod.client.gui.CodexCarnisScreen::open);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }
}
```

## `src/main/java/com/carnis/mod/item/HiveEyeItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.client.renderer.HiveEyeItemRenderer;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.function.Consumer;

public final class HiveEyeItem extends BlockItem implements GeoItem {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public HiveEyeItem(Block block, Properties properties) {
        super(block, properties);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "idle", 0,
                state -> state.setAndContinue(RawAnimation.begin().thenLoop("animation.hive_eye.idle"))));
    }

    @Override
    public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new IClientItemExtensions() {
            private HiveEyeItemRenderer renderer;

            @Override
            public BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new HiveEyeItemRenderer();
                return renderer;
            }
        });
    }
}
```

## `src/main/java/com/carnis/mod/item/MaggotSpawnEggItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraftforge.common.ForgeSpawnEggItem;

import javax.annotation.Nullable;
import java.util.List;
import java.util.function.Supplier;

public final class MaggotSpawnEggItem extends ForgeSpawnEggItem {
    public MaggotSpawnEggItem(Supplier<? extends EntityType<? extends Mob>> entityType,
                              int backgroundColor, int highlightColor, Properties properties) {
        super(entityType, backgroundColor, highlightColor, properties);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.carnis.biomass_maggot.mechanics").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.carnis.biomass_maggot.lore").withStyle(ChatFormatting.DARK_RED));
    }
}
```

## `src/main/java/com/carnis/mod/item/NeuroArmorMaterial.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.init.ModItems;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.ArmorMaterials;
import net.minecraft.world.item.crafting.Ingredient;

public enum NeuroArmorMaterial implements ArmorMaterial {
    INSTANCE;

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> 330;
            case CHESTPLATE -> 480;
            case LEGGINGS -> 450;
            case BOOTS -> 390;
        };
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> 3;
            case CHESTPLATE -> 7;
            case LEGGINGS -> 5;
            case BOOTS -> 2;
        };
    }

    @Override public int getEnchantmentValue() { return 15; }
    @Override public SoundEvent getEquipSound() { return SoundEvents.ARMOR_EQUIP_IRON; }
    @Override public Ingredient getRepairIngredient() { return Ingredient.of(ModItems.LIVING_FLESH.get()); }
    @Override public String getName() { return "carnis:neuro_resonator"; }
    @Override public float getToughness() { return 1.5F; }
    @Override public float getKnockbackResistance() { return 0.025F; }
}
```

## `src/main/java/com/carnis/mod/item/NeuroResonatorArmorItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.item.armor.NeuroArmorItem;

/** Keeps existing item registrations and references compatible. */
public class NeuroResonatorArmorItem extends NeuroArmorItem {
    public NeuroResonatorArmorItem(Type type, Properties properties) { super(type, properties); }
}
```

## `src/main/java/com/carnis/mod/item/NeuroResonatorHelmetItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;

import java.util.Objects;

public final class NeuroResonatorHelmetItem extends NeuroResonatorArmorItem {
    public NeuroResonatorHelmetItem(Properties properties) {
        super(Type.HELMET, properties);
    }

    public static boolean isEquipped(LivingEntity entity) {
        Objects.requireNonNull(entity, "entity");

        return entity.getItemBySlot(EquipmentSlot.HEAD).getItem()
                instanceof NeuroResonatorHelmetItem;
    }
}
```

## `src/main/java/com/carnis/mod/item/NeuroWeave.java`

```java
package com.carnis.mod.item;

import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;

public final class NeuroWeave {
    public static final String TAG = "carnis:neuro_woven";
    private static final EquipmentSlot[] ARMOR_SLOTS = {
            EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET
    };

    private NeuroWeave() { }

    public static boolean isWoven(ItemStack stack) {
        return stack.getItem() instanceof ArmorItem && stack.hasTag() && stack.getTag().getBoolean(TAG);
    }

    public static int protectedPieces(LivingEntity entity) {
        int count = 0;
        for (EquipmentSlot slot : ARMOR_SLOTS) {
            ItemStack stack = entity.getItemBySlot(slot);
            if (isWoven(stack) || stack.getItem() instanceof com.carnis.mod.item.armor.NeuroArmorItem) count++;
        }
        return count;
    }

    public static float infectionMultiplier(LivingEntity entity) {
        return Math.max(0.0F, 1.0F - 0.25F * protectedPieces(entity));
    }

    public static boolean hasSludgeImmuneBoots(LivingEntity entity) {
        ItemStack boots = entity.getItemBySlot(EquipmentSlot.FEET);
        return boots.getItem() instanceof com.carnis.mod.item.armor.NeuroArmorItem armor
                && armor.getType() == ArmorItem.Type.BOOTS;
    }
}
```

## `src/main/java/com/carnis/mod/item/OrganBlockItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.block.PustuleClusterBlock;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import javax.annotation.Nullable;

public final class OrganBlockItem extends BlockItem {
    public OrganBlockItem(Block block, Properties properties) {
        super(block, properties);
    }

    @Nullable
    @Override
    protected BlockState getPlacementState(BlockPlaceContext context) {
        BlockState state = super.getPlacementState(context);
        if (state != null && state.getBlock() instanceof PustuleClusterBlock
                && (state.getValue(PustuleClusterBlock.BURST)
                || state.getValue(PustuleClusterBlock.AGE) > 0)) {
            return null;
        }
        return state;
    }
}
```

## `src/main/java/com/carnis/mod/item/OrganicTooltipBlockItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;

import javax.annotation.Nullable;
import java.util.List;

public final class OrganicTooltipBlockItem extends BlockItem {
    private final String tooltipName;

    public OrganicTooltipBlockItem(Block block, Properties properties, String tooltipName) {
        super(block, properties);
        this.tooltipName = tooltipName;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.carnis." + tooltipName + ".mechanics").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.carnis." + tooltipName + ".lore").withStyle(ChatFormatting.DARK_RED));
    }
}
```

## `src/main/java/com/carnis/mod/item/OssifiedScytheItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.init.ModSounds;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import javax.annotation.Nullable;
import java.util.List;

public final class OssifiedScytheItem extends SwordItem {
    public OssifiedScytheItem(Tier tier, int attackDamage, float attackSpeed, Properties properties) {
        super(tier, attackDamage, attackSpeed, properties);
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        boolean hit = super.hurtEnemy(stack, target, attacker);
        attacker.level().playSound(null, target.blockPosition(), ModSounds.OSSIFIED_SCYTHE_HIT.get(),
                SoundSource.PLAYERS, 1.0F, 1.0F);
        return hit;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        super.appendHoverText(stack, level, tooltip, flag);
        tooltip.add(Component.translatable("tooltip.carnis.ossified_scythe"));
    }
}
```

## `src/main/java/com/carnis/mod/item/PneumaticInoculatorItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.client.renderer.PneumaticInoculatorRenderer;
import com.carnis.mod.entity.PurificationDartEntity;
import com.carnis.mod.entity.ViralDartEntity;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.SingletonGeoAnimatable;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.function.Consumer;

public final class PneumaticInoculatorItem extends Item implements GeoItem {
    private static final int COOLDOWN_TICKS = 15;
    private static final RawAnimation FIRE = RawAnimation.begin().thenPlay("animation.pneumatic_inoculator.fire");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public PneumaticInoculatorItem(Properties properties) {
        super(properties);
        SingletonGeoAnimatable.registerSyncedAnimatable(this);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() { return geoCache; }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<PneumaticInoculatorItem>(this, "action", 0,
                state -> PlayState.STOP).triggerableAnim("fire", FIRE));
    }

    @Override
    public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new IClientItemExtensions() {
            private PneumaticInoculatorRenderer renderer;
            @Override
            public BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new PneumaticInoculatorRenderer();
                return renderer;
            }
        });
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack weapon = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(this)) return InteractionResultHolder.fail(weapon);
        ItemStack ammo = findAmmo(player);
        if (ammo.isEmpty()) return InteractionResultHolder.fail(weapon);

        if (level instanceof ServerLevel server) {
            com.carnis.mod.entity.projectile.InoculatorDartEntity dart = new com.carnis.mod.entity.projectile.InoculatorDartEntity(
                    level, player, ammo.is(ModItems.VIRAL_DART.get())
                    ? com.carnis.mod.entity.projectile.InoculatorDartEntity.DartType.VIRAL
                    : com.carnis.mod.entity.projectile.InoculatorDartEntity.DartType.PURIFICATION);
            dart.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 2.8F, 1.0F);
            if (!server.addFreshEntity(dart)) return InteractionResultHolder.fail(weapon);
            if (!player.getAbilities().instabuild) ammo.shrink(1);
            player.getCooldowns().addCooldown(this, COOLDOWN_TICKS);
            triggerAnim(player, GeoItem.getOrAssignId(weapon, server), "action", "fire");

            Vec3 forward = player.getLookAngle().normalize();
            Vec3 horizontal = new Vec3(forward.x, 0.0D, forward.z);
            if (horizontal.lengthSqr() < 1.0E-8D) {
                float yaw = player.getYRot() * ((float) Math.PI / 180.0F);
                horizontal = new Vec3(-Math.sin(yaw), 0.0D, Math.cos(yaw));
            } else {
                horizontal = horizontal.normalize();
            }
            Vec3 right = new Vec3(-horizontal.z, 0.0D, horizontal.x);
            HumanoidArm heldArm = hand == InteractionHand.MAIN_HAND
                    ? player.getMainArm() : player.getMainArm().getOpposite();
            double side = heldArm == HumanoidArm.RIGHT ? 1.0D : -1.0D;
            Vec3 eye = player.getEyePosition();
            Vec3 muzzle = eye.add(right.scale(0.24D * side)).add(0.0D, -0.24D, 0.0D)
                    .add(forward.scale(0.65D));
            var obstruction = server.clip(new ClipContext(eye, muzzle, ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE, player));
            if (obstruction.getType() != HitResult.Type.MISS) {
                muzzle = obstruction.getLocation().add(eye.subtract(obstruction.getLocation()).normalize().scale(0.02D));
            }
            server.sendParticles(ParticleTypes.POOF, muzzle.x, muzzle.y, muzzle.z,
                    3, 0.025D, 0.025D, 0.025D, 0.01D);
            for (int i = 0; i < 5; i++) {
                double lateral = (i - 2) * 0.045D;
                Vec3 velocity = forward.scale(0.12D).add(right.scale(lateral * 0.12D));
                server.sendParticles(ParticleTypes.CLOUD, muzzle.x, muzzle.y, muzzle.z, 0,
                        velocity.x, velocity.y, velocity.z, 1.0D);
            }
            server.playSound(null, player.blockPosition(), ModSounds.INOCULATOR_FIRE.get(),
                    SoundSource.PLAYERS, 1.0F, 1.0F);
        }
        return InteractionResultHolder.sidedSuccess(weapon, level.isClientSide);
    }

    private static ItemStack findAmmo(Player player) {
        ItemStack selected = player.getMainHandItem();
        if (isAmmo(selected)) return selected;
        ItemStack offhand = player.getOffhandItem();
        if (isAmmo(offhand)) return offhand;
        for (int slot = 0; slot < player.getInventory().getContainerSize(); slot++) {
            ItemStack stack = player.getInventory().getItem(slot);
            if (isAmmo(stack)) return stack;
        }
        return ItemStack.EMPTY;
    }

    private static boolean isAmmo(ItemStack stack) {
        return stack.is(ModItems.VIRAL_DART.get()) || stack.is(ModItems.PURIFICATION_DART.get());
    }
}
```

## `src/main/java/com/carnis/mod/item/PulsingHeartItem.java`

```java
package com.carnis.mod.item;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.level.block.Block;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
public final class PulsingHeartItem extends BlockItem implements GeoItem {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    public PulsingHeartItem(Block block, Properties properties) { super(block, properties); }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "pulse", 0, state -> state.setAndContinue(RawAnimation.begin().thenLoop("animation.pulsing_heart.pulse"))));
    }
    @Override public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientItemExtensions> consumer) {
        consumer.accept(new net.minecraftforge.client.extensions.common.IClientItemExtensions() {
            private com.carnis.mod.client.renderer.PulsingHeartItemRenderer renderer;
            @Override public net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new com.carnis.mod.client.renderer.PulsingHeartItemRenderer();
                return renderer;
            }
        });
    }
}
```

## `src/main/java/com/carnis/mod/item/PurificationDartItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import javax.annotation.Nullable;
import java.util.List;

public final class PurificationDartItem extends Item {
    public PurificationDartItem(Properties properties) { super(properties); }
    @Override public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.carnis.purification_dart.mechanics").withStyle(ChatFormatting.AQUA));
        tooltip.add(Component.translatable("tooltip.carnis.purification_dart.protocol").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.carnis.dart.use").withStyle(ChatFormatting.DARK_GRAY));
    }
}
```

## `src/main/java/com/carnis/mod/item/PurificationSerumItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.event.HallucinationEvents;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;

public final class PurificationSerumItem extends Item {
    public static final float INFECTION_REDUCTION = 35.0F;
    private static final int DRINK_DURATION_TICKS = 32;

    public PurificationSerumItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(
            Level level,
            Player player,
            InteractionHand hand
    ) {
        ItemStack stack = player.getItemInHand(hand);
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public ItemStack finishUsingItem(
            ItemStack stack,
            Level level,
            LivingEntity user
    ) {
        if (!level.isClientSide() && user instanceof ServerPlayer player) {
            float infectionLevel = PlayerInfectionApi.getInfectionLevel(player);
            PlayerInfectionApi.setInfectionLevel(
                    player,
                    Math.max(0.0F, infectionLevel - INFECTION_REDUCTION)
            );
            HallucinationEvents.resetHallucinationTimer(player);
        }

        if (user instanceof Player player
                && player.getAbilities().instabuild) {
            return stack;
        }

        stack.shrink(1);
        ItemStack emptyBottle = new ItemStack(Items.GLASS_BOTTLE);

        if (stack.isEmpty()) {
            return emptyBottle;
        }

        if (user instanceof Player player
                && !player.getInventory().add(emptyBottle)) {
            player.drop(emptyBottle, false);
        }

        return stack;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.DRINK;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return DRINK_DURATION_TICKS;
    }

    @Override
    public void appendHoverText(ItemStack stack, @javax.annotation.Nullable Level level,
                                java.util.List<net.minecraft.network.chat.Component> tooltip,
                                net.minecraft.world.item.TooltipFlag flag) {
        tooltip.add(net.minecraft.network.chat.Component.translatable("tooltip.carnis.purification_serum.mechanics")
                .withStyle(net.minecraft.ChatFormatting.AQUA));
        tooltip.add(net.minecraft.network.chat.Component.translatable("tooltip.carnis.purification_serum.use")
                .withStyle(net.minecraft.ChatFormatting.GRAY));
    }

    @Override
    public SoundEvent getDrinkingSound() {
        return SoundEvents.GENERIC_DRINK;
    }
}
```

## `src/main/java/com/carnis/mod/item/PurificationVialItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.init.ModSounds;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import javax.annotation.Nullable;
import java.util.List;

public final class PurificationVialItem extends Item {
    public PurificationVialItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(player.getItemInHand(hand));
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return 32;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.DRINK;
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity user) {
        if (!level.isClientSide) {
            user.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 1));
            level.playSound(null, user.getX(), user.getY(), user.getZ(), ModSounds.PURIFICATION_VIAL_BREAK.get(),
                    SoundSource.PLAYERS, 1.0F, 1.0F);
        }
        if (user instanceof Player player && player.getAbilities().instabuild) return stack;
        stack.shrink(1);
        ItemStack bottle = new ItemStack(Items.GLASS_BOTTLE);
        if (user instanceof Player player && !player.getInventory().add(bottle)) player.drop(bottle, false);
        return stack.isEmpty() ? bottle : stack;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        super.appendHoverText(stack, level, tooltip, flag);
        tooltip.add(Component.translatable("tooltip.carnis.purification_vial"));
    }
}
```

## `src/main/java/com/carnis/mod/item/PustuleGrenadeItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.entity.PustuleGrenadeEntity;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import javax.annotation.Nullable;
import java.util.List;

public final class PustuleGrenadeItem extends Item {
    public PustuleGrenadeItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!level.isClientSide) {
            PustuleGrenadeEntity grenade = new PustuleGrenadeEntity(level, player);
            grenade.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 1.0F, 1.0F);
            level.addFreshEntity(grenade);
            level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.PUSTULE_GRENADE_THROW.get(),
                    SoundSource.PLAYERS, 1.0F, 1.0F);
            if (!player.getAbilities().instabuild) stack.shrink(1);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        super.appendHoverText(stack, level, tooltip, flag);
        tooltip.add(Component.translatable("tooltip.carnis.pustule_grenade"));
    }
}
```

## `src/main/java/com/carnis/mod/item/SinewShieldItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import javax.annotation.Nullable;
import java.util.List;

public final class SinewShieldItem extends ShieldItem {
    public SinewShieldItem(Properties properties) {
        super(properties);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        super.appendHoverText(stack, level, tooltip, flag);
        tooltip.add(Component.translatable("tooltip.carnis.sinew_shield"));
    }
}
```

## `src/main/java/com/carnis/mod/item/ViralDartItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import javax.annotation.Nullable;
import java.util.List;

public final class ViralDartItem extends Item {
    public ViralDartItem(Properties properties) { super(properties); }
    @Override public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.carnis.viral_dart.mechanics").withStyle(ChatFormatting.LIGHT_PURPLE));
        tooltip.add(Component.translatable("tooltip.carnis.viral_dart.protocol").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.carnis.dart.use").withStyle(ChatFormatting.DARK_GRAY));
    }
}
```

## `src/main/java/com/carnis/mod/item/armor/NeuroArmorItem.java`

```java
package com.carnis.mod.item.armor;

import com.carnis.mod.client.renderer.NeuroArmorRenderer;
import com.carnis.mod.init.ModArmorMaterials;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.function.Consumer;

public class NeuroArmorItem extends ArmorItem implements GeoItem {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    public NeuroArmorItem(Type type, Properties properties) {
        super(ModArmorMaterials.NEURO_RESONATOR, type, properties);
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) { }
    @Override public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new IClientItemExtensions() {
            private NeuroArmorRenderer renderer;
            @Override public HumanoidModel<?> getHumanoidArmorModel(LivingEntity entity, ItemStack stack,
                    EquipmentSlot slot, HumanoidModel<?> original) {
                if (renderer == null) renderer = new NeuroArmorRenderer();
                renderer.prepForRender(entity, stack, slot, original);
                return renderer;
            }
        });
    }
}
```

## `src/main/java/com/carnis/mod/network/ModMessages.java`

```java
package com.carnis.mod.network;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.network.packet.ClientboundHallucinationPacket;
import com.carnis.mod.network.packet.SyncCarnisWorldDataPacket;
import com.carnis.mod.network.packet.SyncPlayerBiomassPacket;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

import java.util.Objects;

public final class ModMessages {
    private static final String PROTOCOL_VERSION = "3";

    private static final SimpleChannel CHANNEL =
            NetworkRegistry.ChannelBuilder
                    .named(new ResourceLocation(CarnisMod.MOD_ID, "messages"))
                    .networkProtocolVersion(() -> PROTOCOL_VERSION)
                    .clientAcceptedVersions(PROTOCOL_VERSION::equals)
                    .serverAcceptedVersions(PROTOCOL_VERSION::equals)
                    .simpleChannel();

    private static int nextPacketId;
    private static volatile boolean registered;

    private ModMessages() {
    }

    public static synchronized void register() {
        if (registered) {
            throw new IllegalStateException("Carnis network packets are already registered");
        }

        CHANNEL.messageBuilder(
                        SyncCarnisWorldDataPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(SyncCarnisWorldDataPacket::encode)
                .decoder(SyncCarnisWorldDataPacket::decode)
                .consumerMainThread(SyncCarnisWorldDataPacket::handle)
                .add();

        CHANNEL.messageBuilder(
                        SyncPlayerInfectionPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(SyncPlayerInfectionPacket::encode)
                .decoder(SyncPlayerInfectionPacket::decode)
                .consumerMainThread(SyncPlayerInfectionPacket::handle)
                .add();

        CHANNEL.messageBuilder(
                        ClientboundHallucinationPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(ClientboundHallucinationPacket::encode)
                .decoder(ClientboundHallucinationPacket::decode)
                .consumerMainThread(ClientboundHallucinationPacket::handle)
                .add();

        CHANNEL.messageBuilder(
                        SyncPlayerBiomassPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(SyncPlayerBiomassPacket::encode)
                .decoder(SyncPlayerBiomassPacket::decode)
                .consumerMainThread(SyncPlayerBiomassPacket::handle)
                .add();

        registered = true;
    }

    public static void sendToPlayer(SyncPlayerBiomassPacket packet, ServerPlayer player) {
        Objects.requireNonNull(packet, "packet");
        Objects.requireNonNull(player, "player");
        ensureRegistered();
        CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), packet);
    }

    public static void sendToPlayer(ServerPlayer player) {
        Objects.requireNonNull(player, "player");
        ensureRegistered();

        CarnisWorldData worldData = CarnisWorldData.get(player.serverLevel());
        sendToPlayer(player, SyncCarnisWorldDataPacket.from(worldData));
    }

    public static void sendPlayerInfection(ServerPlayer player) {
        Objects.requireNonNull(player, "player");
        ensureRegistered();

        sendToPlayer(player, SyncPlayerInfectionPacket.from(player));
    }

    public static void sendHallucination(
            ServerPlayer player,
            ClientboundHallucinationPacket packet
    ) {
        Objects.requireNonNull(player, "player");
        Objects.requireNonNull(packet, "packet");
        ensureRegistered();

        sendToPlayer(player, packet);
    }

    public static void sendToPlayersInLevel(ServerLevel level) {
        Objects.requireNonNull(level, "level");
        ensureRegistered();

        SyncCarnisWorldDataPacket packet = SyncCarnisWorldDataPacket.from(
                CarnisWorldData.get(level)
        );

        for (ServerPlayer player : level.players()) {
            sendToPlayer(player, packet);
        }
    }

    public static void sendToAllPlayers(MinecraftServer server) {
        Objects.requireNonNull(server, "server");
        ensureRegistered();

        for (ServerLevel level : server.getAllLevels()) {
            sendToPlayersInLevel(level);
        }
    }

    private static void sendToPlayer(
            ServerPlayer player,
            SyncCarnisWorldDataPacket packet
    ) {
        CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                packet
        );
    }

    private static void sendToPlayer(
            ServerPlayer player,
            SyncPlayerInfectionPacket packet
    ) {
        CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                packet
        );
    }

    private static void sendToPlayer(
            ServerPlayer player,
            ClientboundHallucinationPacket packet
    ) {
        CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                packet
        );
    }

    private static int nextPacketId() {
        return nextPacketId++;
    }

    private static void ensureRegistered() {
        if (!registered) {
            throw new IllegalStateException(
                    "Carnis network packets have not been registered yet"
            );
        }
    }
}
```

## `src/main/java/com/carnis/mod/network/SyncPlayerInfectionPacket.java`

```java
package com.carnis.mod.network;

import com.carnis.mod.infection.PlayerInfectionManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

public record SyncPlayerInfectionPacket(int infectionPoints, int stage) {
    public SyncPlayerInfectionPacket {
        infectionPoints = Math.max(0, Math.min(100, infectionPoints));
        stage = Math.max(0, Math.min(4, stage));
    }
    public static SyncPlayerInfectionPacket from(Player player) {
        return new SyncPlayerInfectionPacket(PlayerInfectionManager.displayPoints(player),
                PlayerInfectionManager.stage(PlayerInfectionManager.getPoints(player)));
    }
    public static void encode(SyncPlayerInfectionPacket packet, FriendlyByteBuf buffer) {
        buffer.writeVarInt(packet.infectionPoints());
        buffer.writeVarInt(packet.stage());
    }
    public static SyncPlayerInfectionPacket decode(FriendlyByteBuf buffer) {
        return new SyncPlayerInfectionPacket(buffer.readVarInt(), buffer.readVarInt());
    }
    public static void handle(SyncPlayerInfectionPacket packet, Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        if (context.getDirection() == NetworkDirection.PLAY_TO_CLIENT)
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> com.carnis.mod.client.data.ClientInfectionData.apply(packet));
        context.setPacketHandled(true);
    }
}
```

## `src/main/java/com/carnis/mod/network/packet/ClientboundHallucinationPacket.java`

```java
package com.carnis.mod.network.packet;

import com.carnis.mod.client.sound.PhantomSoundManager;
import com.carnis.mod.hallucination.HallucinationType;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;

import java.util.Objects;
import java.util.function.Supplier;

/**
 * Carries one purely client-side auditory hallucination. The relative offset
 * uses player-local axes: positive X is right, positive Y is up and positive
 * Z is forward, so a negative Z value is heard behind the player.
 */
public record ClientboundHallucinationPacket(
        HallucinationType type,
        float volumeMultiplier,
        Vec3 relativeOffset
) {
    private static final float MAX_VOLUME_MULTIPLIER = 2.0F;
    private static final double MAX_OFFSET_COMPONENT = 16.0D;

    public ClientboundHallucinationPacket {
        type = Objects.requireNonNull(type, "type");
        relativeOffset = sanitizeOffset(
                Objects.requireNonNull(relativeOffset, "relativeOffset")
        );

        if (Float.isNaN(volumeMultiplier)) {
            volumeMultiplier = 1.0F;
        } else {
            volumeMultiplier = Math.max(
                    0.0F,
                    Math.min(MAX_VOLUME_MULTIPLIER, volumeMultiplier)
            );
        }
    }

    public static void encode(
            ClientboundHallucinationPacket packet,
            FriendlyByteBuf buffer
    ) {
        buffer.writeEnum(packet.type());
        buffer.writeFloat(packet.volumeMultiplier());
        buffer.writeDouble(packet.relativeOffset().x);
        buffer.writeDouble(packet.relativeOffset().y);
        buffer.writeDouble(packet.relativeOffset().z);
    }

    public static ClientboundHallucinationPacket decode(
            FriendlyByteBuf buffer
    ) {
        return new ClientboundHallucinationPacket(
                buffer.readEnum(HallucinationType.class),
                buffer.readFloat(),
                new Vec3(
                        buffer.readDouble(),
                        buffer.readDouble(),
                        buffer.readDouble()
                )
        );
    }

    public static void handle(
            ClientboundHallucinationPacket packet,
            Supplier<NetworkEvent.Context> contextSupplier
    ) {
        NetworkEvent.Context context = contextSupplier.get();

        if (context.getDirection() != NetworkDirection.PLAY_TO_CLIENT) {
            context.setPacketHandled(true);
            return;
        }

        DistExecutor.unsafeRunWhenOn(
                Dist.CLIENT,
                () -> () -> PhantomSoundManager.handle(packet)
        );

        context.setPacketHandled(true);
    }

    private static Vec3 sanitizeOffset(Vec3 offset) {
        return new Vec3(
                sanitizeOffsetComponent(offset.x),
                sanitizeOffsetComponent(offset.y),
                sanitizeOffsetComponent(offset.z)
        );
    }

    private static double sanitizeOffsetComponent(double component) {
        if (!Double.isFinite(component)) {
            return 0.0D;
        }

        return Math.max(
                -MAX_OFFSET_COMPONENT,
                Math.min(MAX_OFFSET_COMPONENT, component)
        );
    }
}
```

## `src/main/java/com/carnis/mod/network/packet/SyncCarnisWorldDataPacket.java`

```java
package com.carnis.mod.network.packet;

import com.carnis.mod.client.data.ClientCarnisWorldData;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;

import java.util.Objects;
import java.util.function.Supplier;

public record SyncCarnisWorldDataPacket(
        long biomassPoints,
        long fireAdaptation,
        long rangedAdaptation,
        long meleeAdaptation,
        long pillaringAdaptation,
        long explosiveAdaptation,
        long darkAdaptation
) {
    public SyncCarnisWorldDataPacket {
        biomassPoints = nonNegative(biomassPoints);
        fireAdaptation = nonNegative(fireAdaptation);
        rangedAdaptation = nonNegative(rangedAdaptation);
        meleeAdaptation = nonNegative(meleeAdaptation);
        pillaringAdaptation = nonNegative(pillaringAdaptation);
        explosiveAdaptation = nonNegative(explosiveAdaptation);
        darkAdaptation = nonNegative(darkAdaptation);
    }

    public static SyncCarnisWorldDataPacket from(CarnisWorldData worldData) {
        Objects.requireNonNull(worldData, "worldData");

        return new SyncCarnisWorldDataPacket(
                worldData.getBiomassPoints(),
                worldData.getFireAdaptation(),
                worldData.getRangedAdaptation(),
                worldData.getMeleeAdaptation(),
                worldData.getPillaringAdaptation(),
                worldData.getExplosiveAdaptation(),
                worldData.getDarkAdaptation()
        );
    }

    public static void encode(
            SyncCarnisWorldDataPacket packet,
            FriendlyByteBuf buffer
    ) {
        buffer.writeLong(packet.biomassPoints());
        buffer.writeLong(packet.fireAdaptation());
        buffer.writeLong(packet.rangedAdaptation());
        buffer.writeLong(packet.meleeAdaptation());
        buffer.writeLong(packet.pillaringAdaptation());
        buffer.writeLong(packet.explosiveAdaptation());
        buffer.writeLong(packet.darkAdaptation());
    }

    public static SyncCarnisWorldDataPacket decode(FriendlyByteBuf buffer) {
        return new SyncCarnisWorldDataPacket(
                buffer.readLong(),
                buffer.readLong(),
                buffer.readLong(),
                buffer.readLong(),
                buffer.readLong(),
                buffer.readLong(),
                buffer.readLong()
        );
    }

    public static void handle(
            SyncCarnisWorldDataPacket packet,
            Supplier<NetworkEvent.Context> contextSupplier
    ) {
        NetworkEvent.Context context = contextSupplier.get();

        if (context.getDirection() != NetworkDirection.PLAY_TO_CLIENT) {
            context.setPacketHandled(true);
            return;
        }

        DistExecutor.unsafeRunWhenOn(
                Dist.CLIENT,
                () -> () -> ClientCarnisWorldData.apply(packet)
        );

        context.setPacketHandled(true);
    }

    private static long nonNegative(long value) {
        return Math.max(0L, value);
    }
}
```

## `src/main/java/com/carnis/mod/network/packet/SyncPlayerBiomassPacket.java`

```java
package com.carnis.mod.network.packet;

import com.carnis.mod.client.data.ClientPlayerBiomassData;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Серверное значение персональной биомассы для одного игрока. */
public final class SyncPlayerBiomassPacket {
    private final long biomassPoints;

    public SyncPlayerBiomassPacket(long biomassPoints) {
        this.biomassPoints = Math.max(0L, biomassPoints);
    }

    public static void encode(SyncPlayerBiomassPacket packet, FriendlyByteBuf buffer) {
        buffer.writeLong(packet.biomassPoints);
    }

    public static SyncPlayerBiomassPacket decode(FriendlyByteBuf buffer) {
        return new SyncPlayerBiomassPacket(buffer.readLong());
    }

    public static void handle(SyncPlayerBiomassPacket packet, Supplier<NetworkEvent.Context> contextSupplier) {
        NetworkEvent.Context context = contextSupplier.get();
        if (context.getDirection() == NetworkDirection.PLAY_TO_CLIENT) {
            context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                    () -> () -> ClientPlayerBiomassData.apply(packet.biomassPoints)));
        }
        context.setPacketHandled(true);
    }
}
```

## `src/main/java/com/carnis/mod/sound/CarnisCombatSounds.java`

```java
package com.carnis.mod.sound;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.init.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.common.ToolAction;
import net.minecraftforge.common.ToolActions;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.lang.ref.WeakReference;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;

/** Server-side combat sound routing and short delayed dismemberment playback. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisCombatSounds {
    private static final long HEAVY_HIT_COOLDOWN_TICKS = 2L;
    private static final long DISMEMBER_COOLDOWN_TICKS = 20L;

    private static final Map<LivingEntity, Long> LAST_HEAVY_HIT = new WeakHashMap<>();
    private static final Map<LivingEntity, Long> LAST_DISMEMBER = new WeakHashMap<>();
    private static final List<PendingSound> PENDING_DISMEMBER_SOUNDS = new ArrayList<>();

    private CarnisCombatSounds() { }

    /** Plays the regular flesh-hit variation for a server-side target. */
    public static void onHit(LivingEntity target) {
        ServerLevel level = serverLevel(target);
        if (level == null) return;
        playAt(level, target, ModSounds.COMBAT_FLESH_HIT.get(), 1.0F);
    }

    /** Plays a deep hit at most once per target every two game ticks (100 ms). */
    public static void onHeavyHit(LivingEntity target) {
        ServerLevel level = serverLevel(target);
        if (level == null) return;

        long now = level.getGameTime();
        synchronized (LAST_HEAVY_HIT) {
            Long previous = LAST_HEAVY_HIT.get(target);
            if (previous != null && now >= previous && now - previous < HEAVY_HIT_COOLDOWN_TICKS) return;
            LAST_HEAVY_HIT.put(target, now);
        }

        playAt(level, target, ModSounds.COMBAT_FLESH_HIT_DEEP.get(), 1.0F);
    }

    /**
     * Schedules a dismemberment sound 3–5 ticks after the hit, with a one-second per-target cooldown.
     * The caller supplies the current game time so this can be used by existing combat/dismemberment logic.
     */
    public static void onDismember(LivingEntity target, DamageSource src, long now) {
        ServerLevel level = serverLevel(target);
        if (level == null || src == null) return;

        synchronized (LAST_DISMEMBER) {
            Long previous = LAST_DISMEMBER.get(target);
            if (previous != null && now >= previous && now - previous < DISMEMBER_COOLDOWN_TICKS) return;
            LAST_DISMEMBER.put(target, now);
        }

        int delay = 3 + target.getRandom().nextInt(3);
        float volume = 1.0F;
        PendingSound pending = new PendingSound(new WeakReference<>(level),
                level.getGameTime() + delay, target.getX(), target.getY(), target.getZ(),
                ModSounds.COMBAT_DISMEMBER.get(), volume);
        synchronized (PENDING_DISMEMBER_SOUNDS) {
            PENDING_DISMEMBER_SOUNDS.add(pending);
        }
    }

    /** Routes combat sounds for Hive targets and armored non-Hive targets. */
    @SubscribeEvent
    public static void onLivingHurt(LivingHurtEvent event) {
        LivingEntity target = event.getEntity();
        if (event.isCanceled() || !(target.level() instanceof ServerLevel level)
                || event.getAmount() <= 0.0F) return;

        DamageSource source = event.getSource();
        Entity attacker = source.getEntity();
        boolean explosion = source.is(DamageTypeTags.IS_EXPLOSION);
        if (attacker == target || attacker == null && source.getDirectEntity() == null && !explosion) return;

        boolean axeHit = hasToolAction(attacker, ToolActions.AXE_DIG);
        boolean swordHit = hasToolAction(attacker, ToolActions.SWORD_DIG);
        boolean hiveTarget = NeuralMossBlock.isHive(target);

        if (!hiveTarget) {
            if (hasArmorItem(target) && (axeHit || swordHit)) {
                playAt(level, target, ModSounds.COMBAT_ARMOR_DEFLECT.get(), 1.0F);
            }
            if (attacker instanceof Player player
                    && player.getAttackStrengthScale(0.5F) > 0.9F
                    && event.getAmount() > 6.0F) {
                playAt(level, target, ModSounds.COMBAT_BLOCK_STAB.get(), 1.0F);
            }
            return;
        }

        boolean criticalHit = isCriticalHit(attacker);
        boolean highDamage = event.getAmount() > 6.0F && !swordHit;
        if (axeHit || criticalHit || explosion || highDamage) {
            onHeavyHit(target);
        } else {
            onHit(target);
        }
    }

    @SubscribeEvent
    public static void onLivingDeath(LivingDeathEvent event) {
        LivingEntity victim = event.getEntity();
        if (event.isCanceled() || !(victim.level() instanceof ServerLevel level)
                || !NeuralMossBlock.isHive(victim)) return;

        Entity attacker = event.getSource().getEntity();
        boolean eligibleAttacker = attacker instanceof Player
                || attacker instanceof Mob mob && NeuralMossBlock.isHive(mob);
        if (eligibleAttacker) onDismember(victim, event.getSource(), level.getGameTime());
    }

    private static boolean hasToolAction(Entity entity, ToolAction action) {
        if (!(entity instanceof LivingEntity living)) return false;
        return living.getMainHandItem().canPerformAction(action)
                || living.getOffhandItem().canPerformAction(action);
    }

    private static boolean hasArmorItem(LivingEntity entity) {
        for (ItemStack stack : entity.getArmorSlots()) {
            if (!stack.isEmpty() && stack.getItem() instanceof ArmorItem) return true;
        }
        return false;
    }

    private static boolean isCriticalHit(Entity attacker) {
        if (!(attacker instanceof Player player)) return false;
        return player.getAttackStrengthScale(0.5F) > 0.9F
                && player.fallDistance > 0.0F
                && !player.onGround()
                && !player.onClimbable()
                && !player.isInWater()
                && !player.hasEffect(MobEffects.BLINDNESS)
                && !player.isPassenger()
                && !player.isSprinting()
                && !player.isFallFlying();
    }

    @SubscribeEvent
    public static void onLevelTick(TickEvent.LevelTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.level instanceof ServerLevel level)) return;

        List<PendingSound> ready = new ArrayList<>();
        synchronized (PENDING_DISMEMBER_SOUNDS) {
            Iterator<PendingSound> iterator = PENDING_DISMEMBER_SOUNDS.iterator();
            while (iterator.hasNext()) {
                PendingSound pending = iterator.next();
                ServerLevel pendingLevel = pending.level().get();
                if (pendingLevel == null) {
                    iterator.remove();
                } else if (pendingLevel == level && level.getGameTime() >= pending.dueAt()) {
                    ready.add(pending);
                    iterator.remove();
                }
            }
        }

        for (PendingSound pending : ready) {
            level.playSound(null, pending.x(), pending.y(), pending.z(), pending.sound(),
                    SoundSource.HOSTILE, pending.volume(), 1.0F);
        }
    }

    private static ServerLevel serverLevel(LivingEntity target) {
        return target.level() instanceof ServerLevel level ? level : null;
    }

    private static void playAt(ServerLevel level, LivingEntity target, SoundEvent sound, float volume) {
        level.playSound(null, target.getX(), target.getY(), target.getZ(), sound,
                SoundSource.HOSTILE, volume, 1.0F);
    }

    private record PendingSound(WeakReference<ServerLevel> level, long dueAt,
                                double x, double y, double z, SoundEvent sound,
                                float volume) { }
}
```

## `src/main/java/com/carnis/mod/sound/CarnisSoundTypes.java`

```java
package com.carnis.mod.sound;

import com.carnis.mod.init.ModSounds;
import net.minecraft.world.level.block.SoundType;

/** SoundType factory for the mod's organic blocks. */
public final class CarnisSoundTypes {
    private CarnisSoundTypes() { }

    /**
     * Must be called from a deferred block-registration supplier, after the sound registry objects exist.
     * SoundType argument order: break, step, place, hit, fall.
     */
    public static SoundType membrane() {
        return new SoundType(1.0F, 1.0F,
                ModSounds.HIVE_BLOCK_BREAK.get(),
                ModSounds.HIVE_MEMBRANE_STEP.get(),
                ModSounds.HIVE_MEMBRANE_PLACE.get(),
                ModSounds.COMBAT_FLESH_HIT.get(),
                ModSounds.HIVE_MEMBRANE_STEP.get());
    }

    public static SoundType organic() {
        return new SoundType(
                1.0F,
                1.0F,
                ModSounds.HIVE_BLOCK_BREAK.get(),
                ModSounds.FLESH_BLOCK_STEP.get(),
                ModSounds.HIVE_BLOCK_PLACE.get(),
                ModSounds.COMBAT_FLESH_HIT.get(),
                ModSounds.FLESH_BLOCK_STEP.get()
        );
    }
}
```

## `src/main/java/com/carnis/mod/util/HiveGrowthSuppression.java`

```java
package com.carnis.mod.util;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

import java.util.HashMap;
import java.util.Map;
import java.util.WeakHashMap;

/** Утилиты поиска блоков Улья и оценки подавления роста флоры. */
public final class HiveGrowthSuppression {
    public static final TagKey<Block> HIVE_BLOCKS = TagKey.create(
            Registries.BLOCK,
            new ResourceLocation("carnis", "hive_blocks")
    );

    /** Кэш изолирован по уровню и радиусу; packed BlockPos остаётся ключом самой записи. */
    private static final Map<Level, Map<Integer, Map<Long, Boolean>>> NEAR_HIVE_CACHE = new WeakHashMap<>();

    private HiveGrowthSuppression() {
    }

    /** Проверяет, входит ли блок в тег блоков Улья. */
    public static boolean isHiveBlock(Level level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        return state.is(HIVE_BLOCKS);
    }

    /** Ищет блок Улья в кубе с центром в указанной позиции. */
    public static boolean isNearHive(Level level, BlockPos pos, int radius) {
        if (radius < 0) {
            return false;
        }

        long packedPos = pos.asLong();
        synchronized (NEAR_HIVE_CACHE) {
            Map<Integer, Map<Long, Boolean>> levelCache = NEAR_HIVE_CACHE.get(level);
            if (levelCache != null) {
                Map<Long, Boolean> radiusCache = levelCache.get(radius);
                if (radiusCache != null) {
                    Boolean cached = radiusCache.get(packedPos);
                    if (cached != null) {
                        return cached;
                    }
                }
            }
        }

        boolean found = false;
        BlockPos.MutableBlockPos cursor = new BlockPos.MutableBlockPos();
        search:
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dy = -radius; dy <= radius; dy++) {
                for (int dz = -radius; dz <= radius; dz++) {
                    cursor.setWithOffset(pos, dx, dy, dz);
                    if (isHiveBlock(level, cursor)) {
                        found = true;
                        break search;
                    }
                }
            }
        }

        synchronized (NEAR_HIVE_CACHE) {
            NEAR_HIVE_CACHE
                    .computeIfAbsent(level, ignored -> new HashMap<>())
                    .computeIfAbsent(radius, ignored -> new HashMap<>())
                    .put(packedPos, found);
        }
        return found;
    }

    /** Возвращает долю обычного роста, если рядом найден блок Улья. */
    public static float getSuppressionFactor(Level level, BlockPos pos, int radius, int strength) {
        if (!isNearHive(level, pos, radius)) {
            return 1.0F;
        }
        int boundedStrength = Math.max(0, Math.min(100, strength));
        return 1.0F - boundedStrength / 100.0F;
    }

    /** Сбрасывает результаты поиска; вызывается периодически серверным обработчиком. */
    public static void clearCache() {
        synchronized (NEAR_HIVE_CACHE) {
            NEAR_HIVE_CACHE.clear();
        }
    }
}
```

## `src/main/java/com/carnis/mod/world/CarnisWorldData.java`

```java
package com.carnis.mod.world;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public final class CarnisWorldData extends SavedData {
    public static final String DATA_NAME = "carnis_world_data";

    public static final long SYNAPSE_SHOCK_DURATION_TICKS = 180L * 20L;
    public static final int SYNAPSE_SHOCK_RADIUS_CHUNKS = 1;

    private static final int DATA_VERSION = 1;

    private static final String TAG_DATA_VERSION = "DataVersion";
    private static final String TAG_BIOMASS_POINTS = "BiomassPoints";
    private static final String TAG_ADAPTATION = "Adaptation";
    private static final String TAG_FIRE = "Fire";
    private static final String TAG_RANGED = "Ranged";
    private static final String TAG_MELEE = "Melee";
    private static final String TAG_PILLARING = "Pillaring";
    private static final String TAG_EXPLOSIVE = "Explosive";
    private static final String TAG_DARK = "Dark";
    private static final String TAG_SHOCKED_CHUNKS = "ShockedChunks";
    private static final String TAG_CHUNK_X = "ChunkX";
    private static final String TAG_CHUNK_Z = "ChunkZ";
    private static final String TAG_EXPIRES_AT = "ExpiresAt";

    private long biomassPoints;

    private long fireAdaptation;
    private long rangedAdaptation;
    private long meleeAdaptation;
    private long pillaringAdaptation;
    private long explosiveAdaptation;
    private long darkAdaptation;

    private final Map<ChunkPos, Long> shockedChunks = new HashMap<>();
    // Ephemeral per-dimension cooldowns. Expired entries are pruned on use;
    // no world chunks are loaded or kept alive by this map.
    private final Map<AdaptationCooldownKey, Long> adaptationCooldowns = new HashMap<>();

    private record AdaptationCooldownKey(ChunkPos chunk, AdaptationType type) {
    }

    public boolean tryAwardDamageAdaptation(ChunkPos chunk, AdaptationType type, long tick) {
        Objects.requireNonNull(chunk, "chunk");
        Objects.requireNonNull(type, "type");
        adaptationCooldowns.entrySet().removeIf(entry -> tick < entry.getValue()
                || tick - entry.getValue() >= 10L);
        AdaptationCooldownKey key = new AdaptationCooldownKey(chunk, type);
        if (adaptationCooldowns.containsKey(key)) {
            return false;
        }
        adaptationCooldowns.put(key, tick);
        incrementAdaptation(type);
        return true;
    }

    public void decayAdaptation(AdaptationType type, long amount) {
        requireNonNegative(amount, "amount");
        long value = getAdaptation(type);
        setAdaptation(type, value - Math.min(value, amount));
    }

    /** Log-interpolated between the specified resistance milestones. */
    public static float damageMitigation(long points) {
        long[] thresholds = {0L, 100L, 300L, 600L, 1000L};
        double[] resistance = {0.0D, 0.25D, 0.50D, 0.70D, 0.80D};
        double p = Math.max(0L, points);
        if (p >= 1000.0D) {
            return 0.80F;
        }
        for (int i = 1; i < thresholds.length; i++) {
            if (p <= thresholds[i]) {
                double start = Math.log1p(thresholds[i - 1]);
                double end = Math.log1p(thresholds[i]);
                double fraction = (Math.log1p(p) - start) / (end - start);
                return (float) Math.min(0.80D, Math.max(0.0D,
                        resistance[i - 1] + fraction * (resistance[i] - resistance[i - 1])));
            }
        }
        return 0.80F;
    }

    public CarnisWorldData() {
    }

    public static CarnisWorldData get(ServerLevel level) {
        Objects.requireNonNull(level, "level");
        return level.getDataStorage().computeIfAbsent(
                CarnisWorldData::load,
                CarnisWorldData::new,
                DATA_NAME
        );
    }

    public static CarnisWorldData load(CompoundTag rootTag) {
        CarnisWorldData data = new CarnisWorldData();

        data.biomassPoints = nonNegative(rootTag.getLong(TAG_BIOMASS_POINTS));

        if (rootTag.contains(TAG_ADAPTATION, Tag.TAG_COMPOUND)) {
            CompoundTag adaptationTag = rootTag.getCompound(TAG_ADAPTATION);
            data.fireAdaptation = nonNegative(adaptationTag.getLong(TAG_FIRE));
            data.rangedAdaptation = nonNegative(adaptationTag.getLong(TAG_RANGED));
            data.meleeAdaptation = nonNegative(adaptationTag.getLong(TAG_MELEE));
            data.pillaringAdaptation = nonNegative(adaptationTag.getLong(TAG_PILLARING));
            data.explosiveAdaptation = nonNegative(adaptationTag.getLong(TAG_EXPLOSIVE));
            data.darkAdaptation = nonNegative(adaptationTag.getLong(TAG_DARK));
        }

        ListTag shockedChunksTag = rootTag.getList(
                TAG_SHOCKED_CHUNKS,
                Tag.TAG_COMPOUND
        );

        for (int index = 0; index < shockedChunksTag.size(); index++) {
            CompoundTag chunkTag = shockedChunksTag.getCompound(index);
            long expiresAt = chunkTag.getLong(TAG_EXPIRES_AT);

            if (expiresAt <= 0L) {
                continue;
            }

            ChunkPos chunkPos = new ChunkPos(
                    chunkTag.getInt(TAG_CHUNK_X),
                    chunkTag.getInt(TAG_CHUNK_Z)
            );

            data.shockedChunks.merge(chunkPos, expiresAt, Math::max);
        }

        return data;
    }

    @Override
    public CompoundTag save(CompoundTag rootTag) {
        rootTag.putInt(TAG_DATA_VERSION, DATA_VERSION);
        rootTag.putLong(TAG_BIOMASS_POINTS, biomassPoints);

        CompoundTag adaptationTag = new CompoundTag();
        adaptationTag.putLong(TAG_FIRE, fireAdaptation);
        adaptationTag.putLong(TAG_RANGED, rangedAdaptation);
        adaptationTag.putLong(TAG_MELEE, meleeAdaptation);
        adaptationTag.putLong(TAG_PILLARING, pillaringAdaptation);
        adaptationTag.putLong(TAG_EXPLOSIVE, explosiveAdaptation);
        adaptationTag.putLong(TAG_DARK, darkAdaptation);
        rootTag.put(TAG_ADAPTATION, adaptationTag);

        ListTag shockedChunksTag = new ListTag();
        shockedChunks.entrySet().stream()
                .sorted(
                        Comparator
                                .comparingInt(
                                        (Map.Entry<ChunkPos, Long> entry) ->
                                                entry.getKey().x
                                )
                                .thenComparingInt(entry -> entry.getKey().z)
                )
                .forEach(entry -> {
                    CompoundTag chunkTag = new CompoundTag();
                    chunkTag.putInt(TAG_CHUNK_X, entry.getKey().x);
                    chunkTag.putInt(TAG_CHUNK_Z, entry.getKey().z);
                    chunkTag.putLong(TAG_EXPIRES_AT, entry.getValue());
                    shockedChunksTag.add(chunkTag);
                });
        rootTag.put(TAG_SHOCKED_CHUNKS, shockedChunksTag);

        return rootTag;
    }

    public long getBiomassPoints() {
        return biomassPoints;
    }

    public void setBiomassPoints(long points) {
        requireNonNegative(points, "points");

        if (biomassPoints != points) {
            biomassPoints = points;
            setDirty();
        }
    }

    public long addBiomassPoints(long points) {
        requireNonNegative(points, "points");
        long updatedPoints = saturatingAdd(biomassPoints, points);

        if (updatedPoints != biomassPoints) {
            biomassPoints = updatedPoints;
            setDirty();
        }

        return biomassPoints;
    }

    public boolean tryConsumeBiomassPoints(long points) {
        requireNonNegative(points, "points");

        if (biomassPoints < points) {
            return false;
        }

        if (points > 0L) {
            biomassPoints -= points;
            setDirty();
        }

        return true;
    }

    public long getAdaptation(AdaptationType type) {
        Objects.requireNonNull(type, "type");

        return switch (type) {
            case FIRE -> fireAdaptation;
            case RANGED -> rangedAdaptation;
            case MELEE -> meleeAdaptation;
            case PILLARING -> pillaringAdaptation;
            case EXPLOSIVE -> explosiveAdaptation;
            case DARK -> darkAdaptation;
        };
    }

    public long setAdaptation(AdaptationType type, long value) {
        Objects.requireNonNull(type, "type");
        requireNonNegative(value, "value");

        if (getAdaptation(type) != value) {
            setAdaptationValue(type, value);
            setDirty();
        }

        return getAdaptation(type);
    }

    public long addAdaptation(AdaptationType type, long amount) {
        Objects.requireNonNull(type, "type");
        requireNonNegative(amount, "amount");

        long currentValue = getAdaptation(type);
        long updatedValue = saturatingAdd(currentValue, amount);

        if (updatedValue != currentValue) {
            setAdaptationValue(type, updatedValue);
            setDirty();
        }

        return updatedValue;
    }

    public long incrementAdaptation(AdaptationType type) {
        return addAdaptation(type, 1L);
    }

    public void resetAdaptations() {
        boolean changed = fireAdaptation != 0L
                || rangedAdaptation != 0L
                || meleeAdaptation != 0L
                || pillaringAdaptation != 0L
                || explosiveAdaptation != 0L
                || darkAdaptation != 0L;

        if (!changed) {
            return;
        }

        fireAdaptation = 0L;
        rangedAdaptation = 0L;
        meleeAdaptation = 0L;
        pillaringAdaptation = 0L;
        explosiveAdaptation = 0L;
        darkAdaptation = 0L;
        setDirty();
    }

    public long getFireAdaptation() {
        return fireAdaptation;
    }

    public long getRangedAdaptation() {
        return rangedAdaptation;
    }

    public long getMeleeAdaptation() {
        return meleeAdaptation;
    }

    public long getPillaringAdaptation() {
        return pillaringAdaptation;
    }

    public long getExplosiveAdaptation() {
        return explosiveAdaptation;
    }

    public long getDarkAdaptation() {
        return darkAdaptation;
    }

    public Map<ChunkPos, Long> getShockedChunks() {
        return Collections.unmodifiableMap(shockedChunks);
    }

    /**
     * Shocks the center chunk and every horizontal neighbor at Chebyshev
     * distance one: an inclusive 3-by-3 square of nine whole chunks. The
     * expiry is extended to exactly 3,600 ticks (180 seconds) from the
     * supplied game time.
     */
    public void shockSynapseArea(ChunkPos center, long currentGameTime) {
        shockChunkArea(
                center,
                SYNAPSE_SHOCK_RADIUS_CHUNKS,
                currentGameTime
        );
    }

    public int shockChunkArea(
            ChunkPos center,
            int radiusChunks,
            long currentGameTime
    ) {
        Objects.requireNonNull(center, "center");
        requireNonNegative(currentGameTime, "currentGameTime");

        if (radiusChunks < 0) {
            throw new IllegalArgumentException(
                    "radiusChunks must not be negative"
            );
        }

        long expiresAt = saturatingAdd(
                currentGameTime,
                SYNAPSE_SHOCK_DURATION_TICKS
        );
        int changedChunks = 0;

        for (
                int offsetX = -radiusChunks;
                offsetX <= radiusChunks;
                offsetX++
        ) {
            for (
                    int offsetZ = -radiusChunks;
                    offsetZ <= radiusChunks;
                    offsetZ++
            ) {
                ChunkPos affectedChunk = new ChunkPos(
                        center.x + offsetX,
                        center.z + offsetZ
                );
                Long previousExpiration = shockedChunks.get(affectedChunk);

                if (
                        previousExpiration == null
                                || previousExpiration < expiresAt
                ) {
                    shockedChunks.put(affectedChunk, expiresAt);
                    changedChunks++;
                }
            }
        }

        if (changedChunks > 0) {
            setDirty();
        }

        return changedChunks;
    }

    /** Extends, but never shortens, an existing shock. */
    public boolean shockChunkFor(ChunkPos chunk, long currentGameTime, long durationTicks) {
        Objects.requireNonNull(chunk, "chunk");
        requireNonNegative(currentGameTime, "currentGameTime");
        requireNonNegative(durationTicks, "durationTicks");
        long expiry = saturatingAdd(currentGameTime, durationTicks);
        Long old = shockedChunks.get(chunk);
        if (old != null && old >= expiry) return false;
        shockedChunks.put(chunk, expiry);
        setDirty();
        return true;
    }

    /** Add shock duration without discarding the remaining active duration. */
    public void extendChunkShock(ChunkPos chunk, long now, long extraTicks) {
        Objects.requireNonNull(chunk, "chunk");
        requireNonNegative(now, "now");
        requireNonNegative(extraTicks, "extraTicks");
        long old = shockedChunks.getOrDefault(chunk, now);
        shockedChunks.put(chunk, saturatingAdd(Math.max(now, old), extraTicks));
        setDirty();
    }

    public boolean isChunkShocked(
            ChunkPos chunkPos,
            long currentGameTime
    ) {
        Objects.requireNonNull(chunkPos, "chunkPos");
        requireNonNegative(currentGameTime, "currentGameTime");

        Long expiresAt = shockedChunks.get(chunkPos);

        if (expiresAt == null) {
            return false;
        }

        if (expiresAt > currentGameTime) {
            return true;
        }

        if (shockedChunks.remove(chunkPos, expiresAt)) {
            setDirty();
        }

        return false;
    }

    public boolean halveRemainingShock(ChunkPos chunkPos, long currentGameTime) {
        Objects.requireNonNull(chunkPos, "chunkPos");
        requireNonNegative(currentGameTime, "currentGameTime");
        Long expiry = shockedChunks.get(chunkPos);
        if (expiry == null || expiry <= currentGameTime) {
            return false;
        }
        long remaining = expiry - currentGameTime;
        long shortened = currentGameTime + remaining / 2L;
        if (shortened <= currentGameTime) {
            shockedChunks.remove(chunkPos);
        } else {
            shockedChunks.put(chunkPos, shortened);
        }
        setDirty();
        return true;
    }

    public long getRemainingShockTicks(
            ChunkPos chunkPos,
            long currentGameTime
    ) {
        Objects.requireNonNull(chunkPos, "chunkPos");
        requireNonNegative(currentGameTime, "currentGameTime");

        Long expiresAt = shockedChunks.get(chunkPos);

        if (expiresAt == null || expiresAt <= currentGameTime) {
            if (expiresAt != null && shockedChunks.remove(chunkPos, expiresAt)) {
                setDirty();
            }
            return 0L;
        }

        return expiresAt - currentGameTime;
    }

    public int purgeExpiredShockedChunks(long currentGameTime) {
        requireNonNegative(currentGameTime, "currentGameTime");

        int previousSize = shockedChunks.size();
        shockedChunks.entrySet().removeIf(
                entry -> entry.getValue() <= currentGameTime
        );
        int removedCount = previousSize - shockedChunks.size();

        if (removedCount > 0) {
            setDirty();
        }

        return removedCount;
    }

    public void clearShockedChunks() {
        if (!shockedChunks.isEmpty()) {
            shockedChunks.clear();
            setDirty();
        }
    }

    private void setAdaptationValue(AdaptationType type, long value) {
        switch (type) {
            case FIRE -> fireAdaptation = value;
            case RANGED -> rangedAdaptation = value;
            case MELEE -> meleeAdaptation = value;
            case PILLARING -> pillaringAdaptation = value;
            case EXPLOSIVE -> explosiveAdaptation = value;
            case DARK -> darkAdaptation = value;
        }
    }

    private static long nonNegative(long value) {
        return Math.max(0L, value);
    }

    private static void requireNonNegative(long value, String name) {
        if (value < 0L) {
            throw new IllegalArgumentException(name + " must not be negative");
        }
    }

    private static long saturatingAdd(long current, long amount) {
        if (amount > Long.MAX_VALUE - current) {
            return Long.MAX_VALUE;
        }
        return current + amount;
    }

    public enum AdaptationType {
        FIRE,
        RANGED,
        MELEE,
        PILLARING,
        EXPLOSIVE,
        DARK
    }
}
```

## `src/main/java/com/carnis/mod/world/GestationCystFeature.java`

```java
package com.carnis.mod.world;

import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

public final class GestationCystFeature extends Feature<NoneFeatureConfiguration> {
    private static final int RADIUS = 6;
    private static final int INNER_RADIUS = 4;

    public GestationCystFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos center = context.origin();
        if (center.getY() < -50 || center.getY() > 0
                || !level.getBlockState(center).is(Blocks.DEEPSLATE)) {
            return false;
        }
        // Reject fluids adjacent to the shell as well as inside it.
        for (int x = -RADIUS - 1; x <= RADIUS + 1; x++) {
            for (int y = -RADIUS - 1; y <= RADIUS + 1; y++) {
                for (int z = -RADIUS - 1; z <= RADIUS + 1; z++) {
                    if (x * x + y * y + z * z > (RADIUS + 1) * (RADIUS + 1)) continue;
                    BlockPos p = center.offset(x, y, z);
                    if (level.isOutsideBuildHeight(p) || !level.getFluidState(p).isEmpty()) return false;
                }
            }
        }
        // Validate the complete footprint before writing: never erase block entities,
        // fluids, bedrock, or existing structures with non-natural blocks.
        for (int x = -RADIUS; x <= RADIUS; x++) {
            for (int y = -RADIUS; y <= RADIUS; y++) {
                for (int z = -RADIUS; z <= RADIUS; z++) {
                    if (x * x + y * y + z * z > RADIUS * RADIUS) continue;
                    BlockPos p = center.offset(x, y, z);
                    BlockState state = level.getBlockState(p);
                    if (state.hasBlockEntity() || !state.getFluidState().isEmpty()
                            || !(state.isAir() || state.is(Blocks.DEEPSLATE) || state.is(Blocks.TUFF))) {
                        return false;
                    }
                }
            }
        }
        for (int x = -RADIUS; x <= RADIUS; x++) {
            for (int y = -RADIUS; y <= RADIUS; y++) {
                for (int z = -RADIUS; z <= RADIUS; z++) {
                    int distance = x * x + y * y + z * z;
                    if (distance > RADIUS * RADIUS) continue;
                    BlockState replacement = distance >= INNER_RADIUS * INNER_RADIUS
                            ? ModBlocks.OSSIFIED_FLESH.get().defaultBlockState()
                            : Blocks.AIR.defaultBlockState();
                    level.setBlock(center.offset(x, y, z), replacement, 2);
                }
            }
        }
        level.setBlock(center, ModBlocks.PULSING_HEART.get().defaultBlockState(), 2);
        level.setBlock(center.offset(2, 0, 0), ModBlocks.HIVE_EYE.get().defaultBlockState(), 2);
        level.setBlock(center.offset(-2, 0, 0), ModBlocks.HIVE_EYE.get().defaultBlockState(), 2);
        level.setBlock(center.offset(0, -2, 0), ModBlocks.NERVE_PILLAR.get().defaultBlockState(), 2);
        BlockPos moss = center.offset(2, -2, 0);
        BlockPos sprout = center.offset(-2, -2, 0);
        level.setBlock(moss.below(), ModBlocks.LIVING_FLESH.get().defaultBlockState(), 2);
        level.setBlock(sprout.below(), ModBlocks.LIVING_FLESH.get().defaultBlockState(), 2);
        if (ModBlocks.NEURAL_MOSS.get().defaultBlockState().canSurvive(level, moss))
            level.setBlock(moss, ModBlocks.NEURAL_MOSS.get().defaultBlockState(), 2);
        if (ModBlocks.SPORE_SPROUT.get().defaultBlockState().canSurvive(level, sprout))
            level.setBlock(sprout, ModBlocks.SPORE_SPROUT.get().defaultBlockState(), 2);
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/world/HiveNetwork.java`

```java
package com.carnis.mod.world;

import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.world.infection.InfectionTickQueue;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

/** Persisted, per-dimension position index. Only known positions are visited; no voxel scans. */
public final class HiveNetwork extends SavedData {
    public enum Kind { INFECTION, EYE, POOL, PILLAR }
    private final EnumMap<Kind, Map<Long, Set<Long>>> byChunk = new EnumMap<>(Kind.class);
    private final Set<UUID> deadSentinels = new HashSet<>();
    public HiveNetwork() { for (Kind k : Kind.values()) byChunk.put(k, new HashMap<>()); }
    public static HiveNetwork get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(HiveNetwork::load, HiveNetwork::new, "carnis_hive_network");
    }
    public static HiveNetwork load(CompoundTag tag) {
        HiveNetwork data = new HiveNetwork();
        for (Kind k : Kind.values()) for (long packed : tag.getLongArray(k.name())) data.put(k, BlockPos.of(packed), true);
        var dead = tag.getList("DeadSentinels", net.minecraft.nbt.Tag.TAG_STRING);
        for (int i = 0; i < dead.size(); i++) {
            try { data.deadSentinels.add(UUID.fromString(dead.getString(i))); } catch (IllegalArgumentException ignored) { }
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag tag) {
        for (Kind k : Kind.values()) {
            List<Long> list = new ArrayList<>();
            byChunk.get(k).values().forEach(list::addAll);
            tag.putLongArray(k.name(), list);
        }
        var dead = new net.minecraft.nbt.ListTag();
        deadSentinels.forEach(id -> dead.add(net.minecraft.nbt.StringTag.valueOf(id.toString())));
        tag.put("DeadSentinels", dead);
        return tag;
    }
    public void noteSentinelDeath(UUID id) { if (deadSentinels.add(id)) setDirty(); }
    public boolean consumeSentinelDeath(UUID id) { boolean found = deadSentinels.remove(id); if (found) setDirty(); return found; }
    private boolean put(Kind kind, BlockPos pos, boolean present) {
        long chunk = new ChunkPos(pos).toLong();
        Map<Long, Set<Long>> map = byChunk.get(kind);
        if (present) return map.computeIfAbsent(chunk, k -> new HashSet<>()).add(pos.asLong());
        Set<Long> entries = map.get(chunk);
        if (entries == null || !entries.remove(pos.asLong())) return false;
        if (entries.isEmpty()) map.remove(chunk);
        return true;
    }
    public static void observe(ServerLevel level, BlockPos pos, BlockState state, boolean present) {
        HiveNetwork index = get(level);
        for (Kind kind : Kind.values()) {
            boolean matches = switch (kind) {
                case INFECTION -> InfectionTickQueue.isInfectionSource(state);
                case EYE -> state.is(ModBlocks.HIVE_EYE.get());
                case POOL -> state.is(ModBlocks.STOMACH_POOL.get());
                case PILLAR -> state.is(ModBlocks.NERVE_PILLAR.get());
            };
            if (matches && index.put(kind, pos, present)) {
                index.setDirty();
                if (kind == Kind.INFECTION) for (PulsingHeartBlockEntity heart : nearbyHearts(level, pos, 32)) heart.observeInfection(pos, present);
            }
        }
    }
    /** Register a bounded batch of world-generated tissue after its chunk is live. */
    public static void registerGenerated(ServerLevel level, BlockPos origin, List<BlockPos> positions) {
        HiveNetwork index = get(level);
        List<PulsingHeartBlockEntity> hearts = nearbyHearts(level, origin, 40);
        boolean changed = false;
        for (BlockPos pos : positions) {
            if (!level.hasChunkAt(pos) || !InfectionTickQueue.isInfectionSource(level.getBlockState(pos))) continue;
            changed |= index.put(Kind.INFECTION, pos, true);
            for (PulsingHeartBlockEntity heart : hearts) heart.observeInfection(pos, true);
        }
        if (changed) index.setDirty();
    }
    public List<BlockPos> positions(Kind kind, BlockPos origin, int radius) {
        List<BlockPos> found = new ArrayList<>();
        int minX = (origin.getX() - radius) >> 4, maxX = (origin.getX() + radius) >> 4;
        int minZ = (origin.getZ() - radius) >> 4, maxZ = (origin.getZ() + radius) >> 4;
        for (int x = minX; x <= maxX; x++) for (int z = minZ; z <= maxZ; z++) {
            Set<Long> set = byChunk.get(kind).get(ChunkPos.asLong(x, z));
            if (set == null) continue;
            for (long packed : set) {
                BlockPos p = BlockPos.of(packed);
                if (p.distSqr(origin) <= (double) radius * radius) found.add(p);
            }
        }
        return found;
    }
    public static List<PulsingHeartBlockEntity> nearbyHearts(ServerLevel level, BlockPos origin, int radius) {
        List<PulsingHeartBlockEntity> result = new ArrayList<>();
        int minX = (origin.getX() - radius) >> 4, maxX = (origin.getX() + radius) >> 4;
        int minZ = (origin.getZ() - radius) >> 4, maxZ = (origin.getZ() + radius) >> 4;
        for (int x = minX; x <= maxX; x++) for (int z = minZ; z <= maxZ; z++) {
            var chunk = level.getChunkSource().getChunkNow(x, z);
            if (chunk == null) continue;
            for (var be : chunk.getBlockEntities().values())
                if (be instanceof PulsingHeartBlockEntity heart && heart.getBlockPos().distSqr(origin) <= (double)radius * radius) result.add(heart);
        }
        return result;
    }
    public static PulsingHeartBlockEntity nearestHeart(ServerLevel level, BlockPos pos, int radius) {
        return nearbyHearts(level, pos, radius).stream().min(Comparator.comparingDouble(h -> h.getBlockPos().distSqr(pos))).orElse(null);
    }
    public static BlockPos nearestLoaded(ServerLevel level, Kind kind, BlockPos pos, int radius) {
        BlockPos best = null; double distance = Double.MAX_VALUE;
        for (BlockPos p : get(level).positions(kind, pos, radius)) {
            if (!level.hasChunkAt(p)) continue;
            BlockState state = level.getBlockState(p);
            boolean valid = switch(kind) {
                case INFECTION -> InfectionTickQueue.isInfectionSource(state);
                case EYE -> state.is(ModBlocks.HIVE_EYE.get());
                case POOL -> state.is(ModBlocks.STOMACH_POOL.get());
                case PILLAR -> state.is(ModBlocks.NERVE_PILLAR.get());
            };
            if (!valid) { get(level).put(kind, p, false); get(level).setDirty(); continue; }
            double d = p.distSqr(pos); if (d < distance) { best = p; distance = d; }
        }
        return best;
    }
    public static boolean shielded(ServerLevel level, BlockPos pos) {
        BlockPos pillar = nearestLoaded(level, Kind.PILLAR, pos, 32);
        if (pillar == null) return false;
        if (level.getBlockEntity(pillar) instanceof com.carnis.mod.block.entity.NervePillarBlockEntity organ) organ.discharge(level);
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/world/ModConfiguredFeatures.java`

```java
package com.carnis.mod.world;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModFeatures;
import net.minecraft.core.registries.Registries;
import net.minecraft.data.worldgen.BootstapContext;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** Optional data-generation bootstrap; runtime entries are provided by data JSON. */
public final class ModConfiguredFeatures {
    public static final ResourceKey<ConfiguredFeature<?, ?>> FLESH_NEST = key("flesh_nest");
    public static final ResourceKey<ConfiguredFeature<?, ?>> SPORE_POCKET = key("spore_pocket");
    private ModConfiguredFeatures() { }
    private static ResourceKey<ConfiguredFeature<?, ?>> key(String name) {
        return ResourceKey.create(Registries.CONFIGURED_FEATURE, new ResourceLocation(CarnisMod.MOD_ID, name));
    }
    public static void bootstrap(BootstapContext<ConfiguredFeature<?, ?>> context) {
        context.register(FLESH_NEST, new ConfiguredFeature<>(ModFeatures.FLESH_NEST.get(), NoneFeatureConfiguration.INSTANCE));
        context.register(SPORE_POCKET, new ConfiguredFeature<>(ModFeatures.SPORE_POCKET.get(), NoneFeatureConfiguration.INSTANCE));
    }
}
```

## `src/main/java/com/carnis/mod/world/ModPlacedFeatures.java`

```java
package com.carnis.mod.world;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.data.worldgen.BootstapContext;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.VerticalAnchor;
import net.minecraft.world.level.levelgen.placement.BiomeFilter;
import net.minecraft.world.level.levelgen.placement.HeightRangePlacement;
import net.minecraft.world.level.levelgen.placement.InSquarePlacement;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;
import net.minecraft.world.level.levelgen.placement.RarityFilter;
import java.util.List;

/** Optional data-generation bootstrap; matching JSON supplies the runtime registry. */
public final class ModPlacedFeatures {
    public static final ResourceKey<PlacedFeature> FLESH_NEST = key("flesh_nest");
    public static final ResourceKey<PlacedFeature> SPORE_POCKET = key("spore_pocket");
    private ModPlacedFeatures() { }
    private static ResourceKey<PlacedFeature> key(String name) {
        return ResourceKey.create(Registries.PLACED_FEATURE, new ResourceLocation(CarnisMod.MOD_ID, name));
    }
    public static void bootstrap(BootstapContext<PlacedFeature> context) {
        var configured = context.lookup(Registries.CONFIGURED_FEATURE);
        context.register(FLESH_NEST, new PlacedFeature(configured.getOrThrow(ModConfiguredFeatures.FLESH_NEST), List.of(
                RarityFilter.onAverageOnceEvery(32), InSquarePlacement.spread(),
                HeightRangePlacement.uniform(VerticalAnchor.absolute(-58), VerticalAnchor.absolute(-10)), BiomeFilter.biome())));
        context.register(SPORE_POCKET, new PlacedFeature(configured.getOrThrow(ModConfiguredFeatures.SPORE_POCKET), List.of(
                RarityFilter.onAverageOnceEvery(24), InSquarePlacement.spread(),
                HeightRangePlacement.uniform(VerticalAnchor.absolute(-30), VerticalAnchor.absolute(40)), BiomeFilter.biome())));
    }
}
```

## `src/main/java/com/carnis/mod/world/SubstratePlacer.java`

```java
package com.carnis.mod.world;

import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/** Seeds a horizontal, ground-level patch without loading chunks; only selected ground blocks are eligible. */
public final class SubstratePlacer {
    private SubstratePlacer() { }

    /** Returns the number of blocks newly converted. The center is a ground position. */
    public static int placePatch(ServerLevel level, BlockPos center) {
        return placePatch(level, center, 3);
    }

    /** Places an odd-width square, bounded to at most nine blocks per side. */
    public static int placePatch(ServerLevel level, BlockPos center, int width) {
        if (width < 1 || width > 9 || (width & 1) == 0) throw new IllegalArgumentException("width must be odd and between 1 and 9");
        if (!level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)) return 0;
        int placed = 0;
        int radius = width / 2;
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dz = -radius; dz <= radius; dz++) {
                BlockPos pos = center.offset(dx, 0, dz);
                if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) continue;
                BlockState state = level.getBlockState(pos);
                if (state.hasBlockEntity() || !state.getFluidState().isEmpty()
                        || state.getDestroySpeed(level, pos) < 0 || !isNaturalGround(state)) continue;
                if (level.setBlockAndUpdate(pos, ModBlocks.LIVING_FLESH.get().defaultBlockState())) placed++;
            }
        }
        return placed;
    }

    private static boolean isNaturalGround(BlockState state) {
        return state.is(BlockTags.DIRT) || state.is(Blocks.STONE) || state.is(Blocks.DEEPSLATE)
                || state.is(Blocks.SAND) || state.is(Blocks.RED_SAND) || state.is(Blocks.GRAVEL);
    }
}
```

## `src/main/java/com/carnis/mod/world/feature/FleshNestFeature.java`

```java
package com.carnis.mod.world.feature;

import com.carnis.mod.block.FleshBulbBlock;
import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.entity.BiomassMaggotEntity;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import java.util.ArrayList;
import java.util.List;

public final class FleshNestFeature extends Feature<NoneFeatureConfiguration> {
    private static final int MIN_Y = -58, MAX_Y = 0;
    public FleshNestFeature() { super(NoneFeatureConfiguration.CODEC); }
    @Override public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        RandomSource random = context.random();
        BlockPos origin = context.origin();
        // The center is fixed inside the placement chunk, leaving a one-block border.
        BlockPos center = new BlockPos((origin.getX() & ~15) + 7, origin.getY(), (origin.getZ() & ~15) + 7);
        int radius = 3 + random.nextInt(4);
        int vertical = Math.max(3, radius - 2);
        if (!preflight(level, center, radius, vertical)) return false;
        if (!level.setBlock(center, ModBlocks.PULSING_HEART.get().defaultBlockState(), 2)) return false;
        List<BlockPos> tissue = new ArrayList<>();
        for (int x = -radius; x <= radius; x++) for (int y = -vertical; y <= vertical; y++)
            for (int z = -radius; z <= radius; z++) {
                double d = ellipsoid(x, y, z, radius, vertical);
                if (d > 1.0D || x == 0 && y == 0 && z == 0) continue;
                BlockPos pos = center.offset(x, y, z);
                if (d >= .50D) {
                    BlockState flesh = random.nextInt(5) == 0 ? ModBlocks.OSSIFIED_FLESH.get().defaultBlockState()
                            : ModBlocks.LIVING_FLESH.get().defaultBlockState();
                    if (level.setBlock(pos, flesh, 2)) tissue.add(pos.immutable());
                } else level.setBlock(pos, Blocks.AIR.defaultBlockState(), 2);
            }
        List<BlockPos> ceiling = new ArrayList<>();
        List<BlockPos> floor = new ArrayList<>();
        for (int x = -radius + 1; x < radius; x++) for (int z = -radius + 1; z < radius; z++) {
            for (int y = 1; y <= vertical; y++) {
                BlockPos pos = center.offset(x, y, z), support = pos.above();
                if (OrganicFeatureUtil.inWindow(center, support) && OrganicFeatureUtil.safeHeight(level, support, MIN_Y, MAX_Y)
                        && level.getBlockState(pos).isAir()
                        && level.getBlockState(support).isFaceSturdy(level, support, Direction.DOWN)) {
                    ceiling.add(pos.immutable()); break;
                }
            }
            for (int y = -vertical + 1; y <= -1; y++) {
                BlockPos pos = center.offset(x, y, z), support = pos.below();
                if (OrganicFeatureUtil.inWindow(center, support) && OrganicFeatureUtil.safeHeight(level, support, MIN_Y, MAX_Y)
                        && level.getBlockState(pos).isAir()
                        && level.getBlockState(support).isFaceSturdy(level, support, Direction.UP)) {
                    floor.add(pos.immutable()); break;
                }
            }
        }
        OrganicFeatureUtil.shuffle(ceiling, random);
        int bulbs = 2 + random.nextInt(3), placedBulbs = 0;
        BlockState hanging = ModBlocks.FLESH_BULB.get().defaultBlockState()
                .setValue(FleshBulbBlock.HANGING, true).setValue(FleshBulbBlock.PULSING, false);
        for (BlockPos pos : ceiling) {
            if (placedBulbs >= bulbs) break;
            if (hanging.canSurvive(level, pos) && level.setBlock(pos, hanging, 2)) placedBulbs++;
        }
        OrganicFeatureUtil.shuffle(floor, random);
        int clusters = 1 + random.nextInt(3);
        List<BlockPos> centers = new ArrayList<>();
        List<BlockPos> spawnSites = new ArrayList<>();
        BlockState remains = ModBlocks.BIOMASS_REMAINS.get().defaultBlockState();
        for (BlockPos pos : floor) {
            if (centers.size() >= clusters) break;
            if (centers.stream().anyMatch(p -> p.distSqr(pos) < 5.0D) || !level.getBlockState(pos).isAir()
                    || !remains.canSurvive(level, pos) || !level.setBlock(pos, remains, 2)) continue;
            centers.add(pos); spawnSites.add(pos);
            for (Direction direction : Direction.Plane.HORIZONTAL) {
                BlockPos next = pos.relative(direction);
                if (!floor.contains(next) || !OrganicFeatureUtil.inWindow(center, next) || random.nextBoolean()
                        || !level.getBlockState(next).isAir() || !remains.canSurvive(level, next)) continue;
                if (level.setBlock(next, remains, 2)) spawnSites.add(next.immutable());
            }
        }
        for (BlockPos pos : floor) {
            if (spawnSites.size() >= 4) break;
            if (!spawnSites.contains(pos) && level.getBlockState(pos).isAir()) spawnSites.add(pos);
        }
        for (int x = -radius + 1; x < radius; x++) for (int y = -vertical + 1; y < vertical; y++)
            for (int z = -radius + 1; z < radius; z++) {
                BlockPos pos = center.offset(x, y, z);
                if (spawnSites.contains(pos) || spawnSites.contains(pos.below())
                        || random.nextInt(3) != 0 || !OrganicFeatureUtil.inWindow(center, pos)) continue;
                if (OrganicFeatureUtil.placeVein(level, center, pos, MIN_Y, MAX_Y)) tissue.add(pos.immutable());
            }
        if (level.getBlockEntity(center) instanceof PulsingHeartBlockEntity heart) heart.seedGeneratedTissue(tissue);
        spawnMaggots(level, random, center, spawnSites, 1 + random.nextInt(2));
        return true;
    }
    private static double ellipsoid(int x, int y, int z, int radius, int vertical) {
        return (x * x + z * z) / (double) (radius * radius) + y * y / (double) (vertical * vertical);
    }
    private static boolean preflight(WorldGenLevel level, BlockPos center, int radius, int vertical) {
        if (!OrganicFeatureUtil.safeHeight(level, center.offset(0, -vertical, 0), MIN_Y, MAX_Y)
                || !OrganicFeatureUtil.safeHeight(level, center.offset(0, vertical, 0), MIN_Y, MAX_Y)) return false;
        int deep = 0;
        int caveAir = 0;
        for (int x = -radius - 1; x <= radius + 1; x++) for (int z = -radius - 1; z <= radius + 1; z++) {
            BlockPos column = center.offset(x, 0, z);
            if (!OrganicFeatureUtil.inWindow(center, column)) continue;
            if (!OrganicFeatureUtil.covered(level, column.above(vertical), 8)) return false;
            for (int y = -vertical - 1; y <= vertical + 1; y++) {
                BlockPos pos = center.offset(x, y, z);
                if (level.isOutsideBuildHeight(pos)) return false;
                BlockState state = level.getBlockState(pos);
                if (!state.getFluidState().isEmpty()) return false;
                if (Math.abs(x) <= radius && Math.abs(z) <= radius && Math.abs(y) <= vertical
                        && ellipsoid(x, y, z, radius, vertical) <= 1.0D) {
                    if (!OrganicFeatureUtil.validNatural(state)) return false;
                    if (state.is(Blocks.DEEPSLATE)) deep++;
                    if (state.isAir() && ellipsoid(x, y, z, radius, vertical) < .50D) caveAir++;
                }
            }
        }
        return deep >= 20 && caveAir >= 4;
    }
    private static void spawnMaggots(WorldGenLevel level, RandomSource random, BlockPos center,
                                     List<BlockPos> sites, int count) {
        OrganicFeatureUtil.shuffle(sites, random);
        int placed = 0;
        for (BlockPos pos : sites) {
            if (placed >= count) break;
            BlockPos above = pos.above();
            if (!OrganicFeatureUtil.inWindow(center, pos) || !OrganicFeatureUtil.safeHeight(level, above, MIN_Y, MAX_Y)
                    || !level.getBlockState(above).isAir()) continue;
            BiomassMaggotEntity maggot = ModEntities.BIOMASS_MAGGOT.get().create(level.getLevel());
            if (maggot == null) continue;
            maggot.moveTo(pos.getX() + .5D, pos.getY(), pos.getZ() + .5D, random.nextFloat() * 360.0F, 0);
            maggot.setPersistenceRequired();
            if (level.addFreshEntity(maggot)) placed++;
        }
    }
}
```

## `src/main/java/com/carnis/mod/world/feature/OrganicFeatureUtil.java`

```java
package com.carnis.mod.world.feature;

import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import java.util.List;

/** All positions, including support reads, are restricted to the central chunk interior. */
public final class OrganicFeatureUtil {
    private OrganicFeatureUtil() { }
    public static boolean inWindow(BlockPos origin, BlockPos pos) {
        int minX = origin.getX() & ~15, minZ = origin.getZ() & ~15;
        int x = pos.getX() - minX, z = pos.getZ() - minZ;
        return x >= 1 && x <= 14 && z >= 1 && z <= 14;
    }
    public static boolean safeHeight(WorldGenLevel level, BlockPos pos, int minY, int maxY) {
        return pos.getY() >= minY && pos.getY() <= maxY && !level.isOutsideBuildHeight(pos);
    }
    public static boolean covered(WorldGenLevel level, BlockPos pos, int clearance) {
        return pos.getY() + clearance < level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, pos.getX(), pos.getZ());
    }
    public static boolean naturalStone(BlockState state) {
        return state.is(Blocks.STONE) || state.is(Blocks.DEEPSLATE) || state.is(Blocks.TUFF)
                || state.is(Blocks.GRANITE) || state.is(Blocks.DIORITE) || state.is(Blocks.ANDESITE);
    }
    public static boolean validNatural(BlockState state) {
        return !state.hasBlockEntity() && state.getFluidState().isEmpty() && (state.isAir() || naturalStone(state));
    }
    public static boolean placeVein(WorldGenLevel level, BlockPos origin, BlockPos pos, int minY, int maxY) {
        if (!inWindow(origin, pos) || !safeHeight(level, pos, minY, maxY)) return false;
        BlockState existing = level.getBlockState(pos);
        if (!existing.isAir() || !existing.getFluidState().isEmpty()) return false;
        BlockState vein = existing;
        for (Direction face : Direction.values()) {
            BlockPos support = pos.relative(face);
            if (!inWindow(origin, support) || !safeHeight(level, support, minY, maxY)) continue;
            if (!level.getBlockState(support).isFaceSturdy(level, support, face.getOpposite())) continue;
            BlockState next = ModBlocks.FLESH_VEINS.get().getStateForPlacement(vein, level, pos, face);
            if (next != null) vein = next;
        }
        return vein.is(ModBlocks.FLESH_VEINS.get()) && level.setBlock(pos, vein, 2);
    }
    public static <T> void shuffle(List<T> list, RandomSource random) {
        for (int i = list.size() - 1; i > 0; i--) {
            int j = random.nextInt(i + 1);
            T previous = list.get(i); list.set(i, list.get(j)); list.set(j, previous);
        }
    }
}
```

## `src/main/java/com/carnis/mod/world/feature/SporePocketFeature.java`

```java
package com.carnis.mod.world.feature;

import com.carnis.mod.block.FleshBulbBlock;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import java.util.ArrayList;
import java.util.List;

public final class SporePocketFeature extends Feature<NoneFeatureConfiguration> {
    private static final int MIN_Y = -30, MAX_Y = 40;
    public SporePocketFeature() { super(NoneFeatureConfiguration.CODEC); }
    @Override public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        RandomSource random = context.random();
        BlockPos origin = context.origin();
        int radius = 2 + random.nextInt(2);
        // Include a one-cell margin in the same chunk for support and fluid checks.
        if (!OrganicFeatureUtil.inWindow(origin, origin.offset(-radius - 1, 0, -radius - 1))
                || !OrganicFeatureUtil.inWindow(origin, origin.offset(radius + 1, 0, radius + 1))) return false;
        BlockPos floor = null;
        BlockPos ceiling = null;
        for (int dy = -4; dy <= 4 && floor == null; dy++) {
            BlockPos pos = origin.offset(0, dy, 0);
            if (!OrganicFeatureUtil.safeHeight(level, pos, MIN_Y, MAX_Y)
                    || !OrganicFeatureUtil.safeHeight(level, pos.below(), MIN_Y, MAX_Y)
                    || !level.getBlockState(pos).isAir() || !OrganicFeatureUtil.naturalStone(level.getBlockState(pos.below()))
                    || !level.getBlockState(pos.below()).isFaceSturdy(level, pos.below(), Direction.UP)) continue;
            for (int rise = 2; rise <= 7; rise++) {
                BlockPos candidate = pos.above(rise);
                if (!OrganicFeatureUtil.safeHeight(level, candidate.above(), MIN_Y, MAX_Y)) break;
                if (!level.getBlockState(candidate).isAir()) break;
                BlockPos support = candidate.above();
                if (OrganicFeatureUtil.naturalStone(level.getBlockState(support))
                        && level.getBlockState(support).isFaceSturdy(level, support, Direction.DOWN)) {
                    floor = pos.immutable(); ceiling = candidate.immutable(); break;
                }
            }
        }
        if (floor == null || ceiling == null || !OrganicFeatureUtil.covered(level, ceiling.above(), 8)) return false;
        List<BlockPos> patch = new ArrayList<>();
        for (int x = -radius - 1; x <= radius + 1; x++) for (int z = -radius - 1; z <= radius + 1; z++) {
            BlockPos column = floor.offset(x, 0, z);
            if (!OrganicFeatureUtil.inWindow(origin, column) || !OrganicFeatureUtil.covered(level, column.above(7), 4)) return false;
            for (int y = -1; y <= 7; y++) {
                BlockPos pos = column.above(y);
                if (!OrganicFeatureUtil.safeHeight(level, pos, MIN_Y, MAX_Y) || !level.getFluidState(pos).isEmpty()) return false;
            }
            if (x*x + z*z > radius*radius) continue;
            BlockPos ground = column.below();
            BlockState state = level.getBlockState(ground);
            if (OrganicFeatureUtil.naturalStone(state) && !state.hasBlockEntity() && state.getFluidState().isEmpty()
                    && level.getBlockState(column).isAir() && state.isFaceSturdy(level, ground, Direction.UP)) patch.add(ground.immutable());
        }
        if (patch.size() < 4) return false;
        BlockState bulb = ModBlocks.FLESH_BULB.get().defaultBlockState()
                .setValue(FleshBulbBlock.HANGING, true).setValue(FleshBulbBlock.PULSING, false);
        if (!bulb.canSurvive(level, ceiling) || !level.setBlock(ceiling, bulb, 2)) return false;
        for (BlockPos pos : patch) level.setBlock(pos, ModBlocks.LIVING_FLESH.get().defaultBlockState(), 2);
        for (BlockPos ground : patch) {
            BlockPos pos = ground.above();
            if (random.nextInt(3) != 0) OrganicFeatureUtil.placeVein(level, origin, pos, MIN_Y, MAX_Y);
        }
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/world/infection/InfectionTickQueue.java`

```java
package com.carnis.mod.world.infection;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.MultifaceBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class InfectionTickQueue {
    public static final int MAX_QUEUE_SIZE = 10000;
    public static final int HEART_CHUNK_PRIORITY_BUDGET = 4;

    private static final long HEART_ACTIVITY_LEASE_TICKS = 2L;
    private static final long FIREPROOF_ADAPTATION_THRESHOLD = 25L;
    private static final double FIREPROOF_BASE_CHANCE = 0.10D;
    private static final double FIREPROOF_CHANCE_PER_LEVEL = 0.01D;
    private static final double FIREPROOF_MAX_CHANCE = 0.75D;

    private static final Direction[] SPREAD_DIRECTIONS = Direction.values();

    private static final Map<MinecraftServer, InfectionTickQueue> INSTANCES =
            new WeakHashMap<>();

    private final Map<ResourceKey<Level>, LinkedHashSet<BlockPos>>
            queuedPositions = new LinkedHashMap<>();

    private final Map<ResourceKey<Level>, LinkedHashMap<Long, Long>>
            activeHeartChunks = new LinkedHashMap<>();

    private final LinkedHashSet<QueuedPosition> heartPriorityPositions =
            new LinkedHashSet<>();

    private int queuedPositionCount;

    private InfectionTickQueue() {
    }

    public static boolean enqueue(ServerLevel serverLevel, BlockPos pos) {
        if (!serverLevel.hasChunkAt(pos)) {
            return false;
        }

        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);
        ChunkPos chunkPos = new ChunkPos(pos);

        if (
                worldData.isChunkShocked(
                        chunkPos,
                        serverLevel.getGameTime()
                )
        ) {
            return false;
        }

        InfectionTickQueue manager = getOrCreate(serverLevel.getServer());
        return manager.enqueueInternal(
                serverLevel.dimension(),
                pos.immutable(),
                serverLevel.getGameTime()
        );
    }

    public static boolean refreshHeartChunk(
            ServerLevel serverLevel,
            BlockPos heartPos
    ) {
        if (!serverLevel.hasChunkAt(heartPos)) {
            return false;
        }

        ChunkPos heartChunk = new ChunkPos(heartPos);
        long currentGameTime = serverLevel.getGameTime();
        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);

        if (worldData.isChunkShocked(heartChunk, currentGameTime)) {
            InfectionTickQueue existingManager = getExisting(
                    serverLevel.getServer()
            );

            if (existingManager != null) {
                existingManager.deactivateHeartChunk(
                        serverLevel.dimension(),
                        heartChunk.toLong()
                );
            }

            return false;
        }

        InfectionTickQueue manager = getOrCreate(serverLevel.getServer());
        manager.refreshHeartChunkInternal(
                serverLevel.dimension(),
                heartChunk.toLong(),
                currentGameTime
        );
        return true;
    }

    public static int enqueueHeartPulse(
            ServerLevel serverLevel,
            BlockPos selectedFleshPos
    ) {
        if (
                !serverLevel.hasChunkAt(selectedFleshPos)
                        || !isInfectionSource(
                                serverLevel.getBlockState(selectedFleshPos)
                        )
        ) {
            return 0;
        }

        int enqueuedPositions = enqueue(
                serverLevel,
                selectedFleshPos
        ) ? 1 : 0;

        for (Direction direction : SPREAD_DIRECTIONS) {
            BlockPos adjacentPos = selectedFleshPos.relative(direction);

            if (
                    !serverLevel.isOutsideBuildHeight(adjacentPos)
                            && serverLevel.hasChunkAt(adjacentPos)
                            && isInfectionSource(
                                    serverLevel.getBlockState(adjacentPos)
                            )
                            && enqueue(serverLevel, adjacentPos)
            ) {
                enqueuedPositions++;
            }
        }

        return enqueuedPositions;
    }

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }

        InfectionTickQueue manager = getExisting(event.getServer());

        if (manager == null) {
            return;
        }

        manager.processQueuedPositions(
                event.getServer(),
                CarnisConfig.SERVER.infectionBlocksPerTick.get()
        );
    }

    @SubscribeEvent
    public static void onServerStopped(ServerStoppedEvent event) {
        synchronized (INSTANCES) {
            INSTANCES.remove(event.getServer());
        }
    }

    private static InfectionTickQueue getOrCreate(MinecraftServer server) {
        synchronized (INSTANCES) {
            return INSTANCES.computeIfAbsent(
                    server,
                    ignored -> new InfectionTickQueue()
            );
        }
    }

    private static InfectionTickQueue getExisting(MinecraftServer server) {
        synchronized (INSTANCES) {
            return INSTANCES.get(server);
        }
    }

    private boolean enqueueInternal(
            ResourceKey<Level> dimension,
            BlockPos pos,
            long currentGameTime
    ) {
        LinkedHashSet<BlockPos> dimensionQueue = queuedPositions.get(
                dimension
        );
        QueuedPosition queuedPosition = new QueuedPosition(dimension, pos);

        if (dimensionQueue != null && dimensionQueue.contains(pos)) {
            prioritizeIfHeartActive(queuedPosition, currentGameTime);
            return false;
        }

        if (queuedPositionCount >= MAX_QUEUE_SIZE) {
            return false;
        }

        if (dimensionQueue == null) {
            dimensionQueue = new LinkedHashSet<>();
            queuedPositions.put(dimension, dimensionQueue);
        }

        if (!dimensionQueue.add(pos)) {
            return false;
        }

        queuedPositionCount++;
        prioritizeIfHeartActive(queuedPosition, currentGameTime);
        return true;
    }

    private void refreshHeartChunkInternal(
            ResourceKey<Level> dimension,
            long chunkKey,
            long currentGameTime
    ) {
        LinkedHashMap<Long, Long> dimensionHeartChunks =
                activeHeartChunks.computeIfAbsent(
                        dimension,
                        ignored -> new LinkedHashMap<>()
                );
        Long previousExpiration = dimensionHeartChunks.put(
                chunkKey,
                currentGameTime + HEART_ACTIVITY_LEASE_TICKS
        );

        if (
                previousExpiration != null
                        && previousExpiration >= currentGameTime
        ) {
            return;
        }

        LinkedHashSet<BlockPos> dimensionQueue = queuedPositions.get(
                dimension
        );

        if (dimensionQueue == null) {
            return;
        }

        for (BlockPos queuedPos : dimensionQueue) {
            if (new ChunkPos(queuedPos).toLong() == chunkKey) {
                heartPriorityPositions.add(
                        new QueuedPosition(dimension, queuedPos)
                );
            }
        }
    }

    private void deactivateHeartChunk(
            ResourceKey<Level> dimension,
            long chunkKey
    ) {
        LinkedHashMap<Long, Long> dimensionHeartChunks =
                activeHeartChunks.get(dimension);

        if (
                dimensionHeartChunks == null
                        || dimensionHeartChunks.remove(chunkKey) == null
        ) {
            return;
        }

        if (dimensionHeartChunks.isEmpty()) {
            activeHeartChunks.remove(dimension);
        }

        removeHeartPrioritiesForChunk(dimension, chunkKey);
    }

    private void prioritizeIfHeartActive(
            QueuedPosition queuedPosition,
            long currentGameTime
    ) {
        long chunkKey = new ChunkPos(queuedPosition.pos()).toLong();

        if (
                isHeartChunkActive(
                        queuedPosition.dimension(),
                        chunkKey,
                        currentGameTime
                )
        ) {
            heartPriorityPositions.add(queuedPosition);
        }
    }

    private boolean isHeartChunkActive(
            ResourceKey<Level> dimension,
            long chunkKey,
            long currentGameTime
    ) {
        Map<Long, Long> dimensionHeartChunks = activeHeartChunks.get(
                dimension
        );

        if (dimensionHeartChunks == null) {
            return false;
        }

        Long expirationGameTime = dimensionHeartChunks.get(chunkKey);
        return expirationGameTime != null
                && expirationGameTime >= currentGameTime;
    }

    private void expireInactiveHeartChunks(MinecraftServer server) {
        Iterator<Map.Entry<ResourceKey<Level>, LinkedHashMap<Long, Long>>>
                dimensionIterator = activeHeartChunks.entrySet().iterator();

        while (dimensionIterator.hasNext()) {
            Map.Entry<ResourceKey<Level>, LinkedHashMap<Long, Long>> entry =
                    dimensionIterator.next();
            ServerLevel serverLevel = server.getLevel(entry.getKey());

            if (serverLevel == null) {
                ResourceKey<Level> missingDimension = entry.getKey();
                dimensionIterator.remove();
                heartPriorityPositions.removeIf(
                        queuedPosition -> queuedPosition.dimension().equals(
                                missingDimension
                        )
                );
                continue;
            }

            long currentGameTime = serverLevel.getGameTime();
            Iterator<Map.Entry<Long, Long>> chunkIterator =
                    entry.getValue().entrySet().iterator();

            while (chunkIterator.hasNext()) {
                Map.Entry<Long, Long> chunkEntry = chunkIterator.next();

                if (chunkEntry.getValue() < currentGameTime) {
                    long expiredChunkKey = chunkEntry.getKey();
                    chunkIterator.remove();
                    removeHeartPrioritiesForChunk(
                            entry.getKey(),
                            expiredChunkKey
                    );
                }
            }

            if (entry.getValue().isEmpty()) {
                dimensionIterator.remove();
            }
        }
    }

    private void removeHeartPrioritiesForChunk(
            ResourceKey<Level> dimension,
            long chunkKey
    ) {
        heartPriorityPositions.removeIf(
                queuedPosition -> queuedPosition.dimension().equals(dimension)
                        && new ChunkPos(queuedPosition.pos()).toLong()
                        == chunkKey
        );
    }

    private void processQueuedPositions(
            MinecraftServer server,
            int maxPositions
    ) {
        expireInactiveHeartChunks(server);

        if (maxPositions <= 0 || queuedPositionCount == 0) {
            return;
        }

        List<QueuedPosition> batch = drainBatch(server, maxPositions);

        for (QueuedPosition queuedPosition : batch) {
            ServerLevel serverLevel = server.getLevel(
                    queuedPosition.dimension()
            );

            if (serverLevel != null) {
                processPosition(serverLevel, queuedPosition.pos());
            }
        }
    }

    private List<QueuedPosition> drainBatch(
            MinecraftServer server,
            int maxPositions
    ) {
        List<QueuedPosition> batch = new ArrayList<>(
                Math.min(maxPositions, queuedPositionCount)
        );

        drainHeartPriorityPositions(
                server,
                batch,
                Math.min(HEART_CHUNK_PRIORITY_BUDGET, maxPositions)
        );

        while (
                batch.size() < maxPositions
                        && queuedPositionCount > 0
                        && !queuedPositions.isEmpty()
        ) {
            boolean removedPositionThisPass = false;
            Iterator<Map.Entry<ResourceKey<Level>, LinkedHashSet<BlockPos>>>
                    dimensionIterator = queuedPositions.entrySet().iterator();

            while (
                    dimensionIterator.hasNext()
                            && batch.size() < maxPositions
            ) {
                Map.Entry<ResourceKey<Level>, LinkedHashSet<BlockPos>> entry =
                        dimensionIterator.next();
                LinkedHashSet<BlockPos> dimensionQueue = entry.getValue();

                if (server.getLevel(entry.getKey()) == null) {
                    ResourceKey<Level> missingDimension = entry.getKey();
                    queuedPositionCount -= dimensionQueue.size();
                    dimensionIterator.remove();
                    heartPriorityPositions.removeIf(
                            queuedPosition -> queuedPosition.dimension().equals(
                                    missingDimension
                            )
                    );
                    continue;
                }

                Iterator<BlockPos> positionIterator =
                        dimensionQueue.iterator();

                if (positionIterator.hasNext()) {
                    BlockPos pos = positionIterator.next();
                    QueuedPosition queuedPosition = new QueuedPosition(
                            entry.getKey(),
                            pos
                    );
                    positionIterator.remove();
                    heartPriorityPositions.remove(queuedPosition);
                    queuedPositionCount--;
                    removedPositionThisPass = true;
                    batch.add(queuedPosition);
                }

                if (dimensionQueue.isEmpty()) {
                    dimensionIterator.remove();
                }
            }

            if (!removedPositionThisPass) {
                break;
            }
        }

        return batch;
    }

    private void drainHeartPriorityPositions(
            MinecraftServer server,
            List<QueuedPosition> batch,
            int priorityBudget
    ) {
        Iterator<QueuedPosition> priorityIterator =
                heartPriorityPositions.iterator();

        while (
                priorityIterator.hasNext()
                        && batch.size() < priorityBudget
        ) {
            QueuedPosition queuedPosition = priorityIterator.next();
            ServerLevel serverLevel = server.getLevel(
                    queuedPosition.dimension()
            );
            LinkedHashSet<BlockPos> dimensionQueue = queuedPositions.get(
                    queuedPosition.dimension()
            );
            long chunkKey = new ChunkPos(queuedPosition.pos()).toLong();

            if (
                    serverLevel == null
                            || dimensionQueue == null
                            || !isHeartChunkActive(
                                    queuedPosition.dimension(),
                                    chunkKey,
                                    serverLevel.getGameTime()
                            )
                            || !dimensionQueue.remove(queuedPosition.pos())
            ) {
                priorityIterator.remove();
                continue;
            }

            priorityIterator.remove();
            queuedPositionCount--;
            batch.add(queuedPosition);

            if (dimensionQueue.isEmpty()) {
                queuedPositions.remove(queuedPosition.dimension());
            }
        }
    }

    // Vein propagation and mutation are exclusively driven by block random ticks.
    private void processPosition(ServerLevel serverLevel, BlockPos sourcePos) {
    }

    public static boolean isInfectionSource(BlockState state) {
        return state.is(ModBlocks.LIVING_FLESH.get())
                || state.is(ModBlocks.OSSIFIED_FLESH.get())
                || state.is(ModBlocks.FIREPROOF_FLESH.get())
                || state.is(ModBlocks.FLESH_VEINS.get());
    }

    private static BlockState getInfectedState(
            ServerLevel serverLevel,
            CarnisWorldData worldData,
            BlockState targetState
    ) {
        if (targetState.is(Blocks.GRASS_BLOCK)
                || targetState.is(Blocks.DIRT)
                || targetState.is(Blocks.STONE)
                || targetState.is(Blocks.DEEPSLATE)) {
            return selectFleshState(serverLevel, worldData);
        }

        if (targetState.is(BlockTags.LOGS)) {
            return null;
        }

        if (targetState.canBeReplaced() && targetState.getFluidState().isEmpty()) {
            return ModBlocks.LIVING_FLESH.get().defaultBlockState();
        }

        return null;
    }

    private static BlockState selectFleshState(
            ServerLevel serverLevel,
            CarnisWorldData worldData
    ) {
        long fireAdaptation = worldData.getFireAdaptation();

        if (fireAdaptation < FIREPROOF_ADAPTATION_THRESHOLD) {
            return ModBlocks.LIVING_FLESH.get().defaultBlockState();
        }

        double fireproofChance = Math.min(
                FIREPROOF_MAX_CHANCE,
                FIREPROOF_BASE_CHANCE
                        + (fireAdaptation - FIREPROOF_ADAPTATION_THRESHOLD)
                        * FIREPROOF_CHANCE_PER_LEVEL
        );

        if (serverLevel.getRandom().nextDouble() < fireproofChance) {
            return ModBlocks.FIREPROOF_FLESH.get().defaultBlockState();
        }

        return ModBlocks.LIVING_FLESH.get().defaultBlockState();
    }

    private record QueuedPosition(
            ResourceKey<Level> dimension,
            BlockPos pos
    ) {
    }
}
```

## `src/main/java/com/carnis/mod/world/infection/VeinMutationEngine.java`

```java
package com.carnis.mod.world.infection;

import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.MultifaceBlock;
import net.minecraft.world.level.block.state.BlockState;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.WeakHashMap;

/** Bounded, random-tick-driven vein growth and observed-coverage mutation. */
public final class VeinMutationEngine {
    private static final int ANCHOR_RADIUS = 4;
    private static final long MUTATION_TICKS = 200L;
    private static final long BIOMASS_COST = 5L;
    private static final int MAX_TRACKED = 10000;
    private static final Direction[] DIRECTIONS = Direction.values();
    private static final Map<net.minecraft.server.MinecraftServer, LinkedHashMap<Key, Observation>> TRACKED = new WeakHashMap<>();

    private VeinMutationEngine() { }

    private record Key(ResourceKey<Level> dimension, BlockPos pos) { }
    private record Observation(BlockState host, int faces, long since) { }
    private enum Anchor { FOUND, MISSING, UNKNOWN }

    public static void tickVein(ServerLevel level, BlockPos pos, BlockState state, RandomSource random) {
        Anchor anchor = findAnchor(level, pos);
        if (anchor == Anchor.MISSING) {
            level.removeBlock(pos, false);
            return;
        }
        if (anchor != Anchor.FOUND || shocked(level, pos)) return;
        for (Direction direction : DIRECTIONS) {
            if (MultifaceBlock.hasFace(state, direction)) {
                BlockPos host = pos.relative(direction);
                if (loaded(level, host)) observeHost(level, host);
            }
        }
        spread(level, pos, random);
    }

    /** Called by a flesh block's random tick to seed veins on neighboring hosts. */
    public static void tickFlesh(ServerLevel level, BlockPos pos, RandomSource random) {
        if (!shocked(level, pos)) spread(level, pos, random);
    }

    private static void observeHost(ServerLevel level, BlockPos hostPos) {
        var map = TRACKED.computeIfAbsent(level.getServer(), ignored -> new LinkedHashMap<>());
        Key key = new Key(level.dimension(), hostPos.immutable());
        BlockState host = level.getBlockState(hostPos);
        int faces = 0;
        boolean complete = true;
        for (Direction direction : DIRECTIONS) {
            BlockPos outside = hostPos.relative(direction);
            if (!loaded(level, outside)) { complete = false; continue; }
            BlockState vein = level.getBlockState(outside);
            if (vein.is(ModBlocks.FLESH_VEINS.get()) && MultifaceBlock.hasFace(vein, direction.getOpposite()))
                faces |= 1 << direction.ordinal();
        }
        if (!complete || faces == 0 || !eligibleHost(level, hostPos, host) || shocked(level, hostPos)) {
            map.remove(key);
            return;
        }
        long now = level.getGameTime();
        Observation old = map.get(key);
        if (old == null || !old.host().equals(host) || old.faces() != faces || now < old.since()) {
            if (old == null && map.size() >= MAX_TRACKED) map.remove(map.keySet().iterator().next());
            map.put(key, new Observation(host, faces, now));
            return;
        }
        if (now - old.since() < MUTATION_TICKS) return;
        CarnisWorldData data = CarnisWorldData.get(level);
        if (!data.tryConsumeBiomassPoints(BIOMASS_COST)) return;
        BlockState replacement = data.getFireAdaptation() >= 300L
                ? ModBlocks.OSSIFIED_FLESH.get().defaultBlockState()
                : ModBlocks.LIVING_FLESH.get().defaultBlockState();
        if (level.setBlockAndUpdate(hostPos, replacement)) {
            map.remove(key);
            ModMessages.sendToPlayersInLevel(level);
        } else {
            data.addBiomassPoints(BIOMASS_COST);
        }
    }

    private static void spread(ServerLevel level, BlockPos source, RandomSource random) {
        int start = random.nextInt(6);
        for (int i = 0; i < 6; i++) {
            BlockPos hostPos = source.relative(DIRECTIONS[(start + i) % 6]);
            if (!loaded(level, hostPos) || shocked(level, hostPos)) continue;
            BlockState host = level.getBlockState(hostPos);
            if (!eligibleHost(level, hostPos, host)) continue;
            int first = random.nextInt(6);
            for (int j = 0; j < 6; j++) {
                Direction face = DIRECTIONS[(first + j) % 6];
                BlockPos outside = hostPos.relative(face);
                if (!loaded(level, outside) || shocked(level, outside) || findAnchor(level, outside) != Anchor.FOUND) continue;
                BlockState existing = level.getBlockState(outside);
                if (forbidden(existing)) continue;
                boolean vein = existing.is(ModBlocks.FLESH_VEINS.get());
                if (!vein && !existing.isAir() && (existing.isSolidRender(level, outside) || !existing.canBeReplaced())) continue;
                BlockState placementBase = vein ? existing : Blocks.AIR.defaultBlockState();
                BlockState result = ModBlocks.FLESH_VEINS.get().getStateForPlacement(
                        placementBase, level, outside, face.getOpposite());
                if (result != null && !result.equals(existing) && level.setBlockAndUpdate(outside, result)) return;
            }
        }
    }

    private static boolean eligibleHost(ServerLevel level, BlockPos pos, BlockState state) {
        float hardness = state.getDestroySpeed(level, pos);
        return !forbidden(state) && !state.isAir() && !state.hasBlockEntity()
                && !InfectionTickQueue.isInfectionSource(state) && state.isSolidRender(level, pos)
                && hardness >= 0.0F && hardness <= 5.0F;
    }

    private static boolean forbidden(BlockState state) {
        return state.is(BlockTags.FIRE) || state.is(BlockTags.PORTALS)
                || state.getBlock() instanceof LiquidBlock || !state.getFluidState().isEmpty();
    }

    private static boolean loaded(ServerLevel level, BlockPos pos) {
        return !level.isOutsideBuildHeight(pos) && level.hasChunkAt(pos);
    }

    private static boolean shocked(ServerLevel level, BlockPos pos) {
        return CarnisWorldData.get(level).isChunkShocked(new ChunkPos(pos), level.getGameTime());
    }

    private static Anchor findAnchor(ServerLevel level, BlockPos center) {
        boolean unknown = false;
        for (int dx = -ANCHOR_RADIUS; dx <= ANCHOR_RADIUS; dx++) {
            for (int dy = -ANCHOR_RADIUS; dy <= ANCHOR_RADIUS; dy++) {
                for (int dz = -ANCHOR_RADIUS; dz <= ANCHOR_RADIUS; dz++) {
                    if (Math.abs(dx) + Math.abs(dy) + Math.abs(dz) > ANCHOR_RADIUS) continue;
                    BlockPos pos = center.offset(dx, dy, dz);
                    if (level.isOutsideBuildHeight(pos)) continue;
                    if (!level.hasChunkAt(pos)) { unknown = true; continue; }
                    BlockState state = level.getBlockState(pos);
                    if (state.is(ModBlocks.LIVING_FLESH.get()) && state.isSolidRender(level, pos)) return Anchor.FOUND;
                }
            }
        }
        return unknown ? Anchor.UNKNOWN : Anchor.MISSING;
    }
}
```
