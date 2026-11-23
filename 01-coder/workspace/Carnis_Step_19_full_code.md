# Шаг 19 — полный код и ресурсы

## `src/main/java/com/carnis/mod/block/NeuralMossBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.CarnisMod;
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
        return entity instanceof HivemindLinkedMob || entity.getType().is(HIVE_MEMBERS);
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

## `src/main/java/com/carnis/mod/block/SinewSpikesBlock.java`

```java
package com.carnis.mod.block;

import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
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
import net.minecraft.world.phys.shapes.VoxelShape;
import javax.annotation.Nullable;

public final class SinewSpikesBlock extends Block {
    private static final VoxelShape SHAPE = Block.box(1, 0, 1, 15, 6, 15);
    private static final String NEXT_HIT = "carnis:sinew_spikes_next_hit";
    public SinewSpikesBlock(BlockBehaviour.Properties properties) { super(properties); }
    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) { return SHAPE; }
    @Override public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) { return SHAPE; }
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
        if (living.getBoundingBox().minY > pos.getY() + 6.0D / 16.0D + .05D
                || living.getBoundingBox().maxY < pos.getY()) return;
        long now = level.getGameTime();
        var data = living.getPersistentData();
        if (data.contains(NEXT_HIT) && data.getLong(NEXT_HIT) > now) return;
        data.putLong(NEXT_HIT, now + 20L);
        if (living.hurt(level.damageSources().cactus(), 4.0F)) {
            living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 0));
            level.playSound(null, pos, ModSounds.ORGANIC_CREAK.get(), SoundSource.BLOCKS, .75F,
                    .9F + level.random.nextFloat() * .2F);
        }
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
        blockItem(ModBlocks.PUSTULE_CLUSTER);

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
        simpleCube(ModBlocks.PUSTULE_CLUSTER, "pustule_cluster");

        crossBlock(ModBlocks.SPORE_SPROUT, "spore_sprout");
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

## `src/main/java/com/carnis/mod/datagen/ModLanguageProvider.java`

```java
package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModItems;
import net.minecraft.data.PackOutput;
import net.minecraftforge.common.data.LanguageProvider;

public final class ModLanguageProvider extends LanguageProvider {
    private static final String EN_US = "en_us";
    private static final String RU_RU = "ru_ru";

    private final String locale;

    public ModLanguageProvider(PackOutput output, String locale) {
        super(output, CarnisMod.MOD_ID, locale);
        this.locale = locale;
    }

    @Override
    protected void addTranslations() {
        switch (locale) {
            case EN_US -> addEnglishTranslations();
            case RU_RU -> addRussianTranslations();
            default -> throw new IllegalStateException(
                    "Unsupported Carnis language provider locale: " + locale
            );
        }
    }

    private void addEnglishTranslations() {
        add("subtitles.carnis.inoculator_fire", "Inoculator fires");
        add("subtitles.carnis.dart_hit", "Dart hits");
        add("tooltip.carnis.flesh_bulb.mechanics", "An incubation sac that can attach to ceilings and floors.");
        add("tooltip.carnis.flesh_bulb.lore", "The muffled, rapid heartbeat of a maturing brood can be heard inside.");
        add("tooltip.carnis.sinew_spikes.mechanics", "Deals piercing damage and slows any creature that steps on it.");
        add("tooltip.carnis.sinew_spikes.lore", "Taut sinews respond to the slightest vibration of footsteps.");
        add("tooltip.carnis.biomass_maggot.mechanics", "A voracious scavenger. Devours organic remains and pupates in soil.");
        add("tooltip.carnis.biomass_maggot.lore", "The first link in the Hive’s parasitic cycle.");
        add("item.carnis.infected_zombie_spawn_egg", "Infected Zombie Spawn Egg");
        add("entity.carnis.infected_zombie", "Infected Zombie");
        add("tooltip.carnis.infected_zombie_spawn_egg", "Spawns an infected zombie.");
        add("item.carnis.antibiotics", "Antibiotics");
        add("effect.carnis.immunosuppression", "Immunosuppression");
        add("tooltip.carnis.antibiotics", "Prevents exposure for 3 minutes.");
        add("entity.carnis.parasitic_tendril", "Parasitic Tendril");
        add("entity.carnis.hive_sentinel", "Hive Sentinel");
        add("entity.carnis.cerebral_nexus", "Cerebral Nexus");
        add("effect.carnis.incubating", "Incubating");
        add("subtitles.carnis.flamethrower_fire", "Flamethrower roars");
        add("subtitles.carnis.amalgam_roar", "Amalgam roars");
        add("codex.carnis.chapter.0", "Inception & Biomes");
        add("codex.carnis.body.0", "Veins spread across supported faces; incomplete faces may resist growth. Sludge contaminates players and reacts with water and lava. Infection spreads by a queued process.");
        add("codex.carnis.chapter.1", "Adaptive Hivemind");
        add("codex.carnis.body.1", "FIRE / RANGED / MELEE / EXPLOSIVE use the same logarithmic mitigation curve. Points: 0 / 100 / 300 / 600 / 1000. Reduction: 0% / 25% / 50% / 70% / 80%. Between thresholds: linear interpolation in ln(1+points). Cap 80%.");
        add("codex.carnis.chapter.2", "Hive Organs & Flora");
        add("codex.carnis.body.2", "Hive Eye detects players within 24 blocks and alerts linked mobs within 32. Placing a Nerve Pillar halves remaining chunk shock. Stomach Pool dissolves items: flesh or meat gives 5 biomass each; other items give 1. Living creatures take 4 damage per second.");
        add("codex.carnis.chapter.3", "Medical & Armor Weaving");
        add("codex.carnis.body.3", "Serum reduces infection by 35. Antibiotics block positive exposure for 3600 ticks. On an anvil, combine armor and one neural binding matrix for 5 levels. Each woven or resonator armor piece reduces exposure by 25%; four pieces reach 100%.");
        add("codex.carnis.chapter.4", "Mutants & Amalgamation");
        add("codex.carnis.body.4", "Zombie: 35 health, 4.5 attack; skeleton: 28 health, 4.5 attack; creeper: 24 health; spider: 20 health, 3 attack. Spat: 2 damage, Slowness II for 100 ticks and +5 exposure on successful damage. Three zombies near a heart at 300 biomass can fuse.");
        add("entity.carnis.flesh_spat", "Flesh Spat");
        add("item.carnis.flesh_spat", "Flesh Spat");
        add("tooltip.carnis.flesh_spat", "A glob of infectious tissue.");
        add("subtitles.carnis.heartbeat_loop", "Heart beats");
        add("item.carnis.research_journal", "Codex Carnis");
        add("tooltip.carnis.research_journal", "A field guide to the hive.");
        add("item.carnis.tainted_sludge_bucket", "Tainted Sludge Bucket");
        add("item.carnis.bone_scythe_arm", "Bone Scythe Arm");
        add("block.carnis.tainted_sludge", "Tainted Sludge");
        add("fluid_type.carnis.tainted_sludge", "Tainted Sludge");
        add("tooltip.carnis.tainted_sludge_bucket", "A bucket of infectious sludge.");
        add("tooltip.carnis.bone_scythe_arm", "A jagged bone blade.");
        add("subtitles.carnis.amalgam_step", "Flesh Amalgam squelches");
        add("block.carnis.flesh_veins", "Flesh Veins");
        add("tooltip.carnis.flesh_veins", "Organic growth on exposed surfaces.");

        add("entity.carnis.infected_skeleton", "Infected Skeleton");
        add("item.carnis.infected_skeleton_spawn_egg", "Infected Skeleton Spawn Egg");
        add("tooltip.carnis.infected_skeleton_spawn_egg", "Spawns an infected skeleton.");
        add("entity.carnis.infected_creeper", "Infected Creeper");
        add("item.carnis.infected_creeper_spawn_egg", "Infected Creeper Spawn Egg");
        add("tooltip.carnis.infected_creeper_spawn_egg", "Spawns an infected creeper.");
        add("entity.carnis.infected_spider", "Infected Spider");
        add("item.carnis.infected_spider_spawn_egg", "Infected Spider Spawn Egg");
        add("tooltip.carnis.infected_spider_spawn_egg", "Spawns an infected spider.");
        add("item.carnis.neuro_resonator_chestplate", "Neuro-Resonator Chestplate");
        add("item.carnis.neuro_resonator_leggings", "Neuro-Resonator Leggings");
        add("item.carnis.neuro_resonator_boots", "Neuro-Resonator Boots");
        add("block.carnis.flesh_bulb", "Flesh Bulb");
        add("block.carnis.biomass_remains", "Biomass Remains");
        add("block.carnis.sinew_spikes", "Sinew Spikes");
        add("entity.carnis.biomass_maggot", "Biomass Maggot");
        add("item.carnis.biomass_maggot_spawn_egg", "Biomass Maggot Spawn Egg");
        add("item.carnis.neural_binding_matrix", "Neural Binding Matrix");
        add("tooltip.carnis.neuro_resonator_chestplate", "A biological chestplate reduces infection exposure.");
        add("tooltip.carnis.neuro_resonator_leggings", "Biological leggings reduce infection exposure.");
        add("tooltip.carnis.neuro_resonator_boots", "Biological boots reduce infection exposure.");
        add("tooltip.carnis.neural_binding_matrix", "Weave into armor at an anvil for five levels.");
        add("block.carnis.nerve_pillar", "Nerve Pillar");
        add("item.carnis.pneumatic_inoculator", "Pneumatic Inoculator");
        add("item.carnis.viral_dart", "Viral Dart");
        add("item.carnis.purification_dart", "Purification Dart");
        add("entity.carnis.viral_dart", "Viral Dart");
        add("entity.carnis.purification_dart", "Purification Dart");
        add("death.attack.carnis_tainted_sludge", "%1$s dissolved in tainted sludge");
        add("death.attack.purification_dart", "%1$s was purified by a dart");
        add("death.attack.purification_dart.player", "%1$s was purified by %2$s");
        add("tooltip.carnis.nerve_pillar", "Placement halves remaining shock time in this chunk.");
        add("tooltip.carnis.pneumatic_inoculator", "Right-click to fire a carried dart; 15-tick cooldown.");
        add("tooltip.carnis.viral_dart", "Adds 30 infection to players; poisons and slows mobs.");
        add("tooltip.carnis.purification_dart", "Removes 35 infection or damages Carnis mobs for 25.");
        add("tooltip.carnis.hold_shift", "Hold Shift for details");
        add("tooltip.carnis.living_flesh", "Living tissue spreads through nearby terrain.");
        add("tooltip.carnis.charred_flesh", "Burned tissue yields bone meal and charcoal.");
        add("tooltip.carnis.spore_sprout", "An organic sprout releases drifting spores.");
        add("tooltip.carnis.neural_moss", "A fleshy carpet impedes movement.");
        add("tooltip.carnis.neural_moss.mechanics", "Slows outsiders; spreads near water or Hive tissue.");
        add("tooltip.carnis.neural_moss.lore", "A living carpet listens for unfamiliar footsteps.");
        add("tooltip.carnis.creeping_tendrils", "Climb the tendrils attached to solid flesh.");
        add("tooltip.carnis.pustule_cluster", "Step on it without sneaking to burst infectious spores.");
        add("tooltip.carnis.stomach_pool", "Corrosive tissue dissolves items into biomass.");
        add("tooltip.carnis.ossified_flesh", "Hardened tissue spreads the hive.");
        add("tooltip.carnis.fireproof_flesh", "Adapted tissue resistant to flame.");
        add("tooltip.carnis.veins", "Living veins carry infection through wood.");
        add("tooltip.carnis.pulsing_heart", "The hive heart accelerates nearby infection.");
        add("tooltip.carnis.hive_eye", "Detects intruders and alerts nearby Amalgams.");
        add("tooltip.carnis.flesh_amalgam_spawn_egg", "Spawns a Flesh Amalgam.");
        add("tooltip.carnis.purification_serum", "Drink to remove 35 infection points.");
        add("effect.carnis.thermal_shock", "Thermal Shock");
        add("subtitles.carnis.purifier_ignite", "Purifier ignites");
        add("subtitles.carnis.purifier_loop", "Purifier fires");
        add("tooltip.carnis.bio_purifier", "Hold use: 6.5-block cone of flame.");
        add("tooltip.carnis.neuro_resonator_helmet", "Dampens hallucinations, reduces exposure by 25% and reveals nearby biomass.");
        add("itemGroup.carnis", "Carnis: Adaptive Hivemind");

        add("death.attack.necrotic_consumption", "%1$s was consumed by the hivemind");
        add(ModBlocks.CREEPING_TENDRILS.get(), "Creeping Tendrils");
        add(ModBlocks.PUSTULE_CLUSTER.get(), "Pustule Cluster");
        add(ModBlocks.STOMACH_POOL.get(), "Stomach Pool");
        add(ModBlocks.SPORE_SPROUT.get(), "Spore Sprout");
        add(ModBlocks.NEURAL_MOSS.get(), "Neural Moss");
        add(ModBlocks.CHARRED_FLESH.get(), "Charred Flesh");
        add(ModBlocks.LIVING_FLESH.get(), "Living Flesh");
        add(ModBlocks.OSSIFIED_FLESH.get(), "Ossified Flesh");
        add(ModBlocks.FIREPROOF_FLESH.get(), "Fireproof Flesh");
        add(ModBlocks.PULSING_HEART.get(), "Pulsing Heart");
        add(ModBlocks.HIVE_EYE.get(), "Hive Eye");
        add("entity.carnis.assimilated_player", "Assimilated %s");
        add("death.attack.organic_consumption", "%1$s was consumed by the hive");
        add("entity.carnis.flesh_amalgam", "Flesh Amalgam");
        add("item.carnis.amalgam_bile_glob", "Amalgam Bile");
        add("entity.carnis.amalgam_bile", "Amalgam Bile");
        add("tooltip.carnis.amalgam_bile_glob", "A corrosive organic glob.");
        add("subtitles.carnis.amalgam_smash", "Amalgam slams the ground");
        add("subtitles.carnis.organic_creak", "Sinew lashes");
        add(
                "item.carnis.flesh_amalgam_spawn_egg",
                "Flesh Amalgam Spawn Egg"
        );
        add(ModItems.PURIFICATION_SERUM.get(), "Purification Serum");
        add(ModItems.BIO_PURIFIER.get(), "Bio-Purifier");
        add(
                ModItems.NEURO_RESONATOR_HELMET.get(),
                "Neuro-Resonator Helmet"
        );
        add(
                "death.attack.bio_purifier",
                "%1$s was incinerated by a bio-purifier"
        );
        add(
                "death.attack.bio_purifier.player",
                "%1$s was incinerated by %2$s's bio-purifier"
        );

        add("subtitles.carnis.phantom_creeper", "Something hisses behind you");
        add("subtitles.carnis.phantom_footsteps", "Footsteps squelch through flesh");
        add("subtitles.carnis.phantom_whisper", "The hivemind whispers");
        add("subtitles.carnis.pulsing_heart_beat", "A biome heart beats");
        add("subtitles.carnis.synapse_shock", "A synapse discharges");
        add("subtitles.carnis.synapse_rupture", "Nerve tissue tears apart");
        add("subtitles.carnis.digestor_churn", "A digestor churns");
        add("subtitles.carnis.hive_eye_screech", "The hive eye shrieks");
        add(
                "subtitles.carnis.amalgamation_fuse",
                "Flesh fuses into an amalgam"
        );
        add(
                "subtitles.carnis.bone_deflect",
                "A projectile ricochets off bone"
        );
        add(
                "subtitles.carnis.acid_splash",
                "Corrosive acid splashes"
        );
        add(
                "subtitles.carnis.flesh_amalgam_ambient",
                "The Flesh Amalgam groans"
        );
        add(
                "subtitles.carnis.flesh_amalgam_hurt",
                "The Flesh Amalgam recoils"
        );
        add(
                "subtitles.carnis.flesh_amalgam_death",
                "The Flesh Amalgam collapses"
        );
    }

    private void addRussianTranslations() {
        add("entity.carnis.hive_sentinel", "Страж Улья");
        add("entity.carnis.cerebral_nexus", "Мозговой узел");
        add("subtitles.carnis.inoculator_fire", "Выстрел инокулятора");
        add("subtitles.carnis.dart_hit", "Дротик ударяется");
        add("tooltip.carnis.flesh_bulb.mechanics", "Инкубационный мешок, способный закрепляться на потолке и полу.");
        add("tooltip.carnis.flesh_bulb.lore", "Внутри слышно глухое, частое сердцебиение зреющего выводка.");
        add("tooltip.carnis.sinew_spikes.mechanics", "Наносят колющий урон и замедляют любое наступившее существо.");
        add("tooltip.carnis.sinew_spikes.lore", "Натянутые жилы реагируют на малейшую вибрацию шагов.");
        add("tooltip.carnis.biomass_maggot.mechanics", "Ненасытный трупоед. Пожирает органические останки и окукливается в почве.");
        add("tooltip.carnis.biomass_maggot.lore", "Начальное звено паразитического круговорота Улья.");
        add("item.carnis.infected_zombie_spawn_egg", "Яйцо призыва заражённого зомби");
        add("entity.carnis.infected_zombie", "Заражённый зомби");
        add("tooltip.carnis.infected_zombie_spawn_egg", "Призывает заражённого зомби.");
        add("item.carnis.antibiotics", "Антибиотики");
        add("effect.carnis.immunosuppression", "Иммуносупрессия");
        add("tooltip.carnis.antibiotics", "Предотвращает заражение на 3 минуты.");
        add("entity.carnis.parasitic_tendril", "Паразитический усик");
        add("effect.carnis.incubating", "Инкубация");
        add("subtitles.carnis.flamethrower_fire", "Огнемёт ревёт");
        add("subtitles.carnis.amalgam_roar", "Амальгама ревёт");
        add("codex.carnis.chapter.0", "Истоки и биомы");
        add("codex.carnis.body.0", "Вены растут по поддерживаемым граням; неполные грани могут мешать росту. Жижа заражает игроков и реагирует с водой и лавой. Распространение обрабатывается очередью.");
        add("codex.carnis.chapter.1", "Адаптивный разум");
        add("codex.carnis.body.1", "ОГОНЬ / ДАЛЬНИЙ / БЛИЖНИЙ / ВЗРЫВ: общая логарифмическая кривая. Очки: 0 / 100 / 300 / 600 / 1000. Снижение: 0% / 25% / 50% / 70% / 80%. Между порогами — интерполяция по ln(1+очки). Предел 80%.");
        add("codex.carnis.chapter.2", "Органы и флора улья");
        add("codex.carnis.body.2", "Глаз видит игроков в 24 блоках и предупреждает связанных мобов в 32. Установка нервного столба вдвое сокращает оставшийся шок чанка. Желудочный бассейн даёт 5 биомассы за мясо или плоть, 1 за иной предмет; живым наносит 4 урона в секунду.");
        add("codex.carnis.chapter.3", "Медицина и нейроплетение");
        add("codex.carnis.body.3", "Сыворотка снижает заражение на 35. Антибиотики блокируют положительную экспозицию на 3600 тиков. На наковальне соедините броню с одной матрицей за 5 уровней. Каждая защищённая часть снижает экспозицию на 25%, четыре — на 100%.");
        add("codex.carnis.chapter.4", "Мутанты и слияние");
        add("codex.carnis.body.4", "Зомби: 35 здоровья, 4,5 урона; скелет: 28 и 4,5; крипер: 24 здоровья; паук: 20 и 3. Плевок: 2 урона, замедление II на 100 тиков и +5 экспозиции при успешном уроне. Три зомби у сердца при 300 биомассы могут слиться.");
        add("entity.carnis.flesh_spat", "Плевок плоти");
        add("item.carnis.flesh_spat", "Плевок плоти");
        add("tooltip.carnis.flesh_spat", "Сгусток заражённой ткани.");
        add("subtitles.carnis.heartbeat_loop", "Сердце бьётся");
        add("item.carnis.research_journal", "Кодекс Карнис");
        add("tooltip.carnis.research_journal", "Полевой справочник по улью.");
        add("item.carnis.tainted_sludge_bucket", "Ведро заражённой слизи");
        add("item.carnis.bone_scythe_arm", "Костяная коса-рука");
        add("block.carnis.tainted_sludge", "Заражённая слизь");
        add("fluid_type.carnis.tainted_sludge", "Заражённая слизь");
        add("tooltip.carnis.tainted_sludge_bucket", "Ведро заразной слизи.");
        add("tooltip.carnis.bone_scythe_arm", "Зазубренный костяной клинок.");
        add("subtitles.carnis.amalgam_step", "Плотяная амальгама чавкает");
        add("block.carnis.flesh_veins", "Плотяные жилы");
        add("tooltip.carnis.flesh_veins", "Органические жилы на открытых поверхностях.");

        add("entity.carnis.infected_skeleton", "Заражённый скелет");
        add("item.carnis.infected_skeleton_spawn_egg", "Яйцо призыва: Заражённый скелет");
        add("tooltip.carnis.infected_skeleton_spawn_egg", "Призывает заражённого скелета.");
        add("entity.carnis.infected_creeper", "Заражённый крипер");
        add("item.carnis.infected_creeper_spawn_egg", "Яйцо призыва: Заражённый крипер");
        add("tooltip.carnis.infected_creeper_spawn_egg", "Призывает заражённого крипера.");
        add("entity.carnis.infected_spider", "Заражённый паук");
        add("item.carnis.infected_spider_spawn_egg", "Яйцо призыва: Заражённый паук");
        add("tooltip.carnis.infected_spider_spawn_egg", "Призывает заражённого паука.");
        add("item.carnis.neuro_resonator_chestplate", "Нейро-резонаторный нагрудник");
        add("item.carnis.neuro_resonator_leggings", "Нейро-резонаторные поножи");
        add("item.carnis.neuro_resonator_boots", "Нейро-резонаторные ботинки");
        add("block.carnis.flesh_bulb", "Мясная луковица");
        add("block.carnis.biomass_remains", "Останки биомассы");
        add("block.carnis.sinew_spikes", "Сухожильные шипы");
        add("entity.carnis.biomass_maggot", "Личинка биомассы");
        add("item.carnis.biomass_maggot_spawn_egg", "Яйцо призыва: Личинка биомассы");
        add("item.carnis.neural_binding_matrix", "Матрица нейронного сплетения");
        add("tooltip.carnis.neuro_resonator_chestplate", "Биологический нагрудник снижает заражение.");
        add("tooltip.carnis.neuro_resonator_leggings", "Биологические поножи снижают заражение.");
        add("tooltip.carnis.neuro_resonator_boots", "Биологические ботинки снижают заражение.");
        add("tooltip.carnis.neural_binding_matrix", "Вплетите в броню на наковальне за пять уровней.");
        add("block.carnis.nerve_pillar", "Нервный столп");
        add("item.carnis.pneumatic_inoculator", "Пневматический инокулятор");
        add("item.carnis.viral_dart", "Вирусный дротик");
        add("item.carnis.purification_dart", "Очищающий дротик");
        add("entity.carnis.viral_dart", "Вирусный дротик");
        add("entity.carnis.purification_dart", "Очищающий дротик");
        add("death.attack.carnis_tainted_sludge", "%1$s растворился в заражённой жиже");
        add("death.attack.purification_dart", "%1$s очищен дротиком");
        add("death.attack.purification_dart.player", "%1$s очищен игроком %2$s");
        add("tooltip.carnis.nerve_pillar", "При установке вдвое сокращает оставшийся шок чанка.");
        add("tooltip.carnis.pneumatic_inoculator", "ПКМ: выстрел дротиком из инвентаря; задержка 15 тиков.");
        add("tooltip.carnis.viral_dart", "Добавляет игрокам 30 заражения; травит и замедляет мобов.");
        add("tooltip.carnis.purification_dart", "Снимает 35 заражения или наносит мобам Carnis 25 урона.");
        add("tooltip.carnis.hold_shift", "Удерживайте Shift для подробностей");
        add("tooltip.carnis.living_flesh", "Живая ткань распространяется по окружающим блокам.");
        add("tooltip.carnis.charred_flesh", "Обгоревшая ткань даёт костную муку и уголь.");
        add("tooltip.carnis.spore_sprout", "Органический росток выпускает споры.");
        add("tooltip.carnis.neural_moss", "Мясистый мох замедляет движение.");
        add("tooltip.carnis.neural_moss.mechanics", "Замедляет чужаков; растёт у воды и тканей Улья.");
        add("tooltip.carnis.neural_moss.lore", "Живой ковёр прислушивается к чужим шагам.");
        add("tooltip.carnis.creeping_tendrils", "Взбирайтесь по усикам на поверхности плоти.");
        add("tooltip.carnis.pustule_cluster", "Наступите без приседания: пустулы лопнут и заразят вас.");
        add("tooltip.carnis.stomach_pool", "Едкая ткань растворяет предметы в биомассу.");
        add("tooltip.carnis.ossified_flesh", "Окостеневшая ткань распространяет улей.");
        add("tooltip.carnis.fireproof_flesh", "Ткань, приспособленная к огню.");
        add("tooltip.carnis.veins", "Живые вены несут инфекцию через древесину.");
        add("tooltip.carnis.pulsing_heart", "Сердце улья ускоряет заражение поблизости.");
        add("tooltip.carnis.hive_eye", "Обнаруживает чужаков и тревожит ближайших амальгам.");
        add("tooltip.carnis.flesh_amalgam_spawn_egg", "Призывает амальгаму плоти.");
        add("tooltip.carnis.purification_serum", "Выпейте, чтобы снизить заражение на 35 пунктов.");
        add("effect.carnis.thermal_shock", "Термический шок");
        add("subtitles.carnis.purifier_ignite", "Очиститель зажигается");
        add("subtitles.carnis.purifier_loop", "Очиститель выпускает пламя");
        add("tooltip.carnis.bio_purifier", "Удерживайте: конус пламени на 6,5 блока.");
        add("tooltip.carnis.neuro_resonator_helmet", "Подавляет галлюцинации, снижает экспозицию на 25% и обнаруживает биомассу.");
        add("itemGroup.carnis", "Carnis: Адаптивный коллективный разум");

        add("death.attack.necrotic_consumption", "%1$s поглощён коллективным разумом");
        add(ModBlocks.CREEPING_TENDRILS.get(), "Ползучие щупальца");
        add(ModBlocks.PUSTULE_CLUSTER.get(), "Скопление пустул");
        add(ModBlocks.STOMACH_POOL.get(), "Желудочный бассейн");
        add(ModBlocks.SPORE_SPROUT.get(), "Споровый росток");
        add(ModBlocks.NEURAL_MOSS.get(), "Нервный мох");
        add(ModBlocks.CHARRED_FLESH.get(), "Обугленная плоть");
        add(ModBlocks.LIVING_FLESH.get(), "Живая плоть");
        add(ModBlocks.OSSIFIED_FLESH.get(), "Окостенелая плоть");
        add(ModBlocks.FIREPROOF_FLESH.get(), "Огнеупорная плоть");
        add(ModBlocks.PULSING_HEART.get(), "Сердце биома");
        add(ModBlocks.HIVE_EYE.get(), "Око разума");
        add("entity.carnis.assimilated_player", "Ассимилированный %s");
        add("death.attack.organic_consumption", "%1$s был поглощён Ульем");
        add("entity.carnis.flesh_amalgam", "Амальгама плоти");
        add("item.carnis.amalgam_bile_glob", "Желчь амальгамы");
        add("entity.carnis.amalgam_bile", "Желчь амальгамы");
        add("tooltip.carnis.amalgam_bile_glob", "Едкий органический сгусток.");
        add("subtitles.carnis.amalgam_smash", "Амальгама сотрясает землю");
        add("subtitles.carnis.organic_creak", "Сухожилие хлещет");
        add(
                "item.carnis.flesh_amalgam_spawn_egg",
                "Яйцо призыва амальгамы плоти"
        );
        add(ModItems.PURIFICATION_SERUM.get(), "Очищающая сыворотка");
        add(ModItems.BIO_PURIFIER.get(), "Очищающий огнемёт");
        add(
                ModItems.NEURO_RESONATOR_HELMET.get(),
                "Нейро-резонаторный шлем"
        );
        add(
                "death.attack.bio_purifier",
                "%1$s сожжён биоочистителем"
        );
        add(
                "death.attack.bio_purifier.player",
                "%1$s сожжён биоочистителем игрока %2$s"
        );

        add("subtitles.carnis.phantom_creeper", "Что-то шипит за спиной");
        add("subtitles.carnis.phantom_footsteps", "Шаги хлюпают по плоти");
        add("subtitles.carnis.phantom_whisper", "Коллективный разум шепчет");
        add("subtitles.carnis.pulsing_heart_beat", "Сердце биома бьётся");
        add("subtitles.carnis.synapse_shock", "Нервный столб разряжается");
        add("subtitles.carnis.synapse_rupture", "Нервная ткань разрывается");
        add("subtitles.carnis.digestor_churn", "Желудочный пруд бурлит");
        add("subtitles.carnis.hive_eye_screech", "Око разума визжит");
        add(
                "subtitles.carnis.amalgamation_fuse",
                "Плоть сливается в амальгаму"
        );
        add(
                "subtitles.carnis.bone_deflect",
                "Снаряд рикошетит от кости"
        );
        add(
                "subtitles.carnis.acid_splash",
                "Едкая кислота брызжет"
        );
        add(
                "subtitles.carnis.flesh_amalgam_ambient",
                "Амальгама плоти стонет"
        );
        add(
                "subtitles.carnis.flesh_amalgam_hurt",
                "Амальгама плоти вздрагивает"
        );
        add(
                "subtitles.carnis.flesh_amalgam_death",
                "Амальгама плоти обрушивается"
        );
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
            "pustule_cluster", () -> new PustuleClusterBlock(BlockBehaviour.Properties.copy(Blocks.MOSS_CARPET)));
    public static final RegistryObject<Block> STOMACH_POOL = BLOCKS.register(
            "stomach_pool", () -> new StomachPoolBlock(BlockBehaviour.Properties.of()
                    .noOcclusion().strength(0.5F).sound(SoundType.SLIME_BLOCK).randomTicks()));

    public static final RegistryObject<Block> SPORE_SPROUT = BLOCKS.register(
            "spore_sprout", () -> new SporeSproutBlock(
                    BlockBehaviour.Properties.copy(Blocks.CRIMSON_ROOTS)));
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
            "pustule_cluster", () -> new BlockItem(ModBlocks.PUSTULE_CLUSTER.get(), new Item.Properties()));
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

## `src/main/resources/data/carnis/tags/entity_types/hive_members.json`

```json
{
  "replace": false,
  "values": [
    "carnis:parasitic_tendril",
    "carnis:biomass_maggot",
    "carnis:hive_sentinel",
    "carnis:cerebral_nexus",
    "carnis:infected_zombie",
    "carnis:infected_skeleton",
    "carnis:infected_creeper",
    "carnis:infected_spider",
    "carnis:flesh_amalgam"
  ]
}
```

## `src/main/resources/data/carnis/loot_tables/blocks/neural_moss.json`

```json
{
  "type": "minecraft:block",
  "pools": [
    {
      "rolls": 1,
      "conditions": [
        {
          "condition": "minecraft:survives_explosion"
        }
      ],
      "entries": [
        {
          "type": "minecraft:alternatives",
          "children": [
            {
              "type": "minecraft:item",
              "name": "carnis:neural_moss",
              "conditions": [
                {
                  "condition": "minecraft:match_tool",
                  "predicate": {
                    "items": [
                      "minecraft:shears"
                    ]
                  }
                }
              ]
            },
            {
              "type": "minecraft:item",
              "name": "carnis:neural_moss",
              "conditions": [
                {
                  "condition": "minecraft:match_tool",
                  "predicate": {
                    "enchantments": [
                      {
                        "enchantment": "minecraft:silk_touch",
                        "levels": {
                          "min": 1
                        }
                      }
                    ]
                  }
                }
              ]
            },
            {
              "type": "minecraft:item",
              "name": "carnis:biomass_remains",
              "conditions": [
                {
                  "condition": "minecraft:random_chance",
                  "chance": 0.25
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## `src/main/resources/assets/carnis/models/item/neural_moss.json`

```json
{
  "parent": "carnis:block/neural_moss",
  "display": {
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
    "thirdperson_lefthand": {
      "rotation": [
        75,
        225,
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
    },
    "firstperson_lefthand": {
      "rotation": [
        0,
        225,
        0
      ],
      "scale": [
        0.4,
        0.4,
        0.4
      ]
    },
    "gui": {
      "rotation": [
        30,
        225,
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
    }
  }
}
```

## `src/main/resources/assets/carnis/models/item/sinew_spikes.json`

```json
{
  "parent": "carnis:block/sinew_spikes",
  "display": {
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
    "thirdperson_lefthand": {
      "rotation": [
        75,
        225,
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
    },
    "firstperson_lefthand": {
      "rotation": [
        0,
        225,
        0
      ],
      "scale": [
        0.4,
        0.4,
        0.4
      ]
    },
    "gui": {
      "rotation": [
        30,
        225,
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
    }
  }
}
```

## `src/main/resources/assets/carnis/models/block/neural_moss.json`

```json
{
  "textures": { "particle": "carnis:block/neural_moss", "all": "carnis:block/neural_moss" },
  "elements": [
    {
      "from": [0, 0, 0], "to": [16, 1, 16],
      "faces": {
        "down": { "texture": "#all" }, "up": { "texture": "#all" },
        "north": { "texture": "#all" }, "south": { "texture": "#all" },
        "west": { "texture": "#all" }, "east": { "texture": "#all" }
      }
    },
    {
      "from": [1, 1, 2], "to": [7, 2, 6],
      "faces": {
        "down": { "texture": "#all" }, "up": { "texture": "#all" },
        "north": { "texture": "#all" }, "south": { "texture": "#all" },
        "west": { "texture": "#all" }, "east": { "texture": "#all" }
      }
    },
    {
      "from": [8, 1, 1], "to": [14, 2, 5],
      "faces": {
        "down": { "texture": "#all" }, "up": { "texture": "#all" },
        "north": { "texture": "#all" }, "south": { "texture": "#all" },
        "west": { "texture": "#all" }, "east": { "texture": "#all" }
      }
    },
    {
      "from": [3, 1, 7], "to": [10, 2, 12],
      "faces": {
        "down": { "texture": "#all" }, "up": { "texture": "#all" },
        "north": { "texture": "#all" }, "south": { "texture": "#all" },
        "west": { "texture": "#all" }, "east": { "texture": "#all" }
      }
    },
    {
      "from": [11, 1, 8], "to": [15, 2, 14],
      "faces": {
        "down": { "texture": "#all" }, "up": { "texture": "#all" },
        "north": { "texture": "#all" }, "south": { "texture": "#all" },
        "west": { "texture": "#all" }, "east": { "texture": "#all" }
      }
    },
    {
      "from": [1, 1, 13], "to": [7, 2, 15],
      "faces": {
        "down": { "texture": "#all" }, "up": { "texture": "#all" },
        "north": { "texture": "#all" }, "south": { "texture": "#all" },
        "west": { "texture": "#all" }, "east": { "texture": "#all" }
      }
    },
    {
      "from": [5, 2, 8], "to": [7, 3, 10],
      "faces": {
        "down": { "texture": "#all" }, "up": { "texture": "#all" },
        "north": { "texture": "#all" }, "south": { "texture": "#all" },
        "west": { "texture": "#all" }, "east": { "texture": "#all" }
      }
    },
    {
      "from": [12, 2, 10], "to": [14, 3, 12],
      "faces": {
        "down": { "texture": "#all" }, "up": { "texture": "#all" },
        "north": { "texture": "#all" }, "south": { "texture": "#all" },
        "west": { "texture": "#all" }, "east": { "texture": "#all" }
      }
    }
  ]
}
```

## `src/main/resources/assets/carnis/models/block/sinew_spikes.json`

```json
{
  "textures": {
    "particle": "carnis:block/sinew_spikes",
    "all": "carnis:block/sinew_spikes"
  },
  "elements": [
    {
      "from": [
        1,
        0,
        1
      ],
      "to": [
        15,
        0.462,
        15
      ],
      "faces": {
        "up": {
          "texture": "#all"
        },
        "down": {
          "texture": "#all"
        },
        "north": {
          "texture": "#all"
        },
        "south": {
          "texture": "#all"
        },
        "east": {
          "texture": "#all"
        },
        "west": {
          "texture": "#all"
        }
      }
    },
    {
      "from": [
        2,
        0.462,
        2
      ],
      "to": [
        5,
        3.231,
        5
      ],
      "faces": {
        "up": {
          "texture": "#all"
        },
        "down": {
          "texture": "#all"
        },
        "north": {
          "texture": "#all"
        },
        "south": {
          "texture": "#all"
        },
        "east": {
          "texture": "#all"
        },
        "west": {
          "texture": "#all"
        }
      }
    },
    {
      "from": [
        3,
        3.231,
        3
      ],
      "to": [
        4,
        4.615,
        4
      ],
      "faces": {
        "up": {
          "texture": "#all"
        },
        "down": {
          "texture": "#all"
        },
        "north": {
          "texture": "#all"
        },
        "south": {
          "texture": "#all"
        },
        "east": {
          "texture": "#all"
        },
        "west": {
          "texture": "#all"
        }
      }
    },
    {
      "from": [
        7,
        0.462,
        4
      ],
      "to": [
        10,
        4.615,
        7
      ],
      "faces": {
        "up": {
          "texture": "#all"
        },
        "down": {
          "texture": "#all"
        },
        "north": {
          "texture": "#all"
        },
        "south": {
          "texture": "#all"
        },
        "east": {
          "texture": "#all"
        },
        "west": {
          "texture": "#all"
        }
      }
    },
    {
      "from": [
        8,
        4.615,
        5
      ],
      "to": [
        9,
        6.0,
        6
      ],
      "faces": {
        "up": {
          "texture": "#all"
        },
        "down": {
          "texture": "#all"
        },
        "north": {
          "texture": "#all"
        },
        "south": {
          "texture": "#all"
        },
        "east": {
          "texture": "#all"
        },
        "west": {
          "texture": "#all"
        }
      }
    },
    {
      "from": [
        10,
        0.462,
        10
      ],
      "to": [
        14,
        2.769,
        14
      ],
      "faces": {
        "up": {
          "texture": "#all"
        },
        "down": {
          "texture": "#all"
        },
        "north": {
          "texture": "#all"
        },
        "south": {
          "texture": "#all"
        },
        "east": {
          "texture": "#all"
        },
        "west": {
          "texture": "#all"
        }
      }
    },
    {
      "from": [
        11,
        2.769,
        11
      ],
      "to": [
        13,
        4.154,
        13
      ],
      "faces": {
        "up": {
          "texture": "#all"
        },
        "down": {
          "texture": "#all"
        },
        "north": {
          "texture": "#all"
        },
        "south": {
          "texture": "#all"
        },
        "east": {
          "texture": "#all"
        },
        "west": {
          "texture": "#all"
        }
      }
    }
  ]
}
```

## `src/generated/resources/assets/carnis/lang/en_us.json`

```json
{
  "block.carnis.charred_flesh": "Charred Flesh",
  "block.carnis.creeping_tendrils": "Creeping Tendrils",
  "block.carnis.fireproof_flesh": "Fireproof Flesh",
  "block.carnis.flesh_bulb": "Flesh Bulb",
  "block.carnis.flesh_veins": "Flesh Veins",
  "block.carnis.hive_eye": "Hive Eye",
  "block.carnis.living_flesh": "Living Flesh",
  "block.carnis.nerve_pillar": "Nerve Pillar",
  "block.carnis.neural_moss": "Neural Moss",
  "block.carnis.ossified_flesh": "Ossified Flesh",
  "block.carnis.pulsing_heart": "Pulsing Heart",
  "block.carnis.pustule_cluster": "Pustule Cluster",
  "block.carnis.sinew_spikes": "Sinew Spikes",
  "block.carnis.spore_sprout": "Spore Sprout",
  "block.carnis.stomach_pool": "Stomach Pool",
  "block.carnis.tainted_sludge": "Tainted Sludge",
  "codex.carnis.body.0": "Veins spread across supported faces; incomplete faces may resist growth. Sludge contaminates players and reacts with water and lava. Infection spreads by a queued process.",
  "codex.carnis.body.1": "FIRE / RANGED / MELEE / EXPLOSIVE use the same logarithmic mitigation curve. Points: 0 / 100 / 300 / 600 / 1000. Reduction: 0% / 25% / 50% / 70% / 80%. Between thresholds: linear interpolation in ln(1+points). Cap 80%.",
  "codex.carnis.body.2": "Hive Eye detects players within 24 blocks and alerts linked mobs within 32. Placing a Nerve Pillar halves remaining chunk shock. Stomach Pool dissolves items: flesh or meat gives 5 biomass each; other items give 1. Living creatures take 4 damage per second.",
  "codex.carnis.body.3": "Serum reduces infection by 35. Antibiotics block positive exposure for 3600 ticks. On an anvil, combine armor and one neural binding matrix for 5 levels. Each woven or resonator armor piece reduces exposure by 25%; four pieces reach 100%.",
  "codex.carnis.body.4": "Zombie: 35 health, 4.5 attack; skeleton: 28 health, 4.5 attack; creeper: 24 health; spider: 20 health, 3 attack. Spat: 2 damage, Slowness II for 100 ticks and +5 exposure on successful damage. Three zombies near a heart at 300 biomass can fuse.",
  "codex.carnis.chapter.0": "Inception & Biomes",
  "codex.carnis.chapter.1": "Adaptive Hivemind",
  "codex.carnis.chapter.2": "Hive Organs & Flora",
  "codex.carnis.chapter.3": "Medical & Armor Weaving",
  "codex.carnis.chapter.4": "Mutants & Amalgamation",
  "death.attack.bio_purifier": "%1$s was incinerated by a bio-purifier",
  "death.attack.bio_purifier.player": "%1$s was incinerated by %2$s's bio-purifier",
  "death.attack.carnis_tainted_sludge": "%1$s dissolved in tainted sludge",
  "death.attack.necrotic_consumption": "%1$s was consumed by the hivemind",
  "death.attack.purification_dart": "%1$s was purified by a dart",
  "death.attack.purification_dart.player": "%1$s was purified by %2$s",
  "effect.carnis.immunosuppression": "Immunosuppression",
  "effect.carnis.incubating": "Incubating",
  "entity.carnis.biomass_maggot": "Biomass Maggot",
  "entity.carnis.flesh_amalgam": "Flesh Amalgam",
  "entity.carnis.flesh_spat": "Flesh Spat",
  "entity.carnis.infected_creeper": "Infected Creeper",
  "entity.carnis.infected_skeleton": "Infected Skeleton",
  "entity.carnis.infected_spider": "Infected Spider",
  "entity.carnis.infected_zombie": "Infected Zombie",
  "entity.carnis.parasitic_tendril": "Parasitic Tendril",
  "entity.carnis.purification_dart": "Purification Dart",
  "entity.carnis.viral_dart": "Viral Dart",
  "fluid_type.carnis.tainted_sludge": "Tainted Sludge",
  "item.carnis.antibiotics": "Antibiotics",
  "item.carnis.bio_purifier": "Bio-Purifier",
  "item.carnis.biomass_maggot_spawn_egg": "Biomass Maggot Spawn Egg",
  "item.carnis.bone_scythe_arm": "Bone Scythe Arm",
  "item.carnis.flesh_amalgam_spawn_egg": "Flesh Amalgam Spawn Egg",
  "item.carnis.flesh_spat": "Flesh Spat",
  "item.carnis.infected_creeper_spawn_egg": "Infected Creeper Spawn Egg",
  "item.carnis.infected_skeleton_spawn_egg": "Infected Skeleton Spawn Egg",
  "item.carnis.infected_spider_spawn_egg": "Infected Spider Spawn Egg",
  "item.carnis.infected_zombie_spawn_egg": "Infected Zombie Spawn Egg",
  "item.carnis.neural_binding_matrix": "Neural Binding Matrix",
  "item.carnis.neuro_resonator_boots": "Neuro-Resonator Boots",
  "item.carnis.neuro_resonator_chestplate": "Neuro-Resonator Chestplate",
  "item.carnis.neuro_resonator_helmet": "Neuro-Resonator Helmet",
  "item.carnis.neuro_resonator_leggings": "Neuro-Resonator Leggings",
  "item.carnis.pneumatic_inoculator": "Pneumatic Inoculator",
  "item.carnis.purification_dart": "Purification Dart",
  "item.carnis.purification_serum": "Purification Serum",
  "item.carnis.research_journal": "Codex Carnis",
  "item.carnis.tainted_sludge_bucket": "Tainted Sludge Bucket",
  "item.carnis.viral_dart": "Viral Dart",
  "itemGroup.carnis": "Carnis: Adaptive Hivemind",
  "subtitles.carnis.acid_splash": "Corrosive acid splashes",
  "subtitles.carnis.amalgam_roar": "Amalgam roars",
  "subtitles.carnis.amalgam_step": "Flesh Amalgam squelches",
  "subtitles.carnis.amalgamation_fuse": "Flesh fuses into an amalgam",
  "subtitles.carnis.bone_deflect": "A projectile ricochets off bone",
  "subtitles.carnis.digestor_churn": "A digestor churns",
  "subtitles.carnis.flamethrower_fire": "Flamethrower roars",
  "subtitles.carnis.flesh_amalgam_ambient": "The Flesh Amalgam groans",
  "subtitles.carnis.flesh_amalgam_death": "The Flesh Amalgam collapses",
  "subtitles.carnis.flesh_amalgam_hurt": "The Flesh Amalgam recoils",
  "subtitles.carnis.heartbeat_loop": "Heart beats",
  "subtitles.carnis.hive_eye_screech": "The hive eye shrieks",
  "subtitles.carnis.phantom_creeper": "Something hisses behind you",
  "subtitles.carnis.phantom_footsteps": "Footsteps squelch through flesh",
  "subtitles.carnis.phantom_whisper": "The hivemind whispers",
  "subtitles.carnis.pulsing_heart_beat": "A biome heart beats",
  "subtitles.carnis.synapse_rupture": "Nerve tissue tears apart",
  "subtitles.carnis.synapse_shock": "A synapse discharges",
  "tooltip.carnis.antibiotics": "Prevents exposure for 3 minutes.",
  "tooltip.carnis.bio_purifier": "Hold use: 6.5-block cone of flame.",
  "tooltip.carnis.bone_scythe_arm": "A jagged bone blade.",
  "tooltip.carnis.charred_flesh": "Burned tissue yields bone meal and charcoal.",
  "tooltip.carnis.creeping_tendrils": "Climb the tendrils attached to solid flesh.",
  "tooltip.carnis.fireproof_flesh": "Adapted tissue resistant to flame.",
  "tooltip.carnis.flesh_amalgam_spawn_egg": "Spawns a Flesh Amalgam.",
  "tooltip.carnis.flesh_spat": "A glob of infectious tissue.",
  "tooltip.carnis.flesh_veins": "Organic growth on exposed surfaces.",
  "tooltip.carnis.hive_eye": "Detects intruders and alerts nearby Amalgams.",
  "tooltip.carnis.hold_shift": "Hold Shift for details",
  "tooltip.carnis.infected_creeper_spawn_egg": "Spawns an infected creeper.",
  "tooltip.carnis.infected_skeleton_spawn_egg": "Spawns an infected skeleton.",
  "tooltip.carnis.infected_spider_spawn_egg": "Spawns an infected spider.",
  "tooltip.carnis.infected_zombie_spawn_egg": "Spawns an infected zombie.",
  "tooltip.carnis.living_flesh": "Living tissue spreads through nearby terrain.",
  "tooltip.carnis.nerve_pillar": "Placement halves remaining shock time in this chunk.",
  "tooltip.carnis.neural_binding_matrix": "Weave into armor at an anvil for five levels.",
  "tooltip.carnis.neural_moss": "A fleshy carpet impedes movement.",
  "tooltip.carnis.neuro_resonator_boots": "Biological boots reduce infection exposure.",
  "tooltip.carnis.neuro_resonator_chestplate": "A biological chestplate reduces infection exposure.",
  "tooltip.carnis.neuro_resonator_helmet": "Dampens hallucinations, reduces exposure by 25% and reveals nearby biomass.",
  "tooltip.carnis.neuro_resonator_leggings": "Biological leggings reduce infection exposure.",
  "tooltip.carnis.ossified_flesh": "Hardened tissue spreads the hive.",
  "tooltip.carnis.pneumatic_inoculator": "Right-click to fire a carried dart; 15-tick cooldown.",
  "tooltip.carnis.pulsing_heart": "The hive heart accelerates nearby infection.",
  "tooltip.carnis.purification_dart": "Removes 35 infection or damages Carnis mobs for 25.",
  "tooltip.carnis.purification_serum": "Drink to remove 35 infection points.",
  "tooltip.carnis.pustule_cluster": "Step on it without sneaking to burst infectious spores.",
  "tooltip.carnis.research_journal": "A field guide to the hive.",
  "tooltip.carnis.spore_sprout": "An organic sprout releases drifting spores.",
  "tooltip.carnis.stomach_pool": "Corrosive tissue dissolves items into biomass.",
  "tooltip.carnis.tainted_sludge_bucket": "A bucket of infectious sludge.",
  "tooltip.carnis.veins": "Living veins carry infection through wood.",
  "tooltip.carnis.viral_dart": "Adds 30 infection to players; poisons and slows mobs.",
  "tooltip.carnis.flesh_bulb.mechanics": "An incubation sac that can attach to ceilings and floors.",
  "tooltip.carnis.flesh_bulb.lore": "The muffled, rapid heartbeat of a maturing brood can be heard inside.",
  "tooltip.carnis.sinew_spikes.mechanics": "Deals piercing damage and slows any creature that steps on it.",
  "tooltip.carnis.sinew_spikes.lore": "Taut sinews respond to the slightest vibration of footsteps.",
  "tooltip.carnis.biomass_maggot.mechanics": "A voracious scavenger. Devours organic remains and pupates in soil.",
  "tooltip.carnis.biomass_maggot.lore": "The first link in the Hive’s parasitic cycle.",
  "subtitles.carnis.inoculator_fire": "Inoculator fires",
  "subtitles.carnis.dart_hit": "Dart hits",
  "block.carnis.biomass_remains": "Biomass Remains",
  "entity.carnis.hive_sentinel": "Hive Sentinel",
  "entity.carnis.cerebral_nexus": "Cerebral Nexus",
  "effect.carnis.thermal_shock": "Thermal Shock",
  "subtitles.carnis.purifier_ignite": "Purifier ignites",
  "subtitles.carnis.purifier_loop": "Purifier fires",
  "item.carnis.amalgam_bile_glob": "Amalgam Bile",
  "entity.carnis.amalgam_bile": "Amalgam Bile",
  "tooltip.carnis.amalgam_bile_glob": "A corrosive organic glob.",
  "subtitles.carnis.amalgam_smash": "Amalgam slams the ground",
  "subtitles.carnis.organic_creak": "Sinew lashes",
  "entity.carnis.assimilated_player": "Assimilated %s",
  "death.attack.organic_consumption": "%1$s was consumed by the hive",
  "tooltip.carnis.neural_moss.mechanics": "Slows outsiders; spreads near water or Hive tissue.",
  "tooltip.carnis.neural_moss.lore": "A living carpet listens for unfamiliar footsteps."
}
```

## `src/generated/resources/assets/carnis/lang/ru_ru.json`

```json
{
  "block.carnis.charred_flesh": "Обугленная плоть",
  "block.carnis.creeping_tendrils": "Ползучие щупальца",
  "block.carnis.fireproof_flesh": "Огнеупорная плоть",
  "block.carnis.flesh_bulb": "Мясная луковица",
  "block.carnis.flesh_veins": "Плотяные жилы",
  "block.carnis.hive_eye": "Око разума",
  "block.carnis.living_flesh": "Живая плоть",
  "block.carnis.nerve_pillar": "Нервный столп",
  "block.carnis.neural_moss": "Нервный мох",
  "block.carnis.ossified_flesh": "Окостенелая плоть",
  "block.carnis.pulsing_heart": "Сердце биома",
  "block.carnis.pustule_cluster": "Скопление пустул",
  "block.carnis.sinew_spikes": "Сухожильные шипы",
  "block.carnis.spore_sprout": "Споровый росток",
  "block.carnis.stomach_pool": "Желудочный бассейн",
  "block.carnis.tainted_sludge": "Заражённая слизь",
  "codex.carnis.body.0": "Вены растут по поддерживаемым граням; неполные грани могут мешать росту. Жижа заражает игроков и реагирует с водой и лавой. Распространение обрабатывается очередью.",
  "codex.carnis.body.1": "ОГОНЬ / ДАЛЬНИЙ / БЛИЖНИЙ / ВЗРЫВ: общая логарифмическая кривая. Очки: 0 / 100 / 300 / 600 / 1000. Снижение: 0% / 25% / 50% / 70% / 80%. Между порогами — интерполяция по ln(1+очки). Предел 80%.",
  "codex.carnis.body.2": "Глаз видит игроков в 24 блоках и предупреждает связанных мобов в 32. Установка нервного столба вдвое сокращает оставшийся шок чанка. Желудочный бассейн даёт 5 биомассы за мясо или плоть, 1 за иной предмет; живым наносит 4 урона в секунду.",
  "codex.carnis.body.3": "Сыворотка снижает заражение на 35. Антибиотики блокируют положительную экспозицию на 3600 тиков. На наковальне соедините броню с одной матрицей за 5 уровней. Каждая защищённая часть снижает экспозицию на 25%, четыре — на 100%.",
  "codex.carnis.body.4": "Зомби: 35 здоровья, 4,5 урона; скелет: 28 и 4,5; крипер: 24 здоровья; паук: 20 и 3. Плевок: 2 урона, замедление II на 100 тиков и +5 экспозиции при успешном уроне. Три зомби у сердца при 300 биомассы могут слиться.",
  "codex.carnis.chapter.0": "Истоки и биомы",
  "codex.carnis.chapter.1": "Адаптивный разум",
  "codex.carnis.chapter.2": "Органы и флора улья",
  "codex.carnis.chapter.3": "Медицина и нейроплетение",
  "codex.carnis.chapter.4": "Мутанты и слияние",
  "death.attack.bio_purifier": "%1$s сожжён биоочистителем",
  "death.attack.bio_purifier.player": "%1$s сожжён биоочистителем игрока %2$s",
  "death.attack.carnis_tainted_sludge": "%1$s растворился в заражённой жиже",
  "death.attack.necrotic_consumption": "%1$s поглощён коллективным разумом",
  "death.attack.purification_dart": "%1$s очищен дротиком",
  "death.attack.purification_dart.player": "%1$s очищен игроком %2$s",
  "effect.carnis.immunosuppression": "Иммуносупрессия",
  "effect.carnis.incubating": "Инкубация",
  "entity.carnis.biomass_maggot": "Личинка биомассы",
  "entity.carnis.flesh_amalgam": "Амальгама плоти",
  "entity.carnis.flesh_spat": "Плевок плоти",
  "entity.carnis.infected_creeper": "Заражённый крипер",
  "entity.carnis.infected_skeleton": "Заражённый скелет",
  "entity.carnis.infected_spider": "Заражённый паук",
  "entity.carnis.infected_zombie": "Заражённый зомби",
  "entity.carnis.parasitic_tendril": "Паразитический усик",
  "entity.carnis.purification_dart": "Очищающий дротик",
  "entity.carnis.viral_dart": "Вирусный дротик",
  "fluid_type.carnis.tainted_sludge": "Заражённая слизь",
  "item.carnis.antibiotics": "Антибиотики",
  "item.carnis.bio_purifier": "Очищающий огнемёт",
  "item.carnis.biomass_maggot_spawn_egg": "Яйцо призыва: Личинка биомассы",
  "item.carnis.bone_scythe_arm": "Костяная коса-рука",
  "item.carnis.flesh_amalgam_spawn_egg": "Яйцо призыва амальгамы плоти",
  "item.carnis.flesh_spat": "Плевок плоти",
  "item.carnis.infected_creeper_spawn_egg": "Яйцо призыва: Заражённый крипер",
  "item.carnis.infected_skeleton_spawn_egg": "Яйцо призыва: Заражённый скелет",
  "item.carnis.infected_spider_spawn_egg": "Яйцо призыва: Заражённый паук",
  "item.carnis.infected_zombie_spawn_egg": "Яйцо призыва заражённого зомби",
  "item.carnis.neural_binding_matrix": "Матрица нейронного сплетения",
  "item.carnis.neuro_resonator_boots": "Нейро-резонаторные ботинки",
  "item.carnis.neuro_resonator_chestplate": "Нейро-резонаторный нагрудник",
  "item.carnis.neuro_resonator_helmet": "Нейро-резонаторный шлем",
  "item.carnis.neuro_resonator_leggings": "Нейро-резонаторные поножи",
  "item.carnis.pneumatic_inoculator": "Пневматический инокулятор",
  "item.carnis.purification_dart": "Очищающий дротик",
  "item.carnis.purification_serum": "Очищающая сыворотка",
  "item.carnis.research_journal": "Кодекс Карнис",
  "item.carnis.tainted_sludge_bucket": "Ведро заражённой слизи",
  "item.carnis.viral_dart": "Вирусный дротик",
  "itemGroup.carnis": "Carnis: Адаптивный коллективный разум",
  "subtitles.carnis.acid_splash": "Едкая кислота брызжет",
  "subtitles.carnis.amalgam_roar": "Амальгама ревёт",
  "subtitles.carnis.amalgam_step": "Плотяная амальгама чавкает",
  "subtitles.carnis.amalgamation_fuse": "Плоть сливается в амальгаму",
  "subtitles.carnis.bone_deflect": "Снаряд рикошетит от кости",
  "subtitles.carnis.digestor_churn": "Желудочный пруд бурлит",
  "subtitles.carnis.flamethrower_fire": "Огнемёт ревёт",
  "subtitles.carnis.flesh_amalgam_ambient": "Амальгама плоти стонет",
  "subtitles.carnis.flesh_amalgam_death": "Амальгама плоти обрушивается",
  "subtitles.carnis.flesh_amalgam_hurt": "Амальгама плоти вздрагивает",
  "subtitles.carnis.heartbeat_loop": "Сердце бьётся",
  "subtitles.carnis.hive_eye_screech": "Око разума визжит",
  "subtitles.carnis.phantom_creeper": "Что-то шипит за спиной",
  "subtitles.carnis.phantom_footsteps": "Шаги хлюпают по плоти",
  "subtitles.carnis.phantom_whisper": "Коллективный разум шепчет",
  "subtitles.carnis.pulsing_heart_beat": "Сердце биома бьётся",
  "subtitles.carnis.synapse_rupture": "Нервная ткань разрывается",
  "subtitles.carnis.synapse_shock": "Нервный столб разряжается",
  "tooltip.carnis.antibiotics": "Предотвращает заражение на 3 минуты.",
  "tooltip.carnis.bio_purifier": "Удерживайте: конус пламени на 6,5 блока.",
  "tooltip.carnis.bone_scythe_arm": "Зазубренный костяной клинок.",
  "tooltip.carnis.charred_flesh": "Обгоревшая ткань даёт костную муку и уголь.",
  "tooltip.carnis.creeping_tendrils": "Взбирайтесь по усикам на поверхности плоти.",
  "tooltip.carnis.fireproof_flesh": "Ткань, приспособленная к огню.",
  "tooltip.carnis.flesh_amalgam_spawn_egg": "Призывает амальгаму плоти.",
  "tooltip.carnis.flesh_spat": "Сгусток заражённой ткани.",
  "tooltip.carnis.flesh_veins": "Органические жилы на открытых поверхностях.",
  "tooltip.carnis.hive_eye": "Обнаруживает чужаков и тревожит ближайших амальгам.",
  "tooltip.carnis.hold_shift": "Удерживайте Shift для подробностей",
  "tooltip.carnis.infected_creeper_spawn_egg": "Призывает заражённого крипера.",
  "tooltip.carnis.infected_skeleton_spawn_egg": "Призывает заражённого скелета.",
  "tooltip.carnis.infected_spider_spawn_egg": "Призывает заражённого паука.",
  "tooltip.carnis.infected_zombie_spawn_egg": "Призывает заражённого зомби.",
  "tooltip.carnis.living_flesh": "Живая ткань распространяется по окружающим блокам.",
  "tooltip.carnis.nerve_pillar": "При установке вдвое сокращает оставшийся шок чанка.",
  "tooltip.carnis.neural_binding_matrix": "Вплетите в броню на наковальне за пять уровней.",
  "tooltip.carnis.neural_moss": "Мясистый мох замедляет движение.",
  "tooltip.carnis.neuro_resonator_boots": "Биологические ботинки снижают заражение.",
  "tooltip.carnis.neuro_resonator_chestplate": "Биологический нагрудник снижает заражение.",
  "tooltip.carnis.neuro_resonator_helmet": "Подавляет галлюцинации, снижает экспозицию на 25% и обнаруживает биомассу.",
  "tooltip.carnis.neuro_resonator_leggings": "Биологические поножи снижают заражение.",
  "tooltip.carnis.ossified_flesh": "Окостеневшая ткань распространяет улей.",
  "tooltip.carnis.pneumatic_inoculator": "ПКМ: выстрел дротиком из инвентаря; задержка 15 тиков.",
  "tooltip.carnis.pulsing_heart": "Сердце улья ускоряет заражение поблизости.",
  "tooltip.carnis.purification_dart": "Снимает 35 заражения или наносит мобам Carnis 25 урона.",
  "tooltip.carnis.purification_serum": "Выпейте, чтобы снизить заражение на 35 пунктов.",
  "tooltip.carnis.pustule_cluster": "Наступите без приседания: пустулы лопнут и заразят вас.",
  "tooltip.carnis.research_journal": "Полевой справочник по улью.",
  "tooltip.carnis.spore_sprout": "Органический росток выпускает споры.",
  "tooltip.carnis.stomach_pool": "Едкая ткань растворяет предметы в биомассу.",
  "tooltip.carnis.tainted_sludge_bucket": "Ведро заразной слизи.",
  "tooltip.carnis.veins": "Живые вены несут инфекцию через древесину.",
  "tooltip.carnis.viral_dart": "Добавляет игрокам 30 заражения; травит и замедляет мобов.",
  "tooltip.carnis.flesh_bulb.mechanics": "Инкубационный мешок, способный закрепляться на потолке и полу.",
  "tooltip.carnis.flesh_bulb.lore": "Внутри слышно глухое, частое сердцебиение зреющего выводка.",
  "tooltip.carnis.sinew_spikes.mechanics": "Наносят колющий урон и замедляют любое наступившее существо.",
  "tooltip.carnis.sinew_spikes.lore": "Натянутые жилы реагируют на малейшую вибрацию шагов.",
  "tooltip.carnis.biomass_maggot.mechanics": "Ненасытный трупоед. Пожирает органические останки и окукливается в почве.",
  "tooltip.carnis.biomass_maggot.lore": "Начальное звено паразитического круговорота Улья.",
  "subtitles.carnis.inoculator_fire": "Выстрел инокулятора",
  "subtitles.carnis.dart_hit": "Дротик ударяется",
  "block.carnis.biomass_remains": "Останки биомассы",
  "entity.carnis.hive_sentinel": "Страж Улья",
  "entity.carnis.cerebral_nexus": "Мозговой узел",
  "effect.carnis.thermal_shock": "Термический шок",
  "subtitles.carnis.purifier_ignite": "Очиститель зажигается",
  "subtitles.carnis.purifier_loop": "Очиститель выпускает пламя",
  "item.carnis.amalgam_bile_glob": "Желчь амальгамы",
  "entity.carnis.amalgam_bile": "Желчь амальгамы",
  "tooltip.carnis.amalgam_bile_glob": "Едкий органический сгусток.",
  "subtitles.carnis.amalgam_smash": "Амальгама сотрясает землю",
  "subtitles.carnis.organic_creak": "Сухожилие хлещет",
  "entity.carnis.assimilated_player": "Ассимилированный %s",
  "death.attack.organic_consumption": "%1$s был поглощён Ульем",
  "tooltip.carnis.neural_moss.mechanics": "Замедляет чужаков; растёт у воды и тканей Улья.",
  "tooltip.carnis.neural_moss.lore": "Живой ковёр прислушивается к чужим шагам."
}
```
