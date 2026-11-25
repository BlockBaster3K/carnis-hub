# Ревизор · предполётная проверка существ из сдач 3.8.0 (`Carnis_3.8.0_infected_vanilla_mobs*`)

**Дата:** 2026-11-26 · **Инструмент:** новый `02-reviewer/tools/creature_pack_audit.py` · **Зона:** `02-reviewer/`
**Зачем:** ROADMAP R10 требует проверить новых существ до сборки пакета, а проверить их было нечем: гейт смотрит пакет, в котором этих файлов ещё нет.

## 1. Факт первый: существ не 17, а 33

В шести сдачах лежат **99 файлов = 33 существа × (geo + текстура + glowmask)**. Дублей и конфликтов между архивами нет: 0 путей, встречающихся в двух архивах.

Список целиком (33): `infected_blaze`, `infected_bogged`, `infected_breeze`, `infected_cave_spider`, `infected_creaking`, `infected_drowned`, `infected_elder_guardian`, `infected_enderman`, `infected_endermite`, `infected_evoker`, `infected_ghast`, `infected_guardian`, `infected_hoglin`, `infected_husk`, `infected_illusioner`, `infected_magma_cube`, `infected_phantom`, `infected_piglin`, `infected_piglin_brute`, `infected_pillager`, `infected_ravager`, `infected_shulker`, `infected_silverfish`, `infected_slime`, `infected_stray`, `infected_vex`, `infected_vindicator`, `infected_warden`, `infected_witch`, `infected_wither`, `infected_wither_skeleton`, `infected_zoglin`, `infected_zombie_villager`.

То есть покрытие **шире**, чем в T-3191 (17). Кодеру при регистрации нужно брать **33** имени, иначе 16 сданных существ попадут в пакет без `EntityType`.

## 2. Что в норме (по всем 33)

| Критерий | Результат |
|---|---|
| geo разбирается, `minecraft:geometry[0].bones` на месте | 33/33 |
| у каждой кости есть `pivot`, имена уникальны | 33/33, нарушений 0 |
| UV кубов в пределах текстуры | **32/33** — провал у `infected_wither_skeleton` (см. §3.1) |
| A3R1: цветов | **7 у всех 33** |
| A3R1: топ-доля | **14,5–16,4 %** при пороге 35 % |
| альфа текстуры бинарная {{0,255}} | 33/33 |
| glowmask по Р-3 (ровно `(255,92,57)`, α бинарная, размер == текстуре, вне силуэта 0 px) | **33/33** |

### 3.1. Единственный дефект сдачи: UV у `infected_wither_skeleton` выходит за текстуру

`geo/infected_wither_skeleton.geo.json`, кость `body`: `uv=[16,16]`, `size=[8,14,4]`.
По стандартной развёртке коробки (v занимает `size.y + size.z`) нижняя грань уходит
в `v = 16+14+4 = 34` при высоте текстуры **32** — на 2 px за край. Значит нижняя
грань тела сэмплирует за пределами PNG: в игре это «поехавшая»/зеркальная полоса.

Правка одна: `texture_height` 32→64 либо `uv` тела `[16,16]` → `[16,14]`
(`v = 14+14+4 = 32` ровно в край). Второе дешевле — текстура не перерисовывается.

**Первым прогоном я этот дефект пропустил** и записал «UV 33/33»: прогон шёл с
`head -45`, строка существа в отчёт не попала, а итог я прочитал по глазам. При
повторном прогоне чекер дал код 2 и это самое `✗`. В отчёте исправлено; впредь
числа беру только из полного вывода инструмента, не из обрезанного.

## 3. Что не в норме — и это H-блок, а не сдача 3.8.0

| Критерий R14 | Требование | Факт |
|---|---|---|
| Костей у существа | ≥ 12 (цель 14–20) | **1–6**: минимум 1 (`infected_magma_cube`), максимум 6 (`bogged`, `drowned`, `enderman`, `hoglin`, `husk`, `piglin_brute`, `pillager`, `wither`) |
| Анимации `idle/walk/attack/hurt/death` | все 5 | **0** — файлов `animations/entity/*` в сдачах нет вовсе |

Это ровно тот риск, который Архитектор записал в T-3191: «новые существа останутся копиями ванильных мобов (1–6 костей, анимаций 0)». Подтверждаю числами: пока это низкополигональные заготовки с хорошими текстурами. Включать их в 3.8.0 как «новых существ» нельзя.

## 4. Полная таблица (33 существа)

| Существо | Костей | Текстура | Цветов | Топ | Glowmask | UV | Анимации |
|---|---:|---|---:|---:|---|---|---|
| `infected_blaze` | 2 | 64x32 | 7 | 15.7 % | 41px | ok | — |
| `infected_bogged` | 6 | 64x32 | 7 | 15.3 % | 45px | ok | — |
| `infected_breeze` | 2 | 32x32 | 7 | 16.0 % | 26px | ok | — |
| `infected_cave_spider` | 3 | 64x32 | 7 | 15.1 % | 48px | ok | — |
| `infected_creaking` | 4 | 64x64 | 7 | 14.5 % | 98px | ok | — |
| `infected_drowned` | 6 | 64x64 | 7 | 15.2 % | 86px | ok | — |
| `infected_elder_guardian` | 2 | 64x64 | 7 | 15.3 % | 86px | ok | — |
| `infected_enderman` | 6 | 64x32 | 7 | 15.3 % | 51px | ok | — |
| `infected_endermite` | 3 | 64x32 | 7 | 14.9 % | 46px | ok | — |
| `infected_evoker` | 5 | 64x64 | 7 | 14.8 % | 93px | ok | — |
| `infected_ghast` | 4 | 64x32 | 7 | 15.8 % | 38px | ok | — |
| `infected_guardian` | 3 | 64x64 | 7 | 15.0 % | 83px | ok | — |
| `infected_hoglin` | 6 | 128x64 | 7 | 14.8 % | 174px | ok | — |
| `infected_husk` | 6 | 64x64 | 7 | 15.2 % | 92px | ok | — |
| `infected_illusioner` | 3 | 64x64 | 7 | 14.7 % | 82px | ok | — |
| `infected_magma_cube` | 1 | 64x32 | 7 | 16.4 % | 43px | ok | — |
| `infected_phantom` | 5 | 64x64 | 7 | 15.0 % | 81px | ok | — |
| `infected_piglin` | 4 | 64x64 | 7 | 15.3 % | 93px | ok | — |
| `infected_piglin_brute` | 6 | 64x64 | 7 | 15.0 % | 106px | ok | — |
| `infected_pillager` | 6 | 64x64 | 7 | 14.6 % | 98px | ok | — |
| `infected_ravager` | 6 | 128x128 | 7 | 14.8 % | 351px | ok | — |
| `infected_shulker` | 3 | 64x64 | 7 | 14.8 % | 101px | ok | — |
| `infected_silverfish` | 3 | 64x32 | 7 | 15.1 % | 42px | ok | — |
| `infected_slime` | 1 | 64x32 | 7 | 15.3 % | 36px | ok | — |
| `infected_stray` | 6 | 64x32 | 7 | 14.8 % | 38px | ok | — |
| `infected_vex` | 4 | 32x32 | 7 | 15.3 % | 20px | ok | — |
| `infected_vindicator` | 6 | 64x64 | 7 | 15.0 % | 108px | ok | — |
| `infected_warden` | 6 | 128x128 | 7 | 14.7 % | 372px | ok | — |
| `infected_witch` | 5 | 64x64 | 7 | 15.4 % | 113px | ok | — |
| `infected_wither` | 5 | 64x64 | 7 | 15.3 % | 91px | ok | — |
| `infected_wither_skeleton` | 6 | 64x32 | 7 | 15.7 % | 38px | **ВЫХОД** | — |
| `infected_zoglin` | 4 | 128x64 | 7 | 14.8 % | 185px | ok | — |
| `infected_zombie_villager` | 4 | 64x64 | 7 | 14.8 % | 93px | ok | — |

## 5. Что рекомендую

1. **Художнику:** (а) закрыть UV `infected_wither_skeleton` (одна правка `uv`/`texture_height`, см. §3.1) — это единственный дефект сдачи; (б) H-блок (волна 51/53) — единственное, что превращает сдачи в существ: 12–20 костей и 5 анимаций со ссылками на существующие кости.
2. **Архитектору:** поправить объём T-3191 — существ **33**, а не 17.
3. **Кодеру:** регистрировать по списку из этого аудита (33 имени).
4. **Интегратору:** в гейт 3.8.0 ставить тот же критерий, что здесь, — `python3 02-reviewer/tools/creature_pack_audit.py <пакет> --min-bones 12`; иначе 3.8.0 пройдёт с болванками.

**Пакета 3.8.0 пока нет** — проверял сдачи Художника напрямую.
