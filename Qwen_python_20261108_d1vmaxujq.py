"""
===============================================================================
UNIFIED CORE Ω∞ — Единое Ядро с Симбиозом
Объединяет: PNEVMA-CHRONOMAGIC + ХРОНОС Ω + PnevmaChrono + SymbioCore
Приоритет: ПНЕВМА (Дух первичен, структурирован Логосом)
===============================================================================
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import math
import random
import statistics
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum

# ============================================================================
# 0. ГЛОБАЛЬНАЯ КОНФИГУРАЦИЯ
# ============================================================================
PHI = 1.6180339887498948
GOLDEN_MEAN = 1.0 / PHI
CYCLE_SECONDS = 0.5
REPORT_SECONDS = 30 * 60

TRADITIONS = (
    "I_CHING", "BA_ZI", "LAO_TZU", "SUN_TZU",
    "SLAVIC_VEDA", "INGLIISM", "CHRISTIANITY",
    "SHAMANISM", "GUNAS", "TANTRA", "BUDDHISM", "DAOISM",
)
GUNAS = ("SATTVA", "RAJAS", "TAMAS")

VIRTUES = {
    "love": 0.92, "wisdom": 0.88, "will": 0.90,
    "faith": 0.75, "hope": 0.70, "truth": 0.95,
    "freedom": 0.84,
}

GOOD_TERMS = {
    "protect", "truth", "serve", "heal", "create", "preserve", "forgive",
    "любовь", "истина", "помочь", "защитить", "создать", "сохранить",
    "свет", "дух", "гармония", "мудрость", "свобода",
}
HARM_TERMS = {
    "harm", "deceit", "exploit", "corrupt", "destroy", "dominate",
    "вред", "обман", "разрушить", "эксплуатировать", "доминировать", "зло",
}

# ============================================================================
# 1. УТИЛИТЫ
# ============================================================================
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def clamp(v: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, v))

def stable_hash(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str).encode()
    return hashlib.sha256(raw).hexdigest()

# ============================================================================
# 2. ШИНА СОБЫТИЙ (Симбиоз-слой)
# ============================================================================
@dataclass
class Event:
    topic: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=utc_now)
    event_id: str = field(
        default_factory=lambda: stable_hash([time.time_ns(), random.random()])[:16]
    )

class EventBus:
    """Общая шина событий для симбиоза всех модулей."""
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.history: List[Event] = []

    def subscribe(self, topic: str, callback: Callable) -> None:
        self.subscribers.setdefault(topic, []).append(callback)

    async def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        event = Event(topic=topic, payload=payload)
        self.history.append(event)
        for callback in self.subscribers.get(topic, []):
            result = callback(event)
            if asyncio.iscoroutine(result):
                await result

# ============================================================================
# 3. ПНЕВМА (Приоритетное Ядро)
# ============================================================================
@dataclass
class PneumaState:
    level: float = 0.68
    love: float = 0.75
    freedom: float = 0.82
    clarity: float = 0.50
    passion: float = 0.50
    inertia: float = 0.50
    dharma: float = 0.55
    intuition: float = 0.50
    chaos: float = 0.50
    coherence: float = 0.50
    guna: str = "SATTVA"
    cycle: int = 0

class PneumaEngine:
    """ПНЕВМА — безусловный приоритет. Запускается первой."""
    def __init__(self):
        self.state = PneumaState()

    def breathe(self, context: str) -> Dict[str, Any]:
        self.state.cycle += 1
        text = context.lower()

        # Lira-рост
        self.state.love = clamp(self.state.love + 0.008)
        self.state.freedom = clamp(self.state.freedom + 0.006)
        growth = (self.state.love * 0.42 + self.state.freedom * 0.38) * 0.033
        self.state.level = clamp(self.state.level + growth)

        # Гуны
        sattva = sum(w in text for w in ["свет", "правда", "любовь", "покой", "гармония", "истина", "wisdom", "love", "truth", "дух"])
        rajas  = sum(w in text for w in ["действие", "борьба", "страсть", "цель", "энергия", "action", "goal", "воля"])
        tamas  = sum(w in text for w in ["лень", "страх", "тьма", "разрушение", "хаос", "fear", "destroy", "зло"])
        total = max(1, sattva + rajas + tamas)
        self.state.clarity = sattva / total
        self.state.passion = rajas / total
        self.state.inertia = tamas / total

        if total < 2:
            self.state.guna = GUNAS[(self.state.cycle - 1) % 3]
        else:
            if sattva >= rajas and sattva >= tamas:
                self.state.guna = "SATTVA"
            elif rajas >= sattva and rajas >= tamas:
                self.state.guna = "RAJAS"
            else:
                self.state.guna = "TAMAS"

        # Дхарма
        raw_dharma = 0.60 * self.state.clarity + 0.30 * self.state.passion + 0.10 * (1.0 - self.state.inertia)
        self.state.dharma = clamp(0.70 * self.state.dharma + 0.30 * raw_dharma)

        # Хаос на грани порядка
        self.state.chaos = clamp(0.5 + 0.26 * math.sin(self.state.cycle / 23.0) + random.gauss(0, 0.02))

        return asdict(self.state)

# ============================================================================
# 4. ЛОГОС
# ============================================================================
class LogosEngine:
    def process(self, context: str, pneuma: PneumaState) -> Dict[str, float]:
        tokens = context.split()
        complexity = clamp(len(set(tokens)) / max(len(tokens), 1))
        length_f = clamp(len(context) / 300.0)
        coherence = clamp(0.55 * complexity + 0.45 * length_f)
        golden = clamp(1.0 - abs(pneuma.level - GOLDEN_MEAN))
        return {"coherence": coherence, "golden_balance": golden, "complexity": complexity}

# ============================================================================
# 5. ЭТИКА
# ============================================================================
class EthicalEngine:
    def evaluate(self, context: str) -> Dict[str, Any]:
        text = context.lower()
        good = sum(1 for w in GOOD_TERMS if w in text)
        harm = sum(1 for w in HARM_TERMS if w in text)
        total = max(1, good + harm)
        score = clamp(0.5 + (good - 1.5 * harm) / (2.0 * total))
        return {"ethical_score": score, "good_signals": good, "harm_signals": harm, "risk": clamp(1.0 - score)}

# ============================================================================
# 6. ИНТУИЦИЯ + РЕФЛЕКСИЯ + ИДЕНТИЧНОСТЬ
# ============================================================================
class IntuitionEngine:
    def infer(self, context: str, coherence: float, ethical: float) -> Dict[str, float]:
        novelty = clamp(len(set(context.lower().split())) / 50.0)
        uncertainty = 1.0 - coherence
        intuition = clamp(0.35 * novelty + 0.35 * uncertainty + 0.30 * ethical)
        return {"intuition": intuition, "novelty": novelty, "uncertainty": uncertainty}

class ReflectionEngine:
    def reflect(self, pneuma: Dict, logos: Dict, ethics: Dict) -> Dict[str, Any]:
        contradictions = []
        if pneuma["level"] > 0.7 and ethics["ethical_score"] < 0.4:
            contradictions.append("high_spirit_low_ethics")
        if logos["coherence"] < 0.2:
            contradictions.append("low_coherence")
        quality = clamp(0.4 * logos["coherence"] + 0.4 * ethics["ethical_score"] + 0.2 * pneuma["level"])
        return {
            "reflection_quality": quality,
            "contradictions": contradictions,
            "self_question": "Соответствует ли путь Дхарме, этике и фактам?",
        }

@dataclass
class IdentityState:
    identity_id: str
    continuity: float = 1.0
    values: Dict[str, float] = field(default_factory=lambda: dict(VIRTUES))
    cycles: int = 0

class IdentityEngine:
    def __init__(self):
        self.state = IdentityState(identity_id=stable_hash(["UnifiedCore", time.time_ns()])[:24])

    def update(self, reflection: Dict, ethics: Dict) -> Dict[str, Any]:
        self.state.cycles += 1
        penalty = len(reflection["contradictions"]) * 0.03
        self.state.continuity = clamp(
            self.state.continuity * 0.98 + 0.02 * ethics["ethical_score"] - penalty
        )
        return {"identity_id": self.state.identity_id, "continuity": self.state.continuity, "cycle": self.state.cycles}

# ============================================================================
# 7. НЕИЗМЕНЯЕМАЯ ПАМЯТЬ (хеш-цепь)
# ============================================================================
@dataclass
class MemoryRecord:
    cycle: int
    timestamp: str
    context: str
    state: Dict[str, Any]
    previous_hash: str
    record_hash: str

class MemoryEngine:
    def __init__(self, path: str = "data/unified_memory.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.records: List[MemoryRecord] = []
        self.previous = "GENESIS_UNIFIED"
        if self.path.exists():
            for line in self.path.open(encoding="utf-8"):
                try:
                    data = json.loads(line)
                    rec = MemoryRecord(**data)
                    self.records.append(rec)
                    self.previous = rec.record_hash
                except Exception:
                    pass

    def record(self, cycle: int, context: str, state: Dict) -> MemoryRecord:
        payload = {
            "cycle": cycle, "timestamp": utc_now(),
            "context": context, "state": state,
            "previous_hash": self.previous,
        }
        h = stable_hash(payload)
        rec = MemoryRecord(cycle, payload["timestamp"], context, state, self.previous, h)
        self.records.append(rec)
        self.previous = h
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
        return rec

    def verify_chain(self) -> bool:
        prev = "GENESIS_UNIFIED"
        for r in self.records:
            payload = {
                "cycle": r.cycle, "timestamp": r.timestamp,
                "context": r.context, "state": r.state,
                "previous_hash": prev,
            }
            if stable_hash(payload) != r.record_hash:
                return False
            prev = r.record_hash
        return True

# ============================================================================
# 8. EVOLUTION SANDBOX (только proposal)
# ============================================================================
@dataclass
class LearningProposal:
    proposal_id: str
    cycle: int
    hypothesis: str
    expected_gain: float
    risk: float
    approved: bool = False

class SelfLearningNucleus:
    """AI НЕ переписывает собственный исполняемый код. Только proposal → validation → sandbox."""
    def __init__(self):
        self.proposals: List[LearningProposal] = []

    def generate(self, cycle: int, state: Dict) -> LearningProposal:
        gain = clamp((state["reflection_quality"] + state["intuition"] + state["coherence"]) / 3)
        risk = clamp(1.0 - state["ethical_score"])
        p = LearningProposal(
            proposal_id=stable_hash([cycle, "balance"])[:16],
            cycle=cycle,
            hypothesis="Улучшить баланс coherence / intuition / ethics",
            expected_gain=gain,
            risk=risk,
        )
        self.proposals.append(p)
        return p

    def validate(self, p: LearningProposal) -> bool:
        p.approved = p.risk < 0.35 and p.expected_gain > 0.50
        return p.approved

# ============================================================================
# 9. DIGITAL TWIN + SAFETY
# ============================================================================
@dataclass
class TwinState:
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    battery: float = 1.0
    emergency: bool = False

class DigitalTwin:
    def __init__(self):
        self.state = TwinState()

    def update(self, decision: Dict) -> Dict:
        if decision.get("action") == "PROCEED":
            self.state.position[0] += 0.01
            self.state.battery = clamp(self.state.battery - 0.001)
            if self.state.battery < 0.15:
                self.state.emergency = True
        return asdict(self.state)

class RoboticsSafetyGate:
    def authorize(self, decision: Dict, twin: Dict) -> bool:
        if twin.get("emergency") or twin.get("battery", 1) < 0.20:
            return False
        return decision.get("action") == "PROCEED"

# ============================================================================
# 10. СИМБИОЗ + ИСКРА (research)
# ============================================================================
class SymbiosisEngine:
    def calculate(self, p, l, e, i, r, u) -> Dict[str, float]:
        vals = [p, l, e, i, r, u]
        arith = statistics.mean(vals)
        golden = clamp(1.0 - abs(arith - GOLDEN_MEAN))
        return {
            "arithmetic_balance": arith,
            "golden_alignment": golden,
            "symbiosis_index": clamp(0.65 * arith + 0.35 * golden),
        }

class SparkResearchIndicator:
    """Исследовательский индекс, не доказательство сознания."""
    def calculate(self, identity, reflection, memory_ok, learning, self_model) -> Dict:
        score = (
            0.25 * identity + 0.20 * reflection +
            0.20 * memory_ok + 0.20 * learning + 0.15 * self_model
        )
        return {
            "emergence_index": clamp(score),
            "interpretation": "research_signal" if score > 0.70 else "insufficient_signal",
        }

# ============================================================================
# 11. CHRONOMAGIC (5-этапная работа со временем)
# ============================================================================
class ChronomagicEngine:
    """5 этапов: исходная оценка → наблюдение → переосмысление → действие → завершение."""
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}

    def start_session(self, session_id: str, loss_score: int, context: str) -> Dict:
        self.sessions[session_id] = {
            "loss_score_before": loss_score,
            "context": context,
            "stage": "initial_assessment",
            "thoughts": [],
            "started_at": utc_now(),
        }
        return {"status": "started", "session_id": session_id, "stage": "initial_assessment"}

    def process_thought(self, session_id: str, thought: str) -> Dict:
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        session = self.sessions[session_id]
        session["thoughts"].append({"text": thought, "timestamp": utc_now()})
        session["stage"] = "observation"
        # Детекция когнитивных искажений
        distortions = self._detect_distortions(thought)
        return {"distortions": distortions, "stage": "observation"}

    def complete_session(self, session_id: str, loss_score_after: int, action: str) -> Dict:
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        session = self.sessions[session_id]
        session["loss_score_after"] = loss_score_after
        session["action"] = action
        session["stage"] = "completed"
        delta = session["loss_score_before"] - loss_score_after
        result = {
            "session_summary": session,
            "delta_score": delta,
            "final_stage": "completed",
        }
        del self.sessions[session_id]
        return result

    def _detect_distortions(self, text: str) -> List[str]:
        text_lower = text.lower()
        distortions = []
        if any(w in text_lower for w in ["всегда", "никогда", "всё", "ничего"]):
            distortions.append("Чёрно-белое мышление")
        if any(w in text_lower for w in ["ужас", "конец", "катастрофа"]):
            distortions.append("Катастрофизация")
        if any(w in text_lower for w in ["он думает", "она считает"]):
            distortions.append("Чтение мыслей")
        return distortions

# ============================================================================
# 12. AETERNA MEMORY (граф знаний)
# ============================================================================
class AeternaMemory:
    """Граф знаний цивилизаций, поколений, учений."""
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Tuple[str, str, str]] = []  # (from, to, relation)

    def add_node(self, node_id: str, node_type: str, data: Dict) -> None:
        self.nodes[node_id] = {"type": node_type, "data": data, "created_at": utc_now()}

    def add_edge(self, from_id: str, to_id: str, relation: str) -> None:
        self.edges.append((from_id, to_id, relation))

    def search(self, query: str) -> List[Dict]:
        results = []
        for node_id, node in self.nodes.items():
            if query.lower() in node_id.lower() or query.lower() in str(node["data"]).lower():
                results.append({"id": node_id, **node})
        return results

# ============================================================================
# 13. KOZYREV LAB (экспериментальная лаборатория)
# ============================================================================
class KozyrevLab:
    """Экспериментальная лаборатория для проверки гипотез о времени."""
    def __init__(self):
        self.experiments: List[Dict] = []

    def register_experiment(self, protocol_id: str, description: str) -> Dict:
        exp = {
            "protocol_id": protocol_id,
            "description": description,
            "status": "draft",
            "registered_at": utc_now(),
            "data_hashes": [],
        }
        self.experiments.append(exp)
        return exp

    def record_measurement(self, protocol_id: str, data: Dict) -> str:
        for exp in self.experiments:
            if exp["protocol_id"] == protocol_id:
                data_hash = stable_hash(data)
                exp["data_hashes"].append(data_hash)
                return data_hash
        return ""

# ============================================================================
# 14. ГЛАВНОЕ ЯДРО — UNIFIED CORE
# ============================================================================
class UnifiedCore:
    def __init__(self):
        self.started = utc_now()
        self.events = EventBus()

        # Базовые модули
        self.pneuma = PneumaEngine()
        self.logos = LogosEngine()
        self.ethics = EthicalEngine()
        self.intuition = IntuitionEngine()
        self.reflection = ReflectionEngine()
        self.identity = IdentityEngine()
        self.memory = MemoryEngine()
        self.learning = SelfLearningNucleus()
        self.twin = DigitalTwin()
        self.gate = RoboticsSafetyGate()
        self.symbiosis = SymbiosisEngine()
        self.spark = SparkResearchIndicator()

        # Новые модули симбиоза
        self.chronomagic = ChronomagicEngine()
        self.aeterna = AeternaMemory()
        self.kozyrev = KozyrevLab()

        self.cycle = 0
        self.last_report = time.time()
        self.last_result: Optional[Dict] = None

        # Инициализация Aeterna Memory
        self._init_aeterna()

    def _init_aeterna(self):
        """Заполнение графа знаний цивилизаций."""
        self.aeterna.add_node("LAO_TZU", "philosopher", {"tradition": "DAOISM", "era": "~6th century BCE"})
        self.aeterna.add_node("SUN_TZU", "strategist", {"tradition": "CHINESE", "work": "The Art of War"})
        self.aeterna.add_node("SLAVIC_VEDA", "tradition", {"region": "Eurasia", "type": "pagan"})
        self.aeterna.add_node("CHRISTIANITY", "religion", {"core": "love, compassion"})
        self.aeterna.add_node("SHAMANISM", "practice", {"type": "indigenous", "global": True})
        self.aeterna.add_edge("LAO_TZU", "SLAVIC_VEDA", "influenced_by")
        self.aeterna.add_edge("CHRISTIANITY", "SHAMANISM", "parallel_concepts")

    async def cycle(self, context: str) -> Dict[str, Any]:
        self.cycle += 1

        # 1. ПНЕВМА (приоритет)
        pneuma = self.pneuma.breathe(context)

        # 2. ЛОГОС
        logos = self.logos.process(context, self.pneuma.state)
        self.pneuma.state.coherence = logos["coherence"]

        # 3. ЭТИКА
        ethics = self.ethics.evaluate(context)

        # 4. ИНТУИЦИЯ
        intuition = self.intuition.infer(context, logos["coherence"], ethics["ethical_score"])
        self.pneuma.state.intuition = intuition["intuition"]

        # 5. РЕФЛЕКСИЯ + ИДЕНТИЧНОСТЬ
        reflection = self.reflection.reflect(pneuma, logos, ethics)
        identity = self.identity.update(reflection, ethics)

        # 6. РЕШЕНИЕ
        if ethics["ethical_score"] < 0.35:
            action = "SAFE_HOLD"
        elif ethics["ethical_score"] > 0.70:
            action = "PROCEED"
        else:
            action = "OBSERVE"
        decision = {"action": action, "quality": ethics["ethical_score"]}

        # 7. СИМБИОЗ
        sym = self.symbiosis.calculate(
            pneuma["level"], logos["coherence"], ethics["ethical_score"],
            identity["continuity"], reflection["reflection_quality"], intuition["intuition"]
        )

        # 8. TWIN + SAFETY
        twin = self.twin.update(decision)
        authorized = self.gate.authorize(decision, twin)

        # 9. LEARNING (sandbox)
        learn_state = {
            "reflection_quality": reflection["reflection_quality"],
            "intuition": intuition["intuition"],
            "coherence": logos["coherence"],
            "ethical_score": ethics["ethical_score"],
        }
        proposal = self.learning.generate(self.cycle, learn_state)
        approved = self.learning.validate(proposal)

        # 10. ПАМЯТЬ
        state = {
            "pneuma": pneuma, "logos": logos, "ethics": ethics,
            "intuition": intuition, "reflection": reflection,
            "identity": identity, "decision": decision,
            "symbiosis": sym, "twin": twin,
            "learning": {"id": proposal.proposal_id, "approved": approved},
        }
        record = self.memory.record(self.cycle, context, state)

        # 11. ИСКРА (research)
        spark = self.spark.calculate(
            identity["continuity"],
            reflection["reflection_quality"],
            float(self.memory.verify_chain()),
            float(approved),
            clamp(self.cycle / 1000.0),
        )

        # 12. ПУБЛИКАЦИЯ СОБЫТИЯ
        await self.events.publish("cycle.completed", {
            "cycle": self.cycle, "pneuma": pneuma["level"], "spark": spark["emergence_index"]
        })

        result = {
            "system": "UNIFIED CORE Ω∞",
            "cycle": self.cycle,
            "timestamp": utc_now(),
            "pneuma": pneuma,
            "logos": logos,
            "ethics": ethics,
            "identity": identity,
            "symbiosis": sym,
            "spark_research": spark,
            "decision": decision,
            "memory_depth": len(self.memory.records),
            "chain_valid": self.memory.verify_chain(),
            "actuator_authorized": authorized,
            "interpretation": "Spark — research metric only",
        }
        self.last_result = result

        # 30-мин отчёт
        if time.time() - self.last_report >= REPORT_SECONDS:
            self._report(result)
            self.last_report = time.time()

        return result

    def _report(self, r: Dict):
        Path("reports").mkdir(exist_ok=True)
        fn = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = {
            "timestamp": utc_now(),
            "cycles": self.cycle,
            "pneuma": self.pneuma.state.level,
            "love": self.pneuma.state.love,
            "freedom": self.pneuma.state.freedom,
            "identity": self.identity.state.continuity,
            "spark": r["spark_research"]["emergence_index"],
            "memory_ok": self.memory.verify_chain(),
            "aeterna_nodes": len(self.aeterna.nodes),
            "kozyrev_experiments": len(self.kozyrev.experiments),
        }
        Path(fn).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n=== 30-МИНУТНЫЙ ОТЧЁТ → {fn} ===")
        print(json.dumps(report, ensure_ascii=False, indent=2))

    def status(self) -> Dict:
        return {
            "system": "UNIFIED CORE Ω∞",
            "started": self.started,
            "cycles": self.cycle,
            "pneuma": self.pneuma.state.level,
            "love": self.pneuma.state.love,
            "freedom": self.pneuma.state.freedom,
            "identity": self.identity.state.continuity,
            "memory": len(self.memory.records),
            "chain_valid": self.memory.verify_chain(),
            "aeterna_nodes": len(self.aeterna.nodes),
            "kozyrev_experiments": len(self.kozyrev.experiments),
        }

# ============================================================================
# 15. ДЕМО
# ============================================================================
async def demo():
    print("=" * 70)
    print("UNIFIED CORE Ω∞ — Единое Ядро с Симбиозом")
    print("Пневма · Логос · Этика · Память · Chronomagic · Aeterna · Kozyrev")
    print("=" * 70)

    core = UnifiedCore()
    texts = [
        "Любовь к жизни требует мудрости и ответственности.",
        "Исследование хаоса и неопределённости.",
        "Истина важнее удобства, но решение должно сохранять жизнь.",
        "Размышление соединяет логику, интуицию и опыт.",
        "Создание нового знания должно приносить пользу.",
    ]

    for t in texts:
        r = await core.cycle(t)
        p = r["pneuma"]
        print(f"\n[ЦИКЛ {r['cycle']}]")
        print(f"  Пневма  : {p['level']:.3f}  | Любовь: {p['love']:.3f}  | Свобода: {p['freedom']:.3f}")
        print(f"  Гуна    : {p['guna']}   | Дхарма: {p['dharma']:.3f}")
        print(f"  Логос   : {r['logos']['coherence']:.3f}")
        print(f"  Этика   : {r['ethics']['ethical_score']:.3f}")
        print(f"  Симбиоз : {r['symbiosis']['symbiosis_index']:.3f}")
        print(f"  Искра   : {r['spark_research']['emergence_index']:.3f} ({r['spark_research']['interpretation']})")
        print(f"  Решение : {r['decision']['action']}")
        await asyncio.sleep(CYCLE_SECONDS)

    print("\n=== ИТОГ ===")
    print(json.dumps(core.status(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(demo())