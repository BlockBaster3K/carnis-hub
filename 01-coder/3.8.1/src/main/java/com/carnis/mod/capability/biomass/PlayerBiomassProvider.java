package com.carnis.mod.capability.biomass;

import javax.annotation.Nullable;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ICapabilitySerializable;
import net.minecraftforge.common.util.LazyOptional;

/** Владеет одним экземпляром данных на время жизни прикрепления. */
public final class PlayerBiomassProvider implements ICapabilitySerializable<CompoundTag> {
    private final PlayerBiomassData instance = new PlayerBiomassData();
    private LazyOptional<PlayerBiomassData> holder = LazyOptional.of(() -> instance);

    @Override
    public <T> LazyOptional<T> getCapability(Capability<T> capability, @Nullable Direction side) {
        if (capability == PlayerBiomassCapability.PLAYER_BIOMASS) {
            // После reviveCaps прежний LazyOptional может быть инвалидирован.
            if (!holder.isPresent()) holder = LazyOptional.of(() -> instance);
            return holder.cast();
        }
        return LazyOptional.empty();
    }

    @Override
    public CompoundTag serializeNBT() {
        return instance.serializeNBT();
    }

    @Override
    public void deserializeNBT(CompoundTag nbt) {
        instance.deserializeNBT(nbt);
    }

    public void invalidateCaps() {
        holder.invalidate();
    }
}
