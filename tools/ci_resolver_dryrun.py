#!/usr/bin/env python3
"""Резолвер CI: сухой прогон выбора пакета — БЕЗ сборки и БЕЗ сети.

Зачем (I6 плана Интегратора)
----------------------------
`build.yml` выбирает старший каталог `01-coder/<версия>/`, у которого есть
ZIP **и** положительный вердикт Ревизора. Логика живёт только в YAML, поэтому
локально её не прогнать: ошибка обнаруживается только когда CI уже собрал
(или не собрал) релиз.

Что найдено этим прогоном на текущем дереве (2026-11-26)
--------------------------------------------------------
`build.yml` считает вердикт отрицательным, если слово-триггер встречается
**где угодно** в файле:

    NEG=$(grep -oiE 'НЕ ПРИНЯТ|ОТКЛОНЁН|ОТКЛОНЕНО|REJECTED' "$VERD2" || true)

Но вердикты Ревизора содержат **историю сдач** в шапке. У 3.7.3 строка 7:

    Цепочка сдач: `d19169b4…` — не принята (правка `pitch` вне S17) →

Это описывает ПРОШЛУЮ сдачу того же пакета, а решение — на строке 11:
`# ПРИНЯТО`. То же у 3.7.2 («Отклонение | Что не так в 3.7.2» — таблица
дефектов, которые исправили).

Следствие: CI пропускает 3.7.3 и 3.7.2 как «отрицательные» и выпускает
релиз из **3.7.1** — то есть из старого пакета. Это ровно тот класс, против
которого написан З-CИ-1.

Коды
----
0 — CI выберет старший принятый пакет, вердикт привязан к его sha256
2 — CI выберет НЕ старший (пропуск из-за слова в истории) либо вердикт не
    подтверждает sha — дефект, релиз уйдёт из старого пакета
1 — CI не выберет ничего
"""
import glob
import hashlib
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODER = os.path.join(REPO, "01-coder")
REPORTS = os.path.join(REPO, "00-board", "reports")

# Решение вердикта читает тот же модуль, что и сам CI (З-CИ-4): иначе прогон
# проверял бы одну логику, а конвейер работал по другой.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict_decision as _decision  # noqa: E402

# Ровно те слова, что в build.yml (регистронезависимо).
NEG = re.compile(r"НЕ ПРИНЯТ|ОТКЛОНЁН|ОТКЛОНЕНО|REJECTED", re.IGNORECASE)


def _lines_with(text, rx):
    """[(номер строки, строка)] для строк, где нашлось rx."""
    return [(i + 1, ln) for i, ln in enumerate(text.splitlines()) if rx.search(ln)]


def verdict_decision(text):
    """Строка-РЕШЕНИЕ вердикта или None.

    Решение — это строка, которая НАЧИНАЕТСЯ с маркера (после снятия `#`, `*`):
    «# ПРИНЯТО», «**НЕ ПРИНЯТО** — …», «## ВЕРДИКТ: ПРИНЯТО». Упоминание
    слова в середине предложения решением не считается — иначе история сдач
    («`d19169b4…` — не принята») читается как отказ по текущему пакету.
    """
    for ln in text.splitlines():
        st = ln.strip().lstrip("#").strip().lstrip("*").strip()
        if not st:
            continue
        m = re.match(r"(НЕ\s+ПРИНЯТ|ПРИНЯТ|ОТКЛОНЕНО|ОТКЛОНЁН|REJECTED)", st, re.I)
        if m:
            return ln.strip()
        # «## ВЕРДИКТ: ПРИНЯТО»
        m2 = re.match(r"(ВЕРДИКТ|ИТОГ|РЕШЕНИЕ)\s*:?\s*\**\s*(НЕ\s+ПРИНЯТ|ПРИНЯТ|ОТКЛОНЕНО|ОТКЛОНЁН|REJECTED)",
                      st, re.I)
        if m2:
            return ln.strip()
    return None


def verdict_negative_by_ci(text):
    """Как build.yml: есть ли слово-триггер ГДЕ УГОДНО. Возвращает (строка, текст)."""
    hits = _lines_with(text, NEG)
    return hits[0] if hits else (None, None)


def _vdirs():
    out = [n for n in os.listdir(CODER)
           if os.path.isdir(os.path.join(CODER, n))
           and re.fullmatch(r"\d+\.\d+(\.\d+)?(-R\d*)?", n)]
    return sorted(out, key=lambda s: [int(x) for x in re.findall(r"\d+", s)[:3]],
                  reverse=True)


def resolve():
    log = []
    for cand in _vdirs():
        zips = sorted(glob.glob(os.path.join(CODER, cand, "project-*-clean.zip")))
        if not zips:
            log.append(("skip-nozip", cand, "ZIP нет"))
            continue
        vbase = cand.split("-R")[0]
        verd = None
        for f in (os.path.join(REPORTS, "reviewer_%s_verdict.md" % vbase),
                  os.path.join(REPORTS, "reviewer_%s_verdict.md" % vbase.replace(".", ""))):
            if os.path.isfile(f):
                verd = f
                break
        if not verd:
            log.append(("skip-noverdict", cand, "вердикта нет"))
            continue
        text = open(verd, encoding="utf-8", errors="replace").read()
        if not re.search(r"\S", text):
            log.append(("fail-empty", cand, "вердикт пуст по содержанию"))
            continue
        rej, why = _decision.is_rejected(text)
        if rej:
            log.append(("skip-neg", cand, why[:90]))
            continue
        log.append(("pick", cand, "принят"))
        return cand, zips[0], verd, log
    return None, None, None, log


def main():
    print("Резолвер CI — сухой прогон (логика build.yml воспроизведена)")
    cand, zp, verd, log = resolve()
    marks = {"pick": "✅", "skip-nozip": "·", "skip-noverdict": "⛔",
             "skip-neg": "⛔", "fail-empty": "⛔"}
    for kind, name, why in log:
        print("  %s %-8s %s" % (marks[kind], name, why))

    if cand is None:
        print("\n  ИТОГ: CI не выбрал пакет — сборка упала бы (код 1)")
        return 1

    sha = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    text = open(verd, encoding="utf-8", errors="replace").read()
    dec = _decision.find_decision(text)[1]
    # Вердикты цитируют sha сокращённо (`c7d782544708de4d…`), поэтому
    # проверяем префикс: 12+ hex-символов от начала хеша.
    bound = any(sha[:n] in text.lower() for n in (64, 40, 16, 12))
    print("\n  CI выберет: %s" % cand)
    print("  ZIP:        %s (%d Б)" % (os.path.basename(zp), os.path.getsize(zp)))
    print("  sha256:     %s" % sha)
    print("  Решение вердикта: %s" % (dec or "НЕ НАЙДЕНО"))
    print("  sha в вердикте:   %s" % ("ДА" if bound else "НЕТ"))

    idx = [n for k, n, _ in log].index(cand)
    newer = [n for k, n, _ in log[:idx]]
    rc = 0
    if newer:
        print("  ⛔ пропущены более старшие версии: %s" % ", ".join(newer))
        print("     релиз уйдёт ИЗ СТАРОГО пакета")
        rc = 2
    if not bound:
        print("  ⛔ вердикт не подтверждает sha256 этого ZIP")
        rc = 2
    if rc == 0:
        print("\n  ИТОГ: старший принятый пакет выбран, вердикт привязан к файлу (код 0)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
