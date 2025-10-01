"""
Test suite for DuRi common emotion modules.
Tests core functionality of EmotionVector and emotion handlers.
"""

import json
import os
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest
from pytest import approx

from duri_core.common.emotion_handlers import (
    EmotionDeltaHandler,
    EmotionLogger,
    EmotionTransmitter,
)
from duri_core.common.emotion_vector import EmotionVector


# EmotionVector 테스트
class TestEmotionVector:
    def test_init_empty(self):
        """빈 벡터 초기화 테스트"""
        vector = EmotionVector()
        assert all(val == approx(0.0) for val in vector.values.values())
        assert len(vector.values) == len(EmotionVector.DIMENSIONS)

    def test_init_with_values(self):
        """값이 있는 벡터 초기화 테스트"""
        values = {"joy": 0.8, "trust": 0.6}
        vector = EmotionVector(values)
        assert vector.values["joy"] == approx(0.8)
        assert vector.values["trust"] == approx(0.6)
        assert vector.values["anger"] == approx(0.0)  # 지정되지 않은 차원

    def test_value_bounds(self):
        """감정 값 범위 제한 테스트"""
        values = {"joy": 1.5, "anger": -0.5}  # 범위 벗어난 값
        vector = EmotionVector(values)
        assert vector.values["joy"] == approx(1.0)  # 최대값으로 제한
        assert vector.values["anger"] == approx(0.0)  # 최소값으로 제한

    def test_from_keyword(self):
        """키워드 기반 벡터 생성 테스트"""
        vector = EmotionVector.from_keyword("칭찬")
        assert vector.values["joy"] == approx(0.8)
        assert vector.values["trust"] == approx(0.6)

    def test_compute_importance(self):
        """중요도 계산 테스트"""
        values = {"joy": 0.8, "trust": 0.6}
        vector = EmotionVector(values)
        importance = vector.compute_importance()
        assert 0 <= importance <= 1

        # 모든 값이 0인 경우
        zero_vector = EmotionVector()
        assert zero_vector.compute_importance() == approx(0.0)

    def test_get_dominant_emotions(self):
        """주요 감정 추출 테스트"""
        values = {"joy": 0.8, "trust": 0.6, "anger": 0.2, "fear": 0.0}  # 임계값 미만
        vector = EmotionVector(values)
        dominant = vector.get_dominant_emotions(threshold=0.3)
        assert len(dominant) == 2
        assert dominant[0][0] == "joy"
        assert dominant[1][0] == "trust"


# EmotionLogger 테스트
class TestEmotionLogger:
    @pytest.fixture
    def temp_dir(self, tmp_path):
        """임시 디렉토리 생성"""
        return str(tmp_path)

    def test_log_change(self, temp_dir):
        """감정 변화 로깅 테스트"""
        logger = EmotionLogger(base_path=temp_dir)
        old_vector = EmotionVector({"joy": 0.5})
        new_vector = EmotionVector({"joy": 0.8})

        logger.log_change(old_vector, new_vector)

        log_file = os.path.join(
            temp_dir, datetime.now().strftime("%Y-%m-%d"), "emotion_change_log.json"
        )

        assert os.path.exists(log_file)
        with open(log_file, "r") as f:
            log_entry = json.loads(f.readline())
            assert "timestamp" in log_entry
            assert "old_emotions" in log_entry
            assert "new_emotions" in log_entry
            assert "importance_delta" in log_entry


# EmotionDeltaHandler 테스트
class TestEmotionDeltaHandler:
    def test_compute_delta(self):
        """감정 벡터 델타 계산 테스트"""
        handler = EmotionDeltaHandler()
        old_vector = EmotionVector({"joy": 0.5, "trust": 0.3})
        new_vector = EmotionVector({"joy": 0.8, "trust": 0.2})

        delta = handler.compute_delta(old_vector, new_vector)
        assert delta["joy"] == approx(0.3)
        assert delta["trust"] == approx(-0.1)
        assert all(dim in delta for dim in EmotionVector.DIMENSIONS)

    def test_update_from_delta(self):
        """델타 적용 테스트"""
        handler = EmotionDeltaHandler()
        current = EmotionVector({"joy": 0.5, "trust": 0.3})
        delta = {"joy": 0.3, "trust": -0.1}

        updated = handler.update_from_delta(current, delta)
        assert updated.values["joy"] == approx(0.8)
        assert updated.values["trust"] == approx(0.2)
        assert all(0 <= val <= 1 for val in updated.values.values())


# EmotionTransmitter 테스트
class TestEmotionTransmitter:
    @pytest.fixture
    def transmitter(self):
        return EmotionTransmitter(dest_url="http://test.local/emotion")

    @patch("requests.post")
    def test_send_emotion_success(self, mock_post, transmitter):
        """감정 전송 성공 테스트"""
        mock_post.return_value.status_code = 200
        vector = EmotionVector({"joy": 0.8})

        success = transmitter.send_emotion(vector)
        assert success
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_send_emotion_failure(self, mock_post, transmitter):
        """감정 전송 실패 테스트"""
        mock_post.return_value.status_code = 500
        vector = EmotionVector({"joy": 0.8})

        with patch("builtins.open", mock_open()) as mock_file:
            success = transmitter.send_emotion(vector)
            assert not success
            mock_file.assert_called_once()  # 큐에 저장되었는지 확인

    def test_load_importance_threshold(self, transmitter):
        """중요도 임계값 로드 테스트"""
        # 설정 파일이 없는 경우
        threshold = transmitter.load_importance_threshold()
        assert threshold == approx(0.3)  # 기본값

        # 설정 파일이 있는 경우
        mock_config = {"importance_threshold": 0.5}
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            threshold = transmitter.load_importance_threshold()
            assert threshold == approx(0.5)


if __name__ == "__main__":
    pytest.main([__file__])
