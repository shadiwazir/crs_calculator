import pytest

from crs.language_mapper import InvalidScoreError, map_scores, to_level

A = ("speaking", "listening", "reading", "writing")

# (test, ability, score, expected level) – edges of IRCC grids
CASES = [
    ("celpip", "reading", 3, 0), ("celpip", "reading", 4, 4), ("celpip", "reading", 9, 9),
    ("celpip", "reading", 10, 10), ("celpip", "reading", 12, 10),
    ("ielts", "speaking", 3.5, 0), ("ielts", "speaking", 4.0, 4), ("ielts", "speaking", 4.5, 4),
    ("ielts", "speaking", 5.0, 5), ("ielts", "speaking", 7.0, 9), ("ielts", "speaking", 7.5, 10),
    ("ielts", "reading", 3.5, 4), ("ielts", "reading", 4.0, 5), ("ielts", "reading", 4.5, 5),
    ("ielts", "reading", 5.0, 6), ("ielts", "reading", 8.0, 10), ("ielts", "reading", 7.5, 9),
    ("ielts", "listening", 8.0, 9), ("ielts", "listening", 8.5, 10), ("ielts", "listening", 4.0, 0),
    ("ielts", "listening", 4.5, 4), ("ielts", "writing", 6.5, 8), ("ielts", "writing", 6.0, 7),
    ("pte", "listening", 27, 0), ("pte", "listening", 28, 4), ("pte", "listening", 59, 6),
    ("pte", "listening", 60, 7), ("pte", "listening", 71, 8), ("pte", "listening", 82, 9),
    ("pte", "listening", 89, 10), ("pte", "writing", 88, 9), ("pte", "writing", 89, 9),
    ("pte", "writing", 90, 10), ("pte", "reading", 88, 10), ("pte", "speaking", 41, 0),
    ("pte", "speaking", 42, 4), ("pte", "speaking", 68, 7),
    ("tef", "speaking", 180, 0), ("tef", "speaking", 181, 4), ("tef", "speaking", 310, 7),
    ("tef", "speaking", 393, 10), ("tef", "listening", 249, 7), ("tef", "listening", 316, 10),
    ("tef", "reading", 206, 6), ("tef", "reading", 207, 7), ("tef", "reading", 263, 10),
    ("tcf", "speaking", 3, 0), ("tcf", "speaking", 4, 4), ("tcf", "speaking", 10, 7),
    ("tcf", "speaking", 16, 10), ("tcf", "listening", 457, 6), ("tcf", "listening", 458, 7),
    ("tcf", "listening", 549, 10), ("tcf", "reading", 523, 8), ("tcf", "reading", 524, 9),
    ("tcf", "reading", 330, 0), ("tcf", "reading", 342, 4), ("tcf", "writing", 14, 9),
]


@pytest.mark.parametrize("test,ability,score,expected", CASES)
def test_to_level(test, ability, score, expected):
    assert to_level(test, ability, score) == expected


def test_map_scores_result():
    r = map_scores("ielts", dict(speaking=7.0, listening=8.0, reading=7.0, writing=7.0))
    assert r.levels == dict(speaking=9, listening=9, reading=9, writing=9)
    assert r.language == "english" and r.minimum == 9
    assert map_scores("tef", dict(speaking=400, listening=320, reading=270, writing=400)).language == "french"


def test_below_clb4_does_not_raise():
    r = map_scores("celpip", dict(speaking=1, listening=1, reading=1, writing=1))
    assert r.minimum == 0


@pytest.mark.parametrize("test,scores", [
    ("ielts", dict(speaking=9.5, listening=8, reading=8, writing=8)),
    ("ielts", dict(speaking=6.25, listening=8, reading=8, writing=8)),
    ("celpip", dict(speaking=-1, listening=8, reading=8, writing=8)),
    ("tcf", dict(speaking=21, listening=500, reading=500, writing=10)),
    ("tef", dict(speaking=100, listening=361, reading=100, writing=100)),
    ("pte", dict(speaking=91, listening=50, reading=50, writing=50)),
    ("ielts", dict(speaking=8, listening=8, reading=8)),
    ("toefl", dict(speaking=8, listening=8, reading=8, writing=8)),
    ("ielts", dict(speaking="8", listening=8, reading=8, writing=8)),
])
def test_invalid_scores(test, scores):
    with pytest.raises(InvalidScoreError):
        map_scores(test, scores)
