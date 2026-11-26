#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""geo_pairs_d5.py — воспроизводимый счётчик для Д5 (компланарные пары + мёртвые кубы).

Методика: 00-board/reports/reviewer_D5_methodology.md (Ревизор, волна 29).
Зависимостей нет, только стандартная библиотека Python 3.8+.

Запуск:
    python3 geo_pairs_d5.py <файл.geo.json>              # обычный отчёт
    python3 geo_pairs_d5.py <файл.geo.json> --drop 4,5,11 # сценарий «если эти кубы убрать»
    python3 geo_pairs_d5.py <файл.geo.json> --json out.json

Код возврата: 0 — приёмка Д5 пройдена (0 видимых пар и 0 мёртвых кубов),
               2 — не пройдена. Печатается ИТОГ.
"""
import json
import sys

EPS = 1e-6          # допуск на совпадение координат (единицы модели, 1/16 блока)
COVER_STEP = 0.25   # шаг сетки при подсчёте доли перекрытия, единицы модели
COVER_MAX = 128     # предел числа шагов по каждой оси


def load_cubes(path):
    with open(path, encoding='utf-8') as fh:
        geo = json.load(fh)
    roots = geo.get('minecraft:geometry') if isinstance(geo, dict) else None
    if roots is None:
        roots = geo if isinstance(geo, list) else [geo]
    cubes = []
    for g in roots:
        for bone in g.get('bones', []):
            for ci, c in enumerate(bone.get('cubes', [])):
                o = [float(v) for v in c.get('origin', [0, 0, 0])]
                s = [float(v) for v in c.get('size', [1, 1, 1])]
                inf = float(c.get('inflate', 0) or 0)
                lo = [o[k] - inf for k in range(3)]
                hi = [o[k] - inf + s[k] + 2 * inf for k in range(3)]
                cubes.append(dict(bone=bone.get('name', '?'), idx=ci, lo=lo, hi=hi,
                                  rot=c.get('rotation')))
    return cubes


def rect(c, axis):
    o = [a for a in range(3) if a != axis]
    return [c['lo'][o[0]], c['hi'][o[0]]], [c['lo'][o[1]], c['hi'][o[1]]]


def box(c):
    return 'x %g..%g, y %g..%g, z %g..%g' % (c['lo'][0], c['hi'][0], c['lo'][1],
                                             c['hi'][1], c['lo'][2], c['hi'][2])


def in_front(c, axis, sign, plane):
    """Куб лежит строго перед плоскостью со стороны её нормали."""
    return c['hi'][axis] > plane + EPS if sign > 0 else c['lo'][axis] < plane - EPS


def coverage(rect_u, rect_v, blockers, axis):
    """Доля площадки, закрытая ОБЪЕДИНЕНИЕМ кубов-блокеров (сетка COVER_STEP)."""
    u0, u1 = rect_u
    v0, v1 = rect_v
    du, dv = u1 - u0, v1 - v0
    nu = min(COVER_MAX, max(1, int(round(du / COVER_STEP))))
    nv = min(COVER_MAX, max(1, int(round(dv / COVER_STEP))))
    total = hit = 0
    for iu in range(nu):
        u = u0 + du * (iu + 0.5) / nu
        for iv in range(nv):
            v = v0 + dv * (iv + 0.5) / nv
            total += 1
            for c in blockers:
                (cu0, cu1), (cv0, cv1) = rect(c, axis)
                if cu0 - EPS <= u <= cu1 + EPS and cv0 - EPS <= v <= cv1 + EPS:
                    hit += 1
                    break
    return hit / total if total else 0.0


def find_pairs(cubes):
    min_y = min(c['lo'][1] for c in cubes) if cubes else 0.0
    out = []
    for i in range(len(cubes)):
        for j in range(i + 1, len(cubes)):
            a, b = cubes[i], cubes[j]
            for axis in range(3):
                for sign in (1, -1):
                    pa = a['hi'][axis] if sign > 0 else a['lo'][axis]
                    pb = b['hi'][axis] if sign > 0 else b['lo'][axis]
                    if abs(pa - pb) > EPS:
                        continue
                    (ua, va), (ub, vb) = rect(a, axis), rect(b, axis)
                    u = [max(ua[0], ub[0]), min(ua[1], ub[1])]
                    v = [max(va[0], vb[0]), min(va[1], vb[1])]
                    du, dv = u[1] - u[0], v[1] - v[0]
                    if du <= EPS or dv <= EPS:
                        continue
                    blockers = [c for k, c in enumerate(cubes)
                                if k not in (i, j) and in_front(c, axis, sign, pa)]
                    full = False
                    for c in blockers:                      # закрыта ЦЕЛИКОМ одним кубом
                        (cu0, cu1), (cv0, cv1) = rect(c, axis)
                        if cu0 - EPS <= u[0] and cu1 + EPS >= u[1] and \
                           cv0 - EPS <= v[0] and cv1 + EPS >= v[1]:
                            full = True
                            break
                    ground = (axis == 1 and sign < 0 and abs(pa - min_y) <= EPS)
                    out.append(dict(i=i, j=j, axis='XYZ'[axis], sign=sign, plane=pa,
                                    area=du * dv, u=u, v=v, full=full, ground=ground,
                                    cover=coverage(u, v, blockers, axis),
                                    n_blockers=len(blockers)))
    return out


def dead_cubes(cubes):
    out = []
    for i, inner in enumerate(cubes):
        for j, outer in enumerate(cubes):
            if i == j:
                continue
            if all(inner['lo'][k] >= outer['lo'][k] - EPS and
                   inner['hi'][k] <= outer['hi'][k] + EPS for k in range(3)):
                share = 1.0
                for k in range(3):
                    vol_i = inner['hi'][k] - inner['lo'][k]
                    vol_o = max(outer['hi'][k] - outer['lo'][k], EPS)
                    share *= vol_i / vol_o
                coincident = sum(1 for k in range(3)
                                 if abs(inner['lo'][k] - outer['lo'][k]) <= 0.01) + \
                             sum(1 for k in range(3)
                                 if abs(inner['hi'][k] - outer['hi'][k]) <= 0.01)
                out.append(dict(inner=i, outer=j, share=share, coincident=coincident))
    return out


def classify(pairs, cubes):
    for p in pairs:
        if p['ground']:
            p['class'] = 'земля'
        elif p['full']:
            p['class'] = 'скрыта'
        else:
            p['class'] = 'ВИДИМАЯ'
        p['who'] = 'закрыта целиком' if p['full'] else (
            'закрыта на %.0f%% (объединением)' % (p['cover'] * 100) if p['cover'] > 0 else 'не закрыта')
    return pairs


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    drop = set()
    as_json = None
    k = 2
    while k < len(argv):
        if argv[k] == '--drop' and k + 1 < len(argv):
            drop = {int(x) for x in argv[k + 1].split(',') if x.strip()}
            k += 2
        elif argv[k] == '--json' and k + 1 < len(argv):
            as_json = argv[k + 1]
            k += 2
        else:
            k += 1

    cubes = load_cubes(path)
    print('файл: %s' % path)
    if drop:
        for idx in sorted(drop):
            if idx < len(cubes):
                print('СЦЕНАРИЙ: убран #%d /%s#%d (%s)' % (idx, cubes[idx]['bone'],
                                                           cubes[idx]['idx'], box(cubes[idx])))
        cubes = [c for kk, c in enumerate(cubes) if kk not in drop]
    print('кубов %d, костей %d' % (len(cubes), len({c['bone'] for c in cubes})))
    for b in dict.fromkeys(c['bone'] for c in cubes):
        print('  /%s: %d' % (b, sum(1 for c in cubes if c['bone'] == b)))

    pairs = classify(find_pairs(cubes), cubes)
    visible = [p for p in pairs if p['class'] == 'ВИДИМАЯ']
    ground = [p for p in pairs if p['class'] == 'земля']
    hidden = [p for p in pairs if p['class'] == 'скрыта']

    print('\nкомпланарных пар «в одну сторону» с перекрытием: %d' % len(pairs))
    print('  | № | пара | грань | плоскость | площадь | закрыто | класс |')
    for n, p in enumerate(sorted(pairs, key=lambda x: (x['class'] != 'ВИДИМАЯ', -x['area'])), 1):
        print('  | %d | #%d /%s#%d + #%d /%s#%d | %s%s | %g | %g | %s | %s |' % (
            n, p['i'], cubes[p['i']]['bone'], cubes[p['i']]['idx'],
            p['j'], cubes[p['j']]['bone'], cubes[p['j']]['idx'],
            p['axis'], '+' if p['sign'] > 0 else '-', p['plane'], p['area'], p['who'], p['class']))

    dead = dead_cubes(cubes)
    print('\nмёртвых кубов (целиком внутри другого): %d' % len(dead))
    for d in sorted(dead, key=lambda x: -x['share']):
        print('  #%d /%s#%d внутри #%d /%s#%d | доля объёма %.3f | совпадающих граней %d' % (
            d['inner'], cubes[d['inner']]['bone'], cubes[d['inner']]['idx'],
            d['outer'], cubes[d['outer']]['bone'], cubes[d['outer']]['idx'],
            d['share'], d['coincident']))

    print('\nИТОГО: видимых %d, земля %d, скрыто %d, мёртвых кубов %d' %
          (len(visible), len(ground), len(hidden), len(dead)))
    ok = not visible and not dead
    print('ИТОГ Д5:', 'ПРИЁМКА (0 видимых, 0 мёртвых)' if ok else 'НЕ ПРИНЯТО')
    if as_json:
        with open(as_json, 'w', encoding='utf-8') as fh:
            json.dump(dict(cubes=len(cubes), visible=len(visible), ground=len(ground),
                           hidden=len(hidden), dead=len(dead),
                           pairs=[dict(i=p['i'], j=p['j'], axis=p['axis'] + ('+' if p['sign'] > 0 else '-'),
                                       plane=p['plane'], area=p['area'], cover=round(p['cover'], 4),
                                       cls=p['class']) for p in pairs]),
                      fh, ensure_ascii=False, indent=1)
        print('json -> %s' % as_json)
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
