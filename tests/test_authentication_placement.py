import json
import unittest
from pathlib import Path

import yaml
from jsonschema import ValidationError, validate


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/services.schema.json").read_text())


def catalog(mode: str) -> dict:
    return {
        "services": [
            {
                "id": "example-service",
                "name": "Example Service",
                "category": "tools",
                "url": "https://service.example.internal/",
                "exposure": {"authentication": {"mode": mode}},
            }
        ]
    }


class AuthenticationPlacementSchemaTest(unittest.TestCase):
    def test_accepts_all_portable_modes(self) -> None:
        for mode in ("none", "application", "proxy"):
            with self.subTest(mode=mode):
                validate(catalog(mode), SCHEMA)

    def test_rejects_provider_or_unknown_mode(self) -> None:
        with self.assertRaises(ValidationError):
            validate(catalog("better-auth"), SCHEMA)

    def test_sanitized_services_example_validates(self) -> None:
        example = yaml.safe_load(
            (ROOT / "examples/home-infra/catalog/services.yml").read_text()
        )
        validate(example, SCHEMA)


if __name__ == "__main__":
    unittest.main()
