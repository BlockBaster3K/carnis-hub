package com.carnis.mod.item;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.FleshIncineration;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.event.InfectionHandler;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.init.ModEffects;
import com.carnis.mod.init.ModParticles;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.HashSet;
import java.util.Set;

public final class BioPurifierItem extends Item implements GeoItem {
    public static final int MAX_DURABILITY = 500;
    private static final int DURATION = 72000;
    private static final int SHOCK_TICKS = 60;
    private static final double RANGE = 6.5D;
    // 25 degrees is the cone half-angle, measured from its axis.
    private static final double COS_ANGLE = Math.cos(Math.toRadians(25.0D));
    private static final double TAN_ANGLE = Math.tan(Math.toRadians(25.0D));
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.bio_purifier.idle");
    private static final RawAnimation FIRING = RawAnimation.begin().thenLoop("animation.bio_purifier.firing");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public BioPurifierItem(Properties properties) { super(properties.durability(MAX_DURABILITY)); }

    @Override public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientItemExtensions> consumer) {
        consumer.accept(new net.minecraftforge.client.extensions.common.IClientItemExtensions() {
            private com.carnis.mod.client.renderer.item.BioPurifierRenderer renderer;
            @Override public net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new com.carnis.mod.client.renderer.item.BioPurifierRenderer();
                return renderer;
            }
        });
    }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "operation", 0, state -> state.setAndContinue(
                com.carnis.mod.client.BioPurifierAnimationState.isFiring(state) ? FIRING : IDLE)));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
    @Override public int getUseDuration(ItemStack stack) { return DURATION; }
    @Override public UseAnim getUseAnimation(ItemStack stack) { return UseAnim.NONE; }

    @Override public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        player.startUsingItem(hand);
        if (level instanceof ServerLevel server) server.playSound(null, player.blockPosition(), ModSounds.PURIFIER_IGNITE.get(),
                SoundSource.PLAYERS, 1.0F, 1.0F);
        return InteractionResultHolder.consume(stack);
    }

    @Override public void onUseTick(Level level, LivingEntity user, ItemStack stack, int count) {
        if (!(level instanceof ServerLevel server)) return;
        if (stack.isEmpty()) { user.stopUsingItem(); return; }
        int elapsed = DURATION - count;
        if (elapsed % 10 == 0) server.playSound(null, user.blockPosition(), ModSounds.PURIFIER_LOOP.get(),
                SoundSource.PLAYERS, 1.0F, 1.0F);
        if (elapsed % 2 == 0 && (!(user instanceof Player player) || !player.getAbilities().instabuild)) {
            stack.hurtAndBreak(1, user, entity -> entity.broadcastBreakEvent(entity.getUsedItemHand()));
            if (stack.isEmpty()) { user.stopUsingItem(); return; }
        }

        Vec3 forward = user.getLookAngle().normalize();
        double yaw = Math.toRadians(user.getYRot());
        Vec3 right = new Vec3(-Math.cos(yaw), 0.0D, -Math.sin(yaw)).normalize();
        Vec3 up = forward.cross(right).normalize();
        double side = 1.0D;
        if (user instanceof Player player) {
            HumanoidArm arm = user.getUsedItemHand() == InteractionHand.MAIN_HAND
                    ? player.getMainArm() : player.getMainArm().getOpposite();
            side = arm == HumanoidArm.RIGHT ? 1.0D : -1.0D;
        }
        Vec3 eye = user.getEyePosition();
        Vec3 origin = eye.add(right.scale(0.28D * side)).add(0, -0.35D, 0).add(forward.scale(0.85D));
        if (server.clip(new ClipContext(eye, origin, ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE, user)).getType() == HitResult.Type.BLOCK) return;

        emitParticles(server, user, origin, forward, right, up);
        damageEntities(server, user, origin, forward, elapsed % 4 == 0);
        if (elapsed % 4 == 0) burnConeBlocks(server, user, origin, forward, right, up);
    }

    private static boolean insideCone(Vec3 origin, Vec3 forward, Vec3 point) {
        Vec3 delta = point.subtract(origin);
        double distanceSquared = delta.lengthSqr();
        if (distanceSquared < 1.0E-8D || distanceSquared > RANGE * RANGE) return false;
        return delta.dot(forward) / Math.sqrt(distanceSquared) >= COS_ANGLE;
    }

    private static boolean clearRay(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 target) {
        return level.clip(new ClipContext(origin, target, ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE, user)).getType() == HitResult.Type.MISS;
    }

    private static boolean exposedInCone(ServerLevel level, LivingEntity user, LivingEntity target, Vec3 origin, Vec3 forward) {
        AABB b = target.getBoundingBox();
        double x = (b.minX + b.maxX) * .5D, z = (b.minZ + b.maxZ) * .5D;
        double y = (b.minY + b.maxY) * .5D;
        Vec3[] samples = {new Vec3(x, y, z), new Vec3(x, b.minY + .05D, z),
                new Vec3(x, b.maxY - .05D, z), new Vec3(b.minX, y, z), new Vec3(b.maxX, y, z),
                new Vec3(x, y, b.minZ), new Vec3(x, y, b.maxZ)};
        for (Vec3 point : samples) if (insideCone(origin, forward, point) && clearRay(level, user, origin, point)) return true;
        return false;
    }

    private static void damageEntities(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 forward, boolean damageTick) {
        Vec3 end = origin.add(forward.scale(RANGE));
        AABB bounds = new AABB(origin, end).inflate(RANGE * TAN_ANGLE);
        for (LivingEntity target : level.getEntitiesOfClass(LivingEntity.class, bounds,
                e -> e != user && e.isAlive() && !e.isSpectator())) {
            if (user instanceof Player attacker && target instanceof Player victim && !attacker.canHarmPlayer(victim)) continue;
            if (!exposedInCone(level, user, target, origin, forward)) continue;
            if (!damageTick) {
                if (target instanceof Player player) PlayerInfectionApi.addInfection(player, -5.0F);
                continue;
            }
            boolean protectedByPillar = HiveNetwork.shielded(level, target.blockPosition());
            target.setSecondsOnFire(4);
            if (protectedByPillar) target.setRemainingFireTicks(Math.min(target.getRemainingFireTicks(), 20));
            if (!protectedByPillar && infected(target))
                target.addEffect(new MobEffectInstance(ModEffects.THERMAL_SHOCK.get(), SHOCK_TICKS, 0));
            // Permit the four-tick stream cadence without clearing unrelated immunity afterwards.
            int previous = target.invulnerableTime;
            target.invulnerableTime = 0;
            try { target.hurt(ModDamageTypes.bioPurifierSurface(level, user), 3.0F); }
            finally { target.invulnerableTime = Math.max(previous, target.invulnerableTime); }
            if (target instanceof Player player && player.isAlive()) PlayerInfectionApi.addInfection(player, -5.0F);
        }
    }

    private static boolean infected(LivingEntity target) {
        if (target instanceof HivemindLinkedMob || InfectionHandler.isInfected(target)
                || target.hasEffect(ModEffects.INCUBATING.get())) return true;
        if (target instanceof Player player && PlayerInfectionApi.getInfectionLevel(player) > 0) return true;
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(target.getType());
        return id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }

    private static Vec3 rayDirection(Vec3 forward, Vec3 right, Vec3 up, double fraction, double angle) {
        return forward.add(right.scale(TAN_ANGLE * fraction * Math.cos(angle)))
                .add(up.scale(TAN_ANGLE * fraction * Math.sin(angle))).normalize();
    }

    private static void burnConeBlocks(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 forward, Vec3 right, Vec3 up) {
        Set<BlockPos> hitBlocks = new HashSet<>();
        traceBlock(level, user, origin, forward, hitBlocks);
        for (int ring = 1; ring <= 2; ring++) for (int i = 0; i < 12; i++) {
            double angle = 2.0D * Math.PI * (i + (ring == 1 ? 0.5D : 0.0D)) / 12.0D;
            traceBlock(level, user, origin, rayDirection(forward, right, up, ring / 2.0D, angle), hitBlocks);
        }
        for (BlockPos pos : hitBlocks) burnBlock(level, pos);
    }

    private static void traceBlock(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 direction, Set<BlockPos> found) {
        BlockHitResult hit = level.clip(new ClipContext(origin, origin.add(direction.scale(RANGE)),
                ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, user));
        if (hit.getType() == HitResult.Type.BLOCK) found.add(hit.getBlockPos().immutable());
    }

    private static void burnBlock(ServerLevel level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        if (state.is(ModBlocks.LIVING_FLESH.get()) || state.is(ModBlocks.OSSIFIED_FLESH.get())) {
            FleshIncineration.tryBurn(level, pos, state);
        } else if (state.is(ModBlocks.FLESH_VEINS.get())) {
            BlockState replacement = state.getFluidState().isEmpty() ? Blocks.AIR.defaultBlockState()
                    : state.getFluidState().createLegacyBlock();
            level.setBlockAndUpdate(pos, replacement);
        }
        // FIREPROOF_FLESH is not changed; it also blocks rays like any solid block.
    }

    private static void emitParticles(ServerLevel level, LivingEntity user, Vec3 origin, Vec3 forward, Vec3 right, Vec3 up) {
        for (int i = 0; i < 5; i++) {
            double angle = level.random.nextDouble() * Math.PI * 2.0D;
            double radius = Math.sqrt(level.random.nextDouble());
            Vec3 ray = rayDirection(forward, right, up, radius, angle);
            double distance = 0.4D + level.random.nextDouble() * (RANGE - 0.4D);
            Vec3 intended = origin.add(ray.scale(distance));
            BlockHitResult hit = level.clip(new ClipContext(origin, intended, ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE, user));
            Vec3 point = hit.getType() == HitResult.Type.BLOCK ? hit.getLocation().subtract(ray.scale(.05D)) : intended;
            Vec3 velocity = ray.scale(.06D);
            level.sendParticles(ModParticles.PURIFIER_FLAME.get(), point.x, point.y, point.z, 0,
                    velocity.x, velocity.y, velocity.z, 1.0D);
            level.sendParticles(ParticleTypes.FLAME, point.x, point.y, point.z, 0,
                    velocity.x, velocity.y, velocity.z, 1.0D);
            if (i % 2 == 0) level.sendParticles(ParticleTypes.SMOKE, point.x, point.y, point.z, 0,
                    velocity.x * .5D, velocity.y * .5D + .01D, velocity.z * .5D, 1.0D);
        }
    }
}
