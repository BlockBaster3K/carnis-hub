# CARNIS · ответы Q6/Q7 для диффа 18B (версия 3.4.5, банк на 121 файл)

Проверено не по памяти: манифест (121 .ogg) сверен с декларациями из присланного ранее `sounds.json` (62 события, 113 уникальных ссылок).

**Сводка сверки:** 113 ссылок → **85 закрыты файлами**, **28 без файла**; обратная сторона — **36 файлов без события** (из них 14 — архив `*_w1516`, 22 — новые/неподключённые).

---

## Q7. Официальная таблица переименований — 29 строк

Это ровно то, что я сделал в аудите 3.4.5, чтобы файлы совпали с декларациями. Колонки: **старое имя (что могло быть в дереве Кодера) → новое имя (что лежит у меня = декларация)**.

### `combat/` — 13 строк (расширение `combat_armor_deflect_*` → `combat_deflect_*` и т. д.)

| # | Старое (в проекте/в старом банке) | Новое (= в моём банке и в `sounds.json`) |
|---|---|---|
| 1 | `combat/combat_armor_deflect_01_chitin.ogg` | `combat/combat_deflect_01_chitin.ogg` |
| 2 | `combat/combat_armor_deflect_02_bone.ogg` | `combat/combat_deflect_02_bone.ogg` |
| 3 | `combat/combat_armor_deflect_03_metal.ogg` | `combat/combat_deflect_03_metal.ogg` |
| 4 | `combat/combat_armor_deflect_04_glance.ogg` | `combat/combat_deflect_04_glance.ogg` |
| 5 | `combat/combat_armor_deflect_05_parry.ogg` | `combat/combat_deflect_05_parry.ogg` |
| 6 | `combat/combat_block_stab_01_bone.ogg` | `combat/combat_stab_01_bone.ogg` |
| 7 | `combat/combat_block_stab_02_chitin.ogg` | `combat/combat_stab_02_chitin.ogg` |
| 8 | `combat/combat_block_stab_03_shield.ogg` | `combat/combat_stab_03_shield.ogg` |
| 9 | `combat/combat_dismember_01_ribs.ogg` | `combat/dismember_01.ogg` |
| 10 | `combat/combat_dismember_02_pustule.ogg` | `combat/dismember_02.ogg` |
| 11 | `combat/combat_dismember_03_sinew.ogg` | `combat/dismember_03.ogg` |
| 12 | `combat/combat_dismember_04_plate.ogg` | `combat/dismember_04.ogg` |
| 13 | `combat/combat_dismember_05_limb.ogg` | `combat/dismember_05.ogg` |

### `hive/` → `hive/` — 6 строк (`hive_detail_*` → `detail_*`)

| # | Старое | Новое |
|---|---|---|
| 14 | `hive/hive_detail_flow_01.ogg` | `hive/detail_flow_01.ogg` |
| 15 | `hive/hive_detail_flow_02.ogg` | `hive/detail_flow_02.ogg` |
| 16 | `hive/hive_detail_membrane_01.ogg` | `hive/detail_membrane_01.ogg` |
| 17 | `hive/hive_detail_bubbles_01.ogg` | `hive/detail_bubbles_01.ogg` |
| 18 | `hive/hive_detail_creak_01.ogg` | `hive/detail_creak_01.ogg` |
| 19 | `hive/hive_detail_scuttle_01.ogg` | `hive/detail_scuttle_01.ogg` |

### `hive/` — 4 строки (`spawn_hurt_critical_*` → `hive_spawn_hurt_critical_*`)

| # | Старое | Новое |
|---|---|---|
| 20 | `hive/spawn_hurt_critical_01.ogg` | `hive/hive_spawn_hurt_critical_01.ogg` |
| 21 | `hive/spawn_hurt_critical_02.ogg` | `hive/hive_spawn_hurt_critical_02.ogg` |
| 22 | `hive/spawn_hurt_critical_03.ogg` | `hive/hive_spawn_hurt_critical_03.ogg` |
| 23 | `hive/spawn_hurt_critical_04.ogg` | `hive/hive_spawn_hurt_critical_04.ogg` |

### `hive/` → `block/` — 6 строк (перенос каталога + имя уже было верным)

| # | Старое (каталог неверный) | Новое |
|---|---|---|
| 24 | `hive/hive_block_place_01_soft.ogg` | `block/hive_block_place_01_soft.ogg` |
| 25 | `hive/hive_block_place_02_dense.ogg` | `block/hive_block_place_02_dense.ogg` |
| 26 | `hive/hive_block_place_03_wet.ogg` | `block/hive_block_place_03_wet.ogg` |
| 27 | `hive/hive_block_break_01_tear.ogg` | `block/hive_block_break_01_tear.ogg` |
| 28 | `hive/hive_block_break_02_pop.ogg` | `block/hive_block_break_02_pop.ogg` |
| 29 | `hive/hive_block_break_03_crunch.ogg` | `block/hive_block_break_03_crunch.ogg` |

Итого 29/29. Уточнение: в вопросе было `spawn_hunt_critical_*` — правильное имя `spawn_hurt_critical_*` (стр. 20–23).

### Дополнительно: 5 «алиасов», которые не переименование, а сопоставление
Эти позиции **закрыты файлами, но под другими именами с номером варианта** — в декларации имя без номера. Не переименовывать, а привязать:

| Позиция в `sounds.json` | Чем закрывается у меня |
|---|---|
| `entity/amalgam_smash` | `entity/flesh_amalgam_smash_01.ogg`, `_02.ogg` |
| `entity/amalgam_roar` | `entity/flesh_amalgam_roar_01.ogg`, `_02.ogg` |
| `entity/amalgam_step` | `entity/flesh_amalgam_step_01.ogg`, `_02.ogg` |
| `entity/flesh_amalgam_hurt` | `entity/flesh_amalgam_hurt_01.ogg` |
| `entity/flesh_amalgam_death` | `entity/flesh_amalgam_death_01.ogg` |

Вариант решения (зона Кодера): либо добавить эти файлы вторыми `{"name": …, "weight": …}` в те же события, либо объявить позиции с номерами. Генерация тут **не нужна**.

---

## Q6. Категории, для которых я НИКОГДА не генерировал файлов

### 6.1 Реальные дыры с моей стороны — 23 позиции в 4 каталогах

| Каталог | Кол-во | Позиции | Комментарий |
|---|---|---|---|
| `hallucination/` | **3** | `phantom_creeper`, `phantom_footsteps`, `phantom_whisper` | Каталог не создавался ни в одной волне. Спецификации на галлюцинации в ТЗ волн 1–18 не было |
| `item/` | **4** | `inoculator_fire`, `dart_hit`, `purifier_ignite`, `purifier_loop` | Инокулятор, дротик, Био-Очиститель. Предметных волн у меня не было вообще |
| `block/` | **11** | `heartbeat_loop`, `hive_heartbeat`, `heart_pulse`, `hive_alarm`, `hive_eye_screech`, `digestor_churn`, `synapse_rupture`, `nervous_twitch`, `bone_deflect`, `pustule_burst`, `creeper_rupture` | Блочные/механические звуки вне волн 9–10. Два из них (`heart_pulse`, `heartbeat_loop`) — заявленные лупы, их я не делал ни разу |
| `entity/` | **5** | `acid_splash`, `amalgamation_fuse`, `flamethrower_fire`, `organic_creak`, `flesh_amalgam_ambient` | `flesh_amalgam_ambient` — единственная позиция амальгамы, которую я пропустил в волне 17 (делал smash/roar/step/hurt/death, ambient — нет) |
| **всего** | **23** | | |

### 6.2 Позиции, которые выглядят дырой, но закрываются алиасом — 5
См. таблицу выше (`entity/amalgam_smash|roar|step`, `entity/flesh_amalgam_hurt|death`). **Итого 23 + 5 = 28** = ровно столько, сколько даёт сверка.

### 6.3 Что есть у меня, но не объявлено в событиях — 36 файлов
Из них:
- **14** — архив `*_w1516` (в проект не переносить, откат по вашему правилу);
- **14** — новые файлы волны 18 (`hive/amalgam_shuffle_01…03`, `amalgam_breath_01…02`, `amalgam_slam_01…02`, `spawn_creeper_sac_01…03`, `crawl_01…02`, `detonate_01…02`) → **нужны события `hive.amalgam.*` и `hive.spawn.creeper_*` в `sounds.json`**, иначе файлы остаются сиротами (это и есть главная причина тишины по этим 6 событиям);
- **8** — `entity/flesh_amalgam_*` (5 закрывают алиасы из Q7, 3 требуют привязки по номерам).

### 6.4 Типы, которых я не делал вообще (для планирования 18B)
- **лупы** (`stream: true`, зацикленные: `heartbeat_loop`, `purifier_loop`) — у меня весь банк one-shot, кроме амбиентов `amb/*` и `hive/amb_*`;
- **предметы и инструменты** (`item.*`) — 4 позиции, ни одной волны;
- **галлюцинации** (`hallucination/`) — 3 позиции, каталог пуст;
- **блок-механика вне улья** (`pustule_burst`, `bone_deflect`, `creeper_rupture`, `synapse_rupture`, `nervous_twitch`) — 5 позиций.

Оценка объёма, если дифф покажет, что всё это надо генерировать: **23 файла** (при 1 файле на позицию). Это **2 батча** по моей ёмкости 12–16: батч 1 — `entity/` (5) + `block/` (11) = 16; батч 2 — `item/` (4) + `hallucination/` (3) + доборы = 7–9. Если по каким-то позициям потребуется по 2–3 варианта (как у скелета/крипера), объём вырастет до 40–60 и станет 4 батча.

---

## Важное предупреждение к диффу (следствие моей замены в 18A)

В 18A я по вашему протоколу положил 14 новых файлов **на канонические пути**, а старые убрал в `*_w1516.ogg` **внутрь рабочего дерева** `assets/carnis/sounds/hive/`. Из этого два следствия для вашего диффа:

1. Если Кодер/Ревизор увидит в ресурсах `hive/*_w1516.ogg` — это **не** игровые ассеты, а мой архив отката. В манифесте они помечены и в проект не переносятся (**107 строк к переносу из 121**).
2. Если вы будете диффить по именам **без** учёта моего манифеста, 14 канонических имён `amalgam_*`/`spawn_creeper_*` у Кодера сейчас, скорее всего, содержат **старые** файлы волн 15/16 (размеры 18 436…44 121 байт вместо моих 11 723…47 090). Это тоже даст «расхождение», хотя оба варианта лежат у меня.

Чтобы дифф был однозначным, присылайте дерево Кодера **с размерами в байтах** — я сопоставлю по (путь + размер) и однозначно скажу для каждой строки: «файла нет», «файл есть, но старый вариант (w1516)», «файл есть, имя отличается (см. Q7)».

## Служебное

- `build/` — удалён после сверки, в воркспейсе только `.ogg`, `.md`, `MANIFEST_ogg.txt`.
- Манифест не менялся с предыдущего отчёта: **121 строка**, 11 247 270 байт.
- Генерацию 18B не начинал — жду дифф.
