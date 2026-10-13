"""Section C: skill transferability factors."""
from .. import tables
from ..engine import lookup_band
from ..models import Profile


def _combined(tier: str, language_level: int, canadian_work_level: int) -> int:
    """Points for a tier combined with a language strength and a Canadian-work strength."""
    partial, full = tables.TRANSFER_TIER_POINTS[tier]
    by_level = (0, partial, full)
    return min(by_level[language_level] + by_level[canadian_work_level], tables.TRANSFER_GROUP_CAP)


def score_transferability(profile: Profile) -> dict:
    clb = profile.first_language.minimum
    lang_level = lookup_band(tables.TRANSFER_LANGUAGE_LEVEL_BANDS, clb)
    cwe_level = lookup_band(tables.TRANSFER_CANADIAN_WORK_LEVEL_BANDS, profile.canadian_work_years)

    education = _combined(tables.EDUCATION_TIER[profile.education], lang_level, cwe_level)
    foreign_tier = lookup_band(tables.FOREIGN_WORK_TIER_BANDS, profile.foreign_work_years)
    foreign = _combined(foreign_tier, lang_level, cwe_level)

    certificate = 0
    if profile.has_certificate_of_qualification:
        cert_level = lookup_band(tables.CERTIFICATE_LANGUAGE_LEVEL_BANDS, clb)
        certificate = min((0, *tables.CERTIFICATE_POINTS)[cert_level], tables.TRANSFER_GROUP_CAP)

    return {"education": education, "foreign_work": foreign, "certificate": certificate}
