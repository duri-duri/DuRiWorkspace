#!/usr/bin/env python3
"""
이미지 처리 및 분석 유틸리티
"""

import argparse
from datetime import datetime
import hashlib
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ImageProcessor:
    """이미지 처리 및 분석 클래스"""

    def __init__(self):
        self.supported_formats = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"]
        self.analysis_cache = {}

    def analyze_image(
        self, image_path: str, analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        이미지 분석 함수

        Args:
            image_path: 분석할 이미지 파일 경로
            analysis_type: 분석 타입 ("comprehensive", "basic", "metadata")

        Returns:
            이미지 분석 결과
        """
        try:
            # 파일 존재 확인
            if not os.path.exists(image_path):
                return {
                    "status": "error",
                    "error": f"이미지 파일이 존재하지 않습니다: {image_path}",
                    "timestamp": datetime.now().isoformat(),
                }

            # 파일 확장자 확인
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in self.supported_formats:
                return {
                    "status": "error",
                    "error": f"지원하지 않는 이미지 형식입니다: {file_ext}",
                    "timestamp": datetime.now().isoformat(),
                }

            # 캐시 확인
            cache_key = self._generate_cache_key(image_path, analysis_type)
            if cache_key in self.analysis_cache:
                logger.info(f"캐시된 분석 결과 사용: {image_path}")
                return self.analysis_cache[cache_key]

            # 기본 메타데이터 분석
            metadata = self._analyze_metadata(image_path)

            # 분석 타입에 따른 처리
            if analysis_type == "comprehensive":
                analysis_result = self._comprehensive_analysis(image_path, metadata)
            elif analysis_type == "basic":
                analysis_result = self._basic_analysis(image_path, metadata)
            elif analysis_type == "metadata":
                analysis_result = self._metadata_only_analysis(metadata)
            else:
                analysis_result = self._basic_analysis(image_path, metadata)

            # 결과에 공통 정보 추가
            analysis_result.update(
                {
                    "image_path": image_path,
                    "analysis_type": analysis_type,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                }
            )

            # 캐시에 저장
            self.analysis_cache[cache_key] = analysis_result

            logger.info(f"이미지 분석 완료: {image_path} ({analysis_type})")
            return analysis_result

        except Exception as e:
            logger.error(f"이미지 분석 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "image_path": image_path,
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_cache_key(self, image_path: str, analysis_type: str) -> str:
        """캐시 키 생성"""
        content = f"{image_path}_{analysis_type}_{os.path.getmtime(image_path)}"
        return hashlib.md5(content.encode()).hexdigest()

    def _analyze_metadata(self, image_path: str) -> Dict[str, Any]:
        """이미지 메타데이터 분석"""
        try:
            stat_info = os.stat(image_path)

            metadata = {
                "file_size": stat_info.st_size,
                "file_size_mb": round(stat_info.st_size / (1024 * 1024), 2),
                "created_time": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "file_name": os.path.basename(image_path),
                "file_extension": os.path.splitext(image_path)[1].lower(),
                "file_path": image_path,
            }

            return metadata

        except Exception as e:
            logger.error(f"메타데이터 분석 실패: {e}")
            return {"error": str(e)}

    def _basic_analysis(
        self, image_path: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """기본 이미지 분석"""
        try:
            # 파일 크기 기반 분석
            file_size_mb = metadata.get("file_size_mb", 0)

            # 파일 크기에 따른 품질 추정
            if file_size_mb > 10:
                quality_estimate = "high"
            elif file_size_mb > 5:
                quality_estimate = "medium"
            elif file_size_mb > 1:
                quality_estimate = "low"
            else:
                quality_estimate = "very_low"

            return {
                "analysis_level": "basic",
                "quality_estimate": quality_estimate,
                "file_size_category": self._categorize_file_size(file_size_mb),
                "metadata": metadata,
            }

        except Exception as e:
            logger.error(f"기본 분석 실패: {e}")
            return {"error": str(e)}

    def _comprehensive_analysis(
        self, image_path: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """종합 이미지 분석"""
        try:
            # 기본 분석 결과
            basic_result = self._basic_analysis(image_path, metadata)

            # 추가 분석 정보
            comprehensive_result = {
                "analysis_level": "comprehensive",
                "basic_analysis": basic_result,
                "image_characteristics": {
                    "format": metadata.get("file_extension", ""),
                    "size_category": basic_result.get("file_size_category", "unknown"),
                    "quality_estimate": basic_result.get("quality_estimate", "unknown"),
                },
                "processing_recommendations": self._generate_recommendations(
                    metadata, basic_result
                ),
                "metadata": metadata,
            }

            return comprehensive_result

        except Exception as e:
            logger.error(f"종합 분석 실패: {e}")
            return {"error": str(e)}

    def _metadata_only_analysis(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """메타데이터만 분석"""
        return {"analysis_level": "metadata_only", "metadata": metadata}

    def _categorize_file_size(self, file_size_mb: float) -> str:
        """파일 크기 분류"""
        if file_size_mb > 50:
            return "very_large"
        elif file_size_mb > 20:
            return "large"
        elif file_size_mb > 10:
            return "medium_large"
        elif file_size_mb > 5:
            return "medium"
        elif file_size_mb > 1:
            return "small"
        else:
            return "very_small"

    def _generate_recommendations(
        self, metadata: Dict[str, Any], basic_result: Dict[str, Any]
    ) -> List[str]:
        """처리 권장사항 생성"""
        recommendations = []

        file_size_mb = metadata.get("file_size_mb", 0)
        quality_estimate = basic_result.get("quality_estimate", "unknown")

        if file_size_mb > 20:
            recommendations.append("대용량 파일이므로 압축을 고려하세요")

        if quality_estimate == "very_low":
            recommendations.append("이미지 품질이 낮으므로 고해상도 버전을 사용하세요")

        if not recommendations:
            recommendations.append("현재 이미지가 적절한 상태입니다")

        return recommendations


# 전역 인스턴스 생성
image_processor = ImageProcessor()


def analyze_image(
    image_path: str, analysis_type: str = "comprehensive"
) -> Dict[str, Any]:
    """
    이미지 분석 함수 (전역 함수)

    Args:
        image_path: 분석할 이미지 파일 경로
        analysis_type: 분석 타입 ("comprehensive", "basic", "metadata")

    Returns:
        이미지 분석 결과
    """
    return image_processor.analyze_image(image_path, analysis_type)


def save_analysis_result(result: Dict[str, Any], output_path: str) -> bool:
    """
    분석 결과를 JSON 파일로 저장

    Args:
        result: 분석 결과
        output_path: 저장할 파일 경로

    Returns:
        저장 성공 여부
    """
    try:
        # 디렉토리 생성 (경로가 있는 경우에만)
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # JSON 파일로 저장
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"분석 결과 저장 완료: {output_path}")
        return True

    except Exception as e:
        logger.error(f"분석 결과 저장 실패: {e}")
        return False


def main():
    """CLI 메인 함수"""
    parser = argparse.ArgumentParser(
        description="이미지 분석 유틸리티",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python image_processor.py --image_path resources/images/test.png --mode comprehensive
  python image_processor.py --image_path test.png --mode metadata --output result.json
  python image_processor.py --image_path test.png --mode basic --refresh-cache
        """,
    )

    parser.add_argument(
        "--image_path", "-i", required=True, help="분석할 이미지 파일 경로"
    )

    parser.add_argument(
        "--mode",
        "-m",
        choices=["basic", "metadata", "comprehensive"],
        default="comprehensive",
        help="분석 모드 (기본값: comprehensive)",
    )

    parser.add_argument("--output", "-o", help="결과를 저장할 JSON 파일 경로")

    parser.add_argument(
        "--refresh-cache", action="store_true", help="캐시를 무시하고 재분석"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="상세 출력")

    args = parser.parse_args()

    # 로깅 설정
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    print(f"🔍 이미지 분석 시작: {args.image_path}")
    print(f"📊 분석 모드: {args.mode}")

    # 캐시 무시 옵션 처리
    if args.refresh_cache:
        image_processor.analysis_cache.clear()
        print("🔄 캐시 무시하고 재분석합니다.")

    # 이미지 분석 실행
    result = analyze_image(args.image_path, args.mode)

    # 결과 출력
    if result.get("status") == "success":
        print(f"✅ 분석 완료!")
        print(f"📁 파일: {result.get('image_path')}")
        print(f"📊 분석 레벨: {result.get('analysis_level', 'unknown')}")

        if args.mode == "comprehensive":
            basic_analysis = result.get("basic_analysis", {})
            quality = basic_analysis.get("quality_estimate", "unknown")
            size_category = basic_analysis.get("file_size_category", "unknown")
            print(f"🎯 품질 추정: {quality}")
            print(f"📏 크기 분류: {size_category}")

        # JSON 파일로 저장
        if args.output:
            if save_analysis_result(result, args.output):
                print(f"💾 결과 저장됨: {args.output}")
            else:
                print(f"❌ 결과 저장 실패: {args.output}")

        # 상세 출력
        if args.verbose:
            print("\n📋 상세 결과:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        print(f"❌ 분석 실패: {result.get('error', '알 수 없는 오류')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
