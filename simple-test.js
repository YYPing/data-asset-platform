// 数据资产平台 - 简单测试脚本

const http = require('http');

const API_BASE = 'http://localhost:3000/api';
let token = '';

function makeRequest(method, path, data = null, headers = {}) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: 3000,
      path: path,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      }
    };

    const req = http.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsed = JSON.parse(responseData);
          resolve({
            statusCode: res.statusCode,
            data: parsed
          });
        } catch (error) {
          resolve({
            statusCode: res.statusCode,
            data: responseData
          });
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    if (data) {
      req.write(JSON.stringify(data));
    }

    req.end();
  });
}

async function runTests() {
  console.log('🚀 开始测试数据资产平台API...\n');

  try {
    // 1. 健康检查
    console.log('1. 测试健康检查...');
    const healthRes = await makeRequest('GET', '/api/health');
    console.log(`   ✅ 状态: ${healthRes.data.data.status}`);
    console.log(`   服务: ${healthRes.data.data.service}\n`);

    // 2. 用户登录
    console.log('2. 测试用户登录...');
    const loginRes = await makeRequest('POST', '/api/auth/login', {
      username: 'admin',
      password: 'admin123'
    });
    
    if (loginRes.data.code === 200) {
      token = loginRes.data.data.token;
      console.log(`   ✅ 登录成功: ${loginRes.data.data.username}`);
      console.log(`   真实姓名: ${loginRes.data.data.realName}\n`);
    } else {
      throw new Error('登录失败: ' + loginRes.data.message);
    }

    // 3. 获取当前用户
    console.log('3. 测试获取当前用户...');
    const meRes = await makeRequest('GET', '/api/auth/me', null, {
      Authorization: `Bearer ${token}`
    });
    console.log(`   ✅ 当前用户: ${meRes.data.data.realName}\n`);

    // 4. 生成客户编码
    console.log('4. 测试生成客户编码...');
    const customerCodeRes = await makeRequest('GET', '/api/customers/generate-code', null, {
      Authorization: `Bearer ${token}`
    });
    console.log(`   ✅ 客户编码: ${customerCodeRes.data.data}\n`);

    // 5. 创建客户
    console.log('5. 测试创建客户...');
    const customerData = {
      companyName: '测试科技有限公司',
      industry: '信息技术',
      companyScale: 'medium',
      contactName: '张三',
      contactPhone: '13800138000',
      contactEmail: 'zhangsan@test.com',
      registeredAddress: '北京市海淀区测试路1号',
      officeAddress: '北京市朝阳区测试路2号'
    };

    const createCustomerRes = await makeRequest('POST', '/api/customers', customerData, {
      Authorization: `Bearer ${token}`
    });
    console.log(`   ✅ 创建客户成功: ${createCustomerRes.data.data.companyName}`);
    console.log(`   客户ID: ${createCustomerRes.data.data.id}`);
    console.log(`   客户编码: ${createCustomerRes.data.data.customerCode}\n`);

    // 6. 查询客户列表
    console.log('6. 测试查询客户列表...');
    const customersRes = await makeRequest('GET', '/api/customers', null, {
      Authorization: `Bearer ${token}`
    });
    console.log(`   ✅ 查询成功，共 ${customersRes.data.data.total} 个客户\n`);

    // 7. 生成项目编码
    console.log('7. 测试生成项目编码...');
    const projectCodeRes = await makeRequest('GET', '/api/projects/generate-code', null, {
      Authorization: `Bearer ${token}`
    });
    console.log(`   ✅ 项目编码: ${projectCodeRes.data.data}\n`);

    // 8. 创建项目
    console.log('8. 测试创建项目...');
    const projectData = {
      customerId: createCustomerRes.data.data.id,
      projectName: '数据资产价值评估项目',
      projectType: 'consulting',
      description: '为客户提供数据资产价值评估服务',
      contractAmount: 500000,
      startDate: '2026-02-01',
      endDate: '2026-06-30'
    };

    const createProjectRes = await makeRequest('POST', '/api/projects', projectData, {
      Authorization: `Bearer ${token}`
    });
    console.log(`   ✅ 创建项目成功: ${createProjectRes.data.data.projectName}`);
    console.log(`   项目ID: ${createProjectRes.data.data.id}`);
    console.log(`   项目编码: ${createProjectRes.data.data.projectCode}\n`);

    // 9. 查询项目列表
    console.log('9. 测试查询项目列表...');
    const projectsRes = await makeRequest('GET', '/api/projects', null, {
      Authorization: `Bearer ${token}`
    });
    console.log(`   ✅ 查询成功，共 ${projectsRes.data.data.total} 个项目`);
    console.log(`   第一个项目: ${projectsRes.data.data.records[0]?.projectName}\n`);

    // 测试总结
    console.log('🎉 所有API测试完成！');
    console.log('='.repeat(50));
    console.log('测试结果总结:');
    console.log(`  ✅ 健康检查`);
    console.log(`  ✅ 用户登录认证`);
    console.log(`  ✅ 客户管理 (创建、查询)`);
    console.log(`  ✅ 项目管理 (创建、查询)`);
    console.log('');
    console.log('📊 数据统计:');
    console.log(`  客户数量: ${customersRes.data.data.total}`);
    console.log(`  项目数量: ${projectsRes.data.data.total}`);
    console.log('');
    console.log('🔗 API服务运行在: http://localhost:3000');
    console.log('='.repeat(50));

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    process.exit(1);
  }
}

// 运行测试
runTests();
