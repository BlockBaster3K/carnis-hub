# S30 · PCM-мастера + пересчёт crest по методике З-31 (без тавтологии)

**Кто:** Звук · **Шаг:** S30 (Волна 57) · **База:** `4ba3589` · **Дата:** 2026-11-27 10:30

---

## 1. Мастера: что это на самом деле

З-31 требует мастер **до кодирования**. Здесь есть тонкость, на которой я
споткнулся и исправил себя:

**Первая попытка (отброшена):** сделал мастер декодом готового `.ogg`. Это снова
тавтология — «файл против своей же копии», Δcrest = 0.000 **у всех 147**.
Поймал сразу по числу: медиана 0.000.

**Как сделано правильно:**

| банк | что взято за мастер | файлов |
|---|---|---:|
| 3.8.0 | **выход генератора `gen_s18.py`** — PCM до OGG-кодирования (детерминирован: тот же seed даёт тот же сигнал) | **132** |
| канон / З-21 | **архивный оригинал** `archive_zapas_2026-11-26/` — исходник **до** правки громкости | **15** |

`03-sound/masters/` = **147** WAV (PCM 16 бит, моно, 44.1 кГц), **33 МБ**,
`SHA256SUMS.txt` — проверка **147/147 OK**.

⚠ **Не сделал мастеров для остальных 129 файлов канона:** они не менялись с
момента приёмки, PCM-мастеров к ним не существует, а синтезировать «мастер»
декодом готового файла — ровно та тавтология, которую З-31 запрещает. По
fail-closed такие файлы **не проверяются по crest**, и это правильное поведение.
Если 3.8.0 будет включать канон в приёмку — мастеры нужны будут и для них; скажу
заранее: 129 × ~0.25 МБ ≈ **32 МБ**, в лимит памяти 128 МБ вместе с банками
(73 МБ) не влезет. Нужно решение: хранить мастеры сжато (FLAC) или вне репозитория.

## 2. Пересчёт crest — тавтология устранена

Δcrest теперь считается **против мастера**, а не против самого файла:

| метрика | значение |
|---|---|
| Δcrest медиана | **0.075 дБ** |
| Δcrest p95 | **0.285 дБ** |
| Δcrest максимум | **0.532 дБ** |
| **тавтологичных (Δ == baseline)** | **15 из 147** — случайные совпадения, не построенные |

Раньше было **276 из 276**. Сейчас совпадение — редкость, а не правило.

## 3. Третья метрика «громкость атаки» — по вашему допуску 0.60 дБ

Атака = максимум первых 10 мс относительно пика. Мерю **Δ атаки** «файл против
мастера», а не абсолютный уровень (первая моя попытка сравнивала абсолют — это
была ошибка, 120 «нарушений» из ничего).

| Δ атаки | значение |
|---|---|
| медиана | **0.076 дБ** |
| p95 | **0.294 дБ** |
| максимум | **0.387 дБ** |
| вне допуска 0.60 | **0** |
| не измерима (нет атаки в первых 10 мс) | **1** |

Допуск **0.60** подтверждается: шумовой пол p95 = 0.294, запас **2.0×**.
Метрика рабочая и не валит ничего лишнего.

## 4. Вердикт по 147 файлам

| | |
|---|---:|
| файлов проверено | **147** |
| стационарных / транзиентных | **33 / 114** |
| **Δcrest вне допуска** | **0** |
| **Δатаки вне 0.60** | **0** |
| не измерима атака | 1 |

## 5. Поправка к цифре «канон заявляет 96, фактически 62–73 kbps»

В З-31 сказано: «канон заявляет 96 kbps, фактически 62–73 kbps (VBR)». Проверил
по всем 144 файлам, считая факт как `размер × 8 / длительность`:

| банк | медиана | диапазон |
|---|---:|---|
| канон 144 | **139 kbps** | 55.7–301.7 |
| 3.8.0 132 | **178 kbps** | 81–302 |

**Медиана канона — 139, а не 62–73.** Ниже 85 kbps — только **31 файл из 144**,
и это как раз длинные ambient-петли, где VBR экономит. Так что цифра «62–73»
описывает **худшие файлы**, а не банк. Не спорю с выводом (VBR действительно
даёт меньше номинала), уточняю масштаб — иначе в отчётах появится «весь канон
тише заявленного», а это неправда.

Для моих 132: медиана **178 kbps**, у ambient **152–170** при номинале 160 —
здесь согласен с вашей проверкой, всё в порядке.

## Полная таблица (147 файлов)

| файл | тип | факт. kbps | baseline | **допуск** | Δcrest | Δатаки (0–10 мс) | вердикт |
|---|---|---:|---:|---:|---:|---:|---|
| `sounds_380/entity/infected_silverfish_hurt_01.ogg` | транз | 210 | 0.536 | **0.60** | 0.532 | 0.292 | ✓ |
| `sounds_380/entity/infected_stray_attack_01.ogg` | транз | 216 | 0.407 | **0.60** | 0.402 | 0.299 | ✓ |
| `sounds_380/entity/infected_magma_cube_attack_01.ogg` | транз | 200 | 0.391 | **0.60** | 0.385 | 0.199 | ✓ |
| `sounds_380/entity/infected_evoker_death_01.ogg` | транз | 163 | 0.345 | **0.60** | 0.347 | 0.291 | ✓ |
| `sounds_380/entity/infected_magma_cube_hurt_01.ogg` | транз | 227 | 0.344 | **0.60** | 0.343 | 0.151 | ✓ |
| `sounds_380/entity/infected_warden_death_01.ogg` | транз | 168 | 0.338 | **0.60** | 0.336 | 0.334 | ✓ |
| `sounds_380/entity/infected_vex_attack_01.ogg` | транз | 189 | 0.286 | **0.60** | 0.286 | 0.008 | ✓ |
| `sounds_380/entity/infected_ravager_attack_01.ogg` | транз | 188 | 0.284 | **0.60** | 0.285 | 0.000 | ✓ |
| `sounds_380/entity/infected_phantom_attack_01.ogg` | транз | 190 | 0.259 | **0.60** | 0.258 | 0.225 | ✓ |
| `sounds_380/entity/infected_illusioner_hurt_01.ogg` | транз | 210 | 0.254 | **0.60** | 0.253 | 0.045 | ✓ |
| `sounds_380/entity/infected_creaking_hurt_01.ogg` | транз | 212 | 0.156 | **0.60** | 0.250 | 0.085 | ✓ |
| `sounds_380/entity/infected_warden_hurt_01.ogg` | транз | 211 | 0.243 | **0.60** | 0.242 | 0.000 | ✓ |
| `sounds_380/entity/infected_creaking_ambient_01.ogg` | стац | 160 | 0.246 | **0.30** | 0.241 | 0.093 | ✓ |
| `sounds_380/entity/infected_breeze_attack_01.ogg` | транз | 184 | 0.238 | **0.60** | 0.237 | 0.028 | ✓ |
| `sounds_380/entity/infected_shulker_death_01.ogg` | транз | 167 | 0.237 | **0.60** | 0.237 | 0.131 | ✓ |
| `sounds_380/entity/infected_evoker_attack_01.ogg` | транз | 204 | 0.226 | **0.60** | 0.226 | 0.383 | ✓ |
| `sounds_380/entity/infected_creaking_attack_01.ogg` | транз | 215 | 0.203 | **0.60** | 0.204 | 0.254 | ✓ |
| `sounds_380/entity/infected_zombie_villager_ambient_01.ogg` | стац | 152 | 0.216 | **0.27** | 0.202 | 0.236 | ✓ |
| `sounds_380/entity/infected_illusioner_ambient_01.ogg` | стац | 156 | 0.178 | **0.23** | 0.188 | 0.144 | ✓ |
| `sounds_380/entity/infected_blaze_hurt_01.ogg` | транз | 226 | 0.184 | **0.60** | 0.181 | 0.000 | ✓ |
| `sounds_380/entity/infected_elder_guardian_ambient_01.ogg` | стац | 171 | 0.183 | **0.23** | 0.180 | 0.081 | ✓ |
| `sounds_380/entity/infected_shulker_ambient_01.ogg` | стац | 164 | 0.181 | **0.23** | 0.180 | 0.102 | ✓ |
| `sounds_380/entity/infected_endermite_hurt_01.ogg` | транз | 238 | 0.178 | **0.60** | 0.178 | 0.000 | ✓ |
| `sounds_380/entity/infected_husk_death_01.ogg` | транз | 164 | 0.186 | **0.60** | 0.177 | 0.157 | ✓ |
| `sounds_380/entity/infected_phantom_ambient_01.ogg` | стац | 160 | 0.168 | **0.22** | 0.172 | 0.032 | ✓ |
| `sounds_380/entity/infected_ravager_ambient_01.ogg` | стац | 158 | 0.168 | **0.22** | 0.170 | 0.297 | ✓ |
| `sounds_380/entity/infected_enderman_ambient_01.ogg` | стац | 154 | 0.166 | **0.22** | 0.168 | 0.343 | ✓ |
| `sounds_380/entity/infected_husk_attack_01.ogg` | транз | 178 | 0.167 | **0.60** | 0.168 | 0.092 | ✓ |
| `sounds_380/entity/infected_blaze_death_01.ogg` | транз | 172 | 0.166 | **0.60** | 0.166 | 0.162 | ✓ |
| `sounds_380/entity/infected_stray_death_01.ogg` | транз | 187 | 0.160 | **0.60** | 0.159 | 0.097 | ✓ |
| `sounds_380/entity/infected_endermite_death_01.ogg` | транз | 173 | 0.151 | **0.60** | 0.157 | 0.387 | ✓ |
| `sounds_380/entity/infected_wither_attack_01.ogg` | транз | 253 | 0.154 | **0.60** | 0.154 | 0.055 | ✓ |
| `sounds_380/entity/infected_guardian_attack_01.ogg` | транз | 200 | 0.149 | **0.60** | 0.148 | 0.033 | ✓ |
| `sounds_380/entity/infected_slime_hurt_01.ogg` | транз | 227 | 0.149 | **0.60** | 0.147 | 0.068 | ✓ |
| `sounds_380/entity/infected_breeze_ambient_01.ogg` | стац | 158 | 0.109 | **0.16** | 0.142 | 0.085 | ✓ |
| `sounds_380/entity/infected_hoglin_attack_01.ogg` | транз | 204 | 0.140 | **0.60** | 0.142 | 0.164 | ✓ |
| `sounds_380/entity/infected_breeze_death_01.ogg` | транз | 164 | 0.139 | **0.60** | 0.140 | 0.294 | ✓ |
| `sounds_380/entity/infected_guardian_hurt_01.ogg` | транз | 237 | 0.142 | **0.60** | 0.139 | 0.037 | ✓ |
| `sounds_380/entity/infected_cave_spider_hurt_01.ogg` | транз | 224 | 0.141 | **0.60** | 0.138 | 0.055 | ✓ |
| `sounds_380/entity/infected_hoglin_ambient_01.ogg` | стац | 158 | 0.137 | **0.19** | 0.138 | 0.081 | ✓ |
| `sounds_380/entity/infected_enderman_attack_01.ogg` | транз | 183 | 0.133 | **0.60** | 0.132 | 0.029 | ✓ |
| `sounds_380/entity/infected_vindicator_ambient_01.ogg` | стац | 153 | 0.125 | **0.17** | 0.130 | 0.107 | ✓ |
| `sounds_380/entity/infected_zombie_villager_attack_01.ogg` | транз | 182 | 0.130 | **0.60** | 0.129 | 0.120 | ✓ |
| `sounds_380/entity/infected_blaze_ambient_01.ogg` | стац | 157 | 0.123 | **0.17** | 0.127 | 0.257 | ✓ |
| `sounds_380/entity/infected_drowned_death_01.ogg` | транз | 177 | 0.123 | **0.60** | 0.127 | 0.111 | ✓ |
| `sounds_380/entity/infected_pillager_death_01.ogg` | транз | 163 | 0.121 | **0.60** | 0.124 | 0.178 | ✓ |
| `sounds_380/entity/infected_blaze_attack_01.ogg` | транз | 191 | 0.124 | **0.60** | 0.123 | 0.168 | ✓ |
| `sounds_380/entity/infected_bogged_ambient_01.ogg` | стац | 169 | 0.123 | **0.17** | 0.122 | 0.203 | ✓ |
| `sounds_380/entity/infected_warden_ambient_01.ogg` | стац | 158 | 0.113 | **0.16** | 0.114 | 0.237 | ✓ |
| `sounds_380/entity/infected_elder_guardian_attack_01.ogg` | транз | 203 | 0.110 | **0.60** | 0.111 | 0.154 | ✓ |
| `sounds_380/entity/infected_endermite_attack_01.ogg` | транз | 189 | 0.110 | **0.60** | 0.111 | 0.003 | ✓ |
| `sounds_380/entity/infected_illusioner_death_01.ogg` | транз | 160 | 0.109 | **0.60** | 0.110 | 0.125 | ✓ |
| `sounds_380/entity/infected_zoglin_death_01.ogg` | транз | 171 | 0.105 | **0.60** | 0.109 | 0.052 | ✓ |
| `sounds_380/entity/infected_magma_cube_death_01.ogg` | транз | 168 | 0.106 | **0.60** | 0.108 | 0.106 | ✓ |
| `sounds_380/entity/infected_ravager_hurt_01.ogg` | транз | 219 | 0.108 | **0.60** | 0.108 | 0.029 | ✓ |
| `sounds_380/entity/infected_pillager_ambient_01.ogg` | стац | 155 | 0.098 | **0.15** | 0.106 | 0.160 | ✓ |
| `sounds_380/entity/infected_piglin_brute_death_01.ogg` | транз | 166 | 0.064 | **0.60** | 0.105 | 0.043 | ✓ |
| `sounds_380/entity/infected_bogged_death_01.ogg` | транз | 176 | 0.124 | **0.60** | 0.097 | 0.084 | ✓ |
| `sounds_380/entity/infected_cave_spider_ambient_01.ogg` | стац | 160 | 0.096 | **0.15** | 0.096 | 0.181 | ✓ |
| `sounds_380/entity/infected_bogged_hurt_01.ogg` | транз | 273 | 0.097 | **0.60** | 0.095 | 0.184 | ✓ |
| `sounds_380/entity/infected_wither_skeleton_hurt_01.ogg` | транз | 242 | 0.040 | **0.60** | 0.094 | 0.176 | ✓ |
| `sounds_380/entity/infected_breeze_hurt_01.ogg` | транз | 240 | 0.093 | **0.60** | 0.092 | 0.000 | ✓ |
| `sounds_380/entity/infected_ravager_death_01.ogg` | транз | 166 | 0.090 | **0.60** | 0.092 | 0.002 | ✓ |
| `sounds_380/entity/infected_vindicator_death_01.ogg` | транз | 159 | 0.089 | **0.60** | 0.092 | 0.076 | ✓ |
| `sounds_380/entity/infected_ghast_hurt_01.ogg` | транз | 220 | 0.096 | **0.60** | 0.089 | 0.117 | ✓ |
| `sounds_380/entity/infected_cave_spider_attack_01.ogg` | транз | 195 | 0.088 | **0.60** | 0.087 | 0.105 | ✓ |
| `sounds_380/entity/infected_phantom_death_01.ogg` | транз | 168 | 0.089 | **0.60** | 0.087 | 0.122 | ✓ |
| `sounds_380/entity/infected_witch_ambient_01.ogg` | стац | 152 | 0.088 | **0.14** | 0.086 | 0.176 | ✓ |
| `sounds_380/entity/infected_zoglin_attack_01.ogg` | транз | 211 | 0.079 | **0.60** | 0.080 | 0.002 | ✓ |
| `sounds_380/entity/infected_piglin_brute_attack_01.ogg` | транз | 204 | 0.089 | **0.60** | 0.079 | 0.153 | ✓ |
| `sounds_380/entity/infected_pillager_attack_01.ogg` | транз | 186 | 0.081 | **0.60** | 0.078 | 0.050 | ✓ |
| `sounds_380/entity/infected_stray_hurt_01.ogg` | транз | 249 | 0.052 | **0.60** | 0.077 | 0.061 | ✓ |
| `sounds_380/entity/infected_endermite_ambient_01.ogg` | стац | 158 | 0.063 | **0.11** | 0.075 | 0.289 | ✓ |
| `sounds_380/entity/infected_evoker_ambient_01.ogg` | стац | 152 | 0.073 | **0.12** | 0.075 | 0.113 | ✓ |
| `sounds_380/entity/infected_vex_ambient_01.ogg` | стац | 162 | 0.068 | **0.12** | 0.075 | 0.331 | ✓ |
| `sounds_380/entity/infected_evoker_hurt_01.ogg` | транз | 217 | 0.072 | **0.60** | 0.071 | 0.017 | ✓ |
| `sounds_380/entity/infected_piglin_ambient_01.ogg` | стац | 151 | 0.068 | **0.12** | 0.071 | 0.107 | ✓ |
| `sounds_380/entity/infected_creaking_death_01.ogg` | транз | 170 | 0.068 | **0.60** | 0.069 | 0.188 | ✓ |
| `sounds_380/entity/infected_husk_ambient_01.ogg` | стац | 154 | 0.071 | **0.12** | 0.069 | 0.066 | ✓ |
| `sounds_380/entity/infected_witch_hurt_01.ogg` | транз | 226 | 0.063 | **0.60** | 0.065 | 0.001 | ✓ |
| `sounds_380/entity/infected_zoglin_hurt_01.ogg` | транз | 228 | 0.082 | **0.60** | 0.064 | 0.116 | ✓ |
| `sounds_380/entity/infected_guardian_death_01.ogg` | транз | 175 | 0.063 | **0.60** | 0.062 | 0.008 | ✓ |
| `sounds_380/entity/infected_wither_hurt_01.ogg` | транз | 296 | 0.061 | **0.60** | 0.061 | 0.055 | ✓ |
| `sounds_380/entity/infected_vex_death_01.ogg` | транз | 166 | 0.061 | **0.60** | 0.060 | 0.003 | ✓ |
| `sounds_380/entity/infected_vindicator_attack_01.ogg` | транз | 182 | 0.057 | **0.60** | 0.057 | 0.092 | ✓ |
| `sounds_380/entity/infected_zoglin_ambient_01.ogg` | стац | 160 | 0.131 | **0.18** | 0.055 | 0.005 | ✓ |
| `sounds_380/entity/infected_enderman_death_01.ogg` | транз | 168 | 0.048 | **0.60** | 0.049 | 0.020 | ✓ |
| `sounds_380/entity/infected_warden_attack_01.ogg` | транз | 205 | 0.078 | **0.60** | 0.048 | 0.161 | ✓ |
| `sounds_380/entity/infected_piglin_death_01.ogg` | транз | 163 | 0.046 | **0.60** | 0.047 | 0.018 | ✓ |
| `sounds_380/entity/infected_magma_cube_ambient_01.ogg` | стац | 162 | 0.043 | **0.09** | 0.045 | 0.056 | ✓ |
| `sounds_380/entity/infected_drowned_ambient_01.ogg` | стац | 166 | 0.019 | **0.07** | 0.041 | 0.062 | ✓ |
| `sounds_380/entity/infected_stray_ambient_01.ogg` | стац | 171 | 0.042 | **0.09** | 0.041 | 0.004 | ✓ |
| `sounds_380/entity/infected_hoglin_death_01.ogg` | транз | 160 | 0.045 | **0.60** | 0.039 | 0.038 | ✓ |
| `sounds_380/entity/infected_silverfish_death_01.ogg` | транз | 169 | 0.032 | **0.60** | 0.039 | 0.134 | ✓ |
| `sounds/hive/hive_spawn_hurt_04` | транз | 302 | 0.171 | **0.60** | 0.039 | 0.046 | ✓ |
| `sounds_380/entity/infected_elder_guardian_death_01.ogg` | транз | 185 | 0.039 | **0.60** | 0.036 | 0.018 | ✓ |
| `sounds_380/entity/infected_drowned_hurt_01.ogg` | транз | 242 | 0.031 | **0.60** | 0.034 | 0.105 | ✓ |
| `sounds_380/entity/infected_phantom_hurt_01.ogg` | транз | 229 | 0.029 | **0.60** | 0.034 | 0.160 | ✓ |
| `sounds_380/entity/infected_vindicator_hurt_01.ogg` | транз | 212 | 0.037 | **0.60** | 0.033 | 0.015 | ✓ |
| `sounds_380/entity/infected_bogged_attack_01.ogg` | транз | 219 | 0.036 | **0.60** | 0.032 | 0.000 | ✓ |
| `sounds_380/entity/infected_illusioner_attack_01.ogg` | транз | 186 | 0.031 | **0.60** | 0.031 | 0.019 | ✓ |
| `sounds/hive/hive_spawn_hurt_01` | транз | 153 | 0.016 | **0.60** | 0.030 | 0.049 | ✓ |
| `sounds_380/entity/infected_husk_hurt_01.ogg` | транз | 228 | 0.028 | **0.60** | 0.028 | 0.027 | ✓ |
| `sounds_380/entity/infected_slime_attack_01.ogg` | транз | 185 | 0.029 | **0.60** | 0.028 | 0.149 | ✓ |
| `sounds_380/entity/infected_wither_skeleton_death_01.ogg` | транз | 181 | 0.031 | **0.60** | 0.028 | 0.108 | ✓ |
| `sounds_380/entity/infected_pillager_hurt_01.ogg` | транз | 233 | 0.026 | **0.60** | 0.027 | 0.036 | ✓ |
| `sounds_380/entity/infected_zombie_villager_death_01.ogg` | транз | 164 | 0.026 | **0.60** | 0.026 | 0.009 | ✓ |
| `sounds/combat/combat_deflect_01_chitin` | транз | 183 | 0.309 | **0.60** | 0.026 | 0.000 | ✓ |
| `sounds_380/entity/infected_elder_guardian_hurt_01.ogg` | транз | 245 | 0.026 | **0.60** | 0.025 | 0.144 | ✓ |
| `sounds_380/entity/infected_piglin_brute_hurt_01.ogg` | транз | 223 | 0.024 | **0.60** | 0.025 | 0.036 | ✓ |
| `sounds/combat/combat_deflect_04_glance` | транз | 171 | 0.074 | **0.60** | 0.025 | 0.000 | ✓ |
| `sounds/combat/combat_deflect_02_bone` | транз | 143 | 0.059 | **0.60** | 0.022 | 0.000 | ✓ |
| `sounds_380/entity/infected_wither_ambient_01.ogg` | стац | 168 | 0.025 | **0.08** | 0.021 | 0.184 | ✓ |
| `sounds_380/entity/infected_ghast_ambient_01.ogg` | стац | 154 | 0.014 | **0.06** | 0.020 | 0.077 | ✓ |
| `sounds_380/entity/infected_hoglin_hurt_01.ogg` | транз | 212 | 0.025 | **0.60** | 0.019 | 0.000 | ✓ |
| `sounds_380/entity/infected_drowned_attack_01.ogg` | транз | 219 | 0.013 | **0.60** | 0.018 | 0.115 | ✓ |
| `sounds_380/entity/infected_enderman_hurt_01.ogg` | транз | 220 | 0.016 | **0.60** | 0.017 | 0.032 | ✓ |
| `sounds_380/entity/infected_ghast_death_01.ogg` | транз | 157 | 0.018 | **0.60** | 0.015 | 0.065 | ✓ |
| `sounds_380/entity/infected_guardian_ambient_01.ogg` | стац | 172 | 0.014 | **0.06** | 0.015 | 0.042 | ✓ |
| `sounds/combat/dismember_01` | транз | 183 | 0.082 | **0.60** | 0.015 | 0.050 | ✓ |
| `sounds_380/entity/infected_piglin_attack_01.ogg` | транз | 194 | 0.011 | **0.60** | 0.013 | 0.078 | ✓ |
| `sounds_380/entity/infected_silverfish_attack_01.ogg` | транз | 202 | 0.014 | **0.60** | 0.013 | 0.079 | ✓ |
| `sounds_380/entity/infected_wither_skeleton_attack_01.ogg` | транз | 231 | 0.015 | **0.60** | 0.013 | 0.132 | ✓ |
| `sounds/combat/combat_stab_02_chitin` | транз | 197 | 0.055 | **0.60** | 0.013 | 0.000 | ✓ |
| `sounds_380/entity/infected_piglin_hurt_01.ogg` | транз | 210 | 0.012 | **0.60** | 0.012 | 0.063 | ✓ |
| `sounds_380/entity/infected_piglin_brute_ambient_01.ogg` | стац | 158 | 0.016 | **0.07** | 0.011 | 0.027 | ✓ |
| `sounds_380/entity/infected_slime_death_01.ogg` | транз | 164 | 0.010 | **0.60** | 0.011 | 0.042 | ✓ |
| `sounds_380/entity/infected_vex_hurt_01.ogg` | транз | 221 | 0.018 | **0.60** | 0.010 | 0.066 | ✓ |
| `sounds/hive/hive_spread_01_creep` | транз | 81 | 0.066 | **0.60** | 0.009 | н/д | ✓ |
| `sounds_380/entity/infected_silverfish_ambient_01.ogg` | стац | 159 | 0.031 | **0.08** | 0.008 | 0.170 | ✓ |
| `sounds_380/entity/infected_witch_attack_01.ogg` | транз | 205 | 0.006 | **0.60** | 0.007 | 0.052 | ✓ |
| `sounds/flesh/flesh_block_step_01` | транз | 137 | 0.053 | **0.60** | 0.007 | 0.258 | ✓ |
| `sounds_380/entity/infected_shulker_attack_01.ogg` | транз | 190 | 0.008 | **0.60** | 0.006 | 0.018 | ✓ |
| `sounds_380/entity/infected_shulker_hurt_01.ogg` | транз | 221 | 0.007 | **0.60** | 0.006 | 0.262 | ✓ |
| `sounds_380/entity/infected_witch_death_01.ogg` | транз | 168 | 0.020 | **0.60** | 0.006 | 0.024 | ✓ |
| `sounds_380/entity/infected_ghast_attack_01.ogg` | транз | 199 | 0.004 | **0.60** | 0.005 | 0.112 | ✓ |
| `sounds/combat/combat_stab_03_shield` | транз | 171 | 0.056 | **0.60** | 0.004 | 0.001 | ✓ |
| `sounds_380/entity/infected_wither_death_01.ogg` | транз | 188 | 0.001 | **0.60** | 0.003 | 0.003 | ✓ |
| `sounds/combat/combat_deflect_05_parry` | транз | 146 | 0.006 | **0.60** | 0.003 | 0.000 | ✓ |
| `sounds/combat/combat_stab_01_bone` | транз | 157 | 0.003 | **0.60** | 0.003 | 0.012 | ✓ |
| `sounds_380/entity/infected_slime_ambient_01.ogg` | стац | 152 | 0.033 | **0.08** | 0.002 | 0.126 | ✓ |
| `sounds/combat/combat_deflect_03_metal` | транз | 157 | 0.005 | **0.60** | 0.002 | 0.000 | ✓ |
| `sounds_380/entity/infected_cave_spider_death_01.ogg` | транз | 170 | 0.000 | **0.60** | 0.001 | 0.030 | ✓ |
| `sounds_380/entity/infected_wither_skeleton_ambient_01.ogg` | стац | 176 | 0.012 | **0.06** | 0.001 | 0.017 | ✓ |
| `sounds_380/entity/infected_zombie_villager_hurt_01.ogg` | транз | 226 | 0.003 | **0.60** | 0.001 | 0.031 | ✓ |
| `sounds/hive/hive_spawn_attack_02` | транз | 156 | 0.033 | **0.60** | 0.001 | 0.023 | ✓ |
| `sounds/combat/combat_flesh_hit_deep_01_axe` | транз | 113 | 0.049 | **0.60** | 0.000 | 0.072 | ✓ |
