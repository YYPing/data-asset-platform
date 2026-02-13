import React, { useEffect, useState } from 'react';
import { Table, Button, Tag, message, Modal, Input } from 'antd';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import api from '../../api/client';
import { getStageName } from '../../utils';

interface PendingRecord {
  id: number;
  asset_id: number;
  asset_name: string;
  stage: string;
  status: string;
  submitted_by: number | null;
}

const ApprovalList: React.FC = () => {
  const [records, setRecords] = useState<PendingRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [rejectModal, setRejectModal] = useState<{ visible: boolean; recordId: number | null }>({ visible: false, recordId: null });
  const [reason, setReason] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      // TODO: HARDCODED - 需要后端提供待审批列表API
      await api.get('/assets');
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleApprove = async (recordId: number) => {
    try {
      await api.post(`/stages/records/${recordId}/approve`);
      message.success('审批通过');
      load();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '操作失败');
    }
  };

  const handleReject = async () => {
    if (!rejectModal.recordId) return;
    try {
      await api.post(`/stages/records/${rejectModal.recordId}/reject`, { reason });
      message.success('已退回');
      setRejectModal({ visible: false, recordId: null });
      setReason('');
      load();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '操作失败');
    }
  };

  const columns = [
    { title: '资产名称', dataIndex: 'asset_name', key: 'name' },
    { title: '阶段', dataIndex: 'stage', key: 'stage', render: (s: string) => getStageName(s) },
    { title: '状态', dataIndex: 'status', key: 'status',
      render: (s: string) => <Tag color={s === 'submitted' ? 'processing' : s === 'approved' ? 'success' : 'error'}>{s}</Tag> },
    { title: '操作', key: 'action',
      render: (_: any, record: PendingRecord) => record.status === 'submitted' && (
        <>
          <Button type="link" icon={<CheckOutlined />} onClick={() => handleApprove(record.id)}>通过</Button>
          <Button type="link" danger icon={<CloseOutlined />} onClick={() => setRejectModal({ visible: true, recordId: record.id })}>退回</Button>
        </>
      ),
    },
  ];

  return (
    <div>
      <h3>审批管理</h3>
      <Table dataSource={records} columns={columns} rowKey="id" loading={loading} />
      <Modal title="退回原因" open={rejectModal.visible} onOk={handleReject}
        onCancel={() => setRejectModal({ visible: false, recordId: null })}>
        <Input.TextArea value={reason} onChange={e => setReason(e.target.value)} placeholder="请输入退回原因" rows={3} />
      </Modal>
    </div>
  );
};

export default ApprovalList;
