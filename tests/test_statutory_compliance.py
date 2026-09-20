import unittest
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from reinheitsgebot_auditor import ReinheitsgebotAuditor

class TestReinheitsgebotCompliance(unittest.TestCase):
    def setUp(self):
        self.auditor = ReinheitsgebotAuditor()
        self.recipes_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "recipes"))

    def test_pagerank_pilsner_passes_purity(self):
        with open(os.path.join(self.recipes_dir, "pagerank_pilsner.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        cert = self.auditor.audit_recipe(data)
        self.assertTrue(cert["is_reinheitsgebot_compliant"])
        self.assertEqual(cert["purity_score_percent"], 100.0)
        self.assertIn("100% PURE", cert["verdict"])
        self.assertEqual(len(cert["statutory_violations"]), 0)

    def test_spotted_googler_passes_purity(self):
        with open(os.path.join(self.recipes_dir, "spotted_googler.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        cert = self.auditor.audit_recipe(data)
        self.assertTrue(cert["is_reinheitsgebot_compliant"])
        self.assertEqual(cert["purity_score_percent"], 100.0)

    def test_adulterated_batch_fails_statutory_ci(self):
        with open(os.path.join(self.recipes_dir, "adulterated_macro_lager.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        cert = self.auditor.audit_recipe(data)
        self.assertFalse(cert["is_reinheitsgebot_compliant"])
        self.assertLess(cert["purity_score_percent"], 50.0)
        self.assertIn("REJECTED", cert["verdict"])
        # Ensure corn syrup, rice extract, propylene glycol, etc. were caught
        violation_text = " ".join(cert["statutory_violations"])
        self.assertIn("High Fructose Corn Syrup", violation_text)
        self.assertIn("Rice Extract", violation_text)
        self.assertIn("Propylene Glycol", violation_text)

if __name__ == "__main__":
    unittest.main()
