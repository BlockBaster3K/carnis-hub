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
