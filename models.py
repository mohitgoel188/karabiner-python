from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Manipulator:
    """Represents a single Karabiner manipulator block."""
    description: str
    from_: Dict[str, Any]
    to: List[Dict[str, Any]] = field(default_factory=list)
    to_after_key_up: List[Dict[str, Any]] = field(default_factory=list)
    to_if_alone: List[Dict[str, Any]] = field(default_factory=list)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    type: str = "basic"


@dataclass
class Rule:
    """High-level rule grouping multiple manipulators."""
    description: str
    manipulators: List[Dict[str, Any]] = field(default_factory=list)
