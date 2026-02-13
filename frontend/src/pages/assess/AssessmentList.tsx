import React from 'react';
import { Card, Table, Tag } from 'antd';

const AssessmentList: React.FC = () => {
  // TODO: HARDCODED - 需要后端提供评估任务列表API
  const columns = [
    { title: '资产名称', dataIndex: 'asset_name', key: 'name' },
    { title: '评估类型', dataIndex: 'type', key: 'type' },
    { title: '状态', dataIndex: 'status', key: 'status',
      render: (s: string) => <Tag color={s === 'pending' ? 'processing' : 'success'}>{s === 'pending' ? '待评估' : '已完成'}</Tag> },
  ];

  return (
    <Card title="评估管理">
      <Table dataSource={[]} columns={columns} rowKey="id" />
    </Card>
  );
};

export default AssessmentList;
