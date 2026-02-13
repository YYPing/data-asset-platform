import React, { useState } from 'react';
import { Form, Input, Select, Button, Card, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { assetApi } from '../../api/assets';

const AssetCreate: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await assetApi.create(values);
      message.success('资产创建成功');
      navigate('/assets');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '创建失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="新建数据资产" style={{ maxWidth: 600 }}>
      <Form layout="vertical" onFinish={onFinish}>
        <Form.Item name="name" label="资产名称" rules={[{ required: true }]}>
          <Input placeholder="请输入数据资产名称" />
        </Form.Item>
        <Form.Item name="description" label="描述">
          <Input.TextArea rows={3} placeholder="资产描述" />
        </Form.Item>
        <Form.Item name="asset_type" label="资产类型">
          <Select placeholder="选择类型" allowClear>
            <Select.Option value="structured">结构化数据</Select.Option>
            <Select.Option value="unstructured">非结构化数据</Select.Option>
            <Select.Option value="semi_structured">半结构化数据</Select.Option>
          </Select>
        </Form.Item>
        <Form.Item name="data_classification" label="数据分类">
          <Select placeholder="选择分类" allowClear>
            <Select.Option value="public">公共数据</Select.Option>
            <Select.Option value="internal">内部数据</Select.Option>
            <Select.Option value="sensitive">敏感数据</Select.Option>
          </Select>
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>创建</Button>
          <Button style={{ marginLeft: 8 }} onClick={() => navigate('/assets')}>取消</Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default AssetCreate;
