package com.company.dataasset.vo;

import com.company.dataasset.entity.SystemAssessment;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 客户系统视图对象
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-06
 */
@Data
@Schema(description = "客户系统视图对象")
public class CustomerSystemVO {

    @Schema(description = "主键ID")
    private Long id;

    @Schema(description = "项目ID")
    private Long projectId;

    @Schema(description = "项目名称")
    private String projectName;

    @Schema(description = "系统编码")
    private String systemCode;

    @Schema(description = "系统名称")
    private String systemName;

    @Schema(description = "系统类型")
    private String systemType;

    @Schema(description = "系统类型名称")
    private String systemTypeName;

    @Schema(description = "业务领域")
    private String businessDomain;

    @Schema(description = "系统简介")
    private String description;

    @Schema(description = "开发商/供应商")
    private String vendor;

    @Schema(description = "系统版本")
    private String version;

    @Schema(description = "数据库类型")
    private String databaseType;

    @Schema(description = "预估数据量")
    private String estimatedDataVolume;

    @Schema(description = "数据增长率")
    private String dataGrowthRate;

    @Schema(description = "等保级别")
    private String securityLevel;

    @Schema(description = "数据分级")
    private String dataClassification;

    @Schema(description = "合规认证清单")
    private String complianceCertifications;

    @Schema(description = "上次安全评估时间")
    private LocalDate lastSecurityAssessment;

    @Schema(description = "业务关键性：1-5级")
    private Integer businessCriticality;

    @Schema(description = "业务关键性描述")
    private String businessCriticalityDesc;

    @Schema(description = "用户数量")
    private Integer userCount;

    @Schema(description = "日均交易量")
    private Integer dailyTransactionVolume;

    @Schema(description = "年交易金额")
    private BigDecimal annualTransactionAmount;

    @Schema(description = "业务负责人")
    private String businessOwner;

    @Schema(description = "业务负责人电话")
    private String businessOwnerPhone;

    @Schema(description = "IT负责人")
    private String itOwner;

    @Schema(description = "IT负责人电话")
    private String itOwnerPhone;

    @Schema(description = "数据负责人")
    private String dataOwner;

    @Schema(description = "数据负责人电话")
    private String dataOwnerPhone;

    @Schema(description = "状态")
    private String status;

    @Schema(description = "状态名称")
    private String statusName;

    @Schema(description = "是否被选中挖掘")
    private Integer isSelected;

    @Schema(description = "选中理由")
    private String selectionReason;

    @Schema(description = "优先级")
    private String priorityLevel;

    @Schema(description = "优先级名称")
    private String priorityLevelName;

    @Schema(description = "创建时间")
    private LocalDateTime createdAt;

    @Schema(description = "更新时间")
    private LocalDateTime updatedAt;

    @Schema(description = "评估结果")
    private SystemAssessment assessment;

    @Schema(description = "是否需要评估")
    private Boolean needAssessment;

    @Schema(description = "是否需要安全评估")
    private Boolean needSecurityAssessment;

    @Schema(description = "数据价值评分")
    private BigDecimal dataValueScore;

    @Schema(description = "业务价值评分")
    private BigDecimal businessValueScore;

    @Schema(description = "综合价值评分")
    private BigDecimal totalValueScore;

    @Schema(description = "数据质量评分")
    private BigDecimal dataQualityScore;

    @Schema(description = "风险评估等级")
    private String riskLevel;

    @Schema(description = "推荐挖掘优先级")
    private String recommendedPriority;

    @Schema(description = "预计挖掘价值")
    private BigDecimal estimatedMiningValue;

    @Schema(description = "预计实施周期")
    private Integer estimatedImplementationPeriod;

    @Schema(description = "技术复杂度")
    private String technicalComplexity;

    @Schema(description = "数据可访问性")
    private String dataAccessibility;

    @Schema(description = "系统集成难度")
    private String integrationDifficulty;

    @Schema(description = "合规风险等级")
    private String complianceRiskLevel;

    @Schema(description = "安全风险等级")
    private String securityRiskLevel;

    @Schema(description = "业务影响度")
    private String businessImpact;

    @Schema(description = "数据敏感性")
    private String dataSensitivity;

    @Schema(description = "数据新鲜度")
    private String dataFreshness;

    @Schema(description = "数据完整性")
    private String dataCompleteness;

    @Schema(description = "数据准确性")
    private String dataAccuracy;

    @Schema(description = "数据一致性")
    private String dataConsistency;

    @Schema(description = "数据可用性")
    private String dataAvailability;

    @Schema(description = "备注")
    private String remark;
}