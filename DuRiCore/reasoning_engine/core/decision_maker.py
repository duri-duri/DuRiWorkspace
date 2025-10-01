"""
Optional compatibility wrapper for DecisionMaker symbol.
If the HDD module exports a different name or none, we keep a lightweight shim.
"""

try:
    from .logical_reasoning_engine import DecisionMaker  # type: ignore
except Exception:
    # fallback: create a no-op shim to keep imports alive; replace if needed
    class DecisionMaker:  # pragma: no cover
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            raise NotImplementedError(
                "DecisionMaker is not exported by logical_reasoning_engine. "
                "Provide the real implementation or adjust imports."
            )


__all__ = ["DecisionMaker"]
