#!/usr/bin/env python3
"""
Database Manager - Core 데이터베이스 관리자

감정 데이터와 의사결정 결과를 데이터베이스에 저장하고 관리하는 역할을 합니다.
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from datetime import datetime
from typing import Dict, Optional, Any, List
from duri_common.logger import get_logger
from duri_common.config.config import Config

logger = get_logger("duri_core.database")
config = Config()


class DatabaseManager:
    """데이터베이스 관리자"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        DatabaseManager 초기화
        
        Args:
            database_url (str, optional): 데이터베이스 연결 URL
        """
        self.database_url = database_url or config.get_database_url()
        self.connection = None
        self._test_connection()
    
    def _test_connection(self):
        """데이터베이스 연결 테스트"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            logger.info("데이터베이스 연결 성공")
        except Exception as e:
            logger.warning(f"데이터베이스 연결 실패: {e}")
            self.connection = None
    
    def get_connection(self):
        """데이터베이스 연결 반환"""
        if self.connection is None or self.connection.closed:
            try:
                self.connection = psycopg2.connect(self.database_url)
            except Exception as e:
                logger.error(f"데이터베이스 재연결 실패: {e}")
                return None
        return self.connection
    
    def close_connection(self):
        """데이터베이스 연결 종료"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("데이터베이스 연결 종료")


class EmotionRequestLogger:
    """감정 요청/응답 로거"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        EmotionRequestLogger 초기화
        
        Args:
            database_url (str, optional): 데이터베이스 연결 URL
        """
        self.db_manager = DatabaseManager(database_url)
    
    def save_emotion_request(
        self,
        request_id: str,
        emotion: str,
        request_data: Dict[str, Any],
        client_ip: str,
        user_agent: str,
        timestamp: str
    ) -> bool:
        """
        감정 요청을 데이터베이스에 저장
        
        Args:
            request_id (str): 요청 ID
            emotion (str): 감정
            request_data (Dict): 요청 데이터
            client_ip (str): 클라이언트 IP
            user_agent (str): User-Agent
            timestamp (str): 타임스탬프
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            conn = self.db_manager.get_connection()
            if conn is None:
                logger.error("데이터베이스 연결 실패")
                return False
            
            with conn.cursor() as cursor:
                # core.emotion_requests 테이블에 저장
                cursor.execute("""
                    INSERT INTO core.emotion_requests (
                        request_id, emotion, request_data, client_ip, 
                        user_agent, timestamp, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    request_id,
                    emotion,
                    Json(request_data),
                    client_ip,
                    user_agent,
                    timestamp,
                    datetime.now()
                ))
                
                conn.commit()
                logger.info(f"감정 요청 저장 성공: {request_id}")
                return True
                
        except Exception as e:
            logger.error(f"감정 요청 저장 실패: {e}")
            if conn:
                conn.rollback()
            return False
    
    def save_emotion_response(
        self,
        request_id: str,
        response_data: Dict[str, Any],
        processing_time: float,
        status: str,
        timestamp: str
    ) -> bool:
        """
        감정 응답을 데이터베이스에 저장
        
        Args:
            request_id (str): 요청 ID
            response_data (Dict): 응답 데이터
            processing_time (float): 처리 시간
            status (str): 응답 상태
            timestamp (str): 타임스탬프
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            conn = self.db_manager.get_connection()
            if conn is None:
                logger.error("데이터베이스 연결 실패")
                return False
            
            with conn.cursor() as cursor:
                # core.emotion_responses 테이블에 저장
                cursor.execute("""
                    INSERT INTO core.emotion_responses (
                        request_id, response_data, processing_time, 
                        status, timestamp, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    request_id,
                    Json(response_data),
                    processing_time,
                    status,
                    timestamp,
                    datetime.now()
                ))
                
                conn.commit()
                logger.info(f"감정 응답 저장 성공: {request_id}")
                return True
                
        except Exception as e:
            logger.error(f"감정 응답 저장 실패: {e}")
            if conn:
                conn.rollback()
            return False
    
    def get_emotion_request_history(
        self,
        limit: int = 100,
        emotion: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        감정 요청 히스토리 조회
        
        Args:
            limit (int): 조회할 최대 개수
            emotion (str, optional): 특정 감정 필터링
            start_date (str, optional): 시작 날짜 (YYYY-MM-DD)
            end_date (str, optional): 종료 날짜 (YYYY-MM-DD)
        
        Returns:
            List[Dict]: 요청 히스토리
        """
        try:
            conn = self.db_manager.get_connection()
            if conn is None:
                logger.error("데이터베이스 연결 실패")
                return []
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT r.*, resp.response_data, resp.processing_time, resp.status
                    FROM core.emotion_requests r
                    LEFT JOIN core.emotion_responses resp ON r.request_id = resp.request_id
                    WHERE 1=1
                """
                params = []
                
                if emotion:
                    query += " AND r.emotion = %s"
                    params.append(emotion)
                
                if start_date:
                    query += " AND DATE(r.timestamp) >= %s"
                    params.append(start_date)
                
                if end_date:
                    query += " AND DATE(r.timestamp) <= %s"
                    params.append(end_date)
                
                query += " ORDER BY r.created_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                # RealDictCursor 결과를 일반 딕셔너리로 변환
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"감정 요청 히스토리 조회 실패: {e}")
            return []
    
    def get_emotion_statistics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        감정 처리 통계 조회
        
        Args:
            start_date (str, optional): 시작 날짜 (YYYY-MM-DD)
            end_date (str, optional): 종료 날짜 (YYYY-MM-DD)
        
        Returns:
            Dict: 통계 데이터
        """
        try:
            conn = self.db_manager.get_connection()
            if conn is None:
                logger.error("데이터베이스 연결 실패")
                return {}
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 기본 WHERE 조건
                where_conditions = ["1=1"]
                params = []
                
                if start_date:
                    where_conditions.append("DATE(r.timestamp) >= %s")
                    params.append(start_date)
                
                if end_date:
                    where_conditions.append("DATE(r.timestamp) <= %s")
                    params.append(end_date)
                
                where_clause = " AND ".join(where_conditions)
                
                # 전체 요청 수
                cursor.execute(f"""
                    SELECT COUNT(*) as total_requests
                    FROM core.emotion_requests r
                    WHERE {where_clause}
                """, params)
                total_requests = cursor.fetchone()['total_requests']
                
                # 감정별 요청 수
                cursor.execute(f"""
                    SELECT emotion, COUNT(*) as count
                    FROM core.emotion_requests r
                    WHERE {where_clause}
                    GROUP BY emotion
                    ORDER BY count DESC
                """, params)
                emotion_counts = [dict(row) for row in cursor.fetchall()]
                
                # 성공/실패 통계
                cursor.execute(f"""
                    SELECT resp.status, COUNT(*) as count
                    FROM core.emotion_requests r
                    LEFT JOIN core.emotion_responses resp ON r.request_id = resp.request_id
                    WHERE {where_clause}
                    GROUP BY resp.status
                """, params)
                status_counts = [dict(row) for row in cursor.fetchall()]
                
                # 평균 처리 시간
                cursor.execute(f"""
                    SELECT AVG(resp.processing_time) as avg_processing_time
                    FROM core.emotion_requests r
                    LEFT JOIN core.emotion_responses resp ON r.request_id = resp.request_id
                    WHERE {where_clause} AND resp.processing_time IS NOT NULL
                """, params)
                avg_processing_time = cursor.fetchone()['avg_processing_time']
                
                return {
                    "total_requests": total_requests,
                    "emotion_counts": emotion_counts,
                    "status_counts": status_counts,
                    "avg_processing_time": float(avg_processing_time) if avg_processing_time else 0.0
                }
                
        except Exception as e:
            logger.error(f"감정 통계 조회 실패: {e}")
            return {}


# 전역 인스턴스
emotion_logger = EmotionRequestLogger()


def save_emotion_request_to_db(
    request_id: str,
    emotion: str,
    request_data: Dict[str, Any],
    client_ip: str,
    user_agent: str,
    timestamp: str
) -> bool:
    """감정 요청을 데이터베이스에 저장 (편의 함수)"""
    return emotion_logger.save_emotion_request(
        request_id, emotion, request_data, client_ip, user_agent, timestamp
    )


def save_emotion_response_to_db(
    request_id: str,
    response_data: Dict[str, Any],
    processing_time: float,
    status: str,
    timestamp: str
) -> bool:
    """감정 응답을 데이터베이스에 저장 (편의 함수)"""
    return emotion_logger.save_emotion_response(
        request_id, response_data, processing_time, status, timestamp
    ) 