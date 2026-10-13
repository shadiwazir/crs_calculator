"""Generic evaluation of declarative rule tables."""
from typing import Sequence, TypeVar

T = TypeVar("T")


def lookup_band(bands: Sequence[tuple[float, T]], value: float) -> T:
    """Return the value of the highest band whose minimum is <= ``value``.

    ``bands`` must be ascending by minimum; the first band is the fallback for lower values.
    """
    result = bands[0][1]
    for minimum, band_value in bands:
        if value >= minimum:
            result = band_value
        else:
            break
    return result
