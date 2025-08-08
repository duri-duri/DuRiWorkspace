"""
Day 6-2: 진화 서비스
Truth Memory 자동 진화 및 패턴 기반 학습 시스템
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from collections import Counter, defaultdict

from ..models.memory import MemoryEntry
# from ..utils.retry_decorator import retry_on_db_error

logger = logging.getLogger(__name__)

class EvolutionService:
    """진화 서비스 - Truth Memory 자동 진화 및 패턴 학습"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.pattern_threshold = 0.7  # 패턴 감지 임계값
        self.evolution_confidence = 0.8  # 진화 신뢰도 임계값
        
    # @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def auto_evolve_truth_memories(self) -> Dict[str, Any]:
        """새로운 성공/실패 패턴에 따라 Truth Memory 자동 진화"""
        try:
            evolution_results = {
                "evolved_truths": [],
                "new_truths": [],
                "modified_truths": [],
                "deleted_truths": [],
                "patterns_detected": 0,
                "evolution_confidence": 0.0
            }
            
            # 1. 최근 Medium Memory에서 강한 패턴 감지
            recent_patterns = self._detect_strong_patterns_in_medium()
            evolution_results["patterns_detected"] = len(recent_patterns)
            
            # 2. 각 패턴에 대해 Truth Memory와 비교
            for pattern in recent_patterns:
                evolution_result = self._process_pattern_evolution(pattern)
                if evolution_result:
                    evolution_results["evolved_truths"].append(evolution_result)
            
            # 3. 새로운 Truth Memory 생성
            new_truths = self._create_new_truth_memories(recent_patterns)
            evolution_results["new_truths"] = new_truths
            
            # 4. 기존 Truth Memory 수정
            modified_truths = self._modify_existing_truth_memories(recent_patterns)
            evolution_results["modified_truths"] = modified_truths
            
            # 5. 신뢰도 낮은 Truth Memory 삭제
            deleted_truths = self._cleanup_low_confidence_truths()
            evolution_results["deleted_truths"] = deleted_truths
            
            # 6. 진화 신뢰도 계산
            evolution_results["evolution_confidence"] = self._calculate_evolution_confidence(
                evolution_results
            )
            
            logger.info(f"진화 완료: {len(evolution_results['evolved_truths'])}개 진화, "
                       f"{len(evolution_results['new_truths'])}개 신규, "
                       f"{len(evolution_results['modified_truths'])}개 수정")
            
            return evolution_results
            
        except Exception as e:
            logger.error(f"Truth Memory 진화 실패: {e}")
            return {"error": str(e), "evolved": False}
    
    def _detect_strong_patterns_in_medium(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Medium Memory에서 강한 패턴 감지"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # 최근 Medium Memory 조회
            recent_medium = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'medium',
                    MemoryEntry.created_at >= cutoff_time
                )
            ).all()
            
            patterns = []
            
            # 1. 타입별 패턴 분석
            type_patterns = self._analyze_type_patterns(recent_medium)
            patterns.extend(type_patterns)
            
            # 2. 소스별 패턴 분석
            source_patterns = self._analyze_source_patterns(recent_medium)
            patterns.extend(source_patterns)
            
            # 3. 태그별 패턴 분석
            tag_patterns = self._analyze_tag_patterns(recent_medium)
            patterns.extend(tag_patterns)
            
            # 4. 중요도 패턴 분석
            importance_patterns = self._analyze_importance_patterns(recent_medium)
            patterns.extend(importance_patterns)
            
            # 강한 패턴만 필터링 (임계값 이상)
            strong_patterns = [
                pattern for pattern in patterns 
                if pattern.get('strength', 0) >= self.pattern_threshold
            ]
            
            logger.info(f"강한 패턴 {len(strong_patterns)}개 감지됨")
            return strong_patterns
            
        except Exception as e:
            logger.error(f"패턴 감지 실패: {e}")
            return []
    
    def _analyze_type_patterns(self, memories: List[MemoryEntry]) -> List[Dict[str, Any]]:
        """타입별 패턴 분석"""
        type_counter = Counter()
        type_importance = defaultdict(list)
        
        for memory in memories:
            type_counter[memory.type] += 1
            type_importance[memory.type].append(memory.importance_score)
        
        patterns = []
        for memory_type, count in type_counter.most_common(10):
            if count >= 3:  # 최소 3번 이상 나타난 패턴만
                avg_importance = sum(type_importance[memory_type]) / len(type_importance[memory_type])
                strength = min(1.0, count / 10.0)  # 최대 10번을 기준으로 정규화
                
                patterns.append({
                    'pattern_type': 'type',
                    'pattern_value': memory_type,
                    'frequency': count,
                    'avg_importance': avg_importance,
                    'strength': strength,
                    'confidence': min(0.9, strength * avg_importance / 100.0)
                })
        
        return patterns
    
    def _analyze_source_patterns(self, memories: List[MemoryEntry]) -> List[Dict[str, Any]]:
        """소스별 패턴 분석"""
        source_counter = Counter()
        source_importance = defaultdict(list)
        
        for memory in memories:
            source_counter[memory.source] += 1
            source_importance[memory.source].append(memory.importance_score)
        
        patterns = []
        for source, count in source_counter.most_common(5):
            if count >= 2:  # 최소 2번 이상 나타난 패턴만
                avg_importance = sum(source_importance[source]) / len(source_importance[source])
                strength = min(1.0, count / 8.0)  # 최대 8번을 기준으로 정규화
                
                patterns.append({
                    'pattern_type': 'source',
                    'pattern_value': source,
                    'frequency': count,
                    'avg_importance': avg_importance,
                    'strength': strength,
                    'confidence': min(0.9, strength * avg_importance / 100.0)
                })
        
        return patterns
    
    def _analyze_tag_patterns(self, memories: List[MemoryEntry]) -> List[Dict[str, Any]]:
        """태그별 패턴 분석"""
        tag_counter = Counter()
        tag_importance = defaultdict(list)
        
        for memory in memories:
            if memory.tags:
                for tag in memory.tags:
                    tag_counter[tag] += 1
                    tag_importance[tag].append(memory.importance_score)
        
        patterns = []
        for tag, count in tag_counter.most_common(10):
            if count >= 2:  # 최소 2번 이상 나타난 패턴만
                avg_importance = sum(tag_importance[tag]) / len(tag_importance[tag])
                strength = min(1.0, count / 6.0)  # 최대 6번을 기준으로 정규화
                
                patterns.append({
                    'pattern_type': 'tag',
                    'pattern_value': tag,
                    'frequency': count,
                    'avg_importance': avg_importance,
                    'strength': strength,
                    'confidence': min(0.9, strength * avg_importance / 100.0)
                })
        
        return patterns
    
    def _analyze_importance_patterns(self, memories: List[MemoryEntry]) -> List[Dict[str, Any]]:
        """중요도 패턴 분석"""
        high_importance = [m for m in memories if m.importance_score >= 80]
        medium_importance = [m for m in memories if 50 <= m.importance_score < 80]
        low_importance = [m for m in memories if m.importance_score < 50]
        
        patterns = []
        
        # 고중요도 패턴
        if len(high_importance) >= 3:
            patterns.append({
                'pattern_type': 'importance',
                'pattern_value': 'high',
                'frequency': len(high_importance),
                'avg_importance': sum(m.importance_score for m in high_importance) / len(high_importance),
                'strength': min(1.0, len(high_importance) / 5.0),
                'confidence': 0.9
            })
        
        # 중중요도 패턴
        if len(medium_importance) >= 5:
            patterns.append({
                'pattern_type': 'importance',
                'pattern_value': 'medium',
                'frequency': len(medium_importance),
                'avg_importance': sum(m.importance_score for m in medium_importance) / len(medium_importance),
                'strength': min(1.0, len(medium_importance) / 8.0),
                'confidence': 0.7
            })
        
        return patterns
    
    def _process_pattern_evolution(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """개별 패턴의 진화 처리"""
        try:
            pattern_type = pattern['pattern_type']
            pattern_value = pattern['pattern_value']
            strength = pattern['strength']
            confidence = pattern['confidence']
            
            # 기존 Truth Memory와 비교
            existing_truths = self._find_conflicting_truth_memories(pattern)
            
            if existing_truths:
                # 충돌하는 Truth Memory가 있으면 수정
                return self._modify_conflicting_truth(pattern, existing_truths)
            else:
                # 새로운 Truth Memory 생성
                return self._create_truth_from_pattern(pattern)
                
        except Exception as e:
            logger.error(f"패턴 진화 처리 실패: {e}")
            return None
    
    def _find_conflicting_truth_memories(self, pattern: Dict[str, Any]) -> List[MemoryEntry]:
        """패턴과 충돌하는 Truth Memory 찾기"""
        pattern_type = pattern['pattern_type']
        pattern_value = pattern['pattern_value']
        
        if pattern_type == 'type':
            return self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'truth',
                    MemoryEntry.type == pattern_value
                )
            ).all()
        elif pattern_type == 'source':
            return self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'truth',
                    MemoryEntry.source == pattern_value
                )
            ).all()
        elif pattern_type == 'tag':
            # 태그 기반 검색 (JSONB 연산자 사용)
            return self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'truth',
                    MemoryEntry.tags.contains([pattern_value])
                )
            ).all()
        
        return []
    
    def _modify_conflicting_truth(self, pattern: Dict[str, Any], 
                                 conflicting_truths: List[MemoryEntry]) -> Dict[str, Any]:
        """충돌하는 Truth Memory 수정"""
        try:
            # 가장 강한 패턴을 기준으로 Truth Memory 수정
            strongest_truth = max(conflicting_truths, key=lambda t: t.importance_score)
            
            # 패턴 강도가 기존 Truth보다 강하면 수정
            if pattern['strength'] > strongest_truth.importance_score / 100.0:
                strongest_truth.importance_score = min(100, int(pattern['strength'] * 100))
                strongest_truth.content = f"진화된 패턴: {pattern['pattern_type']}={pattern['pattern_value']}"
                strongest_truth.updated_at = datetime.utcnow()
                
                self.db.commit()
                
                return {
                    'action': 'modified',
                    'truth_id': strongest_truth.id,
                    'pattern': pattern,
                    'new_importance': strongest_truth.importance_score
                }
            
            return None
            
        except Exception as e:
            logger.error(f"충돌하는 Truth 수정 실패: {e}")
            return None
    
    def _create_truth_from_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """패턴에서 새로운 Truth Memory 생성"""
        try:
            new_truth = MemoryEntry(
                type=pattern['pattern_type'],
                context=f"진화된 패턴: {pattern['pattern_value']}",
                content=f"강한 패턴 감지: {pattern['pattern_type']}={pattern['pattern_value']} "
                        f"(빈도: {pattern['frequency']}, 강도: {pattern['strength']:.2f})",
                raw_data={
                    'pattern_type': pattern['pattern_type'],
                    'pattern_value': pattern['pattern_value'],
                    'frequency': pattern['frequency'],
                    'strength': pattern['strength'],
                    'confidence': pattern['confidence'],
                    'evolution_source': 'auto_evolution'
                },
                source='evolution_service',
                tags=[pattern['pattern_type'], 'evolved', 'auto_generated'],
                importance_score=int(pattern['strength'] * 100),
                memory_level='truth'
            )
            
            self.db.add(new_truth)
            self.db.commit()
            
            return {
                'action': 'created',
                'truth_id': new_truth.id,
                'pattern': pattern,
                'importance': new_truth.importance_score
            }
            
        except Exception as e:
            logger.error(f"패턴에서 Truth 생성 실패: {e}")
            return None
    
    def _create_new_truth_memories(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """패턴에서 새로운 Truth Memory 생성"""
        new_truths = []
        
        for pattern in patterns:
            if pattern['strength'] >= self.evolution_confidence:
                result = self._create_truth_from_pattern(pattern)
                if result:
                    new_truths.append(result)
        
        return new_truths
    
    def _modify_existing_truth_memories(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """기존 Truth Memory 수정"""
        modified_truths = []
        
        for pattern in patterns:
            conflicting_truths = self._find_conflicting_truth_memories(pattern)
            if conflicting_truths:
                result = self._modify_conflicting_truth(pattern, conflicting_truths)
                if result:
                    modified_truths.append(result)
        
        return modified_truths
    
    def _cleanup_low_confidence_truths(self, min_confidence: float = 0.3) -> List[int]:
        """신뢰도 낮은 Truth Memory 삭제"""
        try:
            # 오래되고 신뢰도 낮은 Truth Memory 찾기
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            low_confidence_truths = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'truth',
                    MemoryEntry.importance_score < min_confidence * 100,
                    MemoryEntry.created_at < cutoff_time
                )
            ).all()
            
            deleted_ids = [truth.id for truth in low_confidence_truths]
            
            for truth in low_confidence_truths:
                self.db.delete(truth)
            
            self.db.commit()
            
            logger.info(f"신뢰도 낮은 Truth Memory {len(deleted_ids)}개 삭제")
            return deleted_ids
            
        except Exception as e:
            logger.error(f"신뢰도 낮은 Truth Memory 정리 실패: {e}")
            return []
    
    def _calculate_evolution_confidence(self, evolution_results: Dict[str, Any]) -> float:
        """진화 신뢰도 계산"""
        try:
            total_operations = (
                len(evolution_results['evolved_truths']) +
                len(evolution_results['new_truths']) +
                len(evolution_results['modified_truths'])
            )
            
            if total_operations == 0:
                return 0.0
            
            # 각 작업의 신뢰도 가중 평균
            confidence_sum = 0.0
            weight_sum = 0.0
            
            for evolved in evolution_results['evolved_truths']:
                confidence = evolved.get('pattern', {}).get('confidence', 0.5)
                confidence_sum += confidence
                weight_sum += 1.0
            
            for new_truth in evolution_results['new_truths']:
                confidence = new_truth.get('pattern', {}).get('confidence', 0.5)
                confidence_sum += confidence
                weight_sum += 1.0
            
            for modified in evolution_results['modified_truths']:
                confidence = modified.get('pattern', {}).get('confidence', 0.5)
                confidence_sum += confidence
                weight_sum += 1.0
            
            return confidence_sum / weight_sum if weight_sum > 0 else 0.0
            
        except Exception as e:
            logger.error(f"진화 신뢰도 계산 실패: {e}")
            return 0.0
    
    # @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_evolution_statistics(self) -> Dict[str, Any]:
        """진화 통계 조회"""
        try:
            # 최근 24시간 진화 통계
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            evolved_truths = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'truth',
                    MemoryEntry.source == 'evolution_service',
                    MemoryEntry.created_at >= cutoff_time
                )
            ).count()
            
            modified_truths = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'truth',
                    MemoryEntry.updated_at >= cutoff_time,
                    MemoryEntry.created_at < cutoff_time
                )
            ).count()
            
            total_truths = self.db.query(MemoryEntry).filter(
                MemoryEntry.memory_level == 'truth'
            ).count()
            
            return {
                'evolved_truths_24h': evolved_truths,
                'modified_truths_24h': modified_truths,
                'total_truths': total_truths,
                'evolution_rate': evolved_truths / max(1, total_truths) * 100,
                'last_evolution': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"진화 통계 조회 실패: {e}")
            return {} 