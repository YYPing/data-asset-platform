-- 数据资产全流程管理平台 - 数据库初始化脚本
-- 版本: 1.0.0
-- 创建日期: 2026-02-05

-- 创建数据库
CREATE DATABASE IF NOT EXISTS data_asset 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE data_asset;

-- ===========================================
-- 1. 基础数据表
-- ===========================================

-- 用户表
CREATE TABLE IF NOT EXISTS `sys_user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `password` VARCHAR(255) COMMENT '密码',
  `real_name` VARCHAR(50) COMMENT '真实姓名',
  `email` VARCHAR(100) COMMENT '邮箱',
  `phone` VARCHAR(20) COMMENT '手机号',
  `avatar` VARCHAR(255) COMMENT '头像',
  `user_type` VARCHAR(20) DEFAULT 'internal' COMMENT '用户类型：internal-内部用户，customer-客户用户',
  `status` TINYINT DEFAULT 1 COMMENT '状态：1-有效，0-禁用',
  `last_login_time` TIMESTAMP NULL DEFAULT NULL COMMENT '最后登录时间',
  `created_by` BIGINT COMMENT '创建人',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_by` BIGINT COMMENT '更新人',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` TINYINT DEFAULT 0 COMMENT '删除标记：0-正常，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  INDEX `idx_user_type` (`user_type`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 角色表
CREATE TABLE IF NOT EXISTS `sys_role` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `role_code` VARCHAR(50) NOT NULL COMMENT '角色编码',
  `role_name` VARCHAR(100) NOT NULL COMMENT '角色名称',
  `description` VARCHAR(255) COMMENT '角色描述',
  `role_type` VARCHAR(20) COMMENT '角色类型：admin/manager/consultant/customer',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS `sys_user_role` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `role_id` BIGINT NOT NULL COMMENT '角色ID',
  `project_id` BIGINT COMMENT '项目ID（为空表示全局角色）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_role_project` (`user_id`, `role_id`, `project_id`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';

-- 权限表
CREATE TABLE IF NOT EXISTS `sys_permission` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `permission_code` VARCHAR(100) NOT NULL COMMENT '权限编码',
  `permission_name` VARCHAR(100) NOT NULL COMMENT '权限名称',
  `resource_type` VARCHAR(50) COMMENT '资源类型：menu/button/api',
  `parent_id` BIGINT COMMENT '父权限ID',
  `sort_order` INT COMMENT '排序',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_permission_code` (`permission_code`),
  INDEX `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS `sys_role_permission` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `role_id` BIGINT NOT NULL COMMENT '角色ID',
  `permission_id` BIGINT NOT NULL COMMENT '权限ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_permission` (`role_id`, `permission_id`),
  INDEX `idx_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色权限关联表';

-- ===========================================
-- 2. 客户与项目表
-- ===========================================

-- 客户表
CREATE TABLE IF NOT EXISTS `customer` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `customer_code` VARCHAR(50) NOT NULL COMMENT '客户编码，唯一',
  `company_name` VARCHAR(200) NOT NULL COMMENT '公司名称',
  `company_short_name` VARCHAR(100) COMMENT '公司简称',
  `industry` VARCHAR(50) COMMENT '所属行业',
  `company_scale` VARCHAR(20) COMMENT '企业规模: large/medium/small',
  `business_license` VARCHAR(100) COMMENT '统一社会信用代码',
  `legal_representative` VARCHAR(50) COMMENT '法定代表人',
  `registered_capital` DECIMAL(18,2) COMMENT '注册资本(万元)',
  `establishment_date` DATE COMMENT '成立日期',
  `registered_address` VARCHAR(500) COMMENT '注册地址',
  `office_address` VARCHAR(500) COMMENT '办公地址',
  `contact_name` VARCHAR(50) COMMENT '联系人姓名',
  `contact_phone` VARCHAR(20) COMMENT '联系人电话',
  `contact_email` VARCHAR(100) COMMENT '联系人邮箱',
  `contact_position` VARCHAR(50) COMMENT '联系人职位',
  `company_website` VARCHAR(200) COMMENT '公司官网',
  `company_introduction` TEXT COMMENT '公司简介',
  `business_scope` TEXT COMMENT '经营范围',
  `status` TINYINT DEFAULT 1 COMMENT '状态：1-有效，0-停用',
  `manager_id` BIGINT COMMENT '客户经理ID',
  `source` VARCHAR(50) COMMENT '客户来源',
  `remark` TEXT COMMENT '备注',
  `created_by` BIGINT COMMENT '创建人',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_by` BIGINT COMMENT '更新人',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` TINYINT DEFAULT 0 COMMENT '删除标记：0-正常，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_customer_code` (`customer_code`),
  INDEX `idx_company_name` (`company_name`),
  INDEX `idx_industry` (`industry`),
  INDEX `idx_status` (`status`),
  INDEX `idx_manager_id` (`manager_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户信息表';

-- 项目表
CREATE TABLE IF NOT EXISTS `project` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `project_code` VARCHAR(50) NOT NULL COMMENT '项目编号',
  `customer_id` BIGINT NOT NULL COMMENT '客户ID',
  `project_name` VARCHAR(200) NOT NULL COMMENT '项目名称',
  `project_type` VARCHAR(50) COMMENT '项目类型',
  `description` TEXT COMMENT '项目描述',
  `contract_amount` DECIMAL(18,2) COMMENT '合同金额',
  `start_date` DATE COMMENT '开始日期',
  `end_date` DATE COMMENT '结束日期',
  `current_phase` VARCHAR(50) DEFAULT 'system_registry' COMMENT '当前阶段',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态',
  `manager_id` BIGINT COMMENT '项目经理ID',
  `progress` INT DEFAULT 0 COMMENT '整体进度（百分比）',
  `created_by` BIGINT COMMENT '创建人',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_by` BIGINT COMMENT '更新人',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` TINYINT DEFAULT 0 COMMENT '删除标记',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_project_code` (`project_code`),
  INDEX `idx_customer_id` (`customer_id`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目信息表';

-- 项目阶段记录表
CREATE TABLE IF NOT EXISTS `project_phase` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `project_id` BIGINT NOT NULL COMMENT '项目ID',
  `phase_code` VARCHAR(50) NOT NULL COMMENT '阶段编码',
  `phase_name` VARCHAR(100) NOT NULL COMMENT '阶段名称',
  `phase_order` INT COMMENT '阶段顺序',
  `start_date` DATE COMMENT '实际开始时间',
  `end_date` DATE COMMENT '实际结束时间',
  `planned_start_date` DATE COMMENT '计划开始时间',
  `planned_end_date` DATE COMMENT '计划结束时间',
  `status` VARCHAR(20) DEFAULT 'pending' COMMENT '状态',
  `progress` INT DEFAULT 0 COMMENT '阶段进度',
  `output_documents` JSON COMMENT '产出物清单',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `idx_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目阶段表';

-- ===========================================
-- 3. 系统登记与评估表
-- ===========================================

-- 客户系统表
CREATE TABLE IF NOT EXISTS `customer_system` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `project_id` BIGINT NOT NULL COMMENT '项目ID',
  `system_code` VARCHAR(50) COMMENT '系统编码',
  `system_name` VARCHAR(200) NOT NULL COMMENT '系统名称',
  `system_type` VARCHAR(50) NOT NULL COMMENT '系统类型',
  `business_domain` VARCHAR(50) COMMENT '业务领域',
  `description` TEXT COMMENT '系统简介',
  `vendor` VARCHAR(200) COMMENT '开发商/供应商',
  `version` VARCHAR(50) COMMENT '系统版本',
  `database_type` VARCHAR(50) COMMENT '数据库类型',
  `estimated_data_volume` VARCHAR(50) COMMENT '预估数据量',
  `data_growth_rate` VARCHAR(20) COMMENT '数据增长率',
  `security_level` VARCHAR(10) COMMENT '等保级别',
  `data_classification` VARCHAR(20) COMMENT '数据分级',
  `compliance_certifications` JSON COMMENT '合规认证清单',
  `last_security_assessment` DATE COMMENT '上次安全评估时间',
  `business_criticality` TINYINT COMMENT '业务关键性：1-5级',
  `user_count` INT COMMENT '用户数量',
  `daily_transaction_volume` INT COMMENT '日均交易量',
  `annual_transaction_amount` DECIMAL(18,2) COMMENT '年交易金额',
  `business_owner` VARCHAR(50) COMMENT '业务负责人',
  `business_owner_phone` VARCHAR(20),
  `it_owner` VARCHAR(50) COMMENT 'IT负责人',
  `it_owner_phone` VARCHAR(20),
  `data_owner` VARCHAR(50) COMMENT '数据负责人',
  `data_owner_phone` VARCHAR(20),
  `status` VARCHAR(20) DEFAULT 'registered' COMMENT '状态',
  `is_selected` TINYINT DEFAULT 0 COMMENT '是否被选中挖掘',
  `selection_reason` TEXT COMMENT '选中理由',
  `priority_level` VARCHAR(20) COMMENT '优先级',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` TINYINT DEFAULT 0 COMMENT '删除标记',
  PRIMARY KEY (`id`),
  INDEX `idx_project_id` (`project_id`),
  INDEX `idx_system_type` (`system_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户系统表';

-- 系统评估表
CREATE TABLE IF NOT EXISTS `system_assessment` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `system_id` BIGINT NOT NULL COMMENT '系统ID',
  `project_id` BIGINT NOT NULL COMMENT '项目ID',
  `business_value_score` DECIMAL(5,2) COMMENT '业务价值评分',
  `data_quality_score` DECIMAL(5,2) COMMENT '数据质量预估评分',
  `compliance_risk_score` DECIMAL(5,2) COMMENT '合规风险评分',
  `technical_feasibility_score` DECIMAL(5,2) COMMENT '技术可行性评分',
  `total_score` DECIMAL(5,2) COMMENT '综合评分',
  `business_value_detail` JSON COMMENT '业务价值评估详情',
  `data_quality_detail` JSON COMMENT '数据质量评估详情',
  `compliance_risk_detail` JSON COMMENT '合规风险评估详情',
  `technical_feasibility_detail` JSON COMMENT '技术可行性评估详情',
  `recommendation` VARCHAR(50) COMMENT '建议',
  `priority_level` VARCHAR(20) COMMENT '优先级',
  `estimated_roi` DECIMAL(10,4) COMMENT '预估投资回报率',
  `estimated_benefit` DECIMAL(18,2) COMMENT '预估年收益',
  `estimated_cost` DECIMAL(18,2) COMMENT '预估实施成本',
  `estimated_effort_days` INT COMMENT '预估实施天数',
  `implementation_roadmap` JSON COMMENT '实施路线图',
  `suggested_data_products` JSON COMMENT '建议的数据产品类型',
  `risk_warnings` TEXT COMMENT '风险提示',
  `assessor_id` BIGINT COMMENT '评估人ID',
  `assessment_date` DATE COMMENT '评估日期',
  `review_status` VARCHAR(20) DEFAULT 'pending' COMMENT '审核状态',
  `reviewer_id` BIGINT COMMENT '审核人ID',
  `review_date` DATE COMMENT '审核日期',
  `review_comments` TEXT COMMENT '审核意见',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_system_id` (`system_id`),
  INDEX `idx_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统价值评估表';

-- 初始化数据
-- 插入默认管理员账号（密码：admin123）
INSERT INTO `sys_user` (`username`, `password`, `real_name`, `user_type`, `status`) 
VALUES ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5E', '系统管理员', 'internal', 1)
ON DUPLICATE KEY UPDATE `username` = `username`;

-- 插入默认角色
INSERT INTO `sys_role` (`role_code`, `role_name`, `role_type`) VALUES
('admin', '系统管理员', 'admin'),
('manager', '项目经理', 'manager'),
('consultant', '咨询顾问', 'consultant'),
('customer', '客户用户', 'customer')
ON DUPLICATE KEY UPDATE `role_code` = `role_code`;
