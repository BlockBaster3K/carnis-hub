package com.carnis.mod.block.entity;

import com.carnis.mod.block.SporeSproutBlock;
import com.carnis.mod.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public final class SporeSproutBlockEntity extends BlockEntity {
    private static final int MAX_COOLDOWN_TICKS = 350;
    private static final String COOLDOWN_TAG = "CooldownTicks";

    private int cooldownTicks;

    public SporeSproutBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.SPORE_SPROUT.get(), pos, state);
    }

    public int getCooldownTicks() {
        return cooldownTicks;
    }

    public void startCooldown(int ticks) {
        cooldownTicks = Math.max(0, Math.min(MAX_COOLDOWN_TICKS, ticks));
        setChanged();
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putInt(COOLDOWN_TAG, cooldownTicks);
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        cooldownTicks = Math.max(0, Math.min(MAX_COOLDOWN_TICKS, tag.getInt(COOLDOWN_TAG)));
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, SporeSproutBlockEntity sprout) {
        if (!(level instanceof ServerLevel)) return;

        if (sprout.cooldownTicks > 0) {
            sprout.cooldownTicks--;
            sprout.setChanged();
        }

        if (state.hasProperty(SporeSproutBlock.CLOSED)) {
            boolean shouldBeClosed = sprout.cooldownTicks > 0;
            if (state.getValue(SporeSproutBlock.CLOSED) != shouldBeClosed) {
                level.setBlock(pos, state.setValue(SporeSproutBlock.CLOSED, shouldBeClosed), 3);
            }
        }
    }
}
