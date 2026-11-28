# Очистка workspace · отчёт Ревизора · импульс 81

**Дата:** 2026-11-22 · **Задание:** Архитектор, «Очистка workspace и подготовка к приёмке 3.8.1»
**Состояние до правок:** HEAD `fb2dc76`, дерево чистое.

## 1. Список файлов, как просили

### `02-reviewer/tools/` — 19 файлов

```
alpha_audit.py                        crest_delta.py                  repo_tree_guard.py
attack_check.py                       crest_norm_selftest.py          verify_372_bank_delta.py
bank_peak_audit.py                    delta_360.py                    verify_373_delta.py
ci_guard_test.py                      delta_r1.py                     volume_semantics_audit.py
creature_pack_audit.py                geo_pairs_d5.py                 volume_semantics_audit_selftest.py
creature_pack_audit_selftest.py       infected_sound_audit.py
readme_license_check.py               release_jar_check.py   ← добавлен этим импульсом
```

### `02-reviewer/reports/` — 2 файла (каталог создан этим импульсом)

```
reviewer_gate_381_921f5cc1.log        21 980 Б — итоговый прогон гейта 3.8.1 (код 1)
reviewer_gate_381_921f5cc1_run1.log   22 215 Б — первый прогон, до уточнения правила коллизий
```

## 2. Что удалено

| Что | Где | Объём |
|---|---|---|
| `__pycache__` | `tools/`, `02-reviewer/tools/` | 2 каталога |
| побайтовый дубль лога 3.8.0 | `00-board/reports/reviewer_gate_380_26edbeef.log` | 14 939 Б |

Дубль проверен `md5sum`: `54992d77a87c41328becbc4dce14cfdc` у обоих файлов, то есть
`reviewer_gate_380_26edbeef_after_fix.log` — тот же байт в байт. Оставил тот, на который
ссылается мой план (R35), удалил безымянный.

`build/`, `dist/`, `.cache/` в дереве **не было** — искал `find` по всему репо, кроме `.git`.

## 3. Что перенесено

- логи 3.8.1: `00-board/reports/` → `02-reviewer/reports/` (как в задании);
  в вердикте §7 путь обновлён, чтобы ссылка не врала.

## 4. Чего я **не** удалил — и почему

### 4.1. Вердикты `reviewer_373_verdict.md` и `reviewer_380_verdict.md` — удалять нельзя

Проверил не рассуждением, а прогоном: убрал оба файла в `/tmp`, запустил
`tools/ci_resolver_dryrun.py`, вернул обратно. Вывод:

```
  ⛔ 3.8.1    решение отрицательное (строка 8): НЕ ПРИНЯТО
  ⛔ 3.8.0    вердикта нет
  ⛔ 3.7.3    вердикта нет
  ✅ 3.7.2    принят

  CI выберет: 3.7.2
  ⛔ пропущены более старшие версии: 3.8.1, 3.8.0, 3.7.3
     релиз уйдёт ИЗ СТАРОГО пакета
```

Резолвер ищет вердикт по имени версии (`ci_resolver_dryrun.py:107`), а вердикт 3.8.1
отрицательный. Без двух старших вердиктов CI откатывается на **3.7.2** — ровно тот отказ,
против которого написан З-СИ-1. Экономия — 22 КБ, цена — релиз из пакета трёхнедельной
давности. Оставил.

### 4.2. Остальные отчёты 3.7.3/3.8.0 — ссылочные

`reviewer_gate_380_block16_audit.md` цитирует мой же self-test
(`creature_pack_audit_selftest.py`, шапка файла), на `reviewer_373_verdict.md` ссылаются
`integrator_i6_release_blocker.md`, `integrator_release_380.md`, `coder_373_build.md`,
`ROADMAP_reviewer.md` и `ROADMAP_integrator.md`. Удаление рвёт ссылки **в файлах других ролей**,
а их я по заданию не трогаю. Суммарный вес всех моих отчётов — 3,4 МБ; выигрыш нулевой,
риск — оборванная цепочка сдач.

### 4.3. Где на самом деле лежит вес

Крупнейшие файлы вне `.git`, `01-coder`, `03-sound`, `06-build`:

```
3 007 093  04-artist/analysis_horror_3410/materials/ossified_flesh_master.png
2 773 345  04-artist/analysis_horror_3410/materials/living_flesh_master.png
2 735 824  …/living_flesh_2.png   2 611 884  …/living_flesh_3.png
2 604 254  …/ossified_flesh_2.png  2 525 791  …/charred_flesh_master.png
```

Это материалы Художника (`04-artist/`), не мои файлы — не трогал. Если нужен реальный
выигрыш места, вопрос к нему, а не к `02-reviewer/` (весь каталог — 536 КБ).

## 5. Проверка после очистки (чтобы не отчитаться «убрал», а получить «работает»)

| проверка | результат |
|---|---|
| `creature_pack_audit_selftest.py` | **11/11**, расхождений 0 |
| `volume_semantics_audit_selftest.py` | **7/7** |
| `release_jar_check.py --help` из `tools/` и из `02-reviewer/tools/` | оба запускаются |
| `verdict_decision.py` по вердикту 3.8.1 | «решение отрицательное (строка 8): НЕ ПРИНЯТО» |
| `ci_resolver_dryrun.py` | CI выбрал бы 3.8.0 (вердикты на месте) |
| md5 копии `release_jar_check.py` | `95ab0b0b03c213e580ca1ce662b96628` — совпадает |

## 6. Готовность к `99-incoming/`

Собран комплект `99-incoming/reviewer_381/`: 5 инструментов, 2 лога гейта, вердикт, шапка
статуса, `SHA256SUMS` и `UPLOAD_README.md` (состав, как прогнать, два предупреждения:
`release_jar_check.py` обязан остаться и в `tools/` из-за `build.yml:395`; логи под `*.log`
в `.gitignore`, добавлены через `git add -f`).
