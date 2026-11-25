# Художник · Д6 — четыре варианта окостеневшей плоти

Партия отправлена по срочному приказу заказчика. База 3.5.2-R; ожидаемый перенос Кодером в 3.5.3/3.5.3-R. Публикация в `04-artist/` не изменяет JAR.

- Архив `04-artist/deliverables/Carnis_3.5.3-R_D6_ossified_flesh.zip` — 51824 Б, SHA-256 `3e46e474eb386dff0c692b39f57f01371557121142fbded8329b6cb1d7fd437a`.
- Отчёт `04-artist/deliverables/REPORT_D6_ossified_flesh.md` — SHA-256 `bdec3d5a9970dc06c6437979813939b6571d91456d5b7b1883cb41beccfa9dfa`.
- Превью `04-artist/deliverables/Carnis_3.5.3-R_D6_ossified_flesh.preview.png` — SHA-256 `f896a5286e885aa9478c2af616eba6bcae8d79d3a39986258f30fc2942c33181`.
- Все варианты RGBA 64×64, α=255. В ZIP — полные пути `src/main/resources/assets/carnis/textures/block/ossified_flesh_0.png` … `_3.png`.
- `src/main/resources/assets/carnis/textures/block/ossified_flesh_0.png` → одноимённый файл из ZIP, 11813 Б, SHA-256 PNG `0380c2c288f62c9cf8b55808fad36ccda3c41ba798d1289766e4c0a8373116ec`; SHA-256 декодированных RGBA пикселей `56134dcd17f4f0387614c08ea8df04d08cddcbe55edd368ec5dcd59b767d4749`.
- `src/main/resources/assets/carnis/textures/block/ossified_flesh_1.png` → одноимённый файл из ZIP, 11176 Б, SHA-256 PNG `dcf3a77cdaa45901aefdef58a29fe98277bed12e86d235e522ab8bcdb0ffcb34`; SHA-256 декодированных RGBA пикселей `e96ad1123608222fc80a225cf7f2c6c287e33f2d06d2acd49aaafc863555ceac`.
- `src/main/resources/assets/carnis/textures/block/ossified_flesh_2.png` → одноимённый файл из ZIP, 12136 Б, SHA-256 PNG `76afe5487bceb7edb701516755d3153fb93db0f4544932262d34159404718451`; SHA-256 декодированных RGBA пикселей `eab6df59bf7a81e2e07732ba94f69ee92674f682a8bacb076810c9998aaee833`.
- `src/main/resources/assets/carnis/textures/block/ossified_flesh_3.png` → одноимённый файл из ZIP, 11164 Б, SHA-256 PNG `cb97a4649746f9fe03d6ba62b43c2e4ff485b6849b5d81855951936869628f23`; SHA-256 декодированных RGBA пикселей `22c6e37620703e0ce71c4ec95308c51f2fdd0d7747d5afe593dd19a578194a9c`.

Независимо: средний RGB каждого варианта (89,465088; 53,750977; 47,434326); разница средних каждого из шести сочетаний = 0,000000, максимум = 0,000000. Хеши попарно разные; по попиксельному сравнению каждая пара различается на 4095–4096 из 4096 пикселей.

`tools/flesh_spread.py` появился и запущен: `РАЗБРОС = 0.00`, `ИТОГ: СХОДИТСЯ`, код 0. Полный вывод и хеши декодированных пикселей в отчёте по партии. Рендер и художественная приёмка не проверены.
