from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class VariantConfig:
    name: str
    temperature: float
    max_tokens: int

def get_variant_config(variant_name: str, cfg: dict) -> VariantConfig:
    v = cfg["variants"][variant_name]["parameters"]
    return VariantConfig(
        name=variant_name,
        temperature=float(v.get("temperature", 0.2)),
        max_tokens=int(v.get("max_tokens", 256)),
    )

def run_variant_logic(payload: dict, vcfg: VariantConfig) -> dict:
    # 실제 모델 호출/비즈니스 로직 자리. 지금은 모의 처리.
    score = (1.0 - vcfg.temperature)  # 온도 낮을수록 안정 점수↑ 라는 가상의 규칙
    latency_ms = 100 + int(vcfg.temperature * 100)
    return {
        "ok": True,
        "score": round(score, 3),
        "latency_ms": latency_ms,
        "used": {"temperature": vcfg.temperature, "max_tokens": vcfg.max_tokens},
        "echo": payload,
    }
