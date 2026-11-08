from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class EvidenceClass(str, Enum):
    EMPIRICAL = "empirical"
    HISTORICAL = "historical"
    INTERPRETIVE = "interpretive"
    TRADITION = "tradition"
    HYPOTHESIS = "hypothesis"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class Source:
    source_id: str
    title: str
    url: str
    source_type: str = "unspecified"


@dataclass
class Claim:
    text: str
    evidence_class: EvidenceClass
    sources: list[Source] = field(default_factory=list)
    notes: str = ""


@dataclass(frozen=True)
class Assessment:
    status: str
    source_count: int
    caution: str


def assess_claim(claim: Claim) -> Assessment:
    """Conservative evidence triage; not an automated truth detector."""
    count = len(claim.sources)
    if claim.evidence_class == EvidenceClass.UNSUPPORTED:
        return Assessment("unsupported", count, "Не выдавать за установленный факт.")
    if claim.evidence_class == EvidenceClass.HYPOTHESIS:
        return Assessment("requires_testing", count, "Нужен заранее заданный проверяемый протокол.")
    if claim.evidence_class == EvidenceClass.INTERPRETIVE:
        return Assessment("interpretation", count, "Не представлять как причинное доказательство.")
    if claim.evidence_class == EvidenceClass.TRADITION:
        return Assessment("within_tradition", count, "Атрибутировать конкретной традиции или тексту.")
    if count == 0:
        return Assessment("insufficient_sources", 0, "Найти и проверить источники.")
    return Assessment("documented_for_review", count, "Проверить качество и независимость источников.")


def compare_claims(claims: Iterable[Claim]) -> list[Assessment]:
    return [assess_claim(claim) for claim in claims]
