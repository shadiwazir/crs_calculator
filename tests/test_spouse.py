import pytest

from crs.models import SpouseProfile
from crs.sections.spouse import score_spouse
from helpers import lang, profile

EDU = {"none": 0, "secondary": 2, "one_year": 6, "two_year": 7, "bachelor": 8,
       "two_or_more": 9, "master": 10, "doctoral": 10}
LANG = {0: 0, 4: 0, 5: 1, 6: 1, 7: 3, 8: 3, 9: 5, 10: 5}
WORK = {0: 0, 1: 5, 2: 7, 3: 8, 4: 9, 5: 10}


def sp(**kw):
    return profile(spouse=SpouseProfile(**kw))


@pytest.mark.parametrize("edu", EDU)
def test_education(edu):
    assert score_spouse(sp(education=edu))["education"] == EDU[edu]


@pytest.mark.parametrize("level", LANG)
@pytest.mark.parametrize("language", ["english", "french"])
def test_language(level, language):
    assert score_spouse(sp(language=lang(level, language)))["language"] == 4 * LANG[level]


@pytest.mark.parametrize("years", WORK)
def test_work(years):
    assert score_spouse(sp(canadian_work_years=years))["canadian_work"] == WORK[years]


def test_no_language_test_is_zero():
    assert score_spouse(sp(language=None))["language"] == 0


def test_no_spouse_scores_zero():
    assert sum(score_spouse(profile()).values()) == 0


def test_spouse_maximum_40():
    full = sp(education="doctoral", language=lang(10), canadian_work_years=5)
    assert sum(score_spouse(full).values()) == 40
