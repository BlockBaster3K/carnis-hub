# Carnis 3.1.6 — audio-bank audit and self-check

## Status

**The 66 requested Wave 1–10 OGG resources were not found anywhere under `/home/user`; Wave audio integration is therefore incomplete.** The catalogue and locale files were made safe: no absent OGG path remains referenced. Wave events without available assets were omitted rather than represented as working. No successful build is claimed.

## Audio audit

- Removed obsolete/duplicate resources: 6 OGG files (the five earlier removals plus `hallucination/phantom_footsteps.ogg`).
- Remaining physical OGG files: 24.
- Remaining audio events in `sounds.json`: 23.
- 66 expected Wave resources currently absent; exact filenames are listed below.
- Unreferenced physical OGG files: 0.

### Removed files

- `block/hive_ambient_drone.ogg`
- `block/synapse_fire.ogg`
- `entity/bone_deflect.ogg`
- `entity/amalgam_step.ogg`
- `entity/organic_creak.ogg`
- `hallucination/phantom_footsteps.ogg`

### Remaining OGG files

- `block/creeper_rupture.ogg`
- `block/digestor_churn.ogg`
- `block/heart_pulse.ogg`
- `block/heartbeat_loop.ogg`
- `block/hive_alarm.ogg`
- `block/hive_eye_screech.ogg`
- `block/hive_heartbeat.ogg`
- `block/nervous_twitch.ogg`
- `block/pustule_burst.ogg`
- `block/synapse_rupture.ogg`
- `entity/acid_splash.ogg`
- `entity/amalgam_roar.ogg`
- `entity/amalgam_smash.ogg`
- `entity/amalgamation_fuse.ogg`
- `entity/flamethrower_fire.ogg`
- `entity/flesh_amalgam_ambient.ogg`
- `entity/flesh_amalgam_death.ogg`
- `entity/flesh_amalgam_hurt.ogg`
- `hallucination/phantom_creeper.ogg`
- `hallucination/phantom_whisper.ogg`
- `item/dart_hit.ogg`
- `item/inoculator_fire.ogg`
- `item/purifier_ignite.ogg`
- `item/purifier_loop.ogg`

### Expected Wave 1–10 files not present

- `amb/hive_ambient_01.ogg`
- `amb/hive_ambient_02.ogg`
- `amb/hive_ambient_03.ogg`
- `amb/hive_ambient_close_01.ogg`
- `amb/hive_ambient_close_02.ogg`
- `amb/hive_ambient_tonal_stinger.ogg`
- `amb/hive_pulse_01.ogg`
- `amb/hive_pulse_02.ogg`
- `amb/hive_pulse_03.ogg`
- `block/hive_block_break_01_tear.ogg`
- `block/hive_block_break_02_pop.ogg`
- `block/hive_block_break_03_crunch.ogg`
- `block/hive_block_place_01_soft.ogg`
- `block/hive_block_place_02_dense.ogg`
- `block/hive_block_place_03_wet.ogg`
- `combat/combat_deflect_01_chitin.ogg`
- `combat/combat_deflect_02_bone.ogg`
- `combat/combat_deflect_03_metal.ogg`
- `combat/combat_deflect_04_glance.ogg`
- `combat/combat_deflect_05_parry.ogg`
- `combat/combat_dismember_01_ribs.ogg`
- `combat/combat_dismember_02_pustule.ogg`
- `combat/combat_dismember_03_sinew.ogg`
- `combat/combat_dismember_04_plate.ogg`
- `combat/combat_dismember_05_limb.ogg`
- `combat/combat_flesh_hit_01.ogg`
- `combat/combat_flesh_hit_02.ogg`
- `combat/combat_flesh_hit_03.ogg`
- `combat/combat_flesh_hit_deep_01_axe.ogg`
- `combat/combat_flesh_hit_deep_02_crit.ogg`
- `combat/combat_flesh_hit_deep_03_blast.ogg`
- `combat/combat_stab_01_bone.ogg`
- `combat/combat_stab_02_chitin.ogg`
- `combat/combat_stab_03_shield.ogg`
- `flesh/flesh_block_step_01.ogg`
- `flesh/flesh_block_step_02.ogg`
- `flesh/flesh_block_step_03.ogg`
- `hive/detail_bubbles_01.ogg`
- `hive/detail_creak_01.ogg`
- `hive/detail_flow_01.ogg`
- `hive/detail_flow_02.ogg`
- `hive/detail_membrane_01.ogg`
- `hive/detail_scuttle_01.ogg`
- `hive/hive_spawn_alert_01.ogg`
- `hive/hive_spawn_alert_02.ogg`
- `hive/hive_spawn_alert_03.ogg`
- `hive/hive_spawn_alert_04.ogg`
- `hive/hive_spawn_attack_01.ogg`
- `hive/hive_spawn_attack_02.ogg`
- `hive/hive_spawn_attack_03.ogg`
- `hive/hive_spawn_attack_04.ogg`
- `hive/hive_spawn_death_01.ogg`
- `hive/hive_spawn_death_02.ogg`
- `hive/hive_spawn_death_03.ogg`
- `hive/hive_spawn_death_04.ogg`
- `hive/hive_spawn_hurt_01.ogg`
- `hive/hive_spawn_hurt_02.ogg`
- `hive/hive_spawn_hurt_03.ogg`
- `hive/hive_spawn_hurt_04.ogg`
- `hive/hive_spawn_idle_01.ogg`
- `hive/hive_spawn_idle_02.ogg`
- `hive/hive_spawn_idle_03.ogg`
- `hive/hive_spawn_idle_04.ogg`
- `hive/hive_spread_01_creep.ogg`
- `hive/hive_spread_02_pulse.ogg`
- `hive/hive_spread_03_swell.ogg`

## Self-check

- `sounds.json` events: 23
- Unique Carnis sound paths referenced: 24
- Existing referenced paths: 24
- Missing referenced paths: 0
- Unreferenced physical OGG files: 0
- `en_us.json` subtitle keys: 23
- `ru_ru.json` subtitle keys: 23
- Every event has a `carnis.subtitle.*` key; both locale key sets match the event set.
- Wave-specific streaming/pitch rules cannot be verified as applied because those Wave files are missing and their events were omitted.
- Gradle version: `3.1.6`; `mod_group_id` absent; `mods.toml` uses `${mod_version}`.
- JSON syntax and these file/path/key invariants were checked with Python. Gradle build not run.

## Currently defined sound events

- `acid_splash`
- `amalgam_roar`
- `amalgam_smash`
- `amalgamation_fuse`
- `creeper_rupture`
- `digestor_churn`
- `entity.dart.hit`
- `flamethrower_fire`
- `flesh_amalgam_ambient`
- `flesh_amalgam_death`
- `flesh_amalgam_hurt`
- `heartbeat_loop`
- `hive_alarm`
- `hive_eye_screech`
- `item.inoculator.fire`
- `item.purifier.ignite`
- `item.purifier.loop`
- `phantom_creeper`
- `phantom_whisper`
- `pulsing_heart_beat`
- `pustule_burst`
- `synapse_rupture`
- `synapse_shock`
