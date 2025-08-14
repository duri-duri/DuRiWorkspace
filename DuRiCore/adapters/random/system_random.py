from DuRiCore.trace import emit_trace
"""
Random number generator adapters implementing RandomPort interface.
Provides both system random and controlled random for testing.
"""
import random
from typing import List, Any
from core.ports import RandomPort

class SystemRandom(RandomPort):
    """
    System random implementation using Python's random module.
    Suitable for production environments.
    """

    def __init__(self):
        self._random = random.Random()

    def seed(self, seed_value: int) -> None:
        """Set random seed for reproducibility"""
        self._random.seed(seed_value)

    def random(self) -> float:
        """Generate random float between 0.0 and 1.0"""
        return self._random.random()

    def choice(self, choices: List[Any]) -> Any:
        """Choose random element from choices"""
        return self._random.choice(choices)

    def uniform(self, a: float, b: float) -> float:
        """Generate random float between a and b"""
        return self._random.uniform(a, b)

    def normal(self, mu: float=0.0, sigma: float=1.0) -> float:
        """Generate random number from normal distribution"""
        return self._random.normalvariate(mu, sigma)

    def randint(self, a: int, b: int) -> int:
        """Generate random integer between a and b (inclusive)"""
        return self._random.randint(a, b)

class ControlledRandom(RandomPort):
    """
    Controlled random implementation for deterministic testing.
    Allows precise control over random number generation.
    """

    def __init__(self, seed: int=42):
        self._random = random.Random(seed)
        self._sequence: List[float] = []
        self._choice_sequence: List[Any] = []
        self._sequence_index = 0
        self._choice_index = 0

    def seed(self, seed_value: int) -> None:
        """Set random seed for reproducibility"""
        self._random.seed(seed_value)
        self._sequence_index = 0
        self._choice_index = 0

    def random(self) -> float:
        """Generate random float between 0.0 and 1.0"""
        if self._sequence_index < len(self._sequence):
            result = self._sequence[self._sequence_index]
            self._sequence_index += 1
            return result
        return self._random.random()

    def choice(self, choices: List[Any]) -> Any:
        """Choose random element from choices"""
        if self._choice_index < len(self._choice_sequence):
            result = self._choice_sequence[self._choice_index]
            self._choice_index += 1
            return result
        return self._random.choice(choices)

    def randint(self, a: int, b: int) -> int:
        """Generate random integer between a and b (inclusive)"""
        return self._random.randint(a, b)

    def set_random_sequence(self, sequence: List[float]) -> None:
        """Set predefined sequence of random numbers"""
        self._sequence = sequence.copy()
        self._sequence_index = 0

    def set_choice_sequence(self, sequence: List[Any]) -> None:
        """Set predefined sequence of choices"""
        self._choice_sequence = sequence.copy()
        self._choice_index = 0

    def reset_sequences(self) -> None:
        """Reset sequence indices to start"""
        self._sequence_index = 0
        self._choice_index = 0

    def get_remaining_random_count(self) -> int:
        """Get count of remaining predefined random numbers"""
        return max(0, len(self._sequence) - self._sequence_index)

    def get_remaining_choice_count(self) -> int:
        """Get count of remaining predefined choices"""
        return max(0, len(self._choice_sequence) - self._choice_index)