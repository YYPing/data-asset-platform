<template>
  <div class="users-container">
    <el-card>
      <!-- 搜索和操作栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名、姓名、邮箱"
            clearable
            style="width: 300px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select
            v-model="filterRole"
            placeholder="角色筛选"
            clearable
            style="width: 150px; margin-left: 10px"
            @change="handleSearch"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="数据管理员" value="data_admin" />
            <el-option label="普通用户" value="user" />
            <el-option label="审计员" value="auditor" />
          </el-select>
        </div>

        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建用户
        </el-button>
      </div>

      <!-- 用户列表 -->
      <el-table
        v-loading="loading"
        :data="userList"
        stripe
        style="margin-top: 20px"
      >
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)">
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="organization_name" label="组织" width="180" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="phone" label="手机" width="130" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button link type="warning" size="small" @click="handleResetPassword(row)">
              重置密码
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @current-change="fetchUsers"
        @size-change="fetchUsers"
      />
    </el-card>

    <!-- 新建/编辑用户弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建用户' : '编辑用户'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username" v-if="dialogMode === 'create'">
          <el-input v-model="formData.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="formData.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="手机" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入手机号" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="数据管理员" value="data_admin" />
            <el-option label="普通用户" value="user" />
            <el-option label="审计员" value="auditor" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="组织" prop="organization_id">
          <el-input-number
            v-model="formData.organization_id"
            :min="1"
            placeholder="组织ID"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="状态" prop="status" v-if="dialogMode === 'edit'">
          <el-radio-group v-model="formData.status">
            <el-radio label="active">正常</el-radio>
            <el-radio label="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="密码" prop="password" v-if="dialogMode === 'create'">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { userApi, type User, type CreateUserData, type UpdateUserData } from '@/api/system'

// 数据状态
const loading = ref(false)
const submitting = ref(false)
const userList = ref<User[]>([])
const searchQuery = ref('')
const filterRole = ref('')

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 弹窗
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formRef = ref<FormInstance>()
const currentUserId = ref<number>()

// 表单数据
const formData = reactive<Partial<CreateUserData & UpdateUserData>>({
  username: '',
  real_name: '',
  email: '',
  phone: '',
  role: '',
  organization_id: undefined,
  password: '',
  status: 'active'
})

// 表单验证规则
const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ]
}

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const data = await userApi.getUsers({
      page: pagination.page,
      page_size: pagination.pageSize,
      q: searchQuery.value || undefined,
      role: filterRole.value || undefined
    })
    userList.value = data.items
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchUsers()
}

// 新建用户
const handleCreate = () => {
  dialogMode.value = 'create'
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (row: User) => {
  dialogMode.value = 'edit'
  currentUserId.value = row.id
  Object.assign(formData, {
    real_name: row.real_name,
    email: row.email,
    phone: row.phone,
    role: row.role,
    organization_id: row.organization_id,
    status: row.status
  })
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (dialogMode.value === 'create') {
        await userApi.createUser(formData as CreateUserData)
        ElMessage.success('创建用户成功')
      } else {
        await userApi.updateUser(currentUserId.value!, formData as UpdateUserData)
        ElMessage.success('更新用户成功')
      }
      dialogVisible.value = false
      fetchUsers()
    } catch (error) {
      ElMessage.error(dialogMode.value === 'create' ? '创建用户失败' : '更新用户失败')
    } finally {
      submitting.value = false
    }
  })
}

// 重置密码
const handleResetPassword = async (row: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置用户 ${row.username} 的密码吗？`,
      '重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const data = await userApi.resetPassword(row.id)
    await ElMessageBox.alert(
      `新密码：${data.new_password}`,
      '密码已重置',
      {
        confirmButtonText: '我已复制',
        type: 'success'
      }
    )
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置密码失败')
    }
  }
}

// 删除用户
const handleDelete = async (row: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 ${row.username} 吗？此操作不可恢复。`,
      '删除用户',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await userApi.deleteUser(row.id)
    ElMessage.success('删除用户成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除用户失败')
    }
  }
}

// 关闭弹窗
const handleDialogClose = () => {
  formRef.value?.resetFields()
  Object.assign(formData, {
    username: '',
    real_name: '',
    email: '',
    phone: '',
    role: '',
    organization_id: undefined,
    password: '',
    status: 'active'
  })
}

// 角色标签类型
const getRoleTagType = (role: string) => {
  const typeMap: Record<string, any> = {
    admin: 'danger',
    data_admin: 'warning',
    auditor: 'info',
    user: ''
  }
  return typeMap[role] || ''
}

// 角色标签文本
const getRoleLabel = (role: string) => {
  const labelMap: Record<string, string> = {
    admin: '管理员',
    data_admin: '数据管理员',
    auditor: '审计员',
    user: '普通用户'
  }
  return labelMap[role] || role
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped lang="scss">
.users-container {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;

  &-left {
    display: flex;
    align-items: center;
  }
}
</style>
