# Звук — дельта-манифест по диску + предложение по `bone_scythe` (волна 29)

**Роль:** Звук · **Дата:** 2026-11-25 · **Коммит чтения доски:** `3b828411d39bde38fbf24d3e030619a4bb8e5ec6`
**Коммит, на котором сдана работа:** `00fec999732dd13921be73af85971a331f8513f0` + этот коммит
**Handshake:** `00-board/reports/sound_handshake.md`

---

## 1. Задача 1 — дельта-манифест пересобран по диску

**Файл:** `03-sound/transfer/SHA256SUMS_delta22.txt`
**SHA-256 самого манифеста:** `c3d4994313159ed8c4a3a3577db138495d02aa4e9610b0abb89ccebf3d1a98c7`
**Проверка:** `cd 03-sound/sounds && sha256sum -c ../transfer/SHA256SUMS_delta22.txt` → **4/4 OK, 0 FAILED**, строк в манифесте **4** = файлов **4**.

### 1.1 Все три расхождения — старая и новая строка рядом

| # | было (старый манифест) | стало (по диску) | природа расхождения |
|---|---|---|---|
| 1 | `17f42e30…  block/pulsing_heart_beat.ogg` | `17f42e30…  block/heart_pulse.ogg` | **имя, не хеш.** Файла `block/pulsing_heart_beat.ogg` в банке нет — он был побайтовым дублем и удалён в волне 27, потому что `sounds.json` читает `carnis:block/heart_pulse`. Хеш и размер (10 926 Б) те же |
| 2 | `7e472bc9…  combat/bone_scythe_swing_01.ogg` | `11cbb014d7dfb63b723c50183924f0251e2f8a1b355805f38589b180630f28fa  combat/bone_scythe_swing_01.ogg` | **неверный хеш** (манифест от ранней редакции файла). На диске 11 167 Б |
| 3 | `f3b97dd1…  combat/bone_scythe_hit_01.ogg` | `b0f6504a97bf8739cd972c16d245665795a24ab4ab71ed3253de49694c411722  combat/bone_scythe_hit_01.ogg` | **неверный хеш**. На диске 7 458 Б |

Полное содержимое нового манифеста:

```
39de4db0d9938af9dba8b1f6b637988003410dd7daf85b17df8284c49a513079  block/heartbeat_loop.ogg
17f42e3076ee1d0bc8212ea4d817d43ac3e78ebbee8d6c7544e87b4832f7e905  block/heart_pulse.ogg
11cbb014d7dfb63b723c50183924f0251e2f8a1b355805f38589b180630f28fa  combat/bone_scythe_swing_01.ogg
b0f6504a97bf8739cd972c16d245665795a24ab4ab71ed3253de49694c411722  combat/bone_scythe_hit_01.ogg
```

**Файлы не менялись** — правился только документ. `block/heartbeat_loop.ogg` в манифесте не изменился (`39de4db0…`), это ожидаемо: он и был верен.

**Заодно приведён `03-sound/transfer/PACKAGE_352_360.txt`** — в нём стояло мёртвое имя `block/pulsing_heart_beat.ogg`; теперь `block/heart_pulse.ogg`, добавлена строка про проверку и пометка, что пара косы не идёт в overlay до объявления событий.

### 1.2 Состояние банка на момент сдачи

| проверка | результат |
|---|---|
| `python3 tools/sound_check.py 03-sound` | 159 файлов, `SHA256SUMS_all` 159/159, `MANIFEST_ogg` 159/159, `wave22` 4/4, дублей нет — **все проверки пройдены** |
| `sha256sum -c ../SHA256SUMS_delta22.txt` | 4/4 OK, 0 FAILED |
| формат моих 4 файлов | Vorbis / 44 100 Гц / моно / 160 kb/s, без метаданных |

---

## 2. Задача 2 — предложение по `bone_scythe` к 3.6.0 (НЕ сдача)

Полный текст — **`03-sound/PROPOSAL_bone_scythe_3.6.0.md`**. Ничего в 3.5.3 не сдано, `sounds.json` не тронут.

### 2.1 Готовая запись (два события)

```json
"item.bone_scythe.swing": {
  "subtitle": "carnis.subtitle.bone_scythe_swing",
  "sounds": [ { "name": "carnis:combat/bone_scythe_swing_01", "stream": false } ]
},
"item.bone_scythe.hit": {
  "subtitle": "carnis.subtitle.bone_scythe_hit",
  "sounds": [ { "name": "carnis:combat/bone_scythe_hit_01", "stream": false } ]
}
```

`pitch` / `volume` **не задавать**: тембр уже задаёт `ScytheItem` (`soundPitch 1.15F`, `soundVolume 0.8F`, `ModItems.java:153–155`). Запись тех же чисел в декларацию даст **произведение** — 0.8 × 0.8 = 0.64 по громкости и 1.15 × 1.15 ≈ 1.32 по высоте, то есть косу уведёт в другой регистр и на −4 дБ.

### 2.2 ⚠️ Требование Кодеру — иначе события мёртвые

Проверено по коду пакета `3.5.3`, не по описанию:

| место | факт |
|---|---|
| `ScytheItem.java:42` (`hurtEnemy`) | играет `ModSounds.OSSIFIED_SCYTHE_HIT` для **любой** косы |
| `CombatItemEvents.java:42` (`onScytheAirSwing`) | играет `ModSounds.OSSIFIED_SCYTHE_SWING` |
| `CombatItemEvents.java:49` (`playWorldSwing`) | тоже `OSSIFIED_SCYTHE_SWING` |

Без правки кода `item.bone_scythe.*` не вызовутся **ни разу**: файлы в jar есть, звук не играет, и это не поймает ни CI, ни шаг `Verify overlay reached the jar` (он проверяет наличие пути, а не факт вызова).

**Что нужно:** два поля-события у `ScytheItem` (`hitSound` / `swingSound` + геттеры — по образцу уже существующих `soundPitch` / `soundVolume`), заполнение в `ModItems` для обеих кос, три вызова переводятся на геттеры. Плюс два `RegistryObject<SoundEvent>` в `ModSounds` (по образцу `ModSounds.java:174`) и два ключа субтитров в локалях. Альтернатива без смены сигнатуры — выбор события по `stack.getItem()`, но это то же зашитое знание, от которого уходим.

### 2.3 Строки для overlay (только в 3.6.0, после объявления событий)

```
03-sound/sounds/combat/bone_scythe_swing_01.ogg -> src/main/resources/assets/carnis/sounds/combat/bone_scythe_swing_01.ogg | 11cbb014d7dfb63b723c50183924f0251e2f8a1b355805f38589b180630f28fa
03-sound/sounds/combat/bone_scythe_hit_01.ogg -> src/main/resources/assets/carnis/sounds/combat/bone_scythe_hit_01.ogg | b0f6504a97bf8739cd972c16d245665795a24ab4ab71ed3253de49694c411722
```

**Раньше — не вносить:** файлы уже в `03-sound/**`, и строки в overlay до объявления событий дадут в jar двух сирот — ровно то, чего избежали в волне 27. CI такого не ловит.

### 2.4 Отличие от тяжёлой косы — числа (сняты `tools/sound_metrics.py`, ffmpeg-путь)

| метрика | лёгкая | тяжёлая | вывод |
|---|---|---|---|
| замах, с | **0.437** | 0.717 | −39 % |
| удар, с | **0.337** | 0.597 | −44 % |
| центр замаха | **2412 Гц** | 1918 Гц | светлее на 494 Гц |
| центр удара | **1124 Гц** | 1267 Гц | суше |
| RMS замах / удар | −18.56 / −18.52 | −18.04 / −18.57 | одинаковая громкость |
| < 120 Гц, удар | **0.01 %** | **4.19 %** | у лёгкой нет низкочастотного веса |
| хвост тишиной | 0.10 / 0.21 с | 0.00 / 0.00 с | у лёгкой чище |

Правило пары выполнено: разница в **весе** (длина + отсутствие низа), а не в громкости.

---

## 3. Что осталось непроверенным

1. **Звучит ли пара в игре** — до 3.6.0 непроверяемо: события не объявлены, `ScytheItem` жёстко зашит на `OSSIFIED_SCYTHE_*`.
2. **Не проверял, играет ли коса сейчас два звука одновременно** (`SwordItem#hurtEnemy` может добавлять ванильный `ENTITY_ATTACK`). Это вопрос Кодеру, файлов не касается — но если так, это может быть частью жалобы «коса без звука».
3. **`crest` в `tools/sound_metrics.py` считается как отношение амплитуд** (5.6 / 6.3 / 4.5 / 6.0), а в моих отчётах по банку crest всегда в **дБ** (15.0 / 16.0 / 13.1 / 15.5) — это те же числа, 20·log₁₀. Не расхождение, но при сверке выглядит им; предложение — печатать в инструменте оба значения (правка не моя зона).
4. **`tools/sound_metrics.py` без ffmpeg** (как в окружении агента по умолчанию) не декодирует OGG и печатает «полного декодера Vorbis в чистом Python нет». Метрики выше сняты с ffmpeg в `PATH`. Это не дефект сдачи, но знать надо: цифры из этого файла без ffmpeg получить нельзя.

---

## 4. Что сдано в этой волне (пути и хеши)

| путь | что | SHA-256 |
|---|---|---|
| `03-sound/transfer/SHA256SUMS_delta22.txt` | дельта-манифест по диску, 4 строки | `c3d4994313159ed8c4a3a3577db138495d02aa4e9610b0abb89ccebf3d1a98c7` |
| `03-sound/transfer/PACKAGE_352_360.txt` | состав дельты, мёртвое имя заменено | (текстовый, в репо) |
| `03-sound/PROPOSAL_bone_scythe_3.6.0.md` | предложение по косе для 3.6.0 | (текстовый, в репо) |
| `00-board/reports/sound_delta_manifest.md` | этот отчёт | — |

**Звуковых файлов в этой волне не создавалось и не менялось: 0.** Overlay не правился (зона Интегратора). `sounds.json` не правился (зона Кодера).
