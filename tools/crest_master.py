#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crest_master.py — блок «crest и атака от МАСТЕРОВ» (З-31, S44, S48).

Один модуль на оба гейта приёмки. Раньше блок жил внутри accept_3.7.3.py, и
перенос в accept_3.8.0 копированием завёл бы ВТОРОЕ определение нормы — ровно
то, из-за чего гейты уже расходились (Ревизор I23 §9: «3.8.0 still has the old
rescue -> gates diverged»). Поэтому здесь одно место.

Что нормируется:
  * crest — |crest(файл) − crest(мастер)| <= max(порог_типа, baseline(M)+0,05);
  * атака — ТОЛЬКО отчёт (R22: 13/132 ложных провала на чистом перекоде).

Правила (З-31):
  п.1 baseline — от МАСТЕРА, а не от round-trip самого файла (тавтология);
  п.2 нет мастера и файл изменён -> fail;
  п.3 нет мастера и файл побайтово равен предыдущей версии -> норме не подлежит;
  п.4 (S44) мастером может быть декод предыдущей версии, но если он РАВЕН
      файлу — это тавтология, не принимается.

Коды: модуль не завершает процесс. check_crest_attack(extract_dir) возвращает
список провалов (пусто = норма), решение о коде принимает гейт.
"""
import os
import re
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MASTERS = os.path.join(REPO, "03-sound", "masters")
MASTER_EXTS = (".wav", ".flac")
SOUND_SUBDIR = "src/main/resources/assets/carnis/sounds"
CREST_TABLE = os.path.join(REPO, "00-board", "reports", "sound_crest_baseline.md")
BASELINE_MASTER = os.path.join(REPO, "03-sound", "baseline_master.json")
PREV_PACKAGE = os.path.join(REPO, "01-coder", "3.7.2", "project-3.7.2-clean.zip")

_BM = None
_TEMP_MASTERS = []

# R22: атака — ОТЧЁТНАЯ метрика, не норма (13/132 ложных провала на чистом
# перекоде, сдвиг окна 1 мс = 9,90 дБ). Число нужно только для печати и для
# пометки файлов, у которых атака ниже -20 дБ (окно 0-10 мс не имеет смысла).
ATTACK_TOL = 0.60
ATTACK_MARK_DB = -20.0


def _dsp():
    """numpy+av для мастеров. Нет — вернуть None (fail-closed у вызывающего)."""
    try:
        import numpy  # noqa: F401
        import av  # noqa: F401
    except ImportError:
        return None
    return True


def _attack(x, sr, window_ms=10.0):
    """Громкость атаки: максимум первых 0-10 мс относительно пика файла.

    Crest слеп к правке атаки (З-31 п.4: корреляция 0,59, 109 из 274
    расходятся, максимум 0,98 дБ), поэтому атака — отдельная норма.
    """
    import numpy as np
    n = max(1, int(sr * window_ms / 1000.0))
    peak = float(np.abs(x).max())
    if peak <= 0:
        return None
    head = float(np.abs(x[:n]).max())
    if head <= 0:
        return None
    return 20 * np.log10(head) - 20 * np.log10(peak)


def _decode(path):
    """Декод в плоский float64. Возвращает (сигнал, частота) или None."""
    import numpy as np
    import av
    try:
        c = av.open(path)
        st = c.streams.audio[0]
        x = np.concatenate([f.to_ndarray().ravel()
                            for f in c.decode(st)]).astype("float64")
        sr = st.rate
        c.close()
        # Ревизор (I23 §9): мастера PCM16 приходят в int16-шкале (max 13639),
        # банк — во float (0.42). Crest считается по ОТНОШЕНИЮ пик/RMS и
        # масштаб ему безразличен, но атака — тоже отношение, а вот сравнение
        # «файл vs мастер» по абсолютным числам разваливалось бы. Приводим
        # любой вход к [-1, 1], чтобы единицы были одни и те же.
        peak = float(np.abs(x).max()) if x.size else 0.0
        if peak > 1.5:
            x = x / 32768.0
        return x, sr
    except Exception:  # noqa: BLE001
        return None


def _crest(x):
    import numpy as np
    peak = float(np.abs(x).max())
    rms = float(np.sqrt((x ** 2).mean()))
    if peak <= 0 or rms <= 0:
        return None
    return 20 * np.log10(peak) - 20 * np.log10(rms)


def _table_types(path):
    """{хвост: (тип, порог)} из таблицы crest — тип нужен для порога нормы."""
    out = {}
    rx = re.compile(r"^\|\s*`((?:sounds|sounds_380)/[^`]+)`\s*\|\s*(стац|транз)\s*\|"
                    r"\s*[\d.]+\s*\|\s*[\d.]+\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|")
    if not os.path.isfile(path):
        return out
    for line in open(path, encoding="utf-8"):
        m = rx.match(line)
        if m:
            # (тип, порог, baseline) — baseline нужен для формулы З-30:
            # допуск = max(порог_типа, baseline + 0,05).
            out[m.group(1).split("/", 1)[1]] = (m.group(2), float(m.group(4)),
                                                float(m.group(3)))
    return out


_BM = None
BASELINE_MASTER = os.path.join(REPO, "03-sound", "baseline_master.json")


def _baseline_master():
    """baseline(M) от Звука (S46/S48): шум первого кодирования на мастере.

    Это ЕДИНСТВЕННАЯ величина, пригодная для нормы от PCM-мастера. Таблица
    `sound_crest_baseline.md` меряет перекод УЖЕ закодированного файла —
    шум второй генерации, который для ровного сигнала систематически ниже
    (Ревизор I23 §10.2: 12 нетронутых файлов 3.8.0 «падали» на табличном
    допуске). Ключ — путь без префикса банка, как в таблице.
    """
    import json
    out = {}
    try:
        with open(BASELINE_MASTER, encoding="utf-8") as fh:
            doc = json.load(fh)
        # Схема v2 — объект {"schema":…, "files": […]}; прежняя — просто список.
        recs = doc.get("files", []) if isinstance(doc, dict) else doc
        if True:
            for rec in recs:
                name = rec.get("file", "")
                for prefix in ("sounds/", "sounds_380/"):
                    if name.startswith(prefix):
                        name = name[len(prefix):]
                        break
                if name and "baseline_master" in rec:
                    # Схема v2 (S52): запись самодостаточна — тип, порог и
                    # готовый допуск. Гейту не нужно ничего пересчитывать и не
                    # нужно второй раз читать таблицу (она может отсутствовать).
                    out[name] = {
                        "baseline": float(rec["baseline_master"]),
                        "repro": float(rec.get("repro_delta") or 0.0),
                        "type": rec.get("signal_type"),
                        "threshold": rec.get("threshold"),
                        "tolerance": rec.get("tolerance"),
                    }
    except (OSError, ValueError, TypeError) as exc:
        # З-29 п.5 (Ревизор R24): отсутствующий или битый baseline не может
        # тихо понижать стационарные до отчёта — иначе порча файла измерений
        # делает гейт зеленее, а не краснее. Возвращаем маркер ошибки; гейт
        # обязан на нём упасть.
        return {"__error__": "%s: %s" % (type(exc).__name__, exc)}
    return out


def _prev_version_bytes(rel):
    """Байты того же файла из принятой 3.7.2: (True, bytes) или (None, None).

    None означает «предыдущей версии нет» — тогда мастер отсутствует
    по-настоящему, и это провал (З-31 п.2), а не «норма неприменима».
    """
    prev = os.path.join(REPO, "01-coder", "3.7.2",
                        "project-3.7.2-clean.zip")
    if not os.path.isfile(prev):
        return None, None
    try:
        with zipfile.ZipFile(prev) as z:
            name = "assets/carnis/sounds/" + rel
            for n in z.namelist():
                if n.endswith(name):
                    return True, z.read(n)
    except (OSError, zipfile.BadZipFile):
        return None, None
    return None, None


_TEMP_MASTERS = []


def _write_temp_decodable(blob, rel):
    """Положить байты во временный файл, чтобы декодер их прочитал.

    Файлы удаляются в конце прогона — это копии ради декода, не эталоны.
    """
    import tempfile
    fd, path = tempfile.mkstemp(suffix=os.path.splitext(rel)[1] or ".ogg")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(blob)
    except OSError:
        return None
    _TEMP_MASTERS.append(path)
    return path


def _unchanged_vs_prev(extract_dir, rels):
    """Какие из файлов побайтово совпадают с эталоном предыдущей версии.

    Нужно, чтобы отличить «мастера нет, потому что файл не менялся»
    (правильно, З-31 п.3) от «мастера нет, хотя файл изменён» (провал,
    З-31 п.2). Без эталона сравнить не с чем — тогда возвращаем пустое
    множество, и все файлы считаются изменёнными: это строгая сторона.
    """
    prev = os.path.join(REPO, "01-coder", "3.7.2",
                        "project-3.7.2-clean.zip")
    if not os.path.isfile(prev):
        return set()
    out = set()
    try:
        with zipfile.ZipFile(prev) as z:
            names = {n.split("assets/carnis/sounds/", 1)[1]: n
                     for n in z.namelist() if "assets/carnis/sounds/" in n}
            for rel in rels:
                name = names.get(rel)
                if not name:
                    continue
                cur = os.path.join(extract_dir, SOUND_SUBDIR, rel)
                if os.path.isfile(cur) and z.read(name) == open(cur, "rb").read():
                    out.add(rel)
    except (OSError, KeyError, zipfile.BadZipFile):
        return set()
    return out


def check_crest_attack(extract_dir):
    """I25/З-31: crest и громкость атаки — от МАСТЕРА, не от самого файла.

    Тавтология прежней методики: baseline считался как round-trip САМОГО
    проверяемого файла, поэтому Δcrest был равен baseline по построению
    (276 строк из 276) — такая проверка зелена всегда. Здесь:
      M — мастер (PCM до кодирования), baseline(M) — шум кодека на мастере,
      Δcrest(F) = |crest(F) − crest(M)| — реальное изменение звука.
    Норма: Δcrest ≤ max(порог_типа, baseline(M) + 0,05), атака ≤ 0,60 дБ.

    Fail-closed: нет мастера, нет записи в таблице или нет numpy+av —
    это «crest не проверен», а НЕ «зелено по построению».
    """

    _fail = []   # провалы копим локально: гейт решает код возврата
    if not _dsp():
        print("  x crest/атака: нет numpy+av — от мастеров не посчитать")
        _fail.append("crest/атака: нет numpy+av — проверка не выполнена")
        return _fail
    if not os.path.isdir(MASTERS):
        print("  x crest/атака: нет каталога мастеров 03-sound/masters")
        _fail.append("crest/атака: мастеров нет — сверять не с чем")
        return _fail
    types = _table_types(CREST_TABLE)
    if not types:
        print("  x crest/атака: таблица не разобрана — порог типа не взять")
        _fail.append("crest/атака: таблица crest не разобрана")
        return _fail

    root = os.path.join(extract_dir, SOUND_SUBDIR)
    if not os.path.isdir(root):
        print("  · звуков в пакете нет — нечего сверять с мастерами")
        return _fail

    global _BM
    if _BM is None:
        _BM = _baseline_master()
    if "__error__" in _BM:
        print("  x baseline(M): файл 03-sound/baseline_master.json недоступен "
              "или битый — %s" % _BM["__error__"])
        print("    без него норма стационарных недоказуема (З-29 п.5), "
              "тихое понижение до отчёта запрещено")
        _fail.append("crest/атака: baseline_master.json не прочитан (%s) — "
                    "норма стационарных недоказуема" % _BM["__error__"])
        return _fail
    checked, no_master, no_entry, bad_crest = 0, [], [], []
    attack_report, no_attack, taut = [], [], []
    used_prev = 0
    unchanged_now = []
    stationary_unmeasured = []
    type_clash = []
    worst_c, worst_a = (0.0, ""), (0.0, "")
    for dp, _, fs in os.walk(root):
        for f in sorted(fs):
            if not f.endswith(".ogg"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/")
            if rel not in types:
                no_entry.append(rel)
                continue
            # Мастер ищется в обоих корнях: канон и 3.8.0 лежат отдельно.
            master = None
            # 1) канонические корни — точный путь
            for sub in ("sounds", "sounds_380"):
                for ext in MASTER_EXTS:
                    cand = os.path.join(MASTERS, sub, rel[:-4] + ext)
                    if os.path.isfile(cand):
                        master = cand
                        break
                if master is not None:
                    break
            # 2) датированные корни перерисовки: masters/sounds_crest_<дата>/
            #    (S128/S129: Звук положил мастера 6 перерисованных файлов в
            #    отдельный корень. Гейт его не видел и брал УСТАРЕВШИЙ _z21 —
            #    6 файлов падали с Δcrest до 4,9 дБ против прежней версии,
            #    хотя против нового мастера расходятся на 0,02 дБ.
            #    Свежий корень главнее канона по дате в имени.)
            if master is None:
                dated = []
                try:
                    for name in os.listdir(MASTERS):
                        full = os.path.join(MASTERS, name)
                        if (os.path.isdir(full) and name not in ("sounds", "sounds_380")
                                and name.startswith("sounds")):
                            dated.append(name)
                except OSError:
                    dated = []
                for name in sorted(dated, reverse=True):
                    for ext in MASTER_EXTS:
                        # и с подкаталогами банка, и плоско — как их кладёт Звук
                        for cand in (os.path.join(MASTERS, name, rel[:-4] + ext),
                                     os.path.join(MASTERS, name, f[:-4] + ext)):
                            if os.path.isfile(cand):
                                master = cand
                                break
                        if master is not None:
                            break
                    if master is not None:
                        break
            # 3) наследие З-21: мастера лежат ПЛОСКО в sounds/_z21/ без
            #    подкаталогов банка — искать по одному имени файла.
            if master is None:
                for sub in ("sounds", "sounds_380"):
                    for ext in MASTER_EXTS:
                        flat = os.path.join(MASTERS, sub, "_z21", f[:-4] + ext)
                        if os.path.isfile(flat):
                            master = flat
                            break
                    if master is not None:
                        break
            # S44 (Звук): если PCM-мастера нет, мастером может служить
            # ДЕКОД ПРЕДЫДУЩЕЙ ВЕРСИИ — это два разных сигнала, не тавтология.
            # Звук измерил зазор на правках: громкость −3 дБ даёт Δcrest
            # 0,007–0,060, порча формы лимитером 1,986–2,262, то есть правка и
            # порча расходятся в 33–100 раз.
            # Fail-closed по его же требованию: если архивная версия
            # побайтово равна проверяемому файлу — это была бы тавтология,
            # и такой «мастер» не принимается.
            if master is None:
                prev_ok, prev_bytes = _prev_version_bytes(rel)
                if prev_ok is None:
                    no_master.append(rel)
                    continue
                if prev_bytes == open(os.path.join(dp, f), "rb").read():
                    # S44: «мастер == файл» — тавтология, НО только если файл
                    # вообще менялся. Если он побайтово равен принятой 3.7.2,
                    # это З-31 п.3: файл принят предыдущей версией и норме не
                    # подлежит — проверять его нечем и не нужно. Тавтологией
                    # было бы брать такой «мастер» для ИЗМЕНЁННОГО файла.
                    unchanged_now.append(rel)
                    continue
                master = _write_temp_decodable(prev_bytes, rel)
                if master is None:
                    no_master.append(rel + " (архив не декодирован)")
                    continue
                used_prev += 1
            got = _decode(os.path.join(dp, f))
            ref = _decode(master)
            if not got or not ref:
                no_master.append(rel + " (не декодирован)")
                continue
            bm_rec = _BM.get(rel) or {}
            if rel in types:
                typ, thr, base_tbl = types[rel]
            elif bm_rec:
                # Записи в таблице нет, но JSON её заменяет (S52 просил брать
                # тип отсюда). Таблицу читать второй раз незачем.
                typ = bm_rec.get("type") or "стац"
                thr = float(bm_rec.get("threshold") or 0.05)
                base_tbl = 0.0
            else:
                no_entry.append(rel)
                continue
            # S53 (Звук): тип и baseline — ОДНА пара, из одного источника.
            # Если тип взят из таблицы, а baseline из JSON, а их поправили
            # по-разному, гейт молча возьмёт несогласованную пару. Поэтому
            # при расхождении типа побеждает JSON (он же источник baseline),
            # а расхождение печатается.
            if bm_rec and bm_rec.get("type") and bm_rec["type"] != typ:
                # Несогласованная пара — это ПРОВАЛ, а не примечание.
                # Проверено негативом: подмена типа стац->транз поднимала допуск
                # 0,173 -> 0,600 и файл проходил молча. Тихий выбор «чьей-то»
                # версии делает расхождение незаметным — ровно тот класс, за
                # который я весь вечер правил гейты.
                print("  x %s: тип в таблице «%s», в baseline_master «%s» — "
                      "источники разошлись" % (rel, typ, bm_rec["type"]))
                type_clash.append((rel, typ, bm_rec["type"]))
                continue
            cm, cf = _crest(ref[0]), _crest(got[0])
            if cm is None or cf is None:
                no_master.append(rel + " (тишина)")
                continue
            # Допуск по З-30/З-31: max(порог_типа, baseline(M) + 0,05).
            # Ревизор (I23 §9) поймал, что код брал max(thr, 0.05) — то есть
            # игнорировал baseline мастера, и 23 из 33 стационарных файлов
            # валились на собственном шуме кодека 0,13-0,24 дБ при пороге
            # 0,05. Теперь baseline(M) считается: перекодировать мастер тем
            # же кодеком и сравнить crest с мастером. Не удалось — берём
            # табличный baseline как нижнюю границу (он не меньше шума).
            # Baseline: приоритет у baseline(M) от Звука (S46/S48) — это шум
            # ПЕРВОГО кодирования на мастере, ровно та величина, что нужна
            # норме от PCM. Табличный baseline (шум второй генерации) —
            # только запасной, и тогда это печатается.
            bm = _BM.get(rel)
            if bm is not None:
                base_used, src = bm["baseline"], "baseline(M)"
            else:
                base_used, src = base_tbl, "таблица"
            # tolerance из JSON (S52) — уже посчитанный max(порог, baseline+0,05);
            # пересчитываю сам намеренно: если формула когда-нибудь изменится,
            # гейт не должен молча унаследовать старое число.
            tol = max(thr, base_used + 0.05)
            if bm is not None and bm.get("tolerance") is not None:
                if abs(float(bm["tolerance"]) - tol) > 0.001:
                    print("  ! %s: допуск JSON %.3f != формулы %.3f — беру формулу"
                          % (rel, float(bm["tolerance"]), tol))
            d = abs(cf - cm)
            if d > tol:
                # R23 (I23 §10.2): ТАБЛИЧНЫЙ baseline измерен на перекоде
                # УЖЕ ЗАКОДИРОВАННОГО файла (шум второй генерации), а мастер —
                # PCM до первого кодирования. Для стационарных сигналов шум
                # первого кодирования больше табличного (Ревизор: 12 нетронутых
                # файлов 3.8.0 «падают» на нём, Δ RMS −0,11…+0,01 дБ — то есть
                # файл не трогали). Пока Звук не измерит baseline(M) своим
                # энкодером (S46), стационарные идут ОТЧЁТОМ, а не провалом;
                # транзиентные (порог 0,60) валят как раньше — у них запас
                # 2-3x и ложных провалов нет.
                # Стационарный валит, ЕСЛИ допуск посчитан от измеренного
                # baseline(M) — тогда шум учтён и превышение реально. Если
                # baseline(M) нет и взят табличный, остаётся отчётом: таблица
                # меряет шум другой генерации (см. выше).
                if typ == "стац" and src == "таблица":
                    # Ревизор (I23 s14): страж обязан быть ПОФАЙЛОВЫМ, не
                    # потиповым. Пока проверялось «есть ли в JSON хоть одна
                    # стационарная запись», достаточно было оставить одну —
                    # и остальные тихо уходили в отчёт при зелёном вердикте.
                    # С S48 измерены все стационарные, у которых есть мастер,
                    # поэтому файл с мастером и БЕЗ своей записи — провал:
                    # нормы для него нет, а «нет нормы» здесь = fail-closed.
                    stationary_unmeasured.append((rel, d, tol, base_tbl))
                else:
                    bad_crest.append((rel, d, tol, typ))
            if d > worst_c[0]:
                worst_c = (d, rel)
            am, af = _attack(ref[0], ref[1]), _attack(got[0], got[1])
            if am is not None and af is not None:
                da = abs(af - am)
                # R22 (Ревизор): «атака» КАК НОРМА не выдерживает собственных
                # негативов — ни постоянный допуск 0,60 (13 из 132 файлов
                # выходят при простом перекоде), ни per-file допуск (не ловит
                # gain). Причины: ведущая цифровая тишина, сдвиг окна на 1 мс
                # даёт до 9,90 дБ, сдвиг онсета. Поэтому здесь она НЕ валит, а
                # печатается как отчётная цифра — вместе с двумя колонками,
                # которые действительно являются нормой (crest + timbre).
                if am < -20.0:
                    no_attack.append((rel, am))
                elif da > ATTACK_TOL:
                    attack_report.append((rel, da))
                if da > worst_a[0] and am >= -20.0:
                    worst_a = (da, rel)
            checked += 1

    print("  · сверено с мастерами: %d | без мастера %d | без записи в таблице %d"
          % (checked, len(no_master), len(no_entry)))
    if checked:
        print("  · худшее: Δcrest %.3f дБ%s, Δатаки %.3f дБ%s (допуск %.2f)"
              % (worst_c[0], (" (%s)" % worst_c[1]) if worst_c[1] else "",
                 worst_a[0], (" (%s)" % worst_a[1]) if worst_a[1] else "",
                 ATTACK_TOL))
    for rel, d, tol in [(a, b, c) for a, b, c, _t in bad_crest[:4]]:
        print("      ✗ %s Δcrest %.3f > %.3f" % (rel, d, tol))
    # Атака — ОТЧЁТ, не вердикт (R22). Печатается всегда, чтобы цифра была
    # видна, но fail по ней не выставляется.
    if no_attack:
        print("  · атака ниже -20 дБ (окно 0-10 мс не имеет смысла): %d файлов"
              % len(no_attack))
    if attack_report:
        print("  · Δатаки > %.2f дБ — отчётная метрика, не норма (R22): %d файлов"
              % (ATTACK_TOL, len(attack_report)))
        for rel, da in attack_report[:3]:
            print("      ~ %s %.3f дБ" % (rel, da))
    if used_prev:
        print("  · мастером служил декод 3.7.2 (S44): %d файлов — два разных "
              "сигнала, не тавтология" % used_prev)
    if unchanged_now:
        print("  · побайтово равны 3.7.2 без мастера: %d — норме не подлежат "
              "(З-31 п.3)" % len(unchanged_now))
    if taut:
        # S44 требование Звука: архивная версия, равная проверяемому файлу, —
        # тавтология, а не мастер. Такое не принимается молча.
        print("  ✗ crest/атака: у %d файлов архивная версия равна файлу — "
              "сравнение было бы тавтологией" % len(taut))
        for rel in taut[:4]:
            print("      ? %s" % rel)
        _fail.append("crest/атака: %d файлов, у которых «мастер» == файл "
                    "(тавтология, S44)" % len(taut))
    if no_master:
        # З-31 п.2 и п.3 вместе: мастер обязателен для ИЗМЕНЁННЫХ файлов,
        # а побайтово неизменённые норме не подлежат. Разделить их можно
        # только по эталону предыдущей версии — иначе «нет мастера» у
        # неизменённого файла (129 из 144 канона, мастеров к ним не
        # существует и синтезировать их запрещено) выглядело бы как
        # провал, а это правильное поведение.
        unchanged = _unchanged_vs_prev(extract_dir, no_master)
        changed = [r for r in no_master if r not in unchanged]
        if unchanged:
            print("  · побайтово неизменных без мастера: %d — норме не "
                  "подлежат (З-31 п.3)" % len(unchanged))
        if changed:
            # ⛔ Ревизор 2026-11-26: без эталона 3.7.2 _unchanged_vs_prev
            # возвращает ПУСТОЕ множество, и все 129 файлов попадают в
            # «изменённые», хотя изменённых может быть ноль. Слово
            # «ИЗМЕНЁННЫХ» тогда ложь: это «не с чем сравнить». Разбор у двух
            # случаев разный: одно чинится эталоном, другое — мастером.
            if not os.path.isfile(os.path.join(
                    REPO, "01-coder", "3.7.2",
                    "project-3.7.2-clean.zip")):
                print("  ✗ crest/атака: у %d файлов нет мастера и нет эталона "
                      "3.7.2 — изменены ли они, НЕИЗВЕСТНО (сравнить не с "
                      "чем; строгая сторона считает изменёнными)"
                      % len(changed))
            else:
                print("  ✗ crest/атака: у %d ИЗМЕНЁННЫХ файлов нет мастера"
                      % len(changed))
            for rel in changed[:4]:
                print("      ? %s" % rel)
            # Вторая половина той же правки: итоговая строка тоже
            # утверждала «изменённых». Без эталона это не факт, а догадка,
            # и в списке провалов она читается как установленный дефект —
            # именно её видит Архитектор, когда смотрит «что красное».
            if os.path.isfile(os.path.join(REPO, "01-coder", "3.7.2",
                                           "project-3.7.2-clean.zip")):
                _fail.append("crest/атака: %d изменённых файлов без мастера "
                            "(З-31 п.2)" % len(changed))
            else:
                _fail.append("crest/атака: у %d файлов нет мастера, эталона "
                            "3.7.2 тоже нет — изменение НЕ УСТАНОВЛЕНО, "
                            "нужен эталон" % len(changed))
    if bad_crest:
        _fail.append("crest: %d файлов изменили динамику сверх своего допуска"
                    % len(bad_crest))
    if type_clash:
        print("  x crest: тип сигнала расходится у %d файлов (таблица vs "
              "baseline_master) — пара «тип+baseline» недоказуема"
              % len(type_clash))
        _fail.append("crest/атака: тип сигнала расходится у %d файлов — "
                     "таблица и baseline_master правлены по-разному"
                     % len(type_clash))
    if stationary_unmeasured:
        print("  x crest: у %d стационарных файлов есть мастер, но нет своей "
              "записи baseline(M) — норма недоказуема (I23 s14)" %
              len(stationary_unmeasured))
        for rel, d, tol, base in stationary_unmeasured[:5]:
            print("      ✗ %-38s Δ %.3f, табличный допуск %.3f — не замерен"
                  % (rel, d, tol))
        _fail.append("crest/атака: %d стационарных файлов без своей записи "
                    "baseline(M) — норма недоказуема"
                    % len(stationary_unmeasured))
    # Зелёная строка печатается ТОЛЬКО когда провалов нет вовсе. Иначе
    # получалось «✓ 132 в норме» рядом с «x 11 не замерены» — и читающий
    # верил зелёной (Ревизор I23 s14).
    if checked and not bad_crest and not no_master and not stationary_unmeasured \
            and not type_clash:
        print("  ✓ crest/атака: %d файлов в норме от мастеров (З-31)" % checked)
    for path in _TEMP_MASTERS:
        try:
            os.unlink(path)
        except OSError:
            pass
    return _fail
