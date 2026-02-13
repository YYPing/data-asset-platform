import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Tag } from 'antd';
import { statsApi } from '../../api/assets';
import { getStageName } from '../../utils';

interface CityData {
  total_assets: number;
  stage_distribution: { stage: string; count: number }[];
  org_count: number;
}

const CityDashboard: React.FC = () => {
  const [data, setData] = useState<CityData | null>(null);

  useEffect(() => {
    statsApi.city().then(res => setData(res.data)).catch(() => {});
  }, []);

  if (!data) return null;

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>全市数据资产监管大屏</h2>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card><Statistic title="全市资产总量" value={data.total_assets} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="参与组织数" value={data.org_count} /></Card>
        </Col>
        <Col span={8}>
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

export default CityDashboard;
