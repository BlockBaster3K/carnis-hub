# Комплект к загрузке в `99-incoming/` · Ревизор · 3.8.1

**Импульс 82.** По указанию Архитектора «всё готово к скачиванию и загрузке в `99-incoming/`».
Копии **не** делал: файлы ниже — единственные экземпляры в репо (требование «дубликаты
побайтово одинаковые — удалить» сильнее; комплект-копия в `99-incoming/` была и снята).
Загружать эти пути как есть.

| Файл (путь в репо) | sha256 (16) | Что это |
|---|---|---|
| `02-reviewer/tools/creature_pack_audit.py` | `df1b63648b2d264f…` | чекер моделей/анимаций (блоки A и C) |
| `02-reviewer/tools/creature_pack_audit_selftest.py` | `18b2d605bd33d2a1…` | self-test — 11/11 |
| `02-reviewer/tools/volume_semantics_audit.py` | `413b3c4405ea4949…` | семантика громкости |
| `02-reviewer/tools/volume_semantics_audit_selftest.py` | `3ff3ea937a57877d…` | self-test — 7/7 |
| `02-reviewer/tools/release_jar_check.py` | `ffe70458f937352d…` | сверка JAR ↔ пакет (копия `tools/release_jar_check.py`, md5 совпадает) |
| `02-reviewer/reports/reviewer_gate_381_921f5cc1.log` | `0c068c778400e63e…` | итоговый прогон гейта 3.8.1 (код 1) |
| `02-reviewer/reports/reviewer_gate_381_921f5cc1_run1.log` | `56f6d519bca0bc66…` | первый прогон, до уточнения правила коллизий |
| `00-board/reports/reviewer_381_verdict.md` | `f4b0c95974ebfc3b…` | вердикт: НЕ ПРИНЯТО |
| `00-board/agents/reviewer.md` | — | статус-файл (отчёт о выполнении) |

Полные sha256: `sha256sum <путь>` — файлы не менялись с коммита `5cc86df`.
