package com.carnis.mod.block.entity;

import com.carnis.mod.block.PustuleClusterBlock;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import software.bernie.geckolib.animatable.GeoBlockEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

public final class PustuleClusterBlockEntity extends BlockEntity implements GeoBlockEntity {
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.pustule_cluster.idle");
    private static final RawAnimation PULSE = RawAnimation.begin().thenLoop("animation.pustule_cluster.pulse");
    private static final RawAnimation EMPTY = RawAnimation.begin().thenPlayAndHold("animation.pustule_cluster.burst");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private int ambientTicks;
    private int ambientAge = -1;

    public PustuleClusterBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.PUSTULE_CLUSTER.get(), pos, state); }

    public static void serverTick(Level level, BlockPos pos, BlockState state, PustuleClusterBlockEntity entity) {
        if (!state.hasProperty(PustuleClusterBlock.AGE) || !state.hasProperty(PustuleClusterBlock.BURST)) return;
        int age = state.getValue(PustuleClusterBlock.AGE);
        if (state.getValue(PustuleClusterBlock.BURST) || age < 2) {
            entity.ambientTicks = 0;
            entity.ambientAge = -1;
            return;
        }
        if (entity.ambientAge != age) {
            entity.ambientAge = age;
            entity.ambientTicks = 0;
        }
        int interval = age == 2 ? 60 : 40;
        if (++entity.ambientTicks >= interval) {
            entity.ambientTicks = 0;
            float volume = age == 2 ? 0.4F : 0.5F;
            level.playSound(null, pos, SoundEvents.SLIME_BLOCK_STEP, SoundSource.BLOCKS, volume, 1.0F);
        }
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "pustules", 0, animation -> {
            BlockState state = getBlockState();
            if (!state.hasProperty(PustuleClusterBlock.BURST)) return animation.setAndContinue(IDLE);
            if (state.getValue(PustuleClusterBlock.BURST)) return animation.setAndContinue(EMPTY);
            return animation.setAndContinue(state.getValue(PustuleClusterBlock.AGE) == 3 ? PULSE : IDLE);
        }));
    }
}
