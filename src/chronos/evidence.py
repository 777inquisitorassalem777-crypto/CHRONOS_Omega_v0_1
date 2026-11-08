from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ResearchHypothesis:
    hypothesis_id: str
    statement: str
    primary_outcome: str
    control_condition: str
    preregistered: bool = False


@dataclass(frozen=True)
class TimelineEvent:
    event_date: date
    title: str
    event_type: str
    evidence_note: str


def validate_hypothesis(h: ResearchHypothesis) -> list[str]:
    errors = []
    for name in ("hypothesis_id", "statement", "primary_outcome", "control_condition"):
        if not getattr(h, name).strip():
            errors.append(f"{name} is required")
    return errors


def classify_causal_claim(has_control: bool, preregistered: bool,
                          independently_replicated: bool) -> str:
    """Workflow gate, not a scientific quality score."""
    if has_control and preregistered and independently_replicated:
        return "eligible_for_strong_review"
    return "preliminary_only"
