# Реестр звуков CARNIS — 158 файлов банка

**Кто:** Звук · **Задача:** шаг **S9** плана на версии вперёд · **База:** `9e4fff6`
**Дата:** 2026-11-26 14:20 · **Источник:** `03-sound/sounds/` + `sounds.json` и `ModSounds.java` из 3.7.3

Аналог `creature_registry.md` у Художника: одна строка на файл — имя, категория,
длительность, пик, запас, crest, спектральный центр, доля < 80 Гц и **где
используется** (включая признак «играется / событие спящее / архив»).

## Сводка

| показатель | значение |
|---|---:|
| файлов в банке | **158** |
| в пакете 3.7.3 | 144 |
| **играется из кода** | **129** |
| **событие есть, но не вызывается** | **15** |
| архивные материалы (вне пакета) | 14 |
| без события | **0** |
| пик > −1.00 dBFS | **0** |
| запас < 0.20 дБ | **0** |
| клиппинг | **0** |

**Ключевой факт:** из 144 файлов пакета **129 звучат в игре, 15 — нет.**
Это 11 событий из находки, принятой в доску как T-3184 (Кодер) и
T-3185 (`sound_orphans`).


### Категория `amb` — 9 файлов

| файл | длит., с | пик | запас | crest | центр, Гц | <80 Гц, % | КБ | где используется |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `amb/hive_ambient_01` | 120.00 | -7.06 | 6.06 | 15.1 | 2772 | 14.7 | 979.4 | играется: hive.ambient |
| `amb/hive_ambient_02` | 120.00 | -6.16 | 5.16 | 16.0 | 3074 | 19.7 | 912.2 | играется: hive.ambient |
| `amb/hive_ambient_03` | 120.00 | -5.57 | 4.57 | 16.6 | 2674 | 13.2 | 1022.7 | играется: hive.ambient |
| `amb/hive_ambient_close_01` | 120.00 | -4.02 | 3.02 | 16.9 | 2950 | 16.0 | 1047.4 | играется: hive.ambient_close |
| `amb/hive_ambient_close_02` | 120.00 | -3.63 | 2.63 | 17.1 | 3238 | 16.8 | 1009.3 | играется: hive.ambient_close |
| `amb/hive_ambient_tonal_stinger` | 10.00 | -5.34 | 4.34 | 14.1 | 4032 | 9.4 | 88.5 | играется: hive.ambient_tonal_stinger |
| `amb/hive_pulse_01` | 13.40 | -3.40 | 2.40 | 17.4 | 924 | 8.2 | 96.7 | играется: hive.pulse |
| `amb/hive_pulse_02` | 13.40 | -2.22 | 1.22 | 18.5 | 920 | 8.1 | 96.6 | играется: hive.pulse |
| `amb/hive_pulse_03` | 13.40 | -3.04 | 2.04 | 17.7 | 881 | 8.0 | 96.3 | играется: hive.pulse |

### Категория `archive` — 14 файлов

| файл | длит., с | пик | запас | crest | центр, Гц | <80 Гц, % | КБ | где используется |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `archive/hive/amalgam_breath_01_w1516` | 2.10 | -12.10 | 11.10 | 6.4 | 867 | 0.2 | 37.3 | архив (не в пакете) |
| `archive/hive/amalgam_breath_02_w1516` | 2.40 | -12.12 | 11.12 | 6.9 | 755 | 0.2 | 37.9 | архив (не в пакете) |
| `archive/hive/amalgam_shuffle_01_w1516` | 1.90 | -6.13 | 5.13 | 8.1 | 1366 | 34.1 | 43.1 | архив (не в пакете) |
| `archive/hive/amalgam_shuffle_02_w1516` | 2.10 | -6.12 | 5.12 | 8.1 | 1351 | 44.0 | 43.0 | архив (не в пакете) |
| `archive/hive/amalgam_shuffle_03_w1516` | 1.60 | -6.12 | 5.12 | 8.2 | 1316 | 31.4 | 33.5 | архив (не в пакете) |
| `archive/hive/amalgam_slam_01_w1516` | 2.00 | -5.18 | 4.18 | 15.3 | 2580 | 8.8 | 18.0 | архив (не в пакете) |
| `archive/hive/amalgam_slam_02_w1516` | 1.75 | -5.26 | 4.26 | 14.7 | 2336 | 16.6 | 17.0 | архив (не в пакете) |
| `archive/hive/spawn_creeper_crawl_01_w1516` | 1.05 | -10.12 | 9.12 | 7.8 | 1400 | 18.1 | 21.6 | архив (не в пакете) |
| `archive/hive/spawn_creeper_crawl_02_w1516` | 1.10 | -10.13 | 9.13 | 7.3 | 1752 | 22.6 | 25.0 | архив (не в пакете) |
| `archive/hive/spawn_creeper_detonate_01_w1516` | 1.60 | -6.24 | 5.24 | 6.7 | 1618 | 0.1 | 36.4 | архив (не в пакете) |
| `archive/hive/spawn_creeper_detonate_02_w1516` | 1.20 | -6.16 | 5.16 | 7.8 | 1811 | 0.1 | 23.0 | архив (не в пакете) |
| `archive/hive/spawn_creeper_sac_01_w1516` | 0.85 | -12.19 | 11.19 | 7.8 | 978 | 0.7 | 19.1 | архив (не в пакете) |
| `archive/hive/spawn_creeper_sac_02_w1516` | 0.95 | -12.11 | 11.11 | 6.8 | 1019 | 0.9 | 21.9 | архив (не в пакете) |
| `archive/hive/spawn_creeper_sac_03_w1516` | 1.00 | -12.18 | 11.18 | 7.3 | 1004 | 1.0 | 20.6 | архив (не в пакете) |

### Категория `block` — 20 файлов

| файл | длит., с | пик | запас | crest | центр, Гц | <80 Гц, % | КБ | где используется |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `block/bone_deflect` | 0.36 | -3.85 | 2.85 | 16.1 | 3367 | 0.0 | 10.5 | играется: bone_deflect |
| `block/creeper_rupture` | 0.90 | -3.11 | 2.11 | 14.0 | 1372 | 2.1 | 16.5 | СПЯЩЕЕ: creeper_rupture |
| `block/digestor_churn` | 2.30 | -5.24 | 4.24 | 10.8 | 703 | 47.3 | 30.1 | играется: digestor_churn |
| `block/heart_pulse` | 0.60 | -2.44 | 1.44 | 16.1 | 627 | 0.0 | 10.7 | играется: pulsing_heart_beat |
| `block/heartbeat_loop` | 1.40 | -3.11 | 2.11 | 15.5 | 912 | 1.4 | 19.4 | играется: heartbeat_loop |
| `block/hive_alarm` | 1.55 | -3.13 | 2.13 | 14.1 | 2421 | 0.9 | 28.2 | играется: hive.alarm |
| `block/hive_block_break_01_tear` | 0.62 | -1.20 | 0.20 | 18.6 | 1319 | 0.2 | 9.4 | играется: hive.block_break |
| `block/hive_block_break_02_pop` | 0.72 | -1.28 | 0.28 | 19.2 | 1196 | 0.0 | 10.0 | играется: hive.block_break |
| `block/hive_block_break_03_crunch` | 0.75 | -1.22 | 0.22 | 18.8 | 1748 | 1.2 | 11.0 | играется: hive.block_break |
| `block/hive_block_place_01_soft` | 0.30 | -1.74 | 0.74 | 19.9 | 2062 | 0.3 | 5.8 | играется: hive.block_place |
| `block/hive_block_place_02_dense` | 0.34 | -1.39 | 0.39 | 21.0 | 1444 | 0.1 | 5.5 | играется: hive.block_place |
| `block/hive_block_place_03_wet` | 0.26 | -1.85 | 0.85 | 18.5 | 1116 | 0.3 | 5.6 | играется: hive.block_place |
| `block/hive_eye_screech` | 1.90 | -4.15 | 3.15 | 12.9 | 2275 | 0.0 | 32.9 | играется: hive.eye_screech |
| `block/hive_heartbeat` | 2.34 | -7.92 | 6.92 | 10.0 | 1030 | 79.5 | 39.1 | играется: hive.heartbeat |
| `block/hive_membrane_place_01` | 0.42 | -4.00 | 3.00 | 15.0 | 1732 | 16.3 | 10.3 | играется: block.hive_membrane.place |
| `block/hive_membrane_step_01` | 0.52 | -4.17 | 3.17 | 15.4 | 1302 | 10.8 | 12.2 | играется: block.hive_membrane.step |
| `block/pustule_burst` | 0.80 | -3.08 | 2.08 | 13.9 | 1700 | 0.0 | 15.9 | играется: pustule_burst |
| `block/synapse_node_pulse_01` | 1.54 | -7.39 | 6.39 | 10.6 | 1212 | 63.2 | 26.1 | играется: block.synapse_node.pulse |
| `block/synapse_rupture` | 0.70 | -3.16 | 2.16 | 14.6 | 1791 | 0.0 | 15.8 | играется: synapse_rupture |
| `block/synapse_shock` | 0.55 | -3.03 | 2.03 | 15.0 | 2947 | 0.1 | 13.1 | СПЯЩЕЕ: synapse_shock |

### Категория `combat` — 23 файлов

| файл | длит., с | пик | запас | crest | центр, Гц | <80 Гц, % | КБ | где используется |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `combat/bone_scythe_hit_01` | 0.34 | -2.57 | 1.57 | 15.9 | 2653 | 0.0 | 7.3 | играется: item.bone_scythe.hit |
| `combat/bone_scythe_swing_01` | 0.44 | -3.54 | 2.54 | 15.0 | 2902 | 0.0 | 10.9 | играется: item.bone_scythe.swing |
| `combat/combat_deflect_01_chitin` | 0.34 | -1.27 | 0.27 | 18.5 | 3462 | 0.0 | 7.5 | играется: combat.armor_deflect |
| `combat/combat_deflect_02_bone` | 0.38 | -1.29 | 0.29 | 18.8 | 3513 | 0.0 | 6.6 | играется: combat.armor_deflect |
| `combat/combat_deflect_03_metal` | 0.30 | -1.92 | 0.92 | 18.2 | 3583 | 0.0 | 5.7 | играется: combat.armor_deflect |
| `combat/combat_deflect_04_glance` | 0.46 | -1.26 | 0.26 | 19.5 | 3492 | 0.0 | 9.5 | играется: combat.armor_deflect |
| `combat/combat_deflect_05_parry` | 0.40 | -1.27 | 0.27 | 18.6 | 3382 | 0.0 | 7.1 | играется: combat.armor_deflect |
| `combat/combat_flesh_hit_01` | 0.61 | -1.47 | 0.47 | 18.0 | 787 | 0.0 | 9.3 | играется: combat.flesh_hit |
| `combat/combat_flesh_hit_02` | 0.80 | -1.97 | 0.97 | 19.6 | 768 | 0.0 | 10.3 | играется: combat.flesh_hit |
| `combat/combat_flesh_hit_03` | 0.51 | -2.60 | 1.60 | 21.5 | 1096 | 0.0 | 8.3 | играется: combat.flesh_hit |
| `combat/combat_flesh_hit_deep_01_axe` | 1.05 | -1.25 | 0.25 | 15.5 | 371 | 10.5 | 14.5 | играется: combat.flesh_hit_deep |
| `combat/combat_flesh_hit_deep_02_crit` | 0.88 | -1.24 | 0.24 | 16.1 | 383 | 12.3 | 9.5 | играется: combat.flesh_hit_deep |
| `combat/combat_flesh_hit_deep_03_blast` | 1.18 | -1.22 | 0.22 | 15.1 | 417 | 1.2 | 11.6 | играется: combat.flesh_hit_deep |
| `combat/combat_stab_01_bone` | 0.38 | -1.25 | 0.25 | 19.1 | 2017 | 3.3 | 7.2 | играется: combat.block_stab |
| `combat/combat_stab_02_chitin` | 0.28 | -1.29 | 0.29 | 17.3 | 1988 | 3.1 | 6.7 | играется: combat.block_stab |
| `combat/combat_stab_03_shield` | 0.34 | -1.25 | 0.25 | 18.3 | 2007 | 3.8 | 7.0 | играется: combat.block_stab |
| `combat/dismember_01` | 1.28 | -1.25 | 0.25 | 17.2 | 1573 | 0.1 | 28.6 | играется: combat.dismember |
| `combat/dismember_02` | 1.14 | -1.95 | 0.95 | 17.9 | 1412 | 0.2 | 14.5 | играется: combat.dismember |
| `combat/dismember_03` | 1.42 | -1.88 | 0.88 | 18.3 | 1684 | 0.6 | 16.2 | играется: combat.dismember |
| `combat/dismember_04` | 0.94 | -1.64 | 0.64 | 16.3 | 1658 | 0.7 | 12.1 | играется: combat.dismember |
| `combat/dismember_05` | 1.36 | -1.34 | 0.34 | 16.6 | 1637 | 0.2 | 16.4 | играется: combat.dismember |
| `combat/ossified_scythe_hit_01` | 0.60 | -3.04 | 2.04 | 15.5 | 2108 | 0.8 | 12.9 | играется: item.ossified_scythe.hit |
| `combat/ossified_scythe_swing_01` | 0.72 | -4.95 | 3.95 | 13.1 | 2427 | 0.0 | 15.9 | играется: item.ossified_scythe.swing |

### Категория `entity` — 18 файлов

| файл | длит., с | пик | запас | crest | центр, Гц | <80 Гц, % | КБ | где используется |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `entity/acid_splash` | 0.70 | -3.13 | 2.13 | 13.4 | 3130 | 0.0 | 16.9 | играется: acid_splash |
| `entity/amalgamation_fuse` | 2.20 | -5.65 | 4.65 | 12.0 | 765 | 6.3 | 32.5 | играется: amalgamation_fuse |
| `entity/flamethrower_fire` | 1.64 | -6.26 | 5.26 | 12.7 | 2187 | 1.9 | 28.0 | СПЯЩЕЕ: flamethrower_fire |
| `entity/flesh_amalgam_ambient` | 2.30 | -9.77 | 8.77 | 10.2 | 896 | 0.5 | 31.6 | СПЯЩЕЕ: flesh_amalgam_ambient, hive.amalgam_breath |
| `entity/flesh_amalgam_death_01` | 2.60 | -8.43 | 7.43 | 8.1 | 946 | 33.6 | 42.8 | играется: flesh_amalgam_death |
| `entity/flesh_amalgam_hurt_01` | 1.15 | -8.07 | 7.07 | 8.2 | 1737 | 1.3 | 23.3 | играется: flesh_amalgam_hurt |
| `entity/flesh_amalgam_roar_01` | 1.85 | -5.12 | 4.12 | 8.5 | 1303 | 2.4 | 30.5 | играется: amalgam_roar |
| `entity/flesh_amalgam_roar_02` | 1.05 | -5.12 | 4.12 | 8.5 | 1159 | 1.9 | 19.3 | играется: amalgam_roar |
| `entity/flesh_amalgam_smash_01` | 2.60 | -3.15 | 2.15 | 15.1 | 1389 | 36.0 | 23.6 | СПЯЩЕЕ: amalgam_smash |
| `entity/flesh_amalgam_smash_02` | 1.90 | -3.02 | 2.02 | 14.0 | 1268 | 35.9 | 23.3 | СПЯЩЕЕ: amalgam_smash |
| `entity/flesh_amalgam_step_01` | 1.15 | -10.14 | 9.14 | 8.3 | 917 | 7.9 | 20.3 | играется: amalgam_step |
| `entity/flesh_amalgam_step_02` | 0.82 | -10.22 | 9.22 | 8.0 | 911 | 9.3 | 14.8 | играется: amalgam_step |
| `entity/incubation_cyst_ambient_01` | 2.30 | -9.47 | 8.47 | 11.6 | 790 | 31.1 | 31.9 | играется: entity.incubation_cyst.ambient |
| `entity/incubation_cyst_rupture_01` | 0.85 | -3.05 | 2.05 | 14.0 | 1636 | 0.5 | 17.0 | играется: entity.incubation_cyst.rupture |
| `entity/organic_creak` | 1.25 | -10.30 | 9.30 | 13.7 | 2537 | 0.0 | 23.5 | играется: organic_creak |
| `entity/pustule_grenade_impact_01` | 1.10 | -2.93 | 1.93 | 14.0 | 1995 | 4.4 | 18.7 | играется: entity.pustule_grenade.impact |
| `entity/pustule_grenade_throw_01` | 0.56 | -5.91 | 4.91 | 13.1 | 3269 | 0.0 | 13.4 | играется: entity.pustule_grenade.throw |
| `entity/sinew_shield_block_01` | 0.55 | -3.53 | 2.53 | 15.0 | 863 | 19.3 | 11.7 | играется: entity.sinew_shield.block |

### Категория `flesh` — 3 файлов

| файл | длит., с | пик | запас | crest | центр, Гц | <80 Гц, % | КБ | где используется |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `flesh/flesh_block_step_01` | 0.39 | -1.25 | 0.25 | 16.4 | 1289 | 1.3 | 6.6 | играется: flesh_block_step |
| `flesh/flesh_block_step_02` | 0.43 | -1.30 | 0.30 | 16.7 | 1453 | 3.5 | 7.7 | играется: flesh_block_step |
| `flesh/flesh_block_step_03` | 0.33 | -3.44 | 2.44 | 14.9 | 1273 | 0.8 | 7.0 | играется: flesh_block_step |

### Категория `hallucination` — 3 файлов

| файл | длит., с | пик | запас | crest | центр, Гц | <80 Гц, % | КБ | где используется |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `hallucination/phantom_creeper` | 1.90 | -5.98 | 4.98 | 13.0 | 3404 | 0.0 | 37.0 | играется: phantom_creeper |
| `hallucination/phantom_footsteps` | 2.40 | -6.43 | 5.43 | 13.6 | 695 | 23.5 | 35.3 | играется: phantom_footsteps |
| `hallucination/phantom_whisper` | 1.60 | -17.22 | 16.22 | 11.8 | 3403 | 0.0 | 31.6 | играется: phantom_whisper |

### Категория `hive` — 62 файлов

| файл | длит., с | пик | запас | crest | центр, Гц | <80 Гц, % | КБ | где используется |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `hive/amalgam_breath_01` | 2.00 | -14.14 | 13.14 | 7.4 | 2497 | 0.9 | 38.0 | играется: hive.amalgam_breath |
| `hive/amalgam_breath_02` | 2.40 | -14.64 | 13.64 | 7.4 | 2569 | 0.9 | 46.0 | играется: hive.amalgam_breath |
| `hive/amalgam_shuffle_01` | 1.30 | -8.53 | 7.53 | 8.0 | 956 | 15.3 | 21.0 | играется: hive.amalgam_shuffle |
| `hive/amalgam_shuffle_02` | 1.55 | -8.86 | 7.86 | 8.0 | 944 | 16.6 | 23.5 | играется: hive.amalgam_shuffle |
| `hive/amalgam_shuffle_03` | 1.10 | -8.27 | 7.27 | 8.0 | 968 | 8.0 | 18.7 | играется: hive.amalgam_shuffle |
| `hive/amalgam_slam_01` | 1.60 | -5.76 | 4.76 | 8.7 | 1423 | 59.1 | 26.9 | играется: hive.amalgam_slam |
| `hive/amalgam_slam_02` | 1.35 | -5.59 | 4.59 | 8.4 | 1144 | 57.7 | 24.0 | играется: hive.amalgam_slam |
| `hive/amb_core` | 120.00 | -12.24 | 11.24 | 15.2 | 1762 | 7.4 | 1154.5 | играется: hive.ambient_core |
| `hive/amb_deep` | 120.00 | -9.95 | 8.95 | 16.7 | 1265 | 12.2 | 852.7 | играется: hive.ambient_deep |
| `hive/amb_surface` | 120.00 | -13.27 | 12.27 | 14.2 | 2026 | 1.1 | 1207.5 | играется: hive.ambient_surface |
| `hive/amb_threshold` | 120.00 | -8.36 | 7.36 | 18.3 | 2976 | 13.2 | 875.6 | играется: hive.ambient_threshold |
| `hive/detail_bubbles_01` | 0.78 | -5.37 | 4.37 | 16.6 | 3754 | 0.1 | 10.5 | СПЯЩЕЕ: hive.detail_bubbles |
| `hive/detail_creak_01` | 1.12 | -5.99 | 4.99 | 16.0 | 3366 | 0.0 | 14.5 | СПЯЩЕЕ: hive.detail_creak |
| `hive/detail_flow_01` | 1.32 | -15.12 | 14.12 | 14.4 | 4186 | 0.0 | 15.7 | СПЯЩЕЕ: hive.detail_flow |
| `hive/detail_flow_02` | 0.48 | -7.33 | 6.33 | 14.5 | 3165 | 0.0 | 8.2 | СПЯЩЕЕ: hive.detail_flow |
| `hive/detail_membrane_01` | 0.54 | -4.97 | 3.97 | 16.8 | 4176 | 0.0 | 9.1 | СПЯЩЕЕ: hive.detail_membrane |
| `hive/detail_scuttle_01` | 0.62 | -2.80 | 1.80 | 19.3 | 4080 | 0.0 | 9.9 | СПЯЩЕЕ: hive.detail_scuttle |
| `hive/hive_spawn_alert_01` | 0.58 | -1.64 | 0.64 | 18.7 | 1892 | 0.3 | 11.2 | играется: hive.spawn_alert |
| `hive/hive_spawn_alert_02` | 0.72 | -1.51 | 0.51 | 17.9 | 1887 | 0.4 | 12.0 | играется: hive.spawn_alert |
| `hive/hive_spawn_alert_03` | 0.88 | -1.74 | 0.74 | 19.1 | 1943 | 0.5 | 15.3 | играется: hive.spawn_alert |
| `hive/hive_spawn_alert_04` | 1.12 | -1.51 | 0.51 | 19.4 | 1875 | 1.1 | 16.9 | играется: hive.spawn_alert |
| `hive/hive_spawn_attack_01` | 0.46 | -1.48 | 0.48 | 14.4 | 606 | 49.8 | 7.0 | играется: hive.spawn_attack |
| `hive/hive_spawn_attack_02` | 0.61 | -1.26 | 0.26 | 15.2 | 620 | 49.2 | 11.8 | играется: hive.spawn_attack |
| `hive/hive_spawn_attack_03` | 0.80 | -1.27 | 0.27 | 14.4 | 612 | 52.6 | 9.3 | играется: hive.spawn_attack |
| `hive/hive_spawn_attack_04` | 0.95 | -1.44 | 0.44 | 15.0 | 620 | 56.2 | 10.2 | играется: hive.spawn_attack |
| `hive/hive_spawn_death_01` | 2.42 | -2.39 | 1.39 | 11.3 | 683 | 77.5 | 18.0 | играется: hive.spawn_death |
| `hive/hive_spawn_death_02` | 2.87 | -2.69 | 1.69 | 11.0 | 703 | 73.7 | 21.3 | играется: hive.spawn_death |
| `hive/hive_spawn_death_03` | 3.02 | -3.18 | 2.18 | 11.3 | 732 | 72.3 | 21.7 | играется: hive.spawn_death |
| `hive/hive_spawn_death_04` | 1.97 | -2.94 | 1.94 | 11.3 | 654 | 75.7 | 15.7 | играется: hive.spawn_death |
| `hive/hive_spawn_hurt_01` | 0.40 | -1.26 | 0.26 | 13.2 | 1089 | 0.0 | 7.4 | играется: hive.spawn_hurt |
| `hive/hive_spawn_hurt_02` | 0.36 | -1.23 | 0.23 | 12.4 | 1245 | 0.0 | 6.4 | играется: hive.spawn_hurt |
| `hive/hive_spawn_hurt_03` | 0.41 | -1.42 | 0.42 | 13.3 | 1136 | 0.0 | 7.4 | играется: hive.spawn_hurt |
| `hive/hive_spawn_hurt_04` | 0.27 | -1.23 | 0.23 | 14.3 | 1251 | 0.0 | 9.9 | играется: hive.spawn_hurt |
| `hive/hive_spawn_hurt_critical_01` | 1.10 | -10.65 | 9.65 | 7.8 | 515 | 27.4 | 9.7 | играется: hive.spawn_hurt_critical |
| `hive/hive_spawn_hurt_critical_02` | 0.97 | -10.75 | 9.75 | 7.3 | 502 | 18.5 | 8.1 | играется: hive.spawn_hurt_critical |
| `hive/hive_spawn_hurt_critical_03` | 1.10 | -10.80 | 9.80 | 7.7 | 698 | 1.2 | 8.7 | играется: hive.spawn_hurt_critical |
| `hive/hive_spawn_hurt_critical_04` | 1.00 | -10.72 | 9.72 | 8.2 | 534 | 16.3 | 9.1 | играется: hive.spawn_hurt_critical |
| `hive/hive_spawn_idle_01` | 7.02 | -16.34 | 15.34 | 12.8 | 570 | 73.0 | 47.7 | играется: hive.spawn_idle |
| `hive/hive_spawn_idle_02` | 5.02 | -8.78 | 7.78 | 13.2 | 598 | 63.2 | 38.0 | играется: hive.spawn_idle |
| `hive/hive_spawn_idle_03` | 4.02 | -8.07 | 7.07 | 13.9 | 631 | 49.8 | 31.6 | играется: hive.spawn_idle |
| `hive/hive_spawn_idle_04` | 9.02 | -8.03 | 7.03 | 14.0 | 577 | 80.3 | 67.0 | играется: hive.spawn_idle |
| `hive/hive_spread_01_creep` | 0.90 | -1.30 | 0.30 | 23.1 | 1115 | 1.6 | 8.9 | СПЯЩЕЕ: hive.spread |
| `hive/hive_spread_02_pulse` | 0.80 | -3.29 | 2.29 | 18.8 | 1146 | 0.1 | 9.1 | СПЯЩЕЕ: hive.spread |
| `hive/hive_spread_03_swell` | 1.05 | -1.27 | 0.27 | 22.8 | 1189 | 0.3 | 12.5 | СПЯЩЕЕ: hive.spread |
| `hive/spawn_creeper_crawl_01` | 0.75 | -9.05 | 8.05 | 8.1 | 1803 | 0.5 | 19.2 | играется: hive.spawn_creeper_crawl |
| `hive/spawn_creeper_crawl_02` | 0.90 | -9.23 | 8.23 | 8.1 | 1690 | 0.3 | 21.4 | играется: hive.spawn_creeper_crawl |
| `hive/spawn_creeper_detonate_01` | 0.55 | -4.20 | 3.20 | 9.8 | 2192 | 19.5 | 12.6 | играется: hive.spawn_creeper_detonate |
| `hive/spawn_creeper_detonate_02` | 0.45 | -3.85 | 2.85 | 9.6 | 2464 | 17.7 | 11.4 | играется: hive.spawn_creeper_detonate |
| `hive/spawn_creeper_sac_01` | 0.85 | -9.97 | 8.97 | 9.1 | 2548 | 13.6 | 17.6 | играется: hive.spawn_creeper_sac |
| `hive/spawn_creeper_sac_02` | 0.70 | -9.85 | 8.85 | 8.7 | 2599 | 23.8 | 15.4 | играется: hive.spawn_creeper_sac |
| `hive/spawn_creeper_sac_03` | 0.97 | -10.50 | 9.50 | 8.9 | 2381 | 7.1 | 22.3 | играется: hive.spawn_creeper_sac |
| `hive/spawn_skeleton_blade_01` | 0.50 | -8.10 | 7.10 | 7.4 | 1954 | 0.0 | 14.9 | играется: hive.spawn_skeleton_blade |
| `hive/spawn_skeleton_blade_02` | 0.66 | -8.16 | 7.16 | 7.3 | 1679 | 0.0 | 17.7 | играется: hive.spawn_skeleton_blade |
| `hive/spawn_skeleton_blade_03` | 0.58 | -8.17 | 7.17 | 7.3 | 2261 | 0.0 | 13.3 | играется: hive.spawn_skeleton_blade |
| `hive/spawn_skeleton_bonecrack_01` | 0.44 | -11.38 | 10.38 | 10.6 | 5263 | 0.7 | 9.4 | играется: hive.spawn_skeleton_bonecrack |
| `hive/spawn_skeleton_bonecrack_02` | 0.50 | -11.48 | 10.48 | 10.5 | 5038 | 1.0 | 9.5 | играется: hive.spawn_skeleton_bonecrack |
| `hive/spawn_skeleton_whip_01` | 0.62 | -8.20 | 7.20 | 8.2 | 2744 | 0.0 | 14.9 | играется: hive.spawn_skeleton_whip |
| `hive/spawn_skeleton_whip_02` | 0.44 | -8.13 | 7.13 | 8.3 | 2480 | 0.0 | 11.9 | играется: hive.spawn_skeleton_whip |
| `hive/spawn_skeleton_whip_03` | 0.72 | -8.15 | 7.15 | 8.3 | 2369 | 0.0 | 17.7 | играется: hive.spawn_skeleton_whip |
| `hive/zone_stinger_deep` | 2.80 | -12.69 | 11.69 | 6.4 | 1022 | 84.8 | 22.4 | играется: hive.zone_stinger_deep |
| `hive/zone_stinger_intensify` | 2.40 | -12.67 | 11.67 | 9.5 | 988 | 51.8 | 19.1 | играется: hive.zone_stinger_intensify |
| `hive/zone_stinger_release` | 1.70 | -12.13 | 11.13 | 8.9 | 973 | 81.4 | 13.7 | играется: hive.zone_stinger_release |

### Категория `item` — 6 файлов

| файл | длит., с | пик | запас | crest | центр, Гц | <80 Гц, % | КБ | где используется |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `item/dart_hit` | 0.42 | -3.08 | 2.08 | 15.0 | 2856 | 0.0 | 11.2 | играется: entity.dart.hit |
| `item/inoculator_fire` | 0.70 | -3.41 | 2.41 | 14.1 | 544 | 0.0 | 10.2 | играется: item.inoculator.fire |
| `item/purification_vial_break_01` | 0.70 | -3.28 | 2.28 | 15.1 | 4411 | 0.0 | 14.6 | играется: item.purification_vial.break |
| `item/purifier_ignite` | 0.90 | -5.40 | 4.40 | 13.1 | 2974 | 0.0 | 19.4 | играется: item.purifier.ignite |
| `item/purifier_lamp_ignite_01` | 1.30 | -7.99 | 6.99 | 12.0 | 2703 | 2.5 | 24.9 | играется: block.purifier_lamp.ignite |
| `item/purifier_loop` | 2.89 | -8.12 | 7.12 | 13.9 | 2380 | 2.8 | 45.8 | играется: item.purifier.loop |

---

## Что реестр показал сразу (материал для S12/S13, не правка)

### Нормы уровня — все выполнены

| проверка | результат |
|---|---|
| пик ≤ −1.00 dBFS | **158/158** |
| запас ≥ 0.20 дБ | **158/158** |
| клиппинг | **0** |

### Спектральный центр < 400 Гц — 2 файла

Порог `timbre_check` (≥ 400 Гц) применяется к **ambient-слоям** (13 файлов), и
там он выполняется. Но реестр мерит все 158, и у двух боевых файлов центр ниже:

| файл | центр | < 80 Гц |
|---|---:|---:|
| `combat/combat_flesh_hit_deep_01_axe` | 371 Гц | 10.5 % |
| `combat/combat_flesh_hit_deep_02_crit` | 383 Гц | 12.3 % |

Это удары по плоти — низкий центр **ожидаем и уместен**. Предлагаю не
переделывать, а записать как принятое отклонение: порог 400 Гц писался для
эмбиента, распространять его на удары нет причин.

### Энергия < 80 Гц больше 25 % — 28 файлов

Тот же нюанс: норма «≤ 25 %» из ТЗ по ambient. Среди 28 файлов — почти все
`hive_spawn_death_*`, `hive_spawn_idle_*`, `zone_stinger_*`, `hive_heartbeat`.
Для «смерти улья» и «сердцебиения» низ — это суть звука.

**Худшие:** `zone_stinger_deep` 84.8 %, `zone_stinger_release` 81.4 %,
`hive_spawn_idle_04` 80.3 %, `hive_heartbeat` 79.5 %.

**Предлагаю:** норму < 80 Гц ≤ 25 % оставить **только для ambient-слоёв**
(9 длинных + 3 пульса + стингер = 13 файлов, там она и проверяется), а для
боевых и существ зафиксировать фактические значения как справочные.

**Важно:** я ничего не переделывал. Это материал для S13 (решение по каждому
отклонению) — решение за Архитектором.

### Спящие события — 15 файлов

Полный список — в таблицах выше (`СПЯЩЕЕ: ...`). Это находка, принятая в доску
как **T-3184** (Кодер: подвязать или удалить) и **T-3185** (`sound_orphans`
должен это ловить). Зона не моя — жду результат.

---

## Как читать реестр

- **длит.** — длительность в секундах (сэмплов / 44100).
- **пик** — максимум |амплитуды| в dBFS.
- **запас** — сколько дБ до порога −1.00. Норма ≥ 0.20.
- **crest** — Peak − RMS, дБ. Характеризует «ударность»: 6–8 дБ — фон, 12–20 — эффект, 20+ — резкий транзиент.
- **центр** — спектральный центр (Гц), «яркость».
- **<80 Гц, %** — доля энергии в самом низу, «телесность».
- **где используется** — `играется` (событие вызывается из кода), `СПЯЩЕЕ` (событие объявлено, но вызова нет), `архив` (файл вне пакета).

Все числа измерены декодированием в PCM 44.1 кГц моно; спектр — FFT с окном
Ханна. Скрипт замера — разовый, в репозиторий не кладу (зона `tools/` не моя).
