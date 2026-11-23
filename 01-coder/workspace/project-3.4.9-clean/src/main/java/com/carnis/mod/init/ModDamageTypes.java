package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;

import java.util.Objects;

public final class ModDamageTypes {
    public static final ResourceKey<DamageType> BIO_PURIFIER =
            ResourceKey.create(
                    Registries.DAMAGE_TYPE,
                    new ResourceLocation(CarnisMod.MOD_ID, "bio_purifier")
            );

    public static final ResourceKey<DamageType> BIO_PURIFIER_SURFACE = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "bio_purifier_surface"));

    public static DamageSource bioPurifierSurface(Level level, Entity wielder) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(BIO_PURIFIER_SURFACE), wielder, wielder);
    }

    public static final ResourceKey<DamageType> NECROTIC_CONSUMPTION = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "necrotic_consumption"));

    public static DamageSource necroticConsumption(Level level) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(NECROTIC_CONSUMPTION));
    }

    public static final ResourceKey<DamageType> TAINTED_SLUDGE = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "tainted_sludge"));

    public static DamageSource taintedSludge(Level level) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(TAINTED_SLUDGE));
    }

    public static final ResourceKey<DamageType> PURIFICATION_DART = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "purification_dart"));

    public static DamageSource purificationDart(Level level, Entity projectile, Entity shooter) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(PURIFICATION_DART), projectile, shooter);
    }

    private ModDamageTypes() {
    }

    public static DamageSource bioPurifier(Level level, Entity wielder) {
        Objects.requireNonNull(level, "level");
        Objects.requireNonNull(wielder, "wielder");

        Registry<DamageType> damageTypes = level.registryAccess()
                .registryOrThrow(Registries.DAMAGE_TYPE);

        return new DamageSource(
                damageTypes.getHolderOrThrow(BIO_PURIFIER),
                wielder,
                wielder
        );
    }
}
