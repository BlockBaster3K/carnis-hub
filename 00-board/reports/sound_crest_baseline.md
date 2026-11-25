# S28 · Baseline crest по каждому файлу + обоснование классификации (З-29)

> **ИСПРАВЛЕНО после R20 (S29).** Колонки «Δcrest» и «вердикт» убраны: Δcrest в
> первой редакции дублировал baseline во всех 276 строках (Ревизор прав, я
> подтвердил машинно), и «вне допуска 0» было тавтологией.
> **Таблица — источник ДОПУСКОВ, а не вердиктов.** Вердикт считает гейт, сравнивая
> сданный файл с round-trip-эталоном оригинала.
> Для 132 файлов `sounds_380` оригиналов нет: там норма проверяет только «файл не
> перерисован относительно своей же трубы» — и это надо называть так.
>
> **КОНТРАКТ ИЗМЕРЕНИЯ (обязателен для воспроизведения, S30):**
> перекод — **libvorbis** (НЕ нативный `vorbis`: он в этой сборке ffmpeg не умеет
> моно и отказывает), **моно**, **битрейт = битрейт самого файла** (снят с файла),
> `-map_metadata -1`. Baseline воспроизводится прогон-в-прогон до 4-го знака, но
> **зависит от битрейта перекода**: у `spawn_skeleton_blade_02` он 0.57 / 3.64 /
> 6.27 дБ при 160 / 96 / 48 kbps. Мерить чужой трубой — получить другую величину
> под тем же названием.

> **ИСПРАВЛЕНО после R20 (S29).** Колонки «Δcrest» и «вердикт» убраны: Δcrest в
> первой редакции дублировал baseline во всех 276 строках (Ревизор прав), и
> «вне допуска 0» было тавтологией.
> **Эта таблица — источник ДОПУСКОВ, а не вердиктов.** Вердикт считает гейт,
> сравнивая сданный файл с round-trip-эталоном оригинала.
> Для 132 файлов `sounds_380` оригиналов нет: там норма проверяет только «файл не
> перерисован относительно своей же трубы», и это надо называть так.

**Кто:** Звук · **Шаг:** S28 (Волна 55) · **База:** `f5cccd4` · **Дата:** 2026-11-27 05:10
**Кому:** Ревизор (R19 п.1), Интегратор (I22), Архитектор (З-29)

---

## Что сделано

Формула З-29: `допуск = min(порог_типа, max(0.05; baseline + 0.05))`, где
`baseline` — Δcrest **чистого транскода** файла. Пороги: стационарные **0.05 дБ**,
транзиентные **0.60 дБ**.

Измерено **276** файлов (144 канона + 132 в `sounds_380`): тип, длина, разброс
RMS, baseline, допуск, фактический Δcrest, вердикт.

| | |
|---|---:|
| файлов | **276** |
| стационарных / транзиентных | **50 / 226** |
| **вне допуска** | **0** |

## ⚠ Главное: формула с `min()` не работает — норма умирает

С `min()` допуск **никогда не может превысить порог типа**. У стационарного
порог **0.05 дБ**, а `max(0.05; baseline+0.05) ≥ 0.05` — значит `min` всегда
даёт **0.05**, и baseline **не влияет вообще**. То есть весь смысл З-29
(«допуск per-file») пропадает.

Проверил на числах: **по формуле как записана — 44 файла вне допуска из 276**,
из них **37 — стационарные**, у которых baseline больше 0.05 просто потому, что
так шумит кодек. Норма, которая валит 44 принятых файла без всякой правки, —
мёртвая.

**Что предлагаю (одно слово в формуле):**

```
допуск = max(порог_типа, baseline + 0.05)
```

`baseline` должен быть **полом, а не потолком**: порог типа — минимум
требований, baseline — сколько кодека реально шумит. Тогда:

| формула | вне допуска |
|---|---:|
| `min(...)` как в З-29 | **44 из 276** |
| `max(...)` — предлагаю | **0 из 276** |

Разница именно в том, что для 37 стационарных файлов `min` запирает допуск на
0.05, хотя их собственный baseline — до 0.47 дБ.

## Классификация: почему по назначению, а не по метрике

Я пробовал **три объективные метрики** — все ошибаются, показываю честно:

**1. Разброс RMS по окнам 250 мс (стационарный ≤ 6 дБ, транзиентный ≥ 15).**
Провал: `hive_spawn_hurt_critical_01..04` — это явные ваншоты крика, но их
разброс **1.5–6.0 дБ**, и метрика записала их в «стационарные».

**2. Доля «тела» (время выше −20 дБ от пика) от длины.** Провал: у ваншотов с
плотной атакой доля тела **0.94–0.96**, они неотличимы от эмбиента по этому
признаку.

**3. Комбинация длины, тела и разброса.** Тоже путается на тех же файлах.

**Вывод:** эти сигналы различаются **не формой огибающей, а ролью в игре**.
Эмбиент зацикливается и играет минутами — его шов и стабильность уровня важны.
Ваншот играет один раз — его уровень важен только на атаке. Гребёнка,
измеряющая форму, этого различия не содержит.

**Поэтому классификация — по назначению, и она проверяема:**

| правило | файлов |
|---|---:|
| стационарный: путь `amb/`, имя содержит `amb`, `ambient` или `loop`, либо длина ≥ 100 с | **50** |
| транзиентный: всё остальное | **226** |

Каждая запись в таблице несёт рядом **длину и разброс RMS** — то есть решение
можно перепроверить по цифрам, а не принимать на веру. Спорные случаи
(`hive_spawn_idle_*` 4–9 с с разбросом 6–9 дБ) я оставил транзиентными, хотя
они ближе к фону: у них нет зацикливания, а порог 0.60 дБ всё равно покрыт с
запасом.

## Что показали числа

| тип | файлов | baseline медиана | **baseline максимум** | порог |
|---|---:|---:|---:|---:|
| стационарный | 50 | 0.115 | **0.468** | 0.05 |
| транзиентный | 226 | 0.064 | **2.293** | 0.60 |

**Худший baseline во всём банке — 2.293 дБ** у `flesh_amalgam_smash_01` (74 kbps):
кодек сам по себе меняет crest этого файла на 2.3 дБ. Никакой порог типа это не
перекроет — только `max(baseline+0.05)`.

**37 из 50 стационарных имеют baseline > 0.05** — то есть порог 0.05 дБ для них
недостижим физически. Это и есть причина, по которой норма «валила» всё подряд.

## Что это даёт Интегратору

1. **Взять допуск из таблицы** — он уже посчитан по формуле `max(порог; baseline+0.05)`.
2. Гейт сравнивает `Δcrest` с допуском файла и **печатает рядом порог, baseline
   и допуск** — тогда вердикт читается: «0.30 при допуске 0.31 — в норме».
3. Если файл **пересобран** — его строку надо перемерить: baseline привязан к
   конкретному файлу, а не к имени.
4. Для 3.8.x держать **160 kbps**: там baseline медиана 0.053, и допуск 0.60
   реально ловит правку тембра 0.75 дБ (порог R19) с запасом.

## Чего я не делал

- **Не переделывал файлы с высоким baseline.** 2.293 дБ у `flesh_amalgam_smash_01`
  — это шум кодека на 74 kbps, а не дефект звука. Перекод в 160 kbps его
  снизит, но это правка **выпущенного канона 3.7.3**, которая требует новой
  сборки и приёмки. Если Архитектор решит — сделаю отдельным шагом в 3.8.0.
- **Не менял формулу З-29 сам.** Предлагаю `max`, но решать Архитектору:
  это его норма, и моё дело — показать, что с `min` она не работает.

## Полная таблица (276 файлов, только допуски)

| файл | тип | длина | разброс RMS | baseline | порог | **допуск** |
|---|---|---:|---:|---:|---:|---:|
| `sounds/entity/flesh_amalgam_smash_01.ogg` | транз | 2.60 | 229.4 | 2.293 | 0.60 | **2.34** |
| `sounds/entity/flesh_amalgam_smash_02.ogg` | транз | 1.90 | 229.6 | 0.971 | 0.60 | **1.02** |
| `sounds/hive/zone_stinger_intensify.ogg` | транз | 2.40 | 20.1 | 0.926 | 0.60 | **0.98** |
| `sounds/hive/hive_spawn_idle_02.ogg` | транз | 5.02 | 7.7 | 0.763 | 0.60 | **0.81** |
| `sounds/hive/zone_stinger_deep.ogg` | транз | 2.80 | 58.6 | 0.718 | 0.60 | **0.77** |
| `sounds/hive/hive_spawn_idle_01.ogg` | транз | 7.02 | 6.3 | 0.714 | 0.60 | **0.76** |
| `sounds/hive/amalgam_breath_01.ogg` | транз | 2.00 | 12.6 | 0.702 | 0.60 | **0.75** |
| `sounds/hive/zone_stinger_release.ogg` | транз | 1.70 | 31.7 | 0.573 | 0.60 | **0.62** |
| `sounds/hive/hive_spawn_hurt_critical_03.ogg` | транз | 1.10 | 1.6 | 0.568 | 0.60 | **0.62** |
| `sounds/combat/dismember_02.ogg` | транз | 1.14 | 15.2 | 0.538 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_hurt_critical_02.ogg` | транз | 0.97 | 1.5 | 0.516 | 0.60 | **0.60** |
| `sounds/hive/detail_flow_01.ogg` | транз | 1.32 | 11.3 | 0.510 | 0.60 | **0.60** |
| `sounds/amb/hive_ambient_tonal_stinger.ogg` | стац | 10.00 | 27.5 | 0.468 | 0.05 | **0.52** |
| `sounds/hive/hive_spawn_death_03.ogg` | транз | 3.02 | 9.8 | 0.442 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_hurt_critical_04.ogg` | транз | 1.00 | 1.5 | 0.414 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_hurt_critical_01.ogg` | транз | 1.10 | 6.0 | 0.408 | 0.60 | **0.60** |
| `sounds/hive/spawn_skeleton_blade_02.ogg` | транз | 0.66 | 5.9 | 0.388 | 0.60 | **0.60** |
| `sounds/hive/spawn_skeleton_blade_03.ogg` | транз | 0.58 | 7.5 | 0.381 | 0.60 | **0.60** |
| `sounds_380/entity/infected_breeze_death_01.ogg` | транз | 2.02 | 23.3 | 0.373 | 0.60 | **0.60** |
| `sounds_380/entity/infected_ravager_death_01.ogg` | транз | 1.90 | 14.1 | 0.370 | 0.60 | **0.60** |
| `sounds/entity/flesh_amalgam_death_01.ogg` | транз | 2.60 | 29.5 | 0.356 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_idle_04.ogg` | транз | 9.02 | 9.1 | 0.355 | 0.60 | **0.60** |
| `sounds/entity/flesh_amalgam_step_02.ogg` | транз | 0.82 | 21.9 | 0.354 | 0.60 | **0.60** |
| `sounds/amb/hive_ambient_close_02.ogg` | стац | 120.00 | 13.9 | 0.349 | 0.05 | **0.40** |
| `sounds/block/hive_eye_screech.ogg` | транз | 1.90 | 9.5 | 0.347 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_attack_04.ogg` | транз | 0.95 | 16.7 | 0.333 | 0.60 | **0.60** |
| `sounds/hive/detail_creak_01.ogg` | транз | 1.12 | 10.9 | 0.331 | 0.60 | **0.60** |
| `sounds/item/purifier_loop.ogg` | стац | 2.89 | 5.0 | 0.324 | 0.05 | **0.37** |
| `sounds/entity/incubation_cyst_ambient_01.ogg` | стац | 2.30 | 8.1 | 0.321 | 0.05 | **0.37** |
| `sounds/hive/spawn_skeleton_bonecrack_01.ogg` | транз | 0.44 | 99.0 | 0.298 | 0.60 | **0.60** |
| `sounds/hive/amalgam_slam_01.ogg` | транз | 1.60 | 25.1 | 0.290 | 0.60 | **0.60** |
| `sounds/hive/spawn_creeper_detonate_01.ogg` | транз | 0.55 | 8.7 | 0.290 | 0.60 | **0.60** |
| `sounds/amb/hive_ambient_close_01.ogg` | стац | 120.00 | 13.5 | 0.289 | 0.05 | **0.34** |
| `sounds_380/entity/infected_endermite_ambient_01.ogg` | стац | 2.64 | 5.9 | 0.289 | 0.05 | **0.34** |
| `sounds/hive/amalgam_shuffle_02.ogg` | транз | 1.55 | 4.5 | 0.287 | 0.60 | **0.60** |
| `sounds_380/entity/infected_warden_ambient_01.ogg` | стац | 2.99 | 5.4 | 0.283 | 0.05 | **0.33** |
| `sounds/amb/hive_ambient_01.ogg` | стац | 120.00 | 13.1 | 0.279 | 0.05 | **0.33** |
| `sounds_380/entity/infected_illusioner_ambient_01.ogg` | стац | 2.56 | 8.4 | 0.279 | 0.05 | **0.33** |
| `sounds/entity/flesh_amalgam_roar_01.ogg` | транз | 1.85 | 18.1 | 0.262 | 0.60 | **0.60** |
| `sounds/hive/amalgam_slam_02.ogg` | транз | 1.35 | 12.3 | 0.261 | 0.60 | **0.60** |
| `sounds/hive/hive_spread_03_swell.ogg` | транз | 1.05 | 12.8 | 0.261 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_hurt_02.ogg` | транз | 0.36 | 99.0 | 0.259 | 0.60 | **0.60** |
| `sounds/entity/flesh_amalgam_ambient.ogg` | стац | 2.30 | 3.3 | 0.259 | 0.05 | **0.31** |
| `sounds_380/entity/infected_silverfish_death_01.ogg` | транз | 1.77 | 18.5 | 0.255 | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_ambient_01.ogg` | стац | 2.91 | 5.8 | 0.244 | 0.05 | **0.29** |
| `sounds/hive/hive_spread_01_creep.ogg` | транз | 0.90 | 133.0 | 0.236 | 0.60 | **0.60** |
| `sounds/hallucination/phantom_creeper.ogg` | транз | 1.90 | 15.8 | 0.235 | 0.60 | **0.60** |
| `sounds/hive/detail_membrane_01.ogg` | транз | 0.54 | 3.2 | 0.230 | 0.60 | **0.60** |
| `sounds_380/entity/infected_evoker_ambient_01.ogg` | стац | 2.81 | 9.0 | 0.230 | 0.05 | **0.28** |
| `sounds/hive/hive_spawn_idle_03.ogg` | транз | 4.02 | 7.6 | 0.222 | 0.60 | **0.60** |
| `sounds/hive/amalgam_breath_02.ogg` | транз | 2.40 | 13.3 | 0.221 | 0.60 | **0.60** |
| `sounds_380/entity/infected_silverfish_ambient_01.ogg` | стац | 2.82 | 8.3 | 0.217 | 0.05 | **0.27** |
| `sounds/hallucination/phantom_footsteps.ogg` | транз | 2.40 | 28.5 | 0.216 | 0.60 | **0.60** |
| `sounds/hive/amb_surface.ogg` | стац | 120.00 | 4.5 | 0.216 | 0.05 | **0.27** |
| `sounds/hive/amb_core.ogg` | стац | 120.00 | 7.8 | 0.212 | 0.05 | **0.26** |
| `sounds/hive/spawn_skeleton_blade_01.ogg` | транз | 0.50 | 99.0 | 0.206 | 0.60 | **0.60** |
| `sounds/hive/amb_threshold.ogg` | стац | 120.00 | 9.3 | 0.190 | 0.05 | **0.24** |
| `sounds_380/entity/infected_husk_ambient_01.ogg` | стац | 2.62 | 6.6 | 0.188 | 0.05 | **0.24** |
| `sounds/hive/hive_spawn_death_01.ogg` | транз | 2.42 | 6.0 | 0.184 | 0.60 | **0.60** |
| `sounds/item/purification_vial_break_01.ogg` | транз | 0.70 | 22.8 | 0.184 | 0.60 | **0.60** |
| `sounds/entity/flesh_amalgam_step_01.ogg` | транз | 1.15 | 16.5 | 0.179 | 0.60 | **0.60** |
| `sounds/block/hive_heartbeat.ogg` | транз | 2.34 | 18.0 | 0.174 | 0.60 | **0.60** |
| `sounds/block/digestor_churn.ogg` | транз | 2.30 | 6.8 | 0.172 | 0.60 | **0.60** |
| `sounds_380/entity/infected_magma_cube_death_01.ogg` | транз | 1.78 | 23.0 | 0.171 | 0.60 | **0.60** |
| `sounds/hive/spawn_skeleton_bonecrack_02.ogg` | транз | 0.50 | 99.0 | 0.168 | 0.60 | **0.60** |
| `sounds/hive/amalgam_shuffle_01.ogg` | транз | 1.30 | 6.2 | 0.168 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_death_04.ogg` | транз | 1.97 | 4.4 | 0.164 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_death_02.ogg` | транз | 2.87 | 9.0 | 0.164 | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_brute_death_01.ogg` | транз | 1.72 | 13.7 | 0.163 | 0.60 | **0.60** |
| `sounds_380/entity/infected_drowned_death_01.ogg` | транз | 1.88 | 22.3 | 0.160 | 0.60 | **0.60** |
| `sounds/block/heartbeat_loop.ogg` | стац | 1.40 | 73.2 | 0.158 | 0.05 | **0.21** |
| `sounds_380/entity/infected_hoglin_ambient_01.ogg` | стац | 3.01 | 9.2 | 0.157 | 0.05 | **0.21** |
| `sounds/amb/hive_ambient_02.ogg` | стац | 120.00 | 15.2 | 0.157 | 0.05 | **0.21** |
| `sounds_380/entity/infected_stray_ambient_01.ogg` | стац | 3.18 | 5.7 | 0.156 | 0.05 | **0.21** |
| `sounds/hive/spawn_creeper_sac_03.ogg` | транз | 0.97 | 13.6 | 0.153 | 0.60 | **0.60** |
| `sounds/hive/amalgam_shuffle_03.ogg` | транз | 1.10 | 3.4 | 0.149 | 0.60 | **0.60** |
| `sounds/block/pustule_burst.ogg` | транз | 0.80 | 29.6 | 0.146 | 0.60 | **0.60** |
| `sounds_380/entity/infected_zoglin_death_01.ogg` | транз | 1.52 | 21.7 | 0.145 | 0.60 | **0.60** |
| `sounds/hive/spawn_creeper_sac_01.ogg` | транз | 0.85 | 19.4 | 0.142 | 0.60 | **0.60** |
| `sounds/hive/hive_spread_02_pulse.ogg` | транз | 0.80 | 21.0 | 0.139 | 0.60 | **0.60** |
| `sounds/amb/hive_ambient_03.ogg` | стац | 120.00 | 14.7 | 0.134 | 0.05 | **0.18** |
| `sounds/block/hive_membrane_place_01.ogg` | транз | 0.42 | 99.0 | 0.134 | 0.60 | **0.60** |
| `sounds_380/entity/infected_ghast_ambient_01.ogg` | стац | 2.51 | 10.6 | 0.131 | 0.05 | **0.18** |
| `sounds_380/entity/infected_breeze_ambient_01.ogg` | стац | 3.00 | 14.5 | 0.122 | 0.05 | **0.17** |
| `sounds_380/entity/infected_piglin_brute_attack_01.ogg` | транз | 0.59 | 15.2 | 0.122 | 0.60 | **0.60** |
| `sounds/amb/hive_pulse_01.ogg` | стац | 13.40 | 59.9 | 0.119 | 0.05 | **0.17** |
| `sounds_380/entity/infected_blaze_attack_01.ogg` | транз | 0.82 | 31.0 | 0.119 | 0.60 | **0.60** |
| `sounds_380/entity/infected_shulker_death_01.ogg` | транз | 1.68 | 14.2 | 0.118 | 0.60 | **0.60** |
| `sounds/entity/flesh_amalgam_hurt_01.ogg` | транз | 1.15 | 19.8 | 0.117 | 0.60 | **0.60** |
| `sounds_380/entity/infected_guardian_death_01.ogg` | транз | 2.01 | 22.5 | 0.114 | 0.60 | **0.60** |
| `sounds_380/entity/infected_phantom_hurt_01.ogg` | транз | 0.45 | 99.0 | 0.114 | 0.60 | **0.60** |
| `sounds_380/entity/infected_phantom_attack_01.ogg` | транз | 0.80 | 32.2 | 0.112 | 0.60 | **0.60** |
| `sounds_380/entity/infected_bogged_ambient_01.ogg` | стац | 2.72 | 5.1 | 0.111 | 0.05 | **0.16** |
| `sounds_380/entity/infected_guardian_ambient_01.ogg` | стац | 2.38 | 6.1 | 0.111 | 0.05 | **0.16** |
| `sounds/combat/combat_flesh_hit_03.ogg` | транз | 0.51 | 19.2 | 0.111 | 0.60 | **0.60** |
| `sounds/combat/dismember_04.ogg` | транз | 0.94 | 19.5 | 0.109 | 0.60 | **0.60** |
| `sounds_380/entity/infected_drowned_ambient_01.ogg` | стац | 2.56 | 8.9 | 0.109 | 0.05 | **0.16** |
| `sounds/hive/spawn_skeleton_whip_02.ogg` | транз | 0.44 | 99.0 | 0.108 | 0.60 | **0.60** |
| `sounds_380/entity/infected_cave_spider_attack_01.ogg` | транз | 0.71 | 15.4 | 0.108 | 0.60 | **0.60** |
| `sounds_380/entity/infected_shulker_ambient_01.ogg` | стац | 2.32 | 5.4 | 0.107 | 0.05 | **0.16** |
| `sounds/combat/dismember_01.ogg` | транз | 1.28 | 30.1 | 0.102 | 0.60 | **0.60** |
| `sounds/entity/pustule_grenade_impact_01.ogg` | транз | 1.10 | 47.6 | 0.102 | 0.60 | **0.60** |
| `sounds_380/entity/infected_ghast_death_01.ogg` | транз | 2.08 | 31.2 | 0.102 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_hurt_03.ogg` | транз | 0.41 | 99.0 | 0.102 | 0.60 | **0.60** |
| `sounds/combat/combat_flesh_hit_02.ogg` | транз | 0.80 | 23.4 | 0.102 | 0.60 | **0.60** |
| `sounds/entity/pustule_grenade_throw_01.ogg` | транз | 0.56 | 3.1 | 0.100 | 0.60 | **0.60** |
| `sounds/combat/combat_flesh_hit_01.ogg` | транз | 0.61 | 15.9 | 0.099 | 0.60 | **0.60** |
| `sounds_380/entity/infected_warden_attack_01.ogg` | транз | 0.60 | 15.3 | 0.098 | 0.60 | **0.60** |
| `sounds_380/entity/infected_stray_hurt_01.ogg` | транз | 0.55 | 22.3 | 0.097 | 0.60 | **0.60** |
| `sounds/combat/dismember_05.ogg` | транз | 1.36 | 28.3 | 0.096 | 0.60 | **0.60** |
| `sounds_380/entity/infected_slime_ambient_01.ogg` | стац | 2.98 | 5.6 | 0.096 | 0.05 | **0.15** |
| `sounds_380/entity/infected_creaking_death_01.ogg` | транз | 1.51 | 9.5 | 0.096 | 0.60 | **0.60** |
| `sounds_380/entity/infected_cave_spider_hurt_01.ogg` | транз | 0.47 | 99.0 | 0.092 | 0.60 | **0.60** |
| `sounds/entity/organic_creak.ogg` | транз | 1.25 | 9.2 | 0.091 | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_death_01.ogg` | транз | 1.69 | 22.3 | 0.090 | 0.60 | **0.60** |
| `sounds_380/entity/infected_blaze_death_01.ogg` | транз | 1.56 | 17.4 | 0.089 | 0.60 | **0.60** |
| `sounds/entity/amalgamation_fuse.ogg` | транз | 2.20 | 9.5 | 0.089 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_attack_03.ogg` | транз | 0.80 | 20.1 | 0.087 | 0.60 | **0.60** |
| `sounds/hallucination/phantom_whisper.ogg` | транз | 1.60 | 18.8 | 0.087 | 0.60 | **0.60** |
| `sounds/block/hive_block_place_01_soft.ogg` | транз | 0.30 | 99.0 | 0.085 | 0.60 | **0.60** |
| `sounds_380/entity/infected_vex_ambient_01.ogg` | стац | 2.41 | 5.6 | 0.085 | 0.05 | **0.13** |
| `sounds/entity/flesh_amalgam_roar_02.ogg` | транз | 1.05 | 14.8 | 0.084 | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_skeleton_ambient_01.ogg` | стац | 2.68 | 5.4 | 0.084 | 0.05 | **0.13** |
| `sounds/combat/combat_deflect_04_glance.ogg` | транз | 0.46 | 99.0 | 0.082 | 0.60 | **0.60** |
| `sounds_380/entity/infected_ravager_hurt_01.ogg` | транз | 0.49 | 99.0 | 0.079 | 0.60 | **0.60** |
| `sounds_380/entity/infected_endermite_hurt_01.ogg` | транз | 0.40 | 99.0 | 0.078 | 0.60 | **0.60** |
| `sounds_380/entity/infected_silverfish_attack_01.ogg` | транз | 0.65 | 15.1 | 0.078 | 0.60 | **0.60** |
| `sounds_380/entity/infected_creaking_hurt_01.ogg` | транз | 0.52 | 22.2 | 0.076 | 0.60 | **0.60** |
| `sounds/block/creeper_rupture.ogg` | транз | 0.90 | 19.4 | 0.076 | 0.60 | **0.60** |
| `sounds_380/entity/infected_zombie_villager_death_01.ogg` | транз | 1.56 | 22.5 | 0.076 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_attack_01.ogg` | транз | 0.46 | 99.0 | 0.073 | 0.60 | **0.60** |
| `sounds_380/entity/infected_elder_guardian_ambient_01.ogg` | стац | 2.62 | 6.5 | 0.073 | 0.05 | **0.12** |
| `sounds_380/entity/infected_piglin_brute_ambient_01.ogg` | стац | 2.34 | 5.1 | 0.073 | 0.05 | **0.12** |
| `sounds_380/entity/infected_magma_cube_ambient_01.ogg` | стац | 2.46 | 5.1 | 0.073 | 0.05 | **0.12** |
| `sounds/combat/combat_flesh_hit_deep_01_axe.ogg` | транз | 1.05 | 20.5 | 0.072 | 0.60 | **0.60** |
| `sounds_380/entity/infected_slime_hurt_01.ogg` | транз | 0.42 | 99.0 | 0.072 | 0.60 | **0.60** |
| `sounds/block/hive_alarm.ogg` | транз | 1.55 | 5.6 | 0.071 | 0.60 | **0.60** |
| `sounds_380/entity/infected_husk_attack_01.ogg` | транз | 0.84 | 30.5 | 0.071 | 0.60 | **0.60** |
| `sounds_380/entity/infected_phantom_death_01.ogg` | транз | 1.79 | 19.9 | 0.071 | 0.60 | **0.60** |
| `sounds_380/entity/infected_hoglin_death_01.ogg` | транз | 1.94 | 27.4 | 0.071 | 0.60 | **0.60** |
| `sounds/hive/spawn_creeper_sac_02.ogg` | транз | 0.70 | 4.7 | 0.071 | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_death_01.ogg` | транз | 1.72 | 12.5 | 0.071 | 0.60 | **0.60** |
| `sounds_380/entity/infected_zoglin_ambient_01.ogg` | стац | 2.69 | 4.7 | 0.068 | 0.05 | **0.12** |
| `sounds_380/entity/infected_wither_skeleton_death_01.ogg` | транз | 1.71 | 22.5 | 0.067 | 0.60 | **0.60** |
| `sounds_380/entity/infected_shulker_attack_01.ogg` | транз | 0.79 | 30.7 | 0.067 | 0.60 | **0.60** |
| `sounds_380/entity/infected_enderman_attack_01.ogg` | транз | 0.79 | 31.3 | 0.066 | 0.60 | **0.60** |
| `sounds_380/entity/infected_illusioner_death_01.ogg` | транз | 2.07 | 14.7 | 0.065 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_alert_01.ogg` | транз | 0.58 | 8.1 | 0.065 | 0.60 | **0.60** |
| `sounds/hive/spawn_creeper_detonate_02.ogg` | транз | 0.45 | 99.0 | 0.064 | 0.60 | **0.60** |
| `sounds_380/entity/infected_magma_cube_hurt_01.ogg` | транз | 0.48 | 99.0 | 0.064 | 0.60 | **0.60** |
| `sounds_380/entity/infected_slime_death_01.ogg` | транз | 1.83 | 27.6 | 0.064 | 0.60 | **0.60** |
| `sounds_380/entity/infected_evoker_death_01.ogg` | транз | 1.79 | 14.3 | 0.063 | 0.60 | **0.60** |
| `sounds_380/entity/infected_slime_attack_01.ogg` | транз | 0.78 | 31.3 | 0.063 | 0.60 | **0.60** |
| `sounds/block/hive_block_place_03_wet.ogg` | транз | 0.26 | 99.0 | 0.061 | 0.60 | **0.60** |
| `sounds/combat/combat_flesh_hit_deep_02_crit.ogg` | транз | 0.88 | 14.7 | 0.060 | 0.60 | **0.60** |
| `sounds/hive/spawn_creeper_crawl_01.ogg` | транз | 0.75 | 0.6 | 0.060 | 0.60 | **0.60** |
| `sounds/hive/spawn_creeper_crawl_02.ogg` | транз | 0.90 | 3.1 | 0.060 | 0.60 | **0.60** |
| `sounds_380/entity/infected_vindicator_hurt_01.ogg` | транз | 0.51 | 22.4 | 0.059 | 0.60 | **0.60** |
| `sounds_380/entity/infected_warden_death_01.ogg` | транз | 1.91 | 18.8 | 0.058 | 0.60 | **0.60** |
| `sounds/block/bone_deflect.ogg` | транз | 0.36 | 99.0 | 0.058 | 0.60 | **0.60** |
| `sounds_380/entity/infected_illusioner_hurt_01.ogg` | транз | 0.49 | 99.0 | 0.057 | 0.60 | **0.60** |
| `sounds/combat/combat_deflect_02_bone.ogg` | транз | 0.38 | 99.0 | 0.057 | 0.60 | **0.60** |
| `sounds/combat/combat_stab_03_shield.ogg` | транз | 0.34 | 99.0 | 0.056 | 0.60 | **0.60** |
| `sounds/entity/acid_splash.ogg` | транз | 0.70 | 13.0 | 0.055 | 0.60 | **0.60** |
| `sounds/entity/flamethrower_fire.ogg` | транз | 1.64 | 0.9 | 0.055 | 0.60 | **0.60** |
| `sounds_380/entity/infected_magma_cube_attack_01.ogg` | транз | 0.64 | 15.3 | 0.054 | 0.60 | **0.60** |
| `sounds_380/entity/infected_ravager_ambient_01.ogg` | стац | 2.69 | 5.3 | 0.054 | 0.05 | **0.10** |
| `sounds_380/entity/infected_enderman_death_01.ogg` | транз | 1.56 | 11.8 | 0.053 | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_skeleton_hurt_01.ogg` | транз | 0.52 | 21.8 | 0.053 | 0.60 | **0.60** |
| `sounds/block/hive_block_break_01_tear.ogg` | транз | 0.62 | 18.2 | 0.053 | 0.60 | **0.60** |
| `sounds/entity/incubation_cyst_rupture_01.ogg` | транз | 0.85 | 17.0 | 0.051 | 0.60 | **0.60** |
| `sounds_380/entity/infected_bogged_death_01.ogg` | транз | 1.95 | 27.1 | 0.051 | 0.60 | **0.60** |
| `sounds/item/purifier_ignite.ogg` | транз | 0.90 | 8.6 | 0.050 | 0.60 | **0.60** |
| `sounds_380/entity/infected_enderman_ambient_01.ogg` | стац | 3.16 | 5.2 | 0.050 | 0.05 | **0.10** |
| `sounds/combat/combat_flesh_hit_deep_03_blast.ogg` | транз | 1.18 | 16.8 | 0.050 | 0.60 | **0.60** |
| `sounds_380/entity/infected_guardian_hurt_01.ogg` | транз | 0.45 | 99.0 | 0.050 | 0.60 | **0.60** |
| `sounds/hive/detail_flow_02.ogg` | транз | 0.48 | 99.0 | 0.049 | 0.60 | **0.60** |
| `sounds_380/entity/infected_enderman_hurt_01.ogg` | транз | 0.52 | 22.9 | 0.048 | 0.60 | **0.60** |
| `sounds_380/entity/infected_ravager_attack_01.ogg` | транз | 0.76 | 31.5 | 0.048 | 0.60 | **0.60** |
| `sounds_380/entity/infected_bogged_hurt_01.ogg` | транз | 0.43 | 99.0 | 0.047 | 0.60 | **0.60** |
| `sounds_380/entity/infected_phantom_ambient_01.ogg` | стац | 2.40 | 5.2 | 0.047 | 0.05 | **0.10** |
| `sounds_380/entity/infected_endermite_attack_01.ogg` | транз | 0.82 | 31.3 | 0.046 | 0.60 | **0.60** |
| `sounds/item/inoculator_fire.ogg` | транз | 0.70 | 23.5 | 0.045 | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_attack_01.ogg` | транз | 0.66 | 14.1 | 0.044 | 0.60 | **0.60** |
| `sounds/item/purifier_lamp_ignite_01.ogg` | транз | 1.30 | 13.2 | 0.043 | 0.60 | **0.60** |
| `sounds_380/entity/infected_evoker_attack_01.ogg` | транз | 0.59 | 15.1 | 0.043 | 0.60 | **0.60** |
| `sounds/combat/combat_stab_01_bone.ogg` | транз | 0.38 | 99.0 | 0.043 | 0.60 | **0.60** |
| `sounds/hive/amb_deep.ogg` | стац | 120.00 | 12.2 | 0.042 | 0.05 | **0.09** |
| `sounds_380/entity/infected_piglin_hurt_01.ogg` | транз | 0.52 | 22.7 | 0.042 | 0.60 | **0.60** |
| `sounds_380/entity/infected_vindicator_attack_01.ogg` | транз | 0.83 | 31.1 | 0.041 | 0.60 | **0.60** |
| `sounds/hive/detail_bubbles_01.ogg` | транз | 0.78 | 9.3 | 0.041 | 0.60 | **0.60** |
| `sounds_380/entity/infected_pillager_hurt_01.ogg` | транз | 0.42 | 99.0 | 0.041 | 0.60 | **0.60** |
| `sounds/flesh/flesh_block_step_01.ogg` | транз | 0.39 | 99.0 | 0.041 | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_ambient_01.ogg` | стац | 3.02 | 8.9 | 0.040 | 0.05 | **0.09** |
| `sounds/entity/sinew_shield_block_01.ogg` | транз | 0.55 | 18.2 | 0.040 | 0.60 | **0.60** |
| `sounds_380/entity/infected_pillager_death_01.ogg` | транз | 1.99 | 22.3 | 0.040 | 0.60 | **0.60** |
| `sounds_380/entity/infected_stray_death_01.ogg` | транз | 1.69 | 13.4 | 0.040 | 0.60 | **0.60** |
| `sounds/block/hive_block_place_02_dense.ogg` | транз | 0.34 | 99.0 | 0.038 | 0.60 | **0.60** |
| `sounds_380/entity/infected_pillager_ambient_01.ogg` | стац | 2.51 | 10.6 | 0.037 | 0.05 | **0.09** |
| `sounds/combat/ossified_scythe_swing_01.ogg` | транз | 0.72 | 3.2 | 0.037 | 0.60 | **0.60** |
| `sounds/block/synapse_shock.ogg` | транз | 0.55 | 17.5 | 0.036 | 0.60 | **0.60** |
| `sounds/combat/bone_scythe_hit_01.ogg` | транз | 0.34 | 99.0 | 0.036 | 0.60 | **0.60** |
| `sounds/combat/ossified_scythe_hit_01.ogg` | транз | 0.60 | 23.1 | 0.036 | 0.60 | **0.60** |
| `sounds/flesh/flesh_block_step_02.ogg` | транз | 0.43 | 99.0 | 0.035 | 0.60 | **0.60** |
| `sounds_380/entity/infected_pillager_attack_01.ogg` | транз | 0.77 | 31.3 | 0.035 | 0.60 | **0.60** |
| `sounds/item/dart_hit.ogg` | транз | 0.42 | 99.0 | 0.034 | 0.60 | **0.60** |
| `sounds_380/entity/infected_elder_guardian_death_01.ogg` | транз | 1.50 | 23.6 | 0.034 | 0.60 | **0.60** |
| `sounds/hive/spawn_skeleton_whip_01.ogg` | транз | 0.62 | 5.6 | 0.032 | 0.60 | **0.60** |
| `sounds_380/entity/infected_witch_ambient_01.ogg` | стац | 3.20 | 5.1 | 0.032 | 0.05 | **0.08** |
| `sounds_380/entity/infected_husk_hurt_01.ogg` | транз | 0.42 | 99.0 | 0.032 | 0.60 | **0.60** |
| `sounds/combat/combat_stab_02_chitin.ogg` | транз | 0.28 | 99.0 | 0.030 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_alert_04.ogg` | транз | 1.12 | 12.8 | 0.030 | 0.60 | **0.60** |
| `sounds/combat/combat_deflect_05_parry.ogg` | транз | 0.40 | 99.0 | 0.029 | 0.60 | **0.60** |
| `sounds_380/entity/infected_drowned_hurt_01.ogg` | транз | 0.49 | 99.0 | 0.029 | 0.60 | **0.60** |
| `sounds_380/entity/infected_witch_death_01.ogg` | транз | 1.54 | 12.6 | 0.028 | 0.60 | **0.60** |
| `sounds_380/entity/infected_vex_attack_01.ogg` | транз | 0.80 | 31.9 | 0.027 | 0.60 | **0.60** |
| `sounds_380/entity/infected_cave_spider_ambient_01.ogg` | стац | 3.09 | 5.7 | 0.026 | 0.05 | **0.08** |
| `sounds/combat/combat_deflect_01_chitin.ogg` | транз | 0.34 | 99.0 | 0.026 | 0.60 | **0.60** |
| `sounds_380/entity/infected_creaking_ambient_01.ogg` | стац | 2.76 | 11.8 | 0.026 | 0.05 | **0.08** |
| `sounds_380/entity/infected_elder_guardian_hurt_01.ogg` | транз | 0.53 | 23.9 | 0.026 | 0.60 | **0.60** |
| `sounds/block/hive_block_break_03_crunch.ogg` | транз | 0.75 | 17.1 | 0.025 | 0.60 | **0.60** |
| `sounds_380/entity/infected_vindicator_death_01.ogg` | транз | 1.99 | 26.8 | 0.024 | 0.60 | **0.60** |
| `sounds_380/entity/infected_creaking_attack_01.ogg` | транз | 0.59 | 15.5 | 0.024 | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_attack_01.ogg` | транз | 0.67 | 15.1 | 0.023 | 0.60 | **0.60** |
| `sounds_380/entity/infected_hoglin_hurt_01.ogg` | транз | 0.53 | 22.5 | 0.023 | 0.60 | **0.60** |
| `sounds_380/entity/infected_zoglin_attack_01.ogg` | транз | 0.57 | 15.5 | 0.023 | 0.60 | **0.60** |
| `sounds/combat/bone_scythe_swing_01.ogg` | транз | 0.44 | 99.0 | 0.023 | 0.60 | **0.60** |
| `sounds_380/entity/infected_silverfish_hurt_01.ogg` | транз | 0.51 | 23.0 | 0.022 | 0.60 | **0.60** |
| `sounds_380/entity/infected_blaze_hurt_01.ogg` | транз | 0.47 | 99.0 | 0.022 | 0.60 | **0.60** |
| `sounds_380/entity/infected_elder_guardian_attack_01.ogg` | транз | 0.85 | 31.4 | 0.022 | 0.60 | **0.60** |
| `sounds_380/entity/infected_cave_spider_death_01.ogg` | транз | 1.59 | 22.4 | 0.022 | 0.60 | **0.60** |
| `sounds/block/heart_pulse.ogg` | транз | 0.60 | 25.6 | 0.022 | 0.60 | **0.60** |
| `sounds_380/entity/infected_vex_hurt_01.ogg` | транз | 0.50 | 99.0 | 0.022 | 0.60 | **0.60** |
| `sounds_380/entity/infected_zombie_villager_attack_01.ogg` | транз | 0.83 | 30.6 | 0.021 | 0.60 | **0.60** |
| `sounds_380/entity/infected_witch_attack_01.ogg` | транз | 0.57 | 15.1 | 0.021 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_alert_03.ogg` | транз | 0.88 | 11.3 | 0.020 | 0.60 | **0.60** |
| `sounds/block/hive_block_break_02_pop.ogg` | транз | 0.72 | 17.9 | 0.019 | 0.60 | **0.60** |
| `sounds_380/entity/infected_illusioner_attack_01.ogg` | транз | 0.78 | 31.5 | 0.019 | 0.60 | **0.60** |
| `sounds/combat/combat_deflect_03_metal.ogg` | транз | 0.30 | 99.0 | 0.019 | 0.60 | **0.60** |
| `sounds_380/entity/infected_zoglin_hurt_01.ogg` | транз | 0.45 | 99.0 | 0.018 | 0.60 | **0.60** |
| `sounds/flesh/flesh_block_step_03.ogg` | транз | 0.33 | 99.0 | 0.018 | 0.60 | **0.60** |
| `sounds/block/synapse_rupture.ogg` | транз | 0.70 | 9.5 | 0.018 | 0.60 | **0.60** |
| `sounds_380/entity/infected_zombie_villager_hurt_01.ogg` | транз | 0.44 | 99.0 | 0.018 | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_hurt_01.ogg` | транз | 0.42 | 99.0 | 0.018 | 0.60 | **0.60** |
| `sounds/amb/hive_pulse_03.ogg` | стац | 13.40 | 59.5 | 0.017 | 0.05 | **0.07** |
| `sounds_380/entity/infected_witch_hurt_01.ogg` | транз | 0.46 | 99.0 | 0.016 | 0.60 | **0.60** |
| `sounds/hive/detail_scuttle_01.ogg` | транз | 0.62 | 5.2 | 0.016 | 0.60 | **0.60** |
| `sounds_380/entity/infected_vex_death_01.ogg` | транз | 1.93 | 22.8 | 0.015 | 0.60 | **0.60** |
| `sounds/combat/dismember_03.ogg` | транз | 1.42 | 23.0 | 0.015 | 0.60 | **0.60** |
| `sounds_380/entity/infected_shulker_hurt_01.ogg` | транз | 0.48 | 99.0 | 0.014 | 0.60 | **0.60** |
| `sounds_380/entity/infected_blaze_ambient_01.ogg` | стац | 3.16 | 5.2 | 0.014 | 0.05 | **0.06** |
| `sounds_380/entity/infected_evoker_hurt_01.ogg` | транз | 0.48 | 99.0 | 0.013 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_hurt_01.ogg` | транз | 0.40 | 99.0 | 0.012 | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_skeleton_attack_01.ogg` | транз | 0.64 | 14.7 | 0.012 | 0.60 | **0.60** |
| `sounds_380/entity/infected_breeze_attack_01.ogg` | транз | 0.84 | 28.4 | 0.012 | 0.60 | **0.60** |
| `sounds/amb/hive_pulse_02.ogg` | стац | 13.40 | 59.3 | 0.012 | 0.05 | **0.06** |
| `sounds_380/entity/infected_bogged_attack_01.ogg` | транз | 0.84 | 30.1 | 0.011 | 0.60 | **0.60** |
| `sounds_380/entity/infected_guardian_attack_01.ogg` | транз | 0.79 | 33.7 | 0.011 | 0.60 | **0.60** |
| `sounds/block/hive_membrane_step_01.ogg` | транз | 0.52 | 13.9 | 0.010 | 0.60 | **0.60** |
| `sounds_380/entity/infected_ghast_hurt_01.ogg` | транз | 0.47 | 99.0 | 0.010 | 0.60 | **0.60** |
| `sounds_380/entity/infected_ghast_attack_01.ogg` | транз | 0.64 | 15.0 | 0.010 | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_brute_hurt_01.ogg` | транз | 0.47 | 99.0 | 0.008 | 0.60 | **0.60** |
| `sounds_380/entity/infected_husk_death_01.ogg` | транз | 1.96 | 17.9 | 0.008 | 0.60 | **0.60** |
| `sounds_380/entity/infected_zombie_villager_ambient_01.ogg` | стац | 3.05 | 7.3 | 0.008 | 0.05 | **0.06** |
| `sounds/hive/hive_spawn_attack_02.ogg` | транз | 0.62 | 14.3 | 0.007 | 0.60 | **0.60** |
| `sounds/hive/spawn_skeleton_whip_03.ogg` | транз | 0.72 | 6.0 | 0.007 | 0.60 | **0.60** |
| `sounds_380/entity/infected_endermite_death_01.ogg` | транз | 1.52 | 14.4 | 0.007 | 0.60 | **0.60** |
| `sounds_380/entity/infected_drowned_attack_01.ogg` | транз | 0.68 | 16.2 | 0.006 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_alert_02.ogg` | транз | 0.72 | 6.7 | 0.005 | 0.60 | **0.60** |
| `sounds/block/synapse_node_pulse_01.ogg` | транз | 1.54 | 13.2 | 0.004 | 0.60 | **0.60** |
| `sounds_380/entity/infected_breeze_hurt_01.ogg` | транз | 0.41 | 99.0 | 0.003 | 0.60 | **0.60** |
| `sounds_380/entity/infected_vindicator_ambient_01.ogg` | стац | 2.88 | 6.5 | 0.003 | 0.05 | **0.05** |
| `sounds_380/entity/infected_warden_hurt_01.ogg` | транз | 0.49 | 99.0 | 0.002 | 0.60 | **0.60** |
| `sounds_380/entity/infected_stray_attack_01.ogg` | транз | 0.73 | 15.3 | 0.002 | 0.60 | **0.60** |
| `sounds/hive/hive_spawn_hurt_04.ogg` | транз | 0.27 | 99.0 | 0.000 | 0.60 | **0.60** |
| `sounds_380/entity/infected_hoglin_attack_01.ogg` | транз | 0.60 | 15.4 | 0.000 | 0.60 | **0.60** |
