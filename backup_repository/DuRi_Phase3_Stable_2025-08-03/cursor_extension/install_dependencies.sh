#!/bin/bash

echo "Node.js와 npm 설치 중..."
sudo apt update
sudo apt install -y nodejs npm

echo "Node.js 버전 확인..."
node --version
npm --version

echo "의존성 설치 중..."
npm install

echo "TypeScript 컴파일 중..."
npm run compile

echo "설치 완료!" 