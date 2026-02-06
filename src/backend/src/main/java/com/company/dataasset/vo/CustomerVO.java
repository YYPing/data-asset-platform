package com.company.dataasset.vo;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 客户VO
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Data
public class CustomerVO {

    /**
     * 主键ID
     */
    private Long id;

    /**
     * 客户编码
     */
    private String customerCode;

    /**
     * 公司名称
     */
    private String companyName;

    /**
     * 公司简称
     */
    private String companyShortName;

    /**
     * 所属行业
     */
    private String industry;

    /**
     * 企业规模
     */
    private String companyScale;

    /**
     * 统一社会信用代码
     */
    private String businessLicense;

    /**
     * 法定代表人
     */
    private String legalRepresentative;

    /**
     * 注册资本(万元)
     */
    private BigDecimal registeredCapital;

    /**
     * 成立日期
     */
    private LocalDate establishmentDate;

    /**
     * 注册地址
     */
    private String registeredAddress;

    /**
     * 办公地址
     */
    private String officeAddress;

    /**
     * 联系人姓名
     */
    private String contactName;

    /**
     * 联系人电话
     */
    private String contactPhone;

    /**
     * 联系人邮箱
     */
    private String contactEmail;

    /**
     * 联系人职位
     */
    private String contactPosition;

    /**
     * 公司官网
     */
    private String companyWebsite;

    /**
     * 公司简介
     */
    private String companyIntroduction;

    /**
     * 经营范围
     */
    private String businessScope;

    /**
     * 状态：1-有效，0-停用
     */
    private Integer status;

    /**
     * 客户经理ID
     */
    private Long managerId;

    /**
     * 客户来源
     */
    private String source;

    /**
     * 备注
     */
    private String remark;

    /**
     * 创建时间
     */
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    private LocalDateTime updatedAt;

    /**
     * 关联项目数量
     */
    private Integer projectCount;
}
