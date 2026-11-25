#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ci_guard_test.py — проверка защиты CI от релиза непринятого пакета (T-3138).

Что делает: вытаскивает из `.github/workflows/build.yml` **настоящие** shell-блоки
шагов «Resolve package» и «Assert version», подставляет их в синтетические деревья
репозитория (в /tmp) и прогоняет сценарии. Проверяется именно тот код, который
выполнит GitHub Actions — не пересказ логики.

Использование:
    python3 02-reviewer/tools/ci_guard_test.py [--workflow путь] [-v]

Код возврата: 0 — все сценарии дали ожидаемое, 2 — есть расхождения, 1 — ошибка запуска.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

DEFAULT_WF = ".github/workflows/build.yml"


def extract_step_run(wf_text, step_name):
    """Возвращает shell-текст шага `- name: <step_name>` (блок `run: |`)."""
    lines = wf_text.splitlines()
    out, indent, found = [], None, False
    for i, line in enumerate(lines):
        if line.strip() == "- name: %s" % step_name:
            found = True
            continue
        if not found:
            continue
        if indent is None:
            if line.strip() == "run: |":
                indent = len(line) - len(line.lstrip()) + 2
            continue
        if line.strip() and (len(line) - len(line.lstrip())) < indent:
            break
        out.append(line[indent:] if line.strip() else "")
    if indent is None:
        raise RuntimeError("в шаге %r не найден блок 'run: |'" % step_name)
    return "\n".join(out) + "\n"


def prepare_script(script, with_inputs=True):
    """Убираем выражения GitHub Actions, которые вне раннера не существуют."""
    script = script.replace("${{ github.event.inputs.package }}", "${INPUT_PKG:-}")
    script = script.replace("${{ steps.pkg.outputs.path }}", "${PKG_PATH:-}")
    for var in ("GITHUB_STEP_SUMMARY", "GITHUB_OUTPUT"):
        script = script.replace('>> "$%s"' % var, '>> "$%s"' % var)
    return script


def run_step(script, root, env_extra=None):
    env = dict(os.environ)
    env["GITHUB_STEP_SUMMARY"] = os.path.join(root, "_summary.md")
    env["GITHUB_OUTPUT"] = os.path.join(root, "_output.txt")
    env.pop("INPUT_PKG", None)
    if env_extra:
        env.update({k: str(v) for k, v in env_extra.items()})
    for f in (env["GITHUB_STEP_SUMMARY"], env["GITHUB_OUTPUT"]):
        open(f, "w").close()
    p = subprocess.run(["bash", "-c", script], cwd=root, env=env,
                       capture_output=True, text=True)
    out = (env["GITHUB_OUTPUT"] and open(env["GITHUB_OUTPUT"]).read()) or ""
    return p.returncode, p.stdout + p.stderr, out


# ---------- построение синтетического дерева ----------

def make_zip(path, version=None, files=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(path, "w") as z:
        if version is not None:
            z.writestr("gradle.properties", "mod_version=%s\n" % version)
        for name, data in (files or {}).items():
            z.writestr(name, data)


def add_package(root, ver, with_zip=True, zip_version=None, zip_name=None):
    d = os.path.join(root, "01-coder", ver)
    os.makedirs(d, exist_ok=True)
    if with_zip:
        name = zip_name or ("project-%s-clean.zip" % ver.split("-R")[0])
        make_zip(os.path.join(d, name), version if (version := zip_version if zip_version is not None else ver.split("-R")[0]) else None)


def add_verdict(root, name, text):
    d = os.path.join(root, "00-board", "reports")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write(text + "\n")


def new_root(tmp):
    root = tempfile.mkdtemp(dir=tmp)
    os.makedirs(os.path.join(root, "00-board", "reports"), exist_ok=True)
    return root


# ---------- проверка выходного пути и шага версии ----------

def selected_pkg(output_text):
    m = re.search(r"^path=(.+)$", output_text, re.M)
    return m.group(1).strip() if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", default=DEFAULT_WF)
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    try:
        wf = open(a.workflow, encoding="utf-8").read()
        resolve = prepare_script(extract_step_run(wf, "Resolve package"))
        assert_ver = prepare_script(extract_step_run(wf, "Assert version"))
    except Exception as exc:  # noqa: BLE001
        print("ОШИБКА: не удалось прочитать workflow: %s" % exc)
        return 1

    tmp = tempfile.mkdtemp(prefix="ci_guard_")
    rows = []

    def case(name, expect, root, script=resolve, env=None, check=None):
        code, log, out = run_step(script, root, env)
        pkg = selected_pkg(out)
        ok, fact = check(code, log, out, pkg) if check else (False, "нет проверки")
        rows.append((name, expect, fact, ok, log))
        return ok

    def err_expected(substring=None):
        def f(code, log, out, pkg):
            good = code != 0 and not pkg and (substring is None or substring in log)
            return good, "код %d, пакет %r%s" % (code, pkg or "—",
                                                 "" if substring is None else
                                                 (", сообщение есть" if substring in log else ", СООБЩЕНИЯ НЕТ"))
        return f

    def ok_expected(ver):
        def f(code, log, out, pkg):
            good = code == 0 and ("01-coder/%s/" % ver) in pkg
            return good, "код %d, пакет %s" % (code, pkg or "—")
        return f

    try:
        # 0. исходное состояние репозитория как есть (регресс на реальных данных)
        add_package(new_root(tmp), "3.7.1", with_zip=False)  # просто чтобы каталог был
        r = new_root(tmp)
        add_package(r, "3.7.1")
        add_verdict(r, "reviewer_371_verdict.md", "# Вердикт\n\n**ПРИНЯТО.**")
        case("реальный случай: 3.7.1 + reviewer_371_verdict.md", "выбрана 3.7.1",
             r, check=ok_expected("3.7.1"))

        # 1. пакет без вердикта
        r = new_root(tmp)
        add_package(r, "3.9.9")
        case("пакет 3.9.9 без вердикта", "код != 0, релиза нет",
             r, check=err_expected("вердикта Ревизора нет"))

        # 2. отрицательный вердикт (вид без точек)
        r = new_root(tmp)
        add_package(r, "3.9.9")
        add_verdict(r, "reviewer_399_verdict.md", "# Вердикт\n\n**НЕ ПРИНЯТО** — светотень 81 %.")
        case("отрицательный вердикт reviewer_399_verdict.md", "код != 0, релиза нет",
             r, check=err_expected("отрицательный"))

        # 3. отрицательный вердикт (вид с точками) и слово ОТКЛОНЕНО
        r = new_root(tmp)
        add_package(r, "3.9.9")
        add_verdict(r, "reviewer_3.9.9_verdict.md", "# Вердикт\n\nПакет ОТКЛОНЕНО по швам.")
        case("отрицательный вердикт reviewer_3.9.9_verdict.md («ОТКЛОНЕНО»)", "код != 0",
             r, check=err_expected("отрицательный"))

        # 4. положительный вердикт (без точек)
        r = new_root(tmp)
        add_package(r, "3.9.9")
        add_verdict(r, "reviewer_399_verdict.md", "# Вердикт\n\n**ПРИНЯТО.**")
        case("положительный вердикт reviewer_399_verdict.md", "пакет 3.9.9 выбран",
             r, check=ok_expected("3.9.9"))

        # 5. положительный вердикт (с точками)
        r = new_root(tmp)
        add_package(r, "3.9.9")
        add_verdict(r, "reviewer_3.9.9_verdict.md", "# Вердикт\n\n**ПРИНЯТО.**")
        case("положительный вердикт reviewer_3.9.9_verdict.md", "пакет 3.9.9 выбран",
             r, check=ok_expected("3.9.9"))

        # 6. РЕПРО инцидента: 3.7.2 (пакет, вердикта нет) + 3.7.1 (пакет, вердикт есть)
        r = new_root(tmp)
        add_package(r, "3.7.2")
        add_package(r, "3.7.1")
        add_verdict(r, "reviewer_371_verdict.md", "**ПРИНЯТО.**")
        case("репро инцидента: 3.7.2 без вердикта, 3.7.1 принята", "выбрана 3.7.1, 3.7.2 пропущена",
             r, check=ok_expected("3.7.1"))

        # 7. старшая версия отклонена, младшая принята
        r = new_root(tmp)
        add_package(r, "3.9.9")
        add_package(r, "3.7.1")
        add_verdict(r, "reviewer_399_verdict.md", "**НЕ ПРИНЯТО**")
        add_verdict(r, "reviewer_371_verdict.md", "**ПРИНЯТО.**")
        case("3.9.9 отклонена, 3.7.1 принята", "выбрана 3.7.1",
             r, check=ok_expected("3.7.1"))

        # 8. каталог без ZIP (заготовка) + принятая версия
        r = new_root(tmp)
        add_package(r, "3.9.9", with_zip=False)
        add_package(r, "3.7.1")
        add_verdict(r, "reviewer_371_verdict.md", "**ПРИНЯТО.**")
        case("3.9.9 — каталог без ZIP, 3.7.1 принята", "выбрана 3.7.1",
             r, check=ok_expected("3.7.1"))

        # 9. ни одного пакета
        r = new_root(tmp)
        add_package(r, "3.7.1", with_zip=False)
        case("ни одного ZIP", "код != 0", r, check=err_expected("Нет ни одного принятого"))

        # 10. пересдача -R5 берёт вердикт базовой версии
        r = new_root(tmp)
        add_package(r, "3.9.9-R5", zip_version="3.9.9", zip_name="project-3.9.9-clean.zip")
        add_verdict(r, "reviewer_399_verdict.md", "**ПРИНЯТО.**")
        case("пересдача 3.9.9-R5 с вердиктом 3.9.9", "пакет 3.9.9-R5 выбран",
             r, check=ok_expected("3.9.9-R5"))

        # 11. РИСК: вердикт чужой версии подходит по подстроке (3.1.2 ↔ reviewer_3120_…)
        r = new_root(tmp)
        add_package(r, "3.1.2")
        add_verdict(r, "reviewer_3120_delta_verdict.md", "**ПРИНЯТО.**")  # вердикт про 3.12.0
        case("РИСК подстроки: пакет 3.1.2 без своего вердикта, рядом вердикт 3.12.0",
             "ожидание: код != 0 (своего вердикта нет)",
             r, check=err_expected(None))

        # 12. обход через workflow_dispatch: package задан вручную
        r = new_root(tmp)
        add_package(r, "3.9.9")
        case("workflow_dispatch с ручным package: вердикта нет",
             "ожидание: защита работает и здесь",
             r, env={"INPUT_PKG": "01-coder/3.9.9/project-3.9.9-clean.zip"},
             check=err_expected(None))

        # 13. РИСК: пустой файл вердикта (заглушка) — считается принятым
        r = new_root(tmp)
        add_package(r, "3.9.9")
        add_verdict(r, "reviewer_399_verdict.md", "")
        case("РИСК: файл вердикта — пустая заглушка",
             "ожидание: код != 0 (в файле нет ни одного слова)",
             r, check=err_expected(None))

        # 14. РИСК: слово «НЕ ПРИНЯТО» в теле положительного вердикта
        r = new_root(tmp)
        add_package(r, "3.9.9")
        add_verdict(r, "reviewer_399_verdict.md",
                    "**ПРИНЯТО.** В §3 перечислены файлы, получившие ранее НЕ ПРИНЯТО.")
        case("РИСК: «НЕ ПРИНЯТО» внутри принятого вердикта",
             "ожидание: код != 0 или явное предупреждение",
             r, check=err_expected(None))

        # 15. Assert version: совпадает / не совпадает / -R
        def assert_case(name, ver_dir, zip_ver, expect_ok, env_pkg):
            r = new_root(tmp)
            add_package(r, ver_dir, zip_version=zip_ver,
                        zip_name="project-%s-clean.zip" % zip_ver)
            os.makedirs(os.path.join(r, "build-src"), exist_ok=True)
            with zipfile.ZipFile(os.path.join(r, "01-coder", ver_dir,
                                              "project-%s-clean.zip" % zip_ver)) as z:
                z.extractall(os.path.join(r, "build-src"))
            code, log, _ = run_step(assert_ver, r, {"PKG_PATH": env_pkg})
            ok = (code == 0) == expect_ok
            rows.append((name, "версия совпадает" if expect_ok else "ошибка",
                         "код %d" % code, ok, log))

        assert_case("Assert version: 3.9.9 = 3.9.9", "3.9.9", "3.9.9", True,
                    "01-coder/3.9.9/project-3.9.9-clean.zip")
        assert_case("Assert version: пакет 3.9.8 в каталоге 3.9.9", "3.9.9", "3.9.8", False,
                    "01-coder/3.9.9/project-3.9.8-clean.zip")
        assert_case("Assert version: пересдача 3.9.9-R5 → ожидается 3.9.9", "3.9.9-R5", "3.9.9", True,
                    "01-coder/3.9.9-R5/project-3.9.9-clean.zip")

    finally:
        if a.verbose:
            for name, expect, fact, ok, log in rows:
                print("=" * 70)
                print(name, "|", "OK" if ok else "РАСХОЖДЕНИЕ")
                print(log.strip()[:1200])
        shutil.rmtree(tmp, ignore_errors=True)

    print("%-62s %-22s %s" % ("сценарий", "факт", "итог"))
    print("-" * 104)
    bad = 0
    for name, expect, fact, ok, _log in rows:
        if not ok:
            bad += 1
        print("%-62s %-22s %s" % (name[:62], fact[:22], "OK" if ok else "РАСХОЖДЕНИЕ"))
    print("-" * 104)
    print("Сценариев: %d, расхождений: %d" % (len(rows), bad))
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
