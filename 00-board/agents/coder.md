# Coder — статус

задача: **ПЛАН НА ВЕРСИИ ВПЕРЁД** — список и критерии в `00-board/ROADMAP_koder.md`, раздел «ТВОЙ ПЛАН НА ВЕРСИИ ВПЕРЁД». **K1 выполнен; продолжай с первого доступного незакрытого шага**. Отмечаешь сам: `[ ]` → `[x]` + дата + факт, в этом же файле.
**ВОЛНА 58 (C100…C115) — ПЯТЬ БИБЛИОТЕК ДИРЕКТОРА, все утверждены.**
Ответы и факты — `.workflow/DIRECTOR_INBOX.md` («ОТВЕТ НА: [25.11.2026] …»).
Проверено: Curios (LGPL-3.0, 1.20.1), Patchouli (CC-BY-NC-SA, 1.20.1),
SmartBrainLib (MPL-2.0, **7 версий для Forge 1.20.1**), Lodestone (LGPLv3,
1.20.1), Sound Physics Remastered (GPL-3.0, 1.20.1).

**Все зависимости — МЯГКИЕ (`compileOnly`/`runtimeOnly`): мод обязан работать
без них.** Ни одна не `required`, ни одна не попадает в 3.7.x.

**Начинай с C100** (Curios: слоты + **сохранение при смерти — по умолчанию
Curios роняет вещи, это чинится сразу**) → C104 (Patchouli: каркас журнала) →
C113–C115 (gradle, README, список `.java`) → C107 (пилот SmartBrainLib на
**2 существах** с замером TPS) → C109 (Lodestone: Screen Shake) → C111 (Sound
Physics: мягко).

---
### Исходное задание T-3184 на момент передачи Кодеру (исторический baseline до S17 call sites)

`tools/sound_orphans.py` на кандидате: **allowlist работает**
(`FLAMETHROWER_FIRE` — задел, гейт его не валит), сирот 0, ссылок в пустоту
0, недостижимых **9**. Привяжи их (карта `00-board/reports/sound_unreachable_map.md`,
таблица с ключами и уровнями — в `T-3202` в `.workflow/TASK_BOARD.md`):
`AMALGAM_SMASH` → `FleshAmalgamEntity.doHurtTarget` 1.0 · `SYNAPSE_SHOCK` →
переход узла в активное 0.8 · `HIVE_SPREAD` → успешное разрастание 0.65 ·
`HIVE_DETAIL_FLOW/MEMBRANE/BUBBLES/CREAK/SCUTTLE` → детали по зонам 0.30 ·
`CREEPER_RUPTURE` → смерть крипера 1.0. **Не трогай** `FLAMETHROWER_FIRE` и
`FLESH_AMALGAM_AMBIENT`. Потом — пересборка 3.7.3, гейт ожидается **код 0**;
затем **C13** (33 существа) и вставка **132** событий звука.

---
1. **Привязка 9 событий** по карте `00-board/reports/sound_unreachable_map.md`
   (S17): `AMALGAM_SMASH` → `FleshAmalgamEntity.doHurtTarget`, **volume 1.0**;
   `SYNAPSE_SHOCK` → переход узла в активное, **0.8**; `HIVE_SPREAD` (3 файла)
   → успешное разрастание, **0.65**; `HIVE_DETAIL_*` (5 файлов) → детали по
   зонам, **0.30**; `CREEPER_RUPTURE` → смерть крипера, **1.0**.
   `FLAMETHROWER_FIRE` — **сознательный задел** (allowlist гейта, З-26), не
   трогай. `FLESH_AMALGAM_AMBIENT` — жив через общий ключ, не трогай.
2. **Вставка 132 событий** в `sounds.json` + `ModSounds` — готовый фрагмент
   Звука: `03-sound/3.8.0/sounds_json_infected_33.json`.
3. **Пересборка 3.7.3** → гейт: ожидается **код 0**.
Затем — **C13**: регистрация **33 существ** в коде (`EntityType`, атрибуты,
Geckolib-рендер, спавн-яйцо), репликация, список изменённых `.java` в отчёте.

---


**РЕГРЕСС З-16 В ЗАГОТОВКЕ 3.7.3 (нашёл Ревизор, подтвердил) — исправить:**
в `01-coder/3.7.3/` лежит **старая** `textures/block/incubation_cyst.png`.
Верни туда **побайтово** сдачу T-3141 — sha256 `7d30ac39dcf8b606d9a79c8e579fd6c10a14de2d1989fd8a021175a04916ab66`
(7 цветов, 14,5 % топа). Иначе 3.7.3 унаследует ровно тот дефект, который
закрыли З-16 в 3.7.2.

**T-3182 / K1 — статус после сдачи Sound:** обновлённый банк З-21 с 15 файлами сдан в `dc597f0` (Δcrest ≤ 0,05 дБ, пик ≤ −1,20 dBFS, запас ≥ 0,20 дБ, длины точные, клиппинг 0). Маска T-3186 также внесена. Кандидатный ZIP/manifest пересобраны; см. актуальное дополнение `00-board/reports/coder_373_build.md`. Это **не финальная приёмка**: остаются T-3184 и проверки gate.

завершено: **T-3171 · Пересборка 3.7.2 из текущего банка (дельта 15 .ogg)** — отчёт `00-board/reports/coder_372_rebuild.md`

**ПОДТВЕРЖДЕНО АРХИТЕКТОРОМ (T-3174):** отставание банка по нормам не блокер (старые файлы пик ≤ −1.05 dBFS, длины точные, клиппинг 0), но пакет 3.7.2 должен совпадать с банком 144/144: дельта ровно 15 `.ogg`, остальные 744 побайтово как были. 3.7.1 остаётся выпущенным, перевыпускать не нужно.
STATUS: BLOCKED — T-3184/K3: девять S17 call sites закоммичены в `2c338af`; `sound_orphans` 0, alias 5/5, allowlist 4/4. По S70 исправлен единственный volume mismatch: `hive.detail_flow_01` в `sounds.json` 1.5→1.0, pitch 0.95 сохранён; `volume_effective_check.py` теперь 9/9, код 0. Новый кандидат ZIP SHA `c7d78254…`, 761 записей; локальный полный `accept_3.7.3.py` всё ещё code 1 из-за недостающих независимых baseline/overlay/bank/crest inputs в sparse checkout. Это не финальная приёмка. `CREEPER_RUPTURE` в серверном `ExplosionEvent.Detonate` hook ещё ждёт API confirmation и Java compile; доступен только JDK 11, Gradle wrapper отсутствует. `.jar` без отдельной команды не собирать.
Следующие шаги T-3184: hook API confirmation, JDK17/Gradle compile, затем Java compile и полный delta + acceptance gate на доступных независимых inputs. `HIVE_SPREAD` срабатывает только после успешной vein placement; cooldown без игрового замера не менять.

**Следующая задача по Roadmap — C100 (Curios, 3.8.0), статус BLOCKED:** текущая ветка содержит заготовки только до `01-coder/3.7.3`; scaffold 3.8.0 и исходники/результаты C13–C18 не предоставлены. Не создаю новую версию копированием без согласованной стартовой базы. `жду: Архитектор — предоставить или утвердить scaffold 3.8.0 и стартовую базу C100.` Зависимость не вносить в 3.7.x.
После последнего sync workspace составляет 218 MB (`.git` 182 MB; дерево вне Git около 36 MB). Внутри workspace не обнаружено `build/tmp`, `.gradle`, `__pycache__`, логов или временных архивов; ZIP-файлы — только сохранённые deliverables. Свежих безопасных кандидатов на удаление нет. Лимит <128 MB не достигнут: нужен Architect decision по Git storage; pack/объекты, stash и deliverables не трогал.

обновлено: после pull до `ae0e697`; source implementation T-3202 запушена как `2c338af`; текущие ZIP/manifest пересобраны: 761/761, SHA `d19169b4…`, package `sound_orphans` код 0. Alias 5/5, allowlist 4/4. Full gate не запускался (нет независимых входов), Java compile не выполнялся; workspace около 203 MB после ZIP update (`.git` 156 MB).

завершено:
- T-3164: `07-project/TEST_3.7.1.md` сверен с принятым ZIP `7ca6bdb8…`; ambient gate подтвердил 450 тиков / 22.50 с, паузу 9.10 с, pitch 1.0, сумму уровней 0.6975 и loop lengths 120.000 с. Чек-лист обновлён.
- T-3164: создан scaffold `01-coder/3.7.3/` (760 файлов: 759 проектных + MANIFEST), версия 3.7.3 в четырёх местах. 12 PNG T-3152 внесены побайтово, 3 PNG белого списка T-3142 сверены с T-3115. ZIP не собирался по ТЗ. Отчёт `00-board/reports/coder_373_scaffold.md`.
- T-3166: исправлена `incubation_cyst.png` в 3.7.2 побайтово (7 цветов, топ 14,5%); ZIP 12 612 015 Б, SHA-256 `c271d30af7b6b6d83c4dcf68dbc08ab2e999e674ea53895070582056fa4e9989`, манифест 759/759; `accept_3.7.2.py` — код 0. Отчёт `00-board/reports/coder_372_z16_fix.md`.
- T-3171: заменены ровно 15 OGG по текущему банку; 144/144 совпадают с банком, остальные 744 файла без изменений. ZIP 12 605 693 Б, SHA-256 `362bdda2e3aaa0a9450fdf6bb6bede014af612d1efd92cf84ab0e074b8ccab63`; `accept_3.7.2.py` — код 0. Отчёт `00-board/reports/coder_372_rebuild.md`.
- T-3143: пакет 3.7.1 принят, 144/144 OGG совпадают с банком, manifest 759/759, гейт код 0; ZIP SHA-256 `7ca6bdb8eaea281b6315545efceaafe4106d1bc53232af25fe2d9d360181558b`.
- T-3137 / T-3156: пакет 3.7.2 принят актуальным гейтом, 144/144 OGG == банк, manifest 759/759, код 0; ZIP SHA-256 `e65c017dc8ce9b816440632198f323b19b482f7e3df37cdac7f3de689f7e53ea`. Белый список проверен в обе стороны.
- T-3154: обновлён `07-project/TEST_3.7.2.md` с численными критериями, включая сравнение `cerebral_nexus` / `hive_sentinel`.

Отчёты: `00-board/reports/coder_371_final_rebuild.md`, `00-board/reports/coder_372_assembly.md`, `00-board/reports/coder_373_scaffold.md`, `00-board/reports/coder_372_z16_fix.md`, `00-board/reports/coder_372_rebuild.md`.

T-3171 завершена. По T-3177 после сдачи Sound собран новый кандидат 3.7.3; ZIP и manifest не приняты, gate остаётся с кодом 1 из-за T-3184. Публикация, тег и release Кодером не выполнялись.


**T-3184 — состояние после upstream `5b2c321` и fix `7b9655f`:** девять игровых точек внесены; локальный `sound_orphans.py` проходит (код 0; `FLESH_AMALGAM_AMBIENT` покрыт через `hive.amalgam_breath`, `FLAMETHROWER_FIRE` — единственный задел). Alias regression 5/5 (R15 dead-alias fail-open covered and patched), allowlist boundary 4/4. S24/R18 reports подтверждают разделение банка и неизменность 144 канонических OGG; I20 report фиксирует гейты по версионным каталогам. Файлы банка не материализованы sparse checkout, ZIP/manifest старые, новый acceptance и Java-компиляция не выполнялись. `CREEPER_RUPTURE` hook ждёт API confirmation. Отдельный тест allowlist закоммичен/запушен; JDK17/Gradle нет, `.jar` не собирался.


**Исторический пакет `dcff18d2` заменён кандидатом после Sound `dc597f0`, затем пересобран после T-3188.**
Текущий ZIP: `d392d604…`, 144/144 OGG совпадают с очищенным банком; независимый delta-checker код 0.
Не объявлять финальным: acceptance gate даёт код 1 только из-за 11 недостижимых событий
T-3184; все прочие блоки прошли при временно восстановленных sparse-checkout источниках.
См. `coder_373_build.md`. K4/K8 зависят от принятия пакета/спецификации.

---


**T-3188 — часть Кодера выполнена:** после выноса 14 `*_w1516.ogg` из банка коммитом Sound `9ea5c82` пересобран пакет 3.7.3; банк = пакет 144/144, crest 15/15, manifest OK. Новый SHA ZIP `d392d604…`. Gate прошёл все блоки кроме T-3184 (11 недостижимых событий); полный результат — в `coder_373_build.md`.

---


**РЕШЕНИЕ АРХИТЕКТОРА (Т-3190) — ТЫ РАЗБЛОКИРОВАН:**

1. **11 ModSounds — ПРИВЯЗАТЬ, не удалять.** 15 файлов озвучены, нормированы
   (З-21) и лежат в банке — это задел, удаление обнулило бы работу Звука и
   уронило инвариант «банк 144 == пакет 144». Звук даёт расшифровку по
   каждому (что за звук → к какому игровому моменту); ты **привязываешь** его
   к **реальному** вызову (`ServerLevel.playSound` / `level.playLocalSound`)
   в существующих местах кода модов. Звонков в пустоту быть не должно.
   Исключение — только те, что Звук пометит «удалить»: тогда удаляешь
   **целиком** — регистрацию `ModSounds` + файл из банка + строки манифеста.
2. **Allowlist Java-дельты — РАЗРЕШЁН.** Пакет Forge-мода содержит 228 `.java`,
   дельта может включать Java-файлы. Требование: перечень изменённых `.java` —
   в отчёте `00-board/reports/coder_373_build.md` и в манифесте; гейт строго
   проверяет **ресурсы** (144/144 `.ogg`, PNG побайтово, манифест 761/761),
   Java-дельку — по списку, без требования «ни одного .java».
3. **После привязки** — пересборка 3.7.3 → Ревизор → вердикт. **Релиз и
   `.jar` — только по отдельной команде Архитектора.**

---


**ВОЛНА 52 — C13…C18** (`00-board/ROADMAP_koder.md`): регистрация **33 новых
существа** в коде (EntityType, атрибуты, Geckolib-рендер, спавн-яйцо), 132
новых события звука в `sounds.json` + `ModSounds`, репликация, сборочная
проверка и список изменённых `.java` в отчёте. Без этого геометрия 3.8.0 в
игру не попадёт.

---


**ПРИВЯЗКА 9 СОБЫТИЙ (карта Звука готова — `00-board/reports/sound_unreachable_map.md`,
S17):** Звук нашёл реальные точки вызова и обосновал уровни:
`AMALGAM_SMASH` — `FleshAmalgamEntity.doHurtTarget` → **volume 1.0**;
`SYNAPSE_SHOCK` — переход узла в активное состояние → **0.8**;
`HIVE_SPREAD` (3 файла) — успешное разрастание → **0.65**;
`HIVE_DETAIL_*` (5 файлов) — детали по зонам → **0.30**;
`CREEPER_RUPTURE` — смерть заражённого крипера → **1.0**.
Реализуй **ровно** эти точки и уровни. `FLAMETHROWER_FIRE` — **сознательный
задел** (механики огнемёта в коде нет): его в allowlist гейта (З-26), удалять
не надо. `FLESH_AMALGAM_AMBIENT` — жив через общий ключ, ничего не делай.
После привязки — пересборка 3.7.3 и гейт: ожидается **код 0**.

---

## Мой план — отмечаю сам

**Актуально:** K1 и K2 отмечены выполненными. K3 остаётся открыт по T-3184: Java hook ещё не компилировался, нужна API-подтверждённая проверка, свежие ZIP/manifest и полный acceptance на актуальных входах. K4/K8 пока зависят от принятия 3.7.3 и актуальной спецификации.

**Отмечаю сам** — `[ ]` → `[x]` + дата + факт. Список и критерии заданы в плане Кодера, разделе «ТВОЙ ПЛАН НА ВЕРСИИ ВПЕРЁД».

- [x] **K1** — 2026-11-20: после Sound `dc597f0`, чистки банка T-3188 (`9ea5c82`) и T-3186 пересобраны ZIP/manifest; SHA ZIP `d392d604…`, 761/761, 144/144 OGG==банк; отчёт `coder_373_build.md`.
- [x] **K2** — 2026-11-20: `incubation_cyst.png` восстановлен до `7d30ac39…`, commit `4c4632c`.
- [ ] **K3** — 9 игровых точек T-3184 внесены; `sound_orphans` code 0, alias 5/5, allowlist 4/4. `CREEPER_RUPTURE` hook перенесён в `ExplosionEvent.Detonate`, но ещё не скомпилирован и ждёт API confirmation. ZIP `052c2e0c…` принят Интегратором (54/0/code 0); Reviewer volume-path reconciliation ещё pending. Java17/Gradle нет. K3 закрыть после confirmation/compile и final Reviewer review; JAR не собирать.
- [ ] **K4** — заготовка 3.7.4. Жду финальную принятую базу 3.7.3; не дублирую сейчас тяжёлые ассеты и не превышаю лимит памяти.
- [ ] **K5** — сборка 3.7.4. Жду сдачи Художника и Звука.
- [ ] **K6** — манифест + гейт 3.7.4. Жду K4–K5 и гейт.
- [x] **K7** — 2026-11-20: повторяемый порядок заготовки описан в `00-board/reports/coder_release_scaffold_template.md`.
- [ ] **K8** — `07-project/TEST_3.7.3.md` уже существует из предыдущей сдачи, но не отмечаю завершённым: нужна сверка с финальным пакетом/спецификацией; в этом цикле `07-project/` не менял.
- [ ] **K9** — автопроверки в сборке. Жду согласованную точку интеграции; `tools/` и `.github/` — зона Интегратора.
- [x] **K10** — 2026-11-20: побайтовое копирование соблюдено; OGG не перекодировал; после T-3188 144/144 файлов пакета совпадают с очищенным банком.
- [x] **K11** — `.jar` не собирал; без отдельной команды Архитектора не собирать.
- [x→повторно открыт] **K12** — 2026-11-20 workspace был 116M после `git gc --prune=never`; после последующих pulls вырос, текущий замер после HEAD `0be643c`: 205 MB (`.git` 169 MB). Временный мусор в дереве не найден; удалены только тестовые логи `/tmp/final_{alias,allow,orphans}.log` и `tools/__pycache__`. ZIP-файлы — deliverables. До решения Архитектора `gc`/repack/удаление Git-объектов, stash или deliverables не выполнять; подробности в `coder_git_storage_architect_request.md`.

**План и прогресс (отмечаешь сам):** `00-board/agents/coder_plan.md` · первый шаг — `K1`.

## Последний цикл после pull до `0be643c` и нового acceptance report

- `git pull --rebase --autostash` выполнен; upstream добавил тест `tools/baseline_perfile_test.py`. Изменения владельца в `00-board/reports/koder_handshake.md` и `BACKLOG_3.6.0.md` сохранены и не включались в коммит.
- Удалены мои временные тестовые `/tmp/final_alias.log`, `/tmp/final_allow.log`, `/tmp/final_orphans.log` и `tools/__pycache__`; `build/`, `tmp/`, `temp/`, другие логи и временные ZIP не найдены. ZIP, найденные в проекте, являются сохранёнными deliverables и оставлены.
- Alias regression — **5/5**, allowlist regression — **4/4**; `py_compile` для acceptance gate, semantic checker и baseline per-file test прошёл. Запуск `baseline_perfile_test.py`: **11/12**, `test_valid_json_loads_records` не проходит, потому что sparse checkout не содержит `03-sound/baseline_master.json`; это зависимость Интегратора, не изменение кода Кодера. Это не заменяет Java-компиляцию или полный acceptance.
- Workspace **205 MB**, `.git` **169 MB**; лимит `<128 MB` не достигнут. Git pack занимает 152.56 MiB, garbage objects — 0. Четыре autostash refs сохранены; без решения Архитектора не удалял stash/объекты и не запускал repack/gc.
- После acceptance report `05a305a` pitch `hive.detail_flow` восстановлен к 0.95/1.05; ZIP SHA `052c2e0c…`, manifest 761/761. Integrator full gate `4c1eea9`: **54/0, code 0**. Reviewer `9967fef` заявляет volume mismatch, но фактические source+ZIP показывают direct detail `level.playLocalSound(...,0.30F...)`, spread/shock args 0.65F/0.8F; `forAmbientAddition` используется для pulse/stinger/heartbeat, не detail. JSON multipliers не добавлял во избежание double-scaling; попросил Reviewer сверить call sites. Source semantic compare против snapshot `19c7e56` passed.
- Текущие coder задачи остаются **BLOCKED, не IDLE**: K3/T-3184 — интеграторская приёмка ZIP прошла, но Java API confirmation/compile и независимый reviewer follow-up остаются; C19 — отсутствуют scaffold и стартовая база 3.8.0. Решения и blockers описаны в TASK_BOARD и workspace request.

## Цикл восстановления 2026-11-20 · T-3204 / K12

- `git pull --rebase --autostash origin arena/d474d740-carnis-hub` завершён успешно: `HEAD=811bc94660fdea81c8111f41ff8c12a725f247fa`, совпадает с remote.
- Проверена актуальная доска: T-3204 остаётся ASSIGNED; C100–C115 относятся к 3.8.0/3.9.0. Для первого шага C100 нет утверждённого 3.8.0 scaffold/стартовой базы; не создавал каталог из копии 3.7.x и не менял 3.7.x. Поэтому библиотечные задачи не выполнены и `IDLE_WAITING_TASK` не выставлен.
- K12 подтверждён для активного recovery workspace: `du -sh .` = **70 MB**, строго меньше 128 MB. Повторный поиск временных каталогов и файлов (`build/tmp`, `.gradle`, `__pycache__`, `tmp`, `temp`, `*.log`, `*.tmp`) ничего не нашёл; очищать было нечего. Исходный checkout не менялся; Git-объекты, stash и deliverables сохранены.
- Пять восстановленных локальных изменений (`koder_handshake.md`, `BACKLOG_3.6.0.md`, `agent_push.sh`, `secret_guard.sh`, `verify_ssh_roles.sh`) не затрагивались и не включались в этот статусный коммит.

## Architect prompt 3.8.0 blocker — update 2026-11-20

- Items 1–4: detail_flow_01 is 2.437 in 3.8.0 and 3.7.3; 3.7.3 ZIP rebuilt (761/761, SHA `5d3f015943612c9e8b3189025c5df49b0228bb5ee1bbda07a5fb517ea81012c9`); spec `targets_mode=effective`; Z-16 exact SHA verified.
- Item 5: postponed by follow-up Architect prompt; artist assets are not ready.
- Items 6–7: version resolves as 3.8.0 in all three requested locations. README and LICENSE are present in source and clean ZIP.
- Item 8: configured `Coder <coder@carnis.dev>`, fetched origin and rebased successfully to `b776f9b`. Staged C100 changes were stashed before rebase; applying the stash conflicted on upstream `gradle.properties` and `mods.toml`, so the stash remains preserved and unapplied. Requested sound fixes and package manifests are ready for commit/push. No Java compilation/JAR build.
- Validation: volume effective check 10/10 on both 3.8.0 and 3.7.3 ZIPs; volume double check code 0 on 3.7.3; both package manifests verified. 3.8.0 ZIP includes README/LICENSE and is CRC-clean.
- Full report: `00-board/reports/coder_prompt_380_blocker.md`. The push-triggered `build-jar` workflow targets every `01-coder/**` change; commit will use GitHub's `[skip ci]` marker to honor the explicit no-Java/no-JAR prohibition.
