-- 数据资产平台 - 数据库初始化脚本
-- 版本: V2.0
-- 创建时间: 2026-02-10
-- 描述: 创建17张核心表结构

-- 1. 用户和组织表
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE,
    unified_credit_code VARCHAR(18),
    type VARCHAR(50),
    parent_id INTEGER REFERENCES organizations(id),
    level INTEGER DEFAULT 1,
    contact_person VARCHAR(100),
    contact_phone VARCHAR(20),
    address TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    password_expires_at TIMESTAMP,
    failed_login_count INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(45),
    real_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(30) NOT NULL,
    organization_id INTEGER REFERENCES organizations(id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 数据资产相关表
CREATE TABLE IF NOT EXISTS data_assets (
    id SERIAL PRIMARY KEY,
    asset_code VARCHAR(100) UNIQUE NOT NULL,
    asset_name VARCHAR(200) NOT NULL,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    category VARCHAR(50),
    data_classification VARCHAR(20) DEFAULT 'internal',
    sensitivity_level VARCHAR(20) DEFAULT 'low',
    description TEXT,
    data_source TEXT,
    data_volume VARCHAR(50),
    data_format VARCHAR(50),
    update_frequency VARCHAR(50),
    current_stage VARCHAR(30) DEFAULT 'registration',
    status VARCHAR(20) DEFAULT 'draft',
    asset_type VARCHAR(30),
    estimated_value NUMERIC(15, 2),
    created_by INTEGER REFERENCES users(id),
    assigned_to INTEGER REFERENCES users(id),
    version INTEGER DEFAULT 1,
    previous_version_id INTEGER REFERENCES data_assets(id),
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS materials (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES data_assets(id),
    material_name VARCHAR(200) NOT NULL,
    material_type VARCHAR(50),
    stage VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    file_format VARCHAR(20),
    file_hash VARCHAR(64) NOT NULL,
    version INTEGER DEFAULT 1,
    is_required BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'pending',
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    review_comment TEXT
);

CREATE TABLE IF NOT EXISTS registration_certificates (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES data_assets(id),
    certificate_type VARCHAR(50) NOT NULL,
    certificate_number VARCHAR(100) NOT NULL,
    issuing_authority VARCHAR(200),
    issue_date DATE NOT NULL,
    expiry_date DATE,
    file_path VARCHAR(500),
    file_hash VARCHAR(64),
    status VARCHAR(20) DEFAULT 'active',
    imported_by INTEGER REFERENCES users(id),
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- 3. 工作流相关表
CREATE TABLE IF NOT EXISTS workflow_definitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    stages JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'active',
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_instances (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES data_assets(id),
    definition_id INTEGER NOT NULL REFERENCES workflow_definitions(id),
    current_stage VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_nodes (
    id SERIAL PRIMARY KEY,
    instance_id INTEGER NOT NULL REFERENCES workflow_instances(id),
    stage_name VARCHAR(50) NOT NULL,
    node_type VARCHAR(20) NOT NULL,
    assignee_type VARCHAR(20),
    assignee_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    due_date TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS approval_records (
    id SERIAL PRIMARY KEY,
    node_id INTEGER NOT NULL REFERENCES workflow_nodes(id),
    operator_id INTEGER NOT NULL REFERENCES users(id),
    action VARCHAR(20) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 评估相关表
CREATE TABLE IF NOT EXISTS assessment_records (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES data_assets(id),
    assessment_type VARCHAR(50) NOT NULL,
    evaluator_org_id INTEGER REFERENCES organizations(id),
    evaluator_id INTEGER REFERENCES users(id),
    report_material_id INTEGER REFERENCES materials(id),
    score NUMERIC(5, 2),
    result VARCHAR(20),
    details JSONB,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 系统表
-- 审计日志表（建议按时间分区）
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL,
    user_id INTEGER,
    username VARCHAR(50),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    detail JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    result VARCHAR(10) DEFAULT 'success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 创建默认分区
CREATE TABLE IF NOT EXISTS audit_logs_default PARTITION OF audit_logs DEFAULT;

CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    resource VARCHAR(50),
    action VARCHAR(20),
    description TEXT
);

CREATE TABLE IF NOT EXISTS role_permissions (
    id SERIAL PRIMARY KEY,
    role VARCHAR(30) NOT NULL,
    permission_id INTEGER NOT NULL REFERENCES permissions(id),
    UNIQUE(role, permission_id)
);

CREATE TABLE IF NOT EXISTS data_dictionaries (
    id SERIAL PRIMARY KEY,
    dict_type VARCHAR(50) NOT NULL,
    dict_code VARCHAR(50) NOT NULL,
    dict_label VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    status VARCHAR(10) DEFAULT 'active',
    UNIQUE(dict_type, dict_code)
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'system',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    updater_id INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS async_jobs (
    id SERIAL PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL,
    params JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- 6. 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    operation_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id INTEGER,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    result VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_data_assets_organization ON data_assets(organization_id);
CREATE INDEX idx_data_assets_status ON data_assets(status);
CREATE INDEX idx_materials_asset ON materials(asset_id);
CREATE INDEX idx_workflow_instances_asset ON workflow_instances(asset_id);
CREATE INDEX idx_workflow_instances_status ON workflow_instances(status);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_operation_logs_user ON operation_logs(user_id);
CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at);

-- 创建全文搜索索引（使用zhparser中文分词）
-- 注意：需要先安装zhparser扩展
-- CREATE EXTENSION IF NOT EXISTS zhparser;
-- CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
-- CREATE TEXT SEARCH DICTIONARY simple_dict (TEMPLATE = simple);
-- ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR n,v,a,i,e,l WITH simple_dict;
-- CREATE INDEX idx_data_assets_search ON data_assets USING GIN (to_tsvector('chinese', asset_name || ' ' || COALESCE(description, '')));

-- 插入初始数据
-- 1. 插入默认组织
INSERT INTO organizations (name, code, type, level, status) VALUES
('数据资产登记中心', 'DARC', 'government', 1, 'active'),
('第三方评估机构', 'TPA', 'evaluator', 1, 'active')
ON CONFLICT (code) DO NOTHING;

-- 2. 插入默认用户（密码：admin123，实际使用时需要加密）
INSERT INTO users (username, password_hash, real_name, role, organization_id, status) VALUES
('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '系统管理员', 'admin', 1, 'active'),
('center_auditor', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '登记中心审核员', 'center_auditor', 1, 'active'),
('evaluator', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '评估专家', 'evaluator', 2, 'active'),
('data_holder', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '数据持有方', 'data_holder', NULL, 'active')
ON CONFLICT (username) DO NOTHING;

-- 3. 插入默认权限
INSERT INTO permissions (code, name, resource, action, description) VALUES
('user:read', '查看用户', 'user', 'read', '查看用户信息'),
('user:write', '管理用户', 'user', 'write', '创建、修改、删除用户'),
('asset:read', '查看资产', 'asset', 'read', '查看数据资产'),
('asset:write', '管理资产', 'asset', 'write', '创建、修改、删除数据资产'),
('workflow:read', '查看工作流', 'workflow', 'read', '查看工作流状态'),
('workflow:write', '管理工作流', 'workflow', 'write', '审批、驳回工作流'),
('assessment:read', '查看评估', 'assessment', 'read', '查看评估结果'),
('assessment:write', '管理评估', 'assessment', 'write', '创建、修改评估'),
('audit:read', '查看审计日志', 'audit', 'read', '查看系统审计日志'),
('system:config', '系统配置', 'system', 'config', '管理系统配置')
ON CONFLICT (code) DO NOTHING;

-- 4. 插入角色权限
INSERT INTO role_permissions (role, permission_id) 
SELECT 'admin', id FROM permissions
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO role_permissions (role, permission_id) 
SELECT 'center_auditor', id FROM permissions WHERE code IN ('asset:read', 'asset:write', 'workflow:read', 'workflow:write', 'assessment:read')
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO role_permissions (role, permission_id) 
SELECT 'evaluator', id FROM permissions WHERE code IN ('asset:read', 'assessment:read', 'assessment:write')
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO role_permissions (role, permission_id) 
SELECT 'data_holder', id FROM permissions WHERE code IN ('asset:read', 'asset:write', 'workflow:read')
ON CONFLICT (role, permission_id) DO NOTHING;

-- 5. 插入数据字典
INSERT INTO data_dictionaries (dict_type, dict_code, dict_label, sort_order) VALUES
('asset_category', 'basic', '基础数据', 1),
('asset_category', 'business', '业务数据', 2),
('asset_category', 'management', '管理数据', 3),
('asset_category', 'external', '外部数据', 4),
('data_classification', 'public', '公开', 1),
('data_classification', 'internal', '内部', 2),
('data_classification', 'confidential', '机密', 3),
('data_classification', 'secret', '绝密', 4),
('sensitivity_level', 'low', '低', 1),
('sensitivity_level', 'medium', '中', 2),
('sensitivity_level', 'high', '高', 3),
('asset_stage', 'registration', '登记', 1),
('asset_stage', 'compliance_assessment', '合规评估', 2),
('asset_stage', 'value_assessment', '价值评估', 3),
('asset_stage', 'ownership_confirmation', '权属确认', 4),
('asset_stage', 'registration_certificate', '确权登记', 5),
('asset_stage', 'account_entry', '入账', 6),
('asset_stage', 'operation', '运营', 7),
('asset_stage', 'change_management', '变更管理', 8),
('asset_stage', 'supervision', '监管', 9),
('asset_stage', 'exit', '退出', 10),
('material_type', 'data_description', '数据描述文档', 1),
('material_type', 'compliance_report', '合规报告', 2),
('material_type', 'data_quality_report', '数据质量报告', 3),
('material_type', 'registration_certificate', '登记证书', 4),
('material_type', 'assessment_report', '评估报告', 5),
('workflow_status', 'pending', '待处理', 1),
('workflow_status', 'approved', '已通过', 2),
('workflow_status', 'rejected', '已驳回', 3),
('workflow_status', 'cancelled', '已取消', 4)
ON CONFLICT (dict_type, dict_code) DO NOTHING;

-- 6. 插入系统配置
INSERT INTO system_configs (config_key, config_value, description) VALUES
('system.name', '数据资产全流程管理平台', '系统名称'),
('system.version', 'V2.0', '系统版本'),
('password.min_length', '8', '密码最小长度'),
('password.expire_days', '90', '密码过期天数（天）'),
('login.max_attempts', '5', '最大登录失败次数'),
('login.lock_minutes', '30', '账户锁定时间（分钟）'),
('file.max_size_mb', '50', '文件最大大小（MB）'),
('session.timeout_minutes', '30', '会话超时时间（分钟）')
ON CONFLICT (config_key) DO NOTHING;

-- 7. 创建工作流定义
INSERT INTO workflow_definitions (name, description, stages, version) VALUES
('标准数据资产登记流程', '从登记到确权的完整流程', '[
  {"name": "登记", "approvers": ["data_holder"], "timeout_days": 7},
  {"name": "合规评估", "approvers": ["center_auditor"], "timeout_days": 5},
  {"name": "价值评估", "approvers": ["evaluator"], "timeout_days": 10},
  {"name": "权属确认", "approvers": ["center_auditor"], "timeout_days": 3},
  {"name": "确权登记", "approvers": ["center_auditor"], "timeout_days": 3}
]', 1)
ON CONFLICT DO NOTHING;

COMMIT;

-- 输出完成信息
SELECT '数据库初始化完成！' AS message;
SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema = 'public';
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;