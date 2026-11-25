# Отчёт A4-p7: Палитра существ и glowmask (Carnis 3.7.0)

- **Статус**: СДАНО (`ИТОГ: СХОДИТСЯ`, код возврата `0`)
- **Артефакт**: `04-artist/deliverables/Carnis_3.7.0_A4p7_palette.zip`
- **SHA-256**: `e6ebb8d11a9c79f703e11bb08f6b9542b0c3aec762c1cc57ae6eb42de7d0c767`
- **Чекер приёмки**: `tools/glow_check.py` (SHA-256 `0003b8eaf9513c403c4ec9e664bc9ee72255405df45385dee31dfda0956825f8`, принят Интегратором в `00-board/reports/integrator_a4p7_unblock.md` вместо отсутствующего `02-reviewer/A4_p7_methodology.md`).

## Выполненные работы
1. Взяты эталонные 8 текстур из `01-coder/3.6.0-R/src/main/resources/assets/carnis/textures/entity/`.
2. Четыре текстуры тел (`infected_creeper.png` 64×32, `infected_skeleton.png` 64×32, `infected_spider.png` 64×32, `infected_zombie.png` 64×64) перекрашены по ранговому распределению яркости в ровно 7 непрозрачных цветов `BASELINE_PALETTE` с сохранением альфы `255` и побитовой идентичности маски `α>0`.
3. Четыре glowmask (`*_glowmask.png`) приведены к единому цвету свечения `(255, 92, 57, 255)` на всех пикселях `α>0` эталона и `(0, 0, 0, 0)` на `α=0` (включая бинаризацию полупрозрачных пикселей `200/210` у `infected_skeleton_glowmask.png`).
4. Архив `04-artist/deliverables/Carnis_3.7.0_A4p7_palette.zip` собран с целевыми путями `src/main/resources/assets/carnis/textures/entity/<имя>.png`.
5. Манифест `04-artist/deliverables/SHA256SUMS.txt` дополнен новой записью.

## Результаты `tools/glow_check.py`
- Размеры и альфа: все 8 файлов `ok` (тела `[255]`, glowmask `[0, 255]`).
- Палитра тел: ровно 7 непрозрачных цветов из `BASELINE_PALETTE`, вне палитры `0 ok`.
- Glowmask: ровно 1 непрозрачный цвет `(255, 92, 57, 255)` у всех 4 файлов.
- Маска побитово идентична эталону: пропало `0`, добавилось `0 ok` у всех 8 файлов.
- Итог: `ИТОГ: СХОДИТСЯ`.
