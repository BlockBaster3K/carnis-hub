package com.carnis.mod.capability.infection;

import com.carnis.mod.network.ModMessages;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ICapabilitySerializable;
import net.minecraftforge.common.util.LazyOptional;

import java.util.Objects;

public final class PlayerInfectionProvider
        implements ICapabilitySerializable<CompoundTag> {
    private static final String INFECTION_LEVEL_TAG = "infection_level";

    private final PlayerInfection infection;
    private final LazyOptional<IPlayerInfection> holder;

    public PlayerInfectionProvider(Player owner) {
        Objects.requireNonNull(owner, "owner");

        infection = new PlayerInfection(() -> onLegacyChange(owner));
        holder = LazyOptional.of(() -> infection);
    }

    private void onLegacyChange(Player owner) {
        if (!owner.level().isClientSide)
            com.carnis.mod.infection.PlayerInfectionManager.setPoints(owner, infection.getInfectionLevel());
    }

    @Override
    public <T> LazyOptional<T> getCapability(
            Capability<T> capability,
            Direction side
    ) {
        if (capability == PlayerInfectionCapability.PLAYER_INFECTION) {
            return holder.cast();
        }

        return LazyOptional.empty();
    }

    @Override
    public CompoundTag serializeNBT() {
        return serializeInfection(infection);
    }

    @Override
    public void deserializeNBT(CompoundTag tag) {
        deserializeInfection(infection, tag);
    }

    public static CompoundTag serializeInfection(IPlayerInfection infection) {
        CompoundTag tag = new CompoundTag();
        tag.putFloat(INFECTION_LEVEL_TAG, infection.getInfectionLevel());
        return tag;
    }

    public static void deserializeInfection(IPlayerInfection infection, CompoundTag tag) {
        float level = tag.getFloat(INFECTION_LEVEL_TAG);
        if (infection instanceof PlayerInfection data) {
            data.setInfectionLevelSilently(level);
        } else {
            infection.setInfectionLevel(level);
        }
    }

    public void invalidate() {
        holder.invalidate();
    }
}
