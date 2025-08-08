#!/usr/bin/env python3
"""
DuRiCore - Vector Database
FAISS 기반 벡터 데이터베이스 구현
"""

import numpy as np
import faiss
import pickle
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class VectorDatabase:
    """FAISS 기반 벡터 데이터베이스"""
    
    def __init__(self, dimension: int = 768, index_type: str = "l2"):
        """
        벡터 데이터베이스 초기화
        
        Args:
            dimension: 벡터 차원 (기본값: 768 - BERT 임베딩)
            index_type: 인덱스 타입 ("l2", "cosine", "ip")
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.metadata = []
        self.vector_count = 0
        
        # 인덱스 초기화
        self._initialize_index()
        
        # 저장 경로
        self.save_dir = "vector_db"
        os.makedirs(self.save_dir, exist_ok=True)
    
    def _initialize_index(self):
        """FAISS 인덱스 초기화"""
        try:
            if self.index_type == "l2":
                self.index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == "cosine":
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product for cosine
            elif self.index_type == "ip":
                self.index = faiss.IndexFlatIP(self.dimension)
            else:
                raise ValueError(f"지원하지 않는 인덱스 타입: {self.index_type}")
            
            logger.info(f"FAISS 인덱스 초기화 완료: {self.index_type}, 차원: {self.dimension}")
            
        except Exception as e:
            logger.error(f"FAISS 인덱스 초기화 실패: {e}")
            raise
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> bool:
        """
        벡터와 메타데이터 추가
        
        Args:
            vectors: 벡터 배열 (numpy array)
            metadata: 메타데이터 리스트
            
        Returns:
            성공 여부
        """
        try:
            if len(vectors) != len(metadata):
                raise ValueError("벡터와 메타데이터의 개수가 일치하지 않습니다.")
            
            # 벡터 정규화 (cosine similarity를 위한 경우)
            if self.index_type == "cosine":
                faiss.normalize_L2(vectors)
            
            # 인덱스에 벡터 추가
            self.index.add(vectors)
            
            # 메타데이터 추가
            for meta in metadata:
                meta["id"] = self.vector_count
                meta["timestamp"] = datetime.now().isoformat()
                self.metadata.append(meta)
                self.vector_count += 1
            
            logger.info(f"{len(vectors)}개의 벡터가 추가되었습니다. 총 벡터: {self.vector_count}")
            return True
            
        except Exception as e:
            logger.error(f"벡터 추가 실패: {e}")
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        유사한 벡터 검색
        
        Args:
            query_vector: 쿼리 벡터
            k: 반환할 최대 개수
            
        Returns:
            (거리, 인덱스, 메타데이터) 튜플
        """
        try:
            # 쿼리 벡터 정규화 (cosine similarity를 위한 경우)
            if self.index_type == "cosine":
                query_vector = query_vector.reshape(1, -1)
                faiss.normalize_L2(query_vector)
            
            # 검색 실행
            distances, indices = self.index.search(query_vector, k)
            
            # 메타데이터 추출
            results_metadata = []
            for idx in indices[0]:
                if idx < len(self.metadata):
                    results_metadata.append(self.metadata[idx])
                else:
                    results_metadata.append({"id": idx, "error": "메타데이터 없음"})
            
            return distances[0], indices[0], results_metadata
            
        except Exception as e:
            logger.error(f"벡터 검색 실패: {e}")
            return np.array([]), np.array([]), []
    
    def batch_search(self, query_vectors: np.ndarray, k: int = 5) -> List[Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]]:
        """
        배치 벡터 검색
        
        Args:
            query_vectors: 쿼리 벡터 배열
            k: 반환할 최대 개수
            
        Returns:
            검색 결과 리스트
        """
        try:
            results = []
            
            for i, query_vector in enumerate(query_vectors):
                distances, indices, metadata = self.search(query_vector, k)
                results.append((distances, indices, metadata))
            
            return results
            
        except Exception as e:
            logger.error(f"배치 벡터 검색 실패: {e}")
            return []
    
    def get_vector_by_id(self, vector_id: int) -> Optional[Dict[str, Any]]:
        """
        ID로 벡터 메타데이터 조회
        
        Args:
            vector_id: 벡터 ID
            
        Returns:
            메타데이터 또는 None
        """
        try:
            if 0 <= vector_id < len(self.metadata):
                return self.metadata[vector_id]
            return None
            
        except Exception as e:
            logger.error(f"벡터 ID 조회 실패: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """벡터 데이터베이스 통계"""
        try:
            return {
                "total_vectors": self.vector_count,
                "dimension": self.dimension,
                "index_type": self.index_type,
                "metadata_count": len(self.metadata),
                "index_size": self.index.ntotal if self.index else 0
            }
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}
    
    def save(self, filename: str = None) -> bool:
        """
        벡터 데이터베이스 저장
        
        Args:
            filename: 저장할 파일명 (기본값: 자동 생성)
            
        Returns:
            성공 여부
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"vector_db_{timestamp}"
            
            # 인덱스 저장
            index_path = os.path.join(self.save_dir, f"{filename}.index")
            faiss.write_index(self.index, index_path)
            
            # 메타데이터 저장
            metadata_path = os.path.join(self.save_dir, f"{filename}.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"벡터 데이터베이스 저장 완료: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"벡터 데이터베이스 저장 실패: {e}")
            return False
    
    def load(self, filename: str) -> bool:
        """
        벡터 데이터베이스 로드
        
        Args:
            filename: 로드할 파일명
            
        Returns:
            성공 여부
        """
        try:
            # 인덱스 로드
            index_path = os.path.join(self.save_dir, f"{filename}.index")
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"인덱스 파일을 찾을 수 없습니다: {index_path}")
            
            self.index = faiss.read_index(index_path)
            
            # 메타데이터 로드
            metadata_path = os.path.join(self.save_dir, f"{filename}.json")
            if not os.path.exists(metadata_path):
                raise FileNotFoundError(f"메타데이터 파일을 찾을 수 없습니다: {metadata_path}")
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            self.vector_count = len(self.metadata)
            logger.info(f"벡터 데이터베이스 로드 완료: {filename}, 벡터 수: {self.vector_count}")
            return True
            
        except Exception as e:
            logger.error(f"벡터 데이터베이스 로드 실패: {e}")
            return False
    
    def clear(self):
        """벡터 데이터베이스 초기화"""
        try:
            self._initialize_index()
            self.metadata = []
            self.vector_count = 0
            logger.info("벡터 데이터베이스가 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"벡터 데이터베이스 초기화 실패: {e}")
    
    def delete_vector(self, vector_id: int) -> bool:
        """
        벡터 삭제 (주의: FAISS는 삭제를 지원하지 않으므로 재구성 필요)
        
        Args:
            vector_id: 삭제할 벡터 ID
            
        Returns:
            성공 여부
        """
        try:
            if vector_id >= len(self.metadata):
                return False
            
            # 메타데이터에서 삭제
            self.metadata.pop(vector_id)
            
            # 인덱스 재구성 (실제로는 새로 생성)
            # 주의: FAISS는 개별 벡터 삭제를 지원하지 않음
            logger.warning("FAISS는 개별 벡터 삭제를 지원하지 않습니다. 전체 재구성이 필요합니다.")
            return False
            
        except Exception as e:
            logger.error(f"벡터 삭제 실패: {e}")
            return False 
 
 