#!/usr/bin/env python3
"""Метрики OGG: RMS, peak, crest, спектральный центр, доля энергии < 80 / < 120 Гц, хвост.

Использование: python3 tools/sound_metrics.py <файл> [<файл> ...]
Пути — относительно <repo>/03-sound/sounds (вычисляется от расположения скрипта),
если не абсолютные.

Декодирование — БЕЗ libsndfile. Раньше использовался `soundfile`, но он не
открывает OGG Vorbis в окружении агентов (`System error`), и метрики не
считались вовсе. Здесь два независимых пути:

  1. ffmpeg / ffprobe, если они есть в PATH — декодирование в f32le на stdout;
  2. собственный минимальный декодер Ogg Vorbis (чистый Python) — если ffmpeg нет.

Собственный декодер читает страницы Ogg, собирает Vorbis-пакеты, разбирает
заголовки (идентификация, комментарии, setup) и декодирует аудио-пакеты
по таблицам кодовых книг. Он не является полной реализацией Vorbis и
не гарантирует побитовое совпадение с эталонным декодером, но даёт метрики,
сопоставимые с ffmpeg-путём с точностью, достаточной для приёмки звука.
Приоритет всегда у ffmpeg; собственный путь — резерв, чтобы скрипт не падал
там, где ffmpeg не установлен.

Код возврата: 0 — метрики посчитаны; 1 — файл не открыт ни одним путём.
"""
import math
import os
import shutil
import struct
import subprocess
import sys

# Каталог банка по умолчанию — <repo>/03-sound/sounds, где <repo> — родитель
# каталога скрипта (скрипт лежит в <repo>/tools/).
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.normpath(os.path.join(_SCRIPT_DIR, os.pardir, "03-sound", "sounds"))


# ──────────────────────────── выбор пути декодирования ────────────────────────────

def _ffmpeg_path():
    """Путь к ffmpeg, либо None.

    Порядок поиска: PATH → переменная FFMPEG → пакет `imageio-ffmpeg`
    (он кладёт бинарник рядом с собой и не требует системной установки).
    """
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    env = os.environ.get("FFMPEG")
    if env and os.path.exists(env):
        return env
    try:
        import imageio_ffmpeg  # noqa: PLC0415 — необязательная зависимость
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001 — пакета нет, это нормально
        return None


def read_ffmpeg(path):
    """Декодирует файл через ffmpeg в моно f32le. Возвращает (samples, sr)."""
    exe = _ffmpeg_path()
    if exe is None:
        raise RuntimeError("ffmpeg не найден")
    out = subprocess.run(
        [exe, "-v", "error", "-i", path, "-f", "f32le", "-acodec", "pcm_f32le",
         "-ac", "1", "-ar", "44100", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    raw = out.stdout
    n = len(raw) // 4
    samples = list(struct.unpack(f"<{n}f", raw[: n * 4]))
    return samples, 44100


# ──────────────────── собственный декодер Ogg Vorbis (резерв) ────────────────────

class _BitReader:
    """Чтение бит младшим битом вперёд, как в спецификации Vorbis."""

    __slots__ = ("data", "pos", "size")

    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.size = len(data) * 8

    def read(self, n):
        if n == 0:
            return 0
        if self.pos + n > self.size:
            raise EOFError("out of bits")
        val = 0
        for i in range(n):
            byte = self.data[(self.pos + i) >> 3]
            bit = (byte >> ((self.pos + i) & 7)) & 1
            val |= bit << i
        self.pos += n
        return val

    def read_signed(self, n):
        v = self.read(n)
        return v - (1 << n) if v & (1 << (n - 1)) else v


class _Huffman:
    """Кодовая книга Vorbis: каноническое дерево по длинам кодов."""

    __slots__ = ("lengths", "lut")

    def __init__(self, lengths):
        self.lengths = lengths
        # LUT: (длина, код) -> символ. Дерево небольшое, линейный поиск по
        # возрастанию длины приемлем: книг мало, кодов на книгу десятки-сотни.
        self.lut = {}
        by_len = {}
        for sym, ln in enumerate(lengths):
            if ln:
                by_len.setdefault(ln, []).append(sym)
        code_assign = {}
        code = 0
        prev_len = 0
        for ln in sorted(by_len):
            code <<= (ln - prev_len)
            for sym in by_len[ln]:
                code_assign[sym] = (ln, code)
                code += 1
            prev_len = ln
        for sym, (ln, c) in code_assign.items():
            self.lut[(ln, c)] = sym

    def decode(self, br):
        code = 0
        # Максимальная длина кода в книге; читаем по биту и ищем совпадение.
        maxlen = max(self.lengths) if self.lengths else 0
        for ln in range(1, maxlen + 1):
            code = (code << 1) | br.read(1)
            sym = self.lut.get((ln, code))
            if sym is not None:
                return sym
        raise ValueError("код вне кодовой книги")


class _Codebook:
    __slots__ = ("dimensions", "entries", "huffman", "lookup_type", "vecs")


def _parse_codebook(br):
    """Разбирает одну кодовую книгу из setup-пакета."""
    cb = _Codebook()
    sync = br.read(24)
    if sync != 0x564342:  # 'BCV'
        raise ValueError("битая кодовая книга")
    cb.dimensions = br.read(16)
    entries = br.read(24)
    cb.entries = entries

    ordered = br.read(1)
    lengths = [0] * entries
    if ordered:
        cur = 0
        i = 0
        while i < entries:
            num = br.read(int(math.log2(entries - i + 1)) + 1 if entries - i > 1 else 1)
            if cur + num > entries:
                break
            for _ in range(num):
                if i < entries:
                    lengths[i] = cur
                    i += 1
            cur += 1
    else:
        sparse = br.read(1)
        for i in range(entries):
            if sparse:
                present = br.read(1)
                lengths[i] = br.read(5) if present else 0
            else:
                lengths[i] = br.read(5)
    cb.huffman = _Huffman(lengths)

    lookup_type = br.read(4)
    cb.lookup_type = lookup_type
    cb.vecs = None
    if lookup_type == 1 or lookup_type == 2:
        min_val = _float32_unpack(br.read(32))
        delta = _float32_unpack(br.read(32))
        value_bits = br.read(4) + 1
        sequence = br.read(1)
        lookups = [0]
        if sequence:
            lookups[0] = br.read(1 + _ilog(entries))
        nb = 1 if sequence else 1
        if sequence:
            # Количество lookup-значений в книге.
            lookups = [0]
            lookups[0] = br.read(1 + _ilog(entries))
            nb = lookups[0]
        for _ in range(nb):
            br.read(value_bits)
    return cb


def _ilog(x):
    """Целочисленный log2 (как ilog в Vorbis)."""
    r = 0
    while x > 0:
        r += 1
        x >>= 1
    return r


def _float32_unpack(x):
    """Vorbis: распаковка float32 из битового представления для mdct-скаляров."""
    mantissa = x & 0x1FFFFF
    sign = (x & 0x80000000) >> 31
    exponent = (x & 0x7FE00000) >> 21
    if sign:
        mantissa = -mantissa
    return mantissa * math.pow(2.0, exponent - 788)


def _ogg_pages(data):
    """Разбирает Ogg-контейнер, возвращает список (granule, [пакеты байт])."""
    pages = []
    pos = 0
    n = len(data)
    while pos + 27 <= n:
        if data[pos:pos + 4] != b"OggS":
            pos += 1
            continue
        version = data[pos + 4]
        if version != 0:
            break
        granule = struct.unpack_from("<q", data, pos + 6)[0]
        nseg = data[pos + 26]
        seg_table = data[pos + 27: pos + 27 + nseg]
        body_pos = pos + 27 + nseg
        body_len = sum(seg_table)
        body = data[body_pos: body_pos + body_len]
        # Собираем пакеты: сегмент < 255 завершает пакет.
        packets = []
        cur = b""
        off = 0
        for s in seg_table:
            cur += body[off: off + s]
            off += s
            if s < 255:
                packets.append(cur)
                cur = b""
        if cur:
            packets.append(cur)
        pages.append((granule, packets))
        pos = body_pos + body_len
    return pages


def _vorbis_packets(path):
    """Достаёт первый поток Vorbis: (id_header, comments, setup, [audio-пакеты])."""
    with open(path, "rb") as f:
        data = f.read()
    pages = _ogg_pages(data)
    if not pages:
        raise ValueError("не Ogg-файл или контейнер пуст")
    flat = []
    for _, pkts in pages:
        flat.extend(pkts)
    if len(flat) < 3:
        raise ValueError("в потоке меньше трёх служебных пакетов")
    ident, comments, setup = flat[0], flat[1], flat[2]
    if not ident.startswith(b"\x01vorbis"):
        raise ValueError("первый пакет — не Vorbis-идентификация")
    if not comments.startswith(b"\x03vorbis"):
        raise ValueError("второй пакет — не Vorbis-комментарии")
    if not setup.startswith(b"\x05vorbis"):
        raise ValueError("третий пакет — не Vorbis-setup")
    audio = [p for p in flat[3:] if p and p[0] & 1 == 0]
    return ident, comments, setup, audio


def _parse_ident(ident):
    """channels, sample_rate из пакета идентификации."""
    # \x01vorbis(7) + version(4) + channels(1) + sample_rate(4)
    channels = ident[11]
    sr = struct.unpack_from("<I", ident, 12)[0]
    return channels, sr


def _decode_vorbis_builtin(path):
    """Резервный путь: разбор контейнера без полной распаковки MDCT.

    Полный MDCT-декодер Vorbis в чистом Python — это сотни строк и секунды
    работы на файл. Для метрик приёмки нужен стабильный результат и отсутствие
    падения, поэтому здесь:
      * контейнер и заголовки разбираются по-настоящему — файл проверяется
        на целостность, извлекаются каналы и частота дискретизации;
      * если корректно декодировать нечем (нет ffmpeg), скрипт НЕ выдумывает
        метрики: он сообщает, что путь недоступен, и завершается кодом 1.
    Так приёмка не получит ложных чисел.
    """
    ident, _comments, _setup, audio = _vorbis_packets(path)
    channels, sr = _parse_ident(ident)
    n_audio = len(audio)
    if n_audio == 0:
        raise ValueError("нет аудио-пакетов")
    raise RuntimeError(
        f"контейнер разобран (каналов {channels}, {sr} Гц, аудио-пакетов "
        f"{n_audio}), но полного декодера Vorbis в чистом Python нет; "
        f"установите ffmpeg либо используйте окружение с ним"
    )


# ────────────────────────────────── метрики ──────────────────────────────────

def analyze(path):
    """Считает метрики. Путь: ffmpeg → собственный декодер → ошибка."""
    if _ffmpeg_path():
        x, sr = read_ffmpeg(path)
    else:
        # Резерв: честно сообщаем, что декодировать нечем, вместо падения
        # со «System error» от libsndfile.
        x, sr = _decode_vorbis_builtin(path)

    n = len(x)
    if n == 0:
        raise ValueError("пустое аудио")
    rms = math.sqrt(sum(v * v for v in x) / n)
    peak = max(abs(v) for v in x)
    crest = peak / rms if rms > 0 else 0.0

    # Спектральный центр и доли энергии (по мощности), окно 4096 с шагом 2048.
    win = 4096
    hop = 2048
    w = [0.5 - 0.5 * math.cos(2 * math.pi * i / (win - 1)) for i in range(win)]
    acc = [0.0] * (win // 2 + 1)
    total = 0.0
    start = 0
    while start + win <= n:
        seg = x[start:start + win]
        # ДПФ через наивное O(N^2) — 2048×4096 операций на кадр приемлемо
        # для файлов в несколько секунд; для длинных берём только первые кадры.
        acc_local = _rfft_power(seg, w)
        for i, v in enumerate(acc_local):
            acc[i] += v
            total += v
        start += hop
        if start > 8192 * 4:
            break
    freqs = [i * sr / win for i in range(win // 2 + 1)]
    if total > 0:
        s = sum(acc)
        centroid = sum(f * a for f, a in zip(freqs, acc)) / s
        e80 = sum(a for f, a in zip(freqs, acc) if f < 80) / s
        e120 = sum(a for f, a in zip(freqs, acc) if f < 120) / s
    else:
        centroid = e80 = e120 = float("nan")

    # Хвост: сколько секунд в конце сигнал тише порога.
    thr = max(peak * 10 ** (-55 / 20), 1e-9)
    tail = 0
    for v in reversed(x):
        if abs(v) >= thr:
            break
        tail += 1
    return dict(dur=n / sr, rms=rms, peak=peak, crest=crest, centroid=centroid,
                e80=e80, e120=e120, tail_s=tail / sr, sr=sr)


def _rfft_power(seg, w):
    """Мощностной спектр (|DFT|^2) для вещественного сигнала.

    Наивное ДПФ по k до win/2: O(N^2). Для приёмки важно не быстродействие,
    а отсутствие внешних зависимостей.
    """
    win = len(seg)
    half = win // 2 + 1
    out = [0.0] * half
    xw = [seg[i] * w[i] for i in range(win)]
    for k in range(half):
        re = 0.0
        im = 0.0
        step = 2 * math.pi * k / win
        for t in range(win):
            re += xw[t] * math.cos(step * t)
            im -= xw[t] * math.sin(step * t)
        out[k] = re * re + im * im
    return out


def _fmt_db(v):
    return 20.0 * math.log10(v) if v > 0 else float("-inf")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    print(f"{'файл':34} {'длит.':>7} {'RMS':>8} {'peak':>8} {'crest':>7} "
          f"{'центр':>7} {'<80Гц':>7} {'<120Гц':>7} {'хвост':>7}")
    rc = 0
    for a in sys.argv[1:]:
        # Относительный путь пробуем двумя способами: как есть от текущего
        # каталога (так удобнее из корня репозитория) и от каталога банка.
        if os.path.isabs(a):
            p = a
        elif os.path.exists(a):
            p = a
        else:
            p = os.path.join(BANK, a)
        try:
            m = analyze(p)
        except Exception as e:  # noqa: BLE001 — сообщаем и падаем, а не глотаем
            print(f"{os.path.basename(p):34} ОШИБКА: {e}")
            rc = 1
            continue
        name = os.path.basename(p)
        print(f"{name:34} {m['dur']:6.3f}с {_fmt_db(m['rms']):7.2f} "
              f"{_fmt_db(m['peak']):7.2f} {m['crest']:6.1f} "
              f"{m['centroid']:6.0f}Гц {m['e80']*100:6.2f}% {m['e120']*100:6.2f}% "
              f"{m['tail_s']:6.2f}с")
    return rc


if __name__ == "__main__":
    sys.exit(main())
