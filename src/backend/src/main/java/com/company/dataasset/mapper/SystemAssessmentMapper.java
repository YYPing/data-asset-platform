package com.company.dataasset.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.company.dataasset.entity.SystemAssessment;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * 系统价值评估Mapper接口
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2026-02-06
 */
@Mapper
public interface SystemAssessmentMapper extends BaseMapper<SystemAssessment> {

    /**
     * 根据系统ID查询评估记录
     */
    SystemAssessment selectBySystemId(@Param("systemId") Long systemId);

    /**
     * 根据项目ID查询评估列表
     */
    List<SystemAssessment> selectByProjectId(@Param("projectId") Long projectId);

    /**
     * 分页查询评估记录
     */
    IPage<SystemAssessment> selectPage(Page<SystemAssessment> page,
                                       @Param("systemName") String systemName,
                                       @Param("projectId") Long projectId,
                                       @Param("reviewStatus") String reviewStatus,
                                       @Param("priorityLevel") String priorityLevel);

    /**
     * 根据综合评分排序查询
     */
    List<SystemAssessment> selectByTotalScoreDesc(@Param("limit") Integer limit);

    /**
     * 查询需要审核的评估记录
     */
    List<SystemAssessment> selectNeedReview();

    /**
     * 查询已审核通过的评估记录
     */
    List<SystemAssessment> selectApproved();

    /**
     * 更新审核状态
     */
    int updateReviewStatus(@Param("id") Long id,
                           @Param("reviewStatus") String reviewStatus,
                           @Param("reviewerId") Long reviewerId,
                           @Param("reviewComments") String reviewComments);

    /**
     * 批量更新审核状态
     */
    int batchUpdateReviewStatus(@Param("ids") List<Long> ids,
                                @Param("reviewStatus") String reviewStatus,
                                @Param("reviewerId") Long reviewerId);

    /**
     * 计算系统平均评分
     */
    Map<String, Object> calculateAverageScores(@Param("systemId") Long systemId);

    /**
     * 获取项目评估统计
     */
    Map<String, Object> getProjectAssessmentStats(@Param("projectId") Long projectId);

    /**
     * 获取优先级分布
     */
    List<Map<String, Object>> getPriorityDistribution(@Param("projectId") Long projectId);

    /**
     * 获取评分区间分布
     */
    List<Map<String, Object>> getScoreDistribution(@Param("projectId") Long projectId);

    /**
     * 获取投资回报率排名
     */
    List<Map<String, Object>> getRoiRanking(@Param("limit") Integer limit);

    /**
     * 获取实施成本排名
     */
    List<Map<String, Object>> getCostRanking(@Param("limit") Integer limit);

    /**
     * 获取预计收益排名
     */
    List<Map<String, Object>> getBenefitRanking(@Param("limit") Integer limit);

    /**
     * 查询即将到期的评估（一年未更新）
     */
    List<SystemAssessment> selectExpiringAssessments();

    /**
     * 根据评估日期范围查询
     */
    List<SystemAssessment> selectByAssessmentDateRange(@Param("startDate") LocalDate startDate,
                                                       @Param("endDate") LocalDate endDate);

    /**
     * 获取评估人统计
     */
    List<Map<String, Object>> getAssessorStatistics();

    /**
     * 获取审核人统计
     */
    List<Map<String, Object>> getReviewerStatistics();

    /**
     * 查询高风险评估（合规风险高）
     */
    List<SystemAssessment> selectHighRiskAssessments(@Param("threshold") BigDecimal threshold);

    /**
     * 查询高价值评估（综合评分高）
     */
    List<SystemAssessment> selectHighValueAssessments(@Param("threshold") BigDecimal threshold);

    /**
     * 查询推荐立即挖掘的评估
     */
    List<SystemAssessment> selectRecommendedForImmediateMining();

    /**
     * 查询推荐优先挖掘的评估
     */
    List<SystemAssessment> selectRecommendedForPriorityMining();

    /**
     * 更新评估分数
     */
    int updateScores(@Param("id") Long id,
                     @Param("businessValueScore") BigDecimal businessValueScore,
                     @Param("dataQualityScore") BigDecimal dataQualityScore,
                     @Param("complianceRiskScore") BigDecimal complianceRiskScore,
                     @Param("technicalFeasibilityScore") BigDecimal technicalFeasibilityScore,
                     @Param("totalScore") BigDecimal totalScore);

    /**
     * 更新投资回报分析
     */
    int updateRoiAnalysis(@Param("id") Long id,
                          @Param("estimatedRoi") BigDecimal estimatedRoi,
                          @Param("estimatedBenefit") BigDecimal estimatedBenefit,
                          @Param("estimatedCost") BigDecimal estimatedCost,
                          @Param("estimatedEffortDays") Integer estimatedEffortDays);

    /**
     * 查询相似系统评估（同类型系统）
     */
    List<SystemAssessment> selectSimilarAssessments(@Param("systemType") String systemType,
                                                    @Param("limit") Integer limit);

    /**
     * 获取评估趋势分析（按时间）
     */
    List<Map<String, Object>> getAssessmentTrend(@Param("projectId") Long projectId,
                                                 @Param("days") Integer days);

    /**
     * 逻辑删除
     */
    int deleteById(@Param("id") Long id,
                   @Param("updatedBy") Long updatedBy);
}