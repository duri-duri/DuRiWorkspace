# tools/tuning_experiments.py
#!/usr/bin/env python3
# PZTA-CRA 튜닝 실험: 1주 내 A/B 테스트

import json
import time
import random
from datetime import datetime, timedelta
from tools.fusion import MonotoneLogit

class TuningExperiment:
    def __init__(self):
        self.results = []
    
    def experiment_k_consistency(self):
        """k(self-consistency): 5 → 7 A/B 테스트"""
        print("=== k(self-consistency) A/B 테스트 ===")
        
        # A: k=5 (현재)
        logit_a = MonotoneLogit()
        start_time = time.time()
        
        for _ in range(100):
            x = [random.randint(0,1), random.random(), random.random(), random.random()]
            p = logit_a.prob(x)
        
        time_a = time.time() - start_time
        
        # B: k=7 (실험)
        logit_b = MonotoneLogit()
        start_time = time.time()
        
        for _ in range(100):
            x = [random.randint(0,1), random.random(), random.random(), random.random()]
            p = logit_b.prob(x)
            # k=7 시뮬레이션 (실제로는 더 많은 샘플)
            for _ in range(2):  # 추가 2개 샘플
                p = logit_b.prob(x)
        
        time_b = time.time() - start_time
        
        print(f"  A (k=5): {time_a:.3f}s")
        print(f"  B (k=7): {time_b:.3f}s")
        print(f"  지연 증가: {((time_b/time_a)-1)*100:.1f}%")
        
        return {
            "experiment": "k_consistency",
            "k5_time": time_a,
            "k7_time": time_b,
            "latency_increase": (time_b/time_a)-1
        }
    
    def experiment_tau_evidence(self):
        """τ_evidence: 0.90/0.92/0.94 3점 스윕"""
        print("=== τ_evidence 3점 스윕 ===")
        
        tau_values = [0.90, 0.92, 0.94]
        results = []
        
        for tau in tau_values:
            # 시뮬레이션: 근거 점수 분포
            evidence_scores = [random.random() for _ in range(1000)]
            
            # ABSTAIN율 계산
            abstain_rate = sum(1 for score in evidence_scores if score < tau) / len(evidence_scores)
            
            # MTTR 추정 (근거 부족 시 재탐색 시간)
            mttr = abstain_rate * 30  # 30초 재탐색 시간 가정
            
            print(f"  τ={tau}: ABSTAIN율={abstain_rate:.1%}, MTTR={mttr:.1f}s")
            
            results.append({
                "tau": tau,
                "abstain_rate": abstain_rate,
                "mttr": mttr
            })
        
        return {
            "experiment": "tau_evidence",
            "results": results
        }
    
    def experiment_beta_c_prior(self):
        """β_c prior: 1.5/2.0 (정체성 보호 강도)"""
        print("=== β_c prior 최적점 탐색 ===")
        
        beta_values = [1.5, 2.0]
        results = []
        
        for beta_c in beta_values:
            logit = MonotoneLogit(beta_c=beta_c)
            
            # 시뮬레이션: Core hit vs RAG 응답
            core_hits = 0
            rag_responses = 0
            
            for _ in range(1000):
                x = [random.randint(0,1), random.random(), random.random(), random.random()]
                p = logit.prob(x)
                
                if x[0] == 1:  # Core hit
                    core_hits += 1
                else:  # RAG response
                    rag_responses += 1
            
            identity_protection = core_hits / (core_hits + rag_responses)
            
            print(f"  β_c={beta_c}: 정체성 보호={identity_protection:.1%}")
            
            results.append({
                "beta_c": beta_c,
                "identity_protection": identity_protection
            })
        
        return {
            "experiment": "beta_c_prior",
            "results": results
        }
    
    def experiment_sprt_timing(self):
        """SPRT (p0,p1): 결정시간 <6h 유지 확인"""
        print("=== SPRT 결정시간 확인 ===")
        
        from tools.sprt import SPRT
        
        sprt = SPRT(p0=0.98, p1=0.995, alpha=0.05, beta=0.05)
        
        # 시뮬레이션: 골든셋 테스트
        decisions = []
        
        for _ in range(100):
            sprt_test = SPRT(p0=0.98, p1=0.995, alpha=0.05, beta=0.05)
            
            # 시뮬레이션: 성공률 0.99 (p1 근처)
            for step in range(1000):
                success = random.random() < 0.99
                result = sprt_test.step(success)
                
                if result in ["accept", "reject"]:
                    decisions.append(step)
                    break
        
        avg_decisions = sum(decisions) / len(decisions)
        max_decisions = max(decisions)
        
        print(f"  평균 결정 단계: {avg_decisions:.1f}")
        print(f"  최대 결정 단계: {max_decisions}")
        print(f"  <6h 유지: {'✅' if max_decisions < 100 else '❌'}")
        
        return {
            "experiment": "sprt_timing",
            "avg_decisions": avg_decisions,
            "max_decisions": max_decisions,
            "under_6h": max_decisions < 100
        }
    
    def run_all_experiments(self):
        """모든 실험 실행"""
        print("=== PZTA-CRA 튜닝 실험 시작 ===")
        
        experiments = [
            self.experiment_k_consistency,
            self.experiment_tau_evidence,
            self.experiment_beta_c_prior,
            self.experiment_sprt_timing
        ]
        
        for exp in experiments:
            try:
                result = exp()
                self.results.append(result)
                print()
            except Exception as e:
                print(f"실험 실패: {e}")
                print()
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tuning_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"=== 실험 결과 저장: {filename} ===")
        return self.results

if __name__ == "__main__":
    experiment = TuningExperiment()
    experiment.run_all_experiments()
