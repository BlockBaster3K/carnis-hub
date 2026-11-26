#!/usr/bin/env python3
"""Покрытие событий: sounds.json ↔ банк, и звуки в пакете vs в банке.

Пункт 3 задачи T-3180 и постоянный шаг S16 («побайтовая сверка пакета с банком
ДО приёмки, а не после»).

Проверки:
  1. Каждое событие `sounds.json` ссылается на существующий `.ogg` (в пакете/банке).
  2. Каждый `.ogg` банка упомянут хотя бы одним событием (сирот 0).
  3. `volume` и `pitch` в разумных пределах (0 < volume <= 4; 0.5 <= pitch <= 2).
  4. Если заданы оба (пакет и репозиторий) — перечислить ОТЛИЧИЯ содержимого,
     отдельно от «пакет отстал от правки р��позитория».

Коды: 0 — всё сходится; 2 — есть расхождения; 3 — проверить не удалось.
"""
import argparse
import json
import os
import sys
import zipfile

VOL_MAX = 4.0
PITCH_RANGE = (0.5, 2.0)


def load_json_from(pkg):
    """sounds.json из zip или каталога."""
    if pkg.endswith(".zip") and os.path.isfile(pkg):
        with zipfile.ZipFile(pkg) as z:
            name = [n for n in z.namelist()
                    if n.endswith("assets/carnis/sounds.json")]
            if not name:
                return None, None, "в архиве нет sounds.json"
            return json.loads(z.read(name[0])), {
                os.path.basename(n)[:-4] for n in z.namelist() if n.endswith(".ogg")
            }, None
    if os.path.isdir(pkg):
        p = os.path.join(pkg, "src", "main", "resources", "assets", "carnis",
                         "sounds.json")
        if not os.path.isfile(p):
            return None, None, "нет %s" % p
        ogg = set()
        for dp, _, fs in os.walk(pkg):
            for f in fs:
                if f.endswith(".ogg"):
                    ogg.add(f[:-4])
        return json.load(open(p, encoding="utf-8")), ogg, None
    return None, None, "нет такого каталога или zip: %s" % pkg


def norm(sj):
    out = {}
    for ev, node in sj.items():
        if not isinstance(node, dict):
            continue
        lst = []
        for s in node.get("sounds", []):
            if isinstance(s, dict):
                lst.append((s.get("name", ""), s.get("volume"), s.get("pitch")))
            else:
                lst.append((str(s), None, None))
        out[ev] = {"subtitle": node.get("subtitle"), "sounds": lst}
    return out


def check(pkg):
    sj, ogg, err = load_json_from(pkg)
    if err:
        return None, err
    d = norm(sj)
    refs = {}
    for ev, node in d.items():
        for name, vol, pitch in node["sounds"]:
            stem = name.split("/")[-1].replace(".ogg", "")
            refs.setdefault(stem, []).append(ev)
    dangling = {f: evs for f, evs in refs.items() if f not in ogg}
    orphan = sorted(ogg - set(refs))
    bad_vol, bad_pitch = [], []
    for ev, node in d.items():
        for name, vol, pitch in node["sounds"]:
            if vol is not None and not (0 < float(vol) <= VOL_MAX):
                bad_vol.append((ev, name, vol))
            if pitch is not None and not (PITCH_RANGE[0] <= float(pitch) <= PITCH_RANGE[1]):
                bad_pitch.append((ev, name, pitch))
    return {"events": len(d), "files": len(ogg), "refs": sum(len(v) for v in refs.values()),
            "dangling": dangling, "orphan": orphan, "bad_vol": bad_vol,
            "bad_pitch": bad_pitch, "norm": d}, None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", required=True)
    ap.add_argument("--repo", default=None,
                    help="исходники для сверки содержимого (каталог проекта)")
    a = ap.parse_args(argv)

    r, err = check(a.pkg)
    if err:
        print("ОШИБКА: %s" % err)
        return 3
    print("пакет: %s" % a.pkg)
    uniq = r["refs"]
    for ev, node in r["norm"].items():
        pass
    print("  событий %d | .ogg %d | ссылок %d" % (r["events"], r["files"], r["refs"]))
    problems = 0
    if r["dangling"]:
        problems += len(r["dangling"])
        print("  ✗ события ссылаются на отсутствующие файлы: %d" % len(r["dangling"]))
        for f, evs in list(r["dangling"].items())[:10]:
            print("      %s <- %s" % (f, ", ".join(evs)))
    if r["orphan"]:
        problems += len(r["orphan"])
        print("  ✗ файлы без события (сироты): %d" % len(r["orphan"]))
        for o in r["orphan"][:10]:
            print("      %s" % o)
    if r["bad_vol"]:
        problems += len(r["bad_vol"])
        print("  ✗ volume вне (0, %.0f]: %s" % (VOL_MAX, r["bad_vol"][:5]))
    if r["bad_pitch"]:
        problems += len(r["bad_pitch"])
        print("  ✗ pitch вне %s: %s" % (PITCH_RANGE, r["bad_pitch"][:5]))

    if a.repo:
        r2, err2 = check(a.repo)
        if err2:
            print("ОШИБКА сверки с %s: %s" % (a.repo, err2))
            return 3
        A, B = r["norm"], r2["norm"]
        only_pkg = sorted(set(A) - set(B))
        only_repo = sorted(set(B) - set(A))
        diffs = []
        for ev in sorted(set(A) & set(B)):
            if A[ev] != B[ev]:
                for i, (x, y) in enumerate(zip(A[ev]["sounds"], B[ev]["sounds"])):
                    if x != y:
                        diffs.append((ev, i, x, y))
                if len(A[ev]["sounds"]) != len(B[ev]["sounds"]):
                    diffs.append((ev, -1, "%d сэмплов" % len(A[ev]["sounds"]),
                                  "%d сэмплов" % len(B[ev]["sounds"])))
        print()
        print("сверка содержимого с %s:" % a.repo)
        print("  события только в пакете: %s" % (only_pkg or "нет"))
        print("  события только в репозитории: %s" % (only_repo or "нет"))
        if diffs:
            print("  ОТЛИЧИЙ: %d — пакет и исходники расходятся" % len(diffs))
            for ev, i, x, y in diffs:
                print("    %s [%s]:" % (ev, i))
                print("      пакет:      %s" % (x,))
                print("      репозиторий:%s" % (y,))
            print("  ⇒ приёмка проверяет ПАКЕТ. Пока он не пересобран, правки "
                  "исходников в игре отсутствуют.")
            problems += len(diffs)
        else:
            print("  совпадает полностью")

    if problems:
        print()
        print("ИТОГ: расхождений %d — покрытие НЕ подтверждено" % problems)
        return 2
    print()
    print("ИТОГ: СХОДИТСЯ — событий без файла 0, сирот 0, регуляторы в пределах")
    return 0


if __name__ == "__main__":
    sys.exit(main())
