#!/usr/bin/env python3
"""Проверка, которая молча выключается, когда пакет и так красный.

Зачем. Интегратор в `integrator_380_gate_first_run.md` §3 нашёл свой дефект:

    if not fail:
        run_tool("infected_sound_audit", ...)

`fail` — список ВСЕХ провалов гейта. К моменту этой проверки в нём уже лежали
замечания другого блока, поэтому проверка не выполнялась. На настоящем пакете
это незаметно: он и так красный. Но покрытие остаётся НЕИЗВЕСТНЫМ, а в отчёте
об этом ни слова.

Он нашёл это чтением. Этот тест ищет класс машинно: вызов проверки, обёрнутый
в условие по глобальному списку провалов (`fail`, `skipped_checks`, `problems`),
— то есть проверку, которая отключается из-за чужих результатов.

Ложные срабатывания отсекаются:
  * финальный вывод гейта (`if fail: print(...)`) — там смотреть на fail ВЕРНО;
  * строки-комментарии;
  * условия по ЛОКАЛЬНЫМ счётчикам (`if failed:`, `if skipped:`) — они про
    собственный результат блока, а не про чужие.

Коды возврата: 0 — таких вызовов нет; 2 — есть (называет строки);
               3 — файл не читается.
"""
import argparse
import io
import os
import re
import sys
import tokenize

# Вызов проверки: run_tool(...) или имя вида check_xxx(
CALL_RE = re.compile(r"\b(run_tool|check_\w+)\s*\(")
# Условие по ГЛОБАЛЬНОМУ списку провалов гейта
GLOBAL_RE = re.compile(r"^\s*(if|elif)\s+(not\s+)?(fail|skipped_checks|problems)\b\s*:")
# Строки, которые лишь печатают итог — смотреть на fail там правильно
PRINT_RE = re.compile(r"\b(print|fail\.append|sys\.exit|return)\b")


def logical_lines(src):
    """Строки кода без комментариев и строк-литералов, с номерами."""
    out = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                continue
            ln = tok.start[0]
            out.setdefault(ln, []).append(tok.string)
    except (tokenize.TokenError, IndentationError):
        return None
    return out


def scan(path):
    src = open(path, encoding="utf-8").read()
    toks = logical_lines(src)
    if toks is None:
        return None
    lines = src.split("\n")
    hits = []
    for ln, parts in toks.items():
        text = " ".join(parts)
        if not GLOBAL_RE.match(text):
            continue
        if PRINT_RE.search(text):        # финальный вывод — не проверка
            continue
        if "append" in text:
            continue
        # что стоит под условием: ищем вызов проверки в следующих строках,
        # пока не начался блок на том же уровне отступа
        indent = len(lines[ln - 1]) - len(lines[ln - 1].lstrip())
        for j in range(ln, min(ln + 12, len(lines))):
            cur = lines[j]
            if not cur.strip():
                continue
            cur_indent = len(cur) - len(cur.lstrip())
            if cur_indent <= indent:
                break
            if CALL_RE.search(cur) and not PRINT_RE.search(cur):
                hits.append((ln, j + 1, lines[ln - 1].strip(), cur.strip()))
                break
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    total = 0
    for path in a.files:
        if not os.path.isfile(path):
            print("ОШИБКА: нет файла %s" % path)
            return 3
        hits = scan(path)
        if hits is None:
            print("ОШИБКА: %s не разобран (токенизатор)" % path)
            return 3
        if not a.quiet:
            print("%s: подозрительных условий %d" % (path, len(hits)))
        for cond_ln, call_ln, cond, call in hits:
            total += 1
            print("  строка %d: %s" % (cond_ln, cond))
            print("    вызов на строке %d: %s" % (call_ln, call[:90]))
            print("    проверка отключится, если ЧУЖОЙ блок уже дал провал")
    print()
    if total:
        print("ИТОГ: НАЙДЕНО %d — проверка отключается по чужому состоянию"
              % total)
        return 2
    print("ИТОГ: ЧИСТО — ни одна проверка не обёрнута в условие по общему списку")
    return 0


if __name__ == "__main__":
    sys.exit(main())
