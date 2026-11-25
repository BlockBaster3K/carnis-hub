package com.carnis.mod.entity;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** Entry exposure is per cloud and player, not a repeated dose every tick. */
public final class HiveSporeCloudEntity extends AreaEffectCloud {
    private final Set<UUID> inside = new HashSet<>();
    public HiveSporeCloudEntity(EntityType<? extends AreaEffectCloud> type, Level level) { super(type, level); }
    @Override public void tick() {
        super.tick();
        if (!(level() instanceof ServerLevel server) || isRemoved() || tickCount % 5 != 0) return;
        Set<UUID> current = new HashSet<>();
        double radius = getRadius();
        for (ServerPlayer player : server.getEntitiesOfClass(ServerPlayer.class, getBoundingBox(),
                p -> p.isAlive() && !p.isSpectator() && !p.isCreative())) {
            double dx = player.getX() - getX(), dz = player.getZ() - getZ();
            if (dx * dx + dz * dz > radius * radius) continue;
            current.add(player.getUUID());
            if (!inside.contains(player.getUUID())) PlayerInfectionApi.addInfection(player, 20F);
        }
        inside.retainAll(current);
        inside.addAll(current);
    }
}
