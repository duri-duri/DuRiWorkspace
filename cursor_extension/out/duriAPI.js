"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DuRiAPI = void 0;
const axios_1 = require("axios");
const vscode = require("vscode");
class DuRiAPI {
    constructor() {
        const config = vscode.workspace.getConfiguration('duri');
        this.baseUrl = config.get('apiUrl', 'http://localhost:8090'); // Core Node
    }
    /**
     * DuRi 통합 시스템 API 서버 상태 확인
     */
    async checkHealth() {
        try {
            const response = await axios_1.default.get(`${this.baseUrl}/`);
            return response.status === 200;
        }
        catch (error) {
            console.error('DuRi 통합 시스템 API 서버 연결 실패:', error);
            return false;
        }
    }
    /**
     * 통합 대화 처리 시스템에 대화 전송
     */
    async sendUnifiedConversation(data) {
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/conversation/process`, data, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (response.data.status === 'success') {
                console.log('DuRi 통합 학습 성공:', response.data);
                return response.data;
            }
            else {
                console.error('DuRi 통합 학습 실패:', response.data);
                return null;
            }
        }
        catch (error) {
            console.error('DuRi 통합 API 호출 실패:', error);
            return null;
        }
    }
    /**
     * 통합 시스템 테스트
     */
    async testUnifiedSystem() {
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/conversation/test`, {}, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (response.data.status === 'success') {
                console.log('DuRi 통합 시스템 테스트 성공:', response.data);
                return response.data;
            }
            else {
                console.error('DuRi 통합 시스템 테스트 실패:', response.data);
                return null;
            }
        }
        catch (error) {
            console.error('DuRi 통합 시스템 테스트 API 호출 실패:', error);
            return null;
        }
    }
    /**
     * 통합 시스템 통계 조회
     */
    async getUnifiedStatistics() {
        try {
            const response = await axios_1.default.get(`${this.baseUrl}/conversation/statistics`);
            return response.data;
        }
        catch (error) {
            console.error('통합 시스템 통계 조회 실패:', error);
            return null;
        }
    }
    /**
     * 통합 시스템 히스토리 조회
     */
    async getUnifiedHistory(limit = 10) {
        try {
            const response = await axios_1.default.get(`${this.baseUrl}/conversation/history?limit=${limit}`);
            return response.data;
        }
        catch (error) {
            console.error('통합 시스템 히스토리 조회 실패:', error);
            return null;
        }
    }
    /**
     * 대화를 DuRi에게 전송 (기존 호환성)
     */
    async sendConversation(data) {
        try {
            // 기존 API 호환성을 위한 변환
            const unifiedData = {
                user_input: data.content,
                duri_response: data.content,
                metadata: {
                    source: data.context?.source || 'cursor_extension',
                    speaker: data.speaker
                }
            };
            const result = await this.sendUnifiedConversation(unifiedData);
            if (result) {
                return {
                    success: true,
                    package_id: result.conversation_id,
                    summary: `통합 점수: ${result.integrated_score}`,
                    learning_value: result.integrated_score
                };
            }
            else {
                return {
                    success: false,
                    reason: '통합 시스템 처리 실패'
                };
            }
        }
        catch (error) {
            console.error('DuRi 학습 실패:', error);
            return null;
        }
    }
    /**
     * 적응적 학습으로 대화 전송 (기존 호환성)
     */
    async sendAdaptiveLearningRequest(data) {
        try {
            const unifiedData = {
                user_input: data.user,
                duri_response: data.cursor,
                metadata: {
                    source: 'adaptive_learning',
                    context: data.context
                }
            };
            const result = await this.sendUnifiedConversation(unifiedData);
            if (result) {
                return {
                    success: true,
                    selected_format: 'unified',
                    learning_result: result,
                    efficiency_metrics: {
                        response_accuracy: result.integrated_score,
                        application_power: result.integrated_score,
                        reproducibility: result.integrated_score,
                        learning_speed: result.integrated_score,
                        overall_score: result.integrated_score
                    },
                    exploration_rate: 0.1,
                    optimal_format: 'unified',
                    reason: '통합 시스템으로 처리됨'
                };
            }
            else {
                return {
                    success: false,
                    selected_format: 'none',
                    learning_result: null,
                    efficiency_metrics: {
                        response_accuracy: 0,
                        application_power: 0,
                        reproducibility: 0,
                        learning_speed: 0,
                        overall_score: 0
                    },
                    exploration_rate: 0,
                    optimal_format: 'none',
                    reason: '통합 시스템 처리 실패'
                };
            }
        }
        catch (error) {
            console.error('DuRi 적응적 학습 API 호출 실패:', error);
            return null;
        }
    }
    /**
     * 특정 형식으로 테스트 (기존 호환성)
     */
    async testSpecificFormat(formatType, data) {
        return this.sendAdaptiveLearningRequest(data);
    }
    /**
     * 적응적 학습 시스템 상태 조회 (기존 호환성)
     */
    async getAdaptiveSystemStatus() {
        return this.getUnifiedStatistics();
    }
    /**
     * 적응적 학습 성능 지표 조회 (기존 호환성)
     */
    async getAdaptivePerformanceMetrics() {
        return this.getUnifiedStatistics();
    }
    /**
     * 적응적 학습 사용 가능한 형식 조회 (기존 호환성)
     */
    async getAdaptiveFormats() {
        return {
            formats: ['unified'],
            default_format: 'unified'
        };
    }
    /**
     * 메모리 시스템 상태 확인 (기존 호환성)
     */
    async getMemoryStatus() {
        return this.getUnifiedStatistics();
    }
    /**
     * API 서버 URL 업데이트
     */
    updateBaseUrl(newUrl) {
        this.baseUrl = newUrl;
    }
}
exports.DuRiAPI = DuRiAPI;
//# sourceMappingURL=duriAPI.js.map
