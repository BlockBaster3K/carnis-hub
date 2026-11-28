"""Эталон для проверок — из git-объекта, а не из рабочего дерева (З-17).

Проблема, которую решает модуль
-------------------------------
`glow_check`, `tendril_flesh_match` и `alpha_audit --baseline` брали эталон
(пакет 3.6.0-R) прямо из рабочего дерева:

    open("01-coder/3.6.0-R/project-3.6.0-R-clean.zip")

У Ревизора рабочее дерево собрано через sparse-checkout (лимит 128 МБ на
диск), и `01-coder/3.6.0-R/` там **нет**. Файл не открывался — и проверка
выдавала **✗ расхождение**, хотя расхождения не было. Один и тот же пакет
получал код 0 у Архитектора и код 1 у Ревизора только из-за устройства
дерева проверяющего. Это З-17.

Как теперь
----------
1. Если файл есть на диске — берём его (быстро, обратная совместимость).
2. Иначе пробуем **git-объект**: `git show <rev>:<path>`. Он есть у любого
   полного клона независимо от sparse-checkout, потому что живёт в
   `.git/objects`, а не в рабочем дереве.
3. Если нет ни того, ни другого — возвращаем `None` и статус
   `UNAVAILABLE`. Вызывающая проверка обязана сказать
   **«эталон недоступен — проверка пропущена»** и **не** выдавать это
   за расхождение.

Пропуск и отказ — разные вещи: «не смог проверить» нельзя показывать
как «проверил, не сходится».
"""

import atexit
import os
import subprocess
import tempfile

#: Путь эталона в репозитории (от корня).
REF_PATH = "01-coder/3.6.0-R/project-3.6.0-R-clean.zip"

#: Коммит, в котором эталон заведомо есть. Если `git show` по HEAD не
#: находит файл (например его вычистили из истории ветки), пробуем этот.
REF_REV = "a000b665"

OK = "ok"                # эталон получен
UNAVAILABLE = "unavailable"   # эталона нет — проверка пропускается

#: Временные файлы, созданные модулем (I103). Удаляются при выходе из
#: процесса — иначе каждый прогон гейта оставлял 12 МБ в `/tmp`.
_TEMP_REFS = []


def cleanup_temp_refs():
    """Удалить все временные эталоны, созданные модулем.

    Возвращает число удалённых файлов. Ошибки игнорируются: файл мог
    уже исчезнуть (кто-то вычистил `/tmp`).
    """
    removed = 0
    while _TEMP_REFS:
        path = _TEMP_REFS.pop()
        try:
            os.unlink(path)
            removed += 1
        except OSError:
            pass
    return removed


#: Страховка: файл удаляется при любом выходе из процесса, включая падение
#: проверки с исключением.
atexit.register(cleanup_temp_refs)


def _repo_root(start=None):
    """Корень рабочего дерева (или None, если это не git-репозиторий)."""
    d = os.path.abspath(start or os.getcwd())
    while True:
        marker = os.path.join(d, ".git")
        # .git бывает КАТАЛОГОМ (обычный клон), ФАЙЛОМ с «gitdir: …»
        # (worktree, submodule, часть CI-клонов) или ссылкой на каталог.
        if os.path.isdir(marker) or os.path.isfile(marker):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def _git_show(rev, path, root):
    """Вернуть bytes из `git show rev:path` или None."""
    try:
        p = subprocess.run(
            ["git", "-C", root, "show", "%s:%s" % (rev, path)],
            capture_output=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0 or not p.stdout:
        return None
    return p.stdout


def resolve(path=REF_PATH, rev=REF_REV, verbose=True):
    """Найти эталон. Возвращает (путь_к_читаемому_объекту, статус, откуда).

    Путь_к_читаемому_объекту — файл на диске (временный, если достали из
    git). Вызывающий может открывать его как обычный ZIP. Если эталона
    нет, первый элемент None, статус UNAVAILABLE.

    Временный файл **живёт только до выхода из процесса**: он создаётся
    через `mkstemp` (файл на диске, а не в памяти) и **удаляется в
    `atexit`** — даже если проверка упала или процесс прерван.

    И103: раньше файл оставался в `/tmp` навсегда. Эталон 3.6.0-R — 12 МБ,
    и каждый прогон гейта оставлял ещё один: за 17 прогонов накопилось
    200 МБ, что и упирало workspace в лимит. Теперь `cleanup_temp_refs()`
    удаляет всё, что создал модуль, а `atexit` — страховка на любой путь
    выхода из процесса.
    """
    # 1. Рабочее дерево — самый быстрый путь и полная совместимость.
    if os.path.exists(path):
        if verbose:
            print("  · эталон: рабочее дерево (%s)" % path)
        return path, OK, "worktree"

    # 2. git-объект.
    root = _repo_root()
    if root:
        # git show требует путь ОТНОСИТЕЛЬНО корня репозитория. Вызывающие
        # (например accept_3.7.2.py) передают абсолютный путь — приводим.
        rel = path
        if os.path.isabs(rel):
            rel = os.path.relpath(rel, root)
        rel = rel.replace(os.sep, "/")
        for r in (rev, "HEAD"):
            data = _git_show(r, rel, root)
            if data:
                fd, tmp = tempfile.mkstemp(prefix="baseline-", suffix=".zip")
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                # I103: файл обязателен к удалению при выходе из процесса.
                _TEMP_REFS.append(tmp)
                if verbose:
                    print("  · эталон: git-объект %s:%s (%d Б)"
                          % (r, rel, len(data)))
                return tmp, OK, "git:" + r

    # 3. Ничего нет — честный пропуск.
    if verbose:
        print("  · эталон недоступен (ни в рабочем дереве, ни в git) — "
              "проверка пропускается")
    return None, UNAVAILABLE, "none"


def describe_unavailable():
    """Единая формулировка для отчётов: это пропуск, а не расхождение."""
    return ("эталон недоступен — проверка пропущена "
            "(нет %s ни на диске, ни в git)" % REF_PATH)
