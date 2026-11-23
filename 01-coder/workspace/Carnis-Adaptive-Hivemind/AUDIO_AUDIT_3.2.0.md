# Carnis 3.2.0 — аудит Wave 11 и зональных амбиентов

## Изменения и проверка

- `mod_version=3.2.0`.
- Сохранены все 51 прежнее событие, добавлены 4 `ambient.hive.*` события; итого 55 регистраций и 55 записей в `sounds.json`.
- В обеих локалях 55 ключей субтитров; все subtitle-ссылки событий имеют перевод, мёртвых ключей нет.
- Существующие `hive_ambient`, `hive_ambient_close`, heartbeat, pulse и stinger события не удалялись.
- Wave 11 файлы `hive/amb_surface.ogg`, `amb_deep.ogg`, `amb_core.ogg`, `amb_threshold.ogg` не обнаружены в проекте или workspace. Зональные события ссылаются на ожидаемые пути; код выбирает старый `hive_ambient` как fallback, если выбранный зональный ресурс отсутствует.
- Плотность считается по блокам улья в сфере радиуса 16; ветви выбора реализуют пороги >32, >8 с Y<40, >8 и иначе.
- `HIVE_AMBIENT_CLOSE` сохранён отдельным слоем при `insideStructure`; pulse, stinger и heartbeat-таймеры сохранены.
- Wave 12 transition-stingers не подключались: это опционально и файлы Wave 12 не найдены.
- Самопроверка JSON, путей и ключей прошла. Сборка не запускалась: отсутствуют `./gradlew` и установленная команда `gradle`.

## Самопроверка

- События в `ModSounds`: 55
- События в `sounds.json`: 55
- Уникальных путей: 97
- Существуют `.ogg`: 23
- Отсутствуют `.ogg`: 74
- Физические OGG-файлы: 24
- Неиспользуемые физические OGG-файлы: 1
- Новые зональные OGG из 4: 0 найдены из 4.

### Отсутствующие пути

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
- `sounds/hive/amb_core.ogg`
- `sounds/hive/amb_deep.ogg`
- `sounds/hive/amb_surface.ogg`
- `sounds/hive/amb_threshold.ogg`
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

### Физические OGG без ссылки из sounds.json

- `sounds/block/nervous_twitch.ogg`
