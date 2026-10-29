"""Classification package."""

from src.classification.types import (
    ClassificationLabel,
    ClassificationResult,
    MatchedSignal,
)
from src.classification.engine import ClassificationEngine, default_classifier
from src.classification.audience import (
    TargetAudience,
    detect_target_audience,
    get_audience_label_uz,
    get_audience_icon,
)

__all__ = [
    "ClassificationLabel",
    "ClassificationResult",
    "MatchedSignal",
    "ClassificationEngine",
    "default_classifier",
    "TargetAudience",
    "detect_target_audience",
    "get_audience_label_uz",
    "get_audience_icon",
]

