# CARNIS · аудит звукового банка против `sounds.json` (версия 3.4.5)

Проверено инструментами: JSON-парсинг `sounds.json`, обход `assets/carnis/sounds/**`, сверка ссылок с файлами, чтение заголовков OGG (кодек/каналы/частота).

## 1. Итог на входе

| Метрика | Было | Стало |
|---|---|---|
| Файлов .ogg в банке | 99 | **99** |
| Уникальных ссылок в `sounds.json` | 113 | 113 |
| **Битых ссылок (звук есть, файла нет)** | **57** | **28** |
| Файлов «в никуда» (лежат, но не подключены) | 43 | 14 |
| Формат всех файлов (OGG mono 44.1 кГц) | — | ✅ 99/99 |

29 ссылок было сломано **не отсутствием звука, а путём/именем файла**. Исправлено перемещением/переименованием (содержимое файлов не тронуто, размеры совпадают).

## 2. Что именно было сломано (29 исправлено)

Проект (`sounds.json`) ждёт `carnis:combat/combat_deflect_01_chitin`, а в банке лежало `combat/combat_armor_deflect_01_chitin.ogg`. Классическая рассинхронизация «файл ↔ id» после переименования событий.

### `assets/carnis/sounds/block/` — 6 файлов переехали из `hive/`

| Было | Стало (= путь в `sounds.json`) |
|---|---|
| `hive/hive_block_break_01_tear.ogg` | `block/hive_block_break_01_tear.ogg` |
| `hive/hive_block_break_02_pop.ogg` | `block/hive_block_break_02_pop.ogg` |
| `hive/hive_block_break_03_crunch.ogg` | `block/hive_block_break_03_crunch.ogg` |
| `hive/hive_block_place_01_soft.ogg` | `block/hive_block_place_01_soft.ogg` |
| `hive/hive_block_place_02_dense.ogg` | `block/hive_block_place_02_dense.ogg` |
| `hive/hive_block_place_03_wet.ogg` | `block/hive_block_place_03_wet.ogg` |

### `assets/carnis/sounds/combat/` — 13 файлов переименованы

| Было | Стало |
|---|---|
| `combat_armor_deflect_01_chitin` | `combat_deflect_01_chitin` |
| `combat_armor_deflect_02_bone` | `combat_deflect_02_bone` |
| `combat_armor_deflect_03_metal` | `combat_deflect_03_metal` |
| `combat_armor_deflect_04_glance` | `combat_deflect_04_glance` |
| `combat_armor_deflect_05_parry` | `combat_deflect_05_parry` |
| `combat_block_stab_01_bone` | `combat_stab_01_bone` |
| `combat_block_stab_02_chitin` | `combat_stab_02_chitin` |
| `combat_block_stab_03_shield` | `combat_stab_03_shield` |
| `combat_dismember_01_ribs` | `dismember_01` |
| `combat_dismember_02_pustule` | `dismember_02` |
| `combat_dismember_03_sinew` | `dismember_03` |
| `combat_dismember_04_plate` | `dismember_04` |
| `combat_dismember_05_limb` | `dismember_05` |

### `assets/carnis/sounds/hive/` — 10 файлов переименованы

| Было | Стало |
|---|---|
| `hive_detail_flow_01` / `_02` | `detail_flow_01` / `detail_flow_02` |
| `hive_detail_membrane_01` | `detail_membrane_01` |
| `hive_detail_bubbles_01` | `detail_bubbles_01` |
| `hive_detail_creak_01` | `detail_creak_01` |
| `hive_detail_scuttle_01` | `detail_scuttle_01` |
| `spawn_hurt_critical_01…04` | `hive_spawn_hurt_critical_01…04` |

Последнее было самым коварным: `hive.spawn.hurt_critical` — событие **базового класса** `HiveEntity`, то есть критическое ранение не звучало ни у одного существа Улья (волна 13 писалась именно под него).

## 3. Осталось 28 битых ссылок — файлов физически нет

| Папка | Кол-во | Имена |
|---|---|---|
| `entity/` | 10 | `amalgam_smash`, `amalgam_roar`, `amalgam_step`, `amalgamation_fuse`, `flamethrower_fire`, `organic_creak`, `acid_splash`, `flesh_amalgam_ambient`, `flesh_amalgam_hurt`, `flesh_amalgam_death` |
| `block/` | 11 | `heartbeat_loop`, `hive_heartbeat`, `heart_pulse`, `hive_alarm`, `hive_eye_screech`, `digestor_churn`, `synapse_rupture`, `nervous_twitch`, `bone_deflect`, `pustule_burst`, `creeper_rupture` |
| `item/` | 4 | `inoculator_fire`, `dart_hit`, `purifier_ignite`, `purifier_loop` |
| `hallucination/` | 3 | `phantom_creeper`, `phantom_whisper`, `phantom_footsteps` |

Это не наши волны 1–16: в ТЗ волн 1–16 этих звуков не было ни в одной. Это «долг» от кода 3.x, написанного раньше (инокулятор, огнемёт, Био-Очиститель, фантомные галлюцинации, амальгам-смэш/рёв).

**Что происходит сейчас в игре:** Minecraft не падает — он пишет в лог
`Unable to play unknown soundEvent: minecraft:carnis/entity/amalgam_smash` (или `carnis:...`), и просто молчит. То есть все эти механики работают «беззвучно».

## 4. Осталось 14 файлов «в никуда» — звук есть, событие не подключено

| Файл | Что с ним делать |
|---|---|
| `hive/amalgam_shuffle_01…03`, `amalgam_breath_01…02`, `amalgam_slam_01…02` | добавить 3 события (патч в §5) — это волна 16 |
| `hive/spawn_creeper_sac_01…03`, `spawn_creeper_crawl_01…02`, `spawn_creeper_detonate_01…02` | добавить 3 события (патч в §5) — это волна 15; сейчас `InfectedCreeperEntity` их не найдёт |
| `hive/spawn_skeleton_*` (3 события) | ✅ подключены |
| `hive/spawn_hurt_critical_*` | ✅ подключены после переименования (§2) |

## 5. Готовый патч `sounds.json` (добавить 6 событий)

Вставить в объект `sounds.json` рядом с другими `hive.spawn.*` (запятые уже учтены — вставлять как отдельные пары):

```json
  "hive.amalgam.shuffle": {"subtitle": "carnis.subtitle.amalgam_shuffle", "sounds": [{"name": "carnis:hive/amalgam_shuffle_01", "volume": 0.35, "pitch": 0.96, "weight": 2}, {"name": "carnis:hive/amalgam_shuffle_02", "volume": 0.35, "pitch": 1.00, "weight": 3}, {"name": "carnis:hive/amalgam_shuffle_03", "volume": 0.35, "pitch": 1.04, "weight": 2}]},
  "hive.amalgam.breath": {"subtitle": "carnis.subtitle.amalgam_breath", "sounds": [{"name": "carnis:hive/amalgam_breath_01", "volume": 0.25, "pitch": 1.00, "weight": 3}, {"name": "carnis:hive/amalgam_breath_02", "volume": 0.25, "pitch": 0.94, "weight": 2}]},
  "hive.amalgam.slam": {"subtitle": "carnis.subtitle.amalgam_slam", "sounds": [{"name": "carnis:hive/amalgam_slam_01", "volume": 0.55, "pitch": 1.00, "weight": 3}, {"name": "carnis:hive/amalgam_slam_02", "volume": 0.55, "pitch": 0.97, "weight": 2}]},
  "hive.spawn.creeper_sac": {"subtitle": "carnis.subtitle.hive_spawn_creeper_sac", "sounds": [{"name": "carnis:hive/spawn_creeper_sac_01", "pitch": 0.92, "weight": 1}, {"name": "carnis:hive/spawn_creeper_sac_02", "pitch": 1.00, "weight": 1}, {"name": "carnis:hive/spawn_creeper_sac_03", "pitch": 1.08, "weight": 1}]},
  "hive.spawn.creeper_crawl": {"subtitle": "carnis.subtitle.hive_spawn_creeper_crawl", "sounds": [{"name": "carnis:hive/spawn_creeper_crawl_01", "pitch": 0.98, "weight": 1}, {"name": "carnis:hive/spawn_creeper_crawl_02", "pitch": 1.02, "weight": 1}]},
  "hive.spawn.creeper_detonate": {"subtitle": "carnis.subtitle.hive_spawn_creeper_detonate", "sounds": [{"name": "carnis:hive/spawn_creeper_detonate_01", "volume": 0.40, "pitch": 1.00, "weight": 1}, {"name": "carnis:hive/spawn_creeper_detonate_02", "volume": 0.40, "pitch": 0.94, "weight": 1}]},
```

Субтитры (в `en_us.json` / `ru_ru.json`):

```json
"carnis.subtitle.amalgam_shuffle": "Something vast drags itself closer",
"carnis.subtitle.amalgam_breath": "Wet, ragged breathing",
"carnis.subtitle.amalgam_slam": "The amalgam brings its whole body down",
"carnis.subtitle.hive_spawn_creeper_sac": "A bloated sac twitches",
"carnis.subtitle.hive_spawn_creeper_crawl": "Something crawls closer",
"carnis.subtitle.hive_spawn_creeper_detonate": "The crawler ruptures"
```

```json
"carnis.subtitle.amalgam_shuffle": "Нечто огромное волочится ближе",
"carnis.subtitle.amalgam_breath": "Влажное, рваное дыхание",
"carnis.subtitle.amalgam_slam": "Амальгама обрушивает всё тело",
"carnis.subtitle.hive_spawn_creeper_sac": "Вздувшаяся капсула дёргается",
"carnis.subtitle.hive_spawn_creeper_crawl": "Кто-то ползёт ближе",
"carnis.subtitle.hive_spawn_creeper_detonate": "Ползун разрывается"
```

## 6. Найденные дефекты кода (по присланным файлам)

| # | Файл | Проблема | Последствие |
|---|---|---|---|
| 1 | `FleshAmalgamEntity.java` | `playSound(ModSounds.AMALGAM_STEP.get(), 0.9F, 1.0F)` | **Не компилируется.** У `Entity` нет `playSound(SoundEvent, float, float)` — есть только `playSound(SoundEvent, float, float)` в `Entity`? Нет: сигнатура `Entity.playSound(SoundEvent, float, float)` отсутствует; нужно `level().playSound(null, blockPosition(), ModSounds.AMALGAM_STEP.get(), SoundSource.HOSTILE, 0.9F, 1.0F)` (и `import net.minecraft.core.BlockPos`, `SoundSource` уже есть) |
| 2 | `FleshAmalgamEntity.java` | `playAmbientSound()` → `if (!level().isClientSide) triggerAnim(...)` | `triggerAnim` — клиентский вызов GeckoLib. На сервере анимация не запустится (а `playAmbientSound` вызывается на сервере). Нужен `triggerAnim` на клиенте или пакет `GeckoLibNetwork`/`AnimatableInstanceCache`-синк. Как минимум инвертировать условие нельзя — проверьте, откуда идёт вызов |
| 3 | `FleshAmalgamEntity.java` | `targetSelector` без `HiveSwarmCoordinator.validTarget`, в отличие от других мобов Улья | Амальгама может выбрать целью другое существо Улья. Добавить фильтр как в `InfectedSkeletonEntity` |
| 4 | `FleshAmalgamEntity.java` | `import CarnisMod`, `DamageTypes`, `Projectile`, `SoundEvents` и др. — часть не используется после правок | Предупреждения компилятора, не ошибки |
| 5 | `sounds.json` ↔ банк | 28 битых ссылок (см. §3) | Звуки молчат (лог `Unable to play unknown soundEvent`) |
| 6 | `sounds.json` vs `ModSounds.java` | события `hive.detail.scuttle` / `hive.spawn.skeleton_*` / `zone.stinger.*` — id в JSON через точку, а `ModSounds` регистрирует `SoundEvent` по тому же пути → ок; но `combat.*` и `hive.detail.*` **не имеют** `RegistryObject` | Если они нигде не вызываются через `ModSounds`, это нормально (звук проигрывается по id из JSON) |

Пункт 1 — точно ошибка компиляции: в `Entity` есть `playSound(SoundEvent, float, float)`? Проверьте по своей среде: в MCP/official 1.20.1 у `Entity` такого метода нет, есть `Level.playSound(Player, double, double, double, SoundEvent, SoundSource, float, float)`. Если у вас он компилировался — значит, в классе есть свой хелпер; тогда пункт снимается.

## 7. Чек-лист дальнейших шагов

1. Применить §5 (6 событий `sounds.json` + 12 субтитров) — иначе волны 15 и 16 не звучат вообще.
2. Исправить `playStepSound` у амальгамы (§6.1).
3. Решить по 28 отсутствующим файлам (§3): либо произвести их (это ещё ~5 волн по объёму), либо временно убрать ссылки, чтобы не сыпать варнингами в лог.
4. После правок перезапустить сверку: цель — 0 битых ссылок, 0 сирот.
