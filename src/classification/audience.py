"""Target audience (Tenant type) detection for apartment rental listings."""

import re
from enum import Enum
from typing import Optional


class TargetAudience(str, Enum):
    """Target audience categories for rental listings."""

    FAMILY = "family"    # Oila uchun / Семейным
    FEMALE = "female"    # Qizlar / Ayollar uchun / Девушкам, студенткам
    MALE = "male"        # Yigitlar / Erkaklar uchun / Парням, студентам
    ANY = "any"          # Barchaga / Belgilanmagan / Для всех

    @property
    def label_uz(self) -> str:
        if self == TargetAudience.FAMILY:
            return "Oila uchun"
        elif self == TargetAudience.FEMALE:
            return "Qizlar uchun"
        elif self == TargetAudience.MALE:
            return "Yigitlar uchun"
        return "Barchaga"

    @property
    def icon(self) -> str:
        if self == TargetAudience.FAMILY:
            return "👨‍👩‍👧"
        elif self == TargetAudience.FEMALE:
            return "👩"
        elif self == TargetAudience.MALE:
            return "👨"
        return "👥"


# Negation patterns (e.g. "studentlarga berilmaydi", "парням не сдаём")
RE_NEG_FEMALE = re.compile(
    r"(?:девушк|студентк|женщин|qizlar|қизлар)[^\.\!\?\n]{0,25}(?:не\s+сда|бер[иы]лмай|мумкин\s+эмас|йўқ|yo['`‘]?q)|"
    r"(?:не\s+сда[её]|бер[иы]лмай)[^\.\!\?\n]{0,25}(?:девушк|студентк|qizlar|қизлар)",
    re.IGNORECASE,
)

RE_NEG_MALE = re.compile(
    r"(?:парн|мальчик|мужчин|yigit|йигит|bollar|болалар|[ўу][ғг]ил)[^\.\!\?\n]{0,25}(?:не\s+сда|бер[иы]лмай|мумкин\s+эмас|йўқ|yo['`‘]?q)|"
    r"(?:не\s+сда[её]|бер[иы]лмай)[^\.\!\?\n]{0,25}(?:парн|yigit|мальчик|болалар|студент)",
    re.IGNORECASE,
)

RE_NEG_FAMILY = re.compile(
    r"(?:семь|семейн|оила|oila)[^\.\!\?\n]{0,25}(?:не\s+сда|бер[иы]лмай|мумкин\s+эмас|йўқ|yo['`‘]?q)|"
    r"(?:не\s+сда[её]|бер[иы]лмай)[^\.\!\?\n]{0,25}(?:семь|семейн|оила|oila)",
    re.IGNORECASE,
)

# Positive patterns
RE_FEMALE = re.compile(
    r"\b(?:faqat\s+)?qiz(?:lar|la)?(?:ga|cha)?\b|"
    r"\bqiz\s+bola(?:ga|lar)?\b|"
    r"\b(?:faqat\s+)?ayol(?:lar)?(?:ga)?\b|"
    r"\bstudentka(?:lar)?(?:ga)?\b|"
    r"\bsheriklikka\s+qiz\b|"
    r"\b(?:только\s+)?девушк(?:ам|е|а|и)\b|"
    r"\b(?:только\s+)?девочк(?:ам|е|и)\b|"
    r"\b(?:только\s+)?женщин(?:ам|е|ы)\b|"
    r"\bстудентк(?:ам|е|и)\b|"
    r"\bженскому\s+полу\b|"
    r"\bқиз(?:лар|ла)?(?:га)?\b",
    re.IGNORECASE,
)

RE_MALE = re.compile(
    r"\b(?:faqat\s+)?yigit(?:lar|la)?(?:ga|ni|cha)?\b|"
    r"\byigit\s+kishi(?:ga)?\b|"
    r"\b(?:talaba\s+)?yigitlar\b|"
    r"\bsheriklikka\s+yigit\b|"
    r"\b(?:faqat\s+)?bollar(?:ga)?\b|"
    r"\b(?:o['`‘]?g['`‘]?il|[ўу][ғг]ил)\s+бол(?:алар|ар)?(?:ga|га)?\b|"
    r"\bбол(?:алар|ар)?(?:га)?\s+(?:кв|уй|ижара|бор|бер)|"
    r"\b(?:только\s+)?парн(?:ям|ю|и)\b|"
    r"\b(?:только\s+)?мальчик(?:ам|у|ов)\b|"
    r"\b(?:только\s+)?мужчин(?:ам|е|ы)\b|"
    r"\bмужскому\s+полу\b|"
    r"\bйигит(?:лар)?(?:га)?\b",
    re.IGNORECASE,
)

RE_FAMILY = re.compile(
    r"\b(?:faqat\s+)?oila(?:ga|viy|cha)?\b|"
    r"\boila\s+(?:uchun|bilan)\b|"
    r"\byosh\s+oila\b|"
    r"\btartibli\s+oila\b|"
    r"\b(?:za[gk]s|nikoh)(?:li|lik|i\s+bor)?\b|"
    r"\b(?:только\s+)?семь(?:е|я|ю|ям)\b|"
    r"\bсемейн(?:ым|ой|ая)\b|"
    r"\bдля\s+семьи\b|"
    r"\bсемейная\s+пара\b|"
    r"\bмолодож[её]н\b|"
    r"\bоила(?:га|вий)?\b",
    re.IGNORECASE,
)


def detect_target_audience(title: str, description: Optional[str] = None) -> str:
    """
    Determine target tenant audience from title and description.
    Returns: 'family', 'female', 'male', or 'any'.
    """
    full_text = f"{title or ''} {description or ''}".lower()
    if not full_text.strip():
        return TargetAudience.ANY.value

    # Check for negations
    neg_fem = bool(RE_NEG_FEMALE.search(full_text))
    neg_male = bool(RE_NEG_MALE.search(full_text))
    neg_fam = bool(RE_NEG_FAMILY.search(full_text))

    # Evaluate positives
    is_fam = bool(RE_FAMILY.search(full_text)) and not neg_fam
    is_fem = bool(RE_FEMALE.search(full_text)) and not neg_fem
    is_male = bool(RE_MALE.search(full_text)) and not neg_male

    matches = []
    if is_fam:
        matches.append(TargetAudience.FAMILY.value)
    if is_fem:
        matches.append(TargetAudience.FEMALE.value)
    if is_male:
        matches.append(TargetAudience.MALE.value)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        # Resolve strict explicit phrases
        if any(w in full_text for w in ["faqat oila", "только семье", "только семейным", "загс", "zaks"]):
            return TargetAudience.FAMILY.value
        if any(w in full_text for w in ["faqat qiz", "только девушк"]):
            return TargetAudience.FEMALE.value
        if any(w in full_text for w in ["faqat yigit", "только парн"]):
            return TargetAudience.MALE.value
        # If open to multiple (e.g. family or students), treat as any
        return TargetAudience.ANY.value

    return TargetAudience.ANY.value


def get_audience_label_uz(audience: str) -> str:
    """Return Uzbek display label for target audience."""
    try:
        return TargetAudience(audience).label_uz
    except ValueError:
        return "Barchaga"


def get_audience_icon(audience: str) -> str:
    """Return emoji icon for target audience."""
    try:
        return TargetAudience(audience).icon
    except ValueError:
        return "👥"
