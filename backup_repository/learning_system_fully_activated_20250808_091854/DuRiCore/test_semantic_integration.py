#!/usr/bin/env python3
"""
DuRiCore Phase 6.2.6 - 시맨틱 지식 연결망 통합 테스트
시맨틱 지식 연결망 시스템의 기능과 통합 시스템과의 연동을 테스트
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# 테스트 대상 시스템들
from semantic_knowledge_graph import SemanticKnowledgeGraph, ConceptType, InferenceType
from enhanced_memory_system import EnhancedMemorySystem
from integrated_system_manager import IntegratedSystemManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SemanticIntegrationTest:
    """시맨틱 지식 연결망 통합 테스트 클래스"""
    
    def __init__(self):
        """초기화"""
        self.semantic_graph = SemanticKnowledgeGraph()
        self.memory_system = EnhancedMemorySystem()
        self.integrated_manager = IntegratedSystemManager()
        self.test_results = []
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        logger.info("=== 시맨틱 지식 연결망 통합 테스트 시작 ===")
        start_time = time.time()
        
        # 테스트 시나리오들
        test_scenarios = [
            ("시맨틱 기본 기능 테스트", self.test_semantic_basic_functionality),
            ("시맨틱 개념 관리 테스트", self.test_semantic_concept_management),
            ("시맨틱 추론 시스템 테스트", self.test_semantic_inference_system),
            ("시맨틱 경로 찾기 테스트", self.test_semantic_path_finding),
            ("시맨틱 지식 추론 테스트", self.test_semantic_knowledge_inference),
            ("메모리 시스템 통합 테스트", self.test_memory_system_integration),
            ("통합 시스템 매니저 테스트", self.test_integrated_system_manager)
        ]
        
        # 각 테스트 실행
        for test_name, test_func in test_scenarios:
            try:
                logger.info(f"테스트 실행: {test_name}")
                test_start = time.time()
                success = await test_func()
                test_duration = time.time() - test_start
                
                test_result = {
                    'test_name': test_name,
                    'success': success,
                    'duration': test_duration,
                    'timestamp': datetime.now().isoformat()
                }
                self.test_results.append(test_result)
                
                logger.info(f"테스트 완료: {test_name} - 성공: {success}")
                
            except Exception as e:
                logger.error(f"테스트 실패: {test_name} - {e}")
                test_result = {
                    'test_name': test_name,
                    'success': False,
                    'error': str(e),
                    'duration': 0,
                    'timestamp': datetime.now().isoformat()
                }
                self.test_results.append(test_result)
        
        # 전체 결과 계산
        total_duration = time.time() - start_time
        successful_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # 결과 요약
        summary = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': total_tests - successful_tests,
            'success_rate': success_rate,
            'total_duration': total_duration,
            'test_results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }
        
        # 결과 출력
        print(f"\n=== 시맨틱 지식 연결망 통합 테스트 결과 ===")
        print(f"총 테스트 수: {total_tests}")
        print(f"성공한 테스트: {successful_tests}")
        print(f"실패한 테스트: {total_tests - successful_tests}")
        print(f"성공률: {success_rate:.1f}%")
        print(f"총 소요 시간: {total_duration:.3f}초")
        
        if failed_tests := [r for r in self.test_results if not r['success']]:
            print(f"\n실패한 테스트들:")
            for result in failed_tests:
                print(f"  - {result['test_name']}: {result.get('error', '알 수 없는 오류')}")
        
        # 결과를 파일로 저장
        with open('semantic_integration_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info("테스트 결과가 semantic_integration_test_results.json에 저장되었습니다.")
        return summary
    
    async def test_semantic_basic_functionality(self) -> bool:
        """시맨틱 기본 기능 테스트"""
        try:
            # 기본 개념 추가
            concept_id = await self.semantic_graph.add_concept(
                "테스트 개념", ConceptType.ENTITY, "테스트용 개념"
            )
            
            if not concept_id:
                return False
            
            # 기본 추론 추가
            edge_id = await self.semantic_graph.add_inference(
                "테스트 개념", "관련 개념", InferenceType.ASSOCIATED_WITH, 0.8
            )
            
            if not edge_id:
                return False
            
            # 그래프 상태 확인
            status = await self.semantic_graph.get_knowledge_graph_status()
            
            if status.concept_count < 1 or status.edge_count < 1:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"시맨틱 기본 기능 테스트 실패: {e}")
            return False
    
    async def test_semantic_concept_management(self) -> bool:
        """시맨틱 개념 관리 테스트"""
        try:
            # 다양한 개념들 추가
            concepts = [
                ("사람", ConceptType.ENTITY, "인간 개체"),
                ("동물", ConceptType.ENTITY, "동물 개체"),
                ("이동", ConceptType.ACTION, "움직이는 행동"),
                ("생각", ConceptType.ACTION, "머리로 생각하는 행동"),
                ("크다", ConceptType.PROPERTY, "크기가 큰 속성"),
                ("빠르다", ConceptType.PROPERTY, "속도가 빠른 속성")
            ]
            
            concept_ids = []
            for name, concept_type, description in concepts:
                concept_id = await self.semantic_graph.add_concept(
                    name, concept_type, description
                )
                if concept_id:
                    concept_ids.append(concept_id)
            
            if len(concept_ids) < len(concepts) * 0.8:  # 80% 이상 성공해야 함
                return False
            
            # 개념 유사도 분석
            similarity = await self.semantic_graph.analyze_semantic_similarity("사람", "동물")
            
            if similarity < 0.0 or similarity > 1.0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"시맨틱 개념 관리 테스트 실패: {e}")
            return False
    
    async def test_semantic_inference_system(self) -> bool:
        """시맨틱 추론 시스템 테스트"""
        try:
            # 다양한 추론들 추가
            inferences = [
                ("사람", "동물", InferenceType.IS_A, 0.9),
                ("동물", "이동", InferenceType.CAN_DO, 0.8),
                ("사람", "생각", InferenceType.CAN_DO, 0.9),
                ("사람", "크다", InferenceType.HAS_PROPERTY, 0.7),
                ("동물", "빠르다", InferenceType.HAS_PROPERTY, 0.6)
            ]
            
            edge_ids = []
            for source, target, inference_type, confidence in inferences:
                edge_id = await self.semantic_graph.add_inference(
                    source, target, inference_type, confidence
                )
                if edge_id:
                    edge_ids.append(edge_id)
            
            if len(edge_ids) < len(inferences) * 0.8:  # 80% 이상 성공해야 함
                return False
            
            # 그래프 상태 확인
            status = await self.semantic_graph.get_knowledge_graph_status()
            
            if status.edge_count < len(edge_ids):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"시맨틱 추론 시스템 테스트 실패: {e}")
            return False
    
    async def test_semantic_path_finding(self) -> bool:
        """시맨틱 경로 찾기 테스트"""
        try:
            # 경로 찾기 테스트
            path_result = await self.semantic_graph.find_semantic_path("사람", "이동", 3)
            
            if not path_result:
                # 경로가 없어도 정상 (개념이 충분하지 않을 수 있음)
                return True
            
            # 경로 정보 확인
            if not hasattr(path_result, 'source_concept') or not hasattr(path_result, 'target_concept'):
                return False
            
            if not hasattr(path_result, 'total_confidence') or not hasattr(path_result, 'path_length'):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"시맨틱 경로 찾기 테스트 실패: {e}")
            return False
    
    async def test_semantic_knowledge_inference(self) -> bool:
        """시맨틱 지식 추론 테스트"""
        try:
            # 지식 추론 테스트
            inferences = await self.semantic_graph.infer_new_knowledge("사람")
            
            # 추론 결과가 리스트 형태인지 확인
            if not isinstance(inferences, list):
                return False
            
            # 추가 추론 테스트
            inferences2 = await self.semantic_graph.infer_new_knowledge("동물")
            
            if not isinstance(inferences2, list):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"시맨틱 지식 추론 테스트 실패: {e}")
            return False
    
    async def test_memory_system_integration(self) -> bool:
        """메모리 시스템 통합 테스트"""
        try:
            # 메모리 시스템의 시맨틱 기능들 테스트
            
            # 시맨틱 개념 추가
            concept_id = await self.memory_system.add_semantic_concept(
                "메모리 테스트 개념", ConceptType.ENTITY, "메모리 시스템 통합 테스트용 개념"
            )
            
            if not concept_id:
                return False
            
            # 시맨틱 추론 추가
            edge_id = await self.memory_system.add_semantic_inference(
                "메모리 테스트 개념", "관련 개념", InferenceType.ASSOCIATED_WITH, 0.7
            )
            
            if not edge_id:
                return False
            
            # 시맨틱 경로 찾기
            path_result = await self.memory_system.find_semantic_path(
                "메모리 테스트 개념", "관련 개념", 3
            )
            
            # 경로가 없어도 정상 (개념이 충분하지 않을 수 있음)
            if path_result and not path_result.get('success', False):
                return False
            
            # 시맨틱 지식 추론
            inferences = await self.memory_system.infer_semantic_knowledge("메모리 테스트 개념")
            
            if not isinstance(inferences, list):
                return False
            
            # 시맨틱 그래프 상태 확인
            graph_status = await self.memory_system.get_semantic_graph_status()
            
            if not graph_status.get('success', False):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"메모리 시스템 통합 테스트 실패: {e}")
            return False
    
    async def test_integrated_system_manager(self) -> bool:
        """통합 시스템 매니저 테스트"""
        try:
            # 통합 시스템 매니저의 시맨틱 기능 테스트
            
            # 통합 사이클 실행
            test_context = {
                'situation': '시맨틱 지식 연결망 테스트 상황',
                'priority': 'high',
                'complexity': 'medium',
                'emotion': {'type': 'excited', 'intensity': 0.8},
                'available_resources': ['time', 'energy', 'attention']
            }
            
            result = await self.integrated_manager.run_integrated_cycle(test_context)
            
            # 결과에 시맨틱 관련 정보가 포함되어 있는지 확인
            if 'semantic_result' not in result:
                return False
            
            semantic_result = result['semantic_result']
            
            # 시맨틱 결과의 기본 필드들 확인
            required_fields = ['concepts_added', 'inferences_added', 'success']
            for field in required_fields:
                if field not in semantic_result:
                    return False
            
            # 성공 여부 확인
            if not semantic_result.get('success', False):
                return False
            
            # 시스템 상태 확인
            status = await self.integrated_manager.get_system_status()
            
            if 'semantic_knowledge' not in status.get('systems', {}):
                return False
            
            if status['systems']['semantic_knowledge'] != 'active':
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"통합 시스템 매니저 테스트 실패: {e}")
            return False

async def main():
    """메인 테스트 함수"""
    logger.info("시맨틱 지식 연결망 통합 테스트 시작")
    
    # 테스트 실행
    test_runner = SemanticIntegrationTest()
    results = await test_runner.run_all_tests()
    
    # 결과 출력
    print(f"\n=== 최종 테스트 결과 ===")
    print(f"성공률: {results['success_rate']:.1f}%")
    print(f"총 소요 시간: {results['total_duration']:.3f}초")
    
    if results['success_rate'] >= 80:
        print("✅ 시맨틱 지식 연결망 통합 테스트 성공!")
    else:
        print("❌ 시맨틱 지식 연결망 통합 테스트 실패")

if __name__ == "__main__":
    asyncio.run(main()) 