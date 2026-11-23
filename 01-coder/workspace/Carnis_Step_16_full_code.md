# Шаг 16 — полные исходные файлы и интеграция

Исходники и JSON приведены целиком.

## `src/main/java/com/carnis/mod/infection/PlayerInfectionManager.java`

```java
package com.carnis.mod.infection;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfection;
import com.carnis.mod.capability.infection.PlayerInfectionCapability;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlocks;
import com.carnis.mod.init.ModDamageSources;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.item.NeuroWeave;
import com.carnis.mod.network.ModMessages;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingChangeTargetEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.UUID;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerInfectionManager {
    public static final String POINTS = "carnis:infection_points";
    public static final String METAMORPHOSED = "carnis:human_metamorphosed";
    private static final String FRACTION = "carnis:infection_fraction";
    private static final String AGONY = "carnis:infection_agony_remaining";
    private static final String TERMINAL_ATTEMPT = "carnis:terminal_attempt";
    private static final String DEATH_OBSERVED = "carnis:terminal_death_observed";
    private static final UUID SLOW_ID = UUID.fromString("048ac83b-cbb9-4f41-96c8-9f62a6db0200");
    private static final AttributeModifier SLOW = new AttributeModifier(SLOW_ID, "Carnis infection", -.10D,
            AttributeModifier.Operation.MULTIPLY_TOTAL);
    private PlayerInfectionManager() { }

    /** The integer NBT value is authoritative; fractional exposure is retained separately. */
    public static float getPoints(Player player) {
        CompoundTag data = player.getPersistentData();
        if (!data.contains(POINTS)) {
            float legacy = player.getCapability(PlayerInfectionCapability.PLAYER_INFECTION)
                    .resolve().map(cap -> cap.getInfectionLevel()).orElse(0.0F);
            writeRaw(player, legacy);
        }
        int whole = Math.max(0, Math.min(100, data.getInt(POINTS)));
        float fraction = data.getFloat(FRACTION);
        if (!Float.isFinite(fraction) || fraction < 0 || fraction >= 1 || whole == 100) fraction = 0;
        return whole + fraction;
    }
    public static int stage(float points) {
        if (points <= 0) return 0;
        if (points < 25) return 1;
        if (points < 50) return 2;
        if (points < 90) return 3;
        return 4;
    }
    public static int displayPoints(Player player) { return (int) Math.floor(getPoints(player)); }
    private static void writeRaw(Player player, float value) {
        if (!Float.isFinite(value)) value = 0;
        value = Math.max(0, Math.min(100, value));
        int whole = (int) Math.floor(value);
        player.getPersistentData().putInt(POINTS, whole);
        player.getPersistentData().putFloat(FRACTION, whole == 100 ? 0 : value - whole);
        float mirror = value;
        player.getCapability(PlayerInfectionCapability.PLAYER_INFECTION).ifPresent(cap -> {
            if (cap instanceof PlayerInfection legacy) legacy.setInfectionLevelSilently(mirror);
        });
    }
    public static boolean setPoints(Player player, float value) {
        float before = getPoints(player);
        if (!Float.isFinite(value)) return false;
        value = Math.max(0, Math.min(100, value));
        if (Float.compare(before, value) == 0) return false;
        writeRaw(player, value);
        if (value < 100) player.getPersistentData().remove(AGONY);
        if (!player.level().isClientSide) {
            updateSlow(player, stage(value) >= 2);
            if (player instanceof ServerPlayer server && ((int) Math.floor(before) != (int) Math.floor(value)
                    || stage(before) != stage(value))) ModMessages.sendPlayerInfection(server);
        }
        return true;
    }
    public static void copyToClone(Player original, Player replacement, boolean death) {
        float points = getPoints(original);
        writeRaw(replacement, points);
        replacement.getPersistentData().remove(METAMORPHOSED);
        if (!death && original.getPersistentData().contains(AGONY))
            replacement.getPersistentData().putInt(AGONY, original.getPersistentData().getInt(AGONY));
        else replacement.getPersistentData().remove(AGONY);
    }
    private static void updateSlow(Player player, boolean active) {
        AttributeInstance speed = player.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed == null) return;
        boolean present = speed.getModifier(SLOW_ID) != null;
        if (active && !present) speed.addTransientModifier(SLOW);
        else if (!active && present) speed.removeModifier(SLOW_ID);
    }
    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)) return;
        float points = getPoints(player);
        int stage = stage(points);
        updateSlow(player, player.isAlive() && stage >= 2);
        if (player.tickCount % 20 == 0) {
            ModMessages.sendPlayerInfection(player);
            if (player.isAlive() && !player.isSpectator() && stage >= 1) player.causeFoodExhaustion(.02F);
        }
        if (!player.isAlive() || player.isSpectator() || player.isCreative() || points < 100) {
            if (points < 100) player.getPersistentData().remove(AGONY);
            return;
        }
        CompoundTag data = player.getPersistentData();
        if (!data.contains(AGONY)) { data.putInt(AGONY, 100); return; }
        int remaining = data.getInt(AGONY) - 1;
        data.putInt(AGONY, remaining);
        if (remaining <= 0) metamorphose(player);
    }
    @SubscribeEvent(priority = EventPriority.NORMAL)
    public static void onHurt(LivingHurtEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof ServerPlayer player) || stage(getPoints(player)) < 3) return;
        if (NeuroArmorEventHandler.isHiveEntity(event.getSource().getEntity())) event.setAmount(event.getAmount() * .8F);
        if (event.getSource().is(DamageTypeTags.IS_FIRE)) event.setAmount(event.getAmount() * 1.5F);
    }
    private static boolean neutralAtDistance(Mob mob, Player player) {
        return stage(getPoints(player)) >= 2 && mob.distanceToSqr(player) > 144.0D;
    }
    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void onTargetChange(LivingChangeTargetEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide
                || !NeuroArmorEventHandler.isHiveEntity(mob) || !(event.getNewTarget() instanceof Player player)) return;
        if (neutralAtDistance(mob, player)) event.setCanceled(true);
    }
    @SubscribeEvent
    public static void onLivingTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide
                || !NeuroArmorEventHandler.isHiveEntity(mob) || !(mob.getTarget() instanceof Player player)) return;
        if (neutralAtDistance(mob, player)) mob.setTarget(null);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onTerminalDeath(LivingDeathEvent event) {
        if (!event.isCanceled() && event.getEntity() instanceof ServerPlayer player
                && player.getPersistentData().getBoolean(TERMINAL_ATTEMPT)
                && event.getSource().is(ModDamageSources.ORGANIC_CONSUMPTION))
            player.getPersistentData().putBoolean(DEATH_OBSERVED, true);
    }
    private static void metamorphose(ServerPlayer player) {
        ServerLevel level = player.serverLevel();
        // Do not transfer equipment if vanilla keepInventory protects the player's inventory.
        boolean transfer = !level.getGameRules().getBoolean(GameRules.RULE_KEEPINVENTORY);
        ItemStack weapon = ItemStack.EMPTY, helmet = ItemStack.EMPTY;
        if (transfer) {
            ItemStack held = player.getMainHandItem();
            if (held.getItem() instanceof net.minecraft.world.item.SwordItem
                    || held.getItem() instanceof net.minecraft.world.item.AxeItem
                    || held.getItem() instanceof net.minecraft.world.item.BowItem
                    || held.getItem() instanceof net.minecraft.world.item.CrossbowItem
                    || held.getItem() instanceof net.minecraft.world.item.TridentItem) {
                weapon = held.copy();
                player.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
            }
            helmet = player.getItemBySlot(EquipmentSlot.HEAD).copy();
            player.setItemSlot(EquipmentSlot.HEAD, ItemStack.EMPTY);
        }
        CompoundTag data = player.getPersistentData();
        data.remove(DEATH_OBSERVED);
        data.putBoolean(TERMINAL_ATTEMPT, true);
        try { player.hurt(ModDamageSources.organicConsumption(level), 10000.0F); }
        finally { data.remove(TERMINAL_ATTEMPT); }
        boolean deathObserved = data.getBoolean(DEATH_OBSERVED);
        data.remove(DEATH_OBSERVED);
        if (!deathObserved || player.isAlive()) {
            restore(player, EquipmentSlot.MAINHAND, weapon);
            restore(player, EquipmentSlot.HEAD, helmet);
            player.getPersistentData().putInt(AGONY, 20);
            return;
        }
        player.getPersistentData().putBoolean(METAMORPHOSED, true);
        setPoints(player, 0);
        player.getPersistentData().remove(AGONY);
        InfectedZombieEntity clone = ModEntities.INFECTED_ZOMBIE.get().create(level);
        boolean spawned = false;
        if (clone != null) {
            clone.moveTo(player.getX(), player.getY(), player.getZ(), player.getYRot(), 0);
            clone.setCustomName(Component.translatable("entity.carnis.assimilated_player", player.getGameProfile().getName()));
            clone.setCustomNameVisible(true);
            clone.setPersistenceRequired();
            clone.setItemSlot(EquipmentSlot.MAINHAND, weapon);
            clone.setItemSlot(EquipmentSlot.HEAD, helmet);
            clone.setDropChance(EquipmentSlot.MAINHAND, 1.0F);
            clone.setDropChance(EquipmentSlot.HEAD, 1.0F);
            for (int[] offset : new int[][]{{0,0,0},{1,0,0},{-1,0,0},{0,0,1},{0,0,-1},{0,1,0}}) {
                BlockPos spot = player.blockPosition().offset(offset[0], offset[1], offset[2]);
                if (!level.hasChunkAt(spot) || level.isOutsideBuildHeight(spot)) continue;
                clone.moveTo(spot.getX() + .5D, spot.getY(), spot.getZ() + .5D, player.getYRot(), 0);
                if (!level.noCollision(clone)) continue;
                spawned = level.addFreshEntity(clone);
                break;
            }
        }
        if (!spawned) {
            dropAt(level, player, weapon);
            dropAt(level, player, helmet);
        }
        if (level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)) seedTissue(level, player.blockPosition());
    }
    private static void restore(ServerPlayer player, EquipmentSlot slot, ItemStack stack) {
        if (stack.isEmpty()) return;
        if (player.getItemBySlot(slot).isEmpty()) player.setItemSlot(slot, stack);
        else if (!player.getInventory().add(stack)) player.drop(stack, false);
    }
    private static void dropAt(ServerLevel level, Player player, ItemStack stack) {
        if (!stack.isEmpty()) level.addFreshEntity(new ItemEntity(level, player.getX(), player.getY(), player.getZ(), stack));
    }
    private static void seedTissue(ServerLevel level, BlockPos center) {
        BlockState remains = ModBlocks.BIOMASS_REMAINS.get().defaultBlockState();
        for (BlockPos pos : BlockPos.betweenClosed(center.offset(-1, -1, -1), center.offset(1, 1, 1))) {
            if (!level.hasChunkAt(pos) || level.isOutsideBuildHeight(pos) || !level.isEmptyBlock(pos)) continue;
            if (remains.canSurvive(level, pos) && level.setBlockAndUpdate(pos, remains)) break;
        }
        for (BlockPos pos : BlockPos.betweenClosed(center.offset(-3, -3, -3), center.offset(3, 3, 3))) {
            if (pos.distSqr(center) > 9 || level.isOutsideBuildHeight(pos) || !level.hasChunkAt(pos)) continue;
            BlockState state = level.getBlockState(pos);
            if (!state.isAir() || !state.getFluidState().isEmpty()) continue;
            BlockState vein = Blocks.AIR.defaultBlockState();
            for (Direction face : Direction.values()) {
                BlockPos support = pos.relative(face);
                if (!level.hasChunkAt(support) || level.isOutsideBuildHeight(support)
                        || !level.getBlockState(support).isFaceSturdy(level, support, face.getOpposite())) continue;
                BlockState next = ModBlocks.FLESH_VEINS.get().getStateForPlacement(vein, level, pos, face);
                if (next != null) vein = next;
            }
            if (vein.is(ModBlocks.FLESH_VEINS.get())) level.setBlockAndUpdate(pos, vein);
        }
    }
}
```

## `src/main/java/com/carnis/mod/network/SyncPlayerInfectionPacket.java`

```java
package com.carnis.mod.network;

import com.carnis.mod.infection.PlayerInfectionManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

public record SyncPlayerInfectionPacket(int infectionPoints, int stage) {
    public SyncPlayerInfectionPacket {
        infectionPoints = Math.max(0, Math.min(100, infectionPoints));
        stage = Math.max(0, Math.min(4, stage));
    }
    public static SyncPlayerInfectionPacket from(Player player) {
        return new SyncPlayerInfectionPacket(PlayerInfectionManager.displayPoints(player),
                PlayerInfectionManager.stage(PlayerInfectionManager.getPoints(player)));
    }
    public static void encode(SyncPlayerInfectionPacket packet, FriendlyByteBuf buffer) {
        buffer.writeVarInt(packet.infectionPoints());
        buffer.writeVarInt(packet.stage());
    }
    public static SyncPlayerInfectionPacket decode(FriendlyByteBuf buffer) {
        return new SyncPlayerInfectionPacket(buffer.readVarInt(), buffer.readVarInt());
    }
    public static void handle(SyncPlayerInfectionPacket packet, Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        if (context.getDirection() == NetworkDirection.PLAY_TO_CLIENT)
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> com.carnis.mod.client.data.ClientInfectionData.apply(packet));
        context.setPacketHandled(true);
    }
}
```

## `src/main/java/com/carnis/mod/client/data/ClientInfectionData.java`

```java
package com.carnis.mod.client.data;

import com.carnis.mod.network.SyncPlayerInfectionPacket;
import net.minecraft.client.Minecraft;

/** Client-side presentation snapshot, replaced only by server packets. */
public final class ClientInfectionData {
    private static int points;
    private static int stage;
    private ClientInfectionData() { }
    public static void apply(SyncPlayerInfectionPacket packet) {
        points = packet.infectionPoints();
        stage = packet.stage();
        var player = Minecraft.getInstance().player;
        if (player != null) {
            player.getPersistentData().putInt("carnis:infection_points", points);
            player.getPersistentData().putFloat("carnis:infection_fraction", 0.0F);
        }
    }
    public static int points() { return points; }
    public static int stage() { return stage; }
    public static void reset() { points = 0; stage = 0; }
}
```

## `src/main/java/com/carnis/mod/client/PlayerHallucinationHandler.java`

```java
package com.carnis.mod.client;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientInfectionData;
import com.carnis.mod.config.CarnisConfig;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Presentation only: camera changes do not alter server-side aim or motion. */
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerHallucinationHandler {
    private static int soundDelay;
    private static int spasm;
    private static int agonyTicks;
    private PlayerHallucinationHandler() { }
    @SubscribeEvent public static void onTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        int stage = ClientInfectionData.stage();
        if (mc.level == null || player == null || !player.isAlive() || player.isSpectator() || stage == 0) {
            soundDelay = 0; spasm = 0; agonyTicks = 0; return;
        }
        if (ClientInfectionData.points() >= 100) {
            if (agonyTicks == 0) soundDelay = 0;
            agonyTicks = Math.min(100, agonyTicks + 1);
        } else agonyTicks = 0;
        if (spasm > 0) spasm--;
        if (NeuroResonatorHelmetItem.isEquipped(player)) { soundDelay = 0; spasm = 0; return; }
        if (stage >= 3 && player.getRandom().nextInt(180) == 0) spasm = 8;
        if (!CarnisConfig.CLIENT.hallucinationSoundsEnabled.get()) return;
        if (soundDelay > 0) { soundDelay--; return; }
        float volume = CarnisConfig.CLIENT.hallucinationSoundVolume.get().floatValue();
        volume *= com.carnis.mod.item.NeuroWeave.infectionMultiplier(player);
        if (volume > 0) {
            SoundEvent sound;
            Vec3 pos;
            if (agonyTicks > 0) {
                sound = agonyTicks == 1 ? ModSounds.AMALGAM_ROAR.get() : ModSounds.HEARTBEAT_LOOP.get();
                pos = player.position().add(0, 1, 0);
                volume *= .4F + .6F * agonyTicks / 100.0F;
                soundDelay = Math.max(8, 24 - agonyTicks / 7);
            } else {
                boolean whisper = stage == 1 || player.getRandom().nextBoolean();
                sound = whisper ? ModSounds.PHANTOM_WHISPER.get() : ModSounds.PHANTOM_FOOTSTEPS.get();
                if (stage == 1 && player.getRandom().nextBoolean()) sound = ModSounds.HEARTBEAT_LOOP.get();
                Vec3 behind = player.getLookAngle().multiply(1, 0, 1).normalize().scale(-2.5D);
                pos = player.position().add(behind).add(0, .6D, 0);
                soundDelay = stage == 1 ? 400 + player.getRandom().nextInt(601)
                        : 200 + player.getRandom().nextInt(501);
            }
            mc.level.playLocalSound(pos.x, pos.y, pos.z, sound, SoundSource.AMBIENT, volume, .9F, false);
        } else soundDelay = 200;
    }
    @SubscribeEvent public static void onCamera(ViewportEvent.ComputeCameraAngles event) {
        LocalPlayer player = Minecraft.getInstance().player;
        if (player == null || !player.isAlive() || player.isSpectator() || event.getCamera().getEntity() != player
                || NeuroResonatorHelmetItem.isEquipped(player) || ClientInfectionData.stage() < 3) return;
        double t = player.tickCount + event.getPartialTick();
        float strength = spasm > 0 ? .8F * spasm / 8.0F : 0;
        if (agonyTicks > 0) strength += .35F * agonyTicks / 100.0F;
        event.setYaw(event.getYaw() + (float) Math.sin(t * 2.4D) * strength);
        event.setPitch(event.getPitch() + (float) Math.cos(t * 1.7D) * strength * .7F);
        event.setRoll(event.getRoll() + (float) Math.sin(t * 1.2D) * strength * .6F);
    }
}
```

## `src/main/java/com/carnis/mod/init/ModDamageSources.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.level.Level;

public final class ModDamageSources {
    public static final ResourceKey<DamageType> ORGANIC_CONSUMPTION = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(CarnisMod.MOD_ID, "organic_consumption"));
    private ModDamageSources() { }
    public static DamageSource organicConsumption(Level level) {
        return new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(ORGANIC_CONSUMPTION));
    }
}
```

## `src/main/java/com/carnis/mod/capability/infection/PlayerInfectionApi.java`

```java
package com.carnis.mod.capability.infection;

import com.carnis.mod.infection.PlayerInfectionManager;
import com.carnis.mod.item.NeuroWeave;
import net.minecraft.world.entity.player.Player;

/** Compatibility facade. Persistent player data is the authoritative store. */
public final class PlayerInfectionApi {
    private PlayerInfectionApi() { }
    public static float getInfectionLevel(Player player) { return PlayerInfectionManager.getPoints(player); }
    public static boolean setInfectionLevel(Player player, float value) {
        if (value > getInfectionLevel(player) && player.hasEffect(com.carnis.mod.init.ModEffects.IMMUNOSUPPRESSION.get())) return false;
        return PlayerInfectionManager.setPoints(player, value);
    }
    public static boolean addInfection(Player player, float amount) {
        if (Float.isNaN(amount) || amount == 0) return false;
        return setInfectionLevel(player, getInfectionLevel(player) + amount);
    }
    public static boolean addExposure(Player player, float amount) {
        if (amount > 0 && player.hasEffect(com.carnis.mod.init.ModEffects.IMMUNOSUPPRESSION.get())) return false;
        return addInfection(player, amount > 0 ? amount * NeuroWeave.infectionMultiplier(player) : amount);
    }
    /** A living carrier has not yet been assimilated into a clone. */
    public static boolean isAssimilated(Player player) {
        return player.getPersistentData().getBoolean(PlayerInfectionManager.METAMORPHOSED);
    }
    public static boolean isHostileTarget(Player player) {
        return player.isAlive() && !player.isSpectator() && !player.isCreative();
    }
    public static void copy(Player source, Player target) {
        PlayerInfectionManager.copyToClone(source, target, false);
    }
}
```

## `src/main/java/com/carnis/mod/capability/infection/PlayerInfection.java`

```java
package com.carnis.mod.capability.infection;

import java.util.Objects;

/**
 * Clamped data implementation for the player infection capability.
 */
public final class PlayerInfection implements IPlayerInfection {
    private static final Runnable NO_CHANGE_LISTENER = () -> {
    };

    private final Runnable changeListener;
    private float infectionLevel;

    public PlayerInfection() {
        this(NO_CHANGE_LISTENER);
    }

    public PlayerInfection(Runnable changeListener) {
        this.changeListener = Objects.requireNonNull(
                changeListener,
                "changeListener"
        );
    }

    @Override
    public float getInfectionLevel() {
        return infectionLevel;
    }

    @Override
    public boolean setInfectionLevel(float infectionLevel) {
        float sanitizedLevel = sanitize(infectionLevel);

        if (Float.compare(this.infectionLevel, sanitizedLevel) == 0) {
            return false;
        }

        this.infectionLevel = sanitizedLevel;
        changeListener.run();
        return true;
    }

    @Override
    public boolean addInfection(float amount) {
        if (Float.isNaN(amount) || amount == 0.0F) {
            return false;
        }

        return setInfectionLevel(infectionLevel + amount);
    }

    static float sanitize(float infectionLevel) {
        if (Float.isNaN(infectionLevel)) {
            return MIN_INFECTION;
        }

        return Math.max(
                MIN_INFECTION,
                Math.min(MAX_INFECTION, infectionLevel)
        );
    }

    public void setInfectionLevelSilently(float infectionLevel) {
        this.infectionLevel = sanitize(infectionLevel);
    }
}
```

## `src/main/java/com/carnis/mod/capability/infection/PlayerInfectionProvider.java`

```java
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
```

## `src/main/java/com/carnis/mod/event/PlayerInfectionEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.capability.infection.PlayerInfectionCapability;
import com.carnis.mod.capability.infection.PlayerInfectionProvider;
import com.carnis.mod.entity.FleshSpatProjectileEntity;
import com.carnis.mod.entity.InfectedZombieEntity;
import com.carnis.mod.entity.InfectedSkeletonEntity;
import com.carnis.mod.entity.InfectedSpiderEntity;
import com.carnis.mod.infection.PlayerInfectionManager;
import com.carnis.mod.init.ModBlockTags;
import com.carnis.mod.network.ModMessages;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.AttachCapabilitiesEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class PlayerInfectionEvents {
    public static final float SURFACE_INFECTION_PER_TICK = .05F;
    public static final float MOB_HIT_BASE_INFECTION = 1.0F;
    public static final float MOB_HIT_INFECTION_PER_DAMAGE = .5F;
    private PlayerInfectionEvents() { }
    @SubscribeEvent public static void onAttachCapabilities(AttachCapabilitiesEvent<Entity> event) {
        if (!(event.getObject() instanceof Player player)) return;
        PlayerInfectionProvider provider = new PlayerInfectionProvider(player);
        event.addCapability(PlayerInfectionCapability.ID, provider);
        event.addListener(provider::invalidate);
    }
    @SubscribeEvent public static void onPlayerClone(PlayerEvent.Clone event) {
        Player old = event.getOriginal();
        old.reviveCaps();
        try { PlayerInfectionManager.copyToClone(old, event.getEntity(), event.isWasDeath()); }
        finally { old.invalidateCaps(); }
    }
    @SubscribeEvent public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) { sync(event.getEntity()); }
    @SubscribeEvent public static void onRespawn(PlayerEvent.PlayerRespawnEvent event) { sync(event.getEntity()); }
    @SubscribeEvent public static void onDimension(PlayerEvent.PlayerChangedDimensionEvent event) { sync(event.getEntity()); }
    private static void sync(Player player) { if (player instanceof ServerPlayer server) ModMessages.sendPlayerInfection(server); }
    @SubscribeEvent public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)
                || !player.isAlive() || player.isSpectator() || !player.onGround()
                || !player.getBlockStateOn().is(ModBlockTags.INFECTIOUS_SURFACES)) return;
        PlayerInfectionApi.addExposure(player, SURFACE_INFECTION_PER_TICK);
    }
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onLivingHurt(LivingHurtEvent event) {
        if (event.isCanceled() || event.getAmount() <= 0 || !(event.getEntity() instanceof ServerPlayer player)
                || event.getSource().getDirectEntity() instanceof FleshSpatProjectileEntity
                || !NeuroArmorEventHandler.isHiveEntity(event.getSource().getEntity())) return;
        Entity attacker = event.getSource().getEntity();
        boolean direct = event.getSource().getDirectEntity() == attacker;
        float amount = direct && attacker instanceof InfectedZombieEntity ? 8.0F
                : direct && attacker instanceof InfectedSkeletonEntity ? 10.0F
                : direct && attacker instanceof InfectedSpiderEntity ? 5.0F
                : MOB_HIT_BASE_INFECTION + event.getAmount() * MOB_HIT_INFECTION_PER_DAMAGE;
        PlayerInfectionApi.addExposure(player, amount);
    }
}
```

## `src/main/java/com/carnis/mod/network/ModMessages.java`

```java
package com.carnis.mod.network;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.network.packet.ClientboundHallucinationPacket;
import com.carnis.mod.network.packet.SyncCarnisWorldDataPacket;
import com.carnis.mod.world.CarnisWorldData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

import java.util.Objects;

public final class ModMessages {
    private static final String PROTOCOL_VERSION = "2";

    private static final SimpleChannel CHANNEL =
            NetworkRegistry.ChannelBuilder
                    .named(new ResourceLocation(CarnisMod.MOD_ID, "messages"))
                    .networkProtocolVersion(() -> PROTOCOL_VERSION)
                    .clientAcceptedVersions(PROTOCOL_VERSION::equals)
                    .serverAcceptedVersions(PROTOCOL_VERSION::equals)
                    .simpleChannel();

    private static int nextPacketId;
    private static volatile boolean registered;

    private ModMessages() {
    }

    public static synchronized void register() {
        if (registered) {
            throw new IllegalStateException("Carnis network packets are already registered");
        }

        CHANNEL.messageBuilder(
                        SyncCarnisWorldDataPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(SyncCarnisWorldDataPacket::encode)
                .decoder(SyncCarnisWorldDataPacket::decode)
                .consumerMainThread(SyncCarnisWorldDataPacket::handle)
                .add();

        CHANNEL.messageBuilder(
                        SyncPlayerInfectionPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(SyncPlayerInfectionPacket::encode)
                .decoder(SyncPlayerInfectionPacket::decode)
                .consumerMainThread(SyncPlayerInfectionPacket::handle)
                .add();

        CHANNEL.messageBuilder(
                        ClientboundHallucinationPacket.class,
                        nextPacketId(),
                        NetworkDirection.PLAY_TO_CLIENT
                )
                .encoder(ClientboundHallucinationPacket::encode)
                .decoder(ClientboundHallucinationPacket::decode)
                .consumerMainThread(ClientboundHallucinationPacket::handle)
                .add();

        registered = true;
    }

    public static void sendToPlayer(ServerPlayer player) {
        Objects.requireNonNull(player, "player");
        ensureRegistered();

        CarnisWorldData worldData = CarnisWorldData.get(player.serverLevel());
        sendToPlayer(player, SyncCarnisWorldDataPacket.from(worldData));
    }

    public static void sendPlayerInfection(ServerPlayer player) {
        Objects.requireNonNull(player, "player");
        ensureRegistered();

        sendToPlayer(player, SyncPlayerInfectionPacket.from(player));
    }

    public static void sendHallucination(
            ServerPlayer player,
            ClientboundHallucinationPacket packet
    ) {
        Objects.requireNonNull(player, "player");
        Objects.requireNonNull(packet, "packet");
        ensureRegistered();

        sendToPlayer(player, packet);
    }

    public static void sendToPlayersInLevel(ServerLevel level) {
        Objects.requireNonNull(level, "level");
        ensureRegistered();

        SyncCarnisWorldDataPacket packet = SyncCarnisWorldDataPacket.from(
                CarnisWorldData.get(level)
        );

        for (ServerPlayer player : level.players()) {
            sendToPlayer(player, packet);
        }
    }

    public static void sendToAllPlayers(MinecraftServer server) {
        Objects.requireNonNull(server, "server");
        ensureRegistered();

        for (ServerLevel level : server.getAllLevels()) {
            sendToPlayersInLevel(level);
        }
    }

    private static void sendToPlayer(
            ServerPlayer player,
            SyncCarnisWorldDataPacket packet
    ) {
        CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                packet
        );
    }

    private static void sendToPlayer(
            ServerPlayer player,
            SyncPlayerInfectionPacket packet
    ) {
        CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                packet
        );
    }

    private static void sendToPlayer(
            ServerPlayer player,
            ClientboundHallucinationPacket packet
    ) {
        CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                packet
        );
    }

    private static int nextPacketId() {
        return nextPacketId++;
    }

    private static void ensureRegistered() {
        if (!registered) {
            throw new IllegalStateException(
                    "Carnis network packets have not been registered yet"
            );
        }
    }
}
```

## `src/main/java/com/carnis/mod/client/data/ClientPlayerInfection.java`

```java
package com.carnis.mod.client.data;

/** Compatibility facade for earlier overlays and fog renderers. */
public final class ClientPlayerInfection {
    private ClientPlayerInfection() { }
    public static float getInfectionLevel() { return ClientInfectionData.points(); }
    public static boolean isAssimilated() { return ClientInfectionData.points() >= 100; }
    public static void reset() { ClientInfectionData.reset(); }
}
```

## `src/main/java/com/carnis/mod/event/HallucinationEvents.java`

```java
package com.carnis.mod.event;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.hallucination.HallucinationType;
import com.carnis.mod.item.NeuroResonatorHelmetItem;
import com.carnis.mod.item.NeuroWeave;
import com.carnis.mod.network.ModMessages;
import com.carnis.mod.network.packet.ClientboundHallucinationPacket;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(
        modid = CarnisMod.MOD_ID,
        bus = Mod.EventBusSubscriber.Bus.FORGE
)
public final class HallucinationEvents {
    public static final float INFECTION_THRESHOLD = 60.0F;
    public static final int MIN_DELAY_TICKS = 20 * 20;
    public static final int MAX_DELAY_TICKS = 50 * 20;

    private static final float MIN_VOLUME_MULTIPLIER = 0.85F;
    private static final float MAX_VOLUME_MULTIPLIER = 1.15F;
    private static final String DELAY_TAG =
            CarnisMod.MOD_ID + ":hallucination_delay_ticks";
    private static final HallucinationType[] TYPES =
            HallucinationType.values();

    private HallucinationEvents() {
    }

    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (
                event.phase != TickEvent.Phase.END
                        || !(event.player instanceof ServerPlayer player)
        ) {
            return;
        }

        CompoundTag persistentData = player.getPersistentData();

        if (
                !player.isAlive()
                        || player.isSpectator()
                        || NeuroResonatorHelmetItem.isEquipped(player)
                        || PlayerInfectionApi.getInfectionLevel(player)
                        < INFECTION_THRESHOLD
        ) {
            resetHallucinationTimer(player);
            return;
        }

        if (!persistentData.contains(DELAY_TAG)) {
            scheduleNextHallucination(persistentData, player.getRandom(), PlayerInfectionApi.getInfectionLevel(player) >= 100.0F);
            return;
        }

        int remainingTicks = persistentData.getInt(DELAY_TAG);

        if (remainingTicks > 1) {
            persistentData.putInt(DELAY_TAG, remainingTicks - 1);
            return;
        }

        RandomSource random = player.getRandom();
        HallucinationType type = TYPES[random.nextInt(TYPES.length)];
        float volumeMultiplier = MIN_VOLUME_MULTIPLIER
                + random.nextFloat()
                * (MAX_VOLUME_MULTIPLIER - MIN_VOLUME_MULTIPLIER);
        volumeMultiplier *= NeuroWeave.infectionMultiplier(player);
        Vec3 relativeOffset = createRelativeOffset(type, random);

        ModMessages.sendHallucination(
                player,
                new ClientboundHallucinationPacket(
                        type,
                        volumeMultiplier,
                        relativeOffset
                )
        );
        scheduleNextHallucination(persistentData, random, PlayerInfectionApi.getInfectionLevel(player) >= 100.0F);
    }

    public static void resetHallucinationTimer(ServerPlayer player) {
        player.getPersistentData().remove(DELAY_TAG);
    }

    private static void scheduleNextHallucination(
            CompoundTag persistentData,
            RandomSource random, boolean critical
    ) {
        persistentData.putInt(
                DELAY_TAG,
                random.nextIntBetweenInclusive(
                        critical ? 100 : MIN_DELAY_TICKS,
                        critical ? 200 : MAX_DELAY_TICKS
                )
        );
    }

    private static Vec3 createRelativeOffset(
            HallucinationType type,
            RandomSource random
    ) {
        return switch (type) {
            case CREEPER_HISS -> new Vec3(
                    0.0D,
                    0.75D,
                    -randomBetween(random, 2.0D, 3.0D)
            );
            case PHANTOM_FOOTSTEPS -> new Vec3(
                    randomBetween(random, -1.25D, 1.25D),
                    -0.15D,
                    -randomBetween(random, 2.0D, 3.5D)
            );
            case WHISPER -> new Vec3(
                    (random.nextBoolean() ? 1.0D : -1.0D)
                            * randomBetween(random, 0.55D, 1.1D),
                    1.25D,
                    -randomBetween(random, 1.0D, 2.0D)
            );
            case FALSE_DAMAGE -> new Vec3(0.0D, 1.0D, 0.0D);
        };
    }

    private static double randomBetween(
            RandomSource random,
            double minimum,
            double maximum
    ) {
        return minimum + random.nextDouble() * (maximum - minimum);
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/NecroticCameraEffects.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerInfection;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@OnlyIn(Dist.CLIENT)
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class NecroticCameraEffects {
    private NecroticCameraEffects() {
    }

    public static void onCameraAngles(ViewportEvent.ComputeCameraAngles event) {
        LocalPlayer player = Minecraft.getInstance().player;
        if (player == null || !player.isAlive() || player.isSpectator()
                || ClientPlayerInfection.getInfectionLevel() < 100.0F) {
            return;
        }
        double phase = (player.tickCount % 20) + event.getPartialTick();
        if (phase < 4.0D) {
            float roll = (float) (Math.sin(phase * 4.0D) * (1.0D - phase / 4.0D) * 1.5D);
            event.setRoll(event.getRoll() + roll);
        }
    }
}
```

## `src/main/java/com/carnis/mod/client/renderer/CarnisFogRenderer.java`

```java
package com.carnis.mod.client.renderer;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerInfection;
import com.carnis.mod.config.CarnisConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.util.Mth;
import net.minecraft.world.level.material.FogType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@OnlyIn(Dist.CLIENT)
@Mod.EventBusSubscriber(modid = CarnisMod.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CarnisFogRenderer {
    private static final float FOG_RED = 0.32F;
    private static final float FOG_GREEN = 0.04F;
    private static final float FOG_BLUE = 0.06F;
    private static final float SMOOTHING_PER_TICK = 0.10F;
    private static final float DENSITY_THRESHOLD = 0.50F;
    private static final float FAR_DISTANCE_LOW = 24.0F;
    private static final float FAR_DISTANCE_HIGH = 12.0F;
    private static float previousInfection;
    private static float smoothedInfection;

    private CarnisFogRenderer() {
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.player == null || minecraft.level == null) {
            previousInfection = 0.0F;
            smoothedInfection = 0.0F;
            return;
        }
        if (com.carnis.mod.client.data.ClientInfectionData.stage() < 3) {
            previousInfection = 0.0F;
            smoothedInfection = 0.0F;
            return;
        }
        float infection = ClientPlayerInfection.getInfectionLevel();
        float target = Float.isFinite(infection)
                ? Mth.clamp(infection / 100.0F, 0.0F, 1.0F)
                : 0.0F;
        previousInfection = smoothedInfection;
        smoothedInfection = Mth.lerp(SMOOTHING_PER_TICK, smoothedInfection, target);
    }

    @SubscribeEvent
    public static void onLogout(ClientPlayerNetworkEvent.LoggingOut event) {
        previousInfection = 0.0F;
        smoothedInfection = 0.0F;
        ClientPlayerInfection.reset();
    }

    private static float infectionForFrame(double partialTick) {
        float partial = Mth.clamp((float) partialTick, 0.0F, 1.0F);
        return Mth.lerp(partial, previousInfection, smoothedInfection);
    }

    @SubscribeEvent
    public static void onFogColor(ViewportEvent.ComputeFogColor event) {
        Minecraft minecraft = Minecraft.getInstance();
        if (!CarnisConfig.CLIENT.atmosphericFogEnabled.get()
                || minecraft.player == null || minecraft.level == null
                || event.getCamera().getFluidInCamera() != FogType.NONE) {
            return;
        }
        float strength = infectionForFrame(event.getPartialTick());
        if (strength <= 0.0F) {
            return;
        }
        event.setRed(Mth.lerp(strength, event.getRed(), FOG_RED));
        event.setGreen(Mth.lerp(strength, event.getGreen(), FOG_GREEN));
        event.setBlue(Mth.lerp(strength, event.getBlue(), FOG_BLUE));
    }

    @SubscribeEvent
    public static void onRenderFog(ViewportEvent.RenderFog event) {
        Minecraft minecraft = Minecraft.getInstance();
        if (!CarnisConfig.CLIENT.atmosphericFogEnabled.get()
                || minecraft.player == null || minecraft.level == null
                || event.getType() != FogType.NONE
                || event.getMode() != FogRenderer.FogMode.FOG_TERRAIN) {
            return;
        }
        float infection = infectionForFrame(event.getPartialTick());
        float density = Mth.clamp(
                (infection - DENSITY_THRESHOLD) / (1.0F - DENSITY_THRESHOLD),
                0.0F, 1.0F
        );
        if (density <= 0.0F) {
            return;
        }
        float originalEnd = event.getFarPlaneDistance();
        float originalStart = event.getNearPlaneDistance();
        float desiredEnd = Mth.lerp(density, FAR_DISTANCE_LOW, FAR_DISTANCE_HIGH);
        float end = Mth.lerp(density, originalEnd, Math.min(originalEnd, desiredEnd));
        float start = Mth.lerp(density, originalStart, Math.min(originalStart, end * 0.25F));
        if (end < originalEnd || start < originalStart) {
            event.setFarPlaneDistance(end);
            event.setNearPlaneDistance(Math.min(start, end));
            event.setCanceled(true);
        }
    }
}
```

## `src/main/java/com/carnis/mod/client/gui/InfectionVeinsOverlay.java`

```java
package com.carnis.mod.client.gui;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.client.data.ClientPlayerInfection;
import com.carnis.mod.config.CarnisConfig;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

@OnlyIn(Dist.CLIENT)
public final class InfectionVeinsOverlay implements IGuiOverlay {
    private static final ResourceLocation VEINS_TEXTURE = new ResourceLocation(
            CarnisMod.MOD_ID,
            "textures/misc/vein_overlay.png"
    );

    private static final int TEXTURE_SIZE = 256;
    private static final float HIGH_INFECTION_THRESHOLD = 70.0F;
    private static final double MIN_PULSE_SPEED = 0.055D;
    private static final double MAX_PULSE_SPEED = 0.180D;

    @Override
    public void render(
            ForgeGui gui,
            GuiGraphics guiGraphics,
            float partialTick,
            int screenWidth,
            int screenHeight
    ) {
        if (!CarnisConfig.CLIENT.veinOverlayEnabled.get()) {
            return;
        }

        float infectionLevel = ClientPlayerInfection.getInfectionLevel();

        if (com.carnis.mod.client.data.ClientInfectionData.stage() < 2) {
            return;
        }

        ClientLevel level = gui.getMinecraft().level;

        if (level == null || screenWidth <= 0 || screenHeight <= 0) {
            return;
        }

        float configuredIntensity = CarnisConfig.CLIENT
                .veinOverlayIntensity
                .get()
                .floatValue();

        if (configuredIntensity <= 0.0F) {
            return;
        }

        float normalizedInfection = Mth.clamp(
                infectionLevel / 100.0F,
                0.0F,
                1.0F
        );
        float baseAlpha = normalizedInfection;
        double speed = Mth.lerp(
                normalizedInfection,
                MIN_PULSE_SPEED,
                MAX_PULSE_SPEED
        );
        double gameTime = level.getGameTime() + partialTick;
        float pulse = 0.72F + 0.28F * (float) (
                (Math.sin(gameTime * speed) + 1.0D) * 0.5D
        );
        float overlayAlpha = Mth.clamp(
                baseAlpha * pulse * configuredIntensity,
                0.0F,
                1.0F
        );

        gui.setupOverlayRenderState(true, false);
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();

        try {
            RenderSystem.setShaderColor(
                    1.0F,
                    0.52F,
                    0.60F,
                    overlayAlpha
            );
            blitFullScreen(guiGraphics, screenWidth, screenHeight);

            if (infectionLevel >= HIGH_INFECTION_THRESHOLD) {
                float severeInfection = Mth.clamp(
                        (infectionLevel - HIGH_INFECTION_THRESHOLD)
                                / (100.0F - HIGH_INFECTION_THRESHOLD),
                        0.0F,
                        1.0F
                );
                float darkeningAlpha = Mth.clamp(
                        configuredIntensity
                                * pulse
                                * (0.08F + 0.42F * severeInfection),
                        0.0F,
                        1.0F
                );

                RenderSystem.setShaderColor(
                        0.28F,
                        0.018F,
                        0.032F,
                        darkeningAlpha
                );
                blitFullScreen(guiGraphics, screenWidth, screenHeight);
            }
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            int stage = com.carnis.mod.client.data.ClientInfectionData.stage();
            if (stage >= 3 && Math.floorMod(level.getGameTime(), 120L) < 5L) {
                int alpha = (int) (configuredIntensity * 24.0F);
                guiGraphics.fill(0, 0, screenWidth, screenHeight, (alpha << 24) | 0x356D42);
            }
            if (infectionLevel >= 100.0F) {
                int alpha = (int) (configuredIntensity * 45.0F * pulse);
                guiGraphics.fill(0, 0, screenWidth, screenHeight, (alpha << 24) | 0x110408);
            }
        } finally {
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            RenderSystem.defaultBlendFunc();
            RenderSystem.disableBlend();
            RenderSystem.enableDepthTest();
        }
    }

    private static void blitFullScreen(
            GuiGraphics guiGraphics,
            int screenWidth,
            int screenHeight
    ) {
        guiGraphics.blit(
                VEINS_TEXTURE,
                0,
                0,
                screenWidth,
                screenHeight,
                0.0F,
                0.0F,
                TEXTURE_SIZE,
                TEXTURE_SIZE,
                TEXTURE_SIZE,
                TEXTURE_SIZE
        );
    }
}
```

## `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
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
    public static final double HIVEMIND_ALERT_RADIUS = 28.0D;
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
                    && (com.carnis.mod.event.NeuroArmorEventHandler.hiddenFromSensor(player, distance)
                    || com.carnis.mod.infection.PlayerInfectionManager.stage(
                            com.carnis.mod.infection.PlayerInfectionManager.getPoints(player)) >= 2 && distance > 144.0D)) continue;
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
        com.carnis.mod.entity.ai.HiveSwarmCoordinator.eyeAlarm(level, worldPosition, nearest);
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
            return !player.isCreative();
        }
        return true;
    }
}
```

## `src/main/java/com/carnis/mod/item/BioPurifierItem.java`

```java
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
                SoundSource.PLAYERS, 0.9F, 1.0F);
        return InteractionResultHolder.consume(stack);
    }

    @Override public void onUseTick(Level level, LivingEntity user, ItemStack stack, int count) {
        if (!(level instanceof ServerLevel server)) return;
        if (stack.isEmpty()) { user.stopUsingItem(); return; }
        int elapsed = DURATION - count;
        if (elapsed % 10 == 0) server.playSound(null, user.blockPosition(), ModSounds.PURIFIER_LOOP.get(),
                SoundSource.PLAYERS, 0.7F, 1.0F);
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
            boolean protectedByPillar = HiveNetwork.nearestLoaded(level, HiveNetwork.Kind.PILLAR, target.blockPosition(), 32) != null;
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
```

## `src/main/java/com/carnis/mod/entity/PurificationDartEntity.java`

```java
package com.carnis.mod.entity;

import com.carnis.mod.CarnisMod;
import com.carnis.mod.capability.infection.PlayerInfectionApi;
import com.carnis.mod.init.ModDamageTypes;
import com.carnis.mod.init.ModEntities;
import com.carnis.mod.init.ModSounds;
import net.minecraft.network.protocol.Packet;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.network.NetworkHooks;
import net.minecraftforge.registries.ForgeRegistries;

public final class PurificationDartEntity extends AbstractArrow {
    public PurificationDartEntity(EntityType<? extends PurificationDartEntity> type, Level level) {
        super(type, level);
        pickup = Pickup.DISALLOWED;
    }

    public PurificationDartEntity(Level level, LivingEntity owner) {
        super(ModEntities.PURIFICATION_DART.get(), owner, level);
        pickup = Pickup.DISALLOWED;
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        if (level().isClientSide) {
            return;
        }
        Entity hit = result.getEntity();
        if (hit instanceof ServerPlayer player) {
            PlayerInfectionApi.addInfection(player, -35.0F);
        } else if (hit instanceof LivingEntity living && isCarnis(living)) {
            living.hurt(ModDamageTypes.purificationDart(level(), this, getOwner()), 25.0F);
        }
        discard();
    }

    private static boolean isCarnis(LivingEntity target) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(target.getType());
        return target instanceof HivemindLinkedMob || id != null && CarnisMod.MOD_ID.equals(id.getNamespace());
    }

    @Override
    protected SoundEvent getDefaultHitGroundSoundEvent() {
        return ModSounds.DART_HIT.get();
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        setSoundEvent(ModSounds.DART_HIT.get());
        super.onHitBlock(result);
    }

    @Override
    protected ItemStack getPickupItem() {
        return ItemStack.EMPTY;
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
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
        add("entity.carnis.assimilated_player", "Assimilated %s");
        add("death.attack.organic_consumption", "%1$s was consumed by the hive");
        add("entity.carnis.flesh_amalgam", "Flesh Amalgam");
        add("item.carnis.amalgam_bile_glob", "Amalgam Bile");
        add("entity.carnis.amalgam_bile", "Amalgam Bile");
        add("tooltip.carnis.amalgam_bile_glob", "A corrosive organic glob.");
        add("subtitles.carnis.amalgam_smash", "Amalgam slams the ground");
        add("subtitles.carnis.organic_creak", "Sinew lashes");
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
        add("entity.carnis.assimilated_player", "Ассимилированный %s");
        add("death.attack.organic_consumption", "%1$s был поглощён Ульем");
        add("entity.carnis.flesh_amalgam", "Амальгама плоти");
        add("item.carnis.amalgam_bile_glob", "Желчь амальгамы");
        add("entity.carnis.amalgam_bile", "Желчь амальгамы");
        add("tooltip.carnis.amalgam_bile_glob", "Едкий органический сгусток.");
        add("subtitles.carnis.amalgam_smash", "Амальгама сотрясает землю");
        add("subtitles.carnis.organic_creak", "Сухожилие хлещет");
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

## `src/main/resources/data/carnis/damage_type/organic_consumption.json`

```json
{
  "message_id": "organic_consumption",
  "scaling": "never",
  "exhaustion": 0.0
}
```

## `src/main/resources/data/minecraft/tags/damage_type/bypasses_armor.json`

```json
{
  "replace": false,
  "values": [
    "carnis:bio_purifier",
    "carnis:necrotic_consumption",
    "carnis:purification_dart",
    "carnis:organic_consumption"
  ]
}
```

## `src/main/resources/data/minecraft/tags/damage_type/is_fire.json`

```json
{
  "replace": false,
  "values": [
    "carnis:bio_purifier",
    "carnis:bio_purifier_surface"
  ]
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
  "subtitles.carnis.purifier_loop": "Purifier fires",
  "item.carnis.amalgam_bile_glob": "Amalgam Bile",
  "entity.carnis.amalgam_bile": "Amalgam Bile",
  "tooltip.carnis.amalgam_bile_glob": "A corrosive organic glob.",
  "subtitles.carnis.amalgam_smash": "Amalgam slams the ground",
  "subtitles.carnis.organic_creak": "Sinew lashes",
  "entity.carnis.assimilated_player": "Assimilated %s",
  "death.attack.organic_consumption": "%1$s was consumed by the hive"
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
  "subtitles.carnis.purifier_loop": "Очиститель выпускает пламя",
  "item.carnis.amalgam_bile_glob": "Желчь амальгамы",
  "entity.carnis.amalgam_bile": "Желчь амальгамы",
  "tooltip.carnis.amalgam_bile_glob": "Едкий органический сгусток.",
  "subtitles.carnis.amalgam_smash": "Амальгама сотрясает землю",
  "subtitles.carnis.organic_creak": "Сухожилие хлещет",
  "entity.carnis.assimilated_player": "Ассимилированный %s",
  "death.attack.organic_consumption": "%1$s был поглощён Ульем"
}
```

