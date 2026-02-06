// 数据资产平台 - 纯Node.js版本（无外部依赖）
// 可以立即运行

const http = require('http');
const url = require('url');
const { StringDecoder } = require('string_decoder');

const PORT = 3000;

// 内存数据库
const db = {
  users: [
    {
      id: 1,
      username: 'admin',
      password: 'admin123', // 简化版本，实际应该加密
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

// 简单的JWT实现（仅用于演示）
const JWT_SECRET = 'data-asset-platform-secret';

function createToken(payload) {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64');
  const data = Buffer.from(JSON.stringify(payload)).toString('base64');
  const signature = 'demo-signature'; // 简化版本
  return `${header}.${data}.${signature}`;
}

function verifyToken(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const data = JSON.parse(Buffer.from(parts[1], 'base64').toString());
    return data;
  } catch (error) {
    return null;
  }
}

// 请求处理器
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const method = req.method.toUpperCase();
  
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // 收集请求体
  const decoder = new StringDecoder('utf-8');
  let buffer = '';
  
  req.on('data', (data) => {
    buffer += decoder.write(data);
  });
  
  req.on('end', () => {
    buffer += decoder.end();
    
    let requestData = {};
    if (buffer) {
      try {
        requestData = JSON.parse(buffer);
      } catch (e) {
        // 不是JSON数据
      }
    }
    
    // 路由处理
    let response = { code: 404, message: 'Not Found' };
    
    // 健康检查
    if (path === '/api/health' && method === 'GET') {
      response = {
        code: 200,
        data: {
          status: 'UP',
          service: 'data-asset-platform',
          version: '1.0.0',
          timestamp: new Date().toISOString()
        }
      };
    }
    
    // 用户登录
    else if (path === '/api/auth/login' && method === 'POST') {
      const { username, password } = requestData;
      const user = db.users.find(u => u.username === username && u.password === password);
      
      if (user) {
        const token = createToken({
          userId: user.id,
          username: user.username,
          userType: user.userType
        });
        
        response = {
          code: 200,
          message: '登录成功',
          data: {
            userId: user.id,
            username: user.username,
            realName: user.realName,
            userType: user.userType,
            token: token,
            expiresIn: 24 * 60 * 60 * 1000
          }
        };
      } else {
        response = { code: 401, message: '用户名或密码错误' };
      }
    }
    
    // 获取当前用户
    else if (path === '/api/auth/me' && method === 'GET') {
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        response = { code: 401, message: '未授权' };
      } else {
        const token = authHeader.substring(7);
        const decoded = verifyToken(token);
        
        if (decoded) {
          const user = db.users.find(u => u.id === decoded.userId);
          if (user) {
            response = {
              code: 200,
              data: {
                userId: user.id,
                username: user.username,
                realName: user.realName,
                userType: user.userType
              }
            };
          } else {
            response = { code: 401, message: '用户不存在' };
          }
        } else {
          response = { code: 401, message: 'token无效' };
        }
      }
    }
    
    // 客户列表
    else if (path === '/api/customers' && method === 'GET') {
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        response = { code: 401, message: '未授权' };
      } else {
        const token = authHeader.substring(7);
        const decoded = verifyToken(token);
        
        if (decoded) {
          response = {
            code: 200,
            data: {
              records: db.customers,
              total: db.customers.length,
              pageNum: 1,
              pageSize: 10
            }
          };
        } else {
          response = { code: 401, message: 'token无效' };
        }
      }
    }
    
    // 创建客户
    else if (path === '/api/customers' && method === 'POST') {
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        response = { code: 401, message: '未授权' };
      } else {
        const token = authHeader.substring(7);
        const decoded = verifyToken(token);
        
        if (decoded) {
          const customer = {
            id: customerId++,
            customerCode: `C${new Date().getFullYear()}${(new Date().getMonth() + 1).toString().padStart(2, '0')}${customerId.toString().padStart(4, '0')}`,
            ...requestData,
            status: 1,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          };
          
          db.customers.push(customer);
          
          response = {
            code: 200,
            message: '创建成功',
            data: customer
          };
        } else {
          response = { code: 401, message: 'token无效' };
        }
      }
    }
    
    // 项目列表
    else if (path === '/api/projects' && method === 'GET') {
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        response = { code: 401, message: '未授权' };
      } else {
        const token = authHeader.substring(7);
        const decoded = verifyToken(token);
        
        if (decoded) {
          const projectsWithCustomer = db.projects.map(project => {
            const customer = db.customers.find(c => c.id === project.customerId);
            return {
              ...project,
              customerName: customer ? customer.companyName : '未知客户'
            };
          });
          
          response = {
            code: 200,
            data: {
              records: projectsWithCustomer,
              total: db.projects.length,
              pageNum: 1,
              pageSize: 10
            }
          };
        } else {
          response = { code: 401, message: 'token无效' };
        }
      }
    }
    
    // 创建项目
    else if (path === '/api/projects' && method === 'POST') {
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        response = { code: 401, message: '未授权' };
      } else {
        const token = authHeader.substring(7);
        const decoded = verifyToken(token);
        
        if (decoded) {
          const project = {
            id: projectId++,
            projectCode: `P${new Date().getFullYear()}${(new Date().getMonth() + 1).toString().padStart(2, '0')}${projectId.toString().padStart(4, '0')}`,
            ...requestData,
            currentPhase: 'system_registry',
            status: 'active',
            progress: 0,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          };
          
          db.projects.push(project);
          
          response = {
            code: 200,
            message: '创建成功',
            data: project
          };
        } else {
          response = { code: 401, message: 'token无效' };
        }
      }
    }
    
    // 生成客户编码
    else if (path === '/api/customers/generate-code' && method === 'GET') {
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        response = { code: 401, message: '未授权' };
      } else {
        const token = authHeader.substring(7);
        const decoded = verifyToken(token);
        
        if (decoded) {
          const code = `C${new Date().getFullYear()}${(new Date().getMonth() + 1).toString().padStart(2, '0')}${(db.customers.length + 1).toString().padStart(4, '0')}`;
          
          response = {
            code: 200,
            data: code
          };
        } else {
          response = { code: 401, message: 'token无效' };
        }
      }
    }
    
    // 生成项目编码
    else if (path === '/api/projects/generate-code' && method === 'GET') {
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        response = { code: 401, message: '未授权' };
      } else {
        const token = authHeader.substring(7);
        const decoded = verifyToken(token);
        
        if (decoded) {
          const code = `P${new Date().getFullYear()}${(new Date().getMonth() + 1).toString().padStart(2, '0')}${(db.projects.length + 1).toString().padStart(4, '0')}`;
          
          response = {
            code: 200,
            data: code
          };
        } else {
          response = { code: 401, message: 'token无效' };
        }
      }
    }
    
    // 返回响应
    res.setHeader('Content-Type', 'application/json');
    res.writeHead(response.code === 200 ? 200 : (response.code || 500));
    res.end(JSON.stringify(response, null, 2));
  });
});

// 启动服务器
server.listen(PORT, () => {
  console.log(`✅ 数据资产平台API服务运行在 http://localhost:${PORT}`);
  console.log('');
  console.log('📋 可用API端点:');
  console.log('  GET  /api/health              - 健康检查');
  console.log('  POST /api/auth/login         - 用户登录');
  console.log('  GET  /api/auth/me            - 当前用户');
  console.log('  GET  /api/customers          - 客户列表');
  console.log('  POST /api/customers          - 创建客户');
  console.log('  GET  /api/projects           - 项目列表');
  console.log('  POST /api/projects           - 创建项目');
  console.log('  GET  /api/customers/generate-code - 生成客户编码');
  console.log('  GET  /api/projects/generate-code  - 生成项目编码');
  console.log('');
  console.log('🔐 默认账号:');
  console.log('  用户名: admin');
  console.log('  密码: admin123');
  console.log('');
  console.log('🚀 测试命令:');
  console.log('  curl http://localhost:3000/api/health');
  console.log('');
  console.log('按 Ctrl+C 停止服务');
});

// 优雅关闭
process.on('SIGINT', () => {
  console.log('\n👋 正在关闭服务...');
  server.close(() => {
    console.log('✅ 服务已关闭');
    process.exit(0);
  });
});
