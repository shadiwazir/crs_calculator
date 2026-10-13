import pytest

from crs.language_mapper import LanguageResult
from crs.sections.additional import french_bonus, score_additional
from helpers import lang, profile


def mixed(language, **levels):
    base = dict(speaking=0, listening=0, reading=0, writing=0)
    base.update(levels)
    return LanguageResult("x", language, base)


def test_french_50_when_english_5_plus():
    p = profile(first_language=lang(7, "french"), second_language=lang(5, "english"))
    assert french_bonus(p) == 50


def test_french_as_second_language():
    p = profile(first_language=lang(9, "english"), second_language=lang(7, "french"))
    assert french_bonus(p) == 50


def test_french_25_when_no_english():
    assert french_bonus(profile(first_language=lang(10, "french"))) == 25


@pytest.mark.parametrize("weak", ["speaking", "listening", "reading", "writing"])
def test_french_25_when_any_english_ability_below_5(weak):
    english = mixed("english", speaking=9, listening=9, reading=9, writing=9)
    english = LanguageResult("x", "english", {**english.levels, weak: 4})
    assert french_bonus(profile(first_language=lang(8, "french"), second_language=english)) == 25


def test_french_requires_nclc7_on_all_abilities():
    weak_french = mixed("french", speaking=10, listening=10, reading=10, writing=6)
    assert french_bonus(profile(first_language=weak_french)) == 0
    assert french_bonus(profile(first_language=lang(7, "french"))) == 25


def test_no_french_no_bonus():
    assert french_bonus(profile(first_language=lang(10))) == 0
    assert french_bonus(profile(first_language=lang(10), second_language=lang(10, "french"))) == 50


def test_sibling_is_flat_15():
    assert score_additional(profile(has_sibling_in_canada=True))["sibling"] == 15
    assert score_additional(profile())["sibling"] == 0


@pytest.mark.parametrize("level,expected", [("none", 0), ("one_two_year", 15), ("three_plus", 30)])
def test_canadian_study(level, expected):
    assert score_additional(profile(canadian_study=level))["canadian_study"] == expected


def test_nomination_600():
    assert score_additional(profile(has_provincial_nomination=True))["nomination"] == 600
