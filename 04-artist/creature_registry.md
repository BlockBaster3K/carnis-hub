# Единый реестр 16 комплектов существ и geo-блоков (Carnis 3.7.3 / 3.7.4)

## 1. 9 мобов (`src/main/resources/assets/carnis/textures/entity/`)
| Существо | Geo | Модель (код) | Текстура | Glowmask (Р-3) | Доля топа | Цветов | Норма A3R1 | Проверено кем/чем |
|---|---|---|---|---|---:|---:|---|---|
| `infected_creeper` | да | да | `64×32` | да (`24 px`, `(255,92,57)`) | 28.3% | 7 | OK | Художник (`glowmask_r3_check.py`, `shade_density.py`) |
| `infected_skeleton` | да | да | `64×32` | да (`28 px`, `(255,92,57)`) | 24.1% | 7 | OK | Художник (`glowmask_r3_check.py`, `shade_density.py`) |
| `infected_spider` | да | да | `64×32` | да (`520 px`, `(255,92,57)`) | 32.2% | 7 | OK | Художник (`glowmask_r3_check.py`, `shade_density.py`) |
| `infected_zombie` | да | да | `64×64` | да (`64 px`, `(255,92,57)`) | 22.9% | 7 | OK | Художник (`glowmask_r3_check.py`, `shade_density.py`) |
| `cerebral_nexus` | да | да | `64×64` | да (`28 px`, `(255,92,57)`) | 14.3% | 7 | OK | Художник (`glowmask_r3_check.py`, `shade_density.py`) |
| `flesh_amalgam` | да | да | `128×128` | **исправлен** (`26 px`, `(255,92,57)`, `Carnis_3.7.4_glowmask_fix.zip`) | 14.3% | 7 | OK | Художник (`glowmask_r3_check.py`, `shade_density.py`) |
| `hive_sentinel` | да | да | `64×64` | да (`28 px`, `(255,92,57)`) | 14.3% | 7 | OK | Художник (`glowmask_r3_check.py`, `shade_density.py`) |
| `biomass_maggot` | да | да | `32×32` | да (`71 px`, `(255,92,57)`, `Carnis_3.7.3_glowmasks.zip`) | 4.5% | 38 | OK | Художник (`glowmask_r3_check.py`) + Ревизор |
| `parasitic_tendril` | да | да | `32×32` | да (`123 px`, `(255,92,57)`, `Carnis_3.7.3_glowmasks.zip`) | 2.5% | 222 | OK | Художник (`glowmask_r3_check.py`) + Ревизор |

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
