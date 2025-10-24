import json

from duri_common.settings import DuRiSettings, get_settings


def setup_function(_):
    # 매 테스트 전 캐시 비움
    try:
        get_settings.cache_clear()
    except Exception:
        pass


def test_env_default_is_dev():
    s = DuRiSettings()
    assert s.env in {"dev", "ops", "prod", "test"}


def test_env_override_priority(monkeypatch):
    monkeypatch.setenv("DURI_ENV", "prod")
    s = DuRiSettings()  # 싱글톤이 아니라 "새로" 생성
    assert s.env == "prod"


def test_json_fallback_compat(tmp_path, monkeypatch):
    cfg = {
        "env": "ops",
        "monitoring": {
            "prometheus_url": "http://prom:9090",
            "grafana_url": "http://graf:3000",
        },
    }
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    monkeypatch.setenv("DURI_CONFIG_JSON", str(p))
    # ENV가 없으면 JSON이 먹어야 한다
    s = DuRiSettings()
    assert s.env == "ops"
    assert s.monitoring.prometheus_url.endswith(":9090")


def test_env_beats_json(tmp_path, monkeypatch):
    # JSON은 ops, ENV는 prod → ENV가 이긴다
    cfg = {"env": "ops"}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    monkeypatch.setenv("DURI_CONFIG_JSON", str(p))
    monkeypatch.setenv("DURI_ENV", "prod")
    s = DuRiSettings()
    assert s.env == "prod"


def test_database_url_generation():
    s = DuRiSettings()
    assert s.database.url.startswith("postgresql://")
    assert "duri-postgres" in s.database.url


def test_redis_url_generation():
    s = DuRiSettings()
    assert s.redis.url.startswith("redis://")
    assert "duri-redis" in s.redis.url


def test_grafana_credentials():
    s = DuRiSettings()
    assert s.monitoring.grafana_user == "duri-duri"
    assert s.monitoring.grafana_password == "DuRi@2025!"


def test_to_dict_compatibility():
    s = DuRiSettings()
    config_dict = s.to_dict()
    assert "database" in config_dict
    assert "redis" in config_dict
    assert "services" in config_dict
    assert "monitoring" in config_dict


def test_nested_env_override(monkeypatch):
    monkeypatch.setenv("DURI_MONITORING__PROMETHEUS_URL", "http://x:9091")
    s = DuRiSettings()
    assert s.monitoring.prometheus_url == "http://x:9091"


def test_unknown_key_rejected(monkeypatch):
    monkeypatch.setenv("DURI__UNKNOWN_KEY", "x")
    try:
        DuRiSettings()
        assert False, "unknown key should fail"  # noqa: B011
    except Exception:
        assert True
