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

# from ..models.memory import MemoryEntry
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
            # 문제 길이와 키워드 수로 복잡성 추정
            words = problem.split()
            complexity_score = min(1.0, len(words) / 50)  # 50단어를 최대 복잡성으로 가정
            
            # 도메인별 복잡성 조정
            domain_complexity_factors = {
                "technical": 1.2,
                "business": 1.0,
                "creative": 0.8,
                "social": 0.9,
                "general": 1.0
            }
            
            adjusted_complexity = complexity_score * domain_complexity_factors.get(domain, 1.0)
            
            # 복잡성 수준 결정
            if adjusted_complexity < 0.3:
                complexity_level = "simple"
            elif adjusted_complexity < 0.6:
                complexity_level = "moderate"
            else:
                complexity_level = "complex"
            
            return {
                "complexity_score": adjusted_complexity,
                "complexity_level": complexity_level,
                "word_count": len(words),
                "domain_factor": domain_complexity_factors.get(domain, 1.0),
                "requires_creative_thinking": adjusted_complexity > 0.5
            }
            
        except Exception as e:
            logger.error(f"문제 복잡성 분석 실패: {e}")
            return {"complexity_score": 0.5, "complexity_level": "moderate"}
    
    def _analyze_constraints(self, constraints: List[str]) -> Dict[str, Any]:
        """제약 조건 분석"""
        try:
            constraint_count = len(constraints)
            constraint_types = {
                "technical": 0,
                "resource": 0,
                "time": 0,
                "budget": 0,
                "legal": 0,
                "other": 0
            }
            
            # 제약 조건 분류
            for constraint in constraints:
                constraint_lower = constraint.lower()
                if any(word in constraint_lower for word in ["기술", "technical", "code", "system"]):
                    constraint_types["technical"] += 1
                elif any(word in constraint_lower for word in ["자원", "resource", "인력", "manpower"]):
                    constraint_types["resource"] += 1
                elif any(word in constraint_lower for word in ["시간", "time", "deadline", "기한"]):
                    constraint_types["time"] += 1
                elif any(word in constraint_lower for word in ["예산", "budget", "비용", "cost"]):
                    constraint_types["budget"] += 1
                elif any(word in constraint_lower for word in ["법적", "legal", "규정", "regulation"]):
                    constraint_types["legal"] += 1
                else:
                    constraint_types["other"] += 1
            
            # 제약 조건 강도 계산
            total_constraints = sum(constraint_types.values())
            constraint_intensity = min(1.0, total_constraints / 5)  # 5개를 최대 강도로 가정
            
            return {
                "constraint_count": constraint_count,
                "constraint_types": constraint_types,
                "constraint_intensity": constraint_intensity,
                "primary_constraint": max(constraint_types.items(), key=lambda x: x[1])[0] if total_constraints > 0 else "none",
                "requires_creative_solution": constraint_intensity > 0.6
            }
            
        except Exception as e:
            logger.error(f"제약 조건 분석 실패: {e}")
            return {"constraint_count": 0, "constraint_intensity": 0}
    
    def _analyze_goals(self, goals: List[str]) -> Dict[str, Any]:
        """목표 분석"""
        try:
            goal_count = len(goals)
            goal_types = {
                "efficiency": 0,
                "innovation": 0,
                "quality": 0,
                "cost_reduction": 0,
                "user_experience": 0,
                "other": 0
            }
            
            # 목표 분류
            for goal in goals:
                goal_lower = goal.lower()
                if any(word in goal_lower for word in ["효율", "efficiency", "성능", "performance"]):
                    goal_types["efficiency"] += 1
                elif any(word in goal_lower for word in ["혁신", "innovation", "창의", "creative"]):
                    goal_types["innovation"] += 1
                elif any(word in goal_lower for word in ["품질", "quality", "정확", "accuracy"]):
                    goal_types["quality"] += 1
                elif any(word in goal_lower for word in ["비용절감", "cost", "경제", "economic"]):
                    goal_types["cost_reduction"] += 1
                elif any(word in goal_lower for word in ["사용자경험", "user", "사용성", "usability"]):
                    goal_types["user_experience"] += 1
                else:
                    goal_types["other"] += 1
            
            # 목표 우선순위 계산
            total_goals = sum(goal_types.values())
            primary_goal = max(goal_types.items(), key=lambda x: x[1])[0] if total_goals > 0 else "none"
            
            # 목표 복잡성 계산
            goal_complexity = min(1.0, goal_count / 3)  # 3개를 최대 복잡성으로 가정
            
            return {
                "goal_count": goal_count,
                "goal_types": goal_types,
                "primary_goal": primary_goal,
                "goal_complexity": goal_complexity,
                "requires_creative_approach": goal_complexity > 0.5 or goal_types["innovation"] > 0
            }
            
        except Exception as e:
            logger.error(f"목표 분석 실패: {e}")
            return {"goal_count": 0, "goal_complexity": 0}
    
    def _detect_creative_opportunities(
        self,
        complexity_analysis: Dict[str, Any],
        constraint_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """창의적 기회 탐지"""
        opportunities = []
        
        # 복잡성 기반 기회
        if complexity_analysis.get("requires_creative_thinking", False):
            opportunities.append({
                "type": "complexity_based",
                "description": "복잡한 문제로 인한 창의적 해결책 필요",
                "priority": "high",
                "confidence": complexity_analysis.get("complexity_score", 0)
            })
        
        # 제약 조건 기반 기회
        if constraint_analysis.get("requires_creative_solution", False):
            opportunities.append({
                "type": "constraint_based",
                "description": "제약 조건 극복을 위한 창의적 접근 필요",
                "priority": "high",
                "confidence": constraint_analysis.get("constraint_intensity", 0)
            })
        
        # 목표 기반 기회
        if goal_analysis.get("requires_creative_approach", False):
            opportunities.append({
                "type": "goal_based",
                "description": "혁신적 목표 달성을 위한 창의적 방법 필요",
                "priority": "medium",
                "confidence": goal_analysis.get("goal_complexity", 0)
            })
        
        return opportunities
    
    def _calculate_context_confidence(
        self,
        complexity_analysis: Dict[str, Any],
        constraint_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> float:
        """컨텍스트 신뢰도 계산"""
        try:
            # 각 분석의 신뢰도 계산
            complexity_confidence = complexity_analysis.get("complexity_score", 0.5)
            constraint_confidence = constraint_analysis.get("constraint_intensity", 0.5)
            goal_confidence = goal_analysis.get("goal_complexity", 0.5)
            
            # 가중 평균으로 전체 신뢰도 계산
            total_confidence = (
                complexity_confidence * 0.4 +
                constraint_confidence * 0.3 +
                goal_confidence * 0.3
            )
            
            return min(1.0, total_confidence)
            
        except Exception as e:
            logger.error(f"컨텍스트 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _analyze_existing_patterns(self, context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """기존 패턴 분석"""
        try:
            domain = context_analysis.get("domain", "general")
            problem = context_analysis.get("problem", "")
            
            # 도메인별 패턴 분석
            domain_patterns = self._analyze_domain_patterns(domain)
            
            # 문제별 패턴 분석
            problem_patterns = self._analyze_problem_patterns(problem)
            
            # 패턴 연결 분석
            pattern_connections = self._analyze_pattern_connections(
                domain_patterns, problem_patterns
            )
            
            # 혁신 기회 탐지
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
                "technical": {
                    "patterns": ["modular_design", "scalability", "performance_optimization"],
                    "innovation_areas": ["automation", "ai_integration", "cloud_native"],
                    "constraint_patterns": ["resource_limitation", "compatibility", "security"]
                },
                "business": {
                    "patterns": ["process_optimization", "customer_focus", "data_driven"],
                    "innovation_areas": ["digital_transformation", "platform_economics", "personalization"],
                    "constraint_patterns": ["budget_limitation", "time_pressure", "regulatory"]
                },
                "creative": {
                    "patterns": ["divergent_thinking", "experimentation", "user_centered"],
                    "innovation_areas": ["interactive_experience", "emotional_design", "storytelling"],
                    "constraint_patterns": ["aesthetic_constraints", "brand_guidelines", "user_preferences"]
                },
                "social": {
                    "patterns": ["collaboration", "inclusivity", "sustainability"],
                    "innovation_areas": ["community_engagement", "social_impact", "accessibility"],
                    "constraint_patterns": ["cultural_sensitivity", "ethical_considerations", "diversity"]
                }
            }
            
            return domain_patterns.get(domain, domain_patterns["general"])
            
        except Exception as e:
            logger.error(f"도메인 패턴 분석 실패: {e}")
            return {"patterns": [], "innovation_areas": [], "constraint_patterns": []}
    
    def _analyze_problem_patterns(self, problem: str) -> Dict[str, Any]:
        """문제별 패턴 분석"""
        try:
            # 키워드 추출
            key_components = self._extract_key_components(problem)
            
            # 문제 유형 분류
            problem_types = {
                "optimization": 0,
                "automation": 0,
                "integration": 0,
                "user_experience": 0,
                "efficiency": 0,
                "innovation": 0
            }
            
            for component in key_components:
                component_lower = component.lower()
                if any(word in component_lower for word in ["최적화", "optimization", "개선", "improve"]):
                    problem_types["optimization"] += 1
                elif any(word in component_lower for word in ["자동화", "automation", "자동", "auto"]):
                    problem_types["automation"] += 1
                elif any(word in component_lower for word in ["통합", "integration", "연결", "connect"]):
                    problem_types["integration"] += 1
                elif any(word in component_lower for word in ["사용자", "user", "경험", "experience"]):
                    problem_types["user_experience"] += 1
                elif any(word in component_lower for word in ["효율", "efficiency", "성능", "performance"]):
                    problem_types["efficiency"] += 1
                elif any(word in component_lower for word in ["혁신", "innovation", "창의", "creative"]):
                    problem_types["innovation"] += 1
            
            primary_problem_type = max(problem_types.items(), key=lambda x: x[1])[0]
            
            return {
                "key_components": key_components,
                "problem_types": problem_types,
                "primary_problem_type": primary_problem_type,
                "problem_complexity": len(key_components)
            }
            
        except Exception as e:
            logger.error(f"문제 패턴 분석 실패: {e}")
            return {"key_components": [], "problem_types": {}, "primary_problem_type": "unknown"}
    
    def _extract_key_components(self, problem: str) -> List[str]:
        """키워드 추출"""
        try:
            # 간단한 키워드 추출 (실제로는 NLP 사용)
            words = problem.split()
            # 3글자 이상의 단어만 키워드로 간주
            keywords = [word for word in words if len(word) >= 3]
            return keywords[:10]  # 최대 10개 키워드
        except Exception as e:
            logger.error(f"키워드 추출 실패: {e}")
            return []
    
    def _analyze_pattern_connections(
        self,
        domain_patterns: Dict[str, Any],
        problem_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """패턴 연결 분석"""
        try:
            connections = []
            domain_pattern_list = domain_patterns.get("patterns", [])
            problem_type = problem_patterns.get("primary_problem_type", "unknown")
            
            for domain_pattern in domain_pattern_list:
                # 패턴과 문제 유형 간의 연결 강도 계산
                connection_strength = self._calculate_connection_strength(
                    domain_pattern, problem_type
                )
                
                if connection_strength > 0.3:  # 임계값 이상인 연결만 포함
                    connections.append({
                        "domain_pattern": domain_pattern,
                        "problem_type": problem_type,
                        "connection_strength": connection_strength,
                        "connection_type": "strong" if connection_strength > 0.6 else "moderate"
                    })
            
            return connections
            
        except Exception as e:
            logger.error(f"패턴 연결 분석 실패: {e}")
            return []
    
    def _calculate_connection_strength(self, pattern1: str, pattern2: str) -> float:
        """연결 강도 계산"""
        try:
            # 간단한 연결 강도 계산 (실제로는 더 복잡한 알고리즘 사용)
            pattern1_words = set(pattern1.split("_"))
            pattern2_words = set(pattern2.split("_"))
            
            # 공통 단어 수로 연결 강도 계산
            common_words = pattern1_words.intersection(pattern2_words)
            total_words = pattern1_words.union(pattern2_words)
            
            if total_words:
                return len(common_words) / len(total_words)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"연결 강도 계산 실패: {e}")
            return 0.0
    
    def _detect_innovation_opportunities(
        self,
        domain_patterns: Dict[str, Any],
        problem_patterns: Dict[str, Any],
        pattern_connections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """혁신 기회 탐지"""
        try:
            opportunities = []
            innovation_areas = domain_patterns.get("innovation_areas", [])
            problem_type = problem_patterns.get("primary_problem_type", "unknown")
            
            # 강한 연결이 있는 패턴들에서 혁신 기회 탐지
            strong_connections = [conn for conn in pattern_connections if conn.get("connection_strength", 0) > 0.6]
            
            for connection in strong_connections:
                for innovation_area in innovation_areas:
                    # 혁신 영역과 문제 유형의 적합성 평가
                    innovation_fit = self._calculate_connection_strength(innovation_area, problem_type)
                    
                    if innovation_fit > 0.4:
                        opportunities.append({
                            "innovation_area": innovation_area,
                            "problem_type": problem_type,
                            "fit_score": innovation_fit,
                            "potential_impact": "high" if innovation_fit > 0.7 else "medium"
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
        """패턴 신뢰도 계산"""
        try:
            # 도메인 패턴의 풍부성
            domain_pattern_count = len(domain_patterns.get("patterns", []))
            domain_confidence = min(1.0, domain_pattern_count / 5)
            
            # 문제 패턴의 명확성
            problem_complexity = problem_patterns.get("problem_complexity", 0)
            problem_confidence = min(1.0, problem_complexity / 10)
            
            # 종합 신뢰도
            total_confidence = (domain_confidence * 0.6 + problem_confidence * 0.4)
            
            return min(1.0, total_confidence)
            
        except Exception as e:
            logger.error(f"패턴 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _generate_ideas(
        self,
        context_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """아이디어 생성"""
        try:
            ideas = []
            
            # 1. 패턴 기반 아이디어 생성
            pattern_based_ideas = self._generate_pattern_based_ideas(context_analysis, pattern_analysis)
            ideas.extend(pattern_based_ideas)
            
            # 2. 혁신 기반 아이디어 생성
            innovation_based_ideas = self._generate_innovation_based_ideas(context_analysis, pattern_analysis)
            ideas.extend(innovation_based_ideas)
            
            # 3. 제약 조건 기반 아이디어 생성
            constraint_based_ideas = self._generate_constraint_based_ideas(context_analysis)
            ideas.extend(constraint_based_ideas)
            
            # 4. 목표 기반 아이디어 생성
            goal_based_ideas = self._generate_goal_based_ideas(context_analysis)
            ideas.extend(goal_based_ideas)
            
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
                    "type": "pattern_based",
                    "title": f"{pattern.replace('_', ' ').title()} 접근법",
                    "description": f"기존 {pattern} 패턴을 활용한 해결책",
                    "confidence": 0.7,
                    "innovation_level": "moderate",
                    "feasibility": "high"
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
        """혁신 기반 아이디어 생성"""
        try:
            ideas = []
            domain_patterns = pattern_analysis.get("domain_patterns", {})
            innovation_areas = domain_patterns.get("innovation_areas", [])
            
            for innovation_area in innovation_areas:
                idea = {
                    "type": "innovation_based",
                    "title": f"{innovation_area.replace('_', ' ').title()} 적용",
                    "description": f"최신 {innovation_area} 기술을 활용한 혁신적 해결책",
                    "confidence": 0.6,
                    "innovation_level": "high",
                    "feasibility": "medium"
                }
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"혁신 기반 아이디어 생성 실패: {e}")
            return []
    
    def _generate_constraint_based_ideas(self, context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """제약 조건 기반 아이디어 생성"""
        try:
            ideas = []
            constraint_analysis = context_analysis.get("constraint_analysis", {})
            primary_constraint = constraint_analysis.get("primary_constraint", "none")
            
            if primary_constraint != "none":
                idea = {
                    "type": "constraint_based",
                    "title": f"{primary_constraint.replace('_', ' ').title()} 제약 극복 방안",
                    "description": f"{primary_constraint} 제약을 창의적으로 해결하는 방법",
                    "confidence": 0.8,
                    "innovation_level": "high",
                    "feasibility": "medium"
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
            primary_goal = goal_analysis.get("primary_goal", "none")
            
            if primary_goal != "none":
                idea = {
                    "type": "goal_based",
                    "title": f"{primary_goal.replace('_', ' ').title()} 달성 전략",
                    "description": f"{primary_goal} 목표를 효과적으로 달성하는 창의적 전략",
                    "confidence": 0.75,
                    "innovation_level": "moderate",
                    "feasibility": "high"
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
                return {"innovation_score": 0, "innovation_level": "low"}
            
            # 각 아이디어의 혁신성 점수 계산
            innovation_scores = []
            for idea in ideas:
                innovation_level = idea.get("innovation_level", "moderate")
                level_scores = {"low": 0.3, "moderate": 0.6, "high": 0.9}
                innovation_scores.append(level_scores.get(innovation_level, 0.5))
            
            # 평균 혁신성 점수
            avg_innovation_score = sum(innovation_scores) / len(innovation_scores)
            
            # 혁신성 수준 결정
            if avg_innovation_score >= 0.7:
                innovation_level = "high"
            elif avg_innovation_score >= 0.4:
                innovation_level = "moderate"
            else:
                innovation_level = "low"
            
            return {
                "innovation_score": avg_innovation_score,
                "innovation_level": innovation_level,
                "idea_count": len(ideas),
                "high_innovation_ideas": len([score for score in innovation_scores if score >= 0.7])
            }
            
        except Exception as e:
            logger.error(f"혁신성 평가 실패: {e}")
            return {"innovation_score": 0, "innovation_level": "low"}
    
    def _calculate_innovation_confidence(
        self,
        ideas: List[Dict[str, Any]],
        pattern_analysis: Dict[str, Any]
    ) -> float:
        """혁신 신뢰도 계산"""
        try:
            if not ideas:
                return 0.0
            
            # 아이디어 품질 기반 신뢰도
            quality_scores = []
            for idea in ideas:
                confidence = idea.get("confidence", 0.5)
                feasibility = idea.get("feasibility", "medium")
                feasibility_scores = {"low": 0.3, "medium": 0.6, "high": 0.9}
                feasibility_score = feasibility_scores.get(feasibility, 0.5)
                
                quality_score = (confidence + feasibility_score) / 2
                quality_scores.append(quality_score)
            
            avg_quality = sum(quality_scores) / len(quality_scores)
            
            # 패턴 분석 신뢰도
            pattern_confidence = pattern_analysis.get("pattern_confidence", 0.5)
            
            # 종합 신뢰도
            total_confidence = (avg_quality * 0.7 + pattern_confidence * 0.3)
            
            return min(1.0, total_confidence)
            
        except Exception as e:
            logger.error(f"혁신 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _analyze_feasibility(
        self,
        ideas: List[Dict[str, Any]],
        context_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실현 가능성 분석"""
        try:
            if not ideas:
                return {"feasibility_score": 0, "feasibility_level": "low"}
            
            # 각 아이디어의 실현 가능성 평가
            feasibility_scores = []
            for idea in ideas:
                feasibility = idea.get("feasibility", "medium")
                feasibility_levels = {"low": 0.3, "medium": 0.6, "high": 0.9}
                feasibility_scores.append(feasibility_levels.get(feasibility, 0.5))
            
            # 평균 실현 가능성 점수
            avg_feasibility = sum(feasibility_scores) / len(feasibility_scores)
            
            # 실현 가능성 수준 결정
            if avg_feasibility >= 0.7:
                feasibility_level = "high"
            elif avg_feasibility >= 0.4:
                feasibility_level = "moderate"
            else:
                feasibility_level = "low"
            
            # 제약 조건 고려
            constraint_analysis = context_analysis.get("constraint_analysis", {})
            constraint_intensity = constraint_analysis.get("constraint_intensity", 0)
            
            # 제약 조건에 따른 조정
            adjusted_feasibility = avg_feasibility * (1 - constraint_intensity * 0.3)
            
            return {
                "feasibility_score": adjusted_feasibility,
                "feasibility_level": feasibility_level,
                "constraint_impact": constraint_intensity,
                "high_feasibility_ideas": len([score for score in feasibility_scores if score >= 0.7])
            }
            
        except Exception as e:
            logger.error(f"실현 가능성 분석 실패: {e}")
            return {"feasibility_score": 0, "feasibility_level": "low"}
    
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
            innovation_score = innovation_assessment.get("innovation_score", 0)
            
            # 실현 가능성 점수
            feasibility_score = feasibility_analysis.get("feasibility_score", 0)
            
            # 아이디어 다양성 점수
            idea_diversity = len(set(idea.get("type", "") for idea in ideas))
            diversity_score = min(1.0, idea_diversity / 4)  # 4가지 타입을 최대 다양성으로 가정
            
            # 종합 창의성 점수 계산
            creativity_score = (
                innovation_score * 0.4 +
                feasibility_score * 0.3 +
                diversity_score * 0.3
            )
            
            return min(1.0, creativity_score)
            
        except Exception as e:
            logger.error(f"창의적 사고 점수 계산 실패: {e}")
            return 0.0
    
    def get_creative_thinking_stats(self) -> Dict[str, Any]:
        """창의적 사고 통계 조회"""
        try:
            # 최근 24시간 데이터 분석
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            # 창의적 사고 패턴 분석
            creative_patterns = self._analyze_creative_patterns(cutoff_time)
            
            # 창의성 점수 계산
            creativity_score = self._calculate_overall_creativity_score(creative_patterns)
            
            return {
                "creativity_score": creativity_score,
                "creative_patterns": creative_patterns,
                "analysis_period": "24_hours",
                "confidence_level": 0.85
            }
            
        except Exception as e:
            logger.error(f"창의적 사고 통계 조회 실패: {e}")
            return {"error": str(e)}
    
    def _analyze_creative_patterns(self, cutoff_time: datetime) -> List[Dict[str, Any]]:
        """창의적 패턴 분석"""
        try:
            # 최근 메모리 엔트리 조회 (임시로 빈 리스트 반환)
            recent_memories = []
            
            patterns = []
            
            for memory in recent_memories:
                if memory.context and "creative" in memory.context.lower():
                    # 창의적 사고 패턴 분석
                    creative_pattern = {
                        "timestamp": memory.timestamp.isoformat(),
                        "context": memory.context,
                        "creativity_level": "high" if "innovation" in memory.context.lower() else "moderate"
                    }
                    patterns.append(creative_pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"창의적 패턴 분석 실패: {e}")
            return []
    
    def _calculate_overall_creativity_score(self, patterns: List[Dict[str, Any]]) -> float:
        """전체 창의성 점수 계산"""
        try:
            if not patterns:
                return 0.5
            
            # 창의성 수준별 점수
            creativity_levels = {"low": 0.3, "moderate": 0.6, "high": 0.9}
            level_scores = [creativity_levels.get(p.get("creativity_level", "moderate"), 0.5) for p in patterns]
            
            # 평균 창의성 점수
            avg_creativity = sum(level_scores) / len(level_scores)
            
            return min(1.0, avg_creativity)
            
        except Exception as e:
            logger.error(f"전체 창의성 점수 계산 실패: {e}")
            return 0.5 