package com.carnis.mod.entity;

import com.carnis.mod.init.ModSounds;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/** Common base for living hive monsters; keeps shared sound and critical-wound behavior centralized. */
public abstract class HiveEntity extends Monster implements BiomassValued {
    private static final String CRITICAL_HURT_COOLDOWN = "carnis:hive_critical_hurt_ms";
    private static final long CRITICAL_HURT_COOLDOWN_MS = 120L;

    protected HiveEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    public static net.minecraft.world.entity.ai.attributes.AttributeSupplier.Builder createAttributes() {
        return HiveEntityAttributes.create();
    }

    // Явное значение биомассы. Множители НЕ применяются.
    @Override
    public long getBiomassValue() {
        return 0L;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HIVE_SPAWN_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.HIVE_SPAWN_DEATH.get();
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !level().isClientSide && isAlive() && getMaxHealth() > 0.0F
                && getHealth() / getMaxHealth() < 0.25F) {
            long now = System.currentTimeMillis();
            long last = getPersistentData().getLong(CRITICAL_HURT_COOLDOWN);
            if (now - last >= CRITICAL_HURT_COOLDOWN_MS) {
                getPersistentData().putLong(CRITICAL_HURT_COOLDOWN, now);
                level().playSound(null, blockPosition(), ModSounds.HIVE_SPAWN_HURT_CRITICAL.get(),
                        SoundSource.HOSTILE, 1.0F, 1.0F);
            }
        }
        return hurt;
    }
}
