import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/services.schema.json").read_text())
BASE = {"services": [{"id": "example", "name": "Example", "category": "tools", "url": "https://example.invalid"}]}


class ServiceIconTest(unittest.TestCase):
    def errors(self, value):
        catalog = copy.deepcopy(BASE)
        catalog["services"][0]["icon"] = value
        return list(Draft202012Validator(SCHEMA).iter_errors(catalog))

    def test_optional_and_open_vocabulary(self):
        self.assertEqual(list(Draft202012Validator(SCHEMA).iter_errors(BASE)), [])
        for value in ("portal", "home-assistant", "unknown-vendor-2026", "x" * 32, "constructor"):
            with self.subTest(value=value):
                self.assertEqual(self.errors(value), [])

    def test_rejects_markup_paths_urls_and_malformed_tokens(self):
        for value in (None, True, 7, {}, [], "", "<svg>", "https://example.invalid/a.svg", "data:image/svg+xml,test", "../icon", "UPPER", "x_1", "x--y", "-x", "x-", "x\n", "x" * 33, "__proto__"):
            with self.subTest(value=value):
                self.assertTrue(self.errors(value))


if __name__ == "__main__":
    unittest.main()
