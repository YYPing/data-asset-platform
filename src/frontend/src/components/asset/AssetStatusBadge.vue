<template>
  <el-tag
    :type="statusType"
    :effect="effect"
    :size="size"
    :round="round"
    :closable="closable"
    @close="handleClose"
  >
    <el-icon v-if="showIcon" class="status-icon">
      <component :is="statusIcon" />
    </el-icon>
    <span>{{ statusLabel }}</span>
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Document,
  Clock,
  CircleCheck,
  CircleClose,
  FolderOpened
} from '@element-plus/icons-vue'
import { getAssetStatusLabel, getAssetStatusType } from '@/utils/asset-helper'
import type { AssetStatus } from '@/types/asset'

interface Props {
  status: AssetStatus | undefined
  showIcon?: boolean
  effect?: 'dark' | 'light' | 'plain'
  size?: 'large' | 'default' | 'small'
  round?: boolean
  closable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showIcon: false,
  effect: 'light',
  size: 'default',
  round: false,
  closable: false
})

const emit = defineEmits<{
  close: []
}>()

// 状态标签文本
const statusLabel = computed(() => getAssetStatusLabel(props.status))

// 状态标签类型
const statusType = computed(() => getAssetStatusType(props.status))

// 状态图标
const statusIcon = computed(() => {
  const iconMap: Record<AssetStatus, any> = {
    draft: Document,
    pending: Clock,
    approved: CircleCheck,
    rejected: CircleClose,
    archived: FolderOpened
  }
  return props.status ? iconMap[props.status] : Document
})

// 关闭事件
const handleClose = () => {
  emit('close')
}
</script>

<style scoped lang="scss">
.status-icon {
  margin-right: 4px;
  vertical-align: middle;
}
</style>
