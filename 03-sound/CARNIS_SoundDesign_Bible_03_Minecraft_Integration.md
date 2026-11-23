# CARNIS: ADAPTIVE HIVEMIND — ЗВУКОВАЯ БИБЛИЯ
### Документ 3 из 3: Интеграция в Minecraft Forge 1.20.1
**Версия:** 1.0 · **Неймспейс:** `carnis`

---

## 1. Структура ассетов

```
src/main/resources/
└── assets/carnis/
    ├── sounds.json
    ├── lang/en_us.json            # сабтайтлы
    ├── lang/ru_ru.json
    └── sounds/
        ├── hive/
        │   ├── spawn_idle_01.ogg ... spawn_idle_06.ogg
        │   ├── spawn_alert_01.ogg ... spawn_alert_06.ogg
        │   ├── walker_step_01.ogg ... walker_step_08.ogg
        │   └── ...
        ├── flesh/
        │   ├── block_step_01.ogg ...
        │   ├── block_break_01.ogg ...
        │   ├── node_pulse_calm.ogg
        │   └── details/ (drip_flesh_01.ogg ...)
        ├── amb/
        │   ├── zone_bed_low.ogg / zone_bed_mid.ogg / zone_bed_high.ogg
        │   └── cavern_bed_abyss.ogg
        ├── combat/
        ├── player/
        ├── music/
        ├── ui/
        └── boss/
```

**Правила имён:** только `a-z0-9_`, без пробелов и декоративных символов; версия/вариант — числом в конце (`_01`); назначение — префиксом (`_distant`, `_wet`, `_phase3`).

---

## 2. sounds.json — рабочий шаблон

```json
{
  "hive.spawn.idle": {
    "subtitle": "carnis.subtitle.hive_spawn_idle",
    "sounds": [
      { "name": "carnis:hive/spawn_idle_01", "volume": 0.55, "pitch": 1.0, "weight": 1 },
      { "name": "carnis:hive/spawn_idle_02", "volume": 0.55, "pitch": 0.98, "weight": 1 },
      { "name": "carnis:hive/spawn_idle_03", "volume": 0.55, "pitch": 1.02, "weight": 1 },
      { "name": "carnis:hive/spawn_idle_04", "volume": 0.55, "pitch": 1.0, "weight": 1 },
      { "name": "carnis:hive/spawn_idle_05", "volume": 0.55, "pitch": 0.96, "weight": 1 },
      { "name": "carnis:hive/spawn_idle_06", "volume": 0.55, "pitch": 1.04, "weight": 1 }
    ]
  },

  "combat.flesh_hit": {
    "subtitle": "carnis.subtitle.combat_flesh_hit",
    "sounds": [
      { "name": "carnis:combat/flesh_hit_01", "pitch": 1.0 },
      { "name": "carnis:combat/flesh_hit_02", "pitch": 0.95 },
      { "name": "carnis:combat/flesh_hit_03", "pitch": 1.05 },
      { "name": "carnis:combat/flesh_hit_04", "pitch": 0.92 },
      { "name": "carnis:combat/flesh_hit_05", "pitch": 1.08 },
      { "name": "carnis:combat/flesh_hit_06", "pitch": 1.0 },
      { "name": "carnis:combat/flesh_hit_07", "pitch": 0.98 },
      { "name": "carnis:combat/flesh_hit_08", "pitch": 1.02 },
      { "name": "carnis:combat/flesh_hit_09", "pitch": 1.1 },
      { "name": "carnis:combat/flesh_hit_10", "pitch": 0.9 },
      { "name": "carnis:combat/flesh_hit_11", "pitch": 1.06 },
      { "name": "carnis:combat/flesh_hit_12", "pitch": 0.94 }
    ]
  },

  "amb.hive.zone_bed": {
    "sounds": [
      { "name": "carnis:amb/zone_bed_low",  "stream": true, "volume": 0.30, "pitch": 1.0, "weight": 1 },
      { "name": "carnis:amb/zone_bed_mid",  "stream": true, "volume": 0.38, "pitch": 1.0, "weight": 1 },
      { "name": "carnis:amb/zone_bed_high", "stream": true, "volume": 0.45, "pitch": 1.0, "weight": 1 }
    ]
  },

  "amb.hive.detail.drip_flesh": {
    "sounds": [
      { "name": "carnis:amb/details/drip_flesh_01", "volume": 0.35, "pitch": 1.0 },
      { "name": "carnis:amb/details/drip_flesh_02", "volume": 0.35, "pitch": 0.94 },
      { "name": "carnis:amb/details/drip_flesh_03", "volume": 0.35, "pitch": 1.06 },
      { "name": "carnis:amb/details/drip_flesh_04", "volume": 0.35, "pitch": 0.9 },
      { "name": "carnis:amb/details/drip_flesh_05", "volume": 0.35, "pitch": 1.1 }
    ]
  },

  "boss.hivemind.breath": {
    "sounds": [
      { "name": "carnis:boss/hivemind_breath_p1", "stream": true, "volume": 0.5, "pitch": 1.0 },
      { "name": "carnis:boss/hivemind_breath_p2", "stream": true, "volume": 0.5, "pitch": 1.0 }
    ]
  }
}
```

**Важно:** `volume`/`pitch` в `sounds.json` — статические (не рандом!). Рандомизация достигается *разными значениями `pitch` у разных файлов* + кодом (`playSound` с `random.nextFloat()`). Диапазоны `pitch` в спецификациях — это рекомендация для этих значений и для кода.

**Lang-файл (без спойлеров):**
```json
{
  "carnis.subtitle.hive_spawn_idle": "Carnis breathes",
  "carnis.subtitle.hive_spawn_alert": "Something notices you",
  "carnis.subtitle.player_sanity_whisper": "Someone whispers",
  "carnis.subtitle.amb_tension_accent": "Something moved"
}
```

---

## 3. Билд-пайплайн (WAV → OGG)

Скрипт `tools/build_sounds.sh` (в репозитории): конвертирует мастер-WAV 96/48 кГц в OGG Vorbis моно 44.1 кГц с нормализацией пика.

```bash
# один файл
ffmpeg -i master.wav -ac 1 -ar 44100 -c:a libvorbis -q:a 5 -af "loudnorm=I=-18:TP=-1.0:LRA=7" out.ogg

# пачкой
for f in masters/*.wav; do
  ffmpeg -y -i "$f" -ac 1 -ar 44100 -c:a libvorbis -q:a 5 \
    -af "loudnorm=I=-18:TP=-1.0:LRA=7" "out/$(basename "${f%.wav}").ogg"
done
```

**Целевые уровни (LUFS-I):**

| Тип | LUFS-I | TP |
|---|---|---|
| One-shot SFX (атаки, импакты) | −16…−18 | −1.0 |
| Детали/акценты эмбиента | −22…−24 | −1.0 |
| Bed-петли | −24…−26 | −1.0 |
| Музыка | −17…−19 | −1.0 |
| Босс (рёв) | −14…−16 | −1.0 |

> Внутренняя динамика внутри файла **важнее** общего уровня: `loudnorm` с LRA 7–11 для SFX, чтобы не «сплющить» транзиенты. Для хрустов и импактов — не использовать лимитер сильнее −3 дБ GR.

**Проверка перед сборкой (обязательно):**
```bash
ffprobe -hide_banner out.ogg        # channels=1, sample_rate=44100, codec=vorbis
```

---

## 4. Регистрация событий (Forge 1.20.1)

```java
public final class CarnisSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS =
        DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, Carnis.MODID);

    public static final Holder<SoundEvent> HIVE_SPAWN_IDLE = reg("hive.spawn.idle");
    public static final Holder<SoundEvent> COMBAT_FLESH_HIT = reg("combat.flesh_hit");
    public static final Holder<SoundEvent> AMB_ZONE_BED     = reg("amb.hive.zone_bed");
    // ...

    private static Holder<SoundEvent> reg(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(
            new ResourceLocation(Carnis.MODID, name)));
    }
}
```

`createVariableRangeEvent` = затухание по расстоянию (`attenuation_distance`, кап 16). `createFixedRangeEvent` — без затухания (для UI/музыки).

---

## 5. Адаптивная система: 3 контроллера

### 5.1 Corruption director (уровень заражения зоны)

Читает `corruption` (0..100) в чанке/зоне и управляет:
- выбором bed-петли (`low` <35, `mid` 35–70, `high` >70) с кроссфейдом 3 с;
- частотой деталей (гауссов интервал, см. ниже);
- темпом `FLESH_NODE_PULSE` (файлы, не питч!);
- вероятностью «злых» акцентов.

```java
float c = ZoneCorruption.get(player.level(), player.blockPosition()); // 0..100
float detailRate = Mth.lerp(c / 100f, 1f / 90f, 1f / 25f); // событий в секунду
```

### 5.2 Detail scheduler (гауссовы интервалы вместо таймера)

Ключевой приём против repetition fatigue: интервал **не фиксирован**, а нормально распределён.

```java
private long nextDelay(RandomSource rnd, float meanSeconds) {
    // N(mean, 0.35*mean), обрезка в [0.4*mean, 2.2*mean]
    float sigma = meanSeconds * 0.35f;
    float v = meanSeconds + (float) rnd.nextGaussian() * sigma;
    v = Mth.clamp(v, meanSeconds * 0.4f, meanSeconds * 2.2f);
    return (long) (v * 20); // в тиках
}
```

Плюс **anti-repeat guard**: последние 3 сыгранных ID деталей хранятся в `Deque`; новый выбор исключает их (и 20% времени — принудительная пауза без звука вообще: «absence», см. Док. 01 §4.2).

### 5.3 Channel budget (защита от обрывов)

Движок не сообщает о нехватке каналов — считаем сами, на клиенте:

```java
// глобальный бюджет «наших» звуков
private static final int MAX_CONCURRENT = 16;
private static final Map<ResourceLocation, int[]> ACTIVE = new HashMap<>();

static boolean canPlay(ResourceLocation id, int perEventCap) {
    int total = ACTIVE.values().stream().mapToInt(a -> a[0]).sum();
    int mine  = ACTIVE.getOrDefault(id, new int[]{0})[0];
    return total < MAX_CONCURRENT && mine < perEventCap;
}
```

Правила бюджета:
- глобально ≤16 одновременных «наших» источников в радиусе слышимости;
- ≤6–8 экземпляров одного события (`COMBAT_FLESH_HIT` — исключение: ≤4 и cooldown 50 мс);
- ≤2 bed-петли одновременно (кроссфейд заменяет, а не суммируясь);
- приоритет при переполнении: BOSS > HIVE (угроза) > COMBAT > PLAYER > AMB > детали. Детали дропаются первыми.

> Для справки: OpenAL Soft даёт до 256 источников; MC делит их на ~247 статических + ~8 стриминговых. В плотной сцене ваниль уже ест десятки — поэтому бюджет обязателен.

### 5.4 Ducking (нет в движке — делаем сами)

За 0.5 с до пикового события (атака, рёв, dismember) временно снижаем громкость bed-петель и музыки на −10…−12 дБ, через 1.2 с после — плавный возврат за 1.5 с. Реализация: `TickableSoundInstance` с изменяемым `volume()` для bed/музыки + серверный/клиентский флаг `duckUntil`.

```java
public class BedSound extends TickableSoundInstance {
    private float target = 1f, current = 1f;
    @Override public void tick() {
        current = Mth.lerp(0.05f, current, target);
        this.volume = baseVolume * current;
    }
    public void duck(float db) { target = Mth.clamp(1f - db / 40f, 0.1f, 1f); }
}
```

---

## 6. Карта триггеров (кто вызывает что)

| Событие в игре | Звук | Сторона | Примечание |
|---|---|---|---|
| Спавн существа | — (тишина 0.6 с) | — | **Намеренно:** не озвучивать спавн; пусть первый звук будет `IDLE`/`ALERT` |
| Игрок в 4–16 блоках от Spawn, кулдаун | `HIVE_SPAWN_IDLE` | Server → `playSound` по позиции | cooldown 22–45 с |
| Обнаружение игрока (AI target set) | `HIVE_SPAWN_ALERT` | Server | 1 раз на агро |
| Атака (hit-момент) | `HIVE_SPAWN_ATTACK` | Server | промах → `_02` |
| Смерть | `HIVE_SPAWN_DEATH` | Server | |
| Шаг Walker (по анимации/расстоянию) | `HIVE_WALKER_STEPS` | Server | по каждому шагу цикла |
| Разрушение блока биомассы | `FLESH_BLOCK_BREAK` | Client (`BlockEvent`) | + `FLESH_VEIN_TEAR` при разрушении узла |
| Шаг по `flesh_block` | `FLESH_BLOCK_STEP` | Client (`playStepSound`) | bank 8, pitch 0.90–1.10 |
| Попадание по Улью | `COMBAT_FLESH_HIT` | Server | cooldown 50 мс, cap 4 |
| Расчленение | `COMBAT_DISMEMBER` | Server | |
| `corruption` delta | `AMB_*` переключение | Client (director) | кроссфейд 3 с |
| Заражение ≥10% / ≥60% | `PLAYER_INFECTION_*` | Client (personal) | non-positional |
| Рассудок < порога | `PLAYER_SANITY_WHISPER` | Client | интервал гауссов |
| Первое появление босса | `BOSS_HIVEMIND_BREATH` → `ROAR` | Server + клиент-стрим | |

---

## 7. Подводные/закрытые пространства

- Под водой MC применяет LP-фильтр ко всему — у `HIVE_*` не должно быть смысла в 6–14 кГц (иначе «пропадёт»).
- Для помещений зон: применяйте разные bed-петли (`_cavern`, `_flooded`), а не меняйте один файл — движок не умеет фильтровать по зоне.
- Мембранные проходы (`FLESH_MEMBRANE_PASSAGE`) — единственный корректный способ «сменить акустику»: два события (`_out` сухое, `_in` гулкое) + смена bed-петли.

---

## 8. Чек-лист интеграции (перед релизом волны)

- [ ] `ffprobe`: все файлы — Vorbis, 44100, **mono**, ≤3.5 LU расхождения по типам.
- [ ] Нет файлов с тишиной >20 мс в начале (иначе задержка воспринимается как «баг»).
- [ ] Для каждого события существует `subtitle` в `en_us.json` и `ru_ru.json` (без спойлеров).
- [ ] `attenuation_distance` ≤16 везде, где нужно затухание.
- [ ] Проверка в игре: 4 / 8 / 16 блоков; в бою с 5+ мобами; с музыкой; с открытым инвентарём.
- [ ] 10 минут ходьбы по заражённой зоне: ни один файл не узнан повторно в схожем контексте.
- [ ] Channel budget: в худшей сцене (босс + 6 мобов + бой) число одновременных ≤16, обрывов нет.
- [ ] Тест на ноутбучных динамиках и в наушниках: смысл (приближение, угроза) читается в обоих.
- [ ] Итоговый вес папки `sounds/`: SFX ≤ 25–30 МБ; эмбиенты/музыка — стрим, отдельно.

---

## 9. Ограничения, которые надо принять (и не бороться)

1. Нет оффсета старта файла → петли «слышны», лечится длиной (150 с+) и гранулярной сборкой.
2. Нет фильтров/эквалайзера в данных → «за стеной» = отдельные обрезанные файлы.
3. Нет ducking → только код.
4. Питч меняет длительность → для «реалистичных» звуков узкий диапазон.
5. 16 блоков — предел слышимости позиционного события → дальние акценты играем non-positional.
6. Стерео не позиционируется → только моно для мира; стерео — только музыка.
7. Игрок может выключить `AMBIENT` слайдер → критичные сигналы держим в `HOSTILE`, не в `AMBIENT`.
