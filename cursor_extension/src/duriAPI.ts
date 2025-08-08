import axios, { AxiosResponse } from 'axios';
import * as vscode from 'vscode';

export interface ConversationData {
    speaker: string;
    content: string;
    context?: {
        source: string;
        [key: string]: any;
    };
}

export interface UnifiedConversationRequest {
    user_input: string;
    duri_response: string;
    metadata?: {
        source: string;
        session_id?: string;
        user_id?: string;
        [key: string]: any;
    };
}

export interface UnifiedConversationResponse {
    status: string;
    conversation_id: string;
    integrated_score: number;
    improvement_suggestions: string[];
    processing_time: number;
    timestamp: string;
    analysis: {
        meaning: any;
        context: any;
        emotion: any;
    };
    evaluation: {
        chatgpt: any;
        result: any;
        self_reflection: any;
    };
    learning: {
        autonomous: any;
        realtime: any;
    };
}

export interface DuRiResponse {
    success: boolean;
    package_id?: string;
    summary?: string;
    learning_value?: number;
    reason?: string;
}

export interface AdaptiveLearningRequest {
    user: string;
    cursor: string;
    context?: any;
}

export interface AdaptiveLearningResponse {
    success: boolean;
    selected_format: string;
    learning_result: any;
    efficiency_metrics: {
        response_accuracy: number;
        application_power: number;
        reproducibility: number;
        learning_speed: number;
        overall_score: number;
    };
    exploration_rate: number;
    optimal_format: string;
    reason: string;
}

export class DuRiAPI {
    private baseUrl: string;

    constructor() {
        const config = vscode.workspace.getConfiguration('duri');
        this.baseUrl = config.get('apiUrl', 'http://localhost:8090'); // Core Node
    }

    /**
     * DuRi 통합 시스템 API 서버 상태 확인
     */
    async checkHealth(): Promise<boolean> {
        try {
            const response = await axios.get(`${this.baseUrl}/`);
            return response.status === 200;
        } catch (error) {
            console.error('DuRi 통합 시스템 API 서버 연결 실패:', error);
            return false;
        }
    }

    /**
     * 통합 대화 처리 시스템에 대화 전송
     */
    async sendUnifiedConversation(data: UnifiedConversationRequest): Promise<UnifiedConversationResponse | null> {
        try {
            const response: AxiosResponse<UnifiedConversationResponse> = await axios.post(
                `${this.baseUrl}/conversation/process`,
                data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (response.data.status === 'success') {
                console.log('DuRi 통합 학습 성공:', response.data);
                return response.data;
            } else {
                console.error('DuRi 통합 학습 실패:', response.data);
                return null;
            }
        } catch (error) {
            console.error('DuRi 통합 API 호출 실패:', error);
            return null;
        }
    }

    /**
     * 통합 시스템 테스트
     */
    async testUnifiedSystem(): Promise<UnifiedConversationResponse | null> {
        try {
            const response: AxiosResponse<UnifiedConversationResponse> = await axios.post(
                `${this.baseUrl}/conversation/test`,
                {},
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (response.data.status === 'success') {
                console.log('DuRi 통합 시스템 테스트 성공:', response.data);
                return response.data;
            } else {
                console.error('DuRi 통합 시스템 테스트 실패:', response.data);
                return null;
            }
        } catch (error) {
            console.error('DuRi 통합 시스템 테스트 API 호출 실패:', error);
            return null;
        }
    }

    /**
     * 통합 시스템 통계 조회
     */
    async getUnifiedStatistics(): Promise<any> {
        try {
            const response = await axios.get(`${this.baseUrl}/conversation/statistics`);
            return response.data;
        } catch (error) {
            console.error('통합 시스템 통계 조회 실패:', error);
            return null;
        }
    }

    /**
     * 통합 시스템 히스토리 조회
     */
    async getUnifiedHistory(limit: number = 10): Promise<any> {
        try {
            const response = await axios.get(`${this.baseUrl}/conversation/history?limit=${limit}`);
            return response.data;
        } catch (error) {
            console.error('통합 시스템 히스토리 조회 실패:', error);
            return null;
        }
    }

    /**
     * 대화를 DuRi에게 전송 (기존 호환성)
     */
    async sendConversation(data: ConversationData): Promise<DuRiResponse | null> {
        try {
            // 기존 API 호환성을 위한 변환
            const unifiedData: UnifiedConversationRequest = {
                user_input: data.content,
                duri_response: data.content, // 임시로 동일하게 설정
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
            } else {
                return {
                    success: false,
                    reason: '통합 시스템 처리 실패'
                };
            }
        } catch (error) {
            console.error('DuRi 학습 실패:', error);
            return null;
        }
    }

    /**
     * 적응적 학습으로 대화 전송 (기존 호환성)
     */
    async sendAdaptiveLearningRequest(data: AdaptiveLearningRequest): Promise<AdaptiveLearningResponse | null> {
        try {
            const unifiedData: UnifiedConversationRequest = {
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
            } else {
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
        } catch (error) {
            console.error('DuRi 적응적 학습 API 호출 실패:', error);
            return null;
        }
    }

    /**
     * 특정 형식으로 테스트 (기존 호환성)
     */
    async testSpecificFormat(formatType: string, data: AdaptiveLearningRequest): Promise<AdaptiveLearningResponse | null> {
        return this.sendAdaptiveLearningRequest(data);
    }

    /**
     * 적응적 학습 시스템 상태 조회 (기존 호환성)
     */
    async getAdaptiveSystemStatus(): Promise<any> {
        return this.getUnifiedStatistics();
    }

    /**
     * 적응적 학습 성능 지표 조회 (기존 호환성)
     */
    async getAdaptivePerformanceMetrics(): Promise<any> {
        return this.getUnifiedStatistics();
    }

    /**
     * 적응적 학습 사용 가능한 형식 조회 (기존 호환성)
     */
    async getAdaptiveFormats(): Promise<any> {
        return {
            formats: ['unified'],
            default_format: 'unified'
        };
    }

    /**
     * 메모리 시스템 상태 확인 (기존 호환성)
     */
    async getMemoryStatus(): Promise<any> {
        return this.getUnifiedStatistics();
    }

    /**
     * API 서버 URL 업데이트
     */
    updateBaseUrl(newUrl: string): void {
        this.baseUrl = newUrl;
    }
} 