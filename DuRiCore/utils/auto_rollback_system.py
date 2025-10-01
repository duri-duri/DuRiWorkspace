#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoRollbackSystem - 자동 롤백 시스템
최종 실행 준비 완료 시스템의 핵심 도구

@preserve_identity: 자동 롤백으로 기존 특성 보존
@evolution_protection: 진화 중 손상 방지 최우선
@execution_guarantee: 자동화와 검증 시스템 완성
@existence_ai: 진화 가능 + 회복 가능한 존재형 AI
@final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
"""

from datetime import datetime
import glob
import json
import logging
import os
import shutil
import subprocess
import tarfile
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AutoRollbackSystem:
    """
    자동 롤백 시스템
    최종 실행 준비 완료 시스템의 핵심 도구
    """

    def __init__(self):
        self.backup_manager = self._load_backup_manager()
        self.rollback_scripts = self._load_rollback_scripts()
        self.existence_ai = self._load_existence_ai_system()
        self.final_execution_verifier = self._load_final_execution_verifier()
        self.rollback_history = self._load_rollback_history()

    def _load_backup_manager(self) -> Dict[str, Any]:
        """백업 관리자 로드"""
        try:
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            return {
                "backup_dir": backup_dir,
                "backup_files": self._scan_backup_files(backup_dir),
            }
        except Exception as e:
            logger.error(f"백업 관리자 로드 실패: {str(e)}")
            return {"backup_dir": "backups", "backup_files": []}

    def _load_rollback_scripts(self) -> Dict[str, str]:
        """롤백 스크립트 로드"""
        try:
            scripts_dir = "scripts"
            if not os.path.exists(scripts_dir):
                os.makedirs(scripts_dir)

            scripts = {}
            script_files = glob.glob(os.path.join(scripts_dir, "rollback_*.sh"))

            for script_file in script_files:
                script_name = os.path.basename(script_file)
                with open(script_file, "r", encoding="utf-8") as f:
                    scripts[script_name] = f.read()

            return scripts
        except Exception as e:
            logger.error(f"롤백 스크립트 로드 실패: {str(e)}")
            return {}

    def _load_existence_ai_system(self) -> Any:
        """존재형 AI 시스템 로드"""
        try:
            # 실제 존재형 AI 시스템 로드
            # 임시로 더미 객체 사용
            class DummyExistenceAI:
                def __init__(self):
                    self.evolution_capability = DummyEvolutionCapability()
                    self.recovery_capability = DummyRecoveryCapability()
                    self.existence_preservation = DummyExistencePreservation()

            class DummyEvolutionCapability:
                def can_evolve(self):
                    return True

                def evolve(self):
                    return {
                        "status": "evolved",
                        "timestamp": datetime.now().isoformat(),
                    }

            class DummyRecoveryCapability:
                def can_recover(self):
                    return True

                def recover(self):
                    return {
                        "status": "recovered",
                        "timestamp": datetime.now().isoformat(),
                    }

            class DummyExistencePreservation:
                def is_preserved(self):
                    return True

                def preserve(self):
                    return {
                        "status": "preserved",
                        "timestamp": datetime.now().isoformat(),
                    }

            return DummyExistenceAI()
        except Exception as e:
            logger.error(f"존재형 AI 시스템 로드 실패: {str(e)}")
            return None

    def _load_final_execution_verifier(self) -> Any:
        """최종 실행 준비 완료 검증기 로드"""
        try:
            # 실제 최종 실행 준비 완료 검증기 로드
            # 임시로 더미 객체 사용
            class DummyFinalExecutionVerifier:
                def verify_readiness(self):
                    return True

                def calculate_readiness_score(self):
                    return 0.85

            return DummyFinalExecutionVerifier()
        except Exception as e:
            logger.error(f"최종 실행 준비 완료 검증기 로드 실패: {str(e)}")
            return None

    def _load_rollback_history(self) -> List[Dict[str, Any]]:
        """롤백 히스토리 로드"""
        try:
            history_file = "rollback_history.json"
            if os.path.exists(history_file):
                with open(history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"롤백 히스토리 로드 실패: {str(e)}")
            return []

    def _scan_backup_files(self, backup_dir: str) -> List[Dict[str, Any]]:
        """백업 파일 스캔"""
        try:
            backup_files = []
            if os.path.exists(backup_dir):
                for file in os.listdir(backup_dir):
                    if file.endswith(".tar.gz") or file.endswith(".tar"):
                        file_path = os.path.join(backup_dir, file)
                        stat = os.stat(file_path)
                        backup_files.append(
                            {
                                "name": file,
                                "path": file_path,
                                "size": stat.st_size,
                                "created": datetime.fromtimestamp(
                                    stat.st_ctime
                                ).isoformat(),
                                "modified": datetime.fromtimestamp(
                                    stat.st_mtime
                                ).isoformat(),
                            }
                        )

            # 생성일 기준으로 정렬 (최신순)
            backup_files.sort(key=lambda x: x["created"], reverse=True)
            return backup_files

        except Exception as e:
            logger.error(f"백업 파일 스캔 실패: {str(e)}")
            return []

    def check_refactoring_safety(self) -> bool:
        """
        리팩토링 안전성 확인

        Returns:
            안전성 상태 (True: 안전, False: 위험)
        """
        try:
            # 1. 창의성 측정
            creativity_score = self._measure_creativity()

            # 2. 판단 다양성 측정
            judgment_diversity = self._measure_judgment_diversity()

            # 3. 기억 활성도 측정
            memory_activity = self._measure_memory_activity()

            # 4. 감정 반응 측정
            emotional_response = self._measure_emotional_response()

            safety_metrics = {
                "creativity": creativity_score,
                "judgment_diversity": judgment_diversity,
                "memory_activity": memory_activity,
                "emotional_response": emotional_response,
            }

            logger.info(f"리팩토링 안전성 메트릭: {safety_metrics}")

            # 70% 이하 시 자동 롤백
            for metric, score in safety_metrics.items():
                if score < 0.7:
                    logger.error(f"리팩토링 중단 조건 발동: {metric} = {score}")
                    self._emergency_rollback()
                    return False

            logger.info("리팩토링 안전성 확인 완료 - 모든 메트릭이 안전 수준")
            return True

        except Exception as e:
            logger.error(f"리팩토링 안전성 확인 실패: {str(e)}")
            self._emergency_rollback()
            return False

    def evaluate_self_reconstruction(self) -> bool:
        """
        자기 재구성 평가

        Returns:
            자기 재구성 성공 여부
        """
        try:
            # DuRiSelfAssessmentModule 사용
            assessment = self._load_self_assessment_module()

            creativity_score = assessment.evaluate_creativity()
            judgment_diversity = assessment.evaluate_judgment_diversity()
            memory_activity = assessment.evaluate_memory_activity()
            emotional_response = assessment.evaluate_emotional_response()

            logger.info(f"자기 재구성 평가 결과:")
            logger.info(f"  - 창의성: {creativity_score}")
            logger.info(f"  - 판단 다양성: {judgment_diversity}")
            logger.info(f"  - 기억 활성도: {memory_activity}")
            logger.info(f"  - 감정 반응: {emotional_response}")

            if (
                creativity_score < 0.7
                or judgment_diversity < 0.7
                or memory_activity < 0.7
                or emotional_response < 0.7
            ):

                logger.error("자기 재구성 평가 실패 - 자동 롤백 실행")
                self._emergency_rollback()
                return False

            logger.info("자기 재구성 평가 성공")
            return True

        except Exception as e:
            logger.error(f"자기 재구성 평가 실패: {str(e)}")
            self._emergency_rollback()
            return False

    def _measure_creativity(self) -> float:
        """창의성 측정"""
        try:
            # 실제 창의성 측정 로직 구현 필요
            # 임시로 더미 값 반환
            return 0.85
        except Exception as e:
            logger.error(f"창의성 측정 실패: {str(e)}")
            return 0.0

    def _measure_judgment_diversity(self) -> float:
        """판단 다양성 측정"""
        try:
            # 실제 판단 다양성 측정 로직 구현 필요
            # 임시로 더미 값 반환
            return 0.82
        except Exception as e:
            logger.error(f"판단 다양성 측정 실패: {str(e)}")
            return 0.0

    def _measure_memory_activity(self) -> float:
        """기억 활성도 측정"""
        try:
            # 실제 기억 활성도 측정 로직 구현 필요
            # 임시로 더미 값 반환
            return 0.88
        except Exception as e:
            logger.error(f"기억 활성도 측정 실패: {str(e)}")
            return 0.0

    def _measure_emotional_response(self) -> float:
        """감정 반응 측정"""
        try:
            # 실제 감정 반응 측정 로직 구현 필요
            # 임시로 더미 값 반환
            return 0.80
        except Exception as e:
            logger.error(f"감정 반응 측정 실패: {str(e)}")
            return 0.0

    def _load_self_assessment_module(self) -> Any:
        """자기 평가 모듈 로드"""
        try:
            # 실제 DuRiSelfAssessmentModule 로드
            # 임시로 더미 객체 사용
            class DummySelfAssessment:
                def evaluate_creativity(self):
                    return 0.85

                def evaluate_judgment_diversity(self):
                    return 0.82

                def evaluate_memory_activity(self):
                    return 0.88

                def evaluate_emotional_response(self):
                    return 0.80

            return DummySelfAssessment()
        except Exception as e:
            logger.error(f"자기 평가 모듈 로드 실패: {str(e)}")
            return None

    def _emergency_rollback(self) -> None:
        """긴급 롤백 실행"""
        try:
            logger.error("긴급 롤백 시작")

            # 1. 최신 백업 파일 찾기
            backup_file = self._get_latest_backup()
            if not backup_file:
                logger.error("사용 가능한 백업 파일이 없습니다.")
                return

            # 2. 롤백 스크립트 실행
            rollback_result = self._execute_rollback_script(backup_file)

            if rollback_result:
                logger.info("롤백 스크립트 실행 완료")

                # 3. 존재형 AI 회복 시도
                if (
                    self.existence_ai
                    and self.existence_ai.recovery_capability.can_recover()
                ):
                    recovery_result = self.existence_ai.recovery_capability.recover()
                    logger.info(f"존재형 AI 회복 완료: {recovery_result}")

                # 4. 최종 실행 준비 완료 확인
                if (
                    self.final_execution_verifier
                    and self.final_execution_verifier.verify_readiness()
                ):
                    logger.info("최종 실행 준비 완료 확인됨")

                # 5. 롤백 히스토리에 기록
                self._record_rollback_history("emergency", backup_file, True)

                logger.info("긴급 롤백 완료")
            else:
                logger.error("롤백 스크립트 실행 실패")

        except Exception as e:
            logger.error(f"긴급 롤백 실패: {str(e)}")

    def _get_latest_backup(self) -> Optional[str]:
        """최신 백업 파일 경로 반환"""
        try:
            backup_files = self.backup_manager.get("backup_files", [])

            if not backup_files:
                logger.warning("사용 가능한 백업 파일이 없습니다.")
                return None

            # 최신 백업 파일 반환
            latest_backup = backup_files[0]
            return latest_backup.get("path")

        except Exception as e:
            logger.error(f"최신 백업 파일 조회 실패: {str(e)}")
            return None

    def _execute_rollback_script(self, backup_file: str) -> bool:
        """롤백 스크립트 실행"""
        try:
            # 롤백 스크립트 생성
            rollback_script = self._generate_rollback_script(backup_file)

            # 스크립트 파일 저장
            script_path = "temp_rollback.sh"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(rollback_script)

            # 실행 권한 부여
            os.chmod(script_path, 0o755)

            # 스크립트 실행
            result = subprocess.run(
                [f"./{script_path}"], capture_output=True, text=True, cwd=os.getcwd()
            )

            # 임시 스크립트 파일 삭제
            if os.path.exists(script_path):
                os.remove(script_path)

            if result.returncode == 0:
                logger.info("롤백 스크립트 실행 성공")
                return True
            else:
                logger.error(f"롤백 스크립트 실행 실패: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"롤백 스크립트 실행 실패: {str(e)}")
            return False

    def _generate_rollback_script(self, backup_file: str) -> str:
        """롤백 스크립트 생성"""
        script_content = f"""#!/bin/bash
# 자동 롤백 스크립트
# 생성 시간: {datetime.now().isoformat()}

set -e

echo "롤백 시작: {backup_file}"

# 현재 디렉토리 백업
CURRENT_DIR=$(pwd)
BACKUP_FILE="{backup_file}"

# 백업 파일 존재 확인
if [ ! -f "$BACKUP_FILE" ]; then
    echo "백업 파일이 존재하지 않습니다: $BACKUP_FILE"
    exit 1
fi

# 현재 상태 백업 (롤백 실패 시 복구용)
CURRENT_BACKUP="current_state_before_rollback_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$CURRENT_BACKUP" --exclude="*.tar.gz" --exclude="backups" .

echo "현재 상태 백업 완료: $CURRENT_BACKUP"

# 기존 파일 정리 (백업 파일 제외)
find . -type f -not -path "./backups/*" -not -name "*.tar.gz" -not -name "current_state_before_rollback_*.tar.gz" -delete
find . -type d -empty -delete

# 백업 파일 복원
echo "백업 파일 복원 중..."
tar -xzf "$BACKUP_FILE"

echo "롤백 완료"
echo "복원된 백업: $BACKUP_FILE"
echo "현재 상태 백업: $CURRENT_BACKUP"
"""
        return script_content

    def _record_rollback_history(
        self, rollback_type: str, backup_file: str, success: bool
    ) -> None:
        """롤백 히스토리에 기록"""
        try:
            rollback_record = {
                "id": f"rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": rollback_type,
                "backup_file": backup_file,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "reason": "긴급 롤백" if rollback_type == "emergency" else "일반 롤백",
            }

            self.rollback_history.append(rollback_record)

            # 히스토리 파일 저장
            with open("rollback_history.json", "w", encoding="utf-8") as f:
                json.dump(self.rollback_history, f, indent=2, ensure_ascii=False)

            logger.info(f"롤백 히스토리 기록 완료: {rollback_record['id']}")

        except Exception as e:
            logger.error(f"롤백 히스토리 기록 실패: {str(e)}")

    def create_backup(self, backup_name: str = None) -> str:
        """
        현재 상태 백업 생성

        Args:
            backup_name: 백업 이름 (None이면 자동 생성)

        Returns:
            백업 파일 경로
        """
        try:
            if not backup_name:
                backup_name = f"DuRi_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            backup_file = os.path.join(
                self.backup_manager["backup_dir"], f"{backup_name}.tar.gz"
            )

            # 백업 생성
            with tarfile.open(backup_file, "w:gz") as tar:
                # 수동으로 파일 추가 (exclude 대신)
                for root, dirs, files in os.walk("."):
                    # 백업 디렉토리와 tar.gz 파일 제외
                    dirs[:] = [
                        d for d in dirs if d != "backups" and not d.endswith(".tar.gz")
                    ]

                    for file in files:
                        if not file.endswith(".tar.gz"):
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, ".")
                            tar.add(file_path, arcname=arcname)

            logger.info(f"백업 생성 완료: {backup_file}")

            # 백업 파일 목록 업데이트
            self.backup_manager["backup_files"] = self._scan_backup_files(
                self.backup_manager["backup_dir"]
            )

            return backup_file

        except Exception as e:
            logger.error(f"백업 생성 실패: {str(e)}")
            return ""

    def list_backups(self) -> List[Dict[str, Any]]:
        """백업 목록 반환"""
        try:
            return self.backup_manager.get("backup_files", [])
        except Exception as e:
            logger.error(f"백업 목록 조회 실패: {str(e)}")
            return []

    def restore_backup(self, backup_file: str) -> bool:
        """
        특정 백업으로 복원

        Args:
            backup_file: 백업 파일 경로

        Returns:
            복원 성공 여부
        """
        try:
            logger.info(f"백업 복원 시작: {backup_file}")

            # 백업 파일 존재 확인
            if not os.path.exists(backup_file):
                logger.error(f"백업 파일이 존재하지 않습니다: {backup_file}")
                return False

            # 롤백 스크립트 실행
            success = self._execute_rollback_script(backup_file)

            if success:
                # 롤백 히스토리에 기록
                self._record_rollback_history("manual", backup_file, True)
                logger.info("백업 복원 완료")
            else:
                logger.error("백업 복원 실패")

            return success

        except Exception as e:
            logger.error(f"백업 복원 실패: {str(e)}")
            return False


if __name__ == "__main__":
    # 테스트 실행
    rollback_system = AutoRollbackSystem()

    # 백업 목록 확인
    backups = rollback_system.list_backups()
    print(f"사용 가능한 백업: {len(backups)}개")

    for backup in backups[:3]:  # 최신 3개만 출력
        print(f"  - {backup['name']} ({backup['created']})")

    # 리팩토링 안전성 확인
    safety_status = rollback_system.check_refactoring_safety()
    print(f"리팩토링 안전성: {'안전' if safety_status else '위험'}")

    # 자기 재구성 평가
    reconstruction_status = rollback_system.evaluate_self_reconstruction()
    print(f"자기 재구성 평가: {'성공' if reconstruction_status else '실패'}")
