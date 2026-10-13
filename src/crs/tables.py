"""Declarative CRS rule data (source: IRCC CRS criteria page, see REQUIREMENTS_ANALYSIS.md).

Band lists are ``[(minimum, value), ...]`` in ascending order of minimum; see engine.lookup_band.
Columns are keyed "couple" (scored with spouse) or "single" (scored without).
"""

# --- Section A: core / human capital ---------------------------------------------------------

AGE_BANDS = {
    "couple": [(0, 0), (18, 90), (19, 95), (20, 100), (30, 95), (31, 90), (32, 85), (33, 80),
               (34, 75), (35, 70), (36, 65), (37, 60), (38, 55), (39, 50), (40, 45), (41, 35),
               (42, 25), (43, 15), (44, 5), (45, 0)],
    "single": [(0, 0), (18, 99), (19, 105), (20, 110), (30, 105), (31, 99), (32, 94), (33, 88),
               (34, 83), (35, 77), (36, 72), (37, 66), (38, 61), (39, 55), (40, 50), (41, 39),
               (42, 28), (43, 17), (44, 6), (45, 0)],
}

# Education keys, ordered lowest to highest.
EDUCATION_LEVELS = ["none", "secondary", "one_year", "two_year", "bachelor",
                    "two_or_more", "master", "doctoral"]

EDUCATION_POINTS = {
    "couple": {"none": 0, "secondary": 28, "one_year": 84, "two_year": 91, "bachelor": 112,
               "two_or_more": 119, "master": 126, "doctoral": 140},
    "single": {"none": 0, "secondary": 30, "one_year": 90, "two_year": 98, "bachelor": 120,
               "two_or_more": 128, "master": 135, "doctoral": 150},
}

# Per ability, keyed by CLB/NCLC level (0 = below CLB 4).
FIRST_LANGUAGE_BANDS = {
    "couple": [(0, 0), (4, 6), (6, 8), (7, 16), (8, 22), (9, 29), (10, 32)],
    "single": [(0, 0), (4, 6), (6, 9), (7, 17), (8, 23), (9, 31), (10, 34)],
}
SECOND_LANGUAGE_BANDS = [(0, 0), (5, 1), (7, 3), (9, 6)]
SECOND_LANGUAGE_CAP = {"couple": 22, "single": 24}

CANADIAN_WORK_BANDS = {
    "couple": [(0, 0), (1, 35), (2, 46), (3, 56), (4, 63), (5, 70)],
    "single": [(0, 0), (1, 40), (2, 53), (3, 64), (4, 72), (5, 80)],
}

# --- Section B: spouse / common-law partner --------------------------------------------------

SPOUSE_EDUCATION_POINTS = {"none": 0, "secondary": 2, "one_year": 6, "two_year": 7, "bachelor": 8,
                           "two_or_more": 9, "master": 10, "doctoral": 10}
SPOUSE_LANGUAGE_BANDS = [(0, 0), (5, 1), (7, 3), (9, 5)]  # per ability
SPOUSE_CANADIAN_WORK_BANDS = [(0, 0), (1, 5), (2, 7), (3, 8), (4, 9), (5, 10)]

# --- Section C: skill transferability --------------------------------------------------------

TRANSFER_GROUP_CAP = 50
TRANSFER_TOTAL_CAP = 100

# Education level -> tier. "post_secondary" = credential of one year or longer;
# "high" = two or more credentials (one 3+ years), master's/professional, doctoral.
EDUCATION_TIER = {"none": "none", "secondary": "none", "one_year": "post_secondary",
                  "two_year": "post_secondary", "bachelor": "post_secondary",
                  "two_or_more": "high", "master": "high", "doctoral": "high"}
# Foreign work years -> tier (same point scale as education tiers).
FOREIGN_WORK_TIER_BANDS = [(0, "none"), (1, "post_secondary"), (3, "high")]
# Tier -> (points at strength level 1, points at strength level 2).
TRANSFER_TIER_POINTS = {"none": (0, 0), "post_secondary": (13, 25), "high": (25, 50)}
# Strength levels (0 none, 1 partial, 2 full) from first-language CLB or Canadian work years.
TRANSFER_LANGUAGE_LEVEL_BANDS = [(0, 0), (7, 1), (9, 2)]
TRANSFER_CANADIAN_WORK_LEVEL_BANDS = [(0, 0), (1, 1), (2, 2)]
# Certificate of qualification: strength from first-language CLB -> points.
CERTIFICATE_LANGUAGE_LEVEL_BANDS = [(0, 0), (5, 1), (7, 2)]
CERTIFICATE_POINTS = (25, 50)

# --- Section D: additional points ------------------------------------------------------------

ADDITIONAL_CAP = 600
SIBLING_POINTS = 15
PROVINCIAL_NOMINATION_POINTS = 600
CANADIAN_STUDY_POINTS = {"none": 0, "one_two_year": 15, "three_plus": 30}
FRENCH_BONUS_MIN_NCLC = 7
FRENCH_BONUS_POINTS = {"english_below_5": 25, "english_5_plus": 50}
FRENCH_BONUS_ENGLISH_THRESHOLD = 5

# --- Language test conversion (IRCC "Language test results" page) -----------------------------
# Abilities ordered: speaking, listening, reading, writing.
# Each entry: ability -> [(minimum raw score, CLB/NCLC level), ...] ascending; level 10 = "10 or more".

ABILITIES = ("speaking", "listening", "reading", "writing")

TEST_LANGUAGE = {"celpip": "english", "ielts": "english", "pte": "english",
                 "tef": "french", "tcf": "french"}

TEST_LABELS = {"celpip": "CELPIP-General", "ielts": "IELTS General Training", "pte": "PTE Core",
               "tef": "TEF Canada", "tcf": "TCF Canada"}


def _rows(rows):
    """Turn [(level, speaking, listening, reading, writing), ...] into per-ability bands."""
    return {ability: sorted((row[i + 1], row[0]) for row in rows)
            for i, ability in enumerate(ABILITIES)}


CONVERSION = {
    "celpip": {a: [(lvl, lvl) for lvl in range(4, 11)] for a in ABILITIES},
    "ielts": _rows([(10, 7.5, 8.5, 8.0, 7.5), (9, 7.0, 8.0, 7.0, 7.0), (8, 6.5, 7.5, 6.5, 6.5),
                    (7, 6.0, 6.0, 6.0, 6.0), (6, 5.5, 5.5, 5.0, 5.5), (5, 5.0, 5.0, 4.0, 5.0),
                    (4, 4.0, 4.5, 3.5, 4.0)]),
    "pte": _rows([(10, 89, 89, 88, 90), (9, 84, 82, 78, 88), (8, 76, 71, 69, 79),
                  (7, 68, 60, 60, 69), (6, 59, 50, 51, 60), (5, 51, 39, 42, 51),
                  (4, 42, 28, 33, 41)]),
    "tef": _rows([(10, 393, 316, 263, 393), (9, 371, 298, 248, 371), (8, 349, 280, 233, 349),
                  (7, 310, 249, 207, 310), (6, 271, 217, 181, 271), (5, 226, 181, 151, 226),
                  (4, 181, 145, 121, 181)]),
    "tcf": _rows([(10, 16, 549, 549, 16), (9, 14, 523, 524, 14), (8, 12, 503, 499, 12),
                  (7, 10, 458, 453, 10), (6, 7, 398, 406, 7), (5, 6, 369, 375, 6),
                  (4, 4, 331, 342, 4)]),
}

# Valid input range per ability (min, max); step is 0.5 for IELTS and 1 otherwise.
SCORE_RANGES = {
    "celpip": {a: (0, 12) for a in ABILITIES},
    "ielts": {a: (0, 9) for a in ABILITIES},
    "pte": {a: (0, 90) for a in ABILITIES},
    "tef": {"speaking": (0, 450), "listening": (0, 360), "reading": (0, 300), "writing": (0, 450)},
    "tcf": {"speaking": (0, 20), "listening": (0, 699), "reading": (0, 699), "writing": (0, 20)},
}
SCORE_STEP = {"celpip": 1, "ielts": 0.5, "pte": 1, "tef": 1, "tcf": 1}
