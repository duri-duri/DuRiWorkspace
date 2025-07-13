#!/bin/bash
set -e
echo "📡 PostgreSQL 연결 가능 여부 확인 중..."
until pg_isready -h duri-postgres -p 5432; do
  echo "⏳ PostgreSQL 준비 중..."
  sleep 1
done
echo "✅ PostgreSQL 연결 확인됨. 서버 시작 중..."
exec python run.py
