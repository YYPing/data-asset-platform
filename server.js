// 数据资产平台 - Node.js简化版本
// 可以立即运行测试

const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = 3000;
const JWT_SECRET = 'data-asset-platform-secret-key-2026';

// 中间件
app.use(cors());
app.use(express.json());

// 内存数据库
const db = {
  users: [
    {
      id: 1,
      username: 'admin',
      password: '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5E', // admin123
      realName: '系统管理员',
      userType: 'internal',
      status: 1
    }
  ],
  customers: [],
  projects: [],
  systems: [],
  assessments: []
};

// 生成ID
let customerId = 1;
let projectId = 1;
let systemId = 1;
let assessmentId = 1;

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({
    status: 'UP',
    service: 'data-asset-platform',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// 用户登录
app.post('/api/auth/login', async (req, res) => {
  const { username, password } = req.body;
  
  const user = db.users.find(u => u.username === username);
  
  if (!user) {
    return res.status(401).json({ code: 401, message: '用户名或密码错误' });
  }
  
  if (user.status === 0) {
    return res.status(401).json({ code: 401, message: '用户已被禁用' });
  }
  
  // 验证密码 (admin123)
  const isValid = await bcrypt.compare(password, user.password);
  
  if (!isValid) {
    return res.status(401).json({ code: 401, message: '用户名或密码错误' });
  }
  
  // 生成token
  const token = jwt.sign(
    { userId: user.id, username: user.username, userType: user.userType },
    JWT_SECRET,
    { expiresIn: '24h' }
  );
  
  res.json({
    code: 200,
    message: '登录成功',
    data: {
      userId: user.id,
      username: user.username,
      realName: user.realName,
      userType: user.userType,
      token: token,
      expiresIn: 24 * 60 * 60 * 1000 // 24小时
    }
  });
});

// 获取当前用户
app.get('/api/auth/me', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未授权' });
  }
  
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    const user = db.users.find(u => u.id === decoded.userId);
    
    if (!user) {
      return res.status(401).json({ code: 401, message: '用户不存在' });
    }
    
    res.json({
      code: 200,
      data: {
        userId: user.id,
        username: user.username,
        realName: user.realName,
        userType: user.userType,
        token: token
      }
    });
  } catch (error) {
    res.status(401).json({ code: 401, message: 'token无效' });
  }
});

// 客户管理API
app.get('/api/customers', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未授权' });
  }
  
  try {
    jwt.verify(token, JWT_SECRET);
    
    res.json({
      code: 200,
      data: {
        records: db.customers,
        total: db.customers.length,
        pageNum: 1,
        pageSize: 10
      }
    });
  } catch (error) {
    res.status(401).json({ code: 401, message: 'token无效' });
  }
});

app.post('/api/customers', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未授权' });
  }
  
  try {
    jwt.verify(token, JWT_SECRET);
    
    const customer = {
      id: customerId++,
      customerCode: `C${new Date().getFullYear()}${(new Date().getMonth() + 1).toString().padStart(2, '0')}${customerId.toString().padStart(4, '0')}`,
      ...req.body,
      status: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    db.customers.push(customer);
    
    res.json({
      code: 200,
      message: '创建成功',
      data: customer
    });
  } catch (error) {
    res.status(401).json({ code: 401, message: 'token无效' });
  }
});

// 项目管理API
app.get('/api/projects', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未授权' });
  }
  
  try {
    jwt.verify(token, JWT_SECRET);
    
    const projectsWithCustomer = db.projects.map(project => {
      const customer = db.customers.find(c => c.id === project.customerId);
      return {
        ...project,
        customerName: customer ? customer.companyName : '未知客户'
      };
    });
    
    res.json({
      code: 200,
      data: {
        records: projectsWithCustomer,
        total: db.projects.length,
        pageNum: 1,
        pageSize: 10
      }
    });
  } catch (error) {
    res.status(401).json({ code: 401, message: 'token无效' });
  }
});

app.post('/api/projects', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未授权' });
  }
  
  try {
    jwt.verify(token, JWT_SECRET);
    
    const project = {
      id: projectId++,
      projectCode: `P${new Date().getFullYear()}${(new Date().getMonth() + 1).toString().padStart(2, '0')}${projectId.toString().padStart(4, '0')}`,
      ...req.body,
      currentPhase: 'system_registry',
      status: 'active',
      progress: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    db.projects.push(project);
    
    res.json({
      code: 200,
      message: '创建成功',
      data: project
    });
  } catch (error) {
    res.status(401).json({ code: 401, message: 'token无效' });
  }
});

// 系统登记API
app.post('/api/systems', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未授权' });
  }
  
  try {
    jwt.verify(token, JWT_SECRET);
    
    const system = {
      id: systemId++,
      ...req.body,
      status: 'registered',
      isSelected: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    db.systems.push(system);
    
    res.json({
      code: 200,
      message: '创建成功',
      data: system
    });
  } catch (error) {
    res.status(401).json({ code: 401, message: 'token无效' });
  }
});

// 价值评估API
app.post('/api/assessments', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未授权' });
  }
  
  try {
    jwt.verify(token, JWT_SECRET);
    
    const assessment = {
      id: assessmentId++,
      ...req.body,
      reviewStatus: 'pending',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    db.assessments.push(assessment);
    
    res.json({
      code: 200,
      message: '创建成功',
      data: assessment
    });
  } catch (error) {
    res.status(401).json({ code: 401, message: 'token无效' });
  }
});

// 生成客户编码
app.get('/api/customers/generate-code', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未授权' });
  }
  
  try {
    jwt.verify(token, JWT_SECRET);
    
    const code = `C${new Date().getFullYear()}${(new Date().getMonth() + 1).toString().padStart(2, '0')}${(db.customers.length + 1).toString().padStart(4, '0')}`;
    
    res.json({
      code: 200,
      data: code
    });
  } catch (error) {
    res.status(401).json({ code: 401, message: 'token无效' });
  }
});

// 生成项目编码
app.get('/api/projects/generate-code', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未授权' });
  }
  
  try {
    jwt.verify(token, JWT_SECRET);
    
    const code = `P${new Date().getFullYear()}${(new Date().getMonth() + 1).toString().padStart(2, '0')}${(db.projects.length + 1).toString().padStart(4, '0')}`;
    
    res.json({
      code: 200,
      data: code
    });
  } catch (error) {
    res.status(401).json({ code: 401, message: 'token无效' });
  }
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`数据资产平台API服务运行在 http://localhost:${PORT}`);
  console.log('可用端点:');
  console.log('  GET  /api/health              - 健康检查');
  console.log('  POST /api/auth/login         - 用户登录');
  console.log('  GET  /api/auth/me            - 当前用户');
  console.log('  GET  /api/customers          - 客户列表');
  console.log('  POST /api/customers          - 创建客户');
  console.log('  GET  /api/projects           - 项目列表');
  console.log('  POST /api/projects           - 创建项目');
  console.log('  POST /api/systems            - 系统登记');
  console.log('  POST /api/assessments        - 价值评估');
  console.log('');
  console.log('默认账号:');
  console.log('  用户名: admin');
  console.log('  密码: admin123');
});
