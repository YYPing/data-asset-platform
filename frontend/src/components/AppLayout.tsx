import React from 'react';
import { Layout, Menu, Button, Typography } from 'antd';
import {
  DatabaseOutlined,
  AuditOutlined,
  BarChartOutlined,
  SettingOutlined,
  DashboardOutlined,
  LogoutOutlined,
  FileProtectOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { getUser, clearAuth, ROLE_LABELS } from '../utils';

const { Header, Sider, Content } = Layout;

const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const user = getUser();

  const menuItems = [
    { key: '/assets', icon: <DatabaseOutlined />, label: '资产管理' },
    { key: '/approval', icon: <AuditOutlined />, label: '审批管理' },
    { key: '/assess', icon: <FileProtectOutlined />, label: '评估管理' },
    { key: '/dashboard', icon: <DashboardOutlined />, label: '持有方大屏' },
    { key: '/monitor', icon: <BarChartOutlined />, label: '全市监管大屏' },
    { key: '/admin', icon: <SettingOutlined />, label: '系统管理' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={200}>
        <div style={{ color: '#fff', textAlign: 'center', padding: '16px 0', fontSize: 16, fontWeight: 'bold' }}>
          数据资产管理
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 16 }}>
          <Typography.Text>{user?.real_name || user?.username} ({ROLE_LABELS[user?.role || ''] || user?.role})</Typography.Text>
          <Button icon={<LogoutOutlined />} onClick={() => { clearAuth(); navigate('/login'); }}>退出</Button>
        </Header>
        <Content style={{ margin: 24, padding: 24, background: '#fff', borderRadius: 8 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
