from .config import Config


def load_env():
    """환경변수 로드 함수 (호환성을 위한 래퍼)"""
    from pathlib import Path

    from dotenv import load_dotenv

    env_path = Path("/app/.env")
    load_dotenv(dotenv_path=env_path)


__all__ = ["Config", "load_env"]
