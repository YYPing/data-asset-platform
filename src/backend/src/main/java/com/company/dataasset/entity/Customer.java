package com.company.dataasset.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 客户实体类
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Data
@TableName("customer")
public class Customer implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
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
    private java.math.BigDecimal registeredCapital;

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
     * 创建人
     */
    @TableField(fill = FieldFill.INSERT)
    private Long createdBy;

    /**
     * 创建时间
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /**
     * 更新人
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Long updatedBy;

    /**
     * 更新时间
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    /**
     * 删除标记：0-正常，1-已删除
     */
    @TableLogic
    @TableField(fill = FieldFill.INSERT)
    private Integer deleted;
}
