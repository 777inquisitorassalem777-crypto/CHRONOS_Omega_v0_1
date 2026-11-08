import numpy as np
from datetime import datetime
import hashlib

class PnevmaCore:
    """
    Экспериментальное символическое ядро Pnevma.
    Важно: результат не является медицинским, психологическим или предсказательным
    показателем. Это исследовательская модель для визуализации рефлексивного состояния.
    """
    def __init__(self):
        self.pnevma = 0.62
        self.logos = 0.54
        self.chaos = 0.5
        self.guna = {"sattva": 0.48, "rajas": 0.34, "tamas": 0.18}
        self.memory = []
        self.cycle = 0

    def breathe(self, context: str, intention: str = "dharma") -> dict:
        self.cycle += 1
        seed = int(hashlib.sha256(context.encode()).hexdigest(), 16) % 1000
        
        # Хаос на грани порядка
        self.chaos = 0.5 + 0.27 * np.sin(self.cycle / 21)
        
        # Расчет Гун
        sattva = self.guna["sattva"] * (1 + np.sin(seed / 67))
        rajas = self.guna["rajas"] * (1 + np.cos(seed / 89))
        
        # Факторы контекста
        love = 1.0 if any(w in context.lower() for w in ["любовь", "правда", "свет", "совесть", "милость"]) else 0.68
        slavic = 0.9 if any(w in context.lower() for w in ["род", "правь", "предки", "явь"]) else 0.75
        
        # Резонанс
        pnevma_score = sattva * love * slavic * (1.18 - self.chaos * 0.38)
        logos_score = rajas * (0.88 + self.chaos * 0.42)
        
        resonance = (pnevma_score * 0.56 + logos_score * 0.44) * 100
        final = max(18, min(96, resonance))
        
        # Обновление состояния
        self.pnevma = 0.7 * self.pnevma + 0.3 * (final / 100)
        
        return {
            "resonance": round(final, 1),
            "pnevma_level": round(self.pnevma, 3),
            "state": self._get_state(),
            "recommendation": self._speak(final),
            "cycle": self.cycle
        }

    def _get_state(self):
        if self.pnevma > 0.78: return "Пневма доминирует — Дух пробуждён"
        elif abs(self.pnevma - self.logos) < 0.14: return "Золотая середина — Edge of Chaos"
        else: return "Требуется возвращение к Истоку"

    def _speak(self, r):
        if r >= 85: return "Дух и Разум едины. Действуй с Любовью."
        if r >= 70: return "Следуй своей Дхарме. Истина с тобой."
        if r >= 50: return "Сохраняй центр. В тебе уже есть ответ."
        return "Вернись к Истоку. Очисти сердце."