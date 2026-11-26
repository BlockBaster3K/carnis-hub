#!/usr/bin/env python3
"""Итоговая громкость события = call-site (Java) x sounds.json.

Зачем: S62 [sound] сравнил ТЗ с ОДНИМ множителем (sounds.json) и выдал вывод
«7 из 9 событий не по ТЗ». Фактически множителей два, они перемножаются, и
верное число было «1 из 9». Этот тест считает итог и не даёт повторить ошибку.

    effective = call_site_volume (из Java) * volume каждого сэмпла (sounds.json)

Цель задаётся ДВУМЯ способами (схема carnis.volume_spec/2):
  * "target": одно число на событие — когда сэмплы события равноценны;
  * "targets_by_sample": цель по имени сэмпла — когда сэмплы разной громкости
    ПО ПРИРОДЕ и одна цель на событие неверна.

Второй случай не гипотетический: `hive.detail_flow_01` тише пары на 8 дБ
(пик −15.1 / RMS −29.6 против −7.3 / −21.9), поэтому S17 назначил ему 0.45,
а `flow_02` — 0.30. Схема «одна цель на событие» вынудила бы выровнять
множители и создать слышимый провал «то есть звук, то нет».

Коды возврата:
  0 — все события спеки в пределах tolerance
  2 — есть расхождение (печатает событие, сэмпл, ожидание, факт)
  3 — спек/пакет/поле не читаются (fail-closed: не «нет данных», а ошибка)

Пути к Java берутся из спеки (поле call_site.file) — тест НЕ угадывает, в каком
файле живёт вызов, и НЕ ищет вызовы по всему дереву: неоднозначность дала бы
ложное «всё хорошо» при верном числе файлов.

Использование:
  python3 tools/volume_effective_check.py --pkg 01-coder/3.7.3 \
      --spec 03-sound/spec/volume_spec_t3202.json
"""
import argparse
import json
import os
import re
import sys
import zipfile

# volume — последний float-литерал в аргументах playSound/playLocalSound
CALL_RE = re.compile(r"(?:playLocalSound|playSound)\s*\((.*?)\)\s*;", re.S)


SJ_REL = "src/main/resources/assets/carnis/sounds.json"


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_zip(pkg):
    """Пакет может быть ZIP — гейт передаёт путь к архиву, а не каталог.

    Пока чекер умел только каталог, интеграция с гейтом давала код 3 на
    ЛЮБОМ пакете: блок 9в передавал `os.path.dirname(zip_path)`, и проверка
    громкости не выполнялась ни разу. Поддержка ZIP убирает эту зависимость
    от того, распакован пакет или нет.
    """
    return os.path.isfile(pkg) and zipfile.is_zipfile(pkg)


def _read_from_zip(zf, rel):
    try:
        return zf.read(rel).decode("utf-8")
    except KeyError:
        raise FileNotFoundError("%s (внутри %s)" % (rel, os.path.basename(zf.filename)))


def volumes_of_event(sj, event):
    """[(имя сэмпла или None, volume)] по звукам события из sounds.json."""
    reg = sj.get("sounds", sj)
    node = reg.get(event)
    if node is None:
        raise KeyError(event)
    out = []
    for s in node.get("sounds", []):
        if isinstance(s, dict):
            name = s.get("name")
            name = name.split(":")[-1].split("/")[-1] if name else None
            out.append((name, float(s.get("volume", 1.0))))
        else:
            out.append((None, 1.0))
    return out or [(None, 1.0)]


def volume_from_args(args):
    """Громкость из аргументов вызова — ПО ПОЗИЦИИ, а не «предпоследний float».

    Раньше брался предпоследний float-литерал, и это молча ломалось, если вызов
    между событием и громкостью несёт ещё одно число: например
    `playSound(null, pos, ev, SoundSource.BLOCKS, 1.0F, 0.8F, 1.0F)` (volume,
    pitch, ещё что-то) дало бы 1.0 вместо 0.8. Код при этом выглядел рабочим.

    Известные сигнатуры (Minecraft 1.20.x):
      playSound(Player, BlockPos, SoundEvent, SoundSource, float volume, float pitch)
      playLocalSound(double x, double y, double z, SoundEvent, SoundSource,
                     float volume, float pitch, boolean distanceDelay)
    В обеих volume — ПЕРВЫЙ float после SoundSource. Если SoundSource в вызове
    нет, позицию определить нельзя — возвращаем None (пусть вызывающий код
    скажет «не нашёл», а не подставит первое попавшееся число).
    """
    m = re.search(r"SoundSource\s*\.\s*\w+", args)
    if m is None:
        return None
    rest = args[m.end():]
    f = re.search(r"(\d+(?:\.\d+)?)F", rest)
    return float(f.group(1)) if f else None


def call_site_volume(pkg_path, event, spec_entry, zf=None):
    """vol из Java: ищем playSound/playLocalSound(...), где встречается событие.

    Если код множителя НЕ задаёт (поле call_site.kind == "no_code_multiplier" или
    call_site.volume is None), множитель равен 1.0 по определению: тогда
    эффективная громкость — это volume из sounds.json. Иначе события вроде
    hive.spawn_idle (getAmbientSound, без аргумента громкости) получали
    «вызов не найден» и код 3, хотя проверять их надо как раз по JSON.
    """
    cs = spec_entry.get("call_site", {})
    if cs.get("kind") == "no_code_multiplier" or (
            "volume" in cs and cs.get("volume") is None):
        return 1.0
    rel = cs.get("file")
    if not rel:
        raise KeyError("call_site.file")
    if zf is not None:
        src = _read_from_zip(zf, rel)
    else:
        path = os.path.join(pkg_path, rel)
        if not os.path.isfile(path):
            raise FileNotFoundError(rel)
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
    ev = event.replace(".", "_").upper()          # hive.spread -> HIVE_SPREAD
    marker = spec_entry.get("call_site", {}).get("arg_marker")
    if marker:
        # Общий call-site через переменную: событие должно ВЫБИРАТЬСЯ в этом же
        # файле, иначе маркер — допущение, а не факт кода.
        if ev not in src.upper():
            raise LookupError("%s: событие %s не выбирается в этом файле, "
                              "arg_marker '%s' не подтверждается" % (rel, ev, marker))
        needle = marker
    else:
        needle = ev
    unparsed = []
    for m in CALL_RE.finditer(src):
        args = m.group(1)
        if needle not in args:
            continue
        vol = volume_from_args(args)
        if vol is not None:
            return vol
        # Вызов НАЙДЕН, но громкость не разобрана — это отказ, а не «пропустить».
        # Иначе незнакомая форма вызова (playLocalSound без SoundSource,
        # playSound с this.getSoundSource()) молча давала бы «вызов не найден»,
        # а в блоке 9д — «заявление подтверждено» (Ревизор, §1).
        unparsed.append(args.strip().replace("\n", " ")[:80])
    if unparsed:
        raise LookupError("%s: вызов %s найден, но громкость не разобрана — "
                          "форма вызова не поддержана: %s"
                          % (rel, ev, unparsed[0]))
    raise LookupError("%s: вызов %s не найден" % (rel, ev))



def java_sources(pkg_path, zf=None):
    """{относительный путь: текст} по всем .java пакета."""
    out = {}
    if zf is not None:
        for rel in zf.namelist():
            if rel.endswith(".java"):
                out[rel] = _read_from_zip(zf, rel)
        return out
    for dp, _, fs in os.walk(pkg_path):
        for f in fs:
            if f.endswith(".java"):
                full = os.path.join(dp, f)
                out[os.path.relpath(full, pkg_path)] = open(
                    full, encoding="utf-8", errors="replace").read()
    return out


def prove_no_code_multiplier(pkg_path, event, zf=None):
    """Проверить заявление «в коде множителя громкости нет» ПО КОДУ, а не на слово.

    Заявление `call_site.kind = "no_code_multiplier"` раньше принималось на веру:
    в спеке писали «множителя нет», чекер ставил 1.0 и не смотрел Java. Ревизор
    (reviewer_volume_key_verified.md §3) показал, что цель и заявление лежат в
    ОДНОМ файле — кто может написать «множителя нет», тот может поправить и цель.

    Здесь заявление проверяется:
      1. найти регистрацию события: ModSounds.* -> имя "carnis:<event с _>"
         (или любую строку с именем события);
      2. взять константу ModSounds.X;
      3. найти ВСЕ её использования вне ModSounds;
      4. провал, если хоть одна передана в playSound/playLocalSound с громкостью.

    Возвращает (ok: bool, точки: [(файл, строка, текст)], причина: str).
    """
    src = java_sources(pkg_path, zf)
    if not src:
        return False, [], "в пакете нет .java — заявление не проверить"

    # Имя события в Java пишется по-разному: registerVariableRangeSound("hive.spawn_idle")
    # (с точками, как в sounds.json) либо "carnis:hive_spawn_idle". Пробуем все формы.
    forms = [event, "carnis:" + event, event.replace(".", "_"),
             "carnis:" + event.replace(".", "_")]
    const = None
    for rel, text in src.items():
        if not rel.endswith("ModSounds.java"):
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if not any('"%s"' % f in line for f in forms):
                continue
            # константа объявлена на этой же строке или на предыдущей:
            #     public static final RegistryObject<SoundEvent> HIVE_SPAWN_IDLE =
            #             registerVariableRangeSound("hive.spawn_idle");
            for j in (i, i - 1):
                if j < 0:
                    continue
                m = re.search(r"\b([A-Z][A-Z0-9_]{2,})\s*=", lines[j])
                if m:
                    const = m.group(1)
                    break
            if const:
                break
        if const:
            break
    if not const:
        return False, [], "константа ModSounds для %s не найдена" % event

    uses = []
    for rel, text in src.items():
        if rel.endswith("ModSounds.java"):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"ModSounds\." + re.escape(const) + r"\b", line):
                uses.append((rel, i, line.strip()))

    # БЕЛЫЙ СПИСОК, а не чёрный (Ревизор, reviewer_prove_no_code_multiplier_bypass).
    # Раньше провал ставился только если volume_from_args() РАЗОБРАЛ громкость.
    # Значит любую незнакомую форму вызова можно было «доказать»: playLocalSound
    # без SoundSource или playSound с this.getSoundSource() давали None ->
    # «передана без громкости» -> заявление проходило.
    # Теперь доказуема ТОЛЬКО форма возврата события: "return X.CONST.get();".
    # Всё остальное (любой вызов, присваивание, аргумент) -> заявление не доказано.
    good_re = re.compile(r"^return\s+[\w.]*\." + re.escape(const) + r"\.get\(\)\s*;\s*$")
    bad = [(r, i, l) for r, i, l in uses if not good_re.match(l)]
    if bad:
        return False, bad, ("константа %s используется не только как возврат события "
                            "(вызов/присваивание) — множитель может задаваться в коде"
                            % const)
    return True, uses, "константа %s: %d использований, ни одного с громкостью" % (const, len(uses))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", required=True, help="каталог версии пакета, напр. 01-coder/3.7.3")
    ap.add_argument("--spec", required=True, help="JSON спеки громкостей")
    a = ap.parse_args(argv)

    zf = None
    try:
        spec = read_json(a.spec)
        if is_zip(a.pkg):
            zf = zipfile.ZipFile(a.pkg)
            sj = json.loads(_read_from_zip(zf, SJ_REL))
        else:
            sj = read_json(os.path.join(a.pkg, SJ_REL))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print("ОШИБКА: %s" % exc)
        return 3
    try:
        return _run(a, spec, sj, zf)
    finally:
        if zf is not None:
            zf.close()


def _run(a, spec, sj, zf=None):

    tol = float(spec.get("tolerance", 0.005))
    bad = 0
    total = 0
    print("пакет: %s" % a.pkg)
    print("%-22s %10s %8s %10s  %s" % ("событие", "ТЗ", "call-site", "факт", "вердикт"))
    for ent in spec.get("events", []):
        ev = ent["event"]
        by_sample = ent.get("targets_by_sample")
        target = ent.get("target")
        if by_sample is None and target is None:
            print("%-22s %6s %8s %10s  ОШИБКА: нет цели (target или targets_by_sample)" % (ev, "?", "?", "?"))
            return 3
        try:
            cs = call_site_volume(a.pkg, ev, ent, zf)
            if ent.get("call_site", {}).get("kind") == "no_code_multiplier":
                proved, pts, why = prove_no_code_multiplier(a.pkg, ev, zf)
                where = ", ".join("%s:%d" % (r, i) for r, i, _ in pts[:4])
                print("  [проверка заявления] %-20s %s — %s%s"
                      % (ev, "ПОДТВЕРЖДЕНО" if proved else "НЕВЕРНО", why,
                         (" [" + where + "]") if where else ""))
                if not proved:
                    print("  [проверка заявления] %s: заявление no_code_multiplier "
                          "не доказано — считать множитель 1.0 нельзя" % ev)
                    return 3
            vols = volumes_of_event(sj, ev)
        except (OSError, KeyError, LookupError) as exc:
            print("%-22s %6s %8s %10s  ОШИБКА: %s" % (ev, target or "по сэмплам", "?", "?", exc))
            return 3
        # Для каждого сэмпла — своя цель: из targets_by_sample либо общая target.
        per = []
        for name, v in vols:
            if by_sample is not None:
                if name not in by_sample:
                    print("%-22s  ОШИБКА: цель для сэмпла '%s' не задана в targets_by_sample" % (ev, name))
                    return 3
                t = float(by_sample[name])
            else:
                t = float(target)
            per.append((name, v, cs * v, t))
        total += 1
        worst = max(per, key=lambda r: abs(r[2] - r[3]))
        ok = abs(worst[2] - worst[3]) <= tol
        if not ok:
            bad += 1
        label = ("%.2f" % float(target)) if target is not None else "по сэмплам"
        print("%-22s %10s %8.2f %10.3f  %s" % (
            ev, label, cs, worst[2],
            "ok" if ok else "РАСХОЖДЕНИЕ (x%.2f)" % (worst[2] / worst[3])))
        if not ok or by_sample is not None:
            for name, v, eff, t in per:
                mark = "" if abs(eff - t) <= tol else "  <-- вне допуска"
                print("      %s: sounds.json volume %.2f -> %.3f (цель %.2f)%s"
                      % (name or "?", v, eff, t, mark))

    if bad:
        print("ИТОГ: %d из %d вне допуска (tolerance %.3f)" % (bad, total, tol))
        print("Починка — править ОДИН множитель, не оба: снижение в sounds.json\n"
              "поверх уже понижённого call-site даёт двойное умножение (S62/S68).")
        return 2
    print("ИТОГ: %d из %d в норме" % (total, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
