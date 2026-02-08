<template>
  <div class="asset-list-container">
    <!-- 搜索栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.q"
            placeholder="资产名称/编号"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="阶段">
          <el-select
            v-model="searchForm.stage"
            placeholder="请选择阶段"
            clearable
            style="width: 150px"
          >
            <el-option label="登记" value="registration" />
            <el-option label="盘点" value="inventory" />
            <el-option label="评估" value="evaluation" />
            <el-option label="入表" value="cataloging" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="searchForm.category"
            placeholder="请选择分类"
            clearable
            style="width: 150px"
          >
            <el-option label="业务数据" value="business" />
            <el-option label="技术数据" value="technical" />
            <el-option label="管理数据" value="management" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="toolbar-card" shadow="never">
      <el-button
        v-if="hasRole('holder')"
        type="primary"
        :icon="Plus"
        @click="handleCreate"
      >
        新建资产
      </el-button>
    </el-card>

    <!-- 表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="asset_code" label="资产编号" width="180" />
        <el-table-column prop="asset_name" label="资产名称" min-width="200" />
        <el-table-column
          prop="organization_name"
          label="所属组织"
          width="150"
        />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            {{ getCategoryLabel(row.category) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_stage" label="当前阶段" width="120">
          <template #default="{ row }">
            <el-tag :type="getStageTagType(row.current_stage)">
              {{ getStageLabel(row.current_stage) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="estimated_value" label="估值" width="120">
          <template #default="{ row }">
            {{ row.estimated_value ? `¥${row.estimated_value.toLocaleString()}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              :icon="View"
              @click="handleView(row.id)"
            >
              查看
            </el-button>
            <el-button
              v-if="row.status === 'draft'"
              type="primary"
              link
              :icon="Edit"
              @click="handleEdit(row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'draft'"
              type="success"
              link
              :icon="Upload"
              @click="handleSubmit(row)"
            >
              提交
            </el-button>
            <el-button
              v-if="row.status === 'draft'"
              type="danger"
              link
              :icon="Delete"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Plus,
  View,
  Edit,
  Delete,
  Upload
} from '@element-plus/icons-vue'
import { getAssetList, deleteAsset, submitAsset, type Asset } from '@/api/asset'
import { hasRole } from '@/utils/permission'

const router = useRouter()

// ==================== 状态管理 ====================

const loading = ref(false)
const tableData = ref<Asset[]>([])

const searchForm = reactive({
  q: '',
  status: '',
  stage: '',
  category: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// ==================== 生命周期 ====================

onMounted(() => {
  loadData()
})

// ==================== 数据加载 ====================

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      q: searchForm.q || undefined,
      status: searchForm.status || undefined,
      stage: searchForm.stage || undefined,
      category: searchForm.category || undefined
    }
    const res = await getAssetList(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// ==================== 搜索操作 ====================

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.q = ''
  searchForm.status = ''
  searchForm.stage = ''
  searchForm.category = ''
  pagination.page = 1
  loadData()
}

// ==================== 分页操作 ====================

const handleSizeChange = (val: number) => {
  pagination.page_size = val
  pagination.page = 1
  loadData()
}

const handleCurrentChange = (val: number) => {
  pagination.page = val
  loadData()
}

// ==================== CRUD 操作 ====================

const handleCreate = () => {
  router.push('/assets/create')
}

const handleView = (id: number) => {
  router.push(`/assets/${id}`)
}

const handleEdit = (id: number) => {
  router.push(`/assets/${id}/edit`)
}

const handleSubmit = async (row: Asset) => {
  try {
    await ElMessageBox.confirm(
      `确定要提交资产"${row.asset_name}"进行审批吗？`,
      '提交确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    loading.value = true
    await submitAsset(row.id)
    ElMessage.success('提交成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '提交失败')
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}

const handleDelete = async (row: Asset) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除资产"${row.asset_name}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    loading.value = true
    await deleteAsset(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}

// ==================== 辅助函数 ====================

const getCategoryLabel = (category: string) => {
  const map: Record<string, string> = {
    business: '业务数据',
    technical: '技术数据',
    management: '管理数据'
  }
  return map[category] || category
}

const getStageLabel = (stage: string) => {
  const map: Record<string, string> = {
    registration: '登记',
    inventory: '盘点',
    evaluation: '评估',
    cataloging: '入表'
  }
  return map[stage] || stage
}

const getStageTagType = (stage: string) => {
  const map: Record<string, any> = {
    registration: '',
    inventory: 'warning',
    evaluation: 'success',
    cataloging: 'info'
  }
  return map[stage] || ''
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    pending: '待审批',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, any> = {
    draft: 'info',
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return map[status] || ''
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped lang="scss">
.asset-list-container {
  padding: 20px;

  .search-card,
  .toolbar-card,
  .table-card {
    margin-bottom: 20px;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
