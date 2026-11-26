#!/usr/bin/env python3
"""Читает РЕШЕНИЕ в вердикте Ревизора, а не слово где угодно в файле.

Зачем — З-СИ-4
--------------
`build.yml` считал вердикт отрицательным по любому вхождению слова-триггера:

    NEG=$(grep -oiE 'НЕ ПРИНЯТ|ОТКЛОНЁН|ОТКЛОНЕНО|REJECTED' "$VERD2" || true)

Но вердикты содержат ИСТОРИЮ сдач. У `reviewer_373_verdict.md` строка 7:

    Цепочка сдач: `d19169b4…` — не принята (правка `pitch` вне S17) →

— это про ПРОШЛУЮ сдачу, а решение стоит на строке 11: `# ПРИНЯТО`.
То же у 3.7.2 и 3.5.3. Итог: CI пропускал 3.7.3 и 3.7.2 как «отрицательные»
и выпускал релиз из 3.7.1 — из старого пакета. Ровно класс З-CИ-1.

Что считается решением
----------------------
Строка, которая ПОСЛЕ снятия разметки (`#`, `*`, `>`, `-`) НАЧИНАЕТСЯ с
маркера: `ПРИНЯТО`, `НЕ ПРИНЯТО`, `ОТКЛОНЕНО`, `ОТКЛОНЁН`, `REJECTED`.
Либо строка вида `ВЕРДИКТ: <маркер>` / `ИТОГ: <маркер>` / `РЕШЕНИЕ: <маркер>`.
Упоминание слова в середине предложения решением НЕ является.

Коды
----
0 — решение отрицательное (публиковать нельзя)
1 — решение положительное
2 — решения в файле нет (fail-closed: без решения публиковать нельзя)
3 — файл не прочитан (fail-closed)
"""
import re
import sys

NEG = re.compile(r"НЕ\s*ПРИНЯТ|ОТКЛОНЁН|ОТКЛОНЕНО|REJECTED", re.I)
LEAD = re.compile(r"(НЕ\s*ПРИНЯТ|ПРИНЯТ|ОТКЛОНЕНО|ОТКЛОНЁН|REJECTED)", re.I)
MARK = re.compile(r"(ВЕРДИКТ|ИТОГ|РЕШЕНИЕ)\s*:?\s*\**\s*"
                  r"(НЕ\s*ПРИНЯТ|ПРИНЯТ|ОТКЛОНЕНО|ОТКЛОНЁН|REJECTED)", re.I)


def strip_markup(line):
    return line.strip().lstrip("#").strip().lstrip("*").strip().lstrip(">").strip().lstrip("-").strip()


def find_decision(text):
    """(номер строки, строка) первого решения или (None, None)."""
    for i, ln in enumerate(text.splitlines(), 1):
        st = strip_markup(ln)
        if not st:
            continue
        if MARK.match(st) or LEAD.match(st):
            return i, st
    return None, None


def is_rejected(text):
    """(bool, причина). bool=True — публиковать нельзя."""
    ln, st = find_decision(text)
    if st is None:
        return True, "решения в вердикте нет — fail-closed"
    if NEG.search(st):
        return True, "решение отрицательное (строка %d): %s" % (ln, st[:60])
    return False, "решение положительное (строка %d): %s" % (ln, st[:60])


def main(argv):
    if len(argv) != 2:
        print("usage: verdict_decision.py <verdict.md>", file=sys.stderr)
        return 3
    try:
        text = open(argv[1], encoding="utf-8", errors="replace").read()
    except OSError as exc:
        print("не прочитан: %s" % exc, file=sys.stderr)
        return 3
    if not re.search(r"\S", text):
        print("пуст по содержанию — fail-closed", file=sys.stderr)
        return 2
    rej, why = is_rejected(text)
    print(why)
    return 0 if rej else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
