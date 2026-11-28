#!/usr/bin/env python3
"""Проверка ключевых кадров анимаций по правилам GeckoLib.

ЗАЧЕМ. 3.8.1 упал на старте клиента:

    GeckoLibException: carnis:animations/entity/infected_skeleton.animation.json:
        Error loading animation file
    Caused by: JsonParseException: Invalid keyframe data - multiple starting
        keyframes?0.0

Причина не в «двух кадрах на одном времени», как читается по тексту ошибки.
Вот что делает GeckoLib (BakedAnimationsAdapter.getKeyframes, ветка 1.20.1):

    for (entry : obj.entrySet()) {
        double timestamp = readTimestamp(entry.getKey());
        if (timestamp == 0 && !list.isEmpty())
            throw new JsonParseException(
                "Invalid keyframe data - multiple starting keyframes?" + entry.getKey());
        ...
        list.add(DoubleObjectPair.of(timestamp, entry.getValue()));
    }

Обход идёт В ПОРЯДКЕ ЗАПИСИ В JSON, а readTimestamp для нечислового ключа
возвращает 0. Значит ошибка срабатывает, когда кадр с временем 0 стоит в
объекте не первым — независимо от того, есть ли настоящий дубль времени.
В 3.8.1 в animation.infected_skeleton.attack_scythe кадр "0.0" оказался
записан последним (в 3.8.0 он шёл первым), и клиент не запустился.

ЧТО ПРОВЕРЯЕТСЯ:
  - время 0 (или нечисловой ключ, который GeckoLib читает как 0) не первый;
  - времена в канале идут по возрастанию (иначе кривая ломается);
  - кадры вообще разбираются (битый JSON, ключи не числа).

Запуск:
    python3 tools/animation_keyframe_check.py <zip-пакет> [<zip> ...]
    python3 tools/animation_keyframe_check.py --jar <jar>

Код возврата: 0 — чисто, 2 — есть проблемы.
"""

import json
import sys
import zipfile

ANIM_DIR = "assets/carnis/animations/"
PKG_DIR = "src/main/resources/assets/carnis/animations/"
CHANNELS = ("rotation", "position", "scale")


def is_numeric(key):
    """Аналог NumberUtils.isCreatable: GeckoLib парсит ключ как double."""
    try:
        float(key)
        return True
    except (TypeError, ValueError):
        return False


def timestamp_of(key):
    """Аналог readTimestamp: нечисловой ключ GeckoLib читает как 0."""
    return float(key) if is_numeric(key) else 0.0


def check_channel(keys, where, problems):
    """Один канал (rotation/position/scale) одного бона."""
    seen = []
    for key in keys:
        value = timestamp_of(key)

        # Главное правило: кадр с временем 0 обязан быть первым.
        if value == 0.0 and seen:
            problems.append(
                "%s — кадр %r стоит не первым (порядок: %s). "
                "GeckoLib бросит 'multiple starting keyframes?'%s"
                % (where, key, list(keys), key)
            )

        if not is_numeric(key):
            problems.append(
                "%s — ключ %r не число, GeckoLib прочитает его как время 0"
                % (where, key)
            )

        seen.append(value)

    if seen != sorted(seen):
        problems.append(
            "%s — времена не по возрастанию: %s" % (where, seen)
        )


def check_animation_file(name, raw, problems):
    """Разбирает один .animation.json и проверяет все каналы."""
    short = name.rsplit("/", 1)[-1]
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 — нужен любой сбой разбора
        problems.append("%s — JSON не читается: %s" % (short, exc))
        return 0

    animations = data.get("animations")
    if not isinstance(animations, dict):
        problems.append("%s — нет секции 'animations'" % short)
        return 0

    checked = 0
    for anim_name, anim in animations.items():
        if not isinstance(anim, dict):
            continue
        bones = anim.get("bones")
        if not isinstance(bones, dict):
            continue
        for bone_name, bone in bones.items():
            if not isinstance(bone, dict):
                continue
            for channel in CHANNELS:
                frames = bone.get(channel)
                if not isinstance(frames, dict):
                    continue
                # {"vector": [...]} — одиночный кадр, порядок не важен
                if "vector" in frames:
                    continue
                check_channel(
                    list(frames.keys()),
                    "%s :: %s :: %s.%s" % (short, anim_name, bone_name, channel),
                    problems,
                )
                checked += 1
    return checked


def collect(zip_path, prefix):
    """Возвращает [(имя, байты)] для файлов анимаций внутри zip."""
    out = []
    with zipfile.ZipFile(zip_path) as archive:
        for name in sorted(archive.namelist()):
            if name.startswith(prefix) and name.endswith(".json"):
                out.append((name, archive.read(name)))
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1

    args = argv[1:]
    use_jar = False
    if args[0] == "--jar":
        use_jar = True
        args = args[1:]

    if not args:
        print("ОШИБКА: не указан файл пакета")
        return 1

    problems = []
    total_files = 0
    total_channels = 0

    for path in args:
        prefix = ANIM_DIR if use_jar else PKG_DIR
        try:
            entries = collect(path, prefix)
        except Exception as exc:  # noqa: BLE001
            print("ОШИБКА: не читается %s: %s" % (path, exc))
            return 1
        if not entries:
            print("ОШИБКА: в %s нет анимаций по пути %s" % (path, prefix))
            return 1
        for name, raw in entries:
            total_files += 1
            total_channels += check_animation_file(name, raw, problems)
        print("  %s: файлов анимаций %d" % (path.rsplit("/", 1)[-1], len(entries)))

    print("  каналов проверено: %d" % total_channels)

    if problems:
        print("\nНАЙДЕНЫ ПРОБЛЕМЫ: %d" % len(problems))
        for problem in problems:
            print("  ⛔ " + problem)
        print("\nИТОГ: анимации НЕ пройдут загрузку в GeckoLib — клиент не запустится")
        return 2

    print("\nИТОГ: все %d файлов анимаций разбираются GeckoLib (ключи в порядке)"
          % total_files)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
