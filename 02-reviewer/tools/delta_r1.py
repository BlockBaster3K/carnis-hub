#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""delta_r1.py — дельта-гейт Ревизора для R1 (пакет 3.5.3, волна 29).

Проверяет ТОЛЬКО дельту после правки Кодера, без повторного пересчёта Д1–Д7:

  1. ZIP: размер, sha256, число файлов, внешний манифест (sha256 по каждому пути).
  2. `src` в репозитории побайтово равен `src` в ZIP (пакет не рассинхронизирован).
  3. Два файла R1: `cmp` с банком `03-sound/sounds/` — побайтовое совпадение,
     размер, sha256.
  4. Расклад по банку: сколько файлов совпадает, сколько расходится, сколько
     есть только в пакете / только в банке.
  5. Д2 заново: длительность пакетного `heartbeat_loop.ogg` в тиках против
     `soundDelay` 29–39 (нужно строго больше длины файла).
  6. Д1-запас: длительность `heart_pulse.ogg` против минимальной паузы 13 тиков.

Запуск:
    python3 02-reviewer/tools/delta_r1.py <project-3.5.3-clean.zip> \
        [--bank 03-sound/sounds] [--repo-src 01-coder/3.5.3/src]

Код возврата: 0 — дельта сошлась, 2 — нет. Длительности читаются через soundfile;
если его нет, используется разбор Ogg-страниц (только для Vorbis).
"""
import argparse
import hashlib
import os
import shutil
import sys
import tempfile
import zipfile

R1_FILES = ['block/heart_pulse.ogg', 'block/heartbeat_loop.ogg']
MIN_HEARTBEAT_INTERVAL_TICKS = 13     # Д1, из FleshBulbBlockEntity
SOUND_DELAY_RANGE = (29, 39)          # Д2, из PlayerHallucinationHandler
TICKS_PER_SECOND = 20.0


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def ogg_duration_fallback(path):
    """Длительность Vorbis из Ogg-страниц: max granulepos / sample_rate."""
    data = open(path, 'rb').read()
    rate = None
    last_granule = 0
    i = 0
    while i + 27 <= len(data):
        if data[i:i + 4] != b'OggS':
            i += 1
            continue
        granule = int.from_bytes(data[i + 6:i + 14], 'little')
        nseg = data[i + 26]
        headers = data[i + 27:i + 27 + nseg]
        body = i + 27 + nseg
        first_body = data[body:body + 16]
        if first_body[:1] == b'\x01' and first_body[1:7] == b'vorbis' and rate is None:
            rate = int.from_bytes(first_body[12:16], 'little')
        if granule > last_granule:
            last_granule = granule
        i = body + sum(headers)
    if not rate:
        raise RuntimeError('не удалось разобрать Ogg/Vorbis: %s' % path)
    return last_granule / float(rate)


def duration(path):
    try:
        import soundfile as sf
        return float(sf.info(path).duration), 'soundfile'
    except Exception:
        return ogg_duration_fallback(path), 'ogg-парсер'


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('zip')
    ap.add_argument('--bank', default='03-sound/sounds')
    ap.add_argument('--repo-src', default='01-coder/3.5.3/src')
    ap.add_argument('--manifest', default=None,
                    help='манифест внутри пакета (по умолчанию project-3.5.3-clean.manifest.txt рядом с ZIP)')
    a = ap.parse_args(argv[1:])

    ok = True
    print('ZIP: %s' % a.zip)
    print('  размер %d Б' % os.path.getsize(a.zip))
    print('  sha256 %s' % sha256_file(a.zip))

    tmp = tempfile.mkdtemp(prefix='delta_r1_')
    try:
        with zipfile.ZipFile(a.zip) as z:
            names = [n for n in z.namelist() if not n.endswith('/')]
            print('  файлов в архиве: %d' % len(names))
            z.extractall(tmp)

        manifest = a.manifest or os.path.join(os.path.dirname(os.path.abspath(a.zip)),
                                              'project-3.5.3-clean.manifest.txt')
        if os.path.exists(manifest):
            print('\n[1] манифест: %s' % manifest)
            print('    sha256 манифеста %s' % sha256_file(manifest))
            bad, missing, total = [], [], 0
            for line in open(manifest, encoding='utf-8'):
                parts = line.split()
                if len(parts) < 2:
                    continue
                total += 1
                want, rel = parts[0], parts[-1].lstrip('*')
                path = os.path.join(tmp, rel)
                if not os.path.exists(path):
                    missing.append(rel)
                elif sha256_file(path) != want:
                    bad.append(rel)
            print('    строк %d | не сошлось %d | нет файла %d' % (total, len(bad), len(missing)))
            for rel in bad[:5]:
                print('      ХЕШ: %s' % rel)
            for rel in missing[:5]:
                print('      НЕТ: %s' % rel)
            if bad or missing:
                ok = False
            else:
                print('    ИТОГ: манифест сходится')
        else:
            print('\n[1] манифест не найден — проверка хешей по манифесту пропущена')

        print('\n[2] repo/src против zip/src')
        if os.path.isdir(a.repo_src):
            def walk(root):
                out = {}
                for dirpath, _, files in os.walk(root):
                    for f in files:
                        p = os.path.join(dirpath, f)
                        out[os.path.relpath(p, root).replace(os.sep, '/')] = sha256_file(p)
                return out
            repo = walk(a.repo_src)
            zipd = walk(os.path.join(tmp, 'src'))
            only_repo = set(repo) - set(zipd)
            only_zip = set(zipd) - set(repo)
            diff = [k for k in set(repo) & set(zipd) if repo[k] != zipd[k]]
            print('    файлов repo %d, zip %d | только repo %d, только zip %d, различаются %d'
                  % (len(repo), len(zipd), len(only_repo), len(only_zip), len(diff)))
            if only_repo or only_zip or diff:
                ok = False
                for k in sorted(only_zip)[:5]:
                    print('      ТОЛЬКО В ZIP: %s' % k)
                for k in sorted(only_repo)[:5]:
                    print('      ТОЛЬКО В REPO: %s' % k)
                for k in sorted(diff)[:5]:
                    print('      РАЗЛИЧАЕТСЯ: %s' % k)
            else:
                print('    ИТОГ: repo/src == zip/src')
        else:
            print('    каталог %s отсутствует — проверка пропущена' % a.repo_src)

        print('\n[3] два файла R1 против банка %s' % a.bank)
        for rel in R1_FILES:
            in_zip = os.path.join(tmp, 'src', 'main', 'resources', 'assets', 'carnis', 'sounds', rel)
            in_bank = os.path.join(a.bank, rel)
            if not (os.path.exists(in_zip) and os.path.exists(in_bank)):
                ok = False
                print('    %-26s НЕТ ФАЙЛА (%s / %s)' % (rel, os.path.exists(in_zip), os.path.exists(in_bank)))
                continue
            same = open(in_zip, 'rb').read() == open(in_bank, 'rb').read()
            print('    %-26s %s' % (rel, 'cmp: ИДЕНТИЧНЫ' if same else 'cmp: РАЗЛИЧАЮТСЯ'))
            print('      пакет %7d Б %s' % (os.path.getsize(in_zip), sha256_file(in_zip)[:16]))
            print('      банк  %7d Б %s' % (os.path.getsize(in_bank), sha256_file(in_bank)[:16]))
            if not same:
                ok = False

        print('\n[4] расклад по банку (пакет против %s)' % a.bank)
        pkg = os.path.join(tmp, 'src', 'main', 'resources', 'assets', 'carnis', 'sounds')

        def walk_ogg(root):
            out = {}
            for dirpath, _, files in os.walk(root):
                for f in files:
                    if f.endswith('.ogg'):
                        p = os.path.join(dirpath, f)
                        out[os.path.relpath(p, root).replace(os.sep, '/')] = sha256_file(p)
            return out
        bank, pack = walk_ogg(a.bank), walk_ogg(pkg)
        common = set(bank) & set(pack)
        same = [k for k in common if bank[k] == pack[k]]
        diff = [k for k in common if bank[k] != pack[k]]
        only_bank = sorted(set(bank) - set(pack))
        only_pack = sorted(set(pack) - set(bank))
        print('    банк %d | пакет %d | совпадают %d | расходятся %d | только в банке %d | только в пакете %d'
              % (len(bank), len(pack), len(same), len(diff), len(only_bank), len(only_pack)))
        for k in sorted(diff):
            print('      РАСХОЖДЕНИЕ: %s' % k)
        if diff:
            ok = False

        print('\n[5] Д2: soundDelay %d–%d тиков против длины файла' % SOUND_DELAY_RANGE)
        loop = os.path.join(pkg, 'block', 'heartbeat_loop.ogg')
        if os.path.exists(loop):
            d, how = duration(loop)
            ticks = d * TICKS_PER_SECOND
            spacing = (SOUND_DELAY_RANGE[0] + 1, SOUND_DELAY_RANGE[1] + 1)
            print('    heartbeat_loop.ogg: %.3f с = %.1f тика (%s)' % (d, ticks, how))
            print('    фактический интервал между звуками = soundDelay + 1 = %d–%d тиков' % spacing)
            bad_low = spacing[0] <= ticks
            print('    минимальный интервал %d %s %.1f → %s'
                  % (spacing[0], '<=' if bad_low else '>', ticks,
                     'ПЕРЕКРЫТИЕ' if bad_low else 'без перекрытия'))
            if bad_low:
                ok = False
                n = sum(1 for a_ in range(1, 101) if 29 + a_ // 10 + 1 <= ticks)
                print('      перекрытие при agonyTicks 1…%d' % n)
        else:
            ok = False
            print('    НЕТ ФАЙЛА block/heartbeat_loop.ogg')

        print('\n[6] Д1-запас: минимальная пауза %d тиков против длины heart_pulse' % MIN_HEARTBEAT_INTERVAL_TICKS)
        pulse = os.path.join(pkg, 'block', 'heart_pulse.ogg')
        if os.path.exists(pulse):
            d, how = duration(pulse)
            ticks = d * TICKS_PER_SECOND
            print('    heart_pulse.ogg: %.3f с = %.1f тика (%s)' % (d, ticks, how))
            tight = MIN_HEARTBEAT_INTERVAL_TICKS <= ticks
            print('    %d тиков %s %.1f → %s' % (MIN_HEARTBEAT_INTERVAL_TICKS,
                                                 '<=' if tight else '>', ticks,
                                                 'ПЕРЕКРЫТИЕ' if tight else 'без перекрытия'))
            if tight:
                ok = False
        else:
            ok = False
            print('    НЕТ ФАЙЛА block/heart_pulse.ogg')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print('\nДЕЛЬТА:', 'СОШЛАСЬ — можно писать полный вердикт ПРИНЯТО' if ok
          else 'НЕ СОШЛАСЬ — пакет возвращается Кодеру')
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
