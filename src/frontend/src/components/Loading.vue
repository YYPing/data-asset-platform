<template>
  <div v-if="visible" class="loading-overlay" :class="{ fullscreen }">
    <div class="loading-content">
      <el-icon class="loading-icon" :size="size">
        <Loading />
      </el-icon>
      <p v-if="text" class="loading-text">{{ text }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Loading } from '@element-plus/icons-vue'

interface Props {
  visible?: boolean
  text?: string
  fullscreen?: boolean
  size?: number
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  text: '加载中...',
  fullscreen: true,
  size: 40,
})

// 本地状态，用于控制显示
const visible = ref(props.visible)

// 监听 props 变化
watch(
  () => props.visible,
  (newVal) => {
    visible.value = newVal
  }
)
</script>

<style scoped>
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 2000;
}

.loading-overlay.fullscreen {
  position: fixed;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-icon {
  color: #409eff;
  animation: rotate 1.5s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin: 0;
  font-size: 14px;
  color: #606266;
}
</style>
