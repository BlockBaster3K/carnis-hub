#!/usr/bin/env python3
"""Уровни банка БЕЗ PyAV: клиппинг, потолок −1.20 dBFS и crest — на libsndfile.

Зачем этот инструмент, если клиппинг уже проверяется в гейтах.

`accept_3.7.3/3.8.0` считают клиппинг через **PyAV** и после З-Г1 закрыты
fail-closed: нет `av` → провал. Это правильно, но у fail-closed есть обратная
сторона, которую никто не проверил: **если PyAV нет в окружении агента, гейт
уровней красный на ЛЮБОМ пакете** — и звук не может ни принять, ни забраковать
по существу. В этом окружении `import av` падает, то есть проверить пик мне
сейчас нечем, хотя файлы декодируются libsndfile.

Поэтому здесь второй, независимый путь: `soundfile` (libsndfile). Он не
заменяет гейт — он позволяет звуку работать, когда PyAV недоступен, и
перекрёстно проверять гейт, когда доступен.

Нормы (те же, не свои):
  * клиппинг — отсчётов |x| >= 1.0 быть не должно (0 %);
  * потолок T-3182 §1 (З-21) — пик <= −1.20 dBFS, запас >= 0.20 дБ;
  * crest — 20·log10(пик/RMS), сравнивается с мастером при `--masters`.

Fail-closed по З-Г1: отсутствие декодера — это код 3 («не проверено»),
а не 0 («чисто»). Отдельно `--selfcheck` доказывает это экспериментом:
подсовывает пустой модуль soundfile и требует, чтобы прогон упал с кодом 3.

Коды возврата:
  0 — проверено, отклонений нет
  2 — проверено, есть отклонения (печатает список)
  3 — не проверено (нет декодера / нет банка / нет мастеров)
"""
import argparse
import json
import math
import os
import sys
import tempfile

CEIL_DB = -1.20      # T-3182 §1: потолок пика
MARGIN_DB = 0.20     # запас под регулятор громкости в игре
# Норма crest (З-29, уточнённая в S33): допуск = max(порог_типа, baseline + 0.05).
# Сырое сравнение «файл против мастера» с ногой 0.02 дБ — НЕВЕРНО: OGG Vorbis
# добавляет на декоде пики, и crest растёт даже при чистом транскоде. В S23
# измерено: 73 из 144 ПРИНЯТЫХ файлов канона дают Δcrest > 0.05 дБ без всякой
# правки громкости (медиана 0.050, максимум 0.548). Поэтому нужен baseline —
# Δcrest СОБСТВЕННОГО чистого транскода файла, он и есть шум кодека.
FORM_ADD = 0.05      # надбавка к baseline, дБ
TOL_STAT = 0.05      # порог типа: стационарные
TOL_TRANS = 0.60     # порог типа: транзиентные
STAT_MIN_DUR = 2.0   # >= 2 с без атаки — стационарный (как в crest_baseline)


def _load_sf():
    try:
        import soundfile  # noqa: F401
        return soundfile
    except ImportError:
        return None


def _measure(sf, path):
    """(пик, dBFS пика, crest дБ, число отсчётов в клиппинге, SR, длина)."""
    import numpy as np
    x, sr = sf.read(path, dtype="float64", always_2d=False)
    if x.ndim > 1:
        x = x.max(axis=1)          # моно-норма проверяется отдельно (mono_norm_check)
    if x.size == 0:
        return None
    peak = float(np.abs(x).max())
    rms = float(np.sqrt((x ** 2).mean()))
    clipped = int(np.count_nonzero(np.abs(x) >= 1.0))
    crest = (20 * math.log10(peak) - 20 * math.log10(rms)) if peak > 0 and rms > 0 else None
    peak_db = 20 * math.log10(peak) if peak > 0 else None
    return {"peak": peak, "peak_db": peak_db, "crest": crest,
            "clipped": clipped, "sr": int(sr), "dur": len(x) / float(sr)}


def _baseline_dcrest(sf, path, tmpdir):
    """Δcrest чистого транскода (файл → тот же OGG 160k) = шум кодека.

    Это не «второй замер ради галочки»: без него норма валит принятые файлы.
    """
    import numpy as np
    x, sr = sf.read(path, dtype="float64", always_2d=False)
    if x.ndim > 1:
        x = x.max(axis=1)
    if x.size == 0:
        return None
    _cr = lambda y: (20 * math.log10(float(np.abs(y).max()))
                     - 20 * math.log10(float(np.sqrt((y ** 2).mean())))
                     if np.abs(y).max() > 0 and np.sqrt((y ** 2).mean()) > 0 else None)
    c0 = _cr(x)
    if c0 is None:
        return None
    tmp = os.path.join(tmpdir, "rt.ogg")
    try:
        sf.write(tmp, x, sr, format="OGG", subtype="VORBIS")
        y, _ = sf.read(tmp, dtype="float64", always_2d=False)
    except Exception:                                  # noqa: BLE001
        return None
    if y.ndim > 1:
        y = y.max(axis=1)
    c1 = _cr(y)
    if c1 is None:
        return None
    return abs(c1 - c0)


def _is_transient(crest, dur):
    """Транзиентный — короткий ИЛИ с высоким crest (удар, а не ровный фон)."""
    return dur < STAT_MIN_DUR or (crest is not None and crest >= 12.0)


def _collect(bank):
    out = []
    for dp, _, fs in os.walk(bank):
        for f in sorted(fs):
            if f.lower().endswith(".ogg"):
                out.append(os.path.join(dp, f))
    return sorted(out)


def _index_masters(masters):
    """{имя_без_расширения: путь} — мастера ищем по ИМЕНИ, не по relpath.

    Первая версия склеивала `masters/<relpath>`, а в банке каталог называется
    `entity/`, в мастерах — тоже `entity/`, но сравнение шло с путём внутри
    банка, включая подкаталоги, и не совпало у ВСЕХ 132 файлов. При этом
    итог всё равно печатался «в норме» — см. правку ниже: файл без мастера
    НЕ может считаться проверенным по crest.
    """
    idx = {}
    for dp, _, fs in os.walk(masters):
        for f in sorted(fs):
            stem, ext = os.path.splitext(f)
            if ext.lower() in (".flac", ".wav", ".ogg"):
                idx.setdefault(stem, os.path.join(dp, f))
    return idx


def run(bank, masters, json_out, quiet):
    sf = _load_sf()
    if sf is None:
        print("ОШИБКА: нет soundfile — уровни НЕ ПРОВЕРЕНЫ. Это не «чисто».")
        print("        (fail-closed по З-Г1: код 3)")
        return 3
    if not os.path.isdir(bank):
        print("ОШИБКА: банк %s отсутствует — НЕ ПРОВЕРЕНО." % bank)
        return 3

    files = _collect(bank)
    if not files:
        print("ОШИБКА: в %s нет .ogg — НЕ ПРОВЕРЕНО." % bank)
        return 3

    tmpdir = tempfile.mkdtemp(prefix="rt_")
    rows, unread = [], []
    for p in files:
        rel = os.path.relpath(p, bank)
        try:
            m = _measure(sf, p)
        except Exception as exc:                      # noqa: BLE001
            unread.append((rel, str(exc)[:70]))
            continue
        if m is None:
            unread.append((rel, "0 отсчётов"))
            continue
        m["file"] = rel
        rows.append(m)

    bad_clip = [r for r in rows if r["clipped"] > 0]
    bad_ceil = [r for r in rows if r["peak_db"] is not None
                and r["peak_db"] > CEIL_DB]
    # запас: пик выше (CEIL_DB − MARGIN_DB) — потолок есть, но допуска уже нет
    thin = [r for r in rows if r["peak_db"] is not None
            and r["peak_db"] > CEIL_DB - MARGIN_DB and r["clipped"] == 0]

    lost = []
    if masters:
        if not os.path.isdir(masters):
            print("ОШИБКА: мастеров %s нет — crest НЕ ПРОВЕРЕН." % masters)
            return 3
        midx = _index_masters(masters)
        if not midx:
            print("ОШИБКА: в %s нет мастеров — crest НЕ ПРОВЕРЕН." % masters)
            return 3
        for r in rows:
            stem = os.path.splitext(os.path.basename(r["file"]))[0]
            mp = midx.get(stem)
            if mp is None:
                lost.append((r["file"], "нет мастера"))
                continue
            try:
                mm = _measure(sf, mp)
            except Exception as exc:                  # noqa: BLE001
                lost.append((r["file"], "мастер не читается: %s" % str(exc)[:40]))
                continue
            if mm is None or mm["crest"] is None or r["crest"] is None:
                lost.append((r["file"], "нет crest"))
                continue
            r["master_crest"] = mm["crest"]
            r["dcrest"] = abs(r["crest"] - mm["crest"])
            r["master_file"] = os.path.relpath(mp, masters)
            r["baseline"] = _baseline_dcrest(sf, os.path.join(bank, r["file"]),
                                             tmpdir)
            r["transient"] = _is_transient(mm["crest"], mm["dur"])
            base = r["baseline"] if r["baseline"] is not None else 0.0
            r["tol"] = max(TOL_TRANS if r["transient"] else TOL_STAT,
                           base + FORM_ADD)
    bad_crest = [r for r in rows if r.get("dcrest") is not None
                 and r["dcrest"] > r["tol"]]

    peaks = [r["peak_db"] for r in rows if r["peak_db"] is not None]
    crests = [r["crest"] for r in rows if r["crest"] is not None]

    if not quiet:
        print("банк: %s — файлов %d, декодировано %d, не прочитано %d"
              % (bank, len(files), len(rows), len(unread)))
        print("пик: max %.2f dBFS, min %.2f dBFS (потолок %.2f)"
              % (max(peaks) if peaks else 0, min(peaks) if peaks else 0, CEIL_DB))
        print("crest: min %.2f, медиана %.2f, max %.2f дБ"
              % (min(crests) if crests else 0,
                 sorted(crests)[len(crests) // 2] if crests else 0,
                 max(crests) if crests else 0))
        print()
        print("клиппинг (>= 1.0): %d файлов" % len(bad_clip))
        for r in bad_clip[:10]:
            print("  %-46s %d отсч., пик %+.2f dBFS"
                  % (r["file"], r["clipped"], r["peak_db"]))
        print("выше потолка %.2f dBFS: %d файлов" % (CEIL_DB, len(bad_ceil)))
        for r in sorted(bad_ceil, key=lambda t: -t["peak_db"])[:10]:
            print("  %-46s пик %+.2f dBFS" % (r["file"], r["peak_db"]))
        print("запас < %.2f дБ (пик выше %.2f): %d файлов"
              % (MARGIN_DB, CEIL_DB - MARGIN_DB, len(thin)))
        for r in sorted(thin, key=lambda t: -t["peak_db"])[:10]:
            print("  %-46s пик %+.2f dBFS" % (r["file"], r["peak_db"]))
        if masters:
            print("crest вне допуска З-29 (max(порог, baseline+%.2f)): %d файлов"
                  % (FORM_ADD, len(bad_crest)))
            for r in sorted(bad_crest, key=lambda t: t["dcrest"] - t["tol"])[:10]:
                print("  %-44s Δ %.3f > допуск %.3f (baseline %.3f, %s)"
                      % (r["file"], r["dcrest"], r["tol"],
                         r["baseline"] if r["baseline"] is not None else -1,
                         "транз" if r["transient"] else "стац"))
            over = sum(1 for r in rows if r.get("dcrest") is not None
                       and r["dcrest"] > FORM_ADD)
            print("  (для контекста: сырых Δ > %.2f дБ — %d файлов, это шум кодека,"
                  " не провал)" % (FORM_ADD, over))
            print("нет мастера: %d файлов" % len(lost))
            for rel, why in lost[:6]:
                print("  %-46s %s" % (rel, why))
        if unread:
            print("НЕ ДЕКОДИРОВАНЫ: %d" % len(unread))
            for rel, why in unread[:6]:
                print("  %-46s %s" % (rel, why))
            print("  ⚠ не прочитанный файл не может считаться «в норме» — его")
            print("    уровни НЕИЗВЕСТНЫ; это провал проверки, а не пропуск.")
        print()

    problems = (len(unread) + len(bad_clip) + len(bad_ceil) + len(bad_crest))
    if json_out:
        print(json.dumps({
            "bank": bank, "total": len(files), "decoded": len(rows),
            "unread": [{"file": r, "why": w} for r, w in unread],
            "clip": [r["file"] for r in bad_clip],
            "over_ceiling": [{"file": r["file"], "peak_db": r["peak_db"]}
                             for r in bad_ceil],
            "thin_margin": [{"file": r["file"], "peak_db": r["peak_db"]}
                            for r in thin],
            "crest_off": [{"file": r["file"], "dcrest": r["dcrest"]}
                          for r in bad_crest],
            "no_master": [r for r, _ in lost],
        }, ensure_ascii=False, indent=1))

    if problems:
        print("ИТОГ: отклонений %d (клиппинг %d, потолок %d, crest %d, не прочитано %d)"
              % (problems, len(bad_clip), len(bad_ceil), len(bad_crest), len(unread)))
        if lost:
            print("      плюс %d файлов БЕЗ мастера — их crest не проверен" % len(lost))
        return 2
    if lost:
        # Файл без мастера нельзя назвать «в норме по crest»: сравнивать не с
        # чем. Печатаем это как НЕ ПРОВЕРЕНО, а не как ноль отклонений —
        # иначе «132 файла в норме» означало бы «132 файла никто не смотрел».
        print("ИТОГ: уровни в норме (клиппинг 0, потолок %.2f), но crest НЕ ПРОВЕРЕН "
              "у %d из %d файлов — нет мастера" % (CEIL_DB, len(lost), len(rows)))
        print("      код 3: «не проверено», а не «чисто» (З-Г1)")
        return 3
    print("ИТОГ: все %d файлов в норме (клиппинг 0, потолок %.2f, crest 0)"
          % (len(rows), CEIL_DB))
    return 0


def selfcheck(bank):
    """Доказать экспериментом, что без декодера инструмент ПАДАЕТ (З-Г1).

    Первая версия этой самопроверки была НЕВЕРНА: она подменяла PYTHONPATH в
    том же процессе, а `soundfile` к тому моменту уже лежал в `sys.modules` —
    подмена ни на что не влияла, прогон 2 вернул 0, и проверка «прошла» бы
    молча. Поэтому каждый прогон — ОТДЕЛЬНЫЙ ПРОЦЕСС: только так подменный
    пакет реально виден импорту.
    """
    import subprocess
    here = os.path.abspath(__file__)
    print("Самопроверка fail-closed (З-Г1)")

    def _run(env):
        r = subprocess.run([sys.executable, here, "--bank", bank, "--quiet"],
                           capture_output=True, text=True, timeout=600, env=env)
        return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]

    code, tail = _run(dict(os.environ))
    print("  прогон 1 — настоящий декодер:    код %d  %s" % (code, tail[0][:60]))
    if code not in (0, 2):
        print("  ⚠ ожидался 0 или 2 — банк не прочитан, самопроверке нечем")
        return 3

    tmp = tempfile.mkdtemp(prefix="nofile_")
    with open(os.path.join(tmp, "soundfile.py"), "w", encoding="utf-8") as f:
        f.write('raise ImportError("selfcheck: декодер недоступен")\n')
    env2 = dict(os.environ)
    env2["PYTHONPATH"] = tmp + (os.pathsep + env2["PYTHONPATH"]
                                if env2.get("PYTHONPATH") else "")
    code2, tail2 = _run(env2)
    print("  прогон 2 — подменный soundfile:   код %d  %s" % (code2, tail2[0][:60]))

    # Контроль самого контроля: подмена обязана ЛОМАТЬ импорт. Если прогон 2
    # дал 0/2, значит подмена не сработала, и «доказательство» ничего не стоит.
    probe = subprocess.run([sys.executable, "-c", "import soundfile"],
                           capture_output=True, text=True, env=env2, timeout=60)
    if probe.returncode == 0:
        print("  ✗ подменный пакет НЕ блокирует импорт — опыт недействителен")
        return 3

    if code2 == 0:
        print("  ✗ ПРОВАЛ: без декодера вернулось 0 — это fail-OPEN")
        return 2
    if code2 != 3:
        print("  ✗ ПРОВАЛ: без декодера код %d, ожидался 3 («не проверено»)" % code2)
        return 2
    print("  ✓ fail-closed: без декодера код 3, а не 0 — «не проверено», не «чисто»")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", help="каталог банка с .ogg")
    ap.add_argument("--masters", help="каталог мастеров для crest (flac/wav)")
    ap.add_argument("--json", action="store_true", dest="json_out")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selfcheck", action="store_true",
                    help="доказать fail-closed без декодера и выйти")
    a = ap.parse_args(argv)
    if a.selfcheck:
        if not a.bank:
            ap.error("--selfcheck требует --bank")
        return selfcheck(a.bank)
    if not a.bank:
        ap.error("нужен --bank")
    return run(a.bank, a.masters, a.json_out, a.quiet)


if __name__ == "__main__":
    sys.exit(main())
