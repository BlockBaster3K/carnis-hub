# T-3164 — проверка `TEST_3.7.1.md` и scaffold 3.7.3

## 1. Чек-лист 3.7.1 сверён с принятым ZIP

Проверен `01-coder/3.7.1/project-3.7.1-clean.zip`, SHA-256 `7ca6bdb8eaea281b6315545efceaafe4106d1bc53232af25fe2d9d360181558b`. `python3 tools/ambient_gate.py` → `ИТОГ: СХОДИТСЯ`.

| Параметр | Текущее значение |
|---|---:|
| `PULSE_INTERVAL_TICKS` | 450 = 22.50 с |
| pulse audio / пауза | 13.400 с / 9.100 с |
| pitch pulse / bed / close | 1.0 |
| bed / close effective | 0.45 / 0.45 × 0.55 = 0.2475 (≤0.25) |
| одновременно | 0.6975 (≤0.70) |
| bed и close loop lengths | 120.000 с, разброс 0.000 с; допуск ≤0.05 с |

`07-project/TEST_3.7.1.md` дополнен этими значениями и привязкой к SHA-256 принятого ZIP.

## 2. Создан `01-coder/3.7.3/`

Scaffold скопирован из `01-coder/3.7.2/`; исходная 3.7.2 не изменена. В `MANIFEST.txt` обновлено описание новой заготовки, список путей сохранён.

Версия 3.7.3 проверена в требуемых четырёх местах:

1. имя каталога `01-coder/3.7.3/`;
2. `gradle.properties`: `mod_version=3.7.3`;
3. `mods.toml`: `version="3.7.3"`;
4. `mods.toml`: `displayVersion="3.7.3"`.

Из `04-artist/deliverables/Carnis_3.7.3_creatures_recolor.zip` внесены **12 PNG / 12**, побайтово. SHA-256 архива: `822f18c9f07c350a5d0301223b3efe0ceefd2dc19a72c34f37b85ceab2be08e3`. Внесены: `biomass_maggot`, `cerebral_nexus`, `dart`, `flesh_amalgam`, `hive_sentinel`, `incubation_overlay`, `incubation_pustule`, `infected_creeper`, `infected_skeleton`, `infected_spider`, `infected_zombie`, `parasitic_tendril`.

Перекрашенные T-3142 white-list-файлы `spore_sprout.png`, `neural_moss.png`, `pustule_cluster.png` также сверены с принятой сдачей T-3115: **3/3 побайтово**.

В scaffold **760 файлов**: 759 проектных файлов + `MANIFEST.txt`. ZIP 3.7.3 не создавался; он отложен до приёмки Ревизором, как требует задача.