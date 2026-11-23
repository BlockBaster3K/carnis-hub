"""
carnis_px.py — инструментарий Художника (Carnis: Adaptive Hivemind)

Библиотека приёмов пиксель-арта для 16×16 текстур. Содержит ТОЛЬКО
инструменты и данные дизайна, заданные вручную: тональные карты (даётся
каждый из 4 оттенков), карты прожилок, позиции бликов, списки цветов.
Никакой случайной генерации: random не импортируется вовсе.

Скрипты конкретных текстур (flesh_block.py и т.д.) — самодостаточные,
этот файл нужен только для предпросмотра и служебных проверок.
"""

from PIL import Image

SIZE = 16


# ─────────────────────────────────────────────────────────────
# Примитивы
# ─────────────────────────────────────────────────────────────

def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blank():
    """Пустой холст (все пиксели 'не заданы' → поймается валидатором)."""
    return [[None] * SIZE for _ in range(SIZE)]


def wrap(v):
    return v % SIZE


def hdist(a, b):
    """Горизонтальное расстояние на торе (циклическое)."""
    d = abs(a - b) % SIZE
    return min(d, SIZE - d)


# ─────────────────────────────────────────────────────────────
# Тональная карта
# ─────────────────────────────────────────────────────────────

def paint_tone(tone_rows, tones):
    """
    tone_rows: 16 строк по 16 символов; '.' = не задан, остальное — ключ tones.
    tones: dict {symbol: (r, g, b)}.
    Возвращает буфер 16×16 (None = дырка).
    """
    buf = blank()
    for y in range(SIZE):
        row = tone_rows[y]
        assert len(row) == SIZE, f"строка {y}: длина {len(row)} != 16"
        for x in range(SIZE):
            k = row[x]
            if k == '.':
                continue
            buf[y][x] = tones[k]
    return buf


def put(buf, x, y, color):
    buf[y][x] = color


def hput(buf, x, y, color):
    """Покраска с горизонтальным заворотом (для seamless-краёв)."""
    buf[y][wrap(x)] = color


# ─────────────────────────────────────────────────────────────
# Прожилки по маске
# ─────────────────────────────────────────────────────────────

def paint_veins(buf, mask_rows, col, dot, glow=None):
    """
    mask_rows: 16 строк по 16 символов.
      '#' = тело прожилки, 'o' = блик (dot), '.' = пусто.
    col  — цвет тела прожилки;
    dot  — цвет влажного блика (1 пиксель);
    glow — опциональный цвет обвода: ставится на соседние пиксели
           вокруг прожилки, если они заданы и ещё не прожилка.
    Соседство 4-направленное; маска трактуется циклически по X и Y.
    """
    mask = [[False] * SIZE for _ in range(SIZE)]
    for y in range(SIZE):
        assert len(mask_rows[y]) == SIZE, f"маска, строка {y}"
        for x in range(SIZE):
            mask[y][x] = mask_rows[y][x] in ('#', 'o')

    if glow is not None:
        for y in range(SIZE):
            for x in range(SIZE):
                if mask[y][x]:
                    continue
                near = (mask[y][(x - 1) % SIZE] or mask[y][(x + 1) % SIZE]
                        or mask[(y - 1) % SIZE][x] or mask[(y + 1) % SIZE][x])
                if near and buf[y][x] is not None:
                    buf[y][x] = glow

    for y in range(SIZE):
        for x in range(SIZE):
            if mask_rows[y][x] == '#':
                buf[y][x] = col
            elif mask_rows[y][x] == 'o':
                buf[y][x] = dot


# ─────────────────────────────────────────────────────────────
# Сглаживание: убрать «дрожь» — резкие скачки между соседями
# ─────────────────────────────────────────────────────────────

def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def polish(buf, max_jump=26, cycles=3):
    """
    Убирает одиночные пиксели, слишком контрастные к 4 соседям.
    Правило ручного пиксель-арта: каждый пиксель принадлежит кластеру.
    Заменяем такой пиксель на тон, средний между ним и «медианным»
    соседом. Работает по кругу (seamless).
    """
    def median_neighbor(x, y):
        nb = [buf[(y - 1) % SIZE][x], buf[(y + 1) % SIZE][x],
              buf[y][(x - 1) % SIZE], buf[y][(x + 1) % SIZE]]
        nb = [c for c in nb if c is not None]
        nb.sort(key=_lum)
        return nb[len(nb) // 2]

    for _ in range(cycles):
        changed = 0
        snapshot = [[c for c in row] for row in buf]
        for y in range(SIZE):
            for x in range(SIZE):
                c = snapshot[y][x]
                if c is None:
                    continue
                nb = [snapshot[(y - 1) % SIZE][x], snapshot[(y + 1) % SIZE][x],
                      snapshot[y][(x - 1) % SIZE], snapshot[y][(x + 1) % SIZE]]
                nb = [n for n in nb if n is not None]
                if not nb:
                    continue
                # пиксель-выброс: заметно светлее/темнее ВСЕХ 4 соседей
                lum = _lum(c)
                if all(lum - _lum(n) > max_jump for n in nb) or \
                   all(_lum(n) - lum > max_jump for n in nb):
                    mn = median_neighbor(x, y)
                    buf[y][x] = tuple((c[i] + mn[i]) // 2 for i in range(3))
                    changed += 1
        if not changed:
            break
    return buf


# ─────────────────────────────────────────────────────────────
# Seamless-контроль: контрольный лист 3×3
# ─────────────────────────────────────────────────────────────

def seam_sheet(buf):
    """Собирает 3×3 тайл, чтобы глазами проверить стыки."""
    sheet = Image.new('RGBA', (SIZE * 3, SIZE * 3))
    tile = to_image(buf)
    for ty in range(3):
        for tx in range(3):
            sheet.paste(tile, (tx * SIZE, ty * SIZE))
    return sheet


def seam_metric(buf):
    """
    Средний перепад яркости через стык относительно среднего перепада
    внутри тайла. ~1.0 — стык не выделяется. > 1.4 — стык виден.
    """
    def lum(c):
        return _lum(c)
    inside = []
    for y in range(SIZE):
        for x in range(SIZE):
            a = buf[y][x]
            b = buf[y][(x + 1) % SIZE]
            if a and b:
                inside.append(abs(lum(a) - lum(b)))
    horiz = []
    for y in range(SIZE):
        a = buf[y][SIZE - 1]
        b = buf[y][0]
        if a and b:
            horiz.append(abs(lum(a) - lum(b)))
    vert = []
    for x in range(SIZE):
        a = buf[SIZE - 1][x]
        b = buf[0][x]
        if a and b:
            vert.append(abs(lum(a) - lum(b)))
    m_in = sum(inside) / max(1, len(inside))
    m_h = sum(horiz) / max(1, len(horiz))
    m_v = sum(vert) / max(1, len(vert))
    return round(m_h / max(m_in, 0.01), 2), round(m_v / max(m_in, 0.01), 2)


def brightness_range(buf):
    lums = [_lum(buf[y][x]) for y in range(SIZE) for x in range(SIZE) if buf[y][x]]
    return round(min(lums), 1), round(max(lums), 1)


# ─────────────────────────────────────────────────────────────
# Сборка / валидация / вывод
# ─────────────────────────────────────────────────────────────

def covered_count(buf):
    return sum(1 for row in buf for c in row if c is not None)


def main_share(buf, main_color, tol=12):
    """Доля пикселей, совпадающих с основным цветом (для «% покрытия сеткой»)."""
    n = 0
    for row in buf:
        for c in row:
            if c and all(abs(c[i] - main_color[i]) <= tol for i in range(3)):
                n += 1
    return round(100 * n / (SIZE * SIZE))


def to_image(buf):
    img = Image.new('RGBA', (SIZE, SIZE))
    for y in range(SIZE):
        for x in range(SIZE):
            c = buf[y][x]
            if c is not None:
                img.putpixel((x, y), c + (255,))
    return img


def save(buf, path):
    missing = [(x, y) for y in range(SIZE) for x in range(SIZE) if buf[y][x] is None]
    assert not missing, f"не заданы пиксели: {missing[:6]}…"
    img = to_image(buf)
    img.save(path)
    return img
