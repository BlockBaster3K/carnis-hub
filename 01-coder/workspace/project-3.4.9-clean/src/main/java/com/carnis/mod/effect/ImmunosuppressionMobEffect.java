package com.carnis.mod.effect;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;

/** Positive infection changes are blocked by PlayerInfectionApi while this effect is active. */
public final class ImmunosuppressionMobEffect extends MobEffect {
    public ImmunosuppressionMobEffect() { super(MobEffectCategory.BENEFICIAL, 0x4A85A0); }
}
