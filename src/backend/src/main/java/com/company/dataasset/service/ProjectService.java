package com.company.dataasset.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.company.dataasset.dto.ProjectDTO;
import com.company.dataasset.entity.Project;
import com.company.dataasset.vo.ProjectVO;

import java.util.List;
import java.util.Map;

/**
 * 项目Service接口
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
public interface ProjectService extends IService<Project> {

    /**
     * 创建项目
     */
    ProjectVO createProject(ProjectDTO dto, Long createdBy);

    /**
     * 更新项目
     */
    ProjectVO updateProject(Long id, ProjectDTO dto, Long updatedBy);

    /**
     * 获取项目详情
     */
    ProjectVO getProjectDetail(Long id);

    /**
     * 删除项目
     */
    void deleteProject(Long id, Long updatedBy);

    /**
     * 生成项目编码
     */
    String generateProjectCode();

    /**
     * 更新项目进度
     */
    void updateProgress(Long id, Integer progress, Long updatedBy);

    /**
     * 更新项目阶段
     */
    void updatePhase(Long id, String phase, Long updatedBy);

    /**
     * 更新项目状态
     */
    void updateStatus(Long id, String status, Long updatedBy);

    /**
     * 根据客户ID查询项目列表
     */
    List<ProjectVO> listByCustomerId(Long customerId);

    /**
     * 分页查询项目列表
     */
    IPage<ProjectVO> queryProjectPage(Page<Project> page,
                                      String projectName,
                                      Long customerId,
                                      String status,
                                      String projectType);

    /**
     * 根据项目编码查询
     */
    ProjectVO getProjectByCode(String projectCode);

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
    List<ProjectVO> getExpiringProjects();

    /**
     * 查询需要关注的项目
     */
    List<ProjectVO> getNeedAttentionProjects();
}
