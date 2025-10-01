import * as vscode from 'vscode';
import { ConversationCapture } from './conversationCapture';
import { DuRiLearningManager } from './learningManager';
import { DuRiAPI } from './duriAPI';

export function activate(context: vscode.ExtensionContext) {
    console.log('DuRi 통합 학습 확장 프로그램이 활성화되었습니다.');

    // DuRi API 클라이언트 초기화
    const duriAPI = new DuRiAPI();

    // 학습 매니저 초기화
    const learningManager = new DuRiLearningManager(duriAPI);

    // 대화 캡처 시스템 초기화
    const conversationCapture = new ConversationCapture(learningManager);

    // 명령어 등록
    let startCaptureCommand = vscode.commands.registerCommand('duri.startCapture', () => {
        conversationCapture.start();
        vscode.window.showInformationMessage('DuRi 통합 대화 캡처가 시작되었습니다.');
    });

    let stopCaptureCommand = vscode.commands.registerCommand('duri.stopCapture', () => {
        conversationCapture.stop();
        vscode.window.showInformationMessage('DuRi 통합 대화 캡처가 중지되었습니다.');
    });

    let testUnifiedSystemCommand = vscode.commands.registerCommand('duri.testUnifiedSystem', async () => {
        try {
            const result = await duriAPI.testUnifiedSystem();
            if (result) {
                vscode.window.showInformationMessage(`DuRi 통합 시스템 테스트 성공! 점수: ${result.integrated_score}`);
            } else {
                vscode.window.showErrorMessage('DuRi 통합 시스템 테스트 실패');
            }
        } catch (error) {
            vscode.window.showErrorMessage('DuRi 통합 시스템 테스트 중 오류 발생');
        }
    });

    let getUnifiedStatisticsCommand = vscode.commands.registerCommand('duri.getUnifiedStatistics', async () => {
        try {
            const stats = await duriAPI.getUnifiedStatistics();
            if (stats) {
                vscode.window.showInformationMessage(`DuRi 통합 시스템 통계: ${JSON.stringify(stats)}`);
            } else {
                vscode.window.showErrorMessage('DuRi 통합 시스템 통계 조회 실패');
            }
        } catch (error) {
            vscode.window.showErrorMessage('DuRi 통합 시스템 통계 조회 중 오류 발생');
        }
    });

    let getUnifiedHistoryCommand = vscode.commands.registerCommand('duri.getUnifiedHistory', async () => {
        try {
            const history = await duriAPI.getUnifiedHistory(10);
            if (history) {
                vscode.window.showInformationMessage(`DuRi 통합 시스템 히스토리: ${JSON.stringify(history)}`);
            } else {
                vscode.window.showErrorMessage('DuRi 통합 시스템 히스토리 조회 실패');
            }
        } catch (error) {
            vscode.window.showErrorMessage('DuRi 통합 시스템 히스토리 조회 중 오류 발생');
        }
    });

    // 자동 시작 (옵션)
    const config = vscode.workspace.getConfiguration('duri');
    const autoStart = config.get('autoStartCapture', false);

    if (autoStart) {
        // 잠시 후 자동 시작
        setTimeout(() => {
            conversationCapture.start();
            vscode.window.showInformationMessage('DuRi 통합 대화 캡처가 자동으로 시작되었습니다.');
        }, 2000);
    }

    // 컨텍스트에 명령어 추가
    context.subscriptions.push(
        startCaptureCommand,
        stopCaptureCommand,
        testUnifiedSystemCommand,
        getUnifiedStatisticsCommand,
        getUnifiedHistoryCommand
    );
}

export function deactivate() {
    console.log('DuRi 통합 학습 확장 프로그램이 비활성화되었습니다.');
}
