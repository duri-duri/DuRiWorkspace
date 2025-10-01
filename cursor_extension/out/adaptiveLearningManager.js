"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AdaptiveLearningManager = void 0;
const vscode = require("vscode");
class AdaptiveLearningManager {
    constructor(apiClient) {
        this.isAdaptiveLearning = false;
        this.currentOptimalFormat = 'summary';
        this.explorationRate = 0.3;
        this.apiClient = apiClient;
    }
    /**
     * 적응적 학습 시작
     */
    async startAdaptiveLearning() {
        // API 서버 상태 확인
        const isHealthy = await this.apiClient.checkHealth();
        if (!isHealthy) {
            vscode.window.showErrorMessage('DuRi API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
            return;
        }
        this.isAdaptiveLearning = true;
        console.log('DuRi 적응적 학습이 시작되었습니다.');
        // 시스템 상태 조회
        await this.updateSystemStatus();
    }
    /**
     * 적응적 학습 중지
     */
    stopAdaptiveLearning() {
        this.isAdaptiveLearning = false;
        console.log('DuRi 적응적 학습이 중지되었습니다.');
    }
    /**
     * 적응적 학습으로 대화 전송
     */
    async sendAdaptiveConversation(speaker, content, context) {
        try {
            const response = await this.apiClient.sendAdaptiveLearningRequest({
                user: speaker === 'user' ? content : '',
                cursor: speaker === 'cursor' ? content : '',
                context: context || {}
            });
            if (response && response.success) {
                // 시스템 상태 업데이트
                this.currentOptimalFormat = response.optimal_format;
                this.explorationRate = response.exploration_rate;
                console.log('적응적 학습 성공:', {
                    selected_format: response.selected_format,
                    overall_score: response.efficiency_metrics.overall_score,
                    optimal_format: response.optimal_format
                });
                // 성공 알림
                vscode.window.showInformationMessage(`DuRi 적응적 학습 완료: ${response.selected_format} 형식 (효율성: ${(response.efficiency_metrics.overall_score * 100).toFixed(1)}%)`);
                return response;
            }
            else {
                console.error('적응적 학습 실패:', response);
                vscode.window.showErrorMessage('DuRi 적응적 학습에 실패했습니다.');
                return null;
            }
        }
        catch (error) {
            console.error('적응적 학습 API 호출 오류:', error);
            vscode.window.showErrorMessage('적응적 학습 API 호출 중 오류가 발생했습니다.');
            return null;
        }
    }
    /**
     * 특정 형식으로 테스트
     */
    async testSpecificFormat(formatType, content) {
        try {
            const response = await this.apiClient.testSpecificFormat(formatType, {
                user: content,
                cursor: '테스트 응답'
            });
            if (response && response.success) {
                console.log('형식 테스트 성공:', {
                    format: formatType,
                    overall_score: response.efficiency_metrics.overall_score
                });
                vscode.window.showInformationMessage(`${formatType} 형식 테스트 완료 (효율성: ${(response.efficiency_metrics.overall_score * 100).toFixed(1)}%)`);
                return response;
            }
            else {
                console.error('형식 테스트 실패:', response);
                vscode.window.showErrorMessage('형식 테스트에 실패했습니다.');
                return null;
            }
        }
        catch (error) {
            console.error('형식 테스트 API 호출 오류:', error);
            vscode.window.showErrorMessage('형식 테스트 API 호출 중 오류가 발생했습니다.');
            return null;
        }
    }
    /**
     * 시스템 상태 업데이트
     */
    async updateSystemStatus() {
        try {
            const status = await this.apiClient.getAdaptiveSystemStatus();
            if (status && status.success) {
                this.currentOptimalFormat = status.system_status.current_optimal_format;
                this.explorationRate = status.system_status.exploration_rate;
                console.log('시스템 상태 업데이트:', {
                    optimal_format: this.currentOptimalFormat,
                    exploration_rate: this.explorationRate
                });
            }
        }
        catch (error) {
            console.error('시스템 상태 업데이트 실패:', error);
        }
    }
    /**
     * 성능 지표 조회
     */
    async getPerformanceMetrics() {
        try {
            const metrics = await this.apiClient.getAdaptivePerformanceMetrics();
            if (metrics && metrics.success) {
                console.log('성능 지표 조회 완료:', metrics.performance_metrics);
                return metrics.performance_metrics;
            }
            else {
                console.error('성능 지표 조회 실패:', metrics);
                return null;
            }
        }
        catch (error) {
            console.error('성능 지표 조회 API 호출 오류:', error);
            return null;
        }
    }
    /**
     * 사용 가능한 형식 조회
     */
    async getAvailableFormats() {
        try {
            const formats = await this.apiClient.getAdaptiveFormats();
            if (formats && formats.success) {
                console.log('사용 가능한 형식 조회 완료:', formats.available_formats);
                return formats.available_formats;
            }
            else {
                console.error('형식 조회 실패:', formats);
                return [];
            }
        }
        catch (error) {
            console.error('형식 조회 API 호출 오류:', error);
            return [];
        }
    }
    /**
     * 적응적 학습 상태 확인
     */
    isAdaptiveLearningActive() {
        return this.isAdaptiveLearning;
    }
    /**
     * 현재 최적 형식 조회
     */
    getCurrentOptimalFormat() {
        return this.currentOptimalFormat;
    }
    /**
     * 탐색률 조회
     */
    getExplorationRate() {
        return this.explorationRate;
    }
}
exports.AdaptiveLearningManager = AdaptiveLearningManager;
//# sourceMappingURL=adaptiveLearningManager.js.map
