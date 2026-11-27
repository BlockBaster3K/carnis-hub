# Coder · 3.8.1 scaffold and initial Curios port

**Date:** 2026-11-20 · **Status:** scaffold / source implementation only; not release acceptance

## Baseline and package

- Started from the accepted v3.8.0 artifact with SHA-256 `26edbeefa9dc40fcaf29d0d32b2dd65483678d8fb0fc7577f656af13886ea07c`, recovered from the pre-C100 baseline (`99fe2ce^`). No 3.7.x files were used.
- Created `01-coder/3.8.1/` with version declarations updated to 3.8.1 and regenerated internal/external manifests.
- Ported the optional Curios 5.9.1+1.20.1 Maven repository, `compileOnly` API + `runtimeOnly` mod, `mandatory=false` metadata, and guarded HEAD/BACK IMC slot registration.
- Package README clarifies Curios is not required to launch; both client and server need Curios only when using the slots.
- Candidate ZIP: 1,038 entries, CRC and internal/external manifests verified; SHA-256: `921f5cc1ff0f667f5a6ebb942c30b114caeccc7a4acffd939aa7fc5cb110a7ad`.
- `deps_soft_check` code 0; `readme_license_check` code 0. `deps_install_check` code 0 against its configured `install_requirements.md` (3.8.0); the copied 3.8.1 report has the same dependency declarations and SHA of the 3.8.1 scaffold. The install checker is not yet parameterized for the 3.8.1 report. These are static package checks only.

## Scope and checks

- This is a development scaffold, not a claim that C100 is accepted. No Gradle/Java/JAR build or game runtime test was run.
- C101/C102 accessories and death persistence remain open; the respirator behavior/design question is unresolved.
- The six historical local gate findings are closed for published 3.8.0 and are not copied as defects to this 3.8.1 work. See `coder_380_gate_reconciliation.md`.
- Next concurrent track is the approved SBL AI/Goals pilot for `flesh_amalgam` and `hive_sentinel` (C107/C108), moved to 3.8.1 at the user's request. Preserve the vanilla Goal fallback and do not expand to other mobs.
