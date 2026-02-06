package com.company.dataasset.vo;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 项目VO
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Data
public class ProjectVO {

    /**
     * 主键ID
     */
    private Long id;

    /**
     * 项目编号
     */
    private String projectCode;

    /**
     * 客户ID
     */
    private Long customerId;

    /**
     * 客户名称
     */
    private String customerName;

    /**
     * 项目名称
     */
    private String projectName;

    /**
     * 项目类型
     */
    private String projectType;

    /**
     * 项目描述
     */
    private String description;

    /**
     * 合同金额
     */
    private BigDecimal contractAmount;

    /**
     * 开始日期
     */
    private LocalDate startDate;

    /**
     * 结束日期
     */
    private LocalDate endDate;

    /**
     * 当前阶段
     */
    private String currentPhase;

    /**
     * 状态
     */
    private String status;

    /**
     * 项目经理ID
     */
    private Long managerId;

    /**
     * 项目经理姓名
     */
    private String managerName;

    /**
     * 整体进度（百分比）
     */
    private Integer progress;

    /**
     * 创建时间
     */
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    private LocalDateTime updatedAt;

    /**
     * 系统数量
     */
    private Integer systemCount;

    /**
     * 评估完成数量
     */
    private Integer assessmentCount;
}
