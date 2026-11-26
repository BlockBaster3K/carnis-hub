#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""repo_tree_guard.py — страж целостности дерева репозитория.

Зачем: коммит `84f3a43` (Художник, 2026-11-22) сделан **из подкаталога** —
его дерево содержало только `04-artist/` (3 файла) и удаляло **7301 путь**
репозитория: `01-coder/` с пакетом 3.7.3, `02-reviewer/tools/`, `03-sound/`,
`tools/`, `00-board/`. Любой агент, сделавший `git pull`, получал пустой
репозиторий и не мог отличить «пакета нет» от «репозитория нет».

Ни один инструмент этого не ловил: гейты проверяют пакет, CI — сборку.
Проверка целостности самого дерева не делалась ни разу.

Использование:
    python3 02-reviewer/tools/repo_tree_guard.py [rev]      # по умолчанию HEAD

Код возврата: 0 — дерево цело, 2 — целостность нарушена, 1 — не удалось проверить.
"""

import subprocess
import sys

# Каталоги/файлы, без которых репозиторий не является собой.
REQUIRED_DIRS = ["00-board", "00-common", "01-coder", "02-reviewer", "03-sound",
                 "04-artist", "05-architect", "06-build", "07-project",
                 "tools", ".github", ".workflow"]
REQUIRED_FILES = ["README.md"]
MIN_FILES = 1000  # принятый репозиторий — 7304 пути; 1000 ловит обвал, не мешает росту


def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip())
    return r.stdout


def main():
    rev = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    try:
        top = [l for l in git("ls-tree", "--name-only", rev).splitlines() if l]
        total = len(git("ls-tree", "-r", "--name-only", rev).splitlines())
        sha = git("rev-parse", "--short", rev).strip()
    except (RuntimeError, OSError) as exc:
        print("ОШИБКА: не удалось прочитать дерево %s: %s" % (rev, exc))
        return 1

    print("Страж дерева репозитория")
    print("Ревизия: %s | путей в дереве: %d | в корне: %d" % (sha, total, len(top)))
    fails = []

    missing_dirs = [d for d in REQUIRED_DIRS if d not in top]
    missing_files = [f for f in REQUIRED_FILES if f not in top]
    if missing_dirs:
        print("  ✗ нет каталогов в корне: %s" % ", ".join(missing_dirs))
        fails.append("нет каталогов: " + ", ".join(missing_dirs))
    else:
        print("  ✓ все %d обязательных каталогов на месте" % len(REQUIRED_DIRS))
    if missing_files:
        print("  ✗ нет файлов в корне: %s" % ", ".join(missing_files))
        fails.append("нет файлов: " + ", ".join(missing_files))
    if total < MIN_FILES:
        print("  ✗ путей в дереве %d < порога %d — похоже на обвал дерева"
              % (total, MIN_FILES))
        fails.append("путей %d < %d" % (total, MIN_FILES))
    else:
        print("  ✓ путей в дереве %d (порог %d)" % (total, MIN_FILES))

    # Признак «коммит из подкаталога»: в корне один каталог и почти нет файлов.
    if len(top) <= 2 and total < 50:
        print("  ✗ корень выглядит как подкаталог: %s" % top)
        fails.append("корень = подкаталог %s" % top)

    print()
    if fails:
        print("ИТОГ: ЦЕЛОСТНОСТЬ НАРУШЕНА — %s" % "; ".join(fails))
        return 2
    print("ИТОГ: СХОДИТСЯ — дерево репозитория цело")
    return 0


if __name__ == "__main__":
    sys.exit(main())
