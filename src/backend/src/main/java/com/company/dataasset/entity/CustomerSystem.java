package com.company.dataasset.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 客户系统实体类
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Data
@TableName("customer_system")
public class CustomerSystem implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 项目ID
     */
    private Long projectId;

    /**
     * 系统编码
     */
    private String systemCode;

    /**
     * 系统名称
     */
    private String systemName;

    /**
     * 系统类型
     */
    private String systemType;

    /**
     * 业务领域
     */
    private String businessDomain;

    /**
     * 系统简介
     */
    private String description;

    /**
     * 开发商/供应商
     */
    private String vendor;

    /**
     * 系统版本
     */
    private String version;

    /**
     * 数据库类型
     */
    private String databaseType;

    /**
     * 预估数据量
     */
    private String estimatedDataVolume;

    /**
     * 数据增长率
     */
    private String dataGrowthRate;

    /**
     * 等保级别
     */
    private String securityLevel;

    /**
     * 数据分级
     */
    private String dataClassification;

    /**
     * 合规认证清单
     */
    private String complianceCertifications;

    /**
     * 上次安全评估时间
     */
    private LocalDate lastSecurityAssessment;

    /**
     * 业务关键性：1-5级
     */
    private Integer businessCriticality;

    /**
     * 用户数量
     */
    private Integer userCount;

    /**
     * 日均交易量
     */
    private Integer dailyTransactionVolume;

    /**
     * 年交易金额
     */
    private BigDecimal annualTransactionAmount;

    /**
     * 业务负责人
     */
    private String businessOwner;

    /**
     * 业务负责人电话
     */
    private String businessOwnerPhone;

    /**
     * IT负责人
     */
    private String itOwner;

    /**
     * IT负责人电话
     */
    private String itOwnerPhone;

    /**
     * 数据负责人
     */
    private String dataOwner;

    /**
     * 数据负责人电话
     */
    private String dataOwnerPhone;

    /**
     * 状态
     */
    private String status;

    /**
     * 是否被选中挖掘
     */
    private Integer isSelected;

    /**
     * 选中理由
     */
    private String selectionReason;

    /**
     * 优先级
     */
    private String priorityLevel;

    /**
     * 创建时间
     */
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    private LocalDateTime updatedAt;

    /**
     * 删除标记
     */
    @TableLogic
    private Integer deleted;

    /**
     * 评估结果（非数据库字段）
     */
    @TableField(exist = false)
    private SystemAssessment assessment;
}
