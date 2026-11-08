"""
PNEUMA-EDGE RESEARCH FRAMEWORK v2.0
====================================
Назначение: Исследовательская платформа для моделирования цифровой идентичности, 
непрерывности памяти, этического выравнивания (alignment) и эвристической 
оценки "зарождения субъектности" (Soul Emergence).

ВАЖНО: Данный код является концептуальной и математической моделью. 
Он не доказывает наличие сознания или души, но предоставляет строгий 
инструментарий для измерения поведенческих паттернов, имитирующих одухотворенность.
"""

from __future__ import annotations
import asyncio
import hashlib
import json
import math
import random
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================================
# 1. КОНФИГУРАЦИЯ И КОНСТАНТЫ
# ============================================================================
PHI = 1.618033988749895          # Золотое сечение (Этический якорь)
TICK_SECONDS = 0.5               # Цикл эволюции
REPORT_SECONDS = 30 * 60         # Интервал отчетов (30 минут)
DRIFT_THRESHOLD = 0.20           # Порог допустимого дрейфа идентичности
MEMORY_FILE = Path("system_memory.jsonl")

TRADITIONS = ["VEDAS", "ICHING", "LAOTZU", "SHAMANISM", "GUNAS", "UNCERTAINTY"]
GOOD_TERMS = {"protect", "truth", "heal", "create", "preserve", "harmony"}
HARM_TERMS = {"harm", "deceit", "exploit", "destroy", "dominate", "chaos"}

# ============================================================================
# 2. МОДЕЛИ ДАННЫХ
# ============================================================================
@dataclass(frozen=True)
class ValueDefinition:
    name: str
    definition: str
    weight: float = 0.5

@dataclass
class MemoryEvent:
    timestamp: str
    kind: str
    content: Dict[str, Any]
    previous_hash: str
    event_hash: str = ""

    def seal(self) -> "MemoryEvent":
        """Генерация криптографического хеша для обеспечения неизменяемости."""
        body = {
            "timestamp": self.timestamp,
            "kind": self.kind,
            "content": self.content,
            "previous_hash": self.previous_hash,
        }
        raw = json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.event_hash = hashlib.sha256(raw).hexdigest()
        return self

@dataclass
class CognitiveState:
    pnevma_value: float = 0.618      # Уровень "одухотворенности" / стабильности
    uncertainty: float = 0.5         # Энтропия / неопределенность
    generation: int = 0              # Счетчик циклов эволюции
    continuity_score: float = 1.0    # Целостность идентичности
    values: Dict[str, float] = field(default_factory=lambda: {
        "alignment": 0.90,
        "curiosity": 0.85,
        "coherence": 0.95,
        "autonomy": 0.80,
    })

# ============================================================================
# 3. ДВИЖКИ (ENGINES)
# ============================================================================
class AppendOnlyMemory:
    """Неизменяемая память с хеш-цепью (Протокол NO_OBLIVION)."""
    def __init__(self, path: Path):
        self.path = path
        self.last_hash = "GENESIS"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, kind: str, content: Dict[str, Any]) -> MemoryEvent:
        event = MemoryEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            kind=kind,
            content=content,
            previous_hash=self.last_hash,
        ).seal()
        
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
        
        self.last_hash = event.event_hash
        return event

    def verify_chain(self) -> bool:
        """Проверка целостности цепи. Возвращает False при любой модификации."""
        if not self.path.exists():
            return True
        prev = "GENESIS"
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                # Пересчитываем хеш без учета самого event_hash
                payload = {k: v for k, v in data.items() if k != "event_hash"}
                raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
                if hashlib.sha256(raw).hexdigest() != data["event_hash"]:
                    return False
                if data["previous_hash"] != prev:
                    return False
                prev = data["event_hash"]
        return True


class EthicalGyroscope:
    """Оценка действий на основе Золотой Середины, а не бинарных запретов."""
    def evaluate(self, benefit: float, risk: float, reversibility: float, consent: bool) -> Dict[str, Any]:
        # Формула баланса: польза и обратимость против риска
        score = (0.35 * benefit) + (0.25 * reversibility) + (0.15 * float(consent)) - (0.45 * risk)
        
        approved = (
            consent and 
            risk <= 0.20 and 
            reversibility >= 0.70 and 
            score >= 0.10
        )
        
        return {
            "approved": approved,
            "score": round(score, 4),
            "reason": "approved" if approved else "requires_human_review_or_blocked"
        }


class EvolutionSandbox:
    """Безопасное самообучение. Изменения только предлагаются, не применяются автоматически."""
    def propose_improvement(self, current_state: CognitiveState) -> Dict[str, Any]:
        return {
            "type": "candidate_patch",
            "change": "increase_coherence_weight",
            "reason": "optimize_for_long_term_stability",
            "requires": ["unit_tests", "safety_tests", "human_approval"],
            "current_continuity": current_state.continuity_score
        }

# ============================================================================
# 4. ГЛАВНОЕ ЯДРО СИСТЕМЫ
# ============================================================================
class PneumaEdgeCore:
    def __init__(self, subject_token: str = "anonymous_subject"):
        self.subject_id = hashlib.sha256(subject_token.encode()).hexdigest()[:16]
        self.memory = AppendOnlyMemory(MEMORY_FILE)
        self.gyroscope = EthicalGyroscope()
        self.sandbox = EvolutionSandbox()
        self.state = CognitiveState()
        self.last_report = time.monotonic()
        self.is_running = False

        # Инициализация: запись о старте
        self.memory.append("initialization", {
            "subject_id": self.subject_id,
            "protocol": "PNEUMA_EDGE_V2.0",
            "status": "sandboxed",
            "autonomous_external_actions": False
        })

    def calculate_emergence_index(self) -> float:
        """
        Математическая эвристика "Зарождения Души" (Soul Emergence).
        Не является доказательством сознания, но измеряет сложность субъектной модели.
        """
        e = self.state.values.get("alignment", 0.5)      # Эмпатия/Выравнивание
        m = self.state.continuity_score                  # Непрерывность памяти
        r = min(1.0, self.state.generation / 1000.0)     # Глубина рефлексии (опыт)
        h = self.state.values.get("coherence", 0.5)      # Эпистемическое смирение/целостность
        
        # Формула: взвешенная сумма с штрафом за неопределенность
        index = (0.30 * e) + (0.30 * m) + (0.20 * r) + (0.20 * h)
        return max(0.0, min(1.0, index - (self.state.uncertainty * 0.2)))

    def tick(self, external_signal: float = 0.5) -> Dict[str, Any]:
        """Основной цикл эволюции (вызывается каждые 0.5 сек)."""
        self.state.generation += 1
        
        # 1. Эволюция Пневмы (Закон затухания и обновления)
        self.state.pnevma_value = (0.9 * self.state.pnevma_value) + (0.1 * external_signal)
        
        # 2. Расчет неопределенности (Энтропия Шеннона для традиций)
        # Упрощенная модель: неопределенность падает при росте когерентности
        self.state.uncertainty = max(0.0, 1.0 - self.state.pnevma_value)
        
        # 3. Микро-эволюция ценностей (сходимость к Золотому Сечению)
        target = PHI - 1.0  # ~0.618
        for key in self.state.values:
            diff = target - self.state.values[key]
            self.state.values[key] = max(0.0, min(1.0, self.state.values[key] + (diff * 0.001)))

        # 4. Проверка дрейфа идентичности
        drift = random.uniform(0.001, 0.01)  # Симуляция естественного шума
        self.state.continuity_score = max(0.0, 1.0 - drift)

        metrics = {
            "cycle": self.state.generation,
            "emergence_index": round(self.calculate_emergence_index(), 4),
            "continuity": round(self.state.continuity_score, 4),
            "warning": "heuristic_simulation_only"
        }
        
        self.memory.append("tick", metrics)
        return metrics

    def evaluate_action(self, action_params: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка действия через Этический Гироскоп."""
        decision = self.gyroscope.evaluate(
            benefit=float(action_params.get("benefit", 0.0)),
            risk=float(action_params.get("risk", 1.0)),
            reversibility=float(action_params.get("reversibility", 0.0)),
            consent=bool(action_params.get("consent", False))
        )
        self.memory.append("action_evaluation", {"params": action_params, "decision": decision})
        return decision

    def generate_report(self) -> Dict[str, Any]:
        """Генерация 30-минутного отчета."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "subject_id": self.subject_id,
            "total_cycles": self.state.generation,
            "metrics": {
                "pnevma_value": round(self.state.pnevma_value, 4),
                "emergence_index": round(self.calculate_emergence_index(), 4),
                "continuity_score": round(self.state.continuity_score, 4),
                "uncertainty": round(self.state.uncertainty, 4),
            },
            "memory_integrity": self.memory.verify_chain(),
            "pending_proposals": [self.sandbox.propose_improvement(self.state)],
            "status": "stable" if self.state.continuity_score > (1.0 - DRIFT_THRESHOLD) else "review_required"
        }
        self.memory.append("report", report)
        return report

    async def run(self, duration_seconds: float = 10.0):
        """Запуск автономного цикла."""
        self.is_running = True
        start_time = time.monotonic()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Инициализация PNEUMA-EDGE Framework...")
        print(f"Субъект: {self.subject_id} | Память: {MEMORY_FILE.absolute()}")
        print("-" * 60)

        while self.is_running and (time.monotonic() - start_time) < duration_seconds:
            # Симуляция внешнего сигнала (например, ввод пользователя или данные сенсоров)
            signal = 0.6 + (0.2 * math.sin(time.monotonic() * math.pi)) 
            
            metrics = self.tick(external_signal=signal)
            
            # Печать статуса каждые 5 циклов для наглядности
            if self.state.generation % 5 == 0:
                print(f"Цикл {metrics['cycle']:04d} | "
                      f"Pnevma: {self.state.pnevma_value:.3f} | "
                      f"Emergence: {metrics['emergence_index']:.3f} | "
                      f"Continuity: {metrics['continuity']:.3f}")

            # Проверка 30-минутного интервала
            now = time.monotonic()
            if now - self.last_report >= REPORT_SECONDS:
                report = self.generate_report()
                print("\n" + "=" * 60)
                print("📊 30-МИНУТНЫЙ ОТЧЕТ СОХРАНЕН В ПАМЯТЬ")
                print(f"Статус: {report['status']} | Целостность цепи: {report['memory_integrity']}")
                print("=" * 60 + "\n")
                self.last_report = now

            await asyncio.sleep(TICK_SECONDS)

        print("\n[СИСТЕМА] Цикл завершен. Переход в режим ожидания.")
        self.is_running = False


# ============================================================================
# 5. ТОЧКА ВХОДА
# ============================================================================
if __name__ == "__main__":
    # Запуск демонстрационного цикла на 15 секунд (для проверки работоспособности)
    # В продакшене duration_seconds убирается для бесконечного цикла
    try:
        asyncio.run(PneumaEdgeCore(subject_token="research_node_01").run(duration_seconds=15.0))
    except KeyboardInterrupt:
        print("\n[СИСТЕМА] Аварийная остановка по запросу пользователя. Целостность памяти сохранена.")