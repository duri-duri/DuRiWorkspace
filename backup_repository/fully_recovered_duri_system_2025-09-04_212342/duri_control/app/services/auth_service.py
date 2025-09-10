import os
import jwt
import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

from ..models.user_model import UserInDB, UserCreate, UserLogin, UserResponse, UserRole, Token, TokenPayload

logger = logging.getLogger(__name__)

# JWT/비밀번호 관련 상수 (실제 환경에서는 .env에서 불러오는 것이 안전)
JWT_SECRET = os.getenv("JWT_SECRET", "duri_super_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "duri_salt")

# 관리자 계정 환경변수 (없으면 기본값)
DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "secret")
DEFAULT_ADMIN_ROLE = os.getenv("DEFAULT_ADMIN_ROLE", UserRole.ADMIN.value)
ADMIN_AUDIT_LOG = os.getenv("ADMIN_AUDIT_LOG", "/var/log/admin_seed_audit.log")

class AuthService:
    """인증/권한 관리 서비스"""
    def __init__(self):
        self.db_config = {
            'host': 'duri-postgres',
            'port': 5432,
            'database': 'duri',
            'user': 'duri',
            'password': 'duri'
        }
        self._init_user_table()
        self._ensure_admin_user()

    def _get_connection(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"DB 연결 실패: {e}")
            raise

    def _init_user_table(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(128) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("사용자 테이블 초기화 완료")
        except Exception as e:
            logger.error(f"사용자 테이블 초기화 실패: {e}")
            raise

    def _ensure_admin_user(self):
        """최초 관리자 계정 자동 생성 (admin/secret) - 표준 시드 패턴(로깅+감사로그)"""
        try:
            admin = self.get_user_by_username(DEFAULT_ADMIN_USERNAME)
            if admin:
                message = f"✅ Admin already exists. Skipping creation. ({DEFAULT_ADMIN_USERNAME})"
                logger.info(message)
                self._write_audit_log(message)
            else:
                self.create_user(UserCreate(username=DEFAULT_ADMIN_USERNAME, password=DEFAULT_ADMIN_PASSWORD, role=DEFAULT_ADMIN_ROLE))
                message = f"🟢 최초 관리자 계정({DEFAULT_ADMIN_USERNAME}/{DEFAULT_ADMIN_PASSWORD}) 생성 완료"
                logger.info(message)
                print(message)  # 명확한 콘솔 출력도 추가
                self._write_audit_log(message)
        except Exception as e:
            error_msg = f"❌ Admin 계정 시드 중 오류 발생: {e}"
            logger.error(error_msg)
            print(error_msg)
            self._write_audit_log(error_msg)

    def _write_audit_log(self, msg: str):
        try:
            with open(ADMIN_AUDIT_LOG, "a") as f:
                f.write(f"[{datetime.now()}] {msg}\n")
        except Exception:
            logger.warning("⚠️ admin_seed_audit.log 파일 기록 실패")

    def hash_password(self, password: str) -> str:
        return hashlib.pbkdf2_hmac(
            'sha256', password.encode(), PASSWORD_SALT.encode(), 100_000
        ).hex()

    def verify_password(self, password: str, password_hash: str) -> bool:
        return hmac.compare_digest(self.hash_password(password), password_hash)

    def create_user(self, user: UserCreate) -> UserResponse:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            password_hash = self.hash_password(user.password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
                RETURNING id, username, role, is_active, created_at
            ''', (user.username, password_hash, user.role.value if hasattr(user.role, 'value') else user.role))
            row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            return UserResponse(
                id=row[0], username=row[1], role=row[2], is_active=row[3], created_at=row[4]
            )
        except Exception as e:
            logger.error(f"사용자 생성 실패: {e}")
            raise

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT * FROM users WHERE username = %s
            ''', (username,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                return UserInDB(**row)
            return None
        except Exception as e:
            logger.error(f"사용자 조회 실패: {e}")
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        user = self.get_user_by_username(username)
        if user and user.is_active and self.verify_password(password, user.password_hash):
            return user
        return None

    def create_access_token(self, user: UserInDB) -> str:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user.username,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "exp": int(expire.timestamp()),
            "type": "access"
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def create_refresh_token(self, user: UserInDB) -> str:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": user.username,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "exp": int(expire.timestamp()),
            "type": "refresh"
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT 만료")
            return None
        except jwt.InvalidTokenError:
            logger.warning("JWT 무효")
            return None

    def get_current_user(self, token: str) -> Optional[UserInDB]:
        payload = self.decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        username = payload.get("sub")
        return self.get_user_by_username(username)

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        payload = self.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        username = payload.get("sub")
        user = self.get_user_by_username(username)
        if not user or not user.is_active:
            return None
        return self.create_access_token(user)

# 전역 인스턴스
auth_service = None

def get_auth_service() -> AuthService:
    global auth_service
    if auth_service is None:
        auth_service = AuthService()
    return auth_service

def init_auth_service():
    global auth_service
    auth_service = AuthService()
    return auth_service 