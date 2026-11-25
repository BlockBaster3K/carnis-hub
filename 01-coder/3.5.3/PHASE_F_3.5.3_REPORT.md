# PHASE F — пакет Кодера 3.5.3 (подготовка, не отправлен)

**Ветка:** `arena/d474d740-carnis-hub`  
**Исходная база:** `01-coder/3.5.2-R/project-3.5.2-clean.zip`  
**Статус:** Д1–Д7 подготовлены в одном пакете `01-coder/3.5.3/`; локальные сборки не запускались. CI запускается после push.

## Результаты

| Пункт | Изменение / проверка |
|---|---|
| **Д1 — Flesh Bulb** | `FleshBulbBlockEntity` использует накопитель `nextHeartbeatAge`, а не остаток от деления по меняющемуся интервалу. Минимум `MIN_HEARTBEAT_INTERVAL_TICKS = 13`; накопитель назначает следующий старт как `age + max(13, 40 − floor(30 × age / duration))`. Полный проход по age 1…duration−1: duration 1200 — 53 старта, min spacing **13**, max 40; 1500 — 66, min **13**, max 40; 1800 — 80, min **13**, max 40. Ни одного интервала <13. Состояние следующего старта и 3-тикового визуального импульса сохраняется в NBT. `heart_pulse.ogg` не менялся. |
| **Д2 — агония** | `soundDelay = 29 + agonyTicks / 10`; при agonyTicks 1…100 диапазон **29–39 тиков**, всегда >28-тикового файла. `heartbeat_loop.ogg` и `loop=false` не менялись. |
| **Д3 — константа** | Удалена `HEARTBEAT_MAX_SAMPLE_SECONDS`; поиск по пакетным Java/JSON/Markdown-файлам даёт **0** вхождений. |
| **Д4 — иконки** | Побайтовый перенос: `incubating.png` — 320 Б, SHA-256 `e4dd9bd7371995f9833e2ac30af63b09e4282ac35e12e4be4d926ccfef2e43a8`, 18×18; `thermal_shock.png` — 346 Б, SHA-256 `ffb30371f5047a87605f0d1df433df7c8d5450b3f7bcd7ed655b09c9e9023c13`, 18×18. |
| **Д5 — Nexus geo** | Изменение только удалением мёртвых кубов, формы оставлены без изменений. Удалены исходные #4 `/body#1`, #5 `/body#2` (оба полностью внутри `/body#3`) и #11 `/crown#2` (полностью внутри `/crown#3`). Размер геометрии — **21 806 Б** (исходно 26 846 Б). Проверка выполнена утверждённым `02-reviewer/tools/geo_pairs_d5.py`; его дословный вывод приведён ниже: **видимых 0, земля 2, скрыто 1, мёртвых 0**, итог «ПРИЁМКА», код возврата **0**. Необработанные формы и Д6 не менялись. |
| **Д6 — окостеневшая плоть** | Четыре файла взяты побайтово из принятого архива Художника (`Carnis_3.5.3-R_D6_ossified_flesh.zip`, 51 824 Б, SHA-256 `3e46e474eb386dff0c692b39f57f01371557121142fbded8329b6cb1d7fd437a`). PNG SHA-256: `ossified_flesh_0.png` — `0380c2c288f62c9cf8b55808fad36ccda3c41ba798d1289766e4c0a8373116ec`; `_1` — `dcf3a77cdaa45901aefdef58a29fe98277bed12e86d235e522ab8bcdb0ffcb34`; `_2` — `76afe5487bceb7edb701516755d3153fb93db0f4544932262d34159404718451`; `_3` — `cb97a4649746f9fe03d6ba62b43c2e4ff485b6849b5d81855951936869628f23`. `python3 tools/flesh_spread.py` на пакетной папке: **РАЗБРОС = 0.00**, `ИТОГ: СХОДИТСЯ`, code 0. Все шесть различий пикселей ненулевые: **100.00%, 99.98%, 100.00%, 100.00%, 99.98%, 100.00%**. Код `MultifaceSpreader` не менялся. |
| **Д7 — флора** | Добавлены три PNG из принятого архива Художника: `spore_sprout.png` — 254 Б, SHA-256 `c3a2e80c42b0000b64ceeb081b7cb20f802a7b776c9218cebb8285ffbb109346`; `neural_moss.png` — 224 Б, SHA-256 `b18a55b4a996357a891a9b35af4aea9e0f89cd3755d2e9f0ddaf03a63e9a51dd`; `pustule_cluster.png` — 617 Б, SHA-256 `e58a6d7c73a314941eba2421afe4aaa9986deb29e5286e3965d905bd9d04613b`. Размеры 16×16, 16×16 и 64×64; `pustule_cluster_glowmask.png` не менялся. Отчёт Художника: средние L 59,939 / 59,994 / 59,889 %, насыщенность HSL/HSV 0%. |

### Д5 — дословный вывод `02-reviewer/tools/geo_pairs_d5.py`

```text
файл: 01-coder/3.5.3/src/main/resources/assets/carnis/geo/entity/cerebral_nexus.geo.json
кубов 12, костей 6
  /root: 3
  /body: 2
  /core: 2
  /crown: 3
  /tendril_l: 1
  /tendril_r: 1

компланарных пар «в одну сторону» с перекрытием: 3
  | № | пара | грань | плоскость | площадь | закрыто | класс |
  | 1 | #0 /root#0 + #1 /root#1 | Y- | 0 | 8 | не закрыта | земля |
  | 2 | #0 /root#0 + #2 /root#2 | Y- | 0 | 8 | не закрыта | земля |
  | 3 | #3 /body#0 + #5 /core#0 | Y+ | 16 | 5 | закрыта целиком | скрыта |

мёртвых кубов (целиком внутри другого): 0

ИТОГО: видимых 0, земля 2, скрыто 1, мёртвых кубов 0
ИТОГ Д5: ПРИЁМКА (0 видимых, 0 мёртвых)
```

Код возврата скрипта: **0**.

### Д6 — фактический вывод `tools/flesh_spread.py`

```text
ossified_flesh_0.png       средний RGB = ( 89.47,  53.75,  47.43)  непрозрачных px: 4096
ossified_flesh_1.png       средний RGB = ( 89.47,  53.75,  47.43)  непрозрачных px: 4096
ossified_flesh_2.png       средний RGB = ( 89.47,  53.75,  47.43)  непрозрачных px: 4096
ossified_flesh_3.png       средний RGB = ( 89.47,  53.75,  47.43)  непрозрачных px: 4096

пара ossified_flesh_0.png <-> ossified_flesh_1.png:   0.00
пара ossified_flesh_0.png <-> ossified_flesh_2.png:   0.00
пара ossified_flesh_0.png <-> ossified_flesh_3.png:   0.00
пара ossified_flesh_1.png <-> ossified_flesh_2.png:   0.00
пара ossified_flesh_1.png <-> ossified_flesh_3.png:   0.00
пара ossified_flesh_2.png <-> ossified_flesh_3.png:   0.00

SHA-256 01-coder/3.5.3/src/main/resources/assets/carnis/textures/block/ossified_flesh_0.png: 0380c2c288f62c9c
SHA-256 01-coder/3.5.3/src/main/resources/assets/carnis/textures/block/ossified_flesh_1.png: dcf3a77cdaa45901
SHA-256 01-coder/3.5.3/src/main/resources/assets/carnis/textures/block/ossified_flesh_2.png: 76afe5487bceb7ed
SHA-256 01-coder/3.5.3/src/main/resources/assets/carnis/textures/block/ossified_flesh_3.png: cb97a4649746f9fe
различие пикселей ossified_flesh_0.png <-> ossified_flesh_1.png: 100.00 %
различие пикселей ossified_flesh_0.png <-> ossified_flesh_2.png: 99.98 %
различие пикселей ossified_flesh_0.png <-> ossified_flesh_3.png: 100.00 %
различие пикселей ossified_flesh_1.png <-> ossified_flesh_2.png: 100.00 %
различие пикселей ossified_flesh_1.png <-> ossified_flesh_3.png: 99.98 %
различие пикселей ossified_flesh_2.png <-> ossified_flesh_3.png: 100.00 %

РАЗБРОС = 0.00   худшая пара: 
ИТОГ: СХОДИТСЯ
```

## Артефакты пакета

- `project-3.5.3-clean.zip` — 12 294 477 Б, SHA-256 `ba14b913808c5bd12010005aba5ba458d4092124c9e32652cdb70c334daa2557`.
- `project-3.5.3-clean.manifest.txt` — 757 строк, SHA-256 `48d1dce75a00027de6f185455d27aed2615d34a3836c9f49905c762af709f6c0`.
- CI: [прогон #45584880837](https://github.com/BlockBaster3K/carnis-hub/actions/runs/45584880837) для коммита `ba0ceae4763134d3f233ba5093e269a3a599f2fe` — **success**. `Build`, `Verify overlay reached the jar`, публикация JAR — успешно.

## Контроль пакета

- Версия проекта — `3.5.3` в `gradle.properties`, а также в `mods.toml` (`version`, `displayVersion`); настройки Mojmap 1.20.1 и Forge 47.4.28 оставлены без изменений.
- В проектном ZIP **757 файлов** и внешний манифест из **757 строк**; `sha256sum -c` по распакованному пакету — 0 FAILED. Все **258 JSON** разобраны, дублирующихся resource paths нет.
- SHA-256 всех целевых PNG Д4, Д6 и Д7 сверены с исходными архивами; версия 3.5.3 проверена в `gradle.properties` и обоих полях `mods.toml`; `build.gradle` использует `project.property('mod_version')`.
- Локальные Gradle/build-задачи не запускались; CI должен запуститься после push. Сборку и игровое отображение проверяет CI/тестер.
