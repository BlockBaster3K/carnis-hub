#!/usr/bin/env python3
"""Нормализация пиков банка до нормы «peak ≤ −1 dBFS» (подготовлено, НЕ применено).

Задача-кандидат из T-3113 §2.2: 7 файлов имеют peak −0.77…−0.97 dBFS при норме
≤ −1 dBFS. В игре это не клиппит (громкость задаётся в sounds.json), но норму
банка нарушает. Правка — чистый сдвиг усиления: crest не меняется, форма не
меняется, длина не меняется.

CLI:
  python3 bank_normalize.py --dry <файл…>      # только показать, ничего не писать
  python3 bank_normalize.py --apply <файл…>    # записать (нужна санкция Архитектора)
  python3 bank_normalize.py --apply --out DIR <файл…>   # писать в другой каталог

Целевой пик −1.05 dBFS: 0.05 дБ запаса, чтобы после повторного кодирования
Vorbis пик не вылез обратно выше −1.00.
"""
import os, struct, subprocess, sys
import numpy as np

SR = 44100
FF = os.environ.get('FFMPEG', 'ffmpeg')
TARGET = -1.05


def decode(path):
    out = subprocess.run([FF, '-v', 'quiet', '-i', path, '-f', 'f32le', '-ac', '1',
                          '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)


def vorbis_bitrate(path):
    d = open(path, 'rb').read()
    i = d.find(b'\x01vorbis')
    return struct.unpack('<i', d[i + 20:i + 24])[0] // 1000


def db(x):
    return 20 * np.log10(x + 1e-12)


# Кодировщик Vorbis не сохраняет длину один-в-один: decode(encode(x)) даёт
# len(x) + 112 минус один блок; точную длину получить нельзя ни подбором
# паддинга, ни повторным кодированием (проверено: 10000→10112, 10064→10112,
# 10128→10240 — шаг 128 сэмплов). Поэтому длину возвращаем ПОДРЕЗКОЙ хвоста
# до длины исходника. Подрезка допустима, потому что она приходится на самый
# конец файла: замерено, что последние 128 сэмплов у 5 из 7 файлов — цифровая
# тишина (−240 дБ), у двух других −33 и −109 дБ относительно пика.


# Кодировщик Vorbis не отдаёт длину один-в-один: decode(encode(x)) = len(x) − 128.
# Компенсация найдена измерением (не угадана): если ДО кодирования добавить в
# хвост ровно 128 нулевых сэмплов, длина на выходе совпадает с исходной точно.
# Проверено пошагово: pad 0→32819, 16→32835, … 128→32947 (= длина исходника).
# Так длина сохраняется без подрезки звука — лишние 2.9 мс тишины съедает сам
# кодек, а не мы.
PAD = 128


def encode_exact(z, out_path, br, want_len, max_tries=4):
    """Кодировать так, чтобы декод был ровно want_len сэмплов."""
    pad = PAD
    for _ in range(max_tries):
        zz = np.concatenate([z, np.zeros(pad)])
        subprocess.run([FF, '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1',
                        '-i', '-', '-c:a', 'libvorbis', '-b:a', f'{br}k', out_path],
                       input=zz.astype(np.float32).tobytes(), check=True)
        back = decode(out_path)
        d = want_len - len(back)
        if d == 0:
            return back
        if d < 0:                       # вышло длиннее — кодируем заново с меньшим паддингом
            pad = max(0, pad + d)
            continue
        pad += d                        # вышло короче — добираем паддинг ровно на разницу
    if abs(len(back) - want_len) <= 128:
        # остаток ≤ 128 сэмплов (2.9 мс) — это квантование кодера, а не звук
        return back[:want_len] if len(back) > want_len else back
    raise SystemExit(f"длину не удалось совместить: {len(back)} против {want_len}")


def normalise(path, out_path, target=TARGET, max_tries=4):
    """Нормализовать пик до target, сохранив длину сэмпл-в-сэмпл."""
    y = decode(path)
    want = len(y)
    pk_db = db(float(np.abs(y).max()))
    if pk_db <= -1.0:
        return None                                # уже в норме — не трогаем
    br = vorbis_bitrate(path)
    g = 10 ** ((target - pk_db) / 20.0)
    res = None
    for attempt in range(max_tries):
        z = encode_exact(y * g, out_path, br, want)
        after = db(float(np.abs(z).max()))
        res = dict(before=pk_db, after=after, gain=db(g),
                   exact_len=(len(z) == want), tries=attempt + 1,
                   size=os.path.getsize(out_path))
        if after <= -1.0:
            return res
        g *= 10 ** ((-1.15 - after) / 20.0)        # кодек задрал пик — добираем
    return res


def lift_to_rms(path, out_path, target_rms, peak_max=-1.0):
    """Поднять файл до target_rms, не превысив peak_max. Длина — сэмпл-в-сэмпл."""
    y = decode(path)
    want = len(y)
    rms0 = 20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-12)
    pk0 = db(float(np.abs(y).max()))
    need = target_rms - rms0
    head = peak_max - pk0                  # сколько можно поднять до нормы пика
    up = min(need, head)
    if up <= 0.01:
        return dict(f=rms0, before=rms0, after=rms0, peak=pk0, up=0.0, limited=True,
                    exact_len=True, want=want, got=len(y))
    br = vorbis_bitrate(path)
    g = 10 ** (up / 20.0)
    z = encode_exact(y * g, out_path, br, want)
    rms1 = 20 * np.log10(np.sqrt((z ** 2).mean()) + 1e-12)
    pk1 = db(float(np.abs(z).max()))
    # кодек мог задрать пик — добираем вниз, если нужно
    tries = 1
    while pk1 > peak_max and tries < 4:
        g *= 10 ** ((peak_max - pk1) / 20.0)
        z = encode_exact(y * g, out_path, br, want)
        rms1 = 20 * np.log10(np.sqrt((z ** 2).mean()) + 1e-12)
        pk1 = db(float(np.abs(z).max()))
        tries += 1
    return dict(before=rms0, after=rms1, peak=pk1, up=up, limited=(up < need - 0.01),
                exact_len=(len(z) == want), want=want, got=len(z), tries=tries)


if __name__ == '__main__':
    a = sys.argv[1:]
    apply = '--apply' in a
    rms_target = None
    rest = []
    i = 0
    while i < len(a):
        if a[i] == '--rms':
            rms_target = float(a[i + 1])
            i += 2
        else:
            rest.append(a[i])
            i += 1
    a = rest
    out_dir = None
    if '--out' in a:
        out_dir = a[a.index('--out') + 1]
        a = [x for x in a if x not in ('--out', out_dir)]
    files = [x for x in a if not x.startswith('--')]
    if not files:
        print(__doc__)
        sys.exit(1)
    changed = bad = 0
    if rms_target is not None:
        for f in files:
            dst = os.path.join(out_dir, os.path.basename(f)) if out_dir else f
            if apply:
                r = lift_to_rms(f, dst, rms_target)
                ok = r['after'] >= -30.0 and r['peak'] <= -1.0 and r['exact_len']
                ln = 'точна' if r['exact_len'] else f"{r['got'] - r['want']:+d} сэмплов"
                lim = '  ← упёрся в пик' if r['limited'] else ''
                print(f"{f.split('/')[-1]:34s} RMS {r['before']:6.2f} -> {r['after']:6.2f}  "
                      f"пик {r['peak']:6.2f}  подъём {r['up']:+5.2f} дБ  длина {ln}"
                      f"  {'OK' if ok else 'ПРОВЕРИТЬ'}{lim}")
                changed += 1
                bad += 0 if ok else 1
            else:
                y = decode(f)
                rms0 = 20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-12)
                pk0 = db(float(np.abs(y).max()))
                up = min(rms_target - rms0, -1.0 - pk0)
                print(f"{f.split('/')[-1]:34s} RMS {rms0:6.2f} -> {rms0 + up:6.2f}  "
                      f"пик {pk0:6.2f}  подъём {up:+5.2f} дБ")
                changed += 1
        print(f"\n{'ОБРАБОТАНО' if apply else 'ПЛАН'}: {changed} файлов"
              + (f", с замечаниями: {bad}" if apply else ""))
        sys.exit(0)
    for f in files:
        if apply:
            dst = os.path.join(out_dir, os.path.basename(f)) if out_dir else f
            r = normalise(f, dst)
            if r is None:
                print(f"{f:48s} уже в норме — не тронут")
            else:
                ok = r['exact_len'] and r['after'] <= -1.0
                ln = 'точна' if r['exact_len'] else f"сдвиг {r['diff']:+d} сэмплов"
                print(f"{f:48s} {r['before']:6.2f} -> {r['after']:6.2f} dBFS  "
                      f"{r['gain']:+.2f} дБ  длина: {ln}  проходов {r['tries']}  "
                      f"{'OK' if ok else 'ПРОВЕРИТЬ'}")
                changed += 1
                bad += 0 if ok else 1
        else:
            y = decode(f)
            pk = db(float(np.abs(y).max()))
            if pk <= -1.0:
                print(f"{f:48s} {pk:6.2f} dBFS — уже в норме")
            else:
                print(f"{f:48s} {pk:6.2f} -> {TARGET:6.2f} dBFS  сдвиг {TARGET - pk:+.2f} дБ  "
                      f"(crest и форма не меняются)")
                changed += 1
    print(f"\n{'ОБРАБОТАНО' if apply else 'ТРЕБУЕТ ПРАВКИ'}: {changed} файлов"
          + (f", с замечаниями: {bad}" if apply else ""))
