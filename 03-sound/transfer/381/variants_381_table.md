# Таблица 27 звуков → 8 вариантов мобов 3.8.1 (S131)

Сборка **воспроизводима побайтово**: `ffmpeg -fflags +bitexact` обнуляет случайный serial Ogg
(без флага libvorbis вставляет новый serial на каждое кодирование — замер: 0 совпадений из 27).
Проверка: два прогона `gen_381.py` подряд дают **27/27** совпадений SHA-256.

| # | событие | файл | crest | пик | RMS | отсчётов | SHA-256 |
|---|---|---|---:|---:|---:|---:|---|
| 1 | `entity.infected_creeper_charger.charge` | `creeper_b_charge.ogg` | 17.99 | -1.47 | -19.46 | 44100 | `5a0a216c9db0ba92…` |
| 2 | `entity.infected_creeper_charger.directed_blast` | `creeper_b_directed_blast.ogg` | 17.99 | -1.45 | -19.44 | 48510 | `3a02177955f8d288…` |
| 3 | `entity.infected_creeper_charger.freeze` | `creeper_b_freeze.ogg` | 17.93 | -1.54 | -19.47 | 35328 | `d054816564691205…` |
| 4 | `entity.infected_creeper_charger.shield_drop` | `creeper_b_shield_drop.ogg` | 17.95 | -1.47 | -19.42 | 35152 | `7a9073f59df5eb57…` |
| 5 | `entity.infected_creeper_mortar.anchor` | `creeper_a_anchor.ogg` | 17.93 | -1.48 | -19.41 | 57330 | `1fcdab0f7ac31281…` |
| 6 | `entity.infected_creeper_mortar.death_blast` | `creeper_a_death_blast.ogg` | 17.94 | -1.43 | -19.37 | 61739 | `cfc57e1847f5582f…` |
| 7 | `entity.infected_creeper_mortar.launch` | `creeper_a_launch.ogg` | 18.02 | -1.40 | -19.43 | 30741 | `a1a9e30cfdca680c…` |
| 8 | `entity.infected_creeper_mortar.poison_cloud` | `creeper_a_poison_cloud.ogg` | 18.02 | -1.41 | -19.43 | 70560 | `fcc62e7f61fd135e…` |
| 9 | `entity.infected_skeleton_impaler.parry_ricochet` | `skeleton_b_parry_ricochet.ogg` | 17.93 | -1.46 | -19.39 | 35152 | `b05cd8a0fd167c65…` |
| 10 | `entity.infected_skeleton_impaler.pike_thrust` | `skeleton_b_pike_thrust.ogg` | 17.96 | -1.49 | -19.45 | 21922 | `71b529ce11492a24…` |
| 11 | `entity.infected_skeleton_sniper.armor_pierce` | `skeleton_a_armor_pierce.ogg` | 17.98 | -1.44 | -19.42 | 31424 | `d7bb00e08d1a9f70…` |
| 12 | `entity.infected_skeleton_sniper.bow_draw` | `skeleton_a_bow_draw.ogg` | 18.01 | -1.45 | -19.45 | 110250 | `b6010f1b67bf919e…` |
| 13 | `entity.infected_skeleton_sniper.shot` | `skeleton_a_shot.ogg` | 17.99 | -1.41 | -19.40 | 19717 | `819f43867ba7d102…` |
| 14 | `entity.infected_spider_arachnid.jump` | `spider_a_jump.ogg` | 17.99 | -1.42 | -19.42 | 19717 | `ddac8d4bed1716be…` |
| 15 | `entity.infected_spider_arachnid.land` | `spider_a_land.ogg` | 17.90 | -1.41 | -19.31 | 24127 | `16f300a4dba1fd44…` |
| 16 | `entity.infected_spider_arachnid.paralytic` | `spider_a_paralytic.ogg` | 17.99 | -1.43 | -19.42 | 52920 | `b2d4d71d8b436227…` |
| 17 | `entity.infected_spider_arachnid.web` | `spider_a_web.ogg` | 17.93 | -1.51 | -19.44 | 37357 | `7962c8224672f550…` |
| 18 | `entity.infected_spider_crusher.leg_slam` | `spider_b_leg_slam.ogg` | 18.04 | -1.43 | -19.47 | 32947 | `e9c8acaeba89fcde…` |
| 19 | `entity.infected_spider_crusher.shield_break` | `spider_b_shield_break.ogg` | 17.98 | -1.44 | -19.43 | 39562 | `f77e230416807794…` |
| 20 | `entity.infected_spider_crusher.shockwave` | `spider_b_shockwave.ogg` | 17.92 | -1.42 | -19.35 | 43972 | `3dac1a288f438ec7…` |
| 21 | `entity.infected_zombie_ripper.bite_quick` | `zombie_b_bite_quick.ogg` | 17.94 | -1.43 | -19.36 | 30741 | `52e15fc6cb24e4c3…` |
| 22 | `entity.infected_zombie_ripper.leap` | `zombie_b_leap.ogg` | 17.97 | -1.47 | -19.44 | 26496 | `ecf8cd401fa462c8…` |
| 23 | `entity.infected_zombie_ripper.slowness_apply` | `zombie_b_slowness.ogg` | 17.92 | -1.42 | -19.34 | 48510 | `c1b9f67437732550…` |
| 24 | `entity.infected_zombie_ripper.vampiric_drain` | `zombie_b_vampiric.ogg` | 17.96 | -1.45 | -19.41 | 43972 | `568893829b216e97…` |
| 25 | `entity.infected_zombie_scythed.bleed_apply` | `zombie_a_bleed_apply.ogg` | 17.94 | -1.42 | -19.37 | 37357 | `48aeb10defb7efe7…` |
| 26 | `entity.infected_zombie_scythed.cleave_hit` | `zombie_a_cleave_hit.ogg` | 17.99 | -1.43 | -19.42 | 21922 | `081d67ae13ad645f…` |
| 27 | `entity.infected_zombie_scythed.cleave_swing` | `zombie_a_cleave_swing.ogg` | 17.94 | -1.45 | -19.39 | 18394 | `da7da121798732a0…` |
