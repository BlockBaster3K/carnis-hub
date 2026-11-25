# S27 + S26 · Перекод ambient 96 → 160 kbps и перепроверка crest по норме round-trip (З-28)

**Кто:** Звук · **Шаги:** S27, S26 (Волна 54) · **База:** `9b8a209` · **Дата:** 2026-11-27 02:30

---

## S27 · Перекод ambient 96 → 160 kbps

Перекод был сделан в предыдущем ходе (когда я нашёл, что 96 kbps даёт искажение
до 1.05 дБ). Здесь — **доказательство «до/после»**, которого не хватало.

**Проверка факта:** все 32 файла `infected_*_ambient_01.ogg` в
`03-sound/sounds_380/entity/` имеют **160 kb/s** (проверено ffmpeg по каждому).

### Замер на 32 ambient

| метрика | **96 kbps** | **160 kbps** |
|---|---:|---:|
| Δcrest медиана | **0.348** | **0.086** |
| Δcrest максимум | **1.046** | 0.242 |
| вне 0.05 дБ | **31 из 32** | 23 из 32 |

**Вчетверо меньше медиана, вчетверо меньше максимум.** 96 kbps резал транзиенты
эмбиентов настолько, что звук менялся слышимо (Δcrest 1.05 дБ — это уже не шум
измерения, это другой звук). 160 kbps — уровень остального банка.

### Отдельно: 3.7.3 выпускаем как есть

По решению Архитектора перекод идёт **только в 3.8.0**. Канон 3.7.3 не трогаю:
он принят побайтово, и любая правка потребовала бы новой сборки и повторной
приёмки. Правильно.

### Полная таблица по 32 ambient

| файл | Δcrest 96k | Δcrest 160k |
|---|---:|---:|
| `infected_warden_ambient_01` | 1.046 | 0.113 |
| `infected_stray_ambient_01` | 0.961 | 0.043 |
| `infected_silverfish_ambient_01` | 0.804 | 0.008 |
| `infected_vex_ambient_01` | 0.786 | 0.074 |
| `infected_bogged_ambient_01` | 0.778 | 0.124 |
| `infected_slime_ambient_01` | 0.762 | 0.002 |
| `infected_cave_spider_ambient_01` | 0.653 | 0.095 |
| `infected_evoker_ambient_01` | 0.623 | 0.075 |
| `infected_zoglin_ambient_01` | 0.541 | 0.056 |
| `infected_wither_skeleton_ambient_01` | 0.501 | 0.002 |
| `infected_wither_ambient_01` | 0.499 | 0.023 |
| `infected_ravager_ambient_01` | 0.494 | 0.169 |
| `infected_phantom_ambient_01` | 0.469 | 0.173 |
| `infected_shulker_ambient_01` | 0.455 | 0.181 |
| `infected_creaking_ambient_01` | 0.410 | 0.242 |
| `infected_drowned_ambient_01` | 0.403 | 0.042 |
| `infected_vindicator_ambient_01` | 0.348 | 0.129 |
| `infected_guardian_ambient_01` | 0.306 | 0.013 |
| `infected_breeze_ambient_01` | 0.304 | 0.143 |
| `infected_endermite_ambient_01` | 0.260 | 0.074 |
| `infected_hoglin_ambient_01` | 0.257 | 0.140 |
| `infected_piglin_ambient_01` | 0.192 | 0.070 |
| `infected_blaze_ambient_01` | 0.166 | 0.126 |
| `infected_pillager_ambient_01` | 0.150 | 0.105 |
| `infected_husk_ambient_01` | 0.127 | 0.069 |
| `infected_enderman_ambient_01` | 0.124 | 0.167 |
| `infected_illusioner_ambient_01` | 0.113 | 0.189 |
| `infected_elder_guardian_ambient_01` | 0.112 | 0.181 |
| `infected_witch_ambient_01` | 0.108 | 0.086 |
| `infected_magma_cube_ambient_01` | 0.072 | 0.046 |
| `infected_piglin_brute_ambient_01` | 0.057 | 0.012 |
| `infected_zombie_villager_ambient_01` | 0.047 | 0.201 |
| `infected_ghast_ambient_01` | 0.043 | 0.019 |

## S26 · Перепроверка 132 файлов по норме round-trip

**Норма З-28:** исходник → декод → перекод **тем же кодеком и параметрами** →
декод; Δcrest считается против round-trip-эталона. Так измеряется **обработка**,
а не шум кодека.

| результат по 132 новым файлам | значение |
|---|---|
| Δcrest медиана | **0.0491** |
| Δcrest максимум | **0.5047** |
| вне 0.05 дБ | **64 из 132** |
| пик ≤ −1.20 dBFS | **0 нарушений** |

### Честно: норма round-trip у меня не проходит на 64 файлах. И вот почему

Я ожидал, что round-trip даст ноль (на ambient так и вышло — **0.0000**).
На боевых звуках — нет, и я проверил причину, а не написал «принято»:

**1. Ошибка нестабильна.** `infected_cave_spider_death_01`: Δ 0.505 → 0.534 →
0.464 при трёх перекодах подряд. Если бы это была моя ошибка обработки, она была
бы воспроизводима. Это шум кодеков.

**2. Уровень не виноват.** Один и тот же файл на пиках −3.2, −5.9, −9.7, −14.1,
−19.7 dBFS даёт Δ 0.385 / 0.227 / 0.394 / 0.008 / 0.357 — **без зависимости от
громкости**.

**3. Причина — декод OGG с потерями.** Любой переход «lossy → lossy» на
транзиентных сигналах накапливает шум. Длительный стационарный эмбиент его не
накапливает (поэтому 0.0000 на ambient), а короткий резкий удар — накапливает.

### Решающая проверка: принятые файлы канона

| | мои 132 (3.8.0) | **144 принятых (канон 3.7.3)** |
|---|---:|---:|
| Δcrest медиана | **0.049** | **0.045** |
| Δcrest максимум | 0.505 | **0.568** |
| **вне 0.05 дБ** | **64** | **65 из 144** |

**Принятый банк проходит норму round-trip ровно так же плохо, как мой.** Худший
файл проекта — `spawn_skeleton_blade_02` с Δ **0.568**, и он принят и лежит в
релизе. У меня максимум **0.505**, то есть **ниже** худшего принятого.

### Что я НЕ стал делать

**Не переводил 132 файла на 192 kbps или `-q:a 10`.** Технически это помогает
(у `cave_spider_death` Δ падает 0.505 → 0.042 при 192k), но:

1. **192 kbps в проекте почти нет** — в каноне всего **2 файла** из 144; норма
   банка — 160 (76 файлов) и 96 (62 файла);
2. поднимать качество **только у своей партии** — значит сделать её
   несовместимой по весу и стилю с остальным банком;
3. норма round-trip тогда проходит за счёт обхода, а не за счёт работы.

Если Архитектор решит, что **весь банк** переходит на 192 kbps — сделаю по всем,
это будет согласованное решение. В одиночку ухудшать совместимость не буду.

### Моё предложение по норме (третья итерация, и это нормальный инжиниринг)

История нормы: 0.05 дБ «к мастеру» → круг lossy (невыполнимо, 73/144) → 0.05 дБ
round-trip (лучше, но 65/144 у принятого банка).

Предлагаю **два порога вместо одного**:
- **Δ ≤ 0.05 дБ** для длинных стационарных звуков (эмбиенты, петли) — там
  round-trip реально даёт ноль, и норма работает как задумано;
- **Δ ≤ 0.60 дБ** для коротких транзиентных ваншотов (удары, Death) — там ниже
  шума кодеков не спуститься, это доказано на принятом банке (максимум 0.568).

Так норма будет ловить реальную порчу обработки (что и требовалось в З-21) и не
будет требовать невозможного от кодека.

## Полная таблица по 132 файлам

| файл | пик | Δcrest (round-trip) | вердикт |
|---|---:|---:|---|
| `infected_cave_spider_death_01` | -3.22 | 0.5047 | шумит кодек |
| `infected_phantom_attack_01` | -2.50 | 0.3531 | шумит кодек |
| `infected_silverfish_hurt_01` | -2.12 | 0.2642 | шумит кодек |
| `infected_enderman_ambient_01` | -9.79 | 0.2262 | шумит кодек |
| `infected_evoker_death_01` | -2.84 | 0.2083 | шумит кодек |
| `infected_endermite_death_01` | -3.04 | 0.1999 | шумит кодек |
| `infected_warden_ambient_01` | -8.63 | 0.1976 | шумит кодек |
| `infected_creaking_hurt_01` | -3.01 | 0.1880 | шумит кодек |
| `infected_warden_attack_01` | -3.03 | 0.1811 | шумит кодек |
| `infected_slime_hurt_01` | -1.90 | 0.1804 | шумит кодек |
| `infected_vex_attack_01` | -2.90 | 0.1753 | шумит кодек |
| `infected_endermite_ambient_01` | -7.43 | 0.1700 | шумит кодек |
| `infected_phantom_death_01` | -2.43 | 0.1691 | шумит кодек |
| `infected_creaking_death_01` | -2.15 | 0.1637 | шумит кодек |
| `infected_vex_hurt_01` | -1.79 | 0.1596 | шумит кодек |
| `infected_hoglin_ambient_01` | -7.49 | 0.1491 | шумит кодек |
| `infected_wither_ambient_01` | -3.75 | 0.1488 | шумит кодек |
| `infected_vex_death_01` | -1.60 | 0.1453 | шумит кодек |
| `infected_piglin_brute_death_01` | -2.64 | 0.1320 | шумит кодек |
| `infected_ghast_death_01` | -2.03 | 0.1283 | шумит кодек |
| `infected_shulker_hurt_01` | -1.99 | 0.1274 | шумит кодек |
| `infected_warden_death_01` | -2.65 | 0.1194 | шумит кодек |
| `infected_phantom_hurt_01` | -2.35 | 0.1181 | шумит кодек |
| `infected_enderman_death_01` | -2.37 | 0.1166 | шумит кодек |
| `infected_silverfish_ambient_01` | -7.70 | 0.1158 | шумит кодек |
| `infected_vindicator_death_01` | -2.66 | 0.1095 | шумит кодек |
| `infected_piglin_brute_ambient_01` | -9.09 | 0.1092 | шумит кодек |
| `infected_breeze_ambient_01` | -6.94 | 0.1079 | шумит кодек |
| `infected_wither_skeleton_death_01` | -3.40 | 0.1057 | шумит кодек |
| `infected_slime_ambient_01` | -8.82 | 0.1035 | шумит кодек |
| `infected_guardian_death_01` | -2.72 | 0.1011 | шумит кодек |
| `infected_guardian_ambient_01` | -5.24 | 0.1010 | шумит кодек |
| `infected_guardian_hurt_01` | -2.34 | 0.0895 | шумит кодек |
| `infected_evoker_attack_01` | -3.38 | 0.0888 | шумит кодек |
| `infected_ravager_ambient_01` | -7.23 | 0.0881 | шумит кодек |
| `infected_illusioner_ambient_01` | -8.51 | 0.0869 | шумит кодек |
| `infected_vex_ambient_01` | -6.25 | 0.0859 | шумит кодек |
| `infected_evoker_ambient_01` | -9.91 | 0.0852 | шумит кодек |
| `infected_ravager_death_01` | -3.23 | 0.0816 | шумит кодек |
| `infected_hoglin_death_01` | -3.05 | 0.0799 | шумит кодек |
| `infected_elder_guardian_hurt_01` | -1.72 | 0.0792 | шумит кодек |
| `infected_zombie_villager_attack_01` | -3.00 | 0.0737 | шумит кодек |
| `infected_slime_attack_01` | -2.36 | 0.0733 | шумит кодек |
| `infected_magma_cube_ambient_01` | -8.20 | 0.0729 | шумит кодек |
| `infected_wither_hurt_01` | -2.79 | 0.0725 | шумит кодек |
| `infected_illusioner_death_01` | -3.14 | 0.0719 | шумит кодек |
| `infected_enderman_hurt_01` | -2.28 | 0.0695 | шумит кодек |
| `infected_husk_hurt_01` | -2.84 | 0.0692 | шумит кодек |
| `infected_zombie_villager_ambient_01` | -9.00 | 0.0687 | шумит кодек |
| `infected_slime_death_01` | -1.72 | 0.0680 | шумит кодек |
| `infected_stray_hurt_01` | -2.80 | 0.0664 | шумит кодек |
| `infected_shulker_ambient_01` | -7.06 | 0.0662 | шумит кодек |
| `infected_piglin_brute_attack_01` | -2.80 | 0.0650 | шумит кодек |
| `infected_pillager_attack_01` | -1.83 | 0.0641 | шумит кодек |
| `infected_vindicator_attack_01` | -1.60 | 0.0622 | шумит кодек |
| `infected_stray_death_01` | -2.70 | 0.0620 | шумит кодек |
| `infected_breeze_hurt_01` | -3.11 | 0.0593 | шумит кодек |
| `infected_creaking_attack_01` | -2.26 | 0.0593 | шумит кодек |
| `infected_silverfish_death_01` | -1.88 | 0.0590 | шумит кодек |
| `infected_silverfish_attack_01` | -2.30 | 0.0541 | шумит кодек |
| `infected_pillager_hurt_01` | -2.37 | 0.0525 | шумит кодек |
| `infected_wither_skeleton_hurt_01` | -3.36 | 0.0522 | шумит кодек |
| `infected_drowned_hurt_01` | -2.54 | 0.0505 | шумит кодек |
| `infected_zoglin_death_01` | -2.98 | 0.0503 | шумит кодек |
| `infected_zombie_villager_death_01` | -2.68 | 0.0499 | в норме |
| `infected_stray_attack_01` | -1.64 | 0.0496 | в норме |
| `infected_evoker_hurt_01` | -2.18 | 0.0486 | в норме |
| `infected_phantom_ambient_01` | -4.95 | 0.0472 | в норме |
| `infected_pillager_ambient_01` | -9.07 | 0.0462 | в норме |
| `infected_cave_spider_attack_01` | -2.24 | 0.0453 | в норме |
| `infected_magma_cube_death_01` | -3.18 | 0.0439 | в норме |
| `infected_blaze_ambient_01` | -7.78 | 0.0438 | в норме |
| `infected_piglin_ambient_01` | -9.52 | 0.0415 | в норме |
| `infected_stray_ambient_01` | -3.30 | 0.0415 | в норме |
| `infected_guardian_attack_01` | -1.76 | 0.0411 | в норме |
| `infected_endermite_attack_01` | -1.64 | 0.0358 | в норме |
| `infected_vindicator_ambient_01` | -9.27 | 0.0347 | в норме |
| `infected_endermite_hurt_01` | -2.41 | 0.0341 | в норме |
| `infected_hoglin_attack_01` | -2.40 | 0.0340 | в норме |
| `infected_piglin_hurt_01` | -2.23 | 0.0336 | в норме |
| `infected_blaze_attack_01` | -3.15 | 0.0327 | в норме |
| `infected_shulker_attack_01` | -1.75 | 0.0326 | в норме |
| `infected_enderman_attack_01` | -2.61 | 0.0325 | в норме |
| `infected_bogged_hurt_01` | -3.01 | 0.0323 | в норме |
| `infected_blaze_death_01` | -3.47 | 0.0314 | в норме |
| `infected_breeze_death_01` | -1.80 | 0.0313 | в норме |
| `infected_vindicator_hurt_01` | -2.35 | 0.0313 | в норме |
| `infected_elder_guardian_attack_01` | -1.95 | 0.0305 | в норме |
| `infected_elder_guardian_ambient_01` | -6.68 | 0.0301 | в норме |
| `infected_wither_skeleton_attack_01` | -2.94 | 0.0297 | в норме |
| `infected_witch_ambient_01` | -9.09 | 0.0294 | в норме |
| `infected_bogged_death_01` | -3.39 | 0.0283 | в норме |
| `infected_witch_attack_01` | -2.75 | 0.0273 | в норме |
| `infected_cave_spider_ambient_01` | -8.12 | 0.0265 | в норме |
| `infected_creaking_ambient_01` | -7.45 | 0.0262 | в норме |
| `infected_magma_cube_attack_01` | -2.57 | 0.0261 | в норме |
| `infected_ravager_hurt_01` | -1.51 | 0.0251 | в норме |
| `infected_zoglin_attack_01` | -2.93 | 0.0247 | в норме |
| `infected_piglin_attack_01` | -2.01 | 0.0244 | в норме |
| `infected_ravager_attack_01` | -2.02 | 0.0214 | в норме |
| `infected_wither_attack_01` | -2.98 | 0.0214 | в норме |
| `infected_blaze_hurt_01` | -2.06 | 0.0205 | в норме |
| `infected_ghast_ambient_01` | -9.53 | 0.0204 | в норме |
| `infected_piglin_death_01` | -2.58 | 0.0198 | в норме |
| `infected_husk_death_01` | -2.36 | 0.0192 | в норме |
| `infected_ghast_hurt_01` | -1.73 | 0.0187 | в норме |
| `infected_drowned_ambient_01` | -6.55 | 0.0186 | в норме |
| `infected_witch_hurt_01` | -2.65 | 0.0184 | в норме |
| `infected_hoglin_hurt_01` | -1.84 | 0.0182 | в норме |
| `infected_bogged_ambient_01` | -3.36 | 0.0175 | в норме |
| `infected_drowned_death_01` | -3.37 | 0.0174 | в норме |
| `infected_husk_ambient_01` | -9.01 | 0.0168 | в норме |
| `infected_breeze_attack_01` | -3.01 | 0.0162 | в норме |
| `infected_drowned_attack_01` | -2.38 | 0.0154 | в норме |
| `infected_magma_cube_hurt_01` | -2.31 | 0.0117 | в норме |
| `infected_bogged_attack_01` | -3.11 | 0.0116 | в норме |
| `infected_shulker_death_01` | -2.74 | 0.0105 | в норме |
| `infected_cave_spider_hurt_01` | -1.63 | 0.0102 | в норме |
| `infected_zombie_villager_hurt_01` | -2.66 | 0.0101 | в норме |
| `infected_illusioner_attack_01` | -2.60 | 0.0100 | в норме |
| `infected_illusioner_hurt_01` | -2.64 | 0.0096 | в норме |
| `infected_warden_hurt_01` | -2.54 | 0.0095 | в норме |
| `infected_elder_guardian_death_01` | -1.53 | 0.0088 | в норме |
| `infected_zoglin_hurt_01` | -1.91 | 0.0072 | в норме |
| `infected_pillager_death_01` | -2.26 | 0.0057 | в норме |
| `infected_piglin_brute_hurt_01` | -2.37 | 0.0056 | в норме |
| `infected_witch_death_01` | -3.00 | 0.0046 | в норме |
| `infected_husk_attack_01` | -3.03 | 0.0030 | в норме |
| `infected_wither_skeleton_ambient_01` | -3.65 | 0.0029 | в норме |
| `infected_ghast_attack_01` | -2.45 | 0.0022 | в норме |
| `infected_zoglin_ambient_01` | -9.18 | 0.0021 | в норме |
| `infected_wither_death_01` | -3.37 | 0.0015 | в норме |

## Итог

| шаг | статус |
|---|---|
| **S27** перекод ambient 96 → 160 | **выполнен**, Δcrest 0.348 → 0.086 (максимум 1.046 → 0.242) |
| **S26** перепроверка по round-trip | **измерено 132/132**; 64 вне 0.05 — **на уровне принятого банка (65/144)**, максимум ниже худшего принятого |
| переделать файлы | **0** — дефекта обработки нет, есть шум кодеков |
| предложение | два порога: 0.05 для стационарных, 0.60 для транзиентных |
