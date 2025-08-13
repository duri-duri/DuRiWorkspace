# ============================
# File: DuRiCore/decorators/ready.py
# Desc: Production-grade READY barrier decorator (+self-heal counters)
# ============================

import asyncio
import functools
import logging
from typing import Callable

logger = logging.getLogger("DuRiCore.integrated_safety_system")


def requires_ready(fn: Callable):
    """
    Ensures IntegratedSafetySystem methods run only after READY.
    Policy:
      1) If a StateManager.ready_event exists, wait briefly (non-blocking to callers).
      2) If still not READY, call ensure_ready(reason="auto:<fn>").
      3) If still not READY, raise RuntimeError (fail fast; surfaces misconfig).
    Also increments self-heal counters on the system instance, if present.
    """
    @functools.wraps(fn)
    async def _wrapped(self, *args, **kwargs):
        # 0) Optional barrier wait
        try:
            sm = getattr(self, "state_manager", None)
            if sm is not None and hasattr(sm, "ready_event"):
                revent = getattr(sm, "ready_event")
                if hasattr(revent, "is_set") and not revent.is_set():
                    try:
                        await asyncio.wait_for(revent.wait(), timeout=1.0)
                    except Exception:
                        pass  # best effort; continue to self-heal below
        except Exception:
            logger.debug("ready_event wait skipped due to exception", exc_info=True)

        # 1) Self-heal attempt
        if not self._is_ready():
            if hasattr(self, "metrics"):
                # lazily add counters if not present
                setattr(self.metrics, "selfheal_ready_attempts", getattr(self.metrics, "selfheal_ready_attempts", 0) + 1)
            logger.warning("⚠️ READY gate blocked in %s → ensure_ready()", fn.__name__)
            try:
                await self.ensure_ready(reason=f"auto:{fn.__name__}")
                if hasattr(self, "metrics") and self._is_ready():
                    setattr(self.metrics, "selfheal_ready_success", getattr(self.metrics, "selfheal_ready_success", 0) + 1)
            except Exception:
                logger.error("ensure_ready() failed in decorator for %s", fn.__name__, exc_info=True)

        # 2) Final decision
        if not self._is_ready():
            raise RuntimeError("READY gate blocked after ensure_ready()")
        return await fn(self, *args, **kwargs)

    return _wrapped
