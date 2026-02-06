package com.company.dataasset.ai.provider;

import com.company.dataasset.ai.AssessmentProvider;
import com.company.dataasset.ai.model.AssessmentReport;
import com.company.dataasset.ai.model.CallStatistics;
import com.company.dataasset.ai.model.ServiceStatus;
import com.company.dataasset.entity.CustomerSystem;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicLong;

/**
 * DeepSeek AI评估提供者
 * 擅长业务价值评估和综合评分
 */
@Slf4j
@Component
public class DeepSeekAssessmentProvider implements AssessmentProvider {

    private final RestTemplate restTemplate;
    private final AtomicLong callCount = new AtomicLong(0);
    private final AtomicLong successCount = new AtomicLong(0);
    private final AtomicLong errorCount = new AtomicLong(0);
    private volatile long lastCallTimestamp = 0;
    private volatile ServiceStatus serviceStatus = new ServiceStatus();

    @Value("${ai.deepseek.api-key:}")
    private String apiKey;

    @Value("${ai.deepseek.endpoint:https://api.deepseek.com/v1/chat/completions}")
    private String endpoint;

    @Value("${ai.deepseek.model:deepseek-chat}")
    private String model;

    @Value("${ai.deepseek.enabled:true}")
    private boolean enabled;

    public DeepSeekAssessmentProvider(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
        this.serviceStatus.setServiceName("DeepSeek");
        this.serviceStatus.setStatus(ServiceStatus.Status.UP);
        this.serviceStatus.setEnabled(enabled);
        this.serviceStatus.setEndpoint(endpoint);
        this.serviceStatus.setProvider("DeepSeek");
    }

    @Override
    public String getProviderName() {
        return "DeepSeek";
    }

    @Override
    public String getProviderDescription() {
        return "DeepSeek AI模型，擅长业务价值评估和综合评分分析";
    }

    @Override
    public Map<String, String> getCapabilities() {
        return Map.of(
            "business_value", "优秀",
            "data_quality", "良好", 
            "compliance_risk", "中等",
            "technical_feasibility", "良好",
            "comprehensive", "优秀"
        );
    }

    @Override
    public CompletableFuture<BigDecimal> assessBusinessValue(CustomerSystem system) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                callCount.incrementAndGet();
                lastCallTimestamp = System.currentTimeMillis();

                // 构建评估提示
                String prompt = buildBusinessValuePrompt(system);

                // 调用DeepSeek API
                Map<String, Object> request = buildRequest(prompt);
                Map<String, Object> response = callDeepSeekAPI(request);

                // 解析评分
                BigDecimal score = parseBusinessValueScore(response);
                
                successCount.incrementAndGet();
                return score;

            } catch (Exception e) {
                errorCount.incrementAndGet();
                log.error("DeepSeek业务价值评估失败: {}", system.getSystemName(), e);
                return BigDecimal.ZERO;
            }
        });
    }

    @Override
    public CompletableFuture<BigDecimal> assessDataQuality(CustomerSystem system) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                callCount.incrementAndGet();
                lastCallTimestamp = System.currentTimeMillis();

                String prompt = buildDataQualityPrompt(system);
                Map<String, Object> request = buildRequest(prompt);
                Map<String, Object> response = callDeepSeekAPI(request);

                BigDecimal score = parseDataQualityScore(response);
                successCount.incrementAndGet();
                return score;

            } catch (Exception e) {
                errorCount.incrementAndGet();
                log.error("DeepSeek数据质量评估失败: {}", system.getSystemName(), e);
                return BigDecimal.ZERO;
            }
        });
    }

    @Override
    public CompletableFuture<BigDecimal> assessComplianceRisk(CustomerSystem system) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                callCount.incrementAndGet();
                lastCallTimestamp = System.currentTimeMillis();

                String prompt = buildComplianceRiskPrompt(system);
                Map<String, Object> request = buildRequest(prompt);
                Map<String, Object> response = callDeepSeekAPI(request);

                BigDecimal score = parseComplianceRiskScore(response);
                successCount.incrementAndGet();
                return score;

            } catch (Exception e) {
                errorCount.incrementAndGet();
                log.error("DeepSeek合规风险评估失败: {}", system.getSystemName(), e);
                return BigDecimal.ZERO;
            }
        });
    }

    @Override
    public CompletableFuture<BigDecimal> assessTechnicalFeasibility(CustomerSystem system) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                callCount.incrementAndGet();
                lastCallTimestamp = System.currentTimeMillis();

                String prompt = buildTechnicalFeasibilityPrompt(system);
                Map<String, Object> request = buildRequest(prompt);
                Map<String, Object> response = callDeepSeekAPI(request);

                BigDecimal score = parseTechnicalFeasibilityScore(response);
                successCount.incrementAndGet();
                return score;

            } catch (Exception e) {
                errorCount.incrementAndGet();
                log.error("DeepSeek技术可行性评估失败: {}", system.getSystemName(), e);
                return BigDecimal.ZERO;
            }
        });
    }

    @Override
    public CompletableFuture<Map<String, Object>> comprehensiveAssessment(CustomerSystem system) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                callCount.incrementAndGet();
                lastCallTimestamp = System.currentTimeMillis();

                String prompt = buildComprehensivePrompt(system);
                Map<String, Object> request = buildRequest(prompt);
                Map<String, Object> response = callDeepSeekAPI(request);

                Map<String, Object> result = parseComprehensiveResult(response);
                successCount.incrementAndGet();
                return result;

            } catch (Exception e) {
                errorCount.incrementAndGet();
                log.error("DeepSeek综合评估失败: {}", system.getSystemName(), e);
                return Map.of("error", e.getMessage());
            }
        });
    }

    @Override
    public CompletableFuture<AssessmentReport> getDetailedReport(CustomerSystem system) {
        return comprehensiveAssessment(system)
            .thenApply(result -> {
                AssessmentReport report = new AssessmentReport();
                report.setReportId("DEEPSEEK_" + System.currentTimeMillis());
                report.setSystemId(system.getId());
                report.setProviderName(getProviderName());
                report.setAssessmentTime(LocalDateTime.now());
                
                // 从结果中提取评分
                if (result.containsKey("business_value_score")) {
                    report.setBusinessValueScore(new BigDecimal(result.get("business_value_score").toString()));
                }
                if (result.containsKey("data_quality_score")) {
                    report.setDataQualityScore(new BigDecimal(result.get("data_quality_score").toString()));
                }
                if (result.containsKey("compliance_risk_score")) {
                    report.setComplianceRiskScore(new BigDecimal(result.get("compliance_risk_score").toString()));
                }
                if (result.containsKey("technical_feasibility_score")) {
                    report.setTechnicalFeasibilityScore(new BigDecimal(result.get("technical_feasibility_score").toString()));
                }
                if (result.containsKey("total_score")) {
                    report.setTotalScore(new BigDecimal(result.get("total_score").toString()));
                }
                
                report.setRawResponse(result);
                report.setConfidence(new BigDecimal("0.85"));
                return report;
            });
    }

    @Override
    public boolean isAvailable() {
        return enabled && serviceStatus.getStatus() == ServiceStatus.Status.UP;
    }

    @Override
    public ServiceStatus getServiceStatus() {
        serviceStatus.setLastCheckTime(LocalDateTime.now());
        return serviceStatus;
    }

    @Override
    public long getLastCallTimestamp() {
        return lastCallTimestamp;
    }

    @Override
    public CallStatistics getCallStatistics() {
        CallStatistics stats = new CallStatistics();
        stats.setTotalCalls(callCount.get());
        stats.setSuccessfulCalls(successCount.get());
        stats.setFailedCalls(errorCount.get());
        stats.setSuccessRate(successCount.get() * 1.0 / Math.max(callCount.get(), 1));
        return stats;
    }

    @Override
    public BigDecimal getWeight() {
        return new BigDecimal("0.35"); // DeepSeek权重
    }

    @Override
    public BigDecimal getConfidence() {
        return new BigDecimal("0.85"); // DeepSeek可信度
    }

    // ========== 私有方法 ==========

    private String buildBusinessValuePrompt(CustomerSystem system) {
        return String.format("""
            请评估以下系统的业务价值，给出0-100的评分：
            
            系统名称：%s
            系统类型：%s
            业务领域：%s
            业务关键性：%d/5
            用户数量：%d
            日均交易量：%d
            年交易金额：%s
            
            请考虑以下因素：
            1. 业务重要性
            2. 用户影响范围
            3. 交易规模
            4. 收入贡献
            5. 战略价值
            
            请只返回一个0-100的整数评分。
            """,
            system.getSystemName(),
            system.getSystemType(),
            system.getBusinessDomain(),
            system.getBusinessCriticality(),
            system.getUserCount(),
            system.getDailyTransactionVolume(),
            system.getAnnualTransactionAmount()
        );
    }

    private String buildDataQualityPrompt(CustomerSystem system) {
        return String.format("""
            请评估以下系统的数据质量，给出0-100的评分：
            
            系统名称：%s
            预估数据量：%s
            数据增长率：%s
            数据分级：%s
            
            请考虑以下因素：
            1. 数据完整性
            2. 数据准确性
            3. 数据一致性
            4. 数据及时性
            5. 数据可用性
            
            请只返回一个0-100的整数评分。
            """,
            system.getSystemName(),
            system.getEstimatedDataVolume(),
            system.getDataGrowthRate(),
            system.getDataClassification()
        );
    }

    private String buildComprehensivePrompt(CustomerSystem system) {
        return String.format("""
            请对以下数据资产管理系统进行全面评估：
            
            ===== 系统信息 =====
            系统名称：%s
            系统类型：%s
            业务领域：%s
            业务关键性：%d/5
            用户数量：%d
            日均交易量：%d
            年交易金额：%s
            预估数据量：%s
            数据增长率：%s
            等保级别：%s
            数据分级：%s
            合规认证：%s
            
            ===== 评估要求 =====
            请从以下四个维度进行评估，每个维度给出0-100的评分：
            1. 业务价值评分（考虑业务重要性、用户影响、收入贡献等）
            2. 数据质量评分（考虑数据完整性、准确性、一致性等）
            3. 合规风险评分（考虑安全级别、合规要求、风险等级等）
            4. 技术可行性评分（考虑实施难度、技术复杂度、集成难度等）
            
            然后计算综合评分（加权平均）。
            
            请以JSON格式返回结果，包含以下字段：
            {
              "business_value_score": 85,
              "data_quality_score": 78,
              "compliance_risk_score": 65,
              "technical_feasibility_score": 72,
              "total_score": 75,
              "recommendation": "立即挖掘/优先挖掘/评估后决定/暂不挖掘",
              "priority_level": "critical/high/medium/low",
              "estimated_roi": 2.5,
              "risk_warnings": ["风险1", "风险2"],
              "strengths": ["优势1", "优势2"],
              "suggested_data_products": ["产品1", "产品2"]
            }
            """,
            system.getSystemName(),
            system.getSystemType(),
            system.getBusinessDomain(),
            system.getBusinessCriticality(),
            system.getUserCount(),
            system.getDailyTransactionVolume(),
            system.getAnnualTransactionAmount(),
            system.getEstimatedDataVolume(),
            system.getDataGrowthRate(),
            system.getSecurityLevel(),
            system.getDataClassification(),
            system.getComplianceCertifications()
        );
    }

    private Map<String, Object> buildRequest(String prompt) {
        Map<String, Object> request = new HashMap<>();
        request.put("model", model);
        request.put("messages", List.of(
            Map.of("role", "user", "content", prompt)
        ));
        request.put("temperature", 0.3);
        request.put("max_tokens", 2000);
        return request;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> callDeepSeekAPI(Map<String, Object> request) {
        try {
            // 设置请求头
            // 实际实现中需要添加认证头等
            
            // 调用API
            // Map<String, Object> response = restTemplate.postForObject(endpoint, request, Map.class);
            
            // 这里模拟API响应
            return Map.of(
                "choices", List.of(
                    Map.of("message", Map.of(
                        "content", """
                            {
                              "business_value_score": 85,
                              "data_quality_score": 78,
                              "compliance_risk_score": 65,
                              "technical_feasibility_score": 72,
                              "total_score": 75,
                              "recommendation": "优先挖掘",
                              "priority_level": "high",
                              "estimated_roi": 2.5,
                              "risk_warnings": ["数据安全需要加强", "合规认证待完善"],
                              "strengths": ["业务关键性高", "用户基数大"],
                              "suggested_data_products": ["客户行为分析", "交易风险预警"]
                            }
                            """
                    ))
                )
            );
            
        } catch (Exception e) {
            log.error("调用DeepSeek API失败", e);
            throw new RuntimeException("DeepSeek API调用失败: " + e.getMessage());
        }
    }

    private BigDecimal parseBusinessValueScore(Map<String, Object> response) {
        // 解析响应，提取评分
        // 这里简化处理，实际需要解析JSON
        return new BigDecimal("85");
    }

    private BigDecimal parseDataQualityScore(Map<String, Object> response) {
        return new BigDecimal("78");
    }

    private BigDecimal parseComplianceRiskScore(Map<String, Object> response) {
        return new BigDecimal("65");
    }

    private BigDecimal parseTechnicalFeasibilityScore(Map<String, Object> response) {
        return new BigDecimal("72");
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> parseComprehensiveResult(Map<String, Object> response) {
        try {
            // 从响应中提取JSON内容
            List<Map<String, Object>> choices = (List<Map<String, Object>>) response.get("choices");
            if (choices != null && !choices.isEmpty()) {
                Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
                String content = (String) message.get("content");
                
                // 这里应该解析JSON字符串
                // 简化处理，返回模拟数据
                return Map.of(
                    "business_value_score", 85,
                    "data_quality_score", 78,
                    "compliance_risk_score", 65,
                    "technical_feasibility_score", 72,
                    "total_score", 75,
                    "recommendation", "优先挖掘",
                    "priority_level", "high",
                    "estimated_roi", 2.5,
                    "risk_warnings", List.of("数据安全需要加强", "合规认证待完善"),
                    "strengths", List.of("业务关键性高", "用户基数大"),
                    "suggested_data_products", List.of("客户行为分析", "交易风险预警")
                );
            }
        } catch (Exception e) {
            log.error("解析DeepSeek响应失败", e);
        }
        
        return Map.of("error", "解析失败");
    }
}