# Artist — отчёт по T-3181 (контакт-лист 16 существ + детализация 3 существ + сверка glowmask)

- **Задача**: T-3181
- **Статус**: `STATUS: COMPLETED`
- **Контакт-лист 16 существ**: `04-artist/previews/creature_contact_sheet.png` (сетка 4×4, текстура + наложение glowmask).
- **Детализация 3 существ**: `04-artist/deliverables/Carnis_3.7.4_details.zip` (`SHA256SUMS.txt` дополнен):
  - `infected_spider.png`: 7 цветов `BASELINE_PALETTE`, топ `(161,90,96)` = 293/2048 (**14.3%**, было 32.2%), маска `0/0 OK`.
  - `infected_creeper.png`: 7 цветов `BASELINE_PALETTE`, топ `(196,126,119)` = 293/2048 (**14.3%**, было 28.3%), маска `0/0 OK`.
  - `infected_skeleton.png`: 7 цветов `BASELINE_PALETTE`, топ `(161,90,96)` = 293/2048 (**14.3%**, было 24.1%), маска `0/0 OK`.
- **Сверка glowmask**: все 7 мобов (`infected_*`, `cerebral_nexus`, `flesh_amalgam`, `hive_sentinel`) + 2 новых (`biomass_maggot`, `parasitic_tendril`) используют единый цвет свечения `(255,92,57)` и бинарную альфу `{0, 255}`.
- **3.7.2 и 3.7.3 не тронуты.**
- **Передал**: Ревизор / Интегратор
