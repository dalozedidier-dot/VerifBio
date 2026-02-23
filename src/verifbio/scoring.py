from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

LevelStatus = Literal["pass", "partial", "fail"]


@dataclass(frozen=True)
class Weights:
    b1: float = 1.0
    b2: float = 1.0
    b3: float = 1.5
    b4: float = 2.0
    b5: float = 3.0
    sabv: float = 2.0
    blinding: float = 1.5
    randomization: float = 1.5


def _score(status: LevelStatus) -> float:
    if status == "pass":
        return 1.0
    if status == "partial":
        return 0.5
    return 0.0


def weighted_score(
    *,
    b1: LevelStatus,
    b2: LevelStatus,
    b3: LevelStatus,
    b4: LevelStatus,
    b5: LevelStatus,
    sabv: LevelStatus | None = None,
    blinding: LevelStatus | None = None,
    randomization: LevelStatus | None = None,
    weights: Weights | None = None,
) -> int:
    w = weights or Weights()

    total_w = w.b1 + w.b2 + w.b3 + w.b4 + w.b5
    total = (
        w.b1 * _score(b1)
        + w.b2 * _score(b2)
        + w.b3 * _score(b3)
        + w.b4 * _score(b4)
        + w.b5 * _score(b5)
    )

    if sabv is not None:
        total_w += w.sabv
        total += w.sabv * _score(sabv)

    if blinding is not None:
        total_w += w.blinding
        total += w.blinding * _score(blinding)

    if randomization is not None:
        total_w += w.randomization
        total += w.randomization * _score(randomization)

    if total_w <= 0:
        return 0

    return int(round((total / total_w) * 100))
