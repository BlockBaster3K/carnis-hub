# Carnis 3.4.10 — биохоррор, блоки: партия 1

## Передано

16 текстур четырёх семей: `living_flesh_0–3`, `ossified_flesh_0–3`, `charred_flesh_0–3`, `fireproof_flesh_0–3`. Пути внутри архива совпадают с деревом 3.4.10. Это часть категории блоков, а не все 51 PNG и не завершение общего заказа.

Исходные 16×16 RGB заменены 64×64 RGBA с непрозрачной альфой: увеличение разрешения необходимо выбранному подробному материалу и явно отличается от прежнего 16×16 pixel-art задания. Не утверждается, что старая партия ТЗ-1/2 внезапно сменила требования. Имена и файлы моделей/блокстейтов не изменены; источники нормированных UV визуально не перестраивались.

## Художественная оценка и ограничения

По оценке Художника четыре семейства приближены к новой планке: влажные связки и мембраны; костные включения; обугленные провалы без лавы; тёмная термостойкая ткань. Видимые повторения крупных форм на большой стене всё ещё возможны, особенно у вариантов одного сгенерированного исходника: разнообразие — ограничение этой партии, а не доказательство отсутствия повторов. Фактический вид в Minecraft и влияние разрешения на производительность не проверены; окончательная художественная приёмка за Архом.

AI-созданные стилизованные исходники, после чего детерминированно взяты разные области, проведена периодизация и согласование кромок; случайный шум и random.seed не применялись. Четыре варианта семейства не являются точными вращениями друг друга, но часть использует разные фрагменты одного исходника.

## Автопроверки

- Все 16: 64×64 RGBA, alpha 255, нет точных чистых #000000/#FFFFFF или RGB-первичных; имена существуют в 3.4.10.
- Для каждого семейства проверены все 256 упорядоченных сочетаний 4 вариантов и 4 поворотов с каждой стороны. Метрика: средний абсолютный RGB-перепад через кромку / средний внутренний RGB-перепад той же оси. Во всех случаях <2. Это не доказывает смысловую непрерывность рисунка или скрытность повторов.
- 9 LOCK-файлов сердца до и после записи совпали по SHA-256. Других PNG текущей категории не меняли.
- Не проверено в Minecraft/Forge; геометрию, Java, модели и blockstates не меняли.

## Проверка стыков (max по 256 парам, X / Y)

- `living_flesh`: 1.710 / 1.710
- `ossified_flesh`: 1.264 / 1.264
- `charred_flesh`: 0.909 / 0.909
- `fireproof_flesh`: 1.329 / 1.329

## Файлы, размер и SHA-256

- `src/main/resources/assets/carnis/textures/block/living_flesh_0.png` · 10891 байт · 64×64 · `9dfb7148a7b9bb418588ffff9ea7f31b7f02700238e0c14f9cf6091cd111842c`
- `src/main/resources/assets/carnis/textures/block/living_flesh_1.png` · 11024 байт · 64×64 · `fd4a475e349995983115baaa78ad94a433f96c63ba694739e4fdb4c827556dfa`
- `src/main/resources/assets/carnis/textures/block/living_flesh_2.png` · 10757 байт · 64×64 · `a84c7196c677ea3a2082917593daf1557ba77e48e599fa101619b0fe7d9a6968`
- `src/main/resources/assets/carnis/textures/block/living_flesh_3.png` · 10979 байт · 64×64 · `74261efe01f00986c6ffff797e99fe798259fd679823bc59d45031020ed95f19`
- `src/main/resources/assets/carnis/textures/block/ossified_flesh_0.png` · 11955 байт · 64×64 · `b57b41e2b9422d3b6006edae93118163243b889cf513adda4cc5ad6c958fa933`
- `src/main/resources/assets/carnis/textures/block/ossified_flesh_1.png` · 11160 байт · 64×64 · `bc11765e95b1a4934091c8fed760210f1bcaab904ae60c95cd98ce78aee9ef71`
- `src/main/resources/assets/carnis/textures/block/ossified_flesh_2.png` · 12395 байт · 64×64 · `6182c7ad92f68220fddf0c5e320735a34fba696917233a922ce39e81f1d14724`
- `src/main/resources/assets/carnis/textures/block/ossified_flesh_3.png` · 11147 байт · 64×64 · `fa79003ea18f6119f10d006813005200e8b70542e7e2a3d2ccbca5f5bfe3e81f`
- `src/main/resources/assets/carnis/textures/block/charred_flesh_0.png` · 10340 байт · 64×64 · `d57dff5a539d3d8086a9cfee59c25494715bfda9b618ff4f208293126cb316f9`
- `src/main/resources/assets/carnis/textures/block/charred_flesh_1.png` · 10837 байт · 64×64 · `ef1ca5d2b047e858d8275dd0a636f6856dac9702571411efc948b533385a0dfd`
- `src/main/resources/assets/carnis/textures/block/charred_flesh_2.png` · 10618 байт · 64×64 · `22085525a8c6dea4aa7241126e1df4b63d626305c368cd811fedf61a185c81de`
- `src/main/resources/assets/carnis/textures/block/charred_flesh_3.png` · 10486 байт · 64×64 · `8e3aad3946b7b5b132bdafe4ced92233c2dd0b2b9c87439e0a558b5e8d5e53ad`
- `src/main/resources/assets/carnis/textures/block/fireproof_flesh_0.png` · 9722 байт · 64×64 · `0603666a7fcb9b710455c427474514b55f0e852190edcd10224e4f7278753d62`
- `src/main/resources/assets/carnis/textures/block/fireproof_flesh_1.png` · 9799 байт · 64×64 · `0abbbb97c1329bc2ecaf56073277bdf23da1173b8d5d11cb499fc312fbebde17`
- `src/main/resources/assets/carnis/textures/block/fireproof_flesh_2.png` · 9911 байт · 64×64 · `0dcd3f295ade4bc6aba312bdc6f275b622fde512e34d5ef69becfd26e35a5d30`
- `src/main/resources/assets/carnis/textures/block/fireproof_flesh_3.png` · 9860 байт · 64×64 · `2b8eb54b503bf81bf1000d7358d7b9213dabf619990837064564210d00fbf5b2`

## Дальше

Оставшиеся 33 незамороженные PNG блоков: плоские сосуды/тиры, biomass, hive-детали, nerve, spore, sinew, stomach и жидкость. У tainted_sludge рендерер применяет tint `0xFF8A1A22` к серой текстуре; это учитывать, не закрашивать её вслепую. Затем предметы, существа/geo, armor/gui/particle/effect/hallucination/misc. Сердце — неизменный LOCK.
