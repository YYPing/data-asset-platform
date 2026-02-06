package com.company.dataasset.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * 客户DTO
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Data
public class CustomerDTO {

    /**
     * 公司名称
     */
    @NotBlank(message = "公司名称不能为空")
    private String companyName;

    /**
     * 公司简称
     */
    private String companyShortName;

    /**
     * 所属行业
     */
    @NotBlank(message = "所属行业不能为空")
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
    @NotBlank(message = "联系人姓名不能为空")
    private String contactName;

    /**
     * 联系人电话
     */
    @NotBlank(message = "联系人电话不能为空")
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
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
}
