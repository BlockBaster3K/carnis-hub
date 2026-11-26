# Architect prompt — 3.8.0 detail-flow blocker and completion

**Date:** 2026-11-20 · **Status:** items 1–7 verified/completed; item 5 explicitly postponed per follow-up prompt; Git author/fetch/rebase completed, commit/push still pending. No Java compilation or JAR packaging performed.

## Completed in order

1. **3.8.0 detail flow:** changed `hive.detail_flow_01.volume` from 0.731 to 2.437. `_02` remains 1.0; call-site remains 0.30; pitches unchanged.
2. **3.7.3 package:** changed source `hive.detail_flow_01.volume` to 2.437 and rebuilt `project-3.7.3-clean.zip` from all 761 source files. ZIP SHA-256: `5d3f015943612c9e8b3189025c5df49b0228bb5ee1bbda07a5fb517ea81012c9`. Manifest 761/761 and hashes pass; archive payload matches source exactly; existing `spawn_idle_01=2.263` retained.
3. **Sound specification:** set `targets_mode` to `effective` and clarify the 0.731/0.300 targets as effective outputs; JSON multipliers 2.437/1.000 correspond to call-site 0.30.
4. **Z-16:** `incubation_cyst.png` exact SHA-256 `7d30ac39dcf8b606d9a79c8e579fd6c10a14de2d1989fd8a021175a04916ab66` verified in 3.7.3 source and ZIP.
5. **Artist assets:** deferred per `coder_prompt_380_blocker-2.md`; no 99-file assets injected.
6. **Version:** rebased Git HEAD already resolves all three requested version locations to 3.8.0 (`mod_version=3.8.0`; `mods.toml` has `version="3.8.0"` and `displayVersion="3.8.0"`). No version edit required.
7. **README/LICENSE:** both files already exist in the rebased 3.8.0 source and clean ZIP; verified both ZIP entries. Recovery source README now documents MIT code licensing and references LICENSE; local recovery inventory is exact at 787/787.

## Validation

- `volume_effective_check`: **10/10** on 3.8.0 clean ZIP and 3.7.3 clean ZIP.
- `volume_double_check`: exit **0** on 3.7.3 clean ZIP.
- 3.8.0 clean ZIP: 1,037 entries, CRC test clean, internal and external manifests regenerated/verified; README and LICENSE present; ZIP SHA-256 `33e332c54a634382d696491af558d948a25a19ab5b00fdc3a11a57327810fa52`.
- No Java compilation, Gradle task, or JAR build.

## Git publication

- Configured local author exactly as instructed: `Coder <coder@carnis.dev>`.
- Ran `git fetch origin` successfully and rebased to remote `b776f9b` successfully before commit/push.
- Existing staged C100 changes were preserved in `stash@{0}` before rebase. `stash apply --index` conflicted on upstream `gradle.properties` and `mods.toml`; no stash was dropped or overwritten. The stash remains intact and unapplied.
- Committed and pushed as `1267214e97cad45a0bbfef233704cc0868b6eb4c` (`fix: correct effective detail_flow volume [skip ci]`) to `origin/arena/d474d740-carnis-hub`; post-push fetch confirms local and remote refs match and the working tree is clean.
- Existing staged C100 changes were preserved in `stash@{0}` before rebase. `stash apply --index` conflicted on upstream `gradle.properties` and `mods.toml`; no stash was dropped or overwritten. The stash remains intact and unapplied.
- The repository's `build-jar` workflow runs on every `01-coder/**` push. Commit includes `[skip ci]` to honor the explicit prohibition on Java compilation/JAR creation; no Java compilation or JAR packaging was run.
