package com.carnis.mod.item;

import com.carnis.mod.client.renderer.PneumaticInoculatorRenderer;
import com.carnis.mod.entity.PurificationDartEntity;
import com.carnis.mod.entity.ViralDartEntity;
import com.carnis.mod.init.ModItems;
import com.carnis.mod.init.ModSounds;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.SingletonGeoAnimatable;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.function.Consumer;

public final class PneumaticInoculatorItem extends Item implements GeoItem {
    private static final int COOLDOWN_TICKS = 15;
    private static final RawAnimation FIRE = RawAnimation.begin().thenPlay("animation.pneumatic_inoculator.fire");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public PneumaticInoculatorItem(Properties properties) {
        super(properties);
        SingletonGeoAnimatable.registerSyncedAnimatable(this);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() { return geoCache; }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<PneumaticInoculatorItem>(this, "action", 0,
                state -> PlayState.STOP).triggerableAnim("fire", FIRE));
    }

    @Override
    public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new IClientItemExtensions() {
            private PneumaticInoculatorRenderer renderer;
            @Override
            public BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new PneumaticInoculatorRenderer();
                return renderer;
            }
        });
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack weapon = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(this)) return InteractionResultHolder.fail(weapon);
        ItemStack ammo = findAmmo(player);
        if (ammo.isEmpty()) return InteractionResultHolder.fail(weapon);

        if (level instanceof ServerLevel server) {
            com.carnis.mod.entity.projectile.InoculatorDartEntity dart = new com.carnis.mod.entity.projectile.InoculatorDartEntity(
                    level, player, ammo.is(ModItems.VIRAL_DART.get())
                    ? com.carnis.mod.entity.projectile.InoculatorDartEntity.DartType.VIRAL
                    : com.carnis.mod.entity.projectile.InoculatorDartEntity.DartType.PURIFICATION);
            dart.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 2.8F, 1.0F);
            if (!server.addFreshEntity(dart)) return InteractionResultHolder.fail(weapon);
            if (!player.getAbilities().instabuild) ammo.shrink(1);
            player.getCooldowns().addCooldown(this, COOLDOWN_TICKS);
            triggerAnim(player, GeoItem.getOrAssignId(weapon, server), "action", "fire");

            Vec3 forward = player.getLookAngle().normalize();
            Vec3 horizontal = new Vec3(forward.x, 0.0D, forward.z);
            if (horizontal.lengthSqr() < 1.0E-8D) {
                float yaw = player.getYRot() * ((float) Math.PI / 180.0F);
                horizontal = new Vec3(-Math.sin(yaw), 0.0D, Math.cos(yaw));
            } else {
                horizontal = horizontal.normalize();
            }
            Vec3 right = new Vec3(-horizontal.z, 0.0D, horizontal.x);
            HumanoidArm heldArm = hand == InteractionHand.MAIN_HAND
                    ? player.getMainArm() : player.getMainArm().getOpposite();
            double side = heldArm == HumanoidArm.RIGHT ? 1.0D : -1.0D;
            Vec3 eye = player.getEyePosition();
            Vec3 muzzle = eye.add(right.scale(0.24D * side)).add(0.0D, -0.24D, 0.0D)
                    .add(forward.scale(0.65D));
            var obstruction = server.clip(new ClipContext(eye, muzzle, ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE, player));
            if (obstruction.getType() != HitResult.Type.MISS) {
                muzzle = obstruction.getLocation().add(eye.subtract(obstruction.getLocation()).normalize().scale(0.02D));
            }
            server.sendParticles(ParticleTypes.POOF, muzzle.x, muzzle.y, muzzle.z,
                    3, 0.025D, 0.025D, 0.025D, 0.01D);
            for (int i = 0; i < 5; i++) {
                double lateral = (i - 2) * 0.045D;
                Vec3 velocity = forward.scale(0.12D).add(right.scale(lateral * 0.12D));
                server.sendParticles(ParticleTypes.CLOUD, muzzle.x, muzzle.y, muzzle.z, 0,
                        velocity.x, velocity.y, velocity.z, 1.0D);
            }
            server.playSound(null, player.blockPosition(), ModSounds.INOCULATOR_FIRE.get(),
                    SoundSource.PLAYERS, 1.0F, 1.0F);
        }
        return InteractionResultHolder.sidedSuccess(weapon, level.isClientSide);
    }

    private static ItemStack findAmmo(Player player) {
        ItemStack selected = player.getMainHandItem();
        if (isAmmo(selected)) return selected;
        ItemStack offhand = player.getOffhandItem();
        if (isAmmo(offhand)) return offhand;
        for (int slot = 0; slot < player.getInventory().getContainerSize(); slot++) {
            ItemStack stack = player.getInventory().getItem(slot);
            if (isAmmo(stack)) return stack;
        }
        return ItemStack.EMPTY;
    }

    private static boolean isAmmo(ItemStack stack) {
        return stack.is(ModItems.VIRAL_DART.get()) || stack.is(ModItems.PURIFICATION_DART.get());
    }
}
