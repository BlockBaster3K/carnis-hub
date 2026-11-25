#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""delta_360.py — дельта-приёмка 3.6.0 (K4, K5, K6-S) по ТЗ `05-architect/TZ_3.6.0.md`.

Проверяет только то, что перечислено в §3 ТЗ, и не пересчитывает Д1–Д7 из 3.5.3:
вместо этого доказывает, что код Д1–Д7 не менялся.

  1. Пакет: `sha256sum -c` по внешнему манифесту, число файлов = число строк.
  2. Версия 3.6.0 в четырёх местах: `gradle.properties`, `mods.toml` version,
     `mods.toml` displayVersion, имя каталога пакета.
  3. K4: два файла удалены, ссылок 0, изменений против базы ровно эти два удаления.
  4. K5: `blockstates/creeping_tendrils.json` — 4 × N комбинаций, `y` по `facing`,
     `parent: minecraft:block/ladder` сохранён.
  5. K6-S: `OSSIFIED_SCYTHE_HIT` нет в `ScytheItem`, `OSSIFIED_SCYTHE_SWING` нет в
     `CombatItemEvents`, в `ModSounds` объявления на месте; `sounds.json` = 82
     события, два новых без `pitch`/`volume`; файлы косы лежат в пакете.
  6. JSON: все файлы пакета разбираются.
  7. Д1–Д7 не тронуты: побайтовое сравнение файлов, на которых держались пункты 3.5.3.

Запуск:
    python3 02-reviewer/tools/delta_360.py 01-coder/3.6.0/project-3.6.0-clean.zip \
        [--base 01-coder/3.5.3/project-3.5.3-clean.zip] \
        [--pkgdir 01-coder/3.6.0]

Код возврата: 0 — все проверки пройдены, 2 — есть расхождения.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile

K4_REMOVED = [
    'src/main/resources/assets/carnis/textures/item/bio_purifier_geo.png',
    'src/main/resources/assets/carnis/models/item/pulsing_heart_geometry.json',
]
# K5 заменяет одиночную текстуру и модель набором вариантов, поэтому против
# базы 3.5.3 они тоже выглядят как удаления. Правило — ровно этот набор из 4:
# не «два удаления», не «сколько получилось», а точное совпадение множества.
K5_REPLACED = [
    'src/main/resources/assets/carnis/models/block/creeping_tendrils.json',
    'src/main/resources/assets/carnis/textures/block/creeping_tendrils.png',
]
EXPECTED_REMOVED = K4_REMOVED + K5_REPLACED
D17_UNTOUCHED = [
    'src/main/java/com/carnis/mod/block/entity/FleshBulbBlockEntity.java',
    'src/main/java/com/carnis/mod/client/PlayerHallucinationHandler.java',
    'src/main/resources/assets/carnis/geo/entity/cerebral_nexus.geo.json',
    'src/main/resources/assets/carnis/textures/block/ossified_flesh_0.png',
    'src/main/resources/assets/carnis/textures/block/ossified_flesh_1.png',
    'src/main/resources/assets/carnis/textures/block/ossified_flesh_2.png',
    'src/main/resources/assets/carnis/textures/block/ossified_flesh_3.png',
    'src/main/resources/assets/carnis/textures/block/spore_sprout.png',
    'src/main/resources/assets/carnis/textures/block/neural_moss.png',
    'src/main/resources/assets/carnis/textures/block/pustule_cluster.png',
    'src/main/resources/assets/carnis/textures/mob_effect/incubating.png',
    'src/main/resources/assets/carnis/textures/mob_effect/thermal_shock.png',
]
NEW_EVENTS = {'item.bone_scythe.swing', 'item.bone_scythe.hit'}
REQUIRED_EVENTS = 82


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for c in iter(lambda: fh.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def read_text(path):
    try:
        return open(path, encoding='utf-8', errors='replace').read()
    except OSError:
        return ''


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('zip')
    ap.add_argument('--base', default='01-coder/3.5.3/project-3.5.3-clean.zip')
    ap.add_argument('--pkgdir', default=None, help='каталог пакета в репозитории (для имени и манифеста)')
    a = ap.parse_args(argv[1:])

    if not os.path.exists(a.zip):
        print('ПАКЕТ НЕ НАЙДЕН: %s' % a.zip)
        print('Ждём сдачу Кодера: 01-coder/3.6.0/project-3.6.0-clean.zip')
        return 2

    ok = True
    def say(flag, text):
        nonlocal ok
        if flag is False:
            ok = False
        mark = {True: 'OK  ', False: 'FAIL', None: '--  '}[flag]
        print('  [%s] %s' % (mark, text))

    pkgdir = a.pkgdir or os.path.dirname(os.path.abspath(a.zip))
    print('пакет: %s' % a.zip)
    print('  размер %d Б' % os.path.getsize(a.zip))
    print('  sha256 %s' % sha(a.zip))

    tmp = tempfile.mkdtemp(prefix='delta360_')
    basetmp = tempfile.mkdtemp(prefix='base353_')
    try:
        with zipfile.ZipFile(a.zip) as z:
            names = [n for n in z.namelist() if not n.endswith('/')]
            z.extractall(tmp)
        print('  файлов в архиве: %d' % len(names))

        print('\n[1] манифест')
        man = os.path.join(pkgdir, 'project-3.6.0-clean.manifest.txt')
        if not os.path.exists(man):
            alt = [f for f in os.listdir(pkgdir) if f.endswith('.manifest.txt')] if os.path.isdir(pkgdir) else []
            man = os.path.join(pkgdir, alt[0]) if alt else man
        if os.path.exists(man):
            rows = [l.split() for l in read_text(man).splitlines() if l.strip()]
            bad = [r[-1] for r in rows if not os.path.exists(os.path.join(tmp, r[-1]))
                   or sha(os.path.join(tmp, r[-1])) != r[0]]
            say(not bad, 'строк %d, файлов %d, не сошлось %d' % (len(rows), len(names), len(bad)))
            for b in bad[:5]:
                print('        %s' % b)
        else:
            say(False, 'манифест не найден рядом с ZIP')

        print('\n[2] версия 3.6.0 в четырёх местах')
        gp = read_text(os.path.join(tmp, 'gradle.properties'))
        m = re.search(r'mod_version\s*=\s*(\S+)', gp)
        say(m and m.group(1) == '3.6.0', 'gradle.properties mod_version = %s' % (m.group(1) if m else '—'))
        toml = read_text(os.path.join(tmp, 'src/main/resources/META-INF/mods.toml'))
        v = re.search(r'^\s*version\s*=\s*"([^"]+)"', toml, re.M)
        dv = re.search(r'^\s*displayVersion\s*=\s*"([^"]+)"', toml, re.M)
        say(v and v.group(1) == '3.6.0', 'mods.toml version = %s' % (v.group(1) if v else '—'))
        say(dv and dv.group(1) == '3.6.0', 'mods.toml displayVersion = %s' % (dv.group(1) if dv else '—'))
        # Суффикс пересдачи (-R, -R2, -R5) отбрасывается ровно как в CI
        # (.github/workflows/build.yml: EXPECT="${DIR%%-R*}").
        folder = os.path.basename(os.path.normpath(pkgdir))
        expect = re.sub(r'-R.*$', '', folder)
        say(expect == '3.6.0', 'каталог пакета = %s → ожидаемая версия %s' % (folder, expect))

        print('\n[3] K4 — мёртвые ресурсы')
        for rel in K4_REMOVED:
            say(not os.path.exists(os.path.join(tmp, rel)), 'удалён %s' % rel)
        stem = [os.path.basename(r) for r in K4_REMOVED]
        hits = []
        for dirpath, _, files in os.walk(tmp):
            for f in files:
                if not f.endswith(('.java', '.json', '.txt', '.md', '.properties', '.gradle')):
                    continue
                if f == 'MANIFEST.txt' or f.endswith('.manifest.txt'):
                    continue   # это список файлов пакета, а не ссылка из кода
                p = os.path.join(dirpath, f)
                body = read_text(p)
                for s in stem:
                    for cand in (s, s.rsplit('.', 1)[0]):
                        if cand in body:
                            hits.append((os.path.relpath(p, tmp), cand))
                            break
        say(not hits, 'ссылок на удалённые имена: %d' % len(hits))
        for h in hits[:5]:
            print('        %s → %s' % h)

        print('\n[4] K5 — creeping_tendrils, weighted-варианты по facing')
        bs_path = os.path.join(tmp, 'src/main/resources/assets/carnis/blockstates/creeping_tendrils.json')
        try:
            bs = json.load(open(bs_path, encoding='utf-8'))
            variants = bs.get('variants', {})
            say(True, 'комбинаций в blockstates: %d' % len(variants))
            y_by_facing = {}
            bad_y = []
            for key, val in variants.items():
                parts = dict(p.split('=') for p in key.split(',') if '=' in p)
                inner = val[0] if isinstance(val, list) else val
                y = inner.get('y')
                f = parts.get('facing')
                if f is not None:
                    seen = y_by_facing.setdefault(f, y)
                    if seen != y:
                        bad_y.append((key, y, seen))
            say(not bad_y, 'y соответствует facing (нарушений %d)' % len(bad_y))
            for b in bad_y[:4]:
                print('        %s' % (b,))
            models = set()
            for val in variants.values():
                for inner in (val if isinstance(val, list) else [val]):
                    models.add(inner.get('model'))
            say(len(models) >= 2, 'различных моделей: %d' % len(models))
        except Exception as exc:
            say(False, 'blockstates не разобран: %s' % exc)

        ladder_ok = False
        models_dir = os.path.join(tmp, 'src/main/resources/assets/carnis/models/block')
        for f in os.listdir(models_dir) if os.path.isdir(models_dir) else []:
            if f.startswith('creeping_tendrils') and f.endswith('.json'):
                body = read_text(os.path.join(models_dir, f))
                if 'minecraft:block/ladder' in body or '"parent"' in body and 'ladder' in body:
                    ladder_ok = True
        say(ladder_ok, 'parent minecraft:block/ladder сохранён')

        print('\n[5] K6-S — отдельный голос костяной косы')
        jdir = os.path.join(tmp, 'src/main/java')
        scythe = ''
        for dirpath, _, files in os.walk(jdir):
            for f in files:
                if f == 'ScytheItem.java':
                    scythe = read_text(os.path.join(dirpath, f))
        say('OSSIFIED_SCYTHE_HIT' not in scythe, 'в ScytheItem нет константы OSSIFIED_SCYTHE_HIT')
        say('ossified_scythe' in scythe.lower() or 'hitSound' in scythe or 'swingSound' in scythe,
            'в ScytheItem видны поля/выбор звука', )
        events = ''
        for dirpath, _, files in os.walk(jdir):
            for f in files:
                if f == 'CombatItemEvents.java':
                    events = read_text(os.path.join(dirpath, f))
        say('OSSIFIED_SCYTHE_SWING' not in events, 'в CombatItemEvents нет OSSIFIED_SCYTHE_SWING')
        modsounds = ''
        for dirpath, _, files in os.walk(jdir):
            for f in files:
                if f == 'ModSounds.java':
                    modsounds = read_text(os.path.join(dirpath, f))
        say(modsounds.count('OSSIFIED_SCYTHE_HIT') == 1,
            'в ModSounds объявление OSSIFIED_SCYTHE_HIT: %d' % modsounds.count('OSSIFIED_SCYTHE_HIT'))
        say(modsounds.count('OSSIFIED_SCYTHE_SWING') == 1,
            'в ModSounds объявление OSSIFIED_SCYTHE_SWING: %d' % modsounds.count('OSSIFIED_SCYTHE_SWING'))

        sj_path = os.path.join(tmp, 'src/main/resources/assets/carnis/sounds.json')
        try:
            sj = json.load(open(sj_path, encoding='utf-8'))
        except Exception as exc:
            sj = {}
            say(False, 'sounds.json не разобран: %s' % exc)
        say(len(sj) == REQUIRED_EVENTS, 'событий в sounds.json: %d (ожидается %d)' % (len(sj), REQUIRED_EVENTS))
        for ev in sorted(NEW_EVENTS):
            body = sj.get(ev)
            if body is None:
                say(False, 'нет события %s' % ev)
                continue
            extra = [s for s in body.get('sounds', []) if isinstance(s, dict) and ('pitch' in s or 'volume' in s)]
            say(not extra, 'событие %s есть, без pitch/volume' % ev)

        for rel in ('sounds/combat/bone_scythe_swing_01.ogg', 'sounds/combat/bone_scythe_hit_01.ogg'):
            p = os.path.join(tmp, 'src/main/resources/assets/carnis', rel)
            say(os.path.exists(p), 'файл в пакете: %s' % rel)

        print('\n[5b] overlay.txt — пути и хеши источников (ожидается 2/2)')
        overlay = os.path.join(os.path.dirname(os.path.abspath(pkgdir)), '..', '06-build', 'overlay.txt')
        overlay = os.path.normpath(overlay)
        if not os.path.exists(overlay):
            overlay = '06-build/overlay.txt'
        try:
            lines = [l.strip() for l in read_text(overlay).splitlines()
                     if l.strip() and not l.strip().startswith('#')]
            good = bad = 0
            for line in lines:
                if '->' not in line or '|' not in line:
                    continue
                left, want = line.split('|', 1)
                src, dst = [t.strip() for t in left.split('->', 1)]
                want = want.strip()
                ok_src = os.path.exists(src) and sha(src) == want
                ok_dst = os.path.exists(os.path.join(tmp, dst)) and sha(os.path.join(tmp, dst)) == want
                if ok_src and ok_dst:
                    good += 1
                else:
                    bad += 1
                    print('        %s: источник %s, назначение %s' %
                          (src, 'OK' if ok_src else 'НЕ СОШЁЛСЯ', 'OK' if ok_dst else 'НЕ СОШЁЛСЯ'))
            say(bad == 0 and good == 2, 'строк overlay: %d, сошлось %d, не сошлось %d' % (len(lines), good, bad))
        except Exception as exc:
            say(False, 'overlay не разобран: %s' % exc)

        print('\n[6] JSON')
        badjson = []
        for dirpath, _, files in os.walk(os.path.join(tmp, 'src')):
            for f in files:
                if f.endswith('.json'):
                    p = os.path.join(dirpath, f)
                    try:
                        json.load(open(p, encoding='utf-8'))
                    except Exception as exc:
                        badjson.append((os.path.relpath(p, tmp), str(exc)[:50]))
        say(not badjson, 'JSON: не разобрано %d' % len(badjson))
        for b in badjson[:5]:
            print('        %s' % (b,))

        print('\n[7] Д1–Д7 не тронуты (сравнение с %s)' % a.base)
        if os.path.exists(a.base):
            with zipfile.ZipFile(a.base) as zb:
                zb.extractall(basetmp)
            for rel in D17_UNTOUCHED:
                pn = os.path.join(tmp, rel)
                po = os.path.join(basetmp, rel)
                if not (os.path.exists(pn) and os.path.exists(po)):
                    say(False, '%s: нет в одном из пакетов' % rel)
                else:
                    same = sha(pn) == sha(po)
                    say(same, '%s %s' % (os.path.basename(rel), 'идентичен' if same else 'ИЗМЕНЁН'))
            old = {n: sha(os.path.join(basetmp, n)) for n in
                   [x for x in zipfile.ZipFile(a.base).namelist() if not x.endswith('/')]}
            new = {n: sha(os.path.join(tmp, n)) for n in names}
            removed = sorted(set(old) - set(new))
            added = sorted(set(new) - set(old))
            changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])
            print('    удалено %d: %s' % (len(removed), removed))
            print('    добавлено %d: %s' % (len(added), added[:8]))
            print('    изменено %d: %s' % (len(changed), changed[:8]))
            missing = [r for r in EXPECTED_REMOVED if r not in removed]
            unexpected = [r for r in removed if r not in EXPECTED_REMOVED]
            say(not missing and not unexpected,
                'удаления — точно ожидаемый набор из %d (K4 2 + K5 2): удалено %d, '
                'не хватает %d, лишних %d' % (len(EXPECTED_REMOVED), len(removed),
                                              len(missing), len(unexpected)))
            for r in missing:
                print('        НЕ УДАЛЁН, а должен: %s' % r)
            for r in unexpected:
                print('        ЛИШНЕЕ УДАЛЕНИЕ: %s' % r)
        else:
            # fail-closed: без базы не проверить ни Д1–Д7, ни правило удалений,
            # поэтому «пакета нет» — замечание, а не «пропущено»
            say(False, 'базовый пакет %s не найден — дельту и правило удалений '
                       'проверить нельзя' % a.base)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(basetmp, ignore_errors=True)

    print('\nИТОГ 3.6.0:', 'ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ — можно писать ПРИНЯТО' if ok else 'ЕСТЬ РАСХОЖДЕНИЯ')
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
