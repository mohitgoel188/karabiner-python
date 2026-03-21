from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Rule:
    """High-level rule grouping multiple manipulators."""
    description: str
    manipulators: List[Dict[str, Any]] = field(default_factory=list)
