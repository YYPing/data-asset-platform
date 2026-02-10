<template>
  <div class="empty-state">
    <el-icon class="empty-state__icon" :size="iconSize">
      <component :is="iconComponent" />
    </el-icon>
    <p class="empty-state__text">{{ text }}</p>
    <div v-if="$slots.default" class="empty-state__action">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DocumentDelete, FolderOpened, DataLine, Box } from '@element-plus/icons-vue'

interface Props {
  type?: 'no-data' | 'no-result' | 'no-content' | 'empty'
  text?: string
  iconSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'no-data',
  iconSize: 80,
})

// 根据类型选择图标和默认文本
const iconComponent = computed(() => {
  const iconMap = {
    'no-data': Box,
    'no-result': DataLine,
    'no-content': FolderOpened,
    'empty': DocumentDelete,
  }
  return iconMap[props.type]
})

const text = computed(() => {
  if (props.text) return props.text

  const textMap = {
    'no-data': '暂无数据',
    'no-result': '未找到相关结果',
    'no-content': '暂无内容',
    'empty': '空空如也',
  }
  return textMap[props.type]
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state__icon {
  color: #dcdfe6;
  margin-bottom: 16px;
}

.empty-state__text {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: #909399;
}

.empty-state__action {
  margin-top: 8px;
}
</style>
