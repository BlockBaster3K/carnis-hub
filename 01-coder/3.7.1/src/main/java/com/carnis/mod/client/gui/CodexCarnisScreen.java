package com.carnis.mod.client.gui;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.FormattedCharSequence;
import org.lwjgl.glfw.GLFW;
import java.util.ArrayList;
import java.util.List;

public final class CodexCarnisScreen extends Screen {
    private static final ResourceLocation TEXTURE = new ResourceLocation("carnis", "textures/gui/codex_carnis_gui.png");
    private static final int BOOK_WIDTH = 256, BOOK_HEIGHT = 180, TAB_WIDTH = 18;
    private static final int PAGE_WIDTH = 100, LINES_PER_PAGE = 13, LINE_HEIGHT = 10;
    private static final int TITLE_COLOR = 0x6B1D1D, TEXT_COLOR = 0x2B261F, NOTE_COLOR = 0x7A4B2A;
    private static final String[] NUMERALS = {"I", "II", "III", "IV"};
    private record Line(FormattedCharSequence text, int color) { }
    private record Leaf(List<Line> lines) { }

    private final List<List<Leaf>> chapters = new ArrayList<>();
    private int chapter;
    private int spread;
    private float scale;
    private float left;
    private float top;

    public CodexCarnisScreen() { super(Component.translatable("item.carnis.research_journal")); }

    public static void open() {
        Minecraft client = Minecraft.getInstance();
        if (client.player != null && client.level != null) {
            client.level.playLocalSound(client.player.getX(), client.player.getY(), client.player.getZ(),
                    SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 0.8F, 1.0F, false);
        }
        client.setScreen(new CodexCarnisScreen());
    }

    @Override protected void init() {
        scale = Math.min(1.0F, Math.min((width - 8.0F) / (BOOK_WIDTH + TAB_WIDTH), (height - 8.0F) / BOOK_HEIGHT));
        scale = Math.max(0.05F, scale);
        left = (width - (BOOK_WIDTH + TAB_WIDTH) * scale) / 2.0F;
        top = (height - BOOK_HEIGHT * scale) / 2.0F;
        chapters.clear();
        for (CodexContent.Chapter section : CodexContent.CHAPTERS) {
            List<Leaf> leaves = new ArrayList<>();
            for (CodexContent.Page page : section.pages()) paginate(page, leaves);
            if ((leaves.size() & 1) != 0) leaves.add(new Leaf(List.of()));
            chapters.add(List.copyOf(leaves));
        }
        chapter = Math.min(chapter, chapters.size() - 1);
        spread = Math.min(spread, spreadCount() - 1);
    }

    private void paginate(CodexContent.Page page, List<Leaf> leaves) {
        List<Line> lines = new ArrayList<>();
        addLines(lines, Component.translatable(page.title()).withStyle(ChatFormatting.BOLD), TITLE_COLOR);
        lines.add(new Line(FormattedCharSequence.EMPTY, TEXT_COLOR));
        addLines(lines, Component.translatable(page.body()), TEXT_COLOR);
        lines.add(new Line(FormattedCharSequence.EMPTY, TEXT_COLOR));
        addLines(lines, Component.translatable(page.note()).withStyle(ChatFormatting.ITALIC), NOTE_COLOR);
        for (int i = 0; i < lines.size(); i += LINES_PER_PAGE) {
            leaves.add(new Leaf(List.copyOf(lines.subList(i, Math.min(lines.size(), i + LINES_PER_PAGE)))));
        }
    }

    private void addLines(List<Line> target, Component text, int color) {
        for (FormattedCharSequence line : font.split(text, PAGE_WIDTH)) target.add(new Line(line, color));
    }

    private int spreadCount() { return Math.max(1, (chapters.get(chapter).size() + 1) / 2); }
    private void pageSound() {
        Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1.0F));
    }
    private void turn(int amount) {
        int next = Math.max(0, Math.min(spreadCount() - 1, spread + amount));
        if (next != spread) { spread = next; pageSound(); }
    }
    private void selectChapter(int index) {
        if (index != chapter || spread != 0) { chapter = index; spread = 0; pageSound(); }
    }

    @Override public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        float localX = (mouseX - left) / scale, localY = (mouseY - top) / scale;
        graphics.pose().pushPose();
        try {
            graphics.pose().translate(left, top, 0);
            graphics.pose().scale(scale, scale, 1.0F);
            graphics.blit(TEXTURE, 0, 0, 0, 0, BOOK_WIDTH, BOOK_HEIGHT, 256, 256);
            List<Leaf> leaves = chapters.get(chapter);
            drawLeaf(graphics, leaves, spread * 2, 18);
            drawLeaf(graphics, leaves, spread * 2 + 1, 138);
            drawTurn(graphics, 18, Component.translatable("codex.carnis.previous").getString(), spread > 0, inside(localX, localY, 18, 156, 64, 174));
            drawTurn(graphics, 192, Component.translatable("codex.carnis.next").getString(), spread + 1 < spreadCount(), inside(localX, localY, 192, 156, 238, 174));
            graphics.drawCenteredString(font, (spread + 1) + " / " + spreadCount(), 128, 159, 0x5E4935);
            for (int i = 0; i < CodexContent.CHAPTERS.size(); i++) drawTab(graphics, i, localX, localY);
        } finally { graphics.pose().popPose(); }
        int hovered = hoveredTab(localX, localY);
        if (hovered >= 0) graphics.renderTooltip(font,
                Component.literal(NUMERALS[hovered] + ". ").append(Component.translatable("codex.carnis.tab." + hovered)), mouseX, mouseY);
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    private void drawLeaf(GuiGraphics graphics, List<Leaf> leaves, int index, int x) {
        if (index >= leaves.size()) return;
        int y = 16;
        for (Line line : leaves.get(index).lines()) {
            graphics.drawString(font, line.text(), x, y, line.color(), false);
            y += LINE_HEIGHT;
        }
    }

    private void drawTurn(GuiGraphics graphics, int x, String label, boolean enabled, boolean hovered) {
        graphics.fill(x, 156, x + 46, 174, enabled ? (hovered ? 0xBBA76543 : 0x886E4D38) : 0x553A3026);
        graphics.drawCenteredString(font, label, x + 23, 161, enabled ? 0xFFF1DCB3 : 0xFF918577);
    }

    private void drawTab(GuiGraphics graphics, int index, float mouseX, float mouseY) {
        int y = 16 + index * 34;
        boolean hover = inside(mouseX, mouseY, 256, y, 274, y + 28);
        int color = index == chapter ? 0xFF98423E : hover ? 0xFF704337 : 0xFF50352B;
        graphics.fill(256, y, 274, y + 28, 0xFF352219);
        graphics.fill(257, y + 1, 273, y + 27, color);
        // Each icon is drawn inside its tab: heart, cocoon, blade, injector.
        int ink = 0xFFE8CC94;
        switch (index) {
            case 0 -> { graphics.fill(261, y + 7, 264, y + 10, ink); graphics.fill(266, y + 7, 269, y + 10, ink); graphics.fill(261, y + 10, 269, y + 13, ink); graphics.fill(263, y + 13, 267, y + 16, ink); }
            case 1 -> { graphics.fill(262, y + 7, 268, y + 16, ink); graphics.fill(261, y + 9, 269, y + 14, ink); graphics.fill(263, y + 10, 267, y + 11, color); }
            case 2 -> { graphics.fill(267, y + 6, 269, y + 12, ink); graphics.fill(265, y + 10, 267, y + 15, ink); graphics.fill(262, y + 14, 266, y + 16, ink); }
            case 3 -> { graphics.fill(262, y + 8, 268, y + 12, ink); graphics.fill(268, y + 9, 271, y + 10, ink); graphics.fill(260, y + 7, 262, y + 13, ink); graphics.fill(264, y + 12, 266, y + 16, ink); }
        }
        graphics.drawCenteredString(font, NUMERALS[index], 265, y + 18, 0xFFE6CBA3);
    }

    private int hoveredTab(float x, float y) {
        for (int i = 0; i < CodexContent.CHAPTERS.size(); i++)
            if (inside(x, y, 256, 16 + i * 34, 274, 44 + i * 34)) return i;
        return -1;
    }
    private static boolean inside(float x, float y, int x0, int y0, int x1, int y1) {
        return x >= x0 && x < x1 && y >= y0 && y < y1;
    }

    @Override public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (button != 0) return super.mouseClicked(mouseX, mouseY, button);
        float x = (float)((mouseX - left) / scale), y = (float)((mouseY - top) / scale);
        int tab = hoveredTab(x, y);
        if (tab >= 0) { selectChapter(tab); return true; }
        if (inside(x, y, 18, 156, 64, 174)) { turn(-1); return true; }
        if (inside(x, y, 192, 156, 238, 174)) { turn(1); return true; }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode == GLFW.GLFW_KEY_LEFT || keyCode == GLFW.GLFW_KEY_PAGE_UP) { turn(-1); return true; }
        if (keyCode == GLFW.GLFW_KEY_RIGHT || keyCode == GLFW.GLFW_KEY_PAGE_DOWN) { turn(1); return true; }
        if (keyCode >= GLFW.GLFW_KEY_1 && keyCode <= GLFW.GLFW_KEY_4) { selectChapter(keyCode - GLFW.GLFW_KEY_1); return true; }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }
    @Override public boolean isPauseScreen() { return false; }
}
