package com.company.dataasset.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * 客户系统数据传输对象
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-06
 */
@Data
@Schema(description = "客户系统数据传输对象")
public class CustomerSystemDTO {

    @Schema(description = "项目ID", required = true)
    @NotNull(message = "项目ID不能为空")
    private Long projectId;

    @Schema(description = "系统编码", example = "S2024020001")
    private String systemCode;

    @Schema(description = "系统名称", required = true, example = "核心交易系统")
    @NotBlank(message = "系统名称不能为空")
    private String systemName;

    @Schema(description = "系统类型", required = true, example = "transactional", 
            allowableValues = {"transactional", "analytical", "operational", "reporting", "external"})
    @NotBlank(message = "系统类型不能为空")
    private String systemType;

    @Schema(description = "业务领域", example = "交易结算")
    private String businessDomain;

    @Schema(description = "系统简介", example = "处理公司核心交易业务的系统")
    private String description;

    @Schema(description = "开发商/供应商", example = "Oracle公司")
    private String vendor;

    @Schema(description = "系统版本", example = "12.2.0")
    private String version;

    @Schema(description = "数据库类型", example = "Oracle")
    private String databaseType;

    @Schema(description = "预估数据量", example = "large", 
            allowableValues = {"small", "medium", "large", "very_large"})
    private String estimatedDataVolume;

    @Schema(description = "数据增长率", example = "medium", 
            allowableValues = {"low", "medium", "high"})
    private String dataGrowthRate;

    @Schema(description = "等保级别", example = "三级", 
            allowableValues = {"一级", "二级", "三级", "四级"})
    private String securityLevel;

    @Schema(description = "数据分级", example = "核心数据")
    private String dataClassification;

    @Schema(description = "合规认证清单", example = "ISO27001, PCI-DSS")
    private String complianceCertifications;

    @Schema(description = "上次安全评估时间", example = "2025-01-15")
    private LocalDate lastSecurityAssessment;

    @Schema(description = "业务关键性：1-5级", example = "5", 
            minimum = "1", maximum = "5")
    private Integer businessCriticality;

    @Schema(description = "用户数量", example = "1000")
    private Integer userCount;

    @Schema(description = "日均交易量", example = "50000")
    private Integer dailyTransactionVolume;

    @Schema(description = "年交易金额", example = "1000000000.00")
    private BigDecimal annualTransactionAmount;

    @Schema(description = "业务负责人", example = "张三")
    private String businessOwner;

    @Schema(description = "业务负责人电话", example = "13800138000")
    private String businessOwnerPhone;

    @Schema(description = "IT负责人", example = "李四")
    private String itOwner;

    @Schema(description = "IT负责人电话", example = "13900139000")
    private String itOwnerPhone;

    @Schema(description = "数据负责人", example = "王五")
    private String dataOwner;

    @Schema(description = "数据负责人电话", example = "13700137000")
    private String dataOwnerPhone;

    @Schema(description = "状态", example = "active", 
            allowableValues = {"active", "inactive", "maintenance", "decommissioned"})
    private String status;

    @Schema(description = "是否被选中挖掘", example = "0", 
            allowableValues = {"0", "1"})
    private Integer isSelected;

    @Schema(description = "选中理由", example = "数据价值高，业务关键性强")
    private String selectionReason;

    @Schema(description = "优先级", example = "high", 
            allowableValues = {"low", "medium", "high", "critical"})
    private String priorityLevel;
}