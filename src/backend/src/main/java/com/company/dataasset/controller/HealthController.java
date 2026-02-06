package com.company.dataasset.controller;

import com.company.dataasset.common.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * 健康检查Controller
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Slf4j
@RestController
@RequestMapping("/health")
@RequiredArgsConstructor
@Tag(name = "健康检查", description = "系统健康检查接口")
public class HealthController {

    @Value("${spring.application.name}")
    private String appName;

    @Value("${server.port}")
    private String serverPort;

    /**
     * 健康检查
     */
    @GetMapping
    @Operation(summary = "健康检查", description = "检查系统是否正常运行")
    public Result<Map<String, Object>> health() {
        Map<String, Object> healthInfo = new HashMap<>();
        healthInfo.put("status", "UP");
        healthInfo.put("application", appName);
        healthInfo.put("port", serverPort);
        healthInfo.put("timestamp", LocalDateTime.now());
        healthInfo.put("version", "1.0.0");
        
        log.debug("健康检查请求");
        return Result.success(healthInfo);
    }

    /**
     * 就绪检查
     */
    @GetMapping("/ready")
    @Operation(summary = "就绪检查", description = "检查系统是否就绪接收流量")
    public Result<Map<String, Object>> ready() {
        Map<String, Object> readyInfo = new HashMap<>();
        readyInfo.put("status", "READY");
        readyInfo.put("timestamp", LocalDateTime.now());
        
        // TODO: 添加数据库连接检查
        // TODO: 添加Redis连接检查
        // TODO: 添加MinIO连接检查
        
        return Result.success(readyInfo);
    }

    /**
     * 存活检查
     */
    @GetMapping("/live")
    @Operation(summary = "存活检查", description = "检查系统是否存活")
    public Result<Map<String, Object>> live() {
        Map<String, Object> liveInfo = new HashMap<>();
        liveInfo.put("status", "ALIVE");
        liveInfo.put("timestamp", LocalDateTime.now());
        
        return Result.success(liveInfo);
    }

    /**
     * 系统信息
     */
    @GetMapping("/info")
    @Operation(summary = "系统信息", description = "获取系统基本信息")
    public Result<Map<String, Object>> info() {
        Map<String, Object> info = new HashMap<>();
        info.put("name", appName);
        info.put("version", "1.0.0");
        info.put("description", "数据资产全流程管理平台");
        info.put("environment", "development");
        info.put("java.version", System.getProperty("java.version"));
        info.put("os.name", System.getProperty("os.name"));
        info.put("os.arch", System.getProperty("os.arch"));
        info.put("startup.time", LocalDateTime.now());
        
        return Result.success(info);
    }
}
