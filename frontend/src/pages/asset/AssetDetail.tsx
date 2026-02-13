import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Descriptions, Steps, Button, Upload, Table, Tag, message, Space } from 'antd';
import { UploadOutlined, SendOutlined } from '@ant-design/icons';
import { assetApi, stageApi, materialApi } from '../../api/assets';
import type { Asset, Material } from '../../api/assets';
import { getStageName } from '../../utils';

const ALL_STAGES = [
  'resource_inventory', 'asset_inventory', 'usage_scenario', 'compliance_assessment',
  'quality_report', 'accounting_guidance', 'value_assessment', 'operation',
];

const AssetDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [asset, setAsset] = useState<Asset | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [stageRecordId, setStageRecordId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    if (!id) return;
    const res = await assetApi.get(Number(id));
    setAsset(res.data);
  };

  useEffect(() => { load(); }, [id]);

  const handleSubmitStage = async () => {
    if (!asset) return;
    setLoading(true);
    try {
      const res = await stageApi.submit(asset.id);
      setStageRecordId(res.data.id);
      message.success('阶段已提交审批');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '提交失败');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file: File) => {
    if (!stageRecordId) {
      message.warning('请先提交阶段审批以获取阶段记录');
      return false;
    }
    try {
      await materialApi.upload(stageRecordId, file);
      message.success('材料上传成功');
      const res = await materialApi.list(stageRecordId);
      setMaterials(res.data);
    } catch (err: any) {
      message.error('上传失败');
    }
    return false;
  };

  const currentStep = asset ? ALL_STAGES.indexOf(asset.current_stage) : 0;

  const matColumns = [
    { title: '文件名', dataIndex: 'file_name', key: 'name' },
    { title: '版本', dataIndex: 'version', key: 'ver', render: (v: number) => `v${v}` },
    { title: 'SHA-256', dataIndex: 'hash_sha256', key: 'hash',
      render: (h: string) => <Tag>{h.substring(0, 16)}...</Tag> },
    { title: '大小', dataIndex: 'file_size', key: 'size',
      render: (s: number) => s ? `${(s / 1024).toFixed(1)} KB` : '-' },
  ];

  if (!asset) return null;

  return (
    <div>
      <Card title={asset.name} style={{ marginBottom: 16 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="当前阶段">{getStageName(asset.current_stage)}</Descriptions.Item>
          <Descriptions.Item label="资产类型">{asset.asset_type || '-'}</Descriptions.Item>
          <Descriptions.Item label="数据分类">{asset.data_classification || '-'}</Descriptions.Item>
          <Descriptions.Item label="估值金额">{asset.valuation_amount ? `¥${asset.valuation_amount}` : '-'}</Descriptions.Item>
          <Descriptions.Item label="入账类型">{asset.accounting_type || '-'}</Descriptions.Item>
          <Descriptions.Item label="描述">{asset.description || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="生命周期进度" style={{ marginBottom: 16 }}>
        <Steps current={currentStep} size="small"
          items={ALL_STAGES.map(s => ({ title: getStageName(s) }))} />
      </Card>

      <Card title="当前阶段操作">
        <Space>
          <Button type="primary" icon={<SendOutlined />} onClick={handleSubmitStage} loading={loading}>
            提交审批
          </Button>
          <Upload beforeUpload={handleUpload} showUploadList={false}>
            <Button icon={<UploadOutlined />}>上传材料</Button>
          </Upload>
        </Space>
        {materials.length > 0 && (
          <Table dataSource={materials} columns={matColumns} rowKey="id" style={{ marginTop: 16 }} pagination={false} />
        )}
      </Card>
    </div>
  );
};

export default AssetDetail;
