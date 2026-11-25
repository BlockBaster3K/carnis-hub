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
