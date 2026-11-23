# Carnis 3.4.8 — implementation and audit report

> Status: requested changes are implemented. The checks below are static workspace audits. No Gradle build or in-game integration test was run: this checkout has no `gradlew`, system `gradle`, or `.git` metadata.

## A. Amalgam / flesh-amalgam canonical path status

The canonical `flesh_amalgam_*` declarations are retained regardless of which OGGs happen to be present in this checkout. No declared path was redirected to an older file because of local absence. The old `entity/amalgam_roar.ogg` and `entity/amalgam_smash.ogg` remain on disk but are unreferenced by `sounds.json`; no `entity/amalgam_step.ogg` exists.

| Path | Present in actual tree? | Size | Declared use / note |
|---|---|---:|---|
| `entity/amalgam_smash.ogg` | Yes | 6117 B | unreferenced legacy file; retained, not declared |
| `entity/amalgam_roar.ogg` | Yes | 25848 B | unreferenced legacy file; retained, not declared |
| `entity/amalgam_step.ogg` | No | — | legacy candidate does not exist and is not declared |
| `entity/amalgam_hurt.ogg` | No | — | none |
| `entity/amalgam_death.ogg` | No | — | none |
| `entity/flesh_amalgam_smash_01.ogg` | No | — | `amalgam_smash` |
| `entity/flesh_amalgam_smash_02.ogg` | No | — | `amalgam_smash` |
| `entity/flesh_amalgam_roar_01.ogg` | No | — | `amalgam_roar` |
| `entity/flesh_amalgam_roar_02.ogg` | No | — | `amalgam_roar` |
| `entity/flesh_amalgam_step_01.ogg` | No | — | `amalgam_step` |
| `entity/flesh_amalgam_step_02.ogg` | No | — | `amalgam_step` |
| `entity/flesh_amalgam_hurt.ogg` | Yes | 10050 B | used by generic Hive hurt events; Flesh Amalgam hurt event uses `_01` |
| `entity/flesh_amalgam_hurt_01.ogg` | No | — | `flesh_amalgam_hurt` |
| `entity/flesh_amalgam_death.ogg` | Yes | 25848 B | used by generic Hive death event; Flesh Amalgam death event uses `_01` |
| `entity/flesh_amalgam_death_01.ogg` | No | — | `flesh_amalgam_death` |
| `entity/flesh_amalgam_ambient.ogg` | Yes | 22955 B | `flesh_amalgam_ambient`, `hive.amalgam_breath`, `hive.spawn_idle` |

Canonical sound declarations remain: `entity/flesh_amalgam_smash_01..02`, `entity/flesh_amalgam_roar_01..02`, `entity/flesh_amalgam_step_01..02`, `entity/flesh_amalgam_hurt_01`, and `entity/flesh_amalgam_death_01`. The canonical `_01` hurt/death files are not present locally; the older unnumbered hurt/death files remain referenced by generic Hive spawn sound events only.

## B. `validTarget`: before → after

- **Before:** `HiveSwarmCoordinator.validTarget` rejected assimilated players and players wearing a full Neuro Armor set unless provoked. `InfectedCreeperEntity.canAttack` separately accepted any living Player; `setTarget` had another local check; and `NearestLivePlayerTargetGoal` used a third condition set. The sets were inconsistent and could leave the goal occupying priority 1 without setting a usable target.
- **After:** one `HiveSwarmCoordinator.validTarget(Mob, LivingEntity)` is used by `canAttack`, `setTarget`, and the live-player goal's candidate/continuation checks. For a Player it requires the same level, alive, not spectator, and not creative. **Removed from `validTarget`: `PlayerInfectionApi.isAssimilated(player)` and `NeuroArmorEventHandler.hasFullSet(player) && !isProvoked(player)` exclusions.** Infection, assimilation, and neural armor do not make a living player an ally. For non-player entities the existing Hive/allied filter and normal attack-eligibility check remain; the Creeper path avoids recursion through the overridden `canAttack`.
- Prey targeting remains separate from Player targeting: `CarnisHuntPreyGoal` has a maximum range of 16 blocks and requires line of sight. The replacement `PlayerOnlySwellGoal` ensures prey pursuit does not start the fuse.

## C. Fuse lead and control value

`getSwelling(1.0F)` is normalized by `maxSwell − 2 = 28`. The corrected formula is `elapsedFuseTicks = round(getSwelling(1.0F) × 28)`, then `fuse = max(0, 28 − elapsedFuseTicks)`. At `fuse == 5`, `elapsedFuseTicks = 23`, so `swelling = 23/28`; five ticks remain, i.e. **5 × 50 ms = 250 ms** until the 28-tick fuse completes. The old multiplier 30 against the 28-tick denominator produced about 7 ticks / 350 ms. The arithmetic was statically checked; the in-game tick timing was not run.

## D. Volume audit: JSON × Java

All literal runtime volumes on direct Java `ModSounds` playback calls have been set to `1.0F`, and direct-call pitch is `1.0F`. Variant volume, pitch, and weight remain in `sounds.json`. The effective per-sample volume is JSON × Java. An omitted JSON volume means 1.0.

| Java callsite | event ID | JSON volume by variant | Java volume | result |
|---|---|---:|---:|---:|
| `src/main/java/com/carnis/mod/block/NervePillarBlock.java:81` | `synapse_rupture` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/block/PustuleClusterBlock.java:113` | `pustule_burst` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/block/SporeSproutBlock.java:103` | `organic_creak` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/block/StomachPoolBlock.java:116` | `acid_splash` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/block/entity/FleshBulbBlockEntity.java:37` | `acid_splash` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/block/entity/FleshBulbBlockEntity.java:55` | `pulsing_heart_beat` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java:362` | `hive.alarm` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java:474` | `amalgam_roar` | `1/1` | `1.0` | `1/1` |
| `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java:734` | `hive.eye_screech` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/block/entity/HiveEyeBlockEntity.java:754` | `hive.alarm` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/block/entity/PulsingHeartBlockEntity.java:171` | `pulsing_heart_beat` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/block/entity/PulsingHeartBlockEntity.java:198` | `amalgam_roar` | `1/1` | `1.0` | `1/1` |
| `src/main/java/com/carnis/mod/client/HeartAmbientTicker.java:23` | `heartbeat_loop` | `1` | `dynamic client scale (documented below)` | `JSON × configured/proximity scale` |
| `src/main/java/com/carnis/mod/client/PlayerHallucinationHandler.java:87` | `phantom_whisper` | `1` | `dynamic client scale (documented below)` | `JSON × configured/proximity scale` |
| `src/main/java/com/carnis/mod/entity/AmalgamBileProjectile.java:47` | `acid_splash` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:62` | `amalgam_step` | `0.9/0.9` | `1.0` | `0.9/0.9` |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:65` | `hive.amalgam_shuffle` | `0.35` | `1.0` | `0.35` |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:496` | `bone_deflect` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:551` | `acid_splash` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/entity/HiveEntity.java:49` | `hive.spawn_hurt_critical` | `0.8/0.8/0.8` | `1.0` | `0.8/0.8/0.8` |
| `src/main/java/com/carnis/mod/entity/HiveSentinelEntity.java:46` | `phantom_whisper` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java:227` | `hive.spawn_creeper_sac` | `0.32` | `1.0` | `0.32` |
| `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java:237` | `hive.spawn_creeper_detonate` | `0.4` | `1.0` | `0.4` |
| `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java:296` | `hive.spawn_creeper_crawl` | `0.3` | `1.0` | `0.3` |
| `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java:129` | `hive.spawn_skeleton_bonecrack` | `0.55/0.55/0.55` | `1.0` | `0.55/0.55/0.55` |
| `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java:162` | `hive.spawn_death` | `0.9/0.9/0.9` | `1.0` | `0.9/0.9/0.9` |
| `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java:265` | `hive.spawn_skeleton_blade` | `0.7/0.7/0.7` | `1.0` | `0.7/0.7/0.7` |
| `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java:296` | `hive.spawn_skeleton_whip` | `0.65/0.65/0.65` | `1.0` | `0.65/0.65/0.65` |
| `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java:307` | `flesh_block_step` | `1/1/1` | `1.0` | `1/1/1` |
| `src/main/java/com/carnis/mod/entity/InfectedZombieEntity.java:129` | `hive.spawn_attack` | `0.7/0.7/0.7` | `1.0` | `0.7/0.7/0.7` |
| `src/main/java/com/carnis/mod/entity/InfectedZombieEntity.java:141` | `hive.spawn_alert` | `0.6/0.6/0.6` | `1.0` | `0.6/0.6/0.6` |
| `src/main/java/com/carnis/mod/entity/ParasiticTendrilEntity.java:64` | `acid_splash` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/entity/ai/AmalgamBiomassFeast.java:74` | `amalgam_roar` | `1/1` | `1.0` | `1/1` |
| `src/main/java/com/carnis/mod/entity/ai/CarnisFeedingGoal.java:118` | `digestor_churn` | `0.9` | `1.0` | `0.9` |
| `src/main/java/com/carnis/mod/entity/ai/CarnisGestationGoal.java:41` | `amalgam_roar` | `1/1` | `1.0` | `1/1` |
| `src/main/java/com/carnis/mod/entity/ai/FleshAmalgamAbilityGoal.java:64` | `hive.amalgam_slam` | `0.55` | `1.0` | `0.55` |
| `src/main/java/com/carnis/mod/entity/ai/FleshAmalgamAbilityGoal.java:92` | `organic_creak` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/entity/ai/FleshAmalgamAbilityGoal.java:111` | `acid_splash` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/entity/ai/HiveSwarmCoordinator.java:198` | `phantom_whisper` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/event/AmalgamationHandler.java:185` | `amalgam_roar` | `1/1` | `1.0` | `1/1` |
| `src/main/java/com/carnis/mod/event/AmalgamationHandler.java:223` | `amalgamation_fuse` | `1.1` | `1.0` | `1.1` |
| `src/main/java/com/carnis/mod/event/DartTreatmentEvents.java:133` | `acid_splash` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/event/InfectionHandler.java:119` | `acid_splash` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/item/BioPurifierItem.java:80` | `item.purifier.ignite` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/item/BioPurifierItem.java:89` | `item.purifier.loop` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/item/PneumaticInoculatorItem.java:112` | `item.inoculator.fire` | `1` | `1.0` | `1` |
| `src/main/java/com/carnis/mod/sound/CarnisCombatSounds.java:49` | `combat.flesh_hit` | `1` | `1.0` | `1.0` |
| `src/main/java/com/carnis/mod/sound/CarnisCombatSounds.java:64` | `combat.flesh_hit_deep` | `1` | `1.0` | `1.0` |
| `src/main/java/com/carnis/mod/sound/CarnisCombatSounds.java:83` | `combat.dismember` | `1` | `1.0` | `1.0` |
| `src/main/java/com/carnis/mod/sound/CarnisCombatSounds.java:109` | `combat.armor_deflect` | `1` | `1.0` | `1.0` |
| `src/main/java/com/carnis/mod/sound/CarnisCombatSounds.java:114` | `combat.block_stab` | `1` | `1.0` | `1.0` |
| `src/main/java/com/carnis/mod/client/PlayerHallucinationHandler.java:66` | `amalgam_roar / heartbeat_loop / phantom_footsteps` | `1` | `configured/infection scale` | `JSON × configured scale` |
| `src/main/java/com/carnis/mod/client/sound/PhantomSoundManager.java:59` | `phantom_creeper / phantom_footsteps / phantom_whisper` | `1` | `packet runtime volume` | `JSON × packet volume` |
| `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java:197-200` | `hive.ambient / hive.ambient_*` | `1` | `ambient targetVolume envelope` | `JSON × ambient envelope` |
| `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java:197-200` (engine sound hook) | `hive.ambient` | `1.0/1.0/1.0` | `1.0 default` | `1/1/1` |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:628` (engine sound hook) | `hive.amalgam_breath` | `0.25` | `1.0 default` | `0.25` |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:633` (engine sound hook) | `flesh_amalgam_hurt` | `1.0` | `1.0 default` | `1` |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:638` (engine sound hook) | `flesh_amalgam_death` | `1.1` | `1.0 default` | `1.1` |
| `src/main/java/com/carnis/mod/entity/HiveEntity.java:32` (engine sound hook) | `hive.spawn_hurt` | `0.65/0.65/0.65` | `1.0 default` | `0.65/0.65/0.65` |
| `src/main/java/com/carnis/mod/entity/HiveEntity.java:37` (engine sound hook) | `hive.spawn_death` | `0.9/0.9/0.9` | `1.0 default` | `0.9/0.9/0.9` |
| `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java:308` (engine sound hook) | `hive.spawn_idle` | `0.35/0.35/0.35` | `1.0 default` | `0.35/0.35/0.35` |
| `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java:313` (engine sound hook) | `hive.spawn_hurt` | `0.65/0.65/0.65` | `1.0 default` | `0.65/0.65/0.65` |
| `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java:318` (engine sound hook) | `hive.spawn_death` | `0.9/0.9/0.9` | `1.0 default` | `0.9/0.9/0.9` |
| `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java:153` (engine sound hook) | `hive.spawn_hurt` | `0.65/0.65/0.65` | `1.0 default` | `0.65/0.65/0.65` |
| `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java:302` (engine sound hook) | `hive.spawn_skeleton_bonecrack` | `0.55/0.55/0.55` | `1.0 default` | `0.55/0.55/0.55` |
| `src/main/java/com/carnis/mod/entity/InfectedZombieEntity.java:122` (engine sound hook) | `hive.spawn_idle` | `0.35/0.35/0.35` | `1.0 default` | `0.35/0.35/0.35` |
| `src/main/java/com/carnis/mod/entity/PurificationDartEntity.java:56` (engine sound hook) | `entity.dart.hit` | `0.8` | `1.0 default` | `0.8` |
| `src/main/java/com/carnis/mod/entity/ViralDartEntity.java:53` (engine sound hook) | `entity.dart.hit` | `0.8` | `1.0 default` | `0.8` |
| `src/main/java/com/carnis/mod/entity/projectile/InoculatorDartEntity.java:109` (engine sound hook) | `entity.dart.hit` | `0.8` | `1.0 default` | `0.8` |
| `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java:173` | `hive.ambient_close` | `1/1` | `targetVolume × 0.6` | `JSON × ambient envelope × 0.6` |
| `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java:197-200` | `hive.ambient_surface / hive.ambient_deep / hive.ambient_core / hive.ambient_threshold` | `1` each | `targetVolume envelope` | `JSON × ambient envelope` |
| `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java:265` | `hive.zone_stinger_intensify / hive.zone_stinger_release / hive.zone_stinger_deep` | `0.65` each | `1.0` | `0.65` each |
| `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java:272` | `hive.pulse` | `1/1/1` | `1.0 default` | `1/1/1` |
| `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java:281` | `hive.ambient_tonal_stinger` | `1` | `1.0 default` | `1` |
| `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java:291-293` | `hive.heartbeat / heartbeat_loop` | `1` each | `1.0 default` | `1` each |

Client-only dynamic scaling is intentionally retained only for hallucination and ambient systems (client config/infection, proximity, ambient envelopes, or packet volume); it is documented in the mediated-call rows above and is not a duplicate fixed attenuation. Direct server/world sound-bank calls and combat helper calls use Java volume/pitch 1.0F. The Amalgam shuffle (previously JSON .35 × Java .35) is now JSON .35 × Java 1.0 = **.35**, removing the −18 dB double attenuation.

## E. Local silence / Sounder-manifest ledger

The previous audit listed 31 fully silent events. The canonical 3.4.8 `_01` Amalgam hurt and death variants add two more events to the local unresolved ledger. The current manifest therefore has **33 fully silent events and 64 unresolved sample references** in this checkout. Do not infer that the Sounder workspace lacks them: OGG files are not transferred into this workspace by design. Class **B** means an exact audio file exists locally under a different path and the declaration should be corrected; **none were found** (no missing basename exists elsewhere in the observed tree). Every absent path is marked **C***: absent here, presumed to arrive by local User/Sounder synchronization, with final A-vs-C classification pending the Sounder manifest. No sound declarations were deleted or redirected based on local absence.

| Event ID | All unresolved sample paths | Count | Class |
|---|---|---:|---|
| `amalgam_smash` | `entity/flesh_amalgam_smash_01.ogg`, `entity/flesh_amalgam_smash_02.ogg` | 2 | C* — local sync / Sounder-manifest confirmation |
| `organic_creak` | `entity/organic_creak.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `amalgam_roar` | `entity/flesh_amalgam_roar_01.ogg`, `entity/flesh_amalgam_roar_02.ogg` | 2 | C* — local sync / Sounder-manifest confirmation |
| `amalgam_step` | `entity/flesh_amalgam_step_01.ogg`, `entity/flesh_amalgam_step_02.ogg` | 2 | C* — local sync / Sounder-manifest confirmation |
| `phantom_footsteps` | `hallucination/phantom_footsteps.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `flesh_block_step` | `flesh/flesh_block_step_01.ogg`, `flesh/flesh_block_step_02.ogg`, `flesh/flesh_block_step_03.ogg` | 3 | C* — local sync / Sounder-manifest confirmation |
| `hive.spread` | `hive/hive_spread_01_creep.ogg`, `hive/hive_spread_02_pulse.ogg`, `hive/hive_spread_03_swell.ogg` | 3 | C* — local sync / Sounder-manifest confirmation |
| `combat.flesh_hit` | `combat/combat_flesh_hit_01.ogg`, `combat/combat_flesh_hit_02.ogg`, `combat/combat_flesh_hit_03.ogg` | 3 | C* — local sync / Sounder-manifest confirmation |
| `combat.flesh_hit_deep` | `combat/combat_flesh_hit_deep_01_axe.ogg`, `combat/combat_flesh_hit_deep_02_crit.ogg`, `combat/combat_flesh_hit_deep_03_blast.ogg` | 3 | C* — local sync / Sounder-manifest confirmation |
| `combat.dismember` | `combat/dismember_01.ogg`, `combat/dismember_02.ogg`, `combat/dismember_03.ogg`, `combat/dismember_04.ogg`, `combat/dismember_05.ogg` | 5 | C* — local sync / Sounder-manifest confirmation |
| `combat.armor_deflect` | `combat/combat_deflect_01_chitin.ogg`, `combat/combat_deflect_02_bone.ogg`, `combat/combat_deflect_03_metal.ogg`, `combat/combat_deflect_04_glance.ogg`, `combat/combat_deflect_05_parry.ogg` | 5 | C* — local sync / Sounder-manifest confirmation |
| `combat.block_stab` | `combat/combat_stab_01_bone.ogg`, `combat/combat_stab_02_chitin.ogg`, `combat/combat_stab_03_shield.ogg` | 3 | C* — local sync / Sounder-manifest confirmation |
| `bone_deflect` | `block/bone_deflect.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `flesh_amalgam_hurt` | `entity/flesh_amalgam_hurt_01.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `flesh_amalgam_death` | `entity/flesh_amalgam_death_01.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.block_place` | `block/hive_block_place_01_soft.ogg`, `block/hive_block_place_02_dense.ogg`, `block/hive_block_place_03_wet.ogg` | 3 | C* — local sync / Sounder-manifest confirmation |
| `hive.block_break` | `block/hive_block_break_01_tear.ogg`, `block/hive_block_break_02_pop.ogg`, `block/hive_block_break_03_crunch.ogg` | 3 | C* — local sync / Sounder-manifest confirmation |
| `hive.detail_flow` | `hive/detail_flow_01.ogg`, `hive/detail_flow_02.ogg` | 2 | C* — local sync / Sounder-manifest confirmation |
| `hive.detail_membrane` | `hive/detail_membrane_01.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.detail_bubbles` | `hive/detail_bubbles_01.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.detail_creak` | `hive/detail_creak_01.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.detail_scuttle` | `hive/detail_scuttle_01.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.ambient` | `amb/hive_ambient_01.ogg`, `amb/hive_ambient_02.ogg`, `amb/hive_ambient_03.ogg` | 3 | C* — local sync / Sounder-manifest confirmation |
| `hive.ambient_close` | `amb/hive_ambient_close_01.ogg`, `amb/hive_ambient_close_02.ogg` | 2 | C* — local sync / Sounder-manifest confirmation |
| `hive.ambient_tonal_stinger` | `amb/hive_ambient_tonal_stinger.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.pulse` | `amb/hive_pulse_01.ogg`, `amb/hive_pulse_02.ogg`, `amb/hive_pulse_03.ogg` | 3 | C* — local sync / Sounder-manifest confirmation |
| `hive.ambient_surface` | `hive/amb_surface.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.ambient_deep` | `hive/amb_deep.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.ambient_core` | `hive/amb_core.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.ambient_threshold` | `hive/amb_threshold.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.zone_stinger_intensify` | `hive/zone_stinger_intensify.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.zone_stinger_release` | `hive/zone_stinger_release.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |
| `hive.zone_stinger_deep` | `hive/zone_stinger_deep.ogg` | 1 | C* — local sync / Sounder-manifest confirmation |

`C*` is provisional rather than a claim about the external Sounder workspace; the user will verify A/C from its manifest. Existing class-B path errors: 0.

## F. Sound event ID renames

The namespace remains `carnis`; Hive event IDs now use `hive.<snake_case>` with no inner dots after `hive`. Java `ModSounds` field names and subtitle keys were left unchanged; registration identifiers and `sounds.json` event keys were updated together.

| Before | After |
|---|---|
| `carnis:hive.block.place` | `carnis:hive.block_place` |
| `carnis:hive.block.break` | `carnis:hive.block_break` |
| `carnis:hive.detail.flow` | `carnis:hive.detail_flow` |
| `carnis:hive.detail.membrane` | `carnis:hive.detail_membrane` |
| `carnis:hive.detail.bubbles` | `carnis:hive.detail_bubbles` |
| `carnis:hive.detail.creak` | `carnis:hive.detail_creak` |
| `carnis:hive.detail.scuttle` | `carnis:hive.detail_scuttle` |
| `carnis:hive.spawn.alert` | `carnis:hive.spawn_alert` |
| `carnis:hive.spawn.attack` | `carnis:hive.spawn_attack` |
| `carnis:hive.spawn.idle` | `carnis:hive.spawn_idle` |
| `carnis:hive.spawn.hurt` | `carnis:hive.spawn_hurt` |
| `carnis:hive.spawn.hurt_critical` | `carnis:hive.spawn_hurt_critical` |
| `carnis:hive.spawn.death` | `carnis:hive.spawn_death` |
| `carnis:hive.spawn.skeleton_whip` | `carnis:hive.spawn_skeleton_whip` |
| `carnis:hive.spawn.skeleton_blade` | `carnis:hive.spawn_skeleton_blade` |
| `carnis:hive.spawn.skeleton_bonecrack` | `carnis:hive.spawn_skeleton_bonecrack` |
| `carnis:hive_alarm` | `carnis:hive.alarm` |
| `carnis:hive_ambient` | `carnis:hive.ambient` |
| `carnis:hive_ambient_close` | `carnis:hive.ambient_close` |
| `carnis:hive_ambient_tonal_stinger` | `carnis:hive.ambient_tonal_stinger` |
| `carnis:hive_eye_screech` | `carnis:hive.eye_screech` |
| `carnis:hive_heartbeat` | `carnis:hive.heartbeat` |
| `carnis:hive_pulse` | `carnis:hive.pulse` |
| `carnis:ambient.hive.surface` | `carnis:hive.ambient_surface` |
| `carnis:ambient.hive.deep` | `carnis:hive.ambient_deep` |
| `carnis:ambient.hive.core` | `carnis:hive.ambient_core` |
| `carnis:ambient.hive.threshold` | `carnis:hive.ambient_threshold` |
| `carnis:zone.stinger.intensify` | `carnis:hive.zone_stinger_intensify` |
| `carnis:zone.stinger.release` | `carnis:hive.zone_stinger_release` |
| `carnis:zone.stinger.deep` | `carnis:hive.zone_stinger_deep` |

Validation: 68 registry IDs = 68 `sounds.json` events; each locale contains 68 subtitle entries; `en_us` and `ru_ru` were not edited, preserving subtitle parity. No `hive.*` ID has a dotted suffix after the `hive.` prefix.

## G. Git excerpt: `InfectedCreeperEvents`

The requested `git log --all --diff-filter=D -- '*Creeper*'` cannot be run because `/home/user/Carnis-Adaptive-Hivemind` has no `.git` directory; a search under `/home/user` found neither Git metadata nor `InfectedCreeperEvents.java`. Its historical contents therefore cannot be recovered or quoted, and no contents are invented. Current decisions are implemented in the active code: one target predicate; player-only swell; `ExplosionEvent.Detonate` removes `LIVING_FLESH`, `OSSIFIED_FLESH`, `CHARRED_FLESH`, `FIREPROOF_FLESH`, `FLESH_VEINS`, `FLESH_BULB`, `CREEPING_TENDRILS`, `SPORE_SPROUT`, `NEURAL_MOSS`, `PULSING_HEART`, `STOMACH_POOL`, `NERVE_PILLAR`, `SINEW_SPIKES`, `PUSTULE_CLUSTER`, and `HIVE_EYE` from the affected-block list without cancelling the explosion; biomass remains handled by `CarnisEvents.onLivingDeath`. This checkout has one `FLESH_VEINS` registry entry and no separate tier-1..tier-4 vein registry entries. No replacement `InfectedCreeperEvents` class was added.

## H. Biomass from explosive kills

Static event-flow tracing confirms the route: when a cow dies to an Infected Creeper explosion, `LivingDeathEvent` receives the explosion source entity as an `HivemindLinkedMob`; the victim is not `BiomassValued`; the recipient remains null; and the single remaining award branch adds `basePoints(victim) = 5` for an `Animal` to `CarnisWorldData`. The explosion protection handler awards no biomass, and no separate `InfectedCreeperEvents` award path exists, so no second award was found. **The in-game cow-explosion test was not run**; +5 and no duplicate award are verified by static event-flow inspection only.

## I. Complete source dump

Delivered files: `PHASE_F_3_4_8_REPORT.md`, `PHASE_F_3_4_8_FULL_DUMP.md`, and `PHASE_F_3_4_8_FULL_DUMP.zip`. The ZIP contains all 222 project `.java` files in full, all 295 files under `src/main/resources` (including `sounds.json`, both locale files, modified animation JSON, and binary assets), plus `gradle.properties`, `build.gradle`, and `settings.gradle`. The readable Markdown dump gives every Java file, every UTF-8 text resource, and the build/version files a separate complete section with no omissions; binary OGG/PNG assets are in the ZIP.

## J. Version 3.4.8

| File | Verified setting |
|---|---|
| `gradle.properties` | `mod_version=3.4.8` |
| `build.gradle` | `version = project.mod_version` |
| `src/main/resources/META-INF/mods.toml` | `displayVersion="${mod_version}"` |


## Q1. Full actual OGG tree and unresolved declarations

The table below lists files discovered directly in `src/main/resources/assets/carnis/sounds/**/*.ogg` (paths are relative to that directory), not a list generated from `sounds.json`. The reference column is a separate comparison against declarations; the two old Amalgam files are intentionally unreferenced. The separate unresolved-path ledger in section E lists every declared sample path that does not resolve to a local file. The user reports that Sounder’s `MANIFEST_ogg` contains 107 files; that manifest is not present in this workspace, so its contents are not inferred here.

| Actual on-disk OGG path | Size (bytes) | Resolves to a `sounds.json` sample? | Declared event IDs |
|---|---:|---|---|
| `block/creeper_rupture.ogg` | 14000 | Yes | `creeper_rupture`, `hive.spawn_creeper_detonate`, `hive.amalgam_shuffle`, `hive.amalgam_slam`, `hive.spawn_attack`, `hive.spawn_death`, `hive.spawn_skeleton_blade` |
| `block/digestor_churn.ogg` | 15984 | Yes | `digestor_churn`, `hive.spawn_idle`, `hive.spawn_skeleton_bonecrack` |
| `block/heart_pulse.ogg` | 4690 | Yes | `pulsing_heart_beat` |
| `block/heartbeat_loop.ogg` | 4690 | Yes | `heartbeat_loop`, `hive.spawn_alert`, `hive.spawn_idle` |
| `block/hive_alarm.ogg` | 16209 | Yes | `hive.spawn_alert`, `hive.alarm` |
| `block/hive_eye_screech.ogg` | 16209 | Yes | `hive.spawn_alert`, `hive.eye_screech` |
| `block/hive_heartbeat.ogg` | 4690 | Yes | `hive.heartbeat` |
| `block/nervous_twitch.ogg` | 14000 | Yes | `synapse_shock`, `hive.spawn_creeper_crawl`, `hive.spawn_hurt`, `hive.spawn_skeleton_whip`, `hive.spawn_skeleton_bonecrack` |
| `block/pustule_burst.ogg` | 14973 | Yes | `pustule_burst`, `hive.spawn_creeper_sac`, `hive.spawn_hurt_critical`, `hive.spawn_skeleton_bonecrack` |
| `block/synapse_rupture.ogg` | 14000 | Yes | `synapse_rupture`, `hive.spawn_attack`, `hive.spawn_hurt_critical`, `hive.spawn_death`, `hive.spawn_skeleton_blade` |
| `entity/acid_splash.ogg` | 14973 | Yes | `acid_splash`, `hive.spawn_attack`, `hive.spawn_hurt` |
| `entity/amalgam_roar.ogg` | 25848 | No | **unreferenced** |
| `entity/amalgam_smash.ogg` | 6117 | No | **unreferenced** |
| `entity/amalgamation_fuse.ogg` | 13959 | Yes | `amalgamation_fuse`, `hive.spawn_skeleton_whip` |
| `entity/flamethrower_fire.ogg` | 7762 | Yes | `flamethrower_fire`, `hive.spawn_skeleton_whip` |
| `entity/flesh_amalgam_ambient.ogg` | 22955 | Yes | `flesh_amalgam_ambient`, `hive.amalgam_breath`, `hive.spawn_idle` |
| `entity/flesh_amalgam_death.ogg` | 25848 | Yes | `hive.spawn_death` |
| `entity/flesh_amalgam_hurt.ogg` | 10050 | Yes | `hive.spawn_hurt`, `hive.spawn_hurt_critical` |
| `hallucination/phantom_creeper.ogg` | 19302 | Yes | `phantom_creeper` |
| `hallucination/phantom_whisper.ogg` | 28406 | Yes | `phantom_whisper` |
| `item/dart_hit.ogg` | 4027 | Yes | `entity.dart.hit` |
| `item/inoculator_fire.ogg` | 6985 | Yes | `item.inoculator.fire` |
| `item/purifier_ignite.ogg` | 6860 | Yes | `item.purifier.ignite` |
| `item/purifier_loop.ogg` | 6252 | Yes | `item.purifier.loop` |

Actual tree total: **24 OGG files**; 22 resolve to at least one declared `sounds.json` sample, and the two obsolete Amalgam files are unreferenced. `sounds.json` unresolved references: **64 paths across 33 events**. They are not a reason to rewrite declarations.

The Sounder 3.4.5 filename identity mappings supplied for this diff are applied as aliases, not counted as separate files or automatic holes:

| Sounder alias / identity mapping | Reconciliation rule |
|---|---|
| `combat_armor_deflect_*` → `combat_deflect_*` | treat as the same sound identity |
| `combat_block_stab_*` → `combat_stab_*` | treat as the same sound identity |
| `combat_dismember_0N_*` → `dismember_0N` | treat as the same sound identity |
| `hive_detail_*` → `detail_*` | treat as the same sound identity |
| `spawn_hurt_critical_*` → `hive_spawn_hurt_critical_*` | treat as the same sound identity |
| `hive_block_*` in `hive/` → `hive_block_*` in `block/` | directory alias; treat as the same file |

None of the mapped target filenames appears among the 24 files in this checkout, so these aliases produce no class-B path repair here. They must be used when reconciling the Sounder manifest; the complete Q7 mapping is still pending.

## Q2. Resource-existence checks

No code or project script checks whether a sound OGG exists before registration or playback. The old `HiveAmbientSoundHandler` OGG-presence cache, fallback selection, warnings, and stinger suppression were removed. The optional glowmask resource-presence check and its reload cache were also removed. Capability `LazyOptional.isPresent()` calls are capability-state checks, not resource/file checks.

## Q3. Confirmation of §6.1–6.5

Confirmed and implemented: (6.1) only a Player that passes `validTarget` can drive the Creeper swell fuse; prey pursuit never swells/detonates; (6.2) prey selection is within 16 blocks and requires LOS; (6.3) Creeper detonations remove Hive tissue blocks from `ExplosionEvent.Detonate` without cancelling the explosion; (6.4) explosion deaths use the existing `CarnisEvents.onLivingDeath` path, with the cow +5/no-double result statically traced; (6.5) Hive sound event IDs are normalized to `carnis:hive.<snake_case>` and language subtitle keys are unchanged.

## Q4. Dump statistics

The project has **222 `.java` files**. The 3.4.7 delivery contained **19 selected files** (not the full Java project). This 3.4.8 dump contains **222/222 Java files (100%)**, plus all 295 resource files.

## Q5. Dump size / message split

A complete 222-file dump cannot fit safely in one ordinary chat message. The readable dump is split by file into 222 complete Java sections (plus complete text resources); the ZIP includes all source/resources. If the dump is emitted as chat messages instead of using these workspace artifacts, it must be split file-by-file, never truncating a file.

## Verification limits

- Static checks: JSON parse, 68 sound registry IDs = 68 `sounds.json` events, en/ru subtitle parity 68/68, actual OGG inventory and unresolved paths, and no resource-existence checks in code/scripts.
- All 222 Java files and 295 resources were counted and packaged. Delimiters in modified Java files are balanced.
- Compilation/build is unverified: this checkout has no Gradle wrapper or system Gradle. The cow-explosion biomass result is statically traced, not confirmed in a running game.
- Pose.SWIMMING does not change the Creeper hitbox; pose dimensions remain in the Phase H/I backlog. GLB/JSON spec-3 integration (conversion, pivot, 20 FPS keys, emissive sac charge, terminal death/assimilation poses) is a separate step after rev3.1 asset acceptance, not part of 3.4.8.
