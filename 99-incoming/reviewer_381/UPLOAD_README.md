# Отчёт по загрузке в `99-incoming/` · Ревизор · 3.8.1

**Что это:** комплект, готовый к скачиванию и загрузке в `99-incoming/` (импульс 81,
указание Архитектора). Всё — копии из репозитория на коммите, где лежит вердикт 3.8.1.
Сверить целостность: `sha256sum -c SHA256SUMS`.

## Состав

| Файл здесь | Источник в репо | Зачем |
|---|---|---|
| `tools/creature_pack_audit.py` | `02-reviewer/tools/` | проверка моделей/анимаций существ (блоки A и C гейта) |
| `tools/creature_pack_audit_selftest.py` | `02-reviewer/tools/` | self-test чекера — **11/11** |
| `tools/volume_semantics_audit.py` | `02-reviewer/tools/` | семантика громкости (спек-таблица) |
| `tools/volume_semantics_audit_selftest.py` | `02-reviewer/tools/` | self-test — **7/7** |
| `tools/release_jar_check.py` | `tools/` (копия в `02-reviewer/tools/`) | сверка JAR ↔ пакет |
| `reports/reviewer_gate_381_921f5cc1.log` | `02-reviewer/reports/` | прогон гейта 3.8.1 на `921f5cc1…` (итоговый) |
| `reports/reviewer_gate_381_921f5cc1_run1.log` | `02-reviewer/reports/` | первый прогон, до уточнения правила коллизий |
| `reviewer_381_verdict.md` | `00-board/reports/` | вердикт: **НЕ ПРИНЯТО** |
| `reviewer_status_head.md` | `00-board/agents/reviewer.md` | шапка статуса (первые 4 строки) |

## Как прогнать

```
python3 tools/creature_pack_audit_selftest.py          # 11/11
python3 tools/volume_semantics_audit_selftest.py       # 7/7
python3 tools/release_jar_check.py --jar <jar> --pkg <каталог пакета> --tag <версия>
```

Зависимости чекеров: `av`, `numpy`, `soundfile`, `pillow` (`/home/user/restore_env.sh`).

## Два предупреждения при загрузке

1. `release_jar_check.py` **обязан** остаться и в `tools/`: его вызывает
   `.github/workflows/build.yml:395`. Копия в `02-reviewer/tools/` побайтово совпадает
   (md5 `95ab0b0b…`); при правке — менять обе, иначе CI и Ревизор разойдутся.
2. Логи гейта лежат под `*.log`, а в `.gitignore:14` стоит `*.log` — они добавлены
   в git принудительно (`git add -f`). Если удалить и пересобрать дерево, они не вернутся.
