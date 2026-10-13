import pytest

from crs import ValidationError, calculate
from crs.language_mapper import map_scores
from crs.models import Profile, SpouseProfile, resolve_couple
from helpers import lang, profile


def test_single_worked_example():
    # age 29, bachelor, CLB 9 all (first), 3 yrs Canadian work, 3 yrs foreign work, no extras
    p = profile(age=29, education="bachelor", first_language=lang(9), canadian_work_years=3,
                foreign_work_years=3)
    s = calculate(p)
    assert s.core.total == 110 + 120 + 124 + 64
    # education: 25 (CLB 9) + 25 (CWE 2+) = 50; foreign: 3 yrs -> 50 + 50 capped at 50
    assert s.transferability.items == {"education": 50, "foreign_work": 50, "certificate": 0}
    assert s.transferability.total == 100
    assert s.total == 418 + 100


def test_couple_worked_example():
    spouse = SpouseProfile(education="master", canadian_work_years=1, language=lang(7))
    p = profile(age=30, education="master", first_language=lang(8), canadian_work_years=1,
                spouse=spouse)
    s = calculate(p)
    assert s.core.total == 95 + 126 + 4 * 22 + 35
    assert s.spouse.total == 10 + 12 + 5
    assert s.scored_as_couple
    assert s.total == s.core.total + s.spouse.total + s.transferability.total


def test_max_single_is_1200():
    p = Profile(age=25, education="doctoral", first_language=lang(10, "french"),
                second_language=lang(10, "english"), canadian_work_years=5, foreign_work_years=3,
                has_certificate_of_qualification=True, has_sibling_in_canada=True,
                canadian_study="three_plus", has_provincial_nomination=True)
    s = calculate(p)
    assert (s.core.total, s.transferability.total) == (500, 100)
    assert s.additional.items == {"sibling": 15, "french": 50, "canadian_study": 30, "nomination": 600}
    assert s.additional.total == 600  # 695 capped
    assert s.total == 1200


def test_max_couple_is_1200():
    spouse = SpouseProfile("doctoral", 5, lang(10))
    p = Profile(age=25, education="doctoral", first_language=lang(10), second_language=lang(10, "french"),
                canadian_work_years=5, foreign_work_years=3, has_provincial_nomination=True,
                has_sibling_in_canada=True, canadian_study="three_plus", spouse=spouse,
                has_certificate_of_qualification=True)
    s = calculate(p)
    assert (s.core.total, s.spouse.total, s.transferability.total, s.additional.total) == (460, 40, 100, 600)
    assert s.total == 1200


def test_transferability_total_cap():
    p = profile(education="master", first_language=lang(10), canadian_work_years=3,
                foreign_work_years=3, has_certificate_of_qualification=True)
    s = calculate(p)
    assert sum(s.transferability.items.values()) == 150
    assert s.transferability.total == 100


def test_nomination_adds_600():
    base = calculate(profile()).total
    assert calculate(profile(has_provincial_nomination=True)).total == base + 600


def test_canadian_bachelor_scores_in_both_a_and_d():
    s = calculate(profile(education="bachelor", canadian_study="three_plus"))
    assert s.core.items["education"] == 120 and s.additional.items["canadian_study"] == 30


def test_no_job_offer_points_exist():
    assert "job_offer" not in calculate(profile()).to_dict()["sections"]["additional"]["items"]


def test_real_test_scores_end_to_end():
    ielts = map_scores("ielts", dict(speaking=7.0, listening=8.0, reading=7.0, writing=7.0))
    s = calculate(profile(first_language=ielts))
    assert s.core.items["first_language"] == 4 * 31


def test_same_language_rejected():
    with pytest.raises(ValidationError):
        profile(second_language=lang(7, "english"))


@pytest.mark.parametrize("kw", [dict(age=16), dict(age=101), dict(age=25.5), dict(education="phd"),
                                dict(canadian_work_years=6), dict(foreign_work_years=4),
                                dict(canadian_study="x"), dict(canadian_work_years=-1)])
def test_validation(kw):
    with pytest.raises(ValidationError):
        profile(**kw)


@pytest.mark.parametrize("status,citizen,coming,expected", [
    ("single", False, True, False), ("widowed", False, True, False),
    ("married", False, True, True), ("common_law", False, True, True),
    ("married", True, True, False), ("married", False, False, False),
    ("common_law", True, False, False),
])
def test_resolve_couple(status, citizen, coming, expected):
    assert resolve_couple(status, citizen, coming) is expected


def test_to_dict_shape():
    d = calculate(profile()).to_dict()
    assert d["max"] == 1200 and set(d["sections"]) == {"core", "spouse", "transferability", "additional"}
