# S17 · Карта привязки 11 недостижимых событий ModSounds

**Кто:** Звук · **Шаг:** S17 (Волна 52) · **База:** `243e598` · **Дата:** 2026-11-26 19:20
**Задача:** T-3184 / T-3190. Решение Архитектора: **привязать, не удалять.**

---

## Что сделано

Каждое из 11 событий зарегистрировано в `ModSounds.java`, имеет ключ в
`sounds.json` и живые файлы на диске — но **ни разу не вызывается по имени в
`.java`**. Я нашёл в коде для каждого точку вызова и привёл измеренные
характеристики, чтобы уровень и момент подбирались по данным, а не на слух.

**Формулировка, за которую отвечаю:** «не вызывается по имени в `.java`».
Утверждение «звук не играется в игре» я не делаю — это проверил бы только
игровой тест.

## Замеры 15 файлов

| событие | файл | длина | пик | RMS | crest | центр | <80 Гц | тело |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `FLAMETHROWER_FIRE` | `entity/flamethrower_fire` | 1.64 с | −6.3 | −19.0 | 12.7 | 1299 | 1.9 % | 1640 мс |
| `AMALGAM_SMASH` | `entity/flesh_amalgam_smash_01` | 2.60 с | −3.2 | −18.2 | 15.1 | 423 | 36.0 % | 1033 мс |
| `AMALGAM_SMASH` | `entity/flesh_amalgam_smash_02` | 1.90 с | −3.0 | −17.0 | 14.0 | 419 | 35.9 % | 969 мс |
| `SYNAPSE_SHOCK` | `block/synapse_shock` | 0.55 с | −3.0 | −18.0 | 15.0 | 2171 | 0.1 % | 305 мс |
| `HIVE_SPREAD` | `hive/hive_spread_01_creep` | 0.90 с | **−1.3** | −24.4 | **23.1** | 502 | 1.6 % | **95 мс** |
| `HIVE_SPREAD` | `hive/hive_spread_02_pulse` | 0.80 с | −3.3 | −22.1 | 18.8 | 539 | 0.1 % | 488 мс |
| `HIVE_SPREAD` | `hive/hive_spread_03_swell` | 1.05 с | −1.3 | −24.0 | 22.7 | 493 | 0.3 % | 850 мс |
| `HIVE_DETAIL_FLOW` | `hive/detail_flow_01` | 1.32 с | −15.1 | −29.6 | 14.5 | 3592 | 0.0 % | 1161 мс |
| `HIVE_DETAIL_FLOW` | `hive/detail_flow_02` | 0.48 с | −7.3 | −21.8 | 14.5 | 2670 | 0.0 % | 391 мс |
| `HIVE_DETAIL_MEMBRANE` | `hive/detail_membrane_01` | 0.54 с | −5.0 | −21.7 | 16.8 | 3509 | 0.0 % | 425 мс |
| `HIVE_DETAIL_BUBBLES` | `hive/detail_bubbles_01` | 0.78 с | −5.4 | −22.0 | 16.6 | 2936 | 0.1 % | 672 мс |
| `HIVE_DETAIL_CREAK` | `hive/detail_creak_01` | 1.12 с | −6.0 | −22.0 | 16.0 | 2800 | 0.0 % | 770 мс |
| `HIVE_DETAIL_SCUTTLE` | `hive/detail_scuttle_01` | 0.62 с | −2.8 | −22.1 | 19.3 | 2888 | 0.0 % | 486 мс |
| `CREEPER_RUPTURE` | `block/creeper_rupture` | 0.90 с | −3.1 | −17.1 | 14.0 | 379 | 2.1 % | 561 мс |
| `FLESH_AMALGAM_AMBIENT` | `entity/flesh_amalgam_ambient` | 2.30 с | −9.8 | −20.0 | 10.2 | 504 | 0.4 % | 2300 мс |

---

## Привязка: таблица решений

Три события — **прямые попадания**: файл создан именно под этот игровой момент,
и в коде даже есть готовое место. Их привязка не меняет звуковой дизайн вообще.

### 1. `AMALGAM_SMASH` → удар амальгамы (уже есть пустая точка)

`FleshAmalgamEntity.java:298` — `doHurtTarget(Entity target)` уже переопределён
для кислотного всплеска, но звука удара в нём нет:

```java
@Override
public boolean doHurtTarget(Entity target) {
    boolean hit = super.doHurtTarget(target);
    if (
            hit
                    && target instanceof ServerPlayer player
                    && level() instanceof ServerLevel serverLevel
    ) {
        tryAcidSplash(serverLevel, player);
    }
    // ДОБАВИТЬ:
    if (hit && level() instanceof ServerLevel serverLevel) {
        serverLevel.playSound(null, getX(), getY(), getZ(),
                ModSounds.AMALGAM_SMASH.get(), SoundSource.HOSTILE, 1.0F, 1.0F);
    }
    return hit;
}
```

**`volume 1.0`** — обоснованно: файл −3.2/−3.0 dBFS RMS −18, центр 423 Гц,
это ровно «тяжёлый удар», и он должен доминировать над шагом (`AMALGAM_STEP`,
`playStepSound`, уже 1.0). Ниже 1.0 удар потеряется под шагами.

⚠ **Отклонение:** центр 423 и 419 Гц при норме ≥ 400 — **на грани**,
`<80 Гц` = 36 % при норме ≤ 25 %. Файл вне тембровой нормы S20, но норма S20
введена для **68 новых** файлов 3.8.0, к готовому банку 3.7.x не применяется.
Фиксирую как факт, не как нарушение.

### 2. `SYNAPSE_SHOCK` → переход узла в активное состояние

`SynapseNodeBlock.java:71–73` уже играет пульс, когда рядом есть цель:

```java
int nextPower = Math.min(ACTIVE_SIGNAL, nearbyTargets);
if (state.getValue(POWER) != nextPower) {
    level.setBlock(pos, state.setValue(POWER, nextPower), 3);
    level.updateNeighborsAt(pos, this);
    level.updateNeighbourForOutputSignal(pos, this);
}
```

Вставка — **ровно в момент смены состояния**, не в каждый тик:

```java
if (state.getValue(POWER) != nextPower) {
    level.setBlock(pos, state.setValue(POWER, nextPower), 3);
    level.updateNeighborsAt(pos, this);
    level.updateNeighbourForOutputSignal(pos, this);
    // ДОБАВИТЬ: узел «включился» — один раз на переход
    if (nextPower > 0) {
        level.playSound(null, pos, ModSounds.SYNAPSE_SHOCK.get(),
                SoundSource.BLOCKS, 0.8F, 1.0F);
    }
}
```

**`volume 0.8`**, а не 1.0: событие уже звучит пульсом (`SYNAPSE_NODE_PULSE`,
`1.0`) каждые 40 тиков, и шок 1.0 забивал бы его. 0.8 = слышно как «включение»,
не как основное событие.

### 3. `HIVE_SPREAD` → успешное разрастание

`VeinMutationEngine.java:116` — блок фактически поставлен:

```java
if (result != null && !result.equals(existing) && level.setBlockAndUpdate(outside, result)) return;
```

Вставка перед `return`:

```java
if (result != null && !result.equals(existing) && level.setBlockAndUpdate(outside, result)) {
    level.playSound(null, outside, ModSounds.HIVE_SPREAD.get(),
            SoundSource.BLOCKS, 0.65F, 1.0F);
    return;
}
```

**`volume 0.65`, а не 1.0.** Здесь я возражаю против «поставить 1.0»:

| файл | пик | crest | тело |
|---|---:|---:|---:|
| `hive_spread_01_creep` | **−1.3** | **23.1** | **95 мс** |
| `hive_spread_03_swell` | −1.3 | 22.7 | 850 мс |
| `hive_spread_02_pulse` | −3.3 | 18.8 | 488 мс |

`creep` — это **громкий короткий транзиент** (тело 95 мс) при пике почти в
потолок. `VeinMutationEngine.spread()` вызывает `setBlockAndUpdate` **на каждом
random-tick**, где найдено место: в заражённой зоне это могут быть десятки
срабатываний в секунду. При `volume 1.0` и пике −1.3 dBFS получится очередь
ударов на полной громкости — не «разрастание», а треск.

**0.65** даёт пик ≈ −1.3 − 3.7 = **−5.0 dBFS** — заметно, но не перекрывает
амбиент. Если после игрового теста окажется слишком тихо, безопасный потолок
**0.7** (−4.4 dBFS), выше не советую.

⚠ **Проверить Кодеру:** если `spread()` вызывается слишком часто, звук стоит
пустить не чаще раза в N тиков (счётчик в `VeinMutationEngine`). Точное число
назову после замера частоты вызовов в игре — без него я бы гадал.

### 4. `CREEPER_RUPTURE` → смерть заражённого крипера

`InfectedCreeperEntity` extends `Creeper`, то есть взрыв делает **ванильный
`Creeper.explodeCreeper()`**. Своей реализации взрыва в классе нет, поэтому
единственная надёжная точка — переопределить его:

```java
@Override
protected void explodeCreeper() {
    level().playSound(null, getX(), getY(), getZ(), ModSounds.CREEPER_RUPTURE.get(),
            SoundSource.HOSTILE, 1.0F, 1.0F);
    super.explodeCreeper();
}
```

**`volume 1.0`** — момент одноразовый и важный, ванильный звук взрыва пойдёт
поверх, и разрыву нужно быть слышимым. Замер: −3.1 dBFS, центр 379 Гц, тело
561 мс — низкий разрыв, под ванильный взрыв ложится.

⚠ **Оговорка:** `explodeCreeper()` в 1.20.1 объявлен `protected` в `Creeper`.
Если компилятор не даст переопределить (изменился модификатор) — альтернатива:
в `die(DamageSource)` при `source.is(DamageTypes.PLAYER_EXPLOSION)` не играть
(звук уже был). Я это переопределение **не компилировал**, локальный Gradle-билд
мне запрещён — отмечаю как непроверенное.

### 5. `FLAMETHROWER_FIRE` → **привязывать некуда**

Нашёл: событие зарегистрировано (`ModSounds.java:22`), файл есть
(`entity/flamethrower_fire.ogg`, 1.64 с, пик −6.3), **но в коде нет ни одного
оружия-огнемёта**. Биоочиститель (`PurifierLampBlock`, `BioPurifierModel`)
использует `PURIFIER_IGNITE` и `PURIFIER_LOOP`, а не это событие.

**Рекомендация: оставить как задел, не удалять** (решение Архитектора
«привязать, не удалять» я поддерживаю) — но честно пометить: **точки вызова
сейчас не существует**, её надо создавать вместе с механикой огнемёта. Ставить
его на очиститель нельзя: это подмена звука, а не привязка.

### 6. `FLESH_AMALGAM_AMBIENT` → **привязывать не нужно**

Ревизор прав: файл **уже звучит** — `hive.amalgam_breath` использует
`entity/flesh_amalgam_ambient` (замерено, 2.30 с, пик −9.8). Дублирующая
регистрация события не вредит: она ничего не ломает, а удаление ключа
рискованно (файл остаётся живым через другое событие — `sound_orphans` не
упадёт, но правило «не удалять без санкции» действует).

**Рекомендация: ничего не делать.** Записать в карте как «жив через другое
событие», закрыть вопрос.

---

## Пять `hive.detail_*` → зональные эмбиенты

Решение по уровню — в `sound_hive_detail_decision.md`. Здесь — **точные
события и готовый код**.

Файл: `HiveAmbientSoundHandler.java`. Механизм уже есть: `playPeriodicEvents()`
крутит тональный стингер с интервалом `1200L + level.random.nextInt(1201)`
(60–120 с). Для деталей нужен **свой, более частый** таймер.

```java
// Поле рядом с nextTonalStingerAt:
private static long nextHiveDetailAt = NO_SCHEDULED_TIME;
private static final int DETAIL_MIN_TICKS = 160;  // 8 с
private static final int DETAIL_MAX_TICKS = 280;  // 14 с

// Внутри playPeriodicEvents(), после блока тонального стингера:
if (currentZone != -1) {
    if (nextHiveDetailAt == NO_SCHEDULED_TIME) {
        nextHiveDetailAt = now + DETAIL_MIN_TICKS
                + level.random.nextInt(DETAIL_MAX_TICKS - DETAIL_MIN_TICKS + 1);
    } else if (now >= nextHiveDetailAt) {
        SoundEvent detail = hiveDetailForZone(currentZone);
        if (detail != null) playOneShot(client, detail);
        nextHiveDetailAt = now + DETAIL_MIN_TICKS
                + level.random.nextInt(DETAIL_MAX_TICKS - DETAIL_MIN_TICKS + 1);
    }
} else {
    nextHiveDetailAt = NO_SCHEDULED_TIME;
}

// Новый метод:
private static SoundEvent hiveDetailForZone(int zone) {
    return switch (zone) {
        case ZONE_THRESHOLD -> ModSounds.HIVE_DETAIL_CREAK.get();
        case ZONE_SURFACE -> ModSounds.HIVE_DETAIL_SCUTTLE.get();
        case ZONE_DEEP -> ModSounds.HIVE_DETAIL_BUBBLES.get();
        case ZONE_CORE -> ModSounds.HIVE_DETAIL_FLOW.get();
        default -> null;
    };
}
```

**Соответствие зон — по смыслу, а не по алфавиту:**

| событие | зона | почему именно эта |
|---|---|---|
| `HIVE_DETAIL_CREAK` | `ZONE_THRESHOLD` (порог) | скрип конструкции на входе в улей |
| `HIVE_DETAIL_SCUTTLE` | `ZONE_SURFACE` (поверхность) | топот по внешней мембране |
| `HIVE_DETAIL_BUBBLES` | `ZONE_DEEP` (глубина) | пузыри в глубокой биомассе |
| `HIVE_DETAIL_FLOW` | `ZONE_CORE` (ядро) | течение в сердцевине |
| `HIVE_DETAIL_MEMBRANE` | `hive.ambient` | **особый случай**, см. ниже |

**`DETAIL_MEMBRANE` нельзя поставить по зонам** — их четыре, а зон в обработчике
тоже четыре, и все заняты. У мембраны нет своей зоны, потому что зона
поверхности уже занята топотом. Два варианта:

- **A (рекомендую):** дать мембране второй слот в `ZONE_SURFACE` — раз в 8–14 с
  играть **либо** `scuttle`, **либо** `membrane` (50/50). Дёшево, разнообразит
  поверхность, не требует новой зоны.
- **B:** оставить `membrane` вне зон, как редкую деталь общего эмбиента
  `hive.ambient` (условие — `insideStructure`, интервал 20–30 с).

**Уровень: `volume 0.30`** (обоснование — в `sound_hive_detail_decision.md`:
медиана фона −24.4 dBFS, детали RMS ≈ −22, при 1.0 они перекроют фон).
Исключение: `detail_flow_01` уже тише остальных (пик **−15.1**, RMS −29.6) —
ему 0.30 даст пик −25.6, почти неслышно. **Рекомендую `flow_01` играть на
`volume 0.45`**, а `flow_02` (пик −7.3) — на 0.30. Это **не подгонка под
норму**, а выравнивание пары: разница в 8 дБ внутри одного события слышна как
«то есть звук, то нет».

**Важно:** `playOneShot` в этом обработчике клиентский (`SimpleSoundInstance`),
поэтому `volume` из `sounds.json` там не применяется автоматически — громкость
задаётся при создании инстанса. Кодеру: смотреть, как `playOneShot` формирует
`SimpleSoundInstance`, и передать 0.30. Если проще — задать `volume` в
`sounds.json` и играть через обычный путь.

---

## Итог по S17

| событие | решение | уровень | точка вызова найдена |
|---|---|---:|---|
| `AMALGAM_SMASH` | привязать | **1.0** | `FleshAmalgamEntity.doHurtTarget` ✓ |
| `SYNAPSE_SHOCK` | привязать | **0.8** | `SynapseNodeBlock.tick` (переход POWER) ✓ |
| `HIVE_SPREAD` | привязать | **0.65** | `VeinMutationEngine.spread` ✓ |
| `CREEPER_RUPTURE` | привязать | **1.0** | `InfectedCreeperEntity.explodeCreeper` ⚠ не компилировал |
| `HIVE_DETAIL_CREAK` | привязать | **0.30** | `HiveAmbientSoundHandler` ZONE_THRESHOLD ✓ |
| `HIVE_DETAIL_SCUTTLE` | привязать | **0.30** | то же, ZONE_SURFACE ✓ |
| `HIVE_DETAIL_BUBBLES` | привязать | **0.30** | то же, ZONE_DEEP ✓ |
| `HIVE_DETAIL_FLOW` | привязать | **0.30 / 0.45 (flow_01)** | то же, ZONE_CORE ✓ |
| `HIVE_DETAIL_MEMBRANE` | привязать | **0.30** | вариант A (слот в SURFACE) или B ✓ |
| `FLAMETHROWER_FIRE` | **оставить заделом** | — | **нет механики огнемёта** |
| `FLESH_AMALGAM_AMBIENT` | **не трогать** | — | уже звучит через `hive.amalgam_breath` ✓ |

**Удалять не нужно ни одного из 11.** Все 15 файлов остаются в банке.

**Проверка после правки (для Кодера):**
`python3 tools/sound_orphans.py <пакет>` → код **0** (сейчас 3);
`python3 tools/accept_3.7.3.py <пакет>` → код **0** (сейчас 1).

## Что я не проверял — говорю прямо

1. **Не компилировал** ни один фрагмент: локальный Gradle-билд мне запрещён.
   Синтаксис и точки вставки сверены по исходникам `01-coder/3.7.3`, но
   `explodeCreeper()` и `SimpleSoundInstance` требуют проверки сборкой.
2. **Не играл в игру.** Частота `spread()` на random-tick оценена по коду, но
   не замерена — от неё зависит, нужен ли ограничитель (пункт 3).
3. **Уровни 0.65 / 0.8** — расчёт от пиков, а не игровой тест. Финальная
   подстройка возможна только на слух в игре, но база считается.
