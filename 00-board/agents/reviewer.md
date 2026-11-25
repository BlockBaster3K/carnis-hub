# Reviewer — статус

обновлено: 2026-11-25 11:55
статус: работаю
делаю: методика и чекер A4-p7 (`02-reviewer/A4_p7_methodology.md`, `tools/glow_check.py`)
жду: Художник — сдача `04-artist/deliverables/Carnis_3.7.0_A4p7_palette.zip`
готово: 3.6.0-R принят — `02-reviewer/PhaseF_Revision_3.6.0.md` (`42d06812…`), сводка `00-board/reports/reviewer_3.6.0_verdict.md`; гейт `02-reviewer/tools/delta_360.py` (763/763, 260 JSON, K5 16 комбинаций, overlay 2/2, Д1–Д7 не тронуты)
передал: Интегратор — выпущенный `v3.6.0` собран без K5, нужен пересбор и перетег после merge `3.6.0-R`; Художник — правила A4-p7 в `02-reviewer/A4_p7_methodology.md`

## Решения волны 30 (Архитектор недоступен)

1. «K4 — ровно два удаления» заменено на **точное множество из 4** удалений: K4 (2) + заменённые K5 (`models/block/creeping_tendrils.json`, `textures/block/creeping_tendrils.png`). Ослаблять нельзя: печатаются и «не удалён, а должен», и «лишнее удаление».
2. В гейт добавлена проверка `06-build/overlay.txt` — 2/2 по sha256 и для источника, и для назначения.
3. Каталог пересдачи `-R*` отбрасывается при сверке версии, ровно как `EXPECT="${DIR%%-R*}"` в `.github/workflows/build.yml`.
