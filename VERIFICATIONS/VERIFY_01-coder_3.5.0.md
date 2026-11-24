# VERIFY_01-coder_3.5.0 — независимая проверка Интегратора

**Дата:** 2026-11-24
**Объект:** поставка Кодера 3.5.0 — `01-coder/3.5.0/` (6 файлов, 1 988 932 Б)
**Основание:** вердикт Ревизора `02-reviewer/PhaseF_Revision_3.5.0.md` (sha256 `3e36ce40…`)
**Принцип:** правило 5 — не принимать на слово. Все заявления вердикта перепроверены по файлам.
**Вердикт Интегратора:** ✅ **ПОДТВЕРЖДЁН** — ни одного расхождения не найдено.

---

## 1. Состав поставки

| Файл | Байт | SHA-256 |
|---|---:|---|
| `project-3.5.0-clean.zip` | 814 326 | `11833ab250a815fa85c01eb2bef68ef544440e857cf43ccd8ba3a46a789f3ec5` |
| `project-3.5.0-clean.manifest.txt` | 84 154 | `f0ebffeb9e8a0ebaf824579437ddfa5675a2941034021e09451c671d797f3c5f` |
| `PHASE_F_3_5_0_FULL_JAVA_DUMP.md` | 1 039 782 | `5c58109cff686a73ce9547e184bd455117ae465424b9f23f026477d0cf6bb558` |
| `PHASE_F_3_5_0_REPORT.md` | 8 110 | `e6b0fdead99469d6732c45f80a51c6e36b9f501943cda318fc0a5daedb78027c` |
| `MANIFEST.txt` | 42 104 | `9f6ce313a6ceb16c576b84124961e30337025e669ae67862c054c9dac615c2f9` |
| `SHA256SUMS.txt` | 456 | `2bdd70fc59967e0957349f630e8f502a2c32af47b15c6eac3321ada9fe34b37c` |

`sha256sum -c SHA256SUMS.txt` — **5/5 OK** (сам `SHA256SUMS.txt` себя не включает, как и заявлено).

---

## 2. Перепроверка заявлений вердикта

| № | Заявление Ревизора | Независимая проверка | Итог |
|---|---|---|---|
| 1 | SHA256SUMS 5/5 OK | `sha256sum -c` → 5 OK, 0 FAILED | ✅ |
| 2 | Версия 3.5.0 ×3, без `jarVersion` | `gradle.properties:14` `mod_version=3.5.0`; `mods.toml:7` `version="3.5.0"`; `mods.toml:9` `displayVersion="3.5.0"`; `build.gradle:8` `version = project.property('mod_version')`; grep `jarVersion` → 0 | ✅ |
| 3 | G1: `ModLanguageProvider` удалён из кода | `find src -name ModLanguageProvider.java` → 0; grep по `src/` → 0 упоминаний | ✅ |
| 4 | G1: `DataGenerators` без Language-провайдера | Прочитан файл: регистрируются только `CarnisTextureDataGen`, `ModBlockStateProvider`, `ModItemModelProvider`, `ModBlockTagsProvider`. Упоминаний Language — 0 | ✅ |
| 5 | G2: null-фолбэк `getExploder → getIndirectSourceEntity` | `CarnisEvents.java:42-43`: `Entity exploder = explosion.getExploder();` / `if (exploder == null) exploder = explosion.getIndirectSourceEntity();` | ✅ |
| 6 | `sounds.json`: 80 событий, sha `0531beec…` ≠ старый `b44634bc` | 80 событий; sha256 = `0531beecb98e3ba509c3568657a1b83c39ed9133b57e4f4fb8f53f2eb9333b69` | ✅ |
| 7 | 12/12 новых событий на месте | Диф с 3.4.10: **добавлено 12, удалено 0** | ✅ |
| 8 | Dotted-алиасов НЕТ | `hive.spawn.*` → 0; `hive.amalgam.*` (как dotted-алиас) → 0. Ключи вида `hive.spawn_creeper_sac` — легальные MC-имена событий, не алиасы | ✅ |
| 9 | `hive.spawn_creeper_sac` → семейство `_01…03` | 3 записи: `carnis:hive/spawn_creeper_sac_01/02/03` | ✅ |
| 10 | `hive.amalgam_shuffle` → семейство `_01…03` | 3 записи: `carnis:hive/amalgam_shuffle_01/02/03` | ✅ |
| 11 | `synapse_shock` → `block/synapse_shock` | `carnis:block/synapse_shock` | ✅ |
| 12 | `hive.amalgam_breath` не тронут | `{"name":"carnis:entity/flesh_amalgam_ambient","volume":0.25,"pitch":1.0,"weight":1}` — идентичен 3.4.10 | ✅ |
| 13 | lang 341/341 паритет, wrong-ns 0 | `en_us` 341, `ru_ru` 341. Wrong-ns (ключ с namespace не на месте: `subtitles.*`, `carnis.carnis`, `.carnis`-суффикс) → **0**. `itemGroup.carnis` и `death.attack.*` — легальные MC-ключи, не дефект | ✅ |
| 14 | `carnis.subtitle.*` = 88, 20 новых, ни один старый не потерян | 3.4.10: 68 → 3.5.0: **88** (+20). **Потеряно старых: 0.** Добавлено 20 | ✅ |
| 15 | Блоков 21, recipes 41, advancements 6 | `blockstates/*.json` = 21; `recipes/*.json` = 41; `advancements/*.json` = 6 | ✅ |
| 16 | ModItems: 50 уникальных = 50 предметов | `ITEMS.register("…")` → **50 регистраций, 50 уникальных имён, 0 дублей** | ✅ |
| 17 | Манифест: 637 записей, 637/637 OK, файлов вне манифеста нет | На диске 637 файлов; в манифесте 637 записей; сверено **637/637 OK**; missing 0; extra 0 | ✅ |
| 18 | Корень zip: только 5 элементов | `MANIFEST.txt`, `build.gradle`, `gradle.properties`, `settings.gradle`, `src` | ✅ |
| 19 | `SORT_1.md 2134f0f5…`, STATUS `b7228e6f…` | Совпали с содержимым `main` (`7b06b43`) | ✅ |

### 2.1. Разбор «20 новых субтитров»

Ревизор объясняет их как «12 новых событий + 8 переименованных по фрагменту». Проверка по факту:

- 12 ключей — новые события (12/12 из п. 7);
- 6 ключей — переадресация существующих событий на новое семейство: `spawn_creeper_crawl`, `spawn_creeper_detonate`, `spawn_creeper_sac`, `spawn_skeleton_blade`, `spawn_skeleton_bonecrack`, `spawn_skeleton_whip`;
- 2 ключа — `amalgam_shuffle`, `amalgam_slam`.

Итого 12 + 6 + 2 = 20. Формулировка «8 переименованных» по факту распадается на 6 переадресованных + 2 записи с изменённым `volume/pitch/weight`. **Это уточнение формулировки, не дефект** — итоговое число (20) и главное утверждение «ни один старый не потерян» подтверждены.

---

## 3. Минорный дефект дампа — подтверждён

Ревизор: «247 секций вместо 232».

| Проверка | Факт |
|---|---|
| Заголовков `## ` в дампе | **248** |
| Из них с путём `.java` | **247** |
| Уникальных путей `.java` | **233** |
| Задублированных файлов | **14** (ровно те, что названы в вердикте) |
| Лишних секций от дублей | **14** |
| Отдельная секция «Удалённый после baseline файл» | 1 (`ModLanguageProvider.java`) |
| `.java` в zip 3.5.0 | **232** |
| `.java` из zip, не покрытых дампом | **0** |

Арифметика сходится: 247 − 14 дублей = 233 = 232 файла из zip + 1 удалённый `ModLanguageProvider`. Список из 14 задублированных файлов в вердикте совпадает с фактическим **побайтово по именам**.

**Дефект — в артефакте (справочный дамп), не в коде.** Код поставки не затронут. Решение «код не трогать» принято.

---

## 4. Итог

| Показатель | Значение |
|---|---|
| Проверок выполнено | 19 |
| Расхождений с вердиктом | **0** |
| Уточнений формулировки | 1 (§2.1, число 20 подтверждено) |
| Дефектов кода | 0 |
| Дефектов артефакта | 1 (дубли в дампе, подтверждён) |

**Интегратор подтверждает вердикт Ревизора: ПРИНЯТО.**
Изменений в коде поставки не вносилось. Файлы поставки не модифицировались.
