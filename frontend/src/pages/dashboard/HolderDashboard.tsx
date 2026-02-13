import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Tag } from 'antd';
import { statsApi } from '../../api/assets';
import { getStageName } from '../../utils';

interface HolderData {
  total_assets: number;
  stage_distribution: { stage: string; count: number }[];
  valued_count: number;
  total_valuation: number;
}

const HolderDashboard: React.FC = () => {
  const [data, setData] = useState<HolderData | null>(null);

  useEffect(() => {
    statsApi.holder().then(res => setData(res.data)).catch(() => {});
  }, []);

  if (!data) return null;

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>持有方数据大屏</h2>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="资产总数" value={data.total_assets} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="已估值资产" value={data.valued_count} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="估值总额" value={data.total_valuation} prefix="¥" precision={2} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="运营中资产" value={data.stage_distribution.find(s => s.stage === 'operation')?.count || 0} /></Card>
        </Col>
      </Row>

      <Card title="各阶段资产分布">
        <Table
          dataSource={data.stage_distribution}
          columns={[
            { title: '阶段', dataIndex: 'stage', key: 'stage', render: (s: string) => <Tag>{getStageName(s)}</Tag> },
            { title: '数量', dataIndex: 'count', key: 'count' },
          ]}
          rowKey="stage"
          pagination={false}
        />
      </Card>
    </div>
  );
};

export default HolderDashboard;
