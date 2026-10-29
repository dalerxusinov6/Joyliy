"""Classification package."""

from src.classification.types import (
    ClassificationLabel,
    ClassificationResult,
    MatchedSignal,
)
from src.classification.engine import ClassificationEngine, default_classifier

__all__ = [
    "ClassificationLabel",
    "ClassificationResult",
    "MatchedSignal",
    "ClassificationEngine",
    "default_classifier",
]

