// 数据资产平台 - API测试脚本

const axios = require('axios');

const API_BASE = 'http://localhost:3000/api';
let token = '';

async function testAPI() {
  console.log('🚀 开始测试数据资产平台API...\n');

  try {
    // 1. 健康检查
    console.log('1. 测试健康检查...');
    const healthRes = await axios.get(`${API_BASE}/health`);
    console.log(`   ✅ 健康检查: ${JSON.stringify(healthRes.data)}\n`);

    // 2. 用户登录
    console.log('2. 测试用户登录...');
    const loginRes = await axios.post(`${API_BASE}/auth/login`, {
      username: 'admin',
      password: 'admin123'
    });
    
    if (loginRes.data.code === 200) {
      token = loginRes.data.data.token;
      console.log(`   ✅ 登录成功: ${loginRes.data.data.username}`);
      console.log(`   Token: ${token.substring(0, 30)}...\n`);
    } else {
      throw new Error('登录失败');
    }

    // 3. 获取当前用户
    console.log('3. 测试获取当前用户...');
    const meRes = await axios.get(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log(`   ✅ 当前用户: ${meRes.data.data.realName}\n`);

    // 4. 生成客户编码
    console.log('4. 测试生成客户编码...');
    const customerCodeRes = await axios.get(`${API_BASE}/customers/generate-code`, {
      headers: { Authorization: `Bearer ${token}` }
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

    const createCustomerRes = await axios.post(`${API_BASE}/customers`, customerData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log(`   ✅ 创建客户成功: ${createCustomerRes.data.data.companyName}`);
    console.log(`   客户ID: ${createCustomerRes.data.data.id}\n`);

    // 6. 查询客户列表
    console.log('6. 测试查询客户列表...');
    const customersRes = await axios.get(`${API_BASE}/customers`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log(`   ✅ 查询成功，共 ${customersRes.data.data.total} 个客户\n`);

    // 7. 生成项目编码
    console.log('7. 测试生成项目编码...');
    const projectCodeRes = await axios.get(`${API_BASE}/projects/generate-code`, {
      headers: { Authorization: `Bearer ${token}` }
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

    const createProjectRes = await axios.post(`${API_BASE}/projects`, projectData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log(`   ✅ 创建项目成功: ${createProjectRes.data.data.projectName}`);
    console.log(`   项目ID: ${createProjectRes.data.data.id}\n`);

    // 9. 查询项目列表
    console.log('9. 测试查询项目列表...');
    const projectsRes = await axios.get(`${API_BASE}/projects`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log(`   ✅ 查询成功，共 ${projectsRes.data.data.total} 个项目\n`);

    // 10. 系统登记
    console.log('10. 测试系统登记...');
    const systemData = {
      projectId: createProjectRes.data.data.id,
      systemName: 'CRM客户关系管理系统',
      systemType: 'business',
      businessDomain: '销售管理',
      description: '客户关系管理核心系统',
      vendor: '用友软件',
      version: 'V3.0',
      databaseType: 'MySQL',
      estimatedDataVolume: '100GB',
      businessCriticality: 4
    };

    const createSystemRes = await axios.post(`${API_BASE}/systems`, systemData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log(`   ✅ 系统登记成功: ${createSystemRes.data.data.systemName}\n`);

    // 11. 价值评估
    console.log('11. 测试价值评估...');
    const assessmentData = {
      systemId: createSystemRes.data.data.id,
      projectId: createProjectRes.data.data.id,
      businessValueScore: 85.5,
      dataQualityScore: 78.0,
      complianceRiskScore: 65.0,
      technicalFeasibilityScore: 90.0,
      totalScore: 82.5,
      recommendation: 'priority',
      priorityLevel: 'high',
      estimatedBenefit: 1200000,
      estimatedCost: 500000,
      estimatedEffortDays: 90
    };

    const createAssessmentRes = await axios.post(`${API_BASE}/assessments`, assessmentData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log(`   ✅ 价值评估成功，综合评分: ${createAssessmentRes.data.data.totalScore}\n`);

    // 测试总结
    console.log('🎉 所有API测试完成！');
    console.log('='.repeat(50));
    console.log('测试结果总结:');
    console.log(`  ✅ 健康检查`);
    console.log(`  ✅ 用户登录认证`);
    console.log(`  ✅ 客户管理 (创建、查询)`);
    console.log(`  ✅ 项目管理 (创建、查询)`);
    console.log(`  ✅ 系统登记`);
    console.log(`  ✅ 价值评估`);
    console.log('');
    console.log('📊 数据统计:');
    console.log(`  客户数量: ${customersRes.data.data.total}`);
    console.log(`  项目数量: ${projectsRes.data.data.total}`);
    console.log(`  系统数量: 1`);
    console.log(`  评估数量: 1`);
    console.log('');
    console.log('🔗 API服务运行在: http://localhost:3000');
    console.log('='.repeat(50));

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    if (error.response) {
      console.error('响应数据:', error.response.data);
    }
    process.exit(1);
  }
}

// 运行测试
testAPI();
