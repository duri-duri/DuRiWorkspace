#!/usr/bin/env python3
"""
이미지 프로세서 테스트 모듈
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from unittest import TestCase, main

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.image_processor import (ImageProcessor, analyze_image,
                                   save_analysis_result)


class TestImageProcessor(TestCase):
    """이미지 프로세서 테스트 클래스"""

    def setUp(self):
        """테스트 설정"""
        self.image_processor = ImageProcessor()
        self.test_image_path = (
            "resources/images/f2cdf86f-c29b-4c06-97b5-dea28c8d0668.png"
        )
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """테스트 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_analyze_image_basic(self):
        """기본 이미지 분석 테스트"""
        if not os.path.exists(self.test_image_path):
            self.skipTest(f"테스트 이미지가 존재하지 않습니다: {self.test_image_path}")

        result = analyze_image(self.test_image_path, "basic")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["analysis_level"], "basic")
        self.assertIn("quality_estimate", result)
        self.assertIn("file_size_category", result)
        self.assertIn("metadata", result)

    def test_analyze_image_comprehensive(self):
        """종합 이미지 분석 테스트"""
        if not os.path.exists(self.test_image_path):
            self.skipTest(f"테스트 이미지가 존재하지 않습니다: {self.test_image_path}")

        result = analyze_image(self.test_image_path, "comprehensive")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["analysis_level"], "comprehensive")
        self.assertIn("basic_analysis", result)
        self.assertIn("image_characteristics", result)
        self.assertIn("processing_recommendations", result)

    def test_analyze_image_metadata(self):
        """메타데이터만 분석 테스트"""
        if not os.path.exists(self.test_image_path):
            self.skipTest(f"테스트 이미지가 존재하지 않습니다: {self.test_image_path}")

        result = analyze_image(self.test_image_path, "metadata")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["analysis_level"], "metadata_only")
        self.assertIn("metadata", result)

    def test_analyze_image_nonexistent(self):
        """존재하지 않는 이미지 분석 테스트"""
        result = analyze_image("nonexistent_image.png", "basic")

        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertIn("이미지 파일이 존재하지 않습니다", result["error"])

    def test_analyze_image_unsupported_format(self):
        """지원하지 않는 형식 테스트"""
        # 임시 파일 생성
        temp_file = os.path.join(self.temp_dir, "test.txt")
        with open(temp_file, "w") as f:
            f.write("This is not an image")

        result = analyze_image(temp_file, "basic")

        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertIn("지원하지 않는 이미지 형식입니다", result["error"])

    def test_save_analysis_result(self):
        """분석 결과 저장 테스트"""
        test_result = {
            "status": "success",
            "analysis_level": "basic",
            "image_path": "test.png",
            "timestamp": datetime.now().isoformat(),
        }

        output_path = os.path.join(self.temp_dir, "test_result.json")
        success = save_analysis_result(test_result, output_path)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))

        # 저장된 파일 내용 확인
        with open(output_path, "r", encoding="utf-8") as f:
            saved_result = json.load(f)

        self.assertEqual(saved_result["status"], "success")
        self.assertEqual(saved_result["analysis_level"], "basic")

    def test_cache_functionality(self):
        """캐시 기능 테스트"""
        if not os.path.exists(self.test_image_path):
            self.skipTest(f"테스트 이미지가 존재하지 않습니다: {self.test_image_path}")

        # 첫 번째 분석
        result1 = analyze_image(self.test_image_path, "basic")
        self.assertEqual(result1["status"], "success")

        # 두 번째 분석 (캐시 사용)
        result2 = analyze_image(self.test_image_path, "basic")
        self.assertEqual(result2["status"], "success")

        # 결과가 동일한지 확인
        self.assertEqual(result1["timestamp"], result2["timestamp"])

    def test_file_size_categorization(self):
        """파일 크기 분류 테스트"""
        # 매우 작은 파일
        self.assertEqual(self.image_processor._categorize_file_size(0.5), "very_small")

        # 작은 파일
        self.assertEqual(self.image_processor._categorize_file_size(2.0), "small")

        # 중간 파일
        self.assertEqual(self.image_processor._categorize_file_size(7.0), "medium")

        # 중간-큰 파일
        self.assertEqual(
            self.image_processor._categorize_file_size(15.0), "medium_large"
        )

        # 큰 파일
        self.assertEqual(self.image_processor._categorize_file_size(25.0), "large")

        # 매우 큰 파일
        self.assertEqual(self.image_processor._categorize_file_size(60.0), "very_large")

    def test_recommendations_generation(self):
        """권장사항 생성 테스트"""
        metadata = {"file_size_mb": 25.0}
        basic_result = {"quality_estimate": "very_low"}

        recommendations = self.image_processor._generate_recommendations(
            metadata, basic_result
        )

        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

        # 대용량 파일 권장사항 확인
        self.assertTrue(any("압축" in rec for rec in recommendations))

        # 낮은 품질 권장사항 확인
        self.assertTrue(any("품질" in rec for rec in recommendations))


if __name__ == "__main__":
    main()
