#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

// 현재 작업 디렉토리를 프로젝트 루트로 설정
const projectRoot = path.resolve(__dirname, '..');

console.log('🚀 Opening terminal in project directory...');
console.log(`📁 Project root: ${projectRoot}`);

// 터미널 열기
const terminal = spawn('bash', [], {
    cwd: projectRoot,
    stdio: 'inherit',
    shell: true
});

terminal.on('error', (err) => {
    console.error('❌ Failed to open terminal:', err.message);
});

terminal.on('close', (code) => {
    console.log(`✅ Terminal closed with code: ${code}`);
});
