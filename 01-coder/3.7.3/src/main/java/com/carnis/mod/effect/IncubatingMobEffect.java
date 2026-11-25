package com.carnis.mod.effect;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;

/** Client-synchronized visual marker. Lifecycle is owned by InfectionHandler. */
public final class IncubatingMobEffect extends MobEffect {
    public IncubatingMobEffect() { super(MobEffectCategory.HARMFUL, 0x881B2B); }
}
