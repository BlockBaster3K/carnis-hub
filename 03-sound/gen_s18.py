#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S18 — генератор 132 файлов для 33 заражённых ванильных мобов (3.8.0).

ВАЖНО (S24, З-27): пишет ТОЛЬКО в `03-sound/sounds_380/entity/`. Каталог
`03-sound/sounds/` — НЕИЗМЕНЯЕМЫЙ канон 3.7.x (144 файла), и гейт 3.7.3
сверяет пакет именно с ним. Раньше скрипт писал в канон и этим ломал гейт
принятой версии.

По 4 события на существо: ambient / attack / hurt / death.
Стиль: единая «заражённая» сигнатура — низкий резонанс тела, влажная
нестабильность, ВЧ-дыхание; характер задаётся профилем тела (желе, хитин,
кость, вода, огонь, зверь, голос, магия, ветер, скалк, панцирь).

Формат: OGG Vorbis mono 44.1 кГц 160 kbps (ambient — 96 kbps, как в банке).
Громкость не выставляется «на глаз»: после рендера пик приводится к целевому
значению по факту замера.
"""
import os
import numpy as np
import json
import subprocess

SR = 44100
FF = '/tmp/bin/ffmpeg'

# ─────────── профили тел: (низ-резонанс, шум-полоса, «влажность», ВЧ-воздух)
BODY = {
    'slime':        dict(low=90,  wet=0.85, hiss=0.10, grav=0.5, kind='gel'),
    'magma_cube':   dict(low=110, wet=0.55, hiss=0.45, grav=0.6, kind='gel'),
    'shulker':      dict(low=140, wet=0.25, hiss=0.55, grav=0.4, kind='shell'),
    'blaze':        dict(low=120, wet=0.15, hiss=0.80, grav=0.6, kind='fire'),
    'ghast':        dict(low=70,  wet=0.45, hiss=0.30, grav=0.9, kind='voice'),
    'wither':       dict(low=60,  wet=0.20, hiss=0.40, grav=1.0, kind='bone'),
    'wither_skeleton': dict(low=95, wet=0.18, hiss=0.45, grav=0.5, kind='bone'),
    'stray':        dict(low=100, wet=0.22, hiss=0.50, grav=0.5, kind='bone'),
    'bogged':       dict(low=105, wet=0.45, hiss=0.35, grav=0.5, kind='bone'),
    'warden':       dict(low=45,  wet=0.35, hiss=0.30, grav=1.0, kind='sculk'),
    'breeze':       dict(low=180, wet=0.05, hiss=0.70, grav=0.3, kind='wind'),
    'creaking':     dict(low=130, wet=0.10, hiss=0.40, grav=0.5, kind='wood'),
    'cave_spider':  dict(low=260, wet=0.30, hiss=0.60, grav=0.2, kind='chitin'),
    'silverfish':   dict(low=300, wet=0.25, hiss=0.65, grav=0.15, kind='chitin'),
    'endermite':    dict(low=280, wet=0.20, hiss=0.60, grav=0.2, kind='chitin'),
    'enderman':     dict(low=110, wet=0.15, hiss=0.50, grav=0.6, kind='warp'),
    'witch':        dict(low=180, wet=0.40, hiss=0.30, grav=0.4, kind='voice'),
    'evoker':       dict(low=160, wet=0.25, hiss=0.35, grav=0.5, kind='magic'),
    'illusioner':   dict(low=170, wet=0.20, hiss=0.40, grav=0.5, kind='magic'),
    'vex':          dict(low=240, wet=0.10, hiss=0.70, grav=0.2, kind='wing'),
    'pillager':     dict(low=190, wet=0.25, hiss=0.30, grav=0.5, kind='voice'),
    'vindicator':   dict(low=175, wet=0.25, hiss=0.35, grav=0.5, kind='voice'),
    'ravager':      dict(low=65,  wet=0.35, hiss=0.30, grav=1.0, kind='beast', hpf=115),
    'hoglin':       dict(low=75,  wet=0.40, hiss=0.30, grav=0.9, kind='beast', hpf=115),
    'zoglin':       dict(low=70,  wet=0.50, hiss=0.35, grav=0.9, kind='beast', hpf=115),
    'piglin':       dict(low=165, wet=0.30, hiss=0.30, grav=0.5, kind='voice'),
    'piglin_brute': dict(low=140, wet=0.30, hiss=0.35, grav=0.7, kind='voice'),
    'drowned':      dict(low=125, wet=0.75, hiss=0.30, grav=0.5, kind='water'),
    'husk':         dict(low=135, wet=0.35, hiss=0.35, grav=0.5, kind='voice'),
    'zombie_villager': dict(low=150, wet=0.40, hiss=0.30, grav=0.5, kind='voice'),
    'guardian':     dict(low=115, wet=0.60, hiss=0.35, grav=0.6, kind='water'),
    'elder_guardian': dict(low=60, wet=0.55, hiss=0.30, grav=1.0, kind='water'),
    'phantom':      dict(low=200, wet=0.10, hiss=0.65, grav=0.3, kind='wing'),
}

# Длительности: (ambient, attack, hurt, death) — секунды
DUR = dict(ambient=(2.3, 3.2), attack=(0.55, 0.85), hurt=(0.40, 0.55), death=(1.5, 2.1))


def rng_for(name):
    h = 0
    for ch in name:
        h = (h * 131 + ord(ch)) % (2**31 - 1)
    return np.random.default_rng(h)


def bump(n, pos, width):
    t = np.arange(n)
    return np.exp(-0.5 * ((t - pos) / width) ** 2)


def lowpass(x, fc, sr=SR, order=2):
    """Простой БИХ-ФНЧ (каскад однополюсных) — без scipy-зависимостей в рендере."""
    a = np.exp(-2 * np.pi * fc / sr)
    y = x.copy()
    for _ in range(order):
        out = np.empty_like(y)
        acc = 0.0
        for i in range(len(y)):
            acc = (1 - a) * y[i] + a * acc
            out[i] = acc
        y = out
    return y


def highpass(x, fc, sr=SR, order=2):
    return x - lowpass(x, fc, sr, order)


def bandnoise(n, lo, hi, rng):
    w = rng.standard_normal(n)
    return lp_fft(w, hi) - lp_fft(w, lo)


def lp_fft(x, fc, sr=SR):
    """ФНЧ Баттерворта 4-го порядка через FFT-умножение (нулевая фаза)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    H = 1.0 / np.sqrt(1.0 + (f / max(fc, 1.0)) ** 8)
    return np.fft.irfft(X * H, len(x))


def hp_fft(x, fc, sr=SR):
    """ФВЧ Баттерворта 8-го порядка — НЕ x-ФНЧ: вычитание однополюсника
    оставляло низ на уровне 70 % энергии (проверено на пробе). Порядок 8, а не
    4: у зверей основной тон 70–75 Гц, и 4-й порядок давал на нём всего −9 дБ
    (hoglin/zoglin выходили на 38 % низа вместо ≤ 25 %)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    r = f / max(fc, 1.0)
    H = r ** 8 / np.sqrt(1.0 + r ** 16)
    return np.fft.irfft(X * H, len(x))


def bp_fft(x, lo, hi, sr=SR):
    return lp_fft(hp_fft(x, lo, sr), hi, sr)


def voice(p, n, rng, base_hz, fm_depth=0.04, vib=5.0, formants=((700, 1.0), (1200, 0.6))):
    """Голосовой слой: пила с вибрато и формантами — «тело», а не тон."""
    t = np.arange(n) / SR
    f = base_hz * (1 + fm_depth * np.sin(2 * np.pi * vib * t * (0.5 + rng.random())))
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * (ph / (2 * np.pi) % 1.0) - 1.0
    out = np.zeros(n)
    for fc, g in formants:
        out += g * bp_fft(saw, fc * 0.6, fc * 1.6)
    return out / max(np.abs(out).max(), 1e-9)


def gel(p, n, rng):
    t = np.arange(n) / SR
    body = lp_fft(rng.standard_normal(n), p['low'] * 1.4)
    wob = 1 + 0.5 * np.sin(2 * np.pi * (6 + 4 * rng.random()) * t)
    return body * wob


def shell(p, n, rng):
    t = np.arange(n) / SR
    return bp_fft(rng.standard_normal(n), p['low'], p['low'] * 8) * (1 + 0.4 * np.sin(2 * np.pi * 14 * t))


def fire(p, n, rng):
    return bp_fft(rng.standard_normal(n), 200, 6000)


def bone(p, n, rng):
    t = np.arange(n) / SR
    clicks = np.zeros(n)
    for _ in range(int(6 + 8 * rng.random())):
        pos = rng.random() * n
        idx = int(pos)
        w = int(60 + 120 * rng.random())
        seg = np.zeros(min(w, n - idx))
        seg[:] = rng.standard_normal(len(seg)) * np.exp(-np.arange(len(seg)) / (len(seg) / 4))
        clicks[idx:idx + len(seg)] += seg
    return hp_fft(clicks, 900) + 0.3 * bp_fft(rng.standard_normal(n), p['low'], p['low'] * 6)


def sculk(p, n, rng):
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * p['low'] * t) * np.exp(-t / (n / SR / 2))
    return sub + 0.4 * bp_fft(rng.standard_normal(n), 200, 2200)


def wind(p, n, rng):
    t = np.arange(n) / SR
    w = bp_fft(rng.standard_normal(n), 400, 5000)
    env = 0.5 + 0.5 * np.sin(2 * np.pi * (1.2 + rng.random()) * t + rng.random() * 6)
    return w * env


def wood(p, n, rng):
    t = np.arange(n) / SR
    return bp_fft(rng.standard_normal(n), 150, 1400) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t))


def chitin(p, n, rng):
    t = np.arange(n) / SR
    return bp_fft(rng.standard_normal(n), 800, 7000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 22 * t)))


def warp(p, n, rng):
    t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(300 + 200 * np.sin(2 * np.pi * 3 * t)) / SR
    return np.sin(ph) * 0.5 + 0.5 * bp_fft(rng.standard_normal(n), 600, 5000)


def magic(p, n, rng):
    t = np.arange(n) / SR
    tone = 0.5 * np.sin(2 * np.pi * 520 * t + 2 * np.sin(2 * np.pi * 7 * t))
    return tone + 0.5 * bp_fft(rng.standard_normal(n), 900, 6000)


def wing(p, n, rng):
    t = np.arange(n) / SR
    flap = np.pow(np.maximum(np.sin(2 * np.pi * 7 * t), 0), 2)
    return bp_fft(rng.standard_normal(n), 300, 4500) * flap


def beast(p, n, rng):
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * p['low'] * t) * 0.8
    growl = bp_fft(rng.standard_normal(n), 80, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 17 * t))
    return sub + growl


def water(p, n, rng):
    t = np.arange(n) / SR
    bub = np.zeros(n)
    for _ in range(int(8 + 14 * rng.random())):
        idx = int(rng.random() * (n - 400))
        w = int(150 + 250 * rng.random())
        f0 = 250 + 500 * rng.random()
        tt = np.arange(w) / SR
        bub[idx:idx + w] += np.sin(2 * np.pi * f0 * (1 + 1.8 * tt / (w / SR)) * tt) * np.exp(-tt * 14)
    return bub * 0.7 + 0.3 * bp_fft(rng.standard_normal(n), 120, 1400)


KIND = dict(gel=gel, shell=shell, fire=fire, bone=bone, sculk=sculk, wind=wind, wood=wood,
            chitin=chitin, warp=warp, magic=magic, wing=wing, beast=beast, water=water, voice=None)


def render(ent, event, p, rng):
    lo, hi = DUR[event]
    dur = lo + (hi - lo) * rng.random()
    n = int(dur * SR)
    t = np.arange(n) / SR

    # 1. тело: профиль существа
    if p['kind'] == 'voice':
        base = p['low'] * (1.0 if event != 'death' else 0.85)
        body = voice(p, n, rng, base, formants=((p['low'] * 3, 1.0), (p['low'] * 6, 0.5)))
    else:
        body = KIND[p['kind']](p, n, rng)

    # 2. заражение: всегда низкий резонанс + «мокрая» нестабильность
    sub = np.sin(2 * np.pi * p['low'] * 0.5 * t) * p['grav']
    wet_n = bp_fft(rng.standard_normal(n), 120, 1600) * p['wet']
    air = bp_fft(rng.standard_normal(n), 2500, 9000) * p['hiss']

    presence = bp_fft(rng.standard_normal(n), 700, 4000) * 0.45
    x = body * 1.0 + sub * 0.25 + wet_n * 0.5 + air * 0.45 + presence
    # срез низа: у заражённого тела остаётся «вес» 85–110 Гц, но не инфраниз
    x = hp_fft(x, p.get('hpf', 95))

    # 3. огибающая события
    if event == 'ambient':
        env = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.35)
        x *= env * (0.8 + 0.2 * np.sin(2 * np.pi * 0.7 * t))
    elif event == 'attack':
        env = np.minimum(1, t / 0.012) * np.exp(-t * 7.5)
        x *= env
        x[:120] += rng.standard_normal(120) * np.linspace(0.6, 0, 120)  # атака
    elif event == 'hurt':
        env = np.minimum(1, t / 0.008) * np.exp(-t * 11)
        x *= env
    else:  # death
        env = np.minimum(1, t / 0.02) * np.exp(-t * 2.0) * (0.7 + 0.3 * np.exp(-t * 6))
        x *= env
        # предсмертный распад — редкие влажные события
        for _ in range(int(3 + 6 * rng.random())):
            idx = int((0.15 + 0.8 * rng.random()) * n)
            w = min(int(0.05 * SR), n - idx)
            tt = np.arange(w) / SR
            x[idx:idx + w] += np.sin(2 * np.pi * (180 + 300 * rng.random()) * tt) * np.exp(-tt * 40) * 0.35

    # 4. лёгкий фейд по краям, чтобы не было щелчка на границе файла
    f = int(0.004 * SR)
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)

    return x


def norm(x, target_rms_db, peak_ceiling_db=-1.5):
    """Выравнивание по ГРОМКОСТИ с потолком пика.

    Раньше нормировал по пику — и получил разброс RMS в 14 дБ: костяные
    существа (щелчковый слой) при пике −1.5 звучали на −30 dBFS, то есть
    заметно тише всех остальных. В игре это читается как «этот моб шепчет».
    Теперь цель — RMS, а пик только ограничивается сверху.
    """
    rms = np.sqrt((x ** 2).mean())
    if rms < 1e-9:
        return x
    g = (10 ** (target_rms_db / 20)) / rms
    pk = np.abs(x).max() * g
    ceiling = 10 ** (peak_ceiling_db / 20)
    if pk > ceiling:
        g *= ceiling / pk
    return x * g


def tame(x, target_rms_db, ceiling_db=-1.5, rounds=6):
    """Громкость по RMS + мягкий лимитер по пику.

    У костяных существ (wither, stray, bogged) crest 25–29: щелчковый слой даёт
    редкие пики на фоне тихого тела. Если просто ограничить пик, RMS падает до
    −30 и моб «шепчет». Поэтому пики мягко поджимаются tanh, а громкость
    возвращается к цели — crest уменьшается, энергия сохраняется.
    """
    ceil = 10 ** (ceiling_db / 20)
    for _ in range(rounds):
        rms = np.sqrt((x ** 2).mean())
        if rms < 1e-9:
            return x
        x = x * ((10 ** (target_rms_db / 20)) / rms)
        pk = np.abs(x).max()
        if pk <= ceil:
            return x
        x = np.tanh(x / ceil) * ceil
    rms = np.sqrt((x ** 2).mean())
    return x * ((10 ** (target_rms_db / 20)) / rms) if rms > 1e-9 else x


def main():
    ents = json.load(open('/tmp/ents.json'))
    made = []
    for ent in ents:
        key = ent.replace('infected_', '')
        p = BODY[key]
        rng = rng_for(ent)
        for event in ('ambient', 'attack', 'hurt', 'death'):
            x = render(ent, event, p, rng)
            # цель по громкости: ambient тише (это фон), события — вровень
            target_rms = {'ambient': -23.0, 'attack': -19.0, 'hurt': -19.0, 'death': -20.0}[event]
            x = tame(x, target_rms)
            name = f"{ent}_{event}_01"
            raw = f"/tmp/rw/{name}.f32"
            np.asarray(x, dtype=np.float32).tofile(raw)
            br = '96k' if event == 'ambient' else '160k'
            os.makedirs('03-sound/sounds_380/entity', exist_ok=True)
            out = f"03-sound/sounds_380/entity/{name}.ogg"
            subprocess.run([FF, '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1',
                            '-i', raw, '-c:a', 'libvorbis', '-b:a', br, '-map_metadata', '-1', out], check=True)
            made.append(name)
    print(json.dumps(made))
    print(f"сделано: {len(made)}", flush=True)


if __name__ == '__main__':
    main()
