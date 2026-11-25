# Кодер · T-3103 — сборка 3.7.0

**Статус:** выполнено по актуальному рецепту T-3103 и исправленному гейту T-3119.

## Команды и результаты

| Команда / действие | Результат |
|---|---|
| Интеграция `Carnis_3.7.0_A4p7_palette-R.zip` | 8 PNG внесены; принимается именно `-R` (infected_creeper top colour 28.3%). A3R1 уже интегрирован, чекер подтверждает 4/4. |
| `python3 tools/build_3.7.0_assembly.py` | шаги 1–6 выполнены; 9 loop OGG побайтово из банка; breath 2/2 с `volume 0.35`; версия 4/4; ZIP 759 файлов; manifest 759 строк и `sha256sum -c` 759/759. |
| `python3 tools/ambient_gate.py 01-coder/3.7.0` | код 0, `ИТОГ: СХОДИТСЯ`; pulse/bed/close pitches 1.0, pulse interval 450 ticks, gap 9.100 s, effective length spread 0.000 s, gains 0.45+0.25=0.70. |
| `python3 tools/sound_orphans.py 01-coder/3.7.0` | код 0; 82 events, 144 refs/files, сирот 0. |
| `python3 tools/timbre_check.py 01-coder/3.7.0/project-3.7.0-clean.zip` | код 0, `ИТОГ: СХОДИТСЯ`; official Reviewer checker, after PyAV installed outside repository. |
| `python3 tools/accept_3.7.0.py` | код 0, `ИТОГ: ПРИНЯТО`; A4-p7-R 8/8 and A3R1 4/4, accepted 14/14. |
| `git diff --check` | код 0. |

**Release ZIP:** `01-coder/3.7.0/project-3.7.0-clean.zip`, 12,572,981 Б, SHA-256 `6c62c4543e73b6d56c91eb13c96ae067f825e5a093ed73101ce82f05092f38c2`.
**Release manifest:** `01-coder/3.7.0/project-3.7.0-clean.manifest.txt`, 759 entries, SHA-256 `c690b3720245fe7a90057258af7d9bf559961993644464e7ccc392977235d3a6`.

## Полный вывод `python3 tools/accept_3.7.0.py`

```text
Приёмка пакета 3.7.0 (ТЗ 3.7.0)
Пакет:   01-coder/3.7.0/project-3.7.0-clean.zip
Размер:  12572981 Б
SHA-256: 6c62c4543e73b6d56c91eb13c96ae067f825e5a093ed73101ce82f05092f38c2

Распаковано 759 записей, дубликатов путей 0.

1) Манифест (sha256sum -c)
   01-coder/3.7.0/project-3.7.0-clean.manifest.txt
  ✓ совпало 759, расхождений 0, строк 759

2) JSON
  ✓ JSON: 260 файлов, невалидных 0

3) Версия 3.7.0 в четырёх местах
  ✓ gradle.properties: 3.7.0
  ✓ mods.toml version: 3.7.0
  ✓ displayVersion: 3.7.0
  ✓ имя пакета: 3.7.0

4) Overlay (cmp источник — пакет)
  ✓ overlay: совпало 2 из 2

5) A4-p7 — палитра существ (ТЗ §2.3)
  ✓ glow_check → код 0 | ИТОГ: СХОДИТСЯ

6) K8-S — сиротские .ogg (ТЗ §3)
  ✓ sound_orphans → код 0 | ИТОГ: СХОДИТСЯ — сирот 0, ссылок в пустоту 0

7) A3R1 — цвет щупалец под плоть (через чекер Ревизора)
  ✓ A3R1 → код 0 | ИТОГ: СХОДИТСЯ

8) Ambient-фикс (Р-31.2 Архитектора)
  ✓ PULSE_INTERVAL_TICKS = 450 (нужно 420–480)
  ✓ громкость кровати: не 0.85F (нужно 0.45F)
  ✓ pitch ambient-слоёв: все 1.0 или не заданы
      ambient-фикс выполнен
  ✓ ambient_gate (Ревизор) → код 0 | ИТОГ: СХОДИТСЯ
  ✓ amalgam_breath: 2 подключено, volume [0.35] (нужно 0.35)

9) Принятые слои лежат в пакете побайтово
  ✓ A4-p7-R: файлов в архиве 8, в пакете идентично 8, изменено 0, нет 0
  ✓ A3R1: файлов в архиве 4, в пакете идентично 4, изменено 0, нет 0

10) Д1–Д7 и принятое не тронуто
  ✓ сверено с 3.6.0-R: идентично 14, изменено 0, нет 0

ИТОГ: ПРИНЯТО — все проверки пройдены.
Дальше: CI на новом коммите → merge PR → тег v3.7.0 → Release.
```

Игра, Gradle/JAR-сборка и публикация не выполнялись. Автоматическая приёмка пакета зелёная; далее нужны независимый Reviewer и действия Интегратора по релизному процессу.
