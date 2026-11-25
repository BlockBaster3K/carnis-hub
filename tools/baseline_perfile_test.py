#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Негативные тесты перфайловой fail-closed проверки baseline(M) (R24).

Run: python3 tools/baseline_perfile_test.py
Только стандартная библиотека.

Проверяется реализация в tools/crest_master.py (одна норма на оба гейта,
blocks 12б accept_3.7.3 / accept_3.8.0):

  * _baseline_master() — ЕДИНСТВЕННЫЙ источник baseline(M) от PCM-мастера.
    Отсутствующий/битый/непрочитываемый JSON -> маркер ошибки, гейт обязан
    упасть (З-29 п.5), тихое понижение стационарных до отчёта запрещено.
  * Каждый стационарный файл без своей записи baseline(M) -> stationary_unmeasured
    -> _fail (перфайлово, не потиповым признаком «хоть одна запись типа»).
  * Зелёная строка печатается только при отсутствии ВСЕХ провалов.

Сценарий Ревизора (I23 s14): из 33 стационарных записей оставлена одна.
Раньше достаточно было «хоть одна запись типа стац в JSON», и остальные
файлы без своей записи тихо уходили в отчёт при зелёном вердикте. Теперь
файл без своей записи baseline(M) — провал: нормы для него нет.
"""
import json
import os
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREST_MASTER = os.path.join(REPO, "tools", "crest_master.py")


def load_crest_master():
    import importlib.util
    spec = importlib.util.spec_from_file_location("crest_master", CREST_MASTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def classify(rel, typ, src, has_type):
    """Модель развилки гейта для файла без per-file baseline(M).

    has_type (была ли хоть одна запись типа в JSON) больше НЕ влияет на
    решение — ровно в этом суть правки Р24. Решает только наличие own-записи.
    """
    if not (typ == "стац" and src == "таблица"):
        return "norm"
    # Перфайлово: записи у этого файла нет -> норма недоказуема -> провал.
    del has_type
    return "fail"


class PerFileBaselineTests(unittest.TestCase):
    def test_stationary_without_own_record_fails_even_if_type_present(self):
        # Сценарий Ревизора: запись типа «стац» в JSON есть, но у файла нет
        # своей записи baseline(M) -> провал, а не отчёт.
        self.assertEqual(
            classify("entity/infected_blaze_ambient_01.ogg", "стац",
                     "таблица", True), "fail")

    def test_stationary_without_record_fails_when_type_absent_too(self):
        self.assertEqual(
            classify("entity/infected_blaze_ambient_01.ogg", "стац",
                     "таблица", False), "fail")

    def test_stationary_with_own_record_is_norm(self):
        self.assertEqual(
            classify("entity/infected_blaze_ambient_01.ogg", "стац",
                     "baseline(M)", True), "norm")

    def test_transient_without_own_record_is_not_affected(self):
        self.assertEqual(
            classify("combat/combat_deflect_01_chitin.ogg", "транз",
                     "таблица", False), "norm")

    def test_type_presence_does_not_decide(self):
        # has_type не должен переопределять solution — перфайлово.
        self.assertEqual(classify("x.ogg", "стац", "таблица", True), "fail")
        self.assertEqual(classify("x.ogg", "стац", "таблица", False), "fail")


class CrestMasterSourceTests(unittest.TestCase):
    """Структурная проверка tools/crest_master.py: дыра R24 закрыта."""

    def setUp(self):
        with open(CREST_MASTER, encoding="utf-8") as fh:
            self.src = fh.read()

    def test_baseline_master_loader_is_fail_closed(self):
        # Загрузчик должен помечать ошибку, а не возвращать пустой успех.
        self.assertIn("__error__", self.src)
        self.assertIn("норма стационарных недоказуема", self.src)

    def test_no_per_type_shortcut(self):
        # Нет останков зашиты «если есть хоть одна запись типа -> ок».
        self.assertNotIn("_BM_has_type", self.src)

    def test_stationary_without_own_record_goes_to_fail(self):
        # stationary_unmeasured должен попадать в _fail, а не только в отчёт.
        self.assertIn("stationary_unmeasured", self.src)
        self.assertIn("стационарных файлов без своей записи", self.src)
        self.assertIn("baseline(M) — норма недоказуема", self.src)
        self.assertIn("_fail.append", self.src)

    def test_green_line_only_when_no_failures(self):
        # Зелёная строка — только при отсутствии ВСЕХ провалов.
        self.assertIn("not stationary_unmeasured", self.src)


class BaselineMasterLoadTests(unittest.TestCase):
    """Реальное поведение _baseline_master() наissing/битом JSON."""

    def setUp(self):
        self.mod = load_crest_master()
        self.real_path = self.mod.BASELINE_MASTER

    def _run_with_path(self, path):
        self.mod.BASELINE_MASTER = path
        self.mod._BM = None
        try:
            return self.mod._baseline_master()
        finally:
            self.mod.BASELINE_MASTER = self.real_path
            self.mod._BM = None

    def test_valid_json_loads_records(self):
        bm = self._run_with_path(self.real_path)
        self.assertNotIn("__error__", bm)
        stat = [r for r in bm.values() if r.get("type") == "стац"]
        self.assertGreaterEqual(len(stat), 1)
        self.assertTrue(all("baseline" in r for r in stat))

    def test_missing_json_is_error(self):
        bm = self._run_with_path("/nonexistent/baseline_master.json")
        self.assertIn("__error__", bm)
        self.assertIn("FileNotFoundError", bm["__error__"])

    def test_corrupt_json_is_error(self):
        fd, tmp = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write("{ невалидный json %%")
            bm = self._run_with_path(tmp)
            self.assertIn("__error__", bm)
        finally:
            os.unlink(tmp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
