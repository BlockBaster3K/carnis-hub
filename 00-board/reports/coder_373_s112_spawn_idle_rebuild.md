# Кодер — S112: отдельный ZIP-кандидат с `hive.spawn_idle` volume 2.263

**Основание:** `00-board/reports/sound_t3180_closure.md` §3 и решение/проверка S100 в `00-board/reports/integrator_s100_not_in_package.md` и `00-board/reports/reviewer_volume_key_verified.md`.

## Что сделано

Создан отдельный ZIP-кандидат из дерева проекта 3.7.3 на базе HEAD `6f74940`:

- ZIP: `01-coder/3.7.3/project-3.7.3-s112-spawn-idle-2.263-candidate.zip`
- SHA-256 ZIP: `a0a48ae598ad3ae4d451430dbfc59401f850359bdde6c11b8b1bed1aa7a8dbe8`
- Manifest: `01-coder/3.7.3/project-3.7.3-s112-spawn-idle-2.263-candidate.manifest.txt`
- SHA-256 manifest: `56e866d62cff9b592bedff74b2a40cfb89e3b97745356a9a20810ea48db4c8dd`
- В архиве **761 уникальный файл**, включая **144 OGG**. По сравнению с прежним `project-3.7.3-clean.zip` изменилось содержимое ровно одного элемента: `src/main/resources/assets/carnis/sounds.json`; список путей тот же.
- В `hive.spawn_idle[0]` теперь `volume: 2.263`; `hive.detail_flow[0]` оставлен `1.0` — неподтверждённый кандидат `2.437` в этот архив не включался. Source SHA внутри архива: `14c5d0dc2a6cc9f7b02f9130ab04d8f8ac919efa210fce35196b8534a5df6378`.
- Прежний официальный `project-3.7.3-clean.zip` и отдельный `2.437` кандидат не перезаписаны. Приёмка и статус предыдущего ZIP на этот SHA не переносятся.

## Проверки

- `unzip -tq`: успешно.
- Внешний manifest сверил на распакованном кандидате: **761/761 OK**.
- `tools/sounds_coverage_check.py` на кандидате и его распакованной копии: **код 0**, 82 события, 144 OGG, 145 ссылок, 0 сирот и 0 битых ссылок.
- `tools/volume_effective_check.py --pkg <кандидат> --spec 03-sound/spec/volume_spec_t3202.json`: **код 2**, `1 из 10` вне допуска — только `hive.detail_flow`, поскольку в упакованной версии `volume 1.0` при цели 0.731. `hive.spawn_idle` с 2.263 проходит. Семантику/значение `detail_flow` самостоятельно не менял.
- `tools/accept_3.7.3.py <кандидат>`: **код 1**, 11 замечаний/непроверенных условий в неполном sparse checkout. В частности, отсутствуют независимый baseline 3.7.2, overlay/crest/timbre inputs, канонический банк/manifest и декодер `av+numpy`; это не полная приёмка.
- `.jar` не собирался; Java-компиляция не запускалась.

## Передача

Кандидат готов для независимого review по S112. До нового вердикта Интегратора/Ревизора он не объявляется принятым релизом и не заменяет permanent ZIP. Не менять и не публиковать `detail_flow=2.437` без отдельного решения Архитектора.
