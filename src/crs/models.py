"""Input model for a CRS calculation, with validation."""
from dataclasses import dataclass
from typing import Optional

from . import tables
from .language_mapper import LanguageResult

MAX_AGE = 100
MIN_AGE = 17
MAX_WORK_YEARS = 5  # "5 years or more" is the highest band
CANADIAN_STUDY_LEVELS = tuple(tables.CANADIAN_STUDY_POINTS)


class ValidationError(ValueError):
    pass


def _check_choice(name: str, value: str, choices) -> None:
    if value not in choices:
        raise ValidationError(f"{name} must be one of {', '.join(choices)}")


def _check_years(name: str, value: int, maximum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum:
        raise ValidationError(f"{name} must be a whole number from 0 to {maximum}")


@dataclass(frozen=True)
class SpouseProfile:
    """Accompanying spouse / common-law partner (not a citizen/PR)."""
    education: str = "none"
    canadian_work_years: int = 0
    language: Optional[LanguageResult] = None  # None = no official language test

    def __post_init__(self):
        _check_choice("spouse education", self.education, tables.EDUCATION_LEVELS)
        _check_years("spouse Canadian work years", self.canadian_work_years, MAX_WORK_YEARS)


@dataclass(frozen=True)
class Profile:
    """A candidate. ``spouse`` is set only when scored as a couple (spouse is accompanying)."""
    age: int
    education: str
    first_language: LanguageResult
    second_language: Optional[LanguageResult] = None
    canadian_work_years: int = 0
    foreign_work_years: int = 0
    has_certificate_of_qualification: bool = False
    has_provincial_nomination: bool = False
    has_sibling_in_canada: bool = False
    canadian_study: str = "none"
    spouse: Optional[SpouseProfile] = None

    def __post_init__(self):
        if isinstance(self.age, bool) or not isinstance(self.age, int) or not MIN_AGE <= self.age <= MAX_AGE:
            raise ValidationError(f"age must be a whole number from {MIN_AGE} to {MAX_AGE}")
        _check_choice("education", self.education, tables.EDUCATION_LEVELS)
        _check_choice("canadian_study", self.canadian_study, CANADIAN_STUDY_LEVELS)
        _check_years("Canadian work years", self.canadian_work_years, MAX_WORK_YEARS)
        _check_years("foreign work years", self.foreign_work_years, 3)
        if self.second_language and self.second_language.language == self.first_language.language:
            raise ValidationError("first and second official language tests must be in different languages")

    @property
    def scoring_column(self) -> str:
        return "couple" if self.spouse else "single"


def resolve_couple(marital_status: str, spouse_is_citizen_or_pr: bool, spouse_accompanying: bool) -> bool:
    """True when the candidate is scored with a spouse (spouse must be coming and not a citizen/PR)."""
    if marital_status not in ("married", "common_law"):
        return False
    return spouse_accompanying and not spouse_is_citizen_or_pr
