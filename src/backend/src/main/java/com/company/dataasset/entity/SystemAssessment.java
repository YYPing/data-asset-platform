package com.company.dataasset.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 系统价值评估实体类
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Data
@TableName("system_assessment")
public class SystemAssessment implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 系统ID
     */
    private Long systemId;

    /**
     * 项目ID
     */
    private Long projectId;

    /**
     * 业务价值评分
     */
    private BigDecimal businessValueScore;

    /**
     * 数据质量预估评分
     */
    private BigDecimal dataQualityScore;

    /**
     * 合规风险评分
     */
    private BigDecimal complianceRiskScore;

    /**
     * 技术可行性评分
     */
    private BigDecimal technicalFeasibilityScore;

    /**
     * 综合评分
     */
    private BigDecimal totalScore;

    /**
     * 业务价值评估详情
     */
    private String businessValueDetail;

    /**
     * 数据质量评估详情
     */
    private String dataQualityDetail;

    /**
     * 合规风险评估详情
     */
    private String complianceRiskDetail;

    /**
     * 技术可行性评估详情
     */
    private String technicalFeasibilityDetail;

    /**
     * 建议
     */
    private String recommendation;

    /**
     * 优先级
     */
    private String priorityLevel;

    /**
     * 预估投资回报率
     */
    private BigDecimal estimatedRoi;

    /**
     * 预估年收益
     */
    private BigDecimal estimatedBenefit;

    /**
     * 预估实施成本
     */
    private BigDecimal estimatedCost;

    /**
     * 预估实施天数
     */
    private Integer estimatedEffortDays;

    /**
     * 实施路线图
     */
    private String implementationRoadmap;

    /**
     * 建议的数据产品类型
     */
    private String suggestedDataProducts;

    /**
     * 风险提示
     */
    private String riskWarnings;

    /**
     * 评估人ID
     */
    private Long assessorId;

    /**
     * 评估日期
     */
    private LocalDate assessmentDate;

    /**
     * 审核状态
     */
    private String reviewStatus;

    /**
     * 审核人ID
     */
    private Long reviewerId;

    /**
     * 审核日期
     */
    private LocalDate reviewDate;

    /**
     * 审核意见
     */
    private String reviewComments;

    /**
     * 创建时间
     */
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    private LocalDateTime updatedAt;

    /**
     * 建议的数据产品列表（解析后的）
     */
    public List<String> getSuggestedDataProductList() {
        if (suggestedDataProducts == null || suggestedDataProducts.isEmpty()) {
            return List.of();
        }
        return List.of(suggestedDataProducts.replace("[", "").replace("]", "").replace("\"", "").split(","));
    }

    /**
     * 获取建议文本
     */
    public String getRecommendationText() {
        return switch (recommendation) {
            case "immediate" -> "立即挖掘";
            case "priority" -> "优先挖掘";
            case "evaluate" -> "评估后决定";
            case "skip" -> "暂不挖掘";
            default -> "未知";
        };
    }
}
