package com.company.dataasset.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.company.dataasset.entity.Project;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

/**
 * 项目Mapper接口
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Mapper
public interface ProjectMapper extends BaseMapper<Project> {

    /**
     * 根据项目编码查询
     */
    Project selectByProjectCode(@Param("projectCode") String projectCode);

    /**
     * 根据客户ID查询项目
     */
    List<Project> selectByCustomerId(@Param("customerId") Long customerId);

    /**
     * 查询所有进行中的项目
     */
    List<Project> selectAllActive();

    /**
     * 分页查询项目列表
     */
    IPage<Project> selectPage(Page<Project> page,
                              @Param("projectName") String projectName,
                              @Param("customerId") Long customerId,
                              @Param("status") String status,
                              @Param("projectType") String projectType);

    /**
     * 生成项目编码
     */
    String generateProjectCode();

    /**
     * 更新项目进度
     */
    int updateProgress(@Param("id") Long id,
                       @Param("progress") Integer progress,
                       @Param("updatedBy") Long updatedBy);

    /**
     * 更新项目阶段
     */
    int updatePhase(@Param("id") Long id,
                    @Param("currentPhase") String currentPhase,
                    @Param("updatedBy") Long updatedBy);

    /**
     * 更新项目状态
     */
    int updateStatus(@Param("id") Long id,
                     @Param("status") String status,
                     @Param("updatedBy") Long updatedBy);

    /**
     * 逻辑删除项目
     */
    int deleteById(@Param("id") Long id, @Param("updatedBy") Long updatedBy);

    /**
     * 获取项目统计信息
     */
    Map<String, Object> getProjectStats();

    /**
     * 获取客户的项目统计
     */
    List<Map<String, Object>> getCustomerProjectStats();

    /**
     * 获取项目阶段分布
     */
    List<Map<String, Object>> getPhaseDistribution();

    /**
     * 查询即将到期的项目
     */
    List<Project> selectExpiringProjects();

    /**
     * 查询需要关注的项目（进度低于50%且即将到期）
     */
    List<Project> selectNeedAttentionProjects();
}
