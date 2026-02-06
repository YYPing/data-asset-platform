package com.company.dataasset.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.company.dataasset.common.Result;
import com.company.dataasset.dto.CustomerDTO;
import com.company.dataasset.service.CustomerService;
import com.company.dataasset.vo.CustomerVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 客户Controller
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Slf4j
@RestController
@RequestMapping("/customers")
@RequiredArgsConstructor
public class CustomerController {

    private final CustomerService customerService;

    /**
     * 分页查询客户列表
     */
    @GetMapping
    public Result<Page<CustomerVO>> list(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String companyName,
            @RequestParam(required = false) String industry,
            @RequestParam(required = false) Integer status) {
        
        log.info("查询客户列表: pageNum={}, pageSize={}, companyName={}, industry={}, status={}",
                pageNum, pageSize, companyName, industry, status);
        
        Page<com.company.dataasset.entity.Customer> page = new Page<>(pageNum, pageSize);
        Page<CustomerVO> resultPage = customerService.queryCustomerPage(page, companyName, industry, status);
        
        return Result.success(resultPage);
    }

    /**
     * 获取客户详情
     */
    @GetMapping("/{id}")
    public Result<CustomerVO> getById(@PathVariable Long id) {
        log.info("获取客户详情: id={}", id);
        CustomerVO vo = customerService.getCustomerDetail(id);
        return Result.success(vo);
    }

    /**
     * 创建客户
     */
    @PostMapping
    public Result<CustomerVO> create(@Valid @RequestBody CustomerDTO dto) {
        log.info("创建客户: {}", dto.getCompanyName());
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        CustomerVO vo = customerService.createCustomer(dto, currentUserId);
        return Result.success("创建成功", vo);
    }

    /**
     * 更新客户
     */
    @PutMapping("/{id}")
    public Result<CustomerVO> update(@PathVariable Long id, @Valid @RequestBody CustomerDTO dto) {
        log.info("更新客户: id={}", id);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        CustomerVO vo = customerService.updateCustomer(id, dto, currentUserId);
        return Result.success("更新成功", vo);
    }

    /**
     * 删除客户
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        log.info("删除客户: id={}", id);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        customerService.deleteCustomer(id, currentUserId);
        return Result.success("删除成功");
    }

    /**
     * 切换客户状态
     */
    @PatchMapping("/{id}/status")
    public Result<Void> toggleStatus(@PathVariable Long id, @RequestParam Integer status) {
        log.info("切换客户状态: id={}, status={}", id, status);
        // TODO: 从认证信息中获取当前用户ID
        Long currentUserId = 1L; // 临时使用测试用户ID
        customerService.toggleStatus(id, status, currentUserId);
        String msg = status == 1 ? "启用成功" : "停用成功";
        return Result.success(msg);
    }

    /**
     * 生成客户编码
     */
    @GetMapping("/generate-code")
    public Result<String> generateCode() {
        String code = customerService.generateCustomerCode();
        return Result.success(code);
    }

    /**
     * 根据客户编码查询
     */
    @GetMapping("/code/{customerCode}")
    public Result<CustomerVO> getByCode(@PathVariable String customerCode) {
        log.info("根据客户编码查询: code={}", customerCode);
        CustomerVO vo = customerService.getCustomerByCode(customerCode);
        return Result.success(vo);
    }

    /**
     * 获取客户统计信息
     */
    @GetMapping("/stats")
    public Result<Object> getStats() {
        log.info("获取客户统计信息");
        Object stats = customerService.getCustomerStats();
        return Result.success(stats);
    }

    /**
     * 查询所有有效客户
     */
    @GetMapping("/active")
    public Result<List<CustomerVO>> getActiveCustomers() {
        log.info("查询所有有效客户");
        // TODO: 实现查询所有有效客户
        return Result.success(null);
    }
}
