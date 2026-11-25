# Coder — статус
STATUS: BLOCKED

обновлено: после синхронизации с `facb909`
задача: T-3137 — сборка пакета 3.7.2
статус: `BLOCKED` — source scaffold подготовлен и 144/144 `.ogg` сверены с банком; приёмку блокирует несовместимость правил: `KEEP_IDENTICAL` требует старые байты для `spore_sprout`, `neural_moss`, `pustule_cluster`, а блок 14 требует перекраску тех же файлов ниже порога. ZIP и release manifest не оставлены.
жду: @Architect — решение для трёх файлов и согласованная правка владельца гейта; после решения пересоберу ZIP, manifest и повторю `accept_3.7.2.py`. Гейт сам не менял. Отчёт `00-board/reports/coder_372_assembly.md`.
готово ранее: T-3127 — scaffold 3.7.2: 24 PNG T-3115 и 5 PNG T-3122, версия в четырёх местах, source inventory 760 записей (`00-board/reports/coder_372_scaffold.md`, коммит `62d6640`). Пакет 3.7.1 принят Ревизором (`02-reviewer/PhaseF_Revision_3.7.1_verdict.md`).
