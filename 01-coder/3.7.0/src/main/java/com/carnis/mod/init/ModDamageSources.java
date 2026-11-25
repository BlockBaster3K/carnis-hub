package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.level.Level;

public final class ModDamageSources {
    public static final ResourceKey<DamageType> ORGANIC_CONSUMPTION = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "organic_consumption"));
    private ModDamageSources() { }
    public static DamageSource organicConsumption(Level level) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(ORGANIC_CONSUMPTION));
    }
}
