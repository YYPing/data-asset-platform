package com.company.dataasset.service.impl;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.company.dataasset.common.BusinessException;
import com.company.dataasset.dto.CustomerSystemDTO;
import com.company.dataasset.entity.CustomerSystem;
import com.company.dataasset.entity.Project;
import com.company.dataasset.mapper.CustomerSystemMapper;
import com.company.dataasset.mapper.ProjectMapper;
import com.company.dataasset.service.CustomerSystemService;
import com.company.dataasset.vo.CustomerSystemVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 客户系统Service实现类
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-06
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CustomerSystemServiceImpl extends ServiceImpl<CustomerSystemMapper, CustomerSystem> implements CustomerSystemService {

    private final ProjectMapper projectMapper;

    /**
     * 创建客户系统
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public CustomerSystemVO createCustomerSystem(CustomerSystemDTO dto, Long createdBy) {
        // 1. 验证项目是否存在
        Project project = projectMapper.selectById(dto.getProjectId());
        if (project == null) {
            throw new BusinessException("项目不存在");
        }

        // 2. 生成系统编码
        String systemCode = generateSystemCode();

        // 3. 保存系统信息
        CustomerSystem system = new CustomerSystem();
        BeanUtils.copyProperties(dto, system);
        system.setSystemCode(systemCode);
        system.setStatus("active");
        system.setIsSelected(0);
        system.setCreatedAt(LocalDateTime.now());

        baseMapper.insert(system);

        log.info("创建客户系统成功: id={}, code={}, name={}", 
                system.getId(), systemCode, dto.getSystemName());

        return convertToVO(system, project);
    }

    /**
     * 更新客户系统
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public CustomerSystemVO updateCustomerSystem(Long id, CustomerSystemDTO dto, Long updatedBy) {
        // 1. 验证系统是否存在
        CustomerSystem system = baseMapper.selectById(id);
        if (system == null) {
            throw new BusinessException("客户系统不存在");
        }

        // 2. 验证项目是否存在
        Project project = projectMapper.selectById(dto.getProjectId());
        if (project == null) {
            throw new BusinessException("项目不存在");
        }

        // 3. 更新系统信息
        BeanUtils.copyProperties(dto, system, "id", "systemCode", "createdAt");
        system.setUpdatedAt(LocalDateTime.now());

        baseMapper.updateById(system);

        log.info("更新客户系统成功: id={}", id);

        return convertToVO(system, project);
    }

    /**
     * 获取客户系统详情
     */
    @Override
    public CustomerSystemVO getCustomerSystemDetail(Long id) {
        CustomerSystem system = baseMapper.selectById(id);
        if (system == null) {
            throw new BusinessException("客户系统不存在");
        }

        Project project = projectMapper.selectById(system.getProjectId());
        if (project == null) {
            throw new BusinessException("关联项目不存在");
        }

        return convertToVO(system, project);
    }

    /**
     * 删除客户系统
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void deleteCustomerSystem(Long id, Long updatedBy) {
        CustomerSystem system = baseMapper.selectById(id);
        if (system == null) {
            throw new BusinessException("客户系统不存在");
        }

        baseMapper.deleteById(id, updatedBy);
        log.info("删除客户系统成功: id={}", id);
    }

    /**
     * 分页查询客户系统列表
     */
    @Override
    public IPage<CustomerSystemVO> queryCustomerSystemPage(Page<CustomerSystem> page,
                                                           String systemName,
                                                           Long projectId,
                                                           String systemType,
                                                           String status) {
        IPage<CustomerSystem> systemPage = baseMapper.selectPage(page, systemName, projectId, systemType, status);
        
        return systemPage.convert(system -> {
            Project project = projectMapper.selectById(system.getProjectId());
            return convertToVO(system, project);
        });
    }

    /**
     * 根据项目ID查询系统列表
     */
    @Override
    public List<CustomerSystemVO> listByProjectId(Long projectId) {
        List<CustomerSystem> systems = baseMapper.selectByProjectId(projectId);
        Project project = projectMapper.selectById(projectId);
        
        return systems.stream()
                .map(system -> convertToVO(system, project))
                .collect(Collectors.toList());
    }

    /**
     * 根据系统编码查询
     */
    @Override
    public CustomerSystemVO getCustomerSystemByCode(String systemCode) {
        CustomerSystem system = baseMapper.selectBySystemCode(systemCode);
        if (system == null) {
            throw new BusinessException("客户系统不存在");
        }
        
        Project project = projectMapper.selectById(system.getProjectId());
        return convertToVO(system, project);
    }

    /**
     * 更新系统状态
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updateStatus(Long id, String status, Long updatedBy) {
        CustomerSystem system = baseMapper.selectById(id);
        if (system == null) {
            throw new BusinessException("客户系统不存在");
        }

        // 验证状态是否有效
        List<String> validStatuses = List.of("active", "inactive", "maintenance", "decommissioned");
        if (!validStatuses.contains(status)) {
            throw new BusinessException("无效的系统状态");
        }

        baseMapper.updateStatus(id, status, updatedBy);
        log.info("更新系统状态成功: id={}, status={}", id, status);
    }

    /**
     * 更新选中状态
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updateSelection(Long id, Integer isSelected, String selectionReason, Long updatedBy) {
        CustomerSystem system = baseMapper.selectById(id);
        if (system == null) {
            throw new BusinessException("客户系统不存在");
        }

        baseMapper.updateSelection(id, isSelected, selectionReason, updatedBy);
        log.info("更新系统选中状态成功: id={}, isSelected={}", id, isSelected);
    }

    /**
     * 批量更新系统状态
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void batchUpdateStatus(List<Long> ids, String status, Long updatedBy) {
        if (ids == null || ids.isEmpty()) {
            throw new BusinessException("系统ID列表不能为空");
        }

        // 验证状态是否有效
        List<String> validStatuses = List.of("active", "inactive", "maintenance", "decommissioned");
        if (!validStatuses.contains(status)) {
            throw new BusinessException("无效的系统状态");
        }

        baseMapper.batchUpdateStatus(ids, status, updatedBy);
        log.info("批量更新系统状态成功: count={}, status={}", ids.size(), status);
    }

    /**
     * 生成系统编码
     */
    @Override
    public String generateSystemCode() {
        return baseMapper.generateSystemCode();
    }

    /**
     * 获取项目系统统计
     */
    @Override
    public Map<String, Object> getProjectSystemStats(Long projectId) {
        return baseMapper.getProjectSystemStats(projectId);
    }

    /**
     * 获取系统类型分布
     */
    @Override
    public List<Map<String, Object>> getSystemTypeDistribution(Long projectId) {
        return baseMapper.getSystemTypeDistribution(projectId);
    }

    /**
     * 获取业务关键性分布
     */
    @Override
    public List<Map<String, Object>> getBusinessCriticalityDistribution(Long projectId) {
        return baseMapper.getBusinessCriticalityDistribution(projectId);
    }

    /**
     * 获取安全级别分布
     */
    @Override
    public List<Map<String, Object>> getSecurityLevelDistribution(Long projectId) {
        return baseMapper.getSecurityLevelDistribution(projectId);
    }

    /**
     * 查询需要评估的系统
     */
    @Override
    public List<CustomerSystemVO> getNeedAssessmentSystems() {
        List<CustomerSystem> systems = baseMapper.selectNeedAssessmentSystems();
        
        return systems.stream()
                .map(system -> {
                    Project project = projectMapper.selectById(system.getProjectId());
                    return convertToVO(system, project);
                })
                .collect(Collectors.toList());
    }

    /**
     * 查询已选中待挖掘的系统
     */
    @Override
    public List<CustomerSystemVO> getSelectedSystems() {
        List<CustomerSystem> systems = baseMapper.selectSelectedSystems();
        
        return systems.stream()
                .map(system -> {
                    Project project = projectMapper.selectById(system.getProjectId());
                    return convertToVO(system, project);
                })
                .collect(Collectors.toList());
    }

    /**
     * 根据业务领域查询系统
     */
    @Override
    public List<CustomerSystemVO> listByBusinessDomain(String businessDomain) {
        List<CustomerSystem> systems = baseMapper.selectByBusinessDomain(businessDomain);
        
        return systems.stream()
                .map(system -> {
                    Project project = projectMapper.selectById(system.getProjectId());
                    return convertToVO(system, project);
                })
                .collect(Collectors.toList());
    }

    /**
     * 获取系统负责人统计
     */
    @Override
    public List<Map<String, Object>> getOwnerStatistics() {
        return baseMapper.getOwnerStatistics();
    }

    /**
     * 查询即将需要安全评估的系统
     */
    @Override
    public List<CustomerSystemVO> getNeedSecurityAssessmentSystems() {
        List<CustomerSystem> systems = baseMapper.selectNeedSecurityAssessment();
        
        return systems.stream()
                .map(system -> {
                    Project project = projectMapper.selectById(system.getProjectId());
                    return convertToVO(system, project);
                })
                .collect(Collectors.toList());
    }

    /**
     * 获取系统数据量统计
     */
    @Override
    public Map<String, Object> getDataVolumeStatistics(Long projectId) {
        return baseMapper.getDataVolumeStatistics(projectId);
    }

    /**
     * 导入系统数据
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void importSystems(List<CustomerSystemDTO> systems, Long createdBy) {
        if (systems == null || systems.isEmpty()) {
            throw new BusinessException("导入数据不能为空");
        }

        int successCount = 0;
        int failCount = 0;

        for (CustomerSystemDTO dto : systems) {
            try {
                createCustomerSystem(dto, createdBy);
                successCount++;
            } catch (Exception e) {
                log.error("导入系统数据失败: {}", dto.getSystemName(), e);
                failCount++;
            }
        }

        log.info("系统数据导入完成: 成功={}, 失败={}", successCount, failCount);
    }

    /**
     * 导出系统数据
     */
    @Override
    public List<CustomerSystemVO> exportSystems(List<Long> ids) {
        if (ids == null || ids.isEmpty()) {
            // 导出所有系统
            List<CustomerSystem> systems = baseMapper.selectList(null);
            return systems.stream()
                    .map(system -> {
                        Project project = projectMapper.selectById(system.getProjectId());
                        return convertToVO(system, project);
                    })
                    .collect(Collectors.toList());
        } else {
            // 导出指定ID的系统
            return ids.stream()
                    .map(this::getCustomerSystemDetail)
                    .collect(Collectors.toList());
        }
    }

    /**
     * 验证系统数据
     */
    @Override
    public Map<String, Object> validateSystemData(CustomerSystemDTO dto) {
        // TODO: 实现详细的系统数据验证逻辑
        // 包括：必填字段检查、数据格式验证、业务规则验证等
        return Map.of(
            "valid", true,
            "message", "数据验证通过",
            "errors", List.of()
        );
    }

    /**
     * 转换为VO对象
     */
    private CustomerSystemVO convertToVO(CustomerSystem system, Project project) {
        CustomerSystemVO vo = new CustomerSystemVO();
        BeanUtils.copyProperties(system, vo);
        
        // 设置项目信息
        if (project != null) {
            vo.setProjectName(project.getProjectName());
        }
        
        // 设置状态名称
        vo.setStatusName(getStatusName(system.getStatus()));
        
        // 设置系统类型名称
        vo.setSystemTypeName(getSystemTypeName(system.getSystemType()));
        
        // 设置优先级名称
        vo.setPriorityLevelName(getPriorityLevelName(system.getPriorityLevel()));
        
        // 设置业务关键性描述
        vo.setBusinessCriticalityDesc(getBusinessCriticalityDesc(system.getBusinessCriticality()));
        
        // 设置是否需要评估标志
        vo.setNeedAssessment(checkNeedAssessment(system));
        
        // 设置是否需要安全评估标志
        vo.setNeedSecurityAssessment(checkNeedSecurityAssessment(system));
        
        return vo;
    }

    /**
     * 获取状态名称
     */
    private String getStatusName(String status) {
        if (status == null) return "未知";
        
        return switch (status) {
            case "active" -> "活跃";
            case "inactive" -> "停用";
            case "maintenance" -> "维护中";
            case "decommissioned" -> "已下线";
            default -> "未知";
        };
    }

    /**
     * 获取系统类型名称
     */
    private String getSystemTypeName(String systemType) {
        if (systemType == null) return "未知";
        
        return switch (systemType) {
            case "transactional" -> "交易型";
            case "analytical" -> "分析型";
            case "operational" -> "操作型";
            case "reporting" -> "报表型";
            case "external" -> "外部系统";
            default -> "未知";
        };
    }

    /**
     * 获取优先级名称
     */
    private String getPriorityLevelName(String priorityLevel) {
        if (priorityLevel == null) return "普通";
        
        return switch (priorityLevel) {
            case "low" -> "低";
            case "medium" -> "中";
            case "high" -> "高";
            case "critical" -> "紧急";
            default -> "普通";
        };
    }

    /**
     * 获取业务关键性描述
     */
    private String getBusinessCriticalityDesc(Integer businessCriticality) {
        if (businessCriticality == null) return "未评估";
        
        return switch (businessCriticality) {
            case 1 -> "非关键";
            case 2 -> "较低";
            case 3 -> "中等";
            case 4 -> "重要";
            case 5 -> "关键";
            default -> "未评估";
        };
    }

    /**
     * 检查是否需要评估
     */
    private Boolean checkNeedAssessment(CustomerSystem system) {
        // TODO: 实现具体的评估需求判断逻辑
        // 例如：根据最后评估时间、业务关键性等判断
        return system.getIsSelected() == 1;
    }

    /**
     * 检查是否需要安全评估
     */
    private Boolean checkNeedSecurityAssessment(CustomerSystem system) {
        if (system.getLastSecurityAssessment() == null) {
            return true;
        }
        
        // 如果上次安全评估超过1年，则需要重新评估
        return system.getLastSecurityAssessment().isBefore(
            java.time.LocalDate.now().minusYears(1)
        );
    }
}