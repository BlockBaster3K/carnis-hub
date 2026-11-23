# Шаг 20 — полный код и ресурсы

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
    private static void contact(Level level, BlockPos pos, Entity entity) {
        if (!(level instanceof ServerLevel server) || !(entity instanceof LivingEntity living) || !living.isAlive()
                || living.isSpectator() || NeuralMossBlock.isHive(living) || NeuroArmorEventHandler.hasFullSet(living)) return;
        if (living.getBoundingBox().minY > pos.getY() + 10.0D / 16.0D + .05D) return;
        burst(server, pos);
    }
    @Override public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        super.stepOn(level, pos, state, entity); contact(level, pos, entity);
    }
    @Override public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity); contact(level, pos, entity);
    }
    @Override public void onProjectileHit(Level level, BlockState state, BlockHitResult hit, Projectile projectile) {
        if (level instanceof ServerLevel server && projectile.mayInteract(level, hit.getBlockPos())) burst(server, hit.getBlockPos());
    }
    public static boolean burst(ServerLevel level, BlockPos pos) {
        BlockState current = level.getBlockState(pos);
        if (!ready(current)) return false;
        BlockState remains = ModBlocks.BIOMASS_REMAINS.get().defaultBlockState();
        BlockState after = level.random.nextFloat() < .4F && remains.canSurvive(level, pos)
                ? remains : current.setValue(BURST, true);
        // Commit the inert state first to prevent re-entrant detonations.
        if (!level.setBlock(pos, after, 3)) return false;
        double x = pos.getX() + .5D, y = pos.getY() + .5D, z = pos.getZ() + .5D;
        level.playSound(null, pos, ModSounds.ACID_SPLASH.get(), SoundSource.BLOCKS, 1F, .75F);
        level.sendParticles(ParticleTypes.SNEEZE, x, y, z, 45, .8, .55, .8, .12);
        level.sendParticles(ModParticles.BIOMASS_SPARK.get(), x, y, z, 35, .8, .55, .8, .12);
        level.sendParticles(ParticleTypes.ENTITY_EFFECT, x, y, z, 25, .7, .5, .7, .06);
        for (LivingEntity living : level.getEntitiesOfClass(LivingEntity.class, new AABB(x - 3, y - 3, z - 3, x + 3, y + 3, z + 3),
                e -> e.isAlive() && !e.isSpectator() && e.distanceToSqr(x, y, z) <= 9.0D)) {
            living.hurt(level.damageSources().magic(), 6F);
            if (!living.isAlive()) continue;
            living.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 0));
            if (living instanceof Player player) PlayerInfectionApi.addInfection(player, 15F);
        }
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/block/entity/PustuleClusterBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.block.PustuleClusterBlock;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
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
    private static final RawAnimation EMPTY = RawAnimation.begin().thenLoop("animation.pustule_cluster.burst");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    public PustuleClusterBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.PUSTULE_CLUSTER.get(), pos, state); }
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

## `src/main/java/com/carnis/mod/block/SporeSproutBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.event.NeuroArmorEventHandler;
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
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

public final class SporeSproutBlock extends BushBlock {
    public static final BooleanProperty CLOSED = BooleanProperty.create("closed");
    private static final VoxelShape SHAPE = Block.box(4, 0, 4, 12, 14, 12);
    public SporeSproutBlock(BlockBehaviour.Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(CLOSED, false));
    }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) { builder.add(CLOSED); }
    @Override protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
        return state.is(ModBlockTags.INFECTIOUS_SURFACES) || super.mayPlaceOn(state, level, pos);
    }
    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) { return SHAPE; }
    @Override public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) { return SHAPE; }
    @Override public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(5) == 0) level.addParticle(ParticleTypes.CRIMSON_SPORE,
                pos.getX() + random.nextDouble(), pos.getY() + .4D, pos.getZ() + random.nextDouble(), 0, .01D, 0);
    }
    @Override public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        if (!(level instanceof ServerLevel server) || !(entity instanceof Player player) || !player.isAlive()
                || player.isSpectator() || NeuroArmorEventHandler.hasFullSet(player) || state.getValue(CLOSED)) return;
        if (!server.setBlock(pos, state.setValue(CLOSED, true), 3)) return;
        server.scheduleTick(pos, this, 40);
        server.playSound(null, pos, ModSounds.ORGANIC_CREAK.get(), SoundSource.BLOCKS, .7F, 1.2F);
        server.sendParticles(ParticleTypes.SNEEZE, pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D,
                25, .35D, .35D, .35D, .06D);
        server.sendParticles(ModParticles.BIOMASS_SPARK.get(), pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D,
                10, .2D, .3D, .2D, .04D);
        player.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 80, 0));
        PlayerInfectionApi.addExposure(player, 5F);
    }
    @Override public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (state.getValue(CLOSED)) level.setBlock(pos, state.setValue(CLOSED, false), 3);
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

## `src/main/java/com/carnis/mod/init/ModBlockEntities.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.HiveEyeBlockEntity;
import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
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

    private ModBlockEntities() {
    }

    public static void register(IEventBus modEventBus) {
        BLOCK_ENTITY_TYPES.register(modEventBus);
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

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
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
                    BlockBehaviour.Properties.copy(Blocks.WATER).noLootTable()));

    public static final RegistryObject<com.carnis.mod.block.FleshVeinsBlock> FLESH_VEINS = BLOCKS.register(
            "flesh_veins", () -> new com.carnis.mod.block.FleshVeinsBlock(
                    BlockBehaviour.Properties.copy(Blocks.GLOW_LICHEN).randomTicks()));

    public static final RegistryObject<Block> BIOMASS_REMAINS = BLOCKS.register("biomass_remains",
            () -> new com.carnis.mod.block.BiomassRemainsBlock(BlockBehaviour.Properties.of()
                    .noCollission().noOcclusion().strength(0.2F).sound(SoundType.SLIME_BLOCK)));

    public static final RegistryObject<Block> FLESH_BULB = BLOCKS.register("flesh_bulb",
            () -> new com.carnis.mod.block.FleshBulbBlock(BlockBehaviour.Properties.copy(Blocks.CRIMSON_ROOTS)
                    .noCollission().noOcclusion().sound(SoundType.SLIME_BLOCK)));
    public static final RegistryObject<Block> SINEW_SPIKES = BLOCKS.register("sinew_spikes",
            () -> new com.carnis.mod.block.SinewSpikesBlock(BlockBehaviour.Properties.copy(Blocks.STONE)
                    .noOcclusion().strength(0.5F).sound(SoundType.BONE_BLOCK)));

    public static final RegistryObject<Block> NERVE_PILLAR = BLOCKS.register(
            "nerve_pillar", () -> new NervePillarBlock(BlockBehaviour.Properties.of()
                    .noOcclusion().strength(2.0F).sound(SoundType.SLIME_BLOCK).randomTicks()));

    public static final RegistryObject<Block> CREEPING_TENDRILS = BLOCKS.register(
            "creeping_tendrils", () -> new CreepingTendrilsBlock(BlockBehaviour.Properties.copy(Blocks.LADDER).sound(SoundType.SLIME_BLOCK)));
    public static final RegistryObject<Block> PUSTULE_CLUSTER = BLOCKS.register(
            "pustule_cluster", () -> new PustuleClusterBlock(BlockBehaviour.Properties.copy(Blocks.STONE)
                    .noOcclusion().strength(0.5F).sound(SoundType.SLIME_BLOCK).randomTicks()
                    .lightLevel(state -> !state.getValue(PustuleClusterBlock.BURST) && state.getValue(PustuleClusterBlock.AGE) == 3 ? 5 : 0)));
    public static final RegistryObject<Block> STOMACH_POOL = BLOCKS.register(
            "stomach_pool", () -> new StomachPoolBlock(BlockBehaviour.Properties.of()
                    .noOcclusion().strength(0.5F).sound(SoundType.SLIME_BLOCK).randomTicks()));

    public static final RegistryObject<Block> SPORE_SPROUT = BLOCKS.register(
            "spore_sprout", () -> new SporeSproutBlock(
                    BlockBehaviour.Properties.copy(Blocks.STONE).noOcclusion().strength(0.2F).sound(SoundType.GRASS)));
    public static final RegistryObject<Block> NEURAL_MOSS = BLOCKS.register(
            "neural_moss", () -> new NeuralMossBlock(
                    BlockBehaviour.Properties.copy(Blocks.MOSS_CARPET).randomTicks()));

    public static final RegistryObject<Block> CHARRED_FLESH = BLOCKS.register(
            "charred_flesh",
            () -> new Block(BlockBehaviour.Properties.copy(Blocks.BASALT).strength(1.5F))
    );

    public static final RegistryObject<Block> LIVING_FLESH = BLOCKS.register(
            "living_flesh",
            () -> new FleshBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_RED)
                    .strength(0.8F, 1.5F)
                    .sound(SoundType.SLIME_BLOCK)
                    .randomTicks())
    );

    public static final RegistryObject<Block> OSSIFIED_FLESH = BLOCKS.register(
            "ossified_flesh",
            () -> new FleshBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.SAND)
                    .strength(3.0F, 6.0F)
                    .sound(SoundType.BONE_BLOCK)
                    .requiresCorrectToolForDrops()
                    .randomTicks())
    );

    public static final RegistryObject<Block> FIREPROOF_FLESH = BLOCKS.register(
            "fireproof_flesh",
            () -> new FleshBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_BLACK)
                    .strength(4.0F, 12.0F)
                    .sound(SoundType.NETHER_WART)
                    .requiresCorrectToolForDrops()
                    .randomTicks())
    );

    public static final RegistryObject<Block> PULSING_HEART = BLOCKS.register(
            "pulsing_heart",
            () -> new PulsingHeartBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_RED)
                    .strength(2.5F, 6.0F)
                    .sound(SoundType.NETHER_WART)
                    .lightLevel(state -> 9)
                    .noOcclusion())
    );

    public static final RegistryObject<Block> HIVE_EYE = BLOCKS.register(
            "hive_eye",
            () -> new HiveEyeBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_RED)
                    .strength(1.6F, 3.0F)
                    .sound(SoundType.SLIME_BLOCK)
                    .lightLevel(state -> 6))
    );

    private ModBlocks() {
    }

    public static void register(IEventBus modEventBus) {
        BLOCKS.register(modEventBus);
    }
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
            () -> new Item(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<Item> PURIFICATION_DART = ITEMS.register("purification_dart",
            () -> new Item(new Item.Properties().stacksTo(64)));
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

## `src/main/java/com/carnis/mod/client/ClientModEvents.java`

```java
package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.gui.InfectionVeinsOverlay;
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
        event.registerEntityRenderer(ModEntities.VIRAL_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.PURIFICATION_DART.get(), DartRenderer::new);
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
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "neuro_resonance", new com.carnis.mod.client.gui.overlay.NeuroResonanceOverlay());
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/OrganItemRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.block.entity.NervePillarBlockEntity;
import com.carnis.mod.block.entity.StomachPoolBlockEntity;
import com.carnis.mod.init.ModBlocks;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

public final class OrganItemRenderer extends BlockEntityWithoutLevelRenderer {
    private StomachPoolBlockEntity pool;
    private NervePillarBlockEntity pillar;
    private com.carnis.mod.block.entity.PustuleClusterBlockEntity pustule;
    public OrganItemRenderer() { super(Minecraft.getInstance().getBlockEntityRenderDispatcher(), Minecraft.getInstance().getEntityModels()); }
    @Override public void renderByItem(ItemStack stack, ItemDisplayContext context, PoseStack pose,
                                       MultiBufferSource buffers, int light, int overlay) {
        if (!(stack.getItem() instanceof BlockItem item)) return;
        var dispatcher = Minecraft.getInstance().getBlockEntityRenderDispatcher();
        if (item.getBlock() == ModBlocks.STOMACH_POOL.get()) {
            if (pool == null) pool = new StomachPoolBlockEntity(BlockPos.ZERO, ModBlocks.STOMACH_POOL.get().defaultBlockState());
            Minecraft.getInstance().getBlockRenderer().renderSingleBlock(pool.getBlockState(), pose, buffers, light, overlay);
            dispatcher.renderItem(pool, pose, buffers, light, overlay);
        } else if (item.getBlock() == ModBlocks.PUSTULE_CLUSTER.get()) {
            if (pustule == null) pustule = new com.carnis.mod.block.entity.PustuleClusterBlockEntity(BlockPos.ZERO, ModBlocks.PUSTULE_CLUSTER.get().defaultBlockState());
            dispatcher.renderItem(pustule, pose, buffers, light, overlay);
        } else if (item.getBlock() == ModBlocks.NERVE_PILLAR.get()) {
            if (pillar == null) pillar = new NervePillarBlockEntity(BlockPos.ZERO, ModBlocks.NERVE_PILLAR.get().defaultBlockState());
            dispatcher.renderItem(pillar, pose, buffers, light, overlay);
        }
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
        withExistingParent("stomach_pool", new ResourceLocation("minecraft", "builtin/entity"));
        withExistingParent("nerve_pillar", new ResourceLocation("minecraft", "builtin/entity"));
        // Standard cube block items
        blockItem(ModBlocks.LIVING_FLESH);
        blockItem(ModBlocks.OSSIFIED_FLESH);
        blockItem(ModBlocks.CHARRED_FLESH);
        blockItem(ModBlocks.FIREPROOF_FLESH);
        withExistingParent("pustule_cluster", new ResourceLocation("minecraft", "builtin/entity"));

        // 2D flat item representation for Geo & organic hazard block items
        flatBlockItem(ModBlocks.SPORE_SPROUT);
        // Flesh bulb, moss, spikes, and remains item models are hand-authored in main resources.
        flatBlockItem(ModBlocks.CREEPING_TENDRILS);
        flatBlockItem(ModBlocks.FLESH_VEINS);

        // Standard flat items
        flatItem(ModItems.VIRAL_DART);
        flatItem(ModItems.PURIFICATION_DART);
        flatItem(ModItems.PURIFICATION_SERUM);
        flatItem(ModItems.NEURAL_BINDING_MATRIX);
        flatItem(ModItems.TAINTED_SLUDGE_BUCKET);
        flatItem(ModItems.FLESH_AMALGAM_SPAWN_EGG);
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

## `src/main/resources/assets/carnis/geo/block/pustule_cluster.geo.json`

```json
{
  "format_version": "1.12.0",
  "minecraft:geometry": [
    {
      "description": {
        "identifier": "geometry.carnis.pustule_cluster",
        "texture_width": 64,
        "texture_height": 64,
        "visible_bounds_width": 2,
        "visible_bounds_height": 2,
        "visible_bounds_offset": [
          0,
          0.5,
          0
        ]
      },
      "bones": [
        {
          "name": "root",
          "pivot": [
            0,
            0,
            0
          ]
        },
        {
          "name": "crater",
          "parent": "root",
          "pivot": [
            0,
            0,
            0
          ],
          "cubes": [
            {
              "origin": [
                -6,
                0,
                -6
              ],
              "size": [
                12,
                2,
                12
              ],
              "uv": [
                0,
                36
              ]
            },
            {
              "origin": [
                -6,
                1,
                -6
              ],
              "size": [
                12,
                2,
                2
              ],
              "uv": [
                0,
                51
              ]
            },
            {
              "origin": [
                -6,
                1,
                4
              ],
              "size": [
                12,
                2,
                2
              ],
              "uv": [
                0,
                51
              ]
            },
            {
              "origin": [
                -6,
                1,
                -4
              ],
              "size": [
                2,
                2,
                8
              ],
              "uv": [
                28,
                51
              ]
            },
            {
              "origin": [
                4,
                1,
                -4
              ],
              "size": [
                2,
                2,
                8
              ],
              "uv": [
                28,
                51
              ]
            }
          ]
        },
        {
          "name": "bulge_a",
          "parent": "root",
          "pivot": [
            -2,
            1,
            -2
          ],
          "cubes": [
            {
              "origin": [
                -5,
                1,
                -5
              ],
              "size": [
                6,
                6,
                6
              ],
              "uv": [
                0,
                0
              ]
            }
          ]
        },
        {
          "name": "bulge_b",
          "parent": "root",
          "pivot": [
            2,
            1,
            0
          ],
          "cubes": [
            {
              "origin": [
                -1,
                1,
                -3
              ],
              "size": [
                7,
                9,
                7
              ],
              "uv": [
                24,
                0
              ]
            }
          ]
        },
        {
          "name": "bulge_c",
          "parent": "root",
          "pivot": [
            2.5,
            1,
            4.5
          ],
          "cubes": [
            {
              "origin": [
                0,
                1,
                2
              ],
              "size": [
                5,
                5,
                5
              ],
              "uv": [
                0,
                20
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## `src/main/resources/assets/carnis/animations/block/pustule_cluster.animation.json`

```json
{
  "format_version": "1.8.0",
  "animations": {
    "animation.pustule_cluster.idle": {
      "loop": true,
      "animation_length": 2.0,
      "bones": {
        "bulge_a": {
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.5": [
              1.04,
              1.08,
              1.04
            ],
            "1.0": [
              1,
              1,
              1
            ],
            "1.5": [
              0.98,
              1.02,
              0.98
            ],
            "2.0": [
              1,
              1,
              1
            ]
          },
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "1.0": [
              0,
              -2,
              0
            ],
            "2.0": [
              0,
              0,
              0
            ]
          }
        },
        "bulge_b": {
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.5": [
              0.98,
              1.0,
              0.98
            ],
            "1.0": [
              1,
              1,
              1
            ],
            "1.5": [
              1.04,
              1.08,
              1.04
            ],
            "2.0": [
              1,
              1,
              1
            ]
          },
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "1.0": [
              0,
              0,
              0
            ],
            "2.0": [
              0,
              0,
              0
            ]
          }
        },
        "bulge_c": {
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.5": [
              1,
              1,
              1
            ],
            "1.0": [
              1.04,
              1.08,
              1.04
            ],
            "1.5": [
              0.98,
              1.02,
              0.98
            ],
            "2.0": [
              1,
              1,
              1
            ]
          },
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "1.0": [
              0,
              2,
              0
            ],
            "2.0": [
              0,
              0,
              0
            ]
          }
        }
      }
    },
    "animation.pustule_cluster.pulse": {
      "loop": true,
      "animation_length": 0.8,
      "bones": {
        "bulge_a": {
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.2": [
              1.04,
              1.08,
              1.04
            ],
            "0.4": [
              1,
              1,
              1
            ],
            "0.6": [
              0.98,
              1.02,
              0.98
            ],
            "0.8": [
              1,
              1,
              1
            ]
          },
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.4": [
              0,
              -2,
              0
            ],
            "0.8": [
              0,
              0,
              0
            ]
          }
        },
        "bulge_b": {
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.2": [
              0.98,
              1.0,
              0.98
            ],
            "0.4": [
              1,
              1,
              1
            ],
            "0.6": [
              1.04,
              1.08,
              1.04
            ],
            "0.8": [
              1,
              1,
              1
            ]
          },
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.4": [
              0,
              0,
              0
            ],
            "0.8": [
              0,
              0,
              0
            ]
          }
        },
        "bulge_c": {
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.2": [
              1,
              1,
              1
            ],
            "0.4": [
              1.04,
              1.08,
              1.04
            ],
            "0.6": [
              0.98,
              1.02,
              0.98
            ],
            "0.8": [
              1,
              1,
              1
            ]
          },
          "rotation": {
            "0.0": [
              0,
              0,
              0
            ],
            "0.4": [
              0,
              2,
              0
            ],
            "0.8": [
              0,
              0,
              0
            ]
          }
        }
      }
    },
    "animation.pustule_cluster.burst": {
      "loop": true,
      "animation_length": 1.0,
      "bones": {
        "bulge_a": {
          "scale": [
            0.001,
            0.001,
            0.001
          ]
        },
        "bulge_b": {
          "scale": [
            0.001,
            0.001,
            0.001
          ]
        },
        "bulge_c": {
          "scale": [
            0.001,
            0.001,
            0.001
          ]
        }
      }
    }
  }
}
```

## `src/main/resources/assets/carnis/blockstates/pustule_cluster.json`

```json
{
  "multipart": [
    {
      "apply": {
        "model": "carnis:block/pustule_cluster"
      }
    }
  ]
}
```

## `src/main/resources/assets/carnis/blockstates/spore_sprout.json`

```json
{
  "variants": {
    "closed=false": {
      "model": "carnis:block/spore_sprout"
    },
    "closed=true": {
      "model": "carnis:block/spore_sprout_closed"
    }
  }
}
```

## `src/main/resources/assets/carnis/models/block/spore_sprout.json`

```json
{
  "render_type": "minecraft:cutout",
  "textures": {
    "particle": "carnis:block/spore_sprout",
    "cross": "carnis:block/spore_sprout"
  },
  "elements": [
    {
      "from": [
        4.0,
        0,
        8
      ],
      "to": [
        12.0,
        14,
        8
      ],
      "rotation": {
        "origin": [
          8,
          0,
          8
        ],
        "axis": "y",
        "angle": -45
      },
      "faces": {
        "north": {
          "texture": "#cross"
        },
        "south": {
          "texture": "#cross"
        }
      }
    },
    {
      "from": [
        4.0,
        0,
        8
      ],
      "to": [
        12.0,
        14,
        8
      ],
      "rotation": {
        "origin": [
          8,
          0,
          8
        ],
        "axis": "y",
        "angle": 45
      },
      "faces": {
        "north": {
          "texture": "#cross"
        },
        "south": {
          "texture": "#cross"
        }
      }
    }
  ]
}
```

## `src/main/resources/assets/carnis/models/block/spore_sprout_closed.json`

```json
{
  "render_type": "minecraft:cutout",
  "textures": {
    "particle": "carnis:block/spore_sprout",
    "cross": "carnis:block/spore_sprout"
  },
  "elements": [
    {
      "from": [
        5.5,
        0,
        8
      ],
      "to": [
        10.5,
        8,
        8
      ],
      "rotation": {
        "origin": [
          8,
          0,
          8
        ],
        "axis": "y",
        "angle": -45
      },
      "faces": {
        "north": {
          "texture": "#cross"
        },
        "south": {
          "texture": "#cross"
        }
      }
    },
    {
      "from": [
        5.5,
        0,
        8
      ],
      "to": [
        10.5,
        8,
        8
      ],
      "rotation": {
        "origin": [
          8,
          0,
          8
        ],
        "axis": "y",
        "angle": 45
      },
      "faces": {
        "north": {
          "texture": "#cross"
        },
        "south": {
          "texture": "#cross"
        }
      }
    }
  ]
}
```

## `src/main/resources/assets/carnis/models/item/pustule_cluster.json`

```json
{
  "parent": "builtin/entity",
  "display": {
    "gui": {
      "rotation": [
        30,
        225,
        0
      ],
      "translation": [
        0,
        0,
        0
      ],
      "scale": [
        0.625,
        0.625,
        0.625
      ]
    },
    "ground": {
      "translation": [
        0,
        3,
        0
      ],
      "scale": [
        0.25,
        0.25,
        0.25
      ]
    },
    "fixed": {
      "scale": [
        0.5,
        0.5,
        0.5
      ]
    },
    "thirdperson_righthand": {
      "rotation": [
        75,
        45,
        0
      ],
      "translation": [
        0,
        2.5,
        0
      ],
      "scale": [
        0.375,
        0.375,
        0.375
      ]
    },
    "firstperson_righthand": {
      "rotation": [
        0,
        45,
        0
      ],
      "scale": [
        0.4,
        0.4,
        0.4
      ]
    }
  }
}
```

## `src/main/resources/assets/carnis/models/item/spore_sprout.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "carnis:block/spore_sprout"
  }
}
```
