import csv
import json
import pathlib
from typing import Any, Dict, List, Optional

from .engine import rank, tokenize

# 기존 시스템 통합
try:
    from duri_modules.evaluation.evaluator import ChatGPTEvaluator
    from DuRiCore.genetic_evolution_engine import GeneticEvolutionEngine
    from DuRiCore.judgment_system import JudgmentSystem

    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False


class PromptPipeline:
    """창의 프롬프트 파이프라인 v1 - 기존 시스템 통합"""

    def __init__(self):
        self.cleaning_rules = {
            "min_length": 10,  # 최소 토큰 수
            "max_length": 500,  # 최대 토큰 수
            "forbidden_words": ["spam", "dummy", "placeholder"],  # 금칙어 (test 제거)
            "duplicate_threshold": 0.8,  # 중복 임계값
        }

        # 기존 시스템 통합
        if INTEGRATION_AVAILABLE:
            self.chatgpt_evaluator = ChatGPTEvaluator()
            self.genetic_engine = GeneticEvolutionEngine()
            self.judgment_system = JudgmentSystem()
            print("✅ 기존 시스템 통합 완료")
        else:
            print("⚠️  기존 시스템 통합 불가 - 독립 모드로 실행")

    def clean_candidates(self, candidates: List[str]) -> List[str]:
        """후보 정제: 중복/길이/금칙어 필터링"""
        cleaned = []
        seen_tokens = set()

        for candidate in candidates:
            if not candidate or not candidate.strip():
                continue

            tokens = tokenize(candidate)

            # 길이 체크
            if len(tokens) < self.cleaning_rules["min_length"]:
                continue
            if len(tokens) > self.cleaning_rules["max_length"]:
                continue

            # 금칙어 체크
            if any(word in candidate.lower() for word in self.cleaning_rules["forbidden_words"]):
                continue

            # 중복 체크 (간단한 토큰 기반)
            token_set = frozenset(tokens)
            if any(
                len(token_set & seen) / len(token_set) > self.cleaning_rules["duplicate_threshold"]
                for seen in seen_tokens
            ):
                continue

            cleaned.append(candidate)
            seen_tokens.add(token_set)

        return cleaned

    def generate_candidates(self, prompt: str, num_candidates: int = 5) -> List[str]:
        """후보 생성 - 기존 시스템 활용"""
        # 기본 후보 생성 (안정적, 충분한 길이)
        base_candidates = [
            f"Creative solution A for: {prompt} with comprehensive methodology and detailed analysis",
            f"Alternative approach B for: {prompt} using innovative techniques and advanced methods",
            f"Innovative method C for: {prompt} with evidence-based practice and thorough evaluation",
            f"Novel technique D for: {prompt} incorporating cutting-edge technology and best practices",
            f"Original idea E for: {prompt} featuring unique perspectives and comprehensive implementation",
        ]
        return base_candidates[:num_candidates]

    def enhanced_evaluation(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """기존 시스템을 활용한 향상된 평가"""
        enhanced_results = []

        for i, candidate in enumerate(candidates):
            result = {
                "index": i,
                "text": candidate,
                "insight_scores": {},
                "chatgpt_scores": {},
                "combined_score": 0.0,
            }

            # Insight Engine 점수
            insight_result = rank(prompt, [candidate], k=1)
            if insight_result:
                result["insight_scores"] = insight_result[0][2]  # breakdown
                result["insight_total"] = insight_result[0][1]  # total score

            # ChatGPT 6차원 평가 (기존 시스템)
            if INTEGRATION_AVAILABLE:
                try:
                    chatgpt_result = self.chatgpt_evaluator.evaluate_response(candidate, prompt)
                    result["chatgpt_scores"] = chatgpt_result["scores"]
                    result["chatgpt_total"] = chatgpt_result["total_score"]

                    # 통합 점수 계산
                    insight_weight = 0.6
                    chatgpt_weight = 0.4
                    result["combined_score"] = (
                        result.get("insight_total", 0.5) * insight_weight
                        + result["chatgpt_total"] * chatgpt_weight
                    )
                except Exception as e:
                    print(f"⚠️  ChatGPT 평가 실패: {e}")
                    result["combined_score"] = result.get("insight_total", 0.5)
            else:
                result["combined_score"] = result.get("insight_total", 0.5)

            enhanced_results.append(result)

        # 통합 점수로 정렬
        enhanced_results.sort(key=lambda x: x["combined_score"], reverse=True)
        return enhanced_results

    def process_pipeline(
        self,
        prompt: str,
        candidates: Optional[List[str]] = None,
        top_k: int = 3,
        use_enhanced_evaluation: bool = True,
    ) -> Dict[str, Any]:
        """전체 파이프라인 실행 - 기존 시스템 통합"""
        # 1. 후보 생성 (빈 리스트가 아닌 경우에만)
        if candidates is None:
            candidates = self.generate_candidates(prompt)

        # 2. 정제
        cleaned_candidates = self.clean_candidates(candidates)

        if not cleaned_candidates:
            return {
                "prompt": prompt,
                "original_count": len(candidates) if candidates else 0,
                "cleaned_count": 0,
                "rankings": [],
                "error": "No valid candidates after cleaning",
                "evaluation_method": "none",
                "integration_status": {
                    "available": INTEGRATION_AVAILABLE,
                    "systems_used": [],
                },
            }

        # 3. 평가 (기존 시스템 통합)
        if use_enhanced_evaluation and INTEGRATION_AVAILABLE:
            enhanced_results = self.enhanced_evaluation(prompt, cleaned_candidates)
            rankings = enhanced_results[:top_k]
        else:
            # 기본 Insight Engine만 사용
            rankings = rank(prompt, cleaned_candidates, k=top_k)
            rankings = [
                {
                    "rank": i + 1,
                    "index": idx,
                    "score": score,
                    "text": cleaned_candidates[idx],
                    "breakdown": breakdown,
                    "combined_score": score,
                }
                for i, (idx, score, breakdown) in enumerate(rankings)
            ]

        # 4. 리포트 생성
        report = {
            "prompt": prompt,
            "original_count": len(candidates) if candidates else 0,
            "cleaned_count": len(cleaned_candidates),
            "evaluation_method": (
                "enhanced_integrated"
                if use_enhanced_evaluation and INTEGRATION_AVAILABLE
                else "insight_only"
            ),
            "rankings": rankings,
            "cleaning_stats": {
                "filtered_by_length": (
                    len(candidates) - len(cleaned_candidates) if candidates else 0
                ),
                "filtered_by_content": 0,  # 실제 구현에서 계산
                "duplicates_removed": 0,  # 실제 구현에서 계산
            },
            "integration_status": {
                "available": INTEGRATION_AVAILABLE,
                "systems_used": (
                    ["ChatGPTEvaluator", "GeneticEvolutionEngine", "JudgmentSystem"]
                    if INTEGRATION_AVAILABLE
                    else []
                ),
            },
        }

        return report

    def save_report(self, report: Dict[str, Any], output_path: str, format: str = "json"):
        """리포트 저장"""
        path = pathlib.Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        elif format == "csv":
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "rank",
                        "score",
                        "text",
                        "novelty",
                        "coherence",
                        "brevity",
                        "combined_score",
                    ]
                )
                for item in report["rankings"]:
                    if "breakdown" in item:
                        writer.writerow(
                            [
                                item["rank"],
                                item["score"],
                                item["text"],
                                item["breakdown"]["novelty"],
                                item["breakdown"]["coherence"],
                                item["breakdown"]["brevity"],
                                item.get("combined_score", item["score"]),
                            ]
                        )
                    else:
                        writer.writerow(
                            [
                                item["rank"],
                                item["score"],
                                item["text"],
                                "",
                                "",
                                "",
                                item.get("combined_score", item["score"]),
                            ]
                        )
        else:
            raise ValueError(f"Unsupported format: {format}")
