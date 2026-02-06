package com.company.dataasset.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.company.dataasset.entity.CustomerSystem;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

/**
 * 客户系统Mapper接口
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-06
 */
@Mapper
public interface CustomerSystemMapper extends BaseMapper<CustomerSystem> {

    /**
     * 根据项目ID查询系统列表
     */
    List<CustomerSystem> selectByProjectId(@Param("projectId") Long projectId);

    /**
     * 根据系统编码查询
     */
    CustomerSystem selectBySystemCode(@Param("systemCode") String systemCode);

    /**
     * 分页查询系统列表
     */
    IPage<CustomerSystem> selectPage(Page<CustomerSystem> page,
                                     @Param("systemName") String systemName,
                                     @Param("projectId") Long projectId,
                                     @Param("systemType") String systemType,
                                     @Param("status") String status);

    /**
     * 更新系统状态
     */
    int updateStatus(@Param("id") Long id,
                     @Param("status") String status,
                     @Param("updatedBy") Long updatedBy);

    /**
     * 更新选中状态
     */
    int updateSelection(@Param("id") Long id,
                        @Param("isSelected") Integer isSelected,
                        @Param("selectionReason") String selectionReason,
                        @Param("updatedBy") Long updatedBy);

    /**
     * 逻辑删除
     */
    int deleteById(@Param("id") Long id,
                   @Param("updatedBy") Long updatedBy);

    /**
     * 获取项目系统统计
     */
    Map<String, Object> getProjectSystemStats(@Param("projectId") Long projectId);

    /**
     * 获取系统类型分布
     */
    List<Map<String, Object>> getSystemTypeDistribution(@Param("projectId") Long projectId);

    /**
     * 获取业务关键性分布
     */
    List<Map<String, Object>> getBusinessCriticalityDistribution(@Param("projectId") Long projectId);

    /**
     * 获取安全级别分布
     */
    List<Map<String, Object>> getSecurityLevelDistribution(@Param("projectId") Long projectId);

    /**
     * 查询需要评估的系统
     */
    List<CustomerSystem> selectNeedAssessmentSystems();

    /**
     * 查询已选中待挖掘的系统
     */
    List<CustomerSystem> selectSelectedSystems();

    /**
     * 生成系统编码
     */
    String generateSystemCode();

    /**
     * 批量更新系统状态
     */
    int batchUpdateStatus(@Param("ids") List<Long> ids,
                          @Param("status") String status,
                          @Param("updatedBy") Long updatedBy);

    /**
     * 根据业务领域查询系统
     */
    List<CustomerSystem> selectByBusinessDomain(@Param("businessDomain") String businessDomain);

    /**
     * 获取系统负责人统计
     */
    List<Map<String, Object>> getOwnerStatistics();

    /**
     * 查询即将需要安全评估的系统
     */
    List<CustomerSystem> selectNeedSecurityAssessment();

    /**
     * 获取系统数据量统计
     */
    Map<String, Object> getDataVolumeStatistics(@Param("projectId") Long projectId);
}