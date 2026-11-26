# EVIDENCE — dump payload → baseline (проверка предсказания Ревизора)

**Дата:** 2026-11-23 · **Интегратор** · **Вердикт:** предсказание Ревизора
**подтверждено частично** (см. §4).

## 1. Входные артефакты и хеши

| Сторона | Источник в репозитории | Байт | SHA-256 |
|---|---|---:|---|
| LEFT (дамп) | `00-common/PHASE_F_3_4_8_FULL_DUMP.md`, фенс-тело `sounds.json`, строки 46043..46974 (932 строки) + завершающий LF | 20 197 | `819ddccdb733c89c42f4a800f69717255a3cf21576546b3f83431affe05aff27` |
| LEFT без LF | то же тело без финального перевода строки | 20 196 | `c72261bc063b6aeb4d56b65f6f7cc79e6756c3e441a69c07f9bfdf3d5f57b10e` |
| RIGHT (baseline) | `01-coder/3.4.9/sounds-3.4.8-baseline.json` | 20 259 | `66dc02006482041a99d101b611f7fcacdb0091525ed5c216958f7d02070536e7` |

Сам дамп целиком: 1 513 635 Б, 48 582 строки,
`e7b3281d6070b2f6e167b49f1b65f277a0512e249feccebea9e59446fe252187` — **эталон
подтверждён** (00-common). Заголовок секции — строка 46040, открывающий фенс — 46042,
закрывающий — 46975. Все значения совпадают с D2-описанием Ревизора.

Дифф: `VERIFICATIONS/EVIDENCE_dump_to_baseline.diff` (3 964 Б, 119 строк,
`ab7c9d1f0405ed1498fbd086e334f0e9d7711c5eec95ad99eb7d333ea2d836cf`).
**Обратимость проверена:** `patch` применяет дифф к payload и даёт baseline
**побайтово** (`cmp` без отличий).

## 2. Природа изменений — только ПУТИ

После вырезания всех подстрок `"name": "…"` оба JSON **идентичны**
(`diff` без отличий). Значит ни `volume`, ни `pitch`, ни `weight`, ни `stream`,
ни форматирование, ни порядок событий не менялись. Дельта размера +62 Б
объясняется **только** удлинением имён в 9 событиях (сумма дельт длин имён = +62).

## 3. Таблица изменённых событий (9 из 68)

| Событие | Было (дамп) | Стало (baseline) | Тип |
|---|---|---|---|
| `amalgam_smash` | `entity/amalgam_smash` ×2 | `entity/flesh_amalgam_smash_01`, `_02` | путь (нумерация) |
| `amalgam_roar` | `entity/amalgam_roar` ×2 | `entity/flesh_amalgam_roar_01`, `_02` | путь (нумерация) |
| `amalgam_step` | `entity/amalgam_smash` ×2 | `entity/flesh_amalgam_step_01`, `_02` | путь (нумерация **и переименование**: step ссылался на smash) |
| `flesh_amalgam_hurt` | `entity/flesh_amalgam_hurt` | `entity/flesh_amalgam_hurt_01` | путь (нумерация) |
| `flesh_amalgam_death` | `entity/flesh_amalgam_death` | `entity/flesh_amalgam_death_01` | путь (нумерация) |
| `hive.amalgam_shuffle` | `entity/amalgam_smash` | `block/creeper_rupture` | путь (замена сэмпла) |
| `hive.amalgam_slam` | `entity/amalgam_smash` | `block/creeper_rupture` | путь (замена сэмпла) |
| `hive.spawn_attack` | `entity/amalgam_smash`, `block/synapse_rupture`, `entity/acid_splash` | `block/creeper_rupture`, `block/synapse_rupture`, `entity/acid_splash` | путь (замена сэмпла №1) |
| `hive.spawn_skeleton_blade` | `entity/amalgam_smash`, `block/synapse_rupture`, `block/creeper_rupture` | `block/creeper_rupture`, `block/synapse_rupture`, `block/creeper_rupture` | путь (замена сэмпла №1) |

**Ни одного изменения громкости/питча/веса/stream — ноль.** Все 9 событий
изменены по типу «путь».

## 4. Проверка предсказания Ревизора — по пунктам

Формулировка предсказания: **«ровно 5 событий + 4 байта, в четырёх ничего»**.

| Часть предсказания | Факт | Итог |
|---|---|---|
| Изменено ровно **5** событий (smash, roar, step, hurt, death) | Изменено **9** событий | ❌ по числу |
| Эти 5 менялись по **пути** | Да, все 5 — только `name` | ✅ |
| Остальные **4** (shuffle, slam, spawn_attack, spawn_skeleton_blade) — «ничего» | У всех 4 **изменён путь**: `entity/amalgam_smash` → `block/creeper_rupture` | ❌ |

**Итог:** предсказание верно в части «5 из 9 менялись по пути» и
**неверно в части «в четырёх ничего»**. В четырёх hive-событиях менялись
именно **ПУТИ** (замена ссылки на `entity/amalgam_smash`), а не байты
форматирования. При этом `volume`/`pitch`/`weight` в этих четырёх
**не менялись ни на байт**.

## 5. Почему это не косметика — слышимость по трём состояниям

| Событие | дамп + дерево до R11 (24 .ogg) | baseline + после R11 (22 .ogg) | final + после R11 (22 .ogg) |
|---|---|---|---|
| `amalgam_smash` | HEARD | silent | silent |
| `amalgam_roar` | HEARD | silent | silent |
| `amalgam_step` | HEARD | silent | silent |
| `flesh_amalgam_hurt` | HEARD | silent | silent |
| `flesh_amalgam_death` | HEARD | silent | silent |
| `hive.amalgam_shuffle` | HEARD | **HEARD** | silent |
| `hive.amalgam_slam` | HEARD | **HEARD** | silent |
| `hive.spawn_attack` | HEARD | **HEARD** | silent |
| `hive.spawn_skeleton_blade` | HEARD | **HEARD** | silent |

Вывод: замена пути на `block/creeper_rupture` — **не «ничего»**, это замена
на реально существующий файл, из-за которой четыре hive-события оставались
**слышимыми** на baseline и замолчали только в final (после переезда на
`hive/*_01..04`, которых на диске нет). Именно эти 4 события дают дельту
baseline → final = **+4**, а вместе с 5 физически удалёнными R11 — дельту
дамп → final = **+9**.

## 6. Следствие для приёмки

Доказательство A1 закрывает вопрос «какой дифф правильный»:
`R7_baseline_to_final.diff` (4 события) и данный дифф (9 событий) —
**не противоречат друг другу**, они про разные пары состояний.

- 9 = 5 («путь» в 5 Amalgam-событиях) + 4 («путь» в 4 hive-событиях)
- 4 (в R7) = только hive-события, потому что 5 Amalgam-событий в baseline
  и final **совпадают**

Предсказание в редакции «5 путей + 4 ничего» неверно; корректная
формулировка: **«9 событий, все 9 — только пути; в 5 событиях — нумерация
сэмплов, в 4 hive — замена сэмпла на `block/creeper_rupture`»**.

Аномалия A1 в `VERIFY_01-coder_3.4.9.md` переводится в статус
**закрыта доказательством**, без влияния на приёмку: пакет
самодостаточен, `R7` воспроизводит final из baseline байт в байт.
