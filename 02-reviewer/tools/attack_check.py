#!/usr/bin/env python3
"""Проверка «громкости атаки» с формальным предусловием (R22 / S29).

Метрика Звука из S29: `атака = max|x| в первых 10 мс` относительно пика файла.
Величина полезная (crest правку атаки не видит — подтверждено R22), но
**не определена** на части банка: если в первых 10 мс сигнала нет, отношение
двух чисел около нуля даёт мусор (у Звука 123 дБ на `zone_stinger_*`).

Здесь предусловие не «файл неудобный, выкинем», а проверяемое:

  1) УРОВЕНЬ:  окно должно содержать сигнал — `max|окно| ≥ пик − 40 дБ`.
  2) УСТОЙЧИВОСТЬ: метрика не должна зависеть от того, где именно в окне
     стоит максимум. Считаем её же со сдвигом окна на +1 мс; если расхождение
     больше 0.30 дБ — у файла «атака на границе окна», и величина не
     определена (именно так ведёт себя `infected_illusioner_death_01`:
     уровень −5.4 дБ «здоровый», а дрейф перекода −41 дБ).

Только при выполнении обоих условий значение годится для нормы. Остальные
файлы попадают в список «не определено» — и гейт обязан **сверить их число**
с ожидаемым (fail-closed), а не молча пропустить.

Коды возврата: 0 — все файлы определены и в допуске; 2 — есть выходы за
допуск; 3 — есть файлы с неопределённой метрикой (или нет записи в таблице).

Использование:
    attack_check.py --selftest
    attack_check.py --survey 03-sound/sounds
    attack_check.py <эталон.ogg|каталог> <сданное.ogg|каталог> [--table T]
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np

WIN_MS = 10.0
SHIFT_MS = 1.0
LEVEL_GUARD_DB = 40.0     # окно должно быть не тише «пик − 40 дБ»
STABILITY_DB = 0.30       # расхождение при сдвиге окна на 1 мс
DEFAULT_TOL = 0.60        # порог транзиента (З-30: max(порог; baseline+0.05))


def decode(path):
    import av  # PyAV, как в tools/timbre_check.py

    container = av.open(str(path))
    stream = container.streams.audio[0]
    sr = stream.rate
    chunks = []
    for frame in container.decode(stream):
        arr = frame.to_ndarray()
        if arr.ndim > 1:
            arr = arr.mean(axis=0)
        chunks.append(arr.astype("float32"))
    container.close()
    if not chunks:
        raise ValueError(f"пусто: {path}")
    x = np.concatenate(chunks)
    return x, sr


def _win_max(x, sr, start_ms, win_ms):
    n0 = max(0, int(sr * start_ms / 1000.0))
    n1 = min(len(x), n0 + max(1, int(sr * win_ms / 1000.0)))
    if n1 <= n0:
        return 0.0
    return float(np.abs(x[n0:n1]).max())


def attack_metric(x, sr):
    """(значение дБ относительно пика, уровень окна дБ отн. пика, запас устойчивости дБ)."""
    peak = float(np.abs(x).max())
    if peak <= 0.0:
        return None
    a0 = _win_max(x, sr, 0.0, WIN_MS)
    a1 = _win_max(x, sr, SHIFT_MS, WIN_MS)
    level = 20.0 * np.log10(max(a0, 1e-12) / peak)
    if a0 <= 0.0:
        return None, level, float("inf")
    dev = abs(20.0 * np.log10(max(a1, 1e-12) / max(a0, 1e-12)))
    return 20.0 * np.log10(a0 / peak), level, dev


def defined(x, sr):
    """(годна ли метрика, значение или None, причина)."""
    got = attack_metric(x, sr)
    if got is None:
        return False, None, "тишина"
    val, level, dev = got
    if level < -LEVEL_GUARD_DB:
        return False, None, f"нет атаки (уровень {level:.0f} дБ)"
    if dev > STABILITY_DB:
        return False, None, f"атака на границе окна (сдвиг 1 мс → {dev:.2f} дБ)"
    return True, val, ""


# ---------------------------------------------------------------- selftest

def _selftest():
    sr = 48000
    t = np.arange(sr, dtype="float32") / sr
    cases = []

    # 1. явная атака: короткий щелчок в начале, дальше тише
    x = 0.05 * np.sin(2 * np.pi * 200 * t).astype("float32")
    x[: int(sr * 0.004)] = 0.9 * np.sin(2 * np.pi * 900 * t[: int(sr * 0.004)])
    cases.append(("явная атака", x, True))

    # 2. фейд-ин из тишины 30 мс — атаки нет
    x = np.zeros_like(t)
    ramp = np.linspace(0, 1, int(sr * 0.03), dtype="float32")
    body = 0.8 * np.sin(2 * np.pi * 300 * t[int(sr * 0.03):]).astype("float32")
    body[: len(ramp)] *= ramp
    x[int(sr * 0.03):] = body
    cases.append(("фейд-ин 30 мс", x, False))

    # 3. максимум ровно на последнем сэмпле окна, сразу после — спад:
    #    сдвиг окна на 1 мс теряет пик → величина неустойчива
    x = (0.02 * np.sin(2 * np.pi * 200 * t)).astype("float32")
    x[int(sr * 0.0008)] = 0.9   # узкий пик у самого начала окна
    cases.append(("пик на границе окна", x, False))

    # 4. тихая атака (−45 дБ от пика внутри окна) — ниже порога уровня
    x = 0.9 * np.sin(2 * np.pi * 200 * t).astype("float32")
    x[: int(sr * 0.010)] = 0.005 * np.sin(2 * np.pi * 5000 * t[: int(sr * 0.010)])
    cases.append(("атака −45 дБ", x, False))

    # 5. метрика инвариантна к общему усилению (gain не должен ловиться)
    base = cases[0][1]
    ok, v0, _ = defined(base, sr)
    ok2, v1, _ = defined(base * 0.5, sr)
    cases.append(("инвариант к gain", base * 0.5, True))

    failed = 0
    for name, sig, expect in cases:
        ok, val, why = defined(sig, sr)
        if name == "инвариант к gain":
            good = ok and ok2 and abs(v1 - v0) < 1e-6
            print(f"  {'✓' if good else '✗'} {name}: Δ = {v1 - v0:+.2e} дБ")
        else:
            good = ok == expect
            shown = f"{val:+.2f} дБ" if val is not None else why
            print(f"  {'✓' if good else '✗'} {name}: определена={ok} ({shown})")
        failed += 0 if good else 1
    print(f"итог: {len(cases) - failed}/{len(cases)}")
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------- survey

def survey(root):
    root = pathlib.Path(root)
    ok_list, bad_list = [], []
    for p in sorted(root.rglob("*.ogg")):
        x, sr = decode(p)
        ok, val, why = defined(x, sr)
        (ok_list if ok else bad_list).append((str(p.relative_to(root)), val, why))
    print(f"каталог: {root}")
    print(f"метрика определена: {len(ok_list)}, не определена: {len(bad_list)}")
    for name, _, why in bad_list:
        print(f"  ! {name:52s} {why}")
    if ok_list:
        vals = np.array([v for _, v, _ in ok_list])
        print(f"уровень атаки: медиана {np.median(vals):+.1f} дБ, "
              f"диапазон {vals.min():+.1f}…{vals.max():+.1f} дБ")
    return 3 if bad_list else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--survey", metavar="DIR")
    ap.add_argument("ref", nargs="?")
    ap.add_argument("got", nargs="?")
    ap.add_argument("--tol", type=float, default=None,
                    help="единый допуск, если нет таблицы")
    ap.add_argument("--table", help="таблица допусков attack (per-file)")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()
    if a.survey:
        return survey(a.survey)
    if not (a.ref and a.got):
        ap.print_help()
        return 1

    ref_dir = pathlib.Path(a.ref)
    got_dir = pathlib.Path(a.got)
    if not got_dir.is_dir():
        print("сданное должно быть каталогом .ogg", file=sys.stderr)
        return 1
    out = []
    for p in sorted(got_dir.rglob("*.ogg")):
        rel = p.relative_to(got_dir)
        rp = ref_dir / rel
        if not rp.exists():
            print(f"нет эталона для {rel}", file=sys.stderr)
            return 3
        x0, sr = decode(rp)
        x1, _ = decode(p)
        ok0, v0, why0 = defined(x0, sr)
        ok1, v1, why1 = defined(x1, sr)
        if not (ok0 and ok1):
            out.append((str(rel), None, None))
            continue
        tol = a.tol if a.tol is not None else DEFAULT_TOL
        out.append((str(rel), v1 - v0, tol))

    undef = [n for n, d, _ in out if d is None]
    over = [(n, d, t) for n, d, t in out if d is not None and abs(d) > t]
    print(f"Файлов: {len(out)}, метрика не определена: {len(undef)}, "
          f"выходов за допуск: {len(over)}")
    for n in undef:
        print(f"  ? {n}")
    for n, d, t in sorted(over, key=lambda r: -abs(r[1])):
        print(f"  ! {n:52s} {d:+.2f} дБ (допуск {t:.2f})")
    if undef:
        return 3
    return 2 if over else 0


if __name__ == "__main__":
    sys.exit(main())
