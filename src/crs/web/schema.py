"""Translate the JSON request body into a validated ``Profile``."""
from .. import tables
from ..language_mapper import InvalidScoreError, LanguageResult, map_scores
from ..models import Profile, SpouseProfile, ValidationError, resolve_couple

MARITAL_STATUSES = ("single", "married", "common_law", "divorced", "legally_separated",
                    "annulled", "widowed")


def _language(data) -> LanguageResult | None:
    if not data:
        return None
    try:
        return map_scores(data.get("test"), data.get("scores") or {})
    except InvalidScoreError as exc:
        raise ValidationError(str(exc)) from exc


def _spouse(data) -> SpouseProfile:
    data = data or {}
    return SpouseProfile(education=data.get("education", "none"),
                         canadian_work_years=data.get("canadian_work_years", 0),
                         language=_language(data.get("language")))


def parse_profile(body: dict) -> Profile:
    if not isinstance(body, dict):
        raise ValidationError("request body must be a JSON object")
    status = body.get("marital_status", "single")
    if status not in MARITAL_STATUSES:
        raise ValidationError(f"marital_status must be one of {', '.join(MARITAL_STATUSES)}")
    couple = resolve_couple(status, bool(body.get("spouse_is_citizen_or_pr")),
                            bool(body.get("spouse_accompanying")))
    first = _language(body.get("first_language"))
    if first is None:
        raise ValidationError("first_language test results are required")
    return Profile(
        age=body.get("age"),
        education=body.get("education"),
        first_language=first,
        second_language=_language(body.get("second_language")),
        canadian_work_years=body.get("canadian_work_years", 0),
        foreign_work_years=body.get("foreign_work_years", 0),
        has_certificate_of_qualification=bool(body.get("has_certificate_of_qualification")),
        has_provincial_nomination=bool(body.get("has_provincial_nomination")),
        has_sibling_in_canada=bool(body.get("has_sibling_in_canada")),
        canadian_study=body.get("canadian_study", "none"),
        spouse=_spouse(body.get("spouse")) if couple else None,
    )


def test_options() -> dict:
    return {test: {"label": tables.TEST_LABELS[test], "language": tables.TEST_LANGUAGE[test],
                   "step": tables.SCORE_STEP[test],
                   "ranges": {a: list(r) for a, r in tables.SCORE_RANGES[test].items()}}
            for test in tables.CONVERSION}
