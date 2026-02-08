<template>
  <div class="placeholder-container">
    <el-empty description="功能开发中，敬请期待...">
      <el-button type="primary" @click="goBack">返回</el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.placeholder-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background-color: #fff;
  border-radius: 8px;
}
</style>
