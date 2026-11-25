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
