from crs.language_mapper import map_scores
from crs.models import Profile


def celpip(level):
    return map_scores("celpip", {a: level for a in ("speaking", "listening", "reading", "writing")})


def lang(level, language="english"):
    """A LanguageResult with the same CLB/NCLC on every ability (via CELPIP / TCF-free construction)."""
    from crs.language_mapper import LanguageResult
    return LanguageResult("synthetic", language,
                          {a: level for a in ("speaking", "listening", "reading", "writing")})


def profile(**kw):
    kw.setdefault("age", 25)
    kw.setdefault("education", "bachelor")
    kw.setdefault("first_language", lang(9))
    return Profile(**kw)
