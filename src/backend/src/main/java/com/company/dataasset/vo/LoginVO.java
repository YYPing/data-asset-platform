package com.company.dataasset.vo;

import lombok.Data;

/**
 * 登录VO
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Data
public class LoginVO {

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 用户名
     */
    private String username;

    /**
     * 真实姓名
     */
    private String realName;

    /**
     * 用户类型
     */
    private String userType;

    /**
     * token
     */
    private String token;

    /**
     * 过期时间（毫秒）
     */
    private Long expiresIn;

    /**
     * 头像
     */
    private String avatar;
}
