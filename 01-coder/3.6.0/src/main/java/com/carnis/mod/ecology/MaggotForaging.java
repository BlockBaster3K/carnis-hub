package com.carnis.mod.ecology;

import com.carnis.mod.entity.BiomassMaggotEntity;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.AABB;

import java.util.Set;

/** Invoked only from a flesh block's random tick; no world or block scan. */
public final class MaggotForaging {
    private static final Set<Item> MEAT = Set.of(Items.BEEF, Items.COOKED_BEEF, Items.PORKCHOP,
            Items.COOKED_PORKCHOP, Items.CHICKEN, Items.COOKED_CHICKEN, Items.MUTTON,
            Items.COOKED_MUTTON, Items.RABBIT, Items.COOKED_RABBIT, Items.ROTTEN_FLESH);
    private MaggotForaging() { }

    public static void onFleshRandomTick(ServerLevel level, BlockPos pos) {
        AABB local = new AABB(pos).inflate(4.0D, 2.0D, 4.0D);
        for (BiomassMaggotEntity maggot : level.getEntitiesOfClass(BiomassMaggotEntity.class, local, e -> e.isAlive())) {
            AABB reach = maggot.getBoundingBox().inflate(1.0D, 0.5D, 1.0D);
            for (ItemEntity item : level.getEntitiesOfClass(ItemEntity.class, reach,
                    e -> e.isAlive() && e.onGround() && MEAT.contains(e.getItem().getItem()))) {
                ItemStack stack = item.getItem();
                if (stack.isEmpty()) continue;
                stack.shrink(1);
                if (stack.isEmpty()) item.discard(); else item.setItem(stack);
                CarnisWorldData.get(level).addBiomassPoints(5L);
                ModMessages.sendToPlayersInLevel(level);
                return; // At most one item per invocation.
            }
        }
    }
}
