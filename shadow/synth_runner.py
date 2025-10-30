import time

import requests


def main():
    while True:
        try:
            # 실제 shadow 엔드포인트가 있다면 호출; 여기선 메트릭만 의존
            requests.get("http://localhost:9109/metrics", timeout=2)
        except Exception:
            pass
        time.sleep(10)


if __name__ == "__main__":
    main()
