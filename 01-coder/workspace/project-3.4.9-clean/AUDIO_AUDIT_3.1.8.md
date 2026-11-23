# Carnis 3.1.8 — самопроверка аудио и combat

## Версия и сборка

- `gradle.properties`: `mod_version=3.1.8`.
- Сборка была запрошена, но не запущена: нет исполняемого `./gradlew` и команды `gradle`. Не заявляется успешная компиляция.

## Самопроверка

- События в `ModSounds`: 51
- События в `sounds.json`: 51
- Уникальных путей: 93
- Существуют `.ogg`: 23
- Отсутствуют `.ogg`: 70
- Subtitle EN: 51
- Subtitle RU: 51
- Мёртвые subtitle-ключи: 0; ключи обеих локалей точно совпадают с набором событий.
- Pitch-рандомизация: в `CarnisCombatSounds` не найдена; все вызовы передают `pitch=1.0F`, вариативный pitch только в JSON.
- События `COMBAT_ARMOR_DEFLECT` и `COMBAT_BLOCK_STAB` вызываются при заданных проверках; `HIVE_HEARTBEAT` и `HEARTBEAT_LOOP` задействованы в core zone.
- `hive_pulse`: `stream=false`.
- `synapse_shock` → `block/synapse_rupture.ogg` (существует).
- `phantom_footsteps` → `hallucination/phantom_footsteps.ogg` (сейчас отсутствует).
- `heartbeat_loop` → `block/heartbeat_loop.ogg` (существует).
- Лишние физические OGG: 1.

## Отсутствующие ресурсы

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
- `sounds/entity/organic_creak.ogg`
- `sounds/flesh/flesh_block_step_01.ogg`
- `sounds/flesh/flesh_block_step_02.ogg`
- `sounds/flesh/flesh_block_step_03.ogg`
- `sounds/hallucination/phantom_footsteps.ogg`
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

## Файлы, которые физически присутствуют, но не используются

- `sounds/block/nervous_twitch.ogg`
