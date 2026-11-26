#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integration tests: only the explicit FLAMETHROWER_FIRE scaffold is exempt.

Run: python3 tools/sound_orphans_allowlist_test.py
Uses a tiny temporary fixture and the repository's real sound_orphans allowlist.
"""
import json
import subprocess
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHECKER = REPO / "tools" / "sound_orphans.py"
sys.path.insert(0, str(REPO / "tools"))
from sound_orphans import load_allowlist  # noqa: E402


class AllowlistBoundaryTests(unittest.TestCase):
    def make_fixture(self, root: Path, include_unplanned: bool) -> Path:
        package = root / "fixture"
        mod_sounds = package / "src/main/java/com/carnis/mod/init/ModSounds.java"
        mod_sounds.parent.mkdir(parents=True)
        mod_lines = [
            "package com.carnis.mod.init;",
            "import net.minecraft.sounds.SoundEvent;",
            "import net.minecraftforge.registries.RegistryObject;",
            "final class ModSounds {",
            '  RegistryObject<SoundEvent> FLAMETHROWER_FIRE = register("flamethrower_fire");',
        ]
        if include_unplanned:
            mod_lines.append(
                '  RegistryObject<SoundEvent> UNPLANNED_EVENT = register("unplanned_event");'
            )
        mod_lines.append("}")
        mod_sounds.write_text(chr(10).join(mod_lines) + chr(10), encoding="utf-8")
        assets = package / "src/main/resources/assets/carnis"
        (assets / "sounds").mkdir(parents=True)
        sounds = {
            "flamethrower_fire": {
                "sounds": ["carnis:entity/flamethrower_fire"]
            }
        }
        (assets / "sounds/entity").mkdir(parents=True)
        (assets / "sounds/entity/flamethrower_fire.ogg").write_bytes(b"fixture")
        if include_unplanned:
            sounds["unplanned_event"] = {
                "sounds": ["carnis:entity/unplanned_event"]
            }
            (assets / "sounds/entity/unplanned_event.ogg").write_bytes(b"fixture")
        (assets / "sounds.json").write_text(
            json.dumps(sounds), encoding="utf-8"
        )
        return package

    def run_checker(self, package: Path, no_allowlist: bool = False):
        command = [sys.executable, str(CHECKER), str(package), "--quiet"]
        if no_allowlist:
            command.append("--no-allowlist")
        return subprocess.run(
            command,
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_allowlist_contains_only_the_approved_scaffold(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            table = load_allowlist()
        self.assertIsNotNone(table)
        self.assertEqual(set(table), {"FLAMETHROWER_FIRE"})

    def test_explicit_scaffold_is_exempt(self):
        with tempfile.TemporaryDirectory(prefix="sound-allowlist-") as tmp:
            package = self.make_fixture(Path(tmp), include_unplanned=False)
            result = self.run_checker(package)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("FLAMETHROWER_FIRE", result.stdout)
        self.assertNotIn("UNPLANNED_EVENT", result.stdout)

    def test_no_allowlist_flag_exposes_the_scaffold_as_unreachable(self):
        with tempfile.TemporaryDirectory(prefix="sound-allowlist-") as tmp:
            package = self.make_fixture(Path(tmp), include_unplanned=False)
            result = self.run_checker(package, no_allowlist=True)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("FLAMETHROWER_FIRE", result.stdout)
        self.assertIn("недостижимых событий 1", result.stdout)

    def test_unlisted_unreachable_event_still_fails(self):
        with tempfile.TemporaryDirectory(prefix="sound-allowlist-") as tmp:
            package = self.make_fixture(Path(tmp), include_unplanned=True)
            result = self.run_checker(package)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("FLAMETHROWER_FIRE", result.stdout)
        self.assertIn("UNPLANNED_EVENT", result.stdout)
        self.assertIn("недостижимых событий 1", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
