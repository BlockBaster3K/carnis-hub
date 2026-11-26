# Rebuild 3.7.3 and 3.8.0 sound packages

**Date:** 2026-11-20 · **Status:** rebuilt, verified, and published to `arena/d474d740-carnis-hub`. No Java compilation or JAR build.

## Changes

- Inserted S128 `volume` values in both `sounds.json` files:
  - `combat.flesh_hit`: 0.995 / 1.270 / 1.729.
  - `hive.spread`: 1.921 / 1.336 / 1.702.
- Kept `hive.detail_flow_01=2.437`, `_02=1.0`, and `hive.spawn_idle_01=2.263` intact.
- Copied the six corrected canonical OGGs (`combat_flesh_hit_01..03` and `hive_spread_01_creep`, `_02_pulse`, `_03_swell`) from `03-sound/sounds/` into both version source trees.
- Rebuilt both ZIPs and their sidecar manifests. The 3.8.0 internal manifest was regenerated as well.
- Updated the effective targets in `volume_spec_t3202.json` for `hive.spread` to call-site 0.65 × JSON volume: 1.24865 / 0.8684 / 1.1063.

## Artifacts

| Package | ZIP entries | SHA-256 |
|---|---:|---|
| 3.7.3 | 761 | `a9346ef25bbcb246394f573dd6236ec05041da4f216fb56053f723d32144465a` |
| 3.8.0 | 1,037 | `26edbeefa9dc40fcaf29d0d32b2dd65483678d8fb0fc7577f656af13886ea07c` |

Both packages include exact byte matches to the current banks: **144/144** OGGs in 3.7.3 and **276/276** in 3.8.0. Both ZIP CRC tests and external manifests passed; the 3.8.0 internal manifest hashes were verified. `sounds_coverage_check.py` passes for both packages. `volume_double_check.py` returns code 0 on both. The full `volume_effective_check.py` passes **11/11** on each package.

The checker’s no-code-multiplier proof was narrowly extended to allow only explicitly verified unity routes: direct event returns, `playAt(..., 1.0F)`, or a `SoundType` hit argument with constructor volume and pitch exactly `1.0F`. Any unknown usage continues to fail closed. This verifies the existing combat call-sites without changing Java behavior. No Java or JAR build was run.
