package com.company.dataasset.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.company.dataasset.common.BusinessException;
import com.company.dataasset.dto.CustomerDTO;
import com.company.dataasset.entity.Customer;
import com.company.dataasset.mapper.CustomerMapper;
import com.company.dataasset.service.CustomerService;
import com.company.dataasset.vo.CustomerVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

/**
 * 客户Service实现类
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CustomerServiceImpl extends ServiceImpl<CustomerMapper, Customer> implements CustomerService {

    /**
     * 创建客户
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public CustomerVO createCustomer(CustomerDTO dto, Long createdBy) {
        // 1. 校验公司名称唯一性
        if (baseMapper.existsByCompanyName(dto.getCompanyName(), null)) {
            throw new BusinessException("公司名称已存在");
        }

        // 2. 校验营业执照号唯一性
        if (dto.getBusinessLicense() != null && !dto.getBusinessLicense().isEmpty()
                && baseMapper.existsByBusinessLicense(dto.getBusinessLicense(), null)) {
            throw new BusinessException("营业执照号已存在");
        }

        // 3. 生成客户编码
        String customerCode = generateCustomerCode();

        // 4. 保存客户信息
        Customer customer = new Customer();
        BeanUtils.copyProperties(dto, customer);
        customer.setCustomerCode(customerCode);
        customer.setStatus(1);
        customer.setCreatedBy(createdBy);

        baseMapper.insert(customer);

        log.info("创建客户成功: id={}, code={}, name={}", 
                customer.getId(), customerCode, dto.getCompanyName());

        return convertToVO(customer);
    }

    /**
     * 更新客户
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public CustomerVO updateCustomer(Long id, CustomerDTO dto, Long updatedBy) {
        Customer customer = baseMapper.selectById(id);
        if (customer == null) {
            throw new BusinessException("客户不存在");
        }

        // 检查公司名称是否被其他客户使用
        if (baseMapper.existsByCompanyName(dto.getCompanyName(), id)) {
            throw new BusinessException("公司名称已存在");
        }

        // 检查营业执照号是否被其他客户使用
        if (dto.getBusinessLicense() != null && !dto.getBusinessLicense().isEmpty()
                && baseMapper.existsByBusinessLicense(dto.getBusinessLicense(), id)) {
            throw new BusinessException("营业执照号已存在");
        }

        BeanUtils.copyProperties(dto, customer, "id", "customerCode", "createdAt", "createdBy");
        customer.setUpdatedBy(updatedBy);
        baseMapper.updateById(customer);

        log.info("更新客户成功: id={}", id);

        return convertToVO(customer);
    }

    /**
     * 获取客户详情
     */
    @Override
    public CustomerVO getCustomerDetail(Long id) {
        Customer customer = baseMapper.selectById(id);
        if (customer == null) {
            throw new BusinessException("客户不存在");
        }
        return convertToVO(customer);
    }

    /**
     * 删除客户
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void deleteCustomer(Long id, Long updatedBy) {
        Customer customer = baseMapper.selectById(id);
        if (customer == null) {
            throw new BusinessException("客户不存在");
        }

        baseMapper.deleteById(id, updatedBy);
        log.info("删除客户成功: id={}", id);
    }

    /**
     * 生成客户编码
     * 格式: C + yyyyMM + 4位序号
     * 示例: C2024020001
     */
    @Override
    public String generateCustomerCode() {
        return baseMapper.generateCustomerCode();
    }

    /**
     * 切换客户状态
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void toggleStatus(Long id, Integer status, Long updatedBy) {
        Customer customer = baseMapper.selectById(id);
        if (customer == null) {
            throw new BusinessException("客户不存在");
        }

        baseMapper.updateStatus(id, status, updatedBy);
        log.info("切换客户状态成功: id={}, status={}", id, status);
    }

    /**
     * 分页查询客户列表
     */
    @Override
    public IPage<CustomerVO> queryCustomerPage(Page<Customer> page, 
                                               String companyName, 
                                               String industry, 
                                               Integer status) {
        IPage<Customer> customerPage = baseMapper.selectPage(page, companyName, industry, status);
        
        return customerPage.convert(this::convertToVO);
    }

    /**
     * 根据客户编码查询
     */
    @Override
    public CustomerVO getCustomerByCode(String customerCode) {
        Customer customer = baseMapper.selectByCustomerCode(customerCode);
        if (customer == null) {
            throw new BusinessException("客户不存在");
        }
        return convertToVO(customer);
    }

    /**
     * 获取客户统计信息
     */
    @Override
    public Map<String, Object> getCustomerStats() {
        return baseMapper.getCustomerStats();
    }

    /**
     * 转换为VO
     */
    private CustomerVO convertToVO(Customer customer) {
        CustomerVO vo = new CustomerVO();
        BeanUtils.copyProperties(customer, vo);
        return vo;
    }
}
