package com.carnis.mod.fluid;

import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModFluids;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.item.NeuroWeave;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import java.util.Map;
import java.util.WeakHashMap;

public final class TaintedSludgeBlock extends LiquidBlock {
    private static final Map<LivingEntity, Long> LAST_EXPOSURE = new WeakHashMap<>();
    public TaintedSludgeBlock(BlockBehaviour.Properties properties) { super(ModFluids.SLUDGE_SOURCE, properties); }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        super.entityInside(state, level, pos, entity);
        if (!(level instanceof ServerLevel server) || !(entity instanceof LivingEntity living)
                || !living.isAlive() || living.isSpectator() || living.tickCount % 20 != 0) return;
        long time = server.getGameTime();
        Long last = LAST_EXPOSURE.put(living, time);
        if (last != null && last == time) return;
        if (living instanceof Player player) PlayerInfectionApi.addExposure(player, 5.0F);
        living.hurt(ModDamageTypes.taintedSludge(server), 1.0F);
        if (!NeuroWeave.hasSludgeImmuneBoots(living)) {
            living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 0));
        }
        living.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 60, 0));
    }
}
