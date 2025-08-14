from __future__ import annotations
from typing import Dict, Union, Optional
from pathlib import Path
import logging

logger = logging.getLogger("DuRiCore.exporters.metrics")

Number = Union[int, float]

class MetricsSink:
    """메트릭 싱크 인터페이스"""
    def emit(self, name: str, value: Number, labels: Optional[Dict[str,str]]=None) -> None: ...
    def emit_many(self, kv: Dict[str, Number], labels: Optional[Dict[str,str]]=None) -> None: ...

class FileSink(MetricsSink):
    """파일 기반 메트릭 싱크 (Prometheus 텍스트 포맷)"""
    def __init__(self, path: str="var/metrics/prometheus.txt"):
        self.file = Path(path)
        self.file.parent.mkdir(parents=True, exist_ok=True)
    
    def _line(self, k: str, v: Number, labels: Optional[Dict[str,str]]) -> str:
        """메트릭 라인 생성"""
        if labels:
            # 라벨을 정렬하여 일관성 보장
            lbl = ",".join(f'{x}="{labels[x]}"' for x in sorted(labels))
            return f'{k}{{{lbl}}} {v}\n'
        return f"{k} {v}\n"
    
    def emit(self, name: str, value: Number, labels: Optional[Dict[str,str]]=None) -> None:
        """단일 메트릭 방출"""
        try:
            # 원자적 쓰기 (Temp → rename)
            tmp = self.file.with_suffix(".tmp")
            content = self._line(name, value, labels)
            
            if not self.file.exists():
                # 파일이 없으면 새로 생성
                with tmp.open("w", encoding="utf-8") as f:
                    f.write(content)
                tmp.replace(self.file)
            else:
                # 기존 파일에 추가
                existing_content = self.file.read_text(encoding="utf-8")
                new_content = existing_content + content
                with tmp.open("w", encoding="utf-8") as f:
                    f.write(new_content)
                tmp.replace(self.file)
            
            logger.debug(f"메트릭 방출: {name}={value}")
            
        except Exception as e:
            logger.error(f"메트릭 방출 실패: {e}")
            raise
    
    def emit_many(self, kv: Dict[str, Number], labels: Optional[Dict[str,str]]=None) -> None:
        """여러 메트릭 방출"""
        try:
            # 원자적 쓰기 (Temp → rename)
            tmp = self.file.with_suffix(".tmp")
            buf = "".join(self._line(k, v, labels) for k, v in kv.items())
            
            if not self.file.exists():
                # 파일이 없으면 새로 생성
                with tmp.open("w", encoding="utf-8") as f:
                    f.write(buf)
                tmp.replace(self.file)
            else:
                # 기존 파일에 추가
                existing_content = self.file.read_text(encoding="utf-8")
                new_content = existing_content + buf
                with tmp.open("w", encoding="utf-8") as f:
                    f.write(new_content)
                tmp.replace(self.file)
            
            logger.debug(f"메트릭 다중 방출: {len(kv)}개")
            
        except Exception as e:
            logger.error(f"메트릭 다중 방출 실패: {e}")
            raise

def build_sink(_provider=None) -> MetricsSink:
    """메트릭 싱크 빌드 (필요 시 provider에서 sink 타입 결정 가능)"""
    return FileSink()
