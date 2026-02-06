package com.company.dataasset.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.company.dataasset.dto.CustomerSystemDTO;
import com.company.dataasset.entity.CustomerSystem;
import com.company.dataasset.vo.CustomerSystemVO;

import java.util.List;
import java.util.Map;

/**
 * 客户系统Service接口
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-06
 */
public interface CustomerSystemService extends IService<CustomerSystem> {

    /**
     * 创建客户系统
     */
    CustomerSystemVO createCustomerSystem(CustomerSystemDTO dto, Long createdBy);

    /**
     * 更新客户系统
     */
    CustomerSystemVO updateCustomerSystem(Long id, CustomerSystemDTO dto, Long updatedBy);

    /**
     * 获取客户系统详情
     */
    CustomerSystemVO getCustomerSystemDetail(Long id);

    /**
     * 删除客户系统
     */
    void deleteCustomerSystem(Long id, Long updatedBy);

    /**
     * 分页查询客户系统列表
     */
    IPage<CustomerSystemVO> queryCustomerSystemPage(Page<CustomerSystem> page,
                                                    String systemName,
                                                    Long projectId,
                                                    String systemType,
                                                    String status);

    /**
     * 根据项目ID查询系统列表
     */
    List<CustomerSystemVO> listByProjectId(Long projectId);

    /**
     * 根据系统编码查询
     */
    CustomerSystemVO getCustomerSystemByCode(String systemCode);

    /**
     * 更新系统状态
     */
    void updateStatus(Long id, String status, Long updatedBy);

    /**
     * 更新选中状态
     */
    void updateSelection(Long id, Integer isSelected, String selectionReason, Long updatedBy);

    /**
     * 批量更新系统状态
     */
    void batchUpdateStatus(List<Long> ids, String status, Long updatedBy);

    /**
     * 生成系统编码
     */
    String generateSystemCode();

    /**
     * 获取项目系统统计
     */
    Map<String, Object> getProjectSystemStats(Long projectId);

    /**
     * 获取系统类型分布
     */
    List<Map<String, Object>> getSystemTypeDistribution(Long projectId);

    /**
     * 获取业务关键性分布
     */
    List<Map<String, Object>> getBusinessCriticalityDistribution(Long projectId);

    /**
     * 获取安全级别分布
     */
    List<Map<String, Object>> getSecurityLevelDistribution(Long projectId);

    /**
     * 查询需要评估的系统
     */
    List<CustomerSystemVO> getNeedAssessmentSystems();

    /**
     * 查询已选中待挖掘的系统
     */
    List<CustomerSystemVO> getSelectedSystems();

    /**
     * 根据业务领域查询系统
     */
    List<CustomerSystemVO> listByBusinessDomain(String businessDomain);

    /**
     * 获取系统负责人统计
     */
    List<Map<String, Object>> getOwnerStatistics();

    /**
     * 查询即将需要安全评估的系统
     */
    List<CustomerSystemVO> getNeedSecurityAssessmentSystems();

    /**
     * 获取系统数据量统计
     */
    Map<String, Object> getDataVolumeStatistics(Long projectId);

    /**
     * 导入系统数据
     */
    void importSystems(List<CustomerSystemDTO> systems, Long createdBy);

    /**
     * 导出系统数据
     */
    List<CustomerSystemVO> exportSystems(List<Long> ids);

    /**
     * 验证系统数据
     */
    Map<String, Object> validateSystemData(CustomerSystemDTO dto);
}