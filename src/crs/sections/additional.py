"""Section D: additional points."""
from .. import tables
from ..models import Profile


def french_bonus(profile: Profile) -> int:
    """25/50 when NCLC >= 7 on all four French abilities (English level decides which)."""
    tests = [t for t in (profile.first_language, profile.second_language) if t]
    french = next((t for t in tests if t.language == "french"), None)
    if french is None or french.minimum < tables.FRENCH_BONUS_MIN_NCLC:
        return 0
    english = next((t for t in tests if t.language == "english"), None)
    if english and english.minimum >= tables.FRENCH_BONUS_ENGLISH_THRESHOLD:
        return tables.FRENCH_BONUS_POINTS["english_5_plus"]
    return tables.FRENCH_BONUS_POINTS["english_below_5"]


def score_additional(profile: Profile) -> dict:
    return {
        "sibling": tables.SIBLING_POINTS if profile.has_sibling_in_canada else 0,
        "french": french_bonus(profile),
        "canadian_study": tables.CANADIAN_STUDY_POINTS[profile.canadian_study],
        "nomination": tables.PROVINCIAL_NOMINATION_POINTS if profile.has_provincial_nomination else 0,
    }
