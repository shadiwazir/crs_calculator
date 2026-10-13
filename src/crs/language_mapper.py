"""Convert raw language test scores into CLB (English) / NCLC (French) levels."""
from dataclasses import dataclass

from . import tables
from .engine import lookup_band

BELOW_CLB_4 = 0  # internal level for results under CLB/NCLC 4 (displayed "<4")


class InvalidScoreError(ValueError):
    pass


@dataclass(frozen=True)
class LanguageResult:
    """Per-ability CLB/NCLC levels from one language test."""
    test: str
    language: str  # "english" | "french"
    levels: dict   # ability -> int level (0 means below CLB 4, 10 means "10 or more")

    @property
    def minimum(self) -> int:
        return min(self.levels.values())


def validate_score(test: str, ability: str, score: float) -> None:
    low, high = tables.SCORE_RANGES[test][ability]
    step = tables.SCORE_STEP[test]
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise InvalidScoreError(f"{ability} score must be a number")
    if not low <= score <= high:
        raise InvalidScoreError(f"{tables.TEST_LABELS[test]} {ability} must be between {low} and {high}")
    if (score / step) != int(score / step):
        raise InvalidScoreError(f"{tables.TEST_LABELS[test]} {ability} must be in steps of {step}")


def to_level(test: str, ability: str, score: float) -> int:
    """Map one raw score to its CLB/NCLC level (floor-threshold rule)."""
    bands = [(0, BELOW_CLB_4)] + tables.CONVERSION[test][ability]
    return lookup_band(bands, score)


def map_scores(test: str, scores: dict) -> LanguageResult:
    """Validate and convert ``scores`` (ability -> raw score) for ``test``."""
    if test not in tables.CONVERSION:
        raise InvalidScoreError(f"Unknown language test: {test!r}")
    missing = [a for a in tables.ABILITIES if a not in scores]
    if missing:
        raise InvalidScoreError(f"Missing scores: {', '.join(missing)}")
    levels = {}
    for ability in tables.ABILITIES:
        validate_score(test, ability, scores[ability])
        levels[ability] = to_level(test, ability, scores[ability])
    return LanguageResult(test, tables.TEST_LANGUAGE[test], levels)
