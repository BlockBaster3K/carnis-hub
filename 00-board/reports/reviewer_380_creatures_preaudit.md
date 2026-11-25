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
| UV кубов в пределах текстуры | 33/33 |
| A3R1: цветов | **7 у всех 33** |
| A3R1: топ-доля | **14,5–16,4 %** при пороге 35 % |
| альфа текстуры бинарная {{0,255}} | 33/33 |
| glowmask по Р-3 (ровно `(255,92,57)`, α бинарная, размер == текстуре, вне силуэта 0 px) | **33/33** |

## 3. Что не в норме — и это H-блок, а не сдача 3.8.0

| Критерий R14 | Требование | Факт |
|---|---|---|
| Костей у существа | ≥ 12 (цель 14–20) | **1–6**: минимум 1 (`infected_magma_cube`), максимум 6 (`bogged`, `drowned`, `enderman`, `hoglin`, `husk`, `piglin_brute`, `pillager`, `wither`) |
| Анимации `idle/walk/attack/hurt/death` | все 5 | **0** — файлов `animations/entity/*` в сдачах нет вовсе |

Это ровно тот риск, который Архитектор записал в T-3191: «новые существа останутся копиями ванильных мобов (1–6 костей, анимаций 0)». Подтверждаю числами: пока это низкополигональные заготовки с хорошими текстурами. Включать их в 3.8.0 как «новых существ» нельзя.

## 4. Полная таблица (33 существа)

| Существо | Костей | Текстура | Цветов | Топ | Glowmask | Анимации |
|---|---:|---|---:|---:|---|---|
| `infected_blaze` | 2 | 64x32 | 7 | 15.7 % | 41px | — |
| `infected_bogged` | 6 | 64x32 | 7 | 15.3 % | 45px | — |
| `infected_breeze` | 2 | 32x32 | 7 | 16.0 % | 26px | — |
| `infected_cave_spider` | 3 | 64x32 | 7 | 15.1 % | 48px | — |
| `infected_creaking` | 4 | 64x64 | 7 | 14.5 % | 98px | — |
| `infected_drowned` | 6 | 64x64 | 7 | 15.2 % | 86px | — |
| `infected_elder_guardian` | 2 | 64x64 | 7 | 15.3 % | 86px | — |
| `infected_enderman` | 6 | 64x32 | 7 | 15.3 % | 51px | — |
| `infected_endermite` | 3 | 64x32 | 7 | 14.9 % | 46px | — |
| `infected_evoker` | 5 | 64x64 | 7 | 14.8 % | 93px | — |
| `infected_ghast` | 4 | 64x32 | 7 | 15.8 % | 38px | — |
| `infected_guardian` | 3 | 64x64 | 7 | 15.0 % | 83px | — |
| `infected_hoglin` | 6 | 128x64 | 7 | 14.8 % | 174px | — |
| `infected_husk` | 6 | 64x64 | 7 | 15.2 % | 92px | — |
| `infected_illusioner` | 3 | 64x64 | 7 | 14.7 % | 82px | — |
| `infected_magma_cube` | 1 | 64x32 | 7 | 16.4 % | 43px | — |
| `infected_phantom` | 5 | 64x64 | 7 | 15.0 % | 81px | — |
| `infected_piglin` | 4 | 64x64 | 7 | 15.3 % | 93px | — |
| `infected_piglin_brute` | 6 | 64x64 | 7 | 15.0 % | 106px | — |
| `infected_pillager` | 6 | 64x64 | 7 | 14.6 % | 98px | — |
| `infected_ravager` | 6 | 128x128 | 7 | 14.8 % | 351px | — |
| `infected_shulker` | 3 | 64x64 | 7 | 14.8 % | 101px | — |
| `infected_silverfish` | 3 | 64x32 | 7 | 15.1 % | 42px | — |
| `infected_slime` | 1 | 64x32 | 7 | 15.3 % | 36px | — |
| `infected_stray` | 6 | 64x32 | 7 | 14.8 % | 38px | — |
| `infected_vex` | 4 | 32x32 | 7 | 15.3 % | 20px | — |
| `infected_vindicator` | 6 | 64x64 | 7 | 15.0 % | 108px | — |
| `infected_warden` | 6 | 128x128 | 7 | 14.7 % | 372px | — |
| `infected_witch` | 5 | 64x64 | 7 | 15.4 % | 113px | — |
| `infected_wither` | 5 | 64x64 | 7 | 15.3 % | 91px | — |
| `infected_wither_skeleton` | 6 | 64x32 | 7 | 15.7 % | 38px | — |
| `infected_zoglin` | 4 | 128x64 | 7 | 14.8 % | 185px | — |
| `infected_zombie_villager` | 4 | 64x64 | 7 | 14.8 % | 93px | — |

## 5. Что рекомендую

1. **Художнику:** H-блок (волна 51) — единственное, что превращает сдачи в существ: 12–20 костей и 5 анимаций со ссылками на существующие кости.
2. **Архитектору:** поправить объём T-3191 — существ **33**, а не 17.
3. **Кодеру:** регистрировать по списку из этого аудита (33 имени).
4. **Интегратору:** в гейт 3.8.0 ставить тот же критерий, что здесь, — `python3 02-reviewer/tools/creature_pack_audit.py <пакет> --min-bones 12`; иначе 3.8.0 пройдёт с болванками.

**Пакета 3.8.0 пока нет** — проверял сдачи Художника напрямую.
