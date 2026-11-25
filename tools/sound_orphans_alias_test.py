#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused regression tests for Z-G6 shared-resource alias handling.

Run: python3 tools/sound_orphans_alias_test.py
Uses only the Python standard library and does not read Git objects or audio files.
"""
import unittest

from sound_orphans import heard_elsewhere


class HeardElsewhereTests(unittest.TestCase):
    def test_all_dead_event_files_covered_by_other_live_event(self):
        dead = [("FLESH_AMALGAM_AMBIENT", "flesh_amalgam_ambient")]
        data = {
            "flesh_amalgam_ambient": {
                "sounds": ["carnis:entity/flesh_amalgam_ambient"]
            },
            "hive.amalgam_breath": {
                "sounds": ["carnis:entity/flesh_amalgam_ambient"]
            },
        }
        result = heard_elsewhere(dead, data, {}, set())
        self.assertEqual(
            result,
            {"FLESH_AMALGAM_AMBIENT": (
                "flesh_amalgam_ambient", "hive.amalgam_breath"
            )},
        )

    def test_partial_file_coverage_is_not_accepted_as_alias(self):
        dead = [("MULTI_SAMPLE_EVENT", "multi_sample_event")]
        data = {
            "multi_sample_event": {
                "sounds": ["carnis:a/covered", "carnis:a/uncovered"]
            },
            "live_alias": {"sounds": ["carnis:a/covered"]},
        }
        self.assertEqual(heard_elsewhere(dead, data, {}, set()), {})

    def test_event_does_not_cover_itself(self):
        dead = [("SELF_ONLY_EVENT", "self_only_event")]
        data = {
            "self_only_event": {"sounds": ["carnis:a/only"]},
        }
        self.assertEqual(heard_elsewhere(dead, data, {}, set()), {})

    def test_dead_event_without_resources_is_not_reported_as_heard(self):
        dead = [("EMPTY_EVENT", "empty_event")]
        data = {"empty_event": {"sounds": []}}
        self.assertEqual(heard_elsewhere(dead, data, {}, set()), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
