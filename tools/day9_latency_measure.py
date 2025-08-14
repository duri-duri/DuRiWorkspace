#!/usr/bin/env python3
"""
Day 9: 알림 지연 측정 도구
새로운 인터페이스를 사용하여 알림 지연을 측정합니다.
"""

from DuRiCore.config_new.provider import build_provider
from DuRiCore.exporters.metrics import build_sink
from DuRiCore.alerts_new.telemetry import SimAlertProbe, AlertEvaluator
import argparse
import json
import logging
import os
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("day9_latency_measure")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="Day 9: 알림 지연 측정")
    parser.add_argument("--mode", choices=["sim", "real"], default="sim", 
                       help="측정 모드 (sim: 시뮬레이션, real: 실제)")
    parser.add_argument("--trials", type=int, default=600, 
                       help="측정 시도 횟수")
    parser.add_argument("--labels", type=str, default="env=dev,day=9,mode=single", 
                       help="메트릭 라벨 (key=value,key=value 형식)")
    parser.add_argument("--out", type=str, default="var/reports/day9_latency_result.json", 
                       help="결과 JSON 파일 경로")
    parser.add_argument("--seed", type=int, default=None, 
                       help="시뮬레이터 RNG 시드(미지정 시 config 사용)")
    parser.add_argument("--save-samples", type=str, default="", 
                       help="샘플(latency) JSON 저장 경로")
    
    args = parser.parse_args()
    
    try:
        # 설정 제공자 및 메트릭 싱크 빌드
        logger.info("설정 제공자 및 메트릭 싱크 초기화 중...")
        provider = build_provider()
        sink = build_sink(provider)
        
        # Day 9 설정 로드
        timeout_ms = int(provider.get("day9.alert_latency_p95_ms", 1500))
        logger.info(f"설정 로드 완료: timeout_ms={timeout_ms}ms")
        
        # --- sim 파라미터 외부화 ---
        sim_cfg = provider.section("day9.sim")
        seed = args.seed if args.seed is not None else int(sim_cfg.get("seed", 42))
        
        # 알림 프로브 및 평가자 생성
        if args.mode == "sim":
            # config 객체 생성 (SimAlertProbe가 읽을 수 있도록)
            class Config:
                def __init__(self, sim_cfg):
                    # 딕셔너리를 객체로 변환하여 속성 접근 가능하게 함
                    class SimConfig:
                        def __init__(self, data):
                            for key, value in data.items():
                                setattr(self, key, value)
                    
                    self.sim = SimConfig(sim_cfg)
            
            # SimAlertProbe는 이제 baseline profile을 자동으로 사용
            # config가 없어도 안전하게 동작
            config = Config(sim_cfg) if sim_cfg else None
            
            probe = SimAlertProbe(
                seed=seed,
                config=config
            )
            logger.info(f"시뮬레이션 알림 프로브 생성: seed={seed}")
            logger.info(f"[day9] Sim param fingerprint: {probe.param_fingerprint()}")
        else:
            # TODO: Day 10에서 RealAlertProbe 구현
            logger.warning("실제 알림 프로브는 아직 구현되지 않음. 시뮬레이션 모드로 전환")
            probe = SimAlertProbe(seed=seed)
        
        evaluator = AlertEvaluator()
        
        # 알림 성능 평가 실행
        logger.info(f"알림 성능 평가 시작: trials={args.trials}")
        result = evaluator.evaluate(probe, args.trials, timeout_ms, return_samples=bool(args.save_samples))
        
        # 라벨 파싱
        labels = {}
        for pair in args.labels.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                labels[key.strip()] = value.strip()
        
        # 메트릭 방출
        logger.info("메트릭 방출 중...")
        sink.emit_many({
            "alert_latency_p95_ms": result["p95_ms"],
            "alert_timeout_rate": result["timeout_rate"],
            "alert_missing_rate": result["missing_rate"],
            "alerts_total": result["total"],
            "alerts_delivered": result["delivered"],
        }, labels=labels)
        
        # 결과 파일 저장
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # count( timeouts/missings ) 포함 저장
        Path(args.out).write_text(
            json.dumps({k:v for k,v in result.items() if k!="latencies_ms"}, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        logger.info(f"결과 저장 완료: {out_path}")
        
        # 샘플 저장 (필요시)
        if args.save_samples:
            samples_path = Path(args.save_samples)
            samples_path.parent.mkdir(parents=True, exist_ok=True)
            with samples_path.open("w", encoding="utf-8") as f:
                json.dump(result.get("latencies_ms", []), f, ensure_ascii=False)
            logger.info(f"샘플 저장 완료: {samples_path}")
        
        # 결과 출력
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"알림 지연 측정 실패: {e}")
        raise

if __name__ == "__main__":
    main()
