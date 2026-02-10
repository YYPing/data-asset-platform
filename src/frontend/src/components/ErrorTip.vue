<template>
  <div class="error-tip" :class="[`error-tip--${type}`, { 'error-tip--closable': closable }]">
    <el-icon class="error-tip__icon" :size="iconSize">
      <component :is="iconComponent" />
    </el-icon>
    <div class="error-tip__content">
      <p v-if="title" class="error-tip__title">{{ title }}</p>
      <p class="error-tip__message">{{ message }}</p>
      <div v-if="$slots.default" class="error-tip__extra">
        <slot />
      </div>
    </div>
    <el-icon v-if="closable" class="error-tip__close" @click="handleClose">
      <Close />
    </el-icon>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Close, WarningFilled, CircleCloseFilled, InfoFilled, SuccessFilled } from '@element-plus/icons-vue'

interface Props {
  type?: 'error' | 'warning' | 'info' | 'success'
  title?: string
  message: string
  closable?: boolean
  iconSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'error',
  closable: false,
  iconSize: 24,
})

const emit = defineEmits<{
  close: []
}>()

// 根据类型选择图标
const iconComponent = computed(() => {
  const iconMap = {
    error: CircleCloseFilled,
    warning: WarningFilled,
    info: InfoFilled,
    success: SuccessFilled,
  }
  return iconMap[props.type]
})

// 关闭处理
const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.error-tip {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border-radius: 8px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error-tip--error {
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.error-tip--error .error-tip__icon {
  color: #f56c6c;
}

.error-tip--warning {
  border-color: #e6a23c;
  background-color: #fdf6ec;
}

.error-tip--warning .error-tip__icon {
  color: #e6a23c;
}

.error-tip--info {
  border-color: #909399;
  background-color: #f4f4f5;
}

.error-tip--info .error-tip__icon {
  color: #909399;
}

.error-tip--success {
  border-color: #67c23a;
  background-color: #f0f9ff;
}

.error-tip--success .error-tip__icon {
  color: #67c23a;
}

.error-tip__icon {
  flex-shrink: 0;
  margin-right: 12px;
}

.error-tip__content {
  flex: 1;
}

.error-tip__title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.error-tip__message {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.error-tip__extra {
  margin-top: 12px;
}

.error-tip__close {
  flex-shrink: 0;
  margin-left: 12px;
  cursor: pointer;
  color: #909399;
  transition: color 0.3s;
}

.error-tip__close:hover {
  color: #606266;
}

.error-tip--closable {
  padding-right: 40px;
  position: relative;
}

.error-tip--closable .error-tip__close {
  position: absolute;
  top: 16px;
  right: 16px;
}
</style>
