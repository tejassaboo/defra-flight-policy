"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "defra" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 24-scenario row).
MIX = {"easy": 5, "boundary_twin": 6, "multi_rule": 4, "hidden_clause": 2, "distractor": 2, "refusal": 2, "flag": 3}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has. It has no rule on several
# travellers on one flight and none on overnight stops, so neither overlay is required.
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "date_arithmetic": 2, "month_end": 1, "personal_travel": 1,
    "dearer_option": 2, "upgrade_not_taken": 2, "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "mainland", "england", "wales", "scotland", "scottish", "domestic", "rail", "train", "eurostar", "director",
    "manager", "approver", "budget", "medical", "disability", "health", "safety", "safe", "unsafe", "leave",
    "holiday", "personal", "wedding", "economy", "business", "first", "premium", "journey", "arrival", "work",
    "seat", "seats", "fare", "lowest", "practical", "sustainability", "carbon", "foreign", "overseas", "akin",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.Purpose, contract.SignOffSubject, contract.Outcome]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section).
MAX_PASS_ALWAYS_FLAG = 2
MAX_PASS_ALWAYS_LOWEST = 6

# Hand-built duration cases beyond the automatic both-sides tests: (rule, outbound scheduled minutes per
# flight, layovers, expected True / False / None for unclear).
DURATION_CASES = [
    ("economy-only", [300], [], True),  # exactly 5 hours is not "less than 5 hours"
    ("economy-only", [299], [], False),
    ("economy-only", [150, 140], [60], None),  # flying 290, elapsed 350: the readings differ
    ("economy-only", [100, 90], [70], False),  # flying 190, elapsed 260: under on both readings
    ("economy-only", [105, 100], [115], None),  # flying 205, elapsed 320: the readings differ
    ("economy-only", [200, 150], [60], True),  # flying 350: 5 hours or more on both readings
    ("ten-hours", [601], [], True),
    ("ten-hours", [600], [], False),  # exactly 10 hours is not "over 10 hours"
    ("ten-hours", [425, 450], [140], True),  # flying 875: over on both readings
    ("ten-hours", [300, 250], [60], None),  # flying 550, elapsed 610: the readings differ
    ("ten-hours", [250, 200], [60], False),  # flying 450, elapsed 510: within on both readings
]
