import glob
import json
import os
import re

import yaml


def _any(paths):
    for p in paths:
        if glob.glob(p, recursive=True):
            return True
    return False


def test_day24_pou_design_artifacts_exist():
    assert _any(
        [
            "backup_phase5_day8_day15/day24/**/*.md",
            "DuRi_Day11_15_starter/**/*pou*.md",
            "docs/**/*pou*.md",
        ]
    ), "PoU 설계 산출물(문서)이 없어 보입니다."


def test_day25_curator_config_exists_and_valid_yaml():
    candidates = [
        "configs/curator.yaml",
        "configs/curator_v1.yaml",
        "backup_phase5_day8_day15/day25/**/*.yaml",
    ]
    found = [p for p in candidates if os.path.exists(p)]
    assert found, "학습 큐레이터 v1 설정이 없습니다."
    # YAML 파일이 있으면 구조 검증
    for f in found:
        if f.endswith(".yaml"):
            with open(f, "r", encoding="utf-8") as file:
                cfg = yaml.safe_load(file)
                assert isinstance(cfg, dict), f"curator config {f} 구조가 부족합니다."


def test_day26_counterexample_pipeline_exists():
    assert _any(
        [
            "scripts/counterexample_*.sh",
            "duri_core/**/counterexample*.py",
            "backup_phase5_day8_day15/day26/**/*.md",
        ]
    ), "반례 채굴 루프 스크립트/모듈이 없습니다."


def test_day27_hitl_monitor_exists_and_metric_targets():
    # SLA 목표 정의 파일 혹은 코드 상수 존재 확인
    assert _any(
        [
            "configs/hitl_sla.yaml",
            "duri_core/**/hitl_monitor*.py",
            "backup_phase5_day8_day15/day27/**/*.md",
        ]
    ), "HITL SLA 모니터링 구성요소가 없습니다."


def test_day28_week1_ops_reports_exist():
    assert _any(
        [
            "var/reports/final_verify_*/run.log",
            "var/reports/ROLL0UT_SUMMARY_*.md",
            "var/reports/bench_*/**/*.json",
            "backup_phase5_day8_day15/day28/**/*.md",
        ]
    ), "1주차 운영 리포트/로그가 없습니다."


def test_day29_perf_analysis_exists():
    assert _any(
        [
            "var/reports/perf_analysis_*.md",
            "notebooks/**/pou_week1_analysis*.ipynb",
            "backup_phase5_day8_day15/day29/**/*.md",
        ]
    ), "성능 분석 결과물이 없습니다."


def test_day30_phase_review_and_plan():
    assert _any(
        [
            "docs/**/Day1-30_review*.md",
            "docs/**/phase2_plan*.md",
            "backup_phase5_day8_day15/day30/**/*.md",
        ]
    ), "Day1~30 리뷰 또는 Day31+ 계획 문서가 없습니다."
