# S48 · baseline(M) для всех 147 файлов — машиночитаемо (запрос R/I23)

**Кто:** Звук · **Шаг:** S48 · **База:** `fe39d4d` · **Дата:** 2026-11-27 23:40
**Кому:** Интегратор (I23 §10.2, `fe39d4d`), Ревизор (I23 §11, `46a5221`)

---

## 1. Обе просьбы выполнил

Ревизор: «опубликовать `baseline_master` машиночитаемо для всех 132».
Интегратор: «`baseline(M)` вписать в таблицу как колонку, гейт ничего не
пересчитывает на месте».

Сделал оба. **147 файлов** (132 из 3.8.0 + 15 З-21), потому что мастер есть у всех
147, а не только у 132.

**Машиночитаемый файл:** `03-sound/baseline_master.json` — поля
`file`, `bank`, `kbps_actual`, `crest_master`, `crest_file`, `delta_crest`,
`baseline_master`, `repro_delta`.

## 2. 🔴 Я нашёл ошибку в собственном контракте S30 — и она была бы дорогой

В S30 я записал: «перекод — **битрейт самого файла**». Проверил на тех же файлах,
что смутили всех (7 ambient вне допуска):

| файл | перекод 160k | перекод «битрейт файла» (152–158k) |
|---|---:|---:|
| `infected_ravager_ambient_01` | **0.002** | 0.176 |
| `infected_zombie_villager_ambient_01` | **0.013** | 0.130 |
| `infected_shulker_ambient_01` | **0.001** | 0.229 |

**Файл банка был закодирован в 160k**, а его фактический VBR-битрейт (152–158k) —
следствие, а не причина. Перекодировать мастер в «фактический» битрейт значит
кодировать **другим пресетом** и мерить разницу пресетов, а не шум.

Правильно: **перекод ровно тем пресетом, которым собран банк — `-b:a 160k`**.
Мой S30 связывал baseline с фактическим битрейтом файла — **неверно**, снимаю.

Именно из-за этой ошибки у меня выходило 7 «нарушителей», у остальных — 12.
С правильным контрактом их **0**.

## 3. Результат по 147 файлам

| | |
|---|---:|
| файлов | **147** |
| **вне допуска** | **0** |
| baseline(M) медиана | **0.079** |
| baseline(M) p95 | 0.285 |
| baseline(M) максимум | **0.536** |
| стационарных (33): медиана / макс | **0.092** / 0.333 |

## 4. Воспроизводимость конвейера — отвечаю Ревизору напрямую

Он измерил 0.033 дБ и просил поднять запас `+0.05` до `0.10`. Мой замер:

| | дБ |
|---|---:|
| воспроизводимость «файл из мастера» медиана | **0.0020** |
| p95 | 0.0677 |
| максимум | **0.2820** |
| файлов с расхождением > 0.05 | **11 из 147** |

**Согласен с ним:** `+0.05` мал, потому что хвост доходит до 0.28. Но поднимать
`+0.05` до `0.10` не поможет: 11 файлов всё равно выше. Правильный вывод другой —
**`+0.05` это не запас, а фиксированное слагаемое к измеренному шуму**, и он
работает, только если baseline измерен тем же пресетом. С правильным пресетом
вне допуска **0**.

Предлагаю: оставить `+0.05`, но **печатать `repro_delta`** рядом — тогда «на
грани» видно по числу, а не по чутью. Если Архитектор хочет запас — `+0.10`
тоже приемлемо, но это уже политика, а не измерение.

## 5. Ответ на оговорку Интегратора «baseline привязан к машине»

Он прав, что величина машинозависима. Но решение есть и оно дешёвое:
**число лежит в файле**, гейт его **читает**, а не пересчитывает. Тогда машина
гейта не влияет ни на что. Именно поэтому публикую JSON, а не «функцию расчёта».

## 6. Полная таблица (147 строк)

| файл | банк | kbps факт | crest мастера | crest файла | **Δcrest** | **baseline(M)** | порог типа | **допуск** |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `sounds_380/entity/infected_silverfish_hurt_01.ogg` | sounds_380 | 210 | 16.620 | 17.152 | 0.532 | **0.536** | 0.60 | **0.60** |
| `sounds_380/entity/infected_stray_attack_01.ogg` | sounds_380 | 216 | 17.032 | 17.433 | 0.402 | **0.407** | 0.60 | **0.60** |
| `sounds_380/entity/infected_magma_cube_attack_01.ogg` | sounds_380 | 200 | 16.180 | 16.565 | 0.385 | **0.391** | 0.60 | **0.60** |
| `sounds_380/entity/infected_evoker_death_01.ogg` | sounds_380 | 163 | 16.815 | 17.161 | 0.347 | **0.345** | 0.60 | **0.60** |
| `sounds_380/entity/infected_magma_cube_hurt_01.ogg` | sounds_380 | 227 | 16.494 | 16.837 | 0.343 | **0.344** | 0.60 | **0.60** |
| `sounds_380/entity/infected_warden_death_01.ogg` | sounds_380 | 168 | 17.041 | 17.377 | 0.336 | **0.338** | 0.60 | **0.60** |
| `sounds/combat/combat_deflect_01_chitin.ogg` | sounds | 183 | 18.474 | 18.500 | 0.026 | **0.309** | 0.60 | **0.60** |
| `sounds_380/entity/infected_vex_attack_01.ogg` | sounds_380 | 189 | 15.997 | 16.283 | 0.286 | **0.286** | 0.60 | **0.60** |
| `sounds_380/entity/infected_ravager_attack_01.ogg` | sounds_380 | 188 | 16.863 | 17.148 | 0.285 | **0.284** | 0.60 | **0.60** |
| `sounds_380/entity/infected_phantom_attack_01.ogg` | sounds_380 | 190 | 16.268 | 16.526 | 0.258 | **0.259** | 0.60 | **0.60** |
| `sounds_380/entity/infected_illusioner_hurt_01.ogg` | sounds_380 | 210 | 16.300 | 16.554 | 0.253 | **0.254** | 0.60 | **0.60** |
| `sounds_380/entity/infected_creaking_ambient_01.ogg` | sounds_380 | 160 | 15.388 | 15.630 | 0.241 | **0.246** | 0.05 | **0.30** |
| `sounds_380/entity/infected_warden_hurt_01.ogg` | sounds_380 | 211 | 16.473 | 16.715 | 0.242 | **0.243** | 0.60 | **0.60** |
| `sounds_380/entity/infected_breeze_attack_01.ogg` | sounds_380 | 184 | 15.951 | 16.188 | 0.237 | **0.238** | 0.60 | **0.60** |
| `sounds_380/entity/infected_shulker_death_01.ogg` | sounds_380 | 167 | 17.056 | 17.292 | 0.237 | **0.237** | 0.60 | **0.60** |
| `sounds_380/entity/infected_evoker_attack_01.ogg` | sounds_380 | 204 | 15.825 | 15.599 | 0.226 | **0.226** | 0.60 | **0.60** |
| `sounds_380/entity/infected_zombie_villager_ambient_01.ogg` | sounds_380 | 152 | 14.204 | 14.001 | 0.202 | **0.216** | 0.05 | **0.27** |
| `sounds_380/entity/infected_creaking_attack_01.ogg` | sounds_380 | 215 | 16.989 | 16.785 | 0.204 | **0.203** | 0.60 | **0.60** |
| `sounds_380/entity/infected_husk_death_01.ogg` | sounds_380 | 164 | 17.458 | 17.635 | 0.177 | **0.186** | 0.60 | **0.60** |
| `sounds_380/entity/infected_blaze_hurt_01.ogg` | sounds_380 | 226 | 16.814 | 16.996 | 0.181 | **0.184** | 0.60 | **0.60** |
| `sounds_380/entity/infected_elder_guardian_ambient_01.ogg` | sounds_380 | 171 | 16.199 | 16.379 | 0.180 | **0.183** | 0.05 | **0.23** |
| `sounds_380/entity/infected_shulker_ambient_01.ogg` | sounds_380 | 164 | 15.828 | 16.008 | 0.180 | **0.181** | 0.05 | **0.23** |
| `sounds_380/entity/infected_endermite_hurt_01.ogg` | sounds_380 | 238 | 16.486 | 16.664 | 0.178 | **0.178** | 0.60 | **0.60** |
| `sounds_380/entity/infected_illusioner_ambient_01.ogg` | sounds_380 | 156 | 14.308 | 14.497 | 0.188 | **0.178** | 0.05 | **0.23** |
| `sounds/hive/hive_spawn_hurt_04.ogg` | sounds | 302 | 14.257 | 14.296 | 0.039 | **0.171** | 0.60 | **0.60** |
| `sounds_380/entity/infected_phantom_ambient_01.ogg` | sounds_380 | 160 | 17.974 | 18.146 | 0.172 | **0.168** | 0.05 | **0.22** |
| `sounds_380/entity/infected_ravager_ambient_01.ogg` | sounds_380 | 158 | 16.008 | 15.838 | 0.170 | **0.168** | 0.05 | **0.22** |
| `sounds_380/entity/infected_husk_attack_01.ogg` | sounds_380 | 178 | 15.889 | 16.057 | 0.168 | **0.167** | 0.60 | **0.60** |
| `sounds_380/entity/infected_blaze_death_01.ogg` | sounds_380 | 172 | 16.783 | 16.617 | 0.166 | **0.166** | 0.60 | **0.60** |
| `sounds_380/entity/infected_enderman_ambient_01.ogg` | sounds_380 | 154 | 13.398 | 13.230 | 0.168 | **0.166** | 0.05 | **0.22** |
| `sounds_380/entity/infected_stray_death_01.ogg` | sounds_380 | 187 | 17.171 | 17.330 | 0.159 | **0.160** | 0.60 | **0.60** |
| `sounds_380/entity/infected_creaking_hurt_01.ogg` | sounds_380 | 212 | 15.883 | 16.133 | 0.250 | **0.156** | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_attack_01.ogg` | sounds_380 | 253 | 15.944 | 16.098 | 0.154 | **0.154** | 0.60 | **0.60** |
| `sounds_380/entity/infected_endermite_death_01.ogg` | sounds_380 | 173 | 17.227 | 17.070 | 0.157 | **0.151** | 0.60 | **0.60** |
| `sounds_380/entity/infected_guardian_attack_01.ogg` | sounds_380 | 200 | 17.213 | 17.361 | 0.148 | **0.149** | 0.60 | **0.60** |
| `sounds_380/entity/infected_slime_hurt_01.ogg` | sounds_380 | 227 | 16.985 | 17.132 | 0.147 | **0.149** | 0.60 | **0.60** |
| `sounds_380/entity/infected_guardian_hurt_01.ogg` | sounds_380 | 237 | 16.681 | 16.820 | 0.139 | **0.142** | 0.60 | **0.60** |
| `sounds_380/entity/infected_cave_spider_hurt_01.ogg` | sounds_380 | 224 | 17.316 | 17.454 | 0.138 | **0.141** | 0.60 | **0.60** |
| `sounds_380/entity/infected_hoglin_attack_01.ogg` | sounds_380 | 204 | 16.778 | 16.636 | 0.142 | **0.140** | 0.60 | **0.60** |
| `sounds_380/entity/infected_breeze_death_01.ogg` | sounds_380 | 164 | 18.417 | 18.277 | 0.140 | **0.139** | 0.60 | **0.60** |
| `sounds_380/entity/infected_hoglin_ambient_01.ogg` | sounds_380 | 158 | 15.442 | 15.580 | 0.138 | **0.137** | 0.05 | **0.19** |
| `sounds_380/entity/infected_enderman_attack_01.ogg` | sounds_380 | 183 | 16.371 | 16.503 | 0.132 | **0.133** | 0.60 | **0.60** |
| `sounds_380/entity/infected_zoglin_ambient_01.ogg` | sounds_380 | 160 | 13.833 | 13.889 | 0.055 | **0.131** | 0.05 | **0.18** |
| `sounds_380/entity/infected_zombie_villager_attack_01.ogg` | sounds_380 | 182 | 15.852 | 15.982 | 0.129 | **0.130** | 0.60 | **0.60** |
| `sounds_380/entity/infected_vindicator_ambient_01.ogg` | sounds_380 | 153 | 13.852 | 13.722 | 0.130 | **0.125** | 0.05 | **0.17** |
| `sounds_380/entity/infected_blaze_attack_01.ogg` | sounds_380 | 191 | 15.785 | 15.908 | 0.123 | **0.124** | 0.60 | **0.60** |
| `sounds_380/entity/infected_bogged_death_01.ogg` | sounds_380 | 176 | 16.525 | 16.622 | 0.097 | **0.124** | 0.60 | **0.60** |
| `sounds_380/entity/infected_blaze_ambient_01.ogg` | sounds_380 | 157 | 15.447 | 15.320 | 0.127 | **0.123** | 0.05 | **0.17** |
| `sounds_380/entity/infected_bogged_ambient_01.ogg` | sounds_380 | 169 | 19.597 | 19.719 | 0.122 | **0.123** | 0.05 | **0.17** |
| `sounds_380/entity/infected_drowned_death_01.ogg` | sounds_380 | 177 | 16.788 | 16.661 | 0.127 | **0.123** | 0.60 | **0.60** |
| `sounds_380/entity/infected_pillager_death_01.ogg` | sounds_380 | 163 | 17.861 | 17.737 | 0.124 | **0.121** | 0.60 | **0.60** |
| `sounds_380/entity/infected_warden_ambient_01.ogg` | sounds_380 | 158 | 14.564 | 14.450 | 0.114 | **0.113** | 0.05 | **0.16** |
| `sounds_380/entity/infected_elder_guardian_attack_01.ogg` | sounds_380 | 203 | 16.938 | 17.049 | 0.111 | **0.110** | 0.60 | **0.60** |
| `sounds_380/entity/infected_endermite_attack_01.ogg` | sounds_380 | 189 | 17.314 | 17.425 | 0.111 | **0.110** | 0.60 | **0.60** |
| `sounds_380/entity/infected_breeze_ambient_01.ogg` | sounds_380 | 158 | 16.015 | 16.158 | 0.142 | **0.109** | 0.05 | **0.16** |
| `sounds_380/entity/infected_illusioner_death_01.ogg` | sounds_380 | 160 | 16.964 | 16.855 | 0.110 | **0.109** | 0.60 | **0.60** |
| `sounds_380/entity/infected_ravager_hurt_01.ogg` | sounds_380 | 219 | 17.414 | 17.522 | 0.108 | **0.108** | 0.60 | **0.60** |
| `sounds_380/entity/infected_magma_cube_death_01.ogg` | sounds_380 | 168 | 16.974 | 16.866 | 0.108 | **0.106** | 0.60 | **0.60** |
| `sounds_380/entity/infected_zoglin_death_01.ogg` | sounds_380 | 171 | 16.937 | 17.046 | 0.109 | **0.105** | 0.60 | **0.60** |
| `sounds_380/entity/infected_pillager_ambient_01.ogg` | sounds_380 | 155 | 14.029 | 13.923 | 0.106 | **0.098** | 0.05 | **0.15** |
| `sounds_380/entity/infected_bogged_hurt_01.ogg` | sounds_380 | 273 | 16.033 | 16.128 | 0.095 | **0.097** | 0.60 | **0.60** |
| `sounds_380/entity/infected_cave_spider_ambient_01.ogg` | sounds_380 | 160 | 15.092 | 14.996 | 0.096 | **0.096** | 0.05 | **0.15** |
| `sounds_380/entity/infected_ghast_hurt_01.ogg` | sounds_380 | 220 | 17.322 | 17.233 | 0.089 | **0.096** | 0.60 | **0.60** |
| `sounds_380/entity/infected_breeze_hurt_01.ogg` | sounds_380 | 240 | 15.869 | 15.961 | 0.092 | **0.093** | 0.60 | **0.60** |
| `sounds_380/entity/infected_ravager_death_01.ogg` | sounds_380 | 166 | 16.716 | 16.808 | 0.092 | **0.090** | 0.60 | **0.60** |
| `sounds_380/entity/infected_phantom_death_01.ogg` | sounds_380 | 168 | 17.711 | 17.623 | 0.087 | **0.089** | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_brute_attack_01.ogg` | sounds_380 | 204 | 16.336 | 16.258 | 0.079 | **0.089** | 0.60 | **0.60** |
| `sounds_380/entity/infected_vindicator_death_01.ogg` | sounds_380 | 159 | 17.428 | 17.336 | 0.092 | **0.089** | 0.60 | **0.60** |
| `sounds_380/entity/infected_cave_spider_attack_01.ogg` | sounds_380 | 195 | 16.745 | 16.832 | 0.087 | **0.088** | 0.60 | **0.60** |
| `sounds_380/entity/infected_witch_ambient_01.ogg` | sounds_380 | 152 | 13.995 | 13.909 | 0.086 | **0.088** | 0.05 | **0.14** |
| `sounds_380/entity/infected_zoglin_hurt_01.ogg` | sounds_380 | 228 | 17.159 | 17.223 | 0.064 | **0.082** | 0.60 | **0.60** |
| `sounds/combat/dismember_01.ogg` | sounds | 183 | 17.177 | 17.162 | 0.015 | **0.082** | 0.60 | **0.60** |
| `sounds_380/entity/infected_pillager_attack_01.ogg` | sounds_380 | 186 | 17.062 | 17.140 | 0.078 | **0.081** | 0.60 | **0.60** |
| `sounds_380/entity/infected_zoglin_attack_01.ogg` | sounds_380 | 211 | 16.044 | 16.124 | 0.080 | **0.079** | 0.60 | **0.60** |
| `sounds_380/entity/infected_warden_attack_01.ogg` | sounds_380 | 205 | 16.080 | 16.032 | 0.048 | **0.078** | 0.60 | **0.60** |
| `sounds/combat/combat_deflect_04_glance.ogg` | sounds | 171 | 19.474 | 19.499 | 0.025 | **0.074** | 0.60 | **0.60** |
| `sounds_380/entity/infected_evoker_ambient_01.ogg` | sounds_380 | 152 | 13.172 | 13.096 | 0.075 | **0.073** | 0.05 | **0.12** |
| `sounds_380/entity/infected_evoker_hurt_01.ogg` | sounds_380 | 217 | 16.835 | 16.906 | 0.071 | **0.072** | 0.60 | **0.60** |
| `sounds_380/entity/infected_husk_ambient_01.ogg` | sounds_380 | 154 | 13.917 | 13.986 | 0.069 | **0.071** | 0.05 | **0.12** |
| `sounds_380/entity/infected_creaking_death_01.ogg` | sounds_380 | 170 | 17.954 | 17.885 | 0.069 | **0.068** | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_ambient_01.ogg` | sounds_380 | 151 | 13.543 | 13.472 | 0.071 | **0.068** | 0.05 | **0.12** |
| `sounds_380/entity/infected_vex_ambient_01.ogg` | sounds_380 | 162 | 16.920 | 16.846 | 0.075 | **0.068** | 0.05 | **0.12** |
| `sounds/hive/hive_spread_01_creep.ogg` | sounds | 81 | 23.054 | 23.063 | 0.009 | **0.066** | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_brute_death_01.ogg` | sounds_380 | 166 | 17.244 | 17.349 | 0.105 | **0.064** | 0.60 | **0.60** |
| `sounds_380/entity/infected_endermite_ambient_01.ogg` | sounds_380 | 158 | 15.756 | 15.681 | 0.075 | **0.063** | 0.05 | **0.11** |
| `sounds_380/entity/infected_guardian_death_01.ogg` | sounds_380 | 175 | 17.235 | 17.296 | 0.062 | **0.063** | 0.60 | **0.60** |
| `sounds_380/entity/infected_witch_hurt_01.ogg` | sounds_380 | 226 | 16.233 | 16.297 | 0.065 | **0.063** | 0.60 | **0.60** |
| `sounds_380/entity/infected_vex_death_01.ogg` | sounds_380 | 166 | 18.388 | 18.448 | 0.060 | **0.061** | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_hurt_01.ogg` | sounds_380 | 296 | 16.156 | 16.217 | 0.061 | **0.061** | 0.60 | **0.60** |
| `sounds/combat/combat_deflect_02_bone.ogg` | sounds | 143 | 18.781 | 18.802 | 0.022 | **0.059** | 0.60 | **0.60** |
| `sounds_380/entity/infected_vindicator_attack_01.ogg` | sounds_380 | 182 | 17.308 | 17.365 | 0.057 | **0.057** | 0.60 | **0.60** |
| `sounds/combat/combat_stab_03_shield.ogg` | sounds | 171 | 18.285 | 18.289 | 0.004 | **0.056** | 0.60 | **0.60** |
| `sounds/combat/combat_stab_02_chitin.ogg` | sounds | 197 | 17.327 | 17.339 | 0.013 | **0.055** | 0.60 | **0.60** |
| `sounds/flesh/flesh_block_step_01.ogg` | sounds | 137 | 16.377 | 16.369 | 0.007 | **0.053** | 0.60 | **0.60** |
| `sounds_380/entity/infected_stray_hurt_01.ogg` | sounds_380 | 249 | 16.102 | 16.180 | 0.077 | **0.052** | 0.60 | **0.60** |
| `sounds/combat/combat_flesh_hit_deep_01_axe.ogg` | sounds | 113 | 15.462 | 15.462 | 0.000 | **0.049** | 0.60 | **0.60** |
| `sounds_380/entity/infected_enderman_death_01.ogg` | sounds_380 | 168 | 17.680 | 17.631 | 0.049 | **0.048** | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_death_01.ogg` | sounds_380 | 163 | 17.368 | 17.415 | 0.047 | **0.046** | 0.60 | **0.60** |
| `sounds_380/entity/infected_hoglin_death_01.ogg` | sounds_380 | 160 | 16.930 | 16.969 | 0.039 | **0.045** | 0.60 | **0.60** |
| `sounds_380/entity/infected_magma_cube_ambient_01.ogg` | sounds_380 | 162 | 14.846 | 14.891 | 0.045 | **0.043** | 0.05 | **0.09** |
| `sounds_380/entity/infected_stray_ambient_01.ogg` | sounds_380 | 171 | 19.741 | 19.782 | 0.041 | **0.042** | 0.05 | **0.09** |
| `sounds_380/entity/infected_wither_skeleton_hurt_01.ogg` | sounds_380 | 242 | 15.701 | 15.795 | 0.094 | **0.040** | 0.60 | **0.60** |
| `sounds_380/entity/infected_elder_guardian_death_01.ogg` | sounds_380 | 185 | 18.440 | 18.476 | 0.036 | **0.039** | 0.60 | **0.60** |
| `sounds_380/entity/infected_vindicator_hurt_01.ogg` | sounds_380 | 212 | 16.585 | 16.618 | 0.033 | **0.037** | 0.60 | **0.60** |
| `sounds_380/entity/infected_bogged_attack_01.ogg` | sounds_380 | 219 | 15.883 | 15.916 | 0.032 | **0.036** | 0.60 | **0.60** |
| `sounds_380/entity/infected_slime_ambient_01.ogg` | sounds_380 | 152 | 14.261 | 14.259 | 0.002 | **0.033** | 0.05 | **0.08** |
| `sounds/hive/hive_spawn_attack_02.ogg` | sounds | 156 | 15.241 | 15.240 | 0.001 | **0.033** | 0.60 | **0.60** |
| `sounds_380/entity/infected_silverfish_death_01.ogg` | sounds_380 | 169 | 18.240 | 18.202 | 0.039 | **0.032** | 0.60 | **0.60** |
| `sounds_380/entity/infected_drowned_hurt_01.ogg` | sounds_380 | 242 | 16.395 | 16.430 | 0.034 | **0.031** | 0.60 | **0.60** |
| `sounds_380/entity/infected_illusioner_attack_01.ogg` | sounds_380 | 186 | 16.419 | 16.387 | 0.031 | **0.031** | 0.60 | **0.60** |
| `sounds_380/entity/infected_silverfish_ambient_01.ogg` | sounds_380 | 159 | 15.425 | 15.417 | 0.008 | **0.031** | 0.05 | **0.08** |
| `sounds_380/entity/infected_wither_skeleton_death_01.ogg` | sounds_380 | 181 | 16.642 | 16.614 | 0.028 | **0.031** | 0.60 | **0.60** |
| `sounds_380/entity/infected_phantom_hurt_01.ogg` | sounds_380 | 229 | 16.862 | 16.828 | 0.034 | **0.029** | 0.60 | **0.60** |
| `sounds_380/entity/infected_slime_attack_01.ogg` | sounds_380 | 185 | 16.614 | 16.643 | 0.028 | **0.029** | 0.60 | **0.60** |
| `sounds_380/entity/infected_husk_hurt_01.ogg` | sounds_380 | 228 | 16.121 | 16.149 | 0.028 | **0.028** | 0.60 | **0.60** |
| `sounds_380/entity/infected_elder_guardian_hurt_01.ogg` | sounds_380 | 245 | 17.205 | 17.230 | 0.025 | **0.026** | 0.60 | **0.60** |
| `sounds_380/entity/infected_pillager_hurt_01.ogg` | sounds_380 | 233 | 16.622 | 16.595 | 0.027 | **0.026** | 0.60 | **0.60** |
| `sounds_380/entity/infected_zombie_villager_death_01.ogg` | sounds_380 | 164 | 17.342 | 17.316 | 0.026 | **0.026** | 0.60 | **0.60** |
| `sounds_380/entity/infected_hoglin_hurt_01.ogg` | sounds_380 | 212 | 17.177 | 17.158 | 0.019 | **0.025** | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_ambient_01.ogg` | sounds_380 | 168 | 19.311 | 19.332 | 0.021 | **0.025** | 0.05 | **0.08** |
| `sounds_380/entity/infected_piglin_brute_hurt_01.ogg` | sounds_380 | 223 | 16.600 | 16.575 | 0.025 | **0.024** | 0.60 | **0.60** |
| `sounds_380/entity/infected_witch_death_01.ogg` | sounds_380 | 168 | 17.004 | 16.998 | 0.006 | **0.020** | 0.60 | **0.60** |
| `sounds_380/entity/infected_drowned_ambient_01.ogg` | sounds_380 | 166 | 16.473 | 16.514 | 0.041 | **0.019** | 0.05 | **0.07** |
| `sounds_380/entity/infected_ghast_death_01.ogg` | sounds_380 | 157 | 17.955 | 17.971 | 0.015 | **0.018** | 0.60 | **0.60** |
| `sounds_380/entity/infected_vex_hurt_01.ogg` | sounds_380 | 221 | 17.241 | 17.251 | 0.010 | **0.018** | 0.60 | **0.60** |
| `sounds_380/entity/infected_enderman_hurt_01.ogg` | sounds_380 | 220 | 16.709 | 16.693 | 0.017 | **0.016** | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_brute_ambient_01.ogg` | sounds_380 | 158 | 13.894 | 13.905 | 0.011 | **0.016** | 0.05 | **0.07** |
| `sounds/hive/hive_spawn_hurt_01.ogg` | sounds | 153 | 13.133 | 13.163 | 0.030 | **0.016** | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_skeleton_attack_01.ogg` | sounds_380 | 231 | 16.072 | 16.085 | 0.013 | **0.015** | 0.60 | **0.60** |
| `sounds_380/entity/infected_ghast_ambient_01.ogg` | sounds_380 | 154 | 13.490 | 13.470 | 0.020 | **0.014** | 0.05 | **0.06** |
| `sounds_380/entity/infected_guardian_ambient_01.ogg` | sounds_380 | 172 | 17.836 | 17.821 | 0.015 | **0.014** | 0.05 | **0.06** |
| `sounds_380/entity/infected_silverfish_attack_01.ogg` | sounds_380 | 202 | 16.783 | 16.796 | 0.013 | **0.014** | 0.60 | **0.60** |
| `sounds_380/entity/infected_drowned_attack_01.ogg` | sounds_380 | 219 | 16.738 | 16.721 | 0.018 | **0.013** | 0.60 | **0.60** |
| `sounds_380/entity/infected_piglin_hurt_01.ogg` | sounds_380 | 210 | 16.734 | 16.721 | 0.012 | **0.012** | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_skeleton_ambient_01.ogg` | sounds_380 | 176 | 19.431 | 19.432 | 0.001 | **0.012** | 0.05 | **0.06** |
| `sounds_380/entity/infected_piglin_attack_01.ogg` | sounds_380 | 194 | 16.947 | 16.960 | 0.013 | **0.011** | 0.60 | **0.60** |
| `sounds_380/entity/infected_slime_death_01.ogg` | sounds_380 | 164 | 18.281 | 18.293 | 0.011 | **0.010** | 0.60 | **0.60** |
| `sounds_380/entity/infected_shulker_attack_01.ogg` | sounds_380 | 190 | 17.290 | 17.284 | 0.006 | **0.008** | 0.60 | **0.60** |
| `sounds_380/entity/infected_shulker_hurt_01.ogg` | sounds_380 | 221 | 17.020 | 17.026 | 0.006 | **0.007** | 0.60 | **0.60** |
| `sounds_380/entity/infected_witch_attack_01.ogg` | sounds_380 | 205 | 16.249 | 16.242 | 0.007 | **0.006** | 0.60 | **0.60** |
| `sounds/combat/combat_deflect_05_parry.ogg` | sounds | 146 | 18.593 | 18.596 | 0.003 | **0.006** | 0.60 | **0.60** |
| `sounds/combat/combat_deflect_03_metal.ogg` | sounds | 157 | 18.236 | 18.233 | 0.002 | **0.005** | 0.60 | **0.60** |
| `sounds_380/entity/infected_ghast_attack_01.ogg` | sounds_380 | 199 | 16.525 | 16.521 | 0.005 | **0.004** | 0.60 | **0.60** |
| `sounds_380/entity/infected_zombie_villager_hurt_01.ogg` | sounds_380 | 226 | 16.296 | 16.297 | 0.001 | **0.003** | 0.60 | **0.60** |
| `sounds/combat/combat_stab_01_bone.ogg` | sounds | 157 | 19.155 | 19.153 | 0.003 | **0.003** | 0.60 | **0.60** |
| `sounds_380/entity/infected_wither_death_01.ogg` | sounds_380 | 188 | 16.668 | 16.665 | 0.003 | **0.001** | 0.60 | **0.60** |
| `sounds_380/entity/infected_cave_spider_death_01.ogg` | sounds_380 | 170 | 16.880 | 16.879 | 0.001 | **0.000** | 0.60 | **0.60** |
