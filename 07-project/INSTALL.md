# Carnis: Adaptive Hivemind — установка

Мод для **Minecraft Java Edition 1.20.1** (Forge).

## Что понадобится

| Что | Версия | Обязательно? |
|---|---|---|
| Minecraft Java Edition | **1.20.1** | да |
| Forge | **47.4.28** (или новее в ветке 47.x) | да |
| Geckolib | **4.4.4** (или новее) | **да** — без него мод не запустится |

Geckolib ставится отдельным модом — файл `geckolib-forge-4.4.4.jar` берётся с
[Modrinth](https://modrinth.com/mod/geckolib) или [CurseForge](https://www.curseforge.com/minecraft/mc-mods/geckolib).
Без него Minecraft покажет ошибку при запуске и выкинет из игры.

## Где скачать

Релизы на GitHub: **https://github.com/BlockBaster3K/carnis-hub/releases**

Нужен файл **`carnis-3.5.3.jar`** (12 597 741 Б) из релиза **v3.5.3**.
Скачивать из репозитория ZIP не нужно — нужен именно `.jar`.

## Установка

1. Установи Minecraft **1.20.1** и Forge **47.4.28** (обычный установщик, vanilla-профиль не трогаем).
2. Скачайте **Geckolib 4.4.4** и **carnis-3.5.3.jar**.
3. Положите **оба** `.jar` в папку `mods`:
   - **Windows** — `%appdata%\.minecraft\mods`
   - **Linux** — `~/.minecraft/mods`
   - **macOS** — `~/Library/Application Support/minecraft/mods`
4. Запустите профиль **Forge 1.20.1**.
5. В главном меню → «Моды» должен появиться **Carnis: Adaptive Hivemind**, версия **3.5.3**.

## Проверка, что всё встало

- В списке модов видно `Carnis: Adaptive Hivemind` и `Geckolib`, обе версии подсвечены зелёным.
- В игре найдите **Пульсирующее сердце** (луковица с живым мозгом) — оно бьётся и звучит.
- В инвентаре есть **Кодекс Карниса** — по нему читается журнал мода.

## Если не запускается

| Сообщение | Причина | Что делать |
|---|---|---|
| «Mods must be loaded: Geckolib» | не установлен Geckolib | поставьте Geckolib 4.4.4+ в ту же папку `mods` |
| «Mods loaded from incompatible Minecraft version» | не та версия игры | нужна строго 1.20.1 |
| «Incompatible mod set» / Forge не найден | запущен не Forge-профиль | запустите профиль Forge 1.20.1, не ванильный |
| Краш при входе в мир | не хватает памяти | в лаунчере выделите моду **не меньше 4 ГБ** |
| Мод есть в меню, но его нет в игре | старая копия jar | удалите старый `carnis-*.jar` из `mods` и оставьте только один |

## Версии

| Версия | Релиз | Состояние |
|---|---|---|
| **3.5.3** | `v3.5.3` | **текущая, актуальная** |
| 3.5.2 | `v3.5.2` | предыдущая, рабочая |
| 3.5.1 | `v3.5.1` | предыдущая, рабочая |

## Если нашли баг

Пишите сюда: **https://github.com/BlockBaster3K/carnis-hub/issues**
Обязательно приложите: версию Minecraft и Forge, версию Geckolib, версию мода
и лог из `logs/latest.log` (папка `.minecraft`).
