package com.company.dataasset;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class SimpleTestApp {
    
    public static void main(String[] args) {
        SpringApplication.run(SimpleTestApp.class, args);
    }
    
    @GetMapping("/")
    public String hello() {
        return "数据资产平台 - 测试服务运行正常！";
    }
    
    @GetMapping("/health")
    public String health() {
        return "{\"status\": \"UP\", \"service\": \"data-asset-platform\"}";
    }
}
