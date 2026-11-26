# Кодер — S112: пересборка 3.7.3 с `hive.spawn_idle` volume 2.263

**Основание:** `00-board/reports/sound_t3180_closure.md` §3, `00-board/reports/integrator_s100_not_in_package.md` и `00-board/reports/reviewer_volume_key_verified.md`.

## Артефакты

Канонические пути ZIP и manifest теперь указывают на пересобранный пакет:

- ZIP: `01-coder/3.7.3/project-3.7.3-clean.zip`
- SHA-256: `a0a48ae598ad3ae4d451430dbfc59401f850359bdde6c11b8b1bed1aa7a8dbe8`
- Manifest: `01-coder/3.7.3/project-3.7.3-clean.manifest.txt`
- SHA-256 manifest: `56e866d62cff9b592bedff74b2a40cfb89e3b97745356a9a20810ea48db4c8dd`
- Состав: **761 уникальная запись, 144 OGG**.
- В `hive.spawn_idle[0]` задан `volume: 2.263`, как в S100. ZIP отличается от предыдущего стандартного пакета только одним содержимым — `sounds.json`; список путей совпадает.
- В `hive.detail_flow[0]` оставлен `volume: 1.0`; спорное значение не менял. В рабочем дереве есть отдельная незакоммиченная правка `2.437`, но в этот пакет она не включена. Требуется отдельное решение Архитектора по семантике/значению `detail_flow`.
- Прежний ZIP и manifest сохранены побайтно: `project-3.7.3-clean-pre-s112.zip` (SHA `c7d782544708de4d5c48e55211d4bf3c4fcb3f2a681a3453d25c012688e5000c`) и `project-3.7.3-clean-pre-s112.manifest.txt`.
- Отдельная копия того же нового кандидата остаётся по имени `project-3.7.3-s112-spawn-idle-2.263-candidate.zip`.

## Проверки

- `unzip -tq`: успешно.
- Manifest проверен по распакованному ZIP: **761/761 OK**.
- `tools/sounds_coverage_check.py` на ZIP и его распакованной копии: **код 0**, 82 события, 144 OGG, 145 ссылок, 0 сирот, 0 битых ссылок.
- `tools/volume_effective_check.py --pkg <ZIP> --spec 03-sound/spec/volume_spec_t3202.json`: **код 2**, 1 из 10 вне допуска — только `hive.detail_flow`; `hive.spawn_idle` с 2.263 проходит.
- `tools/accept_3.7.3.py <ZIP>`: **код 1**, полный acceptance не подтверждён в sparse checkout: отсутствуют независимые baseline/overlay/crest/timbre inputs, канонический банк/manifest и декодер `av+numpy`. Это не приёмка.
- `.jar` не собирался; Java-компиляция не запускалась.

## Статус

Пересборка по S112 выполнена. Новый SHA **не наследует** verdict предыдущего ZIP; независимые review/acceptance должны проверять именно `a0a48ae5…`. До этого пакет не объявляется принятым релизом. Не менять `detail_flow` без решения Архитектора.
