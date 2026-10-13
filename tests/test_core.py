import pytest

from crs.sections.core import score_core
from crs.models import SpouseProfile
from helpers import lang, profile

AGES = {  # age: (couple, single)
    17: (0, 0), 18: (90, 99), 19: (95, 105), 20: (100, 110), 25: (100, 110), 29: (100, 110),
    30: (95, 105), 31: (90, 99), 32: (85, 94), 33: (80, 88), 34: (75, 83), 35: (70, 77),
    36: (65, 72), 37: (60, 66), 38: (55, 61), 39: (50, 55), 40: (45, 50), 41: (35, 39),
    42: (25, 28), 43: (15, 17), 44: (5, 6), 45: (0, 0), 60: (0, 0), 100: (0, 0),
}
EDU = {
    "none": (0, 0), "secondary": (28, 30), "one_year": (84, 90), "two_year": (91, 98),
    "bachelor": (112, 120), "two_or_more": (119, 128), "master": (126, 135), "doctoral": (140, 150),
}
FIRST = {0: (0, 0), 3: (0, 0), 4: (6, 6), 5: (6, 6), 6: (8, 9), 7: (16, 17), 8: (22, 23),
         9: (29, 31), 10: (32, 34)}  # per ability
SECOND = {0: 0, 4: 0, 5: 1, 6: 1, 7: 3, 8: 3, 9: 6, 10: 6}
WORK = {0: (0, 0), 1: (35, 40), 2: (46, 53), 3: (56, 64), 4: (63, 72), 5: (70, 80)}
SPOUSE = SpouseProfile()


def col(couple):
    return dict(spouse=SPOUSE) if couple else {}


@pytest.mark.parametrize("couple", [True, False])
@pytest.mark.parametrize("age", AGES)
def test_age(age, couple):
    assert score_core(profile(age=age, **col(couple)))["age"] == AGES[age][0 if couple else 1]


@pytest.mark.parametrize("couple", [True, False])
@pytest.mark.parametrize("edu", EDU)
def test_education(edu, couple):
    assert score_core(profile(education=edu, **col(couple)))["education"] == EDU[edu][0 if couple else 1]


@pytest.mark.parametrize("couple", [True, False])
@pytest.mark.parametrize("level", FIRST)
def test_first_language(level, couple):
    pts = score_core(profile(first_language=lang(level), **col(couple)))["first_language"]
    assert pts == 4 * FIRST[level][0 if couple else 1]


@pytest.mark.parametrize("level", SECOND)
def test_second_language_single(level):
    p = profile(second_language=lang(level, "french"))
    assert score_core(p)["second_language"] == 4 * SECOND[level]


def test_second_language_caps():
    assert score_core(profile(second_language=lang(10, "french")))["second_language"] == 24
    assert score_core(profile(second_language=lang(10, "french"), spouse=SPOUSE))["second_language"] == 22
    assert score_core(profile())["second_language"] == 0


def test_language_scored_per_ability():
    from crs.language_mapper import LanguageResult
    mixed = LanguageResult("x", "english", dict(speaking=10, listening=7, reading=4, writing=0))
    assert score_core(profile(first_language=mixed))["first_language"] == 34 + 17 + 6 + 0


@pytest.mark.parametrize("couple", [True, False])
@pytest.mark.parametrize("years", WORK)
def test_canadian_work(years, couple):
    pts = score_core(profile(canadian_work_years=years, **col(couple)))["canadian_work"]
    assert pts == WORK[years][0 if couple else 1]


def test_core_maximums():
    best = dict(age=25, education="doctoral", first_language=lang(10),
                second_language=lang(10, "french"), canadian_work_years=5)
    assert sum(score_core(profile(**best)).values()) == 500
    assert sum(score_core(profile(spouse=SPOUSE, **best)).values()) == 460
