"""
Reinheitsgebot 1516 Statutory Compliance & Linter Engine
The Bavarian Beer Purity Law (Ingolstadt, 23 April 1516) as Executable Code.
Part of the Grow with Google Enterprise Craft Suite.
"""

from __future__ import annotations
import os
import sys
import json
import hashlib
import datetime
from typing import Dict, Any, List

CANONICAL_ALLOWLIST = {
    "water": ["water", "h2o", "artesian_water", "spring_water", "reverse_osmosis", "mineral_water"],
    "grain": ["malted_barley", "barley_malt", "pilsner_malt", "two_row", "six_row", "roasted_barley", "carafa", "malted_wheat"],
    "hops": ["hops", "hop_pellets", "whole_leaf_hops", "cryo_hops", "hallertau", "tettnanger", "saaz", "willamette", "cascade", "citra"],
    "yeast": ["yeast", "saccharomyces_cerevisiae", "saccharomyces_pastorianus", "lager_yeast", "ale_yeast", "wild_yeast"]
}

ILLEGAL_ADJUNCTS_DENYLIST = [
    "corn_syrup", "high_fructose_corn_syrup", "rice_extract", "sorbitol",
    "propylene_glycol", "artificial_coloring", "caramel_color", "sodium_benzoate",
    "potassium_sorbate", "isinglass_synthetic", "belladonna", "henbane", "soot", "chalk"
]

class StatutoryViolationError(Exception):
    """Raised when a recipe violates the Bavarian Landordnung of 1516."""
    pass

class ReinheitsgebotAuditor:
    def __init__(self, statute_year: int = 1516):
        self.statute_year = statute_year
        self.jurisdiction = "Bavarian Landordnung (Ingolstadt, 23 April 1516)"

    def audit_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        batch_name = recipe_data.get("recipe_name", "Unknown Brew")
        ingredients = recipe_data.get("ingredients", [])
        violations: List[str] = []

        # 1. Denylist Check
        for ing in ingredients:
            ing_slug = ing.lower().replace(" ", "_").replace("-", "_")
            for denied in ILLEGAL_ADJUNCTS_DENYLIST:
                if denied in ing_slug:
                    violations.append(f"CRIMINAL ADULTERATION: Prohibited adjunct detected -> '{ing}'")

        # 2. Allowlist Check
        for ing in ingredients:
            ing_slug = ing.lower().replace(" ", "_").replace("-", "_")
            matched = any(any(p in ing_slug for p in permitted) for permitted in CANONICAL_ALLOWLIST.values())
            if not matched and not any(d in ing_slug for d in ILLEGAL_ADJUNCTS_DENYLIST):
                violations.append(f"STATUTORY BREACH: Uncertified ingredient not permitted under 1516 law -> '{ing}'")

        is_pure = len(violations) == 0
        purity_score = 100.0 if is_pure else max(0.0, 100.0 - (len(violations) * 35.0))
        timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sig = hashlib.sha256(f"{batch_name}:{purity_score}:{timestamp_str}:{is_pure}".encode()).hexdigest()

        return {
            "recipe_name": batch_name,
            "statute": self.jurisdiction,
            "purity_score_percent": purity_score,
            "is_reinheitsgebot_compliant": is_pure,
            "timestamp_utc": timestamp_str,
            "cryptographic_seal": sig,
            "audited_ingredients": ingredients,
            "statutory_violations": violations,
            "verdict": "100% PURE — CERTIFIED REINHEITSGEBOT COMPLIANT" if is_pure else "REJECTED — STATUTORY ADULTERATION"
        }

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
    else:
        data = {
            "recipe_name": "PageRank Pilsner",
            "ingredients": ["Reverse Osmosis Water", "Pilsner Malted Barley", "Hallertau Hops", "German Lager Yeast"]
        }
    auditor = ReinheitsgebotAuditor()
    cert = auditor.audit_recipe(data)
    print(json.dumps(cert, indent=2))
