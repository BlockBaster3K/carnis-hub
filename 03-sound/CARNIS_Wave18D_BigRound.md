# CARNIS · Волна 18D — большой раунд (версия 3.4.5)

**Пункт 0 (закрытие счёта) принят:** база 135 OGG / 11 592 878 Б / 136 строк манифеста — зафиксирована, ничего не «догоняю».

**Итог раунда: банк 151 OGG / 11 902 487 байт, манифест 152 строки (151 + заголовок), расхождений манифест↔диск 0, формат vorbis/44100/mono 151/151.**

---

## 0. Что сделано по пунктам заказа

| Пункт | Статус |
|---|---|
| 1. Синхропакет (SHA256 по всем, манифест, таблицы) | **сделано** — §1 |
| 2. Декларации для 14 событий (текст, `sounds.json` не правится) | **сделано** — §2 |
| 3. Новые звуки 3.5.0 | **сделано: 12 файлов** (заказ — минимум 8) — §3 |
| 4. Тишина R9 | **сделано:** 8 из 11 файлов уже были; 3 реально отсутствовали и сгенерированы (класс A) — §4 |
| 5. Сводная метрика банка | **сделано** — отдельный файл `CARNIS_Wave18D_BankQA.md` (151 строка) |
| 6. Отчёт | этот документ, `build/` удалён |

---

## 1. Синхронизационный пакет

### 1.1 Что отдаю

| Файл | Содержимое |
|---|---|
| `MANIFEST_ogg.txt` | **152 строки** (151 файл + заголовок), сверено с диском, 0 расхождений |
| `SHA256SUMS_all.txt` | **новый файл**, 151 строка, SHA256 по всем файлам банка; прежний `SHA256SUMS.txt` (4 строки, 18C + phantom) **не тронут** |
| `CARNIS_Wave18D_BankQA.md` | сводная QA-таблица: путь/байт/длит/RMS/Peak/Crest/Tonal/Persist/Center/Onset/AM/кбит/флаги по всем 151 |
| `transfer/CARNIS_transfer_86.tar.gz` | 86 файлов (74 прежних + 12 новых), подпапки сохранены, 10 404 802 Б распакованных |

### 1.2 Таблица «12 файлов ПЕРЕЗАПИСАТЬ» — **пересчитана, и причина другая**

Перезаписаны будут ровно **14**, а не 12. Все они — из архива 18A (`*_w1516`), и в проекте на этих путях сейчас лежат **файлы волн 15/16**. Это не догадка: предупреждение Q7 (§115 «Диффпрепа») прямо говорит, что по этим 14 именам у Кодера старые файлы. Подтверждение с моей стороны — размеры: старые 17 363…44 121 Б, мои 11 723…47 090 Б.

| # | Путь в проекте | старый размер | старый SHA256 (12) | новый размер | новый SHA256 (12) | Δ |
|---|---|---|---|---|---|---|
| 1 | `hive/amalgam_breath_01.ogg` | 38 235 | `a44f5fec5eb3…` | 38 924 | `88faa04fb83a…` | +689 |
| 2 | `hive/amalgam_breath_02.ogg` | 38 790 | `94200f3a3867…` | 47 090 | `b22c82b2ca5a…` | +8300 |
| 3 | `hive/amalgam_shuffle_01.ogg` | 44 121 | `3fbd6f250641…` | 21 534 | `0413f3b07c07…` | −22 587 |
| 4 | `hive/amalgam_shuffle_02.ogg` | 44 054 | `310e5e2b8dd3…` | 24 032 | `3b1616a347d9…` | −20 022 |
| 5 | `hive/amalgam_shuffle_03.ogg` | 34 281 | `f3300f622eb1…` | 19 130 | `1cdb54d16982…` | −15 151 |
| 6 | `hive/amalgam_slam_01.ogg` | 18 436 | `22a77e04aae3…` | 27 556 | `ae649b998d88…` | +9120 |
| 7 | `hive/amalgam_slam_02.ogg` | 17 363 | `ac8de5bc11dd…` | 24 605 | `4b9cd549947b…` | +7242 |
| 8 | `hive/spawn_creeper_crawl_01.ogg` | 22 169 | `8bddc2a7e3da…` | 19 662 | `79278b146c45…` | −2507 |
| 9 | `hive/spawn_creeper_crawl_02.ogg` | 25 602 | `ac2397db8c7d…` | 21 906 | `2bf9b24c1b50…` | −3696 |
| 10 | `hive/spawn_creeper_detonate_01.ogg` | 37 264 | `3129d9ee9f05…` | 12 919 | `f1dbeb66abb1…` | −24 345 |
| 11 | `hive/spawn_creeper_detonate_02.ogg` | 23 551 | `144c53f894b4…` | 11 723 | `19094a68ab49…` | −11 828 |
| 12 | `hive/spawn_creeper_sac_01.ogg` | 19 563 | `9bfc418c6908…` | 18 010 | `9233040b13dd…` | −1553 |
| 13 | `hive/spawn_creeper_sac_02.ogg` | 22 447 | `9dc01c32b794…` | 15 793 | `bf29f52c8eab…` | −6654 |
| 14 | `hive/spawn_creeper_sac_03.ogg` | 21 073 | `809e5ea2e1ab…` | 22 846 | `0ad91ce7dbea…` | +1773 |

Полные SHA256 — в `SHA256SUMS_all.txt` (новые) и в старом `transfer/SHA256SUMS_transfer74.txt` (для 74 переданных). Если ваш счёт даёт 12 — назовите, какие два из этих 14 вы исключаете; **я не подгоняю** и оставляю 14.

**Перемещения (не перезапись) — 10 путей**, из аудита 3.4.5 §2, содержимое то же, меняется только путь:

| из | в |
|---|---|
| `hive/hive_block_break_01_tear` … `_03_crunch` | `block/hive_block_break_01_tear` … `_03_crunch` |
| `hive/hive_block_place_01_soft` … `_03_wet` | `block/hive_block_place_01_soft` … `_03_wet` |
| `hive/spawn_hurt_critical_01` … `_04` | `hive/hive_spawn_hurt_critical_01` … `_04` |

### 1.3 «10 файлов диска вне манифеста» — **таких нет**

Проверено по диску: **0 файлов вне манифеста и 0 строк манифеста без файла**. Если у вас 10 — это позиции, о которых писал Q7 (алиасы `entity/amalgam_smash|roar|step`, `entity/flesh_amalgam_hurt|death` и `entity/flesh_amalgam_*`), они **внутри** манифеста, просто не подключены событиями. Список «вне манифеста» пуст, и это не ошибка сверки: я пересобираю манифест из `glob` по диску.

### 1.4 🔴 Главная находка пакета: 77 файлов — 96 kbps, а не 160

Формальный формат-контроль «vorbis/44100/mono» — **151/151**. Но битрейт:

| Битрейт | Файлов | Откуда |
|---|---|---|
| 160 kb/s | **74** | волны 18, 18A–18D (все мои сдачи) |
| **96 kb/s** | **77** | волны 1–17, до моего входа |

То есть ТЗ «строго 160 kbps» выполнялось только для моих файлов; **весь исторический банк живёт на 96**. Это не мой долг и не моя правка (правило: старые файлы не трогать без санкции), но в приёмке «формат-контроль 100%» это надо назвать честно: 100% по кодеку/частоте/каналам, **49% по битрейту**. Перекодировать 77 файлов в 160 без санкции не буду — это потеря поколения и рост банка примерно на 8 МБ.

### 1.5 «49 неиспользованных» — цифра не сходится, вот факты

| Категория | Файлов | Какие |
|---|---|---|
| архив `*_w1516` | 14 | не идут в проект (откат) |
| **сироты без события вообще** (не «тимчасово») | **8** | `entity/flesh_amalgam_death_01`, `hurt_01`, `roar_01`, `roar_02`, `smash_01`, `smash_02`, `step_01`, `step_02` — привязка через алиасы Q7 или новые события, ваша зона |
| становятся востребованными **после п.2** | 6 | `hive/hive_spawn_alert_01…04`† , `hive/hive_spawn_attack_01…04`† (см. ниже), `hive/zone_stinger_*` — уже объявлены |
| **не были в проекте, добавлены 18D** | 15 | 12 файлов §3 + 3 файла §4 — для них нужны новые события |

† фактически `hive_spawn_alert_*` (4) и `hive_spawn_attack_*` (4) уже закрыты объявлениями, поэтому в «неиспользованных» их держать нельзя. Честный список неиспользованных: **14 архивных + 8 сирот = 22**, и после п.2/§3 к ним добавляются **15 новых позиций, ждущих событий**. Цифру 49 не подтверждаю.

---

## 2. Декларации: 14 событий с переносом на именные семейства

`sounds.json` я не правлю, это текст для Кодера. Контракт сохранён: события **не удаляются**, `pitch`/`volume` остаются в Java (`1.0F`), в декларацию не тащатся — только переадресация путей на именные семейства, которые уже лежат в банке.

```json
{
  "hive.spawn_alert": { "subtitle": "carnis.subtitle.hive_spawn_alert", "sounds": [
    {"name": "carnis:hive/hive_spawn_alert_01", "stream": false},
    {"name": "carnis:hive/hive_spawn_alert_02", "stream": false},
    {"name": "carnis:hive/hive_spawn_alert_03", "stream": false},
    {"name": "carnis:hive/hive_spawn_alert_04", "stream": false}
  ]},
  "hive.spawn_death": { "subtitle": "carnis.subtitle.hive_spawn_death", "sounds": [
    {"name": "carnis:hive/hive_spawn_death_01", "stream": false},
    {"name": "carnis:hive/hive_spawn_death_02", "stream": false},
    {"name": "carnis:hive/hive_spawn_death_03", "stream": false},
    {"name": "carnis:hive/hive_spawn_death_04", "stream": false}
  ]},
  "hive.spawn_hurt": { "subtitle": "carnis.subtitle.hive_spawn_hurt", "sounds": [
    {"name": "carnis:hive/hive_spawn_hurt_01", "stream": false},
    {"name": "carnis:hive/hive_spawn_hurt_02", "stream": false},
    {"name": "carnis:hive/hive_spawn_hurt_03", "stream": false},
    {"name": "carnis:hive/hive_spawn_hurt_04", "stream": false}
  ]},
  "hive.spawn_hurt_critical": { "subtitle": "carnis.subtitle.hive_spawn_hurt_critical", "sounds": [
    {"name": "carnis:hive/hive_spawn_hurt_critical_01", "stream": false},
    {"name": "carnis:hive/hive_spawn_hurt_critical_02", "stream": false},
    {"name": "carnis:hive/hive_spawn_hurt_critical_03", "stream": false},
    {"name": "carnis:hive/hive_spawn_hurt_critical_04", "stream": false}
  ]},
  "hive.spawn_idle": { "subtitle": "carnis.subtitle.hive_spawn_idle", "sounds": [
    {"name": "carnis:hive/hive_spawn_idle_01", "stream": false},
    {"name": "carnis:hive/hive_spawn_idle_02", "stream": false},
    {"name": "carnis:hive/hive_spawn_idle_03", "stream": false},
    {"name": "carnis:hive/hive_spawn_idle_04", "stream": false}
  ]},
  "hive.spawn.creeper_sac": { "subtitle": "carnis.subtitle.spawn_creeper_sac", "sounds": [
    {"name": "carnis:hive/spawn_creeper_sac_01", "stream": false},
    {"name": "carnis:hive/spawn_creeper_sac_02", "stream": false},
    {"name": "carnis:hive/spawn_creeper_sac_03", "stream": false}
  ]},
  "hive.spawn.creeper_crawl": { "subtitle": "carnis.subtitle.spawn_creeper_crawl", "sounds": [
    {"name": "carnis:hive/spawn_creeper_crawl_01", "stream": false},
    {"name": "carnis:hive/spawn_creeper_crawl_02", "stream": false}
  ]},
  "hive.spawn.creeper_detonate": { "subtitle": "carnis.subtitle.spawn_creeper_detonate", "sounds": [
    {"name": "carnis:hive/spawn_creeper_detonate_01", "stream": false},
    {"name": "carnis:hive/spawn_creeper_detonate_02", "stream": false}
  ]},
  "hive.spawn_skeleton_whip": { "subtitle": "carnis.subtitle.spawn_skeleton_whip", "sounds": [
    {"name": "carnis:hive/spawn_skeleton_whip_01", "stream": false},
    {"name": "carnis:hive/spawn_skeleton_whip_02", "stream": false},
    {"name": "carnis:hive/spawn_skeleton_whip_03", "stream": false}
  ]},
  "hive.spawn_skeleton_bonecrack": { "subtitle": "carnis.subtitle.spawn_skeleton_bonecrack", "sounds": [
    {"name": "carnis:hive/spawn_skeleton_bonecrack_01", "stream": false},
    {"name": "carnis:hive/spawn_skeleton_bonecrack_02", "stream": false}
  ]},
  "hive.spawn_skeleton_blade": { "subtitle": "carnis.subtitle.spawn_skeleton_blade", "sounds": [
    {"name": "carnis:hive/spawn_skeleton_blade_01", "stream": false},
    {"name": "carnis:hive/spawn_skeleton_blade_02", "stream": false},
    {"name": "carnis:hive/spawn_skeleton_blade_03", "stream": false}
  ]},
  "hive.amalgam.shuffle": { "subtitle": "carnis.subtitle.amalgam_shuffle", "sounds": [
    {"name": "carnis:hive/amalgam_shuffle_01", "stream": false},
    {"name": "carnis:hive/amalgam_shuffle_02", "stream": false},
    {"name": "carnis:hive/amalgam_shuffle_03", "stream": false}
  ]},
  "hive.amalgam.slam": { "subtitle": "carnis.subtitle.amalgam_slam", "sounds": [
    {"name": "carnis:hive/amalgam_slam_01", "stream": false},
    {"name": "carnis:hive/amalgam_slam_02", "stream": false}
  ]},
  "hive.amalgam.breath": { "subtitle": "carnis.subtitle.amalgam_breath", "sounds": [
    {"name": "carnis:hive/amalgam_breath_01", "stream": false},
    {"name": "carnis:hive/amalgam_breath_02", "stream": false}
  ]}
}
```

Что здесь **не** делается: ни одно старое событие не удалено и не переименовано; для `hive.spawn.*` сохранены существующие имена событий (у них уже объявлен путь, чинится только имя файла); `hive.amalgam.breath` возвращён в декларацию как **отдельное решение Кодера** — вы говорили, что события в финальном `sounds.json` нет, тогда этот фрагмент просто не используется, файлы остаются в банке (14 архивных + 2 живых).

---

## 3. Новые звуки для контента 3.5.0 — 12 файлов

Сверка перед генерацией: `pustule_burst` (есть, 18B), `synapse_rupture` (есть, 18B), `combat/*` (есть, 19 файлов), `hive/detail_membrane_01` (есть как фон). **Из перечисленного вами не существует: `purifier_ignite/loop`, `purifier_lamp`, `synapse_shock`, `sinew_shield`, `ossified_scythe`, `pustule_grenade`, `purification_vial`, `hive_membrane`, `synapse_node`, `incubation_cyst`** — то есть весь список 3.5.0, кроме двух «влажных» из 18B. Сгенерировано 12 (минимум был 8) — по каждой механике place+step / pulse / rupture+ambient / свист+удар / impact+throw / ignite / break / shock / rupture.

| # | Путь | Байт | Длит. | RMS | Peak | Crest | сверка P−R | Tonal | Center | Onset | AM |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `block/hive_membrane_place_01.ogg` | 10 556 | 0.42 | −19.02 | −4.00 | 15.0 | 15.02 ✓ | 5.8 @202 | 439 | 2.1 мс | 2.76 Гц / 1.91 |
| 2 | `block/hive_membrane_step_01.ogg` | 12 458 | 0.52 | −19.52 | −4.17 | 15.4 | 15.35 ✓ | 6.8 @190 | 478 | 3.0 мс | 2.19 Гц / 1.60 |
| 3 | `block/synapse_node_pulse_01.ogg` (луп) | 26 700 | 1.54 | −17.97 | −7.39 | 10.6 | 10.58 ✓ | 3.7 @240 | 235 | — | 0.63 Гц* |
| 4 | `entity/incubation_cyst_rupture_01.ogg` | 17 373 | 0.85 | −17.01 | −3.05 | 14.0 | 13.96 ✓ | 3.0 @320 | 342 | 0.3 мс | 1.15 Гц / 1.72 |
| 5 | `entity/incubation_cyst_ambient_01.ogg` | 32 621 | 2.30 | −21.03 | −9.47 | 11.6 | 11.56 ✓ | 2.3 @63 | 325 | 23.6 мс | 0.57 Гц / 0.84 |
| 6 | `entity/sinew_shield_block_01.ogg` | 11 958 | 0.55 | −18.50 | −3.53 | 15.0 | 14.97 ✓ | 4.5 @151 | 265 | 1.2 мс | 1.83 Гц / 2.28 |
| 7 | `combat/ossified_scythe_swing_01.ogg` | 16 267 | 0.72 | −18.04 | −4.95 | 13.1 | 13.09 ✓ | 4.6 @226 | 1918 | 9.5 мс | 1.95 Гц / 1.27 |
| 8 | `combat/ossified_scythe_hit_01.ogg` | 13 163 | 0.60 | −18.57 | −3.04 | 15.5 | 15.53 ✓ | 7.6 @180 | 1267 | 0.3 мс | 1.32 Гц / 2.66 |
| 9 | `entity/pustule_grenade_impact_01.ogg` | 19 194 | 1.10 | −16.95 | −2.93 | 14.0 | 14.02 ✓ | 6.2 @151 | 1083 | 0.0 мс | 0.56 Гц / 3.09 |
| 10 | `entity/pustule_grenade_throw_01.ogg` | 13 683 | 0.56 | −19.01 | −5.91 | 13.1 | 13.10 ✓ | 3.0 @269 | 2535 | 9.8 мс | 2.07 Гц / 0.72 |
| 11 | `item/purifier_lamp_ignite_01.ogg` | 25 511 | 1.30 | −20.02 | −7.99 | 12.0 | 12.03 ✓ | 3.1 @160 | 1527 | 23.5 мс | 0.90 Гц / 1.11 |
| 12 | `item/purification_vial_break_01.ogg` | 14 939 | 0.70 | −18.39 | −3.28 | 15.1 | 15.11 ✓ | 5.5 @160 | 4248 | 0.0 мс | 0.91 Гц / 3.07 |

\* у лупа `synapse_node_pulse_01` AM снят по внутренним биениям; темп задан 56 BPM.

**Шов лупа `synapse_node_pulse_01`:** шаг RMS у стыка **0.52 дБ**, медиана внутренних шагов 1.62 дБ, 99-й перцентиль — 9.9 дБ, **перцентиль стыка 17** (порог ≤ 50). Фаза 0.44 с, перебор 24 значений. Методика та же, что принята в 18B (DC-срез 30 Гц → круговой кроссфейд 60 мс equal-power → подложка → перебор фазы).

### 3.1 Сравнение с аналогами и конфликт-чек

| Новый файл | Аналоги (замер) | Чем отличается |
|---|---|---|
| `hive_membrane_place_01` | `hive/detail_membrane_01` (−31.1 / центр 2960 / 0.54), `block/hive_block_place_03_wet` (−20.4 / центр 353) | на 12 дБ громче «детали» (это событие, не фон), центр 439 — между ними; это не «мокрый блок», потому что низ 45–140 ослаблен |
| `hive_membrane_step_01` | `flesh/flesh_block_step_01` (−17.5 / центр 244), `hive_membrane_place_01` | на 2 дБ тише шага по плоти, центр выше (478 vs 244) — мембрана натянута, а не «чавкает» |
| `synapse_node_pulse_01` | `heartbeat_loop` (−17.5 / центр 121), `hive_heartbeat` (−18.0 / 139), `heart_pulse` (−18.2 / 95) | crest 10.6 и RMS как у всех трёх, но **центр 235 вдвое выше** — узел электрический, а не мышечный; в пульс добавлены искры 2–5.5 кГц, которых нет ни у одного из сердец |
| `incubation_cyst_rupture_01` | `pustule_burst` (центр 1040), `acid_splash` (2875), `spawn_creeper_sac_01` (−19.0 / центр 1155) | центр **342** — самый низкий из «влажных»: разрыв кисты даёт пустую оболочку, а не брызги в воздух; по громкости между sac и burst |
| `incubation_cyst_ambient_01` | `flesh_amalgam_ambient` (−20.0 / центр 456), `amalgam_breath_01` (−21.5 / 672), `hive_spawn_idle_01` (−29.1 / 56) | RMS как у амбиента амальгамы, но crest 11.6 против 10.2 и центр 325 — есть толчки изнутри, а не ровное дыхание |
| `sinew_shield_block_01` | `combat_stab_03_shield` (центр **1522**), `combat_deflect_04_glance` (1809) | центр **265** — на порядок ниже: щит из сухожилий гасит удар, а не звенит; crest 15.0 против 18.3–19.5 |
| `ossified_scythe_swing_01` | `combat_stab_01_bone` (−20.3 / 1718), `detail_flow_01` (−29.6 / 3037) | единственный «свист» в банке: центр 1918 при crest 13.1 (у стабов 19.2) — это движение, а не контакт |
| `ossified_scythe_hit_01` | `combat_deflect_02_bone` (2239), `dismember_01` (895), `bone_deflect` (2950 / crest 16.1) | центр 1267 — ниже и «костяного», и «расчленения»: удар косой идёт через плоть, верх 4–5 кГц есть, но не доминирует |
| `pustule_grenade_impact_01` | `pustule_burst` (1040 / crest 13.9), `spawn_creeper_detonate_01` (−14.0 / 1793), `flesh_hit_deep_03_blast` (−15.9 / 208) | RMS −16.95 и crest 14.0 совпадают с `pustule_burst`, но длительность 1.10 против 0.80 и AM 3.09 — это «разлёт после хлопка», а не одномоментный разрыв |
| `pustule_grenade_throw_01` | `detail_flow_02` (2356), `acid_splash` (2875), `flesh_hit_03` (−24.1 / 621) | свист 0.56 с, центр 2535, RMS −19.0 — тише удара на 2 дБ (замах не должен «бить» по ушам) |
| `purifier_lamp_ignite_01` | `hive_eye_screech` (1710), `detail_flow_01` (3037), `ambient_tonal_stinger` (263) | центр 1527, RMS −20.0, crest 12.0 — ровное пламя без «взрыва»; отличие от огнемёта §4 — нет низкого рёва 60–240 и нет потрескивания 26–34/с |
| `purification_vial_break_01` | `acid_splash` (2875), `combat_deflect_03_metal` (2294), `pustule_burst` (1040) | центр **4248** — самый высокий: стекло, а не плоть; RMS −18.4 при crest 15.1 |

**Конфликт-чек по «трём влажным» из 18B** (`pustule_burst` / `acid_splash` / `synapse_rupture`): ни один новый файл не попал в их полосы.
- `incubation_cyst_rupture` — центр 342 (у трёх влажных 1040/2875/1182), самая низкая «влажность» в банке;
- `pustule_grenade_impact` — центр 1083, но длительность 1.10 с и AM 3.09 Гц (у `pustule_burst` 0.80 с и AM 2.84 при центре 1040) — различие по длительности и роли;
- `purification_vial_break` — 4248 (стекло, не жидкость);
- `sinew_shield_block` — 265 (глухой натяг, не хлопок).

---

## 4. Тишина R9 — проверка по диску

| Событие | Файл у меня | Факт |
|---|---|---|
| `hive.spread` | `hive/hive_spread_01_creep`, `_02_pulse`, `_03_swell` | **есть, 3 файла** — в пакет §1 с хешами |
| `flesh_amalgam_ambient` | `entity/flesh_amalgam_ambient.ogg` | **есть** (18B, отложена Архитектором по call-site) |
| `hive.detail_flow` | `detail_flow_01`, `detail_flow_02` | **есть** |
| `hive.detail_membrane` | `detail_membrane_01` | **есть** |
| `hive.detail_bubbles` | `detail_bubbles_01` | **есть** |
| `hive.detail_creak` | `detail_creak_01` | **есть** |
| `hive.detail_scuttle` | `detail_scuttle_01` | **есть** |
| `amalgam_smash` | `entity/amalgam_smash.ogg` — **нет**, но есть `flesh_amalgam_smash_01/02` | закрывается алиасом Q7 (Кодеру: алиас, не новый файл) |
| `flamethrower_fire` | **нет** | 🔴 **класс A** — сгенерирован, см. ниже |
| `synapse_shock` | **нет** | 🔴 **класс A** — сгенерирован |
| `creeper_rupture` | **нет** | 🔴 **класс A** — сгенерирован |

Три файла класса A (Ревизор считал их классом C — по моему банку это не так):

| Путь | Байт | Длит. | RMS | Peak | Crest | Tonal | Center | Onset | AM |
|---|---|---|---|---|---|---|---|---|---|
| `entity/flamethrower_fire.ogg` (**луп**) | 28 688 | 1.64 | −18.97 | −6.26 | 12.7 | 1.7 @60 | 1284 | — | 3.7 Гц (турбулентность) |
| `block/synapse_shock.ogg` | 13 424 | 0.55 | −18.04 | −3.03 | 15.0 | 7.6 @254 | 1664 | 0.7 мс | 1.73 Гц / 1.97 |
| `block/creeper_rupture.ogg` | 16 898 | 0.90 | −17.10 | −3.11 | 14.0 | 4.8 @453 | 587 | 0.2 мс | 0.87 Гц / 2.37 |

Шов `flamethrower_fire`: шаг 0.06 дБ, медиана внутри 0.77 дБ, перцентиль **2.5** — лучший из моих лупов (у пламени нет ударов, шаг почти нулевой).

Отличия от соседей: `synapse_shock` (центр 1664, 0.55 с) против `synapse_rupture` (1182, 0.70 с) — разряд короче и выше по центру, без капель; `creeper_rupture` (центр 587, 0.90 с) против `pustule_burst` (1040, 0.80 с) — газ и мембрана, а не брызги; `flamethrower_fire` — луп с RMS −19.0 против амбиента `amb_core` (−27.4).

---

## 5. Отклонения и открытые вопросы (с обоснованиями)

| # | Что | Факт | Обоснование / что нужно от вас |
|---|---|---|---|
| 1 | **Битрейт** | 160 kb/s — 74 файла, **96 kb/s — 77** (волны 1–17) | не мой долг, но «формат 100%» верно только по кодеку/частоте/каналам. Перекодировку 77 файлов без санкции не делаю |
| 2 | **«12 файлов перезаписать»** | у меня **14** | все 14 — архив 18A против старых файлов волн 15/16 у Кодера (Q7 §115). Назовите два исключённых — приму без спора |
| 3 | **«10 файлов вне манифеста»** | **0** | манифест собирается glob'ом по диску; 10 «лишних» — это алиасы/сироты, они **внутри** манифеста |
| 4 | **«49 неиспользованных»** | 14 архивных + 8 сирот = **22** (+15 новых до объявления событий) | цифру 49 подтвердить не могу, расшифровки не было |
| 5 | **`tonal_band` ложно срабатывает** | у 4 новых файлов (и у 44 старых) `tonal` > 5 | введена вторая метрика **`tonal_persist`** (доля окон с устойчивым пиком). Калибровка: синус **1.00**, шум ≤ **0.25**, `bone_deflect` 0.00, `amb_deep` 0.00. У новых файлов persist 0.25–0.5, у настоящих тонов 1.00 |
| 6 | **Ложные пики измерителя** | `combat_flesh_hit_01/03` показывают `f0=95/143` с уровнем «−200 дБ» | это артефакт грубой сетки 1/12-окт при `np.percentile`, а не звук: реального пика на этой частоте нет (буду чинить метрику, не файлы) |
| 7 | **Onset > 50 мс** | 23 файла, все — старые, `onset` считается от начала файла с задержкой атаки (амбиенты, idle) | для one-shot из 18C–18D onset ≤ 23.6 мс, кроме `incubation_cyst_ambient` (23.6) и `purifier_lamp_ignite` (23.5) — обе «включаются», а не бьют |
| 8 | **`amalgam_breath_*`** | оставлены живыми + добавлены в декларацию §2 | вы говорили, что события нет в финальном реестре. Фрагмент можно не применять — файлы не удаляю по правилу |

---

## 5а. ⚠️ Поправка к §3 (обнаружено при сдаче 18E)

В таблице §3 отчёта 18D были **неверные размеры у всех 15 файлов** — байты снимались с промежуточного каталога генерации, а не с банка после копирования. Цифры **RMS/Peak/Crest/Tonal/Center/Onset/AM — верные** (они всегда снимались с декодированного звука), ошибка только в столбце «Байт», завышение в 1.4–2.4 раза. Проверено по диску: 15/15 расходятся, значения в §3 исправлены.

**Что НЕ затронуто:** `MANIFEST_ogg.txt`, `SHA256SUMS_all.txt` и `CARNIS_Wave18D_BankQA.md` собирались скриптом прямо с диска (`glob` + `os.path.getsize`) — они верные с самого начала. Итоговая сумма банка после 18D (**11 902 487 Б**) тоже верна: она получена из манифеста, а не из текста отчёта. Испорчен был только текст §3 — принятые вами манифест и хеши не пострадали.

## 6. Итог

| Метрика | Значение |
|---|---|
| Файлов | **151** |
| Байт | **11 902 487** |
| Строк манифеста | **152** (151 + заголовок) |
| Расхождений манифест ↔ диск | **0** |
| Формат vorbis/44100/mono | **151 / 151** |
| Битрейт 160 | 74 / 151 (см. §1.4) |
| Новых в 18D | 15 (12 по п.3 + 3 класса A по п.4) |
| `SHA256SUMS_all.txt` | 151 строка |
| `transfer/CARNIS_transfer_86.tar.gz` | 86 файлов, 10 404 802 Б |

**Цифры окончательные.** `build/` удалён.
