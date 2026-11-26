package com.carnis.mod.item;

import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import javax.annotation.Nullable;
import java.util.List;

public final class ScytheItem extends SwordItem {
    private final float soundPitch;
    private final float soundVolume;
    private final SoundEvent hitSound;
    private final SoundEvent swingSound;
    @Nullable
    private final String tooltipKey;

    public ScytheItem(Tier tier, int attackDamage, float attackSpeed, float soundPitch,
                      float soundVolume, SoundEvent hitSound, SoundEvent swingSound,
                      @Nullable String tooltipKey, Properties properties) {
        super(tier, attackDamage, attackSpeed, properties);
        this.soundPitch = soundPitch;
        this.soundVolume = soundVolume;
        this.hitSound = hitSound;
        this.swingSound = swingSound;
        this.tooltipKey = tooltipKey;
    }

    public SoundEvent getHitSound() {
        return hitSound;
    }

    public SoundEvent getSwingSound() {
        return swingSound;
    }

    public float getSoundPitch() {
        return soundPitch;
    }

    public float getSoundVolume() {
        return soundVolume;
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        boolean hit = super.hurtEnemy(stack, target, attacker);
        if (!attacker.level().isClientSide) {
            attacker.level().playSound(null, target.blockPosition(), hitSound,
                    SoundSource.PLAYERS, soundVolume, soundPitch);
        }
        return hit;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        super.appendHoverText(stack, level, tooltip, flag);
        if (tooltipKey != null) tooltip.add(Component.translatable(tooltipKey));
    }
}
