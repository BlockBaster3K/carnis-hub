# Carnis 3.8.1 — требования к установке

**Обновлено:** 2026-11-20 · **Пакет:** `01-coder/3.8.1/project-3.8.1-clean.zip` · **SHA-256:** `921f5cc1ff0f667f5a6ebb942c30b114caeccc7a4acffd939aa7fc5cb110a7ad`

## Кратко

| Компонент | Требование | Сторона |
|---|---|---|
| Minecraft | 1.20.1 | клиент + сервер |
| Forge | 47.1.0+ | клиент + сервер |
| GeckoLib | 4.4.4+, **обязателен** | клиент + сервер |
| Java | 17 | сервер/клиент |
| Curios | **необязателен для запуска Carnis**; нужен для accessory slots | клиент + сервер для этих слотов |
| Patchouli, SmartBrainLib, Lodestone, Sound Physics Remastered | не требуются; не добавлены в 3.8.0 | — |

Установка Curios — **feature-specific**, а не hard requirement: без него Carnis должен запускаться как обычно, но слот-функции Curios недоступны. Чтобы использовать Curios inventory/слоты, Curios должен быть установлен и на клиенте, и на сервере.

## Машиночитаемые требования

`tools/deps_install_check.py` сравнивает этот блок с `mods.toml` пакета. Curios намеренно остаётся `not-required`: его запись имеет `mandatory=false`.

```
forge: required
minecraft: required
geckolib: required
curios: not-required
patchouli: not-required
smartbrainlib: not-required
lodestone: not-required
soundphysics: not-required
```

## Что объявлено в пакете

`mods.toml` объявляет Forge, Minecraft и GeckoLib как обязательные; Curios объявлен `mandatory=false` с порядком `AFTER`. В `build.gradle` Curios API подключён как `compileOnly`, а сам мод — как `runtimeOnly`; это не включает Curios JAR внутрь Carnis и не требует его для загрузки игры.

Лицензия Curios API: **LGPL-3.0-or-later**. В пакет Carnis сторонний Curios JAR не встраивается.

Patchouli, SmartBrainLib, Lodestone и Sound Physics Remastered в `build.gradle`/`mods.toml` 3.8.0 не добавлены. Единственная жёсткая библиотечная зависимость — GeckoLib.

## Статус функции Curios

В этом обновлении зарегистрированы слоты `head` и `back`, если Curios присутствует. Предметы-аксессуары (`neuro_helmet`, `respirator`, `flame_tank`) и защита от выпадения при смерти ещё не включены: это C101/C102, поэтому не следует считать их доступными в текущем пакете.

## Проверка

```bash
python3 tools/deps_install_check.py 01-coder/3.8.1/project-3.8.1-clean.zip
python3 tools/deps_soft_check.py 01-coder/3.8.1/project-3.8.1-clean.zip
```

Обе проверки сверяют требования по содержимому пакета, а не по одному этому отчёту.
