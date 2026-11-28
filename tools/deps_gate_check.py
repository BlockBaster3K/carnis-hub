#!/usr/bin/env python3
"""Проверить, что окружение гейта соответствует tools/requirements-gate.txt.

Зачем не полагаться на «оно само стоит»: без PyAV гейт уровней печатает
«клиппинг не проверен» и остаётся красным на любом пакете — это выглядит как
дефект звука, а не как отсутствие инструмента. Такой отказ обязан быть
обнаружен ДО запуска приёмки и назван своим именем.

Коды: 0 — всё на месте; 2 — чего-то нет (печатает чего и чем лечится);
      3 — не удалось прочитать список требований.
"""
import importlib
import os
import re
import sys

REQ = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "requirements-gate.txt")

# имя пакета в requirements -> модуль, который реально импортируется
MODULE = {"pillow": "PIL", "pyav": "av", "imageio-ffmpeg": "imageio_ffmpeg",
          "soundfile": "soundfile", "numpy": "numpy", "scipy": "scipy"}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selfcheck" in argv:
        return selfcheck()
    if not os.path.isfile(REQ):
        print("ОШИБКА: нет %s — проверить нечего (это не «всё на месте»)." % REQ)
        return 3
    need = []
    for line in open(REQ, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if not line:
            continue
        m = re.match(r"^([A-Za-z0-9_.\-]+)\s*(>=|==|~=)?\s*([\d.]*)$", line)
        if m:
            need.append((m.group(1), m.group(2) or "", m.group(3)))
    if not need:
        print("ОШИБКА: список требований пуст — это не «всё на месте».")
        return 3

    missing = []
    print("окружение гейта (%s):" % os.path.basename(REQ))
    for name, op, ver in need:
        mod = MODULE.get(name.lower(), name.replace("-", "_"))
        try:
            m = importlib.import_module(mod)
            got = getattr(m, "__version__", None) or getattr(
                m, "version", None) or "?"
        except Exception as exc:                        # noqa: BLE001
            missing.append((name, mod, str(exc)[:60]))
            print("  ✗ %-16s нет (модуль %s): %s" % (name, mod, str(exc)[:50]))
            continue
        print("  ✓ %-16s %s%s" % (name, got, "  (требуется >= %s)" % ver
                                  if ver else ""))
    print()
    if missing:
        print("ИТОГ: не хватает %d из %d." % (len(missing), len(need)))
        print("  лечение: pip install -r tools/requirements-gate.txt")
        for name, mod, why in missing:
            if mod == "av":
                print("  ⚠ без av гейт уровней НЕ ПРОВЕРИТ клиппинг и crest —")
                print("    это отказ инструмента, а не дефект пакета.")
        return 2
    print("ИТОГ: все %d зависимостей на месте." % len(need))
    return 0


def selfcheck():
    """Доказать, что отсутствие PyAV действительно ловится (регрессия S126)."""
    import subprocess
    import tempfile
    here = os.path.abspath(__file__)
    env = dict(os.environ)
    print("Самопроверка: подменный пакет av (как будто PyAV не установлен)")
    tmp = tempfile.mkdtemp(prefix="noav_")
    with open(os.path.join(tmp, "av.py"), "w", encoding="utf-8") as f:
        f.write('raise ImportError("selfcheck: PyAV нет")\n')
    env["PYTHONPATH"] = tmp + (os.pathsep + env["PYTHONPATH"]
                               if env.get("PYTHONPATH") else "")
    r = subprocess.run([sys.executable, here], capture_output=True, text=True,
                       env=env, timeout=120)
    tail = [l for l in (r.stdout + r.stderr).splitlines() if "ИТОГ" in l]
    print("  код %d  %s" % (r.returncode, tail[0] if tail else ""))
    if r.returncode != 2:
        print("  ✗ ПРОВАЛ: без av код %d, ожидался 2" % r.returncode)
        return 2
    if "av" not in r.stdout:
        print("  ✗ ПРОВАЛ: av даже не назван в выводе")
        return 2
    print("  ✓ отсутствие PyAV названо прямо, код 2 — не «всё на месте»")
    return 0


if __name__ == "__main__":
    sys.exit(main())
