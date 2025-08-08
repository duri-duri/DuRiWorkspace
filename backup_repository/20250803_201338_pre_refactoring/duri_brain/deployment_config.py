#!/usr/bin/env python3
"""
DuRi Family Interaction MVP - Internet Deployment Configuration
인터넷 배포를 위한 설정 파일
"""
import os
from typing import Dict, Any

class DeploymentConfig:
    """배포 설정 클래스"""
    
    def __init__(self):
        self.deployment_options = {
            "heroku": {
                "name": "Heroku",
                "cost": "무료 (월 550시간)",
                "setup_time": "5분",
                "features": ["자동 배포", "SSL 인증서", "커스텀 도메인"],
                "url": "https://duri-family-interaction.herokuapp.com"
            },
            "railway": {
                "name": "Railway",
                "cost": "무료 (월 $5 크레딧)",
                "setup_time": "3분",
                "features": ["자동 배포", "SSL 인증서", "Git 연동"],
                "url": "https://duri-family-interaction.railway.app"
            },
            "render": {
                "name": "Render",
                "cost": "무료 (월 750시간)",
                "setup_time": "4분",
                "features": ["자동 배포", "SSL 인증서", "커스텀 도메인"],
                "url": "https://duri-family-interaction.onrender.com"
            },
            "vercel": {
                "name": "Vercel",
                "cost": "무료",
                "setup_time": "2분",
                "features": ["자동 배포", "SSL 인증서", "글로벌 CDN"],
                "url": "https://duri-family-interaction.vercel.app"
            }
        }
        
        self.security_settings = {
            "family_only_access": True,
            "password_protection": True,
            "session_timeout": 3600,  # 1시간
            "max_connections": 10,
            "allowed_ips": []  # 특정 IP만 허용 (선택사항)
        }
        
        self.domain_options = [
            "duri-family.herokuapp.com",
            "duri-family.railway.app", 
            "duri-family.onrender.com",
            "duri-family.vercel.app",
            "duri-family.netlify.app"
        ]

    def get_deployment_guide(self, platform: str = "railway") -> Dict[str, Any]:
        """배포 가이드 생성"""
        if platform not in self.deployment_options:
            platform = "railway"
        
        guide = {
            "platform": self.deployment_options[platform],
            "steps": [
                "1. GitHub에 코드 업로드",
                "2. Railway/Render/Heroku 계정 생성",
                "3. 새 프로젝트 생성",
                "4. GitHub 저장소 연결",
                "5. 환경 변수 설정",
                "6. 자동 배포 활성화",
                "7. 도메인 설정 (선택사항)"
            ],
            "environment_variables": {
                "FLASK_ENV": "production",
                "SECRET_KEY": "your-secret-key-here",
                "FAMILY_ACCESS_CODE": "duri2025"
            },
            "requirements": [
                "Flask==2.3.3",
                "gunicorn==21.2.0",
                "python-dotenv==1.0.0"
            ]
        }
        
        return guide

    def create_procfile(self) -> str:
        """Procfile 생성 (Heroku용)"""
        return """web: gunicorn app.services.real_family_interaction_mvp:app"""

    def create_requirements_txt(self) -> str:
        """requirements.txt 생성"""
        return """Flask==2.3.3
gunicorn==21.2.0
python-dotenv==1.0.0
Werkzeug==2.3.7"""

    def create_runtime_txt(self) -> str:
        """runtime.txt 생성"""
        return "python-3.10.12"

    def create_vercel_json(self) -> str:
        """vercel.json 생성 (Vercel용)"""
        return """{
  "version": 2,
  "builds": [
    {
      "src": "app/services/real_family_interaction_mvp.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/services/real_family_interaction_mvp.py"
    }
  ]
}"""

def generate_deployment_files():
    """배포 파일들 생성"""
    config = DeploymentConfig()
    
    # Procfile 생성
    with open("Procfile", "w") as f:
        f.write(config.create_procfile())
    
    # requirements.txt 생성
    with open("requirements.txt", "w") as f:
        f.write(config.create_requirements_txt())
    
    # runtime.txt 생성
    with open("runtime.txt", "w") as f:
        f.write(config.create_runtime_txt())
    
    # vercel.json 생성
    with open("vercel.json", "w") as f:
        f.write(config.create_vercel_json())
    
    print("✅ 배포 파일들 생성 완료!")

def show_deployment_options():
    """배포 옵션 표시"""
    config = DeploymentConfig()
    
    print("🌐 인터넷 배포 옵션:")
    print("=" * 50)
    
    for platform, info in config.deployment_options.items():
        print(f"\n📋 {info['name']}:")
        print(f"   💰 비용: {info['cost']}")
        print(f"   ⏱️  설정 시간: {info['setup_time']}")
        print(f"   🌟 특징: {', '.join(info['features'])}")
        print(f"   🔗 예상 URL: {info['url']}")
    
    print(f"\n🔒 보안 설정:")
    for key, value in config.security_settings.items():
        print(f"   {key}: {value}")
    
    print(f"\n🌍 도메인 옵션:")
    for domain in config.domain_options:
        print(f"   {domain}")

if __name__ == "__main__":
    show_deployment_options()
    generate_deployment_files() 