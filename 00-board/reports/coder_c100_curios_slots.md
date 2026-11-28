# C100 — Curios slot registration (3.8.0)

**Status:** implementation prepared; integration acceptance pending. **Base:** `873d906` (`arena/d474d740-carnis-hub`). **No Java compilation, Gradle build, or JAR build was run.**

## Implemented

- Added Curios Forge `5.9.1+1.20.1` as a soft dependency in 3.8.0 only: `compileOnly` API classifier plus `runtimeOnly` Curios mod; added its Maven repository and version property.
- Added `mandatory=false` Curios metadata for Forge 1.20.1.
- Added an isolated `CuriosSlotRegistration` adapter that sends IMC registrations for one `head` and one `back` slot. The listener is attached only when `ModList` reports Curios present; no Curios API is referenced by the main entrypoint beyond that guarded adapter method reference.
- Rebuilt the 3.8.0 ZIP and both manifests; source `MANIFEST.txt` is now synchronized with the package manifest.

## Checks

- Curios Maven POM for `5.9.1+1.20.1` is available.
- `deps_soft_check.py` on the rebuilt ZIP: **code 0**; Curios API/mod are only `compileOnly`/`runtimeOnly`; no Patchouli, SmartBrainLib, Lodestone, or Sound Physics dependency was added.
- `deps_install_check.py`: **code 0**; Curios is optional in package metadata and matches the install-requirements document.
- ZIP CRC, internal manifest, and external 1,038-entry sidecar manifest: pass.
- ZIP SHA-256: `1cb324ba94ebc83a7d22ec8f09bee2f4bedbae17cea3f2c154aa26bb30ccb3c3`.
- Full `accept_3.8.0.py`: **code 1**. The new `build.gradle` Curios declarations are rejected by the current delta allow-list; other existing gate failures include missing `av`/`numpy` for timbre/crest/clip checks and `infected_sound_audit` code 1. The gate and `tools/` were left unchanged (Integrator-owned).

## Scope and pending

This implements C100’s soft dependency and slot registration only. No Curios item classes/tags were added (C101), and no death-persistence logic was added (C102). The C101 respirator design question remains open. Runtime startup with and without Curios is not claimed until an allowed Java 17/Gradle acceptance is available; C113 remains open. The previous worktrees and all existing stashes were left untouched.
