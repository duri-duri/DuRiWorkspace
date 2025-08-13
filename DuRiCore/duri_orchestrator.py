from DuRiCore.trace import emit_trace
"""
DuRi Orchestrator
DuRi의 중앙 제어 시스템 - DuRi의 심장

기능:
1. judgment → action → feedback 실행 루프 관리
2. 시스템 간 통합 및 조율
3. 상태 관리 및 모니터링
4. 의사결정 엔진
"""
import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import importlib
import sys
try:
    from module_registry import ModuleRegistry, BaseModule, ModuleState, ModulePriority
    MODULE_REGISTRY_AVAILABLE = True
except ImportError:
    MODULE_REGISTRY_AVAILABLE = False
    emit_trace('info', ' '.join(map(str, ['⚠️  모듈 레지스트리 시스템을 찾을 수 없습니다. 기본 모드로 실행됩니다.'])))
try:
    from system_adapters import SystemAdapterFactory, wrap_existing_systems
    SYSTEM_ADAPTERS_AVAILABLE = True
except ImportError:
    SYSTEM_ADAPTERS_AVAILABLE = False
    emit_trace('info', ' '.join(map(str, ['⚠️  시스템 어댑터를 찾을 수 없습니다. 기본 모드로 실행됩니다.'])))
try:
    from act_r_parallel_processor import ACTRParallelProcessor
    ACTR_AVAILABLE = True
except ImportError:
    ACTR_AVAILABLE = False
    emit_trace('info', ' '.join(map(str, ['⚠️  ACT-R 병렬 처리 시스템을 찾을 수 없습니다. 기본 모드로 실행됩니다.'])))
try:
    from lida_attention_system import LIDAAttentionSystem
    LIDA_AVAILABLE = True
except ImportError:
    LIDA_AVAILABLE = False
    emit_trace('info', ' '.join(map(str, ['⚠️  LIDA 주의 시스템을 찾을 수 없습니다. 기본 모드로 실행됩니다.'])))
try:
    from coala_module_interface import CoALAModuleInterface
    COALA_AVAILABLE = True
except ImportError:
    COALA_AVAILABLE = False
    emit_trace('info', ' '.join(map(str, ['⚠️  CoALA 모듈 인터페이스를 찾을 수 없습니다. 기본 모드로 실행됩니다.'])))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """시스템 상태 정보"""
    name: str
    status: str
    last_activity: datetime
    error_count: int = 0
    performance_score: float = 0.0

@dataclass
class ExecutionContext:
    """실행 컨텍스트"""
    input_data: Any
    current_phase: str
    system_states: Dict[str, SystemStatus]
    execution_history: List[Dict]
    metadata: Dict[str, Any]

class DuRiOrchestrator:
    """DuRi 오케스트레이터 - 중앙 제어 시스템"""

    def __init__(self):
        self.systems: Dict[str, Any] = {}
        self.system_status: Dict[str, SystemStatus] = {}
        self.execution_loop_active = False
        self.error_log: List[str] = []
        self.performance_metrics: Dict[str, Any] = {}
        if MODULE_REGISTRY_AVAILABLE:
            self.registry = ModuleRegistry.get_instance()
            logger.info('✅ 모듈 레지스트리 시스템 초기화 완료')
        else:
            self.registry = None
            logger.warning('⚠️  모듈 레지스트리 시스템을 사용할 수 없습니다')
        self._initialize_systems()
        self.parallel_processor = None
        if ACTR_AVAILABLE:
            try:
                self.parallel_processor = ACTRParallelProcessor()
                logger.info('✅ ACT-R 병렬 처리 시스템 초기화 완료')
            except Exception as e:
                logger.warning(f'⚠️  ACT-R 병렬 처리 시스템 초기화 실패: {e}')
        self.attention_system = None
        if LIDA_AVAILABLE:
            try:
                self.attention_system = LIDAAttentionSystem()
                logger.info('✅ LIDA 주의 시스템 초기화 완료')
            except Exception as e:
                logger.warning(f'⚠️  LIDA 주의 시스템 초기화 실패: {e}')
        self.coala_interface = None
        if COALA_AVAILABLE:
            try:
                self.coala_interface = CoALAModuleInterface()
                logger.info('✅ CoALA 모듈 인터페이스 초기화 완료')
            except Exception as e:
                logger.warning(f'⚠️  CoALA 모듈 인터페이스 초기화 실패: {e}')

    def _initialize_systems(self):
        """시스템 초기화"""
        logger.info('🔧 시스템 초기화 시작')
        if MODULE_REGISTRY_AVAILABLE and self.registry:
            self._load_systems_with_registry()
        else:
            self._load_existing_systems()
        self._check_core_systems()
        self._initialize_system_status()
        logger.info('🔧 시스템 초기화 완료')

    def _load_systems_with_registry(self):
        """모듈 레지스트리를 사용한 시스템 로드"""
        logger.info('📦 모듈 레지스트리를 사용한 시스템 로드 중...')
        try:
            all_modules = self.registry.get_all_modules()
            for (module_name, module_info) in all_modules.items():
                try:
                    instance = self.registry.get_module_instance(module_name)
                    if instance:
                        self.systems[module_name] = instance
                        logger.info(f'✅ {module_name} 로드 성공 (레지스트리)')
                    else:
                        logger.warning(f'⚠️  {module_name} 인스턴스 없음')
                except Exception as e:
                    logger.warning(f'⚠️  {module_name} 로드 실패: {e}')
                    self.error_log.append(f'{module_name} 로드 실패: {e}')
            if SYSTEM_ADAPTERS_AVAILABLE:
                self._wrap_existing_systems_with_adapters()
            logger.info(f'✅ 모듈 레지스트리 로드 완료: {len(self.systems)}개 모듈')
        except Exception as e:
            logger.error(f'❌ 모듈 레지스트리 로드 실패: {e}')
            self.error_log.append(f'모듈 레지스트리 로드 실패: {e}')

    def _wrap_existing_systems_with_adapters(self):
        """기존 시스템들을 어댑터로 래핑"""
        logger.info('🔧 기존 시스템들을 어댑터로 래핑 중...')
        try:
            wrapped_systems = {}
            for (system_name, system) in self.systems.items():
                try:
                    adapter = SystemAdapterFactory.create_adapter(system_name, system)
                    if adapter:
                        wrapped_systems[system_name] = adapter
                        logger.info(f'✅ {system_name} 어댑터 래핑 완료')
                except Exception as e:
                    logger.warning(f'⚠️  {system_name} 어댑터 래핑 실패: {e}')
            for (system_name, adapter) in wrapped_systems.items():
                if system_name not in self.systems or isinstance(self.systems[system_name], BaseModule):
                    self.systems[system_name] = adapter
                    logger.info(f'✅ {system_name} 어댑터 적용 완료')
            logger.info(f'✅ 시스템 어댑터 래핑 완료: {len(wrapped_systems)}개 시스템')
        except Exception as e:
            logger.error(f'❌ 시스템 어댑터 래핑 실패: {e}')
            self.error_log.append(f'시스템 어댑터 래핑 실패: {e}')

    def _load_existing_systems(self):
        """기존 시스템들 로드 (하위 호환성)"""
        logger.info('📦 기존 시스템 로드 중...')
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        systems_to_load = ['judgment_system', 'action_system', 'feedback_system', 'memory_association', 'memory_classification', 'enhanced_memory_system']
        for system_name in systems_to_load:
            try:
                module = importlib.import_module(system_name)
                self.systems[system_name] = module
                logger.info(f'✅ {system_name} 로드 성공')
            except ImportError as e:
                logger.warning(f'⚠️  {system_name} 로드 실패: {e}')
                self.error_log.append(f'{system_name} 로드 실패: {e}')

    def _check_core_systems(self):
        """핵심 시스템 상태 확인"""
        logger.info('🔍 핵심 시스템 상태 확인...')
        core_systems = ['judgment_system', 'action_system', 'feedback_system']
        for system_name in core_systems:
            if system_name in self.systems:
                logger.info(f'✅ {system_name} 존재')
            else:
                logger.warning(f'⚠️  {system_name} 없음 - 대체 구현 필요')

    def _initialize_system_status(self):
        """시스템 상태 초기화"""
        for system_name in self.systems.keys():
            self.system_status[system_name] = SystemStatus(name=system_name, status='inactive', last_activity=datetime.now(), error_count=0, performance_score=0.0)

    async def start_execution_loop(self):
        """실행 루프 시작"""
        logger.info('🚀 DuRi 실행 루프 시작')
        if self.execution_loop_active:
            logger.warning('⚠️  실행 루프가 이미 활성화되어 있습니다')
            return
        self.execution_loop_active = True
        try:
            while self.execution_loop_active:
                await self._execute_judgment_phase()
                await self._execute_action_phase()
                await self._execute_feedback_phase()
                await self._update_system_status()
                await self._monitor_performance()
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f'❌ 실행 루프 오류: {e}')
            self.error_log.append(f'실행 루프 오류: {e}')
            self.execution_loop_active = False

    async def _execute_judgment_phase(self):
        """판단 단계 실행 (ACT-R 병렬 처리 적용)"""
        logger.info('🧠 Judgment Phase 실행')
        try:
            if self.attention_system and self.parallel_processor:
                judgment_tasks = [lambda : self._call_judgment_system() if 'judgment_system' in self.systems else self._default_judgment(), lambda : self._analyze_context(), lambda : self._evaluate_priority()]
                attention_context = {'type': 'judgment_phase', 'data': '시스템 판단'}
                lida_judgment = await self.attention_system.make_human_like_judgment(attention_context)
                judgment_results = await self.parallel_processor.execute_judgment_parallel(judgment_tasks)
                judgment_result = judgment_results[0] if judgment_results else None
                if judgment_result and isinstance(judgment_result, dict):
                    judgment_result['lida_attention'] = lida_judgment
                    judgment_result['human_like_accuracy'] = lida_judgment.get('accuracy', 0.0)
                logger.info(f'✅ LIDA + 병렬 판단 결과: {judgment_result}')
            elif self.parallel_processor:
                judgment_tasks = [lambda : self._call_judgment_system() if 'judgment_system' in self.systems else self._default_judgment(), lambda : self._analyze_context(), lambda : self._evaluate_priority()]
                judgment_results = await self.parallel_processor.execute_judgment_parallel(judgment_tasks)
                judgment_result = judgment_results[0] if judgment_results else None
                logger.info(f'✅ 병렬 판단 결과: {judgment_result}')
            elif 'judgment_system' in self.systems:
                judgment_result = await self._call_judgment_system()
                logger.info(f'✅ 판단 결과: {judgment_result}')
            else:
                judgment_result = await self._default_judgment()
                logger.info(f'✅ 기본 판단 결과: {judgment_result}')
            self._store_judgment_result(judgment_result)
        except Exception as e:
            logger.error(f'❌ Judgment Phase 오류: {e}')
            self.error_log.append(f'Judgment Phase 오류: {e}')

    async def _execute_action_phase(self):
        """행동 단계 실행 (ACT-R 병렬 처리 적용)"""
        logger.info('⚡ Action Phase 실행')
        try:
            if self.parallel_processor:
                action_tasks = [lambda : self._call_action_system() if 'action_system' in self.systems else self._default_action(), lambda : self._update_memory(), lambda : self._prepare_response()]
                action_results = await self.parallel_processor.execute_action_parallel(action_tasks)
                action_result = action_results[0] if action_results else None
                logger.info(f'✅ 병렬 행동 결과: {action_result}')
            elif 'action_system' in self.systems:
                action_result = await self._call_action_system()
                logger.info(f'✅ 행동 결과: {action_result}')
            else:
                action_result = await self._default_action()
                logger.info(f'✅ 기본 행동 결과: {action_result}')
            self._store_action_result(action_result)
        except Exception as e:
            logger.error(f'❌ Action Phase 오류: {e}')
            self.error_log.append(f'Action Phase 오류: {e}')

    async def _execute_feedback_phase(self):
        """피드백 단계 실행 (ACT-R 병렬 처리 적용)"""
        logger.info('🔄 Feedback Phase 실행')
        try:
            if self.parallel_processor:
                feedback_tasks = [lambda : self._call_feedback_system() if 'feedback_system' in self.systems else self._default_feedback(), lambda : self._evaluate_performance(), lambda : self._plan_next_steps()]
                feedback_results = await self.parallel_processor.execute_feedback_parallel(feedback_tasks)
                feedback_result = feedback_results[0] if feedback_results else None
                logger.info(f'✅ 병렬 피드백 결과: {feedback_result}')
            elif 'feedback_system' in self.systems:
                feedback_result = await self._call_feedback_system()
                logger.info(f'✅ 피드백 결과: {feedback_result}')
            else:
                feedback_result = await self._default_feedback()
                logger.info(f'✅ 기본 피드백 결과: {feedback_result}')
            self._store_feedback_result(feedback_result)
        except Exception as e:
            logger.error(f'❌ Feedback Phase 오류: {e}')
            self.error_log.append(f'Feedback Phase 오류: {e}')

    async def _call_judgment_system(self):
        """판단 시스템 호출"""
        try:
            judgment_module = self.systems['judgment_system']
            if hasattr(judgment_module, 'JudgmentSystem'):
                judgment_system = judgment_module.JudgmentSystem()
                if hasattr(judgment_system, 'main'):
                    result = await judgment_system.main()
                    return result
                elif hasattr(judgment_system, 'judge'):
                    result = await judgment_system.judge({})
                    return result
                else:
                    return {'status': 'no_judgment_function', 'message': '판단 함수를 찾을 수 없음'}
            else:
                return {'status': 'no_judgment_class', 'message': 'JudgmentSystem 클래스를 찾을 수 없음'}
        except Exception as e:
            logger.error(f'❌ 판단 시스템 호출 실패: {e}')
            return {'status': 'error', 'message': str(e)}

    async def _call_action_system(self):
        """행동 시스템 호출"""
        try:
            action_module = self.systems['action_system']
            if hasattr(action_module, 'ActionSystem'):
                action_system = action_module.ActionSystem()
                if hasattr(action_system, 'main'):
                    result = await action_system.main()
                    return result
                elif hasattr(action_system, 'act'):
                    result = await action_system.act({})
                    return result
                else:
                    return {'status': 'no_action_function', 'message': '행동 함수를 찾을 수 없음'}
            else:
                return {'status': 'no_action_class', 'message': 'ActionSystem 클래스를 찾을 수 없음'}
        except Exception as e:
            logger.error(f'❌ 행동 시스템 호출 실패: {e}')
            return {'status': 'error', 'message': str(e)}

    async def _call_feedback_system(self):
        """피드백 시스템 호출"""
        try:
            feedback_module = self.systems['feedback_system']
            if hasattr(feedback_module, 'FeedbackSystem'):
                feedback_system = feedback_module.FeedbackSystem()
                if hasattr(feedback_system, 'main'):
                    result = await feedback_system.main()
                    return result
                elif hasattr(feedback_system, 'feedback'):
                    result = await feedback_system.feedback({})
                    return result
                else:
                    return {'status': 'no_feedback_function', 'message': '피드백 함수를 찾을 수 없음'}
            else:
                return {'status': 'no_feedback_class', 'message': 'FeedbackSystem 클래스를 찾을 수 없음'}
        except Exception as e:
            logger.error(f'❌ 피드백 시스템 호출 실패: {e}')
            return {'status': 'error', 'message': str(e)}

    async def _default_judgment(self):
        """기본 판단 로직"""
        return {'phase': 'judgment', 'status': 'success', 'decision': 'continue_execution', 'confidence': 0.8, 'timestamp': datetime.now().isoformat()}

    async def _default_action(self):
        """기본 행동 로직"""
        return {'phase': 'action', 'status': 'success', 'action': 'system_monitoring', 'result': 'systems_healthy', 'timestamp': datetime.now().isoformat()}

    async def _default_feedback(self):
        """기본 피드백 로직"""
        return {'phase': 'feedback', 'status': 'success', 'feedback': 'execution_loop_healthy', 'learning': 'maintain_current_state', 'timestamp': datetime.now().isoformat()}

    async def _analyze_context(self):
        """컨텍스트 분석 (병렬 처리용)"""
        await asyncio.sleep(0.02)
        return {'type': 'context_analysis', 'status': 'completed', 'context': '현재 상황 분석 완료', 'timestamp': datetime.now().isoformat()}

    async def _evaluate_priority(self):
        """우선순위 평가 (병렬 처리용)"""
        await asyncio.sleep(0.015)
        return {'type': 'priority_evaluation', 'status': 'completed', 'priority': 'high', 'timestamp': datetime.now().isoformat()}

    async def _update_memory(self):
        """메모리 업데이트 (병렬 처리용)"""
        await asyncio.sleep(0.025)
        return {'type': 'memory_update', 'status': 'completed', 'memory': '메모리 업데이트 완료', 'timestamp': datetime.now().isoformat()}

    async def _prepare_response(self):
        """응답 준비 (병렬 처리용)"""
        await asyncio.sleep(0.02)
        return {'type': 'response_preparation', 'status': 'completed', 'response': '응답 준비 완료', 'timestamp': datetime.now().isoformat()}

    async def _evaluate_performance(self):
        """성능 평가 (병렬 처리용)"""
        await asyncio.sleep(0.01)
        return {'type': 'performance_evaluation', 'status': 'completed', 'performance': '성능 평가 완료', 'timestamp': datetime.now().isoformat()}

    async def _plan_next_steps(self):
        """다음 단계 계획 (병렬 처리용)"""
        await asyncio.sleep(0.015)
        return {'type': 'next_steps_planning', 'status': 'completed', 'plan': '다음 단계 계획 완료', 'timestamp': datetime.now().isoformat()}

    def _store_judgment_result(self, result):
        """판단 결과 저장"""
        logger.info(f'💾 판단 결과 저장: {result}')

    def _store_action_result(self, result):
        """행동 결과 저장"""
        logger.info(f'💾 행동 결과 저장: {result}')

    def _store_feedback_result(self, result):
        """피드백 결과 저장"""
        logger.info(f'💾 피드백 결과 저장: {result}')

    async def _update_system_status(self):
        """시스템 상태 업데이트"""
        for (system_name, status) in self.system_status.items():
            if system_name in self.systems:
                status.status = 'active'
                status.last_activity = datetime.now()
                status.performance_score = min(1.0, status.performance_score + 0.1)
            else:
                status.status = 'inactive'
                status.performance_score = max(0.0, status.performance_score - 0.1)

    async def _monitor_performance(self):
        """성능 모니터링 (ACT-R 병렬 처리 포함)"""
        active_systems = sum((1 for status in self.system_status.values() if status.status == 'active'))
        total_systems = len(self.system_status)
        performance_ratio = active_systems / total_systems if total_systems > 0 else 0
        self.performance_metrics = {'active_systems': active_systems, 'total_systems': total_systems, 'performance_ratio': performance_ratio, 'timestamp': datetime.now().isoformat()}
        if self.parallel_processor:
            parallel_report = self.parallel_processor.get_performance_report()
            self.performance_metrics.update({'act_r_parallel_processing': True, 'parallel_efficiency': parallel_report.get('efficiency', 0.0), 'performance_improvement': parallel_report.get('current_improvement', 0.0), 'target_improvement': parallel_report.get('target_improvement', 23.0), 'baseline_time': parallel_report.get('baseline_time', 0.104), 'target_time': parallel_report.get('target_time', 0.08), 'success_rate': parallel_report.get('success_rate', 0.0)})
        else:
            self.performance_metrics.update({'act_r_parallel_processing': False, 'parallel_efficiency': 0.0, 'performance_improvement': 0.0, 'target_improvement': 23.0, 'baseline_time': 0.104, 'target_time': 0.08, 'success_rate': 0.0})
        if self.attention_system:
            attention_report = self.attention_system.get_performance_report()
            self.performance_metrics.update({'lida_attention_system': True, 'attention_accuracy': attention_report.get('current_accuracy', 0.0), 'accuracy_improvement': attention_report.get('accuracy_improvement', 0.0), 'target_accuracy_improvement': attention_report.get('target_improvement', 15.0), 'attention_state': attention_report.get('attention_state', {}), 'total_attention_tasks': attention_report.get('total_tasks', 0)})
        else:
            self.performance_metrics.update({'lida_attention_system': False, 'attention_accuracy': 0.0, 'accuracy_improvement': 0.0, 'target_accuracy_improvement': 15.0, 'attention_state': {}, 'total_attention_tasks': 0})
        logger.info(f'📊 성능 지표: {active_systems}/{total_systems} 시스템 활성 ({performance_ratio:.1%})')

    def stop_execution_loop(self):
        """실행 루프 중지"""
        logger.info('🛑 DuRi 실행 루프 중지')
        self.execution_loop_active = False

    def get_system_status(self) -> Dict[str, SystemStatus]:
        """시스템 상태 반환"""
        return self.system_status

    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 지표 반환"""
        return self.performance_metrics

    def get_error_log(self) -> List[str]:
        """오류 로그 반환"""
        return self.error_log

    def generate_status_report(self) -> Dict[str, Any]:
        """상태 리포트 생성"""
        return {'orchestrator_status': 'active' if self.execution_loop_active else 'inactive', 'system_count': len(self.systems), 'active_systems': sum((1 for status in self.system_status.values() if status.status == 'active')), 'performance_metrics': self.performance_metrics, 'error_count': len(self.error_log), 'timestamp': datetime.now().isoformat()}

async def main():
    """메인 실행 함수"""
    emit_trace('info', ' '.join(map(str, ['🚀 DuRi Orchestrator 시작'])))
    emit_trace('info', ' '.join(map(str, ['=' * 50])))
    orchestrator = DuRiOrchestrator()
    initial_report = orchestrator.generate_status_report()
    emit_trace('info', ' '.join(map(str, [f'📊 초기 상태: {json.dumps(initial_report, indent=2, ensure_ascii=False)}'])))
    try:
        await orchestrator.start_execution_loop()
    except KeyboardInterrupt:
        emit_trace('info', ' '.join(map(str, ['\n🛑 사용자에 의해 중단됨'])))
        orchestrator.stop_execution_loop()
    except Exception as e:
        emit_trace('info', ' '.join(map(str, [f'❌ 오류 발생: {e}'])))
        orchestrator.stop_execution_loop()
    finally:
        final_report = orchestrator.generate_status_report()
        emit_trace('info', ' '.join(map(str, [f'📊 최종 상태: {json.dumps(final_report, indent=2, ensure_ascii=False)}'])))
        emit_trace('info', ' '.join(map(str, ['\n✅ DuRi Orchestrator 종료'])))
if __name__ == '__main__':
    asyncio.run(main())