package com.company.dataasset.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.company.dataasset.entity.Customer;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

/**
 * 客户Mapper接口
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Mapper
public interface CustomerMapper extends BaseMapper<Customer> {

    /**
     * 根据客户编码查询
     */
    Customer selectByCustomerCode(@Param("customerCode") String customerCode);

    /**
     * 根据公司名称模糊查询
     */
    List<Customer> selectByCompanyName(@Param("companyName") String companyName);

    /**
     * 根据行业查询
     */
    List<Customer> selectByIndustry(@Param("industry") String industry);

    /**
     * 查询所有有效客户
     */
    List<Customer> selectAllActive();

    /**
     * 分页查询客户列表
     */
    IPage<Customer> selectPage(Page<Customer> page, 
                               @Param("companyName") String companyName,
                               @Param("industry") String industry,
                               @Param("status") Integer status);

    /**
     * 生成客户编码
     */
    String generateCustomerCode();

    /**
     * 检查公司名称是否已存在
     */
    Boolean existsByCompanyName(@Param("companyName") String companyName, 
                                @Param("excludeId") Long excludeId);

    /**
     * 检查营业执照号是否已存在
     */
    Boolean existsByBusinessLicense(@Param("businessLicense") String businessLicense,
                                    @Param("excludeId") Long excludeId);

    /**
     * 逻辑删除客户
     */
    int deleteById(@Param("id") Long id, @Param("updatedBy") Long updatedBy);

    /**
     * 更新客户状态
     */
    int updateStatus(@Param("id") Long id, 
                     @Param("status") Integer status,
                     @Param("updatedBy") Long updatedBy);

    /**
     * 获取客户统计信息
     */
    Map<String, Object> getCustomerStats();
}
