"""Maklersiz (Owner vs Agent) Classification Engine supporting Uzbek and Russian."""

import re
import unicodedata
from typing import List, Tuple, Optional
from src.classification.types import (
    ClassificationLabel,
    ClassificationResult,
    MatchedSignal,
)


class ClassificationEngine:
    """Configurable rule-based classification engine with contextual keyword analysis."""

    def __init__(
        self,
        positive_threshold: float = 0.70,
        negative_threshold: float = 0.35,
    ):
        self.positive_threshold = positive_threshold
        self.negative_threshold = negative_threshold

        # 1. Contextual Owner Patterns (contain words like 'makler'/'риелтор', but clearly indicate owner intent)
        # e.g. "Maklerlar bezovta qilmasin", "риелторам не беспокоить", "без комиссии"
        self.contextual_owner_patterns: List[Tuple[re.Pattern, float, str]] = [
            (
                re.compile(
                    r"\b(?:makler(?:lar)?|vositachi(?:lar)?)\s*(?:(?:iltimos|yolvormoqda)\s*)?(?:bezovta\s*qilmasin(?:lar)?|tel\s*qilmasin(?:lar)?|aloqaga\s*chiqmasin|kerak\s*emas)\b",
                    re.IGNORECASE,
                ),
                0.40,
                "Contextual: Brokers do not disturb (Uzbek)",
            ),
            (
                re.compile(
                    r"\b(?:риелтор(?:ам|ов|ы)?|риэлтор(?:ам|ов|ы)?|агентств(?:ам|а)?|посредник(?:ам|ов|и)?)\s*(?:(?:просьба|пожалуйста)\s*)?(?:не\s*беспокоить|не\s*звонить|мимо)\b",
                    re.IGNORECASE,
                ),
                0.40,
                "Contextual: Agents do not disturb (Russian)",
            ),
            (
                re.compile(
                    r"\b(?:без\s*(?:риелтор(?:ов|а)?|риэлтор(?:ов|а)?|посредник(?:ов|а)?|комисси(?:и|й)?|агентств(?:а)?))\b",
                    re.IGNORECASE,
                ),
                0.35,
                "Contextual: No commission / no agents (Russian)",
            ),
            (
                re.compile(
                    r"\b(?:komissiya(?:siz)?\s*0%|0%\s*komissiya|usluga(?:siz)?\s*yo['`‘]?q|maklersiz)\b",
                    re.IGNORECASE,
                ),
                0.35,
                "Contextual: 0% commission / no broker fee (Uzbek)",
            ),
        ]

        # 2. Direct Positive Signals (Owner keywords in Uzbek & Russian)
        self.positive_patterns: List[Tuple[re.Pattern, float, str]] = [
            # Uzbek
            (re.compile(r"\bmaklersiz\s+ijara\b", re.IGNORECASE), 0.35, "maklersiz ijara (UZ)"),
            (re.compile(r"\bmaklersiz\s+beriladi\b", re.IGNORECASE), 0.35, "maklersiz beriladi (UZ)"),
            (re.compile(r"\bmaklersiz\b", re.IGNORECASE), 0.30, "maklersiz (UZ)"),
            (re.compile(r"\bbevosita\s+egasidan\b", re.IGNORECASE), 0.40, "bevosita egasidan (UZ)"),
            (re.compile(r"\b(?:uy|kvartira)?\s*egasidan\b", re.IGNORECASE), 0.35, "egasidan (UZ)"),
            (re.compile(r"\bvositachilarsiz\b", re.IGNORECASE), 0.35, "vositachilarsiz (UZ)"),
            (re.compile(r"\b(?:o['`‘]?zimning|ozimning)\s+(?:uyim|kvartiram)\b", re.IGNORECASE), 0.35, "ozimning uyim (UZ)"),
            (re.compile(r"\b(?:uy|kvartira)?\s*egasiman\b", re.IGNORECASE), 0.35, "egasiman (UZ)"),

            # Russian
            (re.compile(r"\bбез\s+посредников\b", re.IGNORECASE), 0.35, "без посредников (RU)"),
            (re.compile(r"\bот\s+собственника\b", re.IGNORECASE), 0.40, "от собственника (RU)"),
            (re.compile(r"\bнапрямую\s+от\s+владельца\b", re.IGNORECASE), 0.40, "напрямую от владельца (RU)"),
            (re.compile(r"\bсобственн(?:ая|ое|ый)\s+(?:квартира|жилье|дом)?\b", re.IGNORECASE), 0.35, "собственная квартира (RU)"),
            (re.compile(r"\bсобственник\b", re.IGNORECASE), 0.30, "собственник (RU)"),
            (re.compile(r"\bбез\s+риелтор(?:а|ов)?\b", re.IGNORECASE), 0.35, "без риелтора (RU)"),
            (re.compile(r"\bсдаю\s+свою\b", re.IGNORECASE), 0.30, "сдаю свою (RU)"),
            (re.compile(r"\bя\s+хозяин\b", re.IGNORECASE), 0.35, "я хозяин (RU)"),
        ]

        # 3. Direct Negative / Suspicious Signals (Agency keywords and fees)
        self.negative_patterns: List[Tuple[re.Pattern, float, str]] = [
            # Explicit commission mentions
            (re.compile(r"\b\d+%\s*(?:komissiya|usluga|комиссия|услуги)\b", re.IGNORECASE), 0.45, "Explicit commission % mentioned"),
            (re.compile(r"\b(?:komissiya|usluga)\s*(?:bor|mavjud|50%|30%)\b", re.IGNORECASE), 0.40, "Agent fee required (UZ)"),
            (re.compile(r"\b(?:комиссия|услуги)\s*(?:агентства|риелтора|есть|оплачиваются|50%)\b", re.IGNORECASE), 0.40, "Agent fee required (RU)"),

            # Intermediary / Agency names
            (re.compile(r"\b(?:agentlik|agentligi)\b", re.IGNORECASE), 0.40, "Real estate agency (UZ)"),
            (re.compile(r"\bагентство\s*(?:недвижимости)?\b", re.IGNORECASE), 0.40, "Real estate agency (RU)"),
            (re.compile(r"\bпосреднические\s+услуги\b", re.IGNORECASE), 0.35, "Intermediary services (RU)"),
            (re.compile(r"\bуслуги\s+агентства\b", re.IGNORECASE), 0.40, "Agency services (RU)"),

            # General keywords
            (re.compile(r"\bриелтор(?:ские)?\s*(?:услуги)?\b", re.IGNORECASE), 0.35, "риелтор (RU)"),
            (re.compile(r"\bриэлтор(?:ские)?\b", re.IGNORECASE), 0.35, "риэлтор (RU)"),
            (re.compile(r"\bпосредник\b", re.IGNORECASE), 0.35, "посредник (RU)"),
            (re.compile(r"\bкомиссия\b", re.IGNORECASE), 0.30, "комиссия (RU)"),
            (re.compile(r"\bmakler\b", re.IGNORECASE), 0.30, "makler (UZ)"),
            (re.compile(r"\bvositachi\b", re.IGNORECASE), 0.30, "vositachi (UZ)"),
        ]

    def normalize_text(self, text: str) -> str:
        """Normalize text: NFKC unicode, standardized apostrophes, lowercasing."""
        if not text:
            return ""
        norm = unicodedata.normalize("NFKC", text)
        # Standardize various apostrophe types to a single apostrophe '
        norm = re.sub(r"[`‘ʻ’ʼ]", "'", norm)
        return norm

    def classify(self, title: str, description: Optional[str] = None) -> ClassificationResult:
        """Classify a listing by title and description, returning an explainable result."""
        full_text = f"{title or ''} {description or ''}"
        norm_text = self.normalize_text(full_text)

        matched_signals: List[MatchedSignal] = []
        reasons: List[str] = []

        # Step 1: Check Contextual Owner Patterns first
        # We replace matched contextual owner phrases with placeholder text so their sub-words (like 'makler')
        # don't trigger the negative patterns!
        processed_text = norm_text
        context_score_add = 0.0

        for pattern, weight, desc in self.contextual_owner_patterns:
            matches = list(pattern.finditer(processed_text))
            for match in matches:
                matched_str = match.group(0)
                signal = MatchedSignal(
                    signal_type="contextual_owner",
                    matched_text=matched_str,
                    weight=weight,
                    description=desc,
                )
                matched_signals.append(signal)
                reasons.append(f"Egasi belgisi (kontekst): '{matched_str}' -> +{weight:.2f}")
                context_score_add += weight
                # Mask matched region
                processed_text = (
                    processed_text[: match.start()]
                    + (" " * len(matched_str))
                    + processed_text[match.end() :]
                )

        # Step 2: Check Direct Positive Signals on remaining text
        positive_score_add = 0.0
        for pattern, weight, desc in self.positive_patterns:
            matches = list(pattern.finditer(processed_text))
            for match in matches:
                matched_str = match.group(0)
                signal = MatchedSignal(
                    signal_type="positive",
                    matched_text=matched_str,
                    weight=weight,
                    description=desc,
                )
                matched_signals.append(signal)
                reasons.append(f"Ijobiy belgi: '{matched_str}' -> +{weight:.2f}")
                positive_score_add += weight
                # Mask to prevent double counting
                processed_text = (
                    processed_text[: match.start()]
                    + (" " * len(matched_str))
                    + processed_text[match.end() :]
                )

        # Step 3: Check Direct Negative Signals on remaining unmasked text
        negative_score_sub = 0.0
        for pattern, weight, desc in self.negative_patterns:
            matches = list(pattern.finditer(processed_text))
            for match in matches:
                matched_str = match.group(0)
                signal = MatchedSignal(
                    signal_type="negative",
                    matched_text=matched_str,
                    weight=weight,
                    description=desc,
                )
                matched_signals.append(signal)
                reasons.append(f"Salbiy/Agentlik belgisi: '{matched_str}' -> -{weight:.2f}")
                negative_score_sub += weight
                processed_text = (
                    processed_text[: match.start()]
                    + (" " * len(matched_str))
                    + processed_text[match.end() :]
                )

        # Calculate final confidence score
        # Base neutral score is 0.50
        base_score = 0.50
        total_positive = context_score_add + positive_score_add

        if total_positive > 0 and negative_score_sub == 0:
            # Clean positive signals with no negative signals
            confidence_score = min(1.0, base_score + total_positive)
        elif negative_score_sub > 0 and total_positive == 0:
            # Clean negative signals with no positive signals
            confidence_score = max(0.0, base_score - negative_score_sub)
        elif total_positive > 0 and negative_score_sub > 0:
            # Conflicting signals: weigh difference
            confidence_score = min(1.0, max(0.0, base_score + total_positive - negative_score_sub))
        else:
            # No signals at all
            confidence_score = base_score
            reasons.append("Aniq belgilar topilmadi (neytral).")

        confidence_score = round(confidence_score, 2)

        # Determine Classification Label
        if total_positive > 0 and negative_score_sub == 0 and confidence_score >= self.positive_threshold:
            label = ClassificationLabel.LIKELY_OWNER
            summary = "Egasidan bo‘lishi mumkin (Ijobiy dalillar mavjud)"
        elif negative_score_sub >= 0.35 and total_positive == 0:
            label = ClassificationLabel.LIKELY_AGENT
            summary = "Agentlik yoki vositachi ehtimoli yuqori"
        elif total_positive > 0 and negative_score_sub > 0:
            label = ClassificationLabel.NEEDS_REVIEW
            summary = "Ziddiyatli belgilar (Qayta ko‘rib chiqish talab etiladi)"
        elif confidence_score >= self.positive_threshold:
            label = ClassificationLabel.LIKELY_OWNER
            summary = "Egasidan bo‘lishi mumkin"
        elif confidence_score <= self.negative_threshold:
            label = ClassificationLabel.LIKELY_AGENT
            summary = "Agentlik yoki vositachi ehtimoli yuqori"
        else:
            label = ClassificationLabel.NEEDS_REVIEW
            summary = "Yetarli dalil yo‘q yoki noaniq"

        return ClassificationResult(
            label=label,
            confidence_score=confidence_score,
            matched_signals=matched_signals,
            reasons=reasons,
            summary_uz=summary,
        )


# Global default engine instance
default_classifier = ClassificationEngine()
