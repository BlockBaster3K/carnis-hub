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
