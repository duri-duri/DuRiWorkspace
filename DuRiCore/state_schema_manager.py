#!/usr/bin/env python3
"""
DuRi 상태 파일 스키마 관리자
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime

class StateSchemaManager:
    def __init__(self, state_path: str = "./DuRiCore/DuRiCore/memory/learning_cycles.json"):
        self.state_path = state_path
        self.current_schema_version = "2.0"
        
    def migrate_if_needed(self) -> bool:
        """필요시 스키마 마이그레이션 수행"""
        if not os.path.exists(self.state_path):
            return self._create_new_schema()
            
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 기존 dict 형식 (v1.0) -> 새 list 형식 (v2.0) 마이그레이션
            if isinstance(data, dict) and 'cycles' in data:
                return self._migrate_v1_to_v2(data)
            elif isinstance(data, list):
                # 이미 v2.0 형식
                return True
            else:
                # 알 수 없는 형식, 새로 생성
                return self._create_new_schema()
                
        except Exception as e:
            print(f"스키마 마이그레이션 오류: {e}")
            return self._create_new_schema()
            
    def _migrate_v1_to_v2(self, old_data: Dict[str, Any]) -> bool:
        """v1.0 (dict) -> v2.0 (list) 마이그레이션"""
        try:
            cycles = old_data.get('cycles', [])
            
            # 새 스키마로 변환
            new_data = {
                "schema_version": self.current_schema_version,
                "created_at": datetime.now().isoformat(),
                "migrated_from": "1.0",
                "cycles": cycles
            }
            
            # 백업 생성
            backup_path = f"{self.state_path}.backup_v1"
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(old_data, f, ensure_ascii=False, indent=2)
                
            # 새 형식으로 저장
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
                
            print(f"✅ v1.0 -> v2.0 마이그레이션 완료 (백업: {backup_path})")
            return True
            
        except Exception as e:
            print(f"❌ 마이그레이션 실패: {e}")
            return False
            
    def _create_new_schema(self) -> bool:
        """새 스키마 생성"""
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            
            new_data = {
                "schema_version": self.current_schema_version,
                "created_at": datetime.now().isoformat(),
                "cycles": []
            }
            
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
                
            print(f"✅ 새 스키마 생성 완료 (v{self.current_schema_version})")
            return True
            
        except Exception as e:
            print(f"❌ 새 스키마 생성 실패: {e}")
            return False
            
    def append_cycle(self, cycle_data: Dict[str, Any]) -> bool:
        """사이클 데이터 추가"""
        try:
            # 마이그레이션 확인
            if not self.migrate_if_needed():
                return False
                
            # 데이터 로드
            with open(self.state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 사이클 추가
            data['cycles'].append(cycle_data)
            data['last_updated'] = datetime.now().isoformat()
            
            # 저장
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"❌ 사이클 추가 실패: {e}")
            return False
            
    def get_cycles(self) -> List[Dict[str, Any]]:
        """사이클 데이터 조회"""
        try:
            if not os.path.exists(self.state_path):
                return []
                
            with open(self.state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return data.get('cycles', [])
            
        except Exception as e:
            print(f"❌ 사이클 조회 실패: {e}")
            return []
            
    def get_last_cycle_id(self) -> str:
        """마지막 사이클 ID 조회"""
        cycles = self.get_cycles()
        if cycles:
            return cycles[-1].get('cycle_id', 'unknown')
        return 'none'
