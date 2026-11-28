# Единый реестр 16 комплектов существ и geo-блоков (Carnis 3.7.3 / 3.7.4)

## 1. 9 мобов (`src/main/resources/assets/carnis/textures/entity/`)
| Существо | Geo | Модель (код) | Текстура | Glowmask (Р-3) | Доля топа | Цветов | SHA-256 (12) | Норма A3R1 | Проверено кем/чем |
|---|---|---|---|---|---:|---:|---|---|---|
| `infected_creeper` | да | да | `64×32` | да (`24 px`, `(255,92,57)`) | 14.3% | 7 | `a7e3e36fefcb` | OK | Художник (`shade_density.py`, `glowmask_r3_check.py`) |
| `infected_skeleton` | да | да | `64×32` | да (`28 px`, `(255,92,57)`) | 14.3% | 7 | `8725542791ca` | OK | Художник (`shade_density.py`, `glowmask_r3_check.py`) |
| `infected_spider` | да | да | `64×32` | да (`520 px`, `(255,92,57)`) | 14.3% | 7 | `189ff8b84d2f` | OK | Художник (`shade_density.py`, `glowmask_r3_check.py`) |
| `infected_zombie` | да | да | `64×64` | да (`64 px`, `(255,92,57)`) | 14.3% | 7 | `099b174a10f8` | OK | Художник (`shade_density.py`, `glowmask_r3_check.py`) |
| `cerebral_nexus` | да | да | `64×64` | да (`28 px`, `(255,92,57)`) | 14.3% | 7 | `1e169fae8de9` | OK | Художник (`shade_density.py`, `glowmask_r3_check.py`) |
| `flesh_amalgam` | да | да | `128×128` | да (`26 px`, `(255,92,57)`, `Carnis_3.7.4_glowmask_fix.zip`) | 14.3% | 7 | `e6744ebbdf95` | OK | Художник (`shade_density.py`, `glowmask_r3_check.py`) |
| `hive_sentinel` | да | да | `64×64` | да (`28 px`, `(255,92,57)`) | 14.3% | 7 | `a3bbeb22ae02` | OK | Художник (`shade_density.py`, `glowmask_r3_check.py`) |
| `biomass_maggot` | да | да | `32×32` | да (`71 px`, `(255,92,57)`, `Carnis_3.7.3_glowmasks.zip`) | 14.4% | 7 | `cbcebd291f20` | OK | Художник (`shade_density.py`, `glowmask_r3_check.py`) |
| `parasitic_tendril` | да | да | `32×32` | да (`123 px`, `(255,92,57)`, `Carnis_3.7.3_glowmasks.zip`) | 14.4% | 7 | `5b8fca441614` | OK | Художник (`shade_density.py`, `glowmask_r3_check.py`) |

## 2. 7 geo-блоков и предметов (glowmask не требуется)
| Объект | Geo | Модель | Текстура | Glowmask | Норма | Проверено кем/чем |
|---|---|---|---|---|---|---|
| `bio_purifier` | да | да | да | не требуется | OK | Художник (`3.7.3`) |
| `hive_eye` | да | да | да | есть | OK | Художник (`shade_density.py`) |
| `nerve_pillar` | да | да | да | есть | OK | Художник (`shade_density.py`) |
| `neuro_armor` | да | да | да | не требуется | OK | Художник (`3.7.3`) |
| `pneumatic_inoculator` | да | да | да | не требуется | OK | Художник (`3.7.3`) |
| `pulsing_heart` | да | да | да | есть | OK | Художник (`shade_density.py`) |
| `pustule_cluster` | да | да | да | есть | OK | Художник (`shade_density.py`) |

## 3. Вариации существ 3.7.5 (`Carnis_3.7.5_B1_variations.zip`, B1–B3)
| Существо | Стадия 1 (`_stage1`, базовый спавн / ранняя инфекция) | Стадия 2 (`_stage2`, эволюция / мутировавшая форма) | Glowmask (Р-3) |
|---|---|---|---|
| `infected_creeper` | Первичный заражённый крипер (7 цветов, 14.3%) | Мутировавший крипер со сдвинутым тоном (7 цветов, 14.3%) | `24 px`, `outside=0` — **OK** |
| `infected_skeleton` | Первичный заражённый скелет (7 цветов, 14.3%) | Мутировавший скелет (7 цветов, 14.3%) | `28 px`, `outside=0` — **OK** |
| `infected_spider` | Первичный заражённый паук (7 цветов, 14.3%) | Мутировавший паук (7 цветов, 14.3%) | `520 px`, `outside=0` — **OK** |
| `infected_zombie` | Первичный заражённый зомби (7 цветов, 14.3%) | Мутировавший зомби (7 цветов, 14.3%) | `64 px`, `outside=0` — **OK** |

### 3a. Вариант B (`_b`) — вторая боевая форма (3.8.1)

Это НЕ отдельные существа: код (`InfectedVariant`) даёт каждому из четырёх мобов
боевой вариант A или B, и `*GeoModel` переключает модель/текстуру/анимации по
`isVariantA()`. Поэтому в реестре они записаны как отдельные визуальные наборы со
своими геометрией, текстурой и маской, но существами не считаются.

| Набор | Geo | Модель (код) | Текстура | Glowmask (Р-3) | Доля топа | Цветов | SHA-256 (12) | Норма A3R1 | Проверено кем/чем |
|---|---|---|---|---|---|---|---|---|---|
| `infected_creeper_b` | да | да | `64×64` | да (`128 px`, `(255,92,57)`) | 30.7% | 556 | `e0b05dc4f4e2` | OK | Я (`creature_pack_audit.py --require-anims`) |
| `infected_skeleton_b` | да | да | `64×64` | да (`144 px`, `(255,92,57)`) | 13.8% | 22 | `83d137a5c7ca` | OK | Я (`creature_pack_audit.py --require-anims`) |
| `infected_spider_b` | да | да | `64×64` | да (`256 px`, `(255,92,57)`) | 11.4% | 53 | `03e8cb41b70e` | OK | Я (`creature_pack_audit.py --require-anims`) |
| `infected_zombie_b` | да | да | `64×64` | да (`123 px`, `(255,92,57)`) | 20.0% | 70 | `35a7fc41ee38` | OK | Я (`creature_pack_audit.py --require-anims`) |

Маски `_b` пересобраны вручную: у зомби и крипера в исходнике маска была
шахматкой `(0,255,255)` на всём атласе (4096 px, вне силуэта), у зомби вдобавок
текстура имела промежуточную альфу 80/180. Теперь альфа бинарная, маска — ровно
`(255,92,57)`, только внутри силуэта, по светящимся пикселям (глаза/ядро).

## 4. Инвентаризация предметных текстур `textures/item/` (C1)
Всего: **26** текстур; в `BASELINE_PALETTE`: **0**; вне палитры: **26**.

| Файл | Размер | Цветов | Вне `BASELINE_PALETTE` |
|---|---|---:|---:|
| `amalgam_bile_glob.png` | `64×64` | 2150 | 2150 |
| `antibiotics.png` | `64×64` | 1008 | 1008 |
| `bio_purifier.png` | `64×64` | 143 | 143 |
| `bio_purifier_glowmask.png` | `64×64` | 2 | 2 |
| `bone_scythe.png` | `32×32` | 58 | 58 |
| `bone_scythe_arm.png` | `64×64` | 827 | 827 |
| `cerebral_nexus_spawn_egg.png` | `64×64` | 1710 | 1710 |
| `creeping_tendrils.png` | `16×16` | 7 | 5 |
| `flesh_spat.png` | `64×64` | 1419 | 1419 |
| `hive_sentinel_spawn_egg.png` | `64×64` | 1456 | 1456 |
| `neural_binding_matrix.png` | `64×64` | 2315 | 2315 |
| `neuro_resonator_boots.png` | `64×64` | 973 | 973 |
| `neuro_resonator_chestplate.png` | `64×64` | 1161 | 1161 |
| `neuro_resonator_helmet.png` | `64×64` | 1621 | 1621 |
| `neuro_resonator_leggings.png` | `64×64` | 1640 | 1640 |
| `ossified_scythe.png` | `32×32` | 62 | 62 |
| `parasitic_tendril_spawn_egg.png` | `64×64` | 1751 | 1751 |
| `pneumatic_inoculator_geo.png` | `64×64` | 191 | 191 |
| `purification_dart.png` | `64×64` | 378 | 378 |
| `purification_serum.png` | `64×64` | 1322 | 1322 |
| `purification_vial.png` | `64×64` | 1054 | 1054 |
| `pustule_grenade.png` | `64×64` | 1794 | 1794 |
| `research_journal.png` | `64×64` | 971 | 971 |
| `sinew_shield.png` | `32×32` | 668 | 668 |
| `tainted_sludge_bucket.png` | `64×64` | 763 | 763 |
| `viral_dart.png` | `64×64` | 462 | 462 |

## 5. Серия 3.8.0: 33 новых заражённых ванильных моба (`.geo.json` + текстура + `glowmask` Р-3)
| Моб | Архив | Геометрия | Текстура | Glowmask (Р-3) |
|---|---|---|---|---|
| `infected_blaze` | `Carnis_3.8.0_infected_vanilla_mobs.zip` | `infected_blaze.geo.json` | `infected_blaze.png` (7 цв.) | `infected_blaze_glowmask.png` (`OK`) |
| `infected_enderman` | `Carnis_3.8.0_infected_vanilla_mobs.zip` | `infected_enderman.geo.json` | `infected_enderman.png` (7 цв.) | `infected_enderman_glowmask.png` (`OK`) |
| `infected_pillager` | `Carnis_3.8.0_infected_vanilla_mobs.zip` | `infected_pillager.geo.json` | `infected_pillager.png` (7 цв.) | `infected_pillager_glowmask.png` (`OK`) |
| `infected_slime` | `Carnis_3.8.0_infected_vanilla_mobs.zip` | `infected_slime.geo.json` | `infected_slime.png` (7 цв.) | `infected_slime_glowmask.png` (`OK`) |
| `infected_witch` | `Carnis_3.8.0_infected_vanilla_mobs.zip` | `infected_witch.geo.json` | `infected_witch.png` (7 цв.) | `infected_witch_glowmask.png` (`OK`) |
| `infected_drowned` | `Carnis_3.8.0_infected_vanilla_mobs_part2.zip` | `infected_drowned.geo.json` | `infected_drowned.png` (7 цв.) | `infected_drowned_glowmask.png` (`OK`) |
| `infected_ghast` | `Carnis_3.8.0_infected_vanilla_mobs_part2.zip` | `infected_ghast.geo.json` | `infected_ghast.png` (7 цв.) | `infected_ghast_glowmask.png` (`OK`) |
| `infected_guardian` | `Carnis_3.8.0_infected_vanilla_mobs_part2.zip` | `infected_guardian.geo.json` | `infected_guardian.png` (7 цв.) | `infected_guardian_glowmask.png` (`OK`) |
| `infected_phantom` | `Carnis_3.8.0_infected_vanilla_mobs_part2.zip` | `infected_phantom.geo.json` | `infected_phantom.png` (7 цв.) | `infected_phantom_glowmask.png` (`OK`) |
| `infected_ravager` | `Carnis_3.8.0_infected_vanilla_mobs_part2.zip` | `infected_ravager.geo.json` | `infected_ravager.png` (7 цв.) | `infected_ravager_glowmask.png` (`OK`) |
| `infected_wither_skeleton` | `Carnis_3.8.0_infected_vanilla_mobs_part2.zip` | `infected_wither_skeleton.geo.json` | `infected_wither_skeleton.png` (7 цв.) | `infected_wither_skeleton_glowmask.png` (`OK`) |
| `infected_evoker` | `Carnis_3.8.0_infected_vanilla_mobs_part3.zip` | `infected_evoker.geo.json` | `infected_evoker.png` (7 цв.) | `infected_evoker_glowmask.png` (`OK`) |
| `infected_hoglin` | `Carnis_3.8.0_infected_vanilla_mobs_part3.zip` | `infected_hoglin.geo.json` | `infected_hoglin.png` (7 цв.) | `infected_hoglin_glowmask.png` (`OK`) |
| `infected_magma_cube` | `Carnis_3.8.0_infected_vanilla_mobs_part3.zip` | `infected_magma_cube.geo.json` | `infected_magma_cube.png` (7 цв.) | `infected_magma_cube_glowmask.png` (`OK`) |
| `infected_piglin_brute` | `Carnis_3.8.0_infected_vanilla_mobs_part3.zip` | `infected_piglin_brute.geo.json` | `infected_piglin_brute.png` (7 цв.) | `infected_piglin_brute_glowmask.png` (`OK`) |
| `infected_shulker` | `Carnis_3.8.0_infected_vanilla_mobs_part3.zip` | `infected_shulker.geo.json` | `infected_shulker.png` (7 цв.) | `infected_shulker_glowmask.png` (`OK`) |
| `infected_vindicator` | `Carnis_3.8.0_infected_vanilla_mobs_part3.zip` | `infected_vindicator.geo.json` | `infected_vindicator.png` (7 цв.) | `infected_vindicator_glowmask.png` (`OK`) |
| `infected_bogged` | `Carnis_3.8.0_infected_vanilla_mobs_part4.zip` | `infected_bogged.geo.json` | `infected_bogged.png` (7 цв.) | `infected_bogged_glowmask.png` (`OK`) |
| `infected_breeze` | `Carnis_3.8.0_infected_vanilla_mobs_part4.zip` | `infected_breeze.geo.json` | `infected_breeze.png` (7 цв.) | `infected_breeze_glowmask.png` (`OK`) |
| `infected_cave_spider` | `Carnis_3.8.0_infected_vanilla_mobs_part4.zip` | `infected_cave_spider.geo.json` | `infected_cave_spider.png` (7 цв.) | `infected_cave_spider_glowmask.png` (`OK`) |
| `infected_husk` | `Carnis_3.8.0_infected_vanilla_mobs_part4.zip` | `infected_husk.geo.json` | `infected_husk.png` (7 цв.) | `infected_husk_glowmask.png` (`OK`) |
| `infected_stray` | `Carnis_3.8.0_infected_vanilla_mobs_part4.zip` | `infected_stray.geo.json` | `infected_stray.png` (7 цв.) | `infected_stray_glowmask.png` (`OK`) |
| `infected_warden` | `Carnis_3.8.0_infected_vanilla_mobs_part4.zip` | `infected_warden.geo.json` | `infected_warden.png` (7 цв.) | `infected_warden_glowmask.png` (`OK`) |
| `infected_elder_guardian` | `Carnis_3.8.0_infected_vanilla_mobs_part5.zip` | `infected_elder_guardian.geo.json` | `infected_elder_guardian.png` (7 цв.) | `infected_elder_guardian_glowmask.png` (`OK`) |
| `infected_endermite` | `Carnis_3.8.0_infected_vanilla_mobs_part5.zip` | `infected_endermite.geo.json` | `infected_endermite.png` (7 цв.) | `infected_endermite_glowmask.png` (`OK`) |
| `infected_piglin` | `Carnis_3.8.0_infected_vanilla_mobs_part5.zip` | `infected_piglin.geo.json` | `infected_piglin.png` (7 цв.) | `infected_piglin_glowmask.png` (`OK`) |
| `infected_silverfish` | `Carnis_3.8.0_infected_vanilla_mobs_part5.zip` | `infected_silverfish.geo.json` | `infected_silverfish.png` (7 цв.) | `infected_silverfish_glowmask.png` (`OK`) |
| `infected_vex` | `Carnis_3.8.0_infected_vanilla_mobs_part5.zip` | `infected_vex.geo.json` | `infected_vex.png` (7 цв.) | `infected_vex_glowmask.png` (`OK`) |
| `infected_zoglin` | `Carnis_3.8.0_infected_vanilla_mobs_part5.zip` | `infected_zoglin.geo.json` | `infected_zoglin.png` (7 цв.) | `infected_zoglin_glowmask.png` (`OK`) |
| `infected_creaking` | `Carnis_3.8.0_infected_vanilla_mobs_part6.zip` | `infected_creaking.geo.json` | `infected_creaking.png` (7 цв.) | `infected_creaking_glowmask.png` (`OK`) |
| `infected_illusioner` | `Carnis_3.8.0_infected_vanilla_mobs_part6.zip` | `infected_illusioner.geo.json` | `infected_illusioner.png` (7 цв.) | `infected_illusioner_glowmask.png` (`OK`) |
| `infected_wither` | `Carnis_3.8.0_infected_vanilla_mobs_part6.zip` | `infected_wither.geo.json` | `infected_wither.png` (7 цв.) | `infected_wither_glowmask.png` (`OK`) |
| `infected_zombie_villager` | `Carnis_3.8.0_infected_vanilla_mobs_part6.zip` | `infected_zombie_villager.geo.json` | `infected_zombie_villager.png` (7 цв.) | `infected_zombie_villager_glowmask.png` (`OK`) |
