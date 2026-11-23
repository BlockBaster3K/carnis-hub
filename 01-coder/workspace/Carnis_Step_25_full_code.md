# Carnis 3.0.0 — шаг 25: релизный аудит

Рабочий проект: `/home/user/Carnis-Adaptive-Hivemind`. Ни сборка, ни запуск игры не производились. Вердикт: **не подтверждена готовность к релизу**; требуется проверка Архитектора и локальные испытания. Ниже приведены полные текстовые исходники изменённых файлов, включая оба полных языка. PNG — отдельные файлы в проекте, не текстовый код.

## Архитектура
Реестры Forge задают блоки, предметы, сущности, события, частицы и звуки; сетевые данные и серверные обработчики координируют инфекцию и улей. Клиентские рендереры GeckoLib, экран кодекса и звук отделены от серверной логики. Datagen поддерживает ресурсы и локализации; main и generated включены в ресурсы проекта.

## Инженерный аудит-лог для Архитектора
Номера 1–6 — укрупнённые области ранее выполненных работ, а не подтверждённая реконструкция названий исходного плана. Шаги 7–9 ранее приняты; представление остальных не означает приёмку.

1. Реестры Forge и версии — оформлены, совместимость сборкой не проверена.
2. Базовые блоки и распространение — имеются; `InfectionTickQueue.processPosition` пуст, полноценность очереди не подтверждена.
3. Инфекция и эффекты — реализованы, серверные сценарии и персистентность требуют проверки.
4. Анимации/рендер GeckoLib — исходники и ресурсы имеются, игра не проверялась.
5. Предметы, рецепты, ресурсы — имеются; глобальная пригодность всех моделей и рецептов не доказана.
6. Дротики и события — реализованы; совместимость и поведение на сервере не проверены.
7. Личинка и жизненный цикл — ранее принято; runtime повторно не проверен.
8. Паразитизм и инкубация — ранее принято; runtime повторно не проверен.
9. Останки и органические блоки — ранее принято; runtime повторно не проверен.
10. Сеть Улья, сердце, страж, Нексус — реализованы; старые миры могут быть неполно индексированы.
11. Кодекс — экран и 18 записей локализованы на RU/EN; точность всех утверждений кодекса не доказана.
12. Био-очиститель и термошок — реализованы; проверка конуса и взаимодействия щита нужна в игре.
13. Нейроброня — реализована; HUD и баланс требуют испытаний.
14. Координация роя — реализована; у стража и Нексуса нет боевых goals, у личинки атака не гарантирована.
15. Амальгама — навыки реализованы; уничтожение мелких существ через discard не даёт дропа, тесты не проводились.
16. Игровая инфекция и сеть — протокол 2 требует одинаковых версий; смерть, тотем, keepInventory и синхронизация не проверены.
17. Генерация — **не готова к приёмке**: нет гарантий количества и отката, проверки структур и полной индексации; возможны проблемы на границах чанков.
18. Органы и рендер — реализованы, но pulse при разряде не запускается; визуал и длительность щита требуют проверки.
19. Мох и шипы — мох является ковром, влажность проверяется по соседней воде; физика не проверена.
20. Пустулы и ростки — начисление только игрокам, волна затрагивает и улей; взаимодействия и визуал не проверены.
21. Лечение дротиками — реализовано; отражение, перенос NBT, старые миры и полное отключение способностей не проверены.
22. Питание и анимация скелета — есть риск начисления биомассы без созданных останков; визуал не испытан.
23. Крипер и споровое облако — возможно дополнительное ванильное облако; сохранение UUID и визуал требуют проверки.
24. Око и фоновый звук — слушатель проверяет позицию события в 16 блоках и исключает существ по интерфейсу или тегу. Удалён противоречащий отсев источника за 12 блоками, в том числе для владельцев снарядов. Порядок регистрации слушателя и звук не проверены в игре; это не ванильная система вибраций с задержкой/шерстью.
25. Релизная упаковка — версия 3.0.0, зависимости, вкладка и локализации обновлены. Статическая проверка не заменяет локальную сборку или испытания.

### Проверки и ограничения
- 198 JSON разобраны; у локализаций 226 ключей на язык, множества ключей равны. Все буквальные `add("ключ", "значение")` провайдера соответствуют JSON, дубликатов буквальных ключей нет. Это не доказывает семантическую точность всех переводов или всех динамических ключей.
- У всех 41 зарегистрированных предметов найдены item-модели; вкладка включает все 41 без повторов. Три яйца добавлены для зарегистрированных типов; для них созданы собственные текстуры. Исправлены пять отсутствовавших явных ссылок на текстуры моделей. Полный аудит геометрии, Geo, ванильных parents, анимаций и visual QA не выполнен.
- В `src` нет точного реестрового ID `carnis:veins`; используются `flesh_veins`, `neural_moss`, `sinew_spikes`. Миграции старого `carnis:veins` нет: старые миры требуют отдельного плана и теста. Теги hive_members, burrowable, infectious_surfaces присутствуют, но поведение и полнота наборов не доказаны.
- Имеются оставшиеся нелокализованные строки, например trait в NeuroWeavingEvents и заголовок команды. Ряд старых ключей кодекса не используется экраном и может содержать устаревшие сведения. Строгое требование 100% локализации и двух строк тултипа для каждого предмета **не выполнено**: общий обработчик Shift выдаёт одну строку, некоторые предметы добавляют дополнительные собственные строки.
- `processResources` включает generated и main; одинаковых относительных имён файлов на момент проверки нет. Значения dependencies записаны буквально. Динамическая доступность ассетов и фактическое разрешение версий Forge/GeckoLib не тестировались.
- Сборка, запуск игры, загрузка старого мира и прослушивание аудио не выполнялись. Требуются локальные compile/run и регрессионные тесты до релиза.

## Полные исходники и текстовые ресурсы шага 25

### `gradle.properties`

```properties
# Gradle settings
org.gradle.jvmargs=-Xmx3G -Dfile.encoding=UTF-8
org.gradle.daemon=false
org.gradle.parallel=false
org.gradle.workers.max=2
org.gradle.caching=true
org.gradle.configuration-cache=false
org.gradle.warning.mode=all

# Project properties
mod_id=carnis
mod_name=Carnis: Adaptive Hivemind
mod_license=MIT
mod_version=3.0.0
mod_author=BlockBaster3K
mod_authors=BlockBaster3K
mod_group_id=com.carnis.mod
mod_description=The Living Swarm Update: Hive evolution, four parasitic stages, organogenesis, the Flesh Amalgam, Neuro-Resonator armor, the Bio-Purifier and Codex Carnis.

# Versions
minecraft_version=1.20.1
minecraft_version_range=[1.20.1]
forge_version=47.4.5
forge_version_range=[47.1.0,)
loader_version_range=[47,)
geckolib_version=4.4.4
geckolib_version_range=[4.4.4,)
mapping_channel=official
mapping_version=1.20.1

```

### `src/main/resources/META-INF/mods.toml`

```toml
modLoader="javafml"
loaderVersion="[47,)"
license="MIT"

[[mods]]
modId="carnis"
version="3.0.0"
displayName="Carnis: Adaptive Hivemind"
authors="BlockBaster3K"
description='''The Living Swarm Update — version 3.0.0. An adaptive organic Hive evolves through four stages of parasitism, spreading living tissue and developing macroscopic organs. Explore the Pulsing Heart and its network, confront the Flesh Amalgam, and survive the Swarm with Neuro-Resonator armor, the Bio-Purifier, the Pneumatic Inoculator and the Codex Carnis.'''

[[dependencies.carnis]]
modId="forge"
mandatory=true
versionRange="[47.1.0,)"
ordering="NONE"
side="BOTH"

[[dependencies.carnis]]
modId="minecraft"
mandatory=true
versionRange="[1.20.1]"
ordering="NONE"
side="BOTH"

[[dependencies.carnis]]
modId="geckolib"
mandatory=true
versionRange="[4.4.4,)"
ordering="AFTER"
side="BOTH"

```

### `src/main/resources/pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 15,
    "description": "Carnis: Adaptive Hivemind 3.0.0 — The Living Swarm Update (Minecraft 1.20.1)"
  }
}

```

### `src/main/java/com/carnis/mod/init/ModCreativeTabs.java`

```java
package com.carnis.mod.init;

import com.carnis.mod.CarnisMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, CarnisMod.MOD_ID);
    public static final RegistryObject<CreativeModeTab> CARNIS_TAB = CREATIVE_TABS.register("carnis", () ->
            CreativeModeTab.builder().title(Component.translatable("carnis.tab"))
                    .icon(() -> ModItems.PULSING_HEART.get().getDefaultInstance())
                    .displayItems((parameters, output) -> {
                        // Organs and cores
                        output.accept(ModItems.PULSING_HEART.get());
                        output.accept(ModItems.HIVE_EYE.get());
                        output.accept(ModItems.STOMACH_POOL.get());
                        output.accept(ModItems.NERVE_PILLAR.get());
                        // Tissues and flora
                        output.accept(ModItems.LIVING_FLESH.get());
                        output.accept(ModItems.OSSIFIED_FLESH.get());
                        output.accept(ModItems.CHARRED_FLESH.get());
                        output.accept(ModItems.FIREPROOF_FLESH.get());
                        output.accept(ModItems.FLESH_VEINS.get());
                        output.accept(ModItems.NEURAL_MOSS.get());
                        output.accept(ModItems.SINEW_SPIKES.get());
                        output.accept(ModItems.PUSTULE_CLUSTER.get());
                        output.accept(ModItems.SPORE_SPROUT.get());
                        output.accept(ModItems.FLESH_BULB.get());
                        output.accept(ModItems.BIOMASS_REMAINS.get());
                        // Field equipment
                        output.accept(ModItems.RESEARCH_JOURNAL.get());
                        output.accept(ModItems.BIO_PURIFIER.get());
                        output.accept(ModItems.PNEUMATIC_INOCULATOR.get());
                        output.accept(ModItems.PURIFICATION_SERUM.get());
                        output.accept(ModItems.PURIFICATION_DART.get());
                        output.accept(ModItems.VIRAL_DART.get());
                        output.accept(ModItems.NEURAL_BINDING_MATRIX.get());
                        // Neuro-resonator armor
                        output.accept(ModItems.NEURO_RESONATOR_HELMET.get());
                        output.accept(ModItems.NEURO_RESONATOR_CHESTPLATE.get());
                        output.accept(ModItems.NEURO_RESONATOR_LEGGINGS.get());
                        output.accept(ModItems.NEURO_RESONATOR_BOOTS.get());
                        // Materials
                        output.accept(ModItems.CREEPING_TENDRILS.get());
                        output.accept(ModItems.TAINTED_SLUDGE_BUCKET.get());
                        // Spawn eggs
                        output.accept(ModItems.INFECTED_ZOMBIE_SPAWN_EGG.get());
                        output.accept(ModItems.INFECTED_SKELETON_SPAWN_EGG.get());
                        output.accept(ModItems.INFECTED_CREEPER_SPAWN_EGG.get());
                        output.accept(ModItems.BIOMASS_MAGGOT_SPAWN_EGG.get());
                        output.accept(ModItems.PARASITIC_TENDRIL_SPAWN_EGG.get());
                        output.accept(ModItems.FLESH_AMALGAM_SPAWN_EGG.get());
                        output.accept(ModItems.HIVE_SENTINEL_SPAWN_EGG.get());
                        output.accept(ModItems.CEREBRAL_NEXUS_SPAWN_EGG.get());
                        // Existing additional items remain accessible.
                        output.accept(ModItems.INFECTED_SPIDER_SPAWN_EGG.get());
                        output.accept(ModItems.ANTIBIOTICS.get());
                        output.accept(ModItems.BONE_SCYTHE_ARM.get());
                        output.accept(ModItems.FLESH_SPAT.get());
                        output.accept(ModItems.AMALGAM_BILE_GLOB.get());
                    }).build());
    private ModCreativeTabs() { }
    public static void register(IEventBus modEventBus) { CREATIVE_TABS.register(modEventBus); }
}

```

### `src/main/java/com/carnis/mod/init/ModItems.java`

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
    public static final RegistryObject<ForgeSpawnEggItem> PARASITIC_TENDRIL_SPAWN_EGG = ITEMS.register(
            "parasitic_tendril_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.PARASITIC_TENDRIL,
                    0x512b35, 0xd8a178, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> HIVE_SENTINEL_SPAWN_EGG = ITEMS.register(
            "hive_sentinel_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.HIVE_SENTINEL,
                    0x482436, 0x99ca75, new Item.Properties()));
    public static final RegistryObject<ForgeSpawnEggItem> CEREBRAL_NEXUS_SPAWN_EGG = ITEMS.register(
            "cerebral_nexus_spawn_egg", () -> new ForgeSpawnEggItem(ModEntities.CEREBRAL_NEXUS,
                    0x4b2334, 0xd78c7b, new Item.Properties()));
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
    public static final RegistryObject<Item> AMALGAM_BILE_GLOB = ITEMS.register("amalgam_bile_glob", () -> new Item(new Item.Properties()));
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
            () -> new com.carnis.mod.item.OrganBlockItem(ModBlocks.NERVE_PILLAR.get(), new Item.Properties()));
    public static final RegistryObject<Item> VIRAL_DART = ITEMS.register("viral_dart",
            () -> new com.carnis.mod.item.ViralDartItem(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<Item> PURIFICATION_DART = ITEMS.register("purification_dart",
            () -> new com.carnis.mod.item.PurificationDartItem(new Item.Properties().stacksTo(64)));
    public static final RegistryObject<PneumaticInoculatorItem> PNEUMATIC_INOCULATOR = ITEMS.register(
            "pneumatic_inoculator", () -> new PneumaticInoculatorItem(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> CREEPING_TENDRILS = ITEMS.register(
            "creeping_tendrils", () -> new BlockItem(ModBlocks.CREEPING_TENDRILS.get(), new Item.Properties()));
    public static final RegistryObject<Item> PUSTULE_CLUSTER = ITEMS.register(
            "pustule_cluster", () -> new com.carnis.mod.item.OrganBlockItem(ModBlocks.PUSTULE_CLUSTER.get(), new Item.Properties()));
    public static final RegistryObject<Item> STOMACH_POOL = ITEMS.register(
            "stomach_pool", () -> new com.carnis.mod.item.OrganBlockItem(ModBlocks.STOMACH_POOL.get(), new Item.Properties()));

    public static final RegistryObject<Item> SPORE_SPROUT = ITEMS.register(
            "spore_sprout", () -> new BlockItem(ModBlocks.SPORE_SPROUT.get(), new Item.Properties()));
    public static final RegistryObject<Item> NEURAL_MOSS = ITEMS.register(
            "neural_moss", () -> new com.carnis.mod.item.OrganicTooltipBlockItem(ModBlocks.NEURAL_MOSS.get(), new Item.Properties(), "neural_moss"));

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

### `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java`

```java
package com.carnis.mod.block.entity;

import com.carnis.mod.block.NeuralMossBlock;
import com.carnis.mod.entity.ai.HiveSwarmCoordinator;
import com.carnis.mod.event.NeuroArmorEventHandler;
import com.carnis.mod.init.ModBlockEntities;
import com.carnis.mod.init.ModSounds;
import com.carnis.mod.world.HiveNetwork;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoBlockEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
import javax.annotation.Nullable;
import java.lang.ref.WeakReference;

public final class HiveEyeBlockEntity extends BlockEntity implements GeoBlockEntity {
    public static final int SCAN_INTERVAL_TICKS = 20;
    public static final double PLAYER_SCAN_RADIUS = 18D;
    public static final double HIVEMIND_ALERT_RADIUS = 28D;
    private static final java.util.Set<String> AUDIBLE_EVENTS = java.util.Set.of(
            "step", "hit_ground", "projectile_shoot", "projectile_land", "block_destroy",
            "entity_action", "entity_interact", "entity_damage", "entity_roar", "entity_place");
    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private final net.minecraft.world.level.gameevent.GameEventListener vibrationListener = new EyeListener();

    public net.minecraft.world.level.gameevent.GameEventListener getVibrationListener() { return vibrationListener; }

    private final class EyeListener implements net.minecraft.world.level.gameevent.GameEventListener {
        private final net.minecraft.world.level.gameevent.PositionSource source =
                new net.minecraft.world.level.gameevent.BlockPositionSource(worldPosition);
        @Override public net.minecraft.world.level.gameevent.PositionSource getListenerSource() { return source; }
        @Override public int getListenerRadius() { return 16; }
        @Override public boolean handleGameEvent(ServerLevel level, net.minecraft.world.level.gameevent.GameEvent event,
                net.minecraft.world.level.gameevent.GameEvent.Context context, Vec3 position) {
            var id = net.minecraft.core.registries.BuiltInRegistries.GAME_EVENT.getKey(event);
            if (id == null || !id.getNamespace().equals("minecraft") || !AUDIBLE_EVENTS.contains(id.getPath())) return false;
            net.minecraft.world.entity.Entity origin = context.sourceEntity();
            if (origin instanceof net.minecraft.world.entity.projectile.Projectile projectile && projectile.getOwner() != null)
                origin = projectile.getOwner();
            if (!(origin instanceof LivingEntity living) || !isTarget(living)
                    || living instanceof Player player && (player.isSteppingCarefully() || NeuroArmorEventHandler.hasFullSet(player))
                    || position.distanceToSqr(Vec3.atCenterOf(worldPosition)) > 256D) return false;
            hear(level, living);
            return true;
        }
    }
    private WeakReference<LivingEntity> tracked = new WeakReference<>(null);
    private long alertUntil;
    private boolean clientAlert;
    private float yaw, pitch, previousYaw, previousPitch;
    public HiveEyeBlockEntity(BlockPos pos, BlockState state) { super(ModBlockEntities.HIVE_EYE.get(), pos, state); }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return animationCache; }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "blink", 0, state -> state.setAndContinue(RawAnimation.begin()
                .thenLoop(isAlert() ? "animation.hive_eye.alert" : "animation.hive_eye.idle"))));
    }
    public boolean isAlert() { return level != null && (level.isClientSide ? clientAlert : level.getGameTime() < alertUntil); }
    public float trackingYaw(float partial) { return Mth.lerp(partial, previousYaw, yaw); }
    public float trackingPitch(float partial) { return Mth.lerp(partial, previousPitch, pitch); }
    @Override public CompoundTag getUpdateTag() {
        CompoundTag tag = new CompoundTag(); tag.putBoolean("Alert", isAlert()); return tag;
    }
    @Nullable @Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
    @Override public void handleUpdateTag(CompoundTag tag) { clientAlert = tag.getBoolean("Alert"); }
    @Override public void onDataPacket(Connection connection, ClientboundBlockEntityDataPacket packet) {
        if (packet.getTag() != null) handleUpdateTag(packet.getTag());
    }
    public static void serverTick(Level world, BlockPos pos, BlockState state, HiveEyeBlockEntity eye) {
        if (!(world instanceof ServerLevel level)) return;
        if (eye.alertUntil != 0 && level.getGameTime() >= eye.alertUntil) {
            eye.alertUntil = 0;
            level.sendBlockUpdated(pos, state, state, 3);
        }
        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), SCAN_INTERVAL_TICKS), SCAN_INTERVAL_TICKS) == 0) {
            HiveNetwork.observe(level, pos, state, true);
            LivingEntity nearest = eye.findNearest(level);
            if (nearest != null) nearest.addEffect(new MobEffectInstance(MobEffects.GLOWING, 100, 0));
        }
    }
    /** Called when a tracked game event has an eligible living source. */
    public void hear(ServerLevel level, LivingEntity source) {
        // Range is checked against the event position by EyeListener, not the
        // shooter's position: a projectile may land far from its owner.
        if (!isTarget(source)) return;
        boolean wasAlert = isAlert();
        alertUntil = level.getGameTime() + 60;
        if (!wasAlert) {
            level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
            level.playSound(null, worldPosition, ModSounds.HIVE_ALARM.get(), SoundSource.BLOCKS, 1.25F, .92F);
            level.sendParticles(ParticleTypes.ELECTRIC_SPARK, worldPosition.getX() + .5D, worldPosition.getY() + .8D,
                    worldPosition.getZ() + .5D, 12, .25D, .2D, .25D, .02D);
        }
        HiveSwarmCoordinator.eyeAlarm(level, worldPosition, source);
    }
    private static boolean isTarget(LivingEntity entity) {
        return entity.isAlive() && !entity.isSpectator() && !NeuralMossBlock.isHive(entity)
                && (!(entity instanceof Player player) || !player.isCreative() && !NeuroArmorEventHandler.hasFullSet(player));
    }
    @Nullable private LivingEntity findNearest(Level level) {
        Vec3 center = Vec3.atCenterOf(worldPosition);
        LivingEntity nearest = null;
        double best = PLAYER_SCAN_RADIUS * PLAYER_SCAN_RADIUS;
        for (LivingEntity candidate : level.getEntitiesOfClass(LivingEntity.class,
                AABB.ofSize(center, 36, 36, 36), HiveEyeBlockEntity::isTarget)) {
            double d = candidate.position().distanceToSqr(center);
            if (d <= best) { best = d; nearest = candidate; }
        }
        return nearest;
    }
    public static void clientTick(Level level, BlockPos pos, BlockState state, HiveEyeBlockEntity eye) {
        eye.previousYaw = eye.yaw;
        eye.previousPitch = eye.pitch;
        if (Math.floorMod(level.getGameTime() + Math.floorMod(pos.asLong(), 10), 10) == 0)
            eye.tracked = new WeakReference<>(eye.findNearest(level));
        LivingEntity target = eye.tracked.get();
        float wantedYaw = 0, wantedPitch = 0;
        if (target != null && isTarget(target) && target.position().distanceToSqr(Vec3.atCenterOf(pos)) <= 324D) {
            Vec3 delta = target.getEyePosition().subtract(pos.getX() + .5D, pos.getY() + .5625D, pos.getZ() + .5D);
            double horizontal = Math.sqrt(delta.x * delta.x + delta.z * delta.z);
            if (horizontal > 1.0E-5D) wantedYaw = (float) Mth.clamp(Math.atan2(delta.x, -delta.z), -.7D, .7D);
            wantedPitch = (float) Mth.clamp(-Math.atan2(delta.y, Math.max(horizontal, .001D)), -.6D, .6D);
        }
        eye.yaw += (wantedYaw - eye.yaw) * .18F;
        eye.pitch += (wantedPitch - eye.pitch) * .18F;
    }
}

```

### `src/main/java/com/carnis/mod/client/gui/CodexContent.java`

```java
package com.carnis.mod.client.gui;

import java.util.List;

/** Field notes use translation keys; each entry is paginated by the active game font. */
public final class CodexContent {
    public record Page(String title, String body, String note) { }
    public record Chapter(String title, List<Page> pages) { }

    public static final List<Chapter> CHAPTERS = List.of(
        new Chapter("codex.carnis.tab.0", List.of(
            new Page("codex.carnis.entry.0.title", "codex.carnis.entry.0.body", "codex.carnis.entry.0.note"),
            new Page("codex.carnis.entry.1.title", "codex.carnis.entry.1.body", "codex.carnis.entry.1.note"),
            new Page("codex.carnis.entry.2.title", "codex.carnis.entry.2.body", "codex.carnis.entry.2.note"),
            new Page("codex.carnis.entry.3.title", "codex.carnis.entry.3.body", "codex.carnis.entry.3.note"),
            new Page("codex.carnis.entry.4.title", "codex.carnis.entry.4.body", "codex.carnis.entry.4.note"),
            new Page("codex.carnis.entry.5.title", "codex.carnis.entry.5.body", "codex.carnis.entry.5.note"))),
        new Chapter("codex.carnis.tab.1", List.of(
            new Page("codex.carnis.entry.6.title", "codex.carnis.entry.6.body", "codex.carnis.entry.6.note"),
            new Page("codex.carnis.entry.7.title", "codex.carnis.entry.7.body", "codex.carnis.entry.7.note"),
            new Page("codex.carnis.entry.8.title", "codex.carnis.entry.8.body", "codex.carnis.entry.8.note"),
            new Page("codex.carnis.entry.9.title", "codex.carnis.entry.9.body", "codex.carnis.entry.9.note"),
            new Page("codex.carnis.entry.10.title", "codex.carnis.entry.10.body", "codex.carnis.entry.10.note"))),
        new Chapter("codex.carnis.tab.2", List.of(
            new Page("codex.carnis.entry.11.title", "codex.carnis.entry.11.body", "codex.carnis.entry.11.note"),
            new Page("codex.carnis.entry.12.title", "codex.carnis.entry.12.body", "codex.carnis.entry.12.note"),
            new Page("codex.carnis.entry.13.title", "codex.carnis.entry.13.body", "codex.carnis.entry.13.note"),
            new Page("codex.carnis.entry.14.title", "codex.carnis.entry.14.body", "codex.carnis.entry.14.note"))),
        new Chapter("codex.carnis.tab.3", List.of(
            new Page("codex.carnis.entry.15.title", "codex.carnis.entry.15.body", "codex.carnis.entry.15.note"),
            new Page("codex.carnis.entry.16.title", "codex.carnis.entry.16.body", "codex.carnis.entry.16.note"),
            new Page("codex.carnis.entry.17.title", "codex.carnis.entry.17.body", "codex.carnis.entry.17.note")))
    );
    private CodexContent() { }
}

```

### `src/main/java/com/carnis/mod/client/gui/CodexCarnisScreen.java`

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

```

### `src/main/java/com/carnis/mod/datagen/ModLanguageProvider.java`

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
        add("carnis.tab", "Carnis: Adaptive Hivemind");
        add("item.carnis.parasitic_tendril_spawn_egg", "Parasitic Tendril Spawn Egg");
        add("tooltip.carnis.parasitic_tendril_spawn_egg", "Spawns a parasitic tendril.");
        add("item.carnis.hive_sentinel_spawn_egg", "Hive Sentinel Spawn Egg");
        add("tooltip.carnis.hive_sentinel_spawn_egg", "Spawns a hive sentinel.");
        add("item.carnis.cerebral_nexus_spawn_egg", "Cerebral Nexus Spawn Egg");
        add("tooltip.carnis.cerebral_nexus_spawn_egg", "Spawns a cerebral nexus.");
        add("tooltip.carnis.biomass_remains", "Organic remains left by a host.");
        add("tooltip.carnis.flesh_bulb", "An incubating organic sac.");
        add("tooltip.carnis.sinew_spikes", "Piercing growths slow creatures.");
        add("tooltip.carnis.biomass_maggot_spawn_egg", "Spawns a biomass maggot.");
        add("codex.carnis.previous", "< Back");
        add("codex.carnis.next", "Next >");
        add("codex.carnis.tab.0", "Organogenesis");
        add("codex.carnis.tab.1", "Biocenosis");
        add("codex.carnis.tab.2", "Aberrations");
        add("codex.carnis.tab.3", "Biotechnology");
        add("codex.carnis.entry.0.title", "Pulsing Heart");
        add("codex.carnis.entry.0.body", "The colony core pulses every 100 ticks. Known flesh and veins measure growth within 32 blocks; the pulse itself reaches 8.");
        add("codex.carnis.entry.0.note", "The heart counts only tissue it has discovered.");
        add("codex.carnis.entry.1.title", "Order of organs");
        add("codex.carnis.entry.1.body", "At 25, 50, 75 and 100 infected blocks the Hive develops an eye, sentinel, pool and pillar. Growth requires living flesh 8–24 blocks away.");
        add("codex.carnis.entry.1.note", "Organs grow where the cell finds a suitable place.");
        add("codex.carnis.entry.2.title", "Hive Eye");
        add("codex.carnis.entry.2.body", "The sensor detects outsiders within 18 blocks and alerts free Hive mobs within 28 blocks.");
        add("codex.carnis.entry.2.note", "The scream is heard before the pupil is seen.");
        add("codex.carnis.entry.3.title", "Stomach Pool");
        add("codex.carnis.entry.3.body", "Acid dissolves items and living tissue. Livestock killed within it yields 20 biomass to a nearby heart, or 30 for a cow.");
        add("codex.carnis.entry.3.note", "Five damage per second is reason enough to stay out.");
        add("codex.carnis.entry.4.title", "Nerve Pillar");
        add("codex.carnis.entry.4.body", "The pillar blocks new thermal shock within 32 blocks. Its shield reduces ignition of Hive forms but does not make flesh fireproof.");
        add("codex.carnis.entry.4.note", "Destroy the anchor first. Then cleanse the site.");
        add("codex.carnis.entry.5.title", "Sentinel and Nexus");
        add("codex.carnis.entry.5.body", "A psychic anchor draws livestock into a trance and guides it to a pool. With four organs and 200 biomass the heart can become a Cerebral Nexus.");
        add("codex.carnis.entry.5.note", "Two daughter hearts appear on known flesh 48–64 blocks away.");
        add("codex.carnis.entry.6.title", "Biomass Remains");
        add("codex.carnis.entry.6.body", "A host dying on solid ground leaves loose remains. They slow outsiders and Hive creatures alike; maggots appear near carrion.");
        add("codex.carnis.entry.6.note", "No sample was obtained in water or without support.");
        add("codex.carnis.entry.7.title", "Biomass Maggot");
        add("codex.carnis.entry.7.body", "The maggot seeks remains within 16 blocks. Two meals awaken its burrowing instinct; one minute on flesh is enough.");
        add("codex.carnis.entry.7.note", "It chooses loose soil or flesh, not stone.");
        add("codex.carnis.entry.8.title", "Maturing Cocoon");
        add("codex.carnis.entry.8.body", "The Flesh Bulb attaches to ceilings or floors. After 60–90 seconds its heartbeat quickens and the sac bursts, releasing tendrils.");
        add("codex.carnis.entry.8.note", "Time passes only in loaded areas.");
        add("codex.carnis.entry.9.title", "Tendril: implantation");
        add("codex.carnis.entry.9.body", "Contact infects a peaceful host with 85% probability or a monster with 45%; armor reduces the monster chance to 30%. The parasite vanishes after its attempt.");
        add("codex.carnis.entry.9.note", "Failure brings a hiss and a minor wound.");
        add("codex.carnis.entry.10.title", "Four stages");
        add("codex.carnis.entry.10.body", "Up to 10 seconds: incubation; up to 25: veins and growths; up to 30: rupture and soil infection. Then a monster mutates and a peaceful host decomposes.");
        add("codex.carnis.entry.10.note", "In the third stage the wound can kill before transformation.");
        add("codex.carnis.entry.11.title", "Infected Zombie");
        add("codex.carnis.entry.11.body", "Its right arm has grown into a bone blade; tendrils frame its torn head. Near remains it stops and consumes biomass.");
        add("codex.carnis.entry.11.note", "While feeding, its gaze holds one direction.");
        add("codex.carnis.entry.12.title", "Infected Skeleton");
        add("codex.carnis.entry.12.body", "A bone scythe replaces its weapon. A sprouting nerve and ribcage core glow red; a sweep can strike nearby targets.");
        add("codex.carnis.entry.12.note", "An empty eye socket does not mean it cannot see.");
        add("codex.carnis.entry.13.title", "Infected Creeper");
        add("codex.carnis.entry.13.body", "Swollen sacs shudder before rupture. Instead of a normal explosion it releases spores, poisons living creatures and leaves veins on solid faces.");
        add("codex.carnis.entry.13.note", "Frantic antennae signal imminent detonation.");
        add("codex.carnis.entry.14.title", "Flesh Amalgam");
        add("codex.carnis.entry.14.body", "A titanic symbiote forms when infected creatures fuse near a heart. Bone plates and acid change with Hive adaptation.");
        add("codex.carnis.entry.14.note", "A weakened Amalgam consumes remains and lesser forms; beware its shockwave and corrosive bile.");
        add("codex.carnis.entry.15.title", "Pneumatic Inoculator");
        add("codex.carnis.entry.15.body", "A dart carries a viral strain or a purifying compound. Account for projectile drop and cover; firing consumes a suitable carried dart.");
        add("codex.carnis.entry.15.note", "The purifying compound reduces player infection by 35.");
        add("codex.carnis.entry.16.title", "Bio-Purifier");
        add("codex.carnis.entry.16.body", "A stream of fire sterilizes living and ossified flesh, leaving charred tissue. Thermal shock usually affects the infected area.");
        add("codex.carnis.entry.16.note", "An active nerve pillar blocks new thermal shock.");
        add("codex.carnis.entry.17.title", "Neuro armor");
        add("codex.carnis.entry.17.body", "Woven tendons connect the armor to the wearer’s nervous system. Each protected piece reduces infectious exposure by a quarter.");
        add("codex.carnis.entry.17.note", "A full set hides its wearer from the Eye, but does not promise invisibility to all.");
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
        add("tooltip.carnis.purification_dart.mechanics", "Players: removes 35 infection and clears nausea, blindness and slowness.");
        add("tooltip.carnis.purification_dart.protocol", "Regresses infected humanoids; damages and stuns major Hive organisms.");
        add("tooltip.carnis.viral_dart.mechanics", "Players: adds 25 infection and causes weakness.");
        add("tooltip.carnis.viral_dart.protocol", "Accelerates livestock incubation; mutates zombies, skeletons and creepers.");
        add("tooltip.carnis.dart.use", "Load in the Pneumatic Inoculator and fire at the target.");
        add("subtitles.carnis.hive_alarm", "Hive eye screams");
        add("subtitles.carnis.hive_ambient_drone", "The Hive breathes");
        add("subtitles.carnis.creeper_rupture", "Biological rupture");
        add("entity.carnis.hive_spore_cloud", "Hive Spore Cloud");
        add("tooltip.carnis.purification_serum.mechanics", "Drink to remove 35 infection points.");
        add("tooltip.carnis.purification_serum.use", "Use directly or craft into purification darts.");
        add("entity.carnis.inoculator_dart", "Inoculator Dart");
        add("tooltip.carnis.viral_dart", "Adds 25 infection to players and causes weakness.");
        add("tooltip.carnis.purification_dart", "Removes 35 infection or damages Carnis mobs for 25.");
        add("tooltip.carnis.hold_shift", "Hold Shift for details");
        add("tooltip.carnis.living_flesh", "Living tissue spreads through nearby terrain.");
        add("tooltip.carnis.charred_flesh", "Burned tissue yields bone meal and charcoal.");
        add("tooltip.carnis.spore_sprout", "An organic sprout releases drifting spores.");
        add("tooltip.carnis.neural_moss", "A fleshy carpet impedes movement.");
        add("tooltip.carnis.neural_moss.mechanics", "Slows outsiders; spreads near water or Hive tissue.");
        add("tooltip.carnis.neural_moss.lore", "A living carpet listens for unfamiliar footsteps.");
        add("tooltip.carnis.creeping_tendrils", "Climb the tendrils attached to solid flesh.");
        add("tooltip.carnis.pustule_cluster", "Step on it without sneaking to burst infectious spores.");
        add("tooltip.carnis.stomach_pool", "Corrosive tissue dissolves items into biomass.");
        add("tooltip.carnis.ossified_flesh", "Hardened tissue spreads the hive.");
        add("tooltip.carnis.fireproof_flesh", "Adapted tissue resistant to flame.");
        add("tooltip.carnis.veins", "Living veins carry infection through wood.");
        add("tooltip.carnis.pulsing_heart", "The hive heart accelerates nearby infection.");
        add("tooltip.carnis.hive_eye", "Detects intruders and alerts nearby Hive members.");
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
        add("carnis.tab", "Carnis: Адаптивный коллективный разум");
        add("item.carnis.parasitic_tendril_spawn_egg", "Яйцо призыва: Паразитическое щупальце");
        add("tooltip.carnis.parasitic_tendril_spawn_egg", "Призывает существо: Паразитическое щупальце.");
        add("item.carnis.hive_sentinel_spawn_egg", "Яйцо призыва: Страж Улья");
        add("tooltip.carnis.hive_sentinel_spawn_egg", "Призывает существо: Страж Улья.");
        add("item.carnis.cerebral_nexus_spawn_egg", "Яйцо призыва: Мозговой Нексус");
        add("tooltip.carnis.cerebral_nexus_spawn_egg", "Призывает существо: Мозговой Нексус.");
        add("tooltip.carnis.biomass_remains", "Органические останки хозяина.");
        add("tooltip.carnis.flesh_bulb", "Созревающий органический мешок.");
        add("tooltip.carnis.sinew_spikes", "Колючие наросты замедляют существ.");
        add("tooltip.carnis.biomass_maggot_spawn_egg", "Призывает личинку биомассы.");
        add("codex.carnis.previous", "< Назад");
        add("codex.carnis.next", "Вперёд >");
        add("codex.carnis.tab.0", "Органогенез");
        add("codex.carnis.tab.1", "Биоценоз");
        add("codex.carnis.tab.2", "Аберрации");
        add("codex.carnis.tab.3", "Биотехнологии");
        add("codex.carnis.entry.0.title", "Пульсирующее сердце");
        add("codex.carnis.entry.0.body", "Центр колонии пульсирует каждые 100 тиков. Известная ему плоть и жилы дают меру роста в радиусе 32 блоков; сам импульс охватывает 8.");
        add("codex.carnis.entry.0.note", "Сердце считает лишь обнаруженную ткань.");
        add("codex.carnis.entry.1.title", "Порядок органов");
        add("codex.carnis.entry.1.body", "На 25, 50, 75 и 100 заражённых блоках улей закладывает око, стража, бассейн и столп. Для роста требуется живая плоть в 8–24 блоках.");
        add("codex.carnis.entry.1.note", "Орган растёт там, где клетка считает место пригодным.");
        add("codex.carnis.entry.2.title", "Око Улья");
        add("codex.carnis.entry.2.body", "Сенсор замечает чужаков в пределах 18 блоков и передаёт тревогу свободным мобам Улья в радиусе 28 блоков.");
        add("codex.carnis.entry.2.note", "Вопль слышен раньше, чем видно зрачок.");
        add("codex.carnis.entry.3.title", "Желудочный бассейн");
        add("codex.carnis.entry.3.body", "Кислота разлагает предметы и живую ткань. Погибший в ней скот отдаёт ближайшему сердцу 20 единиц биомассы, корова — 30.");
        add("codex.carnis.entry.3.note", "Пять единиц урона в секунду — достаточно, чтобы не входить.");
        add("codex.carnis.entry.4.title", "Нервный столп");
        add("codex.carnis.entry.4.body", "Столп рассеивает новый термический шок в радиусе 32 блоков. Щит сокращает поджог форм Улья, но не делает плоть несгораемой.");
        add("codex.carnis.entry.4.note", "Сначала разрушить якорь. Затем очистить очаг.");
        add("codex.carnis.entry.5.title", "Страж и Нексус");
        add("codex.carnis.entry.5.body", "Пси-якорь вводит скот в транс и ведёт его к бассейну. При четырёх органах и 200 единицах сердце может стать Мозговым Нексусом.");
        add("codex.carnis.entry.5.note", "Два дочерних сердца возникают на известной плоти в 48–64 блоках.");
        add("codex.carnis.entry.6.title", "Остатки биомассы");
        add("codex.carnis.entry.6.body", "На твёрдом полу гибель хозяина оставляет рыхлые останки. Они замедляют и чужаков, и существ Улья; близ падали появляются личинки.");
        add("codex.carnis.entry.6.note", "В воде и без опоры образец получить не удалось.");
        add("codex.carnis.entry.7.title", "Личинка биомассы");
        add("codex.carnis.entry.7.body", "Личинка ищет останки в радиусе 16 блоков. Два приёма пищи пробуждают инстинкт зарывания; час на плоти не требуется — достаточно минуты.");
        add("codex.carnis.entry.7.note", "Она выбирает рыхлую землю или плоть, но не камень.");
        add("codex.carnis.entry.8.title", "Кокон созревания");
        add("codex.carnis.entry.8.body", "Мясная луковица держится на потолке или на полу. Через 60–90 секунд её сердцебиение учащается, мешок лопается и выпускает щупальца.");
        add("codex.carnis.entry.8.note", "Счёт идёт только в загруженной области.");
        add("codex.carnis.entry.9.title", "Щупальце: внедрение");
        add("codex.carnis.entry.9.body", "При контакте вероятность заражения мирного хозяина — 85%, монстра — 45%; броня снижает шанс монстра до 30%. Паразит исчезает после броска.");
        add("codex.carnis.entry.9.note", "Провал сопровождается шипением и слабым ранением.");
        add("codex.carnis.entry.10.title", "Четыре стадии");
        add("codex.carnis.entry.10.body", "До 10 секунд — инкубация; до 25 — вены и опухоли; до 30 — разрыв и заражение почвы. Затем монстр мутирует, а мирный хозяин разлагается.");
        add("codex.carnis.entry.10.note", "На третьей стадии рана способна убить до превращения.");
        add("codex.carnis.entry.11.title", "Заражённый зомби");
        add("codex.carnis.entry.11.body", "Правая рука разрослась в костяной клинок; жгутики обрамляют разорванную голову. У останков он замирает и поглощает биомассу.");
        add("codex.carnis.entry.11.note", "Во время питания его взгляд удерживается на одном направлении.");
        add("codex.carnis.entry.12.title", "Заражённый скелет");
        add("codex.carnis.entry.12.body", "Костяной серп заменяет оружие. Проросший нерв и ядро в рёбрах излучают красный свет; удар лезвием может задеть соседние цели.");
        add("codex.carnis.entry.12.note", "Не принимать пустую глазницу за отсутствие зрения.");
        add("codex.carnis.entry.13.title", "Заражённый крипер");
        add("codex.carnis.entry.13.body", "Раздутые мешки колышутся до разрыва. Вместо обычного взрыва он выбрасывает споры, травит живых и оставляет жилы на прочных гранях.");
        add("codex.carnis.entry.13.note", "Признак детонации — бешеное дрожание нервных усиков.");
        add("codex.carnis.entry.14.title", "Амальгама плоти");
        add("codex.carnis.entry.14.body", "Титанический симбиот возникает из слияния заражённых форм у сердца. Костяные пластины и кислота меняются вместе с адаптацией Улья.");
        add("codex.carnis.entry.14.note", "Ослабленная амальгама поглощает останки и малые формы; берегитесь ударной волны и едкой желчи.");
        add("codex.carnis.entry.15.title", "Пневмоинокулятор");
        add("codex.carnis.entry.15.body", "Дротик несёт вирусный штамм или очищающий состав. На расстоянии учитывайте падение снаряда и укрытия; магазин расходует подходящие дротики.");
        add("codex.carnis.entry.15.note", "Очищающий состав снижает заражение игрока на 35.");
        add("codex.carnis.entry.16.title", "Био-очиститель");
        add("codex.carnis.entry.16.body", "Поток огня стерилизует живую и окостеневшую плоть, оставляя обугленную ткань. Термический удар обычно вызывает шок заражённого участка.");
        add("codex.carnis.entry.16.note", "Действующий нервный столп блокирует новый термошок.");
        add("codex.carnis.entry.17.title", "Нейро-броня");
        add("codex.carnis.entry.17.body", "Вплетённые сухожилия связывают доспех с нервной системой носителя. Каждая защищённая часть уменьшает заражающую экспозицию на четверть.");
        add("codex.carnis.entry.17.note", "Полный комплект скрывает носителя от Ока, но не обещает невидимости всем.");
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
        add("tooltip.carnis.viral_dart", "Добавляет игрокам 25 заражения и вызывает слабость.");
        add("tooltip.carnis.purification_dart.mechanics", "Игрок: −35 заражения; снимает тошноту, слепоту и замедление.");
        add("tooltip.carnis.purification_dart.protocol", "Обращает мутацию гуманоидов; ранит и оглушает крупные организмы Улья.");
        add("tooltip.carnis.viral_dart.mechanics", "Игрок: +25 заражения и слабость.");
        add("tooltip.carnis.viral_dart.protocol", "Ускоряет инкубацию скота; мутирует зомби, скелетов и криперов.");
        add("tooltip.carnis.dart.use", "Зарядите пневматический инокулятор и выстрелите в цель.");
        add("subtitles.carnis.hive_alarm", "Око Улья кричит");
        add("subtitles.carnis.hive_ambient_drone", "Улей дышит");
        add("subtitles.carnis.creeper_rupture", "Биологический разрыв");
        add("entity.carnis.hive_spore_cloud", "Споровое облако Улья");
        add("tooltip.carnis.purification_serum.mechanics", "Выпейте, чтобы снять 35 очков заражения.");
        add("tooltip.carnis.purification_serum.use", "Выпейте напрямую или изготовьте дротики очищения.");
        add("entity.carnis.inoculator_dart", "Дротик инокулятора");
        add("tooltip.carnis.purification_dart", "Снимает 35 заражения или наносит мобам Carnis 25 урона.");
        add("tooltip.carnis.hold_shift", "Удерживайте Shift для подробностей");
        add("tooltip.carnis.living_flesh", "Живая ткань распространяется по окружающим блокам.");
        add("tooltip.carnis.charred_flesh", "Обгоревшая ткань даёт костную муку и уголь.");
        add("tooltip.carnis.spore_sprout", "Органический росток выпускает споры.");
        add("tooltip.carnis.neural_moss", "Мясистый мох замедляет движение.");
        add("tooltip.carnis.neural_moss.mechanics", "Замедляет чужаков; растёт у воды и тканей Улья.");
        add("tooltip.carnis.neural_moss.lore", "Живой ковёр прислушивается к чужим шагам.");
        add("tooltip.carnis.creeping_tendrils", "Взбирайтесь по усикам на поверхности плоти.");
        add("tooltip.carnis.pustule_cluster", "Наступите без приседания: пустулы лопнут и заразят вас.");
        add("tooltip.carnis.stomach_pool", "Едкая ткань растворяет предметы в биомассу.");
        add("tooltip.carnis.ossified_flesh", "Окостеневшая ткань распространяет улей.");
        add("tooltip.carnis.fireproof_flesh", "Ткань, приспособленная к огню.");
        add("tooltip.carnis.veins", "Живые вены несут инфекцию через древесину.");
        add("tooltip.carnis.pulsing_heart", "Сердце улья ускоряет заражение поблизости.");
        add("tooltip.carnis.hive_eye", "Обнаруживает чужаков и тревожит ближайших существ Улья.");
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

### `src/generated/resources/assets/carnis/lang/en_us.json`

```json
{
  "block.carnis.biomass_remains": "Biomass Remains",
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
  "carnis.tab": "Carnis: Adaptive Hivemind",
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
  "codex.carnis.entry.0.body": "The colony core pulses every 100 ticks. Known flesh and veins measure growth within 32 blocks; the pulse itself reaches 8.",
  "codex.carnis.entry.0.note": "The heart counts only tissue it has discovered.",
  "codex.carnis.entry.0.title": "Pulsing Heart",
  "codex.carnis.entry.1.body": "At 25, 50, 75 and 100 infected blocks the Hive develops an eye, sentinel, pool and pillar. Growth requires living flesh 8–24 blocks away.",
  "codex.carnis.entry.1.note": "Organs grow where the cell finds a suitable place.",
  "codex.carnis.entry.1.title": "Order of organs",
  "codex.carnis.entry.10.body": "Up to 10 seconds: incubation; up to 25: veins and growths; up to 30: rupture and soil infection. Then a monster mutates and a peaceful host decomposes.",
  "codex.carnis.entry.10.note": "In the third stage the wound can kill before transformation.",
  "codex.carnis.entry.10.title": "Four stages",
  "codex.carnis.entry.11.body": "Its right arm has grown into a bone blade; tendrils frame its torn head. Near remains it stops and consumes biomass.",
  "codex.carnis.entry.11.note": "While feeding, its gaze holds one direction.",
  "codex.carnis.entry.11.title": "Infected Zombie",
  "codex.carnis.entry.12.body": "A bone scythe replaces its weapon. A sprouting nerve and ribcage core glow red; a sweep can strike nearby targets.",
  "codex.carnis.entry.12.note": "An empty eye socket does not mean it cannot see.",
  "codex.carnis.entry.12.title": "Infected Skeleton",
  "codex.carnis.entry.13.body": "Swollen sacs shudder before rupture. Instead of a normal explosion it releases spores, poisons living creatures and leaves veins on solid faces.",
  "codex.carnis.entry.13.note": "Frantic antennae signal imminent detonation.",
  "codex.carnis.entry.13.title": "Infected Creeper",
  "codex.carnis.entry.14.body": "A titanic symbiote forms when infected creatures fuse near a heart. Bone plates and acid change with Hive adaptation.",
  "codex.carnis.entry.14.note": "A weakened Amalgam consumes remains and lesser forms; beware its shockwave and corrosive bile.",
  "codex.carnis.entry.14.title": "Flesh Amalgam",
  "codex.carnis.entry.15.body": "A dart carries a viral strain or a purifying compound. Account for projectile drop and cover; firing consumes a suitable carried dart.",
  "codex.carnis.entry.15.note": "The purifying compound reduces player infection by 35.",
  "codex.carnis.entry.15.title": "Pneumatic Inoculator",
  "codex.carnis.entry.16.body": "A stream of fire sterilizes living and ossified flesh, leaving charred tissue. Thermal shock usually affects the infected area.",
  "codex.carnis.entry.16.note": "An active nerve pillar blocks new thermal shock.",
  "codex.carnis.entry.16.title": "Bio-Purifier",
  "codex.carnis.entry.17.body": "Woven tendons connect the armor to the wearer’s nervous system. Each protected piece reduces infectious exposure by a quarter.",
  "codex.carnis.entry.17.note": "A full set hides its wearer from the Eye, but does not promise invisibility to all.",
  "codex.carnis.entry.17.title": "Neuro armor",
  "codex.carnis.entry.2.body": "The sensor detects outsiders within 18 blocks and alerts free Hive mobs within 28 blocks.",
  "codex.carnis.entry.2.note": "The scream is heard before the pupil is seen.",
  "codex.carnis.entry.2.title": "Hive Eye",
  "codex.carnis.entry.3.body": "Acid dissolves items and living tissue. Livestock killed within it yields 20 biomass to a nearby heart, or 30 for a cow.",
  "codex.carnis.entry.3.note": "Five damage per second is reason enough to stay out.",
  "codex.carnis.entry.3.title": "Stomach Pool",
  "codex.carnis.entry.4.body": "The pillar blocks new thermal shock within 32 blocks. Its shield reduces ignition of Hive forms but does not make flesh fireproof.",
  "codex.carnis.entry.4.note": "Destroy the anchor first. Then cleanse the site.",
  "codex.carnis.entry.4.title": "Nerve Pillar",
  "codex.carnis.entry.5.body": "A psychic anchor draws livestock into a trance and guides it to a pool. With four organs and 200 biomass the heart can become a Cerebral Nexus.",
  "codex.carnis.entry.5.note": "Two daughter hearts appear on known flesh 48–64 blocks away.",
  "codex.carnis.entry.5.title": "Sentinel and Nexus",
  "codex.carnis.entry.6.body": "A host dying on solid ground leaves loose remains. They slow outsiders and Hive creatures alike; maggots appear near carrion.",
  "codex.carnis.entry.6.note": "No sample was obtained in water or without support.",
  "codex.carnis.entry.6.title": "Biomass Remains",
  "codex.carnis.entry.7.body": "The maggot seeks remains within 16 blocks. Two meals awaken its burrowing instinct; one minute on flesh is enough.",
  "codex.carnis.entry.7.note": "It chooses loose soil or flesh, not stone.",
  "codex.carnis.entry.7.title": "Biomass Maggot",
  "codex.carnis.entry.8.body": "The Flesh Bulb attaches to ceilings or floors. After 60–90 seconds its heartbeat quickens and the sac bursts, releasing tendrils.",
  "codex.carnis.entry.8.note": "Time passes only in loaded areas.",
  "codex.carnis.entry.8.title": "Maturing Cocoon",
  "codex.carnis.entry.9.body": "Contact infects a peaceful host with 85% probability or a monster with 45%; armor reduces the monster chance to 30%. The parasite vanishes after its attempt.",
  "codex.carnis.entry.9.note": "Failure brings a hiss and a minor wound.",
  "codex.carnis.entry.9.title": "Tendril: implantation",
  "codex.carnis.next": "Next >",
  "codex.carnis.previous": "< Back",
  "codex.carnis.tab.0": "Organogenesis",
  "codex.carnis.tab.1": "Biocenosis",
  "codex.carnis.tab.2": "Aberrations",
  "codex.carnis.tab.3": "Biotechnology",
  "death.attack.bio_purifier": "%1$s was incinerated by a bio-purifier",
  "death.attack.bio_purifier.player": "%1$s was incinerated by %2$s's bio-purifier",
  "death.attack.carnis_tainted_sludge": "%1$s dissolved in tainted sludge",
  "death.attack.necrotic_consumption": "%1$s was consumed by the hivemind",
  "death.attack.organic_consumption": "%1$s was consumed by the hive",
  "death.attack.purification_dart": "%1$s was purified by a dart",
  "death.attack.purification_dart.player": "%1$s was purified by %2$s",
  "effect.carnis.immunosuppression": "Immunosuppression",
  "effect.carnis.incubating": "Incubating",
  "effect.carnis.thermal_shock": "Thermal Shock",
  "entity.carnis.amalgam_bile": "Amalgam Bile",
  "entity.carnis.assimilated_player": "Assimilated %s",
  "entity.carnis.biomass_maggot": "Biomass Maggot",
  "entity.carnis.cerebral_nexus": "Cerebral Nexus",
  "entity.carnis.flesh_amalgam": "Flesh Amalgam",
  "entity.carnis.flesh_spat": "Flesh Spat",
  "entity.carnis.hive_sentinel": "Hive Sentinel",
  "entity.carnis.hive_spore_cloud": "Hive Spore Cloud",
  "entity.carnis.infected_creeper": "Infected Creeper",
  "entity.carnis.infected_skeleton": "Infected Skeleton",
  "entity.carnis.infected_spider": "Infected Spider",
  "entity.carnis.infected_zombie": "Infected Zombie",
  "entity.carnis.inoculator_dart": "Inoculator Dart",
  "entity.carnis.parasitic_tendril": "Parasitic Tendril",
  "entity.carnis.purification_dart": "Purification Dart",
  "entity.carnis.viral_dart": "Viral Dart",
  "fluid_type.carnis.tainted_sludge": "Tainted Sludge",
  "item.carnis.amalgam_bile_glob": "Amalgam Bile",
  "item.carnis.antibiotics": "Antibiotics",
  "item.carnis.bio_purifier": "Bio-Purifier",
  "item.carnis.biomass_maggot_spawn_egg": "Biomass Maggot Spawn Egg",
  "item.carnis.bone_scythe_arm": "Bone Scythe Arm",
  "item.carnis.cerebral_nexus_spawn_egg": "Cerebral Nexus Spawn Egg",
  "item.carnis.flesh_amalgam_spawn_egg": "Flesh Amalgam Spawn Egg",
  "item.carnis.flesh_spat": "Flesh Spat",
  "item.carnis.hive_sentinel_spawn_egg": "Hive Sentinel Spawn Egg",
  "item.carnis.infected_creeper_spawn_egg": "Infected Creeper Spawn Egg",
  "item.carnis.infected_skeleton_spawn_egg": "Infected Skeleton Spawn Egg",
  "item.carnis.infected_spider_spawn_egg": "Infected Spider Spawn Egg",
  "item.carnis.infected_zombie_spawn_egg": "Infected Zombie Spawn Egg",
  "item.carnis.neural_binding_matrix": "Neural Binding Matrix",
  "item.carnis.neuro_resonator_boots": "Neuro-Resonator Boots",
  "item.carnis.neuro_resonator_chestplate": "Neuro-Resonator Chestplate",
  "item.carnis.neuro_resonator_helmet": "Neuro-Resonator Helmet",
  "item.carnis.neuro_resonator_leggings": "Neuro-Resonator Leggings",
  "item.carnis.parasitic_tendril_spawn_egg": "Parasitic Tendril Spawn Egg",
  "item.carnis.pneumatic_inoculator": "Pneumatic Inoculator",
  "item.carnis.purification_dart": "Purification Dart",
  "item.carnis.purification_serum": "Purification Serum",
  "item.carnis.research_journal": "Codex Carnis",
  "item.carnis.tainted_sludge_bucket": "Tainted Sludge Bucket",
  "item.carnis.viral_dart": "Viral Dart",
  "itemGroup.carnis": "Carnis: Adaptive Hivemind",
  "subtitles.carnis.acid_splash": "Corrosive acid splashes",
  "subtitles.carnis.amalgam_roar": "Amalgam roars",
  "subtitles.carnis.amalgam_smash": "Amalgam slams the ground",
  "subtitles.carnis.amalgam_step": "Flesh Amalgam squelches",
  "subtitles.carnis.amalgamation_fuse": "Flesh fuses into an amalgam",
  "subtitles.carnis.bone_deflect": "A projectile ricochets off bone",
  "subtitles.carnis.creeper_rupture": "Biological rupture",
  "subtitles.carnis.dart_hit": "Dart hits",
  "subtitles.carnis.digestor_churn": "A digestor churns",
  "subtitles.carnis.flamethrower_fire": "Flamethrower roars",
  "subtitles.carnis.flesh_amalgam_ambient": "The Flesh Amalgam groans",
  "subtitles.carnis.flesh_amalgam_death": "The Flesh Amalgam collapses",
  "subtitles.carnis.flesh_amalgam_hurt": "The Flesh Amalgam recoils",
  "subtitles.carnis.heartbeat_loop": "Heart beats",
  "subtitles.carnis.hive_alarm": "Hive eye screams",
  "subtitles.carnis.hive_ambient_drone": "The Hive breathes",
  "subtitles.carnis.hive_eye_screech": "The hive eye shrieks",
  "subtitles.carnis.inoculator_fire": "Inoculator fires",
  "subtitles.carnis.organic_creak": "Sinew lashes",
  "subtitles.carnis.phantom_creeper": "Something hisses behind you",
  "subtitles.carnis.phantom_footsteps": "Footsteps squelch through flesh",
  "subtitles.carnis.phantom_whisper": "The hivemind whispers",
  "subtitles.carnis.pulsing_heart_beat": "A biome heart beats",
  "subtitles.carnis.purifier_ignite": "Purifier ignites",
  "subtitles.carnis.purifier_loop": "Purifier fires",
  "subtitles.carnis.synapse_rupture": "Nerve tissue tears apart",
  "subtitles.carnis.synapse_shock": "A synapse discharges",
  "tooltip.carnis.amalgam_bile_glob": "A corrosive organic glob.",
  "tooltip.carnis.antibiotics": "Prevents exposure for 3 minutes.",
  "tooltip.carnis.bio_purifier": "Hold use: 6.5-block cone of flame.",
  "tooltip.carnis.biomass_maggot.lore": "The first link in the Hive’s parasitic cycle.",
  "tooltip.carnis.biomass_maggot.mechanics": "A voracious scavenger. Devours organic remains and pupates in soil.",
  "tooltip.carnis.biomass_maggot_spawn_egg": "Spawns a biomass maggot.",
  "tooltip.carnis.biomass_remains": "Organic remains left by a host.",
  "tooltip.carnis.bone_scythe_arm": "A jagged bone blade.",
  "tooltip.carnis.cerebral_nexus_spawn_egg": "Spawns a cerebral nexus.",
  "tooltip.carnis.charred_flesh": "Burned tissue yields bone meal and charcoal.",
  "tooltip.carnis.creeping_tendrils": "Climb the tendrils attached to solid flesh.",
  "tooltip.carnis.dart.use": "Load in the Pneumatic Inoculator and fire at the target.",
  "tooltip.carnis.fireproof_flesh": "Adapted tissue resistant to flame.",
  "tooltip.carnis.flesh_amalgam_spawn_egg": "Spawns a Flesh Amalgam.",
  "tooltip.carnis.flesh_bulb": "An incubating organic sac.",
  "tooltip.carnis.flesh_bulb.lore": "The muffled, rapid heartbeat of a maturing brood can be heard inside.",
  "tooltip.carnis.flesh_bulb.mechanics": "An incubation sac that can attach to ceilings and floors.",
  "tooltip.carnis.flesh_spat": "A glob of infectious tissue.",
  "tooltip.carnis.flesh_veins": "Organic growth on exposed surfaces.",
  "tooltip.carnis.hive_eye": "Detects intruders and alerts nearby Hive members.",
  "tooltip.carnis.hive_sentinel_spawn_egg": "Spawns a hive sentinel.",
  "tooltip.carnis.hold_shift": "Hold Shift for details",
  "tooltip.carnis.infected_creeper_spawn_egg": "Spawns an infected creeper.",
  "tooltip.carnis.infected_skeleton_spawn_egg": "Spawns an infected skeleton.",
  "tooltip.carnis.infected_spider_spawn_egg": "Spawns an infected spider.",
  "tooltip.carnis.infected_zombie_spawn_egg": "Spawns an infected zombie.",
  "tooltip.carnis.living_flesh": "Living tissue spreads through nearby terrain.",
  "tooltip.carnis.nerve_pillar": "Placement halves remaining shock time in this chunk.",
  "tooltip.carnis.neural_binding_matrix": "Weave into armor at an anvil for five levels.",
  "tooltip.carnis.neural_moss": "A fleshy carpet impedes movement.",
  "tooltip.carnis.neural_moss.lore": "A living carpet listens for unfamiliar footsteps.",
  "tooltip.carnis.neural_moss.mechanics": "Slows outsiders; spreads near water or Hive tissue.",
  "tooltip.carnis.neuro_resonator_boots": "Biological boots reduce infection exposure.",
  "tooltip.carnis.neuro_resonator_chestplate": "A biological chestplate reduces infection exposure.",
  "tooltip.carnis.neuro_resonator_helmet": "Dampens hallucinations, reduces exposure by 25% and reveals nearby biomass.",
  "tooltip.carnis.neuro_resonator_leggings": "Biological leggings reduce infection exposure.",
  "tooltip.carnis.ossified_flesh": "Hardened tissue spreads the hive.",
  "tooltip.carnis.parasitic_tendril_spawn_egg": "Spawns a parasitic tendril.",
  "tooltip.carnis.pneumatic_inoculator": "Right-click to fire a carried dart; 15-tick cooldown.",
  "tooltip.carnis.pulsing_heart": "The hive heart accelerates nearby infection.",
  "tooltip.carnis.purification_dart": "Removes 35 infection or damages Carnis mobs for 25.",
  "tooltip.carnis.purification_dart.mechanics": "Players: removes 35 infection and clears nausea, blindness and slowness.",
  "tooltip.carnis.purification_dart.protocol": "Regresses infected humanoids; damages and stuns major Hive organisms.",
  "tooltip.carnis.purification_serum": "Drink to remove 35 infection points.",
  "tooltip.carnis.purification_serum.mechanics": "Drink to remove 35 infection points.",
  "tooltip.carnis.purification_serum.use": "Use directly or craft into purification darts.",
  "tooltip.carnis.pustule_cluster": "Step on it without sneaking to burst infectious spores.",
  "tooltip.carnis.research_journal": "A field guide to the hive.",
  "tooltip.carnis.sinew_spikes": "Piercing growths slow creatures.",
  "tooltip.carnis.sinew_spikes.lore": "Taut sinews respond to the slightest vibration of footsteps.",
  "tooltip.carnis.sinew_spikes.mechanics": "Deals piercing damage and slows any creature that steps on it.",
  "tooltip.carnis.spore_sprout": "An organic sprout releases drifting spores.",
  "tooltip.carnis.stomach_pool": "Corrosive tissue dissolves items into biomass.",
  "tooltip.carnis.tainted_sludge_bucket": "A bucket of infectious sludge.",
  "tooltip.carnis.veins": "Living veins carry infection through wood.",
  "tooltip.carnis.viral_dart": "Adds 25 infection to players and causes weakness.",
  "tooltip.carnis.viral_dart.mechanics": "Players: adds 25 infection and causes weakness.",
  "tooltip.carnis.viral_dart.protocol": "Accelerates livestock incubation; mutates zombies, skeletons and creepers."
}

```

### `src/generated/resources/assets/carnis/lang/ru_ru.json`

```json
{
  "block.carnis.biomass_remains": "Останки биомассы",
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
  "carnis.tab": "Carnis: Адаптивный коллективный разум",
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
  "codex.carnis.entry.0.body": "Центр колонии пульсирует каждые 100 тиков. Известная ему плоть и жилы дают меру роста в радиусе 32 блоков; сам импульс охватывает 8.",
  "codex.carnis.entry.0.note": "Сердце считает лишь обнаруженную ткань.",
  "codex.carnis.entry.0.title": "Пульсирующее сердце",
  "codex.carnis.entry.1.body": "На 25, 50, 75 и 100 заражённых блоках улей закладывает око, стража, бассейн и столп. Для роста требуется живая плоть в 8–24 блоках.",
  "codex.carnis.entry.1.note": "Орган растёт там, где клетка считает место пригодным.",
  "codex.carnis.entry.1.title": "Порядок органов",
  "codex.carnis.entry.10.body": "До 10 секунд — инкубация; до 25 — вены и опухоли; до 30 — разрыв и заражение почвы. Затем монстр мутирует, а мирный хозяин разлагается.",
  "codex.carnis.entry.10.note": "На третьей стадии рана способна убить до превращения.",
  "codex.carnis.entry.10.title": "Четыре стадии",
  "codex.carnis.entry.11.body": "Правая рука разрослась в костяной клинок; жгутики обрамляют разорванную голову. У останков он замирает и поглощает биомассу.",
  "codex.carnis.entry.11.note": "Во время питания его взгляд удерживается на одном направлении.",
  "codex.carnis.entry.11.title": "Заражённый зомби",
  "codex.carnis.entry.12.body": "Костяной серп заменяет оружие. Проросший нерв и ядро в рёбрах излучают красный свет; удар лезвием может задеть соседние цели.",
  "codex.carnis.entry.12.note": "Не принимать пустую глазницу за отсутствие зрения.",
  "codex.carnis.entry.12.title": "Заражённый скелет",
  "codex.carnis.entry.13.body": "Раздутые мешки колышутся до разрыва. Вместо обычного взрыва он выбрасывает споры, травит живых и оставляет жилы на прочных гранях.",
  "codex.carnis.entry.13.note": "Признак детонации — бешеное дрожание нервных усиков.",
  "codex.carnis.entry.13.title": "Заражённый крипер",
  "codex.carnis.entry.14.body": "Титанический симбиот возникает из слияния заражённых форм у сердца. Костяные пластины и кислота меняются вместе с адаптацией Улья.",
  "codex.carnis.entry.14.note": "Ослабленная амальгама поглощает останки и малые формы; берегитесь ударной волны и едкой желчи.",
  "codex.carnis.entry.14.title": "Амальгама плоти",
  "codex.carnis.entry.15.body": "Дротик несёт вирусный штамм или очищающий состав. На расстоянии учитывайте падение снаряда и укрытия; магазин расходует подходящие дротики.",
  "codex.carnis.entry.15.note": "Очищающий состав снижает заражение игрока на 35.",
  "codex.carnis.entry.15.title": "Пневмоинокулятор",
  "codex.carnis.entry.16.body": "Поток огня стерилизует живую и окостеневшую плоть, оставляя обугленную ткань. Термический удар обычно вызывает шок заражённого участка.",
  "codex.carnis.entry.16.note": "Действующий нервный столп блокирует новый термошок.",
  "codex.carnis.entry.16.title": "Био-очиститель",
  "codex.carnis.entry.17.body": "Вплетённые сухожилия связывают доспех с нервной системой носителя. Каждая защищённая часть уменьшает заражающую экспозицию на четверть.",
  "codex.carnis.entry.17.note": "Полный комплект скрывает носителя от Ока, но не обещает невидимости всем.",
  "codex.carnis.entry.17.title": "Нейро-броня",
  "codex.carnis.entry.2.body": "Сенсор замечает чужаков в пределах 18 блоков и передаёт тревогу свободным мобам Улья в радиусе 28 блоков.",
  "codex.carnis.entry.2.note": "Вопль слышен раньше, чем видно зрачок.",
  "codex.carnis.entry.2.title": "Око Улья",
  "codex.carnis.entry.3.body": "Кислота разлагает предметы и живую ткань. Погибший в ней скот отдаёт ближайшему сердцу 20 единиц биомассы, корова — 30.",
  "codex.carnis.entry.3.note": "Пять единиц урона в секунду — достаточно, чтобы не входить.",
  "codex.carnis.entry.3.title": "Желудочный бассейн",
  "codex.carnis.entry.4.body": "Столп рассеивает новый термический шок в радиусе 32 блоков. Щит сокращает поджог форм Улья, но не делает плоть несгораемой.",
  "codex.carnis.entry.4.note": "Сначала разрушить якорь. Затем очистить очаг.",
  "codex.carnis.entry.4.title": "Нервный столп",
  "codex.carnis.entry.5.body": "Пси-якорь вводит скот в транс и ведёт его к бассейну. При четырёх органах и 200 единицах сердце может стать Мозговым Нексусом.",
  "codex.carnis.entry.5.note": "Два дочерних сердца возникают на известной плоти в 48–64 блоках.",
  "codex.carnis.entry.5.title": "Страж и Нексус",
  "codex.carnis.entry.6.body": "На твёрдом полу гибель хозяина оставляет рыхлые останки. Они замедляют и чужаков, и существ Улья; близ падали появляются личинки.",
  "codex.carnis.entry.6.note": "В воде и без опоры образец получить не удалось.",
  "codex.carnis.entry.6.title": "Остатки биомассы",
  "codex.carnis.entry.7.body": "Личинка ищет останки в радиусе 16 блоков. Два приёма пищи пробуждают инстинкт зарывания; час на плоти не требуется — достаточно минуты.",
  "codex.carnis.entry.7.note": "Она выбирает рыхлую землю или плоть, но не камень.",
  "codex.carnis.entry.7.title": "Личинка биомассы",
  "codex.carnis.entry.8.body": "Мясная луковица держится на потолке или на полу. Через 60–90 секунд её сердцебиение учащается, мешок лопается и выпускает щупальца.",
  "codex.carnis.entry.8.note": "Счёт идёт только в загруженной области.",
  "codex.carnis.entry.8.title": "Кокон созревания",
  "codex.carnis.entry.9.body": "При контакте вероятность заражения мирного хозяина — 85%, монстра — 45%; броня снижает шанс монстра до 30%. Паразит исчезает после броска.",
  "codex.carnis.entry.9.note": "Провал сопровождается шипением и слабым ранением.",
  "codex.carnis.entry.9.title": "Щупальце: внедрение",
  "codex.carnis.next": "Вперёд >",
  "codex.carnis.previous": "< Назад",
  "codex.carnis.tab.0": "Органогенез",
  "codex.carnis.tab.1": "Биоценоз",
  "codex.carnis.tab.2": "Аберрации",
  "codex.carnis.tab.3": "Биотехнологии",
  "death.attack.bio_purifier": "%1$s сожжён биоочистителем",
  "death.attack.bio_purifier.player": "%1$s сожжён биоочистителем игрока %2$s",
  "death.attack.carnis_tainted_sludge": "%1$s растворился в заражённой жиже",
  "death.attack.necrotic_consumption": "%1$s поглощён коллективным разумом",
  "death.attack.organic_consumption": "%1$s был поглощён Ульем",
  "death.attack.purification_dart": "%1$s очищен дротиком",
  "death.attack.purification_dart.player": "%1$s очищен игроком %2$s",
  "effect.carnis.immunosuppression": "Иммуносупрессия",
  "effect.carnis.incubating": "Инкубация",
  "effect.carnis.thermal_shock": "Термический шок",
  "entity.carnis.amalgam_bile": "Желчь амальгамы",
  "entity.carnis.assimilated_player": "Ассимилированный %s",
  "entity.carnis.biomass_maggot": "Личинка биомассы",
  "entity.carnis.cerebral_nexus": "Мозговой узел",
  "entity.carnis.flesh_amalgam": "Амальгама плоти",
  "entity.carnis.flesh_spat": "Плевок плоти",
  "entity.carnis.hive_sentinel": "Страж Улья",
  "entity.carnis.hive_spore_cloud": "Споровое облако Улья",
  "entity.carnis.infected_creeper": "Заражённый крипер",
  "entity.carnis.infected_skeleton": "Заражённый скелет",
  "entity.carnis.infected_spider": "Заражённый паук",
  "entity.carnis.infected_zombie": "Заражённый зомби",
  "entity.carnis.inoculator_dart": "Дротик инокулятора",
  "entity.carnis.parasitic_tendril": "Паразитический усик",
  "entity.carnis.purification_dart": "Очищающий дротик",
  "entity.carnis.viral_dart": "Вирусный дротик",
  "fluid_type.carnis.tainted_sludge": "Заражённая слизь",
  "item.carnis.amalgam_bile_glob": "Желчь амальгамы",
  "item.carnis.antibiotics": "Антибиотики",
  "item.carnis.bio_purifier": "Очищающий огнемёт",
  "item.carnis.biomass_maggot_spawn_egg": "Яйцо призыва: Личинка биомассы",
  "item.carnis.bone_scythe_arm": "Костяная коса-рука",
  "item.carnis.cerebral_nexus_spawn_egg": "Яйцо призыва: Мозговой Нексус",
  "item.carnis.flesh_amalgam_spawn_egg": "Яйцо призыва амальгамы плоти",
  "item.carnis.flesh_spat": "Плевок плоти",
  "item.carnis.hive_sentinel_spawn_egg": "Яйцо призыва: Страж Улья",
  "item.carnis.infected_creeper_spawn_egg": "Яйцо призыва: Заражённый крипер",
  "item.carnis.infected_skeleton_spawn_egg": "Яйцо призыва: Заражённый скелет",
  "item.carnis.infected_spider_spawn_egg": "Яйцо призыва: Заражённый паук",
  "item.carnis.infected_zombie_spawn_egg": "Яйцо призыва заражённого зомби",
  "item.carnis.neural_binding_matrix": "Матрица нейронного сплетения",
  "item.carnis.neuro_resonator_boots": "Нейро-резонаторные ботинки",
  "item.carnis.neuro_resonator_chestplate": "Нейро-резонаторный нагрудник",
  "item.carnis.neuro_resonator_helmet": "Нейро-резонаторный шлем",
  "item.carnis.neuro_resonator_leggings": "Нейро-резонаторные поножи",
  "item.carnis.parasitic_tendril_spawn_egg": "Яйцо призыва: Паразитическое щупальце",
  "item.carnis.pneumatic_inoculator": "Пневматический инокулятор",
  "item.carnis.purification_dart": "Очищающий дротик",
  "item.carnis.purification_serum": "Очищающая сыворотка",
  "item.carnis.research_journal": "Кодекс Карнис",
  "item.carnis.tainted_sludge_bucket": "Ведро заражённой слизи",
  "item.carnis.viral_dart": "Вирусный дротик",
  "itemGroup.carnis": "Carnis: Адаптивный коллективный разум",
  "subtitles.carnis.acid_splash": "Едкая кислота брызжет",
  "subtitles.carnis.amalgam_roar": "Амальгама ревёт",
  "subtitles.carnis.amalgam_smash": "Амальгама сотрясает землю",
  "subtitles.carnis.amalgam_step": "Плотяная амальгама чавкает",
  "subtitles.carnis.amalgamation_fuse": "Плоть сливается в амальгаму",
  "subtitles.carnis.bone_deflect": "Снаряд рикошетит от кости",
  "subtitles.carnis.creeper_rupture": "Биологический разрыв",
  "subtitles.carnis.dart_hit": "Дротик ударяется",
  "subtitles.carnis.digestor_churn": "Желудочный пруд бурлит",
  "subtitles.carnis.flamethrower_fire": "Огнемёт ревёт",
  "subtitles.carnis.flesh_amalgam_ambient": "Амальгама плоти стонет",
  "subtitles.carnis.flesh_amalgam_death": "Амальгама плоти обрушивается",
  "subtitles.carnis.flesh_amalgam_hurt": "Амальгама плоти вздрагивает",
  "subtitles.carnis.heartbeat_loop": "Сердце бьётся",
  "subtitles.carnis.hive_alarm": "Око Улья кричит",
  "subtitles.carnis.hive_ambient_drone": "Улей дышит",
  "subtitles.carnis.hive_eye_screech": "Око разума визжит",
  "subtitles.carnis.inoculator_fire": "Выстрел инокулятора",
  "subtitles.carnis.organic_creak": "Сухожилие хлещет",
  "subtitles.carnis.phantom_creeper": "Что-то шипит за спиной",
  "subtitles.carnis.phantom_footsteps": "Шаги хлюпают по плоти",
  "subtitles.carnis.phantom_whisper": "Коллективный разум шепчет",
  "subtitles.carnis.pulsing_heart_beat": "Сердце биома бьётся",
  "subtitles.carnis.purifier_ignite": "Очиститель зажигается",
  "subtitles.carnis.purifier_loop": "Очиститель выпускает пламя",
  "subtitles.carnis.synapse_rupture": "Нервная ткань разрывается",
  "subtitles.carnis.synapse_shock": "Нервный столб разряжается",
  "tooltip.carnis.amalgam_bile_glob": "Едкий органический сгусток.",
  "tooltip.carnis.antibiotics": "Предотвращает заражение на 3 минуты.",
  "tooltip.carnis.bio_purifier": "Удерживайте: конус пламени на 6,5 блока.",
  "tooltip.carnis.biomass_maggot.lore": "Начальное звено паразитического круговорота Улья.",
  "tooltip.carnis.biomass_maggot.mechanics": "Ненасытный трупоед. Пожирает органические останки и окукливается в почве.",
  "tooltip.carnis.biomass_maggot_spawn_egg": "Призывает личинку биомассы.",
  "tooltip.carnis.biomass_remains": "Органические останки хозяина.",
  "tooltip.carnis.bone_scythe_arm": "Зазубренный костяной клинок.",
  "tooltip.carnis.cerebral_nexus_spawn_egg": "Призывает существо: Мозговой Нексус.",
  "tooltip.carnis.charred_flesh": "Обгоревшая ткань даёт костную муку и уголь.",
  "tooltip.carnis.creeping_tendrils": "Взбирайтесь по усикам на поверхности плоти.",
  "tooltip.carnis.dart.use": "Зарядите пневматический инокулятор и выстрелите в цель.",
  "tooltip.carnis.fireproof_flesh": "Ткань, приспособленная к огню.",
  "tooltip.carnis.flesh_amalgam_spawn_egg": "Призывает амальгаму плоти.",
  "tooltip.carnis.flesh_bulb": "Созревающий органический мешок.",
  "tooltip.carnis.flesh_bulb.lore": "Внутри слышно глухое, частое сердцебиение зреющего выводка.",
  "tooltip.carnis.flesh_bulb.mechanics": "Инкубационный мешок, способный закрепляться на потолке и полу.",
  "tooltip.carnis.flesh_spat": "Сгусток заражённой ткани.",
  "tooltip.carnis.flesh_veins": "Органические жилы на открытых поверхностях.",
  "tooltip.carnis.hive_eye": "Обнаруживает чужаков и тревожит ближайших существ Улья.",
  "tooltip.carnis.hive_sentinel_spawn_egg": "Призывает существо: Страж Улья.",
  "tooltip.carnis.hold_shift": "Удерживайте Shift для подробностей",
  "tooltip.carnis.infected_creeper_spawn_egg": "Призывает заражённого крипера.",
  "tooltip.carnis.infected_skeleton_spawn_egg": "Призывает заражённого скелета.",
  "tooltip.carnis.infected_spider_spawn_egg": "Призывает заражённого паука.",
  "tooltip.carnis.infected_zombie_spawn_egg": "Призывает заражённого зомби.",
  "tooltip.carnis.living_flesh": "Живая ткань распространяется по окружающим блокам.",
  "tooltip.carnis.nerve_pillar": "При установке вдвое сокращает оставшийся шок чанка.",
  "tooltip.carnis.neural_binding_matrix": "Вплетите в броню на наковальне за пять уровней.",
  "tooltip.carnis.neural_moss": "Мясистый мох замедляет движение.",
  "tooltip.carnis.neural_moss.lore": "Живой ковёр прислушивается к чужим шагам.",
  "tooltip.carnis.neural_moss.mechanics": "Замедляет чужаков; растёт у воды и тканей Улья.",
  "tooltip.carnis.neuro_resonator_boots": "Биологические ботинки снижают заражение.",
  "tooltip.carnis.neuro_resonator_chestplate": "Биологический нагрудник снижает заражение.",
  "tooltip.carnis.neuro_resonator_helmet": "Подавляет галлюцинации, снижает экспозицию на 25% и обнаруживает биомассу.",
  "tooltip.carnis.neuro_resonator_leggings": "Биологические поножи снижают заражение.",
  "tooltip.carnis.ossified_flesh": "Окостеневшая ткань распространяет улей.",
  "tooltip.carnis.parasitic_tendril_spawn_egg": "Призывает существо: Паразитическое щупальце.",
  "tooltip.carnis.pneumatic_inoculator": "ПКМ: выстрел дротиком из инвентаря; задержка 15 тиков.",
  "tooltip.carnis.pulsing_heart": "Сердце улья ускоряет заражение поблизости.",
  "tooltip.carnis.purification_dart": "Снимает 35 заражения или наносит мобам Carnis 25 урона.",
  "tooltip.carnis.purification_dart.mechanics": "Игрок: −35 заражения; снимает тошноту, слепоту и замедление.",
  "tooltip.carnis.purification_dart.protocol": "Обращает мутацию гуманоидов; ранит и оглушает крупные организмы Улья.",
  "tooltip.carnis.purification_serum": "Выпейте, чтобы снизить заражение на 35 пунктов.",
  "tooltip.carnis.purification_serum.mechanics": "Выпейте, чтобы снять 35 очков заражения.",
  "tooltip.carnis.purification_serum.use": "Выпейте напрямую или изготовьте дротики очищения.",
  "tooltip.carnis.pustule_cluster": "Наступите без приседания: пустулы лопнут и заразят вас.",
  "tooltip.carnis.research_journal": "Полевой справочник по улью.",
  "tooltip.carnis.sinew_spikes": "Колючие наросты замедляют существ.",
  "tooltip.carnis.sinew_spikes.lore": "Натянутые жилы реагируют на малейшую вибрацию шагов.",
  "tooltip.carnis.sinew_spikes.mechanics": "Наносят колющий урон и замедляют любое наступившее существо.",
  "tooltip.carnis.spore_sprout": "Органический росток выпускает споры.",
  "tooltip.carnis.stomach_pool": "Едкая ткань растворяет предметы в биомассу.",
  "tooltip.carnis.tainted_sludge_bucket": "Ведро заразной слизи.",
  "tooltip.carnis.veins": "Живые вены несут инфекцию через древесину.",
  "tooltip.carnis.viral_dart": "Добавляет игрокам 25 заражения и вызывает слабость.",
  "tooltip.carnis.viral_dart.mechanics": "Игрок: +25 заражения и слабость.",
  "tooltip.carnis.viral_dart.protocol": "Ускоряет инкубацию скота; мутирует зомби, скелетов и криперов."
}

```

### `src/main/resources/assets/carnis/models/item/parasitic_tendril_spawn_egg.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "carnis:item/parasitic_tendril_spawn_egg"
  }
}

```

### `src/main/resources/assets/carnis/models/item/hive_sentinel_spawn_egg.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "carnis:item/hive_sentinel_spawn_egg"
  }
}

```

### `src/main/resources/assets/carnis/models/item/cerebral_nexus_spawn_egg.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "carnis:item/cerebral_nexus_spawn_egg"
  }
}

```

## Новые PNG в проекте

- `src/main/resources/assets/carnis/textures/item/parasitic_tendril_spawn_egg.png`
- `src/main/resources/assets/carnis/textures/item/hive_sentinel_spawn_egg.png`
- `src/main/resources/assets/carnis/textures/item/cerebral_nexus_spawn_egg.png`
- `src/main/resources/assets/carnis/textures/item/viral_dart.png`
- `src/main/resources/assets/carnis/textures/item/purification_dart.png`
- `src/main/resources/assets/carnis/textures/item/neural_binding_matrix.png`
- `src/main/resources/assets/carnis/textures/item/creeping_tendrils.png`
- `src/main/resources/assets/carnis/textures/block/creeping_tendrils.png`
