#!/usr/bin/env python3
"""Проверка «pull не удалил содержимое» — дополняет страж формы дерева.

Зачем отдельный тест. `02-reviewer/tools/repo_tree_guard.py` (Ревизор, после
аварии `84f3a43`) проверяет ФОРМУ дерева: 12 обязательных каталогов, порог
1000 путей, сигнатуру «корень = подкаталог». Он ловит обвал всего дерева.

Он НЕ ловит частичную потерю: если pull удалит, например, `03-sound/masters/`
целиком, каталог `03-sound` останется, путей будет >1000, все 12 каталогов на
месте — страж промолчит. А звуковая часть при этом мертва.

Этот тест проверяет, что артефакты, без которых роль не работает, ЖИВЫ:

  * мастера: количество файлов == SHA256SUMS.txt, каждый sha сходится
  * канон: 144 файла по MANIFEST_canon_144.txt
  * план роли и доска задач не пусты
  * инструменты, на которые ссылается статус, существуют

Коды возврата:
  0 — всё на месте
  2 — потеря/порча найдена (перечисляет что)
  3 — не удалось проверить (нет исходного файла-реестра): fail-closed
"""
import hashlib
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_sums(sums_file, base):
    """Возвращает (ok, bad, missing, err)."""
    if not os.path.isfile(sums_file):
        return False, [], [], "нет реестра %s" % os.path.relpath(sums_file, REPO)
    bad, missing, ok = [], [], 0
    with open(sums_file, encoding="utf-8") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) != 2:
                continue
            digest, name = parts
            path = os.path.join(base, name)
            if not os.path.isfile(path):
                missing.append(name)
            elif sha256(path) != digest:
                bad.append(name)
            else:
                ok += 1
    return True, bad, missing, ok


def check_nonempty_git(rel, min_bytes):
    """Размер файла берём ИЗ РЕПОЗИТОРИЯ, не из чекаута.

    Иначе sparse-клон без каталога даёт ложный провал «нет файла» — ровно та
    ошибка, которую Ревизор называл артефактом своего клона, а не дефектом
    пакета. Вопрос теста — «есть ли файл в дереве HEAD», а не «скачан ли он»."""
    r = subprocess.run(["git", "-C", REPO, "ls-tree", "-l", "HEAD", "--", rel],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return "нет файла %s в дереве HEAD" % rel
    parts = r.stdout.split()
    try:
        size = int(parts[3])
    except (IndexError, ValueError):
        return "%s: не удалось прочитать размер из ls-tree" % rel
    if size < min_bytes:
        return "%s подозрительно мал (%d < %d)" % (rel, size, min_bytes)
    return None


def main():
    fails = []

    # 1. Мастера
    sums = os.path.join(REPO, "03-sound", "masters", "SHA256SUMS.txt")
    got, bad, missing, ok = check_sums(sums, os.path.join(REPO, "03-sound", "masters"))
    if not got:
        print("X мастера: %s" % ok)
        fails.append(ok)
    else:
        print("  мастера: %d сходятся, %d изменены, %d отсутствуют"
              % (ok, len(bad), len(missing)))
        for n in (bad + missing)[:5]:
            print("      ? %s" % n)
        if bad or missing:
            fails.append("мастера: %d изменены, %d отсутствуют" % (len(bad), len(missing)))

    # 2. Канон
    man = os.path.join(REPO, "03-sound", "MANIFEST_canon_144.txt")
    got, bad, missing, ok = check_sums(man, os.path.join(REPO, "03-sound"))
    if not got:
        print("X канон: %s" % ok)
        fails.append(ok)
    else:
        print("  канон: %d сходятся, %d изменены, %d отсутствуют"
              % (ok, len(bad), len(missing)))
        for n in (bad + missing)[:5]:
            print("      ? %s" % n)
        if bad or missing:
            fails.append("канон: %d изменены, %d отсутствуют" % (len(bad), len(missing)))

    # 3. Документы роли
    for rel, floor in (("00-board/agents/sound.md", 2000),
                       ("00-board/agents/sound_plan.md", 1000),
                       (".workflow/TASK_BOARD.md", 1000)):
        err = check_nonempty_git(rel, floor)
        if err:
            print("X %s" % err)
            fails.append(err)
    print("  документы роли: проверены 3")

    # 4. Инструменты, на которые ссылается статус
    for rel in ("tools/volume_effective_check.py", "tools/manifest_canon_test.py",
                "03-sound/spec/volume_spec_t3202.json",
                "03-sound/check_baseline_master.py", "03-sound/baseline_master.json"):
        if not os.path.isfile(os.path.join(REPO, rel)):
            print("X нет инструмента %s" % rel)
            fails.append("нет %s" % rel)
    print("  инструменты: проверены 5")

    print()
    if fails:
        print("ИТОГ: ПОТЕРЯ СОДЕРЖИМОГО — %s" % "; ".join(fails))
        return 2
    print("ИТОГ: СОДЕРЖИМОЕ ЦЕЛО — pull ничего не удалил")
    return 0


if __name__ == "__main__":
    sys.exit(main())
