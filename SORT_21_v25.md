# SORT-21 (волна 25) — блок внесён, прогон упал на `Build`; причина — в пакете 3.5.2

**Дата:** 2026-11-24
**Промпт:** v25 (`prompt_v25_integrator.md`, 7 197 Б, `4a2039950f7916ef…`, 113 строк)
**Статус:** ✅ шаги 2, 3, 4, 4-бис выполнены. ⛔ **прогон `45415446373` упал на шаге 9 `Build`.** Лог через CLI недоступен (внешняя служба). Причину нашёл в самом пакете 3.5.2 — **правки не делал**, ниже разбор и письмо (§7).

---

## 1. Что внесено в `build.yml`

Блок `Overlay accepted drops` — **вариант Б, дословно**, сверено программно (побайтово, 1 548 Б).

| Метрика | До | После |
|---|---|---|
| Размер `build.yml` | 7 568 Б | **7 646 Б** |
| Строк | — | 179 |
| Шагов | 13 | **13** |

Diff против `origin/main` — только усиление пиннинга, 4 строки математики + 2 сообщения:

```diff
-            dst="$(echo "${line##*->}" | xargs)"
+            rest="${line#*->}"
+            dst="$(echo "${rest%%|*}" | xargs)"
+            if [ "$rest" = "${rest#*|}" ]; then want=""; else want="$(echo "${rest#*|}" | xargs)"; fi
             test -f "$src" || { echo "::error::источник не найден: $src"; exit 1; }
-            want="$(echo "${line#*|}" | xargs)"
             case "$want" in
               ""|*[!0-9a-fA-F]*) echo "::error::строка без sha256 (файл: $src)"; exit 1 ;;
             esac
             [ "${#want}" = "64" ] || { echo "::error::sha256 неверной длины: $want"; exit 1; }
             got="$(sha256sum "$src" | cut -d' ' -f1)"
-            [ "$got" = "$want" ] || { echo "::error::хеш не совпал: $src"; exit 1; }
+            [ "$got" = "$want" ] || { echo "::error::хеш не совпал: $src (ждали $want, получили $got)"; exit 1; }
             mkdir -p "$(dirname "build-src/$dst")"
             cp "$src" "build-src/$dst"
-            echo "assets/carnis/${dst#src/main/resources/assets/carnis/}" >> /tmp/expect.txt
-            echo "| \`$src\` | \`$dst\` | \`$(sha256sum "$src" | cut -c1-12)\` |" >> "$GITHUB_STEP_SUMMARY"
+            echo "${dst#src/main/resources/}" >> /tmp/expect.txt
+            echo "| \`$src\` | \`$dst\` | \`${want:0:12}\` |" >> "$GITHUB_STEP_SUMMARY"
```

**Сценарии прогнаны на живых ogg** (7 из 7): 2 файла → верные пути, код 0; мусор не создаётся; неверный хеш → 1; строка без `|` → 1; не-hex `zzzz` → 1; пустой файл → 0; не-звук (`textures/block/test.png`) → `assets/carnis/textures/block/test.png`.

---

## 2. Шаги 2–4 и 4-бис

### 2.1. Пакет — `01-coder/3.5.2/`, 3 файла

| Файл | Размер | SHA-256 |
|---|---|---|
| `project-3.5.2-clean.zip` | 12 293 939 Б | `8985e602fff642c51073022bf9fbe7a20e990314bf666b2ebe692a28ad4fe294` |
| `project-3.5.2-clean.manifest.txt` | 100 144 Б | `0674b057411ed98c0f17a9204f6d657fa026252706c28c1b244567f51186e012` |
| `PHASE_F_3_5_2_REPORT.md` | 8 793 Б | `ac5f4758d01789c60de637b853ea797f56ff57b7f117e4920b80c4b794b9ae77` |

Манифест — 755 записей. `mod_version=3.5.2` внутри пакета, `mods.toml` — `version="3.5.2"`, `displayVersion="3.5.2"`.

### 2.2. Звуки

| Файл | Размер | SHA-256 | Совпало с v25 |
|---|---|---|---|
| `block/heartbeat_loop.ogg` | 19 819 Б | `39de4db0d9938af9dba8b1f6b637988003410dd7daf85b17df8284c49a513079` | ✅ |
| `block/heart_pulse.ogg` | 10 926 Б | `17f42e3076ee1d0bc8212ea4d817d43ac3e78ebbee8d6c7544e87b4832f7e905` | ✅ |

Банковский мастер (20 284 Б, `bc4154aa`) не тронут.

### 2.3. `overlay.txt` — 721 Б, 2 строки данных

```
03-sound/sounds/block/heartbeat_loop.ogg -> src/main/resources/assets/carnis/sounds/block/heartbeat_loop.ogg | 39de4db0d9938af9dba8b1f6b637988003410dd7daf85b17df8284c49a513079
03-sound/sounds/block/heart_pulse.ogg    -> src/main/resources/assets/carnis/sounds/block/heart_pulse.ogg    | 17f42e3076ee1d0bc8212ea4d817d43ac3e78ebbee8d6c7544e87b4832f7e905
```

SHA-256 самого файла: `d101e5e019d102b5d0fdbc20bec71e1d79895b4703987c834a92b584aeae68d6`.

### 2.4. Чистка

Удалено: `99-incoming/` (37 МБ), `01-coder/3.5.1-{R,R2,R3,R4}/`, `01-coder/workspace/`.
Осталось в `01-coder/`: `3.4.9`, `3.4.10`, `3.5.0`, `3.5.1`, `3.5.1-R5`, `3.5.2`.

---

## 3. Прогон `45415446373`

Запущен push'ем коммита `ad5da27`. Проверка версии и overlay — **зелёные**, дальше `Build` красный.

| № | Шаг | Итог |
|---|---|---|
| 1–6 | Set up / Checkout / JDK / Gradle / Resolve package / Unpack | ✅ success |
| 7 | **Assert version** | ✅ **success** |
| 8 | **Overlay accepted drops** | ✅ **success** |
| 9 | **Build** | ❌ **failure** |
| 10–14 | Verify / Report / Upload / Publish / Commit jar | ⏭ skipped |

`Build`: 14:33:56 → 14:35:27 = **91 с**. Для сравнения, зелёный `Build` в прогоне `45387777546` — тоже ровно **91 с**. То есть конфигурация Gradle прошла, отказ случился на компиляции, а не на сети или таймауте.

### 3.1. Лог не добывается — это ограничение песочницы

| Путь | Результат |
|---|---|
| `gh run view 45415446373 --log-failed` | `EOF` от `results-receiver.actions.githubusercontent.com` |
| `gh api …/actions/jobs/138520281674/logs` | `EOF` от `productionresultssa2.blob.core.windows.net` |
| `gh api …/check-runs` (аннотации) | доступны, но содержательного текста нет |

Что в аннотациях:

- `failure` — `.github`, строка 388: **«Process completed with exit code 1.»** (номер строки к `build.yml` не относится: в файле 179 строк — аннотация привязана к пути-каталогу, а не к шагу);
- `warning` ×2 — **«Restore Gradle distribution 8.1.1 failed: Cache service responded with 400»** и **«Failed to restore gradle-home-v1… Cache service responded with 400»**;
- `warning` ×2 — устаревание `actions/checkout@v4`, `setup-java@v4`, `setup-gradle@v3` (Node 20).

Два предупреждения про кэш — **не причина**: при отказе кэша Gradle просто тянет заново. Оба прогона уложились в одинаковые 91 с, значит распределение и зависимости поднялись.

**Полного лога у меня нет. Он остаётся в вашей зоне.**

---

## 4. Причина: в пакете 3.5.2 вызов метода, которого нет в 1.20.1

Нашёл сравнением пакета 3.5.2 с работавшим `3.5.1-R5`: изменено 20 файлов, добавлено 8, удалено 8.

**Единственная новая поверхность API — блок в `HiveEyeBlockEntity.java`:**

```java
@Override
public void setLevel(Level level) {
    super.setLevel(level);
    if (listenerLevel == level) return;
    unregisterVibrationListener();
    if (!level.isClientSide) {
        level.getGameEventDispatcher(worldPosition).addListener(vibrationListener);   // ← здесь
        listenerLevel = level;
    }
}

private void unregisterVibrationListener() {
    if (listenerLevel == null) return;
    listenerLevel.getGameEventDispatcher(worldPosition).removeListener(vibrationListener); // ← и здесь
    listenerLevel = null;
}
```

В R5 этого блока не было — и R5 собиралась.

### 4.1. Проверка по маппингам 1.20.1 — метода не существует

| Источник | Что показывает |
|---|---|
| Yarn 1.20.1+build.10, `class-use/GameEventDispatcher` | `GameEventDispatcher` используется **только** в `net.minecraft.world.chunk` (`Chunk`, `WorldChunk`) и в собственном пакете. `net.minecraft.world.level` (**Level**) в списке **отсутствует** |
| `mappings.xhyrom.dev` 1.20.1, `LevelChunk` | метод называется **`getListenerRegistry(int sectionY)`** — принимает `int`, а не `BlockPos` |
| `mappings.xhyrom.dev` 1.20.1, `GameEventListenerRegistry` | методы — **`register`** / **`unregister`**; `addListener` / `removeListener` — это имена **Yarn**, в официальных маппингах их нет |
| Forge 1.20.x, `patches/…/level/Level.java.patch` (10 816 Б) | вхождений `GameEvent` — **0**. Forge такого метода в `Level` не добавляет |

Итого три независимых отказа в одной строке:

1. `Level#getGameEventDispatcher` — **метода нет** в 1.20.1;
2. аргумент `worldPosition` — `BlockPos`, а метод (даже там, где он есть) ждёт `int ySectionCoord`;
3. `addListener` / `removeListener` — в официальных маппингах это `register` / `unregister`.

Набор имён (`getGameEventDispatcher`, `addListener`, `removeListener`) — это связка **Yarn 1.17–1.19**, а не официальные маппинги Forge 1.20.1. Похоже, код собран по памяти или по стороннему источнику.

### 4.2. Зачем это вообще нужно — вероятно, не нужно

`HiveEyeBlockEntity` объявлен как `implements GeoBlockEntity, GameEventListener.Holder<GameEventListener>` (так было и в R5). В 1.20.1 регистрацию `Holder`'ов ведёт движок: в `LevelChunk` есть `addAndRegisterBlockEntity(BlockEntity)` и `private removeGameEventListener(T, ServerLevel)`. R5 жила без ручной регистрации и работала.

**Минимальное исправление — удалить блок `setLevel` + `setRemoved` + `unregisterVibrationListener` и поле `listenerLevel` целиком**, вернувшись к поведению R5. Если ручное управление всё же нужно, правильный вызов в 1.20.1:

```java
level.getChunkAt(worldPosition)
     .getListenerRegistry(SectionPos.blockToSectionCoord(worldPosition.getY()))
     .register(vibrationListener);        // и .unregister(...) для снятия
```

### 4.3. Остальное в пакете — чисто

Проверил, чтобы не свалить в одну кучу:

| Проверка | Результат |
|---|---|
| `build.gradle` vs R5 | отличие — **только комментарий** (`3.5.1` → `3.5.2`) |
| `gradle.properties`, `mods.toml` | только версия |
| Java-файлов | 228 |
| Новых `import com.carnis.*` | **1** — `ScytheItem` (класс на месте) |
| Остатки `HiveGrowthSuppression.HIVE_BLOCKS` | **0** — тег переехал в `ModBlockTags`, класс есть |
| `CarnisConfig.SERVER.*` | 15 полей, все присвоены, ссылок на несуществующие — **0** |
| `countNearbyFlora`, `retaliate` | определены |
| JSON (258 файлов) | ошибок разбора **0** |
| `src/generated` | на месте, 50 файлов, `sourceSets` его подключает |
| Дубли путей `main` / `generated` | **0** |
| `$` в JSON (ломает `expand`) | **0** |

То есть в пакете **одна** поломка — та, что в §4.

---

## 5. Диффы ключевых файлов (для Кодера)

```diff
# HiveEyeBlockEntity.java — единственное изменение, ломающее сборку
+    @Nullable
+    private Level listenerLevel;
+
+    @Override
+    public void setLevel(Level level) {
+        super.setLevel(level);
+        if (listenerLevel == level) return;
+        unregisterVibrationListener();
+        if (!level.isClientSide) {
+            level.getGameEventDispatcher(worldPosition).addListener(vibrationListener);
+            listenerLevel = level;
+        }
+    }
```

Остальные 19 изменённых файлов — игровая логика (`ScytheItem`, ретаргетинг, подавление флоры, свет блоков, конфиг, datagen), к сборке претензий нет.

---

## 6. Отчёт по вашим пунктам §6

| Пункт | Статус |
|---|---|
| 1. Diff `build.yml` | ✅ §1 — 7 568 → 7 646 Б, дословно |
| 2. Хеши разложенных файлов | ✅ §2.1 (3 файла) + §2.2 (2 звука) + §2.3 (`overlay.txt`) |
| 3. `overlay.txt` | ✅ §2.3 — 721 Б, 2 строки |
| 4. Прогон: номер, статус, три шага | ✅ §3 — `45415446373`, failure, `Assert` ✔ / `Overlay` ✔ / `Build` ❌ |
| 5. `carnis-3.5.2.jar` | ⛔ **не создан** — шаги 10–14 пропущены |
| 6. Оба адреса и коды | §8 |
| 7. Дерево до/после, целость 3.5.1 | §7 |
| 8. Хеши не сошлись / `Assert` красный → стоп | ⚠️ не сработало: **хеши сошлись, `Assert` зелёный**, упало дальше. Остановился по духу правила — **правок не делал, письмо ниже** |

---

## 7. Целость 3.5.1 и размеры

| Объект | Состояние |
|---|---|
| `06-build/jars/carnis-3.5.1.jar` | **12 620 144 Б**, `44f4b0b91a40c52b5d8651f70ec110de6ea5aba21efbc8668e16f26f80d96c0e` — не тронут |
| Первые байты jar | `PK\x03\x04` |
| `mods.toml` внутри jar | `version="3.5.1"`, `displayVersion="3.5.1"` |
| Релиз `v3.5.1` | цел: `tag_name=v3.5.1`, имя «Carnis 3.5.1», 1 ассет `carnis-3.5.1.jar` 12 620 144 Б |

Размеры дерева:

| Момент | Всего | `.git` | Рабочее дерево |
|---|---|---|---|
| До чистки | 433 МБ | 231 МБ | 202 МБ |
| После чистки, до коммита | **334 МБ** | 231 МБ | 103 МБ |
| Сейчас (после коммита `ad5da27`) | **346 МБ** | 243 МБ | **103 МБ** |

Разница 334 → 346 МБ — это ровно 12 МБ пакета 3.5.2, вошедшего в историю. Рабочее дерево не изменилось. Напоминаю вашу же цифру 119.6 МБ — это упакованный объём на стороне API, а не `du`.

---

## 8. Оба адреса и коды

| Адрес | Код |
|---|---|
| `…/releases/tag/v3.5.1` | **200** |
| `…/releases/download/v3.5.1/carnis-3.5.1.jar` | **302** → далее `OpenSSL SSL_ERROR_SYSCALL` на `release-assets.githubusercontent.com` (ограничение песочницы) |
| `…/raw/main/06-build/jars/carnis-3.5.1.jar` | **302** → далее тот же `SSL_ERROR_SYSCALL` на `raw.githubusercontent.com` |

Коды редиректов корректны — файл существует и отдаётся. Обрыв на втором хопе — ограничение моего окружения, у вас должно открываться.

---

## 9. Письмо координатору

> **Тема: SORT-21 (v25) — прогон `45415446373` упал на `Build`; лог недоступен, причина найдена в пакете 3.5.2**
>
> 1. **Сделано:** блок `Overlay accepted drops` внесён дословно (7 568 → 7 646 Б); пакет 3.5.2 разложен (3 файла); звуки обновлены (19 819 / 10 926 Б — хеши сошлись); `overlay.txt` — 2 строки; чистка выполнена. Всё одним коммитом `ad5da27`.
> 2. **Прогон `45415446373`:** шаги 1–8 success, **`Assert version` ✔**, **`Overlay accepted drops` ✔**, **шаг 9 `Build` ❌**, шаги 10–14 skipped. `carnis-3.5.2.jar` не создан.
> 3. **Лог получить не удалось** — все три пути (`--log-failed`, REST `jobs/{id}/logs`, check-runs) отдают `EOF` от внешних служб GitHub. Полный лог остаётся у вас.
> 4. **Причина найдена по коду, не по логу.** В `HiveEyeBlockEntity.java` добавлен вызов `level.getGameEventDispatcher(worldPosition).addListener(...)`. В 1.20.1 такого метода у `Level` нет: по Yarn-маппингам 1.20.1 `GameEventDispatcher` используется только в `Chunk`/`WorldChunk`; в Forge-патче `Level.java` для 1.20.x вхождений `GameEvent` — 0. Плюс аргумент `BlockPos` вместо `int` и имена `addListener`/`removeListener` — это Yarn, а в официальных маппингах `register`/`unregister`. В `R5` этого блока не было, и `R5` собиралась.
> 5. **Оценка риска:** правка локальная, один файл, ~25 строк. Остальные 19 изменённых файлов проверил — к сборке претензий нет (`build.gradle` отличается только комментарием; битых ссылок и импортов 0; JSON 258/258 валидны).
> 6. **Правок не делал** — пакет не мой. Нужно решение:
>    - **(А, рекомендую)** Кодер убирает блок `setLevel`/`setRemoved`/`unregisterVibrationListener` и поле `listenerLevel` — возврат к поведению R5, где регистрацию `GameEventListener.Holder` ведёт движок через `LevelChunk.addAndRegisterBlockEntity`. Пересдача `3.5.2-R/`;
>    - **(Б)** Кодер оставляет ручную регистрацию, но через корректный API: `level.getChunkAt(pos).getListenerRegistry(SectionPos.blockToSectionCoord(pos.getY())).register(...)` / `.unregister(...)`;
>    - **(В)** вы присылаете исправленный файл — вношу дословно.
> 7. **`carnis-3.5.1.jar` цел** (12 620 144 Б, `44f4b0b9…`), релиз `v3.5.1` цел. Ничего не удалял.
> 8. **Жду решения.** До него — ни пушей в `01-coder/**`, ни новых прогонов: каждый прогон бесполезен, пока пакет не соберётся.
