# ВЕРДИКТ: приёмка 3.5.0 — ПРИНЯТО

**Дата:** 2026-11-22 · **Проверяющий:** координатор (статика, без сборки — сборка запрещена)
**Пакет:** `01-coder/3.5.0/project-3.5.0-clean.zip` (637 файлов) + `project-3.5.0-clean.manifest.txt` + `PHASE_F_3_5_0_FULL_JAVA_DUMP.md`

## Итог: ПРИНЯТО ✅

Все проверки пройдены. Один минорный дефект артефакта (не кода) — см. ниже.

## Что проверено и сошлось

| Проверка | Результат |
|---|---|
| SHA256SUMS (5 файлов) | 5/5 OK |
| Версия 3.5.0 ×3 (gradle / mods.toml / display), без `jarVersion` | ✅ |
| G1: `ModLanguageProvider` удалён из кода, `DataGenerators` без Language-провайдера | ✅ |
| G2: null-фолбэк `getExploder → getIndirectSourceEntity` | ✅ (прочитан код `CarnisEvents` вручную: `if (exploder == null) exploder = explosion.getIndirectSourceEntity();`) |
| sounds.json: 80 событий, sha `0531beec…` (≠ старый `b44634bc`) | ✅ |
| 12/12 новых событий на месте | ✅ |
| Dotted-алиасов НЕТ; `hive.spawn_creeper_sac` → семейство `hive/spawn_creeper_sac_01…03`, `hive.amalgam_shuffle` → `hive/amalgam_shuffle_01…03` | ✅ |
| `synapse_shock` → `block/synapse_shock` | ✅ |
| `hive.amalgam_breath` не тронут (→ `entity/flesh_amalgam_ambient`) | ✅ |
| lang: 341/341 паритет, wrong-ns 0 | ✅ |
| Субтитры `carnis.subtitle.*` = 88 | ✅ легально: 20 новых = 12 новых событий + 8 переименованных по фрагменту, ни один старый не потерян |
| Блоков 21, recipes 41, advancements 6 | ✅ |
| ModItems: 50 уникальных имён = 50 предметов | ✅ («57 строк» — это строки файла, не предметы) |
| Манифест: 637 записей, все хеши сверены с содержимым zip | 637/637 OK, 0 ошибок, файлов вне манифеста нет |
| Корень zip: только 5 элементов | ✅ |
| SORT_1.md `2134f0f5…` и STATUS `b7228e6f…` | сошлись с репо |

## Минорный дефект (артефакт, не код)

**Дамп `PHASE_F_3_5_0_FULL_JAVA_DUMP.md`: 247 секций вместо 232.**
Разбор: 232 секции = все java-файлы zip (ни один не пропущен) + 1 секция удалённого `ModLanguageProvider.java` (устаревший остаток) + 14 дублей (14 файлов продублированы по 2 раза: `ClientModEvents`, `CodexContent`, `DataGenerators`, `ModBlockStateProvider`, `ModBlockTagsProvider`, `ModItemModelProvider`, `CarnisEvents`, `ModBlockTags`, `ModBlocks`, `ModCreativeTabs`, `ModEntities`, `ModItems`, `ModSounds`, `CarnisSoundTypes`).

**Решение:** код не трогать. Дамп — справочный артефакт; при следующем дампе (3.5.1 или пакетный тест) генерировать из чистого дерева без дублей и без удалённых файлов. На приёмку не влияет.

## Ответы Интегратору на 3 вопроса

1. **Приёмка 3.5.0 — СЕЙЧАС, по файлам.** Сборка (ФАЗА 2) — в пакетном тесте, не раньше. Вердикт выше — финальный по статике.
2. **`AUDIO_AUDIT_*` → Звукарю.** Файлы лежат в `03-sound/incoming/` — это его домен, он решает (включить в Волну 20 или архивировать). Ты их не трогаешь.
3. **R7 — ДА, так и надо.** Канон 3.4.9 нетронут, версия `a05f7467` в workspace — корректное состояние. Ничего не менять.
