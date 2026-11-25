# Artist — отчёт по T-3109 (PALETTE.md и чекер плотности светотени)

- **Задача**: T-3109
- **Статус**: `STATUS: COMPLETED`
- **Артефакты**:
  - `04-artist/PALETTE.md` — заполнен по факту из `Carnis_3.7.0_A4p7_palette-R.zip` и `Carnis_3.7.0_A3R1_tendrils_recolor.zip`.
  - `04-artist/tools/shade_density.py` — чекер плотности светотени (коды `0 / 2 / 1`).
- **Проверка в обе стороны**:
  - `Carnis_3.7.0_A4p7_palette.zip` (`infected_creeper.png` 84.2%) → код `2` (`ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ`).
  - `Carnis_3.7.0_A4p7_palette-R.zip` (`infected_creeper.png` 28.3%) → код `0` (`ИТОГ: СХОДИТСЯ`).
- **Передал**: Ревизор / Интегратор
