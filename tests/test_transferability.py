import pytest

from crs.sections.transferability import score_transferability
from helpers import lang, profile

# education tier, language level (min CLB), cwe years -> expected education-group points
POST, HIGH = "bachelor", "master"


@pytest.mark.parametrize("edu,clb,cwe,expected", [
    ("secondary", 10, 3, 0), ("none", 10, 3, 0),
    (POST, 6, 0, 0), (POST, 7, 0, 13), (POST, 8, 0, 13), (POST, 9, 0, 25), (POST, 10, 0, 25),
    (POST, 0, 1, 13), (POST, 0, 2, 25), (POST, 0, 5, 25),
    (POST, 7, 1, 26), (POST, 9, 2, 50), (POST, 9, 1, 38), (POST, 7, 2, 38),
    ("one_year", 7, 0, 13), ("two_year", 9, 0, 25),
    (HIGH, 6, 0, 0), (HIGH, 7, 0, 25), (HIGH, 9, 0, 50), (HIGH, 0, 1, 25), (HIGH, 0, 2, 50),
    (HIGH, 9, 2, 50), (HIGH, 7, 1, 50), ("doctoral", 7, 0, 25), ("two_or_more", 9, 0, 50),
])
def test_education_group(edu, clb, cwe, expected):
    p = profile(education=edu, first_language=lang(clb), canadian_work_years=cwe)
    assert score_transferability(p)["education"] == expected


@pytest.mark.parametrize("fwe,clb,cwe,expected", [
    (0, 10, 5, 0),
    (1, 7, 0, 13), (2, 8, 0, 13), (1, 9, 0, 25), (2, 10, 0, 25), (1, 6, 0, 0),
    (3, 7, 0, 25), (3, 9, 0, 50), (3, 6, 0, 0),
    (1, 0, 1, 13), (2, 0, 2, 25), (3, 0, 1, 25), (3, 0, 2, 50),
    (1, 7, 1, 26), (3, 9, 2, 50), (3, 7, 1, 50), (2, 9, 2, 50),
])
def test_foreign_work_group(fwe, clb, cwe, expected):
    p = profile(foreign_work_years=fwe, first_language=lang(clb), canadian_work_years=cwe)
    assert score_transferability(p)["foreign_work"] == expected


@pytest.mark.parametrize("clb,expected", [(4, 0), (5, 25), (6, 25), (7, 50), (10, 50)])
def test_certificate(clb, expected):
    p = profile(has_certificate_of_qualification=True, first_language=lang(clb))
    assert score_transferability(p)["certificate"] == expected


def test_certificate_requires_flag():
    assert score_transferability(profile(first_language=lang(10)))["certificate"] == 0


def test_language_uses_minimum_ability():
    from crs.language_mapper import LanguageResult
    weak = LanguageResult("x", "english", dict(speaking=10, listening=10, reading=10, writing=6))
    assert score_transferability(profile(first_language=weak))["education"] == 0
