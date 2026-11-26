# PHASE F — Carnis 3.5.1: отчёт и workspace cleanup

## Выполнено

- Версия `3.5.1` стоит в `gradle.properties`, `mods.toml` (`version` и `displayVersion`); `build.gradle` читает Gradle-свойство. `${file.jarVersion}` отсутствует.
- Два звуковых события уже ссылались на `_01`-носители в исходном дереве 3.5.0; ссылки не менял, файлы `_01` присутствуют. Legacy `entity/flesh_amalgam_death.ogg` и `entity/flesh_amalgam_hurt.ogg` сохранены.
- Взяты artist-партии p1, p2 и p3 из `BlockBaster3K/carnis-hub` (commit `faf461eefe057143cd8cd446a84f72d143d78139`). Проверены SHA изображений и хеши существующих item-моделей. Принято **19 PNG** по точным партиям 7 + 8 + 4; формулировка «20» расходится с перечислением/manifest партиям (19). Все 19 изображений 64×64; магенты нет. Блочные art PNG не добавлялись.
- Для трёх artist spawn eggs (`parasitic_tendril`, `hive_sentinel`, `cerebral_nexus`) первый цветовой аргумент изменён на `0xFFFFFF`; вторичные цвета сохранены.
- Удалён `CarnisTextureDataGen.java` и его регистрация. `DataGenerators` оставляет три других провайдера: block states, item models, block tags. Ссылок на удалённый класс в Java: 0.
- Арт `purification_serum` из p3 помещён в `src/main`; прежняя копия в `src/generated` удалена. По всем девяти перечисленным datagen-путям конфликтов main/generated нет.

## Важное статическое замечание по девяти texture paths

В дереве найдены семь путей с ровно одной копией: ``block/creeping_tendrils`, `item/viral_dart`, `item/purification_dart`, `item/purification_serum`, `item/neural_binding_matrix`, `item/creeping_tendrils`, `item/tainted_sludge_bucket``. Два пути отсутствуют одновременно в `src/main/resources` и `src/generated/resources`: `item/pneumatic_inoculator` и `item/flesh_amalgam_spawn_egg`. Генератор их раньше создавал только при datagen; готовых PNG в переданном чистом дереве/репозитории нет. По прямому указанию «не генерировать заново» я не создавал placeholders и не копировал чужие иконки. Итого дубликатов нет, но требование «ровно одна копия» для этих двух отсутствующих файлов проверить как выполненное нельзя; это отражено, а не скрыто.

## Статические проверки

- JSON: 259 файлов успешно разобраны.
- `en_us` / `ru_ru`: 341/341 ключ, parity соблюдён.
- Блоки: 21; предметы: 50; рецепты: 41; advancement: 6.
- 145 OGG: 142 из банка (SHA256 142/142) + 3 сохранённых проектных файла. `archive/**` и банковский `block/heart_pulse.ogg` не копировались. 80 звуковых событий, 141 ссылок на Carnis-сэмплы, 0 ссылок «в никуда».
- 19/19 art PNG валидны и 64×64; model hashes совпадают с пакетными manifests.
- ZIP: 759 уникальных файлов; корень содержит только `src/`, `build.gradle`, `gradle.properties`, `settings.gradle`, `MANIFEST.txt`. Внутри 231 Java и 145 OGG; повторов путей нет. Внешний SHA256-манифест содержит строку на каждый member ZIP.
- Java dump: 231 уникальная секция, по одному заголовку на актуальный Java-файл; `CarnisTextureDataGen` и удалённые файлы отсутствуют.
- **Сборка не запускалась — запрет заказчика.** Gradle/JDK/datagen/runtime не запускались; компилируемость требует GitHub Actions.



## Очистка workspace

`du -sh` до чистки: **42M**; после чистки: **13M**. Итоговый размер — **13M**, запас до жёсткого потолка 25M — около **12M** (и до внутренней отметки 20M — около 7M). Суммарный apparent size четырёх файлов — около 13.2 MB, поэтому архив не резался и Java dump не выносился отдельно.

Полный остаток workspace (4 файла):

```
/home/user/                                      13M
└── 01-coder/                                    13M
    └── 3.5.1/                                   13M
        ├── project-3.5.1-clean.zip              12128600 B
        ├── project-3.5.1-clean.manifest.txt     100728 B
        ├── PHASE_F_3_5_1_FULL_JAVA_DUMP.md      926187 B
        └── PHASE_F_3_5_1_REPORT.md              5667 B
```

Archive integrity: 759/759 members; checksum verification by `sha256sum -c project-3.5.1-clean.manifest.txt` passed 759/759. В workspace не оставлены старые проекты, архивы, кэши, source inputs или иные файлы.
