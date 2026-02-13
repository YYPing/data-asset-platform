import type { UserInfo } from '../api/auth';

const STAGE_LABELS: Record<string, string> = {
  resource_inventory: '1.数据资源梳理',
  asset_inventory: '2.数据资产梳理',
  usage_scenario: '3.数据使用场景报告',
  compliance_assessment: '4.合规评估报告',
  quality_report: '5.数据质量报告',
  accounting_guidance: '6.入账指导意见',
  value_assessment: '7.数据价值评估',
  operation: '8.运营阶段',
};

export const getStageName = (stage: string) => STAGE_LABELS[stage] || stage;

export const ROLE_LABELS: Record<string, string> = {
  data_holder: '数据持有方',
  registry_center: '登记中心',
  assessor: '评估机构',
  compliance: '合规人员',
  regulator: '行业监管部门',
  admin: '系统管理员',
};

export const getUser = (): UserInfo | null => {
  const s = localStorage.getItem('user');
  return s ? JSON.parse(s) : null;
};

export const setAuth = (token: string, user: UserInfo) => {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
};

export const clearAuth = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};
