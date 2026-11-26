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
