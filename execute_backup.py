#!/usr/bin/env python3
"""
DuRi Control System v1.0.0 백업 생성 스크립트
"""

import os
import subprocess
import datetime
import sys

def run_command(command, description):
    """명령어 실행 및 결과 출력"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} 완료")
            if result.stdout.strip():
                print(f"   출력: {result.stdout.strip()}")
        else:
            print(f"⚠️ {description} 실패")
            if result.stderr.strip():
                print(f"   오류: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} 오류: {e}")
        return False

def main():
    print("🎯 DuRi Control System v1.0.0 백업 생성 시작...")
    print("=" * 60)
    
    # 현재 디렉토리 확인
    if not os.path.exists("docker-compose.yml"):
        print("❌ docker-compose.yml을 찾을 수 없습니다. 올바른 디렉토리에서 실행하세요.")
        sys.exit(1)
    
    # 백업 파일명 생성
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"DuRiWorkspace_v1.0.0_final_{timestamp}.tar.gz"
    
    print(f"📦 백업 파일명: {backup_name}")
    print()
    
    # 1. 기존 백업 파일 정리
    print("🧹 기존 백업 파일 정리 중...")
    run_command("find . -name '*.tar.gz' -type f -delete", "기존 tar.gz 파일 삭제")
    run_command("find . -name '*.zip' -type f -delete", "기존 zip 파일 삭제")
    print()
    
    # 2. 시스템 상태 확인
    print("🔍 시스템 상태 확인 중...")
    run_command("docker-compose ps", "Docker 컨테이너 상태 확인")
    run_command("curl -s http://localhost:8083/health/", "API 서버 상태 확인")
    print()
    
    # 3. 백업 생성
    print("📦 백업 파일 생성 중...")
    exclude_file = "backup_exclude.txt"
    
    if os.path.exists(exclude_file):
        print(f"📋 제외 파일 목록 사용: {exclude_file}")
        success = run_command(
            f"tar --exclude-from='{exclude_file}' -czf '{backup_name}' .",
            "백업 파일 생성"
        )
    else:
        print("⚠️ 제외 파일 목록을 찾을 수 없습니다. 기본 설정으로 백업합니다.")
        success = run_command(
            f"tar --exclude='*.tar.gz' --exclude='*.zip' --exclude='.git' --exclude='__pycache__' --exclude='*.log' --exclude='logs' --exclude='.env' -czf '{backup_name}' .",
            "백업 파일 생성"
        )
    
    if not success:
        print("❌ 백업 생성에 실패했습니다.")
        sys.exit(1)
    
    print()
    
    # 4. 백업 파일 크기 확인
    if os.path.exists(backup_name):
        size_result = subprocess.run(f"du -h '{backup_name}'", shell=True, capture_output=True, text=True)
        if size_result.returncode == 0:
            size = size_result.stdout.strip().split()[0]
            print(f"📊 백업 파일 크기: {size}")
        else:
            print("⚠️ 백업 파일 크기 확인 실패")
    else:
        print("❌ 백업 파일이 생성되지 않았습니다.")
        sys.exit(1)
    
    print()
    
    # 5. 백업 파일 무결성 확인
    print("🔍 백업 파일 무결성 확인 중...")
    integrity_success = run_command(
        f"tar -tzf '{backup_name}' > /dev/null",
        "백업 파일 무결성 검사"
    )
    
    if integrity_success:
        print("✅ 백업 파일이 정상적으로 생성되었습니다.")
    else:
        print("❌ 백업 파일에 문제가 있습니다.")
        sys.exit(1)
    
    print()
    
    # 6. 백업 정보 출력
    print("📋 백업 정보:")
    print(f"  - 파일명: {backup_name}")
    print(f"  - 크기: {size if 'size' in locals() else '확인 불가'}")
    print(f"  - 생성일: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  - 위치: {os.path.abspath(backup_name)}")
    print()
    
    # 7. 현재 디렉토리의 백업 파일 목록
    print("📁 현재 디렉토리의 백업 파일들:")
    backup_files = [f for f in os.listdir('.') if f.endswith('.tar.gz')]
    if backup_files:
        for file in backup_files:
            try:
                file_size = os.path.getsize(file)
                print(f"  - {file} ({file_size:,} bytes)")
            except:
                print(f"  - {file}")
    else:
        print("  백업 파일이 없습니다.")
    
    print()
    print("🎉 DuRi Control System v1.0.0 최종 백업이 성공적으로 완료되었습니다!")
    print("💡 백업 파일을 안전한 곳에 보관하세요.")
    print("=" * 60)

if __name__ == "__main__":
    main() 