import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "integrations/dockit/INTEGRATION.md"
CHECKLIST = ROOT / "integrations/dockit/checklists/PROJECT_CHECKLIST.md"
AGENTS_TEMPLATE = ROOT / "integrations/dockit/templates/AGENTS.md"


class DockitProfileIntegrationTest(unittest.TestCase):
    def test_interface_and_delivery_skills_have_distinct_boundaries(self) -> None:
        text = INTEGRATION.read_text(encoding="utf-8")
        interface = text.index("skills/implement-home-infra-interface/SKILL.md")
        delivery = text.index("skills/ship-homelab-app/SKILL.md")
        self.assertLess(interface, delivery)
        self.assertIn(
            "stops before Home Infra or runtime mutation", " ".join(text.split())
        )

    def test_checklist_publishes_sources_before_apply_and_portal_sync(self) -> None:
        text = CHECKLIST.read_text(encoding="utf-8")
        published = text.index("committed and pushed before DNS")
        apply_edge = text.index("scripts/edge-caddy-config --apply")
        sync_portal = text.index("scripts/sync-portal-inputs-to-nas.sh")
        self.assertLess(published, apply_edge)
        self.assertLess(published, sync_portal)

    def test_profile_uses_current_control_plane_authorities(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (INTEGRATION, CHECKLIST, AGENTS_TEMPLATE)
        )
        self.assertIn("docs/PROJECTS.yml", text)
        self.assertIn("catalog/project-acceptances.yml", text)
        self.assertIn("scripts/edge-caddy-config", text)
        self.assertIn("scripts/sync-portal-inputs-to-nas.sh", text)
        self.assertNotIn("sync-catalog-to-nas.sh", text)
        self.assertNotIn(
            "/share/Container/compose/edge-caddy/docker-compose.yml", text
        )
        self.assertNotIn("restart edge-caddy", text)


if __name__ == "__main__":
    unittest.main()
