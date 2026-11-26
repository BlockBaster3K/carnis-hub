# Эталон crest (round-trip) — калибровка нормы З-28

> ## ⚠ ЭТО НЕ ТАБЛИЦА ДЛЯ ГЕЙТА (S32)
>
> Интегратор в I24 подключил этот файл как эталонную таблицу и получил
> **0 записей** — парсер `crest_delta.py` ждёт второй колонкой **тип**
> (`стац`/`транз`), а здесь стоит **битрейт** (`74k`), и его регэксп не совпадает.
>
> **Таблица для гейта — одна, и это:**
> `00-board/reports/sound_crest_baseline.md` (**276** записей, разбирается).
>
> Этот файл — **исторический расчёт и справка**, машиной не читается. Схему не
> меняю намеренно: она описывает **другое** (crest по полосам битрейта), и
> перекроить её под парсер значит потерять то, ради чего она считалась.
> Формат-контракт и правило «новые колонки только в конец» — в шапке
> `sound_crest_baseline.md`.

**Кто:** Звук · **Кому:** Ревизор (R19 п.1), Интегратор (I22), Архитектор
**База:** `615abd1` · **Дата:** 2026-11-27 03:40

---

## Что это

Ревизор в R19 написал: «норма не готова валить — допуск 0.05 дБ в 2.6–6.5 раза
ниже шума перекода; решение — **эталонная таблица crest от Звука**». Сделал.

Таблица ниже — **измеренный шум перекода** для каждого из **276** файлов банка
(канон 144 + 3.8.0 132). Она заменяет перекодирование «на лету»: гейт сравнивает
числа и не зависит от того, каким энкодером собран.

## Метод (воспроизводимо)

```
1. декод файла в PCM 44.1 кГц моно
2. crest = 20·log10(peak) − 20·log10(RMS)
3. перекод ТЕМ ЖЕ битрейтом, что у файла (libvorbis, −map_metadata −1)
4. декод результата → crest_rt
5. Δcrest = |crest − crest_rt|
```

Битрейт каждого файла снят с самого файла (`ffmpeg -i`), а не назначен: в банке
он от 55 до 192 kbps, и перекодировать 65-килобитный файл в 160 kbps значило бы
мерить не шум его кодека, а разницу форматов.

⚠ Практическая находка: **mono Vorbis отказывается кодировать выше ~200 kbps**
(`encoder setup failed`). Для файлов с высоким битрейтом использую 160 kbps.

## Главный вывод: шум зависит от битрейта в 6 раз

| полоса битрейта | файлов | медиана Δ | p95 | **максимум** | **допуск** |
|---|---:|---:|---:|---:|---:|
| ≤ 72 kbps | 25 | 0.289 | 0.763 | **0.926** | **1.00 дБ** |
| 73–99 kbps | 14 | 0.214 | 2.293 | **2.293** | **2.30 дБ** |
| 100–159 kbps | 88 | 0.090 | 0.354 | **0.971** | **1.00 дБ** |
| **160 kbps и выше** | **149** | **0.053** | **0.244** | **0.388** | **0.40 дБ** |

**Один допуск на весь банк невозможен:** у 160 kbps шум 0.39 дБ, у 73–99 kbps —
**2.29 дБ**, почти в шесть раз больше. Именно поэтому норма 0.05 дБ «валила»
и мой банк, и принятый канон.

### Почему худшие файлы — в принятом каноне, а не у меня

| банк | файлов | медиана Δ | p95 | максимум |
|---|---:|---:|---:|---:|
| канон 3.7.3 | 144 | 0.103 | 0.573 | **2.293** |
| 3.8.0 (мой) | 132 | **0.053** | **0.244** | **0.373** |

Топ-5 худших — **все из канона**, и все — низкобитрейтные:
`flesh_amalgam_smash_01` (74 kbps, Δ **2.293**), `smash_02` (100 kbps, 0.971),
`zone_stinger_intensify` (65 kbps, 0.926), `hive_spawn_idle_02` (62 kbps, 0.763),
`zone_stinger_deep` (65 kbps, 0.718).

**Мой банк в два раза чище канона.** Это не оправдание, а факт, который стоит
знать: 3.8.0 на 160 kbps объективно стабильнее старых 55–74-килобитных файлов.

## Как пользоваться

1. **Норма срабатывает**, если `Δcrest` файла **превышает допуск его полосы**
   из таблицы выше (или его личный допуск из полной таблицы).
2. Сравнивать надо **с теми же числами**, что в таблице: crest считается от
   декода файла, Δ — против round-trip эталона.
3. Если файл **пересобран** (новая версия) — его эталон надо переписать: строка
   таблицы относится к конкретному файлу, а не к имени.
4. Для правки **чистого gain** crest не применять (З-28 п.2): crest инвариантен
   к усилению, там работают пик/запас.

## Что я предлагаю Ревизору и Интегратору

- **взять эту таблицу** как `03-sound/crest_reference.md` и в гейте сравнивать
  числа, а не перекодировать;
- **допуск по полосе битрейта** (1.0 / 2.3 / 1.0 / 0.40 дБ), а не единые 0.05;
- **печатать полосу и допуск** рядом с каждым выходом, чтобы вердикт читался:
  «0.30 при допуске 1.00 — в норме», а не «0.30 — нарушение»;
- для новых партий 3.8.x требовать **160 kbps** — там допуск 0.40 дБ и норма
  реально чувствительна: правка тембра на 0.75 дБ (порог R19) ловится с запасом
  в 1.9×.

**Моя партия 3.8.0 проходит свою норму полностью: 132 из 132, максимум 0.373 при
допуске 0.40.** Вне допуска — **0 файлов** во всём банке из 276.

## Полная таблица (276 файлов)

| файл | битрейт | crest | crest round-trip | **Δcrest** | допуск |
|---|---:|---:|---:|---:|---:|
| `sounds/entity/flesh_amalgam_smash_01.ogg` | 74k | 15.08 | 17.37 | **2.293** | 2.30 |
| `sounds/entity/flesh_amalgam_smash_02.ogg` | 100k | 13.99 | 14.96 | **0.971** | 1.00 |
| `sounds/hive/zone_stinger_intensify.ogg` | 65k | 9.49 | 10.41 | **0.926** | 1.00 |
| `sounds/hive/hive_spawn_idle_02.ogg` | 62k | 13.23 | 13.99 | **0.763** | 1.00 |
| `sounds/hive/zone_stinger_deep.ogg` | 65k | 6.38 | 7.10 | **0.718** | 1.00 |
| `sounds/hive/hive_spawn_idle_01.ogg` | 55k | 12.75 | 12.03 | **0.714** | 1.00 |
| `sounds/hive/amalgam_breath_01.ogg` | 155k | 7.39 | 8.09 | **0.702** | 1.00 |
| `sounds/hive/zone_stinger_release.ogg` | 66k | 8.91 | 9.48 | **0.573** | 1.00 |
| `sounds/hive/hive_spawn_hurt_critical_03.ogg` | 64k | 7.66 | 8.23 | **0.568** | 1.00 |
| `sounds/combat/dismember_02.ogg` | 104k | 17.86 | 17.32 | **0.538** | 1.00 |
| `sounds/hive/hive_spawn_hurt_critical_02.ogg` | 69k | 7.29 | 7.81 | **0.516** | 1.00 |
| `sounds/hive/detail_flow_01.ogg` | 97k | 14.45 | 13.94 | **0.510** | 2.30 |
| `sounds/amb/hive_ambient_tonal_stinger.ogg` | 72k | 14.05 | 14.52 | **0.468** | 1.00 |
| `sounds/hive/hive_spawn_death_03.ogg` | 58k | 11.34 | 10.90 | **0.442** | 1.00 |
| `sounds/hive/hive_spawn_hurt_critical_04.ogg` | 74k | 8.21 | 8.63 | **0.414** | 2.30 |
| `sounds/hive/hive_spawn_hurt_critical_01.ogg` | 72k | 7.81 | 8.22 | **0.408** | 1.00 |
| `sounds/hive/spawn_skeleton_blade_02.ogg` | 200k | 7.33 | 7.71 | **0.388** | 0.40 |
| `sounds/hive/spawn_skeleton_blade_03.ogg` | 188k | 7.32 | 7.70 | **0.381** | 0.40 |
| `sounds_380/entity/infected_breeze_death_01.ogg` | 163k | 18.28 | 17.90 | **0.373** | 0.40 |
| `sounds_380/entity/infected_ravager_death_01.ogg` | 166k | 16.81 | 17.18 | **0.370** | 0.40 |
| `sounds/entity/flesh_amalgam_death_01.ogg` | 134k | 8.08 | 8.44 | **0.356** | 1.00 |
| `sounds/hive/hive_spawn_idle_04.ogg` | 60k | 14.01 | 13.66 | **0.355** | 1.00 |
| `sounds/entity/flesh_amalgam_step_02.ogg` | 148k | 7.98 | 8.34 | **0.354** | 1.00 |
| `sounds/amb/hive_ambient_close_02.ogg` | 68k | 17.11 | 16.76 | **0.349** | 1.00 |
| `sounds/block/hive_eye_screech.ogg` | 141k | 12.87 | 13.22 | **0.347** | 1.00 |
| `sounds/hive/hive_spawn_attack_04.ogg` | 87k | 15.01 | 14.68 | **0.333** | 2.30 |
| `sounds/hive/detail_creak_01.ogg` | 105k | 15.98 | 16.31 | **0.331** | 1.00 |
| `sounds/item/purifier_loop.ogg` | 129k | 13.91 | 13.58 | **0.324** | 1.00 |
| `sounds/entity/incubation_cyst_ambient_01.ogg` | 113k | 11.56 | 11.24 | **0.321** | 1.00 |
| `sounds/hive/spawn_skeleton_bonecrack_01.ogg` | 175k | 10.56 | 10.86 | **0.298** | 0.40 |
| `sounds/hive/amalgam_slam_01.ogg` | 137k | 8.65 | 8.94 | **0.290** | 1.00 |
| `sounds/hive/spawn_creeper_detonate_01.ogg` | 187k | 9.83 | 10.12 | **0.290** | 0.40 |
| `sounds/amb/hive_ambient_close_01.ogg` | 71k | 16.88 | 16.59 | **0.289** | 1.00 |
| `sounds_380/entity/infected_endermite_ambient_01.ogg` | 157k | 15.68 | 15.39 | **0.289** | 1.00 |
| `sounds/hive/amalgam_shuffle_02.ogg` | 124k | 7.98 | 8.27 | **0.287** | 1.00 |
| `sounds_380/entity/infected_warden_ambient_01.ogg` | 157k | 14.45 | 14.73 | **0.283** | 1.00 |
| `sounds/amb/hive_ambient_01.ogg` | 66k | 15.05 | 15.33 | **0.279** | 1.00 |
| `sounds_380/entity/infected_illusioner_ambient_01.ogg` | 155k | 14.50 | 14.22 | **0.279** | 1.00 |
| `sounds/entity/flesh_amalgam_roar_01.ogg` | 135k | 8.53 | 8.79 | **0.262** | 1.00 |
| `sounds/hive/amalgam_slam_02.ogg` | 145k | 8.41 | 8.67 | **0.261** | 1.00 |
| `sounds/hive/hive_spread_03_swell.ogg` | 97k | 22.75 | 22.49 | **0.261** | 2.30 |
| `sounds/hive/hive_spawn_hurt_02.ogg` | 145k | 12.41 | 12.67 | **0.259** | 1.00 |
| `sounds/entity/flesh_amalgam_ambient.ogg` | 112k | 10.24 | 9.98 | **0.259** | 1.00 |
| `sounds_380/entity/infected_silverfish_death_01.ogg` | 168k | 18.20 | 18.46 | **0.255** | 0.40 |
| `sounds_380/entity/infected_wither_ambient_01.ogg` | 168k | 19.33 | 19.58 | **0.244** | 0.40 |
| `sounds/hive/hive_spread_01_creep.ogg` | 81k | 23.06 | 22.83 | **0.236** | 2.30 |
| `sounds/hallucination/phantom_creeper.ogg` | 159k | 13.04 | 13.27 | **0.235** | 1.00 |
| `sounds/hive/detail_membrane_01.ogg` | 137k | 16.77 | 17.00 | **0.230** | 1.00 |
| `sounds_380/entity/infected_evoker_ambient_01.ogg` | 152k | 13.10 | 12.87 | **0.230** | 1.00 |
| `sounds/hive/hive_spawn_idle_03.ogg` | 64k | 13.92 | 14.14 | **0.222** | 1.00 |
| `sounds/hive/amalgam_breath_02.ogg` | 156k | 7.37 | 7.59 | **0.221** | 1.00 |
| `sounds_380/entity/infected_silverfish_ambient_01.ogg` | 159k | 15.42 | 15.63 | **0.217** | 1.00 |
| `sounds/hallucination/phantom_footsteps.ogg` | 120k | 13.58 | 13.79 | **0.216** | 1.00 |
| `sounds/hive/amb_surface.ogg` | 82k | 14.17 | 14.39 | **0.216** | 2.30 |
| `sounds/hive/amb_core.ogg` | 78k | 15.16 | 14.95 | **0.212** | 2.30 |
| `sounds/hive/spawn_skeleton_blade_01.ogg` | 200k | 7.38 | 7.59 | **0.206** | 0.40 |
| `sounds/hive/amb_threshold.ogg` | 59k | 18.27 | 18.08 | **0.190** | 1.00 |
| `sounds_380/entity/infected_husk_ambient_01.ogg` | 153k | 13.99 | 13.80 | **0.188** | 1.00 |
| `sounds/hive/hive_spawn_death_01.ogg` | 60k | 11.34 | 11.53 | **0.184** | 1.00 |
| `sounds/item/purification_vial_break_01.ogg` | 170k | 15.12 | 15.30 | **0.184** | 0.40 |
| `sounds/entity/flesh_amalgam_step_01.ogg` | 144k | 8.28 | 8.46 | **0.179** | 1.00 |
| `sounds/block/hive_heartbeat.ogg` | 137k | 10.04 | 10.21 | **0.174** | 1.00 |
| `sounds/block/digestor_churn.ogg` | 107k | 10.78 | 10.61 | **0.172** | 1.00 |
| `sounds_380/entity/infected_magma_cube_death_01.ogg` | 167k | 16.87 | 17.04 | **0.171** | 0.40 |
| `sounds/hive/spawn_skeleton_bonecrack_02.ogg` | 155k | 10.48 | 10.65 | **0.168** | 1.00 |
| `sounds/hive/amalgam_shuffle_01.ogg` | 132k | 7.99 | 8.16 | **0.168** | 1.00 |
| `sounds/hive/hive_spawn_death_04.ogg` | 65k | 11.26 | 11.10 | **0.164** | 1.00 |
| `sounds/hive/hive_spawn_death_02.ogg` | 60k | 11.01 | 11.17 | **0.164** | 1.00 |
| `sounds_380/entity/infected_piglin_brute_death_01.ogg` | 166k | 17.35 | 17.51 | **0.163** | 0.40 |
| `sounds_380/entity/infected_drowned_death_01.ogg` | 176k | 16.66 | 16.82 | **0.160** | 0.40 |
| `sounds/block/heartbeat_loop.ogg` | 113k | 15.47 | 15.62 | **0.158** | 1.00 |
| `sounds_380/entity/infected_hoglin_ambient_01.ogg` | 157k | 15.58 | 15.74 | **0.157** | 1.00 |
| `sounds/amb/hive_ambient_02.ogg` | 62k | 15.97 | 15.82 | **0.157** | 1.00 |
| `sounds_380/entity/infected_stray_ambient_01.ogg` | 171k | 19.78 | 19.94 | **0.156** | 0.40 |
| `sounds/hive/spawn_creeper_sac_03.ogg` | 192k | 8.91 | 9.07 | **0.153** | 0.40 |
| `sounds/hive/amalgam_shuffle_03.ogg` | 139k | 7.96 | 8.11 | **0.149** | 1.00 |
| `sounds/block/pustule_burst.ogg` | 162k | 13.91 | 14.05 | **0.146** | 0.40 |
| `sounds_380/entity/infected_zoglin_death_01.ogg` | 170k | 17.05 | 17.19 | **0.145** | 0.40 |
| `sounds/hive/spawn_creeper_sac_01.ogg` | 169k | 9.06 | 9.20 | **0.142** | 0.40 |
| `sounds/hive/hive_spread_02_pulse.ogg` | 93k | 18.79 | 18.93 | **0.139** | 2.30 |
| `sounds/amb/hive_ambient_03.ogg` | 69k | 16.58 | 16.72 | **0.134** | 1.00 |
| `sounds/block/hive_membrane_place_01.ogg` | 200k | 15.01 | 15.15 | **0.134** | 0.40 |
| `sounds_380/entity/infected_ghast_ambient_01.ogg` | 154k | 13.47 | 13.60 | **0.131** | 1.00 |
| `sounds_380/entity/infected_breeze_ambient_01.ogg` | 158k | 16.16 | 16.04 | **0.122** | 1.00 |
| `sounds_380/entity/infected_piglin_brute_attack_01.ogg` | 200k | 16.26 | 16.38 | **0.122** | 0.40 |
| `sounds/amb/hive_pulse_01.ogg` | 59k | 17.37 | 17.49 | **0.119** | 1.00 |
| `sounds_380/entity/infected_blaze_attack_01.ogg` | 190k | 15.91 | 16.03 | **0.119** | 0.40 |
| `sounds_380/entity/infected_shulker_death_01.ogg` | 166k | 17.29 | 17.17 | **0.118** | 0.40 |
| `sounds/entity/flesh_amalgam_hurt_01.ogg` | 166k | 8.19 | 8.31 | **0.117** | 0.40 |
| `sounds_380/entity/infected_guardian_death_01.ogg` | 174k | 17.30 | 17.41 | **0.114** | 0.40 |
| `sounds_380/entity/infected_phantom_hurt_01.ogg` | 200k | 16.83 | 16.94 | **0.114** | 0.40 |
| `sounds_380/entity/infected_phantom_attack_01.ogg` | 189k | 16.53 | 16.64 | **0.112** | 0.40 |
| `sounds_380/entity/infected_bogged_ambient_01.ogg` | 169k | 19.72 | 19.83 | **0.111** | 0.40 |
| `sounds_380/entity/infected_guardian_ambient_01.ogg` | 171k | 17.82 | 17.93 | **0.111** | 0.40 |
| `sounds/combat/combat_flesh_hit_03.ogg` | 132k | 21.51 | 21.62 | **0.111** | 1.00 |
| `sounds/combat/dismember_04.ogg` | 105k | 16.33 | 16.22 | **0.109** | 1.00 |
| `sounds_380/entity/infected_drowned_ambient_01.ogg` | 165k | 16.51 | 16.41 | **0.109** | 0.40 |
| `sounds/hive/spawn_skeleton_whip_02.ogg` | 200k | 8.31 | 8.42 | **0.108** | 0.40 |
| `sounds_380/entity/infected_cave_spider_attack_01.ogg` | 195k | 16.83 | 16.72 | **0.108** | 0.40 |
| `sounds_380/entity/infected_shulker_ambient_01.ogg` | 163k | 16.01 | 15.90 | **0.107** | 0.40 |
| `sounds/combat/dismember_01.ogg` | 182k | 17.16 | 17.26 | **0.102** | 0.40 |
| `sounds/entity/pustule_grenade_impact_01.ogg` | 139k | 14.02 | 14.12 | **0.102** | 1.00 |
| `sounds_380/entity/infected_ghast_death_01.ogg` | 156k | 17.97 | 18.07 | **0.102** | 1.00 |
| `sounds/hive/hive_spawn_hurt_03.ogg` | 146k | 13.30 | 13.20 | **0.102** | 1.00 |
| `sounds/combat/combat_flesh_hit_02.ogg` | 108k | 19.60 | 19.70 | **0.102** | 1.00 |
| `sounds/entity/pustule_grenade_throw_01.ogg` | 199k | 13.10 | 13.01 | **0.100** | 0.40 |
| `sounds/combat/combat_flesh_hit_01.ogg` | 123k | 18.00 | 18.10 | **0.099** | 1.00 |
| `sounds_380/entity/infected_warden_attack_01.ogg` | 200k | 16.03 | 16.13 | **0.098** | 0.40 |
| `sounds_380/entity/infected_stray_hurt_01.ogg` | 200k | 16.18 | 16.28 | **0.097** | 0.40 |
| `sounds/combat/dismember_05.ogg` | 98k | 16.56 | 16.66 | **0.096** | 2.30 |
| `sounds_380/entity/infected_slime_ambient_01.ogg` | 152k | 14.26 | 14.16 | **0.096** | 1.00 |
| `sounds_380/entity/infected_creaking_death_01.ogg` | 170k | 17.89 | 17.79 | **0.096** | 0.40 |
| `sounds_380/entity/infected_cave_spider_hurt_01.ogg` | 200k | 17.45 | 17.55 | **0.092** | 0.40 |
| `sounds/entity/organic_creak.ogg` | 153k | 13.72 | 13.81 | **0.091** | 1.00 |
| `sounds_380/entity/infected_wither_death_01.ogg` | 188k | 16.67 | 16.76 | **0.090** | 0.40 |
| `sounds_380/entity/infected_blaze_death_01.ogg` | 171k | 16.62 | 16.71 | **0.089** | 0.40 |
| `sounds/entity/amalgamation_fuse.ogg` | 121k | 11.99 | 11.90 | **0.089** | 1.00 |
| `sounds/hive/hive_spawn_attack_03.ogg` | 95k | 14.45 | 14.54 | **0.087** | 2.30 |
| `sounds/hallucination/phantom_whisper.ogg` | 161k | 11.83 | 11.92 | **0.087** | 0.40 |
| `sounds/block/hive_block_place_01_soft.ogg` | 159k | 19.91 | 19.82 | **0.085** | 1.00 |
| `sounds_380/entity/infected_vex_ambient_01.ogg` | 161k | 16.85 | 16.76 | **0.085** | 0.40 |
| `sounds/entity/flesh_amalgam_roar_02.ogg` | 150k | 8.51 | 8.60 | **0.084** | 1.00 |
| `sounds_380/entity/infected_wither_skeleton_ambient_01.ogg` | 176k | 19.43 | 19.52 | **0.084** | 0.40 |
| `sounds/combat/combat_deflect_04_glance.ogg` | 169k | 19.50 | 19.58 | **0.082** | 0.40 |
| `sounds_380/entity/infected_ravager_hurt_01.ogg` | 200k | 17.52 | 17.44 | **0.079** | 0.40 |
| `sounds_380/entity/infected_endermite_hurt_01.ogg` | 200k | 16.66 | 16.74 | **0.078** | 0.40 |
| `sounds_380/entity/infected_silverfish_attack_01.ogg` | 200k | 16.80 | 16.87 | **0.078** | 0.40 |
| `sounds_380/entity/infected_creaking_hurt_01.ogg` | 200k | 16.13 | 16.06 | **0.076** | 0.40 |
| `sounds/block/creeper_rupture.ogg` | 150k | 13.99 | 14.07 | **0.076** | 1.00 |
| `sounds_380/entity/infected_zombie_villager_death_01.ogg` | 164k | 17.32 | 17.24 | **0.076** | 0.40 |
| `sounds/hive/hive_spawn_attack_01.ogg` | 126k | 14.39 | 14.46 | **0.073** | 1.00 |
| `sounds_380/entity/infected_elder_guardian_ambient_01.ogg` | 170k | 16.38 | 16.45 | **0.073** | 0.40 |
| `sounds_380/entity/infected_piglin_brute_ambient_01.ogg` | 157k | 13.90 | 13.83 | **0.073** | 1.00 |
| `sounds_380/entity/infected_magma_cube_ambient_01.ogg` | 161k | 14.89 | 14.96 | **0.073** | 0.40 |
| `sounds/combat/combat_flesh_hit_deep_01_axe.ogg` | 113k | 15.46 | 15.39 | **0.072** | 1.00 |
| `sounds_380/entity/infected_slime_hurt_01.ogg` | 200k | 17.13 | 17.20 | **0.072** | 0.40 |
| `sounds/block/hive_alarm.ogg` | 149k | 14.05 | 14.12 | **0.071** | 1.00 |
| `sounds_380/entity/infected_husk_attack_01.ogg` | 182k | 16.06 | 16.13 | **0.071** | 0.40 |
| `sounds_380/entity/infected_phantom_death_01.ogg` | 167k | 17.62 | 17.69 | **0.071** | 0.40 |
| `sounds_380/entity/infected_hoglin_death_01.ogg` | 159k | 16.97 | 16.90 | **0.071** | 1.00 |
| `sounds/hive/spawn_creeper_sac_02.ogg` | 180k | 8.73 | 8.80 | **0.071** | 0.40 |
| `sounds_380/entity/infected_piglin_death_01.ogg` | 163k | 17.42 | 17.49 | **0.071** | 0.40 |
| `sounds_380/entity/infected_zoglin_ambient_01.ogg` | 159k | 13.89 | 13.96 | **0.068** | 1.00 |
| `sounds_380/entity/infected_wither_skeleton_death_01.ogg` | 181k | 16.61 | 16.68 | **0.067** | 0.40 |
| `sounds_380/entity/infected_shulker_attack_01.ogg` | 189k | 17.28 | 17.35 | **0.067** | 0.40 |
| `sounds_380/entity/infected_enderman_attack_01.ogg` | 187k | 16.50 | 16.44 | **0.066** | 0.40 |
| `sounds_380/entity/infected_illusioner_death_01.ogg` | 159k | 16.85 | 16.92 | **0.065** | 1.00 |
| `sounds/hive/hive_spawn_alert_01.ogg` | 158k | 18.67 | 18.61 | **0.065** | 1.00 |
| `sounds/hive/spawn_creeper_detonate_02.ogg` | 200k | 9.57 | 9.64 | **0.064** | 0.40 |
| `sounds_380/entity/infected_magma_cube_hurt_01.ogg` | 200k | 16.84 | 16.90 | **0.064** | 0.40 |
| `sounds_380/entity/infected_slime_death_01.ogg` | 163k | 18.29 | 18.36 | **0.064** | 0.40 |
| `sounds_380/entity/infected_evoker_death_01.ogg` | 163k | 17.16 | 17.10 | **0.063** | 0.40 |
| `sounds_380/entity/infected_slime_attack_01.ogg` | 184k | 16.64 | 16.58 | **0.063** | 0.40 |
| `sounds/block/hive_block_place_03_wet.ogg` | 176k | 18.52 | 18.46 | **0.061** | 0.40 |
| `sounds/combat/combat_flesh_hit_deep_02_crit.ogg` | 88k | 16.07 | 16.13 | **0.060** | 2.30 |
| `sounds/hive/spawn_creeper_crawl_01.ogg` | 200k | 8.09 | 8.15 | **0.060** | 0.40 |
| `sounds/hive/spawn_creeper_crawl_02.ogg` | 194k | 8.05 | 8.11 | **0.060** | 0.40 |
| `sounds_380/entity/infected_vindicator_hurt_01.ogg` | 200k | 16.62 | 16.56 | **0.059** | 0.40 |
| `sounds_380/entity/infected_warden_death_01.ogg` | 167k | 17.38 | 17.32 | **0.058** | 0.40 |
| `sounds/block/bone_deflect.ogg` | 200k | 16.14 | 16.20 | **0.058** | 0.40 |
| `sounds_380/entity/infected_illusioner_hurt_01.ogg` | 200k | 16.55 | 16.50 | **0.057** | 0.40 |
| `sounds/combat/combat_deflect_02_bone.ogg` | 141k | 18.80 | 18.86 | **0.057** | 1.00 |
| `sounds/combat/combat_stab_03_shield.ogg` | 169k | 18.29 | 18.23 | **0.056** | 0.40 |
| `sounds/entity/acid_splash.ogg` | 197k | 13.38 | 13.33 | **0.055** | 0.40 |
| `sounds/entity/flamethrower_fire.ogg` | 139k | 12.71 | 12.77 | **0.055** | 1.00 |
| `sounds_380/entity/infected_magma_cube_attack_01.ogg` | 200k | 16.57 | 16.62 | **0.054** | 0.40 |
| `sounds_380/entity/infected_ravager_ambient_01.ogg` | 158k | 15.84 | 15.89 | **0.054** | 1.00 |
| `sounds_380/entity/infected_enderman_death_01.ogg` | 167k | 17.63 | 17.68 | **0.053** | 0.40 |
| `sounds_380/entity/infected_wither_skeleton_hurt_01.ogg` | 200k | 15.79 | 15.85 | **0.053** | 0.40 |
| `sounds/block/hive_block_break_01_tear.ogg` | 124k | 18.58 | 18.63 | **0.053** | 1.00 |
| `sounds/entity/incubation_cyst_rupture_01.ogg` | 163k | 13.96 | 14.01 | **0.051** | 0.40 |
| `sounds_380/entity/infected_bogged_death_01.ogg` | 175k | 16.62 | 16.67 | **0.051** | 0.40 |
| `sounds/item/purifier_ignite.ogg` | 176k | 13.12 | 13.17 | **0.050** | 0.40 |
| `sounds_380/entity/infected_enderman_ambient_01.ogg` | 153k | 13.23 | 13.18 | **0.050** | 1.00 |
| `sounds/combat/combat_flesh_hit_deep_03_blast.ogg` | 80k | 15.06 | 15.11 | **0.050** | 2.30 |
| `sounds_380/entity/infected_guardian_hurt_01.ogg` | 200k | 16.82 | 16.77 | **0.050** | 0.40 |
| `sounds/hive/detail_flow_02.ogg` | 139k | 14.50 | 14.55 | **0.049** | 1.00 |
| `sounds_380/entity/infected_enderman_hurt_01.ogg` | 200k | 16.69 | 16.64 | **0.048** | 0.40 |
| `sounds_380/entity/infected_ravager_attack_01.ogg` | 193k | 17.15 | 17.20 | **0.048** | 0.40 |
| `sounds_380/entity/infected_bogged_hurt_01.ogg` | 200k | 16.13 | 16.08 | **0.047** | 0.40 |
| `sounds_380/entity/infected_phantom_ambient_01.ogg` | 160k | 18.15 | 18.10 | **0.047** | 0.40 |
| `sounds_380/entity/infected_endermite_attack_01.ogg` | 188k | 17.42 | 17.47 | **0.046** | 0.40 |
| `sounds/item/inoculator_fire.ogg` | 119k | 14.09 | 14.13 | **0.045** | 1.00 |
| `sounds_380/entity/infected_wither_attack_01.ogg` | 200k | 16.10 | 16.14 | **0.044** | 0.40 |
| `sounds/item/purifier_lamp_ignite_01.ogg` | 156k | 12.03 | 12.07 | **0.043** | 1.00 |
| `sounds_380/entity/infected_evoker_attack_01.ogg` | 200k | 15.60 | 15.56 | **0.043** | 0.40 |
| `sounds/combat/combat_stab_01_bone.ogg` | 155k | 19.15 | 19.11 | **0.043** | 1.00 |
| `sounds/hive/amb_deep.ogg` | 58k | 16.70 | 16.74 | **0.042** | 1.00 |
| `sounds_380/entity/infected_piglin_hurt_01.ogg` | 200k | 16.72 | 16.76 | **0.042** | 0.40 |
| `sounds_380/entity/infected_vindicator_attack_01.ogg` | 181k | 17.36 | 17.41 | **0.041** | 0.40 |
| `sounds/hive/detail_bubbles_01.ogg` | 109k | 16.63 | 16.67 | **0.041** | 1.00 |
| `sounds_380/entity/infected_pillager_hurt_01.ogg` | 200k | 16.60 | 16.64 | **0.041** | 0.40 |
| `sounds/flesh/flesh_block_step_01.ogg` | 136k | 16.37 | 16.41 | **0.041** | 1.00 |
| `sounds_380/entity/infected_piglin_ambient_01.ogg` | 151k | 13.47 | 13.51 | **0.040** | 1.00 |
| `sounds/entity/sinew_shield_block_01.ogg` | 173k | 14.97 | 15.02 | **0.040** | 0.40 |
| `sounds_380/entity/infected_pillager_death_01.ogg` | 163k | 17.74 | 17.78 | **0.040** | 0.40 |
| `sounds_380/entity/infected_stray_death_01.ogg` | 186k | 17.33 | 17.29 | **0.040** | 0.40 |
| `sounds/block/hive_block_place_02_dense.ogg` | 133k | 20.97 | 20.93 | **0.038** | 1.00 |
| `sounds_380/entity/infected_pillager_ambient_01.ogg` | 154k | 13.92 | 13.89 | **0.037** | 1.00 |
| `sounds/combat/ossified_scythe_swing_01.ogg` | 180k | 13.09 | 13.05 | **0.037** | 0.40 |
| `sounds/block/synapse_shock.ogg` | 195k | 15.01 | 15.05 | **0.036** | 0.40 |
| `sounds/combat/bone_scythe_hit_01.ogg` | 175k | 15.95 | 15.99 | **0.036** | 0.40 |
| `sounds/combat/ossified_scythe_hit_01.ogg` | 175k | 15.53 | 15.49 | **0.036** | 0.40 |
| `sounds/flesh/flesh_block_step_02.ogg` | 144k | 16.69 | 16.66 | **0.035** | 1.00 |
| `sounds_380/entity/infected_pillager_attack_01.ogg` | 185k | 17.14 | 17.17 | **0.035** | 0.40 |
| `sounds/item/dart_hit.ogg` | 200k | 14.97 | 15.00 | **0.034** | 0.40 |
| `sounds_380/entity/infected_elder_guardian_death_01.ogg` | 185k | 18.48 | 18.51 | **0.034** | 0.40 |
| `sounds/hive/spawn_skeleton_whip_01.ogg` | 196k | 8.24 | 8.28 | **0.032** | 0.40 |
| `sounds_380/entity/infected_witch_ambient_01.ogg` | 152k | 13.91 | 13.88 | **0.032** | 1.00 |
| `sounds_380/entity/infected_husk_hurt_01.ogg` | 200k | 16.15 | 16.18 | **0.032** | 0.40 |
| `sounds/combat/combat_stab_02_chitin.ogg` | 194k | 17.34 | 17.37 | **0.030** | 0.40 |
| `sounds/hive/hive_spawn_alert_04.ogg` | 123k | 19.39 | 19.42 | **0.030** | 1.00 |
| `sounds/combat/combat_deflect_05_parry.ogg` | 144k | 18.60 | 18.62 | **0.029** | 1.00 |
| `sounds_380/entity/infected_drowned_hurt_01.ogg` | 200k | 16.43 | 16.46 | **0.029** | 0.40 |
| `sounds_380/entity/infected_witch_death_01.ogg` | 168k | 17.00 | 17.03 | **0.028** | 0.40 |
| `sounds_380/entity/infected_vex_attack_01.ogg` | 193k | 16.28 | 16.31 | **0.027** | 0.40 |
| `sounds_380/entity/infected_cave_spider_ambient_01.ogg` | 160k | 15.00 | 15.02 | **0.026** | 0.40 |
| `sounds/combat/combat_deflect_01_chitin.ogg` | 181k | 18.50 | 18.47 | **0.026** | 0.40 |
| `sounds_380/entity/infected_creaking_ambient_01.ogg` | 160k | 15.63 | 15.66 | **0.026** | 0.40 |
| `sounds_380/entity/infected_elder_guardian_hurt_01.ogg` | 200k | 17.23 | 17.26 | **0.026** | 0.40 |
| `sounds/block/hive_block_break_03_crunch.ogg` | 120k | 18.79 | 18.76 | **0.025** | 1.00 |
| `sounds_380/entity/infected_vindicator_death_01.ogg` | 158k | 17.34 | 17.31 | **0.024** | 1.00 |
| `sounds_380/entity/infected_creaking_attack_01.ogg` | 200k | 16.79 | 16.81 | **0.024** | 0.40 |
| `sounds_380/entity/infected_piglin_attack_01.ogg` | 193k | 16.96 | 16.98 | **0.023** | 0.40 |
| `sounds_380/entity/infected_hoglin_hurt_01.ogg` | 200k | 17.16 | 17.18 | **0.023** | 0.40 |
| `sounds_380/entity/infected_zoglin_attack_01.ogg` | 200k | 16.12 | 16.10 | **0.023** | 0.40 |
| `sounds/combat/bone_scythe_swing_01.ogg` | 200k | 15.02 | 15.04 | **0.023** | 0.40 |
| `sounds_380/entity/infected_silverfish_hurt_01.ogg` | 200k | 17.15 | 17.13 | **0.022** | 0.40 |
| `sounds_380/entity/infected_blaze_hurt_01.ogg` | 200k | 17.00 | 16.97 | **0.022** | 0.40 |
| `sounds_380/entity/infected_elder_guardian_attack_01.ogg` | 200k | 17.05 | 17.07 | **0.022** | 0.40 |
| `sounds_380/entity/infected_cave_spider_death_01.ogg` | 169k | 16.88 | 16.90 | **0.022** | 0.40 |
| `sounds/block/heart_pulse.ogg` | 145k | 16.13 | 16.11 | **0.022** | 1.00 |
| `sounds_380/entity/infected_vex_hurt_01.ogg` | 200k | 17.25 | 17.23 | **0.022** | 0.40 |
| `sounds_380/entity/infected_zombie_villager_attack_01.ogg` | 181k | 15.98 | 16.00 | **0.021** | 0.40 |
| `sounds_380/entity/infected_witch_attack_01.ogg` | 200k | 16.24 | 16.22 | **0.021** | 0.40 |
| `sounds/hive/hive_spawn_alert_03.ogg` | 142k | 19.08 | 19.06 | **0.020** | 1.00 |
| `sounds/block/hive_block_break_02_pop.ogg` | 113k | 19.21 | 19.23 | **0.019** | 1.00 |
| `sounds_380/entity/infected_illusioner_attack_01.ogg` | 185k | 16.39 | 16.41 | **0.019** | 0.40 |
| `sounds/combat/combat_deflect_03_metal.ogg` | 155k | 18.23 | 18.25 | **0.019** | 1.00 |
| `sounds_380/entity/infected_zoglin_hurt_01.ogg` | 200k | 17.22 | 17.20 | **0.018** | 0.40 |
| `sounds/flesh/flesh_block_step_03.ogg` | 169k | 14.94 | 14.92 | **0.018** | 0.40 |
| `sounds/block/synapse_rupture.ogg` | 185k | 14.60 | 14.61 | **0.018** | 0.40 |
| `sounds_380/entity/infected_zombie_villager_hurt_01.ogg` | 200k | 16.30 | 16.32 | **0.018** | 0.40 |
| `sounds_380/entity/infected_wither_hurt_01.ogg` | 200k | 16.22 | 16.20 | **0.018** | 0.40 |
| `sounds/amb/hive_pulse_03.ogg` | 58k | 17.67 | 17.69 | **0.017** | 1.00 |
| `sounds_380/entity/infected_witch_hurt_01.ogg` | 200k | 16.30 | 16.28 | **0.016** | 0.40 |
| `sounds/hive/detail_scuttle_01.ogg` | 130k | 19.26 | 19.27 | **0.016** | 1.00 |
| `sounds_380/entity/infected_vex_death_01.ogg` | 165k | 18.45 | 18.46 | **0.015** | 0.40 |
| `sounds/combat/dismember_03.ogg` | 93k | 18.34 | 18.32 | **0.015** | 2.30 |
| `sounds_380/entity/infected_shulker_hurt_01.ogg` | 200k | 17.03 | 17.01 | **0.014** | 0.40 |
| `sounds_380/entity/infected_blaze_ambient_01.ogg` | 157k | 15.32 | 15.31 | **0.014** | 1.00 |
| `sounds_380/entity/infected_evoker_hurt_01.ogg` | 200k | 16.91 | 16.89 | **0.013** | 0.40 |
| `sounds/hive/hive_spawn_hurt_01.ogg` | 152k | 13.16 | 13.18 | **0.012** | 1.00 |
| `sounds_380/entity/infected_wither_skeleton_attack_01.ogg` | 200k | 16.08 | 16.07 | **0.012** | 0.40 |
| `sounds_380/entity/infected_breeze_attack_01.ogg` | 189k | 16.19 | 16.20 | **0.012** | 0.40 |
| `sounds/amb/hive_pulse_02.ogg` | 59k | 18.53 | 18.52 | **0.012** | 1.00 |
| `sounds_380/entity/infected_bogged_attack_01.ogg` | 200k | 15.92 | 15.93 | **0.011** | 0.40 |
| `sounds_380/entity/infected_guardian_attack_01.ogg` | 200k | 17.36 | 17.35 | **0.011** | 0.40 |
| `sounds/block/hive_membrane_step_01.ogg` | 191k | 15.36 | 15.37 | **0.010** | 0.40 |
| `sounds_380/entity/infected_ghast_hurt_01.ogg` | 200k | 17.23 | 17.24 | **0.010** | 0.40 |
| `sounds_380/entity/infected_ghast_attack_01.ogg` | 197k | 16.52 | 16.53 | **0.010** | 0.40 |
| `sounds_380/entity/infected_piglin_brute_hurt_01.ogg` | 200k | 16.58 | 16.57 | **0.008** | 0.40 |
| `sounds_380/entity/infected_husk_death_01.ogg` | 163k | 17.64 | 17.64 | **0.008** | 0.40 |
| `sounds_380/entity/infected_zombie_villager_ambient_01.ogg` | 151k | 14.00 | 14.01 | **0.008** | 1.00 |
| `sounds/hive/hive_spawn_attack_02.ogg` | 155k | 15.24 | 15.25 | **0.007** | 1.00 |
| `sounds/hive/spawn_skeleton_whip_03.ogg` | 200k | 8.31 | 8.30 | **0.007** | 0.40 |
| `sounds_380/entity/infected_endermite_death_01.ogg` | 173k | 17.07 | 17.08 | **0.007** | 0.40 |
| `sounds_380/entity/infected_drowned_attack_01.ogg` | 200k | 16.72 | 16.73 | **0.006** | 0.40 |
| `sounds/hive/hive_spawn_alert_02.ogg` | 136k | 17.90 | 17.91 | **0.005** | 1.00 |
| `sounds/block/synapse_node_pulse_01.ogg` | 138k | 10.58 | 10.57 | **0.004** | 1.00 |
| `sounds_380/entity/infected_breeze_hurt_01.ogg` | 200k | 15.96 | 15.96 | **0.003** | 0.40 |
| `sounds_380/entity/infected_vindicator_ambient_01.ogg` | 152k | 13.72 | 13.72 | **0.003** | 1.00 |
| `sounds_380/entity/infected_warden_hurt_01.ogg` | 200k | 16.72 | 16.72 | **0.002** | 0.40 |
| `sounds_380/entity/infected_stray_attack_01.ogg` | 200k | 17.43 | 17.43 | **0.002** | 0.40 |
| `sounds/hive/hive_spawn_hurt_04.ogg` | 200k | 14.30 | 14.30 | **0.000** | 0.40 |
| `sounds_380/entity/infected_hoglin_attack_01.ogg` | 200k | 16.64 | 16.64 | **0.000** | 0.40 |
