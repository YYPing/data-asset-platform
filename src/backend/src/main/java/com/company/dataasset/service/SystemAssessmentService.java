package com.company.dataasset.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.company.dataasset.dto.SystemAssessmentDTO;
import com.company.dataasset.entity.SystemAssessment;
import com.company.dataasset.vo.SystemAssessmentVO;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * 系统价值评估Service接口
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-06
 */
public interface SystemAssessmentService extends IService<SystemAssessment> {

    /**
     * 创建系统评估
     */
    SystemAssessmentVO createAssessment(SystemAssessmentDTO dto, Long assessorId);

    /**
     * 更新系统评估
     */
    SystemAssessmentVO updateAssessment(Long id, SystemAssessmentDTO dto, Long updatedBy);

    /**
     * 获取评估详情
     */
    SystemAssessmentVO getAssessmentDetail(Long id);

    /**
     * 删除评估
     */
    void deleteAssessment(Long id, Long updatedBy);

    /**
     * 分页查询评估列表
     */
    IPage<SystemAssessmentVO> queryAssessmentPage(Page<SystemAssessment> page,
                                                  String systemName,
                                                  Long projectId,
                                                  String reviewStatus,
                                                  String priorityLevel);

    /**
     * 根据系统ID查询评估
     */
    SystemAssessmentVO getAssessmentBySystemId(Long systemId);

    /**
     * 根据项目ID查询评估列表
     */
    List<SystemAssessmentVO> listByProjectId(Long projectId);

    /**
     * 更新审核状态
     */
    void updateReviewStatus(Long id, String reviewStatus, Long reviewerId, String reviewComments);

    /**
     * 批量更新审核状态
     */
    void batchUpdateReviewStatus(List<Long> ids, String reviewStatus, Long reviewerId);

    /**
     * 计算系统平均评分
     */
    Map<String, Object> calculateAverageScores(Long systemId);

    /**
     * 获取项目评估统计
     */
    Map<String, Object> getProjectAssessmentStats(Long projectId);

    /**
     * 获取优先级分布
     */
    List<Map<String, Object>> getPriorityDistribution(Long projectId);

    /**
     * 获取评分区间分布
     */
    List<Map<String, Object>> getScoreDistribution(Long projectId);

    /**
     * 获取投资回报率排名
     */
    List<Map<String, Object>> getRoiRanking(Integer limit);

    /**
     * 获取实施成本排名
     */
    List<Map<String, Object>> getCostRanking(Integer limit);

    /**
     * 获取预计收益排名
     */
    List<Map<String, Object>> getBenefitRanking(Integer limit);

    /**
     * 查询需要审核的评估
     */
    List<SystemAssessmentVO> getNeedReviewAssessments();

    /**
     * 查询已审核通过的评估
     */
    List<SystemAssessmentVO> getApprovedAssessments();

    /**
     * 查询即将到期的评估
     */
    List<SystemAssessmentVO> getExpiringAssessments();

    /**
     * 根据评估日期范围查询
     */
    List<SystemAssessmentVO> listByAssessmentDateRange(LocalDate startDate, LocalDate endDate);

    /**
     * 获取评估人统计
     */
    List<Map<String, Object>> getAssessorStatistics();

    /**
     * 获取审核人统计
     */
    List<Map<String, Object>> getReviewerStatistics();

    /**
     * 查询高风险评估
     */
    List<SystemAssessmentVO> getHighRiskAssessments(BigDecimal threshold);

    /**
     * 查询高价值评估
     */
    List<SystemAssessmentVO> getHighValueAssessments(BigDecimal threshold);

    /**
     * 查询推荐立即挖掘的评估
     */
    List<SystemAssessmentVO> getRecommendedForImmediateMining();

    /**
     * 查询推荐优先挖掘的评估
     */
    List<SystemAssessmentVO> getRecommendedForPriorityMining();

    /**
     * 更新评估分数
     */
    void updateScores(Long id,
                      BigDecimal businessValueScore,
                      BigDecimal dataQualityScore,
                      BigDecimal complianceRiskScore,
                      BigDecimal technicalFeasibilityScore,
                      BigDecimal totalScore);

    /**
     * 更新投资回报分析
     */
    void updateRoiAnalysis(Long id,
                           BigDecimal estimatedRoi,
                           BigDecimal estimatedBenefit,
                           BigDecimal estimatedCost,
                           Integer estimatedEffortDays);

    /**
     * 查询相似系统评估
     */
    List<SystemAssessmentVO> getSimilarAssessments(String systemType, Integer limit);

    /**
     * 获取评估趋势分析
     */
    List<Map<String, Object>> getAssessmentTrend(Long projectId, Integer days);

    /**
     * 自动评估系统价值
     */
    SystemAssessmentVO autoAssessSystem(Long systemId, Long assessorId);

    /**
     * 批量自动评估
     */
    void batchAutoAssess(List<Long> systemIds, Long assessorId);

    /**
     * 生成评估报告
     */
    Map<String, Object> generateAssessmentReport(Long assessmentId);

    /**
     * 导出评估数据
     */
    List<SystemAssessmentVO> exportAssessments(List<Long> ids);

    /**
     * 导入评估数据
     */
    void importAssessments(List<SystemAssessmentDTO> assessments, Long createdBy);

    /**
     * 验证评估数据
     */
    Map<String, Object> validateAssessmentData(SystemAssessmentDTO dto);

    /**
     * 重新计算综合评分
     */
    void recalculateTotalScore(Long assessmentId);

    /**
     * 获取评估建议
     */
    Map<String, Object> getAssessmentRecommendation(Long assessmentId);
}