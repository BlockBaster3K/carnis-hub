# VERIFY_01-coder_3.5.2-R — независимая проверка Интегратора

**Дата:** 2026-11-24
**Объект:** пересдача Кодера 3.5.2-R — `01-coder/3.5.2-R/` (3 файла)
**Основание:** отчёт Кодера о волне 26 `01-coder/3.5.2-R/PHASE_F_3_5_2_R_REPORT.md`
(sha256 `2825a286…`), устранение падения CI-прогона `45415446373` на шаге `Build`
**Принцип:** правило 5 — не принимать на слово. Все заявления перепроверены по файлам.
**Вердикт Интегратора:** ✅ **ПРИНЯТО** — пакет самосогласован, правка минимальна,
новые механики и принятое аудио не потеряны. **Остаётся прогон CI-сборки.**

---

## 1. Состав поставки

| Файл | Байт | SHA-256 |
|---|---:|---|
| `project-3.5.2-clean.zip` | 12 297 346 | `a31dc63e34009461b435c433993cc114f5f703cee8c20053511b55538cb973a3` |
| `project-3.5.2-clean.manifest.txt` | 100 144 | `0ec6eb0852438fa248a4d73c1d03e98d30b7b9fbe1634b323b51343eb631bdb9` |
| `PHASE_F_3_5_2_R_REPORT.md` | 10 210 | `2825a286a0023a4d80be4c76bbde6915870e12489a620b3e1933568d0b131016` |

### 1.1. Расхождение хеша ZIP с отчётом — принято и объяснено

Отчёт Кодера волны 26 заявляет ZIP `f61470442d619ba64dd2958d4d2adf2a9b16abe0fe284f052b47cd27f3e06159`
(12 293 774 Б). **Этот файл в сдачу не попал** — ни в `01-coder/3.5.2/`, ни в `uploads/`,
ни в рабочее дерево; доставлен только текст отчёта. Проверка сдачи показала, что
закоммиченный ранее `01-coder/3.5.2/project-3.5.2-clean.zip` (`8985e602…`, 12 293 939 Б)
содержит **исходный, не исправленный** `HiveEyeBlockEntity.java`
(sha256 `d6d4a2e2187f084d7ef5ef3378b0baa1510f1660240ff9cb3d2a7542b99e36b1`, 39 544 Б)
с двумя вызовами `Level#getGameEventDispatcher` — тот самый API, отсутствующий в 1.20.1.

Поэтому Интегратор пересобрал пакет **из исходного 3.5.2, подставив в него побайтово
идентичный исправленный файл Кодера**: SHA-256 файла `HiveEyeBlockEntity.java` в новом
пакете — `f355e81b8bcc4965db6a0e58b5bc00d8045fee4b6b1d8095c10fb5ffff8f630d`, 38 811 Б —
**совпадает с заявленным в отчёте Кодера до последнего бита**. То есть по содержанию
исправления сдача эквивалентна сдаче Кодера; расходится только ZIP-контейнер
(состав, порядок и метаданные записи), на содержимое исходников это не влияет.

> **Вывод:** заявленный Кодером результат воспроизведён независимо и положен в сдачу.
> Сам ZIP Кодера в репозитории отсутствует и проверен быть не может.

---

## 2. Минимальность правки

Полное сравнение нового пакета с исходным 3.5.2 (755 файлов, 755 путей):

| Проверка | Результат |
|---|---|
| Файлов в пакете | **755** (как в `3.5.2/`) |
| Набор путей | **идентичен** исходному `3.5.2/` (755/755) |
| Изменённых файлов | **ровно 1** — `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java` |
| Удалённых / добавленных файлов | **0 / 0** |
| Внешний manifest | **755 записей**, сверка распакованного содержимого — **755/755 OK**, 0 FAILED |
| Изменившихся строк manifest | **1** (строка 75 — хеш `HiveEyeBlockEntity.java`) |
| Файлов вне манифеста | **0** |
| Встроенный `MANIFEST.txt` | 757 строк (2 заголовка + 755 путей), **хешей не содержит** → после правки остаётся корректным, пересборка не требуется |

### 2.1. Что именно удалено

Единственный diff — `HiveEyeBlockEntity.java`, 879 → 854 строки (−25):

```diff
     private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
     private final net.minecraft.world.level.gameevent.GameEventListener vibrationListener = new EyeListener();
-    @Nullable
-    private Level listenerLevel;

@@
-    @Override
-    public void setLevel(Level level) {
-        super.setLevel(level);
-        if (listenerLevel == level) return;
-        unregisterVibrationListener();
-        if (!level.isClientSide) {
-            level.getGameEventDispatcher(worldPosition).addListener(vibrationListener);
-            listenerLevel = level;
-        }
-    }
-
-    @Override
-    public void setRemoved() {
-        unregisterVibrationListener();
-        super.setRemoved();
-    }
-
-    private void unregisterVibrationListener() {
-        if (listenerLevel == null) return;
-        listenerLevel.getGameEventDispatcher(worldPosition).removeListener(vibrationListener);
-        listenerLevel = null;
-    }
-
-    @Override
     public AnimatableInstanceCache getAnimatableInstanceCache() {
         return animationCache;
     }
```

Удалены ровно четыре сущности: поле `listenerLevel`, переопределение `setLevel(Level)`,
переопределение `setRemoved()` и приватный хелпер `unregisterVibrationListener()`.
Больше в файле не изменено **ничего** — правка соответствует решению координатора (А)
«убрать блок — возврат к регистрации движком».

### 2.2. Механизм регистрации сохранён

| Элемент | Состояние в `3.5.2-R` |
|---|---|
| `implements … GameEventListener.Holder<GameEventListener>` | ✅ строка 58 |
| `public GameEventListener getListener()` | ✅ строки 144–146, возвращает `vibrationListener` |
| Внутренний класс `EyeListener implements GameEventListener` | ✅ строка 819, `getListenerSource`/`getListenerRadius`/`handleGameEvent` на месте |
| Вызовы `getGameEventDispatcher` / `addListener` / `removeListener` | **0** — несовместимый API устранён полностью |

Регистрация listener'а теперь выполняется ванилью: `LevelChunk` сам подписывает
`EntityBlock.getListener()` у блок-сущностей. Это подтверждено на реальном bytecode
официального Mojang server bundle 1.20.1 (`LevelChunk`, `EntityBlock`,
`GameEventListener.Holder#getListener()`) — ручной lifecycle не требуется.

---

## 3. Новые механики 3.5.2 не потеряны

| Механика (волна 21/22) | Проверка | Итог |
|---|---|---|
| K-21-1. Общий `ScytheItem` | `item/ScytheItem.java` — класс `ScytheItem(Tier, int, float, float, float, String, Properties)`; в `init/ModItems.java:154` костяная коса `ScytheItem(Tiers.STONE, 2, -2.4F, 1.15F, 0.8F, null, durability 180)`, `:157` оссифицированная `ScytheItem(Tiers.IRON, 5, -2.4F, 1.0F, 1.0F, "tooltip.carnis.ossified_scythe", durability 650)` | ✅ |
| K-21-1. Звуки кос | `sounds.json`: `item.ossified_scythe.swing` → `carnis:combat/ossified_scythe_swing_01`, `item.ossified_scythe.hit` → `carnis:combat/ossified_scythe_hit_01`; OGG-файлы на месте | ✅ |
| K-21-2. Интервал heartbeat 34–46 тиков | `client/HeartAmbientTicker.java:13-14` `HEARTBEAT_INTERVAL_FAR = 46`, `HEARTBEAT_INTERVAL_NEAR = 34`; `:26` `46 - Math.round(proximity * 12.0F)`; `:16` `HEARTBEAT_MAX_SAMPLE_SECONDS = 1.5F` | ✅ |
| K-21-3. Реакция существ | `HurtByTargetGoal` — 4 вхождения в `src/main/java` (CerebralNexus, HiveSentinel, ParasiticTendril и базовый) | ✅ |
| K-21-4. Glow pass | `OptionalGlowLayer` в пакете, изменений не вносилось | ✅ |
| K-21-5. Свет `PULSING_HEART` | `init/ModBlocks.java` в пакете, изменений не вносилось | ✅ |
| K-21-6. Конфиг флоры | `CarnisConfig`: `flora_chance_percent`, `flora_local_cap`, `moss_spread_percent` | ✅ |
| K1. Block-tag JSON только в main | 10 block-tag JSON в `src/main/resources`, 0 в `src/generated` | ✅ |
| K2. Item-модели / spawn egg | `nerve_pillar`, `stomach_pool` — hand-authored модели, provider без конфликтов | ✅ |
| K3. Единственный `HIVE_BLOCKS` | `ModBlockTags.java:10` — единственное объявление | ✅ |
| K6. Ручная регистрация listener | **удалена**, регистрация возвращена движку | ✅ (цель волны 26) |

Состав пакета: **228** java, **258** json (все 258 распарсились, битых 0),
**145** ogg, **113** png.

---

## 4. Версии и совместимость

| Поле | Значение |
|---|---|
| `gradle.properties: mod_version` | `3.5.2` |
| `mods.toml: version` | `3.5.2` |
| `mods.toml: displayVersion` | `3.5.2` |
| `minecraft_version` | `1.20.1` |
| `forge_version` | `47.4.28` |
| `archives_base_name` | `carnis` → итоговый jar `carnis-3.5.2.jar` |

Версия не менялась ни в одной из пересдач.

---

## 5. Принятое аудио (overlay) — на месте

`06-build/overlay.txt` (две принятые партии звука, волна 22) проверен по хешам:

| Источник | Назначение | Ожидаемый SHA-256 | Факт | Итог |
|---|---|---|---|---|
| `03-sound/sounds/block/heartbeat_loop.ogg` | `src/main/resources/assets/carnis/sounds/block/heartbeat_loop.ogg` | `39de4db0…a513079` | совпал | ✅ |
| `03-sound/sounds/block/heart_pulse.ogg` | `src/main/resources/assets/carnis/sounds/block/heart_pulse.ogg` | `17f42e30…e905` | совпал | ✅ |

Overlay **имеет смысл**: файлы внутри пакета отличаются от принятых —
`heartbeat_loop.ogg` в пакете 34 509 Б (`a213f196…`) → в overlay 19 819 Б (`39de4db0…`);
`heart_pulse.ogg` в пакете 4 690 Б (`45dd0e8f…`) → в overlay 10 926 Б (`17f42e30…`).
Именно принятые версии попадут в jar.

---

## 6. Симуляция шагов CI (до Gradle)

Workflow `.github/workflows/build.yml`, ветка `arena/d474d740-carnis-hub`:

| Шаг workflow | Фактический результат симуляции |
|---|---|
| `Resolve package` | каталоги `3.4.9, 3.5.0, 3.5.1, 3.5.1-R5, 3.5.2, 3.5.2-R` → `sort -V \| tail -1` = **`3.5.2-R`**; ZIP `01-coder/3.5.2-R/project-3.5.2-clean.zip` (единственный кандидат под `project-*-clean.zip`) ✅ |
| `Unpack project package` | **755** файлов ✅ |
| `Assert version` | `mod_version=3.5.2` → ожидалось `3.5.2` ✅ |
| `Overlay accepted drops` | 2 строки, обе SHA-256 совпали, файлы скопированы ✅ |
| `Build` (Gradle) | **не выполнялся локально** — см. §8 |
| `Verify overlay reached the jar` / `Report jar version` / `Upload jar` / `Publish release` / `Commit jar into repository` | требуют прогона CI |

---

## 7. Неизменность предыдущих папок

`01-coder/3.5.2/` **не тронута** — восстановлена в исходное состояние коммита `0cc552d`:
`project-3.5.2-clean.zip` `8985e602…`, `project-3.5.2-clean.manifest.txt` `0674b057…`,
`PHASE_F_3_5_2_REPORT.md` `ac5f4758…`. Пересдача оформлена новой папкой `3.5.2-R/`
по конвенции репозитория (`3.5.1-R`, `3.5.1-R2` … `3.5.1-R5`).

---

## 8. Что осталось за Интегратором

1. **Прогон CI-сборки.** Локальная сборка невозможна: в песочнице 1 ГБ RAM, 2 ядра,
   JDK 11 (workflow требует JDK 17) и нет Gradle; прежняя попытка упиралась в OOM.
   Сборка выполняется только GitHub Actions (раннер 7 ГБ).
2. **Push.** Коммит `c9676da` подготовлен локально в ветке `arena/d474d740-carnis-hub`
   (родитель `0cc552d`). Отправка требует прав на запись: в текущей сессии нет PAT и нет
   SSH-ключа в репозитории (`could not read Username for 'https://github.com'`),
   GitHub connector недоступен. Подготовлен ed25519-ключ и команда отправки:

   ```bash
   git -C /home/user/hub5 push git@github.com:BlockBaster3K/carnis-hub.git \
        HEAD:refs/heads/arena/d474d740-carnis-hub
   ```

   Push задевает `01-coder/**`, поэтому workflow `build.yml` запускается сам.
   Готовый скрипт: `/home/user/ci_release.py` (push → ожидание прогона → проверка jar).
3. **Предъявление результата.** После прогона — `carnis-3.5.2.jar` с проверенным SHA-256,
   версией `3.5.2` из `mods.toml` и подтверждением, что оба принятых OGG попали внутрь jar.
