package com.company.dataasset.ai.model;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 服务状态
 */
@Data
public class ServiceStatus {

    /**
     * 服务名称
     */
    private String serviceName;

    /**
     * 服务状态
     */
    private Status status;

    /**
     * 最后检查时间
     */
    private LocalDateTime lastCheckTime;

    /**
     * 响应时间（毫秒）
     */
    private Long responseTimeMs;

    /**
     * 错误信息
     */
    private String errorMessage;

    /**
     * 错误代码
     */
    private String errorCode;

    /**
     * 重试次数
     */
    private Integer retryCount;

    /**
     * 是否启用
     */
    private boolean enabled;

    /**
     * 配置信息
     */
    private String configInfo;

    /**
     * 服务端点
     */
    private String endpoint;

    /**
     * API版本
     */
    private String apiVersion;

    /**
     * 服务提供商
     */
    private String provider;

    /**
     * 服务状态枚举
     */
    public enum Status {
        UP,           // 服务正常
        DOWN,         // 服务不可用
        DEGRADED,     // 服务降级
        UNKNOWN,      // 状态未知
        INITIALIZING, // 初始化中
        MAINTENANCE   // 维护中
    }
}