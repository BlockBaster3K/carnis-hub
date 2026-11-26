#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Аудит семантики `targets_by_sample` и «половинчатых правок» громкости.

ЗАЧЕМ. Пересборка 3.7.3 (`7cd55a2`, пакет `8ef67394…`) получила
`detail_flow_01 = 0.731`, потому что числа в спеке (`0.731`) — это ИТОГОВАЯ
громкость (`call_site 0.30 × 2.437`), а метка в спеке стояла
`targets_mode: "json"` («числа — это volume в sounds.json»). Один инструмент
(`volume_effective_check`) считает по эффективной семантике и увидел
расхождение, второй (`sample_loudness`) смотрит только на отношение
множителей и не увидел ничего. Пакет прошёл гейт зелёным, а баланс пары
ухудшился с 7,71 до 10,43 дБ.

ЧТО ДЕЛАЕТ ЭТОТ ИНСТРУМЕНТ (только чтение, ничего не правит):

  1. Для каждого события с `targets_by_sample` печатает таблицу
     «сэмпл | volume в sounds.json | call_site | эффективная | цель»
     и считает, какой из ДВУХ семантик пакет удовлетворяет:
        json      — значение ключа должно равняться цели;
        effective — call_site × значение ключа должно равняться цели.
  2. Если пакет удовлетворяет семантике, ПРОТИВОПОЛОЖНОЙ метке
     `targets_mode` — это находка «метка врёт» (пакет при этом верен).
  3. Если пакет не удовлетворяет ни одной — находка «пакет не по спеке»,
     и по каждому сэмплу печатается, какое значение ключа требуется
     в каждой из семантик (что именно надо поставить).
  4. **Сторож половинчатой правки** (`--baseline <предыдущий пакет>`):
     если цель требует изменить ключ сэмпла, а ключ остался равен
     базовому — находка «правка применена не ко всей паре». Именно этот
     случай (изменён `_01`, оставлен `_02`) и дал 10,43 дБ.
  5. **Уровень события против доски** (`board_target`): если наигромчайшая
     эффективная громкость события ушла от `board_target` больше чем на
     `--level-tol` дБ — печатается замечание. Это ловит вариант «выровнять
     пару, заглушив всё событие»: пакет формально по спеке, а событие
     на 10,46 дБ тише, чем хотела доска.

  6. **Разброс пары по звуку** (`--baseline`): считается по самим .ogg
     пакета (RMS файла + объявленный множитель) и сравнивается с базой.
     Если правка УВЕЛИЧИЛА разброс больше чем на `--worse-tol` дБ — находка
     «правка ухудшила баланс». Этот канал не зависит ни от какой семантики
     спеки: именно его не хватило в пересборке 0.731 (7,71 → 10,43 дБ).

КОДЫ ВОЗВРАТА: 0 — всё сошлось и метка согласована; 2 — находки (список в
конце); 3 — проверить нельзя (нет sounds.json / спеки / базового пакета).

Запуск:
  python3 02-reviewer/tools/volume_semantics_audit.py \
      --pkg /tmp/vp --spec 03-sound/spec/volume_spec_t3202.json \
      --baseline /tmp/vp_base
"""
import argparse
import json
import math
import os
import sys
import zipfile

DEFAULT_SPEC = os.path.join("03-sound", "spec", "volume_spec_t3202.json")
SOUNDS_JSON = os.path.join("src", "main", "resources", "assets", "carnis", "sounds.json")


# ---------------------------------------------------------------- чтение входа
def _read_text(pkg, rel):
    """Текст файла из каталога или из ZIP-пакета. None — файла нет."""
    if os.path.isdir(pkg):
        p = os.path.join(pkg, rel)
        if not os.path.isfile(p):
            return None
        with open(p, "r", encoding="utf-8") as fh:
            return fh.read()
    if zipfile.is_zipfile(pkg):
        with zipfile.ZipFile(pkg) as z:
            for name in z.namelist():
                if name.endswith(rel.replace(os.sep, "/")):
                    return z.read(name).decode("utf-8")
    return None


def _read_bytes(pkg, rel):
    """Байты файла из каталога или ZIP. None — файла нет."""
    if os.path.isdir(pkg):
        p = os.path.join(pkg, rel)
        return open(p, "rb").read() if os.path.isfile(p) else None
    if zipfile.is_zipfile(pkg):
        with zipfile.ZipFile(pkg) as z:
            for name in z.namelist():
                if name.endswith(rel.replace(os.sep, "/")):
                    return z.read(name)
    return None


def _find_sample_bytes(pkg, stem):
    """Байты <stem>.ogg из sounds/ пакета — путь ищется, а не угадывается:
    события лежат в подкаталогах (hive/, flesh/), а имя события и папка
    не всегда совпадают (hive.detail_flow -> hive/detail_flow_01.ogg)."""
    target = stem + ".ogg"
    if os.path.isdir(pkg):
        for dp, _dn, fs in os.walk(os.path.join(pkg, "src", "main", "resources",
                                                "assets", "carnis", "sounds")):
            if target in fs:
                return open(os.path.join(dp, target), "rb").read()
        return None
    if zipfile.is_zipfile(pkg):
        with zipfile.ZipFile(pkg) as z:
            for name in z.namelist():
                if name.endswith("/" + target) and "/sounds/" in name:
                    return z.read(name)
    return None


def sample_rms(pkg, event, stem):
    """RMS файла сэмпла, dBFS. None — файла нет или нет soundfile."""
    try:
        import io
        import numpy as np
        import soundfile as sf
    except ImportError:
        return None
    raw = _find_sample_bytes(pkg, stem)
    if raw is None:
        return None
    x, _sr = sf.read(io.BytesIO(raw))
    if getattr(x, "ndim", 1) > 1:
        x = x.mean(axis=1)
    return 20.0 * math.log10(float(np.sqrt((x ** 2).mean())) + 1e-12)


def spread_findings(entry, sounds, base_sounds, pkg, base_pkg, worse_tol):
    """Разброс пары по звуку: стало хуже базы? Не зависит от семантики спеки."""
    finds, notes = [], []
    targets = entry.get("targets_by_sample") or {}
    if len(targets) < 2:
        return finds, notes
    event = entry.get("event", "")
    vols = event_volumes(sounds, event) or {}
    base = event_volumes(base_sounds, event) or {}
    mult = call_site_multiplier(entry)

    def spread(vols_, pkg_):
        vals = []
        for stem in targets:
            if stem not in vols_:
                continue
            rms = sample_rms(pkg_, event, stem)
            if rms is None:
                return None
            vals.append(rms + db(vols_[stem] * mult))
        return max(vals) - min(vals) if len(vals) >= 2 else None

    now = spread(vols, pkg)
    was = spread(base, base_pkg)
    if now is None or was is None:
        notes.append("%s: разброс по звуку не посчитан (нет .ogg или soundfile)" % event)
        return finds, notes
    notes.append("%s: разброс пары по звуку %.2f дБ (было %.2f)" % (event, now, was))
    if now - was > worse_tol:
        finds.append("%s: правка УХУДШИЛА разброс пары — %.2f → %.2f дБ "
                     "(+%.2f); правка должна была его уменьшить"
                     % (event, was, now, now - was))
    return finds, notes


def load_sounds(pkg):
    raw = _read_text(pkg, SOUNDS_JSON)
    if raw is None:
        raise SystemExit("НЕ ПРОВЕРЕНО: в %s нет %s" % (pkg, SOUNDS_JSON))
    return json.loads(raw)


def event_volumes(sounds, event):
    """{stem: volume} для события: volume по умолчанию 1.0, как в игре."""
    node = sounds.get(event)
    if node is None:
        return None
    out = {}
    for snd in node.get("sounds", []):
        name = snd.get("name") if isinstance(snd, dict) else snd
        if not name:
            continue
        stem = name.split(":")[-1].split("/")[-1]
        vol = snd.get("volume", 1.0) if isinstance(snd, dict) else 1.0
        out[stem] = float(vol)
    return out


def sample_peak(pkg, stem):
    """Пик файла сэмпла, dBFS. None — файла нет или нет soundfile."""
    try:
        import io
        import numpy as np
        import soundfile as sf
    except ImportError:
        return None
    raw = _find_sample_bytes(pkg, stem)
    if raw is None:
        return None
    x, _sr = sf.read(io.BytesIO(raw))
    if getattr(x, "ndim", 1) > 1:
        x = x.mean(axis=1)
    return 20.0 * math.log10(float(np.abs(x).max()) + 1e-12)


def declared_peak(entry):
    """Первый пик в dBFS, заявленный прозой спеки (`why`/`deviation`/`note`).

    Это единственное АБСОЛЮТНОЕ число, связывающее пакет с замером автора:
    0,731 в спеке — итоговая громкость, а «пик -7.38 dBFS» — замер S80.
    Проверка по нему не зависит от того, как читать targets_by_sample.
    """
    import re
    txt = " ".join(str(entry.get(k, "")) for k in ("why", "deviation", "note"))
    m = re.search(r"([-\u2212]?\d+[.,]\d+)\s*dBFS", txt)
    if not m:
        return None
    return float(m.group(1).replace(",", ".").replace("\u2212", "-"))


def peak_findings(entry, sounds, pkg, level_tol):
    """Пик события после множителей sounds.json против заявленного в спеке."""
    finds, notes = [], []
    targets = entry.get("targets_by_sample") or {}
    if not targets:
        return finds, notes
    event = entry.get("event", "")
    vol = event_volumes(sounds, event) or {}
    want = declared_peak(entry)
    if want is None:
        notes.append("%s: в спеке не заявлен пик в dBFS — абсолютный уровень "
                     "проверить нечем" % event)
        return finds, notes
    peaks = []
    for stem in targets:
        if stem not in vol:
            continue
        pk = sample_peak(pkg, stem)
        if pk is None:
            continue
        peaks.append(pk + db(vol[stem]))
    if not peaks:
        notes.append("%s: пики не посчитаны (нет .ogg или soundfile)" % event)
        return finds, notes
    got = max(peaks)
    d = got - want
    if abs(d) > level_tol:
        finds.append("%s: пик после множителей %.2f dBFS, а в спеке заявлен "
                     "%.2f dBFS (%.2f дБ) — пакет не на том уровне, что мерил "
                     "автор: отношение выровнено, а событие уведено"
                     % (event, got, want, d))
    return finds, notes


def load_spec(path):
    with open(path, "r", encoding="utf-8") as fh:
        sp = json.load(fh)
    return sp


# ------------------------------------------------------------------- расчёты
def call_site_multiplier(entry):
    """Множитель из кода. `no_code_multiplier` / нет поля → 1.0 по определению."""
    cs = entry.get("call_site") or {}
    if cs.get("kind") == "no_code_multiplier":
        return 1.0
    vol = cs.get("volume")
    return 1.0 if vol is None else float(vol)


def db(x):
    return 20.0 * math.log10(x) if x and x > 0 else float("-inf")


def check_event(entry, sounds, tol, level_tol, verbose=True):
    """Возвращает (находки[list[str]], замечания[list[str]])."""
    finds, notes = [], []
    event = entry.get("event", "")
    targets = entry.get("targets_by_sample") or {}
    if not targets:
        return finds, notes
    vols = event_volumes(sounds, event)
    if vols is None:
        finds.append("%s: события нет в sounds.json" % event)
        return finds, notes
    mult = call_site_multiplier(entry)

    missing = [s for s in targets if s not in vols]
    if missing:
        finds.append("%s: цели есть, сэмплов нет в sounds.json: %s"
                     % (event, ", ".join(sorted(missing))))

    rows = []
    for stem, target in sorted(targets.items()):
        vol = vols.get(stem)
        if vol is None:
            continue
        rows.append({
            "stem": stem,
            "json": vol,
            "cs": mult,
            "eff": vol * mult,
            "target": float(target),
            "req_json_if_json": float(target),
            "req_json_if_eff": float(target) / mult if mult else float("inf"),
        })

    ok_json = all(abs(r["json"] - r["target"]) <= tol for r in rows) if rows else False
    ok_eff = all(abs(r["eff"] - r["target"]) <= tol for r in rows) if rows else False

    if verbose:
        print("%s   (call_site ×%g, tolerance %g)" % (event, mult, tol))
        print("   %-28s %10s %10s %10s %10s" %
              ("сэмпл", "volume", "эффект.", "цель", "статус"))
        for r in rows:
            if abs(r["eff"] - r["target"]) <= tol:
                st = "ok (effective)"
            elif abs(r["json"] - r["target"]) <= tol:
                st = "ok (json)"
            else:
                st = "ВНЕ ДОПУСКА"
            print("   %-28s %10.3f %10.3f %10.3f   %s"
                  % (r["stem"], r["json"], r["eff"], r["target"], st))
        if ok_json and ok_eff:
            print("   семантика: удовлетворяет ОБЕИМ (числа совпали случайно)")
        elif ok_json:
            print("   семантика: пакет соответствует «json»")
        elif ok_eff:
            print("   семантика: пакет соответствует «effective»")
        else:
            print("   семантика: НЕ соответствует ни одной")

    if not (ok_json or ok_eff):
        for r in rows:
            finds.append(
                "%s/%s: volume %.3f (эффект. %.3f) — цель %.3f; "
                "нужно volume %.3f при семантике «json» либо %.3f при «effective»"
                % (event, r["stem"], r["json"], r["eff"], r["target"],
                   r["req_json_if_json"], r["req_json_if_eff"]))

    # уровень события против доски — замечание, не норма
    bt = entry.get("board_target")
    if bt and rows:
        loud = max(r["eff"] for r in rows)
        d = db(loud / float(bt))
        if abs(d) > level_tol:
            notes.append("%s: наигромчайшая эффективная %.3f при board_target %.3f "
                         "(%.2f дБ) — %s"
                         % (event, loud, float(bt), d,
                            "объявлено deviation" if entry.get("deviation")
                            else "deviation НЕ объявлено — норма доски нарушена"))
    return finds, notes


def half_fix_findings(entry, sounds, base_sounds, tol):
    """Правка применена не ко всей паре: цель требует смены, ключ остался базовым."""
    finds = []
    event = entry.get("event", "")
    targets = entry.get("targets_by_sample") or {}
    if not targets:
        return finds
    vols = event_volumes(sounds, event) or {}
    base = event_volumes(base_sounds, event) or {}
    mult = call_site_multiplier(entry)
    changed = [s for s in targets if s in vols and s in base
               and abs(vols[s] - base[s]) > tol]
    for stem, target in sorted(targets.items()):
        if stem not in vols or stem not in base:
            continue
        need_json = float(target) / mult if mult else float("inf")
        need_change = abs(need_json - base[stem]) > tol
        untouched = abs(vols[stem] - base[stem]) <= tol
        if need_change and untouched:
            finds.append(
                "%s/%s: половинчатая правка — по спеке нужно volume %.3f "
                "(было %.3f), ключ оставлен базовым %.3f; в событии уже "
                "изменён(ы): %s"
                % (event, stem, need_json, base[stem], vols[stem],
                   ", ".join(changed) if changed else "никто"))
    return finds


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(
        description="Семантика targets_by_sample + сторож половинчатой правки")
    ap.add_argument("--pkg", required=True, help="каталог или ZIP проверяемого пакета")
    ap.add_argument("--spec", default=DEFAULT_SPEC, help="volume_spec*.json")
    ap.add_argument("--baseline", default=None,
                    help="предыдущий принятый пакет — для сторожа половинчатой правки")
    ap.add_argument("--tol", type=float, default=0.005, help="допуск по громкости")
    ap.add_argument("--strict-label", dest="strict_label", action="store_true",
                    help="расхождение метки targets_mode и пакета считать находкой, "
                         "а не замечанием")
    ap.add_argument("--worse-tol", dest="worse_tol", type=float, default=0.5,
                    help="на сколько дБ разброс пары может вырасти, прежде чем это находка")
    ap.add_argument("--level-tol", dest="level_tol", type=float, default=3.0,
                    help="допуск уровня события против board_target, дБ")
    a = ap.parse_args()

    if not os.path.isfile(a.spec):
        print("НЕ ПРОВЕРЕНО: нет спеки %s" % a.spec)
        return 3
    try:
        sounds = load_sounds(a.pkg)
    except SystemExit as exc:
        print(exc)
        return 3
    base_sounds = None
    if a.baseline:
        try:
            base_sounds = load_sounds(a.baseline)
        except SystemExit:
            print("НЕ ПРОВЕРЕНО: в базовом пакете %s нет sounds.json" % a.baseline)
            return 3

    sp = load_spec(a.spec)
    mode = sp.get("targets_mode", "json")
    print("пакет: %s" % a.pkg)
    print("спека: %s — объявленная семантика targets_mode = %r\n" % (a.spec, mode))

    finds, notes = [], []
    for entry in sp.get("events", []):
        f, n = check_event(entry, sounds, a.tol, a.level_tol)
        finds += f
        notes += n
        f3, n3 = peak_findings(entry, sounds, a.pkg, a.level_tol)
        finds += f3
        notes += n3
        if base_sounds is not None:
            finds += half_fix_findings(entry, sounds, base_sounds, a.tol)
            f2, n2 = spread_findings(entry, sounds, base_sounds,
                                     a.pkg, a.baseline, a.worse_tol)
            finds += f2
            notes += n2
        print()

    # согласованность метки и пакета
    for entry in sp.get("events", []):
        targets = entry.get("targets_by_sample") or {}
        if not targets:
            continue
        vols = event_volumes(sounds, entry.get("event", "")) or {}
        if not vols:
            continue
        mult = call_site_multiplier(entry)
        rows = [(vols[s], s) for s in targets if s in vols]
        ok_json = all(abs(v - float(targets[s])) <= a.tol for v, s in rows)
        ok_eff = all(abs(v * mult - float(targets[s])) <= a.tol for v, s in rows)
        msg = None
        if ok_eff and not ok_json and mode == "json":
            msg = ("%s: метка targets_mode=%r, а пакет соответствует семантике "
                   "«effective» — править метку в спеке (числа в "
                   "targets_by_sample заданы как итоговая громкость, "
                   "call_site ×= %g)" % (entry.get("event"), mode, mult))
        if ok_json and not ok_eff and mode == "effective":
            msg = ("%s: метка targets_mode=%r, а пакет соответствует семантике "
                   "«json» — править метку в спеке" % (entry.get("event"), mode))
        if msg:
            (finds if a.strict_label else notes).append(msg)

    print("-" * 78)
    if notes:
        print("ЗАМЕЧАНИЯ (%d):" % len(notes))
        for n in notes:
            print("  · " + n)
    if finds:
        print("НАХОДКИ (%d):" % len(finds))
        for f in finds:
            print("  ✗ " + f)
        print("ИТОГ: ЕСТЬ НАХОДКИ")
        return 2
    print("ИТОГ: СХОДИТСЯ — цели по сэмплам выполнены, метка согласована,"
          " половинчатых правок нет")
    return 0


if __name__ == "__main__":
    sys.exit(main())
