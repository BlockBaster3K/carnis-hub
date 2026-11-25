# Кодер — пересдача 3.6.0-R (K5)

**Основа:** принятый пакет `01-coder/3.6.0/project-3.6.0-clean.zip`. Каталог `01-coder/3.6.0/` не изменялся; SHA-256 его ZIP остался `e1d80864d2e0f72c24df18f99eb03197f136c936c8790507eae4b316704338b1`.

## Принятая графика — побайтовое копирование

Источник: `04-artist/deliverables/Carnis_3.7.0-A3A6_tendrils.zip`, SHA-256 `4882329f5d8d2ff89877dcefc80654e0a44f383d0518c64f883e145bf568aa1d`. Архив содержит четыре PNG и контрольные суммы. Каждый файл сверил через `cmp`; повторного кодирования/сохранения не было. Все четыре — 64×64 RGBA, 8 уникальных RGBA значений (7 непрозрачных + прозрачный), альфа только 0/255.

| Источник | Путь в пакете | SHA-256 |
|---|---|---|
| `creeping_tendrils_0.png` | `src/main/resources/assets/carnis/textures/block/creeping_tendrils_0.png` | `9c0aa4f89bc1c3768cbe5632186846c64cd6dfc7c1f6639fe43961f595ed8e86` |
| `creeping_tendrils_1.png` | `src/main/resources/assets/carnis/textures/block/creeping_tendrils_1.png` | `05307a3355c35e3f720d210724290aa14801503bc3be58339fbe82a596c42362` |
| `creeping_tendrils_2.png` | `src/main/resources/assets/carnis/textures/block/creeping_tendrils_2.png` | `bc98d73ee9444a9bf710d85f6ba7f3d13b36b3cb4f9acd21222058f0b3eb98fd` |
| `creeping_tendrils_3.png` | `src/main/resources/assets/carnis/textures/block/creeping_tendrils_3.png` | `3d0a56bf8848c1ca52d5d5500150eee4f60818e277dd20d0250634d5337623` |

## Модели, blockstates и код

- Созданы `models/block/creeping_tendrils_0.json` … `_3.json`: у каждой модели `parent: minecraft:block/ladder`, `render_type: minecraft:cutout`, текстура `carnis:block/creeping_tendrils_<i>`.
- `blockstates/creeping_tendrils.json`: **16/16** сочетаний `facing` × `variant`. Каждое `variant=0…3` выбирает соответствующую модель; поворот зависит только от facing: north=0°, east=90°, south=180°, west=270°.
- В `CreepingTendrilsBlock` добавлено `IntegerProperty VARIANT` диапазона 0–3, default 0. `FACING` не переобъявлялся: сохраняется унаследованное свойство `LadderBlock`.
- Взвешенный выбор делается только при размещении (`getStateForPlacement`) через `context.getLevel().random`. Константные веса вариантов 0–3: **4:3:2:1**, сумма 10, то есть 40%/30%/20%/10%. Проверка перебора 10 исходов дала соответственно 4/3/2/1; иных точек рандомизации варианта в коде нет.
- `ModBlockStateProvider` приведён к тем же четырём моделям, facing-поворотам и persistent-свойству `variant`.
- Прежний `textures/block/creeping_tendrils.png` (16×16) удалён: после обновления моделей и datagen provider ссылок на него в Java-коде и моделях не осталось. Отдельная текстура предмета `textures/item/creeping_tendrils.png` сохранена.

## Состав и целостность пакета

Путь: `01-coder/3.6.0-R/` — полный исходный проект, `build.gradle`, `settings.gradle`, `gradle.properties`, `MANIFEST.txt`, ZIP и внешний манифест. `mod_version=3.6.0`, оба поля в `mods.toml` — `3.6.0`; `archives_base_name=carnis`.

- ZIP `project-3.6.0-R-clean.zip`: **12 309 048 Б**, SHA-256 `93e258d72ee8ad665ab13f2f2257510362e5e04fd8a2eb92b14b59e740bc03ff`.
- Внешний манифест `project-3.6.0-R-clean.manifest.txt`: **763 строки**, SHA-256 `4cf54657079a9c5d48fd5af7c065ff839ae86b4b1571891ee5f34bd26f29fe6b`.
- В ZIP **763 файла**, дубликатов путей нет, CRC без ошибок; `sha256sum -c`: **763 OK, 0 FAILED**. Все **260 JSON** разбираются.
- Сравнение с пакетом 3.6.0: K5 добавил 4 PNG и 4 модели, убрал старую одиночную модель и более не используемую block-текстуру. Исходный пакет 3.6.0 не менялся.

## Проверки и ограничения

- Официальный `tools/accept_3.6.0.py ZIP MANIFEST`: **ИТОГ: ПРИНЯТО**; манифест 763/763, JSON 260/260, версии 4/4, overlay 2/2, K4 и K6-S на месте, K5 — 16 вариантов и правильный facing/y/ladder parent.
- `02-reviewer/tools/delta_360.py` подтвердил манифест, версии, K4, 16 вариантов, 4 модели, K6-S и неизменность файлов Д1–Д7, но завершился кодом 2 на последней проверке «K4 — ровно два удаления». Причина — этот gate сравнивает с 3.5.3 и считает также две намеренные K5-замены (старые одиночная модель и block-текстура) как дополнительные удаления. K5-дельта относительно принятого 3.6.0: ровно 2 удаления и 8 добавлений, перечисленные выше; скрипт для повторной папки `3.6.0-R` не адаптирован.
- Локальный Gradle build не запускался по требованию; CI для новой пересдачи ожидает push.
- Игровая установка блока, сохранение варианта в мире и визуальный рендер не проверялись в Minecraft.
