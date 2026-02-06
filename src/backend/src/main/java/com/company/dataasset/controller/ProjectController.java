package com.company.dataasset.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.company.dataasset.common.Result;
import com.company.dataasset.dto.ProjectDTO;
import com.company.dataasset.service.ProjectService;
import com.company.dataasset.vo.ProjectVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 项目Controller
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Slf4j
@RestController
@RequestMapping("/projects")
@RequiredArgsConstructor
public class ProjectController {

    private final ProjectService projectService;

    /**
     * 分页查询项目列表
     */
    @GetMapping
    public Result<Page<ProjectVO>> list(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String projectName,
            @RequestParam(required = false) Long customerId,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String projectType) {
        
        log.info("查询项目列表: pageNum={}, pageSize={}, projectName={}, customerId={}, status={}, projectType={}",
                pageNum, pageSize, projectName, customerId, status, projectType);
        
        Page<com.company.dataasset.entity.Project> page = new Page<>(pageNum, pageSize);
        Page<ProjectVO> resultPage = projectService.queryProjectPage(page, projectName, customerId, status, projectType);
        
        return Result.success(resultPage);
    }

    /**
     * 获取项目详情
     */
    @GetMapping("/{id}")
    public Result<ProjectVO> getById(@PathVariable Long id) {
        log.info("获取项目详情: id={}", id);
        ProjectVO vo = projectService.getProjectDetail(id);
        return Result.success(vo);
    }

    /**
     * 创建项目
     */
    @PostMapping
    public Result<ProjectVO> create(@Valid @RequestBody ProjectDTO dto) {
        log.info("创建项目: {}", dto.getProjectName());
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        ProjectVO vo = projectService.createProject(dto, currentUserId);
        return Result.success("创建成功", vo);
    }

    /**
     * 更新项目
     */
    @PutMapping("/{id}")
    public Result<ProjectVO> update(@PathVariable Long id, @Valid @RequestBody ProjectDTO dto) {
        log.info("更新项目: id={}", id);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        ProjectVO vo = projectService.updateProject(id, dto, currentUserId);
        return Result.success("更新成功", vo);
    }

    /**
     * 删除项目
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        log.info("删除项目: id={}", id);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        projectService.deleteProject(id, currentUserId);
        return Result.success("删除成功");
    }

    /**
     * 更新项目进度
     */
    @PatchMapping("/{id}/progress")
    public Result<Void> updateProgress(@PathVariable Long id, @RequestParam Integer progress) {
        log.info("更新项目进度: id={}, progress={}", id, progress);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        projectService.updateProgress(id, progress, currentUserId);
        return Result.success("更新成功");
    }

    /**
     * 更新项目阶段
     */
    @PatchMapping("/{id}/phase")
    public Result<Void> updatePhase(@PathVariable Long id, @RequestParam String phase) {
        log.info("更新项目阶段: id={}, phase={}", id, phase);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        projectService.updatePhase(id, phase, currentUserId);
        return Result.success("更新成功");
    }

    /**
     * 根据客户ID查询项目列表
     */
    @GetMapping("/customer/{customerId}")
    public Result<List<ProjectVO>> listByCustomer(@PathVariable Long customerId) {
        log.info("查询客户项目列表: customerId={}", customerId);
        List<ProjectVO> projects = projectService.listByCustomerId(customerId);
        return Result.success(projects);
    }

    /**
     * 生成项目编码
     */
    @GetMapping("/generate-code")
    public Result<String> generateCode() {
        String code = projectService.generateProjectCode();
        return Result.success(code);
    }

    /**
     * 更新项目状态
     */
    @PatchMapping("/{id}/status")
    public Result<Void> updateStatus(@PathVariable Long id, @RequestParam String status) {
        log.info("更新项目状态: id={}, status={}", id, status);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        projectService.updateStatus(id, status, currentUserId);
        return Result.success("更新成功");
    }

    /**
     * 根据项目编码查询
     */
    @GetMapping("/code/{projectCode}")
    public Result<ProjectVO> getByCode(@PathVariable String projectCode) {
        log.info("根据项目编码查询: code={}", projectCode);
        ProjectVO vo = projectService.getProjectByCode(projectCode);
        return Result.success(vo);
    }

    /**
     * 获取项目统计信息
     */
    @GetMapping("/stats")
    public Result<Object> getStats() {
        log.info("获取项目统计信息");
        Object stats = projectService.getProjectStats();
        return Result.success(stats);
    }

    /**
     * 获取客户的项目统计
     */
    @GetMapping("/customer-stats")
    public Result<Object> getCustomerStats() {
        log.info("获取客户的项目统计");
        Object stats = projectService.getCustomerProjectStats();
        return Result.success(stats);
    }

    /**
     * 获取项目阶段分布
     */
    @GetMapping("/phase-distribution")
    public Result<Object> getPhaseDistribution() {
        log.info("获取项目阶段分布");
        Object distribution = projectService.getPhaseDistribution();
        return Result.success(distribution);
    }

    /**
     * 查询即将到期的项目
     */
    @GetMapping("/expiring")
    public Result<Object> getExpiringProjects() {
        log.info("查询即将到期的项目");
        Object projects = projectService.getExpiringProjects();
        return Result.success(projects);
    }

    /**
     * 查询需要关注的项目
     */
    @GetMapping("/need-attention")
    public Result<Object> getNeedAttentionProjects() {
        log.info("查询需要关注的项目");
        Object projects = projectService.getNeedAttentionProjects();
        return Result.success(projects);
    }
}
