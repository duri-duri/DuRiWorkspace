#!/usr/bin/env python3
"""
DuRi 메트릭 서버 (독립 실행)
"""
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from prometheus_client import generate_latest, REGISTRY

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            try:
                metrics = generate_latest()
                self.wfile.write(metrics)
            except Exception as e:
                self.wfile.write(f"# ERROR: {e}\n".encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def log_message(self, format, *args):
        pass  # 로그 비활성화

def start_metrics_server(port: int = None):
    """메트릭 서버 시작"""
    port = int(port or os.getenv("PROM_PORT", "9108"))
    
    server = HTTPServer(('localhost', port), MetricsHandler)
    print(f"🚀 메트릭 서버 시작: http://localhost:{port}/metrics")
    print(f"📊 레지스트리 상태: {len(REGISTRY._collector_to_names)} collectors")
    
    # 백그라운드 스레드로 서버 실행
    def run_server():
        server.serve_forever()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return server, port

if __name__ == "__main__":
    server, port = start_metrics_server()
    print(f"✅ 메트릭 서버 실행 중 (포트 {port})")
    print("💡 Ctrl+C로 종료")
    
    try:
        while True:
            time.sleep(60)
            print(f"💓 메트릭 서버 활성 상태 (포트 {port})")
    except KeyboardInterrupt:
        print("\n🛑 메트릭 서버 종료 중...")
        server.shutdown()
        print("✅ 메트릭 서버 종료 완료")






















