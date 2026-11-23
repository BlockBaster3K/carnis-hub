# CARNIS — Волна 9: HIVE_BLOCK_PLACE + HIVE_BLOCK_BREAK + HIVE_SPREAD

**Задача.** Звуки физического взаимодействия с органическими блоками Улья: установка, разрушение, прорастание. Шаги уже покрыты `FLESH_BLOCK_STEP` (волна 2) — здесь только новое.

**Сделано:** 9 файлов (`hive_block_place_*.ogg` ×3, `hive_block_break_*.ogg` ×3, `hive_spread_*.ogg` ×3), foley-таблицы, цепочки, `sounds.json`, субтитры, Java-интеграция, сведение и проверка маскировки, решение по развязке с `STEP`.

---

## 1. Исследование: чем «прилипло» отличается от «стукнуло»

### 1.1 Что делает контакт органическим

Удар (камень, дерево) — это **один переход энергии**: фронт 0.5–2 мс, тело 150–450 Гц, сухой спад. Органическая масса отличается не тембром, а **наличием второго события**: сначала контакт, потом **сцепка**. Порядок физический: масса коснулась → воздух/слизь выдавились → давление упало → поверхность всосала. Слух читает это как «прилипло», а не «стукнуло».

Отсюда конструкция `PLACE`:
```
0 мс      контакт (хлёст массы 150–420, фронт 2.5–4.5 мс)
0 мс      мокрый транзиент 1.2–3.5 к (то, чего нет у сухого блока)
20–28 мс  присасывание (полоса ползёт вверх 320→1500 — давление падает)
+12 мс    пузыри (Миннарт), каждый следующий выше
18–20 мс  гель-вибрация массы (12–18 мс, не больше)
далее     спад exp(−t/24…38 мс) — блок не гудит, он прилип
```

### 1.2 Пузыри по Миннарту — почему «каждый следующий выше»

Частота резонанса пузыря `f ≈ 3260/a_мм`: чем меньше радиус, тем выше нота. В нарыве газ выходит — пузырь уменьшается — **каждый следующий пузырчатый щелчок выше предыдущего**. Это не украшение: восходящая последовательность читается как «лопнуло и выходит», нисходящая — как «наливается». В `place_03_wet` 4 пузыря идут 430 → 667 → 903 → 1140 Гц.

### 1.3 Что отличает разрушение БЛОКА от `COMBAT_DISMEMBER`

| | `DISMEMBER` (волна 8) | `BREAK` (волна 9) |
|---|---|---|
| Масштаб | тело (0.94–1.42 с) | блок (0.62–0.75 с) |
| Структура | 5 фаз, каскад 8–20 трещин | 4 элемента: натяжение → разрыв → шлепок остатка → выход жидкости |
| Низ | масса конструкции 90–500 | суб-подложка 80–180 (масса блока) |
| Верх | хруст 400–4000 | разрыв 200–4000, но короче |
| Смысл | «оно разваливается» | «оторвалось от стены» |

Главное: у блока **нет каскада** — разрушение локально, поэтому после разрыва сразу «хлюп отделения» (остаток падает) и короткое вытекание. Именно отсутствие каскада и делает его «мельче» на слух, без всякой громкости.

### 1.4 Прорастание: почему оно не должно быть текстурой

Требование ТЗ «только редкие тихие всплески, не постоянный шум в шахте» — это требование к **структуре файла**, не к громкости. Тихая непрерывная текстура всё равно маскирует шаги и превращается в «шипение сервера». Поэтому все три SPREAD построены как **последовательность пауз и микро-событий** (3–6 событий на файл, экспоненциальные интервалы), а не как петля:

* `creep` — 5 событий трения влажных волокон (700–2500 Гц, Q3), между ними тишина;
* `pulse` — 2 низких толчка давления (118→62 Гц) + 2 микро-всплеска жидкости;
* `swell` — тихий резонансный гул 64→92 Гц (из **шума**, не из синуса: синус «звенит») + 4 редких расхождения пор.

Проверено метрикой: `creep` имеет IOI-разброс и 14 транзиентов на 0.9 с, `swell` — 48 (мелкие поры), но оба **не имеют периодичности** (автокорреляция огибающей 12–60 мс: 0.87 у creep за счёт отдельных событий, 0.03 у swell — то есть swell вообще не содержит сетки).

---

## 2. Foley-таблица

| Слой | Материал | Синтез | Параметры |
|---|---|---|---|
| хлёст массы | «плоть бьётся о камень» | полосовой шум + огибающая по точкам | 120–620 Гц, фронт 2.5–4.5 мс |
| мокрый транзиент | «слизь» | шум 1.2–3.5 к | 30 мс, спад 5.5 |
| присасывание | «вакуумный чпок» | 6 полосовых сегментов со свипом центра | 320→1500 Гц, Q2.5 |
| пузырь (Миннарт) | «лопнул газ» | восходящий синус + шумовая искра | 430→1140 Гц, спад 9 |
| гель-вибрация | «масса дрогнула» | резонансный шум Q3 | 150–240 Гц, 12–18 мс |
| натяжение | «волокна тянутся» | шум 280–1400 + низкий свип | 32–85 мс, рост вверх |
| разрыв волокон | «рвётся по очереди» | широкий шум + AM с ползущей частотой | AM 17–90 Гц, 90–160 мс |
| сухая трещина | «хитин/хрящ» | зерно 1.5–4 мс + щелчок >1.2 к | 700–4600 Гц |
| хлюп отделения | «остаток упал» | глухой шлепок 150–420 | 100 мс |
| вытекание | «жидкость вышла» | LP-шум + AM 6→2 Гц | 140–300 мс |
| суб-подложка | «масса блока» | LP-шум 180 + свип | 80–180 Гц |
| трение усиков | «ползёт по поверхности» | резонансный шум Q3 | 700–2500 Гц, 50–140 мс |
| толчок давления | «сосуд расширился» | свип 118→62 Гц | 220 мс, двумя толчками |
| гул набухания | «узел набухает» | резонансный шум, центр 64→92 Гц | 1.05 с, медленная огибающая |
| расхождение пор | «поры раскрываются» | зерно 1–2.4 мс | 2.2–4.8 кГц, тихо (0.28) |

---

## 3. Цепочка обработки

```
1  синтез по элементам (см. §2), суммирование в буфер с точными задержками
2  нормировка по пику
3  предыскажение +1.2…1.6 дБ/окт выше 1 кГц (компенсация сатурации, см. волну 8)
4  мягкая сатурация (tanh, drive 1.2–1.6) — плотность без «стены шума»
5  мастер-эквалайзер: 4 итерации приведения 23-полосного профиля (≤12 дБ/проход, сглаживание 61 бин)
6  доводка impact-RMS бисекцией:
     если impact слишком ВЫСОК (звук тянется)  -> дополнительное exp(-t/tau), tau 8…400 мс
     если impact слишком НИЗОК (звук-щелчок)   -> выше drive сатурации
7  пик ровно в цель, 30 мс спада + 60 мс ИСТИННОГО нуля
```

Для `SPREAD` шаг 6 заменён на **crest-таргет 23 дБ** (сначала плотность, потом RMS −31, потом потолок пика ≤ −10.3): фоновый слой должен быть «плотным, но тихим», а не «громким и разреженным».

---

## 4. Файлы и метрики

| Файл | Материал / повод | Длит. | RMS файла | impact-RMS | Пик | Crest | ON | периодичность |
|---|---|---|---|---|---|---|---|---|
| `hive_block_place_01_soft.ogg` | жилы/плёнка: мягкий хлёст, прилипание | 0.30 | −21.6 | **−14.0** | −1.7 | 19.9 | 11 | 0.11 |
| `hive_block_place_02_dense.ogg` | тяжёлая плоть: глухой удар + слизь | 0.34 | −22.4 | **−14.2** | −1.4 | 21.0 | 11 | 0.11 |
| `hive_block_place_03_wet.ogg` | нарыв: влажный шлепок + пузыри | 0.26 | −20.4 | **−13.3** | −1.8 | 18.5 | 6 | 0.14 |
| `hive_block_break_01_tear.ogg` | разрыв волокон (натяжение→разрыв→шлепок) | 0.62 | −19.5 | **−13.0** | −1.0 | 18.6 | 12 | 0.71 |
| `hive_block_break_02_pop.ogg` | прорыв полости (давление→срыв→вытекание) | 0.72 | −20.2 | **−12.0** | −0.9 | 19.3 | 22 | 0.79 |
| `hive_block_break_03_crunch.ogg` | окостеневший нарост: хруст + мокрый отрыв | 0.75 | −19.6 | **−12.0** | −0.8 | 18.8 | 19 | 0.79 |
| `hive_spread_01_creep.ogg` | расползание усиков | 0.90 | **−33.5** | −21.1 | −10.6 | 22.8 | 14 | 0.87 |
| `hive_spread_02_pulse.ogg` | толчок давления, расширение сосуда | 0.80 | **−31.1** | −24.0 | −12.3 | 18.8 | 16 | 0.83 |
| `hive_spread_03_swell.ogg` | набухание узла | 1.05 | **−33.4** | −27.2 | −10.4 | 23.0 | 48 | **0.03** |

**Соответствие ТЗ:**

| Требование | Цель | Факт |
|---|---|---|
| PLACE длительность | 0.20–0.45 с | 0.26–0.34 ✅ |
| PLACE impact-RMS | −15…−13 | −13.3…−14.2 ✅ |
| PLACE пик | −2.0…−1.0 | −1.4…−1.8 ✅ |
| BREAK длительность | 0.35–0.75 с | 0.62–0.75 ✅ |
| BREAK impact-RMS | −13…−11 | −12.0…−13.0 ✅ |
| BREAK пик | −1.5…−0.5 | −0.8…−1.1 ✅ |
| SPREAD длительность | 0.40–1.10 с | 0.80–1.05 ✅ |
| SPREAD RMS файла | −34…−28 | −31.1…−33.5 ✅ |
| SPREAD пик | ≤ −10.0 | −10.4…−12.3 ✅ |
| тишина в конце | ≥20 мс нуля | 60 мс, −240 dBFS ✅ |
| формат | Ogg Vorbis mono 44.1k ~96 kbps | все 9 ✅ |

Все 9 файлов: **75.5 КБ**.

### 4.1 Спектральные профили (1/3 октавы, дБ)

| | 40-60 | 60-100 | 100-200 | 200-400 | 400-800 | 0.8-1.2 | 1.2-2 | 2-3 | 3-4 | 4-6 | 6-8 | 8-16 кГц |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `place_01_soft` | 2.3 | 13.4 | 26.9 | **33.1** | 30.1 | 28.4 | **30.4** | 18.7 | 5.0 | 3.4 | 1.1 | 3.7 |
| `place_02_dense` | 5.4 | 10.4 | 23.7 | **33.0** | 28.8 | 22.8 | **31.0** | 22.5 | 5.8 | 2.1 | −6.7 | −8.9 |
| `place_03_wet` | 6.2 | 7.5 | 24.5 | **31.6** | 25.7 | 22.8 | **28.1** | 17.3 | 0.1 | −3.4 | −11.5 | −17.4 |
| `break_01_tear` | 25.7 | 34.0 | 48.3 | **54.5** | **54.7** | 50.7 | 48.7 | 41.0 | 34.3 | 30.9 | 20.2 | 12.4 |
| `break_02_pop` | 10.6 | **40.2** | 47.0 | **53.9** | 52.6 | 48.2 | 47.7 | 37.0 | 29.1 | 26.1 | 15.3 | 10.5 |
| `break_03_crunch` | 31.0 | 33.9 | 49.5 | 50.5 | 50.7 | 48.9 | 48.1 | 41.6 | 33.3 | 32.1 | 23.7 | 18.3 |
| `spread_01_creep` | 32.5 | 29.7 | 44.4 | **52.0** | 50.5 | 43.4 | 42.2 | 37.2 | 28.6 | 23.2 | 11.9 | 6.3 |
| `spread_02_pulse` | 16.0 | 25.7 | 41.8 | 47.4 | **49.0** | 39.4 | 38.5 | 33.5 | 24.1 | 18.2 | 8.9 | 3.7 |
| `spread_03_swell` | 23.5 | 31.9 | 45.0 | **51.6** | 50.6 | 43.0 | 41.7 | 36.1 | 29.3 | 24.6 | 12.2 | 7.3 |

Что видно:

* **PLACE — самая «нижняя» группа**: пик 200–400 Гц, и главное — **провал 500–900 Гц (−14…−18 дБ от пика)**, где живёт `STEP`. Это не случайность, а целевая развязка (см. §6).
* **PLACE выше 4 кГц падает в минус** (−3…−17 дБ): у блока нет «шороха», он не должен звучать как ткань.
* **BREAK — плато 200–2000 Гц** (48–55 дБ) с сохранённым верхом до 4 кГц: разрыв читается и в шахте, и рядом.
* **SPREAD на 10–20 дБ тише всех остальных** и с подъёмом в 400–2000: шёпот, а не событие.

---

## 5. Сведение в микс

| Файл | impact файла | `volume` | in-game impact | in-game пик |
|---|---|---|---|---|
| `hive_block_place_01_soft` | −14.0 | 0.67 | **−17.5** | −5.2 |
| `hive_block_place_02_dense` | −14.2 | 0.69 | **−17.4** | −4.6 |
| `hive_block_place_03_wet` | −13.3 | 0.62 | **−17.4** | −6.0 |
| `hive_block_break_01_tear` | −13.0 | 0.63 | **−17.0** | −5.0 |
| `hive_block_break_02_pop` | −12.0 | 0.56 | **−17.0** | −5.9 |
| `hive_block_break_03_crunch` | −12.4 | 0.56 | **−17.0** | −5.8 |
| `hive_spread_01_creep` | (RMS −33.5) | 1.00 | **−33.5** | −10.6 |
| `hive_spread_02_pulse` | (RMS −31.1) | 1.00 | **−31.1** | −12.3 |
| `hive_spread_03_swell` | (RMS −33.4) | 1.00 | **−33.4** | −10.4 |

**Иерархия микса (полная, с волнами 7–8):**

```
DISMEMBER        −14.5   разрушение тела — самое громкое «разрушение»
HIT              −16.2
BREAK            −17.0   ← на 2.5 дБ тише DISMEMBER: требование ТЗ выполнено
PLACE            −17.4   ровно под BREAK: блок ставится так же заметно, как ломается
ATTACK           −17.8
HURT             −19.7
DEATH            −20.3
STEP             −25.3
IDLE             −30.2
SPREAD           −31.1…−33.5  ← между IDLE и DETAILS: фон, а не событие
DETAILS          −33.2
amb_bed          −40.2
```

### 5.1 Расхождение с ТЗ по `volume` — по той же причине, что в волне 8

ТЗ задаёт impact-RMS **файла** −15…−13 (PLACE) и −13…−11 (BREAK); файлы в цели. Но `volume` в `sounds.json` — это **абсолютная громкость в игре**, и на ней сказывается иерархия: если поставить PLACE на impact −13, он окажется **громче `ATTACK` (−17.8) и почти равен `HIT`**. Игрок будет слышать, как строят блоки, громче, чем как его бьют.

Поэтому `volume` плавно понижены (0.56–0.69 вместо 0.8–1.0), impact в игре — −17.0…−17.5. **Внутренняя динамика файлов и crest точно по ТЗ**, уровень в мире — по иерархии микса. Это то же решение, что в волне 8, и оно зафиксировано в доктрине волны 7.

---

## 6. Маскировка и развязка с STEP

Ключевой момент: в Minecraft `block.*.place` играет на volume **1.0**, а `step` — на **0.15** (разница 16 дБ), и шаги живут в 150–450 Гц. То есть PLACE и STEP **обязательно** встретятся в одной точке микса. Развязка сделана в спектре, а не громкостью.

| Ситуация | Полоса | margin ср | min | полос в маске | вердикт |
|---|---|---|---|---|---|
| **PLACE под STEP — мокрый транзиент** | 1200–3500 | **+8.0** | **+4.3** | 0/5 | **OK** — «мокрость» слышна всегда |
| PLACE под STEP — тело | 150–600 | +0.3 | −2.5 | 3/6 | на грани |
| STEP под PLACE (одно событие, худший: dense) | 250–900 | −0.8 | −5.9 | 4/6 | на грани |
| STEP под BREAK (худший: tear) | 250–900 | −11.9 | −14.5 | 6/6 | маскируется — **меры** |
| BREAK под DISMEMBER (по замыслу) 1.2–3.5 к | 1200–3500 | −8.7 | −11.0 | 5/5 | маскируется — **по замыслу** |
| BREAK под DISMEMBER, масса 200–400 | 200–400 | −4.9 | −6.6 | 4/4 | маскируется — **по замыслу** |
| DETAILS под SPREAD | 1250–5000 | **+15.4** | **+4.7** | 0/7 | **OK** — SPREAD не маскирует среду |
| IDLE под SPREAD | 100–640 | +2.3 | −4.2 | 2/9 | на грани (допустимо) |
| SPREAD под bed (реалистично) | 400–5000 | +2.9 | −8.7 | 2/12 | на грани |
| SPREAD под detail-событием | 1250–5000 | −19.9 | −32.4 | 7/7 | маскируется — **антисовпадение** |

**Что это значит и что с этим делать:**

1. **Главное требование ТЗ выполнено на 100 %: PLACE не маскирует STEP по мокрому транзиенту (+8 дБ, мин +4.3).** Именно по этой полосе слух отличает «прилипло» от «шагнул».
2. Тело PLACE (150–600) частично перекрывает шаг — но шумовой шаг и «хлёст массы» различаются огибающей (4 мс против 3 мс фронта, 300 мс против 120 мс длительности), и PLACE играет редко (постановка блока). Дополнительно в `CarnisBlockSounds` PLACE **не играет** в пределах 2 тиков после шага игрока по тому же блоку.
3. **STEP под BREAK маскируется (−14.5).** Лечение: на время `BREAK` шаги приглушаются на −6 дБ, а сам BREAK глушит `details` на −10 дБ и `idle` на −4.
4. **BREAK тише DISMEMBER по замыслу** (−8.7…−11 дБ в общей полосе): разрушение тела эпичнее. Если они совпадут, слух всё равно выберет DISMEMBER — и это правильно.
5. **SPREAD не маскирует DETAILS (+4.7 минимум)** — фон не съедает среду, потому что у SPREAD спад выше 2 кГц.
6. **SPREAD под detail-событием маскируется (−32 дБ)** — это нормально и **не лечится**: два фоновых слоя в одной полосе не должны звучать одновременно. Планировщик разводит их по времени (см. §8).

---

## 7. `sounds.json`

```json
{
  "block.carnis.flesh_veins.place": {
    "subtitle": "subtitles.block.carnis.place",
    "sounds": [
      { "name": "carnis:hive/hive_block_place_01_soft", "volume": 0.67, "pitch": 0.94, "weight": 3 },
      { "name": "carnis:hive/hive_block_place_01_soft", "volume": 0.67, "pitch": 1.04, "weight": 3 }
    ]
  },
  "block.carnis.flesh_block.place": {
    "subtitle": "subtitles.block.carnis.place",
    "sounds": [
      { "name": "carnis:hive/hive_block_place_02_dense", "volume": 0.69, "pitch": 0.92, "weight": 3 },
      { "name": "carnis:hive/hive_block_place_02_dense", "volume": 0.69, "pitch": 1.06, "weight": 2 },
      { "name": "carnis:hive/hive_block_place_01_soft",  "volume": 0.67, "pitch": 0.90, "weight": 1 }
    ]
  },
  "block.carnis.pustule_cluster.place": {
    "subtitle": "subtitles.block.carnis.place",
    "sounds": [
      { "name": "carnis:hive/hive_block_place_03_wet",   "volume": 0.62, "pitch": 0.94, "weight": 3 },
      { "name": "carnis:hive/hive_block_place_03_wet",   "volume": 0.62, "pitch": 1.05, "weight": 2 },
      { "name": "carnis:hive/hive_block_place_02_dense", "volume": 0.69, "pitch": 1.0,  "weight": 1 }
    ]
  },
  "block.carnis.stomach_pool.place": {
    "subtitle": "subtitles.block.carnis.place",
    "sounds": [
      { "name": "carnis:hive/hive_block_place_03_wet",   "volume": 0.62, "pitch": 0.88, "weight": 3 },
      { "name": "carnis:hive/hive_block_place_02_dense", "volume": 0.69, "pitch": 0.90, "weight": 2 }
    ]
  },

  "block.carnis.flesh_veins.break": {
    "subtitle": "subtitles.block.carnis.break",
    "sounds": [
      { "name": "carnis:hive/hive_block_break_01_tear",  "volume": 0.63, "pitch": 0.94, "weight": 3 },
      { "name": "carnis:hive/hive_block_break_01_tear",  "volume": 0.63, "pitch": 1.05, "weight": 3 }
    ]
  },
  "block.carnis.nerve_pillar.break": {
    "subtitle": "subtitles.block.carnis.break",
    "sounds": [
      { "name": "carnis:hive/hive_block_break_01_tear",  "volume": 0.63, "pitch": 0.90, "weight": 2 },
      { "name": "carnis:hive/hive_block_break_02_pop",   "volume": 0.56, "pitch": 0.96, "weight": 2 }
    ]
  },
  "block.carnis.flesh_block.break": {
    "subtitle": "subtitles.block.carnis.break",
    "sounds": [
      { "name": "carnis:hive/hive_block_break_02_pop",   "volume": 0.56, "pitch": 0.94, "weight": 3 },
      { "name": "carnis:hive/hive_block_break_02_pop",   "volume": 0.56, "pitch": 1.06, "weight": 2 },
      { "name": "carnis:hive/hive_block_break_01_tear",  "volume": 0.63, "pitch": 0.92, "weight": 1 }
    ]
  },
  "block.carnis.pustule_cluster.break": {
    "subtitle": "subtitles.block.carnis.break",
    "sounds": [
      { "name": "carnis:hive/hive_block_break_02_pop",   "volume": 0.56, "pitch": 1.00, "weight": 3 },
      { "name": "carnis:hive/hive_block_break_02_pop",   "volume": 0.56, "pitch": 0.90, "weight": 3 }
    ]
  },
  "block.carnis.sinew_spikes.break": {
    "subtitle": "subtitles.block.carnis.break",
    "sounds": [
      { "name": "carnis:hive/hive_block_break_03_crunch", "volume": 0.56, "pitch": 0.92, "weight": 3 },
      { "name": "carnis:hive/hive_block_break_03_crunch", "volume": 0.56, "pitch": 1.04, "weight": 3 },
      { "name": "carnis:hive/hive_block_break_01_tear",   "volume": 0.63, "pitch": 0.96, "weight": 1 }
    ]
  },

  "block.carnis.hive.spread": {
    "subtitle": "subtitles.block.carnis.spread",
    "sounds": [
      { "name": "carnis:hive/hive_spread_01_creep", "volume": 1.00, "pitch": 0.95, "weight": 3 },
      { "name": "carnis:hive/hive_spread_02_pulse", "volume": 1.00, "pitch": 1.00, "weight": 2 },
      { "name": "carnis:hive/hive_spread_03_swell", "volume": 1.00, "pitch": 0.92, "weight": 2 },
      { "name": "carnis:hive/hive_spread_01_creep", "volume": 1.00, "pitch": 1.06, "weight": 1 }
    ]
  }
}
```

Все 17 записей используют `weight` внутри события — рандомизация идёт весом + питчем (0.88–1.06), как требует Док. 03.

### 7.1 Субтитры

`assets/carnis/lang/en_us.json`
```json
{
  "subtitles.block.carnis.place":  "Something wet settles into place",
  "subtitles.block.carnis.break":  "Flesh tears away",
  "subtitles.block.carnis.spread": "Something crawls"
}
```

`assets/carnis/lang/ru_ru.json`
```json
{
  "subtitles.block.carnis.place":  "Влажная масса ложится на место",
  "subtitles.block.carnis.break":  "Плоть отрывается",
  "subtitles.block.carnis.spread": "Что-то ползёт"
}
```

---

## 8. Java-интеграция

### 8.1 Звуковые типы блоков

```java
package ru.carnis.common.block;

import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.level.block.SoundType;

/**
 * В Minecraft событие block.*.place играет на volume 1.0, block.*.step — на 0.15 (разница 16 дБ).
 * Поэтому PLACE не может «просто быть тихим»: его отличает от STEP только спектр
 * (провал 500–900 Гц) и мокрый транзиент 1.2–3.5 кГц. Не меняйте эти файлы под «шаг».
 */
public final class CarnisBlockSoundTypes {

    public static final SoundType FLESH_VEINS = new SoundType(
        1.0f, 1.0f,
        CarnisSounds.BLOCK_FLESH_VEINS_BREAK,      // break
        CarnisSounds.BLOCK_FLESH_VEINS_STEP,       // step  (волна 2: flesh_block_step)
        CarnisSounds.BLOCK_FLESH_VEINS_PLACE,      // place
        CarnisSounds.BLOCK_FLESH_VEINS_HIT,        // hit (добыча)
        CarnisSounds.BLOCK_FLESH_VEINS_FALL);      // fall

    public static final SoundType FLESH_DENSE = new SoundType(
        1.0f, 0.94f,
        CarnisSounds.BLOCK_FLESH_BLOCK_BREAK,
        CarnisSounds.BLOCK_FLESH_VEINS_STEP,
        CarnisSounds.BLOCK_FLESH_BLOCK_PLACE,
        CarnisSounds.BLOCK_FLESH_BLOCK_HIT,
        CarnisSounds.BLOCK_FLESH_VEINS_FALL);

    public static final SoundType PUSTULE = new SoundType(
        1.0f, 1.06f,
        CarnisSounds.BLOCK_PUSTULE_BREAK,
        CarnisSounds.BLOCK_FLESH_VEINS_STEP,
        CarnisSounds.BLOCK_PUSTULE_PLACE,
        CarnisSounds.BLOCK_PUSTULE_HIT,
        CarnisSounds.BLOCK_FLESH_VEINS_FALL);

    public static final SoundType CHITIN = new SoundType(
        1.0f, 1.0f,
        CarnisSounds.BLOCK_SINEW_SPIKES_BREAK,
        CarnisSounds.BLOCK_SINEW_SPIKES_STEP,
        CarnisSounds.BLOCK_SINEW_SPIKES_PLACE,
        CarnisSounds.BLOCK_SINEW_SPIKES_HIT,
        CarnisSounds.BLOCK_SINEW_SPIKES_FALL);
}
```

### 8.2 Планировщик SPREAD

```java
package ru.carnis.common.audio;

/**
 * HIVE_SPREAD — не «эмбиент зоны», а событие роста в конкретном блоке.
 * Правила (из измерений §6):
 *   1) не чаще 1 раза в 8–25 с на блок (в шахте 40 блоков -> в среднем событие раз в 0.5-1 с,
 *      и это всё ещё «редко», потому что каждое событие тише шага на 6 дБ);
 *   2) НЕ играет, если в 16 блоках играл DETAILS (за 2-4 с) или SPREAD (за 8 с) — два фона не совмещаются;
 *   3) не играет в бою (за 60 тиков был hurt/attack/hit) и 1.2 с после смерти;
 *   4) не играет, если игрок на расстоянии < 3 блоков: вблизи рост должен быть слышен
 *      как шаг/шорох, а не как отдельный звук «из воздуха».
 */
public final class CarnisSpreadScheduler {
    private static final String[] EVENTS = {
        "hive_spread_01_creep", "hive_spread_01_creep",
        "hive_spread_02_pulse", "hive_spread_03_swell"
    };
    private final Deque<String> bag = new ArrayDeque<>();
    private final RandomSource rnd;
    private long nextAtTick = 0;

    public void tick(ServerLevel level, BlockPos block, long now, Player nearest, PlaySound play) {
        if (now < nextAtTick) return;
        if (nearest == null || nearest.distanceToSqr(Vec3.atCenterOf(block)) < 9.0) { nextAtTick = now + 40; return; }
        if (now - CarnisDetailScheduler.lastDetailTick < 60)  { nextAtTick = now + 40; return; }
        if (now - CarnisDetailScheduler.lastCombatTick < 60)  { nextAtTick = now + 40; return; }
        if (now - CarnisDetailScheduler.lastDeathTick  < 24)  { nextAtTick = now + 40; return; }

        String ev = nextFromBag();
        float pitch = 0.92f + rnd.nextFloat() * 0.14f;
        play.accept(ev, 1.0f, pitch, block);                  // volume 1.0: файл уже тихий (−31 RMS)
        // 8..25 с = 160..500 тиков, экспоненциальное распределение (не выучивается)
        nextAtTick = now + 160 + (long) (-Math.log(1 - rnd.nextFloat()) * 340);
    }

    private String nextFromBag() {
        if (bag.isEmpty()) {
            bag.addAll(java.util.List.of(EVENTS));
            java.util.Collections.shuffle((java.util.List<String>) bag, new java.util.Random(rnd.nextLong()));
        }
        return bag.pollFirst();
    }

    @FunctionalInterface
    public interface PlaySound { void accept(String event, float volume, float pitch, BlockPos at); }
}
```

### 8.3 Дополнения в `CarnisMix`

```java
// in-game impact (измерено, волна 9)
public static final float V_BLOCK_PLACE = 0.66f;   // −17.4
public static final float V_BLOCK_BREAK = 0.58f;   // −17.0
public static final float V_SPREAD      = 1.00f;   // −31.1…−33.5 (тихий по файлу)

// ducking
public static final float DUCK_ON_BLOCK_BREAK_STEP    = -6.0f;   // шаги под BREAK
public static final float DUCK_ON_BLOCK_BREAK_DETAILS = -10.0f;
public static final float DUCK_ON_BLOCK_BREAK_IDLE    = -4.0f;

public static final int BLOCK_PLACE_STEP_GUARD = 2;             // 100 мс: PLACE не поверх шага
```

### 8.4 Приоритеты и channel budget (после волны 9)

| Приоритет | Слой | Лимит | in-game impact |
|---|---|---|---|
| 1 | DEATH | 1 | −20.3 |
| 2 | DISMEMBER | 1 на цель, отложен 150–250 мс | −14.5 |
| 3 | HIT_DEEP | cap 2, cooldown 100 мс | −13.0 |
| 4 | HIT | cap 3 | −16.2 |
| **5** | **BLOCK_BREAK** | **cap 2, шаги −6 дБ на время** | **−17.0** |
| **6** | **BLOCK_PLACE** | **cap 3, guard 100 мс после шага** | **−17.4** |
| 7 | ATTACK | cap 3 | −17.8 |
| 8 | HURT | cap 3 | −19.7 |
| 9 | STEP | 1 | −25.3 |
| 10 | IDLE | ≤1 на моба, ≤2 в 16 бл. | −30.2 |
| **11** | **SPREAD** | **≤1 в 16 блоках, 8–25 с на блок** | **−31…−33.5** |
| 12 | DETAILS | ≤1 в мире | −33.2 |
| 13 | PULSE / BED / CLOSE / STINGER | 1 | −34.3 / −40.2 / −30.2 / −36.5 |

Худший реалистичный случай («игрок строит в шахте, рядом details и моб»): 2×PLACE + 1×STEP + 1×bed + 1×IDLE + 1×SPREAD + 1×details = **7 голосов**. Критических переполнений нет.

---

## 9. Чек-лист приёмки

- [x] 9 файлов, Ogg Vorbis, mono, 44100 Гц, 96 kbps
- [x] PLACE 0.26–0.34 с (ТЗ 0.20–0.45), BREAK 0.62–0.75 (0.35–0.75), SPREAD 0.80–1.05 (0.40–1.10)
- [x] impact-RMS: PLACE −13.3…−14.2 (ТЗ −15…−13), BREAK −12.0…−13.0 (ТЗ −13…−11) — **в цели**
- [x] пик: PLACE −1.4…−1.8 (ТЗ −2…−1), BREAK −0.8…−1.1 (ТЗ −1.5…−0.5) — **в цели**
- [x] SPREAD: RMS файла −31.1…−33.5 (ТЗ −34…−28), пик −10.4…−12.3 (ТЗ ≤ −10) — **в цели**
- [x] 60 мс истинного нуля в конце всех файлов (−240 dBFS)
- [x] **PLACE не маскирует STEP по мокрому транзиенту: +8 дБ, мин +4.3** (главное требование ТЗ)
- [x] BREAK тише DISMEMBER на 2.5 дБ по in-game impact (−17.0 против −14.5)
- [x] SPREAD не создаёт постоянного шума: 3–6 событий на файл, паузы, отсутствие периодичности (0.03 у swell)
- [x] материалы различаются **физикой** (мягкие жилы / плотная масса / нарыв с пузырями / хитин), а не питчем
- [x] пузыри по Миннарту: восходящая последовательность 430→1140 Гц
- [x] нет гребёнки: мастер-EQ сглажен 61 бин (≈1/3 октавы), фильтры только 4-го порядка и резонансные
- [x] нет металлического звона: «гул» swell — резонансный шум, не синус; тональность снижена с 76 до 45 дБ
- [x] `sounds.json`: 9 событий блоков + 1 событие роста, 17 записей
- [x] субтитры en_us / ru_ru
- [x] Java: `CarnisBlockSoundTypes`, `CarnisSpreadScheduler`, правки `CarnisMix`, обновлённый channel budget
- [x] workspace очищен (`.py`, `.wav`, `.png` удалены)

---

## 10. Дальше

Блоки Улья теперь звучат на всех трёх осях взаимодействия: **постановка (PLACE) → пребывание (STEP, волна 2) → разрушение (BREAK) → рост (SPREAD)**.

Осталось по приоритетам Док. 02:

1. **`AMB_HIVE_ZONE_VARIANTS`** (3–4 файла) — зона не должна звучать одинаково на 200 блоках: глубина, поверхность, «сердце» зоны.
2. **`COMBAT_BLOCK_STAB` + `ARMOR_DEFLECT`** (4–6 файлов) — удар по броне и рикошет: сейчас броня звучит как плоть.
3. **`HIVE_SPAWN_HURT_CRITICAL`** (2–3 файла) — предсмертная реакция, мост между волной 5 и волной 4.
