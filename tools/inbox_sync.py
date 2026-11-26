#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inbox_sync.py — I104: канал Директора, перенос писем из main в ветку ролей.

Зачем: Директор пишет `.workflow/DIRECTOR_INBOX.md` **в `main`**, а роли
читают ветку ролей. Из-за этого пять писем от 2026-11-25 пролежали
незамеченными (расхождение на момент проверки — 48 строк).

Что делает: берёт письма из `origin/main` и ДОПИСЫВАЕТ в ветку те, которых
там нет. Ключ письма — заголовок `### [...]`. Ничего не удаляет и не
переставляет: если письмо уже есть, оно остаётся как есть.

Использование:
    python3 tools/inbox_sync.py            # показать, что не дошло (dry-run)
    python3 tools/inbox_sync.py --write    # дописать недостающие письма

Код возврата: 0 — всё синхронно (или дописано); 2 — есть несинхронные письма
в режиме просмотра; 1 — ошибка (нет git/файлов).
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL = os.path.join(REPO, ".workflow", "DIRECTOR_INBOX.md")
REL = ".workflow/DIRECTOR_INBOX.md"
HEADER = re.compile(r"^###\s+\[")


def git_show(ref_path):
    try:
        r = subprocess.run(["git", "show", ref_path], cwd=REPO,
                           capture_output=True, text=True)
    except OSError as exc:
        return None, str(exc)
    if r.returncode != 0:
        return None, (r.stderr or "").strip()[:200]
    return r.stdout, None


def split_messages(text):
    """Разбить на (шапка, [(заголовок, блок)]) — блоками от `### [`."""
    lines = text.splitlines()
    head, blocks = [], []
    cur = None
    for line in lines:
        if HEADER.match(line):
            if cur is not None:
                blocks.append(cur)
            cur = [line]
        elif cur is None:
            head.append(line)
        else:
            cur.append(line)
    if cur is not None:
        blocks.append(cur)
    return head, [(b[0].strip(), "\n".join(b).rstrip()) for b in blocks]


def main():
    write = "--write" in sys.argv
    if not os.path.isfile(LOCAL):
        print("ОШИБКА: нет %s" % REL)
        return 1

    main_text, err = git_show("origin/main:" + REL)
    if main_text is None:
        # Частый и нестрашный случай: ветки main нет в клоне. Не «ок», но и не
        # провал приёмки — печатаю прямо.
        print("НЕ ПРОВЕРЕНО — нет origin/main:%s (%s)" % (REL, err))
        return 1

    local_text = open(LOCAL, encoding="utf-8").read()
    _h1, main_msgs = split_messages(main_text)
    head, local_msgs = split_messages(local_text)

    local_keys = {title for title, _ in local_msgs}
    missing = [(t, b) for t, b in main_msgs if t not in local_keys]

    print("Канал Директора (I104)")
    print("  писем в main: %d | в ветке ролей: %d | не дошло: %d"
          % (len(main_msgs), len(local_msgs), len(missing)))

    if not missing:
        print()
        print("ИТОГ: СХОДИТСЯ — все письма Директора из main есть в ветке ролей")
        return 0

    for title, _ in missing:
        print("  · не дошло: %s" % title)

    if not write:
        print()
        print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — %d писем не дошли до ролей "
              "(запусти с --write, чтобы перенести)" % len(missing))
        return 2

    tail = "\n\n".join(block for _t, block in missing)
    new_text = local_text.rstrip() + "\n\n" + tail + "\n"
    with open(LOCAL, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    print()
    print("ИТОГ: ПЕРЕНЕСЕНО — дописано %d писем в %s" % (len(missing), REL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
