# Этап 1 — полный код изменённых и созданных файлов

Все файлы представлены целиком; удалённые файлы перечислены в аудит-логе ответа.

## `gradle.properties`

```properties
# Gradle settings
org.gradle.jvmargs=-Xmx3G -Dfile.encoding=UTF-8
org.gradle.daemon=false
org.gradle.parallel=false
org.gradle.workers.max=2
org.gradle.caching=true
org.gradle.configuration-cache=false
org.gradle.warning.mode=all

# Project properties
mod_id=carnis
mod_name=Carnis: Adaptive Hivemind
mod_license=MIT
mod_version=3.0.0
mod_author=BlockBaster3K
mod_authors=BlockBaster3K
mod_group_id=com.carnis.mod
mod_description=An adaptive organic hivemind mod with procedural growth and GeckoLib animations.

# Versions
minecraft_version=1.20.1
minecraft_version_range=[1.20.1,1.21)
forge_version=47.4.5
forge_version_range=[47,48)
loader_version_range=[47,)
geckolib_version=4.4.4
geckolib_version_range=[4.4.4,)
mapping_channel=official
mapping_version=1.20.1
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

    public static final RegistryObject<Block> FLESH_BULB = BLOCKS.register("flesh_bulb",
            () -> new com.carnis.mod.block.FleshBulbBlock(BlockBehaviour.Properties.copy(Blocks.CRIMSON_ROOTS)
                    .noCollission().noOcclusion().sound(SoundType.SLIME_BLOCK)));
    public static final RegistryObject<Block> SINEW_SPIKES = BLOCKS.register("sinew_spikes",
            () -> new com.carnis.mod.block.SinewSpikesBlock(BlockBehaviour.Properties.copy(Blocks.CRIMSON_ROOTS)
                    .noCollission().noOcclusion().sound(SoundType.BONE_BLOCK)));

    public static final RegistryObject<Block> NERVE_PILLAR = BLOCKS.register(
            "nerve_pillar", () -> new NervePillarBlock(BlockBehaviour.Properties.of()
                    .strength(2.0F).sound(SoundType.SLIME_BLOCK)));

    public static final RegistryObject<Block> CREEPING_TENDRILS = BLOCKS.register(
            "creeping_tendrils", () -> new CreepingTendrilsBlock(BlockBehaviour.Properties.copy(Blocks.LADDER).sound(SoundType.SLIME_BLOCK)));
    public static final RegistryObject<Block> PUSTULE_CLUSTER = BLOCKS.register(
            "pustule_cluster", () -> new PustuleClusterBlock(BlockBehaviour.Properties.copy(Blocks.MOSS_CARPET)));
    public static final RegistryObject<Block> STOMACH_POOL = BLOCKS.register(
            "stomach_pool", () -> new StomachPoolBlock(BlockBehaviour.Properties.of()
                    .noCollission().strength(0.5F).sound(SoundType.SLIME_BLOCK)));

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
    public static final RegistryObject<com.carnis.mod.item.ResearchJournalItem> RESEARCH_JOURNAL = ITEMS.register(
            "research_journal", () -> new com.carnis.mod.item.ResearchJournalItem(new Item.Properties().stacksTo(1)));
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
            () -> new BlockItem(ModBlocks.NERVE_PILLAR.get(), new Item.Properties()));
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
            "stomach_pool", () -> new BlockItem(ModBlocks.STOMACH_POOL.get(), new Item.Properties()));

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
            () -> new BlockItem(
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

    public static final RegistryObject<CreativeModeTab> CARNIS_TAB =
            CREATIVE_TABS.register("carnis", () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.carnis"))
                    .icon(() -> ModItems.LIVING_FLESH.get().getDefaultInstance())
                    .displayItems((parameters, output) -> {
                        output.accept(ModItems.LIVING_FLESH.get());
                        output.accept(ModItems.CHARRED_FLESH.get());
                        output.accept(ModItems.FLESH_BULB.get());
                        output.accept(ModItems.SINEW_SPIKES.get());
                        output.accept(ModItems.BIOMASS_MAGGOT_SPAWN_EGG.get());
                        output.accept(ModItems.CREEPING_TENDRILS.get());
                        output.accept(ModItems.PUSTULE_CLUSTER.get());
                        output.accept(ModItems.STOMACH_POOL.get());
                        output.accept(ModItems.NERVE_PILLAR.get());
                        output.accept(ModItems.PNEUMATIC_INOCULATOR.get());
                        output.accept(ModItems.VIRAL_DART.get());
                        output.accept(ModItems.PURIFICATION_DART.get());
                        output.accept(ModItems.SPORE_SPROUT.get());
                        output.accept(ModItems.NEURAL_MOSS.get());
                        output.accept(ModItems.OSSIFIED_FLESH.get());
                        output.accept(ModItems.FIREPROOF_FLESH.get());
                        output.accept(ModItems.FLESH_VEINS.get());
                        output.accept(ModItems.TAINTED_SLUDGE_BUCKET.get());
                        output.accept(ModItems.BONE_SCYTHE_ARM.get());
                        output.accept(ModItems.PULSING_HEART.get());
                        output.accept(ModItems.HIVE_EYE.get());
                        output.accept(ModItems.FLESH_AMALGAM_SPAWN_EGG.get());
                        output.accept(ModItems.INFECTED_ZOMBIE_SPAWN_EGG.get());
                        output.accept(ModItems.INFECTED_SKELETON_SPAWN_EGG.get());
                        output.accept(ModItems.INFECTED_CREEPER_SPAWN_EGG.get());
                        output.accept(ModItems.INFECTED_SPIDER_SPAWN_EGG.get());

                        output.accept(ModItems.RESEARCH_JOURNAL.get());
                        output.accept(ModItems.ANTIBIOTICS.get());
                        output.accept(ModItems.PURIFICATION_SERUM.get());
                        output.accept(ModItems.BIO_PURIFIER.get());
                        output.accept(ModItems.NEURO_RESONATOR_HELMET.get());
                        output.accept(ModItems.NEURO_RESONATOR_CHESTPLATE.get());
                        output.accept(ModItems.NEURO_RESONATOR_LEGGINGS.get());
                        output.accept(ModItems.NEURO_RESONATOR_BOOTS.get());
                        output.accept(ModItems.NEURAL_BINDING_MATRIX.get());
                    })
                    .build());

    private ModCreativeTabs() {
    }

    public static void register(IEventBus modEventBus) {
        CREATIVE_TABS.register(modEventBus);
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
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.MultifaceBlock;
import net.minecraft.world.level.block.MultifaceSpreader;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;

public final class FleshVeinsBlock extends MultifaceBlock {
    private final MultifaceSpreader spreader = new MultifaceSpreader(this);

    public FleshVeinsBlock(BlockBehaviour.Properties properties) { super(properties); }

    @Override
    public MultifaceSpreader getSpreader() { return spreader; }

    @Override
    public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
                                  LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        BlockState updated = super.updateShape(state, direction, neighbor, level, pos, neighborPos);
        if (!updated.is(this) || !MultifaceBlock.hasFace(updated, direction)
                || neighbor.isFaceSturdy(level, neighborPos, direction.getOpposite())) {
            return updated;
        }
        updated = updated.setValue(MultifaceBlock.getFaceProperty(direction), false);
        for (Direction face : Direction.values()) {
            if (MultifaceBlock.hasFace(updated, face)) return updated;
        }
        return state.getFluidState().is(Fluids.WATER)
                ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState();
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        VeinMutationEngine.tickVein(level, pos, state, random);
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

## `src/main/java/com/carnis/mod/item/BioPurifierItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.FleshIncineration;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModDamageTypes;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
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

import java.util.Optional;

public final class BioPurifierItem extends Item implements software.bernie.geckolib.animatable.GeoItem {
    private final software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache geoCache =
            software.bernie.geckolib.util.GeckoLibUtil.createInstanceCache(this);

    @Override public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientItemExtensions> consumer) {
        consumer.accept(new net.minecraftforge.client.extensions.common.IClientItemExtensions() {
            private com.carnis.mod.client.renderer.BioPurifierRenderer renderer;
            @Override public net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new com.carnis.mod.client.renderer.BioPurifierRenderer();
                return renderer;
            }
        });
    }
    @Override public void registerControllers(software.bernie.geckolib.core.animation.AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this, "idle", 0,
                state -> state.setAndContinue(software.bernie.geckolib.core.animation.RawAnimation.begin().thenLoop(
                        com.carnis.mod.client.BioPurifierAnimationState.isFiring(state)
                                ? "animation.bio_purifier.firing" : "animation.bio_purifier.idle"))));
    }
    @Override public software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache getAnimatableInstanceCache() { return geoCache; }

    public static final int MAX_DURABILITY = 800;
    public static final float CARNIS_DAMAGE = 3.0F;
    public static final float STANDARD_DAMAGE = 1.0F;
    public static final float ARMOR_BYPASS_FRACTION = 0.35F;
    public static final float INFECTED_BLOCK_BURN_CHANCE = 0.35F;

    private static final int USE_DURATION_TICKS = 72_000;
    private static final int BURST_INTERVAL_TICKS = 4;
    private static final int FIRE_DURATION_SECONDS = 4;
    private static final int PARTICLE_STEPS = 10;
    private static final double RANGE = 6.0D;
    private static final double ENTITY_HIT_INFLATION = 0.35D;

    public BioPurifierItem(Properties properties) {
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
    public void onUseTick(
            Level level,
            LivingEntity user,
            ItemStack stack,
            int remainingUseDuration
    ) {
        if (stack.isEmpty()) {
            user.stopUsingItem();
            return;
        }

        int elapsedTicks = getUseDuration(stack) - remainingUseDuration;

        if (!(level instanceof ServerLevel serverLevel)) {
            return;
        }

        Vec3 direction = user.getLookAngle().normalize();
        double yaw = Math.toRadians(user.getYRot());
        Vec3 right = new Vec3(-Math.cos(yaw), 0.0D, -Math.sin(yaw));
        Vec3 eye = user.getEyePosition();
        // X is horizontal right, Y is world up, and Z follows the full look vector.
        Vec3 start = eye.add(right.scale(0.28D)).add(0.0D, -0.35D, 0.0D)
                .add(direction.scale(0.85D));
        // If a wall separates eye and muzzle, suppress the shot rather than move its origin.
        BlockHitResult muzzleCheck = serverLevel.clip(new ClipContext(eye, start,
                ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, user));
        if (muzzleCheck.getType() == HitResult.Type.BLOCK) return;
        Vec3 maximumEnd = start.add(direction.scale(RANGE));
        BlockHitResult blockHit = serverLevel.clip(
                new ClipContext(
                        start,
                        maximumEnd,
                        ClipContext.Block.OUTLINE,
                        ClipContext.Fluid.NONE,
                        user
                )
        );
        Vec3 streamEnd = blockHit.getType() == HitResult.Type.BLOCK
                ? blockHit.getLocation()
                : maximumEnd;

        emitFlameStream(serverLevel, start, streamEnd);

        if (elapsedTicks % BURST_INTERVAL_TICKS != 0) {
            return;
        }

        LivingEntity target = findLivingTarget(
                serverLevel,
                user,
                start,
                streamEnd
        );

        if (target != null) {
            damageTarget(serverLevel, user, target);
        }

        if (blockHit.getType() == HitResult.Type.BLOCK) {
            tryBurnInfectedBlock(serverLevel, blockHit.getBlockPos());
        }

        if (!(user instanceof Player player)
                || !player.getAbilities().instabuild) {
            stack.hurtAndBreak(
                    1,
                    user,
                    entity -> entity.broadcastBreakEvent(
                            entity.getUsedItemHand()
                    )
            );
        }
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.NONE;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return USE_DURATION_TICKS;
    }

    private static LivingEntity findLivingTarget(
            ServerLevel level,
            LivingEntity user,
            Vec3 start,
            Vec3 end
    ) {
        AABB searchArea = new AABB(start, end)
                .inflate(1.0D + ENTITY_HIT_INFLATION);
        LivingEntity closestTarget = null;
        double closestDistanceSquared = Double.MAX_VALUE;

        for (LivingEntity candidate : level.getEntitiesOfClass(
                LivingEntity.class,
                searchArea,
                entity -> entity != user
                        && entity.isAlive()
                        && !entity.isSpectator()
        )) {
            Optional<Vec3> intersection = candidate.getBoundingBox()
                    .inflate(ENTITY_HIT_INFLATION)
                    .clip(start, end);

            if (intersection.isEmpty()) {
                continue;
            }

            double distanceSquared = start.distanceToSqr(intersection.get());

            if (distanceSquared < closestDistanceSquared) {
                closestDistanceSquared = distanceSquared;
                closestTarget = candidate;
            }
        }

        return closestTarget;
    }

    private static void damageTarget(
            ServerLevel level,
            LivingEntity user,
            LivingEntity target
    ) {
        float totalDamage = isCarnisMob(target)
                ? CARNIS_DAMAGE
                : STANDARD_DAMAGE;
        float armorBypassingDamage = totalDamage * ARMOR_BYPASS_FRACTION;
        float surfaceFireDamage = totalDamage - armorBypassingDamage;

        target.setSecondsOnFire(FIRE_DURATION_SECONDS);
        // Bypass the usual invulnerability window so the stream of a
        // flamethrower applies steady damage instead of being swallowed
        // between bursts. The custom damage source lands first so the
        // killing blow credits the wielder in the death message.
        target.invulnerableTime = 0;
        target.hurt(
                ModDamageTypes.bioPurifier(level, user),
                armorBypassingDamage
        );

        if (target.isAlive()) {
            target.invulnerableTime = 0;
            target.hurt(
                    ModDamageTypes.bioPurifierSurface(level, user),
                    surfaceFireDamage
            );
        }
    }

    private static boolean isCarnisMob(LivingEntity entity) {
        if (entity instanceof HivemindLinkedMob) {
            return true;
        }

        ResourceLocation entityTypeId = ForgeRegistries.ENTITY_TYPES.getKey(
                entity.getType()
        );

        return entityTypeId != null
                && CarnisMod.MOD_ID.equals(entityTypeId.getNamespace());
    }

    private static void tryBurnInfectedBlock(
            ServerLevel level,
            BlockPos blockPos
    ) {
        BlockState infectedState = level.getBlockState(blockPos);
        boolean living = infectedState.is(ModBlocks.LIVING_FLESH.get());
        boolean ossified = infectedState.is(ModBlocks.OSSIFIED_FLESH.get());
        boolean fireproof = infectedState.is(ModBlocks.FIREPROOF_FLESH.get());
        boolean veins = infectedState.is(ModBlocks.FLESH_VEINS.get());
        if (!living && !ossified && !fireproof && !veins) return;
        if (living || ossified) {
            if (!FleshIncineration.tryBurn(level, blockPos, infectedState)) return;
        } else if (!level.setBlockAndUpdate(blockPos, veins
                ? Blocks.AIR.defaultBlockState() : ModBlocks.CHARRED_FLESH.get().defaultBlockState())) {
            return;
        }

        Vec3 center = Vec3.atCenterOf(blockPos);
        level.sendParticles(
                ParticleTypes.LARGE_SMOKE,
                center.x,
                center.y,
                center.z,
                12,
                0.35D,
                0.35D,
                0.35D,
                0.025D
        );
        level.sendParticles(
                ParticleTypes.LAVA,
                center.x,
                center.y,
                center.z,
                5,
                0.28D,
                0.28D,
                0.28D,
                0.05D
        );
    }

    private static void emitFlameStream(
            ServerLevel level,
            Vec3 start,
            Vec3 end
    ) {
        Vec3 stream = end.subtract(start);

        // This first particle is emitted at the exact ray origin, with no positional spread.
        level.sendParticles(ParticleTypes.FLAME, start.x, start.y, start.z, 1, 0, 0, 0, 0);
        for (int step = 1; step <= PARTICLE_STEPS; step++) {
            double progress = step / (double) PARTICLE_STEPS;
            Vec3 point = start.add(stream.scale(progress));

            level.sendParticles(
                    ParticleTypes.FLAME,
                    point.x,
                    point.y,
                    point.z,
                    2,
                    0.035D,
                    0.035D,
                    0.035D,
                    0.015D
            );

            if (step % 2 == 0) {
                level.sendParticles(
                        ParticleTypes.SMOKE,
                        point.x,
                        point.y,
                        point.z,
                        1,
                        0.045D,
                        0.045D,
                        0.045D,
                        0.01D
                );
            }
        }
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

## `src/main/java/com/carnis/mod/datagen/CarnisTextureDataGen.java`

```java
package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.google.common.hash.Hashing;
import net.minecraft.data.CachedOutput;
import net.minecraft.data.DataProvider;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.PackType;
import net.minecraftforge.common.data.ExistingFileHelper;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public final class CarnisTextureDataGen implements DataProvider {
    private static final int SIZE = 32;
    private static final int MASK = SIZE - 1;
    private static final long SEED = 0xCA47152L;
    private static final ExistingFileHelper.ResourceType TEXTURE_TYPE =
            new ExistingFileHelper.ResourceType(PackType.CLIENT_RESOURCES, ".png", "textures");

    private final PackOutput.PathProvider blocks;
    private final PackOutput.PathProvider entities;
    private final PackOutput.PathProvider items;
    private final PackOutput.PathProvider armor;
    private final List<Texture> textures = new ArrayList<>();

    public CarnisTextureDataGen(PackOutput output, ExistingFileHelper existingFiles) {
        blocks = output.createPathProvider(PackOutput.Target.RESOURCE_PACK, "textures/block");
        entities = output.createPathProvider(PackOutput.Target.RESOURCE_PACK, "textures/entity");
        items = output.createPathProvider(PackOutput.Target.RESOURCE_PACK, "textures/item");
        armor = output.createPathProvider(PackOutput.Target.RESOURCE_PACK, "textures/armor");

        for (int variant = 0; variant < 4; variant++) {
            register(existingFiles, "block", "living_flesh_" + variant, Kind.LIVING, variant);
            register(existingFiles, "block", "ossified_flesh_" + variant, Kind.OSSIFIED, variant);
            register(existingFiles, "block", "charred_flesh_" + variant, Kind.CHARRED, variant);
        }
        register(existingFiles, "block", "living_flesh", Kind.LIVING, 0);
        register(existingFiles, "block", "ossified_flesh", Kind.OSSIFIED, 0);
        register(existingFiles, "block", "charred_flesh", Kind.CHARRED, 0);
        register(existingFiles, "block", "fireproof_flesh", Kind.FIREPROOF, 0);
        register(existingFiles, "block", "flesh_veins", Kind.VEINS, 0);
        register(existingFiles, "block", "neural_moss", Kind.MOSS, 0);
        register(existingFiles, "block", "pulsing_heart", Kind.HEART, 0);
        register(existingFiles, "block", "hive_eye", Kind.EYE, 0);
        register(existingFiles, "block", "nerve_pillar", Kind.NERVE, 0);
        register(existingFiles, "block", "stomach_pool", Kind.STOMACH, 0);
        register(existingFiles, "block", "pustule_cluster", Kind.PUSTULE, 0);
        register(existingFiles, "block", "spore_sprout", Kind.SPORE, 0);
        register(existingFiles, "block", "flesh_bulb", Kind.BULB, 0);
        register(existingFiles, "block", "sinew_spikes", Kind.SPIKES, 0);
        register(existingFiles, "block", "creeping_tendrils", Kind.TENDRILS, 0);

        register(existingFiles, "item", "viral_dart", Kind.VIRAL_DART, 0);
        register(existingFiles, "item", "purification_dart", Kind.PURIFICATION_DART, 0);
        register(existingFiles, "item", "purification_serum", Kind.SERUM, 0);
        register(existingFiles, "item", "neural_binding_matrix", Kind.MATRIX, 0);
        register(existingFiles, "item", "creeping_tendrils", Kind.TENDRILS, 0);
        register(existingFiles, "item", "bio_purifier", Kind.GUN_ICON, 0);
        register(existingFiles, "item", "bio_purifier_geo", Kind.GUN_GEO, 0);
        register(existingFiles, "item", "pneumatic_inoculator", Kind.INOCULATOR_ICON, 0);
        register(existingFiles, "item", "pneumatic_inoculator_geo", Kind.INOCULATOR_GEO, 0);
        register(existingFiles, "item", "neuro_resonator_helmet", Kind.HELMET, 0);
        register(existingFiles, "item", "neuro_resonator_chestplate", Kind.CHESTPLATE, 0);
        register(existingFiles, "item", "neuro_resonator_leggings", Kind.LEGGINGS, 0);
        register(existingFiles, "item", "neuro_resonator_boots", Kind.BOOTS, 0);
        register(existingFiles, "item", "flesh_amalgam_spawn_egg", Kind.EGG, 0);
        register(existingFiles, "item", "tainted_sludge_bucket", Kind.BUCKET, 0);

        register(existingFiles, "entity", "incubation_overlay", Kind.OVERLAY, 0);
        register(existingFiles, "entity", "biomass_maggot", Kind.LIVING, 1);
        register(existingFiles, "entity", "parasitic_tendril", Kind.TENDRILS, 0);
        register(existingFiles, "entity", "infected_zombie", Kind.LIVING, 2);
        register(existingFiles, "entity", "infected_skeleton", Kind.OSSIFIED, 1);
        register(existingFiles, "armor", "neuro_armor", Kind.ARMOR_SHEET, 0);
    }

    private void register(ExistingFileHelper files, String folder, String name, Kind kind, int variant) {
        textures.add(new Texture(folder, name, kind, variant));
        files.trackGenerated(new ResourceLocation(CarnisMod.MOD_ID, folder + "/" + name), TEXTURE_TYPE);
    }

    @Override
    public CompletableFuture<?> run(CachedOutput cache) {
        try {
            for (Texture texture : textures) {
                BufferedImage image = createTexture(texture.kind(), texture.variant());
                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                if (!ImageIO.write(image, "png", bytes)) throw new IOException("PNG writer unavailable");
                byte[] encoded = bytes.toByteArray();
                PackOutput.PathProvider provider = switch (texture.folder()) {
                    case "block" -> blocks;
                    case "entity" -> entities;
                    case "item" -> items;
                    case "armor" -> armor;
                    default -> throw new IllegalStateException("Unknown texture folder: " + texture.folder());
                };
                Path destination = provider.file(new ResourceLocation(CarnisMod.MOD_ID, texture.name()), "png");
                cache.writeIfNeeded(destination, encoded, Hashing.sha256().hashBytes(encoded));
            }
            return CompletableFuture.completedFuture(null);
        } catch (IOException exception) {
            return CompletableFuture.failedFuture(exception);
        }
    }

    @Override
    public String getName() {
        return "Carnis organic procedural textures";
    }

    private static BufferedImage createTexture(Kind kind, int variant) {
        return switch (kind) {
            case VIRAL_DART -> dart(false);
            case PURIFICATION_DART -> dart(true);
            case SERUM -> serum();
            case MATRIX -> matrix();
            case TENDRILS -> tendrils();
            case GUN_ICON, GUN_GEO -> purifier();
            case INOCULATOR_ICON, INOCULATOR_GEO -> inoculator();
            case HELMET -> armorItem(0);
            case CHESTPLATE -> armorItem(1);
            case LEGGINGS -> armorItem(2);
            case BOOTS -> armorItem(3);
            case EGG -> spawnEgg();
            case BUCKET -> sludgeBucket();
            case ARMOR_SHEET -> armorSheet();
            default -> generateNoiseTexture(kind, variant);
        };
    }

    private static BufferedImage generateNoiseTexture(Kind kind, int variant) {
        BufferedImage image = new BufferedImage(SIZE, SIZE, BufferedImage.TYPE_INT_ARGB);
        long seed = SEED + variant * 8317L + kind.ordinal() * 11897L;
        boolean[][] cells = cellular(seed);
        for (int y = 0; y < SIZE; y++) {
            for (int x = 0; x < SIZE; x++) {
                double noise = fbm(x, y, seed);
                double warp = gradientNoise(x, y, 8, seed + 17) * 2.2;
                double fiber = Math.sin((x * .36) + (y * .43) + warp * 2.7);
                double fine = Math.sin((x * .95) + (y * .77) + warp * 1.8);
                int color = switch (kind) {
                    case LIVING -> living(noise, fiber, fine);
                    case OSSIFIED -> ossified(noise, fiber, fine, cells[y][x]);
                    case CHARRED -> charred(noise, fiber, cells, x, y);
                    case FIREPROOF -> fireproof(noise, fiber, fine);
                    case VEINS -> veins(x, y, seed, noise);
                    case MOSS -> moss(x, y, seed, noise, cells[y][x]);
                    case OVERLAY -> overlay(x, y, seed, noise);
                    case HEART -> heart(x, y, seed, noise);
                    case EYE -> eye(x, y, seed, noise);
                    case NERVE -> nerve(x, y, seed, noise);
                    case STOMACH -> stomach(x, y, seed, noise);
                    case PUSTULE -> pustule(x, y, seed, noise);
                    case SPORE -> spore(x, y, seed, noise);
                    case BULB -> bulb(x, y, seed, noise);
                    case SPIKES -> spikes(x, y, seed, noise);
                    default -> living(noise, fiber, fine);
                };
                image.setRGB(x, y, color);
            }
        }
        return image;
    }

    private static int living(double noise, double fiber, double fine) {
        double n = noise * 42 + fiber * 15 + fine * 5;
        return argb(255, 114 + n, 24 + n * .34, 38 + n * .42);
    }

    private static int ossified(double noise, double fiber, double fine, boolean plate) {
        if (!plate) return living(noise - .16, fiber, fine);
        double ridge = Math.max(0, fiber) * 33 + noise * 26;
        return argb(255, 183 + ridge, 163 + ridge, 130 + ridge * .75);
    }

    private static int charred(double noise, double fiber, boolean[][] cells, int x, int y) {
        boolean edge = cells[y][x] != cells[y][(x + 1) & MASK] || cells[y][x] != cells[(y + 1) & MASK][x];
        if (edge && fiber > -.35) return argb(255, 177 + noise * 36, 40 + noise * 15, 15);
        double n = noise * 24 + fiber * 4;
        return argb(255, 31 + n, 24 + n * .8, 25 + n * .65);
    }

    private static int fireproof(double noise, double fiber, double fine) {
        double n = noise * 35 + fiber * 12 + fine * 6;
        return argb(255, 145 + n, 65 + n * .4, 25 + n * .2);
    }

    private static int veins(int x, int y, long seed, double noise) {
        double field = Math.abs(gradientNoise(x, y, 8, seed + 51) + .42 * gradientNoise(x, y, 4, seed + 73));
        if (field > .085) return 0;
        double core = 1.0 - field / .085;
        return argb(100 + core * 130, 101 + core * 48 + noise * 12, 17 + core * 15, 31 + core * 20);
    }

    private static int moss(int x, int y, long seed, double noise, boolean patch) {
        double fiber = Math.sin(x * 1.2 + y * .55 + noise * 4);
        boolean node = (hash((x / 4), (y / 4), seed + 101) & 7L) == 0 && (x & 3) == 2 && (y & 3) == 2;
        if (node) return 0xFF48D1CC;
        double n = noise * 24 + fiber * 7 + (patch ? 7 : -4);
        return argb(255, 65 + n, 17 + n * .4, 29 + n * .5);
    }

    private static int heart(int x, int y, long seed, double noise) {
        double dist = Math.hypot(x - 16, y - 16);
        double pulse = Math.sin(dist * 0.45 - noise * 3.0);
        if (dist < 11.0) return argb(255, 180 + pulse * 45, 20 + pulse * 10, 45 + pulse * 15);
        return argb(255, 90 + noise * 30, 15 + noise * 10, 25 + noise * 10);
    }

    private static int eye(int x, int y, long seed, double noise) {
        double dist = Math.hypot(x - 16, y - 16);
        if (dist < 4.0) return 0xFF100508;
        if (dist < 9.0) return 0xFF48D1CC;
        if (dist < 13.0) return 0xFFE0E5E5;
        return argb(255, 110 + noise * 30, 25, 35);
    }

    private static int nerve(int x, int y, long seed, double noise) {
        double beam = Math.abs(x - 16) + Math.sin(y * 0.5) * 2.0;
        if (beam < 4.0) return 0xFF5DF5E8;
        return argb(255, 45 + noise * 20, 35 + noise * 15, 55 + noise * 25);
    }

    private static int stomach(int x, int y, long seed, double noise) {
        double pool = Math.sin(x * 0.3) + Math.cos(y * 0.3) + noise;
        return argb(255, 40 + pool * 15, 110 + pool * 35, 35 + pool * 15);
    }

    private static int pustule(int x, int y, long seed, double noise) {
        double spot = Math.hypot((x % 10) - 5, (y % 10) - 5);
        if (spot < 3.0) return 0xFFE5C845;
        return argb(255, 115 + noise * 25, 30, 40);
    }

    private static int spore(int x, int y, long seed, double noise) {
        if (y > 22) return argb(255, 80 + noise * 20, 20, 30);
        return ((x + y) & 3) == 0 ? 0xFF55E2D0 : 0;
    }

    private static int bulb(int x, int y, long seed, double noise) {
        double dist = Math.hypot(x - 16, y - 12);
        if (dist < 8.0) return 0xFFD83050;
        return y < 8 ? 0xFF4A1020 : 0;
    }

    private static int spikes(int x, int y, long seed, double noise) {
        int tip = Math.abs(x - 16);
        if (y >= tip * 2 + 6) return argb(255, 200 - y * 3, 180 - y * 3, 150 - y * 3);
        return 0;
    }

    private static int overlay(int x, int y, long seed, double noise) {
        boolean eye = y >= 7 && y <= 10 && ((x >= 5 && x <= 10) || (x >= 21 && x <= 26));
        if (eye) {
            boolean pupil = (x == 7 || x == 8 || x == 23 || x == 24) && y >= 8 && y <= 9;
            return pupil ? argb(210, 45, 10, 25) : argb(165, 200, 90, 94);
        }
        double vein = Math.abs(gradientNoise(x, y, 8, seed + 7) + .45 * gradientNoise(x, y, 4, seed + 19));
        if (vein < .045) return argb(125, 87 + noise * 15, 28, 74);
        return argb(40, 202 + noise * 15, 178 + noise * 10, 165 + noise * 8);
    }

    private static boolean[][] cellular(long seed) {
        boolean[][] current = new boolean[SIZE][SIZE];
        for (int y = 0; y < SIZE; y++) for (int x = 0; x < SIZE; x++) {
            current[y][x] = (hash(x, y, seed) & 255L) < 126;
        }
        for (int pass = 0; pass < 3; pass++) {
            boolean[][] next = new boolean[SIZE][SIZE];
            for (int y = 0; y < SIZE; y++) for (int x = 0; x < SIZE; x++) {
                int neighbors = 0;
                for (int dy = -1; dy <= 1; dy++) for (int dx = -1; dx <= 1; dx++) {
                    if ((dx != 0 || dy != 0) && current[(y + dy) & MASK][(x + dx) & MASK]) neighbors++;
                }
                next[y][x] = neighbors >= 5 || (current[y][x] && neighbors == 4);
            }
            current = next;
        }
        return current;
    }

    private static double fbm(int x, int y, long seed) {
        return gradientNoise(x, y, 16, seed) * .55
                + gradientNoise(x, y, 8, seed + 1) * .30
                + gradientNoise(x, y, 4, seed + 2) * .15;
    }

    private static double gradientNoise(int x, int y, int cellSize, long seed) {
        int grid = SIZE / cellSize;
        int gx = x / cellSize, gy = y / cellSize;
        double fx = (x % cellSize) / (double) cellSize, fy = (y % cellSize) / (double) cellSize;
        double a = dot(gx, gy, fx, fy, seed, grid);
        double b = dot(gx + 1, gy, fx - 1, fy, seed, grid);
        double c = dot(gx, gy + 1, fx, fy - 1, seed, grid);
        double d = dot(gx + 1, gy + 1, fx - 1, fy - 1, seed, grid);
        double u = fade(fx), v = fade(fy);
        return lerp(lerp(a, b, u), lerp(c, d, u), v);
    }

    private static double dot(int gx, int gy, double x, double y, long seed, int grid) {
        long value = hash(Math.floorMod(gx, grid), Math.floorMod(gy, grid), seed);
        double angle = (value & 1023L) * (2.0 * Math.PI / 1024.0);
        return Math.cos(angle) * x + Math.sin(angle) * y;
    }

    private static long hash(int x, int y, long seed) {
        long n = seed ^ (x * 0x9E3779B97F4A7C15L) ^ (y * 0xC2B2AE3D27D4EB4FL);
        n = (n ^ (n >>> 30)) * 0xBF58476D1CE4E5B9L;
        n = (n ^ (n >>> 27)) * 0x94D049BB133111EBL;
        return n ^ (n >>> 31);
    }

    private static double fade(double value) { return value * value * value * (value * (value * 6 - 15) + 10); }
    private static double lerp(double a, double b, double amount) { return a + (b - a) * amount; }
    private static int channel(double value) { return (int) Math.max(0, Math.min(255, Math.round(value))); }
    private static int argb(double a, double r, double g, double b) {
        return channel(a) << 24 | channel(r) << 16 | channel(g) << 8 | channel(b);
    }

    private static BufferedImage canvas() {
        return new BufferedImage(SIZE, SIZE, BufferedImage.TYPE_INT_ARGB);
    }

    private static BufferedImage dart(boolean clean) {
        BufferedImage image = canvas();
        int outline = clean ? 0xFF25303A : 0xFF372314;
        int shadow = clean ? 0xFF536875 : 0xFF79501F;
        int metal = clean ? 0xFF91A9B1 : 0xFFC09239;
        int shine = clean ? 0xFFDCE9E8 : 0xFFF5D778;
        int glass = clean ? 0xFF30545C : 0xFF532E35;
        int fluid = clean ? 0xFF48D1CC : 0xFFB81135;
        int bright = clean ? 0xFFAAFFED : 0xFFFF5260;
        line(image, 5, 26, 22, 9, 4, outline);
        line(image, 5, 25, 21, 9, 3, shadow);
        line(image, 6, 24, 21, 9, 2, metal);
        line(image, 7, 23, 20, 10, 0, shine);
        line(image, 11, 19, 17, 13, 2, glass);
        line(image, 11, 19, 17, 13, 1, fluid);
        line(image, 12, 17, 16, 13, 0, bright);
        line(image, 21, 9, 24, 6, 1, outline);
        line(image, 24, 6, 29, 1, 0, 0xFFC8DADE);
        return image;
    }

    private static BufferedImage serum() {
        BufferedImage img = canvas();
        disc(img, 16, 18, 8, 0xFF30545C);
        disc(img, 16, 18, 6, 0xFF48D1CC);
        line(img, 14, 8, 18, 8, 2, 0xFF91A9B1);
        return img;
    }

    private static BufferedImage matrix() {
        BufferedImage image = canvas();
        disc(image, 16, 16, 13, 0xFF1B1018);
        disc(image, 16, 16, 10, 0xFF54202B);
        line(image, 8, 11, 14, 15, 0, 0xFF9F293D);
        line(image, 14, 15, 20, 21, 0, 0xFF8C2238);
        return image;
    }

    private static BufferedImage tendrils() {
        BufferedImage image = canvas();
        line(image, 16, 31, 16, 15, 3, 0xFF3C0A1A);
        line(image, 16, 20, 8, 10, 2, 0xFF862740);
        line(image, 16, 20, 24, 10, 2, 0xFF862740);
        return image;
    }

    private static BufferedImage purifier() {
        BufferedImage img = canvas();
        line(img, 6, 22, 24, 10, 4, 0xFF2A2D32);
        line(img, 12, 18, 26, 8, 2, 0xFFD49A38);
        line(img, 24, 10, 28, 7, 1, 0xFF48D1CC);
        return img;
    }

    private static BufferedImage inoculator() {
        BufferedImage img = canvas();
        line(img, 8, 24, 22, 10, 3, 0xFF536875);
        disc(img, 15, 17, 4, 0xFF48D1CC);
        line(img, 22, 10, 27, 5, 0, 0xFFE0E5E5);
        return img;
    }

    private static BufferedImage armorItem(int part) {
        BufferedImage img = canvas();
        int base = 0xFF1E242B;
        int glow = 0xFF48D1CC;
        switch (part) {
            case 0 -> { disc(img, 16, 16, 10, base); line(img, 10, 16, 22, 16, 2, glow); }
            case 1 -> { disc(img, 16, 16, 12, base); disc(img, 16, 14, 4, glow); }
            case 2 -> { line(img, 10, 8, 10, 26, 4, base); line(img, 22, 8, 22, 26, 4, base); }
            case 3 -> { disc(img, 10, 20, 5, base); disc(img, 22, 20, 5, base); }
        }
        return img;
    }

    private static BufferedImage spawnEgg() {
        BufferedImage img = canvas();
        disc(img, 16, 16, 11, 0xFF8A1C30);
        disc(img, 12, 12, 3, 0xFF48D1CC);
        disc(img, 20, 18, 2, 0xFF48D1CC);
        return img;
    }

    private static BufferedImage sludgeBucket() {
        BufferedImage img = canvas();
        disc(img, 16, 18, 9, 0xFF889098);
        disc(img, 16, 17, 6, 0xFF2A0A15);
        return img;
    }

    private static BufferedImage armorSheet() {
        BufferedImage img = new BufferedImage(64, 64, BufferedImage.TYPE_INT_ARGB);
        for (int y = 0; y < 64; y++) for (int x = 0; x < 64; x++) {
            img.setRGB(x, y, ((x + y) & 8) == 0 ? 0xFF1E242B : 0xFF2B333D);
        }
        for (int x = 4; x <= 12; x++) img.setRGB(x, 10, 0xFF48D1CC);
        return img;
    }

    private static void disc(BufferedImage image, int cx, int cy, int radius, int color) {
        for (int y = -radius; y <= radius; y++) {
            for (int x = -radius; x <= radius; x++) {
                if (x * x + y * y <= radius * radius) pixel(image, cx + x, cy + y, color);
            }
        }
    }

    private static void line(BufferedImage image, int x0, int y0, int x1, int y1, int width, int color) {
        int dx = Math.abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
        int dy = -Math.abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
        int error = dx + dy;
        while (true) {
            disc(image, x0, y0, width, color);
            if (x0 == x1 && y0 == y1) break;
            int twice = 2 * error;
            if (twice >= dy) { error += dy; x0 += sx; }
            if (twice <= dx) { error += dx; y0 += sy; }
        }
    }

    private static void pixel(BufferedImage image, int x, int y, int color) {
        if (x >= 0 && y >= 0 && x < image.getWidth() && y < image.getHeight()) image.setRGB(x, y, color);
    }

    private enum Kind {
        LIVING, OSSIFIED, CHARRED, FIREPROOF, VEINS, MOSS, HEART, EYE, NERVE, STOMACH, PUSTULE, SPORE, BULB, SPIKES,
        OVERLAY, VIRAL_DART, PURIFICATION_DART, SERUM, MATRIX, TENDRILS, GUN_ICON, GUN_GEO, INOCULATOR_ICON, INOCULATOR_GEO,
        HELMET, CHESTPLATE, LEGGINGS, BOOTS, EGG, BUCKET, ARMOR_SHEET
    }

    private record Texture(String folder, String name, Kind kind, int variant) { }
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
        tag(ModBlockTags.INFECTIOUS_SURFACES)
                .add(
                        ModBlocks.LIVING_FLESH.get(),
                        ModBlocks.OSSIFIED_FLESH.get(),
                        ModBlocks.FIREPROOF_FLESH.get(),
                        ModBlocks.FLESH_VEINS.get(),
                        ModBlocks.PULSING_HEART.get(),
                        ModBlocks.NERVE_PILLAR.get(),
                        ModBlocks.STOMACH_POOL.get(),
                        ModBlocks.HIVE_EYE.get()
                );

        tag(BlockTags.MINEABLE_WITH_HOE).add(ModBlocks.LIVING_FLESH.get(),
                ModBlocks.PUSTULE_CLUSTER.get(), ModBlocks.NEURAL_MOSS.get(), ModBlocks.STOMACH_POOL.get(),
                ModBlocks.FLESH_BULB.get(), ModBlocks.PULSING_HEART.get(), ModBlocks.HIVE_EYE.get());
        tag(BlockTags.MINEABLE_WITH_AXE).add(ModBlocks.FLESH_VEINS.get(), ModBlocks.NERVE_PILLAR.get());
        tag(BlockTags.MINEABLE_WITH_PICKAXE).add(ModBlocks.OSSIFIED_FLESH.get(),
                ModBlocks.FIREPROOF_FLESH.get(), ModBlocks.CHARRED_FLESH.get(), ModBlocks.SINEW_SPIKES.get());
        TagKey<Block> carnisBlocks = TagKey.create(Registries.BLOCK, new ResourceLocation(CarnisMod.MOD_ID, "carnis_blocks"));
        tag(carnisBlocks).add(ModBlocks.TAINTED_SLUDGE.get(), ModBlocks.FLESH_VEINS.get(),
                ModBlocks.FLESH_BULB.get(), ModBlocks.SINEW_SPIKES.get(), ModBlocks.NERVE_PILLAR.get(),
                ModBlocks.CREEPING_TENDRILS.get(), ModBlocks.PUSTULE_CLUSTER.get(), ModBlocks.STOMACH_POOL.get(),
                ModBlocks.SPORE_SPROUT.get(), ModBlocks.NEURAL_MOSS.get(), ModBlocks.CHARRED_FLESH.get(),
                ModBlocks.LIVING_FLESH.get(), ModBlocks.OSSIFIED_FLESH.get(), ModBlocks.FIREPROOF_FLESH.get(),
                ModBlocks.PULSING_HEART.get(), ModBlocks.HIVE_EYE.get());

        tag(BlockTags.NEEDS_STONE_TOOL)
                .add(ModBlocks.OSSIFIED_FLESH.get());

        tag(BlockTags.NEEDS_IRON_TOOL)
                .add(ModBlocks.FIREPROOF_FLESH.get());
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
import net.minecraftforge.client.model.generators.BlockStateProvider;
import net.minecraftforge.common.data.ExistingFileHelper;
import net.minecraftforge.registries.RegistryObject;

public final class ModBlockStateProvider extends BlockStateProvider {
    public ModBlockStateProvider(PackOutput output, ExistingFileHelper exFileHelper) {
        super(output, CarnisMod.MOD_ID, exFileHelper);
    }

    @Override
    protected void registerStatesAndModels() {
        simpleCube(ModBlocks.LIVING_FLESH, "living_flesh_0");
        simpleCube(ModBlocks.OSSIFIED_FLESH, "ossified_flesh_0");
        simpleCube(ModBlocks.CHARRED_FLESH, "charred_flesh_0");
        simpleCube(ModBlocks.FIREPROOF_FLESH, "fireproof_flesh");
        simpleCube(ModBlocks.NEURAL_MOSS, "neural_moss");
        simpleCube(ModBlocks.PUSTULE_CLUSTER, "pustule_cluster");

        crossBlock(ModBlocks.SPORE_SPROUT, "spore_sprout");
        crossBlock(ModBlocks.FLESH_BULB, "flesh_bulb");
        crossBlock(ModBlocks.SINEW_SPIKES, "sinew_spikes");

        geoBlock(ModBlocks.PULSING_HEART, "pulsing_heart");
        geoBlock(ModBlocks.HIVE_EYE, "hive_eye");
        geoBlock(ModBlocks.NERVE_PILLAR, "nerve_pillar");
        geoBlock(ModBlocks.STOMACH_POOL, "stomach_pool");
        geoBlock(ModBlocks.CREEPING_TENDRILS, "creeping_tendrils");
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
        // Standard cube block items
        blockItem(ModBlocks.LIVING_FLESH);
        blockItem(ModBlocks.OSSIFIED_FLESH);
        blockItem(ModBlocks.CHARRED_FLESH);
        blockItem(ModBlocks.FIREPROOF_FLESH);
        blockItem(ModBlocks.NEURAL_MOSS);
        blockItem(ModBlocks.PUSTULE_CLUSTER);

        // 2D flat item representation for Geo & organic hazard block items
        flatBlockItem(ModBlocks.PULSING_HEART);
        flatBlockItem(ModBlocks.HIVE_EYE);
        flatBlockItem(ModBlocks.NERVE_PILLAR);
        flatBlockItem(ModBlocks.STOMACH_POOL);
        flatBlockItem(ModBlocks.SPORE_SPROUT);
        flatBlockItem(ModBlocks.FLESH_BULB);
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
        flatItem(ModItems.BIO_PURIFIER);
        flatItem(ModItems.PNEUMATIC_INOCULATOR);
        flatItem(ModItems.NEURO_RESONATOR_HELMET);
        flatItem(ModItems.NEURO_RESONATOR_CHESTPLATE);
        flatItem(ModItems.NEURO_RESONATOR_LEGGINGS);
        flatItem(ModItems.NEURO_RESONATOR_BOOTS);
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
        add("tooltip.carnis.bio_purifier", "Hold use: 6-block flame, 35% bypasses armor.");
        add("tooltip.carnis.neuro_resonator_helmet", "Dampens hallucinations and halves surface infection.");
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
        add("entity.carnis.flesh_amalgam", "Flesh Amalgam");
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
        add("tooltip.carnis.bio_purifier", "Удерживайте: огонь на 6 блоков, 35% урона обходит броню.");
        add("tooltip.carnis.neuro_resonator_helmet", "Подавляет галлюцинации и вдвое снижает заражение от поверхности.");
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
        add("entity.carnis.flesh_amalgam", "Амальгама плоти");
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

## `src/main/resources/assets/carnis/models/item/neural_moss.json`

```json
{
  "parent": "carnis:block/neural_moss",
  "display": {
    "gui": {
      "rotation": [
        30,
        45,
        0
      ],
      "translation": [
        0,
        2,
        0
      ],
      "scale": [
        1.25,
        1.25,
        1.25
      ]
    },
    "ground": {
      "rotation": [
        0,
        0,
        0
      ],
      "translation": [
        0,
        2,
        0
      ],
      "scale": [
        0.5,
        0.5,
        0.5
      ]
    },
    "fixed": {
      "rotation": [
        30,
        45,
        0
      ],
      "translation": [
        0,
        2,
        0
      ],
      "scale": [
        1,
        1,
        1
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
        0.75,
        0.75,
        0.75
      ]
    },
    "firstperson_righthand": {
      "rotation": [
        0,
        45,
        0
      ],
      "translation": [
        0,
        2,
        0
      ],
      "scale": [
        0.8,
        0.8,
        0.8
      ]
    }
  }
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
  "tooltip.carnis.bio_purifier": "Hold use: 6-block flame, 35% bypasses armor.",
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
  "tooltip.carnis.neuro_resonator_helmet": "Dampens hallucinations and halves surface infection.",
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
  "tooltip.carnis.biomass_maggot.lore": "The first link in the Hive’s parasitic cycle."
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
  "tooltip.carnis.bio_purifier": "Удерживайте: огонь на 6 блоков, 35% урона обходит броню.",
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
  "tooltip.carnis.neuro_resonator_helmet": "Подавляет галлюцинации и вдвое снижает заражение от поверхности.",
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
  "tooltip.carnis.biomass_maggot.lore": "Начальное звено паразитического круговорота Улья."
}
```

## `src/generated/resources/data/minecraft/tags/blocks/mineable/axe.json`

```json
{
  "replace": false,
  "values": [
    "carnis:nerve_pillar",
    "carnis:flesh_veins"
  ]
}
```

## `src/generated/resources/data/carnis/tags/blocks/infectious_surfaces.json`

```json
{
  "replace": false,
  "values": [
    "carnis:living_flesh",
    "carnis:ossified_flesh",
    "carnis:fireproof_flesh",
    "carnis:pulsing_heart",
    "carnis:nerve_pillar",
    "carnis:stomach_pool",
    "carnis:hive_eye",
    "carnis:flesh_veins"
  ]
}
```

## `src/generated/resources/data/carnis/tags/blocks/carnis_blocks.json`

```json
{
  "replace": false,
  "values": [
    "carnis:tainted_sludge",
    "carnis:flesh_veins",
    "carnis:flesh_bulb",
    "carnis:sinew_spikes",
    "carnis:nerve_pillar",
    "carnis:creeping_tendrils",
    "carnis:pustule_cluster",
    "carnis:stomach_pool",
    "carnis:spore_sprout",
    "carnis:neural_moss",
    "carnis:charred_flesh",
    "carnis:living_flesh",
    "carnis:ossified_flesh",
    "carnis:fireproof_flesh",
    "carnis:pulsing_heart",
    "carnis:hive_eye"
  ]
}
```

## `src/main/resources/data/carnis/recipes/neuro_resonator_helmet.json`

```json
{
  "type": "minecraft:crafting_shapeless",
  "ingredients": [
    {
      "item": "minecraft:iron_helmet"
    },
    {
      "item": "carnis:hive_eye"
    },
    {
      "item": "carnis:neural_moss"
    },
    {
      "item": "carnis:creeping_tendrils"
    }
  ],
  "result": {
    "item": "carnis:neuro_resonator_helmet"
  }
}
```

## `src/main/resources/data/carnis/recipes/neuro_resonator_chestplate.json`

```json
{
  "type": "minecraft:crafting_shapeless",
  "ingredients": [
    {
      "item": "minecraft:iron_chestplate"
    },
    {
      "item": "carnis:sinew_spikes"
    },
    {
      "item": "carnis:ossified_flesh"
    },
    {
      "item": "carnis:fireproof_flesh"
    }
  ],
  "result": {
    "item": "carnis:neuro_resonator_chestplate"
  }
}
```

## `src/main/resources/data/carnis/recipes/neuro_resonator_leggings.json`

```json
{
  "type": "minecraft:crafting_shapeless",
  "ingredients": [
    {
      "item": "minecraft:iron_leggings"
    },
    {
      "item": "carnis:ossified_flesh"
    },
    {
      "item": "carnis:sinew_spikes"
    }
  ],
  "result": {
    "item": "carnis:neuro_resonator_leggings"
  }
}
```

## `src/main/resources/data/carnis/recipes/neuro_resonator_boots.json`

```json
{
  "type": "minecraft:crafting_shapeless",
  "ingredients": [
    {
      "item": "minecraft:leather_boots"
    },
    {
      "item": "carnis:fireproof_flesh"
    },
    {
      "item": "carnis:ossified_flesh"
    }
  ],
  "result": {
    "item": "carnis:neuro_resonator_boots"
  }
}
```

