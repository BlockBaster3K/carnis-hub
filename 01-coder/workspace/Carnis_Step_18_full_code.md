# Шаг 18: полный код и ресурсы

## `src/main/java/com/carnis/mod/block/StomachPoolBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.init.ModItems;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class StomachPoolBlock extends net.minecraft.world.level.block.BaseEntityBlock {
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

    private static final net.minecraft.world.phys.shapes.VoxelShape SHAPE = net.minecraft.world.phys.shapes.Shapes.or(
            box(0, 0, 0, 16, 3, 16), box(0, 3, 0, 2, 16, 16), box(14, 3, 0, 16, 16, 16),
            box(2, 3, 0, 14, 16, 2), box(2, 3, 14, 14, 16, 16));
    @Override public net.minecraft.world.phys.shapes.VoxelShape getShape(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos, net.minecraft.world.phys.shapes.CollisionContext context) { return SHAPE; }
    @Override public net.minecraft.world.phys.shapes.VoxelShape getCollisionShape(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos, net.minecraft.world.phys.shapes.CollisionContext context) { return SHAPE; }
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
            server.playSound(null, pos, SoundEvents.GENERIC_SPLASH, SoundSource.BLOCKS, 0.6F, 0.8F);
            server.sendParticles(ParticleTypes.BUBBLE_POP, item.getX(), item.getY(), item.getZ(),
                    8, 0.2D, 0.2D, 0.2D, 0.02D);
        } else if (entity instanceof LivingEntity living && living.tickCount % 20 == 0) {
            var heart = com.carnis.mod.world.HiveNetwork.nearestHeart(server, pos, 32);
            boolean mob = living instanceof net.minecraft.world.entity.Mob;
            if (heart != null && mob) living.getPersistentData().putBoolean("carnis:pool_dissolving", true);
            digest(server, pos);
            living.hurt(server.damageSources().generic(), 5.0F);
            server.playSound(null, pos, com.carnis.mod.init.ModSounds.ACID_SPLASH.get(), SoundSource.BLOCKS, .7F, .85F);
            if (heart != null && mob && living.isDeadOrDying()) {
                long biomass = living instanceof net.minecraft.world.entity.animal.Cow ? 30L : 20L;
                heart.addBiomass(biomass);
            }
            living.getPersistentData().remove("carnis:pool_dissolving");
        }
    }
}
```

## `src/main/java/com/carnis/mod/block/entity/StomachPoolBlockEntity.java`

```java
package com.carnis.mod.block.entity;

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
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import javax.annotation.Nullable;

public final class StomachPoolBlockEntity extends BlockEntity {
    private long activeUntil;
    public StomachPoolBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.STOMACH_POOL.get(), pos, state); }
    public boolean isDigesting() { return level != null && level.getGameTime() < activeUntil; }
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
        level.addParticle(active && level.random.nextBoolean() ? ModParticles.BIOMASS_SPARK.get() : ParticleTypes.BUBBLE_POP,
                x, pos.getY() + .66, z, 0, .025, 0);
    }
    @Override protected void saveAdditional(CompoundTag tag) { super.saveAdditional(tag); tag.putLong("ActiveUntil", activeUntil); }
    @Override public void load(CompoundTag tag) { super.load(tag); activeUntil = tag.getLong("ActiveUntil"); }
    @Override public CompoundTag getUpdateTag() { return saveWithoutMetadata(); }
    @Nullable @Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
    @Override public void onDataPacket(Connection connection, ClientboundBlockEntityDataPacket packet) {
        CompoundTag tag = packet.getTag(); if (tag != null) load(tag);
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

## `src/main/java/com/carnis/mod/block/NervePillarBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class NervePillarBlock extends net.minecraft.world.level.block.BaseEntityBlock {
    private static final net.minecraft.world.phys.shapes.VoxelShape SHAPE = box(3, 0, 3, 13, 16, 13);
    @Override public net.minecraft.world.phys.shapes.VoxelShape getShape(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos, net.minecraft.world.phys.shapes.CollisionContext context) { return SHAPE; }
    @Override public net.minecraft.world.phys.shapes.VoxelShape getCollisionShape(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos, net.minecraft.world.phys.shapes.CollisionContext context) { return SHAPE; }
    @Override public net.minecraft.world.level.block.RenderShape getRenderShape(BlockState state) { return net.minecraft.world.level.block.RenderShape.ENTITYBLOCK_ANIMATED; }
    @Override public net.minecraft.world.level.block.entity.BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new com.carnis.mod.block.entity.NervePillarBlockEntity(pos, state); }
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
                    1.35F,
                    0.88F + serverLevel.getRandom().nextFloat() * 0.18F
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

## `src/main/java/com/carnis/mod/block/entity/NervePillarBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import software.bernie.geckolib.animatable.GeoBlockEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class NervePillarBlockEntity extends BlockEntity implements GeoBlockEntity {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private long nextDischarge;
    public NervePillarBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.NERVE_PILLAR.get(), pos, state); }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "fibers", 0,
                state -> state.setAndContinue(RawAnimation.begin().thenLoop("animation.nerve_pillar.idle"))));
    }
    public void discharge(ServerLevel server) {
        long now = server.getGameTime();
        if (now < nextDischarge) return;
        nextDischarge = now + 10;
        double x = worldPosition.getX() + .5, y = worldPosition.getY() + .7, z = worldPosition.getZ() + .5;
        server.sendParticles(ParticleTypes.ELECTRIC_SPARK, x, y, z, 18, .3, .45, .3, .08);
        for (int i = 0; i < 16; i++) {
            double angle = Math.PI * 2 * i / 16;
            double dx = Math.cos(angle), dz = Math.sin(angle);
            server.sendParticles(ModParticles.BIOMASS_SPARK.get(), x + dx * .52, y, z + dz * .52,
                    0, dx * .08, .025, dz * .08, 1);
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

## `src/main/java/com/carnis/mod/item/OrganBlockItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.world.item.BlockItem;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import java.util.function.Consumer;

public final class OrganBlockItem extends BlockItem {
    public OrganBlockItem(Block block, Properties properties) { super(block, properties); }
    @Override public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new IClientItemExtensions() {
            private com.carnis.mod.client.renderer.OrganItemRenderer renderer;
            @Override public net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new com.carnis.mod.client.renderer.OrganItemRenderer();
                return renderer;
            }
        });
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
    public OrganItemRenderer() { super(Minecraft.getInstance().getBlockEntityRenderDispatcher(), Minecraft.getInstance().getEntityModels()); }
    @Override public void renderByItem(ItemStack stack, ItemDisplayContext context, PoseStack pose,
                                       MultiBufferSource buffers, int light, int overlay) {
        if (!(stack.getItem() instanceof BlockItem item)) return;
        var dispatcher = Minecraft.getInstance().getBlockEntityRenderDispatcher();
        if (item.getBlock() == ModBlocks.STOMACH_POOL.get()) {
            if (pool == null) pool = new StomachPoolBlockEntity(BlockPos.ZERO, ModBlocks.STOMACH_POOL.get().defaultBlockState());
            Minecraft.getInstance().getBlockRenderer().renderSingleBlock(pool.getBlockState(), pose, buffers, light, overlay);
            dispatcher.renderItem(pool, pose, buffers, light, overlay);
        } else if (item.getBlock() == ModBlocks.NERVE_PILLAR.get()) {
            if (pillar == null) pillar = new NervePillarBlockEntity(BlockPos.ZERO, ModBlocks.NERVE_PILLAR.get().defaultBlockState());
            dispatcher.renderItem(pillar, pose, buffers, light, overlay);
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
            () -> new com.carnis.mod.block.SinewSpikesBlock(BlockBehaviour.Properties.copy(Blocks.CRIMSON_ROOTS)
                    .noCollission().noOcclusion().sound(SoundType.BONE_BLOCK)));

    public static final RegistryObject<Block> NERVE_PILLAR = BLOCKS.register(
            "nerve_pillar", () -> new NervePillarBlock(BlockBehaviour.Properties.of()
                    .noOcclusion().strength(2.0F).sound(SoundType.SLIME_BLOCK).randomTicks()));

    public static final RegistryObject<Block> CREEPING_TENDRILS = BLOCKS.register(
            "creeping_tendrils", () -> new CreepingTendrilsBlock(BlockBehaviour.Properties.copy(Blocks.LADDER).sound(SoundType.SLIME_BLOCK)));
    public static final RegistryObject<Block> PUSTULE_CLUSTER = BLOCKS.register(
            "pustule_cluster", () -> new PustuleClusterBlock(BlockBehaviour.Properties.copy(Blocks.MOSS_CARPET)));
    public static final RegistryObject<Block> STOMACH_POOL = BLOCKS.register(
            "stomach_pool", () -> new StomachPoolBlock(BlockBehaviour.Properties.of()
                    .noOcclusion().strength(0.5F).sound(SoundType.SLIME_BLOCK).randomTicks()));

    public static final RegistryObject<Block> SPORE_SPROUT = BLOCKS.register(
            "spore_sprout", () -> new SporeSproutBlock(
                    BlockBehaviour.Properties.copy(Blocks.CRIMSON_ROOTS)));
    public static final RegistryObject<Block> NEURAL_MOSS = BLOCKS.register(
            "neural_moss", () -> new NeuralMossBlock(
                    BlockBehaviour.Properties.copy(Blocks.MOSS_CARPET).speedFactor(0.65F)));

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
            "pustule_cluster", () -> new BlockItem(ModBlocks.PUSTULE_CLUSTER.get(), new Item.Properties()));
    public static final RegistryObject<Item> STOMACH_POOL = ITEMS.register(
            "stomach_pool", () -> new com.carnis.mod.item.OrganBlockItem(ModBlocks.STOMACH_POOL.get(), new Item.Properties()));

    public static final RegistryObject<Item> SPORE_SPROUT = ITEMS.register(
            "spore_sprout", () -> new BlockItem(ModBlocks.SPORE_SPROUT.get(), new Item.Properties()));
    public static final RegistryObject<Item> NEURAL_MOSS = ITEMS.register(
            "neural_moss", () -> new BlockItem(ModBlocks.NEURAL_MOSS.get(), new Item.Properties()));

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
        blockItem(ModBlocks.NEURAL_MOSS);
        blockItem(ModBlocks.PUSTULE_CLUSTER);

        // 2D flat item representation for Geo & organic hazard block items
        flatBlockItem(ModBlocks.SPORE_SPROUT);
        // Flesh bulb and biomass remains item models are hand-authored in main resources.
        flatBlockItem(ModBlocks.SINEW_SPIKES);
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
                SoundSource.PLAYERS, 0.9F, 1.0F);
        return InteractionResultHolder.consume(stack);
    }

    @Override public void onUseTick(Level level, LivingEntity user, ItemStack stack, int count) {
        if (!(level instanceof ServerLevel server)) return;
        if (stack.isEmpty()) { user.stopUsingItem(); return; }
        int elapsed = DURATION - count;
        if (elapsed % 10 == 0) server.playSound(null, user.blockPosition(), ModSounds.PURIFIER_LOOP.get(),
                SoundSource.PLAYERS, 0.7F, 1.0F);
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

## `src/main/resources/assets/carnis/models/block/stomach_pool.json`

```json
{
  "textures": {
    "particle": "carnis:block/living_flesh_0",
    "flesh": "carnis:block/living_flesh_0"
  },
  "elements": [
    {
      "from": [
        0,
        0,
        0
      ],
      "to": [
        16,
        3,
        16
      ],
      "faces": {
        "down": {
          "texture": "#flesh"
        },
        "up": {
          "texture": "#flesh"
        },
        "north": {
          "texture": "#flesh"
        },
        "south": {
          "texture": "#flesh"
        },
        "west": {
          "texture": "#flesh"
        },
        "east": {
          "texture": "#flesh"
        }
      }
    },
    {
      "from": [
        0,
        3,
        0
      ],
      "to": [
        2,
        16,
        16
      ],
      "faces": {
        "down": {
          "texture": "#flesh"
        },
        "up": {
          "texture": "#flesh"
        },
        "north": {
          "texture": "#flesh"
        },
        "south": {
          "texture": "#flesh"
        },
        "west": {
          "texture": "#flesh"
        },
        "east": {
          "texture": "#flesh"
        }
      }
    },
    {
      "from": [
        14,
        3,
        0
      ],
      "to": [
        16,
        16,
        16
      ],
      "faces": {
        "down": {
          "texture": "#flesh"
        },
        "up": {
          "texture": "#flesh"
        },
        "north": {
          "texture": "#flesh"
        },
        "south": {
          "texture": "#flesh"
        },
        "west": {
          "texture": "#flesh"
        },
        "east": {
          "texture": "#flesh"
        }
      }
    },
    {
      "from": [
        2,
        3,
        0
      ],
      "to": [
        14,
        16,
        2
      ],
      "faces": {
        "down": {
          "texture": "#flesh"
        },
        "up": {
          "texture": "#flesh"
        },
        "north": {
          "texture": "#flesh"
        },
        "south": {
          "texture": "#flesh"
        },
        "west": {
          "texture": "#flesh"
        },
        "east": {
          "texture": "#flesh"
        }
      }
    },
    {
      "from": [
        2,
        3,
        14
      ],
      "to": [
        14,
        16,
        16
      ],
      "faces": {
        "down": {
          "texture": "#flesh"
        },
        "up": {
          "texture": "#flesh"
        },
        "north": {
          "texture": "#flesh"
        },
        "south": {
          "texture": "#flesh"
        },
        "west": {
          "texture": "#flesh"
        },
        "east": {
          "texture": "#flesh"
        }
      }
    }
  ]
}
```

## `src/main/resources/assets/carnis/models/item/stomach_pool.json`

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

## `src/main/resources/assets/carnis/models/item/nerve_pillar.json`

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

## `src/main/resources/assets/carnis/geo/block/nerve_pillar.geo.json`

```json
{
  "format_version": "1.12.0",
  "minecraft:geometry": [
    {
      "description": {
        "identifier": "geometry.carnis.nerve_pillar",
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
          "name": "fibers",
          "parent": "root",
          "pivot": [
            0,
            0,
            0
          ],
          "cubes": [
            {
              "origin": [
                -5,
                0,
                -5
              ],
              "size": [
                10,
                16,
                10
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -6,
                1,
                -2
              ],
              "size": [
                2,
                14,
                4
              ],
              "uv": [
                40,
                0
              ]
            },
            {
              "origin": [
                4,
                1,
                -2
              ],
              "size": [
                2,
                14,
                4
              ],
              "uv": [
                40,
                0
              ]
            },
            {
              "origin": [
                -2,
                1,
                -6
              ],
              "size": [
                4,
                14,
                2
              ],
              "uv": [
                40,
                18
              ]
            },
            {
              "origin": [
                -2,
                1,
                4
              ],
              "size": [
                4,
                14,
                2
              ],
              "uv": [
                40,
                18
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## `src/main/resources/assets/carnis/animations/block/nerve_pillar.animation.json`

```json
{
  "format_version": "1.8.0",
  "animations": {
    "animation.nerve_pillar.idle": {
      "loop": true,
      "animation_length": 1.6,
      "bones": {
        "fibers": {
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.4": [
              1.04,
              0.98,
              1.04
            ],
            "0.8": [
              1,
              1,
              1
            ],
            "1.2": [
              1.02,
              0.99,
              1.02
            ],
            "1.6": [
              1,
              1,
              1
            ]
          }
        }
      }
    },
    "animation.nerve_pillar.pulse": {
      "loop": false,
      "animation_length": 0.4,
      "bones": {
        "fibers": {
          "scale": {
            "0.0": [
              1,
              1,
              1
            ],
            "0.2": [
              1.12,
              0.94,
              1.12
            ],
            "0.4": [
              1,
              1,
              1
            ]
          }
        }
      }
    }
  }
}
```
