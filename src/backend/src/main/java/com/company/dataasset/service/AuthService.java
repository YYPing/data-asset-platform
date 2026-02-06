package com.company.dataasset.service;

import com.company.dataasset.dto.LoginDTO;
import com.company.dataasset.vo.LoginVO;

/**
 * 认证Service接口
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
public interface AuthService {

    /**
     * 用户登录
     */
    LoginVO login(LoginDTO dto);

    /**
     * 用户登出
     */
    void logout(String token);

    /**
     * 刷新token
     */
    LoginVO refreshToken(String token);

    /**
     * 获取当前用户信息
     */
    LoginVO getCurrentUser(String token);
}
