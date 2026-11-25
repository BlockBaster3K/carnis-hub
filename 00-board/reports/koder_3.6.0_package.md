# Кодер — пакет 3.6.0 (K4 + K6-S)

**Основа:** принятый пакет `01-coder/3.5.3/project-3.5.3-clean.zip`  
**Объём:** только K4 и K6-S по заданию. K5, A2, A4, Д2 и рефакторинг не выполнялись. `06-build/overlay.txt` не менялся (зона Интегратора).

## K4 — удалённые мёртвые ресурсы

Хеши и размеры взяты из базового ZIP 3.5.3; перед удалением проверены ссылки в `src/`.

| Удалённый путь | До удаления | SHA-256 до удаления | Ссылок в `src/` после |
|---|---:|---|---:|
| `src/main/resources/assets/carnis/textures/item/bio_purifier_geo.png` | 1 013 Б | `2c7d8884911c1a96bd56bf01b349ed30eb38974c1c02b20f5954190a4dcbd337` | 0 |
| `src/main/resources/assets/carnis/models/item/pulsing_heart_geometry.json` | 4 786 Б | `fbd5a4242f354308f4c2214c66fa9336bf3b336909804ecf73825576634ce1c1` | 0 |

`grep` по обоим именам в `src/` — **0 совпадений**; `find` по обоим путям — **пусто**. Сравнение ZIP 3.6.0 с ZIP 3.5.3: удалены ровно эти два файла, других удалений нет.

## K6-S — костяная коса

- Добавлены `item.bone_scythe.swing` и `item.bone_scythe.hit` в `src/main/resources/assets/carnis/sounds.json`; число событий **80 → 82**. Для каждого указан `stream: false`; `pitch` и `volume` не заданы.
- В `ModSounds` добавлены `BONE_SCYTHE_SWING` и `BONE_SCYTHE_HIT`.
- `ScytheItem` теперь хранит `hitSound` и `swingSound` (`SoundEvent`) и предоставляет геттеры. `hurtEnemy()` воспроизводит `hitSound`; оба пути замаха в `CombatItemEvents` используют `getSwingSound()`.
- `ModItems`: костяная коса получает bone-события, окостенелая — прежние ossified-события; исходные pitch/volume сохранены.
- Добавлены сабтайтлы в обе локали (`en_us`, `ru_ru`).
- Побайтово скопированы аудиофайлы из банка в ресурсы проекта:

| Источник | Путь в проекте | Размер | SHA-256 |
|---|---|---:|---|
| `03-sound/sounds/combat/bone_scythe_swing_01.ogg` | `src/main/resources/assets/carnis/sounds/combat/bone_scythe_swing_01.ogg` | 11 167 Б | `11cbb014d7dfb63b723c50183924f0251e2f8a1b355805f38589b180630f28fa` |
| `03-sound/sounds/combat/bone_scythe_hit_01.ogg` | `src/main/resources/assets/carnis/sounds/combat/bone_scythe_hit_01.ogg` | 7 458 Б | `b0f6504a97bf8739cd972c16d245665795a24ab4ab71ed3253de49694c411722` |

Проверки исходников: `OSSIFIED_SCYTHE_HIT` в `ScytheItem.java` — **0**; `OSSIFIED_SCYTHE_SWING` в `CombatItemEvents.java` — **0**. В архиве относительно 3.5.3 добавлены только два новых OGG-пути; звуковые файлы сверены с SHA-256 банка.

## Версия и пакет

- `gradle.properties`: `mod_version=3.6.0`; `archives_base_name=carnis` сохранён.
- `META-INF/mods.toml`: `version="3.6.0"` и `displayVersion="3.6.0"`.
- ZIP: `01-coder/3.6.0/project-3.6.0-clean.zip` — **12 300 995 Б**, SHA-256 `e1d80864d2e0f72c24df18f99eb03197f136c936c8790507eae4b316704338b1`.
- Внешний манифест: `01-coder/3.6.0/project-3.6.0-clean.manifest.txt` — **757 строк**, SHA-256 `fdb2453314dee21c7f0b64568d46d7064a75922c13e8b3b78a3d2a3756516c5f`.
- ZIP: **757 файлов**, дублирующихся путей нет, CRC успешен. `sha256sum -c`: **757 OK, 0 FAILED**.
- Все **257 JSON** в `src/` разбираются успешно.
- Между ZIP 3.5.3 и 3.6.0: **2 удаления K4**, **2 добавления OGG K6-S**; остальные изменения — только поля/вызовы K6-S, события, локали и версии, перечисленные выше.

## CI, JAR и оставшиеся непроверенные пункты

- Пакет отправлен в коммите `13ab1db` (`[coder] 3.6.0: K4 + K6-S`) в ветку `arena/d474d740-carnis-hub`.
- GitHub Actions [run #45601064084](https://github.com/BlockBaster3K/carnis-hub/actions/runs/45601064084) для `13ab1db` завершился **success**: `Build`, `Verify overlay reached the jar`, загрузка JAR, коммит JAR в `main` и публикация релиза успешны.
- Итоговый `carnis-3.6.0.jar` (в `main`: `06-build/jars/carnis-3.6.0.jar`) проверен: ZIP CRC без ошибок; внутри есть оба `assets/carnis/sounds/combat/bone_scythe_{hit,swing}_01.ogg`; в `mods.toml` `version="3.6.0"` и `displayVersion="3.6.0"`. SHA-256 JAR: `0f4c44ddda467d76455f05895f626cb198c81af7ae72fea6f26f42d2aa26a547`.
- Локальный Gradle build не запускался по требованию.
- Игровое воспроизведение новых звуков не проверялось.
- `06-build/overlay.txt` не менялся; две новые звуковые записи и файлы лежат в ресурсах пакета. CI-сборка и проверка overlay успешны; оба OGG дополнительно найдены в JAR.
