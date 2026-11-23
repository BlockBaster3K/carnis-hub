# 97-path sound silence ledger

Final JSON unique paths: 97. Work-baseline JSON unique paths: 86. Post-R11 physical OGG count: 22.

The row-level baseline is the preserved `sounds-3.4.8-baseline.json`; the final column is `sounds-3.4.9-final.json`. The common-dump aggregate is separately recorded in D4; the reviewer-cited 20197-byte common dump is not present in this workspace, so its other path/event rows are not fabricated. The nine-event R7 reference comparison uses the event/path descriptions provided by the reviewer and labels the local dump separately.

| Path | On disk after R11? | Events in work baseline | Events in 3.4.9 final | Final path status | System of reference |
|---|---|---|---|---|---|
| `sounds/amb/hive_ambient_01.ogg` | No | `hive.ambient` | `hive.ambient` | silent (file absent) | Work baseline → final |
| `sounds/amb/hive_ambient_02.ogg` | No | `hive.ambient` | `hive.ambient` | silent (file absent) | Work baseline → final |
| `sounds/amb/hive_ambient_03.ogg` | No | `hive.ambient` | `hive.ambient` | silent (file absent) | Work baseline → final |
| `sounds/amb/hive_ambient_close_01.ogg` | No | `hive.ambient_close` | `hive.ambient_close` | silent (file absent) | Work baseline → final |
| `sounds/amb/hive_ambient_close_02.ogg` | No | `hive.ambient_close` | `hive.ambient_close` | silent (file absent) | Work baseline → final |
| `sounds/amb/hive_ambient_tonal_stinger.ogg` | No | `hive.ambient_tonal_stinger` | `hive.ambient_tonal_stinger` | silent (file absent) | Work baseline → final |
| `sounds/amb/hive_pulse_01.ogg` | No | `hive.pulse` | `hive.pulse` | silent (file absent) | Work baseline → final |
| `sounds/amb/hive_pulse_02.ogg` | No | `hive.pulse` | `hive.pulse` | silent (file absent) | Work baseline → final |
| `sounds/amb/hive_pulse_03.ogg` | No | `hive.pulse` | `hive.pulse` | silent (file absent) | Work baseline → final |
| `sounds/block/bone_deflect.ogg` | No | `bone_deflect` | `bone_deflect` | silent (file absent) | Work baseline → final |
| `sounds/block/creeper_rupture.ogg` | Yes | `creeper_rupture`; `hive.spawn_creeper_detonate`; `hive.amalgam_shuffle`; `hive.amalgam_slam`; `hive.spawn_attack`; `hive.spawn_death`; `hive.spawn_skeleton_blade`; `hive.spawn_skeleton_blade` | `creeper_rupture`; `hive.spawn_creeper_detonate`; `hive.spawn_death` | heard (file present) | Work baseline → final |
| `sounds/block/digestor_churn.ogg` | Yes | `digestor_churn`; `hive.spawn_idle`; `hive.spawn_skeleton_bonecrack` | `digestor_churn`; `hive.spawn_idle`; `hive.spawn_skeleton_bonecrack` | heard (file present) | Work baseline → final |
| `sounds/block/heart_pulse.ogg` | Yes | `pulsing_heart_beat` | `pulsing_heart_beat` | heard (file present) | Work baseline → final |
| `sounds/block/heartbeat_loop.ogg` | Yes | `heartbeat_loop`; `hive.spawn_alert`; `hive.spawn_idle` | `heartbeat_loop`; `hive.spawn_alert`; `hive.spawn_idle` | heard (file present) | Work baseline → final |
| `sounds/block/hive_alarm.ogg` | Yes | `hive.spawn_alert`; `hive.alarm` | `hive.spawn_alert`; `hive.alarm` | heard (file present) | Work baseline → final |
| `sounds/block/hive_block_break_01_tear.ogg` | No | `hive.block_break` | `hive.block_break` | silent (file absent) | Work baseline → final |
| `sounds/block/hive_block_break_02_pop.ogg` | No | `hive.block_break` | `hive.block_break` | silent (file absent) | Work baseline → final |
| `sounds/block/hive_block_break_03_crunch.ogg` | No | `hive.block_break` | `hive.block_break` | silent (file absent) | Work baseline → final |
| `sounds/block/hive_block_place_01_soft.ogg` | No | `hive.block_place` | `hive.block_place` | silent (file absent) | Work baseline → final |
| `sounds/block/hive_block_place_02_dense.ogg` | No | `hive.block_place` | `hive.block_place` | silent (file absent) | Work baseline → final |
| `sounds/block/hive_block_place_03_wet.ogg` | No | `hive.block_place` | `hive.block_place` | silent (file absent) | Work baseline → final |
| `sounds/block/hive_eye_screech.ogg` | Yes | `hive.spawn_alert`; `hive.eye_screech` | `hive.spawn_alert`; `hive.eye_screech` | heard (file present) | Work baseline → final |
| `sounds/block/hive_heartbeat.ogg` | Yes | `hive.heartbeat` | `hive.heartbeat` | heard (file present) | Work baseline → final |
| `sounds/block/nervous_twitch.ogg` | Yes | `synapse_shock`; `hive.spawn_creeper_crawl`; `hive.spawn_hurt`; `hive.spawn_skeleton_whip`; `hive.spawn_skeleton_bonecrack` | `synapse_shock`; `hive.spawn_creeper_crawl`; `hive.spawn_hurt`; `hive.spawn_skeleton_whip`; `hive.spawn_skeleton_bonecrack` | heard (file present) | Work baseline → final |
| `sounds/block/pustule_burst.ogg` | Yes | `pustule_burst`; `hive.spawn_creeper_sac`; `hive.spawn_hurt_critical`; `hive.spawn_skeleton_bonecrack` | `pustule_burst`; `hive.spawn_creeper_sac`; `hive.spawn_hurt_critical`; `hive.spawn_skeleton_bonecrack` | heard (file present) | Work baseline → final |
| `sounds/block/synapse_rupture.ogg` | Yes | `synapse_rupture`; `hive.spawn_attack`; `hive.spawn_hurt_critical`; `hive.spawn_death`; `hive.spawn_skeleton_blade` | `synapse_rupture`; `hive.spawn_hurt_critical`; `hive.spawn_death` | heard (file present) | Work baseline → final |
| `sounds/combat/combat_deflect_01_chitin.ogg` | No | `combat.armor_deflect` | `combat.armor_deflect` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_deflect_02_bone.ogg` | No | `combat.armor_deflect` | `combat.armor_deflect` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_deflect_03_metal.ogg` | No | `combat.armor_deflect` | `combat.armor_deflect` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_deflect_04_glance.ogg` | No | `combat.armor_deflect` | `combat.armor_deflect` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_deflect_05_parry.ogg` | No | `combat.armor_deflect` | `combat.armor_deflect` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_flesh_hit_01.ogg` | No | `combat.flesh_hit` | `combat.flesh_hit` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_flesh_hit_02.ogg` | No | `combat.flesh_hit` | `combat.flesh_hit` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_flesh_hit_03.ogg` | No | `combat.flesh_hit` | `combat.flesh_hit` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_flesh_hit_deep_01_axe.ogg` | No | `combat.flesh_hit_deep` | `combat.flesh_hit_deep` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_flesh_hit_deep_02_crit.ogg` | No | `combat.flesh_hit_deep` | `combat.flesh_hit_deep` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_flesh_hit_deep_03_blast.ogg` | No | `combat.flesh_hit_deep` | `combat.flesh_hit_deep` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_stab_01_bone.ogg` | No | `combat.block_stab` | `combat.block_stab` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_stab_02_chitin.ogg` | No | `combat.block_stab` | `combat.block_stab` | silent (file absent) | Work baseline → final |
| `sounds/combat/combat_stab_03_shield.ogg` | No | `combat.block_stab` | `combat.block_stab` | silent (file absent) | Work baseline → final |
| `sounds/combat/dismember_01.ogg` | No | `combat.dismember` | `combat.dismember` | silent (file absent) | Work baseline → final |
| `sounds/combat/dismember_02.ogg` | No | `combat.dismember` | `combat.dismember` | silent (file absent) | Work baseline → final |
| `sounds/combat/dismember_03.ogg` | No | `combat.dismember` | `combat.dismember` | silent (file absent) | Work baseline → final |
| `sounds/combat/dismember_04.ogg` | No | `combat.dismember` | `combat.dismember` | silent (file absent) | Work baseline → final |
| `sounds/combat/dismember_05.ogg` | No | `combat.dismember` | `combat.dismember` | silent (file absent) | Work baseline → final |
| `sounds/entity/acid_splash.ogg` | Yes | `acid_splash`; `hive.spawn_attack`; `hive.spawn_hurt` | `acid_splash`; `hive.spawn_hurt` | heard (file present) | Work baseline → final |
| `sounds/entity/amalgamation_fuse.ogg` | Yes | `amalgamation_fuse`; `hive.spawn_skeleton_whip` | `amalgamation_fuse`; `hive.spawn_skeleton_whip` | heard (file present) | Work baseline → final |
| `sounds/entity/flamethrower_fire.ogg` | Yes | `flamethrower_fire`; `hive.spawn_skeleton_whip` | `flamethrower_fire`; `hive.spawn_skeleton_whip` | heard (file present) | Work baseline → final |
| `sounds/entity/flesh_amalgam_ambient.ogg` | Yes | `flesh_amalgam_ambient`; `hive.amalgam_breath`; `hive.spawn_idle` | `flesh_amalgam_ambient`; `hive.amalgam_breath`; `hive.spawn_idle` | heard (file present) | Work baseline → final |
| `sounds/entity/flesh_amalgam_death.ogg` | Yes | `hive.spawn_death` | `hive.spawn_death` | heard (file present) | Work baseline → final |
| `sounds/entity/flesh_amalgam_death_01.ogg` | No | `flesh_amalgam_death` | `flesh_amalgam_death` | silent (file absent) | Work baseline → final |
| `sounds/entity/flesh_amalgam_hurt.ogg` | Yes | `hive.spawn_hurt`; `hive.spawn_hurt_critical` | `hive.spawn_hurt`; `hive.spawn_hurt_critical` | heard (file present) | Work baseline → final |
| `sounds/entity/flesh_amalgam_hurt_01.ogg` | No | `flesh_amalgam_hurt` | `flesh_amalgam_hurt` | silent (file absent) | Work baseline → final |
| `sounds/entity/flesh_amalgam_roar_01.ogg` | No | `amalgam_roar` | `amalgam_roar` | silent (file absent) | Work baseline → final |
| `sounds/entity/flesh_amalgam_roar_02.ogg` | No | `amalgam_roar` | `amalgam_roar` | silent (file absent) | Work baseline → final |
| `sounds/entity/flesh_amalgam_smash_01.ogg` | No | `amalgam_smash` | `amalgam_smash` | silent (file absent) | Work baseline → final |
| `sounds/entity/flesh_amalgam_smash_02.ogg` | No | `amalgam_smash` | `amalgam_smash` | silent (file absent) | Work baseline → final |
| `sounds/entity/flesh_amalgam_step_01.ogg` | No | `amalgam_step` | `amalgam_step` | silent (file absent) | Work baseline → final |
| `sounds/entity/flesh_amalgam_step_02.ogg` | No | `amalgam_step` | `amalgam_step` | silent (file absent) | Work baseline → final |
| `sounds/entity/organic_creak.ogg` | No | `organic_creak` | `organic_creak` | silent (file absent) | Work baseline → final |
| `sounds/flesh/flesh_block_step_01.ogg` | No | `flesh_block_step` | `flesh_block_step` | silent (file absent) | Work baseline → final |
| `sounds/flesh/flesh_block_step_02.ogg` | No | `flesh_block_step` | `flesh_block_step` | silent (file absent) | Work baseline → final |
| `sounds/flesh/flesh_block_step_03.ogg` | No | `flesh_block_step` | `flesh_block_step` | silent (file absent) | Work baseline → final |
| `sounds/hallucination/phantom_creeper.ogg` | Yes | `phantom_creeper` | `phantom_creeper` | heard (file present) | Work baseline → final |
| `sounds/hallucination/phantom_footsteps.ogg` | No | `phantom_footsteps` | `phantom_footsteps` | silent (file absent) | Work baseline → final |
| `sounds/hallucination/phantom_whisper.ogg` | Yes | `phantom_whisper` | `phantom_whisper` | heard (file present) | Work baseline → final |
| `sounds/hive/amalgam_shuffle_01.ogg` | No | — | `hive.amalgam_shuffle` | silent (file absent) | Work baseline → final |
| `sounds/hive/amalgam_shuffle_02.ogg` | No | — | `hive.amalgam_shuffle` | silent (file absent) | Work baseline → final |
| `sounds/hive/amalgam_slam_01.ogg` | No | — | `hive.amalgam_slam` | silent (file absent) | Work baseline → final |
| `sounds/hive/amalgam_slam_02.ogg` | No | — | `hive.amalgam_slam` | silent (file absent) | Work baseline → final |
| `sounds/hive/amb_core.ogg` | No | `hive.ambient_core` | `hive.ambient_core` | silent (file absent) | Work baseline → final |
| `sounds/hive/amb_deep.ogg` | No | `hive.ambient_deep` | `hive.ambient_deep` | silent (file absent) | Work baseline → final |
| `sounds/hive/amb_surface.ogg` | No | `hive.ambient_surface` | `hive.ambient_surface` | silent (file absent) | Work baseline → final |
| `sounds/hive/amb_threshold.ogg` | No | `hive.ambient_threshold` | `hive.ambient_threshold` | silent (file absent) | Work baseline → final |
| `sounds/hive/detail_bubbles_01.ogg` | No | `hive.detail_bubbles` | `hive.detail_bubbles` | silent (file absent) | Work baseline → final |
| `sounds/hive/detail_creak_01.ogg` | No | `hive.detail_creak` | `hive.detail_creak` | silent (file absent) | Work baseline → final |
| `sounds/hive/detail_flow_01.ogg` | No | `hive.detail_flow` | `hive.detail_flow` | silent (file absent) | Work baseline → final |
| `sounds/hive/detail_flow_02.ogg` | No | `hive.detail_flow` | `hive.detail_flow` | silent (file absent) | Work baseline → final |
| `sounds/hive/detail_membrane_01.ogg` | No | `hive.detail_membrane` | `hive.detail_membrane` | silent (file absent) | Work baseline → final |
| `sounds/hive/detail_scuttle_01.ogg` | No | `hive.detail_scuttle` | `hive.detail_scuttle` | silent (file absent) | Work baseline → final |
| `sounds/hive/hive_spawn_attack_01.ogg` | No | — | `hive.spawn_attack` | silent (file absent) | Work baseline → final |
| `sounds/hive/hive_spawn_attack_02.ogg` | No | — | `hive.spawn_attack` | silent (file absent) | Work baseline → final |
| `sounds/hive/hive_spawn_attack_03.ogg` | No | — | `hive.spawn_attack` | silent (file absent) | Work baseline → final |
| `sounds/hive/hive_spawn_attack_04.ogg` | No | — | `hive.spawn_attack` | silent (file absent) | Work baseline → final |
| `sounds/hive/hive_spread_01_creep.ogg` | No | `hive.spread` | `hive.spread` | silent (file absent) | Work baseline → final |
| `sounds/hive/hive_spread_02_pulse.ogg` | No | `hive.spread` | `hive.spread` | silent (file absent) | Work baseline → final |
| `sounds/hive/hive_spread_03_swell.ogg` | No | `hive.spread` | `hive.spread` | silent (file absent) | Work baseline → final |
| `sounds/hive/spawn_skeleton_blade_01.ogg` | No | — | `hive.spawn_skeleton_blade` | silent (file absent) | Work baseline → final |
| `sounds/hive/spawn_skeleton_blade_02.ogg` | No | — | `hive.spawn_skeleton_blade` | silent (file absent) | Work baseline → final |
| `sounds/hive/spawn_skeleton_blade_03.ogg` | No | — | `hive.spawn_skeleton_blade` | silent (file absent) | Work baseline → final |
| `sounds/hive/zone_stinger_deep.ogg` | No | `hive.zone_stinger_deep` | `hive.zone_stinger_deep` | silent (file absent) | Work baseline → final |
| `sounds/hive/zone_stinger_intensify.ogg` | No | `hive.zone_stinger_intensify` | `hive.zone_stinger_intensify` | silent (file absent) | Work baseline → final |
| `sounds/hive/zone_stinger_release.ogg` | No | `hive.zone_stinger_release` | `hive.zone_stinger_release` | silent (file absent) | Work baseline → final |
| `sounds/item/dart_hit.ogg` | Yes | `entity.dart.hit` | `entity.dart.hit` | heard (file present) | Work baseline → final |
| `sounds/item/inoculator_fire.ogg` | Yes | `item.inoculator.fire` | `item.inoculator.fire` | heard (file present) | Work baseline → final |
| `sounds/item/purifier_ignite.ogg` | Yes | `item.purifier.ignite` | `item.purifier.ignite` | heard (file present) | Work baseline → final |
| `sounds/item/purifier_loop.ogg` | Yes | `item.purifier.loop` | `item.purifier.loop` | heard (file present) | Work baseline → final |
