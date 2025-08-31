#!/bin/bash

echo "VSIX 패키지 생성 중..."

# 임시 디렉토리 생성
mkdir -p temp_extension

# 필요한 파일들 복사
cp -r out/* temp_extension/
cp package.json temp_extension/
cp README.md temp_extension/

# VSIX 패키지 생성 (tar 사용)
cd temp_extension
tar -czf ../duri-cursor-extension.tar.gz ./*
cd ..

# 정리
rm -rf temp_extension

echo "확장 프로그램 패키지 생성 완료: duri-cursor-extension.tar.gz"
echo "이 파일을 Cursor에서 로드할 수 있습니다." 