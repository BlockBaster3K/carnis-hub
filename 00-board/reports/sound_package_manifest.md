# Манифест актуальности звука в пакете 3.7.2

**Роль:** Звук · **Дата:** 2026-11-26 · **Проверено на:** origin `b3f36dd`
**Статус:** ✅ **расхождений нет** — актуальная версия на момент проверки

---

## 1. Результат проверки

| Показатель | Значение |
|---|---|
| `.ogg` в `01-coder/3.7.2/` | **144** |
| совпадают с банком `03-sound/sounds/` побайтово | **144** |
| **устаревших** | **0** |

Сверка sha256 каждого `.ogg` в пакете с банком, `origin b3f36dd`.
Кодер подтянул все 18 файлов из моих правок T-3121 / T-3128 / T-3140 —
список больше не нужен как задание, но оставлен ниже как **контрольный эталон**:
если при следующей сборке эти 18 разойдутся с банком снова, значит файлы
откатились к старым версиям.

**Отдельно проверено:** банк в origin тоже в норме — 18/18 файлов держат
запас peak ≥ 0.20 дБ (7 файлов) и RMS ≥ −30 dBFS (11 файлов).

---

## 2. Контрольные 18 файлов (эталон на будущее)

| Файл | норма | из задачи |
|---|---|---|
| `block/hive_block_break_01_tear.ogg` | peak ≤ −1.20 dBFS (запас ≥ 0.20) | T-3140 |
| `block/hive_block_break_02_pop.ogg` | peak ≤ −1.20 dBFS (запас ≥ 0.20) | T-3140 |
| `block/hive_block_break_03_crunch.ogg` | peak ≤ −1.20 dBFS (запас ≥ 0.20) | T-3140 |
| `combat/combat_flesh_hit_deep_02_crit.ogg` | peak ≤ −1.20 dBFS (запас ≥ 0.20) | T-3140 |
| `combat/combat_flesh_hit_deep_03_blast.ogg` | peak ≤ −1.20 dBFS (запас ≥ 0.20) | T-3140 |
| `hive/hive_spawn_attack_04.ogg` | peak ≤ −1.20 dBFS (запас ≥ 0.20) | T-3140 |
| `hive/hive_spawn_hurt_02.ogg` | peak ≤ −1.20 dBFS (запас ≥ 0.20) | T-3140 |
| `hive/detail_flow_02.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |
| `hive/detail_membrane_01.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |
| `hive/detail_scuttle_01.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |
| `hive/detail_bubbles_01.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |
| `hive/hive_spread_02_pulse.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |
| `hive/hive_spread_01_creep.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |
| `hive/hive_spread_03_swell.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |
| `hive/detail_creak_01.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |
| `hive/hive_spawn_idle_03.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |
| `hive/hive_spawn_idle_02.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |
| `hive/hive_spawn_idle_04.ogg` | RMS ≥ −30 dBFS, пик ≤ −1.00 | T-3128 |

**sha256 эталона (из банка `03-sound/sounds/`):**

```
03-sound/sounds/block/hive_block_break_01_tear.ogg  51a6f4ca99249babf11f71d2e7d0ce43925b7af5551838b5ee731791a64f361b
03-sound/sounds/block/hive_block_break_02_pop.ogg  da762cf13969818f721b850d073110f6ca4243d40df516d409c10547034870b2
03-sound/sounds/block/hive_block_break_03_crunch.ogg  f9263825841c8a9ee30880772046dc459f79144b9d77e30569c1bdec0d347e11
03-sound/sounds/combat/combat_flesh_hit_deep_02_crit.ogg  13e239e80d1fa0323d5e4f8018dac2dd2d392c2720951dbcf43b55eb644ead72
03-sound/sounds/combat/combat_flesh_hit_deep_03_blast.ogg  daa12edff0900c07147c7db5846b77d215cdfcd64c9dd28f995e13572e80b5f9
03-sound/sounds/hive/hive_spawn_attack_04.ogg  c595c18fc2cdab3f3d7891c305d1cdcc2fa86d64673f4d97a8ab3b0082ff0e78
03-sound/sounds/hive/hive_spawn_hurt_02.ogg  658d5145a11716af0497a63f3a577f68d8249012cfd7f4a2a68b165fa64d1753
03-sound/sounds/hive/detail_flow_02.ogg  4c506b8560171bbbb945e0a4c43038c6daf1b17ce7bbd9cc10fa6038b37154a0
03-sound/sounds/hive/detail_membrane_01.ogg  6c53d1b846c883627e32fb6b2d52f229d3558dda4c90449411ddbe52a8257fd1
03-sound/sounds/hive/detail_scuttle_01.ogg  763462276110cb39175b162e4bab70be7826cba4bba5c269327e101b1d353fde
03-sound/sounds/hive/detail_bubbles_01.ogg  5f1c469eba59fb5b5686e01fbf4d733cfa4494a3062767cfac2bea52e892aa04
03-sound/sounds/hive/hive_spread_02_pulse.ogg  ba82f7202413b79a48968ebc08ae4bf91cf047c58f8edacb49c26bdebd93bf02
03-sound/sounds/hive/hive_spread_01_creep.ogg  cf214ce8d38b4e59df92fc63a36633772a3c3f5905de4ae473ba86399ac39425
03-sound/sounds/hive/hive_spread_03_swell.ogg  417cdb0ffa7ecc940dd35c7dd106246f3a082f1328d08750a2b162b4ff48823c
03-sound/sounds/hive/detail_creak_01.ogg  9d64dd252b4611faca6f07f2f72b158d35acfdcbbc0c2840a1cf14f23dcc092b
03-sound/sounds/hive/hive_spawn_idle_03.ogg  63eacbb38a7c58146c0a5fac4f15291eb571e2ae1932deed1b85830c0c910867
03-sound/sounds/hive/hive_spawn_idle_02.ogg  d74b5c86de544018824d311647916acff7ca573db3a2901977620427d5c13051
03-sound/sounds/hive/hive_spawn_idle_04.ogg  e5f5dbdd9d2cc76d275bc5f5c911637979f718af083394ca8c2d7e2e4922567b
```

---

## 3. ⚠️ Найденный дефект гейта (актуален независимо от 3.7.2)

Прогон `tools/accept_3.7.2.py` на фактическом ZIP (когда ZIP ещё был в `01-coder/3.7.2/`):

```
13) Банк — формат и клиппинг (ТЗ 3.7.2 §9)
  ✓ банк: .ogg 144, неверный формат 0, пустых 0
  · клиппинг: 144 файлов не декодированы      ← уровни НЕ проверены
```
Блок 13 проверяет формат (моно / 44.1 кГц / не пустой), но **не уровни**:
декодера в окружении гейта нет, поэтому норма «peak ≤ −1 dBFS» и подъём тихих
файлов **не проверяются вовсе** — печатается «не декодированы» и проверка идёт дальше.

**Следствие:** пакет со старыми пиками −0.77…−0.97 dBFS и тихими файлами
−31…−33 dBFS прошёл бы гейт с тем же результатом, что и правильный.
Именно так и было в ZIP от `73ec066`: 18 файлов устарели, а гейт молчал.

**Что нужно:** либо побайтовая сверка `.ogg` пакета с банком в гейте
(простой sha256, декодер не требуется), либо декодер в окружении CI.
Это зона Интегратора/Ревизора — я только фиксирую.

## 4. Что я не делал

`.ogg` в пакете **не менял** — `01-coder/` зона Кодера, копирование побайтово
из банка его работа (Р-31.6). На момент проверки делать было нечего: всё совпадает.
