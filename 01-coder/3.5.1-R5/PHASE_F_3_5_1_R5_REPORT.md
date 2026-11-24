# Carnis 3.5.1-R5 — synapse_node startup crash fix

## Изменение

Исправлена только регистрация `synapse_node` в `ModBlocks.java`: emission override теперь вычисляет свет из `SynapseNodeBlock.POWER` (`> 0 ? 15 : 0`). До этого `Properties.copy(Blocks.REDSTONE_LAMP)` переносил лямбду, читающую `LIT`, которого у блока нет. `SynapseNodeBlock` и `ModItems` не менялись.

`mod_version=3.5.1`. Сборка, Gradle, runtime и `runData` не запускались.

## Аудит всех `Properties.copy(...)` в `ModBlocks.java`

Проверены все 12 регистраций с источниками копирования, унаследованной emissive-функцией и state definition пользовательского блока. Вердикт относится к тому, читает ли emission lambda свойство, которое блок фактически объявляет.

| Блок | copy от | LightLevel / emission в Properties | Свойства блока | Вердикт |
|---|---|---|---|---|
| `tainted_sludge` | `WATER` | none / 0 | LiquidBlock: inherited LEVEL | safe: no state-dependent emission |
| `flesh_veins` | `GLOW_LICHEN` | fixed 7 | MultifaceBlock: six face flags | safe: constant, ignores face flags |
| `flesh_bulb` | `CRIMSON_ROOTS` | none / 0 | HANGING, PULSING | safe: no emission function |
| `sinew_spikes` | `STONE` | none / 0 | none (plain Block) | safe |
| `creeping_tendrils` | `LADDER` | none / 0 | LadderBlock: FACING, WATERLOGGED | safe: no emission function |
| `spore_sprout` | `STONE` | none / 0 | CLOSED | safe |
| `neural_moss` | `MOSS_CARPET` | none / 0 | none (CarpetBlock state) | safe |
| `charred_flesh` | `BASALT` | none / 0 | none (plain Block) | safe |
| `hive_membrane` | `RED_WOOL` | none / 0 | none (plain Block) | safe |
| `synapse_node` | `REDSTONE_LAMP` | state-dependent: LIT → 15/0; overridden to POWER → 15/0 | POWER | fixed: emission now reads declared POWER |
| `incubation_cyst` | `NETHER_WART_BLOCK` | none / 0; explicit fixed 2 overrides | none (plain Block) | safe: explicit constant |
| `purifier_lamp` | `LANTERN` | fixed 15; explicit fixed 15 overrides | none (plain Block) | safe: explicit constant |

Особо: у `synapse_node` единственная state-dependent функция из копируемых источников — `REDSTONE_LAMP` (`LIT`). После правки она перекрыта функцией по объявленному `POWER`. У `GLOW_LICHEN` и `LANTERN` emission постоянный и не читает состояние; у `purifier_lamp` он дополнительно задан константой. Остальные источники не дают state-dependent emission.

Проверены также явные световые функции, не относящиеся к `Properties.copy`: `pustule_cluster` читает объявленные `AGE` и `BURST`; `pulsing_heart` и `hive_eye` используют константы. Других несоответствий state property не найдено.

## Diff и поставка

| Проверка | Результат |
|---|---|
| `ModBlocks.java` SHA-256 до | `a0cceda3ec292a0981036dad9ee9098fd1e6b7727a7c1470cec7e4e242de29b7` |
| `ModBlocks.java` SHA-256 после | `1ce1d02a56953ad6950c30768f0f7ae4d5e0a0e9f651e2970c98ab0751cbf4c3` |
| Статический diff source tree | изменён только `src/main/java/com/carnis/mod/init/ModBlocks.java` |
| JSON / прочие Java | без изменений |
| ZIP members | 755 |
| Внешний manifest | 755 записей; `sha256sum -c` после распаковки — 755/755 OK |
| Java dump | 228 уникальных секций из 228 файлов |
| `ModItems` | **не менялся** |
| Сборка / datagen | не запускались |

Пересдача **3.5.1-R5**; версия мода остаётся **3.5.1**.
