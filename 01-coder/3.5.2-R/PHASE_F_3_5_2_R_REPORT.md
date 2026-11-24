# Carnis 3.5.2 — отчёт по волне 21 + уточнение волны 22

**Уточнение волны 22:** ZIP пересобран без иных изменений содержимого проекта, кроме обновления четырёх заданных версионных полей и заголовка встроенного path manifest до `3.5.2`. Внешний SHA-256 manifest пересоздан. K4 ресурсы сохранены согласно явному решению координатора.

**Исправление волны 26:** удалён только ручной lifecycle-блок из `HiveEyeBlockEntity.java` — API-вызовы `getGameEventDispatcher/addListener/removeListener` отсутствовали в Mojmap 1.20.1. `GameEventListener.Holder` и `getListener()` оставлены; по проверке координатора регистрация выполняется vanilla через `LevelChunk`. SHA-256 файла: `f355e81b8bcc4965db6a0e58b5bc00d8045fee4b6b1d8095c10fb5ffff8f630d` (38,811 B). ZIP: SHA-256 `f61470442d619ba64dd2958d4d2adf2a9b16abe0fe284f052b47cd27f3e06159`, 12,293,774 B. Файлов — 755, paths неизменны, в манифесте изменилась 1 строка, распакованная проверка — 755/755. Версии остались `3.5.2`.

## 1. Выполнено

| Пункт | Изменение | Файлы / строки после правки |
|---|---|---|
| K-21-1 | Введён общий `ScytheItem`: костяная коса — `STONE/2/−2.4F`, pitch/volume `1.15/0.8`; оссифицированная — `IRON/5/−2.4F`, `1/1`. Удар использует прежнее `OSSIFIED_SCYTHE_HIT`, tooltip остаётся только у оссифицированной. Swing/hit работают только на сервере для entity/block; `LeftClickEmpty` использует только локальный звук клиента. | `ModItems.java:153–160`; `ScytheItem.java:17–49`; `CombatItemEvents.java:22–45`. Старый `OssifiedScytheItem.java` заменён новым общим классом. Имена sound events, `sounds.json` и OGG не менялись. |
| K-21-2 | Интервал стал линейным **34–46 тиков** (`46 − round(proximity × 12)`), минимум 1.7 s. Добавлены требуемые границы и предел сэмпла 1.5 s. Громкость и одноразовый `pulsing_heart_beat` не менялись. | `HeartAmbientTicker.java:13–15, 25–31`. |
| K-21-3 | Nexus и Sentinel получили только `HurtByTargetGoal` и ответный урон в пределах 8 блоков; Nexus — 2 урона/40 тиков и лёгкий knockback, Sentinel — 1 урон, Confusion 60 тиков/кулдаун 60. У Tendril добавлен `HurtByTargetGoal` priority 2; его eligibility-фильтр не менялся. | `CerebralNexusEntity.java:34–51`; `HiveSentinelEntity.java:48–78`; `ParasiticTendrilEntity.java:43–46`. Скорость 0 и обнуление движения сохранены. |
| K-21-4 | Glow pass масштабируется `1.002F` вокруг `super.render`, `popPose` гарантирован через `finally`. | `OptionalGlowLayer.java:62–71`. |
| K-21-5 | Свет `PULSING_HEART` снижен с 9 до 3; `HIVE_EYE` больше не задаёт emission. Другие источники света не менялись. Известное следствие: в улье может возобновиться спавн мобов при слабом свете сердца. | `ModBlocks.java:112–129`. |
| K-21-6 | Добавлены server config `flora_chance_percent=0.8` (0–100), `flora_local_cap=3` (1–16), `moss_spread_percent=3` (0–100), с английскими комментариями. Рост флоры на живой плоти использует шанс и предел в кубе ±3; распространение мха использует свой шанс и требует опору из четырёх заданных видов плоти. | `CarnisConfig.java:32–34, 80–94`; `FleshBlock.java:57–106`; `NeuralMossBlock.java:43–56`. `hasSuitableEnvironment`, `canSurvive`, партиклы, замедление, `MaggotForaging` и `VeinMutationEngine` сохранены без изменений. |
| K1 | Выбран один источник block-tag JSON: `src/main/resources`. Семь ранее generated block-tag JSON перенесены в main; `ModBlockTagsProvider.addTags` оставлен намеренно пустым, чтобы `runData` не создавал копии. `hive_blocks` остаётся в main. | `ModBlockTagsProvider.java:21–24`; десять block-tag JSON в main, ноль в generated. |
| K2 | Hand-authored item-модели `nerve_pillar` и `stomach_pool` уже содержали нужные `display` transforms; оставлены без изменения. Из datagen убраны их генераторные записи, которые затёрли бы transforms. Для spawn egg provider теперь задаёт vanilla `template_spawn_egg`, а не несуществующую текстуру. Существующий generated JSON яйца уже использует этот parent. | `ModItemModelProvider.java:20–23, 44–46`; item-модели main не изменены. |
| K3 | Удалено повторное создание `HIVE_BLOCKS`; runtime-вызовы используют единственный `ModBlockTags.HIVE_BLOCKS`. | Единственное объявление: `ModBlockTags.java:10`; использования `HiveGrowthSuppression.java:23`, `HiveAttackEvents.java:25`. |
| K6 | Ручную регистрацию listener не оставлять: `GameEventListener.Holder` и `getListener()` сохранены, а vanilla `LevelChunk` автоматически регистрирует/снимает listener. | `HiveEyeBlockEntity.java:144–147`; в волне 26 удалён несуществующий Mojmap API-блок. |

## 2. Решения и отличия от исходного текста

- Для K1 выбрана схема **main-only**, а не generated-only: provider не пишет эти теги, поэтому последующий datagen не создаст конкурирующие версии.
- Item JSON для `nerve_pillar`, `stomach_pool` и spawn egg не переписывались: transforms и template-parent уже были корректны. Исправлен источник будущего неверного datagen output.
- `SYNAPSE_NODE` сохранён с R5 исправлением, `POWER > 0 → 15`; `PURIFIER_LAMP` и `INCUBATION_CYST` не менялись.
- По уточнению волны 22 версия обновлена внутри ZIP: `gradle.properties` (`mod_version`), `mods.toml` (`version`, `displayVersion`) и комментарий `build.gradle` теперь указывают `3.5.2`. Заголовок встроенного path manifest также обновлён. Код и ресурсы для этого не менялись.

## 3. Не сделано / отложено

- **K4:** `bio_purifier_geo.png` и `pulsing_heart_geometry.json` оставлены по явному решению координатора; возврат к ним — в 3.6.0.
- Варианты `creeping_tendrils` (K5 backlog) не входят в перечисленный scope этой волны и не менялись.
- Версию мода обновил по уточнению волны 22; сборочные проверки остаются за Интегратором.

## 4. Статические проверки поставки

- ZIP: **755 файлов**, ZIP paths уникальны.
- Manifest: **755 SHA-256 записей**; проверка после распаковки — **755/755 OK**.
- JSON: **258** файлов успешно разобраны.
- Дубли resource paths между main/generated: **0**.
- Block-tag JSON: **10 в main, 0 в generated**; `hive_blocks` имеет один TagKey declaration.
- Java: **228** файлов. Число файлов сохранено заменой старого scythe-класса новым.
- K4 ресурсы присутствуют, но не имеют ссылок из Java/JSON (кроме path inventory `MANIFEST.txt`).
- Все четыре указанных version fields — `3.5.2`; версионное имя в `MANIFEST.txt` тоже обновлено. Gradle/build, runtime и `runData` не запускались.

## 5. Что не проверено

- CI Build ранее упал на добавленном `Level#getGameEventDispatcher`; ручные вызовы удалены. После этого исправления повторный Build не запускался, поэтому новая сборка ещё не подтверждена.
- Не запускалась игра: фактическая слышимость кос, паузы heartbeat, ответ мобов, рендер glow pass и поведение конфигурируемой флоры требуют теста в игре.
- K4: наличие будущего плана подключения двух неиспользуемых ресурсов может подтвердить только владелец.

Поставка — `project-3.5.2-clean.zip` + SHA-256 manifest. Изменения ограничены указанными дефектами и вспомогательными корректировками datagen.

**Волна 26 — commit:** не создан и не отправлен. В рабочем пространстве нет git checkout, а GitHub connector для этой сессии недоступен; ветка `arena/d474d740-carnis-hub` не затрагивалась. Commit hash отсутствует.
