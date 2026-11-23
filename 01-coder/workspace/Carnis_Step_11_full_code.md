# Шаг 11 — полный исходный код

## CodexCarnisItem.java

```java
package com.carnis.mod.item;

import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.Level;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;

/** Keeps the original carnis:research_journal registry identity. */
public final class CodexCarnisItem extends Item {
    public CodexCarnisItem(Properties properties) {
        super(properties.stacksTo(1).rarity(Rarity.UNCOMMON));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide) {
            DistExecutor.safeRunWhenOn(Dist.CLIENT,
                    () -> com.carnis.mod.client.gui.CodexCarnisScreen::open);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }
}
```

## CodexCarnisScreen.java

```java
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
                    SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 0.8F, 1.4F, false);
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
        addLines(lines, Component.literal(page.title()).withStyle(ChatFormatting.BOLD), TITLE_COLOR);
        lines.add(new Line(FormattedCharSequence.EMPTY, TEXT_COLOR));
        addLines(lines, Component.literal(page.body()), TEXT_COLOR);
        lines.add(new Line(FormattedCharSequence.EMPTY, TEXT_COLOR));
        addLines(lines, Component.literal(page.note()).withStyle(ChatFormatting.ITALIC), NOTE_COLOR);
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
            drawTurn(graphics, 18, "< Назад", spread > 0, inside(localX, localY, 18, 156, 64, 174));
            drawTurn(graphics, 192, "Вперёд >", spread + 1 < spreadCount(), inside(localX, localY, 192, 156, 238, 174));
            graphics.drawCenteredString(font, (spread + 1) + " / " + spreadCount(), 128, 159, 0x5E4935);
            for (int i = 0; i < CodexContent.CHAPTERS.size(); i++) drawTab(graphics, i, localX, localY);
        } finally { graphics.pose().popPose(); }
        int hovered = hoveredTab(localX, localY);
        if (hovered >= 0) graphics.renderTooltip(font,
                Component.literal(NUMERALS[hovered] + ". " + CodexContent.CHAPTERS.get(hovered).title()), mouseX, mouseY);
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
```

## CodexContent.java

```java
package com.carnis.mod.client.gui;

import java.util.List;

/** Field notes are intentionally Russian; each entry is paginated by the active game font. */
public final class CodexContent {
    public record Page(String title, String body, String note) { }
    public record Chapter(String title, List<Page> pages) { }

    public static final List<Chapter> CHAPTERS = List.of(
        new Chapter("Органогенез", List.of(
            new Page("Пульсирующее сердце",
                "Центр колонии пульсирует каждые 100 тиков. Известная ему плоть и жилы дают меру роста в радиусе 32 блоков; сам импульс охватывает 8.",
                "Сердце считает лишь обнаруженную ткань."),
            new Page("Порядок органов",
                "На 25, 50, 75 и 100 заражённых блоках улей закладывает око, стража, бассейн и столп. Для роста требуется живая плоть в 8–24 блоках.",
                "Орган растёт там, где клетка считает место пригодным."),
            new Page("Око Улья",
                "Сенсор замечает чужаков и подаёт тревогу. Игрок обнаруживается в пределах 24 блоков; амальгамы получают сигнал в пределах 32.",
                "Вопль слышен раньше, чем видно зрачок."),
            new Page("Желудочный бассейн",
                "Кислота разлагает предметы и живую ткань. Погибший в ней скот отдаёт ближайшему сердцу 20 единиц биомассы, корова — 30.",
                "Пять единиц урона в секунду — достаточно, чтобы не входить."),
            new Page("Нервный столп",
                "Столп рассеивает новый термический шок в радиусе 32 блоков. Щит сокращает поджог форм Улья, но не делает плоть несгораемой.",
                "Сначала разрушить якорь. Затем очистить очаг."),
            new Page("Страж и Нексус",
                "Пси-якорь вводит скот в транс и ведёт его к бассейну. При четырёх органах и 200 единицах сердце может стать Мозговым Нексусом.",
                "Два дочерних сердца возникают на известной плоти в 48–64 блоках."))),
        new Chapter("Биоценоз", List.of(
            new Page("Остатки биомассы",
                "На твёрдом полу гибель хозяина оставляет рыхлые останки. Они замедляют и чужаков, и существ Улья; близ падали появляются личинки.",
                "В воде и без опоры образец получить не удалось."),
            new Page("Личинка биомассы",
                "Личинка ищет останки в радиусе 16 блоков. Два приёма пищи пробуждают инстинкт зарывания; час на плоти не требуется — достаточно минуты.",
                "Она выбирает рыхлую землю или плоть, но не камень."),
            new Page("Кокон созревания",
                "Мясная луковица держится на потолке или на полу. Через 60–90 секунд её сердцебиение учащается, мешок лопается и выпускает щупальца.",
                "Счёт идёт только в загруженной области."),
            new Page("Щупальце: внедрение",
                "При контакте вероятность заражения мирного хозяина — 85%, монстра — 45%; броня снижает шанс монстра до 30%. Паразит исчезает после броска.",
                "Провал сопровождается шипением и слабым ранением."),
            new Page("Четыре стадии",
                "До 10 секунд — инкубация; до 25 — вены и опухоли; до 30 — разрыв и заражение почвы. Затем монстр мутирует, а мирный хозяин разлагается.",
                "На третьей стадии рана способна убить до превращения."))),
        new Chapter("Аберрации", List.of(
            new Page("Заражённый зомби",
                "Правая рука разрослась в костяной клинок; жгутики обрамляют разорванную голову. У останков он замирает и поглощает биомассу.",
                "Во время питания его взгляд удерживается на одном направлении."),
            new Page("Заражённый скелет",
                "Костяной серп заменяет оружие. Проросший нерв и ядро в рёбрах излучают красный свет; удар лезвием может задеть соседние цели.",
                "Не принимать пустую глазницу за отсутствие зрения."),
            new Page("Заражённый крипер",
                "Раздутые мешки колышутся до разрыва. Вместо обычного взрыва он выбрасывает споры, травит живых и оставляет жилы на прочных гранях.",
                "Признак детонации — бешеное дрожание нервных усиков."),
            new Page("Амальгама плоти",
                "Титанический симбиот возникает из слияния заражённых форм у сердца. Костяные пластины и кислота меняются вместе с адаптацией Улья.",
                "Регенерация поглощением мелких форм — гипотеза, не подтверждённая опытом."))),
        new Chapter("Биотехнологии", List.of(
            new Page("Пневмоинокулятор",
                "Дротик несёт вирусный штамм или очищающий состав. На расстоянии учитывайте падение снаряда и укрытия; магазин расходует подходящие дротики.",
                "Очищающий состав снижает заражение игрока на 35."),
            new Page("Био-очиститель",
                "Поток огня стерилизует живую и окостеневшую плоть, оставляя обугленную ткань. Термический удар обычно вызывает шок заражённого участка.",
                "Действующий нервный столп блокирует новый термошок."),
            new Page("Нейро-броня",
                "Вплетённые сухожилия связывают доспех с нервной системой носителя. Каждая защищённая часть уменьшает заражающую экспозицию на четверть.",
                "Полный комплект скрывает носителя от Ока, но не обещает невидимости всем.")))
    );
    private CodexContent() { }
}
```

## ModItems.java

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

