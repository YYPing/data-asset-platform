package com.company.dataasset.controller;

import com.company.dataasset.common.Result;
import com.company.dataasset.dto.LoginDTO;
import com.company.dataasset.service.AuthService;
import com.company.dataasset.vo.LoginVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

/**
 * 认证Controller
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Slf4j
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    /**
     * 用户登录
     */
    @PostMapping("/login")
    public Result<LoginVO> login(@Valid @RequestBody LoginDTO dto) {
        log.info("用户登录: username={}", dto.getUsername());
        LoginVO vo = authService.login(dto);
        return Result.success("登录成功", vo);
    }

    /**
     * 用户登出
     */
    @PostMapping("/logout")
    public Result<Void> logout(@RequestHeader("Authorization") String token) {
        log.info("用户登出");
        authService.logout(extractToken(token));
        return Result.success("登出成功");
    }

    /**
     * 刷新token
     */
    @PostMapping("/refresh")
    public Result<LoginVO> refreshToken(@RequestHeader("Authorization") String token) {
        log.info("刷新token");
        LoginVO vo = authService.refreshToken(extractToken(token));
        return Result.success("刷新成功", vo);
    }

    /**
     * 获取当前用户信息
     */
    @GetMapping("/me")
    public Result<LoginVO> getCurrentUser(@RequestHeader("Authorization") String token) {
        log.info("获取当前用户信息");
        LoginVO vo = authService.getCurrentUser(extractToken(token));
        return Result.success(vo);
    }

    /**
     * 从Authorization头中提取token
     */
    private String extractToken(String authorization) {
        if (authorization != null && authorization.startsWith("Bearer ")) {
            return authorization.substring(7);
        }
        return authorization;
    }
}
