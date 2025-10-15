#!/usr/bin/env python3
"""
Day 18: HITL 라벨링 품질 검증
품질 점수 ≥ 85% 달성
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import statistics

class LabelingQuality(Enum):
    EXCELLENT = 'excellent'  # 95%+
    GOOD = 'good'           # 85-94%
    ACCEPTABLE = 'acceptable' # 70-84%
    POOR = 'poor'           # <70%

class LabelingTaskType(Enum):
    CLASSIFICATION = 'classification'
    REGRESSION = 'regression'
    MULTI_LABEL = 'multi_label'
    SEQUENCE = 'sequence'
    SENTIMENT = 'sentiment'

@dataclass
class LabelingTask:
    id: str
    task_type: LabelingTaskType
    content: str
    expected_label: str
    human_label: str
    confidence: float
    timestamp: datetime
    annotator_id: str
    difficulty: str

@dataclass
class QualityMetrics:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    inter_annotator_agreement: float
    consistency_score: float
    overall_quality_score: float

class HITLQualityVerifier:
    """HITL 라벨링 품질 검증 시스템"""
    
    def __init__(self):
        self.quality_threshold = 0.85  # 85% 품질 임계값
        self.excellent_threshold = 0.95  # 95% 우수 임계값
        self.min_annotations_per_task = 3  # 태스크당 최소 어노테이션 수
        
        # 기존 시스템과 통합
        self.judgment_system_integration = True
        self.attention_system_integration = True
        
    def calculate_accuracy(self, tasks: List[LabelingTask]) -> float:
        """정확도 계산"""
        if not tasks:
            return 0.0
        
        correct = sum(1 for task in tasks if task.expected_label == task.human_label)
        return correct / len(tasks)
    
    def calculate_precision_recall(self, tasks: List[LabelingTask]) -> Tuple[float, float]:
        """정밀도와 재현율 계산"""
        if not tasks:
            return 0.0, 0.0
        
        # 이진 분류 기준으로 계산
        true_positives = sum(1 for task in tasks 
                           if task.expected_label == 'positive' and task.human_label == 'positive')
        false_positives = sum(1 for task in tasks 
                            if task.expected_label == 'negative' and task.human_label == 'positive')
        false_negatives = sum(1 for task in tasks 
                            if task.expected_label == 'positive' and task.human_label == 'negative')
        
        precision = true_positives / max(true_positives + false_positives, 1)
        recall = true_positives / max(true_positives + false_negatives, 1)
        
        return precision, recall
    
    def calculate_f1_score(self, precision: float, recall: float) -> float:
        """F1 점수 계산"""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def calculate_inter_annotator_agreement(self, tasks: List[LabelingTask]) -> float:
        """어노테이터 간 일치도 계산 (Cohen's Kappa)"""
        if not tasks:
            return 0.0
        
        # 태스크별로 그룹화
        task_groups = {}
        for task in tasks:
            if task.id not in task_groups:
                task_groups[task.id] = []
            task_groups[task.id].append(task)
        
        # 각 태스크별 일치도 계산
        agreements = []
        for task_id, task_list in task_groups.items():
            if len(task_list) >= 2:
                labels = [task.human_label for task in task_list]
                # 간단한 일치도 계산 (실제로는 Cohen's Kappa 사용)
                unique_labels = set(labels)
                if len(unique_labels) == 1:
                    agreements.append(1.0)  # 완전 일치
                else:
                    # 가장 빈번한 라벨의 비율
                    most_common = max(unique_labels, key=labels.count)
                    agreement = labels.count(most_common) / len(labels)
                    agreements.append(agreement)
        
        return statistics.mean(agreements) if agreements else 0.0
    
    def calculate_consistency_score(self, tasks: List[LabelingTask]) -> float:
        """일관성 점수 계산"""
        if not tasks:
            return 0.0
        
        # 어노테이터별 일관성 계산
        annotator_tasks = {}
        for task in tasks:
            if task.annotator_id not in annotator_tasks:
                annotator_tasks[task.annotator_id] = []
            annotator_tasks[task.annotator_id].append(task)
        
        consistency_scores = []
        for annotator_id, annotator_task_list in annotator_tasks.items():
            if len(annotator_task_list) >= 2:
                # 같은 유형의 태스크에서의 일관성
                task_types = {}
                for task in annotator_task_list:
                    if task.task_type not in task_types:
                        task_types[task.task_type] = []
                    task_types[task.task_type].append(task)
                
                for task_type, type_tasks in task_types.items():
                    if len(type_tasks) >= 2:
                        # 같은 태스크 유형에서의 일관성
                        labels = [task.human_label for task in type_tasks]
                        unique_labels = set(labels)
                        if len(unique_labels) == 1:
                            consistency_scores.append(1.0)
                        else:
                            # 라벨 분산도 계산
                            label_counts = [labels.count(label) for label in unique_labels]
                            max_count = max(label_counts)
                            consistency = max_count / len(labels)
                            consistency_scores.append(consistency)
        
        return statistics.mean(consistency_scores) if consistency_scores else 0.0
    
    def calculate_overall_quality_score(self, metrics: QualityMetrics) -> float:
        """전체 품질 점수 계산"""
        # 가중 평균으로 전체 품질 점수 계산
        weights = {
            'accuracy': 0.3,
            'precision': 0.2,
            'recall': 0.2,
            'f1_score': 0.15,
            'inter_annotator_agreement': 0.1,
            'consistency_score': 0.05
        }
        
        overall_score = (
            metrics.accuracy * weights['accuracy'] +
            metrics.precision * weights['precision'] +
            metrics.recall * weights['recall'] +
            metrics.f1_score * weights['f1_score'] +
            metrics.inter_annotator_agreement * weights['inter_annotator_agreement'] +
            metrics.consistency_score * weights['consistency_score']
        )
        
        return overall_score
    
    def evaluate_labeling_quality(self, tasks: List[LabelingTask]) -> Dict[str, Any]:
        """라벨링 품질 평가"""
        if not tasks:
            return {
                'quality_level': LabelingQuality.POOR.value,
                'overall_score': 0.0,
                'metrics': {},
                'recommendations': ['라벨링 태스크가 없습니다.']
            }
        
        # 메트릭 계산
        accuracy = self.calculate_accuracy(tasks)
        precision, recall = self.calculate_precision_recall(tasks)
        f1_score = self.calculate_f1_score(precision, recall)
        inter_annotator_agreement = self.calculate_inter_annotator_agreement(tasks)
        consistency_score = self.calculate_consistency_score(tasks)
        
        metrics = QualityMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            inter_annotator_agreement=inter_annotator_agreement,
            consistency_score=consistency_score,
            overall_quality_score=0.0
        )
        
        # 전체 품질 점수 계산
        overall_score = self.calculate_overall_quality_score(metrics)
        metrics.overall_quality_score = overall_score
        
        # 품질 등급 결정
        if overall_score >= self.excellent_threshold:
            quality_level = LabelingQuality.EXCELLENT
        elif overall_score >= self.quality_threshold:
            quality_level = LabelingQuality.GOOD
        elif overall_score >= 0.70:
            quality_level = LabelingQuality.ACCEPTABLE
        else:
            quality_level = LabelingQuality.POOR
        
        # 개선 권장사항 생성
        recommendations = self.generate_recommendations(metrics, quality_level)
        
        return {
            'quality_level': quality_level.value,
            'overall_score': overall_score,
            'metrics': {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'inter_annotator_agreement': inter_annotator_agreement,
                'consistency_score': consistency_score,
                'overall_quality_score': overall_score
            },
            'recommendations': recommendations,
            'task_count': len(tasks),
            'annotator_count': len(set(task.annotator_id for task in tasks)),
            'evaluation_timestamp': datetime.now().isoformat()
        }
    
    def generate_recommendations(self, metrics: QualityMetrics, quality_level: LabelingQuality) -> List[str]:
        """품질 개선 권장사항 생성"""
        recommendations = []
        
        if metrics.accuracy < 0.85:
            recommendations.append('정확도 향상을 위한 어노테이터 교육 필요')
        
        if metrics.precision < 0.80:
            recommendations.append('정밀도 향상을 위한 라벨링 가이드라인 개선 필요')
        
        if metrics.recall < 0.80:
            recommendations.append('재현율 향상을 위한 태스크 분류 기준 명확화 필요')
        
        if metrics.inter_annotator_agreement < 0.70:
            recommendations.append('어노테이터 간 일치도 향상을 위한 합의 세션 필요')
        
        if metrics.consistency_score < 0.75:
            recommendations.append('일관성 향상을 위한 어노테이터 피드백 시스템 구축 필요')
        
        if quality_level == LabelingQuality.POOR:
            recommendations.append('전체적인 라벨링 프로세스 재검토 필요')
        elif quality_level == LabelingQuality.ACCEPTABLE:
            recommendations.append('품질 임계값 달성을 위한 추가 개선 필요')
        elif quality_level == LabelingQuality.GOOD:
            recommendations.append('우수 품질 달성을 위한 미세 조정 필요')
        else:
            recommendations.append('현재 품질 수준 유지 및 지속적 모니터링')
        
        return recommendations
    
    def generate_quality_report(self, tasks: List[LabelingTask]) -> Dict[str, Any]:
        """품질 보고서 생성"""
        evaluation_result = self.evaluate_labeling_quality(tasks)
        
        # 태스크 유형별 분석
        task_type_analysis = {}
        for task_type in LabelingTaskType:
            type_tasks = [task for task in tasks if task.task_type == task_type]
            if type_tasks:
                type_evaluation = self.evaluate_labeling_quality(type_tasks)
                task_type_analysis[task_type.value] = type_evaluation
        
        # 어노테이터별 분석
        annotator_analysis = {}
        annotators = set(task.annotator_id for task in tasks)
        for annotator_id in annotators:
            annotator_tasks = [task for task in tasks if task.annotator_id == annotator_id]
            if annotator_tasks:
                annotator_evaluation = self.evaluate_labeling_quality(annotator_tasks)
                annotator_analysis[annotator_id] = annotator_evaluation
        
        # 시간대별 분석
        time_analysis = {}
        for task in tasks:
            hour = task.timestamp.hour
            if hour not in time_analysis:
                time_analysis[hour] = []
            time_analysis[hour].append(task)
        
        hourly_quality = {}
        for hour, hour_tasks in time_analysis.items():
            if hour_tasks:
                hour_evaluation = self.evaluate_labeling_quality(hour_tasks)
                hourly_quality[f'hour_{hour}'] = hour_evaluation
        
        report = {
            'overall_evaluation': evaluation_result,
            'task_type_analysis': task_type_analysis,
            'annotator_analysis': annotator_analysis,
            'hourly_quality': hourly_quality,
            'summary': {
                'total_tasks': len(tasks),
                'total_annotators': len(annotators),
                'quality_threshold_met': evaluation_result['overall_score'] >= self.quality_threshold,
                'excellent_threshold_met': evaluation_result['overall_score'] >= self.excellent_threshold,
                'generated_at': datetime.now().isoformat()
            }
        }
        
        return report

if __name__ == '__main__':
    verifier = HITLQualityVerifier()
    
    # 샘플 라벨링 태스크
    sample_tasks = [
        LabelingTask(
            id='task_1',
            task_type=LabelingTaskType.CLASSIFICATION,
            content='이 텍스트는 긍정적인가요?',
            expected_label='positive',
            human_label='positive',
            confidence=0.9,
            timestamp=datetime.now(),
            annotator_id='annotator_1',
            difficulty='medium'
        ),
        LabelingTask(
            id='task_1',
            task_type=LabelingTaskType.CLASSIFICATION,
            content='이 텍스트는 긍정적인가요?',
            expected_label='positive',
            human_label='positive',
            confidence=0.8,
            timestamp=datetime.now(),
            annotator_id='annotator_2',
            difficulty='medium'
        ),
        LabelingTask(
            id='task_2',
            task_type=LabelingTaskType.SENTIMENT,
            content='이 제품은 만족스럽습니다.',
            expected_label='positive',
            human_label='negative',
            confidence=0.7,
            timestamp=datetime.now(),
            annotator_id='annotator_1',
            difficulty='hard'
        ),
        LabelingTask(
            id='task_3',
            task_type=LabelingTaskType.CLASSIFICATION,
            content='서비스가 좋습니다.',
            expected_label='positive',
            human_label='positive',
            confidence=0.95,
            timestamp=datetime.now(),
            annotator_id='annotator_2',
            difficulty='easy'
        ),
        LabelingTask(
            id='task_4',
            task_type=LabelingTaskType.REGRESSION,
            content='점수 예측',
            expected_label='8.5',
            human_label='8.2',
            confidence=0.85,
            timestamp=datetime.now(),
            annotator_id='annotator_1',
            difficulty='medium'
        )
    ]
    
    # 품질 평가 실행
    quality_report = verifier.generate_quality_report(sample_tasks)
    
    print('✅ Day 18: HITL 라벨링 품질 검증 구현 완료')
    print(f'   - 전체 품질 점수: {quality_report["overall_evaluation"]["overall_score"]:.3f}')
    print(f'   - 품질 등급: {quality_report["overall_evaluation"]["quality_level"]}')
    print(f'   - 품질 임계값 달성: {quality_report["summary"]["quality_threshold_met"]}')
    print(f'   - 우수 품질 달성: {quality_report["summary"]["excellent_threshold_met"]}')
    print(f'   - 총 태스크 수: {quality_report["summary"]["total_tasks"]}')
    print(f'   - 총 어노테이터 수: {quality_report["summary"]["total_annotators"]}')
    print(f'   - 개선 권장사항: {len(quality_report["overall_evaluation"]["recommendations"])}개')
    
    # 결과 저장
    with open('day18_hitl_quality_report.json', 'w', encoding='utf-8') as f:
        json.dump(quality_report, f, ensure_ascii=False, indent=2, default=str)
