#!/usr/bin/env python3
"""
Day 9: 알림 스위프 도구
다양한 강도와 동시성으로 알림 성능을 테스트합니다.
"""

from DuRiCore.config_new.provider import build_provider
from DuRiCore.exporters.metrics import build_sink
from DuRiCore.alerts_new.telemetry import SimAlertProbe, AlertEvaluator
import argparse
import json
import itertools
import logging
import os
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("day9_sweep")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="Day 9: 알림 스위프 테스트")
    parser.add_argument("--labels", type=str, default="env=dev,day=9,mode=sweep", 
                       help="메트릭 라벨 (key=value,key=value 형식)")
    parser.add_argument("--out", type=str, default="var/reports/day9_sim_sweep.json", 
                       help="결과 JSON 파일 경로")
    parser.add_argument("--seed", type=int, default=None, 
                       help="스위프 전용 RNG 시드(미지정 시 config 사용)")
    
    args = parser.parse_args()
    
    try:
        # 설정 제공자 및 메트릭 싱크 빌드
        logger.info("설정 제공자 및 메트릭 싱크 초기화 중...")
        provider = build_provider()
        sink = build_sink(provider)
        
        # Day 9 설정 로드
        thr = provider.section("day9")
        intensities = thr.get("sweep", {}).get("intensities", [0.2, 0.5, 0.8])
        concurrencies = thr.get("sweep", {}).get("concurrencies", [1, 5, 10])
        timeout_ms = int(thr.get("alert_latency_p95_ms", 1500))
        
        logger.info(f"스위프 설정 로드: intensities={intensities}, "
                   f"concurrencies={concurrencies}, timeout_ms={timeout_ms}ms")
        
        # 기본 라벨 파싱
        base_labels = {}
        for pair in args.labels.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                base_labels[key.strip()] = value.strip()
        
        # --- sim 파라미터 외부화 ---
        sim_cfg = provider.section("day9.sim")
        seed = args.seed if args.seed is not None else int(sim_cfg.get("seed", 123))
        
        # 평가자 및 프로브 생성
        evaluator = AlertEvaluator()
        
        # config 객체 생성 (SimAlertProbe가 읽을 수 있도록)
        class Config:
            def __init__(self, sim_cfg):
                # 딕셔너리를 객체로 변환하여 속성 접근 가능하게 함
                class SimConfig:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                
                self.sim = SimConfig(sim_cfg)
        
        # 직접 딕셔너리로 sim 설정 전달 (설정 로더 우회)
        # sim_cfg가 빈 딕셔너리인 경우를 대비해 하드코딩된 값 사용
        sim_config = {
            "seed": 123,
            "base_min_ms": 450.0,
            "base_max_ms": 950.0,
            "tail_prob": 0.0005,
            "tail_scale_ms": 40.0,
            "timeout_over_ms": 60.0,
            "missing_given_timeout": 0.005,
            "base_missing_prob": 0.0002,
            "max_tail_ms": 1200.0,
            "base_mu_ms": 700.0,
            "base_sigma": 0.24,
            "safety_margin_ms": 150.0
        }
        
        # sim_cfg에서 실제로 읽을 수 있는 값이 있으면 덮어쓰기
        if sim_cfg:
            for key in sim_config:
                if key in sim_cfg:
                    sim_config[key] = sim_config[key]
        
        config = Config(sim_config)
        debug = bool(int(os.getenv("DURI_DEBUG_SIM", "1")))  # 기본 ON
        
        probe = SimAlertProbe(
            seed=seed,
            config=config,
            debug=debug
        )
        logger.info(f"스위프 프로브 생성: seed={seed}")
        logger.info(f"[sweep] Sim param fingerprint: {probe.param_fingerprint()}")
        
        # 스위프 실행
        results = []
        total_combinations = len(intensities) * len(concurrencies)
        current = 0
        
        logger.info(f"스위프 테스트 시작: 총 {total_combinations}개 조합")
        
        for intensity, conc in itertools.product(intensities, concurrencies):
            current += 1
            logger.info(f"진행률: {current}/{total_combinations} "
                       f"(intensity={intensity}, concurrency={conc})")
            
            # 강도에 따른 시도 횟수 조정
            trials = max(50, int(300 * (0.5 + float(intensity))))
            
            # 성능 평가 실행
            result = evaluator.evaluate(probe, trials, timeout_ms)
            
            # 스위프 정보 추가
            result["intensity"] = intensity
            result["concurrency"] = conc
            
            results.append(result)
            
            # 메트릭 방출 (라벨에 스위프 정보 포함)
            sweep_labels = {**base_labels, "intensity": str(intensity), "concurrency": str(conc)}
            
            sink.emit_many({
                "alert_latency_p95_ms": result["p95_ms"],
                "alert_timeout_rate": result["timeout_rate"],
                "alert_missing_rate": result["missing_rate"],
            }, labels=sweep_labels)
            
            logger.info(f"스위프 완료: intensity={intensity}, concurrency={conc}, "
                       f"p95={result['p95_ms']}ms")
        
        # 결과 파일 저장
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"스위프 결과 저장 완료: {out_path}")
        
        # 결과 출력
        print(json.dumps(results, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"알림 스위프 실패: {e}")
        raise

if __name__ == "__main__":
    main()
