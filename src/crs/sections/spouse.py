"""Section B: spouse / common-law partner factors (only when scored as a couple)."""
from .. import tables
from ..engine import lookup_band
from ..models import Profile


def score_spouse(profile: Profile) -> dict:
    spouse = profile.spouse
    if spouse is None:
        return {"education": 0, "language": 0, "canadian_work": 0}
    language = 0
    if spouse.language:
        language = sum(lookup_band(tables.SPOUSE_LANGUAGE_BANDS, lvl)
                       for lvl in spouse.language.levels.values())
    return {
        "education": tables.SPOUSE_EDUCATION_POINTS[spouse.education],
        "language": language,
        "canadian_work": lookup_band(tables.SPOUSE_CANADIAN_WORK_BANDS, spouse.canadian_work_years),
    }
