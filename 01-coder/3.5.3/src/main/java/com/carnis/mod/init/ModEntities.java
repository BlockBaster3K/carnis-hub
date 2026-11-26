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
