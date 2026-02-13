import React, { useEffect, useState } from 'react';
import { Tabs, Table, Card, Tag } from 'antd';
import api from '../../api/client';

const AdminPanel: React.FC = () => {
  const [auditLogs, setAuditLogs] = useState([]);

  useEffect(() => {
    api.get('/audit', { params: { limit: 50 } }).then(res => setAuditLogs(res.data)).catch(() => {});
  }, []);

  const auditColumns = [
    { title: '用户', dataIndex: 'username', key: 'user' },
    { title: '操作', dataIndex: 'action', key: 'action', render: (a: string) => <Tag>{a}</Tag> },
    { title: '资源类型', dataIndex: 'resource_type', key: 'type' },
    { title: '资源ID', dataIndex: 'resource_id', key: 'rid' },
    { title: '详情', dataIndex: 'detail', key: 'detail' },
    { title: '时间', dataIndex: 'created_at', key: 'time' },
  ];

  return (
    <Tabs items={[
      {
        key: 'audit',
        label: '审计日志',
        children: (
          <Card>
            <Table dataSource={auditLogs} columns={auditColumns} rowKey="id" />
          </Card>
        ),
      },
      {
        key: 'users',
        label: '用户管理',
        children: <Card><p>用户管理功能开发中...</p></Card>,
      },
      {
        key: 'orgs',
        label: '组织管理',
        children: <Card><p>组织管理功能开发中...</p></Card>,
      },
    ]} />
  );
};

export default AdminPanel;
