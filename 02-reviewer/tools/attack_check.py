#!/usr/bin/env python3
"""ДИАГНОСТИКА «громкости атаки» (S29/S40). В ГЕЙТ НЕ СТАВИТЬ — см. R22 §7.

Итог R22: как НОРМА метрика не годится ни с постоянным порогом 0.60 (S40),
ни с допуском per-file (мой §7.3): на файле с плавным входом чистый gain даёт
ложный провал −13 дБ из-за сдвига онсета после перекода. Как ОТЧЁТНАЯ метрика
полезна: она показывает, что crest слеп к правке атаки там, где пик вне первых
10 мс (60 % банка), и сколько файлов имеет дрожание окна выше 0.60 дБ (39 из 144).

Определение (S29): `атака = max|x| в первых 10 мс` относительно пика файла.
Два дефекта, найденных в R22 и исправленных здесь:

1. **Окно от сэмпла 0 попадает в ведущую цифровую тишину.** В каноне 6 файлов
   начинаются с тишины (у `hive/hive_spread_01_creep` — 246 мс), и метрика
   мерила тишину: `heart_pulse` давал −237 дБ при реальной атаке −2,4 дБ.
   Здесь окно начинается с **онсета** — первого сэмпла не тише «пик − 40 дБ».

2. **Жёсткое окно разрывно по времени.** Сдвиг окна на 1 мс меняет величину до
   16 дБ (`hive/spawn_skeleton_blade_03`). Поэтому метрика возвращает ещё и
   **дрожание** (расхождение при сдвиге ±1 мс) — гейт обязан учитывать его в
   допуске per-file (`max(порог; baseline + 0.05; дрожание)`), а не полагаться
   на постоянный 0.60.

Коды возврата: 0 — в допуске; 2 — есть выходы; 3 — метрика не определена
(нет сигнала в файле) или нет эталона. Строки с уровнями ниже −20 дБ печатаются
как предупреждение «тихая атака» (решение по ним — за таблицей Звука).

Использование:
    attack_check.py --selftest
    attack_check.py --survey 03-sound/sounds
    attack_check.py <эталон.ogg|каталог> <сданное.ogg|каталог> [--tol 0.60]
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np

WIN_MS = 10.0
SHIFT_MS = 1.0
ONSET_DB = -40.0        # онсет = первый сэмпл не тише «пик − 40 дБ»
QUIET_DB = -20.0        # ниже — «тихая атака», предупреждение
DEFAULT_TOL = 0.60


def decode(path):
    import av  # PyAV, как в tools/timbre_check.py и гейте

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
    return np.concatenate(chunks), sr


def onset(x, rel_db=ONSET_DB):
    """Первый сэмпл не тише «пик − rel_db»; так ведущая тишина не съедает окно."""
    peak = float(np.abs(x).max())
    if peak <= 0.0:
        return 0
    idx = np.flatnonzero(np.abs(x) >= peak * 10.0 ** (rel_db / 20.0))
    return int(idx[0]) if len(idx) else 0


def _win_max(x, sr, start, win_ms=WIN_MS):
    n1 = min(len(x), start + max(1, int(sr * win_ms / 1000.0)))
    if n1 <= start:
        return 0.0
    return float(np.abs(x[start:n1]).max())


def attack(x, sr):
    """(значение дБ отн. пика, уровень, дрожание при сдвиге ±1 мс) или None."""
    peak = float(np.abs(x).max())
    if peak <= 0.0:
        return None
    o = onset(x)
    a0 = _win_max(x, sr, o)
    if a0 <= 0.0:
        return None, -np.inf, float("inf")
    level = 20.0 * np.log10(a0 / peak)
    n_shift = int(sr * SHIFT_MS / 1000.0)
    a_minus = _win_max(x, sr, max(0, o - n_shift))
    a_plus = _win_max(x, sr, o + n_shift)
    jitter = max(abs(20.0 * np.log10(max(a_minus, 1e-12) / a0)),
                 abs(20.0 * np.log10(max(a_plus, 1e-12) / a0)))
    return level, level, jitter


def tolerance(jitter, base=None, thr=DEFAULT_TOL):
    """Допуск per-file по З-30 + измеренное дрожание (R22)."""
    tol = thr
    if base is not None:
        tol = max(tol, base + 0.05)
    if jitter is not None and np.isfinite(jitter):
        tol = max(tol, min(jitter, 6.0) + 0.05)
    return tol


# ---------------------------------------------------------------- selftest

def _selftest():
    sr = 48000
    n_total = sr
    t = np.arange(n_total, dtype="float32") / sr
    cases = []

    # 1. явная атака в начале
    x = 0.05 * np.sin(2 * np.pi * 200 * t).astype("float32")
    x[: int(sr * 0.004)] = 0.9 * np.sin(2 * np.pi * 900 * t[: int(sr * 0.004)])
    cases.append(("явная атака", x, True, False))

    # 2. инвариантность к усилению — главное: gain не должен ловиться
    cases.append(("инвариант к gain", x * 0.5, True, False))

    # 3. ведущая тишина 50 мс, затем атака: окно от 0 мерило бы тишину
    y = np.zeros(n_total, dtype="float32")
    y[int(sr * 0.05):] = x[: n_total - int(sr * 0.05)]
    cases.append(("тишина 50 мс + атака", y, True, False))

    # 4. плавный фейд-ин без тишины — величина есть, но она «тихая»
    z = (0.9 * np.linspace(0, 1, n_total, dtype="float32")
         * np.sin(2 * np.pi * 200 * t)).astype("float32")
    cases.append(("плавный фейд 1 с", z, True, True))

    # 5. полная тишина — метрика не определена
    cases.append(("тишина", np.zeros(n_total, dtype="float32"), False, False))

    failed = 0
    for name, sig, expect_def, expect_quiet in cases:
        got = attack(sig, sr)
        if got is None:
            ok, val, jit = False, None, None
        else:
            val, _lvl, jit = got
            ok = True
        quiet = ok and val < QUIET_DB
        good = (ok == expect_def) and (quiet == expect_quiet)
        if name == "инвариант к gain":
            v0 = attack(x, sr)[0]
            good = good and abs(val - v0) < 1e-6
            shown = f"Δ = {val - v0:+.2e} дБ"
        else:
            shown = f"{val:+.2f} дБ, дрожание {jit:.2f}" if ok else "не определена"
        print(f"  {'✓' if good else '✗'} {name}: {shown}")
        failed += 0 if good else 1
    print(f"итог: {len(cases) - failed}/{len(cases)}")
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------- survey

def survey(root):
    root = pathlib.Path(root)
    rows = []
    for p in sorted(root.rglob("*.ogg")):
        x, sr = decode(p)
        got = attack(x, sr)
        rows.append((str(p.relative_to(root)), got))
    undef = [r for r in rows if r[1] is None]
    quiet = [r for r in rows if r[1] is not None and r[1][0] < QUIET_DB]
    vals = np.array([r[1][0] for r in rows if r[1] is not None])
    jits = np.array([r[1][2] for r in rows if r[1] is not None])
    print(f"каталог: {root}")
    print(f"файлов {len(rows)}: метрика определена {len(vals)}, "
          f"не определена {len(undef)}, тихая атака (<{QUIET_DB:.0f} дБ) {len(quiet)}")
    if len(vals):
        print(f"уровень атаки: медиана {np.median(vals):+.1f} дБ, "
              f"диапазон {vals.min():+.1f}…{vals.max():+.1f}")
        print(f"дрожание окна: медиана {np.median(jits):.2f} дБ, "
              f"p95 {np.percentile(jits, 95):.2f}, макс {jits.max():.2f}; "
              f"больше 0.60: {(jits > 0.60).sum()}")
    for name, got in undef:
        print(f"  ! {name}: не определена")
    return 3 if undef else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--survey", metavar="DIR")
    ap.add_argument("ref", nargs="?")
    ap.add_argument("got", nargs="?")
    ap.add_argument("--tol", type=float, default=DEFAULT_TOL)
    ap.add_argument("--flat-tol", action="store_true",
                    help="не учитывать дрожание окна (только --tol)")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()
    if a.survey:
        return survey(a.survey)
    if not (a.ref and a.got):
        ap.print_help()
        return 1

    ref, got = pathlib.Path(a.ref), pathlib.Path(a.got)
    pairs = []
    if ref.is_dir() and got.is_dir():
        for p in sorted(got.rglob("*.ogg")):
            rel = p.relative_to(got)
            rp = ref / rel if (ref / rel).exists() else ref / rel.name
            if not rp.exists():
                print(f"нет эталона для {rel}", file=sys.stderr)
                return 3
            pairs.append((rp, p))
    elif ref.is_file() and got.is_file():
        pairs.append((ref, got))
    else:
        print("нужны либо два каталога, либо два файла", file=sys.stderr)
        return 1

    over, undef, quiet = [], [], []
    for rp, gp in pairs:
        x0, sr = decode(rp)
        x1, _ = decode(gp)
        g0, g1 = attack(x0, sr), attack(x1, sr)
        if g0 is None or g1 is None:
            undef.append(str(gp.name))
            continue
        d = g1[0] - g0[0]
        tol = a.tol if a.flat_tol else tolerance(g1[2], None, a.tol)
        if g1[0] < QUIET_DB:
            quiet.append(str(gp.name))
        if abs(d) > tol:
            over.append((str(gp.name), d, tol, g1[2]))

    print(f"Файлов: {len(pairs)}, метрика не определена: {len(undef)}, "
          f"выходов за допуск: {len(over)}")
    for n in undef:
        print(f"  ? {n}")
    for n, d, tol, jit in sorted(over, key=lambda r: -abs(r[1])):
        print(f"  ! {n:52s} {d:+.2f} дБ (допуск {tol:.2f}, дрожание {jit:.2f})")
    if quiet:
        print(f"  i тихая атака (<{QUIET_DB:.0f} дБ): {len(quiet)} файлов")
    if undef:
        return 3
    return 2 if over else 0


if __name__ == "__main__":
    sys.exit(main())
