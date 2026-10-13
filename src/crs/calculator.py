"""Orchestrates the four CRS sections, applies caps and returns a breakdown."""
from dataclasses import dataclass, field

from . import tables
from .models import Profile
from .sections.additional import score_additional
from .sections.core import score_core
from .sections.spouse import score_spouse
from .sections.transferability import score_transferability

TOTAL_MAX = 1200


@dataclass(frozen=True)
class SectionScore:
    total: int            # after caps
    items: dict           # line item -> points (before the section cap)
    maximum: int

    def to_dict(self) -> dict:
        return {"total": self.total, "max": self.maximum, "items": self.items}


@dataclass(frozen=True)
class Score:
    core: SectionScore
    spouse: SectionScore
    transferability: SectionScore
    additional: SectionScore
    scored_as_couple: bool
    total: int = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "total", sum(s.total for s in (
            self.core, self.spouse, self.transferability, self.additional)))

    def to_dict(self) -> dict:
        return {"total": self.total, "max": TOTAL_MAX, "scored_as_couple": self.scored_as_couple,
                "sections": {"core": self.core.to_dict(), "spouse": self.spouse.to_dict(),
                             "transferability": self.transferability.to_dict(),
                             "additional": self.additional.to_dict()}}


def calculate(profile: Profile) -> Score:
    couple = profile.spouse is not None
    core = score_core(profile)
    spouse = score_spouse(profile)
    transfer = score_transferability(profile)
    additional = score_additional(profile)
    return Score(
        core=SectionScore(sum(core.values()), core, 460 if couple else 500),
        spouse=SectionScore(sum(spouse.values()), spouse, 40 if couple else 0),
        transferability=SectionScore(min(sum(transfer.values()), tables.TRANSFER_TOTAL_CAP),
                                     transfer, tables.TRANSFER_TOTAL_CAP),
        additional=SectionScore(min(sum(additional.values()), tables.ADDITIONAL_CAP),
                                additional, tables.ADDITIONAL_CAP),
        scored_as_couple=couple,
    )
