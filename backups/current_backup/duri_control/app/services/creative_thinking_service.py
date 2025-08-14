"""
Day 9: 창의적 사고 시스템
DuRi가 혁신적이고 독창적인 아이디어를 생성하는 능력 구현
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from collections import Counter, defaultdict
import numpy as np
import random

from ..models.memory import MemoryEntry
# from ..utils.retry_decorator import retry_on_db_error

logger = logging.getLogger(__name__)

class CreativeThinkingService:
    """창의적 사고 서비스 - DuRi가 혁신적 아이디어를 생성하는 능력"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.creativity_threshold = 0.7
        self.innovation_confidence = 0.8
        self.pattern_connection_weight = 0.6
        self.idea_generation_weight = 0.4
        
    def generate_creative_ideas(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """창의적 아이디어 생성"""
        try:
            # 1. 컨텍스트 분석
            context_analysis = self._analyze_creative_context(context)
            
            # 2. 기존 패턴 분석
            pattern_analysis = self._analyze_existing_patterns(context_analysis)
            
            # 3. 아이디어 생성
            ideas = self._generate_ideas(context_analysis, pattern_analysis)
            
            # 4. 혁신성 평가
            innovation_assessment = self._assess_innovation(ideas, pattern_analysis)
            
            # 5. 실현 가능성 분석
            feasibility_analysis = self._analyze_feasibility(ideas, context_analysis)
            
            # 6. 창의적 사고 점수 계산
            creativity_score = self._calculate_creativity_score(
                ideas, innovation_assessment, feasibility_analysis
            )
            
            return {
                "ideas": ideas,
                "pattern_analysis": pattern_analysis,
                "innovation_assessment": innovation_assessment,
                "feasibility_analysis": feasibility_analysis,
                "creativity_score": creativity_score,
                "generation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"창의적 아이디어 생성 실패: {e}")
            return {"error": str(e)}
    
    def _analyze_creative_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """창의적 컨텍스트 분석"""
        try:
            problem = context.get("problem", "")
            domain = context.get("domain", "general")
            constraints = context.get("constraints", [])
            goals = context.get("goals", [])
            
            # 1. 문제 복잡성 분석
            complexity_analysis = self._analyze_problem_complexity(problem, domain)
            
            # 2. 제약 조건 분석
            constraint_analysis = self._analyze_constraints(constraints)
            
            # 3. 목표 분석
            goal_analysis = self._analyze_goals(goals)
            
            # 4. 창의적 기회 탐지
            creative_opportunities = self._detect_creative_opportunities(
                complexity_analysis, constraint_analysis, goal_analysis
            )
            
            return {
                "problem": problem,
                "domain": domain,
                "complexity_analysis": complexity_analysis,
                "constraint_analysis": constraint_analysis,
                "goal_analysis": goal_analysis,
                "creative_opportunities": creative_opportunities,
                "context_confidence": self._calculate_context_confidence(
                    complexity_analysis, constraint_analysis, goal_analysis
                )
            }
            
        except Exception as e:
            logger.error(f"창의적 컨텍스트 분석 실패: {e}")
            return {}
    
    def _analyze_problem_complexity(self, problem: str, domain: str) -> Dict[str, Any]:
        """문제 복잡성 분석"""
        try:
            # 문제 길이 기반 복잡성
            length_complexity = min(1.0, len(problem) / 200.0)
            
            # 키워드 기반 복잡성
            complexity_keywords = ["복잡", "어려운", "다양한", "통합", "시스템", "관련", "연결"]
            keyword_complexity = sum(1 for keyword in complexity_keywords if keyword in problem) / len(complexity_keywords)
            
            # 도메인별 복잡성 가중치
            domain_weights = {
                "technology": 0.9,
                "business": 0.7,
                "social": 0.6,
                "scientific": 0.8,
                "artistic": 0.5,
                "general": 0.6
            }
            
            domain_complexity = domain_weights.get(domain, 0.6)
            
            # 종합 복잡성 계산
            overall_complexity = (
                length_complexity * 0.3 +
                keyword_complexity * 0.4 +
                domain_complexity * 0.3
            )
            
            return {
                "overall_complexity": overall_complexity,
                "length_complexity": length_complexity,
                "keyword_complexity": keyword_complexity,
                "domain_complexity": domain_complexity,
                "complexity_level": "high" if overall_complexity > 0.7 else "medium" if overall_complexity > 0.4 else "low"
            }
            
        except Exception as e:
            logger.error(f"문제 복잡성 분석 실패: {e}")
            return {}
    
    def _analyze_constraints(self, constraints: List[str]) -> Dict[str, Any]:
        """제약 조건 분석"""
        try:
            if not constraints:
                return {
                    "constraint_count": 0,
                    "constraint_types": [],
                    "constraint_severity": 0.0,
                    "flexibility": 1.0
                }
            
            # 제약 조건 유형 분류
            constraint_types = {
                "technical": ["기술", "기능", "성능", "호환성"],
                "resource": ["비용", "시간", "인력", "자원"],
                "legal": ["법적", "규정", "정책", "허가"],
                "social": ["사회적", "문화적", "윤리적", "환경적"]
            }
            
            detected_types = []
            for constraint in constraints:
                for type_name, keywords in constraint_types.items():
                    if any(keyword in constraint for keyword in keywords):
                        detected_types.append(type_name)
                        break
            
            # 제약 조건 심각도
            severity_keywords = ["절대", "필수", "금지", "불가능", "제한"]
            severity_score = sum(1 for constraint in constraints 
                               for keyword in severity_keywords if keyword in constraint) / len(constraints)
            
            # 유연성 계산 (제약이 많을수록 유연성 낮음)
            flexibility = max(0.0, 1.0 - (len(constraints) * 0.1 + severity_score * 0.3))
            
            return {
                "constraint_count": len(constraints),
                "constraint_types": list(set(detected_types)),
                "constraint_severity": severity_score,
                "flexibility": flexibility
            }
            
        except Exception as e:
            logger.error(f"제약 조건 분석 실패: {e}")
            return {}
    
    def _analyze_goals(self, goals: List[str]) -> Dict[str, Any]:
        """목표 분석"""
        try:
            if not goals:
                return {
                    "goal_count": 0,
                    "goal_types": [],
                    "goal_ambition": 0.0,
                    "goal_clarity": 0.0
                }
            
            # 목표 유형 분류
            goal_types = {
                "efficiency": ["효율", "성능", "속도", "최적화"],
                "innovation": ["혁신", "새로운", "창의적", "독창적"],
                "quality": ["품질", "정확성", "신뢰성", "안정성"],
                "user_experience": ["사용자", "경험", "편의성", "만족도"]
            }
            
            detected_types = []
            for goal in goals:
                for type_name, keywords in goal_types.items():
                    if any(keyword in goal for keyword in keywords):
                        detected_types.append(type_name)
                        break
            
            # 목표 야망도 (혁신적 목표일수록 높음)
            ambition_keywords = ["혁신", "혁명적", "완전히 새로운", "파괴적", "급진적"]
            ambition_score = sum(1 for goal in goals 
                               for keyword in ambition_keywords if keyword in goal) / len(goals)
            
            # 목표 명확성 (구체적일수록 높음)
            clarity_keywords = ["구체적", "명확", "정확", "정량적", "측정 가능"]
            clarity_score = sum(1 for goal in goals 
                              for keyword in clarity_keywords if keyword in goal) / len(goals)
            
            return {
                "goal_count": len(goals),
                "goal_types": list(set(detected_types)),
                "goal_ambition": ambition_score,
                "goal_clarity": clarity_score
            }
            
        except Exception as e:
            logger.error(f"목표 분석 실패: {e}")
            return {}
    
    def _detect_creative_opportunities(
        self,
        complexity_analysis: Dict[str, Any],
        constraint_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """창의적 기회 탐지"""
        try:
            opportunities = []
            
            # 복잡성 기반 기회
            complexity = complexity_analysis.get("overall_complexity", 0.5)
            if complexity > 0.7:
                opportunities.append({
                    "type": "complexity_driven",
                    "description": "복잡한 문제로 인한 창의적 해결책 필요",
                    "priority": "high",
                    "confidence": complexity
                })
            
            # 제약 조건 기반 기회
            flexibility = constraint_analysis.get("flexibility", 1.0)
            if flexibility < 0.5:
                opportunities.append({
                    "type": "constraint_driven",
                    "description": "제약 조건 내에서의 혁신적 접근",
                    "priority": "medium",
                    "confidence": 1.0 - flexibility
                })
            
            # 목표 기반 기회
            ambition = goal_analysis.get("goal_ambition", 0.0)
            if ambition > 0.6:
                opportunities.append({
                    "type": "ambition_driven",
                    "description": "야망적인 목표 달성을 위한 혁신적 아이디어",
                    "priority": "high",
                    "confidence": ambition
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"창의적 기회 탐지 실패: {e}")
            return []
    
    def _calculate_context_confidence(
        self,
        complexity_analysis: Dict[str, Any],
        constraint_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> float:
        """컨텍스트 분석 신뢰도 계산"""
        try:
            complexity_confidence = complexity_analysis.get("overall_complexity", 0.5)
            constraint_confidence = constraint_analysis.get("flexibility", 0.5)
            goal_confidence = goal_analysis.get("goal_clarity", 0.5)
            
            confidence = (complexity_confidence * 0.4 + constraint_confidence * 0.3 + goal_confidence * 0.3)
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"컨텍스트 분석 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _analyze_existing_patterns(self, context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """기존 패턴 분석"""
        try:
            domain = context_analysis.get("domain", "general")
            problem = context_analysis.get("problem", "")
            
            # 1. 도메인별 패턴 분석
            domain_patterns = self._analyze_domain_patterns(domain)
            
            # 2. 문제별 패턴 분석
            problem_patterns = self._analyze_problem_patterns(problem)
            
            # 3. 패턴 연결 가능성
            pattern_connections = self._analyze_pattern_connections(domain_patterns, problem_patterns)
            
            # 4. 혁신 기회 탐지
            innovation_opportunities = self._detect_innovation_opportunities(
                domain_patterns, problem_patterns, pattern_connections
            )
            
            return {
                "domain_patterns": domain_patterns,
                "problem_patterns": problem_patterns,
                "pattern_connections": pattern_connections,
                "innovation_opportunities": innovation_opportunities,
                "pattern_confidence": self._calculate_pattern_confidence(
                    domain_patterns, problem_patterns
                )
            }
            
        except Exception as e:
            logger.error(f"기존 패턴 분석 실패: {e}")
            return {}
    
    def _analyze_domain_patterns(self, domain: str) -> Dict[str, Any]:
        """도메인별 패턴 분석"""
        try:
            # 도메인별 일반적인 패턴들
            domain_patterns = {
                "technology": {
                    "patterns": ["모듈화", "확장성", "호환성", "성능 최적화"],
                    "innovation_areas": ["AI/ML", "클라우드", "IoT", "블록체인"],
                    "success_metrics": ["성능", "사용성", "확장성"]
                },
                "business": {
                    "patterns": ["효율성", "수익성", "고객 만족", "시장 점유율"],
                    "innovation_areas": ["디지털 전환", "고객 경험", "지속가능성"],
                    "success_metrics": ["매출", "고객 만족도", "시장 점유율"]
                },
                "social": {
                    "patterns": ["포용성", "지속가능성", "공정성", "접근성"],
                    "innovation_areas": ["사회적 임팩트", "포용적 디자인", "지속가능성"],
                    "success_metrics": ["사회적 임팩트", "포용성", "지속가능성"]
                },
                "scientific": {
                    "patterns": ["정확성", "재현성", "검증 가능성", "일반화"],
                    "innovation_areas": ["새로운 방법론", "크로스 디시플린", "오픈 사이언스"],
                    "success_metrics": ["정확성", "재현성", "임팩트"]
                },
                "artistic": {
                    "patterns": ["표현성", "독창성", "감정적 임팩트", "문화적 의미"],
                    "innovation_areas": ["새로운 매체", "인터랙티브 아트", "크로스 컬처"],
                    "success_metrics": ["독창성", "감정적 임팩트", "문화적 의미"]
                }
            }
            
            return domain_patterns.get(domain, {
                "patterns": ["일반적 패턴"],
                "innovation_areas": ["일반적 혁신 영역"],
                "success_metrics": ["일반적 성공 지표"]
            })
            
        except Exception as e:
            logger.error(f"도메인 패턴 분석 실패: {e}")
            return {}
    
    def _analyze_problem_patterns(self, problem: str) -> Dict[str, Any]:
        """문제별 패턴 분석"""
        try:
            # 문제 유형 분류
            problem_types = {
                "optimization": ["최적화", "효율성", "성능", "개선"],
                "integration": ["통합", "연결", "시스템", "호환성"],
                "innovation": ["혁신", "새로운", "창의적", "독창적"],
                "solving": ["해결", "문제", "어려움", "도전"]
            }
            
            detected_types = []
            for problem_type, keywords in problem_types.items():
                if any(keyword in problem for keyword in keywords):
                    detected_types.append(problem_type)
            
            # 문제 복잡성 패턴
            complexity_patterns = {
                "simple": len(problem) < 50,
                "moderate": 50 <= len(problem) < 150,
                "complex": len(problem) >= 150
            }
            
            return {
                "problem_types": detected_types,
                "complexity_patterns": complexity_patterns,
                "key_components": self._extract_key_components(problem)
            }
            
        except Exception as e:
            logger.error(f"문제 패턴 분석 실패: {e}")
            return {}
    
    def _extract_key_components(self, problem: str) -> List[str]:
        """문제의 핵심 구성 요소 추출"""
        try:
            # 간단한 키워드 추출 (실제로는 NLP 사용)
            keywords = ["시스템", "사용자", "데이터", "프로세스", "결과", "효율성", "품질", "비용", "시간"]
            components = [keyword for keyword in keywords if keyword in problem]
            return components
            
        except Exception as e:
            logger.error(f"핵심 구성 요소 추출 실패: {e}")
            return []
    
    def _analyze_pattern_connections(
        self,
        domain_patterns: Dict[str, Any],
        problem_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """패턴 연결 분석"""
        try:
            connections = []
            
            # 도메인 패턴과 문제 패턴 연결
            domain_pattern_list = domain_patterns.get("patterns", [])
            problem_types = problem_patterns.get("problem_types", [])
            
            for pattern in domain_pattern_list:
                for problem_type in problem_types:
                    connection_strength = self._calculate_connection_strength(pattern, problem_type)
                    if connection_strength > 0.3:
                        connections.append({
                            "from_pattern": pattern,
                            "to_pattern": problem_type,
                            "connection_strength": connection_strength,
                            "connection_type": "domain_problem"
                        })
            
            return connections
            
        except Exception as e:
            logger.error(f"패턴 연결 분석 실패: {e}")
            return []
    
    def _calculate_connection_strength(self, pattern1: str, pattern2: str) -> float:
        """패턴 간 연결 강도 계산"""
        try:
            # 간단한 유사도 계산 (실제로는 더 정교한 알고리즘 사용)
            common_keywords = ["효율", "성능", "품질", "혁신", "통합"]
            pattern1_keywords = [kw for kw in common_keywords if kw in pattern1]
            pattern2_keywords = [kw for kw in common_keywords if kw in pattern2]
            
            if not pattern1_keywords or not pattern2_keywords:
                return 0.1
            
            intersection = len(set(pattern1_keywords) & set(pattern2_keywords))
            union = len(set(pattern1_keywords) | set(pattern2_keywords))
            
            return intersection / union if union > 0 else 0.1
            
        except Exception as e:
            logger.error(f"연결 강도 계산 실패: {e}")
            return 0.1
    
    def _detect_innovation_opportunities(
        self,
        domain_patterns: Dict[str, Any],
        problem_patterns: Dict[str, Any],
        pattern_connections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """혁신 기회 탐지"""
        try:
            opportunities = []
            
            # 강한 패턴 연결 기반 기회
            strong_connections = [conn for conn in pattern_connections if conn.get("connection_strength", 0) > 0.5]
            if strong_connections:
                opportunities.append({
                    "type": "pattern_synthesis",
                    "description": "기존 패턴의 새로운 조합을 통한 혁신",
                    "confidence": np.mean([conn.get("connection_strength", 0) for conn in strong_connections]),
                    "priority": "high"
                })
            
            # 도메인 혁신 영역 기반 기회
            innovation_areas = domain_patterns.get("innovation_areas", [])
            if innovation_areas:
                opportunities.append({
                    "type": "domain_innovation",
                    "description": f"도메인 특화 혁신 영역 활용: {', '.join(innovation_areas[:3])}",
                    "confidence": 0.7,
                    "priority": "medium"
                })
            
            # 복잡한 문제 기반 기회
            complexity_patterns = problem_patterns.get("complexity_patterns", {})
            if complexity_patterns.get("complex", False):
                opportunities.append({
                    "type": "complexity_innovation",
                    "description": "복잡한 문제 해결을 위한 혁신적 접근",
                    "confidence": 0.8,
                    "priority": "high"
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"혁신 기회 탐지 실패: {e}")
            return []
    
    def _calculate_pattern_confidence(
        self,
        domain_patterns: Dict[str, Any],
        problem_patterns: Dict[str, Any]
    ) -> float:
        """패턴 분석 신뢰도 계산"""
        try:
            domain_confidence = len(domain_patterns.get("patterns", [])) / 10.0
            problem_confidence = len(problem_patterns.get("problem_types", [])) / 4.0
            
            confidence = (domain_confidence * 0.6 + problem_confidence * 0.4)
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"패턴 분석 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _generate_ideas(
        self,
        context_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """아이디어 생성"""
        try:
            ideas = []
            
            # 1. 패턴 기반 아이디어
            pattern_ideas = self._generate_pattern_based_ideas(context_analysis, pattern_analysis)
            ideas.extend(pattern_ideas)
            
            # 2. 혁신 기회 기반 아이디어
            innovation_ideas = self._generate_innovation_based_ideas(context_analysis, pattern_analysis)
            ideas.extend(innovation_ideas)
            
            # 3. 제약 조건 기반 아이디어
            constraint_ideas = self._generate_constraint_based_ideas(context_analysis)
            ideas.extend(constraint_ideas)
            
            # 4. 목표 기반 아이디어
            goal_ideas = self._generate_goal_based_ideas(context_analysis)
            ideas.extend(goal_ideas)
            
            return ideas
            
        except Exception as e:
            logger.error(f"아이디어 생성 실패: {e}")
            return []
    
    def _generate_pattern_based_ideas(
        self,
        context_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """패턴 기반 아이디어 생성"""
        try:
            ideas = []
            domain_patterns = pattern_analysis.get("domain_patterns", {})
            patterns = domain_patterns.get("patterns", [])
            
            for pattern in patterns:
                idea = {
                    "title": f"{pattern} 기반 혁신적 접근",
                    "description": f"기존 {pattern} 패턴을 새로운 방식으로 적용하여 문제를 해결합니다.",
                    "type": "pattern_based",
                    "confidence": 0.7,
                    "innovation_level": "medium",
                    "feasibility": 0.6
                }
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"패턴 기반 아이디어 생성 실패: {e}")
            return []
    
    def _generate_innovation_based_ideas(
        self,
        context_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """혁신 기회 기반 아이디어 생성"""
        try:
            ideas = []
            innovation_opportunities = pattern_analysis.get("innovation_opportunities", [])
            
            for opportunity in innovation_opportunities:
                opportunity_type = opportunity.get("type", "")
                description = opportunity.get("description", "")
                
                idea = {
                    "title": f"{opportunity_type} 기반 혁신 아이디어",
                    "description": description,
                    "type": "innovation_based",
                    "confidence": opportunity.get("confidence", 0.5),
                    "innovation_level": "high",
                    "feasibility": 0.4
                }
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"혁신 기회 기반 아이디어 생성 실패: {e}")
            return []
    
    def _generate_constraint_based_ideas(self, context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """제약 조건 기반 아이디어 생성"""
        try:
            ideas = []
            constraint_analysis = context_analysis.get("constraint_analysis", {})
            flexibility = constraint_analysis.get("flexibility", 1.0)
            
            if flexibility < 0.7:
                idea = {
                    "title": "제약 조건 내 혁신적 해결책",
                    "description": "제약 조건을 창의적 기회로 활용하여 혁신적 해결책을 제시합니다.",
                    "type": "constraint_based",
                    "confidence": 0.6,
                    "innovation_level": "medium",
                    "feasibility": 0.5
                }
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"제약 조건 기반 아이디어 생성 실패: {e}")
            return []
    
    def _generate_goal_based_ideas(self, context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """목표 기반 아이디어 생성"""
        try:
            ideas = []
            goal_analysis = context_analysis.get("goal_analysis", {})
            ambition = goal_analysis.get("goal_ambition", 0.0)
            
            if ambition > 0.5:
                idea = {
                    "title": "야망적 목표 달성 아이디어",
                    "description": "혁신적 접근을 통해 야망적인 목표를 달성하는 아이디어입니다.",
                    "type": "goal_based",
                    "confidence": 0.8,
                    "innovation_level": "high",
                    "feasibility": 0.3
                }
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"목표 기반 아이디어 생성 실패: {e}")
            return []
    
    def _assess_innovation(self, ideas: List[Dict[str, Any]], pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """혁신성 평가"""
        try:
            if not ideas:
                return {
                    "overall_innovation_score": 0.0,
                    "innovation_distribution": {},
                    "breakthrough_ideas": [],
                    "incremental_ideas": []
                }
            
            # 혁신 수준별 분류
            innovation_levels = [idea.get("innovation_level", "low") for idea in ideas]
            innovation_distribution = Counter(innovation_levels)
            
            # 혁신 점수 계산
            innovation_scores = []
            breakthrough_ideas = []
            incremental_ideas = []
            
            for idea in ideas:
                innovation_level = idea.get("innovation_level", "low")
                confidence = idea.get("confidence", 0.5)
                
                # 혁신 점수 계산
                level_scores = {"low": 0.3, "medium": 0.6, "high": 0.9}
                innovation_score = level_scores.get(innovation_level, 0.3) * confidence
                innovation_scores.append(innovation_score)
                
                # 아이디어 분류
                if innovation_level == "high":
                    breakthrough_ideas.append(idea)
                else:
                    incremental_ideas.append(idea)
            
            overall_innovation_score = np.mean(innovation_scores) if innovation_scores else 0.0
            
            return {
                "overall_innovation_score": overall_innovation_score,
                "innovation_distribution": dict(innovation_distribution),
                "breakthrough_ideas": breakthrough_ideas,
                "incremental_ideas": incremental_ideas,
                "innovation_confidence": self._calculate_innovation_confidence(ideas, pattern_analysis)
            }
            
        except Exception as e:
            logger.error(f"혁신성 평가 실패: {e}")
            return {}
    
    def _calculate_innovation_confidence(
        self,
        ideas: List[Dict[str, Any]],
        pattern_analysis: Dict[str, Any]
    ) -> float:
        """혁신성 평가 신뢰도 계산"""
        try:
            if not ideas:
                return 0.0
            
            # 아이디어 다양성
            idea_types = [idea.get("type", "") for idea in ideas]
            diversity_score = len(set(idea_types)) / len(idea_types) if idea_types else 0.0
            
            # 패턴 분석 신뢰도
            pattern_confidence = pattern_analysis.get("pattern_confidence", 0.5)
            
            # 혁신 기회 수
            innovation_opportunities = pattern_analysis.get("innovation_opportunities", [])
            opportunity_score = min(1.0, len(innovation_opportunities) / 5.0)
            
            confidence = (diversity_score * 0.4 + pattern_confidence * 0.4 + opportunity_score * 0.2)
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"혁신성 평가 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _analyze_feasibility(
        self,
        ideas: List[Dict[str, Any]],
        context_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실현 가능성 분석"""
        try:
            if not ideas:
                return {
                    "overall_feasibility": 0.0,
                    "feasibility_distribution": {},
                    "high_feasibility_ideas": [],
                    "low_feasibility_ideas": []
                }
            
            feasibility_scores = []
            high_feasibility_ideas = []
            low_feasibility_ideas = []
            
            for idea in ideas:
                feasibility = idea.get("feasibility", 0.5)
                feasibility_scores.append(feasibility)
                
                if feasibility > 0.7:
                    high_feasibility_ideas.append(idea)
                else:
                    low_feasibility_ideas.append(idea)
            
            overall_feasibility = np.mean(feasibility_scores) if feasibility_scores else 0.0
            
            # 실현 가능성 분포
            feasibility_levels = []
            for score in feasibility_scores:
                if score > 0.7:
                    feasibility_levels.append("high")
                elif score > 0.4:
                    feasibility_levels.append("medium")
                else:
                    feasibility_levels.append("low")
            
            feasibility_distribution = Counter(feasibility_levels)
            
            return {
                "overall_feasibility": overall_feasibility,
                "feasibility_distribution": dict(feasibility_distribution),
                "high_feasibility_ideas": high_feasibility_ideas,
                "low_feasibility_ideas": low_feasibility_ideas
            }
            
        except Exception as e:
            logger.error(f"실현 가능성 분석 실패: {e}")
            return {}
    
    def _calculate_creativity_score(
        self,
        ideas: List[Dict[str, Any]],
        innovation_assessment: Dict[str, Any],
        feasibility_analysis: Dict[str, Any]
    ) -> float:
        """창의적 사고 점수 계산"""
        try:
            if not ideas:
                return 0.0
            
            # 혁신성 점수
            innovation_score = innovation_assessment.get("overall_innovation_score", 0.0)
            
            # 실현 가능성 점수
            feasibility_score = feasibility_analysis.get("overall_feasibility", 0.0)
            
            # 아이디어 다양성 점수
            idea_types = [idea.get("type", "") for idea in ideas]
            diversity_score = len(set(idea_types)) / len(idea_types) if idea_types else 0.0
            
            # 창의적 사고 점수 계산 (혁신성 50%, 실현 가능성 30%, 다양성 20%)
            creativity_score = (
                innovation_score * 0.5 +
                feasibility_score * 0.3 +
                diversity_score * 0.2
            )
            
            return float(max(0.0, min(100.0, creativity_score * 100)))
            
        except Exception as e:
            logger.error(f"창의적 사고 점수 계산 실패: {e}")
            return 0.0
    
    def get_creative_thinking_stats(self) -> Dict[str, Any]:
        """창의적 사고 통계 조회"""
        try:
            # 최근 24시간 창의적 사고 활동 통계
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # 아이디어 생성 통계
            idea_generation_stats = {
                "total_ideas_generated": 15,  # 예시 데이터
                "average_creativity_score": 72.5,
                "innovation_distribution": {
                    "high": 5,
                    "medium": 7,
                    "low": 3
                }
            }
            
            # 패턴 분석 통계
            pattern_analysis_stats = {
                "patterns_analyzed": 25,
                "connections_discovered": 12,
                "innovation_opportunities": 8
            }
            
            # 창의적 사고 점수
            creativity_scores = {
                "innovation_ability": 75.0,
                "pattern_recognition": 80.0,
                "idea_generation": 70.0,
                "feasibility_assessment": 65.0
            }
            
            return {
                "idea_generation_stats": idea_generation_stats,
                "pattern_analysis_stats": pattern_analysis_stats,
                "creativity_scores": creativity_scores,
                "overall_creativity_score": np.mean(list(creativity_scores.values()))
            }
            
        except Exception as e:
            logger.error(f"창의적 사고 통계 조회 실패: {e}")
            return {} 