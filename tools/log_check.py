#!/usr/bin/env python3
"""Разбор лога Minecraft (latest.log) → компактный дайджест.

Зачем: лог весит десятки мегабайт и в чат не отправить. Этот скрипт вытаскивает
из него всё, что важно — версии, список модов, ошибки, предупреждения, спам,
стектрейсы — в файл на несколько килобайт.

Использование:
    python3 log_check.py <путь_к_latest.log> [-o <digest.md>] [--json]

Работает на Python 3.8+ без внешних зависимостей, на любой ОС.
"""
import argparse
import collections
import json
import os
import re
import sys

# [12:34:56] [Render thread/ERROR]: текст
LINE_RE = re.compile(r"^\[(?P<ts>[^\]]+)\] \[(?P<thread>[^\]]+)/(?P<level>[A-Z]+)\]: (?P<msg>.*)$")
# Шапка Forge: [xx:xx:xx] [main/INFO]: [Forge] ...
FORGE_MOD_RE = re.compile(r"\[(?:Mod|Mod File|FML)\b", re.I)

TRUNC = 400  # сколько символов строки оставлять в дайджесте


def parse(path):
    """Читает лог и собирает сводку. Файл читается построчно, память не растёт."""
    size = os.path.getsize(path)
    levels = collections.Counter()
    errors = collections.Counter()      # (уровень, текст) -> количество
    warns = collections.Counter()
    first_ts = last_ts = None
    all_lines = collections.Counter()    # самые частые строки целиком
    spam = collections.Counter()         # то же, но без метки времени и уровня —
                                        # именно так находится источник раздувания
    stack = []                          # строки стектрейсов
    mod_ids = set()
    header = []
    crash_markers = []
    total = 0
    tail = collections.deque(maxlen=60)

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            total += 1
            line = raw.rstrip("\n")
            tail.append(line)
            m = LINE_RE.match(line)
            if not m:
                if line.strip():
                    all_lines[line.strip()[:TRUNC]] += 1
                spam[line.strip()[:TRUNC]] += 1
                continue
            ts, level, msg = m.group("ts"), m.group("level"), m.group("msg")
            levels[level] += 1
            if first_ts is None:
                first_ts = ts
            last_ts = ts
            all_lines[f"[{level}] {msg[:TRUNC]}"] += 1
            spam[msg[:TRUNC]] += 1
            if level == "ERROR":
                errors[msg[:TRUNC]] += 1
            elif level == "WARN":
                warns[msg[:TRUNC]] += 1
            if level in ("ERROR", "FATAL"):
                crash_markers.append(f"[{ts}] {msg[:TRUNC]}")
            if re.search(r"Exception|Error|Caused by|at [\w.$]+\(", msg):
                stack.append(f"[{ts}] {msg[:TRUNC]}")
            if total <= 400:
                header.append(line)
            # моды
            mm = re.search(r"Mod ID:\s*'?([a-z0-9_.-]+)'?", msg, re.I)
            if mm:
                mod_ids.add(mm.group(1).lower())

    return dict(
        path=path, size=size, total=total, levels=dict(levels),
        errors=errors, warns=warns, all_lines=all_lines, stack=stack,
        header=header, mod_ids=mod_ids, crash_markers=crash_markers,
        first_ts=first_ts, last_ts=last_ts, tail=list(tail), spam=spam,
    )


def pick_versions(header):
    """Достаёт версии из шапки лога."""
    out = {}
    patterns = {
        "minecraft": r"Loading Minecraft ([0-9.]+)",
        "forge": r"With Forge ([0-9.]+)",
        "java": r"(Java (?:is )?[0-9][^\n,;]*)",
        "os": r"(Operating System: [^\n]*)",
    }
    text = "\n".join(header)
    for key, pat in patterns.items():
        m = re.search(pat, text, re.I)
        if m:
            out[key] = m.group(1).strip()
    return out


def top(counter, n=15):
    return counter.most_common(n)


def render(d, limit=15):
    L = []
    a = L.append
    a(f"# Дайджест лога — `{os.path.basename(d['path'])}`")
    a("")
    a(f"- **Размер:** {d['size']:,} Б".replace(",", " "))
    a(f"- **Строк всего:** {d['total']:,}".replace(",", " "))
    a(f"- **Время в логе:** {d['first_ts']} → {d['last_ts']}")
    a(f"- **Уровни:** " + ", ".join(f"`{k}` {v:,}".replace(",", " ") for k, v in
                                  sorted(d["levels"].items(), key=lambda x: -x[1])))
    v = pick_versions(d["header"])
    if v:
        a("- **Окружение:** " + "; ".join(f"{k} = {val}" for k, val in v.items()))
    if d["mod_ids"]:
        a(f"- **Модов найдено:** {len(d['mod_ids'])}")
        a(f"  - " + ", ".join(sorted(d["mod_ids"])))
    a("")

    a("## 🔴 Ошибки (ERROR/FATAL) — по убыванию частоты")
    a("")
    if d["errors"]:
        a("| Сколько | Сообщение |")
        a("|---:|---|")
        for msg, cnt in top(d["errors"], limit):
            a(f"| **{cnt}** | `{msg.replace('|', '\\|')}` |")
    else:
        a("Ошибок уровня ERROR/FATAL в логе **нет**.")
    a("")

    a("## 🟡 Предупреждения (WARN) — по убыванию частоты")
    a("")
    if d["warns"]:
        a("| Сколько | Сообщение |")
        a("|---:|---|")
        for msg, cnt in top(d["warns"], limit):
            a(f"| **{cnt}** | `{msg.replace('|', '\\|')}` |")
    else:
        a("Предупреждений уровня WARN нет.")
    a("")

    a("## 🔁 Спам: самые частые СООБЩЕНИЯ (без метки времени)")
    a("")
    a("Именно здесь живёт раздувание лога: если одно сообщение повторяется "
      "тысячи раз — это и есть источник мегабайтов.")
    a("")
    a("| Сколько | Сообщение |")
    a("|---:|---|")
    for msg, cnt in top(d["spam"], limit):
        a(f"| **{cnt}** | `{msg.replace('|', '\\|')}` |")
    a("")
    a(f"Всего уникальных сообщений: **{len(d['spam']):,}**".replace(",", " "))
    a("")

    if d["stack"]:
        a("## 💥 Строки со стектрейсами")
        a("")
        a("```")
        for s in d["stack"][:60]:
            a(s)
        a("```")
        a("")

    a("## 🖥 Последние строки лога (хвост)")
    a("")
    a("```")
    for s in d["tail"][-40:]:
        a(s[:TRUNC])
    a("```")
    a("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("-o", "--out", help="куда сохранить дайджест (по умолчанию — в stdout)")
    ap.add_argument("--json", action="store_true", help="вывести сводку в JSON")
    args = ap.parse_args()

    if not os.path.exists(args.log):
        print(f"Файл не найден: {args.log}", file=sys.stderr)
        return 1

    d = parse(args.log)
    if args.json:
        out = json.dumps({
            "size": d["size"], "lines": d["total"], "levels": d["levels"],
            "first_ts": d["first_ts"], "last_ts": d["last_ts"],
            "versions": pick_versions(d["header"]),
            "errors": d["errors"].most_common(30),
            "warns": d["warns"].most_common(30),
            "top_messages": d["spam"].most_common(20),
            "distinct_messages": len(d["spam"]),
        }, ensure_ascii=False, indent=2)
    else:
        out = render(d)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Дайджест сохранён: {args.out} ({len(out.encode('utf-8'))} Б)")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
