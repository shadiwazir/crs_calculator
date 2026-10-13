"""Section A: core / human capital factors."""
from .. import tables
from ..engine import lookup_band
from ..models import Profile


def score_core(profile: Profile) -> dict:
    col = profile.scoring_column
    first = sum(lookup_band(tables.FIRST_LANGUAGE_BANDS[col], lvl)
                for lvl in profile.first_language.levels.values())
    second = 0
    if profile.second_language:
        second = min(sum(lookup_band(tables.SECOND_LANGUAGE_BANDS, lvl)
                         for lvl in profile.second_language.levels.values()),
                     tables.SECOND_LANGUAGE_CAP[col])
    return {
        "age": lookup_band(tables.AGE_BANDS[col], profile.age),
        "education": tables.EDUCATION_POINTS[col][profile.education],
        "first_language": first,
        "second_language": second,
        "canadian_work": lookup_band(tables.CANADIAN_WORK_BANDS[col], profile.canadian_work_years),
    }
