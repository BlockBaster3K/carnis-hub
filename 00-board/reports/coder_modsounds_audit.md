# Кодер · T-3184 — аудит и привязка 11 недостижимых ModSounds

**Состояние после upstream sync `225a750`, fix `7b9655f` и API review:** исходниковый `sound_orphans.py` код 0; 9 игровых событий привязаны, `FLESH_AMALGAM_AMBIENT` покрывается через `hive.amalgam_breath`, `FLAMETHROWER_FIRE` — разрешённый задел. Точка `CREEPER_RUPTURE` перенесена с невозможного override private-метода на существующий серверный `ExplosionEvent.Detonate` hook. Свежий ZIP/gate и Java compile после этого изменения не выполнялись; принятие пакета не заявляю. Старые ниже приведённые статусы сохранены как история.

Карта Sound S17: `sound_unreachable_map.md` (база `243e598`).

## Реализации по карте Sound

| Событие | Реальный вызов (путь:строка) | Параметры / статус |
|---|---|---|
| `AMALGAM_SMASH` | `entity/FleshAmalgamEntity.java:302`, `doHurtTarget` после успешного melee-hit | HOSTILE, volume/pitch 1.0; позиция амальгамы |
| `SYNAPSE_SHOCK` | `block/SynapseNodeBlock.java:69`, `tick`, после изменения POWER, если новое значение > 0 | BLOCKS, volume 0.8, pitch 1.0 |
| `HIVE_SPREAD` | `world/infection/VeinMutationEngine.java:119`, `spread` после успешного размещения новой vein; входы — random tick `block/FleshVeinsBlock.java:143` → `tickVein` и `block/FleshBlock.java:73` → `tickFlesh` | BLOCKS, volume 0.65, pitch 1.0, позиция поставленного блока; один звук максимум на успешный вызов spread, но события могут идти от многих random-ticked блоков; cooldown не добавлял без игрового замера, как требует Sound |
| `CREEPER_RUPTURE` | `event/CarnisEvents.java:52`, `protectHiveTissueFromInfectedCreeper`, `ExplosionEvent.Detonate` для `InfectedCreeperEntity` | HOSTILE, volume/pitch 1.0; серверный реальный взрыв |
| `HIVE_DETAIL_CREAK` | `client/sound/HiveAmbientSoundHandler.java:344,383`, зона THRESHOLD | редкая деталь, случайный интервал 160–280 тиков, volume 0.30 / pitch 1.0 |
| `HIVE_DETAIL_SCUTTLE` | там же, строки 344,387, фактический client playback на строках 345–347; зона SURFACE | 50/50 с `HIVE_DETAIL_MEMBRANE`, interval 160–280 тиков, volume 0.30 / pitch 1.0 |
| `HIVE_DETAIL_MEMBRANE` | там же, строки 344,388, фактический client playback на строках 345–347; зона SURFACE | вариант A из карты Sound: 50/50 с SCUTTLE, volume 0.30 / pitch 1.0 |
| `HIVE_DETAIL_BUBBLES` | там же, строки 344,389, фактический client playback на строках 345–347; зона DEEP | interval 160–280 тиков, volume 0.30 / pitch 1.0 |
| `HIVE_DETAIL_FLOW` | там же, строки 344,390, фактический client playback на строках 345–347; зона CORE | вызов volume 0.30; `sounds.json` задаёт flow_01 multiplier 1.5 (итог 0.45), flow_02 multiplier 1.0 (итог 0.30); pitch 1.0 для обоих |
| `FLAMETHROWER_FIRE` | — | Sound указывает, что механики огнемёта нет. Архитектор T-3196/Z-26 решил оставить событие сознательным заделом и внести в allowlist; Integrator добавил это исключение, checker показывает его отдельной строкой и не валит. Не стал подменять звук Bio Purifier. |
| `FLESH_AMALGAM_AMBIENT` | — (общий ресурс играет через `HIVE_AMALGAM_BREATH`, `entity/FleshAmalgamEntity.java:614`) | Архитектор T-3196 подтвердил, что отдельный вызов не нужен; alias/shared-resource покрытие проверяется отдельными регрессионными тестами. |

### Изменённые файлы исходника

**Java:**
- `01-coder/3.7.3/src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java`
- `01-coder/3.7.3/src/main/java/com/carnis/mod/block/SynapseNodeBlock.java`
- `01-coder/3.7.3/src/main/java/com/carnis/mod/world/infection/VeinMutationEngine.java`
- `01-coder/3.7.3/src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java`
- `01-coder/3.7.3/src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java`
- `01-coder/3.7.3/src/main/java/com/carnis/mod/event/CarnisEvents.java` — обработчик реального explosion event для `CREEPER_RUPTURE`.

**Ресурс по карте Sound:**
- `01-coder/3.7.3/src/main/resources/assets/carnis/sounds.json` — для вариантов `hive.detail_flow` задан pitch 1.0 и per-sample multiplier 1.5/1.0, чтобы при volume вызова 0.30 получить уровни 0.45/0.30 из карты.

Java-список и ресурсный diff должны быть перечислены в build report/manifest при сборке. T-3190 разрешает Java-дельту; `accept_3.7.3.py` ограничивает ресурсный allowlist точными путями, включая только `sounds.json` для S17. `.jar` не собирался.

## Проверка достижимости исходников

Повторная проверка исходников после синхронизации до fix commit `7b9655f`:

- `python3 tools/sound_orphans.py 01-coder/3.7.3 --quiet` — код 0; **82** события, **144** ссылок/OGG; сирот **0**, ссылок в пустоту **0**, недостижимых событий **0**;
- `FLESH_AMALGAM_AMBIENT` распознаётся как покрытый общим ресурсом `hive.amalgam_breath`;
- `FLAMETHROWER_FIRE` остаётся единственным сознательным заделом в allowlist и показывается отдельно;
- `python3 tools/sound_orphans_alias_test.py` — **5/5** тестов пройдены (полное alias-покрытие принимается; частичное покрытие, самопокрытие, пустое событие и взаимное покрытие двух недостижимых событий отвергаются);
- `python3 tools/sound_orphans_allowlist_test.py` — **4/4** интеграционных теста: allowlist содержит только `FLAMETHROWER_FIRE`, задел освобождается, `--no-allowlist` выявляет его как недостижимый, постороннее событие всё равно возвращает код 3;
- `python3 -m json.tool .../sounds.json`, `git diff --check` и статические assertions для серверной точки `CREEPER_RUPTURE` прошли.

Это проверка исходников/статических условий, не Java-компиляция и не игровой тест. В окружении доступен `javac` 11, а проект требует Java 17; Gradle/wrapper отсутствуют. Игрового замера частоты `VeinMutationEngine.spread()` нет.

## Что блокирует окончание T-3184 / принятие 3.7.3

1. Подтверждение Архитектора/Звука для `CREEPER_RUPTURE`: карта предлагала override `Creeper.explodeCreeper()`, но метод `private` в Minecraft 1.20.1. Вместо невалидного override используется серверный `ExplosionEvent.Detonate`; текущий hook ещё не компилировался.
2. T-3197 продвинут upstream: S24 сообщает 144 канонических OGG и 132 файла в `sounds_380/`, R18 независимо подтверждает SHA-256 канона, I20 опубликован с разделением гейтов. Однако sparse checkout не материализует `03-sound/sounds/`; текущий acceptance gate fail-closed пропустит проверку банка, если его нет на диске. Нужны доступные актуальные входы перед полным прогоном.
3. Workspace около 205 MB (`.git` 169 MB, `.git/objects` 168 MB) при лимите `<128 MB`. Удалены 24 временных `/tmp/baseline-*.zip` и `tools/__pycache__`; `build/tmp/temp` отсутствовали. Постоянные ZIPы и Git objects не удалялись. Запрос Архитектору по безопасному уменьшению размера сохранён в `coder_git_storage_architect_request.md`.
4. Нет Java 17/Gradle/Forge classpath для компиляции; игрового прогона и замера частоты spread-звука нет.
5. Постоянные ZIP/manifest старые; полный gate на актуальном кандидате после корректировки CREEPER hook не выполнялся. Следующий шаг — получить/подготовить безопасно актуальные входы, compile без JAR, затем ZIP/manifest и полный gate. Пакет принимать только при зелёных проверках актуальных входов.
6. R15 выявил fail-open в `heard_elsewhere`: два невызванных события с общим OGG оправдывали друг друга. Добавил фильтр dead keys и регрессионный тест взаимного покрытия; alias suite теперь 5/5, включая настоящий `FLESH_AMALGAM_AMBIENT` alias. Минимальный source/test fix закоммичен и запушен как `7b9655f`. Изменение относится к зоне Интегратора/T-3185: ему нужно проверить патч и встроить регрессионные тесты в acceptance/CI; сам T-3185 не закрыт.

## Продолжение после HEAD `487057a`

Предыдущие выводы о ложном срабатывании FLESH и неразрешённом `sounds.json` устарели: обновлённый `sound_orphans.py` считает общий ключ `hive.amalgam_breath` покрытием `FLESH_AMALGAM_AMBIENT`; локальный аудит исходников теперь код 0. В `accept_3.7.3.py` разрешён только точный путь `src/main/resources/assets/carnis/sounds.json` в delta.

Полный acceptance gate был успешно выполнен на временном кандидате в `/tmp` (код 0), с недостающими sparse-checkout inputs и 144-файловым Sound-банком из `9ea5c82`; временные файлы удалены. Этот результат относился к прежней версии Java-дельты: последующий API review выявил невалидный override `Creeper.explodeCreeper()`, поэтому код 0 не подтверждает текущую версию исходников. ZIP/manifest в рабочем каталоге не обновлялись; в HEAD банк всё ещё 276 файлов (S24/T-3197). Java-компиляция/игровой тест не выполнялись; `.jar` не собирался.

## Дополнение · статический review игровых точек

Повторно просмотрены тела всех шести изменённых Java-классов (без Git-обхода):

- `AMALGAM_SMASH` срабатывает только после успешного `super.doHurtTarget` на сервере.
- `SYNAPSE_SHOCK` вызывается из серверного `SynapseNodeBlock.tick` при изменении POWER и ненулевом новом значении, согласно карте S17.
- `HIVE_SPREAD` вызывается только после успешного `setBlockAndUpdate`, в серверном `VeinMutationEngine`; частотный лимит не добавлял, потому что в карте Sound он требует замера частоты в игре, а измерения нет.
- `CREEPER_RUPTURE` перенесён в серверную ветку существующего `CarnisEvents.protectHiveTissueFromInfectedCreeper(ExplosionEvent.Detonate)` после проверки источника взрыва; вызов теперь опирается на реальный Forge event, а не на невозможный override private method.
- `HIVE_DETAIL_*` играют локально на клиенте с задержкой 160–280 тиков по активной зоне.

Это статическая проверка достижимых gameplay hooks, не игровое подтверждение. Дополнительно подтвердил: проект требует Java toolchain 17 (`build.gradle`), в среде доступен только `javac` 11; Gradle wrapper/system Gradle и Gradle cache отсутствуют. Поэтому компиляцию Forge sources выполнить нельзя: не хватает и нужного JDK, и Minecraft/Forge classpath. Ничего не менял по cooldown/механике без игрового замера.

## Коррекция CREEPER_RUPTURE после проверки API Minecraft 1.20.1

Таблица Sound S17 предлагает переопределить `Creeper.explodeCreeper()`. В mappings для целевой версии Minecraft 1.20.1 этот метод имеет модификатор `private`, поэтому такой `@Override` не компилируется. Удалил его из `InfectedCreeperEntity` и перенёс вызов `CREEPER_RUPTURE` в уже существующий серверный обработчик `CarnisEvents.protectHiveTissueFromInfectedCreeper(ExplosionEvent.Detonate)`: он уже фильтрует настоящий взрыв по `InfectedCreeperEntity`, после чего играет звук один раз. Добавлен шестой Java-файл к T-3184: `event/CarnisEvents.java`.

После этой правки `tools/sound_orphans.py` — код 0. Добавил автономный тест `tools/sound_orphans_alias_test.py`; все 4 сценария прошли: полное покрытие файлов alias принимается, частичное покрытие/самопокрытие/пустое событие не принимаются. Тест использует только стандартную библиотеку, Git-объекты и аудио не читает. Старый временный acceptance-код 0 невалиден для текущих исходников, потому что кандидат включал ошибочный override. Новый ZIP/gate не запускал: S24 и storage decision всё ещё открыты. Не менял Sound-карту; расхождение по недоступности override сообщено в этом отчёте для согласования с Архитектором/Звуком.
