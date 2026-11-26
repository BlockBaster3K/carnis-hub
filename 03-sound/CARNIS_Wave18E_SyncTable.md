# CARNIS · Сводная таблица синхронизации (единый документ к сдаче, волна 18E)

**Банк после 18E:** 157 OGG / 12 061 409 Б · манифест 158 строк (157 + заголовок) · расхождений манифест↔диск **0** · формат vorbis/44100/mono **157/157** · битрейт 160 — 80 файлов, 96 — 77 (долг волн 1–17, перекодировка не санкционирована).

**Пакет:** `transfer/CARNIS_transfer_105.tar.gz` — 105 файлов, 10 850 737 Б распакованных, размер архива 10 448 216 Б. SHA256 в архиве == SHA256 на диске: **105/105**. Суммы: `transfer/SHA256SUMS_transfer105.txt` (105 строк, flat).

---
## 1. Прежний пакет 86 был неполным — подтверждаю проверкой

Содержимое `CARNIS_transfer_86.tar.gz`, проверенное по составу архива:

| Позиция | В пакете 86 |
|---|---|
| 74 ранее переданных | есть |
| 12 файлов 18D §3 | есть |
| 10 недостающих из «14 перезаписей» (breath_01/02, shuffle_03, crawl_01/02, detonate_01/02, sac_01/02/03) | **нет** |
| 3 файла класса A (18D §4) | **нет** |
| 6 файлов 18E | **нет** |

Итого дополнено **19** файлов → **74 + 12 + 19 = 105**. Ваша догадка («если 86 = 74+12, пакет неполный») подтвердилась полностью.

---
## 2. Итоговая таблица по проекту

### 2.0 Три числа, которые надо держать вместе

| Действие | Файлов | Байт |
|---|---|---|
| **РАЗМЕСТИТЬ новое** (в проекте нет вообще) | **85** | 10 475 797 |
| **ПЕРЕЗАПИСАТЬ** (в проекте лежит старое по тому же пути) | **14** | 325 730 |
| **ПЕРЕМЕСТИТЬ** (в проекте лежит по старому пути) | **10** | 85 641 |
| **УДАЛИТЬ** (кодеровские, после прихода замен) | **10** | — |
| сумма копирования = пакет | **105** | 10 850 737 |

85 + 14 + 6 = 105: из 10 «перемещений» четыре (`hive_spawn_hurt_critical_01…04`) уже стоят в проекте под новыми именами, поэтому физически копируются только 6 файлов `block/*`.

### 2.1 РАЗМЕСТИТЬ новое — 85 файлов

| # | Путь в проекте | Байт | Группа |
|---|---|---|---|
| 1 | `amb/hive_ambient_01.ogg` | 970994 | амбиенты улья |
| 2 | `amb/hive_ambient_02.ogg` | 965598 | амбиенты улья |
| 3 | `amb/hive_ambient_03.ogg` | 970454 | амбиенты улья |
| 4 | `amb/hive_ambient_close_01.ogg` | 1068391 | амбиенты улья |
| 5 | `amb/hive_ambient_close_02.ogg` | 977381 | амбиенты улья |
| 6 | `amb/hive_ambient_tonal_stinger.ogg` | 83761 | амбиенты улья |
| 7 | `amb/hive_pulse_01.ogg` | 98999 | амбиенты улья |
| 8 | `amb/hive_pulse_02.ogg` | 98907 | амбиенты улья |
| 9 | `amb/hive_pulse_03.ogg` | 98576 | амбиенты улья |
| 10 | `block/bone_deflect.ogg` | 10767 | блоки |
| 11 | `block/creeper_rupture.ogg` | 16898 | блоки |
| 12 | `block/hive_membrane_place_01.ogg` | 10556 | блоки |
| 13 | `block/hive_membrane_step_01.ogg` | 12458 | блоки |
| 14 | `block/synapse_node_pulse_01.ogg` | 26700 | блоки |
| 15 | `block/synapse_shock.ogg` | 13424 | блоки |
| 16 | `combat/combat_deflect_01_chitin.ogg` | 5641 | бой |
| 17 | `combat/combat_deflect_02_bone.ogg` | 5417 | бой |
| 18 | `combat/combat_deflect_03_metal.ogg` | 4760 | бой |
| 19 | `combat/combat_deflect_04_glance.ogg` | 6138 | бой |
| 20 | `combat/combat_deflect_05_parry.ogg` | 5615 | бой |
| 21 | `combat/combat_flesh_hit_01.ogg` | 9490 | бой |
| 22 | `combat/combat_flesh_hit_02.ogg` | 10534 | бой |
| 23 | `combat/combat_flesh_hit_03.ogg` | 8490 | бой |
| 24 | `combat/combat_flesh_hit_deep_01_axe.ogg` | 11116 | бой |
| 25 | `combat/combat_flesh_hit_deep_02_crit.ogg` | 9867 | бой |
| 26 | `combat/combat_flesh_hit_deep_03_blast.ogg` | 12007 | бой |
| 27 | `combat/combat_stab_01_bone.ogg` | 5943 | бой |
| 28 | `combat/combat_stab_02_chitin.ogg` | 5232 | бой |
| 29 | `combat/combat_stab_03_shield.ogg` | 5447 | бой |
| 30 | `combat/dismember_01.ogg` | 15706 | бой |
| 31 | `combat/dismember_02.ogg` | 14863 | бой |
| 32 | `combat/dismember_03.ogg` | 16638 | бой |
| 33 | `combat/dismember_04.ogg` | 12415 | бой |
| 34 | `combat/dismember_05.ogg` | 16827 | бой |
| 35 | `combat/ossified_scythe_hit_01.ogg` | 13163 | бой |
| 36 | `combat/ossified_scythe_swing_01.ogg` | 16267 | бой |
| 37 | `entity/flamethrower_fire.ogg` | 28688 | сущности |
| 38 | `entity/flesh_amalgam_death_01.ogg` | 43857 | сущности |
| 39 | `entity/flesh_amalgam_hurt_01.ogg` | 23888 | сущности |
| 40 | `entity/flesh_amalgam_roar_01.ogg` | 31238 | сущности |
| 41 | `entity/flesh_amalgam_roar_02.ogg` | 19726 | сущности |
| 42 | `entity/flesh_amalgam_smash_01.ogg` | 24183 | сущности |
| 43 | `entity/flesh_amalgam_smash_02.ogg` | 23817 | сущности |
| 44 | `entity/flesh_amalgam_step_01.ogg` | 20741 | сущности |
| 45 | `entity/flesh_amalgam_step_02.ogg` | 15204 | сущности |
| 46 | `entity/incubation_cyst_ambient_01.ogg` | 32621 | сущности |
| 47 | `entity/incubation_cyst_rupture_01.ogg` | 17373 | сущности |
| 48 | `entity/organic_creak.ogg` | 24038 | сущности |
| 49 | `entity/pustule_grenade_impact_01.ogg` | 19194 | сущности |
| 50 | `entity/pustule_grenade_throw_01.ogg` | 13683 | сущности |
| 51 | `entity/sinew_shield_block_01.ogg` | 11958 | сущности |
| 52 | `flesh/flesh_block_step_01.ogg` | 7767 | плоть |
| 53 | `flesh/flesh_block_step_02.ogg` | 7908 | плоть |
| 54 | `flesh/flesh_block_step_03.ogg` | 7146 | плоть |
| 55 | `hallucination/phantom_creeper.ogg` | 37850 | галлюцинации |
| 56 | `hallucination/phantom_whisper.ogg` | 32398 | галлюцинации |
| 57 | `hive/amb_core.ogg` | 1046279 | улей |
| 58 | `hive/amb_deep.ogg` | 913230 | улей |
| 59 | `hive/amb_surface.ogg` | 1041842 | улей |
| 60 | `hive/amb_threshold.ogg` | 1029799 | улей |
| 61 | `hive/detail_bubbles_01.ogg` | 10930 | улей |
| 62 | `hive/detail_creak_01.ogg` | 14453 | улей |
| 63 | `hive/detail_flow_01.ogg` | 16071 | улей |
| 64 | `hive/detail_flow_02.ogg` | 8341 | улей |
| 65 | `hive/detail_membrane_01.ogg` | 9436 | улей |
| 66 | `hive/detail_scuttle_01.ogg` | 10438 | улей |
| 67 | `hive/hive_spawn_attack_01.ogg` | 7188 | улей |
| 68 | `hive/hive_spawn_attack_02.ogg` | 8242 | улей |
| 69 | `hive/hive_spawn_attack_03.ogg` | 9495 | улей |
| 70 | `hive/hive_spawn_attack_04.ogg` | 10533 | улей |
| 71 | `hive/hive_spread_01_creep.ogg` | 6167 | улей |
| 72 | `hive/hive_spread_02_pulse.ogg` | 9150 | улей |
| 73 | `hive/hive_spread_03_swell.ogg` | 12779 | улей |
| 74 | `hive/spawn_skeleton_blade_01.ogg` | 15245 | улей |
| 75 | `hive/spawn_skeleton_blade_02.ogg` | 18133 | улей |
| 76 | `hive/spawn_skeleton_blade_03.ogg` | 13665 | улей |
| 77 | `hive/zone_stinger_deep.ogg` | 22938 | улей |
| 78 | `hive/zone_stinger_intensify.ogg` | 19526 | улей |
| 79 | `hive/zone_stinger_release.ogg` | 14075 | улей |
| 80 | `item/dart_hit.ogg` | 11504 | предметы |
| 81 | `item/inoculator_fire.ogg` | 10490 | предметы |
| 82 | `item/purification_vial_break_01.ogg` | 14939 | предметы |
| 83 | `item/purifier_ignite.ogg` | 19819 | предметы |
| 84 | `item/purifier_lamp_ignite_01.ogg` | 25511 | предметы |
| 85 | `item/purifier_loop.ogg` | 46861 | предметы |

Итого **85** файлов  10 475 797 Б.

### 2.2 ПЕРЕЗАПИСАТЬ — 14 файлов (старые волны 15/16 → архив 18A)

| # | Путь | старый размер | новый размер | Δ |
|---|---|---|---|---|
| 1 | `hive/amalgam_breath_01.ogg` | 38235 | 38924 | +689 |
| 2 | `hive/amalgam_breath_02.ogg` | 38790 | 47090 | +8300 |
| 3 | `hive/amalgam_shuffle_01.ogg` | 44121 | 21534 | -22587 |
| 4 | `hive/amalgam_shuffle_02.ogg` | 44054 | 24032 | -20022 |
| 5 | `hive/amalgam_shuffle_03.ogg` | 34281 | 19130 | -15151 |
| 6 | `hive/amalgam_slam_01.ogg` | 18436 | 27556 | +9120 |
| 7 | `hive/amalgam_slam_02.ogg` | 17363 | 24605 | +7242 |
| 8 | `hive/spawn_creeper_crawl_01.ogg` | 22169 | 19662 | -2507 |
| 9 | `hive/spawn_creeper_crawl_02.ogg` | 25602 | 21906 | -3696 |
| 10 | `hive/spawn_creeper_detonate_01.ogg` | 37264 | 12919 | -24345 |
| 11 | `hive/spawn_creeper_detonate_02.ogg` | 23551 | 11723 | -11828 |
| 12 | `hive/spawn_creeper_sac_01.ogg` | 19563 | 18010 | -1553 |
| 13 | `hive/spawn_creeper_sac_02.ogg` | 22447 | 15793 | -6654 |
| 14 | `hive/spawn_creeper_sac_03.ogg` | 21073 | 22846 | +1773 |

### 2.3 ПЕРЕМЕСТИТЬ — 10 файлов

| # | из | в | байт | уже в проекте? |
|---|---|---|---|---|
| 1 | `hive/hive_block_break_01_tear.ogg` | `block/hive_block_break_01_tear.ogg` | 9890 | нет, скопировать |
| 2 | `hive/hive_block_break_02_pop.ogg` | `block/hive_block_break_02_pop.ogg` | 10439 | нет, скопировать |
| 3 | `hive/hive_block_break_03_crunch.ogg` | `block/hive_block_break_03_crunch.ogg` | 11526 | нет, скопировать |
| 4 | `hive/hive_block_place_01_soft.ogg` | `block/hive_block_place_01_soft.ogg` | 5965 | нет, скопировать |
| 5 | `hive/hive_block_place_02_dense.ogg` | `block/hive_block_place_02_dense.ogg` | 5667 | нет, скопировать |
| 6 | `hive/hive_block_place_03_wet.ogg` | `block/hive_block_place_03_wet.ogg` | 5723 | нет, скопировать |
| 7 | `hive/spawn_hurt_critical_01.ogg` | `hive/hive_spawn_hurt_critical_01.ogg` | 9938 | да, только проверить SHA256 |
| 8 | `hive/spawn_hurt_critical_02.ogg` | `hive/hive_spawn_hurt_critical_02.ogg` | 8267 | да, только проверить SHA256 |
| 9 | `hive/spawn_hurt_critical_03.ogg` | `hive/hive_spawn_hurt_critical_03.ogg` | 8898 | да, только проверить SHA256 |
| 10 | `hive/spawn_hurt_critical_04.ogg` | `hive/hive_spawn_hurt_critical_04.ogg` | 9328 | да, только проверить SHA256 |

### 2.4 УДАЛИТЬ — 10 кодеровских (только после прихода замен)

| # | Путь в проекте | чем закрывается |
|---|---|---|
| 1 | `entity/creeper_rupture.ogg` | `block/creeper_rupture.ogg` (разместить, §2.1) |
| 2 | `entity/flamethrower_fire.ogg` | `entity/flamethrower_fire.ogg` — **тот же путь**, замена файла (18D → 18E, переименование по п.1) |
| 3 | `entity/flesh_amalgam_death.ogg` | `entity/flesh_amalgam_death_01.ogg` — **остаётся единственным носителем**, см. §4 |
| 4 | `entity/flesh_amalgam_hurt.ogg` | `entity/flesh_amalgam_hurt_01.ogg` — **единственный носитель**, см. §4 |
| 5 | `hallucination/phantom_creeper.ogg` | замена файла по тому же пути (§2.1) |
| 6 | `hallucination/phantom_whisper.ogg` | замена файла по тому же пути (§2.1) |
| 7 | `item/dart_hit.ogg` | замена файла по тому же пути (§2.1) |
| 8 | `item/inoculator_fire.ogg` | замена файла по тому же пути (§2.1) |
| 9 | `item/purifier_ignite.ogg` | замена файла по тому же пути (§2.1) |
| 10 | `item/purifier_loop.ogg` | замена файла по тому же пути (§2.1) |

**Порядок важен:** сначала положить замену, потом удалять старое. Для 6 позиций (`phantom_*`, `dart_hit`, `inoculator_fire`, `purifier_ignite`, `purifier_loop`) путь совпадает — это перезапись, а не удаление; удаление касается только `entity/creeper_rupture`, `entity/flamethrower_fire` (старое имя `item/flamethrower_fire`), `entity/flesh_amalgam_death`, `entity/flesh_amalgam_hurt`.

---
## 3. Остаток банка, ещё не размещённый

Всего в банке **157**, в пакете **105**, **остаток 52** — всё это либо архив, либо уже размещённое ранее, либо сироты:

| группа | файлов |
|---|---|
| архив `*_w1516` — **не переносить** | 14 |
| сироты `entity/flesh_amalgam_*` (алиасы Q7, ваша зона) | 1 |
| размещено в проекте ранее (волны 2–18C) | 37 |

**Архив — 14:**
- `hive/amalgam_breath_01_w1516.ogg`
- `hive/amalgam_breath_02_w1516.ogg`
- `hive/amalgam_shuffle_01_w1516.ogg`
- `hive/amalgam_shuffle_02_w1516.ogg`
- `hive/amalgam_shuffle_03_w1516.ogg`
- `hive/amalgam_slam_01_w1516.ogg`
- `hive/amalgam_slam_02_w1516.ogg`
- `hive/spawn_creeper_crawl_01_w1516.ogg`
- `hive/spawn_creeper_crawl_02_w1516.ogg`
- `hive/spawn_creeper_detonate_01_w1516.ogg`
- `hive/spawn_creeper_detonate_02_w1516.ogg`
- `hive/spawn_creeper_sac_01_w1516.ogg`
- `hive/spawn_creeper_sac_02_w1516.ogg`
- `hive/spawn_creeper_sac_03_w1516.ogg`

**Сироты — 8:**
- `entity/flesh_amalgam_ambient.ogg`

**Размещено ранее — 37:**
- `block/digestor_churn.ogg`
- `block/heart_pulse.ogg`
- `block/heartbeat_loop.ogg`
- `block/hive_alarm.ogg`
- `block/hive_eye_screech.ogg`
- `block/hive_heartbeat.ogg`
- `block/nervous_twitch.ogg`
- `block/pustule_burst.ogg`
- `block/synapse_rupture.ogg`
- `entity/acid_splash.ogg`
- `entity/amalgamation_fuse.ogg`
- `hallucination/phantom_footsteps.ogg`
- `hive/hive_spawn_alert_01.ogg`
- `hive/hive_spawn_alert_02.ogg`
- `hive/hive_spawn_alert_03.ogg`
- `hive/hive_spawn_alert_04.ogg`
- `hive/hive_spawn_death_01.ogg`
- `hive/hive_spawn_death_02.ogg`
- `hive/hive_spawn_death_03.ogg`
- `hive/hive_spawn_death_04.ogg`
- `hive/hive_spawn_hurt_01.ogg`
- `hive/hive_spawn_hurt_02.ogg`
- `hive/hive_spawn_hurt_03.ogg`
- `hive/hive_spawn_hurt_04.ogg`
- `hive/hive_spawn_hurt_critical_01.ogg`
- `hive/hive_spawn_hurt_critical_02.ogg`
- `hive/hive_spawn_hurt_critical_03.ogg`
- `hive/hive_spawn_hurt_critical_04.ogg`
- `hive/hive_spawn_idle_01.ogg`
- `hive/hive_spawn_idle_02.ogg`
- `hive/hive_spawn_idle_03.ogg`
- `hive/hive_spawn_idle_04.ogg`
- `hive/spawn_skeleton_bonecrack_01.ogg`
- `hive/spawn_skeleton_bonecrack_02.ogg`
- `hive/spawn_skeleton_whip_01.ogg`
- `hive/spawn_skeleton_whip_02.ogg`
- `hive/spawn_skeleton_whip_03.ogg`
