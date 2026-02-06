package com.company.dataasset.service.impl;

import com.company.dataasset.common.BusinessException;
import com.company.dataasset.common.JwtUtil;
import com.company.dataasset.dto.LoginDTO;
import com.company.dataasset.entity.User;
import com.company.dataasset.mapper.UserMapper;
import com.company.dataasset.service.AuthService;
import com.company.dataasset.vo.LoginVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

/**
 * 认证Service实现类
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final UserMapper userMapper;
    private final JwtUtil jwtUtil;
    private final PasswordEncoder passwordEncoder;

    /**
     * 用户登录
     */
    @Override
    public LoginVO login(LoginDTO dto) {
        // 1. 查询用户
        User user = userMapper.selectByUsername(dto.getUsername());
        if (user == null) {
            throw new BusinessException("用户名或密码错误");
        }

        // 2. 检查用户状态
        if (user.getStatus() == 0) {
            throw new BusinessException("用户已被禁用");
        }

        // 3. 验证密码
        if (!passwordEncoder.matches(dto.getPassword(), user.getPassword())) {
            throw new BusinessException("用户名或密码错误");
        }

        // 4. 更新最后登录时间
        user.setLastLoginTime(LocalDateTime.now());
        userMapper.updateById(user);

        // 5. 生成token
        String token = jwtUtil.generateToken(
                user.getUsername(), 
                user.getId(), 
                user.getUserType()
        );

        // 6. 返回登录结果
        LoginVO vo = new LoginVO();
        BeanUtils.copyProperties(user, vo);
        vo.setToken(token);
        vo.setExpiresIn(jwtUtil.getExpirationDateFromToken(token).getTime() - System.currentTimeMillis());

        log.info("用户登录成功: username={}, userId={}", user.getUsername(), user.getId());

        return vo;
    }

    /**
     * 用户登出
     */
    @Override
    public void logout(String token) {
        // TODO: 实现token黑名单机制
        log.info("用户登出: token={}", token.substring(0, Math.min(token.length(), 20)) + "...");
    }

    /**
     * 刷新token
     */
    @Override
    public LoginVO refreshToken(String token) {
        // 1. 验证原token
        String username = jwtUtil.getUsernameFromToken(token);
        User user = userMapper.selectByUsername(username);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }

        // 2. 生成新token
        String newToken = jwtUtil.refreshToken(token);

        // 3. 返回结果
        LoginVO vo = new LoginVO();
        BeanUtils.copyProperties(user, vo);
        vo.setToken(newToken);
        vo.setExpiresIn(jwtUtil.getExpirationDateFromToken(newToken).getTime() - System.currentTimeMillis());

        log.info("刷新token成功: username={}", username);

        return vo;
    }

    /**
     * 获取当前用户信息
     */
    @Override
    public LoginVO getCurrentUser(String token) {
        String username = jwtUtil.getUsernameFromToken(token);
        User user = userMapper.selectByUsername(username);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }

        LoginVO vo = new LoginVO();
        BeanUtils.copyProperties(user, vo);
        vo.setToken(token);
        vo.setExpiresIn(jwtUtil.getExpirationDateFromToken(token).getTime() - System.currentTimeMillis());

        return vo;
    }
}
