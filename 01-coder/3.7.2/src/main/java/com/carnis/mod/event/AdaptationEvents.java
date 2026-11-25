package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.world.CarnisWorldData;
import com.carnis.mod.world.CarnisWorldData.AdaptationType;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.AbstractArrow;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.event.entity.ProjectileImpactEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class AdaptationEvents {
    private static final String RANGED_COUNTED_TAG =
            CarnisMod.MOD_ID + ":ranged_adaptation_counted";

    private static final int NEARBY_CARNIS_BLOCK_RADIUS = 1;

    private static final double RETALIATION_BASE_CHANCE = 0.05D;
    private static final double RETALIATION_CHANCE_PER_LEVEL = 0.005D;
    private static final double RETALIATION_MAX_CHANCE = 0.45D;
    private static final float RETALIATION_BASE_DAMAGE = 1.0F;
    private static final float RETALIATION_DAMAGE_PER_LEVEL = 0.04F;
    private static final float RETALIATION_MAX_DAMAGE = 4.0F;

    private static final double EXPLOSION_ABSORPTION_BASE_CHANCE = 0.10D;
    private static final double EXPLOSION_ABSORPTION_CHANCE_PER_LEVEL = 0.0075D;
    private static final double EXPLOSION_ABSORPTION_MAX_CHANCE = 0.60D;

    private static final ThreadLocal<Boolean> APPLYING_RETALIATION =
            ThreadLocal.withInitial(() -> false);

    private AdaptationEvents() {
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onLivingHurt(LivingHurtEvent event) {
        if (
                event.isCanceled()
                        || event.getAmount() <= 0.0F
                        || APPLYING_RETALIATION.get()
        ) {
            return;
        }

        LivingEntity target = event.getEntity();

        if (
                !(target.level() instanceof ServerLevel serverLevel)
                        || !isCarnisEntity(target)
        ) {
            return;
        }

        DamageSource source = event.getSource();

        if (source.is(DamageTypes.THORNS)) {
            return;
        }

        CarnisWorldData data = CarnisWorldData.get(serverLevel);
        AdaptationType damageType = source.is(DamageTypeTags.IS_FIRE)
                ? AdaptationType.FIRE
                : source.is(DamageTypeTags.IS_PROJECTILE)
                ? AdaptationType.RANGED
                : source.is(DamageTypeTags.IS_EXPLOSION)
                ? AdaptationType.EXPLOSIVE
                : source.getEntity() instanceof LivingEntity
                && source.getDirectEntity() == source.getEntity()
                ? AdaptationType.MELEE : null;
        if (damageType == null) {
            return;
        }
        float mitigation = CarnisWorldData.damageMitigation(data.getAdaptation(damageType));
        event.setAmount(event.getAmount() * (1.0F - mitigation));

        if (damageType == AdaptationType.MELEE) {
            data.decayAdaptation(AdaptationType.FIRE, 2L);
            data.decayAdaptation(AdaptationType.RANGED, 2L);
        }
        boolean count = damageType != AdaptationType.RANGED
                || (source.getDirectEntity() instanceof AbstractArrow
                    && markProjectileAttackAsCounted(source.getDirectEntity()));
        if (count) {
            data.tryAwardDamageAdaptation(new ChunkPos(target.blockPosition()),
                    damageType, serverLevel.getGameTime());
        }
        if (count || damageType == AdaptationType.MELEE) {
            ModMessages.sendToPlayersInLevel(serverLevel);
        }
        ServerPlayer meleeAttacker = getMeleeAttacker(source);
        if (meleeAttacker == null) {
            return;
        }
        long meleeLevel = data.getAdaptation(AdaptationType.MELEE);

        // Flesh Amalgams own their stronger adaptive thorn response. Keeping
        // the generic retaliation here as well would roll and apply it twice.
        if (!(target instanceof FleshAmalgamEntity)) {
            tryRetaliate(serverLevel, target, meleeAttacker, meleeLevel);
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onProjectileImpact(ProjectileImpactEvent event) {
        Projectile projectile = event.getProjectile();

        if (
                event.isCanceled()
                        || !(projectile.level() instanceof ServerLevel serverLevel)
                        || !(projectile instanceof AbstractArrow)
                        || isIgnoredEntityImpact(event)
                        || !hitsCarnisTarget(
                                serverLevel,
                                event.getRayTraceResult()
                        )
                        || !markProjectileAttackAsCounted(projectile)
        ) {
            return;
        }

        CarnisWorldData data = CarnisWorldData.get(serverLevel);
        BlockPos hitPos = BlockPos.containing(event.getRayTraceResult().getLocation());
        if (data.tryAwardDamageAdaptation(new ChunkPos(hitPos), AdaptationType.RANGED,
                serverLevel.getGameTime())) {
            ModMessages.sendToPlayersInLevel(serverLevel);
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onExplosionDetonate(ExplosionEvent.Detonate event) {
        if (!(event.getLevel() instanceof ServerLevel serverLevel)) {
            return;
        }

        List<BlockPos> affectedBlocks = event.getAffectedBlocks();
        List<Entity> affectedEntities = event.getAffectedEntities();

        boolean threatensCarnis = affectedBlocks.stream().anyMatch(
                pos -> isCarnisBlock(serverLevel.getBlockState(pos))
        ) || affectedEntities.stream().anyMatch(
                AdaptationEvents::isCarnisEntity
        );

        if (!threatensCarnis) {
            return;
        }

        long explosiveLevel = CarnisWorldData.get(serverLevel)
                .getAdaptation(AdaptationType.EXPLOSIVE);
        double absorptionChance = calculateExplosionAbsorptionChance(
                explosiveLevel
        );

        affectedBlocks.removeIf(
                pos -> isCarnisBlock(serverLevel.getBlockState(pos))
                        && serverLevel.getRandom().nextDouble()
                        < absorptionChance
        );
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onBlockPlaced(BlockEvent.EntityPlaceEvent event) {
        if (
                event.isCanceled()
                        || !(event.getLevel() instanceof ServerLevel serverLevel)
                        || !(event.getEntity() instanceof ServerPlayer player)
        ) {
            return;
        }

        BlockPos placedPos = event.getPos();

        if (
                event.getPlacedBlock()
                        .getCollisionShape(serverLevel, placedPos)
                        .isEmpty()
                        || !isPillaring(player, placedPos)
                        || !hasActiveCarnisPresence(serverLevel, placedPos)
        ) {
            return;
        }

        incrementAndSync(serverLevel, AdaptationType.PILLARING);
    }

    private static ServerPlayer getMeleeAttacker(DamageSource source) {
        if (
                source.is(DamageTypeTags.IS_FIRE)
                        || source.is(DamageTypeTags.IS_PROJECTILE)
                        || source.is(DamageTypeTags.IS_EXPLOSION)
                        || !(source.getEntity() instanceof ServerPlayer attacker)
                        || source.getDirectEntity() != attacker
        ) {
            return null;
        }

        return attacker;
    }

    private static void tryRetaliate(
            ServerLevel serverLevel,
            LivingEntity target,
            ServerPlayer attacker,
            long meleeLevel
    ) {
        double chance = Math.min(
                RETALIATION_MAX_CHANCE,
                RETALIATION_BASE_CHANCE
                        + meleeLevel * RETALIATION_CHANCE_PER_LEVEL
        );

        if (serverLevel.getRandom().nextDouble() >= chance) {
            return;
        }

        float damage = Math.min(
                RETALIATION_MAX_DAMAGE,
                RETALIATION_BASE_DAMAGE
                        + meleeLevel * RETALIATION_DAMAGE_PER_LEVEL
        );

        APPLYING_RETALIATION.set(true);

        try {
            attacker.hurt(
                    serverLevel.damageSources().thorns(target),
                    damage
            );
        } finally {
            APPLYING_RETALIATION.remove();
        }
    }

    private static boolean isIgnoredEntityImpact(
            ProjectileImpactEvent event
    ) {
        return event.getImpactResult()
                == ProjectileImpactEvent.ImpactResult.SKIP_ENTITY
                || event.getImpactResult()
                == ProjectileImpactEvent.ImpactResult.STOP_AT_CURRENT_NO_DAMAGE;
    }

    private static boolean hitsCarnisTarget(
            ServerLevel serverLevel,
            HitResult hitResult
    ) {
        if (hitResult instanceof EntityHitResult entityHitResult) {
            return entityHitResult.getEntity() instanceof LivingEntity living
                    && living.isAlive() && isCarnisEntity(living);
        }

        if (hitResult instanceof BlockHitResult blockHitResult) {
            BlockState state = serverLevel.getBlockState(blockHitResult.getBlockPos());
            return state.is(ModBlocks.PULSING_HEART.get()) || state.is(ModBlocks.HIVE_EYE.get())
                    || state.is(ModBlocks.NERVE_PILLAR.get()) || state.is(ModBlocks.STOMACH_POOL.get());
        }

        return false;
    }

    private static boolean markProjectileAttackAsCounted(Entity directEntity) {
        if (!(directEntity instanceof Projectile projectile)) {
            return true;
        }

        if (projectile.getPersistentData().getBoolean(RANGED_COUNTED_TAG)) {
            return false;
        }

        projectile.getPersistentData().putBoolean(RANGED_COUNTED_TAG, true);
        return true;
    }

    private static boolean isPillaring(
            ServerPlayer player,
            BlockPos placedPos
    ) {
        BlockPos blockBelowPlayer = player.blockPosition().below();
        return placedPos.equals(blockBelowPlayer)
                && player.getY() >= placedPos.getY() + 1.0D;
    }

    private static boolean hasActiveCarnisPresence(
            ServerLevel serverLevel,
            BlockPos center
    ) {
        if (CarnisWorldData.get(serverLevel).getBiomassPoints() > 0L) {
            return true;
        }

        BlockPos.MutableBlockPos cursor = new BlockPos.MutableBlockPos();

        for (
                int offsetX = -NEARBY_CARNIS_BLOCK_RADIUS;
                offsetX <= NEARBY_CARNIS_BLOCK_RADIUS;
                offsetX++
        ) {
            for (
                    int offsetY = -NEARBY_CARNIS_BLOCK_RADIUS;
                    offsetY <= NEARBY_CARNIS_BLOCK_RADIUS;
                    offsetY++
            ) {
                int y = center.getY() + offsetY;

                if (
                        y < serverLevel.getMinBuildHeight()
                                || y >= serverLevel.getMaxBuildHeight()
                ) {
                    continue;
                }

                for (
                        int offsetZ = -NEARBY_CARNIS_BLOCK_RADIUS;
                        offsetZ <= NEARBY_CARNIS_BLOCK_RADIUS;
                        offsetZ++
                ) {
                    cursor.set(
                            center.getX() + offsetX,
                            y,
                            center.getZ() + offsetZ
                    );

                    if (
                            serverLevel.hasChunkAt(cursor)
                                    && isCarnisBlock(
                                            serverLevel.getBlockState(cursor)
                                    )
                    ) {
                        return true;
                    }
                }
            }
        }

        return false;
    }

    private static boolean isCarnisEntity(Entity entity) {
        ResourceLocation registryName = ForgeRegistries.ENTITY_TYPES.getKey(
                entity.getType()
        );
        return registryName != null
                && CarnisMod.MOD_ID.equals(registryName.getNamespace());
    }

    private static boolean isCarnisBlock(BlockState state) {
        ResourceLocation registryName = ForgeRegistries.BLOCKS.getKey(
                state.getBlock()
        );
        return registryName != null
                && CarnisMod.MOD_ID.equals(registryName.getNamespace());
    }

    private static double calculateExplosionAbsorptionChance(long level) {
        return Math.min(
                EXPLOSION_ABSORPTION_MAX_CHANCE,
                EXPLOSION_ABSORPTION_BASE_CHANCE
                        + level * EXPLOSION_ABSORPTION_CHANCE_PER_LEVEL
        );
    }

    private static long incrementAndSync(
            ServerLevel serverLevel,
            AdaptationType type
    ) {
        CarnisWorldData worldData = CarnisWorldData.get(serverLevel);
        long previousValue = worldData.getAdaptation(type);
        long updatedValue = worldData.incrementAdaptation(type);

        if (updatedValue != previousValue) {
            ModMessages.sendToPlayersInLevel(serverLevel);
        }

        return updatedValue;
    }
}
