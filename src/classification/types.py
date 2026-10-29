"""Classification types and data structures."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ClassificationLabel(str, Enum):
    """Classification labels for listing owner status."""

    LIKELY_OWNER = "LIKELY_OWNER"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    LIKELY_AGENT = "LIKELY_AGENT"

    @property
    def display_uz(self) -> str:
        if self == ClassificationLabel.LIKELY_OWNER:
            return "Egasi bo‘lishi mumkin"
        elif self == ClassificationLabel.LIKELY_AGENT:
            return "Rieltor / Agentlik"
        return "Tekshirilmoqda"

    @property
    def is_likely_owner(self) -> bool:
        return self == ClassificationLabel.LIKELY_OWNER


class MatchedSignal(BaseModel):
    """Details of a single pattern match in classification."""

    signal_type: str  # "positive", "negative", "contextual_owner"
    matched_text: str
    weight: float
    description: str


class ClassificationResult(BaseModel):
    """Explainable result of the classification process."""

    label: ClassificationLabel
    confidence_score: float = Field(ge=0.0, le=1.0)
    matched_signals: List[MatchedSignal] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)
    summary_uz: str

