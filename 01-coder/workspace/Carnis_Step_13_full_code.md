# Шаг 13 — полный код и сопутствующие файлы

Файлы представлены целиком. PNG находятся в каталоге проекта.

## `src/main/java/com/carnis/mod/item/armor/NeuroArmorItem.java`

```java
package com.carnis.mod.item.armor;

import com.carnis.mod.client.renderer.NeuroArmorRenderer;
import com.carnis.mod.init.ModArmorMaterials;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.function.Consumer;

public class NeuroArmorItem extends ArmorItem implements GeoItem {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    public NeuroArmorItem(Type type, Properties properties) {
        super(ModArmorMaterials.NEURO_RESONATOR, type, properties);
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) { }
    @Override public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new IClientItemExtensions() {
            private NeuroArmorRenderer renderer;
            @Override public HumanoidModel<?> getHumanoidArmorModel(LivingEntity entity, ItemStack stack,
                    EquipmentSlot slot, HumanoidModel<?> original) {
                if (renderer == null) renderer = new NeuroArmorRenderer();
                renderer.prepForRender(entity, stack, slot, original);
                return renderer;
            }
        });
    }
}
```

## `src/main/java/com/carnis/mod/event/NeuroArmorEventHandler.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.item.armor.NeuroArmorItem;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NeuroArmorEventHandler {
    private static final EquipmentSlot[] SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
    private static final String PROVOKED_UNTIL = "carnis:neuro_provoked_until";
    private static final String PROVOKED_DIMENSION = "carnis:neuro_provoked_dimension";
    private static final int PROVOCATION_TICKS = 600;
    private NeuroArmorEventHandler() { }

    private static boolean piece(LivingEntity entity, EquipmentSlot slot, ArmorItem.Type expected) {
        ItemStack stack = entity.getItemBySlot(slot);
        return stack.getItem() instanceof NeuroArmorItem armor && armor.getType() == expected;
    }
    public static boolean hasHelmet(LivingEntity entity) { return piece(entity, EquipmentSlot.HEAD, ArmorItem.Type.HELMET); }
    public static boolean hasSymbioticPair(LivingEntity entity) {
        return piece(entity, EquipmentSlot.CHEST, ArmorItem.Type.CHESTPLATE)
                && piece(entity, EquipmentSlot.LEGS, ArmorItem.Type.LEGGINGS);
    }
    public static int pieces(LivingEntity entity) {
        int count = 0;
        for (EquipmentSlot slot : SLOTS) {
            ItemStack stack = entity.getItemBySlot(slot);
            if (stack.getItem() instanceof NeuroArmorItem armor && armor.getEquipmentSlot() == slot) count++;
        }
        return count;
    }
    public static boolean hasFullSet(LivingEntity entity) { return pieces(entity) == 4; }
    public static boolean isHiveEntity(Entity entity) {
        if (!(entity instanceof LivingEntity)) return false;
        if (entity instanceof HivemindLinkedMob) return true;
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
        return id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }
    private static void provoke(Player player) {
        player.getPersistentData().putLong(PROVOKED_UNTIL, player.level().getGameTime() + PROVOCATION_TICKS);
        player.getPersistentData().putString(PROVOKED_DIMENSION, player.level().dimension().location().toString());
    }
    public static boolean isProvoked(Player player) {
        return player.level().dimension().location().toString().equals(player.getPersistentData().getString(PROVOKED_DIMENSION))
                && player.level().getGameTime() < player.getPersistentData().getLong(PROVOKED_UNTIL);
    }
    /** Eye-like sensors can detect an unprovoked disguised player at four blocks or closer. */
    public static boolean hiddenFromSensor(Player player, double distanceSquared) {
        return hasFullSet(player) && !isProvoked(player) && distanceSquared > 16.0D;
    }
    private static boolean hiddenFromMob(Player player) { return hasFullSet(player) && !isProvoked(player); }

    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onHurt(LivingHurtEvent event) {
        if (event.isCanceled() || event.getEntity().level().isClientSide) return;
        Entity attacker = event.getSource().getEntity();
        if (attacker instanceof Player player && isHiveEntity(event.getEntity()) && event.getAmount() > 0) provoke(player);
        if (event.getEntity() instanceof Player player && isHiveEntity(attacker)) {
            event.setAmount(event.getAmount() * (1.0F - 0.08F * pieces(player)));
        }
    }
    @SubscribeEvent
    public static void onTargetChange(LivingChangeTargetEvent event) {
        if (!event.getEntity().level().isClientSide && isHiveEntity(event.getEntity())
                && event.getNewTarget() instanceof Player player && hiddenFromMob(player)) event.setCanceled(true);
    }
    @SubscribeEvent
    public static void onLivingTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide || !isHiveEntity(mob)) return;
        if (mob.getTarget() instanceof Player player && hiddenFromMob(player)) mob.setTarget(null);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onBreak(BlockEvent.BreakEvent event) {
        if (event.isCanceled() || event.getPlayer().level().isClientSide || !hasFullSet(event.getPlayer())) return;
        BlockState state = event.getState();
        if (!state.is(ModBlocks.LIVING_FLESH.get()) && !state.is(ModBlocks.OSSIFIED_FLESH.get())
                && !state.is(ModBlocks.FIREPROOF_FLESH.get()) && !state.is(ModBlocks.FLESH_VEINS.get())
                && !state.is(ModBlocks.BIOMASS_REMAINS.get())) return;
        Player player = event.getPlayer();
        BlockPos pos = event.getPos();
        var nearby = player.level().getEntitiesOfClass(Mob.class, new AABB(pos).inflate(12.0D),
                mob -> mob.isAlive() && isHiveEntity(mob) && mob.distanceToSqr(pos.getX() + .5D, pos.getY() + .5D, pos.getZ() + .5D) <= 144.0D);
        if (nearby.isEmpty()) return;
        provoke(player);
        for (Mob mob : nearby) if (mob.canAttack(player)) mob.setTarget(player);
    }
    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.player.level().isClientSide) return;
        Player player = event.player;
        if (!player.isAlive() || player.isSpectator() || !player.onGround() || !hasSymbioticPair(player)
                || player.tickCount % 60 != 0 || player.getHealth() >= player.getMaxHealth()) return;
        if (player.getBlockStateOn().is(ModBlocks.LIVING_FLESH.get())) player.heal(1.0F);
    }
}
```

## `src/main/java/com/carnis/mod/client/gui/overlay/NeuroResonanceOverlay.java`

```java
package com.carnis.mod.client.gui.overlay;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.block.entity.PulsingHeartBlockEntity;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlocks;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Incremental, client-only scan of loaded blocks. A completed sweep is atomically published. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NeuroResonanceOverlay implements IGuiOverlay {
    private static final int RADIUS = 24;
    private static final int SIDE = RADIUS * 2 + 1;
    private static final int TOTAL = SIDE * SIDE * SIDE;
    private static final int SCAN_BUDGET = 1024;
    private static ClientLevel scanLevel;
    private static BlockPos anchor;
    private static int cursor;
    private static BlockPos candidateTarget, candidateHeart, target, heart;
    private static double targetDistance, heartDistance;

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        ClientLevel level = mc.level;
        Player player = mc.player;
        if (level == null || player == null || !player.isAlive() || !NeuroArmorEventHandler.hasHelmet(player)) {
            reset();
            return;
        }
        if (scanLevel != level || anchor == null) {
            reset();
            scanLevel = level;
            beginSweep(player);
        }
        for (int n = 0; n < SCAN_BUDGET && cursor < TOTAL; n++, cursor++) {
            int dx = cursor % SIDE - RADIUS;
            int dz = cursor / SIDE % SIDE - RADIUS;
            int dy = cursor / (SIDE * SIDE) - RADIUS;
            if (dx * dx + dy * dy + dz * dz > RADIUS * RADIUS) continue;
            BlockPos pos = anchor.offset(dx, dy, dz);
            if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) continue;
            BlockState state = level.getBlockState(pos);
            boolean isHeart = state.is(ModBlocks.PULSING_HEART.get());
            boolean isPool = state.is(ModBlocks.STOMACH_POOL.get());
            boolean isCluster = state.is(ModBlocks.BIOMASS_REMAINS.get()) && isCluster(level, pos);
            if (!isHeart && !isPool && !isCluster) continue;
            double distance = player.distanceToSqr(Vec3.atCenterOf(pos));
            if (distance > RADIUS * RADIUS) continue;
            if (distance < targetDistance) { targetDistance = distance; candidateTarget = pos; }
            if (isHeart && distance < heartDistance) { heartDistance = distance; candidateHeart = pos; }
        }
        if (cursor == TOTAL) {
            target = candidateTarget;
            heart = candidateHeart;
            beginSweep(player);
        }
    }
    private static boolean isCluster(ClientLevel level, BlockPos pos) {
        int count = 1;
        for (Direction direction : Direction.values()) {
            BlockPos next = pos.relative(direction);
            if (level.hasChunkAt(next) && level.getBlockState(next).is(ModBlocks.BIOMASS_REMAINS.get())) count++;
        }
        return count >= 3;
    }
    private static void beginSweep(Player player) {
        anchor = player.blockPosition().immutable();
        cursor = 0;
        candidateTarget = null;
        candidateHeart = null;
        targetDistance = Double.MAX_VALUE;
        heartDistance = Double.MAX_VALUE;
    }
    private static void reset() {
        scanLevel = null;
        anchor = null;
        cursor = 0;
        candidateTarget = null;
        candidateHeart = null;
        target = null;
        heart = null;
    }
    private static boolean validTarget(ClientLevel level, Player player, BlockPos pos, boolean heartOnly) {
        if (pos == null || !level.hasChunkAt(pos) || player.distanceToSqr(Vec3.atCenterOf(pos)) > RADIUS * RADIUS) return false;
        BlockState state = level.getBlockState(pos);
        if (state.is(ModBlocks.PULSING_HEART.get())) return true;
        return !heartOnly && (state.is(ModBlocks.STOMACH_POOL.get())
                || state.is(ModBlocks.BIOMASS_REMAINS.get()) && isCluster(level, pos));
    }
    private static int color(float alpha) {
        return (Mth.clamp(Math.round(alpha * 255.0F), 0, 255) << 24) | 0x38E094;
    }
    @Override
    public void render(ForgeGui gui, GuiGraphics graphics, float partialTick, int width, int height) {
        Minecraft mc = gui.getMinecraft();
        ClientLevel level = mc.level;
        Player player = mc.player;
        if (level == null || player == null || mc.options.hideGui || !NeuroArmorEventHandler.hasHelmet(player)
                || scanLevel != level) return;
        float opacity = CarnisConfig.CLIENT.neuroSonarOpacity.get().floatValue();
        if (opacity <= 0.0F) return;
        boolean hasHeart = validTarget(level, player, heart, true);
        double time = level.getGameTime() + partialTick;
        double phase = hasHeart
                ? (time + Math.floorMod(heart.asLong(), PulsingHeartBlockEntity.PULSE_INTERVAL_TICKS))
                    / PulsingHeartBlockEntity.PULSE_INTERVAL_TICKS
                : time / 100.0D;
        float pulse = (float) (0.55D + 0.45D * (0.5D + 0.5D * Math.cos(phase * Math.PI * 2.0D)));
        int border = color(opacity * .30F);
        int signal = color(opacity * pulse);
        int cx = width / 2, cy = height / 2;
        graphics.fill(5, 5, 6, Math.min(height - 5, 29), border);
        graphics.fill(5, 5, 29, 6, border);
        graphics.fill(width - 6, 5, width - 5, Math.min(height - 5, 29), border);
        graphics.fill(width - 29, 5, width - 5, 6, border);
        graphics.fill(cx - 2, cy + 24, cx + 3, cy + 29, signal);
        graphics.fill(cx - 5, cy + 26, cx + 6, cy + 27, signal);
        if (!validTarget(level, player, target, false)) return;
        Vec3 delta = Vec3.atCenterOf(target).subtract(player.position());
        double yaw = Math.toRadians(player.getYRot());
        double right = delta.x * -Math.cos(yaw) + delta.z * -Math.sin(yaw);
        double forward = delta.x * -Math.sin(yaw) + delta.z * Math.cos(yaw);
        double length = Math.sqrt(right * right + forward * forward);
        if (length < 1.0E-5D) { right = 0.0D; forward = 1.0D; length = 1.0D; }
        double ux = right / length, uy = -forward / length;
        int x = cx + (int) Math.round(ux * 36), y = cy + (int) Math.round(uy * 36);
        for (int i = -5; i <= 5; i++) {
            int px = x + (int) Math.round(ux * i), py = y + (int) Math.round(uy * i);
            graphics.fill(px, py, px + 2, py + 2, signal);
        }
        for (int i = 0; i <= 4; i++) {
            int bx = x + (int) Math.round(ux * (5 - i));
            int by = y + (int) Math.round(uy * (5 - i));
            int lx = bx + (int) Math.round(-uy * i), ly = by + (int) Math.round(ux * i);
            int rx = bx - (int) Math.round(-uy * i), ry = by - (int) Math.round(ux * i);
            graphics.fill(lx, ly, lx + 2, ly + 2, signal);
            graphics.fill(rx, ry, rx + 2, ry + 2, signal);
        }
        String distance = String.format(java.util.Locale.ROOT, "%.0f m", delta.length());
        graphics.drawCenteredString(mc.font, distance, cx, cy + 34, signal);
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/NeuroArmorRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.client.model.NeuroArmorModel;
import com.carnis.mod.client.renderer.layer.OptionalGlowLayer;
import com.carnis.mod.item.armor.NeuroArmorItem;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoArmorRenderer;

import javax.annotation.Nullable;

public final class NeuroArmorRenderer extends GeoArmorRenderer<NeuroArmorItem> {
    public NeuroArmorRenderer() {
        super(new NeuroArmorModel());
        addRenderLayer(new OptionalGlowLayer<>(this));
    }

    @Nullable @Override public GeoBone getHeadBone() { return getGeoModel().getBone("head").orElse(null); }
    @Nullable @Override public GeoBone getBodyBone() { return getGeoModel().getBone("body").orElse(null); }
    @Nullable @Override public GeoBone getRightArmBone() { return getGeoModel().getBone("right_arm").orElse(null); }
    @Nullable @Override public GeoBone getLeftArmBone() { return getGeoModel().getBone("left_arm").orElse(null); }
    @Nullable @Override public GeoBone getRightLegBone() { return getGeoModel().getBone("right_leg").orElse(null); }
    @Nullable @Override public GeoBone getLeftLegBone() { return getGeoModel().getBone("left_leg").orElse(null); }
    @Nullable @Override public GeoBone getRightBootBone() { return getGeoModel().getBone("right_boot").orElse(null); }
    @Nullable @Override public GeoBone getLeftBootBone() { return getGeoModel().getBone("left_boot").orElse(null); }
}
```

## `src/main/java/com/carnis/mod/client/model/NeuroArmorModel.java`

```java
package com.carnis.mod.client.model;
import com.carnis.mod.item.armor.NeuroArmorItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
public final class NeuroArmorModel extends GeoModel<NeuroArmorItem> {
    @Override public ResourceLocation getModelResource(NeuroArmorItem item) { return new ResourceLocation("carnis", "geo/item/neuro_armor.geo.json"); }
    @Override public ResourceLocation getTextureResource(NeuroArmorItem item) { return new ResourceLocation("carnis", "textures/armor/neuro_armor.png"); }
    @Override public ResourceLocation getAnimationResource(NeuroArmorItem item) { return new ResourceLocation("carnis", "animations/armor/neuro_armor.animation.json"); }
}
```

## `src/main/java/com/carnis/mod/init/ModArmorMaterials.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.item.NeuroArmorMaterial;
import net.minecraft.world.item.ArmorMaterial;

public final class ModArmorMaterials {
    public static final ArmorMaterial NEURO_RESONATOR = NeuroArmorMaterial.INSTANCE;
    private ModArmorMaterials() { }
}
```

## `src/main/java/com/carnis/mod/item/NeuroArmorMaterial.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.init.ModItems;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.ArmorMaterials;
import net.minecraft.world.item.crafting.Ingredient;

public enum NeuroArmorMaterial implements ArmorMaterial {
    INSTANCE;

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> 330;
            case CHESTPLATE -> 480;
            case LEGGINGS -> 450;
            case BOOTS -> 390;
        };
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> 3;
            case CHESTPLATE -> 7;
            case LEGGINGS -> 5;
            case BOOTS -> 2;
        };
    }

    @Override public int getEnchantmentValue() { return 15; }
    @Override public SoundEvent getEquipSound() { return SoundEvents.ARMOR_EQUIP_IRON; }
    @Override public Ingredient getRepairIngredient() { return Ingredient.of(ModItems.LIVING_FLESH.get()); }
    @Override public String getName() { return "carnis:neuro_resonator"; }
    @Override public float getToughness() { return 1.5F; }
    @Override public float getKnockbackResistance() { return 0.025F; }
}
```

## `src/main/java/com/carnis/mod/item/NeuroResonatorArmorItem.java`

```java
package com.carnis.mod.item;

import com.carnis.mod.item.armor.NeuroArmorItem;

/** Keeps existing item registrations and references compatible. */
public class NeuroResonatorArmorItem extends NeuroArmorItem {
    public NeuroResonatorArmorItem(Type type, Properties properties) { super(type, properties); }
}
```

## `src/main/java/com/carnis/mod/item/NeuroResonatorHelmetItem.java`

```java
package com.carnis.mod.item;

import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;

import java.util.Objects;

public final class NeuroResonatorHelmetItem extends NeuroResonatorArmorItem {
    public NeuroResonatorHelmetItem(Properties properties) {
        super(Type.HELMET, properties);
    }

    public static boolean isEquipped(LivingEntity entity) {
        Objects.requireNonNull(entity, "entity");

        return entity.getItemBySlot(EquipmentSlot.HEAD).getItem()
                instanceof NeuroResonatorHelmetItem;
    }
}
```

## `src/main/java/com/carnis/mod/item/NeuroWeave.java`

```java
package com.carnis.mod.item;

import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;

public final class NeuroWeave {
    public static final String TAG = "carnis:neuro_woven";
    private static final EquipmentSlot[] ARMOR_SLOTS = {
            EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET
    };

    private NeuroWeave() { }

    public static boolean isWoven(ItemStack stack) {
        return stack.getItem() instanceof ArmorItem && stack.hasTag() && stack.getTag().getBoolean(TAG);
    }

    public static int protectedPieces(LivingEntity entity) {
        int count = 0;
        for (EquipmentSlot slot : ARMOR_SLOTS) {
            ItemStack stack = entity.getItemBySlot(slot);
            if (isWoven(stack) || stack.getItem() instanceof com.carnis.mod.item.armor.NeuroArmorItem) count++;
        }
        return count;
    }

    public static float infectionMultiplier(LivingEntity entity) {
        return Math.max(0.0F, 1.0F - 0.25F * protectedPieces(entity));
    }

    public static boolean hasSludgeImmuneBoots(LivingEntity entity) {
        ItemStack boots = entity.getItemBySlot(EquipmentSlot.FEET);
        return boots.getItem() instanceof com.carnis.mod.item.armor.NeuroArmorItem armor
                && armor.getType() == ArmorItem.Type.BOOTS;
    }
}
```

## `src/main/java/com/carnis/mod/init/ModItems.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.item.BioPurifierItem;
import com.carnis.mod.item.NeuroResonatorArmorItem;
import net.minecraft.world.item.ArmorItem;
import com.carnis.mod.item.PneumaticInoculatorItem;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.item.PurificationSerumItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, CarnisMod.MOD_ID);

    public static final RegistryObject<Item> BIOMASS_REMAINS = ITEMS.register("biomass_remains",
            () -> new BlockItem(ModBlocks.BIOMASS_REMAINS.get(), new Item.Properties()));

    public static final RegistryObject<Item> FLESH_BULB = ITEMS.register("flesh_bulb",
            () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.FLESH_BULB.get(), new Item.Properties(), "flesh_bulb"));
    public static final RegistryObject<Item> SINEW_SPIKES = ITEMS.register("sinew_spikes",
            () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.SINEW_SPIKES.get(), new Item.Properties(), "sinew_spikes"));
    public static final RegistryObject<ForgeSpawnEggItem> BIOMASS_MAGGOT_SPAWN_EGG = ITEMS.register(
            "biomass_maggot_spawn_egg", () -> new com.carnis.mod.item.MaggotSpawnEggItem(ModEntities.BIOMASS_MAGGOT,
                    0x60202c, 0xc99d79, new Item.Properties()));

    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_ZOMBIE_SPAWN_EGG = ITEMS.register(
            "infected_zombie_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_ZOMBIE,
                    0x552d31, 0x8c9c54, new Item.Properties()));

    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_SKELETON_SPAWN_EGG = ITEMS.register(
            "infected_skeleton_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_SKELETON, 0x552d31, 0xc7b9a6, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_CREEPER_SPAWN_EGG = ITEMS.register(
            "infected_creeper_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_CREEPER, 0x552d31, 0x668b45, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> INFECTED_SPIDER_SPAWN_EGG = ITEMS.register(
            "infected_spider_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.INFECTED_SPIDER, 0x552d31, 0x654643, new Item.Properties()));

    public static final RegistryObject<net.minecraft.world.item.BucketItem> TAINTED_SLUDGE_BUCKET = ITEMS.register(
            "tainted_sludge_bucket", () -> new net.minecraft.world.item.BucketItem(ModFluids.SLUDGE_SOURCE,
                    new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1)));
    public static final RegistryObject<com.carnis.mod.item.CodexCarnisItem> RESEARCH_JOURNAL = ITEMS.register(
            "research_journal", () -> new com.carnis.mod.item.CodexCarnisItem(new Item.Properties()));
    public static final RegistryObject<Item> FLESH_SPAT = ITEMS.register("flesh_spat", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> BONE_SCYTHE_ARM = ITEMS.register("bone_scythe_arm",
            () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> FLESH_VEINS = ITEMS.register("flesh_veins",
            () -> new BlockItem(ModBlocks.FLESH_VEINS.get(), new Item.Properties()));

    public static final RegistryObject<com.carnis.mod.item.AntibioticsItem> ANTIBIOTICS = ITEMS.register("antibiotics",
            () -> new com.carnis.mod.item.AntibioticsItem(new Item.Properties().stacksTo(16)));

    public static final RegistryObject<Item> NEURAL_BINDING_MATRIX = ITEMS.register(
            "neural_binding_matrix", () -> new Item(new Item.Properties()));
    public static final RegistryObject<NeuroResonatorArmorItem> NEURO_RESONATOR_CHESTPLATE = ITEMS.register(
            "neuro_resonator_chestplate", () -> new NeuroResonatorArmorItem(ArmorItem.Type.CHESTPLATE, new Item.Properties()));
    public static final RegistryObject<NeuroResonatorArmorItem> NEURO_RESONATOR_LEGGINGS = ITEMS.register(
            "neuro_resonator_leggings", () -> new NeuroResonatorArmorItem(ArmorItem.Type.LEGGINGS, new Item.Properties()));
    public static final RegistryObject<NeuroResonatorArmorItem> NEURO_RESONATOR_BOOTS = ITEMS.register(
            "neuro_resonator_boots", () -> new NeuroResonatorArmorItem(ArmorItem.Type.BOOTS, new Item.Properties()));

    public static final RegistryObject<Item> NERVE_PILLAR = ITEMS.register("nerve_pillar",
            () -> new BlockItem(ModBlocks.NERVE_PILLAR.get(), new Item.Properties()));
    public static final RegistryObject<Item> VIRAL_DART = ITEMS.register("viral_dart",
            () -> new Item(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<Item> PURIFICATION_DART = ITEMS.register("purification_dart",
            () -> new Item(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<PneumaticInoculatorItem> PNEUMATIC_INOCULATOR = ITEMS.register(
            "pneumatic_inoculator", () -> new PneumaticInoculatorItem(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> CREEPING_TENDRILS = ITEMS.register(
            "creeping_tendrils", () -> new BlockItem(ModBlocks.CREEPING_TENDRILS.get(), new Item.Properties()));
    public static final RegistryObject<Item> PUSTULE_CLUSTER = ITEMS.register(
            "pustule_cluster", () -> new BlockItem(ModBlocks.PUSTULE_CLUSTER.get(), new Item.Properties()));
    public static final RegistryObject<Item> STOMACH_POOL = ITEMS.register(
            "stomach_pool", () -> new BlockItem(ModBlocks.STOMACH_POOL.get(), new Item.Properties()));

    public static final RegistryObject<Item> SPORE_SPROUT = ITEMS.register(
            "spore_sprout", () -> new BlockItem(ModBlocks.SPORE_SPROUT.get(), new Item.Properties()));
    public static final RegistryObject<Item> NEURAL_MOSS = ITEMS.register(
            "neural_moss", () -> new BlockItem(ModBlocks.NEURAL_MOSS.get(), new Item.Properties()));

    public static final RegistryObject<Item> CHARRED_FLESH = ITEMS.register(
            "charred_flesh",
            () -> new BlockItem(ModBlocks.CHARRED_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> LIVING_FLESH = ITEMS.register(
            "living_flesh",
            () -> new BlockItem(ModBlocks.LIVING_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> OSSIFIED_FLESH = ITEMS.register(
            "ossified_flesh",
            () -> new BlockItem(ModBlocks.OSSIFIED_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> FIREPROOF_FLESH = ITEMS.register(
            "fireproof_flesh",
            () -> new BlockItem(ModBlocks.FIREPROOF_FLESH.get(), new Item.Properties())
    );

    public static final RegistryObject<Item> PULSING_HEART = ITEMS.register(
            "pulsing_heart",
            () -> new com.carnis.mod.item.PulsingHeartItem(
                    ModBlocks.PULSING_HEART.get(),
                    new Item.Properties()
            )
    );

    public static final RegistryObject<Item> HIVE_EYE = ITEMS.register(
            "hive_eye",
            () -> new com.carnis.mod.item.HiveEyeItem(
                    ModBlocks.HIVE_EYE.get(),
                    new Item.Properties()
            )
    );

    public static final RegistryObject<ForgeSpawnEggItem>
            FLESH_AMALGAM_SPAWN_EGG = ITEMS.register(
                    "flesh_amalgam_spawn_egg",
                    () -> new ForgeSpawnEggItem(
                            ModEntities.FLESH_AMALGAM,
                            0x6F1B31,
                            0xD98B76,
                            new Item.Properties()
                    )
            );

    public static final RegistryObject<PurificationSerumItem>
            PURIFICATION_SERUM = ITEMS.register(
                    "purification_serum",
                    () -> new PurificationSerumItem(
                            new Item.Properties()
                                    .stacksTo(16)
                                    .craftRemainder(Items.GLASS_BOTTLE)
                                    .rarity(Rarity.UNCOMMON)
                    )
            );

    public static final RegistryObject<BioPurifierItem>
            BIO_PURIFIER = ITEMS.register(
                    "bio_purifier",
                    () -> new BioPurifierItem(
                            new Item.Properties()
                                    .durability(BioPurifierItem.MAX_DURABILITY)
                                    .rarity(Rarity.RARE)
                    )
            );

    public static final RegistryObject<NeuroResonatorHelmetItem>
            NEURO_RESONATOR_HELMET = ITEMS.register(
                    "neuro_resonator_helmet",
                    () -> new NeuroResonatorHelmetItem(
                            new Item.Properties()
                                    .rarity(Rarity.UNCOMMON)
                    )
            );

    private ModItems() {
    }

    public static void register(IEventBus modEventBus) {
        ITEMS.register(modEventBus);
    }
}
```

## `src/main/java/com/carnis/mod/capability/infection/PlayerInfectionApi.java`

```java
package com.carnis.mod.capability.infection;

import net.minecraft.world.entity.player.Player;
import com.carnis.mod.item.NeuroWeave;

import java.util.Objects;

public final class PlayerInfectionApi {
    private PlayerInfectionApi() {
    }

    public static float getInfectionLevel(Player player) {
        Objects.requireNonNull(player, "player");

        return player.getCapability(
                        PlayerInfectionCapability.PLAYER_INFECTION
                )
                .resolve()
                .map(IPlayerInfection::getInfectionLevel)
                .orElse(IPlayerInfection.MIN_INFECTION);
    }

    public static boolean setInfectionLevel(
            Player player,
            float infectionLevel
    ) {
        Objects.requireNonNull(player, "player");
        if (infectionLevel > getInfectionLevel(player)
                && player.hasEffect(com.carnis.mod.init.ModEffects.IMMUNOSUPPRESSION.get())) return false;

        return player.getCapability(
                        PlayerInfectionCapability.PLAYER_INFECTION
                )
                .resolve()
                .map(infection -> infection.setInfectionLevel(infectionLevel))
                .orElse(false);
    }

    public static boolean addInfection(Player player, float amount) {
        Objects.requireNonNull(player, "player");
        if (amount > 0.0F && player.hasEffect(com.carnis.mod.init.ModEffects.IMMUNOSUPPRESSION.get())) return false;

        return player.getCapability(
                        PlayerInfectionCapability.PLAYER_INFECTION
                )
                .resolve()
                .map(infection -> infection.addInfection(amount))
                .orElse(false);
    }

    /** Applies equipment protection to environmental/hostile exposure, not commands or cures. */
    public static boolean addExposure(Player player, float amount) {
        if (amount > 0.0F && player.hasEffect(com.carnis.mod.init.ModEffects.IMMUNOSUPPRESSION.get())) return false;
        return addInfection(player, amount > 0.0F ? amount * NeuroWeave.infectionMultiplier(player) : amount);
    }

    public static boolean isAssimilated(Player player) {
        Objects.requireNonNull(player, "player");

        return player.getCapability(
                        PlayerInfectionCapability.PLAYER_INFECTION
                )
                .resolve()
                .map(IPlayerInfection::isAssimilated)
                .orElse(false);
    }

    public static boolean isHostileTarget(Player player) {
        Objects.requireNonNull(player, "player");
        return player.isAlive()
                && !player.isSpectator()
                && !isAssimilated(player);
    }

    /**
     * Copies state without emitting a packet during PlayerEvent.Clone. The
     * post-clone respawn/dimension lifecycle event performs the authoritative
     * client sync after the replacement ServerPlayer is fully installed.
     */
    public static void copy(Player source, Player target) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(target, "target");

        float sourceLevel = getInfectionLevel(source);
        target.getCapability(PlayerInfectionCapability.PLAYER_INFECTION)
                .ifPresent(infection -> {
                    if (infection instanceof PlayerInfection data) {
                        data.setInfectionLevelSilently(sourceLevel);
                    } else {
                        infection.setInfectionLevel(sourceLevel);
                    }
                });
    }
}
```

## `src/main/java/com/carnis/mod/event/PlayerInfectionEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.capability.infection.PlayerInfectionCapability;
import com.carnis.mod.capability.infection.PlayerInfectionProvider;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;
import com.carnis.mod.init.ModBlockTags;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.network.ModMessages;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.AttachCapabilitiesEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class PlayerInfectionEvents {
    public static final float SURFACE_INFECTION_PER_TICK = 0.05F;
    public static final float MOB_HIT_BASE_INFECTION = 1.0F;
    public static final float MOB_HIT_INFECTION_PER_DAMAGE = 0.5F;

    private PlayerInfectionEvents() {
    }

    @SubscribeEvent
    public static void onAttachCapabilities(
            AttachCapabilitiesEvent<Entity> event
    ) {
        if (!(event.getObject() instanceof Player player)) {
            return;
        }

        PlayerInfectionProvider provider = new PlayerInfectionProvider(player);
        event.addCapability(PlayerInfectionCapability.ID, provider);
        event.addListener(provider::invalidate);
    }

    @SubscribeEvent
    public static void onPlayerClone(PlayerEvent.Clone event) {
        Player original = event.getOriginal();
        original.reviveCaps();

        try {
            // The same NBT contract is used for death and non-death clones.
            original.getCapability(PlayerInfectionCapability.PLAYER_INFECTION)
                    .resolve().ifPresentOrElse(source -> {
                        var snapshot = PlayerInfectionProvider.serializeInfection(source);
                        event.getEntity().getCapability(PlayerInfectionCapability.PLAYER_INFECTION)
                                .resolve().ifPresentOrElse(target -> {
                                    PlayerInfectionProvider.deserializeInfection(target, snapshot);
                                    if (event.getEntity() instanceof ServerPlayer
                                            && CarnisConfig.SERVER.debugLogging.get()) {
                                        CarnisMod.LOGGER.debug(
                                                "Infection clone death={} source={} target={}",
                                                event.isWasDeath(), source.getInfectionLevel(),
                                                target.getInfectionLevel()
                                        );
                                    }
                                }, () -> CarnisMod.LOGGER.warn("Missing infection capability on clone target"));
                    }, () -> CarnisMod.LOGGER.warn("Missing infection capability on clone source"));
        } finally {
            original.invalidateCaps();
        }
    }

    @SubscribeEvent
    public static void onPlayerLoggedIn(
            PlayerEvent.PlayerLoggedInEvent event
    ) {
        sync(event.getEntity());
    }

    @SubscribeEvent
    public static void onPlayerRespawn(
            PlayerEvent.PlayerRespawnEvent event
    ) {
        sync(event.getEntity());
    }

    @SubscribeEvent
    public static void onPlayerChangedDimension(
            PlayerEvent.PlayerChangedDimensionEvent event
    ) {
        sync(event.getEntity());
    }

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (
                event.phase != TickEvent.Phase.END
                        || !(event.player instanceof ServerPlayer player)
                        || !player.isAlive()
                        || player.isSpectator()
                        || !player.onGround()
                        || PlayerInfectionApi.isAssimilated(player)
                        || !player.getBlockStateOn().is(
                                ModBlockTags.INFECTIOUS_SURFACES
                        )
        ) {
            return;
        }

        float surfaceInfection = SURFACE_INFECTION_PER_TICK;

        PlayerInfectionApi.addExposure(player, surfaceInfection);
    }

    @SubscribeEvent
    public static void onNecroticTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END
                || !(event.player instanceof ServerPlayer player)
                || !player.isAlive() || player.isSpectator()
                || !PlayerInfectionApi.isAssimilated(player)
                || player.tickCount % 20 != 0) {
            return;
        }
        player.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 40, 0, false, false));
        ServerLevel level = player.serverLevel();
        level.sendParticles(ParticleTypes.ITEM_SLIME, player.getX(),
                player.getY() + player.getBbHeight() * 0.5D, player.getZ(),
                18, 0.4D, 0.6D, 0.4D, 0.04D);
        player.hurt(ModDamageTypes.necroticConsumption(level), 2.0F);
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onInfectedDeath(LivingDeathEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof ServerPlayer player)
                || PlayerInfectionApi.getInfectionLevel(player) < 90.0F) {
            return;
        }
        ServerLevel level = player.serverLevel();
        int count = 1 + level.getRandom().nextInt(3);
        BlockPos base = player.blockPosition();
        // Prefer the death cell and vertically adjacent cells. Never force-load a chunk
        // or displace fluids, containers, or solid blocks.
        int placed = 0;
        for (int dy = 0; dy <= 2 && placed < count; dy++) {
            BlockPos pos = base.above(dy);
            if (level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) {
                continue;
            }
            BlockState state = level.getBlockState(pos);
            if ((state.isAir() || state.canBeReplaced()) && state.getFluidState().isEmpty()
                    && !state.hasBlockEntity()
                    && level.setBlockAndUpdate(pos, ModBlocks.LIVING_FLESH.get().defaultBlockState())) {
                placed++;
            }
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onLivingHurt(LivingHurtEvent event) {
        if (
                event.isCanceled()
                        || event.getAmount() <= 0.0F
                        || event.getSource().getDirectEntity() instanceof com.carnis.mod.entity.FleshSpatProjectileEntity
                        || !(event.getEntity() instanceof ServerPlayer player)
                        || !isCarnisMobDamage(event.getSource())
        ) {
            return;
        }

        Entity attacker = event.getSource().getEntity();
        boolean direct = event.getSource().getDirectEntity() == attacker;
        float infectionGain = direct && attacker instanceof InfectedZombieEntity ? 8.0F
                : direct && attacker instanceof InfectedSkeletonEntity ? 10.0F
                : direct && attacker instanceof InfectedSpiderEntity ? 5.0F
                : MOB_HIT_BASE_INFECTION + event.getAmount() * MOB_HIT_INFECTION_PER_DAMAGE;
        PlayerInfectionApi.addExposure(player, infectionGain);
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onLivingChangeTarget(
            LivingChangeTargetEvent event
    ) {
        if (
                event.isCanceled()
                        || !(event.getEntity() instanceof Mob mob)
                        || !(mob.level() instanceof ServerLevel)
                        || !isCarnisMob(mob)
                        || !(event.getNewTarget() instanceof Player player)
                        || !PlayerInfectionApi.isAssimilated(player)
        ) {
            return;
        }

        // Cancelling preserves the mob's previous target. For an attempted
        // acquisition of an assimilated player that target is normally null.
        event.setCanceled(true);
    }

    private static boolean isCarnisMobDamage(DamageSource source) {
        return isCarnisMob(source.getEntity())
                || isCarnisMob(source.getDirectEntity());
    }

    private static boolean isCarnisMob(Entity entity) {
        if (!(entity instanceof Mob mob)) {
            return false;
        }

        if (mob instanceof HivemindLinkedMob) {
            return true;
        }

        ResourceLocation entityTypeId = ForgeRegistries.ENTITY_TYPES.getKey(
                mob.getType()
        );

        return entityTypeId != null
                && CarnisMod.MOD_ID.equals(entityTypeId.getNamespace());
    }

    private static void sync(Player player) {
        if (player instanceof ServerPlayer serverPlayer) {
            ModMessages.sendPlayerInfection(serverPlayer);
        }
    }
}
```

## `src/main/java/com/carnis/mod/event/BootCorrosionEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.item.NeuroWeave;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class BootCorrosionEvents {
    private BootCorrosionEvents() { }

    @SubscribeEvent
    public static void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)
                || !player.isAlive() || player.isSpectator() || !player.onGround()
                || player.tickCount % 60 != 0 || !player.getBlockStateOn().is(ModBlocks.LIVING_FLESH.get())) return;
        ItemStack boots = player.getItemBySlot(EquipmentSlot.FEET);
        if (!boots.isEmpty() && !NeuroWeave.isWoven(boots) && !(boots.getItem() instanceof com.carnis.mod.item.armor.NeuroArmorItem)) {
            boots.hurtAndBreak(1, player, entity -> entity.broadcastBreakEvent(EquipmentSlot.FEET));
        }
    }
}
```

## `src/main/java/com/carnis/mod/block/BiomassRemainsBlock.java`

```java
package com.carnis.mod.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

public final class BiomassRemainsBlock extends Block {
    private static final VoxelShape SHAPE = Block.box(0, 0, 0, 16, 3, 16);
    public BiomassRemainsBlock(BlockBehaviour.Properties properties) { super(properties); }
    @Override public VoxelShape getShape(BlockState state, BlockGetter world, BlockPos pos, CollisionContext context) { return SHAPE; }
    @Override public boolean canSurvive(BlockState state, LevelReader world, BlockPos pos) {
        return world.getBlockState(pos.below()).isFaceSturdy(world, pos.below(), Direction.UP);
    }
    @Override public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
            LevelAccessor world, BlockPos pos, BlockPos neighborPos) {
        return direction == Direction.DOWN && !state.canSurvive(world, pos) ? Blocks.AIR.defaultBlockState()
                : super.updateShape(state, direction, neighbor, world, pos, neighborPos);
    }
    @Override public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        if (!(entity instanceof LivingEntity living)) return;
        Vec3 velocity = living.getDeltaMovement();
        if (!(living instanceof net.minecraft.world.entity.player.Player player)
                || !com.carnis.mod.event.NeuroArmorEventHandler.hasSymbioticPair(player))
            living.setDeltaMovement(velocity.x * 0.8D, velocity.y, velocity.z * 0.8D);
        if (!level.isClientSide && living.tickCount % 12 == 0 && velocity.horizontalDistanceSqr() > 0.0004D)
            level.playSound(null, pos, SoundEvents.SLIME_SQUISH, SoundSource.BLOCKS, 0.4F, 0.7F);
    }
}
```

## `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.entity.FleshAmalgamEntity;
import com.carnis.mod.entity.HivemindLinkedMob;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

import java.lang.ref.WeakReference;

public final class HiveEyeBlockEntity extends BlockEntity implements software.bernie.geckolib.animatable.GeoBlockEntity {
    private final software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache animationCache =
            software.bernie.geckolib.util.GeckoLibUtil.createInstanceCache(this);

    @Override
    public software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }

    @Override
    public void registerControllers(software.bernie.geckolib.core.animation.AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this, "idle", 0,
                state -> state.setAndContinue(software.bernie.geckolib.core.animation.RawAnimation.begin()
                        .thenLoop("animation.hive_eye.idle"))));
    }

    public static final int SCAN_INTERVAL_TICKS = 20;
    public static final double PLAYER_SCAN_RADIUS = 24.0D;
    public static final double HIVEMIND_ALERT_RADIUS = 32.0D;
    private WeakReference<LivingEntity> lastDetectedTarget = new WeakReference<>(null);

    public HiveEyeBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.HIVE_EYE.get(), pos, state);
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, HiveEyeBlockEntity eye) {
        if (level instanceof ServerLevel serverLevel
                && Math.floorMod(serverLevel.getGameTime() + Math.floorMod(pos.asLong(), SCAN_INTERVAL_TICKS),
                        SCAN_INTERVAL_TICKS) == 0L) {
            eye.scan(serverLevel);
        }
    }

    private void scan(ServerLevel level) {
        com.carnis.mod.world.HiveNetwork.observe(level, worldPosition, getBlockState(), true);
        Vec3 center = Vec3.atCenterOf(worldPosition);
        AABB search = AABB.ofSize(center, PLAYER_SCAN_RADIUS * 2.0D,
                PLAYER_SCAN_RADIUS * 2.0D, PLAYER_SCAN_RADIUS * 2.0D);
        LivingEntity nearest = null;
        double closest = PLAYER_SCAN_RADIUS * PLAYER_SCAN_RADIUS;
        for (LivingEntity candidate : level.getEntitiesOfClass(LivingEntity.class, search, HiveEyeBlockEntity::isTarget)) {
            double distance = candidate.position().distanceToSqr(center);
            if (candidate instanceof Player player
                    && com.carnis.mod.event.NeuroArmorEventHandler.hiddenFromSensor(player, distance)) continue;
            if (distance <= closest) {
                nearest = candidate;
                closest = distance;
            }
        }
        if (nearest == null) {
            lastDetectedTarget.clear();
            return;
        }
        if (nearest != lastDetectedTarget.get()) {
            level.playSound(null, worldPosition, ModSounds.HIVE_EYE_SCREECH.get(),
                    SoundSource.BLOCKS, 1.25F, 0.92F);
            level.sendParticles(ParticleTypes.ELECTRIC_SPARK, center.x, center.y + 0.5D, center.z,
                    12, 0.25D, 0.2D, 0.25D, 0.02D);
            lastDetectedTarget = new WeakReference<>(nearest);
        }
        nearest.addEffect(new MobEffectInstance(MobEffects.GLOWING, 100, 0));
        LivingEntity target = nearest;
        AABB alert = AABB.ofSize(center, HIVEMIND_ALERT_RADIUS * 2.0D,
                HIVEMIND_ALERT_RADIUS * 2.0D, HIVEMIND_ALERT_RADIUS * 2.0D);
        for (FleshAmalgamEntity mob : level.getEntitiesOfClass(FleshAmalgamEntity.class, alert,
                entity -> entity.isAlive() && entity.position().distanceToSqr(center)
                        <= HIVEMIND_ALERT_RADIUS * HIVEMIND_ALERT_RADIUS)) {
            if (mob.canAttack(target)) {
                mob.setTarget(target);
            }
        }
    }

    private static boolean isTarget(LivingEntity entity) {
        if (!entity.isAlive() || entity.isSpectator() || entity instanceof HivemindLinkedMob) {
            return false;
        }
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
        if (id != null && CarnisMod.MOD_ID.equals(id.getNamespace())) {
            return false;
        }
        if (entity instanceof Player player) {
            return !player.isCreative() && PlayerInfectionApi.getInfectionLevel(player) <= 0.0F;
        }
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/client/ClientModEvents.java`

```java
package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.gui.InfectionVeinsOverlay;
import com.carnis.mod.client.renderer.FleshAmalgamRenderer;
import com.carnis.mod.client.renderer.DartRenderer;
import com.carnis.mod.client.renderer.PulsingHeartRenderer;
import com.carnis.mod.client.renderer.HiveEyeRenderer;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModEntities;
import net.minecraft.client.renderer.entity.ZombieRenderer;
import net.minecraft.client.renderer.entity.SkeletonRenderer;
import net.minecraft.client.renderer.entity.CreeperRenderer;
import net.minecraft.client.renderer.entity.SpiderRenderer;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.MOD,
        value = Dist.CLIENT
)
public final class ClientModEvents {
    private ClientModEvents() {
    }

    @SubscribeEvent
    public static void onRegisterRenderers(
            EntityRenderersEvent.RegisterRenderers event
    ) {
        event.registerEntityRenderer(ModEntities.HIVE_SENTINEL.get(), com.carnis.mod.client.renderer.HiveSentinelRenderer::new);
        event.registerEntityRenderer(ModEntities.CEREBRAL_NEXUS.get(), com.carnis.mod.client.renderer.CerebralNexusRenderer::new);
        event.registerEntityRenderer(ModEntities.BIOMASS_MAGGOT.get(), com.carnis.mod.client.renderer.BiomassMaggotRenderer::new);
        event.registerEntityRenderer(ModEntities.PARASITIC_TENDRIL.get(), com.carnis.mod.client.renderer.ParasiticTendrilRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_ZOMBIE.get(), com.carnis.mod.client.renderer.InfectedZombieRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_SKELETON.get(), com.carnis.mod.client.renderer.InfectedSkeletonRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_CREEPER.get(), com.carnis.mod.client.renderer.InfectedCreeperRenderer::new);
        event.registerEntityRenderer(ModEntities.INFECTED_SPIDER.get(), com.carnis.mod.client.renderer.InfectedSpiderRenderer::new);

        event.registerEntityRenderer(ModEntities.FLESH_SPAT.get(), net.minecraft.client.renderer.entity.ThrownItemRenderer::new);
        event.registerEntityRenderer(ModEntities.VIRAL_DART.get(), DartRenderer::new);
        event.registerEntityRenderer(ModEntities.PURIFICATION_DART.get(), DartRenderer::new);
        event.registerBlockEntityRenderer(
                ModBlockEntities.PULSING_HEART.get(),
                PulsingHeartRenderer::new
        );
        event.registerBlockEntityRenderer(ModBlockEntities.HIVE_EYE.get(), HiveEyeRenderer::new);
        event.registerEntityRenderer(
                ModEntities.FLESH_AMALGAM.get(),
                FleshAmalgamRenderer::new
        );
    }

    @SubscribeEvent
    public static void onRegisterParticles(net.minecraftforge.client.event.RegisterParticleProvidersEvent event) {
        event.registerSpriteSet(com.carnis.mod.init.ModParticles.BIOMASS_SPARK.get(),
                com.carnis.mod.client.particle.BiomassSparkParticle.Provider::new);
        event.registerSpriteSet(com.carnis.mod.init.ModParticles.PURIFIER_FLAME.get(),
                com.carnis.mod.client.particle.BiomassSparkParticle.Provider::new);
    }

    @SubscribeEvent
    public static void onClientSetup(net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            net.minecraft.client.renderer.ItemBlockRenderTypes.setRenderLayer(
                    com.carnis.mod.init.ModFluids.SLUDGE_SOURCE.get(), net.minecraft.client.renderer.RenderType.translucent());
            net.minecraft.client.renderer.ItemBlockRenderTypes.setRenderLayer(
                    com.carnis.mod.init.ModFluids.SLUDGE_FLOWING.get(), net.minecraft.client.renderer.RenderType.translucent());
        });
    }

    @SubscribeEvent
    public static void onRegisterGuiOverlays(
            RegisterGuiOverlaysEvent event
    ) {
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "veins_overlay", new InfectionVeinsOverlay());
        event.registerAbove(VanillaGuiOverlay.VIGNETTE.id(), "neuro_resonance", new com.carnis.mod.client.gui.overlay.NeuroResonanceOverlay());
    }
}
```

## `src/main/java/com/carnis/mod/config/CarnisConfig.java`

```java
package com.carnis.mod.config;

import net.minecraftforge.common.ForgeConfigSpec;

public final class CarnisConfig {
    public static final Server SERVER;
    public static final ForgeConfigSpec SERVER_SPEC;

    public static final Client CLIENT;
    public static final ForgeConfigSpec CLIENT_SPEC;

    static {
        ForgeConfigSpec.Builder serverBuilder = new ForgeConfigSpec.Builder();
        SERVER = new Server(serverBuilder);
        SERVER_SPEC = serverBuilder.build();

        ForgeConfigSpec.Builder clientBuilder = new ForgeConfigSpec.Builder();
        CLIENT = new Client(clientBuilder);
        CLIENT_SPEC = clientBuilder.build();
    }

    private CarnisConfig() {
    }

    public static final class Server {
        public final ForgeConfigSpec.IntValue infectionBlocksPerTick;
        public final ForgeConfigSpec.IntValue pulsingHeartQueueBonus;
        public final ForgeConfigSpec.IntValue digestorMaxItemsPerCycle;
        public final ForgeConfigSpec.BooleanValue debugLogging;

        private Server(ForgeConfigSpec.Builder builder) {
            builder.comment("Server-side gameplay and performance settings.")
                    .push("server");

            builder.comment("Optimized infection queue settings.")
                    .push("infection_queue");

            infectionBlocksPerTick = builder
                    .comment("Maximum number of queued infection positions processed per server tick.")
                    .defineInRange("blocks_per_tick", 64, 1, 4096);

            pulsingHeartQueueBonus = builder
                    .comment("Additional queued positions a nearby Pulsing Heart may process per server tick.")
                    .defineInRange("pulsing_heart_bonus", 32, 0, 1024);

            builder.pop();

            builder.comment("Living organ settings.")
                    .push("organs");

            digestorMaxItemsPerCycle = builder
                    .comment("Maximum number of item entities a Digestor Pit may consume during one cycle.")
                    .defineInRange("digestor_max_items_per_cycle", 16, 1, 256);

            builder.pop();

            debugLogging = builder
                    .comment("Writes additional Carnis diagnostics to the server log.")
                    .define("debug_logging", false);

            builder.pop();
        }
    }

    public static final class Client {
        public final ForgeConfigSpec.BooleanValue veinOverlayEnabled;
        public final ForgeConfigSpec.DoubleValue veinOverlayIntensity;
        public final ForgeConfigSpec.BooleanValue hallucinationSoundsEnabled;
        public final ForgeConfigSpec.DoubleValue hallucinationSoundVolume;
        public final ForgeConfigSpec.BooleanValue atmosphericFogEnabled;
        public final ForgeConfigSpec.DoubleValue neuroSonarOpacity;

        private Client(ForgeConfigSpec.Builder builder) {
            builder.comment("Client-only presentation settings. No gameplay logic is stored here.")
                    .push("client");

            builder.comment("Procedural hallucination overlay settings.")
                    .push("hallucinations");

            veinOverlayEnabled = builder
                    .comment("Enables the procedural pulsing-vein screen overlay.")
                    .define("vein_overlay_enabled", true);

            veinOverlayIntensity = builder
                    .comment("Opacity multiplier for the procedural vein overlay.")
                    .defineInRange("vein_overlay_intensity", 1.0D, 0.0D, 1.0D);

            hallucinationSoundsEnabled = builder
                    .comment("Enables client-side phantom sounds triggered by server packets.")
                    .define("hallucination_sounds_enabled", true);

            hallucinationSoundVolume = builder
                    .comment("Volume multiplier for phantom hallucination sounds.")
                    .defineInRange("hallucination_sound_volume", 0.75D, 0.0D, 1.0D);

            builder.pop();

            neuroSonarOpacity = builder.comment("Neuro-resonance visor and sonar opacity, 0 to 1.")
                    .defineInRange("neuro_sonar_opacity", 0.65D, 0.0D, 1.0D);

            builder.comment("Infection atmosphere settings.")
                    .push("atmosphere");

            atmosphericFogEnabled = builder
                    .comment("Enables infection-driven atmospheric fog color and distance.")
                    .define("atmospheric_fog_enabled", true);

            builder.pop();
            builder.pop();
        }
    }
}
```

## `src/main/java/com/carnis/mod/datagen/ModLanguageProvider.java`

```java
package com.carnis.mod.datagen;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModItems;
import net.minecraft.data.PackOutput;
import net.minecraftforge.common.data.LanguageProvider;

public final class ModLanguageProvider extends LanguageProvider {
    private static final String EN_US = "en_us";
    private static final String RU_RU = "ru_ru";

    private final String locale;

    public ModLanguageProvider(PackOutput output, String locale) {
        super(output, CarnisMod.MOD_ID, locale);
        this.locale = locale;
    }

    @Override
    protected void addTranslations() {
        switch (locale) {
            case EN_US -> addEnglishTranslations();
            case RU_RU -> addRussianTranslations();
            default -> throw new IllegalStateException(
                    "Unsupported Carnis language provider locale: " + locale
            );
        }
    }

    private void addEnglishTranslations() {
        add("subtitles.carnis.inoculator_fire", "Inoculator fires");
        add("subtitles.carnis.dart_hit", "Dart hits");
        add("tooltip.carnis.flesh_bulb.mechanics", "An incubation sac that can attach to ceilings and floors.");
        add("tooltip.carnis.flesh_bulb.lore", "The muffled, rapid heartbeat of a maturing brood can be heard inside.");
        add("tooltip.carnis.sinew_spikes.mechanics", "Deals piercing damage and slows any creature that steps on it.");
        add("tooltip.carnis.sinew_spikes.lore", "Taut sinews respond to the slightest vibration of footsteps.");
        add("tooltip.carnis.biomass_maggot.mechanics", "A voracious scavenger. Devours organic remains and pupates in soil.");
        add("tooltip.carnis.biomass_maggot.lore", "The first link in the Hive’s parasitic cycle.");
        add("item.carnis.infected_zombie_spawn_egg", "Infected Zombie Spawn Egg");
        add("entity.carnis.infected_zombie", "Infected Zombie");
        add("tooltip.carnis.infected_zombie_spawn_egg", "Spawns an infected zombie.");
        add("item.carnis.antibiotics", "Antibiotics");
        add("effect.carnis.immunosuppression", "Immunosuppression");
        add("tooltip.carnis.antibiotics", "Prevents exposure for 3 minutes.");
        add("entity.carnis.parasitic_tendril", "Parasitic Tendril");
        add("entity.carnis.hive_sentinel", "Hive Sentinel");
        add("entity.carnis.cerebral_nexus", "Cerebral Nexus");
        add("effect.carnis.incubating", "Incubating");
        add("subtitles.carnis.flamethrower_fire", "Flamethrower roars");
        add("subtitles.carnis.amalgam_roar", "Amalgam roars");
        add("codex.carnis.chapter.0", "Inception & Biomes");
        add("codex.carnis.body.0", "Veins spread across supported faces; incomplete faces may resist growth. Sludge contaminates players and reacts with water and lava. Infection spreads by a queued process.");
        add("codex.carnis.chapter.1", "Adaptive Hivemind");
        add("codex.carnis.body.1", "FIRE / RANGED / MELEE / EXPLOSIVE use the same logarithmic mitigation curve. Points: 0 / 100 / 300 / 600 / 1000. Reduction: 0% / 25% / 50% / 70% / 80%. Between thresholds: linear interpolation in ln(1+points). Cap 80%.");
        add("codex.carnis.chapter.2", "Hive Organs & Flora");
        add("codex.carnis.body.2", "Hive Eye detects players within 24 blocks and alerts linked mobs within 32. Placing a Nerve Pillar halves remaining chunk shock. Stomach Pool dissolves items: flesh or meat gives 5 biomass each; other items give 1. Living creatures take 4 damage per second.");
        add("codex.carnis.chapter.3", "Medical & Armor Weaving");
        add("codex.carnis.body.3", "Serum reduces infection by 35. Antibiotics block positive exposure for 3600 ticks. On an anvil, combine armor and one neural binding matrix for 5 levels. Each woven or resonator armor piece reduces exposure by 25%; four pieces reach 100%.");
        add("codex.carnis.chapter.4", "Mutants & Amalgamation");
        add("codex.carnis.body.4", "Zombie: 35 health, 4.5 attack; skeleton: 28 health, 4.5 attack; creeper: 24 health; spider: 20 health, 3 attack. Spat: 2 damage, Slowness II for 100 ticks and +5 exposure on successful damage. Three zombies near a heart at 300 biomass can fuse.");
        add("entity.carnis.flesh_spat", "Flesh Spat");
        add("item.carnis.flesh_spat", "Flesh Spat");
        add("tooltip.carnis.flesh_spat", "A glob of infectious tissue.");
        add("subtitles.carnis.heartbeat_loop", "Heart beats");
        add("item.carnis.research_journal", "Codex Carnis");
        add("tooltip.carnis.research_journal", "A field guide to the hive.");
        add("item.carnis.tainted_sludge_bucket", "Tainted Sludge Bucket");
        add("item.carnis.bone_scythe_arm", "Bone Scythe Arm");
        add("block.carnis.tainted_sludge", "Tainted Sludge");
        add("fluid_type.carnis.tainted_sludge", "Tainted Sludge");
        add("tooltip.carnis.tainted_sludge_bucket", "A bucket of infectious sludge.");
        add("tooltip.carnis.bone_scythe_arm", "A jagged bone blade.");
        add("subtitles.carnis.amalgam_step", "Flesh Amalgam squelches");
        add("block.carnis.flesh_veins", "Flesh Veins");
        add("tooltip.carnis.flesh_veins", "Organic growth on exposed surfaces.");

        add("entity.carnis.infected_skeleton", "Infected Skeleton");
        add("item.carnis.infected_skeleton_spawn_egg", "Infected Skeleton Spawn Egg");
        add("tooltip.carnis.infected_skeleton_spawn_egg", "Spawns an infected skeleton.");
        add("entity.carnis.infected_creeper", "Infected Creeper");
        add("item.carnis.infected_creeper_spawn_egg", "Infected Creeper Spawn Egg");
        add("tooltip.carnis.infected_creeper_spawn_egg", "Spawns an infected creeper.");
        add("entity.carnis.infected_spider", "Infected Spider");
        add("item.carnis.infected_spider_spawn_egg", "Infected Spider Spawn Egg");
        add("tooltip.carnis.infected_spider_spawn_egg", "Spawns an infected spider.");
        add("item.carnis.neuro_resonator_chestplate", "Neuro-Resonator Chestplate");
        add("item.carnis.neuro_resonator_leggings", "Neuro-Resonator Leggings");
        add("item.carnis.neuro_resonator_boots", "Neuro-Resonator Boots");
        add("block.carnis.flesh_bulb", "Flesh Bulb");
        add("block.carnis.biomass_remains", "Biomass Remains");
        add("block.carnis.sinew_spikes", "Sinew Spikes");
        add("entity.carnis.biomass_maggot", "Biomass Maggot");
        add("item.carnis.biomass_maggot_spawn_egg", "Biomass Maggot Spawn Egg");
        add("item.carnis.neural_binding_matrix", "Neural Binding Matrix");
        add("tooltip.carnis.neuro_resonator_chestplate", "A biological chestplate reduces infection exposure.");
        add("tooltip.carnis.neuro_resonator_leggings", "Biological leggings reduce infection exposure.");
        add("tooltip.carnis.neuro_resonator_boots", "Biological boots reduce infection exposure.");
        add("tooltip.carnis.neural_binding_matrix", "Weave into armor at an anvil for five levels.");
        add("block.carnis.nerve_pillar", "Nerve Pillar");
        add("item.carnis.pneumatic_inoculator", "Pneumatic Inoculator");
        add("item.carnis.viral_dart", "Viral Dart");
        add("item.carnis.purification_dart", "Purification Dart");
        add("entity.carnis.viral_dart", "Viral Dart");
        add("entity.carnis.purification_dart", "Purification Dart");
        add("death.attack.carnis_tainted_sludge", "%1$s dissolved in tainted sludge");
        add("death.attack.purification_dart", "%1$s was purified by a dart");
        add("death.attack.purification_dart.player", "%1$s was purified by %2$s");
        add("tooltip.carnis.nerve_pillar", "Placement halves remaining shock time in this chunk.");
        add("tooltip.carnis.pneumatic_inoculator", "Right-click to fire a carried dart; 15-tick cooldown.");
        add("tooltip.carnis.viral_dart", "Adds 30 infection to players; poisons and slows mobs.");
        add("tooltip.carnis.purification_dart", "Removes 35 infection or damages Carnis mobs for 25.");
        add("tooltip.carnis.hold_shift", "Hold Shift for details");
        add("tooltip.carnis.living_flesh", "Living tissue spreads through nearby terrain.");
        add("tooltip.carnis.charred_flesh", "Burned tissue yields bone meal and charcoal.");
        add("tooltip.carnis.spore_sprout", "An organic sprout releases drifting spores.");
        add("tooltip.carnis.neural_moss", "A fleshy carpet impedes movement.");
        add("tooltip.carnis.creeping_tendrils", "Climb the tendrils attached to solid flesh.");
        add("tooltip.carnis.pustule_cluster", "Step on it without sneaking to burst infectious spores.");
        add("tooltip.carnis.stomach_pool", "Corrosive tissue dissolves items into biomass.");
        add("tooltip.carnis.ossified_flesh", "Hardened tissue spreads the hive.");
        add("tooltip.carnis.fireproof_flesh", "Adapted tissue resistant to flame.");
        add("tooltip.carnis.veins", "Living veins carry infection through wood.");
        add("tooltip.carnis.pulsing_heart", "The hive heart accelerates nearby infection.");
        add("tooltip.carnis.hive_eye", "Detects intruders and alerts nearby Amalgams.");
        add("tooltip.carnis.flesh_amalgam_spawn_egg", "Spawns a Flesh Amalgam.");
        add("tooltip.carnis.purification_serum", "Drink to remove 35 infection points.");
        add("effect.carnis.thermal_shock", "Thermal Shock");
        add("subtitles.carnis.purifier_ignite", "Purifier ignites");
        add("subtitles.carnis.purifier_loop", "Purifier fires");
        add("tooltip.carnis.bio_purifier", "Hold use: 6.5-block cone of flame.");
        add("tooltip.carnis.neuro_resonator_helmet", "Dampens hallucinations, reduces exposure by 25% and reveals nearby biomass.");
        add("itemGroup.carnis", "Carnis: Adaptive Hivemind");

        add("death.attack.necrotic_consumption", "%1$s was consumed by the hivemind");
        add(ModBlocks.CREEPING_TENDRILS.get(), "Creeping Tendrils");
        add(ModBlocks.PUSTULE_CLUSTER.get(), "Pustule Cluster");
        add(ModBlocks.STOMACH_POOL.get(), "Stomach Pool");
        add(ModBlocks.SPORE_SPROUT.get(), "Spore Sprout");
        add(ModBlocks.NEURAL_MOSS.get(), "Neural Moss");
        add(ModBlocks.CHARRED_FLESH.get(), "Charred Flesh");
        add(ModBlocks.LIVING_FLESH.get(), "Living Flesh");
        add(ModBlocks.OSSIFIED_FLESH.get(), "Ossified Flesh");
        add(ModBlocks.FIREPROOF_FLESH.get(), "Fireproof Flesh");
        add(ModBlocks.PULSING_HEART.get(), "Pulsing Heart");
        add(ModBlocks.HIVE_EYE.get(), "Hive Eye");
        add("entity.carnis.flesh_amalgam", "Flesh Amalgam");
        add(
                "item.carnis.flesh_amalgam_spawn_egg",
                "Flesh Amalgam Spawn Egg"
        );
        add(ModItems.PURIFICATION_SERUM.get(), "Purification Serum");
        add(ModItems.BIO_PURIFIER.get(), "Bio-Purifier");
        add(
                ModItems.NEURO_RESONATOR_HELMET.get(),
                "Neuro-Resonator Helmet"
        );
        add(
                "death.attack.bio_purifier",
                "%1$s was incinerated by a bio-purifier"
        );
        add(
                "death.attack.bio_purifier.player",
                "%1$s was incinerated by %2$s's bio-purifier"
        );

        add("subtitles.carnis.phantom_creeper", "Something hisses behind you");
        add("subtitles.carnis.phantom_footsteps", "Footsteps squelch through flesh");
        add("subtitles.carnis.phantom_whisper", "The hivemind whispers");
        add("subtitles.carnis.pulsing_heart_beat", "A biome heart beats");
        add("subtitles.carnis.synapse_shock", "A synapse discharges");
        add("subtitles.carnis.synapse_rupture", "Nerve tissue tears apart");
        add("subtitles.carnis.digestor_churn", "A digestor churns");
        add("subtitles.carnis.hive_eye_screech", "The hive eye shrieks");
        add(
                "subtitles.carnis.amalgamation_fuse",
                "Flesh fuses into an amalgam"
        );
        add(
                "subtitles.carnis.bone_deflect",
                "A projectile ricochets off bone"
        );
        add(
                "subtitles.carnis.acid_splash",
                "Corrosive acid splashes"
        );
        add(
                "subtitles.carnis.flesh_amalgam_ambient",
                "The Flesh Amalgam groans"
        );
        add(
                "subtitles.carnis.flesh_amalgam_hurt",
                "The Flesh Amalgam recoils"
        );
        add(
                "subtitles.carnis.flesh_amalgam_death",
                "The Flesh Amalgam collapses"
        );
    }

    private void addRussianTranslations() {
        add("entity.carnis.hive_sentinel", "Страж Улья");
        add("entity.carnis.cerebral_nexus", "Мозговой узел");
        add("subtitles.carnis.inoculator_fire", "Выстрел инокулятора");
        add("subtitles.carnis.dart_hit", "Дротик ударяется");
        add("tooltip.carnis.flesh_bulb.mechanics", "Инкубационный мешок, способный закрепляться на потолке и полу.");
        add("tooltip.carnis.flesh_bulb.lore", "Внутри слышно глухое, частое сердцебиение зреющего выводка.");
        add("tooltip.carnis.sinew_spikes.mechanics", "Наносят колющий урон и замедляют любое наступившее существо.");
        add("tooltip.carnis.sinew_spikes.lore", "Натянутые жилы реагируют на малейшую вибрацию шагов.");
        add("tooltip.carnis.biomass_maggot.mechanics", "Ненасытный трупоед. Пожирает органические останки и окукливается в почве.");
        add("tooltip.carnis.biomass_maggot.lore", "Начальное звено паразитического круговорота Улья.");
        add("item.carnis.infected_zombie_spawn_egg", "Яйцо призыва заражённого зомби");
        add("entity.carnis.infected_zombie", "Заражённый зомби");
        add("tooltip.carnis.infected_zombie_spawn_egg", "Призывает заражённого зомби.");
        add("item.carnis.antibiotics", "Антибиотики");
        add("effect.carnis.immunosuppression", "Иммуносупрессия");
        add("tooltip.carnis.antibiotics", "Предотвращает заражение на 3 минуты.");
        add("entity.carnis.parasitic_tendril", "Паразитический усик");
        add("effect.carnis.incubating", "Инкубация");
        add("subtitles.carnis.flamethrower_fire", "Огнемёт ревёт");
        add("subtitles.carnis.amalgam_roar", "Амальгама ревёт");
        add("codex.carnis.chapter.0", "Истоки и биомы");
        add("codex.carnis.body.0", "Вены растут по поддерживаемым граням; неполные грани могут мешать росту. Жижа заражает игроков и реагирует с водой и лавой. Распространение обрабатывается очередью.");
        add("codex.carnis.chapter.1", "Адаптивный разум");
        add("codex.carnis.body.1", "ОГОНЬ / ДАЛЬНИЙ / БЛИЖНИЙ / ВЗРЫВ: общая логарифмическая кривая. Очки: 0 / 100 / 300 / 600 / 1000. Снижение: 0% / 25% / 50% / 70% / 80%. Между порогами — интерполяция по ln(1+очки). Предел 80%.");
        add("codex.carnis.chapter.2", "Органы и флора улья");
        add("codex.carnis.body.2", "Глаз видит игроков в 24 блоках и предупреждает связанных мобов в 32. Установка нервного столба вдвое сокращает оставшийся шок чанка. Желудочный бассейн даёт 5 биомассы за мясо или плоть, 1 за иной предмет; живым наносит 4 урона в секунду.");
        add("codex.carnis.chapter.3", "Медицина и нейроплетение");
        add("codex.carnis.body.3", "Сыворотка снижает заражение на 35. Антибиотики блокируют положительную экспозицию на 3600 тиков. На наковальне соедините броню с одной матрицей за 5 уровней. Каждая защищённая часть снижает экспозицию на 25%, четыре — на 100%.");
        add("codex.carnis.chapter.4", "Мутанты и слияние");
        add("codex.carnis.body.4", "Зомби: 35 здоровья, 4,5 урона; скелет: 28 и 4,5; крипер: 24 здоровья; паук: 20 и 3. Плевок: 2 урона, замедление II на 100 тиков и +5 экспозиции при успешном уроне. Три зомби у сердца при 300 биомассы могут слиться.");
        add("entity.carnis.flesh_spat", "Плевок плоти");
        add("item.carnis.flesh_spat", "Плевок плоти");
        add("tooltip.carnis.flesh_spat", "Сгусток заражённой ткани.");
        add("subtitles.carnis.heartbeat_loop", "Сердце бьётся");
        add("item.carnis.research_journal", "Кодекс Карнис");
        add("tooltip.carnis.research_journal", "Полевой справочник по улью.");
        add("item.carnis.tainted_sludge_bucket", "Ведро заражённой слизи");
        add("item.carnis.bone_scythe_arm", "Костяная коса-рука");
        add("block.carnis.tainted_sludge", "Заражённая слизь");
        add("fluid_type.carnis.tainted_sludge", "Заражённая слизь");
        add("tooltip.carnis.tainted_sludge_bucket", "Ведро заразной слизи.");
        add("tooltip.carnis.bone_scythe_arm", "Зазубренный костяной клинок.");
        add("subtitles.carnis.amalgam_step", "Плотяная амальгама чавкает");
        add("block.carnis.flesh_veins", "Плотяные жилы");
        add("tooltip.carnis.flesh_veins", "Органические жилы на открытых поверхностях.");

        add("entity.carnis.infected_skeleton", "Заражённый скелет");
        add("item.carnis.infected_skeleton_spawn_egg", "Яйцо призыва: Заражённый скелет");
        add("tooltip.carnis.infected_skeleton_spawn_egg", "Призывает заражённого скелета.");
        add("entity.carnis.infected_creeper", "Заражённый крипер");
        add("item.carnis.infected_creeper_spawn_egg", "Яйцо призыва: Заражённый крипер");
        add("tooltip.carnis.infected_creeper_spawn_egg", "Призывает заражённого крипера.");
        add("entity.carnis.infected_spider", "Заражённый паук");
        add("item.carnis.infected_spider_spawn_egg", "Яйцо призыва: Заражённый паук");
        add("tooltip.carnis.infected_spider_spawn_egg", "Призывает заражённого паука.");
        add("item.carnis.neuro_resonator_chestplate", "Нейро-резонаторный нагрудник");
        add("item.carnis.neuro_resonator_leggings", "Нейро-резонаторные поножи");
        add("item.carnis.neuro_resonator_boots", "Нейро-резонаторные ботинки");
        add("block.carnis.flesh_bulb", "Мясная луковица");
        add("block.carnis.biomass_remains", "Останки биомассы");
        add("block.carnis.sinew_spikes", "Сухожильные шипы");
        add("entity.carnis.biomass_maggot", "Личинка биомассы");
        add("item.carnis.biomass_maggot_spawn_egg", "Яйцо призыва: Личинка биомассы");
        add("item.carnis.neural_binding_matrix", "Матрица нейронного сплетения");
        add("tooltip.carnis.neuro_resonator_chestplate", "Биологический нагрудник снижает заражение.");
        add("tooltip.carnis.neuro_resonator_leggings", "Биологические поножи снижают заражение.");
        add("tooltip.carnis.neuro_resonator_boots", "Биологические ботинки снижают заражение.");
        add("tooltip.carnis.neural_binding_matrix", "Вплетите в броню на наковальне за пять уровней.");
        add("block.carnis.nerve_pillar", "Нервный столп");
        add("item.carnis.pneumatic_inoculator", "Пневматический инокулятор");
        add("item.carnis.viral_dart", "Вирусный дротик");
        add("item.carnis.purification_dart", "Очищающий дротик");
        add("entity.carnis.viral_dart", "Вирусный дротик");
        add("entity.carnis.purification_dart", "Очищающий дротик");
        add("death.attack.carnis_tainted_sludge", "%1$s растворился в заражённой жиже");
        add("death.attack.purification_dart", "%1$s очищен дротиком");
        add("death.attack.purification_dart.player", "%1$s очищен игроком %2$s");
        add("tooltip.carnis.nerve_pillar", "При установке вдвое сокращает оставшийся шок чанка.");
        add("tooltip.carnis.pneumatic_inoculator", "ПКМ: выстрел дротиком из инвентаря; задержка 15 тиков.");
        add("tooltip.carnis.viral_dart", "Добавляет игрокам 30 заражения; травит и замедляет мобов.");
        add("tooltip.carnis.purification_dart", "Снимает 35 заражения или наносит мобам Carnis 25 урона.");
        add("tooltip.carnis.hold_shift", "Удерживайте Shift для подробностей");
        add("tooltip.carnis.living_flesh", "Живая ткань распространяется по окружающим блокам.");
        add("tooltip.carnis.charred_flesh", "Обгоревшая ткань даёт костную муку и уголь.");
        add("tooltip.carnis.spore_sprout", "Органический росток выпускает споры.");
        add("tooltip.carnis.neural_moss", "Мясистый мох замедляет движение.");
        add("tooltip.carnis.creeping_tendrils", "Взбирайтесь по усикам на поверхности плоти.");
        add("tooltip.carnis.pustule_cluster", "Наступите без приседания: пустулы лопнут и заразят вас.");
        add("tooltip.carnis.stomach_pool", "Едкая ткань растворяет предметы в биомассу.");
        add("tooltip.carnis.ossified_flesh", "Окостеневшая ткань распространяет улей.");
        add("tooltip.carnis.fireproof_flesh", "Ткань, приспособленная к огню.");
        add("tooltip.carnis.veins", "Живые вены несут инфекцию через древесину.");
        add("tooltip.carnis.pulsing_heart", "Сердце улья ускоряет заражение поблизости.");
        add("tooltip.carnis.hive_eye", "Обнаруживает чужаков и тревожит ближайших амальгам.");
        add("tooltip.carnis.flesh_amalgam_spawn_egg", "Призывает амальгаму плоти.");
        add("tooltip.carnis.purification_serum", "Выпейте, чтобы снизить заражение на 35 пунктов.");
        add("effect.carnis.thermal_shock", "Термический шок");
        add("subtitles.carnis.purifier_ignite", "Очиститель зажигается");
        add("subtitles.carnis.purifier_loop", "Очиститель выпускает пламя");
        add("tooltip.carnis.bio_purifier", "Удерживайте: конус пламени на 6,5 блока.");
        add("tooltip.carnis.neuro_resonator_helmet", "Подавляет галлюцинации, снижает экспозицию на 25% и обнаруживает биомассу.");
        add("itemGroup.carnis", "Carnis: Адаптивный коллективный разум");

        add("death.attack.necrotic_consumption", "%1$s поглощён коллективным разумом");
        add(ModBlocks.CREEPING_TENDRILS.get(), "Ползучие щупальца");
        add(ModBlocks.PUSTULE_CLUSTER.get(), "Скопление пустул");
        add(ModBlocks.STOMACH_POOL.get(), "Желудочный бассейн");
        add(ModBlocks.SPORE_SPROUT.get(), "Споровый росток");
        add(ModBlocks.NEURAL_MOSS.get(), "Нервный мох");
        add(ModBlocks.CHARRED_FLESH.get(), "Обугленная плоть");
        add(ModBlocks.LIVING_FLESH.get(), "Живая плоть");
        add(ModBlocks.OSSIFIED_FLESH.get(), "Окостенелая плоть");
        add(ModBlocks.FIREPROOF_FLESH.get(), "Огнеупорная плоть");
        add(ModBlocks.PULSING_HEART.get(), "Сердце биома");
        add(ModBlocks.HIVE_EYE.get(), "Око разума");
        add("entity.carnis.flesh_amalgam", "Амальгама плоти");
        add(
                "item.carnis.flesh_amalgam_spawn_egg",
                "Яйцо призыва амальгамы плоти"
        );
        add(ModItems.PURIFICATION_SERUM.get(), "Очищающая сыворотка");
        add(ModItems.BIO_PURIFIER.get(), "Очищающий огнемёт");
        add(
                ModItems.NEURO_RESONATOR_HELMET.get(),
                "Нейро-резонаторный шлем"
        );
        add(
                "death.attack.bio_purifier",
                "%1$s сожжён биоочистителем"
        );
        add(
                "death.attack.bio_purifier.player",
                "%1$s сожжён биоочистителем игрока %2$s"
        );

        add("subtitles.carnis.phantom_creeper", "Что-то шипит за спиной");
        add("subtitles.carnis.phantom_footsteps", "Шаги хлюпают по плоти");
        add("subtitles.carnis.phantom_whisper", "Коллективный разум шепчет");
        add("subtitles.carnis.pulsing_heart_beat", "Сердце биома бьётся");
        add("subtitles.carnis.synapse_shock", "Нервный столб разряжается");
        add("subtitles.carnis.synapse_rupture", "Нервная ткань разрывается");
        add("subtitles.carnis.digestor_churn", "Желудочный пруд бурлит");
        add("subtitles.carnis.hive_eye_screech", "Око разума визжит");
        add(
                "subtitles.carnis.amalgamation_fuse",
                "Плоть сливается в амальгаму"
        );
        add(
                "subtitles.carnis.bone_deflect",
                "Снаряд рикошетит от кости"
        );
        add(
                "subtitles.carnis.acid_splash",
                "Едкая кислота брызжет"
        );
        add(
                "subtitles.carnis.flesh_amalgam_ambient",
                "Амальгама плоти стонет"
        );
        add(
                "subtitles.carnis.flesh_amalgam_hurt",
                "Амальгама плоти вздрагивает"
        );
        add(
                "subtitles.carnis.flesh_amalgam_death",
                "Амальгама плоти обрушивается"
        );
    }
}
```

## `src/main/resources/assets/carnis/geo/item/neuro_armor.geo.json`

```json
{
  "format_version": "1.12.0",
  "minecraft:geometry": [
    {
      "description": {
        "identifier": "geometry.carnis.neuro_armor",
        "texture_width": 128,
        "texture_height": 128,
        "visible_bounds_width": 3,
        "visible_bounds_height": 3,
        "visible_bounds_offset": [
          0,
          1,
          0
        ]
      },
      "bones": [
        {
          "name": "head",
          "pivot": [
            0,
            24,
            0
          ],
          "cubes": [
            {
              "origin": [
                -4.5,
                23.5,
                -4.5
              ],
              "size": [
                9,
                9,
                9
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4,
                23,
                -6
              ],
              "size": [
                3,
                3,
                2
              ],
              "uv": [
                48,
                0
              ]
            },
            {
              "origin": [
                1,
                23,
                -6
              ],
              "size": [
                3,
                3,
                2
              ],
              "uv": [
                48,
                0
              ]
            }
          ]
        },
        {
          "name": "body",
          "pivot": [
            0,
            24,
            0
          ],
          "cubes": [
            {
              "origin": [
                -4.5,
                11.5,
                -2.5
              ],
              "size": [
                9,
                12.5,
                5
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -3,
                14,
                2.5
              ],
              "size": [
                6,
                8,
                4
              ],
              "uv": [
                48,
                0
              ]
            },
            {
              "origin": [
                -1,
                13,
                6.5
              ],
              "size": [
                2,
                9,
                1
              ],
              "uv": [
                48,
                48
              ]
            }
          ]
        },
        {
          "name": "right_arm",
          "pivot": [
            -5,
            22,
            0
          ],
          "cubes": [
            {
              "origin": [
                -8.7,
                18,
                -2.7
              ],
              "size": [
                5,
                5,
                5
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -8.4,
                10,
                -2.4
              ],
              "size": [
                4.8,
                8,
                4.8
              ],
              "uv": [
                0,
                0
              ]
            }
          ]
        },
        {
          "name": "left_arm",
          "pivot": [
            5,
            22,
            0
          ],
          "cubes": [
            {
              "origin": [
                3.7,
                18,
                -2.7
              ],
              "size": [
                5,
                5,
                5
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                3.6,
                10,
                -2.4
              ],
              "size": [
                4.8,
                8,
                4.8
              ],
              "uv": [
                0,
                0
              ]
            }
          ]
        },
        {
          "name": "right_leg",
          "pivot": [
            -2,
            12,
            0
          ],
          "cubes": [
            {
              "origin": [
                -4.4,
                3,
                -2.4
              ],
              "size": [
                4.8,
                9,
                4.8
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4.6,
                4,
                -3
              ],
              "size": [
                5,
                3,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -5,
                6,
                -1
              ],
              "size": [
                1,
                6,
                2
              ],
              "uv": [
                48,
                48
              ]
            }
          ]
        },
        {
          "name": "left_leg",
          "pivot": [
            2,
            12,
            0
          ],
          "cubes": [
            {
              "origin": [
                -0.4,
                3,
                -2.4
              ],
              "size": [
                4.8,
                9,
                4.8
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -0.4,
                4,
                -3
              ],
              "size": [
                5,
                3,
                1
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                4,
                6,
                -1
              ],
              "size": [
                1,
                6,
                2
              ],
              "uv": [
                48,
                48
              ]
            }
          ]
        },
        {
          "name": "right_boot",
          "pivot": [
            -2,
            12,
            0
          ],
          "cubes": [
            {
              "origin": [
                -4.5,
                0,
                -2.5
              ],
              "size": [
                5,
                5,
                5
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -4.7,
                0,
                -3.4
              ],
              "size": [
                5.4,
                1.5,
                6
              ],
              "uv": [
                48,
                0
              ]
            }
          ]
        },
        {
          "name": "left_boot",
          "pivot": [
            2,
            12,
            0
          ],
          "cubes": [
            {
              "origin": [
                -0.5,
                0,
                -2.5
              ],
              "size": [
                5,
                5,
                5
              ],
              "uv": [
                0,
                0
              ]
            },
            {
              "origin": [
                -0.7,
                0,
                -3.4
              ],
              "size": [
                5.4,
                1.5,
                6
              ],
              "uv": [
                48,
                0
              ]
            }
          ]
        },
        {
          "name": "visor_strip",
          "parent": "head",
          "pivot": [
            0,
            24,
            0
          ],
          "cubes": [
            {
              "origin": [
                -4,
                25,
                -5
              ],
              "size": [
                8,
                3,
                1
              ],
              "uv": [
                80,
                0
              ]
            }
          ]
        },
        {
          "name": "right_arm_detail",
          "parent": "right_arm",
          "pivot": [
            -5,
            22,
            0
          ],
          "cubes": [
            {
              "origin": [
                -9.8,
                22,
                -3.3
              ],
              "size": [
                6.2,
                2,
                6.6
              ],
              "uv": [
                48,
                16
              ]
            },
            {
              "origin": [
                -10.5,
                19.5,
                -2.8
              ],
              "size": [
                2.7,
                3,
                5.6
              ],
              "uv": [
                48,
                28
              ]
            },
            {
              "origin": [
                -9.8,
                21,
                -3.5
              ],
              "size": [
                6.2,
                1,
                1
              ],
              "uv": [
                48,
                40
              ]
            }
          ]
        },
        {
          "name": "left_arm_detail",
          "parent": "left_arm",
          "pivot": [
            5,
            22,
            0
          ],
          "cubes": [
            {
              "origin": [
                3.6,
                22,
                -3.3
              ],
              "size": [
                6.2,
                2,
                6.6
              ],
              "uv": [
                48,
                16
              ]
            },
            {
              "origin": [
                7.8,
                19.5,
                -2.8
              ],
              "size": [
                2.7,
                3,
                5.6
              ],
              "uv": [
                48,
                28
              ]
            },
            {
              "origin": [
                3.6,
                21,
                -3.5
              ],
              "size": [
                6.2,
                1,
                1
              ],
              "uv": [
                48,
                40
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## `src/main/resources/assets/carnis/animations/armor/neuro_armor.animation.json`

```json
{
  "format_version": "1.8.0",
  "animations": {}
}
```

## `src/generated/resources/assets/carnis/lang/en_us.json`

```json
{
  "block.carnis.charred_flesh": "Charred Flesh",
  "block.carnis.creeping_tendrils": "Creeping Tendrils",
  "block.carnis.fireproof_flesh": "Fireproof Flesh",
  "block.carnis.flesh_bulb": "Flesh Bulb",
  "block.carnis.flesh_veins": "Flesh Veins",
  "block.carnis.hive_eye": "Hive Eye",
  "block.carnis.living_flesh": "Living Flesh",
  "block.carnis.nerve_pillar": "Nerve Pillar",
  "block.carnis.neural_moss": "Neural Moss",
  "block.carnis.ossified_flesh": "Ossified Flesh",
  "block.carnis.pulsing_heart": "Pulsing Heart",
  "block.carnis.pustule_cluster": "Pustule Cluster",
  "block.carnis.sinew_spikes": "Sinew Spikes",
  "block.carnis.spore_sprout": "Spore Sprout",
  "block.carnis.stomach_pool": "Stomach Pool",
  "block.carnis.tainted_sludge": "Tainted Sludge",
  "codex.carnis.body.0": "Veins spread across supported faces; incomplete faces may resist growth. Sludge contaminates players and reacts with water and lava. Infection spreads by a queued process.",
  "codex.carnis.body.1": "FIRE / RANGED / MELEE / EXPLOSIVE use the same logarithmic mitigation curve. Points: 0 / 100 / 300 / 600 / 1000. Reduction: 0% / 25% / 50% / 70% / 80%. Between thresholds: linear interpolation in ln(1+points). Cap 80%.",
  "codex.carnis.body.2": "Hive Eye detects players within 24 blocks and alerts linked mobs within 32. Placing a Nerve Pillar halves remaining chunk shock. Stomach Pool dissolves items: flesh or meat gives 5 biomass each; other items give 1. Living creatures take 4 damage per second.",
  "codex.carnis.body.3": "Serum reduces infection by 35. Antibiotics block positive exposure for 3600 ticks. On an anvil, combine armor and one neural binding matrix for 5 levels. Each woven or resonator armor piece reduces exposure by 25%; four pieces reach 100%.",
  "codex.carnis.body.4": "Zombie: 35 health, 4.5 attack; skeleton: 28 health, 4.5 attack; creeper: 24 health; spider: 20 health, 3 attack. Spat: 2 damage, Slowness II for 100 ticks and +5 exposure on successful damage. Three zombies near a heart at 300 biomass can fuse.",
  "codex.carnis.chapter.0": "Inception & Biomes",
  "codex.carnis.chapter.1": "Adaptive Hivemind",
  "codex.carnis.chapter.2": "Hive Organs & Flora",
  "codex.carnis.chapter.3": "Medical & Armor Weaving",
  "codex.carnis.chapter.4": "Mutants & Amalgamation",
  "death.attack.bio_purifier": "%1$s was incinerated by a bio-purifier",
  "death.attack.bio_purifier.player": "%1$s was incinerated by %2$s's bio-purifier",
  "death.attack.carnis_tainted_sludge": "%1$s dissolved in tainted sludge",
  "death.attack.necrotic_consumption": "%1$s was consumed by the hivemind",
  "death.attack.purification_dart": "%1$s was purified by a dart",
  "death.attack.purification_dart.player": "%1$s was purified by %2$s",
  "effect.carnis.immunosuppression": "Immunosuppression",
  "effect.carnis.incubating": "Incubating",
  "entity.carnis.biomass_maggot": "Biomass Maggot",
  "entity.carnis.flesh_amalgam": "Flesh Amalgam",
  "entity.carnis.flesh_spat": "Flesh Spat",
  "entity.carnis.infected_creeper": "Infected Creeper",
  "entity.carnis.infected_skeleton": "Infected Skeleton",
  "entity.carnis.infected_spider": "Infected Spider",
  "entity.carnis.infected_zombie": "Infected Zombie",
  "entity.carnis.parasitic_tendril": "Parasitic Tendril",
  "entity.carnis.purification_dart": "Purification Dart",
  "entity.carnis.viral_dart": "Viral Dart",
  "fluid_type.carnis.tainted_sludge": "Tainted Sludge",
  "item.carnis.antibiotics": "Antibiotics",
  "item.carnis.bio_purifier": "Bio-Purifier",
  "item.carnis.biomass_maggot_spawn_egg": "Biomass Maggot Spawn Egg",
  "item.carnis.bone_scythe_arm": "Bone Scythe Arm",
  "item.carnis.flesh_amalgam_spawn_egg": "Flesh Amalgam Spawn Egg",
  "item.carnis.flesh_spat": "Flesh Spat",
  "item.carnis.infected_creeper_spawn_egg": "Infected Creeper Spawn Egg",
  "item.carnis.infected_skeleton_spawn_egg": "Infected Skeleton Spawn Egg",
  "item.carnis.infected_spider_spawn_egg": "Infected Spider Spawn Egg",
  "item.carnis.infected_zombie_spawn_egg": "Infected Zombie Spawn Egg",
  "item.carnis.neural_binding_matrix": "Neural Binding Matrix",
  "item.carnis.neuro_resonator_boots": "Neuro-Resonator Boots",
  "item.carnis.neuro_resonator_chestplate": "Neuro-Resonator Chestplate",
  "item.carnis.neuro_resonator_helmet": "Neuro-Resonator Helmet",
  "item.carnis.neuro_resonator_leggings": "Neuro-Resonator Leggings",
  "item.carnis.pneumatic_inoculator": "Pneumatic Inoculator",
  "item.carnis.purification_dart": "Purification Dart",
  "item.carnis.purification_serum": "Purification Serum",
  "item.carnis.research_journal": "Codex Carnis",
  "item.carnis.tainted_sludge_bucket": "Tainted Sludge Bucket",
  "item.carnis.viral_dart": "Viral Dart",
  "itemGroup.carnis": "Carnis: Adaptive Hivemind",
  "subtitles.carnis.acid_splash": "Corrosive acid splashes",
  "subtitles.carnis.amalgam_roar": "Amalgam roars",
  "subtitles.carnis.amalgam_step": "Flesh Amalgam squelches",
  "subtitles.carnis.amalgamation_fuse": "Flesh fuses into an amalgam",
  "subtitles.carnis.bone_deflect": "A projectile ricochets off bone",
  "subtitles.carnis.digestor_churn": "A digestor churns",
  "subtitles.carnis.flamethrower_fire": "Flamethrower roars",
  "subtitles.carnis.flesh_amalgam_ambient": "The Flesh Amalgam groans",
  "subtitles.carnis.flesh_amalgam_death": "The Flesh Amalgam collapses",
  "subtitles.carnis.flesh_amalgam_hurt": "The Flesh Amalgam recoils",
  "subtitles.carnis.heartbeat_loop": "Heart beats",
  "subtitles.carnis.hive_eye_screech": "The hive eye shrieks",
  "subtitles.carnis.phantom_creeper": "Something hisses behind you",
  "subtitles.carnis.phantom_footsteps": "Footsteps squelch through flesh",
  "subtitles.carnis.phantom_whisper": "The hivemind whispers",
  "subtitles.carnis.pulsing_heart_beat": "A biome heart beats",
  "subtitles.carnis.synapse_rupture": "Nerve tissue tears apart",
  "subtitles.carnis.synapse_shock": "A synapse discharges",
  "tooltip.carnis.antibiotics": "Prevents exposure for 3 minutes.",
  "tooltip.carnis.bio_purifier": "Hold use: 6.5-block cone of flame.",
  "tooltip.carnis.bone_scythe_arm": "A jagged bone blade.",
  "tooltip.carnis.charred_flesh": "Burned tissue yields bone meal and charcoal.",
  "tooltip.carnis.creeping_tendrils": "Climb the tendrils attached to solid flesh.",
  "tooltip.carnis.fireproof_flesh": "Adapted tissue resistant to flame.",
  "tooltip.carnis.flesh_amalgam_spawn_egg": "Spawns a Flesh Amalgam.",
  "tooltip.carnis.flesh_spat": "A glob of infectious tissue.",
  "tooltip.carnis.flesh_veins": "Organic growth on exposed surfaces.",
  "tooltip.carnis.hive_eye": "Detects intruders and alerts nearby Amalgams.",
  "tooltip.carnis.hold_shift": "Hold Shift for details",
  "tooltip.carnis.infected_creeper_spawn_egg": "Spawns an infected creeper.",
  "tooltip.carnis.infected_skeleton_spawn_egg": "Spawns an infected skeleton.",
  "tooltip.carnis.infected_spider_spawn_egg": "Spawns an infected spider.",
  "tooltip.carnis.infected_zombie_spawn_egg": "Spawns an infected zombie.",
  "tooltip.carnis.living_flesh": "Living tissue spreads through nearby terrain.",
  "tooltip.carnis.nerve_pillar": "Placement halves remaining shock time in this chunk.",
  "tooltip.carnis.neural_binding_matrix": "Weave into armor at an anvil for five levels.",
  "tooltip.carnis.neural_moss": "A fleshy carpet impedes movement.",
  "tooltip.carnis.neuro_resonator_boots": "Biological boots reduce infection exposure.",
  "tooltip.carnis.neuro_resonator_chestplate": "A biological chestplate reduces infection exposure.",
  "tooltip.carnis.neuro_resonator_helmet": "Dampens hallucinations, reduces exposure by 25% and reveals nearby biomass.",
  "tooltip.carnis.neuro_resonator_leggings": "Biological leggings reduce infection exposure.",
  "tooltip.carnis.ossified_flesh": "Hardened tissue spreads the hive.",
  "tooltip.carnis.pneumatic_inoculator": "Right-click to fire a carried dart; 15-tick cooldown.",
  "tooltip.carnis.pulsing_heart": "The hive heart accelerates nearby infection.",
  "tooltip.carnis.purification_dart": "Removes 35 infection or damages Carnis mobs for 25.",
  "tooltip.carnis.purification_serum": "Drink to remove 35 infection points.",
  "tooltip.carnis.pustule_cluster": "Step on it without sneaking to burst infectious spores.",
  "tooltip.carnis.research_journal": "A field guide to the hive.",
  "tooltip.carnis.spore_sprout": "An organic sprout releases drifting spores.",
  "tooltip.carnis.stomach_pool": "Corrosive tissue dissolves items into biomass.",
  "tooltip.carnis.tainted_sludge_bucket": "A bucket of infectious sludge.",
  "tooltip.carnis.veins": "Living veins carry infection through wood.",
  "tooltip.carnis.viral_dart": "Adds 30 infection to players; poisons and slows mobs.",
  "tooltip.carnis.flesh_bulb.mechanics": "An incubation sac that can attach to ceilings and floors.",
  "tooltip.carnis.flesh_bulb.lore": "The muffled, rapid heartbeat of a maturing brood can be heard inside.",
  "tooltip.carnis.sinew_spikes.mechanics": "Deals piercing damage and slows any creature that steps on it.",
  "tooltip.carnis.sinew_spikes.lore": "Taut sinews respond to the slightest vibration of footsteps.",
  "tooltip.carnis.biomass_maggot.mechanics": "A voracious scavenger. Devours organic remains and pupates in soil.",
  "tooltip.carnis.biomass_maggot.lore": "The first link in the Hive’s parasitic cycle.",
  "subtitles.carnis.inoculator_fire": "Inoculator fires",
  "subtitles.carnis.dart_hit": "Dart hits",
  "block.carnis.biomass_remains": "Biomass Remains",
  "entity.carnis.hive_sentinel": "Hive Sentinel",
  "entity.carnis.cerebral_nexus": "Cerebral Nexus",
  "effect.carnis.thermal_shock": "Thermal Shock",
  "subtitles.carnis.purifier_ignite": "Purifier ignites",
  "subtitles.carnis.purifier_loop": "Purifier fires"
}
```

## `src/generated/resources/assets/carnis/lang/ru_ru.json`

```json
{
  "block.carnis.charred_flesh": "Обугленная плоть",
  "block.carnis.creeping_tendrils": "Ползучие щупальца",
  "block.carnis.fireproof_flesh": "Огнеупорная плоть",
  "block.carnis.flesh_bulb": "Мясная луковица",
  "block.carnis.flesh_veins": "Плотяные жилы",
  "block.carnis.hive_eye": "Око разума",
  "block.carnis.living_flesh": "Живая плоть",
  "block.carnis.nerve_pillar": "Нервный столп",
  "block.carnis.neural_moss": "Нервный мох",
  "block.carnis.ossified_flesh": "Окостенелая плоть",
  "block.carnis.pulsing_heart": "Сердце биома",
  "block.carnis.pustule_cluster": "Скопление пустул",
  "block.carnis.sinew_spikes": "Сухожильные шипы",
  "block.carnis.spore_sprout": "Споровый росток",
  "block.carnis.stomach_pool": "Желудочный бассейн",
  "block.carnis.tainted_sludge": "Заражённая слизь",
  "codex.carnis.body.0": "Вены растут по поддерживаемым граням; неполные грани могут мешать росту. Жижа заражает игроков и реагирует с водой и лавой. Распространение обрабатывается очередью.",
  "codex.carnis.body.1": "ОГОНЬ / ДАЛЬНИЙ / БЛИЖНИЙ / ВЗРЫВ: общая логарифмическая кривая. Очки: 0 / 100 / 300 / 600 / 1000. Снижение: 0% / 25% / 50% / 70% / 80%. Между порогами — интерполяция по ln(1+очки). Предел 80%.",
  "codex.carnis.body.2": "Глаз видит игроков в 24 блоках и предупреждает связанных мобов в 32. Установка нервного столба вдвое сокращает оставшийся шок чанка. Желудочный бассейн даёт 5 биомассы за мясо или плоть, 1 за иной предмет; живым наносит 4 урона в секунду.",
  "codex.carnis.body.3": "Сыворотка снижает заражение на 35. Антибиотики блокируют положительную экспозицию на 3600 тиков. На наковальне соедините броню с одной матрицей за 5 уровней. Каждая защищённая часть снижает экспозицию на 25%, четыре — на 100%.",
  "codex.carnis.body.4": "Зомби: 35 здоровья, 4,5 урона; скелет: 28 и 4,5; крипер: 24 здоровья; паук: 20 и 3. Плевок: 2 урона, замедление II на 100 тиков и +5 экспозиции при успешном уроне. Три зомби у сердца при 300 биомассы могут слиться.",
  "codex.carnis.chapter.0": "Истоки и биомы",
  "codex.carnis.chapter.1": "Адаптивный разум",
  "codex.carnis.chapter.2": "Органы и флора улья",
  "codex.carnis.chapter.3": "Медицина и нейроплетение",
  "codex.carnis.chapter.4": "Мутанты и слияние",
  "death.attack.bio_purifier": "%1$s сожжён биоочистителем",
  "death.attack.bio_purifier.player": "%1$s сожжён биоочистителем игрока %2$s",
  "death.attack.carnis_tainted_sludge": "%1$s растворился в заражённой жиже",
  "death.attack.necrotic_consumption": "%1$s поглощён коллективным разумом",
  "death.attack.purification_dart": "%1$s очищен дротиком",
  "death.attack.purification_dart.player": "%1$s очищен игроком %2$s",
  "effect.carnis.immunosuppression": "Иммуносупрессия",
  "effect.carnis.incubating": "Инкубация",
  "entity.carnis.biomass_maggot": "Личинка биомассы",
  "entity.carnis.flesh_amalgam": "Амальгама плоти",
  "entity.carnis.flesh_spat": "Плевок плоти",
  "entity.carnis.infected_creeper": "Заражённый крипер",
  "entity.carnis.infected_skeleton": "Заражённый скелет",
  "entity.carnis.infected_spider": "Заражённый паук",
  "entity.carnis.infected_zombie": "Заражённый зомби",
  "entity.carnis.parasitic_tendril": "Паразитический усик",
  "entity.carnis.purification_dart": "Очищающий дротик",
  "entity.carnis.viral_dart": "Вирусный дротик",
  "fluid_type.carnis.tainted_sludge": "Заражённая слизь",
  "item.carnis.antibiotics": "Антибиотики",
  "item.carnis.bio_purifier": "Очищающий огнемёт",
  "item.carnis.biomass_maggot_spawn_egg": "Яйцо призыва: Личинка биомассы",
  "item.carnis.bone_scythe_arm": "Костяная коса-рука",
  "item.carnis.flesh_amalgam_spawn_egg": "Яйцо призыва амальгамы плоти",
  "item.carnis.flesh_spat": "Плевок плоти",
  "item.carnis.infected_creeper_spawn_egg": "Яйцо призыва: Заражённый крипер",
  "item.carnis.infected_skeleton_spawn_egg": "Яйцо призыва: Заражённый скелет",
  "item.carnis.infected_spider_spawn_egg": "Яйцо призыва: Заражённый паук",
  "item.carnis.infected_zombie_spawn_egg": "Яйцо призыва заражённого зомби",
  "item.carnis.neural_binding_matrix": "Матрица нейронного сплетения",
  "item.carnis.neuro_resonator_boots": "Нейро-резонаторные ботинки",
  "item.carnis.neuro_resonator_chestplate": "Нейро-резонаторный нагрудник",
  "item.carnis.neuro_resonator_helmet": "Нейро-резонаторный шлем",
  "item.carnis.neuro_resonator_leggings": "Нейро-резонаторные поножи",
  "item.carnis.pneumatic_inoculator": "Пневматический инокулятор",
  "item.carnis.purification_dart": "Очищающий дротик",
  "item.carnis.purification_serum": "Очищающая сыворотка",
  "item.carnis.research_journal": "Кодекс Карнис",
  "item.carnis.tainted_sludge_bucket": "Ведро заражённой слизи",
  "item.carnis.viral_dart": "Вирусный дротик",
  "itemGroup.carnis": "Carnis: Адаптивный коллективный разум",
  "subtitles.carnis.acid_splash": "Едкая кислота брызжет",
  "subtitles.carnis.amalgam_roar": "Амальгама ревёт",
  "subtitles.carnis.amalgam_step": "Плотяная амальгама чавкает",
  "subtitles.carnis.amalgamation_fuse": "Плоть сливается в амальгаму",
  "subtitles.carnis.bone_deflect": "Снаряд рикошетит от кости",
  "subtitles.carnis.digestor_churn": "Желудочный пруд бурлит",
  "subtitles.carnis.flamethrower_fire": "Огнемёт ревёт",
  "subtitles.carnis.flesh_amalgam_ambient": "Амальгама плоти стонет",
  "subtitles.carnis.flesh_amalgam_death": "Амальгама плоти обрушивается",
  "subtitles.carnis.flesh_amalgam_hurt": "Амальгама плоти вздрагивает",
  "subtitles.carnis.heartbeat_loop": "Сердце бьётся",
  "subtitles.carnis.hive_eye_screech": "Око разума визжит",
  "subtitles.carnis.phantom_creeper": "Что-то шипит за спиной",
  "subtitles.carnis.phantom_footsteps": "Шаги хлюпают по плоти",
  "subtitles.carnis.phantom_whisper": "Коллективный разум шепчет",
  "subtitles.carnis.pulsing_heart_beat": "Сердце биома бьётся",
  "subtitles.carnis.synapse_rupture": "Нервная ткань разрывается",
  "subtitles.carnis.synapse_shock": "Нервный столб разряжается",
  "tooltip.carnis.antibiotics": "Предотвращает заражение на 3 минуты.",
  "tooltip.carnis.bio_purifier": "Удерживайте: конус пламени на 6,5 блока.",
  "tooltip.carnis.bone_scythe_arm": "Зазубренный костяной клинок.",
  "tooltip.carnis.charred_flesh": "Обгоревшая ткань даёт костную муку и уголь.",
  "tooltip.carnis.creeping_tendrils": "Взбирайтесь по усикам на поверхности плоти.",
  "tooltip.carnis.fireproof_flesh": "Ткань, приспособленная к огню.",
  "tooltip.carnis.flesh_amalgam_spawn_egg": "Призывает амальгаму плоти.",
  "tooltip.carnis.flesh_spat": "Сгусток заражённой ткани.",
  "tooltip.carnis.flesh_veins": "Органические жилы на открытых поверхностях.",
  "tooltip.carnis.hive_eye": "Обнаруживает чужаков и тревожит ближайших амальгам.",
  "tooltip.carnis.hold_shift": "Удерживайте Shift для подробностей",
  "tooltip.carnis.infected_creeper_spawn_egg": "Призывает заражённого крипера.",
  "tooltip.carnis.infected_skeleton_spawn_egg": "Призывает заражённого скелета.",
  "tooltip.carnis.infected_spider_spawn_egg": "Призывает заражённого паука.",
  "tooltip.carnis.infected_zombie_spawn_egg": "Призывает заражённого зомби.",
  "tooltip.carnis.living_flesh": "Живая ткань распространяется по окружающим блокам.",
  "tooltip.carnis.nerve_pillar": "При установке вдвое сокращает оставшийся шок чанка.",
  "tooltip.carnis.neural_binding_matrix": "Вплетите в броню на наковальне за пять уровней.",
  "tooltip.carnis.neural_moss": "Мясистый мох замедляет движение.",
  "tooltip.carnis.neuro_resonator_boots": "Биологические ботинки снижают заражение.",
  "tooltip.carnis.neuro_resonator_chestplate": "Биологический нагрудник снижает заражение.",
  "tooltip.carnis.neuro_resonator_helmet": "Подавляет галлюцинации, снижает экспозицию на 25% и обнаруживает биомассу.",
  "tooltip.carnis.neuro_resonator_leggings": "Биологические поножи снижают заражение.",
  "tooltip.carnis.ossified_flesh": "Окостеневшая ткань распространяет улей.",
  "tooltip.carnis.pneumatic_inoculator": "ПКМ: выстрел дротиком из инвентаря; задержка 15 тиков.",
  "tooltip.carnis.pulsing_heart": "Сердце улья ускоряет заражение поблизости.",
  "tooltip.carnis.purification_dart": "Снимает 35 заражения или наносит мобам Carnis 25 урона.",
  "tooltip.carnis.purification_serum": "Выпейте, чтобы снизить заражение на 35 пунктов.",
  "tooltip.carnis.pustule_cluster": "Наступите без приседания: пустулы лопнут и заразят вас.",
  "tooltip.carnis.research_journal": "Полевой справочник по улью.",
  "tooltip.carnis.spore_sprout": "Органический росток выпускает споры.",
  "tooltip.carnis.stomach_pool": "Едкая ткань растворяет предметы в биомассу.",
  "tooltip.carnis.tainted_sludge_bucket": "Ведро заразной слизи.",
  "tooltip.carnis.veins": "Живые вены несут инфекцию через древесину.",
  "tooltip.carnis.viral_dart": "Добавляет игрокам 30 заражения; травит и замедляет мобов.",
  "tooltip.carnis.flesh_bulb.mechanics": "Инкубационный мешок, способный закрепляться на потолке и полу.",
  "tooltip.carnis.flesh_bulb.lore": "Внутри слышно глухое, частое сердцебиение зреющего выводка.",
  "tooltip.carnis.sinew_spikes.mechanics": "Наносят колющий урон и замедляют любое наступившее существо.",
  "tooltip.carnis.sinew_spikes.lore": "Натянутые жилы реагируют на малейшую вибрацию шагов.",
  "tooltip.carnis.biomass_maggot.mechanics": "Ненасытный трупоед. Пожирает органические останки и окукливается в почве.",
  "tooltip.carnis.biomass_maggot.lore": "Начальное звено паразитического круговорота Улья.",
  "subtitles.carnis.inoculator_fire": "Выстрел инокулятора",
  "subtitles.carnis.dart_hit": "Дротик ударяется",
  "block.carnis.biomass_remains": "Останки биомассы",
  "entity.carnis.hive_sentinel": "Страж Улья",
  "entity.carnis.cerebral_nexus": "Мозговой узел",
  "effect.carnis.thermal_shock": "Термический шок",
  "subtitles.carnis.purifier_ignite": "Очиститель зажигается",
  "subtitles.carnis.purifier_loop": "Очиститель выпускает пламя"
}
```

