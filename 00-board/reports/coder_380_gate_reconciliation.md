# Reconciliation: 3.8.0 accepted release vs local C100 candidate gate

**Date:** 2026-11-20 · **Decision source:** user correction + repository evidence

## Official 3.8.0 status

- Published tag: `v3.8.0` → commit `be5fdb5386c3fedecd2c1c93e7f1a7419269b0d4` (confirmed with `git ls-remote origin`).
- Accepted package: `01-coder/3.8.0/project-3.8.0-clean.zip`, SHA-256 `26edbeefa9dc40fcaf29d0d32b2dd65483678d8fb0fc7577f656af13886ea07c`.
- `00-board/reports/reviewer_380_verdict.md` records a full `accept_3.8.0.py` run on those exact bytes: code 0, **ПРИНЯТО**. The Integrator's `I40` record also says the 3.8.0 package was accepted, gate code 0.
- Independently verified that the pre-C100 parent snapshot `99fe2ce^` contains a package with the same `26edbeef…` SHA. It is a valid 3.8.0 source baseline for forward work; it is not a reason to rebuild or alter the release.

## Six findings from the later local run

The six findings were produced by `tools/accept_3.8.0.py` against the post-release Curios/documentation working candidate (later SHA `864d1f1750e5a5861b1c0b90e2ac6fe1d7a0fa17499ba83f001ef136b6095b18`), **not** the accepted release archive. The user has confirmed the released 3.8.0 package is accepted. Therefore all six are closed as historical/non-applicable to the published 3.8.0 release; do not reopen 3.8.0 or carry these run results forward as 3.8.1 defects.

| # | Local finding | Reconciliation |
|---:|---|---|
| 1 | Unexpected delta vs 3.7.3 (including `build.gradle`) | Was on the post-release Curios candidate; Curios work is rolled forward to 3.8.1. Not a defect in accepted `26edbeef…` bytes. |
| 2 | `timbre_check` code 1 | Reported only on the later candidate run. The accepted release's complete, exact-SHA gate passed; this does not establish a defect in released bytes. No 3.8.1 task from this diagnostic alone. |
| 3 | `infected_sound_audit` code 1 | Reported only on the later candidate run. Superseded for release status by the exact-SHA accepted verdict; no cause is inferred here and no defect is carried forward from this result alone. |
| 4 | Crest parse 0/15 | The local workspace lacked the independent crest inputs used in full acceptance. Not an open 3.8.0 release issue. |
| 5 | Crest attack unavailable (`numpy+av` missing) | Environment could not execute the check; the full accepted-release run had the required inputs. Not a package defect. |
| 6 | Bank clipping unavailable (`av+numpy` missing) | Environment could not execute the check; the full accepted-release run measured the bank and reported zero clipping. Not a 3.8.1 implementation task. |

For any future 3.8.1 package, run its own version-appropriate gate with its own complete independent inputs. Do not infer a 3.8.1 pass from the 3.8.0 verdict, and do not copy these six local diagnostics as open 3.8.1 work items.

## Forward scope

- The Curios slot-registration and installation-doc changes in commits `99fe2ce` and `24c9c89` are post-release working-branch changes, **not** part of the published `v3.8.0` release. Do not rebuild or relabel the release. Roll the unfinished Curios work (C100–C103) forward to 3.8.1.
- Patchouli journal scaffold (C104–C106) likewise rolls forward; retain JSON-only pages and soft-dependency constraints.
- At the user's direction, schedule the already-approved SBL/AI Goals pilot (C107–C108; `flesh_amalgam` and `hive_sentinel`) alongside those tasks in 3.8.1, instead of the former 3.9.0 target. Preserve optionality and vanilla-Goal fallback; do not expand the pilot to other mobs.
- The 3.8.1 scaffold should derive from the accepted 3.8.0 artifact/source baseline, never from 3.7.x. No 3.8.1 acceptance, Java/Gradle build, or runtime validation is claimed by this reconciliation.
