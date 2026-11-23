# Carnis 3.4.7 — технический отчёт

Состояние аудита и исходников в текущем workspace; сборка не запускалась, так как здесь отсутствуют Gradle wrapper и системный Gradle.

## A. Полный source dump

Полные тексты запрошенных и затронутых файлов собраны в `PHASE_F_3_4_7_FULL_SOURCES.md` (единый dump; файлы целиком). В частности, включены полный `sounds.json`, `ModSounds.java`, `CarnisEvents.java`, `FleshAmalgamEntity.java`, `InfectedSkeletonEntity.java`, новый `InfectedCreeperEntity.java`, `InfectedSpiderEntity.java`, `HiveSwarmCoordinator.java`, relevant goals, три animation JSON, обе локали и три версии Gradle/TOML файла.
`src/main/java/com/carnis/mod/event/InfectedCreeperEvents.java` удалён: его прежняя отмена взрыва заменена ванильным поведением Creeper.

## B. Биомасса

`CarnisEvents.onLivingDeath` сначала обрабатывает любой `BiomassValued` по его финальному `getBiomassValue()` и немедленно возвращается. Множители не применяются. В vanilla-ветке стартовый множитель `1L`; ×3 применяется только при `DartTreatmentEvents.isMutating(mob)`, ×2 — только при стадии `InfectionHandler.isInfected(victim)` (stage > 0).

| Vanilla-группа / пример | База | При обоих stage gates | Фактический код базы |
|---|---:|---:|---|
| Zombie-family (`Zombie`, `Drowned`, `Husk`, `ZombieVillager`, descendants) | 1 | 6 | `victim instanceof Zombie` |
| Passive (`cow`, `pig`, sheep and other `Animal`) | 5 | 30 | `victim instanceof Animal` |
| Vanilla Skeleton | 15 | 90 | ordinary `Monster` |
| Iron Golem / Warden | 25 | 150 | explicit rare-entity list |
| Creeper / Spider | 5 | 30 | explicit before generic Monster |
| Other vanilla Monster | 15 | 90 | `victim instanceof Monster` |
| Other vanilla entities | 5 | 30 | final fallback |

Fixed `BiomassValued` values (one authoritative entity getter each): Infected Zombie **3**, Infected Skeleton **5**, Infected Spider **5**, Infected Creeper **8**, Flesh Amalgam **25**, Hive Sentinel **40**, Cerebral Nexus **100**. They bypass both multipliers. There are no custom-entity biomass cases in `basePoints`.

**Архитектурное решение:** предложение поднять зомби-базу до 5 отклонено. Zombie-family base is 1, so 1×3×2=6; a base of 5 would produce 30 and break the stated code. Drowned/Husk/ZombieVillager now all use the same 1-point family base.

## C. `triggerAnim` inventory (all Java call sites)

| File:line | Guard / server context |
|---|---|
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:71` | `if (!level().isClientSide)` in guarded animation helper |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:75` | `if (!level().isClientSide)` in guarded animation helper |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:296` | `hurt && isAlive() && !level().isClientSide` |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:307` | `if (!level().isClientSide)` in `die()` |
| `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java:623` | `if (!level().isClientSide)` in `playAmbientSound()` |
| `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java:273` | `triggerAnimation`: `if (!level().isClientSide)` |
| `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java:88` | `changed && assimilating && !level().isClientSide` |
| `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java:147` | `damaged && isAlive() && !level().isClientSide` |
| `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java:161` | inside `if (!level().isClientSide)` in `die()` |
| `src/main/java/com/carnis/mod/item/PneumaticInoculatorItem.java:82` | inside `if (level instanceof ServerLevel server)`; GeoItem server-side trigger API |

No `triggerAnim` call remains in `InfectedZombieEntity` or elsewhere on the client. The Amalgam no longer broadcasts custom entity events or calls triggerAnim client-side; GeckoLib server calls fan out to tracking clients.

## D. Sound parity and subtitle audit

- Registered `ModSounds` ids: **68**; `sounds.json` events: **68**; ids match 1:1: **True**.
- Events with subtitles: **68**.
- `en_us`: 68 subtitle keys; missing=0; dead=0; dotted suffixes=0.
- `ru_ru`: 68 subtitle keys; missing=0; dead=0; dotted suffixes=0.
- Wave 15–16 six event identifiers are present and registered: `hive.spawn_creeper_sac`, `hive.spawn_creeper_crawl`, `hive.spawn_creeper_detonate`, `hive.amalgam_shuffle`, `hive.amalgam_breath`, `hive.amalgam_slam`. Their six English and six Russian subtitle lines exist.
- Volumes retained: 0.32 / 0.30 / 0.40 / 0.35 / 0.25 / 0.55. Each event currently points at one existing placeholder sample; the six replacements are listed under sound-author backlog below.
- Wave 17 `amalgam_smash`, `amalgam_roar`, `amalgam_step` now point at the requested `entity/flesh_amalgam_*_01..02` paths; roar pitch 0.75 is retained. Those six OGGs are not present in this workspace. `entity/flesh_amalgam_hurt.ogg` and `entity/flesh_amalgam_death.ogg` exist and remain the hurt/death event samples; requested alternate names `amalgam_hurt_01.ogg` and `amalgam_death_01.ogg` are absent.

## E. Missing OGG path ledger and actual OGG tree

Actual `src/main/resources/assets/carnis/sounds/**/*.ogg`: **24 files** (not 76 in this checkout). `sounds.json` refers to **62 absent sample paths across 31 events**. No declaration was deleted. This is the exact file debt generated from current declarations:

| Event | Missing file paths |
|---|---|
| `amalgam_smash` | `entity/flesh_amalgam_smash_01.ogg`, `entity/flesh_amalgam_smash_02.ogg` |
| `organic_creak` | `entity/organic_creak.ogg` |
| `amalgam_roar` | `entity/flesh_amalgam_roar_01.ogg`, `entity/flesh_amalgam_roar_02.ogg` |
| `amalgam_step` | `entity/flesh_amalgam_step_01.ogg`, `entity/flesh_amalgam_step_02.ogg` |
| `phantom_footsteps` | `hallucination/phantom_footsteps.ogg` |
| `hive_ambient` | `amb/hive_ambient_01.ogg`, `amb/hive_ambient_02.ogg`, `amb/hive_ambient_03.ogg` |
| `hive_ambient_close` | `amb/hive_ambient_close_01.ogg`, `amb/hive_ambient_close_02.ogg` |
| `hive_pulse` | `amb/hive_pulse_01.ogg`, `amb/hive_pulse_02.ogg`, `amb/hive_pulse_03.ogg` |
| `hive_ambient_tonal_stinger` | `amb/hive_ambient_tonal_stinger.ogg` |
| `flesh_block_step` | `flesh/flesh_block_step_01.ogg`, `flesh/flesh_block_step_02.ogg`, `flesh/flesh_block_step_03.ogg` |
| `hive.block.place` | `block/hive_block_place_01_soft.ogg`, `block/hive_block_place_02_dense.ogg`, `block/hive_block_place_03_wet.ogg` |
| `hive.block.break` | `block/hive_block_break_01_tear.ogg`, `block/hive_block_break_02_pop.ogg`, `block/hive_block_break_03_crunch.ogg` |
| `hive.spread` | `hive/hive_spread_01_creep.ogg`, `hive/hive_spread_02_pulse.ogg`, `hive/hive_spread_03_swell.ogg` |
| `combat.flesh_hit` | `combat/combat_flesh_hit_01.ogg`, `combat/combat_flesh_hit_02.ogg`, `combat/combat_flesh_hit_03.ogg` |
| `combat.flesh_hit_deep` | `combat/combat_flesh_hit_deep_01_axe.ogg`, `combat/combat_flesh_hit_deep_02_crit.ogg`, `combat/combat_flesh_hit_deep_03_blast.ogg` |
| `combat.dismember` | `combat/dismember_01.ogg`, `combat/dismember_02.ogg`, `combat/dismember_03.ogg`, `combat/dismember_04.ogg`, `combat/dismember_05.ogg` |
| `combat.armor_deflect` | `combat/combat_deflect_01_chitin.ogg`, `combat/combat_deflect_02_bone.ogg`, `combat/combat_deflect_03_metal.ogg`, `combat/combat_deflect_04_glance.ogg`, `combat/combat_deflect_05_parry.ogg` |
| `combat.block_stab` | `combat/combat_stab_01_bone.ogg`, `combat/combat_stab_02_chitin.ogg`, `combat/combat_stab_03_shield.ogg` |
| `hive.detail.flow` | `hive/detail_flow_01.ogg`, `hive/detail_flow_02.ogg` |
| `hive.detail.membrane` | `hive/detail_membrane_01.ogg` |
| `hive.detail.bubbles` | `hive/detail_bubbles_01.ogg` |
| `hive.detail.creak` | `hive/detail_creak_01.ogg` |
| `hive.detail.scuttle` | `hive/detail_scuttle_01.ogg` |
| `bone_deflect` | `block/bone_deflect.ogg` |
| `ambient.hive.surface` | `hive/amb_surface.ogg` |
| `ambient.hive.deep` | `hive/amb_deep.ogg` |
| `ambient.hive.core` | `hive/amb_core.ogg` |
| `ambient.hive.threshold` | `hive/amb_threshold.ogg` |
| `zone.stinger.intensify` | `hive/zone_stinger_intensify.ogg` |
| `zone.stinger.release` | `hive/zone_stinger_release.ogg` |
| `zone.stinger.deep` | `hive/zone_stinger_deep.ogg` |

Actual OGG tree (path — byte size):

```text
block/creeper_rupture.ogg — 14000 bytes
block/digestor_churn.ogg — 15984 bytes
block/heart_pulse.ogg — 4690 bytes
block/heartbeat_loop.ogg — 4690 bytes
block/hive_alarm.ogg — 16209 bytes
block/hive_eye_screech.ogg — 16209 bytes
block/hive_heartbeat.ogg — 4690 bytes
block/nervous_twitch.ogg — 14000 bytes
block/pustule_burst.ogg — 14973 bytes
block/synapse_rupture.ogg — 14000 bytes
entity/acid_splash.ogg — 14973 bytes
entity/amalgam_roar.ogg — 25848 bytes
entity/amalgam_smash.ogg — 6117 bytes
entity/amalgamation_fuse.ogg — 13959 bytes
entity/flamethrower_fire.ogg — 7762 bytes
entity/flesh_amalgam_ambient.ogg — 22955 bytes
entity/flesh_amalgam_death.ogg — 25848 bytes
entity/flesh_amalgam_hurt.ogg — 10050 bytes
hallucination/phantom_creeper.ogg — 19302 bytes
hallucination/phantom_whisper.ogg — 28406 bytes
item/dart_hit.ogg — 4027 bytes
item/inoculator_fire.ogg — 6985 bytes
item/purifier_ignite.ogg — 6860 bytes
item/purifier_loop.ogg — 6252 bytes
```

Wave 15–16 placeholder replacements that need dedicated files:

| Event | Current valid reused sample |
|---|---|
| `hive.spawn_creeper_sac` | `block/pustule_burst.ogg` |
| `hive.spawn_creeper_crawl` | `block/nervous_twitch.ogg` |
| `hive.spawn_creeper_detonate` | `block/creeper_rupture.ogg` |
| `hive.amalgam_shuffle` | `entity/amalgam_smash.ogg` |
| `hive.amalgam_breath` | `entity/flesh_amalgam_ambient.ogg` |
| `hive.amalgam_slam` | `entity/amalgam_smash.ogg` |

## F. Goal priorities (including inherited vanilla goals)

Within each selector there are no repeated priorities after normalizing the Creeper/Spider inherited random-look goal. Lower number means higher priority.

| Entity class | `goalSelector` priorities | `targetSelector` priorities |
|---|---|---|
| `InfectedZombieEntity` (overrides parent registration) | 0,1,2,3,4,5,6,7 | 1,2,3 |
| `InfectedSkeletonEntity` (overrides parent registration) | 0,1,2,3,4,5,6,7,8,9 | 1,2 |
| `InfectedSpiderEntity` (Spider parent retained; parent random-look moved to 7) | vanilla 1,3,4,5,6,7; mod 8,9,10 | vanilla 1,2; mod prey 4 |
| `InfectedCreeperEntity` (Creeper parent retained; parent random-look moved to 7) | vanilla 1,2,3,4,5,6,7; mod 8,9 | custom live Player 1; inherited hurt-by 2; prey 3 |
| `FleshAmalgamEntity` | 0,1,2,3,5,6,7 | 1,2 |
| `BiomassMaggotEntity` | 0,1,2,3,4 | none |
| `ParasiticTendrilEntity` | 0,2,5 | 1 |

Vanilla parent goals are retained where applicable. Spider has its ordinary player/hurt targets at 1/2; Creeper’s nearest-player goal is replaced by its explicit live-player goal at 1 while vanilla hurt-by remains at 2. The spider prey selector is 4, preserving priorities 1/2/3.

## G. #B-019 Infected Creeper checklist

| Requirement | Result |
|---|---|
| 7.1 extends vanilla `Creeper`; no explosion cancellation/replacement | PASS — removed the prior cancel-and-custom-damage event; `super.tick()` drives the vanilla fuse, explosion damage, block destruction and sound |
| 7.2 fixed biomass | PASS — one `BIOMASS_VALUE = 8L` constant and getter |
| 7.3 own attributes builder / not default 20 HP | PASS — `Creeper.createAttributes()` baseline plus MAX_HEALTH 24; registration calls this class builder |
| 7.4 Hive filter, coordinator prey gate, live player hostility | PASS — Hive targets rejected; custom visible-player goal and `canAttack` accept every living Player (including creative/spectator); prey candidates go through `validTarget` |
| 7.5 sound sequence | PASS — sac on start of swelling; detonate once when local `getFuse()==5` (250ms before vanilla fuse completion); crawl on entry/steps with `Util.getMillis()` 3000ms debounce; hurt/death/idle Hive events; no duplicate custom explosion |
| 7.6 synchronized states | PASS — `SAC_CHARGING`, `CRAWLING` are SynchedEntityData booleans; assimilation remains synchronized |
| 7.7 stealth crawl | PASS — `Pose.SWIMMING` inside 10 blocks without line of sight; previous pose restored on exit |
| 7.8 animation set | PASS — idle, walk, fuse, sac_charge, detonate, crawl, hurt, death; attack remains JSON-only/reserved and is not referenced by Java |
| 7.9 registration/localization | PASS — entity type, attributes event, spawn egg/creative tab and en/ru entity names already exist; three subtitles are present in both languages |
| 7.10 compile / no duplicates / priorities | STATIC PASS — no new duplicate sound calls; selector priorities audited. Compilation is unverified because Gradle is unavailable. |

## H. Version

| File | Declaration |
|---|---|
| `gradle.properties` | `mod_version=3.4.7` |
| `build.gradle` | `version = project.mod_version`; `base { archivesName = project.archives_base_name }` |
| `src/main/resources/META-INF/mods.toml` | `displayVersion="${mod_version}"`; no `${file.jarVersion}` |

## Validation caveats

- Static JSON parsing, registry/lang parity, new animation-key existence, target-priority review, and sound-path inventory passed.
- No Gradle wrapper or system Gradle exists in this workspace; do not treat this report as a successful Java compilation or in-game test.
- The expected Wave 17/claimed 76-file audio package was not present locally; this report describes only the 24 files actually found.
