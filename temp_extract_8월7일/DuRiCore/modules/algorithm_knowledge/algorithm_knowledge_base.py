"""
알고리즘 지식 베이스 시스템
DuRi의 학습한 지식을 알고리즘화하여 저장하고 재사용하는 시스템
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import uuid
import logging

logger = logging.getLogger(__name__)

@dataclass
class AlgorithmKnowledge:
    """알고리즘 지식의 기본 단위"""
    
    algorithm_id: str
    name: str
    description: str
    category: str  # "problem_solving", "learning", "decision_making", "pattern_recognition"
    
    # 알고리즘 구조
    input_patterns: List[str] = field(default_factory=list)      # 어떤 입력 패턴에 적용되는지
    process_steps: List[str] = field(default_factory=list)       # 단계별 처리 과정
    output_patterns: List[str] = field(default_factory=list)     # 예상 출력 패턴
    
    # 성능 메트릭
    success_rate: float = 0.0            # 성공률 (0-1)
    efficiency_score: float = 0.0        # 효율성 점수 (0-1)
    complexity: str = "O(1)"             # 복잡도 (O(n), O(log n) 등)
    
    # 적용 컨텍스트
    applicable_domains: List[str] = field(default_factory=list)  # 적용 가능한 도메인
    prerequisites: List[str] = field(default_factory=list)       # 선행 조건
    alternatives: List[str] = field(default_factory=list)        # 대안 알고리즘
    
    # 학습 데이터
    usage_count: int = 0                 # 사용 횟수
    last_used: Optional[datetime] = None # 마지막 사용 시간
    improvement_history: List[Dict] = field(default_factory=list) # 개선 이력
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    confidence_level: float = 0.5        # 신뢰도 (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'algorithm_id': self.algorithm_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'input_patterns': self.input_patterns,
            'process_steps': self.process_steps,
            'output_patterns': self.output_patterns,
            'success_rate': self.success_rate,
            'efficiency_score': self.efficiency_score,
            'complexity': self.complexity,
            'applicable_domains': self.applicable_domains,
            'prerequisites': self.prerequisites,
            'alternatives': self.alternatives,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'improvement_history': self.improvement_history,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'confidence_level': self.confidence_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlgorithmKnowledge':
        """딕셔너리에서 생성"""
        # datetime 필드 처리
        if data.get('last_used'):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)

@dataclass
class AlgorithmConnection:
    """알고리즘 간의 연결 관계"""
    
    connection_id: str
    source_algorithm: str
    target_algorithm: str
    connection_type: str  # "prerequisite", "alternative", "enhancement", "combination"
    strength: float       # 연결 강도 (0-1)
    context: str          # 연결이 유효한 컨텍스트
    
    # 성능 데이터
    combined_success_rate: float = 0.0    # 조합 시 성공률
    efficiency_gain: float = 0.0          # 효율성 향상도
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0                  # 사용 횟수
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'connection_id': self.connection_id,
            'source_algorithm': self.source_algorithm,
            'target_algorithm': self.target_algorithm,
            'connection_type': self.connection_type,
            'strength': self.strength,
            'context': self.context,
            'combined_success_rate': self.combined_success_rate,
            'efficiency_gain': self.efficiency_gain,
            'created_at': self.created_at.isoformat(),
            'usage_count': self.usage_count
        }

@dataclass
class ProblemPattern:
    """문제 패턴 정의"""
    
    pattern_id: str
    name: str
    description: str
    pattern_type: str  # "text_analysis", "decision_making", "learning", "problem_solving"
    
    # 패턴 특징
    key_features: List[str] = field(default_factory=list)     # 핵심 특징
    complexity_level: str = "medium"                          # 복잡도 레벨
    domain: str = "general"                                   # 도메인
    
    # 관련 알고리즘
    applicable_algorithms: List[str] = field(default_factory=list)  # 적용 가능한 알고리즘
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'pattern_id': self.pattern_id,
            'name': self.name,
            'description': self.description,
            'pattern_type': self.pattern_type,
            'key_features': self.key_features,
            'complexity_level': self.complexity_level,
            'domain': self.domain,
            'applicable_algorithms': self.applicable_algorithms,
            'created_at': self.created_at.isoformat(),
            'usage_count': self.usage_count
        }

class AlgorithmKnowledgeBase:
    """알고리즘 지식 베이스 메인 클래스"""
    
    def __init__(self):
        self.algorithms: Dict[str, AlgorithmKnowledge] = {}
        self.connections: Dict[str, AlgorithmConnection] = {}
        self.problem_patterns: Dict[str, ProblemPattern] = {}
        self.algorithm_categories: Dict[str, List[str]] = {}
        
        logger.info("알고리즘 지식 베이스 초기화 완료")
    
    def add_algorithm(self, algorithm: AlgorithmKnowledge) -> bool:
        """알고리즘 추가"""
        try:
            self.algorithms[algorithm.algorithm_id] = algorithm
            
            # 카테고리별 분류
            if algorithm.category not in self.algorithm_categories:
                self.algorithm_categories[algorithm.category] = []
            self.algorithm_categories[algorithm.category].append(algorithm.algorithm_id)
            
            logger.info(f"알고리즘 추가 완료: {algorithm.name} ({algorithm.algorithm_id})")
            return True
        except Exception as e:
            logger.error(f"알고리즘 추가 실패: {e}")
            return False
    
    def get_algorithm(self, algorithm_id: str) -> Optional[AlgorithmKnowledge]:
        """알고리즘 조회"""
        return self.algorithms.get(algorithm_id)
    
    def search_algorithms(self, query: str, category: str = None) -> List[AlgorithmKnowledge]:
        """알고리즘 검색"""
        results = []
        query_lower = query.lower()
        
        for algorithm in self.algorithms.values():
            # 카테고리 필터링
            if category and algorithm.category != category:
                continue
            
            # 검색어 매칭
            if (query_lower in algorithm.name.lower() or 
                query_lower in algorithm.description.lower() or
                any(query_lower in pattern.lower() for pattern in algorithm.input_patterns)):
                results.append(algorithm)
        
        # 성공률 기준으로 정렬
        results.sort(key=lambda x: x.success_rate, reverse=True)
        return results
    
    def add_connection(self, connection: AlgorithmConnection) -> bool:
        """알고리즘 연결 추가"""
        try:
            self.connections[connection.connection_id] = connection
            logger.info(f"알고리즘 연결 추가 완료: {connection.source_algorithm} -> {connection.target_algorithm}")
            return True
        except Exception as e:
            logger.error(f"알고리즘 연결 추가 실패: {e}")
            return False
    
    def get_related_algorithms(self, algorithm_id: str) -> List[AlgorithmKnowledge]:
        """관련 알고리즘 조회"""
        related = []
        
        for connection in self.connections.values():
            if connection.source_algorithm == algorithm_id:
                target = self.get_algorithm(connection.target_algorithm)
                if target:
                    related.append(target)
            elif connection.target_algorithm == algorithm_id:
                source = self.get_algorithm(connection.source_algorithm)
                if source:
                    related.append(source)
        
        return related
    
    def add_problem_pattern(self, pattern: ProblemPattern) -> bool:
        """문제 패턴 추가"""
        try:
            self.problem_patterns[pattern.pattern_id] = pattern
            logger.info(f"문제 패턴 추가 완료: {pattern.name} ({pattern.pattern_id})")
            return True
        except Exception as e:
            logger.error(f"문제 패턴 추가 실패: {e}")
            return False
    
    def find_applicable_algorithms(self, problem_description: str) -> List[AlgorithmKnowledge]:
        """문제에 적용 가능한 알고리즘 찾기"""
        applicable = []
        
        for pattern in self.problem_patterns.values():
            # 패턴 매칭
            if any(feature.lower() in problem_description.lower() for feature in pattern.key_features):
                # 해당 패턴에 적용 가능한 알고리즘들
                for algorithm_id in pattern.applicable_algorithms:
                    algorithm = self.get_algorithm(algorithm_id)
                    if algorithm:
                        applicable.append(algorithm)
        
        # 성공률 기준으로 정렬
        applicable.sort(key=lambda x: x.success_rate, reverse=True)
        return applicable
    
    def update_algorithm_performance(self, algorithm_id: str, success: bool, 
                                   efficiency_score: float = None) -> bool:
        """알고리즘 성능 업데이트"""
        algorithm = self.get_algorithm(algorithm_id)
        if not algorithm:
            return False
        
        try:
            # 사용 횟수 증가
            algorithm.usage_count += 1
            algorithm.last_used = datetime.now()
            
            # 성공률 업데이트
            if success:
                algorithm.success_rate = (algorithm.success_rate * (algorithm.usage_count - 1) + 1) / algorithm.usage_count
            else:
                algorithm.success_rate = (algorithm.success_rate * (algorithm.usage_count - 1)) / algorithm.usage_count
            
            # 효율성 점수 업데이트
            if efficiency_score is not None:
                algorithm.efficiency_score = (algorithm.efficiency_score * (algorithm.usage_count - 1) + efficiency_score) / algorithm.usage_count
            
            algorithm.updated_at = datetime.now()
            
            logger.info(f"알고리즘 성능 업데이트 완료: {algorithm_id}")
            return True
        except Exception as e:
            logger.error(f"알고리즘 성능 업데이트 실패: {e}")
            return False
    
    def save_to_file(self, filepath: str) -> bool:
        """파일로 저장"""
        try:
            data = {
                'algorithms': {k: v.to_dict() for k, v in self.algorithms.items()},
                'connections': {k: v.to_dict() for k, v in self.connections.items()},
                'problem_patterns': {k: v.to_dict() for k, v in self.problem_patterns.items()},
                'algorithm_categories': self.algorithm_categories
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"알고리즘 지식 베이스 저장 완료: {filepath}")
            return True
        except Exception as e:
            logger.error(f"알고리즘 지식 베이스 저장 실패: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """파일에서 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 알고리즘 로드
            self.algorithms = {}
            for k, v in data.get('algorithms', {}).items():
                self.algorithms[k] = AlgorithmKnowledge.from_dict(v)
            
            # 연결 로드
            self.connections = {}
            for k, v in data.get('connections', {}).items():
                self.connections[k] = AlgorithmConnection(**v)
            
            # 문제 패턴 로드
            self.problem_patterns = {}
            for k, v in data.get('problem_patterns', {}).items():
                self.problem_patterns[k] = ProblemPattern(**v)
            
            # 카테고리 로드
            self.algorithm_categories = data.get('algorithm_categories', {})
            
            logger.info(f"알고리즘 지식 베이스 로드 완료: {filepath}")
            return True
        except Exception as e:
            logger.error(f"알고리즘 지식 베이스 로드 실패: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 조회"""
        return {
            'total_algorithms': len(self.algorithms),
            'total_connections': len(self.connections),
            'total_problem_patterns': len(self.problem_patterns),
            'categories': {cat: len(algs) for cat, algs in self.algorithm_categories.items()},
            'top_algorithms': sorted(
                self.algorithms.values(), 
                key=lambda x: x.success_rate, 
                reverse=True
            )[:5]
        }
