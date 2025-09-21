#!/usr/bin/env python3
from .orchestrator import (
    Orchestrator, DuRiCoreAdapter, InnerThoughtAdapter, ExternalLearningAdapter,
    Telemetry, TurnContext, Message
)

class EnhancedDuRiOrchestrator(Orchestrator):
    """
    Minimal enhanced wrapper expected by some integration tests.
    Exposes a `systems` attribute and a compatibility `run_enhanced_turn`.
    """
    def __init__(self) -> None:
        super().__init__()
        self.systems = {
            "core": self.core,
            "inner": self.inner,
            "learning": self.learnr,
        }

    def run_enhanced_turn(self, ctx: TurnContext) -> TurnContext:
        return self.run_turn(ctx)

__all__ = ["EnhancedDuRiOrchestrator", "TurnContext", "Message"]