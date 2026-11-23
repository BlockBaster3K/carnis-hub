# Carnis Adaptive Hivemind — 3.4.9-R, D1–D4 unblock package

**Package directory:** `/home/user/Carnis-Adaptive-Hivemind/deliverables/3.4.9/`  
**Code status:** no Java code was changed for this resubmission. Resource-tree status did change: the two legacy orphan OGGs described in R11 were removed. Thus “code unchanged” applies to `.java`; it does not mean the resource tree was untouched. This report is outside the package so the requested captured `sha256sum deliverables/3.4.9/*` output does not hash a report that contains its own hash output.

## D1 — Physical package and command evidence

The required files now physically exist in `deliverables/3.4.9/`: `00_R1_FULL_JAVA_DUMP.md`, `sounds-3.4.8-baseline.json`, `sounds-3.4.9-final.json`, `LEDGER_97_PATHS.md`, `OGG_INVENTORY_22.md`, and `SHA256SUMS_349R.txt`. Supporting provenance, diff, callsite, fuse, orphan-removal, resources, build-config, and 11 full Java-source files are also present.

### Literal output: `ls -la deliverables/3.4.9/`

```text
total 1104
drwxr-xr-x 5 user user   4096 Nov 23 10:05 .
drwxr-xr-x 3 user user     60 Nov 23 09:10 ..
-rw-r--r-- 1 user user 953021 Nov 23 09:45 00_R1_FULL_JAVA_DUMP.md
-rw-r--r-- 1 user user    544 Nov 23 10:04 D2_LOCAL_DUMP_MEASUREMENTS.txt
-rw-r--r-- 1 user user   1507 Nov 23 10:04 D3_PROVENANCE_DIFF.md
-rw-r--r-- 1 user user   1262 Nov 23 10:05 D3_Q1_FILE_COMPARE.csv
-rw-r--r-- 1 user user   1094 Nov 23 10:04 D4_LEDGER_COUNTS.md
-rw-r--r-- 1 user user  15379 Nov 23 10:04 LEDGER_97_PATHS.md
-rw-r--r-- 1 user user   3084 Nov 23 10:04 OGG_INVENTORY_22.md
-rw-r--r-- 1 user user    282 Nov 23 09:46 R10_FUSE_TABLE.csv
-rw-r--r-- 1 user user    455 Nov 23 09:46 R11_REMOVED_ORPHAN_OGG.csv
-rw-r--r-- 1 user user    797 Nov 23 09:46 R2_PROVENANCE.txt
-rw-r--r-- 1 user user  20259 Nov 23 09:45 R2_dump_fenced_sounds.json
-rw-r--r-- 1 user user  20258 Nov 23 09:45 R2_dump_fenced_sounds_body_without_final_newline.json
-rw-r--r-- 1 user user   1921 Nov 23 10:04 R7_NINE_EVENT_COMPARISON.csv
-rw-r--r-- 1 user user   2463 Nov 23 09:45 R7_baseline_to_final.diff
-rw-r--r-- 1 user user   2355 Nov 23 09:47 R8_OGG_FILESYSTEM_INVENTORY.csv
-rw-r--r-- 1 user user   6846 Nov 23 09:45 R8_SILENCE_LEDGER.csv
-rw-r--r-- 1 user user    440 Nov 23 09:45 R8_SILENCE_SUMMARY.txt
-rw-r--r-- 1 user user   7987 Nov 23 09:46 R9_JAVA_CALLSITES_ALL_68.csv
-rw-r--r-- 1 user user   4000 Nov 23 10:05 SHA256SUMS_349R.txt
drwxr-xr-x 2 user user    128 Nov 23 09:45 build-config
drwxr-xr-x 3 user user     60 Nov 23 09:14 java
drwxr-xr-x 3 user user     60 Nov 23 10:04 resources
-rw-r--r-- 1 user user  20259 Nov 23 09:10 sounds-3.4.8-baseline.json
-rw-r--r-- 1 user user  20698 Nov 23 09:15 sounds-3.4.9-final.json
```

### Literal output: `sha256sum deliverables/3.4.9/*`

The command hashes the top-level regular files and reports the three matching directories on stderr. The recursive `SHA256SUMS_349R.txt` manifest lists every regular file under the package except itself; this command’s output also supplies the manifest’s own hash.

**stdout:**

```text
359f090adf755c6509c04969517da21295847e5c5a1098bb7bdc616973c20914  deliverables/3.4.9/00_R1_FULL_JAVA_DUMP.md
357ed20fe2b0d841bf5510bfb7679598824ca0943d87d5e0a19f128aa28c1e38  deliverables/3.4.9/D2_LOCAL_DUMP_MEASUREMENTS.txt
520497abcd0c1b43c3690d41fb4534367631d5a7aa81bedae55757260a23bf4b  deliverables/3.4.9/D3_PROVENANCE_DIFF.md
9f878bd0f43eef56d0353ae2dd4521fc5e5bcec56535f7853e4658540b4d7af9  deliverables/3.4.9/D3_Q1_FILE_COMPARE.csv
6d4d75b6e72917bb1b557ae0b2db548bd54df921e40f5acb15002526036bd927  deliverables/3.4.9/D4_LEDGER_COUNTS.md
877f6a3771c589a3a0a1cda58d0f0fc6c1023511a1986de72f3b0c76f0c8993d  deliverables/3.4.9/LEDGER_97_PATHS.md
4987ca3d12bceb08a6446ebbccfd1a8a40b4f408679542039f0146df09573414  deliverables/3.4.9/OGG_INVENTORY_22.md
8c43e5a00052fffb190444481c3da06fc3c9d238a84a305d298d9e1126d4beba  deliverables/3.4.9/R10_FUSE_TABLE.csv
f7c64ca75e786465ab7e3ea503d2d762225dcbc8839754c909463e9a30072b14  deliverables/3.4.9/R11_REMOVED_ORPHAN_OGG.csv
31726410ac8ec258e8b3b7bc95727111e18b567d7c6954c2ae26d7e2a8dd6470  deliverables/3.4.9/R2_PROVENANCE.txt
66dc02006482041a99d101b611f7fcacdb0091525ed5c216958f7d02070536e7  deliverables/3.4.9/R2_dump_fenced_sounds.json
453a01a61bf1d633eaf7db9a40031430f8e1d706d18f780c7523c74f6eb91530  deliverables/3.4.9/R2_dump_fenced_sounds_body_without_final_newline.json
32e8bccb854b60488b598d7c50d4c2dcf388f60d3fa209c90af6f0541c8e4997  deliverables/3.4.9/R7_NINE_EVENT_COMPARISON.csv
993c571068bb06dc375a6f237f18dd7a78a5b968107e375f68376620c7d49412  deliverables/3.4.9/R7_baseline_to_final.diff
aa3a3dd2cb8223aa5b56774cb3b1cf36cabca05402c9d4519647722b1419de0d  deliverables/3.4.9/R8_OGG_FILESYSTEM_INVENTORY.csv
0d3ebd8ab5ed65299a391edca7d3f381287c9a4ea1eab8cea55dc58d8742a38d  deliverables/3.4.9/R8_SILENCE_LEDGER.csv
4842f191586e4892a9c892d4224049d9cb7f880d19d5826275d6726b8aa3d0b3  deliverables/3.4.9/R8_SILENCE_SUMMARY.txt
b174839bef4fc053569a28abf59757560c7fa315a2e3ac884865efe45eb1426d  deliverables/3.4.9/R9_JAVA_CALLSITES_ALL_68.csv
aec3a0ab203b131d242064039d953f13a12118cc565345370c40ba017c150c9f  deliverables/3.4.9/SHA256SUMS_349R.txt
66dc02006482041a99d101b611f7fcacdb0091525ed5c216958f7d02070536e7  deliverables/3.4.9/sounds-3.4.8-baseline.json
b44634bc022bd83e4b455b47129ee22da23bf2756acecaacfc92ace88fc5556c  deliverables/3.4.9/sounds-3.4.9-final.json
```

**stderr:**

```text
sha256sum: deliverables/3.4.9/build-config: Is a directory
sha256sum: deliverables/3.4.9/java: Is a directory
sha256sum: deliverables/3.4.9/resources: Is a directory
```

The checksum manifest was built recursively over all package regular files except itself; its own hash is present in the captured command output above.

## D2 — Hash, size, line count, and identity of the dump actually used

The local file used is **`PHASE_F_3_4_8_FULL_DUMP.md`**. Its measured size is **1,509,456 bytes**, line count (**`wc -l`**) **48,493**, SHA-256 **`d615fd505fe82e52c1511b655c28f0fd9f157425cede0dc2acc9ad8fda2fa10c`**. `stat` reports mtime `2026-11-23 09:08:49.373986144 +0000`. These measurements and section offsets are in `D2_LOCAL_DUMP_MEASUREMENTS.txt`.

This is **not** the Revision note’s stated common dump (`1,513,635` bytes, `48,582` lines, hash beginning `e7b3281d` and ending `252187`). The local file is 4,179 bytes and 89 lines shorter. Its JSON section begins at line 45,951, body lines 45,954–46,885, closing fence line 46,886; the reference offsets supplied by the reviewer are 46,040, 46,043–46,974, and 46,975. Both sections have 932 body lines, but the local fenced body is 20,259 bytes including LF (20,258 without LF), not the cited 20,197/20,196. The local JSON is valid, has 68 events, and `json.dumps(indent=2) + LF` reproduces its body byte-for-byte.

There are two different 3.4.8 dump artifacts. The one available and used here is the local `PHASE_F_3_4_8_FULL_DUMP.md`; its embedded sounds JSON matches the saved work-baseline file exactly. Its event declarations match the post-Q1 saved state, so it is consistent with a later/local export, but the workspace has no Git history or creation record to prove whether it was captured after Q1. The reviewer’s common dump file / `PhaseF_Revision_3.4.9_R.md` was not present in the workspace.

## D3 — Provenance and baseline/Q1 comparison

For the reviewer-cited common dump versus the later 3.4.8 tree, the requested provenance wording is: **«дерево 3.4.8 менялось после снятия дампа»**.

The baseline file in this package is 20,259 bytes, SHA-256 `66dc02006482041a99d101b611f7fcacdb0091525ed5c216958f7d02070536e7`. The reviewer’s stated common payload with LF is 20,197 bytes, SHA-256 fragment `819ddccd…05aff27`; the measured difference using those LF-inclusive sizes is **+62 bytes** (baseline versus body-only it is +63 bytes). Since that common payload is not available locally, a literal byte diff against it cannot be generated. `D3_PROVENANCE_DIFF.md` gives the distinction and `R7_NINE_EVENT_COMPARISON.csv` contains the nine-event semantic comparison using the reviewer-described dump entries, the actual saved baseline file, and final JSON.

The saved baseline file agrees with the older local Q1 report’s sample claims on all nine audited events. The comparison is in `D3_Q1_FILE_COMPARE.csv`; every row says `yes`. Thus the JSON file and that Q1 table do **not** diverge on those nine entries. The key mismatch is instead between that post-Q1 baseline/local dump and the reviewer-cited earlier common dump. The JSON artifact, not the narrative table, remains the content authority.

## D4 — Two ledger reference systems

The two count systems are recorded in `D4_LEDGER_COUNTS.md`:

| Reference system | Silent events | Delta | Newly voiced | Unique paths | OGG files on disk |
|---|---:|---:|---:|---:|---:|
| Reviewer-cited common dump → final | 28 → 37 | +9 | 0 | 80 → 97 | 24 → 22 |
| Actual saved baseline JSON → final | 33 → 37 | +4 | 0 | 86 → 97 | 24 → 22 |

The common-dump row uses the figures supplied by the reviewer; because that common dump file is absent locally, those baseline totals cannot be independently recalculated from its full 68-event JSON here. The second row is calculated from the saved baseline/final JSON and local filesystem evidence. Its four newly silent events are `hive.amalgam_shuffle`, `hive.amalgam_slam`, `hive.spawn_attack`, and `hive.spawn_skeleton_blade`; the five Amalgam Wave 17 entries were already fully silent in the saved baseline.

`LEDGER_97_PATHS.md` is the requested 97-row path ledger. Each row has the exact sample path, physical presence, work-baseline references, final references, final heard/silent status, and reference system. The common-dump aggregate is kept distinct; unavailable path/event rows from that file are not invented. `OGG_INVENTORY_22.md` is the exact post-R11 filesystem inventory with path, byte size, filename, and final-JSON resolution status. The `amb/`, `combat/`, `flesh/`, and `hive/` directories are absent.

## Remaining package items

- `00_R1_FULL_JAVA_DUMP.md`: all **222** `.java` files, path-labelled and fenced, **953,021 bytes**; the 11 changed Java files also exist in full under `java/`.
- `sounds-3.4.8-baseline.json`: **20,259 bytes**, SHA-256 `66dc02006482041a99d101b611f7fcacdb0091525ed5c216958f7d02070536e7`.
- `sounds-3.4.9-final.json`: **20,698 bytes**, SHA-256 `b44634bc022bd83e4b455b47129ee22da23bf2756acecaacfc92ace88fc5556c`.
- R4 resources: `resources/assets/carnis/sounds.json`.
- R5: `build-config/gradle.properties`, `build-config/build.gradle`, `build-config/mods.toml`.
- R6: 11 complete Java sources in `java/`.
- R9: `R9_JAVA_CALLSITES_ALL_68.csv` audits all 68 sound events, a superset of the 23-position request; the 11 no-callsite events match the earlier audit.
- R10 (closed): `R10_FUSE_TABLE.csv` lists reachable fuse values 30..2; the fuse-5 reference remains 250 ms.
- R11 (closed): `sounds/entity/amalgam_roar.ogg` (25,848 bytes) and `sounds/entity/amalgam_smash.ogg` (6,117 bytes) were removed from the project tree. No Sounder-bank files were accessed.

No code was changed in this unblock pass. A Gradle build was not run because there is no wrapper or system Gradle executable in the workspace.


## D1 — Complete package file paths, bytes, and hashes

The following is the recursive file inventory for the upload folder. The manifest itself is listed using its hash from the captured `sha256sum deliverables/3.4.9/*` output; the manifest omits its own line to avoid self-reference. The report remains outside the folder and is not an upload artifact. No files were pushed to GitHub; the user will transfer the folder to `01-coder/3.4.9-R/`.

| Relative path | Bytes | SHA-256 |
|---|---:|---|
| `00_R1_FULL_JAVA_DUMP.md` | 953021 bytes | `359f090adf755c6509c04969517da21295847e5c5a1098bb7bdc616973c20914` |
| `D2_LOCAL_DUMP_MEASUREMENTS.txt` | 544 bytes | `357ed20fe2b0d841bf5510bfb7679598824ca0943d87d5e0a19f128aa28c1e38` |
| `D3_PROVENANCE_DIFF.md` | 1507 bytes | `520497abcd0c1b43c3690d41fb4534367631d5a7aa81bedae55757260a23bf4b` |
| `D3_Q1_FILE_COMPARE.csv` | 1262 bytes | `9f878bd0f43eef56d0353ae2dd4521fc5e5bcec56535f7853e4658540b4d7af9` |
| `D4_LEDGER_COUNTS.md` | 1094 bytes | `6d4d75b6e72917bb1b557ae0b2db548bd54df921e40f5acb15002526036bd927` |
| `LEDGER_97_PATHS.md` | 15379 bytes | `877f6a3771c589a3a0a1cda58d0f0fc6c1023511a1986de72f3b0c76f0c8993d` |
| `OGG_INVENTORY_22.md` | 3084 bytes | `4987ca3d12bceb08a6446ebbccfd1a8a40b4f408679542039f0146df09573414` |
| `R10_FUSE_TABLE.csv` | 282 bytes | `8c43e5a00052fffb190444481c3da06fc3c9d238a84a305d298d9e1126d4beba` |
| `R11_REMOVED_ORPHAN_OGG.csv` | 455 bytes | `f7c64ca75e786465ab7e3ea503d2d762225dcbc8839754c909463e9a30072b14` |
| `R2_PROVENANCE.txt` | 797 bytes | `31726410ac8ec258e8b3b7bc95727111e18b567d7c6954c2ae26d7e2a8dd6470` |
| `R2_dump_fenced_sounds.json` | 20259 bytes | `66dc02006482041a99d101b611f7fcacdb0091525ed5c216958f7d02070536e7` |
| `R2_dump_fenced_sounds_body_without_final_newline.json` | 20258 bytes | `453a01a61bf1d633eaf7db9a40031430f8e1d706d18f780c7523c74f6eb91530` |
| `R7_NINE_EVENT_COMPARISON.csv` | 1921 bytes | `32e8bccb854b60488b598d7c50d4c2dcf388f60d3fa209c90af6f0541c8e4997` |
| `R7_baseline_to_final.diff` | 2463 bytes | `993c571068bb06dc375a6f237f18dd7a78a5b968107e375f68376620c7d49412` |
| `R8_OGG_FILESYSTEM_INVENTORY.csv` | 2355 bytes | `aa3a3dd2cb8223aa5b56774cb3b1cf36cabca05402c9d4519647722b1419de0d` |
| `R8_SILENCE_LEDGER.csv` | 6846 bytes | `0d3ebd8ab5ed65299a391edca7d3f381287c9a4ea1eab8cea55dc58d8742a38d` |
| `R8_SILENCE_SUMMARY.txt` | 440 bytes | `4842f191586e4892a9c892d4224049d9cb7f880d19d5826275d6726b8aa3d0b3` |
| `R9_JAVA_CALLSITES_ALL_68.csv` | 7987 bytes | `b174839bef4fc053569a28abf59757560c7fa315a2e3ac884865efe45eb1426d` |
| `build-config/build.gradle` | 3180 bytes | `ccc1b11f5117cf2d4290480a7fe9ec3f3c9a6eb1c30979674ad543bd2c67cecf` |
| `build-config/gradle.properties` | 778 bytes | `014804b4b610d22fd1bad42f0eb639c5f2700c976fb1e849f90717510f034641` |
| `build-config/mods.toml` | 867 bytes | `b331d3ec4db400290737bdb1f98cd0ecac4aa236138d2f0aec4a82d2184e235e` |
| `java/com/carnis/mod/client/renderer/layer/OptionalGlowLayer.java` | 2894 bytes | `c460a5f45b2789408f59b729c3a5bce98c42abf3760ca10b5d87be086b609169` |
| `java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java` | 17319 bytes | `e7e1b27a9aa0cbb455fe8a8935902fba06ddc9644d5226325b281c722f35196b` |
| `java/com/carnis/mod/entity/FleshAmalgamEntity.java` | 24047 bytes | `e521f4935701275ca1144199db7f15685d87c238a305c54bd537d41b59a49d2e` |
| `java/com/carnis/mod/entity/InfectedCreeperEntity.java` | 13347 bytes | `bff39acbad67e77386a104e453d36d0bfcfe3ca63388733053e364976ad32752` |
| `java/com/carnis/mod/entity/InfectedSkeletonEntity.java` | 15772 bytes | `b87cf35a23a4e696c5883f83b0afd67d504f06a46b0de16618348eebb60a6df2` |
| `java/com/carnis/mod/entity/InfectedZombieEntity.java` | 6793 bytes | `c51a637b00260a58ca344379c263a1dfcf9ead71aa2924f60caf51a8efa77538` |
| `java/com/carnis/mod/entity/ai/AmalgamBiomassFeast.java` | 4027 bytes | `a766a878045be84cd74bb356402f8751f14076664099ca9e7e50b0fde5ec354c` |
| `java/com/carnis/mod/entity/ai/FleshAmalgamAbilityGoal.java` | 6279 bytes | `019e95c3b961be67b68aa18cc511f5f6c9d919cfb8f5100712e4ca00245c7eef` |
| `java/com/carnis/mod/entity/ai/FleshAmalgamChargeGoal.java` | 4705 bytes | `1bcf57b5f8a0c1a3d8c2c4ff4c97048630362c08e34520b630d26ba7391a0c93` |
| `java/com/carnis/mod/entity/ai/HiveSwarmCoordinator.java` | 12445 bytes | `84ba349b7ee0eb8add639b5abbda81a717e385ad5dcb19bb1aabd312c9833423` |
| `java/com/carnis/mod/entity/ai/InfectedSpiderRangedSpatGoal.java` | 1770 bytes | `04d5fa347d52e14ee9edfe7b0bf50211c06c06e5c413d57498d3c2a651d31974` |
| `resources/assets/carnis/sounds.json` | 20698 bytes | `b44634bc022bd83e4b455b47129ee22da23bf2756acecaacfc92ace88fc5556c` |
| `sounds-3.4.8-baseline.json` | 20259 bytes | `66dc02006482041a99d101b611f7fcacdb0091525ed5c216958f7d02070536e7` |
| `sounds-3.4.9-final.json` | 20698 bytes | `b44634bc022bd83e4b455b47129ee22da23bf2756acecaacfc92ace88fc5556c` |
| `SHA256SUMS_349R.txt` | 4000 | `aec3a0ab203b131d242064039d953f13a12118cc565345370c40ba017c150c9f` |

## Exchange repository lookup

The specified `05-architect/3.4.9-R_BLOCKERS.md` URL returned HTTP 404. The public repository’s `05-architect/` directory currently contains only `.gitkeep`; a recursive repository-tree check found no `3.4.9` or `BLOCKERS` file. The user-provided D1–D4 text was used instead. No claim is made that the external blocker file was read.

## Чистый снапшот проекта для шины

Создана полная копия допустимых файлов проекта в `/home/user/project-3.4.9-clean/`. Состав манифеста: **564 файла**, суммарно **2,063,453 байта**. Построчный манифест формата `path|bytes`: `/home/user/project-3.4.9-clean.manifest.txt` (**39,766 байт**), SHA-256: **`c3cee5ca52fcd72168acd7fca2318e9578dfbba7ecb65a5338068d3b33fcee05`**.

Подтверждение: **«кэши и креды исключены»**. Исключены `.git/`, `.gradle/`, build/run/out, IDE caches, logs, compiled files, credentials/local properties/keystores, deliverables и `PHASE_F_*`. Проверка путей снапшота не нашла ни одного такого файла. Снапшот не загружался в GitHub; перенос в `07-project/3.4.9/` остаётся за Пользователем.

В исходном дереве проекта отсутствовали `.gitignore`, `gradle/`, `gradlew` и `gradlew.bat`; копия их не выдумывает и не добавляет. Существующие `src/`, ресурсы и root build files включены.
