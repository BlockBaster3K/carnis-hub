# Carnis 3.1.7 — звуковой банк: аудит и самопроверка

## Состояние

- `mod_version=3.1.7` установлен.
- В `ModSounds.java` восстановлены объявления всех прежних 48 IDs; добавлены отдельный `HIVE_HEARTBEAT` для разделения heartbeat и два запрошенных combat IDs (`COMBAT_ARMOR_DEFLECT`, `COMBAT_BLOCK_STAB`). Итого в классе 51 событие.
- `sounds.json` содержит 51 событие; отсутствующие `.ogg` не подменены чужими звуками и не созданы искусственно.
- В целевой папке физически обнаружено 24 OGG. Указанные для восстановления четыре legacy файла сейчас отсутствуют на диске; они задекларированы по заданным путям, ожидая восстановления пользователем.
- `CarnisSoundTypes.java` не изменён: текущий файл — фабрика одного `SoundType`, использующая существующие зарегистрированные события, а не 10 отдельных sound event IDs.
- Сборка Gradle не запускалась.

## Самопроверка

- События в `ModSounds`: 51
- События в `sounds.json`: 51
- Уникальных путей: 94
- Существуют `.ogg`: 23
- Отсутствуют `.ogg`: 71
- Субтитры EN: 51
- Субтитры RU: 51
- Мёртвые subtitle-ключи: 0; обе локали совпадают с набором subtitle ключей событий.
- Лишние физические OGG: 1
- Проверены stream-флаги для трёх ambient loop, close и pulse событий (true) и tonal stinger (false); pitch combat/spawn находится в запрошенных диапазонах.
- Проверены синтаксис JSON и совпадение всех event ID в `ModSounds` и `sounds.json` через Python.

## Отсутствующие звуковые файлы

- `sounds/amb/hive_ambient_01.ogg`
- `sounds/amb/hive_ambient_02.ogg`
- `sounds/amb/hive_ambient_03.ogg`
- `sounds/amb/hive_ambient_close_01.ogg`
- `sounds/amb/hive_ambient_close_02.ogg`
- `sounds/amb/hive_ambient_tonal_stinger.ogg`
- `sounds/amb/hive_pulse_01.ogg`
- `sounds/amb/hive_pulse_02.ogg`
- `sounds/amb/hive_pulse_03.ogg`
- `sounds/block/bone_deflect.ogg`
- `sounds/block/hive_block_break_01_tear.ogg`
- `sounds/block/hive_block_break_02_pop.ogg`
- `sounds/block/hive_block_break_03_crunch.ogg`
- `sounds/block/hive_block_place_01_soft.ogg`
- `sounds/block/hive_block_place_02_dense.ogg`
- `sounds/block/hive_block_place_03_wet.ogg`
- `sounds/combat/combat_deflect_01_chitin.ogg`
- `sounds/combat/combat_deflect_02_bone.ogg`
- `sounds/combat/combat_deflect_03_metal.ogg`
- `sounds/combat/combat_deflect_04_glance.ogg`
- `sounds/combat/combat_deflect_05_parry.ogg`
- `sounds/combat/combat_dismember_01_ribs.ogg`
- `sounds/combat/combat_dismember_02_pustule.ogg`
- `sounds/combat/combat_dismember_03_sinew.ogg`
- `sounds/combat/combat_dismember_04_plate.ogg`
- `sounds/combat/combat_dismember_05_limb.ogg`
- `sounds/combat/combat_flesh_hit_01.ogg`
- `sounds/combat/combat_flesh_hit_02.ogg`
- `sounds/combat/combat_flesh_hit_03.ogg`
- `sounds/combat/combat_flesh_hit_deep_01_axe.ogg`
- `sounds/combat/combat_flesh_hit_deep_02_crit.ogg`
- `sounds/combat/combat_flesh_hit_deep_03_blast.ogg`
- `sounds/combat/combat_stab_01_bone.ogg`
- `sounds/combat/combat_stab_02_chitin.ogg`
- `sounds/combat/combat_stab_03_shield.ogg`
- `sounds/entity/amalgam_step.ogg`
- `sounds/entity/heartbeat_loop.ogg`
- `sounds/entity/organic_creak.ogg`
- `sounds/entity/phantom_footsteps.ogg`
- `sounds/flesh/flesh_block_step_01.ogg`
- `sounds/flesh/flesh_block_step_02.ogg`
- `sounds/flesh/flesh_block_step_03.ogg`
- `sounds/hive/detail_bubbles_01.ogg`
- `sounds/hive/detail_creak_01.ogg`
- `sounds/hive/detail_flow_01.ogg`
- `sounds/hive/detail_flow_02.ogg`
- `sounds/hive/detail_membrane_01.ogg`
- `sounds/hive/detail_scuttle_01.ogg`
- `sounds/hive/hive_spawn_alert_01.ogg`
- `sounds/hive/hive_spawn_alert_02.ogg`
- `sounds/hive/hive_spawn_alert_03.ogg`
- `sounds/hive/hive_spawn_alert_04.ogg`
- `sounds/hive/hive_spawn_attack_01.ogg`
- `sounds/hive/hive_spawn_attack_02.ogg`
- `sounds/hive/hive_spawn_attack_03.ogg`
- `sounds/hive/hive_spawn_attack_04.ogg`
- `sounds/hive/hive_spawn_death_01.ogg`
- `sounds/hive/hive_spawn_death_02.ogg`
- `sounds/hive/hive_spawn_death_03.ogg`
- `sounds/hive/hive_spawn_death_04.ogg`
- `sounds/hive/hive_spawn_hurt_01.ogg`
- `sounds/hive/hive_spawn_hurt_02.ogg`
- `sounds/hive/hive_spawn_hurt_03.ogg`
- `sounds/hive/hive_spawn_hurt_04.ogg`
- `sounds/hive/hive_spawn_idle_01.ogg`
- `sounds/hive/hive_spawn_idle_02.ogg`
- `sounds/hive/hive_spawn_idle_03.ogg`
- `sounds/hive/hive_spawn_idle_04.ogg`
- `sounds/hive/hive_spread_01_creep.ogg`
- `sounds/hive/hive_spread_02_pulse.ogg`
- `sounds/hive/hive_spread_03_swell.ogg`

## Физические OGG-файлы, оставшиеся на диске

- `sounds/block/creeper_rupture.ogg`
- `sounds/block/digestor_churn.ogg`
- `sounds/block/heart_pulse.ogg`
- `sounds/block/heartbeat_loop.ogg`
- `sounds/block/hive_alarm.ogg`
- `sounds/block/hive_eye_screech.ogg`
- `sounds/block/hive_heartbeat.ogg`
- `sounds/block/nervous_twitch.ogg`
- `sounds/block/pustule_burst.ogg`
- `sounds/block/synapse_rupture.ogg`
- `sounds/entity/acid_splash.ogg`
- `sounds/entity/amalgam_roar.ogg`
- `sounds/entity/amalgam_smash.ogg`
- `sounds/entity/amalgamation_fuse.ogg`
- `sounds/entity/flamethrower_fire.ogg`
- `sounds/entity/flesh_amalgam_ambient.ogg`
- `sounds/entity/flesh_amalgam_death.ogg`
- `sounds/entity/flesh_amalgam_hurt.ogg`
- `sounds/hallucination/phantom_creeper.ogg`
- `sounds/hallucination/phantom_whisper.ogg`
- `sounds/item/dart_hit.ogg`
- `sounds/item/inoculator_fire.ogg`
- `sounds/item/purifier_ignite.ogg`
- `sounds/item/purifier_loop.ogg`

## Лишние физические файлы

- `sounds/block/heartbeat_loop.ogg`
