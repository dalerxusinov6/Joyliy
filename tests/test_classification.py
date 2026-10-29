"""Tests for Uzbek and Russian Maklersiz classification engine."""

import pytest
from src.classification.engine import ClassificationEngine
from src.classification.types import ClassificationLabel


def test_uzbek_positive_signals(classifier: ClassificationEngine):
    """Test standard positive signals in Uzbek."""
    samples = [
        ("Chilonzorda 2 xonali kvartira, maklersiz ijara", ClassificationLabel.LIKELY_OWNER),
        ("Kvartira egasidan beriladi, toza va shinam", ClassificationLabel.LIKELY_OWNER),
        ("Yunusobodda bevosita egasidan 1 xonali kvartira", ClassificationLabel.LIKELY_OWNER),
        ("Kvartira vositachilarsiz ijaraga beriladi", ClassificationLabel.LIKELY_OWNER),
        ("Maklersiz beriladi, barcha sharoitlar mavjud", ClassificationLabel.LIKELY_OWNER),
        ("O‘zimning uyim, oilaga beraman", ClassificationLabel.LIKELY_OWNER),
    ]
    for title, expected_label in samples:
        res = classifier.classify(title=title)
        assert res.label == expected_label, f"Failed for '{title}': got {res.label}"
        assert res.confidence_score >= 0.70
        assert len(res.reasons) > 0


def test_russian_positive_signals(classifier: ClassificationEngine):
    """Test standard positive signals in Russian."""
    samples = [
        ("Сдам 2 комнатную квартиру без посредников", ClassificationLabel.LIKELY_OWNER),
        ("Квартира от собственника в центре", ClassificationLabel.LIKELY_OWNER),
        ("Сдаю свою 1 комнатную квартиру напрямую от владельца", ClassificationLabel.LIKELY_OWNER),
        ("Я хозяин, без риелтора сдам квартиру семье", ClassificationLabel.LIKELY_OWNER),
    ]
    for title, expected_label in samples:
        res = classifier.classify(title=title)
        assert res.label == expected_label, f"Failed for '{title}': got {res.label}"
        assert res.confidence_score >= 0.70


def test_agent_negative_signals(classifier: ClassificationEngine):
    """Test standard intermediary/agency signals."""
    samples = [
        ("Rieltor xizmati mavjud, 50% komissiya", ClassificationLabel.LIKELY_AGENT),
        ("Agentlik orqali beriladi, makler puli bor", ClassificationLabel.LIKELY_AGENT),
        ("Услуги агентства 50%, звонить риелтору", ClassificationLabel.LIKELY_AGENT),
        ("Посреднические услуги, комиссия оплачивается", ClassificationLabel.LIKELY_AGENT),
    ]
    for text, expected_label in samples:
        res = classifier.classify(title="Kvartira", description=text)
        assert res.label == expected_label, f"Failed for '{text}': got {res.label}"
        assert res.confidence_score <= 0.35


def test_contextual_negation_owner_intent(classifier: ClassificationEngine):
    """
    CRITICAL: Phrases where negative words (makler, риелтор) are used in prohibition context
    must be classified as owner intent, NOT agency!
    """
    contextual_samples = [
        "Chilonzorda 2 xonali kvartira. Maklerlar bezovta qilmasin!",
        "Kvartira ijaraga beriladi, makler bezovta qilmasin",
        "Сдам квартиру в Мирабадском районе. Риелторам не беспокоить!",
        "Собственная квартира, агентствам просьба не звонить",
        "Kvartira egasidan, 0% komissiya, maklersiz",
        "Без комиссии! Сдается чистая квартира",
    ]
    for text in contextual_samples:
        res = classifier.classify(title=text)
        assert res.label == ClassificationLabel.LIKELY_OWNER, (
            f"Contextual owner phrase failed: '{text}' classified as {res.label} "
            f"with score {res.confidence_score}"
        )


def test_conflicting_keywords(classifier: ClassificationEngine):
    """
    Listing containing conflicting signals (e.g. mentions 'egasidan' but also explicit '50% komissiya')
    must be flagged for review (NEEDS_REVIEW).
    """
    text = "Kvartira egasidan deb yozilgan, lekin 50% komissiya olinadi agentlik tomonidan."
    res = classifier.classify(title="Kvartira", description=text)
    assert res.label == ClassificationLabel.NEEDS_REVIEW
    # Both positive and negative matched signals should be present in explanation
    signal_types = {s.signal_type for s in res.matched_signals}
    assert "positive" in signal_types or "contextual_owner" in signal_types
    assert "negative" in signal_types


def test_ambiguous_text(classifier: ClassificationEngine):
    """Listing with no clear owner or agent signals should be marked NEEDS_REVIEW."""
    text = "Yakkasaroyda 3 xonali kvartira ijaraga beriladi. Mebel va texnika bor."
    res = classifier.classify(title=text)
    assert res.label == ClassificationLabel.NEEDS_REVIEW
    assert res.confidence_score == 0.50


def test_unicode_and_apostrophe_normalization(classifier: ClassificationEngine):
    """Verify various Unicode apostrophes are handled identically."""
    variants = [
        "O'zimning uyim egasidan",
        "O‘zimning uyim egasidan",
        "Oʻzimning uyim egasidan",
        "O`zimning uyim egasidan",
    ]
    for text in variants:
        res = classifier.classify(title=text)
        assert res.label == ClassificationLabel.LIKELY_OWNER

