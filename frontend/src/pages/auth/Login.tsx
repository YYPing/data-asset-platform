import React, { useState } from 'react';
import { Form, Input, Button, Card, Select, message, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../../api/auth';
import { setAuth, ROLE_LABELS } from '../../utils';

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      if (isRegister) {
        await authApi.register(values);
        message.success('注册成功，请登录');
        setIsRegister(false);
      } else {
        const res = await authApi.login(values);
        setAuth(res.data.access_token, res.data.user);
        message.success('登录成功');
        navigate('/');
      }
    } catch (err: any) {
      message.error(err.response?.data?.detail || '操作失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card title="数据资产全生命周期管理平台" style={{ width: 420 }}>
        <Form onFinish={onFinish} size="large">
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          {isRegister && (
            <>
              <Form.Item name="real_name">
                <Input placeholder="真实姓名" />
              </Form.Item>
              <Form.Item name="role" rules={[{ required: true, message: '请选择角色' }]}>
                <Select placeholder="选择角色">
                  {Object.entries(ROLE_LABELS).map(([k, v]) => (
                    <Select.Option key={k} value={k}>{v}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </>
          )}
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              {isRegister ? '注册' : '登录'}
            </Button>
          </Form.Item>
          <Typography.Link onClick={() => setIsRegister(!isRegister)}>
            {isRegister ? '已有账号？去登录' : '没有账号？去注册'}
          </Typography.Link>
        </Form>
      </Card>
    </div>
  );
};

export default Login;
