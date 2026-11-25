# Кодер · 3.5.3 — исправление R1 (два звуковых файла)

**Ветка:** `arena/d474d740-carnis-hub`  
**Изменённая область:** только два файла OGG в пакете, ZIP и внешний SHA-256-манифест. D1–D4, Д2-код, Д5, Д6, Д7 и R2 не менялись.

## Замена R1 — побайтовая проверка

| Исходник в банке | Целевой путь в проекте | Размер | SHA-256 банка | `cmp` |
|---|---|---:|---|---|
| `03-sound/sounds/block/heart_pulse.ogg` | `01-coder/3.5.3/src/main/resources/assets/carnis/sounds/block/heart_pulse.ogg` | 10 926 Б | `17f42e3076ee1d0bc8212ea4d817d43ac3e78ebbee8d6c7544e87b4832f7e905` | совпадает побайтово |
| `03-sound/sounds/block/heartbeat_loop.ogg` | `01-coder/3.5.3/src/main/resources/assets/carnis/sounds/block/heartbeat_loop.ogg` | 19 819 Б | `39de4db0d9938af9dba8b1f6b637988003410dd7daf85b17df8284c49a513079` | совпадает побайтово |

Файлы скопированы без перекодирования/пересохранения. `cmp -s` вернул 0 для обеих пар; размер и SHA-256 целевых файлов совпали с банком.

## Пересобранные артефакты

- `01-coder/3.5.3/project-3.5.3-clean.zip` — **12 285 744 Б**, SHA-256 `e50c96945aaa8bf5d0cd22332186f319fe21ce8557a1e6a65150b4056f17baaf`.
- `01-coder/3.5.3/project-3.5.3-clean.manifest.txt` — **757 строк**, SHA-256 `4693377546c43ec7031459757c52522e0d216fbf51ed588c24dcd08aa9235fd6`.
- `sha256sum -c project-3.5.3-clean.manifest.txt`: **757 OK, 0 FAILED**.
- ZIP CRC/inventory: 757 members, дубликатов путей 0, внутренний `MANIFEST.txt` совпадает со списком ZIP.
- Проверки ресурсов: **258 JSON** разобраны успешно; дублирующихся resource paths — **0**.
- Проверены версии проекта `3.5.3`; D2 код и все прочие исходники/ресурсы, кроме двух целевых OGG, оставлены без изменений.

## Что осталось непроверенным

- Локальная Gradle-сборка не запускалась; проверку JAR выполняет GitHub Actions после push.
- Рантайм-прослушивание заменённых файлов в Minecraft не выполнялось.
- R2 — бессуффиксные `entity/flesh_amalgam_death.ogg` и `entity/flesh_amalgam_hurt.ogg` — не удалялись и не менялись.
- CI: ожидается запуск после push; ссылку и итог добавлю после завершения прогона.
