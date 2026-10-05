import importlib.util
from pathlib import Path
import subprocess
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("profile_check", ROOT / "scripts/check-installed-profile.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class InstalledProfileTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        for target, source in checker.FILES.items():
            path = self.project / target
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / source).read_bytes())
        (self.project / "CLAUDE.md").symlink_to("AGENTS.md")

    def test_current_profile_and_windows_line_endings(self):
        self.assertEqual(checker.inspect(self.project)["result"], "CURRENT")
        for target in checker.FILES:
            path = self.project / target
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(checker.inspect(self.project)["result"], "CURRENT")

    def test_original_missing_consumer_guidance_is_detected(self):
        path = self.project / "AGENTS.md"
        path.write_text(path.read_text().split(checker.HEADING)[0])
        report = checker.inspect(self.project)
        self.assertEqual(report["files"][0]["integration_section"], "missing_or_ambiguous")
        self.assertEqual(report["result"], "REVIEW_REQUIRED")

    def test_reapplication_preserves_custom_work_and_exposes_skip(self):
        path = self.project / "AGENTS.md"
        path.write_text("# Local project rules\nDo not deploy the sandbox.\n")
        before = path.read_bytes()
        result = subprocess.run(["sh", str(ROOT / "integrations/dockit/apply-profile.sh"), str(self.project)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("REVIEW_REQUIRED", result.stdout)
        self.assertEqual(path.read_bytes(), before)

    def test_source_archive_report_failure_does_not_fail_profile_application(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / "protocol"
            shutil.copytree(ROOT / "integrations", archive / "integrations")
            shutil.copytree(ROOT / "schemas", archive / "schemas")
            shutil.copyfile(ROOT / "VERSION", archive / "VERSION")
            (archive / "scripts").mkdir()
            shutil.copyfile(ROOT / "scripts/check-installed-profile.py", archive / "scripts/check-installed-profile.py")
            shutil.copy2(ROOT / "scripts/validate-project-interface.py", archive / "scripts/validate-project-interface.py")
            target = Path(folder) / "adopter"
            target.mkdir()
            result = subprocess.run(["sh", str(archive / "integrations/dockit/apply-profile.sh"), str(target)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guidance report unavailable", result.stderr)
            self.assertEqual((target / "AGENTS.md").read_bytes(), (ROOT / checker.FILES["AGENTS.md"]).read_bytes())

    def test_standalone_claude_file_is_a_visible_adoption_gap(self):
        (self.project / "CLAUDE.md").unlink()
        (self.project / "CLAUDE.md").write_text("# Local client instructions\n")
        (self.project / "AGENTS.md").unlink()
        result = checker.inspect(self.project)
        self.assertEqual(result["claude_alias"], "standalone_file")
        self.assertEqual(result["result"], "REVIEW_REQUIRED")

    def test_missing_canonical_section_is_a_controlled_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            profile = Path(folder)
            for source in checker.FILES.values():
                path = profile / source
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text((ROOT / source).read_text().replace("## Mandatory updates", "## Renamed updates"))
            with self.assertRaisesRegex(ValueError, "canonical required section"):
                checker.inspect(self.project, profile, published_history=False)

    def test_customization_is_not_declared_obsolete(self):
        path = self.project / "AGENTS.md"
        path.write_text("# Project-specific instruction\n\n" + path.read_text())
        row = checker.inspect(self.project)["files"][0]
        self.assertEqual(row["state"], "customized")
        self.assertEqual(row["integration_section"], "current")

    def test_duplicate_section_and_changed_requirement(self):
        path = self.project / "AGENTS.md"
        path.write_text(path.read_text() + "\n" + checker.HEADING + "\nOmit consumers.\n")
        self.assertEqual(checker.inspect(self.project)["files"][0]["integration_section"], "missing_or_ambiguous")

    def test_missing_and_external_link_are_not_current(self):
        path = self.project / "AGENTS.md"
        path.unlink()
        self.assertEqual(checker.inspect(self.project)["files"][0]["state"], "missing")
        path.symlink_to(ROOT / checker.FILES["AGENTS.md"])
        self.assertEqual(checker.inspect(self.project)["files"][0]["state"], "unverified")

    def test_divergent_claude_instructions_are_reported(self):
        path = self.project / "CLAUDE.md"
        path.unlink()
        path.write_text("Use the older deployment route.\n")
        self.assertEqual(checker.inspect(self.project)["claude_alias"], "different_copy")

    def test_completed_checkboxes_do_not_imply_stale_instructions(self):
        path = self.project / ".claude/checklists/homelab-project.md"
        path.write_text(path.read_text().replace("[ ]", "[x]"))
        self.assertEqual(checker.inspect(self.project)["result"], "CURRENT")

    def test_materialized_symlink_is_a_separate_client_caveat(self):
        path = self.project / "CLAUDE.md"
        path.unlink()
        path.write_text("AGENTS.md")
        self.assertEqual(checker.inspect(self.project)["claude_alias"], "symlink_materialized")

    def test_retired_conditional_is_detected_inside_custom_text(self):
        path = self.project / "AGENTS.md"
        path.write_text(path.read_text() + "\nRegister only if the service is\nportal-visible.\n")
        self.assertIn("portal_visible_conditional", checker.inspect(self.project)["files"][0]["retired_guidance"])

    def test_no_profile_is_not_adoption(self):
        for target in [*checker.FILES, "CLAUDE.md"]:
            (self.project / target).unlink()
        self.assertEqual(checker.inspect(self.project)["result"], "NOT_ADOPTED")

    def test_report_preserves_content_and_timestamps(self):
        files = [self.project / p for p in checker.FILES]
        before = [(p.read_bytes(), p.stat().st_mtime_ns) for p in files]
        checker.inspect(self.project)
        self.assertEqual(before, [(p.read_bytes(), p.stat().st_mtime_ns) for p in files])

    def test_published_historical_template_has_attributed_stale_state(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def git(*args):
                subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
            git("init", "-b", "main")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            for target, source in checker.FILES.items():
                path = root / source
                path.parent.mkdir(parents=True, exist_ok=True)
                data = (ROOT / source).read_text().split(checker.HEADING)[0]
                path.write_text(data)
                (self.project / target).write_text(data)
            (root / "VERSION").write_text("0.1.0\n")
            git("add", ".")
            git("commit", "-m", "Historical profile")
            git("update-ref", "refs/remotes/origin/main", "HEAD")
            for source in checker.FILES.values():
                (root / source).write_bytes((ROOT / source).read_bytes())
            row = checker.inspect(self.project, root)["files"][0]
            self.assertEqual(row["state"], "pristine_stale")
            self.assertEqual(row["historical_match"]["version"], "0.1.0")


if __name__ == "__main__":
    unittest.main()
