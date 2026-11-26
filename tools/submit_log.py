#!/usr/bin/env python3
"""Отправить лог Minecraft в репозиторий — без перетаскивания файлов и без git.

Зачем: лог весит десятки мегабайт, в чат не отправить, а тащить репозиторий
клонировать тестеру не хочется. Скрипт сам:
  1) сжимает лог в gzip;
  2) строит компактный дайджест (ошибки, предупреждения, спам, окружение);
  3) заливает оба файла в репозиторий через GitHub API (только HTTP, git не нужен).

Использование (на машине, где лежит лог):

    python submit_log.py "C:\\Users\\...\\logs\\latest.log"

Токен берётся из переменной окружения GITHUB_TOKEN. Если её нет — спросит
(ввод не отображается) и не сохранит.

Куда грузит по умолчанию: репозиторий BlockBaster3K/carnis-hub, ветка
arena/d474d740-carnis-hub, папка 06-build/test-3.5.2/:
    latest.log.gz              — полный лог, сжатый
    latest.log.digest.md       — дайджест для разбора
    latest.log.filtered.txt    — только ошибки и предупреждения (если gzip велик)

Работает на Python 3.8+ без внешних зависимостей, Windows / Linux / macOS.
"""
import argparse
import base64
import gzip
import json
import os
import re
import sys
import urllib.error
import urllib.request

REPO = "BlockBaster3K/carnis-hub"
BRANCH = "arena/d474d740-carnis-hub"
FOLDER = "06-build/test-3.5.2"
API = "https://api.github.com"

LINE_RE = re.compile(r"^\[(?P<ts>[^\]]+)\] \[(?P<thread>[^\]]+)/(?P<level>[A-Z]+)\]: (?P<msg>.*)$")


# ----------------------------------------------------------------- разбор лога

def analyze(path):
    """Компактная сводка: уровни, ошибки, предупреждения, спам, окружение."""
    import collections
    levels = collections.Counter()
    errors = collections.Counter()
    warns = collections.Counter()
    spam = collections.Counter()
    stack = []
    head = []
    mods = set()
    first_ts = last_ts = None
    total = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            total += 1
            line = raw.rstrip("\n")
            m = LINE_RE.match(line)
            if not m:
                if line.strip():
                    spam[line.strip()[:400]] += 1
                continue
            ts, level, msg = m.group("ts"), m.group("level"), m.group("msg")
            levels[level] += 1
            if first_ts is None:
                first_ts = ts
            last_ts = ts
            spam[msg[:400]] += 1
            if level in ("ERROR", "FATAL"):
                errors[msg[:400]] += 1
            if level == "WARN":
                warns[msg[:400]] += 1
            if re.search(r"Exception|Caused by|at [\w.$]+\(", msg):
                stack.append(f"[{ts}] {msg[:400]}")
            if total <= 400:
                head.append(line)
            mm = re.search(r"Mod ID:\s*'?([a-z0-9_.-]+)'?", msg, re.I)
            if mm:
                mods.add(mm.group(1).lower())
    return dict(levels=levels, errors=errors, warns=warns, spam=spam,
                stack=stack, head=head, mods=mods, first_ts=first_ts,
                last_ts=last_ts, total=total)


def render_digest(path, a):
    size = os.path.getsize(path)
    L = []
    p = L.append
    p(f"# Дайджест лога — `{os.path.basename(path)}`")
    p("")
    p(f"- **Размер:** {size:,} Б".replace(",", " "))
    p(f"- **Строк всего:** {a['total']:,}".replace(",", " "))
    p(f"- **Время в логе:** {a['first_ts']} → {a['last_ts']}")
    p("- **Уровни:** " + ", ".join(
        f"`{k}` {v:,}".replace(",", " ") for k, v in a["levels"].most_common()))
    text = "\n".join(a["head"])
    for key, pat in (("minecraft", r"Loading Minecraft ([0-9.]+)"),
                     ("forge", r"With Forge ([0-9.]+)"),
                     ("java", r"(Java is [0-9][^\n,;]*)"),
                     ("os", r"(Operating System: [^\n]*)")):
        m = re.search(pat, text, re.I)
        if m:
            p(f"- **{key}:** {m.group(1).strip()}")
    if a["mods"]:
        p(f"- **Модов:** {len(a['mods'])} — " + ", ".join(sorted(a["mods"])))
    p("")
    for title, counter, icon in (("🔴 Ошибки (ERROR/FATAL)", a["errors"], "🔴"),
                                 ("🟡 Предупреждения (WARN)", a["warns"], "🟡")):
        p(f"## {title}")
        p("")
        if counter:
            p("| Сколько | Сообщение |")
            p("|---:|---|")
            for m, c in counter.most_common(20):
                p(f"| **{c}** | `{m.replace('|', chr(92)+'|')}` |")
        else:
            p("Не найдено.")
        p("")
    p("## 🔁 Спам: самые частые сообщения (без метки времени)")
    p("")
    p("| Сколько | Сообщение |")
    p("|---:|---|")
    for m, c in a["spam"].most_common(20):
        p(f"| **{c}** | `{m.replace('|', chr(92)+'|')}` |")
    p("")
    p(f"Всего уникальных сообщений: **{len(a['spam']):,}**".replace(",", " "))
    p("")
    if a["stack"]:
        p("## 💥 Строки со стектрейсами")
        p("")
        p("```")
        for s in a["stack"][:80]:
            p(s)
        p("```")
        p("")
    return "\n".join(L)


def filtered_log(path, limit=4000):
    """Только ERROR/WARN/FATAL + первые и последние строки."""
    out = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for i, raw in enumerate(f):
            if i < 300:
                out.append(raw.rstrip("\n"))
    tail = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    tail = [x.rstrip("\n") for x in lines[-300:]]
    mid = [x.rstrip("\n") for x in lines
           if re.search(r"/(ERROR|WARN|FATAL)\]:", x)][:limit]
    return ("\n".join(out) + "\n\n=== ОШИБКИ И ПРЕДУПРЕЖДЕНИЯ ===\n" + "\n".join(mid)
            + "\n\n=== ХВОСТ ЛОГА ===\n" + "\n".join(tail) + "\n")


# ----------------------------------------------------------------- GitHub API

def api(method, path, token, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        API + path, data=data, method=method,
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:400]
        raise SystemExit(f"GitHub API: {e.code} {detail}")


def upload(path_in_repo, data: bytes, token, message):
    """Загружает файл через Git Data API (Contents API ограничен 1 МБ)."""
    ref = api("GET", f"/repos/{REPO}/git/ref/heads/{BRANCH}", token)["object"]
    commit = api("GET", f"/repos/{REPO}/git/commits/{ref['sha']}", token)
    base_tree = commit["tree"]["sha"]
    blob = api("POST", f"/repos/{REPO}/git/blobs", token,
               {"content": base64.b64encode(data).decode("ascii"), "encoding": "base64"})
    tree = api("POST", f"/repos/{REPO}/git/trees", token,
               {"base_tree": base_tree,
                "tree": [{"path": path_in_repo, "mode": "100644",
                          "type": "blob", "sha": blob["sha"]}]})
    new_commit = api("POST", f"/repos/{REPO}/git/commits", token,
                     {"message": message, "tree": tree["sha"],
                      "parents": [ref["sha"]]})
    api("PATCH", f"/repos/{REPO}/git/refs/heads/{BRANCH}", token,
        {"sha": new_commit["sha"], "force": False})
    print(f"  ✅ {path_in_repo}  ({len(data):,} Б)".replace(",", " "))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log", help="путь к latest.log")
    ap.add_argument("--token", help="PAT (или задайте GITHUB_TOKEN)")
    args = ap.parse_args()

    if not os.path.exists(args.log):
        print(f"Файл не найден: {args.log}", file=sys.stderr)
        return 1

    token = args.token or os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        import getpass
        print("Нужен fine-grained PAT (репозиторий " + REPO + ", Contents: Read and write).")
        token = getpass.getpass("Вставьте токен (ввод не отображается): ").strip()
    if not token:
        print("Токен не задан — загрузка отменена.", file=sys.stderr)
        return 1

    print(f"Читаю {args.log} …")
    a = analyze(args.log)
    digest = render_digest(args.log, a).encode("utf-8")
    print(f"  дайджест: {len(digest):,} Б".replace(",", " "))

    print("Сжимаю лог …")
    with open(args.log, "rb") as f:
        raw = f.read()
    gz = gzip.compress(raw, 9)
    print(f"  gzip: {len(gz):,} Б (было {len(raw):,})".replace(",", " "))

    uploads = [(f"{FOLDER}/latest.log.gz", gz, "tester: latest.log (сжатый)"),
               (f"{FOLDER}/latest.log.digest.md", digest,
                "tester: дайджест latest.log")]
    if len(gz) > 8 * 1024 * 1024:
        fl = filtered_log(args.log).encode("utf-8")
        uploads.append((f"{FOLDER}/latest.log.filtered.txt", fl,
                        "tester: фильтр latest.log (ошибки и предупреждения)"))
        print(f"  фильтр: {len(fl):,} Б".replace(",", " "))

    print(f"Загружаю в {REPO} → {BRANCH} → {FOLDER}/")
    for path, data, msg in uploads:
        upload(path, data, token, msg)

    print("\nГотово. Интегратор разберёт лог сам — отвечать в формы не нужно.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
