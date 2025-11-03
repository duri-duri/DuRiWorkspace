#!/usr/bin/env python3
"""C) AB 통계 n=0 필터 유닛 테스트"""
import pathlib
import subprocess
import tempfile


def test_ignore_n0_samples(tmp_path, monkeypatch):
    """n=0 샘플은 제외하고 통계 계산"""
    # var/evolution 구조 모방
    ev_dir = tmp_path / "var" / "evolution" / "EV-TEST"
    ev_dir.mkdir(parents=True)
    
    # 테스트 ab_eval.prom 생성
    prom_file = ev_dir / "ab_eval.prom"
    prom_file.write_text(
        '# HELP duri_ab_p_value Two-tailed p-value from AB eval\n'
        '# TYPE duri_ab_p_value gauge\n'
        'duri_ab_p_value{ev="E1",n="0",build_unixtime="1"} 1\n'
        'duri_ab_p_value{ev="E2",n="5",build_unixtime="2"} 0.03\n'
        '# HELP duri_ab_samples Total sample count for AB eval\n'
        '# TYPE duri_ab_samples gauge\n'
        'duri_ab_samples{ev="E1"} 0\n'
        'duri_ab_samples{ev="E2"} 5\n'
    )
    
    # ab_pvalue_stats.sh 실행 (임시 디렉토리를 var/evolution로 설정)
    result = subprocess.run(
        ["bash", "-c", f"cd {tmp_path} && bash scripts/ab_pvalue_stats.sh '1 hour' 2>&1"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path)
    )
    
    # n=0 샘플은 제외되어야 함 (E1은 제외, E2만 포함)
    assert "샘플 수: 1" in result.stdout or "샘플 수: 1" in result.stderr
    assert "0.03" in result.stdout or "0.03" in result.stderr
    # E1의 p=1.0은 포함되지 않아야 함
    assert result.stdout.count("1.0") == 0 or "평균" not in result.stdout


def test_label_only_samples(tmp_path, monkeypatch):
    """라벨 있는 샘플만 집계 (라벨 없는 라인 제외)"""
    ev_dir = tmp_path / "var" / "evolution" / "EV-TEST2"
    ev_dir.mkdir(parents=True)
    
    prom_file = ev_dir / "ab_eval.prom"
    prom_file.write_text(
        'duri_ab_p_value{ev="E3",n="3",build_unixtime="3"} 0.05\n'
        'duri_ab_p_value 0.07\n'  # 라벨 없는 라인 (제외되어야 함)
    )
    
    result = subprocess.run(
        ["bash", "-c", f"cd {tmp_path} && bash scripts/ab_pvalue_stats.sh '1 hour' 2>&1"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path)
    )
    
    # 라벨 없는 라인은 제외되어야 함
    assert "샘플 수: 1" in result.stdout or "샘플 수: 1" in result.stderr
    assert "0.05" in result.stdout or "0.05" in result.stderr
    # 라벨 없는 라인의 0.07은 포함되지 않아야 함
    assert "0.07" not in result.stdout or "샘플 수: 1" in result.stdout


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

