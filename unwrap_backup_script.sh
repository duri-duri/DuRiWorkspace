#!/bin/bash
F="$1"
echo "테스트 파일: $F"
mkdir -p /tmp/test_result
if file -b "$F" | grep -q "gzip compressed"; then
  echo "gzip 압축 파일 발견"
  tar -xzf "$F" -C /tmp/test_result
  echo "언랩 성공!"
  ls /tmp/test_result
else
  echo "압축되지 않은 파일"
  tar -xf "$F" -C /tmp/test_result
  echo "언랩 성공!"
  ls /tmp/test_result
fi
