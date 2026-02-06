package com.company.dataasset.ai;

import com.company.dataasset.entity.CustomerSystem;

import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * AI评估提供者接口
 * 定义统一的AI模型评估接口
 */
public interface AssessmentProvider {

    /**
     * 获取提供者名称
     */
    String getProviderName();

    /**
     * 获取提供者描述
     */
    String getProviderDescription();

    /**
     * 获取提供者能力描述
     */
    Map<String, String> getCapabilities();

    /**
     * 评估系统业务价值
     */
    CompletableFuture<BigDecimal> assessBusinessValue(CustomerSystem system);

    /**
     * 评估系统数据质量
     */
    CompletableFuture<BigDecimal> assessDataQuality(CustomerSystem system);

    /**
     * 评估系统合规风险
     */
    CompletableFuture<BigDecimal> assessComplianceRisk(CustomerSystem system);

    /**
     * 评估系统技术可行性
     */
    CompletableFuture<BigDecimal> assessTechnicalFeasibility(CustomerSystem system);

    /**
     * 综合评估（所有维度）
     */
    CompletableFuture<Map<String, Object>> comprehensiveAssessment(CustomerSystem system);

    /**
     * 获取详细评估报告
     */
    CompletableFuture<AssessmentReport> getDetailedReport(CustomerSystem system);

    /**
     * 检查服务可用性
     */
    boolean isAvailable();

    /**
     * 获取服务状态
     */
    ServiceStatus getServiceStatus();

    /**
     * 获取最后一次调用时间
     */
    long getLastCallTimestamp();

    /**
     * 获取调用统计
     */
    CallStatistics getCallStatistics();

    /**
     * 评估提供者权重（用于结果融合）
     */
    default BigDecimal getWeight() {
        return BigDecimal.ONE;
    }

    /**
     * 评估提供者可信度
     */
    default BigDecimal getConfidence() {
        return new BigDecimal("0.8");
    }
}