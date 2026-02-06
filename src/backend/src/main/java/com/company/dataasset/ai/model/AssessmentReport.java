package com.company.dataasset.ai.model;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * AI评估报告
 */
@Data
public class AssessmentReport {

    /**
     * 报告ID
     */
    private String reportId;

    /**
     * 系统ID
     */
    private Long systemId;

    /**
     * 评估提供者名称
     */
    private String providerName;

    /**
     * 评估时间
     */
    private LocalDateTime assessmentTime;

    /**
     * 业务价值评分
     */
    private BigDecimal businessValueScore;

    /**
     * 业务价值详情
     */
    private String businessValueDetail;

    /**
     * 数据质量评分
     */
    private BigDecimal dataQualityScore;

    /**
     * 数据质量详情
     */
    private String dataQualityDetail;

    /**
     * 合规风险评分
     */
    private BigDecimal complianceRiskScore;

    /**
     * 合规风险详情
     */
    private String complianceRiskDetail;

    /**
     * 技术可行性评分
     */
    private BigDecimal technicalFeasibilityScore;

    /**
     * 技术可行性详情
     */
    private String technicalFeasibilityDetail;

    /**
     * 综合评分
     */
    private BigDecimal totalScore;

    /**
     * 评分计算方法
     */
    private String scoringMethod;

    /**
     * 评估建议
     */
    private String recommendation;

    /**
     * 建议优先级
     */
    private String priorityLevel;

    /**
     * 预计投资回报率
     */
    private BigDecimal estimatedRoi;

    /**
     * 预计年收益
     */
    private BigDecimal estimatedAnnualBenefit;

    /**
     * 预计实施成本
     */
    private BigDecimal estimatedImplementationCost;

    /**
     * 预计实施周期（天）
     */
    private Integer estimatedImplementationDays;

    /**
     * 建议的数据产品
     */
    private List<String> suggestedDataProducts;

    /**
     * 风险提示
     */
    private List<String> riskWarnings;

    /**
     * 优势分析
     */
    private List<String> strengths;

    /**
     * 劣势分析
     */
    private List<String> weaknesses;

    /**
     * 机会分析
     */
    private List<String> opportunities;

    /**
     * 威胁分析
     */
    private List<String> threats;

    /**
     * 实施路线图建议
     */
    private String implementationRoadmap;

    /**
     * 关键成功因素
     */
    private List<String> keySuccessFactors;

    /**
     * 评估置信度（0-1）
     */
    private BigDecimal confidence;

    /**
     * 原始响应数据（用于调试）
     */
    private Map<String, Object> rawResponse;

    /**
     * 处理时间（毫秒）
     */
    private Long processingTimeMs;

    /**
     * 令牌使用量
     */
    private Integer tokensUsed;

    /**
     * 成本估算
     */
    private BigDecimal costEstimate;

    /**
     * 版本号
     */
    private String version;
}