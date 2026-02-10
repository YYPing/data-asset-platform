<template>
  <div class="pagination-wrapper">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="currentPageSize"
      :page-sizes="pageSizes"
      :total="total"
      :layout="layout"
      :background="background"
      :small="small"
      :disabled="disabled"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  total: number
  page?: number
  pageSize?: number
  pageSizes?: number[]
  layout?: string
  background?: boolean
  small?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  page: 1,
  pageSize: 20,
  pageSizes: () => [10, 20, 50, 100],
  layout: 'total, sizes, prev, pager, next, jumper',
  background: true,
  small: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:page': [page: number]
  'update:pageSize': [pageSize: number]
  change: [page: number, pageSize: number]
}>()

// 本地状态
const currentPage = ref(props.page)
const currentPageSize = ref(props.pageSize)

// 监听 props 变化
watch(
  () => props.page,
  (newVal) => {
    currentPage.value = newVal
  }
)

watch(
  () => props.pageSize,
  (newVal) => {
    currentPageSize.value = newVal
  }
)

// 页码改变
const handleCurrentChange = (page: number) => {
  emit('update:page', page)
  emit('change', page, currentPageSize.value)
}

// 每页条数改变
const handleSizeChange = (pageSize: number) => {
  // 当改变每页条数时，重置到第一页
  currentPage.value = 1
  emit('update:page', 1)
  emit('update:pageSize', pageSize)
  emit('change', 1, pageSize)
}
</script>

<style scoped>
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 20px 0;
}

:deep(.el-pagination) {
  font-weight: normal;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: #409eff;
  color: #fff;
}
</style>
