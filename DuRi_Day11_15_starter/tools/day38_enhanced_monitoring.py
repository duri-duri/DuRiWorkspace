#!/usr/bin/env python3
"""
Day38 Enhanced: PoU 고도화 모니터링 시스템 (Day34 기반 확장)
- 기존 integrated_pou_monitoring_system.py 확장
- 실시간 시계열 수집 (15분 bin)
- 목적함수 J 계산 통합
- 민감도 분석 (∂J/∂metric)
- 운영 알람 시스템
"""

import argparse
import csv
import glob
import json
import logging
import subprocess
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Tuple


class EnhancedPoUMonitoringSystem:
    def __init__(self, config_path: str = "configs/monitoring.yaml"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()

        # 기존 Day34 구조 유지하면서 확장
        self.pilots = {
            "medical": {"status": "active", "last_update": None, "metrics": {}},
            "rehab": {"status": "active", "last_update": None, "metrics": {}},
            "coding": {"status": "active", "last_update": None, "metrics": {}},
        }

        # Day38 확장 기능
        self.time_series_data = defaultdict(list)
        self.alert_history = []
        self.sensitivity_cache = {}

        self.logger.info("Day38 Enhanced PoU 모니터링 시스템 초기화 완료")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            import yaml

            with open(config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f"설정 파일 로드 실패: {e}")
            # 기본 설정 반환
            return {
                "bin_minutes": 15,
                "domains": ["medical", "rehab", "coding"],
                "log_globs": {
                    "medical": "samples/logs/medical_*.jsonl",
                    "rehab": "samples/logs/rehab_*.jsonl",
                    "coding": "samples/logs/coding_*.jsonl",
                },
                "objective": {
                    "config": "configs/objective_params.yaml",
                    "weight_preset": "safety_first",
                    "evaluator": "tools/evaluate_objective.py",
                },
                "alerts": {
                    "fail_rate_p95_threshold": 0.008,
                    "fail_rate_persist_bins": 2,
                    "latency_p95_ms_threshold": 1800,
                    "latency_persist_bins": 2,
                },
                "outdir": {
                    "bins": "artifacts/day38/bins",
                    "series": "artifacts/day38/series",
                    "alerts": "artifacts/day38/alerts",
                    "daily": "artifacts/day38/daily",
                },
            }

    def _setup_logging(self) -> logging.Logger:
        """로깅 설정 (기존 Day34 방식 유지)"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger

    def parse_jsonl(self, path: str) -> List[Dict[str, Any]]:
        """JSONL 파싱 (기존 pou_metrics_ingest.py 방식)"""
        items = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        items.append(json.loads(line))
                    except json.JSONDecodeError:
                        # 리딩 제로 등 비정형 방어
                        line = line.replace(": .", ": 0.")
                        try:
                            items.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            self.logger.warning(f"JSONL 파싱 실패 {path}:{line_num} - {e}")
        except Exception as e:
            self.logger.error(f"JSONL 파일 읽기 실패 {path}: {e}")

        return items

    def normalize_metrics(self, rec: Dict[str, Any]) -> Dict[str, float]:
        """메트릭 정규화 (기존 방식 확장)"""
        lat = rec.get("p95_latency_ms") or rec.get("latency_ms") or rec.get("latency") or 0
        acc = rec.get("accuracy", 0)
        exp = rec.get("explainability", rec.get("explain", 0))
        status = rec.get("status", "ok")
        fail = 1.0 if status not in {"ok", "success"} else 0.0
        ts = rec.get("timestamp")

        return {
            "ts": ts,
            "latency_ms": float(lat),
            "accuracy": float(acc),
            "explainability": float(exp),
            "failure": float(fail),
        }

    def bin_key(self, ts_iso: str, bin_minutes: int) -> datetime:
        """시간 bin 키 생성"""
        dt = datetime.fromisoformat(ts_iso.replace("Z", "+00:00")).astimezone(timezone.utc)
        minute = (dt.minute // bin_minutes) * bin_minutes
        dt2 = dt.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minute)
        return dt2.replace(tzinfo=timezone.utc)

    def p95(self, xs: List[float]) -> float:
        """P95 계산"""
        if not xs:
            return 0.0
        xs = sorted(xs)
        k = max(0, min(len(xs) - 1, int(round(0.95 * (len(xs) - 1)))))
        return float(xs[k])

    def eval_objective_function(self, metrics_dict: Dict[str, float]) -> float:
        """목적함수 J 계산 (기존 evaluate_objective.py 활용)"""
        try:
            with tempfile.NamedTemporaryFile(
                "w", delete=False, suffix=".json", encoding="utf-8"
            ) as tf:
                json.dump(metrics_dict, tf)
                tmp = tf.name

            cmd = [
                "python",
                self.config["objective"]["evaluator"],
                "--metrics",
                tmp,
                "--config",
                self.config["objective"]["config"],
                "--weight_preset",
                self.config["objective"]["weight_preset"],
            ]

            out = subprocess.check_output(cmd, text=True)
            result = json.loads(out)
            return result["J"]
        except Exception as e:
            self.logger.error(f"목적함수 계산 실패: {e}")
            return 0.0
        finally:
            try:
                os.remove(tmp)
            except:
                pass

    def calculate_sensitivity(
        self, base_metrics: Dict[str, float], eps: float = 0.001
    ) -> Tuple[float, float, float]:
        """민감도 계산 (∂J/∂metric)"""
        J0 = self.eval_objective_function(base_metrics)

        # 실패율 민감도
        m2 = dict(base_metrics)
        m2["failure_rate"] = max(0.0, min(1.0, base_metrics["failure_rate"] + eps))
        J1 = self.eval_objective_function(m2)
        dJ_dfail = (J1 - J0) / eps

        # 지연시간 민감도
        m3 = dict(base_metrics)
        m3["latency_ms"] = base_metrics["latency_ms"] + 50.0
        J2 = self.eval_objective_function(m3)
        dJ_dlat = (J2 - J0) / 50.0

        return J0, dJ_dfail, dJ_dlat

    def collect_domain_metrics(self, domain: str) -> Dict[str, Any]:
        """도메인별 메트릭 수집 (기존 Day34 방식 확장)"""
        files = []
        for pat in self.config["log_globs"][domain].split(","):
            files.extend(glob.glob(pat.strip()))

        by_bin = defaultdict(list)
        for fp in files:
            for rec in self.parse_jsonl(fp):
                if not rec.get("timestamp"):
                    continue
                r = self.normalize_metrics(rec)
                by_bin[self.bin_key(r["ts"], self.config["bin_minutes"])].append(r)

        if not by_bin:
            return {"status": "no_data", "metrics": {}}

        # 최신 bin 처리
        latest_complete = max(by_bin.keys())
        rows = by_bin[latest_complete]

        lat_list = [r["latency_ms"] for r in rows]
        acc_list = [r["accuracy"] for r in rows]
        exp_list = [r["explainability"] for r in rows]
        fail_list = [r["failure"] for r in rows]

        metrics = {
            "latency_ms_p95": self.p95(lat_list),
            "accuracy_mean": mean(acc_list) if acc_list else 0.0,
            "explain_mean": mean(exp_list) if exp_list else 0.0,
            "failure_rate": mean(fail_list) if fail_list else 0.0,
            "n": len(rows),
            "bin_start_utc": latest_complete.isoformat(),
        }

        # 목적함수 계산
        J_input = {
            "latency_ms": metrics["latency_ms_p95"],
            "accuracy": metrics["accuracy_mean"],
            "explainability": metrics["explain_mean"],
            "failure_rate": metrics["failure_rate"],
        }

        J, dJ_dfail, dJ_dlat = self.calculate_sensitivity(J_input)
        metrics["J"] = J
        metrics["dJ_dfail"] = dJ_dfail
        metrics["dJ_dlat"] = dJ_dlat

        return {"status": "active", "metrics": metrics}

    def check_alerts(self, domain: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """알람 체크 (기존 Day34 방식 확장)"""
        alerts = []
        al_cfg = self.config["alerts"]

        # 실패율 알람
        if metrics["failure_rate"] > al_cfg["fail_rate_p95_threshold"]:
            alerts.append(
                {
                    "type": "FAIL_RATE_HIGH",
                    "domain": domain,
                    "value": metrics["failure_rate"],
                    "threshold": al_cfg["fail_rate_p95_threshold"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        # 지연시간 알람
        if metrics["latency_ms_p95"] > al_cfg["latency_p95_ms_threshold"]:
            alerts.append(
                {
                    "type": "LATENCY_HIGH",
                    "domain": domain,
                    "value": metrics["latency_ms_p95"],
                    "threshold": al_cfg["latency_p95_ms_threshold"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        return alerts

    def save_time_series(self, domain: str, metrics: Dict[str, Any]):
        """시계열 데이터 저장"""
        series_dir = Path(self.config["outdir"]["series"])
        series_dir.mkdir(parents=True, exist_ok=True)

        csv_file = series_dir / f"{domain}.csv"
        row = {
            "ts_utc": metrics["bin_start_utc"],
            "n": metrics["n"],
            "latency_ms_p95": round(metrics["latency_ms_p95"], 3),
            "accuracy_mean": round(metrics["accuracy_mean"], 6),
            "explain_mean": round(metrics["explain_mean"], 6),
            "failure_rate": round(metrics["failure_rate"], 6),
            "J": round(metrics["J"], 9),
            "dJ_dfail": round(metrics["dJ_dfail"], 6),
            "dJ_dlat": round(metrics["dJ_dlat"], 9),
        }

        header = [
            "ts_utc",
            "n",
            "latency_ms_p95",
            "accuracy_mean",
            "explain_mean",
            "failure_rate",
            "J",
            "dJ_dfail",
            "dJ_dlat",
        ]

        new_file = not csv_file.exists()
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            if new_file:
                writer.writeheader()
            writer.writerow(row)

    def generate_enhanced_dashboard(self) -> Dict[str, Any]:
        """고도화된 대시보드 생성 (기존 Day34 확장)"""
        dashboard_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "healthy",
            "pilots": {},
            "summary_metrics": {},
            "alerts": [],
            "recommendations": [],
            "day38_features": {
                "objective_function": True,
                "sensitivity_analysis": True,
                "time_series": True,
                "enhanced_alerts": True,
            },
        }

        total_quality = 0
        total_safety = 0
        total_performance = 0
        total_error_rate = 0
        total_J = 0
        active_pilots = 0

        for pilot_name in self.pilots.keys():
            result = self.collect_domain_metrics(pilot_name)
            self.pilots[pilot_name]["metrics"] = result["metrics"]
            self.pilots[pilot_name]["last_update"] = datetime.now()

            if result["status"] == "active":
                metrics = result["metrics"]

                # 시계열 저장
                self.save_time_series(pilot_name, metrics)

                # 알람 체크
                alerts = self.check_alerts(pilot_name, metrics)
                dashboard_data["alerts"].extend(alerts)

                # 대시보드 데이터 구성
                dashboard_data["pilots"][pilot_name] = {
                    "status": "healthy",
                    "last_updated": metrics["bin_start_utc"],
                    "quality_score": round(metrics["accuracy_mean"] * 100, 1),
                    "safety_score": round((1 - metrics["failure_rate"]) * 100, 1),
                    "performance_ms": round(metrics["latency_ms_p95"], 0),
                    "error_rate_percent": round(metrics["failure_rate"] * 100, 2),
                    "explainability_score": round(metrics["explain_mean"] * 100, 1),
                    "objective_function_J": round(metrics["J"], 6),
                    "sensitivity_failure": round(metrics["dJ_dfail"], 3),
                    "sensitivity_latency": round(metrics["dJ_dlat"], 6),
                }

                total_quality += metrics["accuracy_mean"] * 100
                total_safety += (1 - metrics["failure_rate"]) * 100
                total_performance += metrics["latency_ms_p95"]
                total_error_rate += metrics["failure_rate"] * 100
                total_J += metrics["J"]
                active_pilots += 1

        # 요약 메트릭 계산
        if active_pilots > 0:
            dashboard_data["summary_metrics"] = {
                "avg_quality_score": round(total_quality / active_pilots, 1),
                "avg_safety_score": round(total_safety / active_pilots, 1),
                "avg_performance_ms": round(total_performance / active_pilots, 0),
                "avg_error_rate_percent": round(total_error_rate / active_pilots, 2),
                "avg_objective_function_J": round(total_J / active_pilots, 6),
                "active_pilots": active_pilots,
                "total_alerts": len(dashboard_data["alerts"]),
            }

        return dashboard_data

    def run_monitoring_cycle(self):
        """모니터링 사이클 실행 (기존 Day34 방식 확장)"""
        self.logger.info("🚀 Day38 Enhanced PoU 모니터링 시작")

        dashboard_data = self.generate_enhanced_dashboard()

        # 결과 저장
        self._save_dashboard(dashboard_data)

        # 콘솔 출력
        self._print_dashboard_summary(dashboard_data)

        self.logger.info("✅ Day38 Enhanced PoU 모니터링 완료")

    def _save_dashboard(self, dashboard_data: Dict[str, Any]):
        """대시보드 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_filename = f"artifacts/day38/day38_enhanced_dashboard_{timestamp}.json"

        Path(dashboard_filename).parent.mkdir(parents=True, exist_ok=True)
        with open(dashboard_filename, "w", encoding="utf-8") as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"📊 대시보드 저장 완료: {dashboard_filename}")

    def _print_dashboard_summary(self, dashboard_data: Dict[str, Any]):
        """대시보드 요약 출력"""
        print("\n" + "=" * 80)
        print("📊 Day38 Enhanced PoU 모니터링 결과")
        print("=" * 80)
        print(f"전체 상태: {dashboard_data['overall_status'].upper()}")
        print(f"활성 파일럿: {dashboard_data['summary_metrics'].get('active_pilots', 0)}개")
        print(f"평균 품질 점수: {dashboard_data['summary_metrics'].get('avg_quality_score', 0)}")
        print(f"평균 안전 점수: {dashboard_data['summary_metrics'].get('avg_safety_score', 0)}")
        print(f"평균 성능: {dashboard_data['summary_metrics'].get('avg_performance_ms', 0)}ms")
        print(f"평균 오류율: {dashboard_data['summary_metrics'].get('avg_error_rate_percent', 0)}%")
        print(
            f"평균 목적함수 J: {dashboard_data['summary_metrics'].get('avg_objective_function_J', 0)}"
        )
        print(f"총 알림 수: {dashboard_data['summary_metrics'].get('total_alerts', 0)}")

        if dashboard_data["alerts"]:
            print("\n⚠️ 알림:")
            for alert in dashboard_data["alerts"]:
                print(f"  - {alert['domain']}: {alert['type']} - {alert['value']}")

        print("=" * 80)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Day38 Enhanced PoU 모니터링")
    parser.add_argument("--config", default="configs/monitoring.yaml", help="설정 파일")
    parser.add_argument("--loop", action="store_true", help="지속 실행 (60초 주기)")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    monitoring_system = EnhancedPoUMonitoringSystem(args.config)

    if args.loop:
        while True:
            try:
                monitoring_system.run_monitoring_cycle()
            except Exception as e:
                print(f"[monitoring] error: {e}")
            time.sleep(60)
    else:
        monitoring_system.run_monitoring_cycle()


if __name__ == "__main__":
    main()
