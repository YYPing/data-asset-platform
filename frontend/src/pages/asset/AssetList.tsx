import React, { useEffect, useState } from 'react';
import { Table, Button, Tag, Space, Input } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { assetApi } from '../../api/assets';
import type { Asset } from '../../api/assets';
import { getStageName } from '../../utils';

const stageColors: Record<string, string> = {
  resource_inventory: 'blue', asset_inventory: 'cyan', usage_scenario: 'geekblue',
  compliance_assessment: 'purple', quality_report: 'orange', accounting_guidance: 'gold',
  value_assessment: 'lime', operation: 'green',
};

const AssetList: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    try {
      const res = await assetApi.list();
      setAssets(res.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = assets.filter(a => a.name.includes(search));

  const columns = [
    { title: '资产名称', dataIndex: 'name', key: 'name' },
    { title: '当前阶段', dataIndex: 'current_stage', key: 'stage',
      render: (s: string) => <Tag color={stageColors[s]}>{getStageName(s)}</Tag> },
    { title: '资产类型', dataIndex: 'asset_type', key: 'type' },
    { title: '数据分类', dataIndex: 'data_classification', key: 'class' },
    { title: '操作', key: 'action',
      render: (_: any, record: Asset) => (
        <Button type="link" onClick={() => navigate(`/assets/${record.id}`)}>详情</Button>
      ),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/assets/create')}>新建资产</Button>
        <Input.Search placeholder="搜索资产名称" value={search} onChange={e => setSearch(e.target.value)} style={{ width: 300 }} />
      </Space>
      <Table dataSource={filtered} columns={columns} rowKey="id" loading={loading} />
    </div>
  );
};

export default AssetList;
