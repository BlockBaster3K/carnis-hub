# Кодер · T-3184 — аудит 11 недостижимых ModSounds

**Статус:** аудит источника выполнен; исправление кода **не завершено**. В текущем исходнике подтверждено 0/11 call sites. До реализации требуется согласовать звукоряд/точки вызова и разрешённую файловую дельту.

## Фактическая проверка

Просканированы все 228 `.java` в доступном исходнике `01-coder/3.7.3/src/main/java`, исключая декларации `ModSounds.java`. Все 11 констант объявлены, но ни одна нигде больше не упоминается. При этом каталог `07-project/` в checkout содержит документацию и старые архивы, Java-исходников там нет; фактическая копия Java проекта находится в scaffold 3.7.3.

| Константа / событие | Декларация | Call sites вне `ModSounds.java` | Возможный реальный триггер (не внесён) |
|---|---|---:|---|
| `FLAMETHROWER_FIRE` / `flamethrower_fire` | `ModSounds.java:22` | 0 | Длительный огонь Bio Purifier; нужен выбор между этим событием и текущим `PURIFIER_LOOP`. |
| `AMALGAM_SMASH` / `amalgam_smash` | `:23` | 0 | Успешный обычный melee-hit Flesh Amalgam (`FleshAmalgamEntity.doHurtTarget`). |
| `SYNAPSE_SHOCK` / `synapse_shock` | `:44` | 0 | Переход Synapse Node из неактивного состояния в активное; сейчас есть отдельный периодический `SYNAPSE_NODE_PULSE`. |
| `HIVE_SPREAD` / `hive.spread` | `:88` | 0 | Успешное размещение новой vein в `VeinMutationEngine.spread`. |
| `HIVE_DETAIL_FLOW` / `hive.detail_flow` | `:101` | 0 | Hive-ambient one-shot. |
| `HIVE_DETAIL_MEMBRANE` / `hive.detail_membrane` | `:103` | 0 | Hive-ambient one-shot. |
| `HIVE_DETAIL_BUBBLES` / `hive.detail_bubbles` | `:105` | 0 | Hive-ambient one-shot. |
| `HIVE_DETAIL_CREAK` / `hive.detail_creak` | `:107` | 0 | Hive-ambient one-shot. |
| `HIVE_DETAIL_SCUTTLE` / `hive.detail_scuttle` | `:109` | 0 | Hive-ambient one-shot. |
| `CREEPER_RUPTURE` / `creeper_rupture` | `:143` | 0 | Взрыв Infected Creeper; сейчас отдельно звучит fuse warning `HIVE_SPAWN_CREEPER_DETONATE`. |
| `FLESH_AMALGAM_AMBIENT` / `flesh_amalgam_ambient` | `:158` | 0 | Ambient Flesh Amalgam; его `getAmbientSound()` сейчас возвращает `HIVE_AMALGAM_BREATH`, который ссылается на тот же ресурс. |

## Почему код пока не менялся

1. У пяти `hive.detail_*` нет найденного решения Sound о размещении в ambient. Контекстом установлен запрет менять ambient/one-shot `hive.pulse` без предварительной сверки с владельцем. В `ROADMAP_sound.md`/решениях доски отдельного одобрения для этих пяти событий нет. Поэтому не менял `HiveAmbientSoundHandler` и не трогал `hive.pulse`.
2. Для `flamethrower_fire` в коде нет отдельного flamethrower; наиболее близок Bio Purifier, у которого уже есть `PURIFIER_IGNITE`/`PURIFIER_LOOP`. Замена или наложение звука меняет дизайн.
3. Для `flesh_amalgam_ambient` нужно решить, использовать ли дублирующее событие вместо `HIVE_AMALGAM_BREATH` либо чередовать события; обе записи указывают на один ресурс. Удаление требует согласования с Sound.
4. Правило приёмки 3.7.3 сейчас требует строго ограниченную delta. Внесение Java-файлов изменит перечень дельты пакета; прежде чем включать код, Архитектор/Ревизор должны согласовать обновлённый allowlist и чекер `verify_373_delta.py`.

Оставшиеся 5 прямых кандидатов выше также не внесены до согласования поведения и аудио-частоты; никаких файлов `.ogg` или регистраций не удалял.

**Итог:** подтверждено **0/11 вызываемых**, **11/11 зарегистрированных**; ни одно событие не удалялось. Для закрытия T-3184 требуется разрешение/решение по точкам вызова и обновлённой файловой дельте. После этого таблица должна быть дополнена конкретными `файл:строка` и итогом `11/11`.
