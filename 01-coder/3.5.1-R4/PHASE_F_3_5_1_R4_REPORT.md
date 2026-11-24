# Carnis 3.5.1-R4 — отчёт о переносе партии p1

Перенесены на существующие пути 16 блок-текстур p1. `mod_version` остаётся `3.5.1`. Все заменённые source images — 64×64; модели/blockstates и UV не менялись. Сборка, Gradle, runtime и `runData` не запускались.

## 16 заменённых PNG

| Файл | SHA-256 до | SHA-256 после | Размер изображения до → после | Размер файла до → после |
|---|---|---|---:|---:|
| `charred_flesh_0.png` | `747d96c5160eeffe95501d0603063dcf65a0a9a3df0857193a57eb5207119010` | `d57dff5a539d3d8086a9cfee59c25494715bfda9b618ff4f208293126cb316f9` | 16×16 → 64×64 | 247 → 10340 B |
| `charred_flesh_1.png` | `52d240864a004258e3f021497ccb1221aaa0a943dc887fc68d8c98d97920c14a` | `ef1ca5d2b047e858d8275dd0a636f6856dac9702571411efc948b533385a0dfd` | 16×16 → 64×64 | 273 → 10837 B |
| `charred_flesh_2.png` | `9c5451ea231718b1e3d5ead23a2abad0c3d5d06640e38a97fc22c097fc80f57f` | `22085525a8c6dea4aa7241126e1df4b63d626305c368cd811fedf61a185c81de` | 16×16 → 64×64 | 267 → 10618 B |
| `charred_flesh_3.png` | `f84385ec19143e0fcf1039ecb3809b0c1e8cf81603d450d856821e2acc770625` | `8e3aad3946b7b5b132bdafe4ced92233c2dd0b2b9c87439e0a558b5e8d5e53ad` | 16×16 → 64×64 | 245 → 10486 B |
| `fireproof_flesh_0.png` | `2913329fbcc7859fd821446379ae80c03c7302817cb2dd705623b1f3c5d2f5ee` | `0603666a7fcb9b710455c427474514b55f0e852190edcd10224e4f7278753d62` | 16×16 → 64×64 | 270 → 9722 B |
| `fireproof_flesh_1.png` | `c7d842b7aa81645843d76563e49d68b641287aa74f1cf4778c6415f6c0f3b05b` | `0abbbb97c1329bc2ecaf56073277bdf23da1173b8d5d11cb499fc312fbebde17` | 16×16 → 64×64 | 288 → 9799 B |
| `fireproof_flesh_2.png` | `a0c12532c9a792e7cccfd5cd7388f1671f10da58fc2fb4dde426f8baabe25307` | `0dcd3f295ade4bc6aba312bdc6f275b622fde512e34d5ef69becfd26e35a5d30` | 16×16 → 64×64 | 297 → 9911 B |
| `fireproof_flesh_3.png` | `dd170af8058cbab6b5e639b80faccfa69974fe2c77fc65c99f02d0da1441f98b` | `2b8eb54b503bf81bf1000d7358d7b9213dabf619990837064564210d00fbf5b2` | 16×16 → 64×64 | 283 → 9860 B |
| `living_flesh_0.png` | `a0ea192029749ed54e0cf10e4985a57a9b7f9608dc8ddfa32e5adebdba11bddd` | `9dfb7148a7b9bb418588ffff9ea7f31b7f02700238e0c14f9cf6091cd111842c` | 16×16 → 64×64 | 269 → 10891 B |
| `living_flesh_1.png` | `ec787b5467fd641a52b284be51c337432377c8b1930dccd5e00f9a6325580d9f` | `fd4a475e349995983115baaa78ad94a433f96c63ba694739e4fdb4c827556dfa` | 16×16 → 64×64 | 276 → 11024 B |
| `living_flesh_2.png` | `e62fde7c74e426826a13b4635cb973870fa9adf62516e72de6043ac1e6868923` | `a84c7196c677ea3a2082917593daf1557ba77e48e599fa101619b0fe7d9a6968` | 16×16 → 64×64 | 289 → 10757 B |
| `living_flesh_3.png` | `0a292fc791de291b629be21034e9329787430660c121e95502f64fc7fd582cc2` | `74261efe01f00986c6ffff797e99fe798259fd679823bc59d45031020ed95f19` | 16×16 → 64×64 | 282 → 10979 B |
| `ossified_flesh_0.png` | `d4aeda3b6803cf34e2d47570e86434b8a2ddeef9895374e3dcf9dc9d2acb508a` | `b57b41e2b9422d3b6006edae93118163243b889cf513adda4cc5ad6c958fa933` | 16×16 → 64×64 | 199 → 11955 B |
| `ossified_flesh_1.png` | `d9a85e4d0d989f834f40c39a8ce10f79baff199a46f62372cae579ebf1ad20e4` | `bc11765e95b1a4934091c8fed760210f1bcaab904ae60c95cd98ce78aee9ef71` | 16×16 → 64×64 | 258 → 11160 B |
| `ossified_flesh_2.png` | `2bc319744a9d18afd3038d32695674641aeafce1916c8836b50c4f91a4238737` | `6182c7ad92f68220fddf0c5e320735a34fba696917233a922ce39e81f1d14724` | 16×16 → 64×64 | 287 → 12395 B |
| `ossified_flesh_3.png` | `0a12711e0aa4f7fc8c0ecb1fe2c442d815ea7b0c99429dfe33a871dc344c0a1a` | `fa79003ea18f6119f10d006813005200e8b70542e7e2a3d2ccbca5f5bfe3e81f` | 16×16 → 64×64 | 258 → 11147 B |

## Сплошная сверка пяти принятых партий

Для каждой принятой партии проверены все PNG в каталоге game assets (`assets/carnis/textures`), по полному пути и SHA-256. Preview/diagnostic PNG не являются игровыми текстурами и исключены.

| Партия | Источник | Проверено | Статус |
|---|---|---:|---|
| p1 | `Carnis_3.4.10_horror_blocks_p1.zip` | 16/16 | все «перенесён» |
| p2 | `Carnis_3.4.10_horror_items_p2.zip` | 8/8 | все «перенесён» |
| p3 | `Carnis_3.5.0_horror_items_p3.zip` | 4/4 | все «перенесён» |
| p4 | `Carnis_3.5.0_horror_tools_p4.zip` | 3/3 | все «перенесён» |
| p5 | `Carnis_3.5.1-R_horror_weapons_p5.zip` | 3/3 | все «перенесён» |

Итого: **34/34 игровых текстур совпадают побайтно** с пятью принятыми поставками. p4 и p5 также повторно сверены в R4, не только унаследованы из R3.

Gate A 35 (`Gate_A_35_block_textures.zip`) исключён намеренно: пакет не принят к слиянию; его текстуры не переносились.

## Проверки поставки

- В ZIP **755 файлов**, пути уникальны; встроенный `MANIFEST.txt` обновлён.
- Внешний SHA-256 manifest — 755 записей; после распаковки `sha256sum -c`: **755/755 OK**.
- Diff R3 → R4: только 16 указанных PNG; внутренний path-only `MANIFEST.txt` пересобран, его содержимое (список путей) идентично. **JSON и Java не менялись** (diff — 0 файлов).
- Java dump сохранён без изменений: 228 уникальных секций.
- Число ZIP members не изменилось. Новые пути не создавались, существующие текстуры заменены на месте.

Пересдача **3.5.1-R4**; версия мода — **3.5.1**.
