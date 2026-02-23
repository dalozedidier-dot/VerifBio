from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .models import ClaimSpec


def load_claim(path: str | Path) -> ClaimSpec:
    p = Path(path)
    data: Any
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    try:
        return ClaimSpec.model_validate(data)
    except ValidationError as e:
        msg = e.json(indent=2)
        raise ValueError(f"Invalid claim spec for {p}:\n{msg}") from e
