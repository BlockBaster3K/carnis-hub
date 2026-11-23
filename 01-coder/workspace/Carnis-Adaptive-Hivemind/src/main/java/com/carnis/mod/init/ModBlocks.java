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
