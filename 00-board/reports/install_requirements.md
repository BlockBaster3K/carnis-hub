# Carnis: требования к установке

**Дата:** 2026-11-26 · **Проверено на пакете:** `01-coder/3.7.3/project-3.7.3-clean.zip`
(sha256 `c7d782544708…`) · **Основание:** I100 (волна 58)

Документ собран **по содержимому пакета**, а не по тексту ТЗ. Каждое
утверждение ниже проверяемо командой, которая приведена рядом.

## 1. Короткая версия

| что | нужно |
|---|---|
| Minecraft | **1.20.1** |
| Forge | **47.1.0+** (loader 47+) |
| **GeckoLib** | **обязателен, 4.4.4+**, ставится и на сервер, и на клиент |
| Java | 17 |
| Curios, Patchouli, SmartBrainLib, Lodestone, Sound Physics | **не требуются** |

## 1a. Машиночитаемый список (сверяется гейтом)

Блок ниже читает `tools/deps_install_check.py` и сверяет с `mods.toml` пакета.
Если Кодер добавит зависимость, а документ не обновят — гейт упадёт.

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

## 2. Откуда это следует

`mods.toml` в пакете объявляет ровно три зависимости:

```toml
[[dependencies.carnis]]  modId="forge"     mandatory=true  side="BOTH"
[[dependencies.carnis]]  modId="minecraft" mandatory=true  side="BOTH"
[[dependencies.carnis]]  modId="geckolib"  mandatory=true  side="BOTH"
```

**GeckoLib — жёсткая зависимость** (`mandatory=true`, `side="BOTH"`), то есть
без него мод не запустится ни на клиенте, ни на сервере. Это же
подтверждается кодом: `154` импорта `software.bernie.geckolib` в `57` файлах.

Проверить:

```bash
unzip -p 01-coder/3.7.3/project-3.7.3-clean.zip \
  src/main/resources/META-INF/mods.toml | grep -A4 dependencies
```

## 3. Пять библиотек из ТЗ — в коде их нет

Требование волны 58 называет Curios, Patchouli, SmartBrainLib, Lodestone,
Sound Physics. Проверил по исходникам пакета — **ни одного импорта, ни одного
упоминания**:

| библиотека | файлов Java | импортов | в `build.gradle` | в `mods.toml` |
|---|---|---|---|---|
| Curios | 0 | 0 | нет | нет |
| Patchouli | 0 | 0 | нет | нет |
| SmartBrainLib | 0 | 0 | нет | нет |
| Lodestone | 0 | 0 | нет | нет |
| Sound Physics | 0 | 0 | нет | нет |
| **GeckoLib** | **57** | **154** | **есть** | **есть** |

Проверить:

```bash
for L in curios patchouli smartbrain lodestone soundphysics geckolib; do
  echo "$L: $(grep -rli "$L" /tmp/p373/src --include='*.java' | wc -l) файлов"
done
```

**Почему это важно, а не придирка.** Если написать в требованиях «нужен
Patchouli», игрок поставит лишний мод, а если написать «не нужен» про
GeckoLib — получит краш при запуске. Ошибка в любую сторону стоит игроку
времени, поэтому пишу то, что вижу в коде.

Книга «Codex Carnis» реализована **своими средствами**, а не через Patchouli:
это видно по отсутствию импортов.

## 4. Где живёт зависимость при сборке

`build.gradle`:

```gradle
repositories {
    mavenCentral()
    maven { url = 'https://dl.cloudsmith.io/public/geckolib3/geckolib/maven/' }
}
implementation fg.deobf("software.bernie.geckolib:geckolib-forge-1.20.1:4.4.4")
```

Один внешний Maven — GeckoLib. `mavenCentral()` нужен для стандартных
библиотек. Это значит: **сборка требует сети** к Cloudsmith, но **запуск** —
нет.

## 5. Чего этот документ не делает

В корневом `README.md` раздела про установку **не было** — он описывает шину
репозитория, а не мод. Я не переписываю README: он документ проекта для ролей,
а требования к установке нужны **игроку**. Раздел «Установка» с ссылкой на
этот файл добавлен в README отдельно, чтобы игрок не искал.

Отдельно: `.jar` в этой версии **не собран** (запрет Архитектора до вердикта),
поэтому «установить» пока можно только из собранного пакета, а не из релиза.
