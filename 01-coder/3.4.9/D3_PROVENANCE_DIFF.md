# 3.4.8 tree/dump provenance difference

Required provenance wording relative to the reviewer-cited common dump: **«дерево 3.4.8 менялось после снятия дампа»**.

The preserved work-baseline file is 20,259 bytes, SHA-256 `66dc02006482041a99d101b611f7fcacdb0091525ed5c216958f7d02070536e7`. The common dump cited by the reviewer is stated as 20,196-byte body / 20,197 bytes with LF, SHA-256 `819ddccd…05aff27`. The stated LF-inclusive size difference is 62 bytes; baseline vs body-only difference is 63 bytes. The cited common-dump payload is not present in this workspace, so a literal byte-level diff against it cannot be generated.

The local available `PHASE_F_3_4_8_FULL_DUMP.md` is a different dump: 1,509,456 bytes, 48,493 lines, SHA-256 `d615fd505fe82e52c1511b655c28f0fd9f157425cede0dc2acc9ad8fda2fa10c`. Its embedded fenced JSON is 20,259 bytes including terminal LF, SHA-256 equal to the preserved baseline. Its sound section is consistent with the post-Q1 baseline state, so it appears to be a later/local export, but absent Git provenance there is no proof of the exact capture sequence.

Composition of the nine event changes between the reviewer-described common dump and the actual local work-baseline JSON is in `R7_NINE_EVENT_COMPARISON.csv`. That semantic comparison is not represented as a full byte diff. The old Q1 narrative report `PHASE_F_3_4_8_REPORT.md` agrees with the saved baseline JSON on these nine entries; the JSON file is the source of truth.
