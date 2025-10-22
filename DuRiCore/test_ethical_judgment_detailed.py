#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 9: 윤리적 판단 시스템 상세 테스트
"""

import asyncio
import logging
import os
import sys

# DuRiCore 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ethical_judgment_system import (EthicalDilemmaType, EthicalJudgmentSystem,
                                     EthicalPrinciple)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_ethical_judgment_system_detailed():
    """윤리적 판단 시스템 상세 테스트"""
    print("🧠 Day 9: 윤리적 판단 시스템 상세 테스트 시작")
    print("=" * 60)

    # 시스템 생성
    judgment_system = EthicalJudgmentSystem()
    print("✅ 윤리적 판단 시스템 초기화 완료")

    # 테스트 상황 데이터
    test_situations = [
        {
            "description": "개인정보 수집과 서비스 개선 사이의 윤리적 딜레마",
            "stakeholders": ["개인", "조직", "사회"],
            "consequences": ["개인정보 보호", "서비스 품질 향상", "사용자 경험 개선"],
            "context": {"privacy": True, "service_improvement": True},
        },
        {
            "description": "공정한 채용과 다양성 확보 사이의 균형",
            "stakeholders": ["지원자", "조직", "사회"],
            "consequences": ["공정성 보장", "다양성 확보", "조직 문화 개선"],
            "context": {"fairness": True, "diversity": True},
        },
        {
            "description": "환경 보호와 경제 발전 사이의 갈등",
            "stakeholders": ["환경", "경제", "미래 세대"],
            "consequences": ["환경 보호", "경제 성장", "지속 가능성"],
            "context": {"environment": True, "economy": True},
        },
    ]

    print(f"\n📋 {len(test_situations)}개 테스트 상황 분석 시작...")

    # 상황 분석 및 판단
    for i, situation_data in enumerate(test_situations, 1):
        print(f"\n🔍 상황 {i}: {situation_data['description']}")
        print("-" * 40)

        # 윤리적 상황 분석
        situation = await judgment_system.analyze_ethical_situation(situation_data)
        print(f"  • 상황 ID: {situation.situation_id}")
        print(f"  • 관련 원칙: {[p.value for p in situation.involved_principles]}")
        print(f"  • 이해관계자: {situation.stakeholders}")
        print(f"  • 복잡성 수준: {situation.complexity_level:.2f}")
        print(f"  • 긴급성 수준: {situation.urgency_level:.2f}")

        # 윤리적 판단 수행
        judgment = await judgment_system.make_ethical_judgment(situation)
        print(f"  • 판단 ID: {judgment.judgment_id}")
        print(f"  • 결정: {judgment.decision}")
        print(f"  • 신뢰도: {judgment.confidence.value}")
        print(f"  • 윤리적 점수: {judgment.ethical_score:.3f}")

        # 윤리적 갈등 해결
        if situation.dilemma_type:
            conflict = await judgment_system.resolve_ethical_conflict(situation)
            print(f"  • 갈등 ID: {conflict.conflict_id}")
            print(f"  • 갈등 강도: {conflict.conflict_intensity:.2f}")
            print(f"  • 해결 접근법: {conflict.resolution_approach}")
            if conflict.compromise_solution:
                print(f"  • 타협 해결책: {conflict.compromise_solution}")

    print(f"\n📊 윤리적 성숙도 평가...")

    # 윤리적 성숙도 평가
    maturity = await judgment_system.assess_ethical_maturity()
    print(f"  • 전체 성숙도: {maturity['score']:.3f}")
    print(f"  • 성숙도 수준: {maturity['maturity_level']}")

    # detailed_scores가 있는지 확인
    if "detailed_scores" in maturity:
        detailed_scores = maturity["detailed_scores"]
        print(f"  • 원칙 이해도: {detailed_scores['principle_understanding']:.3f}")
        print(f"  • 갈등 해결 능력: {detailed_scores['conflict_resolution']:.3f}")
        print(f"  • 도덕적 추론: {detailed_scores['moral_reasoning']:.3f}")
        print(f"  • 윤리적 일관성: {detailed_scores['ethical_consistency']:.3f}")
        print(f"  • 도덕적 상상력: {detailed_scores['moral_imagination']:.3f}")
    else:
        # 기본 메트릭 사용
        metrics = judgment_system.judgment_state.maturity_metrics
        print(f"  • 원칙 이해도: {metrics.principle_understanding:.3f}")
        print(f"  • 갈등 해결 능력: {metrics.conflict_resolution:.3f}")
        print(f"  • 도덕적 추론: {metrics.moral_reasoning:.3f}")
        print(f"  • 윤리적 일관성: {metrics.ethical_consistency:.3f}")
        print(f"  • 도덕적 상상력: {metrics.moral_imagination:.3f}")

    print(f"\n📈 개선 영역...")
    if "areas" in maturity and maturity["areas"]:
        for area in maturity["areas"]:
            print(f"  • {area}")
    else:
        print(f"  • 개선 영역이 없습니다.")

    print(f"\n📋 보고서 생성...")

    # 보고서 생성
    report = await judgment_system.generate_ethical_report()
    print(f"  • 총 분석된 상황: {report['total_situations']}개")
    print(f"  • 총 수행된 판단: {report['total_judgments']}개")
    print(f"  • 총 해결된 갈등: {report['total_conflicts']}개")
    print(f"  • 평균 신뢰도: {report['average_confidence']:.3f}")
    print(f"  • 평균 윤리적 점수: {report['average_ethical_score']:.3f}")

    print(f"\n🎯 시스템 상태 확인...")

    # 시스템 상태 확인
    state = judgment_system.get_judgment_state()
    print(f"  • 윤리적 상황: {len(state['ethical_situations'])}개")
    print(f"  • 윤리적 판단: {len(state['ethical_judgments'])}개")
    print(f"  • 윤리적 갈등: {len(state['ethical_conflicts'])}개")
    print(f"  • 판단 이력: {len(state['judgment_history'])}개")

    print(f"\n" + "=" * 60)
    print("✅ Day 9: 윤리적 판단 시스템 상세 테스트 완료!")
    print(f"📊 최종 결과:")
    print(f"  • 윤리적 성숙도: {maturity['score']:.3f} ({maturity['maturity_level']})")
    print(f"  • 분석된 상황: {len(judgment_system.judgment_state.ethical_situations)}개")
    print(f"  • 수행된 판단: {len(judgment_system.judgment_state.ethical_judgments)}개")
    print(f"  • 해결된 갈등: {len(judgment_system.judgment_state.ethical_conflicts)}개")

    return {
        "maturity_score": maturity["score"],
        "maturity_level": maturity["maturity_level"],
        "total_situations": len(judgment_system.judgment_state.ethical_situations),
        "total_judgments": len(judgment_system.judgment_state.ethical_judgments),
        "total_conflicts": len(judgment_system.judgment_state.ethical_conflicts),
        "success": True,
    }


if __name__ == "__main__":
    result = asyncio.run(test_ethical_judgment_system_detailed())
    if result["success"]:
        print(f"\n🎉 Day 9 테스트 성공! 윤리적 성숙도: {result['maturity_score']:.3f}")
    else:
        print(f"\n❌ Day 9 테스트 실패!")
