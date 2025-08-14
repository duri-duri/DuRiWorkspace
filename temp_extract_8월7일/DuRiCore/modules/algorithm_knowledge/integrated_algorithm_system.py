"""
통합 알고리즘 지식 시스템
알고리즘 지식 베이스, 선택 엔진, 진화 시스템을 통합한 메인 시스템
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid
import json

from .algorithm_knowledge_base import (
    AlgorithmKnowledge, 
    AlgorithmConnection, 
    ProblemPattern,
    AlgorithmKnowledgeBase
)
from .algorithm_selection_engine import (
    ProblemContext, 
    AlgorithmRecommendation,
    AlgorithmSelectionEngine
)
from .algorithm_evolution_system import (
    AlgorithmEvolutionSystem,
    LearningSession,
    AlgorithmImprovement,
    NewAlgorithm
)

logger = logging.getLogger(__name__)

class IntegratedAlgorithmSystem:
    """통합 알고리즘 지식 시스템"""
    
    def __init__(self):
        # 핵심 컴포넌트 초기화
        self.knowledge_base = AlgorithmKnowledgeBase()
        self.selection_engine = AlgorithmSelectionEngine(self.knowledge_base)
        self.evolution_system = AlgorithmEvolutionSystem(self.knowledge_base)
        
        # 시스템 상태
        self.system_status = "initialized"
        self.last_maintenance = datetime.now()
        
        # 기본 알고리즘 및 패턴 초기화
        self._initialize_default_algorithms()
        self._initialize_default_patterns()
        
        logger.info("통합 알고리즘 지식 시스템 초기화 완료")
    
    def _initialize_default_algorithms(self):
        """기본 알고리즘 초기화"""
        default_algorithms = [
            AlgorithmKnowledge(
                algorithm_id="alg_001",
                name="단계별 문제 해결",
                description="복잡한 문제를 단계별로 분해하여 해결하는 기본 알고리즘",
                category="problem_solving",
                input_patterns=["복잡한 문제", "단계별 접근", "문제 분해"],
                process_steps=[
                    "1. 문제를 작은 단위로 분해",
                    "2. 각 단계별 해결책 도출",
                    "3. 단계별 검증 및 피드백",
                    "4. 전체 해결책 조합"
                ],
                output_patterns=["단계별 해결책", "검증된 결과", "재사용 가능한 패턴"],
                success_rate=0.85,
                efficiency_score=0.8,
                complexity="O(n)",
                applicable_domains=["일반", "학습", "문제해결"],
                confidence_level=0.9
            ),
            AlgorithmKnowledge(
                algorithm_id="alg_002",
                name="패턴 기반 학습",
                description="유사한 패턴을 찾아 학습 효율성을 높이는 알고리즘",
                category="learning",
                input_patterns=["학습", "패턴", "유사성", "연결"],
                process_steps=[
                    "1. 새로운 정보와 기존 지식 연결",
                    "2. 공통 패턴 식별",
                    "3. 패턴 기반 일반화",
                    "4. 새로운 상황에 적용"
                ],
                output_patterns=["패턴 인식", "일반화된 지식", "적용 가능한 원리"],
                success_rate=0.78,
                efficiency_score=0.75,
                complexity="O(log n)",
                applicable_domains=["학습", "교육", "연구"],
                confidence_level=0.8
            ),
            AlgorithmKnowledge(
                algorithm_id="alg_003",
                name="의사결정 트리",
                description="여러 선택지 중 최적의 결정을 내리는 알고리즘",
                category="decision_making",
                input_patterns=["의사결정", "선택", "우선순위", "평가"],
                process_steps=[
                    "1. 선택지 식별 및 나열",
                    "2. 각 선택지의 장단점 분석",
                    "3. 기준별 가중치 부여",
                    "4. 최적 선택지 결정"
                ],
                output_patterns=["최적 선택", "근거", "대안"],
                success_rate=0.82,
                efficiency_score=0.7,
                complexity="O(n log n)",
                applicable_domains=["비즈니스", "개인", "전략"],
                confidence_level=0.85
            )
        ]
        
        for algorithm in default_algorithms:
            self.knowledge_base.add_algorithm(algorithm)
        
        logger.info(f"기본 알고리즘 {len(default_algorithms)}개 초기화 완료")
    
    def _initialize_default_patterns(self):
        """기본 문제 패턴 초기화"""
        default_patterns = [
            ProblemPattern(
                pattern_id="pattern_001",
                name="복잡한 문제 해결",
                description="여러 단계와 요소가 얽힌 복잡한 문제",
                pattern_type="problem_solving",
                key_features=["복잡", "단계별", "분해", "통합"],
                complexity_level="complex",
                domain="일반",
                applicable_algorithms=["alg_001"]
            ),
            ProblemPattern(
                pattern_id="pattern_002",
                name="새로운 지식 학습",
                description="기존 지식과 연결하여 새로운 정보를 학습",
                pattern_type="learning",
                key_features=["학습", "새로운", "연결", "패턴"],
                complexity_level="medium",
                domain="교육",
                applicable_algorithms=["alg_002"]
            ),
            ProblemPattern(
                pattern_id="pattern_003",
                name="중요한 의사결정",
                description="여러 선택지 중 최적의 결정을 내려야 하는 상황",
                pattern_type="decision_making",
                key_features=["의사결정", "선택", "우선순위", "평가"],
                complexity_level="medium",
                domain="비즈니스",
                applicable_algorithms=["alg_003"]
            )
        ]
        
        for pattern in default_patterns:
            self.knowledge_base.add_problem_pattern(pattern)
        
        logger.info(f"기본 문제 패턴 {len(default_patterns)}개 초기화 완료")
    
    def solve_problem(self, problem_description: str, domain: str = "general", 
                     complexity_level: str = "medium") -> AlgorithmRecommendation:
        """
        문제 해결을 위한 최적 알고리즘 추천
        """
        try:
            # 문제 컨텍스트 생성
            problem_context = ProblemContext(
                context_id=str(uuid.uuid4()),
                description=problem_description,
                domain=domain,
                complexity_level=complexity_level,
                key_features=self._extract_problem_features(problem_description),
                constraints=[],
                goals=["문제 해결", "효율적인 접근"]
            )
            
            # 최적 알고리즘 선택
            recommendation = self.selection_engine.select_optimal_algorithm(problem_context)
            
            if recommendation:
                logger.info(f"문제 해결 알고리즘 추천 완료: {recommendation.algorithm.name}")
            else:
                logger.warning("적합한 알고리즘을 찾지 못했습니다")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"문제 해결 실패: {e}")
            return None
    
    def _extract_problem_features(self, description: str) -> List[str]:
        """문제 설명에서 특징 추출"""
        # 간단한 키워드 추출 (실제로는 NLP 라이브러리 사용)
        keywords = description.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        features = [word for word in keywords if word not in stop_words and len(word) > 2]
        return features[:5]  # 상위 5개 특징
    
    def learn_from_experience(self, algorithm_id: str, problem_context: str, 
                            success: bool, efficiency_score: float, 
                            execution_time: float, feedback: str = "") -> bool:
        """
        경험으로부터 학습
        """
        try:
            # 진화 시스템에 학습 데이터 전달
            result = self.evolution_system.learn_from_execution(
                algorithm_id, problem_context, success, 
                efficiency_score, execution_time, feedback
            )
            
            if result:
                logger.info(f"경험 학습 완료: {algorithm_id}")
                
                # 시스템 상태 업데이트
                self._update_system_status()
            
            return result
            
        except Exception as e:
            logger.error(f"경험 학습 실패: {e}")
            return False
    
    def add_new_algorithm(self, name: str, description: str, category: str,
                         input_patterns: List[str], process_steps: List[str],
                         output_patterns: List[str], applicable_domains: List[str]) -> str:
        """
        새로운 알고리즘 추가
        """
        try:
            algorithm = AlgorithmKnowledge(
                algorithm_id=str(uuid.uuid4()),
                name=name,
                description=description,
                category=category,
                input_patterns=input_patterns,
                process_steps=process_steps,
                output_patterns=output_patterns,
                applicable_domains=applicable_domains,
                success_rate=0.5,  # 초기값
                efficiency_score=0.5,  # 초기값
                complexity="O(n)",  # 기본값
                confidence_level=0.6  # 초기값
            )
            
            if self.knowledge_base.add_algorithm(algorithm):
                logger.info(f"새로운 알고리즘 추가 완료: {name}")
                return algorithm.algorithm_id
            else:
                logger.error("알고리즘 추가 실패")
                return None
                
        except Exception as e:
            logger.error(f"새로운 알고리즘 추가 실패: {e}")
            return None
    
    def add_problem_pattern(self, name: str, description: str, pattern_type: str,
                          key_features: List[str], complexity_level: str, 
                          domain: str, applicable_algorithms: List[str]) -> str:
        """
        새로운 문제 패턴 추가
        """
        try:
            pattern = ProblemPattern(
                pattern_id=str(uuid.uuid4()),
                name=name,
                description=description,
                pattern_type=pattern_type,
                key_features=key_features,
                complexity_level=complexity_level,
                domain=domain,
                applicable_algorithms=applicable_algorithms
            )
            
            if self.knowledge_base.add_problem_pattern(pattern):
                logger.info(f"새로운 문제 패턴 추가 완료: {name}")
                return pattern.pattern_id
            else:
                logger.error("문제 패턴 추가 실패")
                return None
                
        except Exception as e:
            logger.error(f"새로운 문제 패턴 추가 실패: {e}")
            return None
    
    def search_algorithms(self, query: str, category: str = None) -> List[AlgorithmKnowledge]:
        """알고리즘 검색"""
        return self.knowledge_base.search_algorithms(query, category)
    
    def get_algorithm(self, algorithm_id: str) -> Optional[AlgorithmKnowledge]:
        """알고리즘 조회"""
        return self.knowledge_base.get_algorithm(algorithm_id)
    
    def get_related_algorithms(self, algorithm_id: str) -> List[AlgorithmKnowledge]:
        """관련 알고리즘 조회"""
        return self.knowledge_base.get_related_algorithms(algorithm_id)
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """시스템 통계 조회"""
        try:
            # 기본 통계
            base_stats = self.knowledge_base.get_statistics()
            
            # 선택 엔진 통계
            selection_stats = self.selection_engine.get_selection_statistics()
            
            # 진화 시스템 통계
            evolution_stats = self.evolution_system.get_evolution_statistics()
            
            # 통합 통계
            integrated_stats = {
                'system_status': self.system_status,
                'last_maintenance': self.last_maintenance.isoformat(),
                'total_components': {
                    'algorithms': base_stats.get('total_algorithms', 0),
                    'connections': base_stats.get('total_connections', 0),
                    'problem_patterns': base_stats.get('total_problem_patterns', 0),
                    'learning_sessions': evolution_stats.get('total_learning_sessions', 0),
                    'improvements': evolution_stats.get('total_improvements', 0),
                    'new_algorithms': evolution_stats.get('total_new_algorithms', 0)
                },
                'performance_metrics': {
                    'average_success_rate': self._calculate_average_success_rate(),
                    'average_efficiency': self._calculate_average_efficiency(),
                    'evolution_rate': evolution_stats.get('evolution_rate', 0),
                    'selection_confidence': selection_stats.get('average_confidence', 0)
                },
                'recent_activities': {
                    'recent_selections': selection_stats.get('recent_selections', []),
                    'recent_improvements': evolution_stats.get('recent_improvements', []),
                    'recent_new_algorithms': evolution_stats.get('recent_new_algorithms', [])
                }
            }
            
            return integrated_stats
            
        except Exception as e:
            logger.error(f"시스템 통계 조회 실패: {e}")
            return {}
    
    def _calculate_average_success_rate(self) -> float:
        """평균 성공률 계산"""
        algorithms = list(self.knowledge_base.algorithms.values())
        if not algorithms:
            return 0.0
        
        total_success_rate = sum(alg.success_rate for alg in algorithms)
        return total_success_rate / len(algorithms)
    
    def _calculate_average_efficiency(self) -> float:
        """평균 효율성 계산"""
        algorithms = list(self.knowledge_base.algorithms.values())
        if not algorithms:
            return 0.0
        
        total_efficiency = sum(alg.efficiency_score for alg in algorithms)
        return total_efficiency / len(algorithms)
    
    def _update_system_status(self):
        """시스템 상태 업데이트"""
        try:
            # 성능 지표 계산
            avg_success_rate = self._calculate_average_success_rate()
            avg_efficiency = self._calculate_average_efficiency()
            
            # 시스템 상태 결정
            if avg_success_rate > 0.8 and avg_efficiency > 0.7:
                self.system_status = "optimal"
            elif avg_success_rate > 0.6 and avg_efficiency > 0.5:
                self.system_status = "good"
            elif avg_success_rate > 0.4 and avg_efficiency > 0.3:
                self.system_status = "fair"
            else:
                self.system_status = "needs_improvement"
            
            # 유지보수 시간 업데이트
            self.last_maintenance = datetime.now()
            
        except Exception as e:
            logger.error(f"시스템 상태 업데이트 실패: {e}")
    
    def perform_maintenance(self) -> bool:
        """시스템 유지보수 수행"""
        try:
            logger.info("시스템 유지보수 시작")
            
            # 1. 사용되지 않는 알고리즘 정리
            self._cleanup_unused_algorithms()
            
            # 2. 성능이 낮은 알고리즘 개선
            self._improve_low_performance_algorithms()
            
            # 3. 새로운 알고리즘 생성 시도
            self._generate_new_algorithms_for_patterns()
            
            # 4. 시스템 상태 업데이트
            self._update_system_status()
            
            logger.info("시스템 유지보수 완료")
            return True
            
        except Exception as e:
            logger.error(f"시스템 유지보수 실패: {e}")
            return False
    
    def _cleanup_unused_algorithms(self):
        """사용되지 않는 알고리즘 정리"""
        try:
            unused_algorithms = []
            
            for algorithm in self.knowledge_base.algorithms.values():
                # 30일 이상 사용되지 않고 성공률이 낮은 알고리즘
                if (algorithm.usage_count < 2 and 
                    (not algorithm.last_used or 
                     (datetime.now() - algorithm.last_used).days > 30) and
                    algorithm.success_rate < 0.3):
                    unused_algorithms.append(algorithm.algorithm_id)
            
            # 정리 실행
            for algorithm_id in unused_algorithms:
                if algorithm_id in self.knowledge_base.algorithms:
                    del self.knowledge_base.algorithms[algorithm_id]
                    logger.info(f"사용되지 않는 알고리즘 정리: {algorithm_id}")
            
        except Exception as e:
            logger.error(f"사용되지 않는 알고리즘 정리 실패: {e}")
    
    def _improve_low_performance_algorithms(self):
        """성능이 낮은 알고리즘 개선"""
        try:
            low_performance_algorithms = []
            
            for algorithm in self.knowledge_base.algorithms.values():
                if (algorithm.success_rate < 0.5 or 
                    algorithm.efficiency_score < 0.4) and algorithm.usage_count > 5:
                    low_performance_algorithms.append(algorithm.algorithm_id)
            
            # 개선 시도
            for algorithm_id in low_performance_algorithms:
                self.evolution_system._trigger_evolution(algorithm_id)
                
        except Exception as e:
            logger.error(f"성능이 낮은 알고리즘 개선 실패: {e}")
    
    def _generate_new_algorithms_for_patterns(self):
        """패턴에 대한 새로운 알고리즘 생성 시도"""
        try:
            # 적용 가능한 알고리즘이 적은 패턴 찾기
            patterns_needing_algorithms = []
            
            for pattern in self.knowledge_base.problem_patterns.values():
                if len(pattern.applicable_algorithms) < 2:
                    patterns_needing_algorithms.append(pattern)
            
            # 새로운 알고리즘 생성 시도
            for pattern in patterns_needing_algorithms[:3]:  # 상위 3개만
                new_algorithm = self.evolution_system.generate_new_algorithm(
                    pattern.description
                )
                if new_algorithm:
                    logger.info(f"패턴을 위한 새로운 알고리즘 생성: {pattern.name}")
                    
        except Exception as e:
            logger.error(f"새로운 알고리즘 생성 실패: {e}")
    
    def save_system_state(self, filepath: str) -> bool:
        """시스템 상태 저장"""
        try:
            # 알고리즘 지식 베이스 저장
            knowledge_base_saved = self.knowledge_base.save_to_file(f"{filepath}_knowledge.json")
            
            # 진화 데이터 저장
            evolution_data_saved = self.evolution_system.save_evolution_data(f"{filepath}_evolution.json")
            
            # 시스템 설정 저장
            system_config = {
                'system_status': self.system_status,
                'last_maintenance': self.last_maintenance.isoformat(),
                'evolution_parameters': {
                    'evolution_threshold': self.evolution_system.evolution_threshold,
                    'improvement_threshold': self.evolution_system.improvement_threshold,
                    'combination_probability': self.evolution_system.combination_probability
                }
            }
            
            with open(f"{filepath}_config.json", 'w', encoding='utf-8') as f:
                json.dump(system_config, f, ensure_ascii=False, indent=2)
            
            # 모든 저장이 성공했는지 확인
            if knowledge_base_saved and evolution_data_saved:
                logger.info(f"시스템 상태 저장 완료: {filepath}")
                return True
            else:
                logger.warning("일부 데이터 저장 실패")
                return False
                
        except Exception as e:
            logger.error(f"시스템 상태 저장 실패: {e}")
            return False
    
    def load_system_state(self, filepath: str) -> bool:
        """시스템 상태 로드"""
        try:
            # 알고리즘 지식 베이스 로드
            knowledge_base_loaded = self.knowledge_base.load_from_file(f"{filepath}_knowledge.json")
            
            # 진화 데이터 로드
            evolution_loaded = False
            try:
                with open(f"{filepath}_evolution.json", 'r', encoding='utf-8') as f:
                    evolution_data = json.load(f)
                logger.info("진화 데이터 로드 완료")
                evolution_loaded = True
            except FileNotFoundError:
                logger.info("진화 데이터 파일이 없습니다. 새로 시작합니다.")
            except json.JSONDecodeError:
                logger.warning("진화 데이터 파일이 손상되었습니다. 새로 시작합니다.")
            
            # 시스템 설정 로드
            config_loaded = False
            try:
                with open(f"{filepath}_config.json", 'r', encoding='utf-8') as f:
                    system_config = json.load(f)
                
                self.system_status = system_config.get('system_status', 'initialized')
                if system_config.get('last_maintenance'):
                    self.last_maintenance = datetime.fromisoformat(system_config['last_maintenance'])
                
                # 진화 파라미터 복원
                evolution_params = system_config.get('evolution_parameters', {})
                self.evolution_system.evolution_threshold = evolution_params.get('evolution_threshold', 0.1)
                self.evolution_system.improvement_threshold = evolution_params.get('improvement_threshold', 0.05)
                self.evolution_system.combination_probability = evolution_params.get('combination_probability', 0.3)
                
                logger.info("시스템 설정 로드 완료")
                config_loaded = True
            except FileNotFoundError:
                logger.info("시스템 설정 파일이 없습니다. 기본값을 사용합니다.")
            except json.JSONDecodeError:
                logger.warning("시스템 설정 파일이 손상되었습니다. 기본값을 사용합니다.")
            
            # 지식 베이스는 반드시 로드되어야 함
            if knowledge_base_loaded:
                logger.info(f"시스템 상태 로드 완료: {filepath}")
                return True
            else:
                logger.error("지식 베이스 로드 실패")
                return False
                
        except Exception as e:
            logger.error(f"시스템 상태 로드 실패: {e}")
            return False
