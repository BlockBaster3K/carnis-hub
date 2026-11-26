# Carnis: Adaptive Hivemind — Phase F 3.4.10 report

## §1 — Scope, version, and handoff

Round **3.4.10** is prepared as a single clean source package. `gradle.properties` sets `mod_version=3.4.10`; `build.gradle` assigns the project version from that property; `mods.toml` explicitly declares both `version="3.4.10"` and `displayVersion="3.4.10"`. No GitHub upload or repository transfer was performed; handoff is for the user to carry out.

## §2 — F1: one canonical language-resource source

The two checked-in final locale files live only at `src/generated/resources/assets/carnis/lang/en_us.json` and `ru_ru.json`. The competing `src/main/resources/assets/carnis/lang/` JSON files were removed, so `sourceSets.main.resources` adds the generated directory as the sole language resource source and does not rely on `DuplicatesStrategy.EXCLUDE` to choose between competing locale files. Each locale contains **274 keys** with exact en/ru key parity: 68 canonical `carnis.subtitle.*` entries, 14 custom-damage death entries, and all block/item/entity/tooltip/codex and other existing entries. No `subtitles.carnis.*` key remains. The checked-in JSON was reconciled with `ModLanguageProvider` as the intended datagen output.

## §3 — F5 and F6

- **F5:** `CarnisEvents.java` now tests `event.getExplosion().getExploder()` instead of the removed/obsolete `getSourceMob()` call.
- **F6:** assimilated zombies are no longer assigned a custom player-name component or forced-visible custom name. The previous nameplate setter calls were removed; equipment, persistence, and spawn behavior remain unchanged.

## §4 — Custom damage death-message coverage

Both English and Russian locale files contain all 14 death translation keys below. `%1$s` is present in every value; every `.player` value also has `%2$s`. The aliases for `bio_purifier_surface` (whose JSON `message_id` is `bio_purifier`) and `tainted_sludge` (whose `message_id` is `carnis_tainted_sludge`) are included alongside the actual message IDs.

- `death.attack.bio_purifier`
- `death.attack.bio_purifier.player`
- `death.attack.bio_purifier_surface`
- `death.attack.bio_purifier_surface.player`
- `death.attack.carnis_tainted_sludge`
- `death.attack.carnis_tainted_sludge.player`
- `death.attack.necrotic_consumption`
- `death.attack.necrotic_consumption.player`
- `death.attack.organic_consumption`
- `death.attack.organic_consumption.player`
- `death.attack.purification_dart`
- `death.attack.purification_dart.player`
- `death.attack.tainted_sludge`
- `death.attack.tainted_sludge.player`

The six registered damage type resource files checked were `bio_purifier`, `bio_purifier_surface`, `necrotic_consumption`, `organic_consumption`, `purification_dart`, and `tainted_sludge`.

## §5 — Errata and complete Java comparison

`ClientModEvents.java` is explicitly included in the comparison/report (the F2 retrospective declaration). The raw baseline used is `/home/user/baseline_3.4.8_raw.md`, with SHA-256 `e7b3281d6070b2f6e167b49f1b65f277a0512e249feccebea9e59446fe252187`; it contains 222 Java blocks. The current tree also contains 222 Java files. Exact text comparison identifies the following 15 changed Java files:

- `src/main/java/com/carnis/mod/client/ClientModEvents.java`
- `src/main/java/com/carnis/mod/client/renderer/layer/OptionalGlowLayer.java`
- `src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java`
- `src/main/java/com/carnis/mod/datagen/ModLanguageProvider.java`
- `src/main/java/com/carnis/mod/entity/FleshAmalgamEntity.java`
- `src/main/java/com/carnis/mod/entity/InfectedCreeperEntity.java`
- `src/main/java/com/carnis/mod/entity/InfectedSkeletonEntity.java`
- `src/main/java/com/carnis/mod/entity/InfectedZombieEntity.java`
- `src/main/java/com/carnis/mod/entity/ai/AmalgamBiomassFeast.java`
- `src/main/java/com/carnis/mod/entity/ai/FleshAmalgamAbilityGoal.java`
- `src/main/java/com/carnis/mod/entity/ai/FleshAmalgamChargeGoal.java`
- `src/main/java/com/carnis/mod/entity/ai/HiveSwarmCoordinator.java`
- `src/main/java/com/carnis/mod/entity/ai/InfectedSpiderRangedSpatGoal.java`
- `src/main/java/com/carnis/mod/event/CarnisEvents.java`
- `src/main/java/com/carnis/mod/infection/PlayerInfectionManager.java`

This list includes the original 12 baseline-divergent files, the language provider changed for F1/death messages, and the F5/F6 files. The full, unabridged dump of all 222 `.java` files is `PHASE_F_3_4_10_FULL_JAVA_DUMP.md`.

**F4:** In `deliverables/3.4.9/R7_NINE_EVENT_COMPARISON.csv`, the `amalgam_step` ref was corrected from `carnis:entity/amalgam_step.ogg` to `carnis:entity/amalgam_smash.ogg`; the actual step samples remain as recorded in the comparison column.

## §6 — Validation, proof of life, and exclusions

Static proof-of-life passed: both JSON files parse; each has 274 keys and identical key sets; exactly 68 canonical subtitle keys exist per locale; no legacy subtitle namespace remains; all 14 death keys exist in both locales with required placeholders; F5 and F6 source assertions pass; only one en/ru language JSON pair is present under `src`; version declarations and the F4 CSV ref match the requested values; the archive file list and every embedded manifest hash were validated. The current `sounds.json` byte-compares equal to the prior 3.4.9 checked-in comparison copy.

Gradle is not installed in this workspace, so a Gradle compile, datagen run, jar inspection, and in-game test could not be run. No build success is claimed. Per scope, `sounds.json` was not edited; no listed dead sound events were connected; deprecation warnings and GeckoLib were not changed.

## §7 — Handoff files

- `project-3.4.10-clean.zip` — package contains exactly `src/`, `build.gradle`, `gradle.properties`, `settings.gradle`, and embedded `MANIFEST.txt`.
- `project-3.4.10-clean.manifest.txt` — external readable manifest for every regular payload file in the archive (SHA-256 and byte size).
- `PHASE_F_3_4_10_FULL_JAVA_DUMP.md` — all 222 Java source files, full text.
- `PHASE_F_3_4_10_REPORT.md` — this report.
- `R7_NINE_EVENT_COMPARISON_3.4.10.csv` — corrected R7 comparison CSV (also updated in the project deliverables tree).
- `SHA256SUMS.txt` — flat SHA-256 checksums of the five handoff files above (not self-hashed).
