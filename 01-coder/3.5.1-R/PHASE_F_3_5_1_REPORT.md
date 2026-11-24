# PHASE F — Carnis 3.5.1: фикс провайдеров и очистка

## Остаточный фикс

Удалены три неиспользуемых Java-провайдера, способных перезаписать принятые текстуры:

- `CountermeasureItemTextureProvider.java`
- `OrganicItemTextureProvider.java`
- `ModEntityTextureProvider.java`

Файлов нет, ссылок в `src/` — 0. Они не были зарегистрированы. `DataGenerators` сохраняет только три необходимые регистрации: blockstate, itemmodel и blocktags.

## Пакет и статические проверки

- Удаление трёх классов уменьшило архив **759 → 756 файлов**.
- Java-файлов и заголовков в dump: **228**, все уникальны; дубликатов заголовков и удалённых файлов нет.
- `project-3.5.1-clean.manifest.txt`: 756 SHA256-записей, формат `sha256sum`; проверка после распаковки прошла 756/756.
- ZIP цел, повторов путей нет. Состав: 228 Java, 145 OGG и остальные необходимые ресурсы; корневой allowlist прежний.
- 80 `sounds.json` событий, 141 ссылки на Carnis-сэмплы, 0 отсутствующих; 145 OGG (142 банковских + `heart_pulse` + два legacy).
- 19 предметных PNG по манифестам p1/p2/p3 проверены как 64×64; item model hashes без изменений. Три spawn-egg base tint — `0xFFFFFF`.
- Девять целевых текстурных путей не имеют конфликтов между `main` и `generated`. Координатор подтвердил, что отсутствие `item/pneumatic_inoculator.png` и `item/flesh_amalgam_spawn_egg.png` — предсуществующее и допустимое; placeholders не создавались. Координатор также подтвердил арифметику партий: 7+8+4 = 19 PNG, не 20.
- Версия 3.5.1 остаётся в `gradle.properties` и `mods.toml` (`version`, `displayVersion`); `${file.jarVersion}` отсутствует.
- **Сборка не запускалась — запрет заказчика.** Gradle/datagen/runtime не запускались.

## Workspace

Сохраняется только этот набор из четырёх артефактов. `du -sh` до исходной чистки: **42M**; после неё: **13M** (запас до 25M — около 12M). Суммарный apparent size четырёх файлов около 13.2 MB; дамп не выносился отдельно.

```
01-coder/3.5.1/project-3.5.1-clean.zip
01-coder/3.5.1/project-3.5.1-clean.manifest.txt
01-coder/3.5.1/PHASE_F_3_5_1_FULL_JAVA_DUMP.md
01-coder/3.5.1/PHASE_F_3_5_1_REPORT.md
```

## Deliverables

- `project-3.5.1-clean.zip`
- `project-3.5.1-clean.manifest.txt`
- `PHASE_F_3_5_1_FULL_JAVA_DUMP.md`
- `PHASE_F_3_5_1_REPORT.md`
