import os

# 환경변수에서 경로를 읽고, 없으면 기본값 사용
def get_log_dir():
    path = os.getenv("LOG_DIR", "./logs/control")
    os.makedirs(path, exist_ok=True)
    return path

def get_config_dir():
    path = os.getenv("CONFIG_DIR", "./config/control")
    os.makedirs(path, exist_ok=True)
    return path

def get_script_dir():
    path = os.getenv("SCRIPT_DIR", "./scripts/control")
    os.makedirs(path, exist_ok=True)
    return path 