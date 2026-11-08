import unittest
from chronos.core import Claim, EvidenceClass, Source, assess_claim
from chronos.evidence import ResearchHypothesis, validate_hypothesis, classify_causal_claim


class CoreTests(unittest.TestCase):
    def test_unsupported_claim_is_not_fact(self):
        c = Claim("Часы остановились из-за магии", EvidenceClass.UNSUPPORTED)
        self.assertEqual(assess_claim(c).status, "unsupported")

    def test_hypothesis_requires_testing(self):
        c = Claim("Конструкция меняет оценку времени", EvidenceClass.HYPOTHESIS)
        self.assertEqual(assess_claim(c).status, "requires_testing")

    def test_interpretation_is_not_causation(self):
        c = Claim("Остановка часов символизирует перелом", EvidenceClass.INTERPRETIVE)
        self.assertEqual(assess_claim(c).status, "interpretation")

    def test_source_count(self):
        s = Source("S1", "Example", "https://example.org")
        c = Claim("Historical claim", EvidenceClass.HISTORICAL, [s])
        self.assertEqual(assess_claim(c).source_count, 1)

    def test_valid_hypothesis(self):
        h = ResearchHypothesis("H1", "Test", "duration estimate", "neutral room")
        self.assertEqual(validate_hypothesis(h), [])

    def test_invalid_hypothesis(self):
        h = ResearchHypothesis("", "", "", "")
        self.assertEqual(len(validate_hypothesis(h)), 4)

    def test_replication_gate(self):
        self.assertEqual(classify_causal_claim(True, True, True),
                         "eligible_for_strong_review")
        self.assertEqual(classify_causal_claim(True, False, True), "preliminary_only")


if __name__ == "__main__":
    unittest.main()
