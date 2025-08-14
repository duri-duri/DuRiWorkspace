# ============================
# File: tests/helpers/ready.py (new)
# ============================

import asyncio
from typing import Any

async def ensure_ready(system: Any, reason: str = "test_helper") -> None:
    """Unified READY helper for tests. Prefer calling this in asyncSetUp.
    1) If system.ensure_ready exists → call it.
    2) Else try to set READY on StateManager and wait on ready_event if present.
    """
    if hasattr(system, "ensure_ready"):
        await system.ensure_ready(reason=reason)
        return

    sm = getattr(system, "state_manager", None)
    if sm is not None:
        if hasattr(sm, "set_state"):
            await sm.set_state("ready", reason=reason)
        else:
            setattr(sm, "current_state", "ready")
        # optional barrier
        if hasattr(sm, "ready_event") and not sm.ready_event.is_set():
            sm.ready_event.set()
