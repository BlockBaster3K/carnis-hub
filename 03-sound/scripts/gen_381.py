#!/usr/bin/env python3
"""Генератор звуков для 8 вариантов мобов 3.8.1 (промпт sound_prompt_381.md).

ВАЖНО О СТАТУСЕ: события в sounds.json на момент генерации НЕ объявлены
Кодером (в 3.8.1 те же 214 событий, что в 3.8.0, ни одного варианта моба).
Поэтому имена событий здесь — РАБОЧИЕ имена файлов; их надо согласовать с
объявлением в sounds.json, иначе получится 30 сирот (файлы без события).
Подробности и блокер — в 00-board/reports/sound_s131_variants_381.md.

Что нормируется (те же нормы, что у банка, не свои):
  * моно, 44.1 кГц;
  * пик <= -1.40 dBFS (потолок банка -1.20 плюс запас 0.20);
  * crest 18.0 +- 0.3 дБ — ровно та цель, к которой я привёл канон в S128,
    чтобы внутри события не было разброса и громкость выравнивалась множителем;
  * длина точная (сэмпл-в-сэмпл по декоду ffmpeg).

Синтез, не сэмплы: у проекта нет библиотеки сэмплов, а брать чужие записи
нельзя (лицензии проверяются отдельно). Все звуки собраны из шума с полосовой
фильтрацией, тональных составляющих с огибающими и негармонических «металлических»
партиалов — это стандартный приём для процедурных звуков, и он даёт
воспроизводимый результат при повторном запуске (фиксированные seed).

CLI:
  python3 gen_381.py --out DIR [--only PREFIX]
"""
import argparse
import math
import os
import subprocess
import sys

import numpy as np
from scipy.signal import butter, sosfiltfilt

SR = 44100
CREST_TARGET = 18.0
CREST_TOL = 0.3
PEAK_MAX = -1.40


def _ff():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:                                   # noqa: BLE001
        return "ffmpeg"


def bp(x, lo, hi, order=4):
    hi = min(hi, SR / 2.0 - 100)
    return sosfiltfilt(butter(order, [lo / (SR / 2), hi / (SR / 2)],
                              btype="band", output="sos"), x)


def noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def sweep_tone(n, f0, f1, kind="exp"):
    t = np.arange(n) / SR
    if kind == "exp" and f0 > 0 and f1 > 0:
        f = f0 * (f1 / f0) ** (t / max(t[-1], 1e-9))
    else:
        f = np.linspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph)


def env_ad(n, attack, decay_pow=2.0):
    """Атака + спад; attack и decay_pow в секундах и показателе."""
    a = max(1, int(attack * SR))
    e = np.exp(-np.arange(n) / SR * decay_pow)
    e[:a] *= np.linspace(0, 1, a)
    return e


def fade_tail(x, ms=12):
    n = max(1, int(ms / 1000 * SR))
    n = min(n, len(x))
    x = x.copy()
    x[-n:] *= np.linspace(1, 0, n)
    return x


def metal(n, partials, decay):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f, a in partials:
        out += a * np.sin(2 * np.pi * f * t) * np.exp(-t * decay)
    return out


def squelch(n, seed, lo=180, hi=2600, mod=18.0):
    """Влажный звук: шум через узкие полосы с качанием."""
    x = noise(n, seed)
    t = np.arange(n) / SR
    a = bp(x, lo, hi)
    b = bp(x, lo * 2.2, hi * 0.8)
    wob = 0.55 + 0.45 * np.sin(2 * np.pi * mod * t)
    return a * wob + 0.6 * b * (1 - wob)


def shape_crest(x, crest=CREST_TARGET, max_iter=20):
    """Довести crest до цели В ОБЕ СТОРОНЫ.

    Срез (`clip`) умеет только понижать. Плотные звуки (шумовые и раскатистые)
    имеют crest 10.8–16 и до цели не дотягивают — замерено: `creeper_b_charge`
    11.05, `spider_a_web` 12.56, при цели 18.0.

    Вверх — степенное расширение |y|**p с p > 1: громкое остаётся, тихое
    придавливается, crest растёт. Показатель подбирается бисекцией по
    фактическому замеру, а не по формуле. Вниз — срез, как в crest_redraw.

    ⚠ Первая версия этой функции была неверна дважды и оба раза это ловилось
    прогоном, а не чтением: (1) знак — пик брался НИЖЕ RMS, RMS уезжал в
    −18 dBFS; (2) срез применялся к массиву, который уже был упёрт в свой
    максимум (0.851), поэтому не менял ничего (12.56 → 12.56).
    """
    y = np.array(x, dtype=np.float64)
    lo_rms = float(np.sqrt((y ** 2).mean())) + 1e-12
    y = y / lo_rms
    cur = 20 * math.log10(float(np.abs(y).max()))
    if cur < crest - 0.02:                      # не хватает динамики — вверх
        lo, hi = 1.0, 6.0
        for _ in range(40):
            mid = (lo + hi) / 2.0
            z = np.sign(y) * np.abs(y) ** mid
            if 20 * math.log10(float(np.abs(z).max())) < crest:
                lo = mid
            else:
                hi = mid
        y = np.sign(y) * np.abs(y) ** ((lo + hi) / 2.0)
    for _ in range(max_iter):                   # лишнее — вниз, срезом
        rms = float(np.sqrt((y ** 2).mean()))
        c = rms * 10 ** (crest / 20.0)
        y = np.clip(y, -c, c)
        if crest - (20 * math.log10(float(np.abs(y).max() / rms))) < 0.02:
            break
    return y


def place_peak(x, peak_db=PEAK_MAX):
    """Масштабировать так, чтобы пик встал ровно на peak_db (crest не меняется)."""
    pk = float(np.abs(x).max())
    if pk <= 0:
        raise ValueError("тишина")
    return x * (10 ** (peak_db / 20.0) / pk)


def finish(x, crest=CREST_TARGET, peak_db=PEAK_MAX):
    """Форма: crest к цели, затем пик на потолок банка. Порядок важен."""
    return place_peak(shape_crest(x, crest), peak_db)


def normalize(x, crest=CREST_TARGET):
    return finish(x, crest)


def declick(x, ms=4):
    n = min(len(x), int(ms / 1000 * SR))
    x = x.copy()
    x[:n] *= np.linspace(0, 1, n)
    return fade_tail(x, ms)


def encode(x, path, br="160k"):
    """Кодировать PCM в OGG Vorbis.

    ⚠ `-fflags +bitexact` обязателен. Без него libvorbis вставляет в заголовок
    Ogg СЛУЧАЙНЫЙ serial (замер: c250b819 против d6c00ac1 при одном и том же
    PCM), и два прогона генератора дают разные байты — проверено, 0 совпадений
    из 27. Звук при этом идентичен: PCM после декодирования совпадал побитово,
    различались 31 байт из 27685 (0,1 %) — только служебные поля.
    С флагом serial = 00000000 и сборка воспроизводима побайтово.
    Побочная польза: SHA-256 в отчётах начинает значить «этот звук», а не
    «этот конкретный прогон».
    """
    subprocess.run([_ff(), "-v", "error", "-y", "-f", "f32le", "-ar", str(SR),
                    "-ac", "1", "-i", "-", "-c:a", "libvorbis", "-b:a", br,
                    "-fflags", "+bitexact", path],
                   input=x.astype(np.float32).tobytes(), check=True)


# ---------------------------------------------------------------- звуки
def z_cleave_swing(seed):
    d = 0.42; n = int(d * SR); t = np.arange(n) / SR
    air = bp(noise(n, seed), 700, 7000) * np.exp(-t * 7) * np.exp(-((t - 0.13) ** 2) / 0.004)
    body = sweep_tone(n, 260, 90) * np.exp(-t * 12) * 0.5
    return normalize(declick(air * 0.9 + body))


def z_cleave_hit(seed):
    d = 0.5; n = int(d * SR); t = np.arange(n) / SR
    thud = bp(noise(n, seed), 45, 180) * np.exp(-t * 22)
    flesh = squelch(n, seed + 1, 150, 1800) * np.exp(-t * 16) * 0.8
    low = sweep_tone(n, 120, 55) * np.exp(-t * 20) * 0.7
    return normalize(declick(thud + flesh + low))


def z_bleed_apply(seed):
    d = 0.85; n = int(d * SR); t = np.arange(n) / SR
    drips = sum(squelch(n, seed + k, 300 + 90 * k, 2200) *
                np.exp(-((t - 0.10 - 0.16 * k) ** 2) / 0.0025) * (0.9 - 0.15 * k)
                for k in range(4))
    sting = sweep_tone(n, 420, 180) * np.exp(-t * 5) * 0.25
    return normalize(declick(drips + sting))


def z_leap(seed):
    d = 0.6; n = int(d * SR); t = np.arange(n) / SR
    air = bp(noise(n, seed), 400, 3800) * env_ad(n, 0.01, 6.0)
    growl = sweep_tone(n, 150, 240) * env_ad(n, 0.02, 9.0) * 0.6
    return normalize(declick(air + growl))


def z_bite_quick(seed):
    d = 0.7; n = int(d * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    for k, dt in enumerate((0.02, 0.20, 0.36)):
        snap = bp(noise(n, seed + k), 900, 6500) * np.exp(-((t - dt) ** 2) / 0.0009)
        chomp = sweep_tone(n, 220, 120) * np.exp(-((t - dt) ** 2) / 0.004)
        out += snap * 0.8 + chomp * 0.5
    return normalize(declick(out))


def z_vampiric(seed):
    d = 1.0; n = int(d * SR); t = np.arange(n) / SR
    slurp = squelch(n, seed, 120, 1500, mod=9) * env_ad(n, 0.05, 3.5)
    rise = sweep_tone(n, 90, 260) * env_ad(n, 0.2, 3.0) * 0.45
    return normalize(declick(slurp + rise))


def z_slowness(seed):
    d = 1.1; n = int(d * SR); t = np.arange(n) / SR
    sticky = squelch(n, seed, 90, 900, mod=4) * env_ad(n, 0.06, 2.5)
    sag = sweep_tone(n, 300, 70) * env_ad(n, 0.03, 4.0) * 0.5
    return normalize(declick(sticky + sag))


def sk_bow_draw(seed):
    d = 2.5; n = int(d * SR); t = np.arange(n) / SR
    creak = bp(noise(n, seed), 250, 2400) * (0.35 + 0.65 * np.abs(np.sin(2 * np.pi * 7 * t)))
    creak *= np.clip(t / 2.2, 0, 1) ** 0.7 * np.exp(-np.maximum(0, t - 2.2) * 6)
    string = sweep_tone(n, 320, 520) * 0.18 * np.clip(t / 2.2, 0, 1)
    return normalize(declick(creak + string, 6))


def sk_shot(seed):
    d = 0.45; n = int(d * SR); t = np.arange(n) / SR
    snap = bp(noise(n, seed), 800, 9000) * np.exp(-t * 40)
    tone = sweep_tone(n, 700, 200) * np.exp(-t * 18) * 0.5
    return normalize(declick(snap * 0.9 + tone))


def sk_armor_pierce(seed):
    d = 0.7; n = int(d * SR); t = np.arange(n) / SR
    ring = metal(n, [(1750, 0.5), (2620, 0.4), (3690, 0.3), (5100, 0.2)], 7)
    crack = bp(noise(n, seed), 1200, 8000) * np.exp(-t * 30) * 0.7
    return normalize(declick(ring + crack))


def sk_pike_thrust(seed):
    d = 0.5; n = int(d * SR); t = np.arange(n) / SR
    whoosh = bp(noise(n, seed), 300, 3000) * np.exp(-((t - 0.1) ** 2) / 0.006)
    point = sweep_tone(n, 400, 150) * np.exp(-t * 25) * 0.6
    return normalize(declick(whoosh + point))


def sk_parry_ricochet(seed):
    d = 0.8; n = int(d * SR); t = np.arange(n) / SR
    clang = metal(n, [(2100, 0.5), (3300, 0.35), (4700, 0.25)], 9)
    sparks = sum(bp(noise(n, seed + k), 3000, 9000) *
                 np.exp(-((t - 0.05 - 0.09 * k) ** 2) / 0.0008) * (0.7 - 0.15 * k)
                 for k in range(4))
    return normalize(declick(clang + sparks * 0.6))


def sp_jump(seed):
    d = 0.45; n = int(d * SR); t = np.arange(n) / SR
    scuttle = bp(noise(n, seed), 900, 5200) * env_ad(n, 0.006, 12.0)
    push = sweep_tone(n, 260, 120) * env_ad(n, 0.01, 16.0) * 0.5
    return normalize(declick(scuttle + push))


def sp_land(seed):
    d = 0.55; n = int(d * SR); t = np.arange(n) / SR
    thud = bp(noise(n, seed), 50, 220) * np.exp(-t * 26)
    chitin = metal(n, [(620, 0.4), (980, 0.3), (1500, 0.2)], 14)
    return normalize(declick(thud + chitin * 0.5))


def sp_web(seed):
    d = 0.85; n = int(d * SR); t = np.arange(n) / SR
    spit = bp(noise(n, seed), 1800, 7000) * np.exp(-t * 22)
    strand = sum(sweep_tone(n, 900 - 120 * k, 400 - 60 * k) *
                 np.exp(-((t - 0.08 - 0.13 * k) ** 2) / 0.003) for k in range(3))
    return normalize(declick(spit * 0.8 + strand * 0.45))


def sp_paralytic(seed):
    d = 1.2; n = int(d * SR); t = np.arange(n) / SR
    buzz = bp(noise(n, seed), 2200, 6500) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 26 * t)))
    buzz *= env_ad(n, 0.03, 2.2)
    sting = sweep_tone(n, 640, 140) * np.exp(-t * 3) * 0.3
    return normalize(declick(buzz + sting))


def sp_leg_slam(seed):
    d = 0.75; n = int(d * SR); t = np.arange(n) / SR
    slam = bp(noise(n, seed), 40, 200) * np.exp(-t * 18)
    legs = sum(bp(noise(n, seed + k), 700, 3000) *
               np.exp(-((t - 0.05 - 0.11 * k) ** 2) / 0.0012) * (0.6 - 0.12 * k)
               for k in range(3))
    return normalize(declick(slam + legs * 0.7))


def sp_shockwave(seed):
    d = 1.0; n = int(d * SR); t = np.arange(n) / SR
    boom = bp(noise(n, seed), 30, 160) * np.exp(-t * 9)
    push = sweep_tone(n, 90, 40) * np.exp(-t * 6) * 0.8
    grit = bp(noise(n, seed + 1), 400, 2400) * np.exp(-t * 12) * 0.35
    return normalize(declick(boom + push + grit, 8))


def sp_shield_break(seed):
    d = 0.9; n = int(d * SR); t = np.arange(n) / SR
    shatter = metal(n, [(1400, 0.4), (2350, 0.35), (3900, 0.25), (6200, 0.15)], 11)
    chunks = sum(bp(noise(n, seed + k), 1500, 8000) *
                 np.exp(-((t - 0.06 - 0.1 * k) ** 2) / 0.001) * (0.6 - 0.1 * k)
                 for k in range(5))
    return normalize(declick(shatter * 0.8 + chunks * 0.5))


def cr_anchor(seed):
    d = 1.3; n = int(d * SR); t = np.arange(n) / SR
    roots = squelch(n, seed, 60, 700, mod=3) * env_ad(n, 0.15, 2.0)
    peg = metal(n, [(420, 0.3), (700, 0.2)], 6) * 0.4
    return normalize(declick(roots + peg, 8))


def cr_launch(seed):
    d = 0.7; n = int(d * SR); t = np.arange(n) / SR
    puff = bp(noise(n, seed), 250, 2800) * np.exp(-t * 10)
    rise = sweep_tone(n, 160, 480) * np.exp(-t * 8) * 0.6
    return normalize(declick(puff + rise))


def cr_poison_cloud(seed):
    d = 1.6; n = int(d * SR); t = np.arange(n) / SR
    hiss = bp(noise(n, seed), 500, 5000) * (0.5 + 0.5 * np.sin(2 * np.pi * 3.5 * t))
    hiss *= env_ad(n, 0.25, 1.6)
    low = sweep_tone(n, 120, 70) * env_ad(n, 0.4, 1.4) * 0.35
    return normalize(declick(hiss + low, 10))


def cr_death_blast(seed):
    d = 1.4; n = int(d * SR); t = np.arange(n) / SR
    boom = bp(noise(n, seed), 28, 180) * np.exp(-t * 5)
    boom += sweep_tone(n, 80, 32) * np.exp(-t * 4) * 1.0
    debris = bp(noise(n, seed + 1), 900, 6000) * np.exp(-t * 8) * 0.4
    return normalize(declick(boom + debris, 12))


def cr_freeze(seed):
    d = 0.8; n = int(d * SR); t = np.arange(n) / SR
    charge = bp(noise(n, seed), 400, 3000) * np.clip(t / 0.7, 0, 1) ** 1.5
    hum = sweep_tone(n, 220, 300) * np.clip(t / 0.7, 0, 1) * 0.4
    return normalize(declick(charge + hum))


def cr_charge(seed):
    d = 1.0; n = int(d * SR); t = np.arange(n) / SR
    run = bp(noise(n, seed), 300, 2600) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 11 * t)))
    roar = sweep_tone(n, 120, 200) * np.clip(t / 0.5, 0, 1) * 0.7
    return normalize(declick(run + roar, 6))


def cr_shield_drop(seed):
    d = 0.8; n = int(d * SR); t = np.arange(n) / SR
    clank = metal(n, [(900, 0.45), (1500, 0.3), (2400, 0.2)], 12)
    drop = bp(noise(n, seed), 80, 900) * np.exp(-t * 9) * 0.6
    return normalize(declick(clank + drop))


def cr_directed_blast(seed):
    d = 1.1; n = int(d * SR); t = np.arange(n) / SR
    jet = bp(noise(n, seed), 200, 4500) * np.exp(-t * 7)
    boom = bp(noise(n, seed + 2), 35, 200) * np.exp(-t * 6)
    return normalize(declick(jet + boom, 10))


REGISTRY = [
    ("zombie_a_cleave_swing", z_cleave_swing),
    ("zombie_a_cleave_hit", z_cleave_hit),
    ("zombie_a_bleed_apply", z_bleed_apply),
    ("zombie_b_leap", z_leap),
    ("zombie_b_bite_quick", z_bite_quick),
    ("zombie_b_vampiric", z_vampiric),
    ("zombie_b_slowness", z_slowness),
    ("skeleton_a_bow_draw", sk_bow_draw),
    ("skeleton_a_shot", sk_shot),
    ("skeleton_a_armor_pierce", sk_armor_pierce),
    ("skeleton_b_pike_thrust", sk_pike_thrust),
    ("skeleton_b_parry_ricochet", sk_parry_ricochet),
    ("spider_a_jump", sp_jump),
    ("spider_a_land", sp_land),
    ("spider_a_web", sp_web),
    ("spider_a_paralytic", sp_paralytic),
    ("spider_b_leg_slam", sp_leg_slam),
    ("spider_b_shockwave", sp_shockwave),
    ("spider_b_shield_break", sp_shield_break),
    ("creeper_a_anchor", cr_anchor),
    ("creeper_a_launch", cr_launch),
    ("creeper_a_poison_cloud", cr_poison_cloud),
    ("creeper_a_death_blast", cr_death_blast),
    ("creeper_b_freeze", cr_freeze),
    ("creeper_b_charge", cr_charge),
    ("creeper_b_shield_drop", cr_shield_drop),
    ("creeper_b_directed_blast", cr_directed_blast),
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default=None)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import crest_redraw as C                       # мерим тем же декодером

    print("%-30s %8s %7s %7s %6s %7s" %
          ("файл", "отсчётов", "RMS", "пик", "crest", "байт"))
    bad = 0
    for i, (name, fn) in enumerate(REGISTRY):
        if a.only and not name.startswith(a.only):
            continue
        raw = fn(seed=1000 + i * 7)
        path = os.path.join(a.out, name + ".ogg")
        # Vorbis добавляет собственный crest (шумовые пики), поэтому цель
        # подбирается по ФАКТУ после кодирования: измерили -> поправили цель.
        # 1) crest по факту после кодирования (Vorbis добавляет свои пики);
        # 2) пик по факту тоже: кодек даёт перелёт −1.40 → −1.33, поэтому цель
        #    по пику опускается, пока измеренный не встанет под потолок.
        target, peak_t = CREST_TARGET, PEAK_MAX
        for _ in range(6):
            encode(finish(raw, target, peak_t), path)
            y = C.decode(path)
            got = (20 * math.log10(float(np.abs(y).max()))
                   - 20 * math.log10(float(np.sqrt((y ** 2).mean()))))
            got_pk = 20 * math.log10(float(np.abs(y).max()))
            if abs(got - CREST_TARGET) <= 0.10 and got_pk <= PEAK_MAX:
                break
            target -= (got - CREST_TARGET)
            target = max(10.0, min(26.0, target))
            if got_pk > PEAK_MAX:
                peak_t -= (got_pk - PEAK_MAX) + 0.02
            peak_t = max(-12.0, min(-0.5, peak_t))
        rms = 20 * math.log10(float(np.sqrt((y ** 2).mean())))
        pk = 20 * math.log10(float(np.abs(y).max()))
        cr = pk - rms
        problems = []
        if abs(cr - CREST_TARGET) > CREST_TOL:
            problems.append("crest")
        if pk > PEAK_MAX + 1e-6:
            problems.append("пик")
        bad += 1 if problems else 0
        print("%-30s %8d %7.2f %7.2f %6.2f %7d %s" %
              (name, len(y), rms, pk, cr, os.path.getsize(path),
               "" if not problems else "✗ " + ",".join(problems)))
    print("\nфайлов с замечаниями: %d" % bad)
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
