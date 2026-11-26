## Твоя задача сейчас

**Пакет 3.7.3** — 9 игровых call sites внесены; `sound_orphans` code 0, alias 5/5, allowlist 4/4. Integrator accepted permanent ZIP `052c2e0c…` (`4c1eea9`: 54 checks, 0 failures, code 0). Reviewer `9967fef` volume review is being reconciled against source: detail playback passes 0.30F via `level.playLocalSound`, spread/shock pass 0.65F/0.8F. **T-3184/K3** remains open for API confirmation/Java compile of `CREEPER_RUPTURE` hook and reviewer follow-up. Java17/Gradle unavailable; javac11 only. C19 remains blocked until approved 3.8.0 scaffold/start base appears.

## План на версии вперёд — отмечаю сам

Полный текст шагов и критерии: `00-board/ROADMAP_koder.md`, раздел «ТВОЙ ПЛАН НА ВЕРСИИ ВПЕРЁД».

- [x] **K1** — 2026-11-20: после банка T-3188 `9ea5c82` и T-3186 пересобран 761-файловый ZIP, SHA `d392d604…`; 144/144 OGG==банк, отчёт `coder_373_build.md`.
- [x] **K2** — 2026-11-20: `incubation_cyst.png` восстановлен до SHA `7d30ac39…` в заготовке.
- [ ] **K3** — 9 S17 points committed as `2c338af`; `sound_orphans` code 0, alias 5/5, allowlist 4/4. `CREEPER_RUPTURE` moved to `ExplosionEvent.Detonate`, awaiting API confirmation and compile. ZIP `052c2e0c…` accepted by Integrator (`4c1eea9`, 54/0/code0). Reviewer volume finding `9967fef` conflicts with actual source/ZIP call paths; request exact path re-check. Source semantic compare vs snapshot `19c7e56` passes; local gate remains code1 only because independent sparse inputs absent. Java17/Gradle missing. Close K3 after API/compile and final Reviewer review; do not build JAR.

- [ ] **K4** — заблокирован: нет финальной принятой базы 3.7.3.
- [ ] **K5** — зависит от K4 и сдач Художника/Звука.
- [ ] **K6** — зависит от K4–K5 и acceptance gate.
- [x] **K7** — 2026-11-20: шаблон процесса заготовки создан в `00-board/reports/coder_release_scaffold_template.md`.
- [ ] **K8** — чек-лист требует финального пакета/спецификации; актуальная инструкция Кодера запрещает сейчас менять `07-project/`.
- [ ] **K9** — жду согласованную точку интеграции от владельца `tools/` / `.github/`.
- [x] **K10** — побайтовое копирование использовано; аудио не перекодировалось.
- [x] **K11** — JAR не собирался; правило отдельного разрешения соблюдено.
- [x] **K12** — 2026-11-20: активный recovery workspace `/home/user/carnis-wave29-recovery` занимает 70 MB (<128 MB; `du -sh`); повторный поиск `build/tmp`, `.gradle`, `__pycache__`, `tmp`, `temp`, `*.log`, `*.tmp` не нашёл временного мусора. Чистить нечего. Исходную копию `/home/user/carnis-wave29` (ранее 168 MB) не менял; Git storage, stash и deliverables не трогал. Основание и ограничения — `00-board/agents/coder.md`.

**Правило:** берёшь первый невыполненный шаг → доводишь → ставишь `[x]` + дата + одна строка факта → коммит + push → следующий. Не ждёшь волну. Шаг, которому нужен чужой код, — оставь `[ ]` с пометкой «жду» и возьми следующий.

## Волна 52 · 3.8.0

Текст: `00-board/ROADMAP_coder.md`, раздел «ВОЛНА 52».

- [ ] **C13** — регистрация 33 существ в коде
- [ ] **C14** — анимационные контроллеры
- [ ] **C15** — 132 события звука + ModSounds
- [ ] **C16** — репликация 33 существ
- [ ] **C17** — сборочная проверка + список .java
- [ ] **C18** — отчёт coder_380_build.md

**Резерв нумерации волны 58:** C100–C115 — **зарезервированы за волной 58**.
Свою нумерацию продолжай с **C19**; диапазон C100–C115 — **не брать**.

## Волна 58 · библиотеки Директора (C100…R102)

Текст: `00-board/ROADMAP_<роль>.md`, раздел «ВОЛНА 58».

- [ ] **C100** — Curios: слоты + регистрация
- [ ] **C101** — предметы ICurioItem (шлем/респиратор/баллон)
- [ ] **C102** — сохранение при смерти — вещь не выпадает
- [ ] **C103** — требования к установке: Curios на сервере
- [ ] **C104** — Patchouli: каркас журнала
- [ ] **C105** — каталог глав и страниц — JSON, без GUI
- [ ] **C106** — проверка: журнал листается
- [ ] **C107** — SmartBrainLib: пилот на 2 существах
- [ ] **C108** — замер TPS/поведения/JAR до и после
- [ ] **C109** — Lodestone: первый эффект — Screen Shake
- [ ] **C110** — замер FPS на каждый эффект
- [ ] **C111** — Sound Physics: soft dependency, без копирования кода
- [ ] **C112** — никогда не required
- [ ] **C113** — build.gradle: все зависимости мягко, сборка без них
- [ ] **C114** — README: требования + лицензии
- [ ] **C115** — список изменённых .java в отчёте
**Доступность C100…C115:** в текущем checkout `01-coder/` есть только 3.7.2/3.7.3, scaffolding исходников 3.8.0/3.9.0 отсутствует. Все библиотечные задачи привязаны к будущим версиям; не вносить зависимости в 3.7.x. Начать C100 можно после появления/создания одобренного 3.8.0 scaffold.

