package com.company.dataasset.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.company.dataasset.common.Result;
import com.company.dataasset.dto.CustomerSystemDTO;
import com.company.dataasset.entity.CustomerSystem;
import com.company.dataasset.service.CustomerSystemService;
import com.company.dataasset.vo.CustomerSystemVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 客户系统Controller
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-06
 */
@Slf4j
@Tag(name = "客户系统管理", description = "客户系统信息管理API")
@RestController
@RequestMapping("/customer-systems")
@RequiredArgsConstructor
public class CustomerSystemController {

    private final CustomerSystemService customerSystemService;

    /**
     * 分页查询客户系统列表
     */
    @Operation(summary = "分页查询客户系统列表", description = "根据条件分页查询客户系统信息")
    @GetMapping
    public Result<IPage<CustomerSystemVO>> list(
            @Parameter(description = "页码", example = "1") 
            @RequestParam(defaultValue = "1") Integer pageNum,
            
            @Parameter(description = "每页数量", example = "10") 
            @RequestParam(defaultValue = "10") Integer pageSize,
            
            @Parameter(description = "系统名称") 
            @RequestParam(required = false) String systemName,
            
            @Parameter(description = "项目ID") 
            @RequestParam(required = false) Long projectId,
            
            @Parameter(description = "系统类型") 
            @RequestParam(required = false) String systemType,
            
            @Parameter(description = "状态") 
            @RequestParam(required = false) String status) {
        
        log.info("查询客户系统列表: pageNum={}, pageSize={}, systemName={}, projectId={}, systemType={}, status={}",
                pageNum, pageSize, systemName, projectId, systemType, status);
        
        Page<CustomerSystem> page = new Page<>(pageNum, pageSize);
        IPage<CustomerSystemVO> resultPage = customerSystemService.queryCustomerSystemPage(
                page, systemName, projectId, systemType, status);
        
        return Result.success(resultPage);
    }

    /**
     * 获取客户系统详情
     */
    @Operation(summary = "获取客户系统详情", description = "根据ID获取客户系统详细信息")
    @GetMapping("/{id}")
    public Result<CustomerSystemVO> getById(
            @Parameter(description = "系统ID", required = true) 
            @PathVariable Long id) {
        
        log.info("获取客户系统详情: id={}", id);
        CustomerSystemVO vo = customerSystemService.getCustomerSystemDetail(id);
        return Result.success(vo);
    }

    /**
     * 创建客户系统
     */
    @Operation(summary = "创建客户系统", description = "创建新的客户系统信息")
    @PostMapping
    public Result<CustomerSystemVO> create(
            @Parameter(description = "客户系统信息", required = true) 
            @Valid @RequestBody CustomerSystemDTO dto) {
        
        log.info("创建客户系统: {}", dto.getSystemName());
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        CustomerSystemVO vo = customerSystemService.createCustomerSystem(dto, currentUserId);
        return Result.success("创建成功", vo);
    }

    /**
     * 更新客户系统
     */
    @Operation(summary = "更新客户系统", description = "更新客户系统信息")
    @PutMapping("/{id}")
    public Result<CustomerSystemVO> update(
            @Parameter(description = "系统ID", required = true) 
            @PathVariable Long id,
            
            @Parameter(description = "客户系统信息", required = true) 
            @Valid @RequestBody CustomerSystemDTO dto) {
        
        log.info("更新客户系统: id={}", id);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        CustomerSystemVO vo = customerSystemService.updateCustomerSystem(id, dto, currentUserId);
        return Result.success("更新成功", vo);
    }

    /**
     * 删除客户系统
     */
    @Operation(summary = "删除客户系统", description = "删除客户系统信息")
    @DeleteMapping("/{id}")
    public Result<Void> delete(
            @Parameter(description = "系统ID", required = true) 
            @PathVariable Long id) {
        
        log.info("删除客户系统: id={}", id);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        customerSystemService.deleteCustomerSystem(id, currentUserId);
        return Result.success("删除成功");
    }

    /**
     * 更新系统状态
     */
    @Operation(summary = "更新系统状态", description = "更新客户系统状态")
    @PatchMapping("/{id}/status")
    public Result<Void> updateStatus(
            @Parameter(description = "系统ID", required = true) 
            @PathVariable Long id,
            
            @Parameter(description = "状态", required = true, 
                      example = "active", 
                      allowableValues = {"active", "inactive", "maintenance", "decommissioned"}) 
            @RequestParam String status) {
        
        log.info("更新系统状态: id={}, status={}", id, status);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        customerSystemService.updateStatus(id, status, currentUserId);
        return Result.success("状态更新成功");
    }

    /**
     * 更新选中状态
     */
    @Operation(summary = "更新选中状态", description = "更新系统是否被选中挖掘")
    @PatchMapping("/{id}/selection")
    public Result<Void> updateSelection(
            @Parameter(description = "系统ID", required = true) 
            @PathVariable Long id,
            
            @Parameter(description = "是否选中", required = true, example = "1") 
            @RequestParam Integer isSelected,
            
            @Parameter(description = "选中理由") 
            @RequestParam(required = false) String selectionReason) {
        
        log.info("更新选中状态: id={}, isSelected={}", id, isSelected);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        customerSystemService.updateSelection(id, isSelected, selectionReason, currentUserId);
        return Result.success("选中状态更新成功");
    }

    /**
     * 根据项目ID查询系统列表
     */
    @Operation(summary = "根据项目查询系统列表", description = "根据项目ID查询关联的系统列表")
    @GetMapping("/project/{projectId}")
    public Result<List<CustomerSystemVO>> listByProject(
            @Parameter(description = "项目ID", required = true) 
            @PathVariable Long projectId) {
        
        log.info("查询项目系统列表: projectId={}", projectId);
        List<CustomerSystemVO> systems = customerSystemService.listByProjectId(projectId);
        return Result.success(systems);
    }

    /**
     * 根据系统编码查询
     */
    @Operation(summary = "根据编码查询系统", description = "根据系统编码查询系统信息")
    @GetMapping("/code/{systemCode}")
    public Result<CustomerSystemVO> getByCode(
            @Parameter(description = "系统编码", required = true) 
            @PathVariable String systemCode) {
        
        log.info("根据系统编码查询: code={}", systemCode);
        CustomerSystemVO vo = customerSystemService.getCustomerSystemByCode(systemCode);
        return Result.success(vo);
    }

    /**
     * 生成系统编码
     */
    @Operation(summary = "生成系统编码", description = "生成新的系统编码")
    @GetMapping("/generate-code")
    public Result<String> generateCode() {
        String code = customerSystemService.generateSystemCode();
        return Result.success(code);
    }

    /**
     * 获取项目系统统计
     */
    @Operation(summary = "获取项目系统统计", description = "获取项目的系统统计信息")
    @GetMapping("/project/{projectId}/stats")
    public Result<Map<String, Object>> getProjectStats(
            @Parameter(description = "项目ID", required = true) 
            @PathVariable Long projectId) {
        
        log.info("获取项目系统统计: projectId={}", projectId);
        Map<String, Object> stats = customerSystemService.getProjectSystemStats(projectId);
        return Result.success(stats);
    }

    /**
     * 获取系统类型分布
     */
    @Operation(summary = "获取系统类型分布", description = "获取系统类型分布统计")
    @GetMapping("/project/{projectId}/type-distribution")
    public Result<List<Map<String, Object>>> getTypeDistribution(
            @Parameter(description = "项目ID", required = true) 
            @PathVariable Long projectId) {
        
        log.info("获取系统类型分布: projectId={}", projectId);
        List<Map<String, Object>> distribution = customerSystemService.getSystemTypeDistribution(projectId);
        return Result.success(distribution);
    }

    /**
     * 获取业务关键性分布
     */
    @Operation(summary = "获取业务关键性分布", description = "获取业务关键性分布统计")
    @GetMapping("/project/{projectId}/criticality-distribution")
    public Result<List<Map<String, Object>>> getCriticalityDistribution(
            @Parameter(description = "项目ID", required = true) 
            @PathVariable Long projectId) {
        
        log.info("获取业务关键性分布: projectId={}", projectId);
        List<Map<String, Object>> distribution = customerSystemService.getBusinessCriticalityDistribution(projectId);
        return Result.success(distribution);
    }

    /**
     * 获取安全级别分布
     */
    @Operation(summary = "获取安全级别分布", description = "获取安全级别分布统计")
    @GetMapping("/project/{projectId}/security-distribution")
    public Result<List<Map<String, Object>>> getSecurityDistribution(
            @Parameter(description = "项目ID", required = true) 
            @PathVariable Long projectId) {
        
        log.info("获取安全级别分布: projectId={}", projectId);
        List<Map<String, Object>> distribution = customerSystemService.getSecurityLevelDistribution(projectId);
        return Result.success(distribution);
    }

    /**
     * 查询需要评估的系统
     */
    @Operation(summary = "查询需要评估的系统", description = "查询需要价值评估的系统列表")
    @GetMapping("/need-assessment")
    public Result<List<CustomerSystemVO>> getNeedAssessment() {
        log.info("查询需要评估的系统");
        List<CustomerSystemVO> systems = customerSystemService.getNeedAssessmentSystems();
        return Result.success(systems);
    }

    /**
     * 查询已选中待挖掘的系统
     */
    @Operation(summary = "查询已选中系统", description = "查询已选中待挖掘的系统列表")
    @GetMapping("/selected")
    public Result<List<CustomerSystemVO>> getSelected() {
        log.info("查询已选中待挖掘的系统");
        List<CustomerSystemVO> systems = customerSystemService.getSelectedSystems();
        return Result.success(systems);
    }

    /**
     * 根据业务领域查询系统
     */
    @Operation(summary = "根据业务领域查询", description = "根据业务领域查询系统列表")
    @GetMapping("/business-domain/{businessDomain}")
    public Result<List<CustomerSystemVO>> listByBusinessDomain(
            @Parameter(description = "业务领域", required = true) 
            @PathVariable String businessDomain) {
        
        log.info("根据业务领域查询系统: domain={}", businessDomain);
        List<CustomerSystemVO> systems = customerSystemService.listByBusinessDomain(businessDomain);
        return Result.success(systems);
    }

    /**
     * 获取系统负责人统计
     */
    @Operation(summary = "获取负责人统计", description = "获取系统负责人统计信息")
    @GetMapping("/owner-statistics")
    public Result<List<Map<String, Object>>> getOwnerStats() {
        log.info("获取系统负责人统计");
        List<Map<String, Object>> stats = customerSystemService.getOwnerStatistics();
        return Result.success(stats);
    }

    /**
     * 查询需要安全评估的系统
     */
    @Operation(summary = "查询需要安全评估的系统", description = "查询需要安全评估的系统列表")
    @GetMapping("/need-security-assessment")
    public Result<List<CustomerSystemVO>> getNeedSecurityAssessment() {
        log.info("查询需要安全评估的系统");
        List<CustomerSystemVO> systems = customerSystemService.getNeedSecurityAssessmentSystems();
        return Result.success(systems);
    }

    /**
     * 获取系统数据量统计
     */
    @Operation(summary = "获取数据量统计", description = "获取系统数据量统计信息")
    @GetMapping("/project/{projectId}/data-volume-stats")
    public Result<Map<String, Object>> getDataVolumeStats(
            @Parameter(description = "项目ID", required = true) 
            @PathVariable Long projectId) {
        
        log.info("获取系统数据量统计: projectId={}", projectId);
        Map<String, Object> stats = customerSystemService.getDataVolumeStatistics(projectId);
        return Result.success(stats);
    }

    /**
     * 批量更新系统状态
     */
    @Operation(summary = "批量更新状态", description = "批量更新系统状态")
    @PatchMapping("/batch-status")
    public Result<Void> batchUpdateStatus(
            @Parameter(description = "系统ID列表", required = true) 
            @RequestBody List<Long> ids,
            
            @Parameter(description = "状态", required = true) 
            @RequestParam String status) {
        
        log.info("批量更新系统状态: count={}, status={}", ids.size(), status);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        customerSystemService.batchUpdateStatus(ids, status, currentUserId);
        return Result.success("批量更新成功");
    }

    /**
     * 导入系统数据
     */
    @Operation(summary = "导入系统数据", description = "批量导入系统数据")
    @PostMapping("/import")
    public Result<Void> importSystems(
            @Parameter(description = "系统数据列表", required = true) 
            @RequestBody List<CustomerSystemDTO> systems) {
        
        log.info("导入系统数据: count={}", systems.size());
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        customerSystemService.importSystems(systems, currentUserId);
        return Result.success("导入成功");
    }

    /**
     * 导出系统数据
     */
    @Operation(summary = "导出系统数据", description = "导出系统数据")
    @PostMapping("/export")
    public Result<List<CustomerSystemVO>> exportSystems(
            @Parameter(description = "系统ID列表") 
            @RequestBody(required = false) List<Long> ids) {
        
        log.info("导出系统数据: ids={}", ids != null ? ids.size() : "all");
        List<CustomerSystemVO> systems = customerSystemService.exportSystems(ids);
        return Result.success(systems);
    }

    /**
     * 验证系统数据
     */
    @Operation(summary = "验证系统数据", description = "验证系统数据的有效性")
    @PostMapping("/validate")
    public Result<Map<String, Object>> validate(
            @Parameter(description = "系统数据", required = true) 
            @Valid @RequestBody CustomerSystemDTO dto) {
        
        log.info("验证系统数据: {}", dto.getSystemName());
        Map<String, Object> validationResult = customerSystemService.validateSystemData(dto);
        return Result.success(validationResult);
    }
}