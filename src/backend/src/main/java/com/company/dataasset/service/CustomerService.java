package com.company.dataasset.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.company.dataasset.dto.CustomerDTO;
import com.company.dataasset.entity.Customer;
import com.company.dataasset.vo.CustomerVO;

import java.util.List;
import java.util.Map;

/**
 * 客户Service接口
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
public interface CustomerService extends IService<Customer> {

    /**
     * 创建客户
     */
    CustomerVO createCustomer(CustomerDTO dto, Long createdBy);

    /**
     * 更新客户
     */
    CustomerVO updateCustomer(Long id, CustomerDTO dto, Long updatedBy);

    /**
     * 获取客户详情
     */
    CustomerVO getCustomerDetail(Long id);

    /**
     * 删除客户
     */
    void deleteCustomer(Long id, Long updatedBy);

    /**
     * 生成客户编码
     */
    String generateCustomerCode();

    /**
     * 切换客户状态
     */
    void toggleStatus(Long id, Integer status, Long updatedBy);

    /**
     * 分页查询客户列表
     */
    IPage<CustomerVO> queryCustomerPage(Page<Customer> page, 
                                        String companyName, 
                                        String industry, 
                                        Integer status);

    /**
     * 根据客户编码查询
     */
    CustomerVO getCustomerByCode(String customerCode);

    /**
     * 获取客户统计信息
     */
    Map<String, Object> getCustomerStats();
}
