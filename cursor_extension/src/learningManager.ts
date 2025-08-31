import { DuRiAPI, ConversationData } from './duriAPI';
import * as vscode from 'vscode';

export class DuRiLearningManager {
    private apiClient: DuRiAPI;
    private isLearning: boolean = false;
    private conversationQueue: ConversationData[] = [];

    constructor(apiClient: DuRiAPI) {
        this.apiClient = apiClient;
    }

    /**
     * 자동 학습 시작
     */
    async startLearning(): Promise<void> {
        // API 서버 상태 확인
        const isHealthy = await this.apiClient.checkHealth();
        if (!isHealthy) {
            vscode.window.showErrorMessage('DuRi API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
            return;
        }

        this.isLearning = true;
        console.log('DuRi 자동 학습이 시작되었습니다.');
        
        // 큐에 있는 대화들 처리
        await this.processQueue();
    }

    /**
     * 자동 학습 중지
     */
    stopLearning(): void {
        this.isLearning = false;
        console.log('DuRi 자동 학습이 중지되었습니다.');
    }

    /**
     * 대화 전송
     */
    async sendConversation(speaker: string, content: string, context?: any): Promise<void> {
        const conversationData: ConversationData = {
            speaker,
            content,
            context: context || { source: 'cursor_extension' }
        };

        if (this.isLearning) {
            // 즉시 전송
            await this.sendToDuRi(conversationData);
        } else {
            // 큐에 추가
            this.conversationQueue.push(conversationData);
            console.log('대화가 큐에 추가되었습니다:', content);
        }
    }

    /**
     * DuRi에게 대화 전송
     */
    private async sendToDuRi(data: ConversationData): Promise<void> {
        try {
            const response = await this.apiClient.sendConversation(data);
            
            if (response && response.success) {
                console.log('DuRi 학습 성공:', {
                    package_id: response.package_id,
                    summary: response.summary,
                    learning_value: response.learning_value
                });

                // 성공 알림
                vscode.window.showInformationMessage(
                    `DuRi 학습 완료: ${response.summary} (학습가치: ${response.learning_value})`
                );
            } else {
                console.error('DuRi 학습 실패:', response);
                vscode.window.showErrorMessage('DuRi 학습에 실패했습니다.');
            }
        } catch (error) {
            console.error('DuRi API 호출 오류:', error);
            vscode.window.showErrorMessage('DuRi API 호출 중 오류가 발생했습니다.');
        }
    }

    /**
     * 큐에 있는 대화들 처리
     */
    private async processQueue(): Promise<void> {
        while (this.conversationQueue.length > 0 && this.isLearning) {
            const conversation = this.conversationQueue.shift();
            if (conversation) {
                await this.sendToDuRi(conversation);
                // 처리 간격
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }

    /**
     * 학습 상태 확인
     */
    isLearningActive(): boolean {
        return this.isLearning;
    }

    /**
     * 큐 상태 확인
     */
    getQueueStatus(): { length: number; items: ConversationData[] } {
        return {
            length: this.conversationQueue.length,
            items: [...this.conversationQueue]
        };
    }
} 