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
