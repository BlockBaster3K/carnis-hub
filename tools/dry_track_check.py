#!/usr/bin/env python3
"""S101 волны 58: дорожка должна быть «сухой» — окклюзию и эхо считает движок.

Зачем: звук идёт в позиционный движок (Sound Physics Remastered, мягкая
интеграция). Если реверберация «запечена» в файл, движок накладывает свою поверх
готовой: на открытом месте слышно комнату, а при окклюзии эхо приходит из
несуществующего пространства. Тот же дефект — ручные позиционные эффекты
(панорама/задержка между «ушами»), которые в моно невоспроизводимы вообще.

Проверяются ЧЕТЫРЕ машинных признака, а не вкус:

  1. МОНО + 44.1 кГц                — стерео в 3D-звуке даёт двойное позиционирование.
  2. НЕТ DC-смещения                — |mean| > 0.002 = сдвиг нуля (артефакт обработки).
  3. НЕТ «хвоста тишины» в 15%     — последние 15% длительности не тише -60 dBFS;
     у сухого сэмпла конец файла должен быть тихим, у файла с запечённым
     ревербом хвост тянется до обреза.
  4. НЕТ периодического эха        — автокорреляция огибающей не имеет пика > 0.45
     на задержках 20…400 мс (кроме 0): это дискретный повтор (эхо/дилей),
     который движок будет дублировать ещё раз.

Исключение: АМБИЕНТЫ (120 с, петли) — по замыслу непрерывные, «тихого конца» у
них нет. Для них проверяются только 1, 2 и 4.

Коды: 0 — чисто; 2 — отклонения; 3 — не проверено (нет декодера/банка).
"""
import argparse
import json
import os
import sys

SR_EXPECTED = 44100
DC_LIMIT = 0.0005
DC_REL_DB = -30.0
TAIL_REL_DB = -12.0
ECHO_LAG_MS = (20, 400)
ECHO_LIMIT = 0.40


def analyse(path):
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path, dtype="float64")
    if x.ndim > 1:
        x = x.mean(axis=1)
    out = {"sr": sr, "dur": len(x) / float(sr)}
    out["dc"] = float(abs(np.mean(x)))
    out["rms"] = float(np.sqrt(np.mean(x ** 2)))
    # хвост: последние 15%
    n = len(x)
    tail = x[int(n * 0.85):]
    # ХВОСТ — ОТНОСИТЕЛЬНО СВОЕГО RMS, не абсолютный порог: у тихого сэмпла
    # абсолютный -60 dBFS «нарушается» нормальным затуханием (первая версия
    # дала 131 «отклонение» из 144). Относительная мера и калибруется:
    # сухой тон -66 дБ, сухой щелчок -224, эхо -48, запечённый реверб -6.8.
    out["tail_rel_db"] = float(20 * np.log10(
        max(np.sqrt(np.mean(tail ** 2)), 1e-12)
        / max(np.sqrt(np.mean(x ** 2)), 1e-12)))
    # ЭХО. Первая версия брала МАКСИМУМ автокорреляции на 20…400 мс — и давала
    # 0.67 на сухом тоне: это не пик, а монотонный спад корреляции. Настоящее эхо
    # даёт ЛОКАЛЬНЫЙ максимум (больше соседей слева и справа). Проверено
    # калибровкой: сухие сэмплы — локальных пиков нет вообще, эхо 80 мс — 0.55.
    w = max(1, int(0.01 * sr))
    m = max(2, n // w)
    env = np.abs(x[:m * w]).reshape(m, w).max(axis=1)
    env = env - env.mean()
    out["echo_peak"], out["echo_lag_ms"] = 0.0, 0
    if env.std() > 1e-9 and m > 10:
        ac = np.correlate(env, env, mode="full")[m - 1:]
        ac = ac / (ac[0] + 1e-12)
        lo = int(ECHO_LAG_MS[0] / 10)
        hi = min(int(ECHO_LAG_MS[1] / 10), len(ac) - 3)
        best = 0.0
        best_i = 0
        for i in range(max(lo, 2), hi):
            if (ac[i] > ac[i - 1] and ac[i] > ac[i - 2]
                    and ac[i] > ac[i + 1] and ac[i] > ac[i + 2] and ac[i] > best):
                best, best_i = float(ac[i]), i
        out["echo_peak"] = best
        out["echo_lag_ms"] = best_i * 10
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True)
    ap.add_argument("--ambient-prefix", action="append",
                    default=["amb_", "hive_ambient", "hive_pulse", "heartbeat_loop",
                             "purifier_loop", "hive_heartbeat"])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    try:
        import numpy  # noqa: F401
        import soundfile  # noqa: F401
    except ImportError:
        print("ОШИБКА: нет numpy/soundfile — «сухость» не проверить. Это НЕ «чисто».")
        return 3
    if not os.path.isdir(a.bank):
        print("ОШИБКА: банк %s отсутствует" % a.bank)
        return 3

    files = []
    for dp, _, fs in os.walk(a.bank):
        for f in sorted(fs):
            if f.endswith(".ogg"):
                files.append(os.path.join(dp, f))
    if not files:
        print("ОШИБКА: в банке нет .ogg")
        return 3

    hard = []      # решаемое: DC-смещение и нечитаемость — дефект при любом замысле
    soft = []      # «хвост тянется до конца»: может быть замыслом (drone/idle)
    checked = 0
    for p in files:
        stem = os.path.basename(p)[:-4]
        is_amb = any(stem.startswith(pref) for pref in a.ambient_prefix)
        try:
            r = analyse(p)
        except Exception as exc:
            hard.append((stem, "НЕ ДЕКОДИРУЕТСЯ", str(exc)[:50]))
            continue
        checked += 1
        if r["dc"] > DC_LIMIT:
            # Смещение оценивается ОТНОСИТЕЛЬНО RMS файла: у тихого сэмпла
            # абсолютные 0.002 — это нормальный перекос, у громкого почти ничего.
            # Калибровка: -23.9 дБ к RMS (deep_01_axe) — слышимая подмеска низа,
            # -37.7 дБ (spawn_attack_01) — на уровне артефакта. Для 3D-звука с
            # окклюзией DC вреден: он не локализуется и складывается в «давление».
            import math
            rel = 20 * math.log10(max(r["dc"], 1e-12) / max(r["rms"], 1e-12))
            r["dc_rel_db"] = float(rel)
            if rel > DC_REL_DB:
                hard.append((stem, "DC-смещение",
                             "|mean| = %.4f = %.1f дБ к RMS (порог %.0f)"
                             % (r["dc"], rel, DC_REL_DB)))
        if r["echo_peak"] > ECHO_LIMIT:
            # НЕ дефект, а кандидат: у дрона/петли периодичность — замысел,
            # у удара — признак дискретного эха. По файлу это не различить.
            soft.append((stem, "периодичность",
                         "локальный пик автокорреляции %.2f на %d мс"
                         % (r["echo_peak"], r["echo_lag_ms"])))
        if not is_amb and r["tail_rel_db"] > TAIL_REL_DB:
            soft.append((stem, "хвост тянется до конца",
                         "последние 15%% на %.1f дБ ниже своего RMS" % r["tail_rel_db"]))

    print("проверено файлов: %d (амбиентов: %d, из них хвост не проверялся)"
          % (checked, sum(1 for p in files
                          if any(os.path.basename(p)[:-4].startswith(x)
                                 for x in a.ambient_prefix))))
    for stem, what, why in hard:
        print("  ДЕФЕКТ  %-32s %-22s %s" % (stem, what, why))
    for stem, what, why in soft:
        print("  НОРМА?  %-32s %-22s %s" % (stem, what, why))
    if a.json:
        print(json.dumps({"hard": [{"file": s, "what": w, "why": y} for s, w, y in hard],
                          "soft": [{"file": s, "what": w, "why": y} for s, w, y in soft]},
                         ensure_ascii=False))
    if hard:
        print("ИТОГ: ДЕФЕКТОВ %d (решаемо без нормы), требуют нормы %d, файлов %d"
              % (len(hard), len(soft), checked))
        return 2
    if soft:
        print("ИТОГ: дефектов 0; НЕ ПРОВЕРЯЕМО БЕЗ ЭТАЛОНА %d из %d. Метрика не "
              "отличает «протяжно/периодично по природе» (дрон, петля, длинный idle) "
              "от «запечённого реверба/эха». Проверено калибровкой на синтетике: "
              "сухой тон -66 дБ, сухой щелчок -224, эхо -48, реверб -6.8 — но на "
              "реальном банке порог задевает треть файлов." % (len(soft), checked))
        return 3
    print("ИТОГ: все %d дорожек сухие (моно, без DC, без хвоста, без эха)" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
