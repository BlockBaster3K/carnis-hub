# PHASE F — Carnis 3.5.1: tag fix и отчёт

## Сделано

- Удалён устаревший дубль `src/generated/resources/data/carnis/tags/blocks/hive_blocks.json`; файл в `src/main/resources` оставлен, код `ModBlockTagsProvider` не менялся.
- Дубль `hive_blocks` удалён, сплошных дублей main↔generated — **0** (полный проход по всем ресурсным путям).
- Сверены восемь block-tag наборов с `ModBlockTagsProvider.addTags`. При проверке обнаружено дополнительное расхождение: generated `infectious_surfaces.json` содержал 8 значений при 11 в провайдере. JSON обновлён до 11 значений; провайдер не менялся. Остальные теги содержат все значения провайдера.
  Состав provider/file: `hive_blocks` 21/21; `carnis_blocks` 20/20; `infectious_surfaces` 11/11; `mineable/hoe` 8/8, `axe` 2/2, `pickaxe` 7/7; `needs_stone_tool` 1/1; `needs_iron_tool` 1/1.
- Удалённый в предыдущем фиксе процедурный `CarnisTextureDataGen` и три dormant texture providers отсутствуют; ссылок на них 0. `DataGenerators` сохраняет три действующих провайдера.

## Статические проверки и пакет

- Число файлов: **756 → 755**. В ZIP 228 Java-файлов и 145 OGG; архив без дублирующихся путей.
- Дамп пересоздан из чистого дерева: 228 уникальных заголовков, удалённых/повторных секций нет.
- Внешний manifest: 755 строк `sha256sum`; после распаковки проверка прошла **755/755**.
- JSON: 258 корректных; локали 341/341; блоки 21, предметы 50, рецепты 41, advancements 6.
- 80 звуковых событий; звуковая проверка 145 OGG сохранена. Текстуры и модели этого шага не менялись.
- **Сборка не запускалась — запрет заказчика.** Gradle/datagen/runtime не выполнялись.

## Workspace

`du -sh` до этой чистки: **13M**; после: **13M**. Остаются ровно четыре файла:

```
01-coder/3.5.1/project-3.5.1-clean.zip                 12119869 B
01-coder/3.5.1/project-3.5.1-clean.manifest.txt        100187 B
01-coder/3.5.1/PHASE_F_3_5_1_FULL_JAVA_DUMP.md         895687 B
01-coder/3.5.1/PHASE_F_3_5_1_REPORT.md                 2917 B
```

Запас до потолка 25M — около 12M. Старые проекты, исходные staging-файлы, логи и кэши не оставлены.
