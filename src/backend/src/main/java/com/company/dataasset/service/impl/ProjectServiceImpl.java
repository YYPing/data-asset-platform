package com.company.dataasset.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.company.dataasset.common.BusinessException;
import com.company.dataasset.dto.ProjectDTO;
import com.company.dataasset.entity.Customer;
import com.company.dataasset.entity.Project;
import com.company.dataasset.mapper.CustomerMapper;
import com.company.dataasset.mapper.ProjectMapper;
import com.company.dataasset.service.ProjectService;
import com.company.dataasset.vo.ProjectVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 项目Service实现类
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-05
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ProjectServiceImpl extends ServiceImpl<ProjectMapper, Project> implements ProjectService {

    private final CustomerMapper customerMapper;

    /**
     * 创建项目
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public ProjectVO createProject(ProjectDTO dto, Long createdBy) {
        // 1. 校验客户是否存在
        Customer customer = customerMapper.selectById(dto.getCustomerId());
        if (customer == null) {
            throw new BusinessException("客户不存在");
        }

        // 2. 生成项目编码
        String projectCode = baseMapper.generateProjectCode();

        // 3. 保存项目信息
        Project project = new Project();
        BeanUtils.copyProperties(dto, project);
        project.setProjectCode(projectCode);
        project.setCurrentPhase("system_registry");
        project.setStatus("active");
        project.setProgress(0);
        project.setCreatedBy(createdBy);

        baseMapper.insert(project);

        log.info("创建项目成功: id={}, code={}, name={}", 
                project.getId(), projectCode, dto.getProjectName());

        return convertToVO(project, customer);
    }

    /**
     * 更新项目
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public ProjectVO updateProject(Long id, ProjectDTO dto, Long updatedBy) {
        Project project = baseMapper.selectById(id);
        if (project == null) {
            throw new BusinessException("项目不存在");
        }

        // 校验客户是否存在
        Customer customer = customerMapper.selectById(dto.getCustomerId());
        if (customer == null) {
            throw new BusinessException("客户不存在");
        }

        BeanUtils.copyProperties(dto, project, "id", "projectCode", "currentPhase", "status", "progress");
        project.setUpdatedBy(updatedBy);
        baseMapper.updateById(project);

        log.info("更新项目成功: id={}", id);

        return convertToVO(project, customer);
    }

    /**
     * 获取项目详情
     */
    @Override
    public ProjectVO getProjectDetail(Long id) {
        Project project = baseMapper.selectById(id);
        if (project == null) {
            throw new BusinessException("项目不存在");
        }

        Customer customer = customerMapper.selectById(project.getCustomerId());
        if (customer == null) {
            throw new BusinessException("关联客户不存在");
        }

        return convertToVO(project, customer);
    }

    /**
     * 删除项目
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void deleteProject(Long id, Long updatedBy) {
        Project project = baseMapper.selectById(id);
        if (project == null) {
            throw new BusinessException("项目不存在");
        }

        baseMapper.deleteById(id, updatedBy);
        log.info("删除项目成功: id={}", id);
    }

    /**
     * 生成项目编码
     * 格式: P + yyyyMM + 4位序号
     * 示例: P2024020001
     */
    @Override
    public String generateProjectCode() {
        return baseMapper.generateProjectCode();
    }

    /**
     * 更新项目进度
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updateProgress(Long id, Integer progress, Long updatedBy) {
        Project project = baseMapper.selectById(id);
        if (project == null) {
            throw new BusinessException("项目不存在");
        }

        if (progress < 0 || progress > 100) {
            throw new BusinessException("进度值必须在0-100之间");
        }

        baseMapper.updateProgress(id, progress, updatedBy);
        log.info("更新项目进度: id={}, progress={}%", id, progress);
    }

    /**
     * 更新项目阶段
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updatePhase(Long id, String phase, Long updatedBy) {
        Project project = baseMapper.selectById(id);
        if (project == null) {
            throw new BusinessException("项目不存在");
        }

        // 验证阶段是否有效
        List<String> validPhases = List.of(
            "system_registry", "assessment", "data_import", 
            "compliance", "valuation", "reporting", "completed"
        );

        if (!validPhases.contains(phase)) {
            throw new BusinessException("无效的项目阶段");
        }

        baseMapper.updatePhase(id, phase, updatedBy);
        log.info("更新项目阶段: id={}, phase={}", id, phase);
    }

    /**
     * 更新项目状态
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updateStatus(Long id, String status, Long updatedBy) {
        Project project = baseMapper.selectById(id);
        if (project == null) {
            throw new BusinessException("项目不存在");
        }

        // 验证状态是否有效
        List<String> validStatuses = List.of("active", "completed", "cancelled", "on_hold");
        if (!validStatuses.contains(status)) {
            throw new BusinessException("无效的项目状态");
        }

        baseMapper.updateStatus(id, status, updatedBy);
        log.info("更新项目状态: id={}, status={}", id, status);
    }

    /**
     * 根据客户ID查询项目列表
     */
    @Override
    public List<ProjectVO> listByCustomerId(Long customerId) {
        List<Project> projects = baseMapper.selectByCustomerId(customerId);
        Customer customer = customerMapper.selectById(customerId);
        
        return projects.stream()
                .map(project -> convertToVO(project, customer))
                .collect(Collectors.toList());
    }

    /**
     * 分页查询项目列表
     */
    @Override
    public IPage<ProjectVO> queryProjectPage(Page<Project> page,
                                             String projectName,
                                             Long customerId,
                                             String status,
                                             String projectType) {
        IPage<Project> projectPage = baseMapper.selectPage(page, projectName, customerId, status, projectType);
        
        return projectPage.convert(project -> {
            Customer customer = customerMapper.selectById(project.getCustomerId());
            return convertToVO(project, customer);
        });
    }

    /**
     * 根据项目编码查询
     */
    @Override
    public ProjectVO getProjectByCode(String projectCode) {
        Project project = baseMapper.selectByProjectCode(projectCode);
        if (project == null) {
            throw new BusinessException("项目不存在");
        }
        
        Customer customer = customerMapper.selectById(project.getCustomerId());
        return convertToVO(project, customer);
    }

    /**
     * 获取项目统计信息
     */
    @Override
    public Map<String, Object> getProjectStats() {
        return baseMapper.getProjectStats();
    }

    /**
     * 获取客户的项目统计
     */
    @Override
    public List<Map<String, Object>> getCustomerProjectStats() {
        return baseMapper.getCustomerProjectStats();
    }

    /**
     * 获取项目阶段分布
     */
    @Override
    public List<Map<String, Object>> getPhaseDistribution() {
        return baseMapper.getPhaseDistribution();
    }

    /**
     * 查询即将到期的项目
     */
    @Override
    public List<ProjectVO> getExpiringProjects() {
        List<Project> projects = baseMapper.selectExpiringProjects();
        return projects.stream()
                .map(project -> {
                    Customer customer = customerMapper.selectById(project.getCustomerId());
                    return convertToVO(project, customer);
                })
                .collect(Collectors.toList());
    }

    /**
     * 查询需要关注的项目
     */
    @Override
    public List<ProjectVO> getNeedAttentionProjects() {
        List<Project> projects = baseMapper.selectNeedAttentionProjects();
        return projects.stream()
                .map(project -> {
                    Customer customer = customerMapper.selectById(project.getCustomerId());
                    return convertToVO(project, customer);
                })
                .collect(Collectors.toList());
    }

    /**
     * 转换为VO
     */
    private ProjectVO convertToVO(Project project, Customer customer) {
        ProjectVO vo = new ProjectVO();
        BeanUtils.copyProperties(project, vo);
        vo.setCustomerName(customer.getCompanyName());
        // TODO: 设置项目经理姓名
        // TODO: 查询系统数量和评估数量
        return vo;
    }
}
