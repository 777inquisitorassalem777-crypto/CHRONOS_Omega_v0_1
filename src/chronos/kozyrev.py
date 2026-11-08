"""Pre-registration guardrails for KZ-01. This module does not assert a result."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass
class KZ01Registration:
    protocol_id: str = 'KZ-01'
    version: str = '1.0'
    hypothesis: str = 'Rotation of a gyroscope changes apparent-weight readings beyond pre-specified instrument and environmental uncertainty.'
    null_hypothesis: str = 'Mean apparent-weight difference between rotating and matched control conditions is zero within the pre-specified equivalence margin.'
    primary_outcome: str = 'Within-block difference in mean balance reading (mg), rotating condition minus motor-off control.'
    conditions: tuple = ('motor_off','rotor_spinning','motor_only_rotor_locked','static_mass')
    randomization: str = 'Computer-generated balanced block order; allocation concealed from the analyst.'
    blinding: str = 'Analyst receives coded condition labels until data cleaning and primary analysis are frozen.'
    sample_size: int = 40
    blocks_per_condition: int = 10
    readings_per_block: int = 60
    primary_test: str = 'Two-sided paired/block-aware model; report effect in mg, 95% CI, raw data, and standardized effect.'
    alpha: float = 0.05
    exclusion_rules: tuple = ('Exclude only documented sensor failure or pre-defined environmental excursions.','Never exclude based on effect direction or statistical significance.')
    controls: tuple = ('thermal','electromagnetic','vibration','airflow','electrostatic','tilt','instrument_drift','acoustic','operator_expectancy')
    safety: str = 'Guard rotating parts; secure rotor; remote operation; emergency stop; no human exposure to hazardous speeds.'
    status: str = 'DRAFT_NOT_PREREGISTERED'

    def validate(self):
        errors=[]
        if self.sample_size < 2 or self.blocks_per_condition < 2: errors.append('sample_size and blocks_per_condition must be >=2')
        if not 0 < self.alpha < 1: errors.append('alpha must be between 0 and 1')
        if len(self.conditions)<3: errors.append('at least three conditions required')
        if not self.primary_outcome or not self.null_hypothesis: errors.append('primary outcome and null hypothesis required')
        return errors

def write_registration(path):
    reg=KZ01Registration(); errors=reg.validate()
    if errors: raise ValueError('; '.join(errors))
    Path(path).write_text(json.dumps(asdict(reg),ensure_ascii=False,indent=2),encoding='utf-8')
    return reg
