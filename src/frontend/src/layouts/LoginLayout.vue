<template>
  <div class="login-layout">
    <div class="login-background">
      <div class="background-overlay"></div>
      <div class="background-pattern"></div>
    </div>

    <div class="login-content">
      <slot />
    </div>

    <div class="login-footer">
      <p>© 2026 数据资产管理平台 版权所有</p>
      <p class="footer-links">
        <a href="#">使用条款</a>
        <span class="separator">|</span>
        <a href="#">隐私政策</a>
        <span class="separator">|</span>
        <a href="#">帮助中心</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 登录布局组件，提供统一的登录页面布局
</script>

<style scoped>
.login-layout {
  position: relative;
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 0;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3), transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(138, 43, 226, 0.3), transparent 50%),
    radial-gradient(circle at 40% 20%, rgba(75, 0, 130, 0.2), transparent 50%);
  animation: pulse 15s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.background-pattern {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: movePattern 20s linear infinite;
}

@keyframes movePattern {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

.login-content {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 480px;
  padding: 20px;
}

.login-footer {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  z-index: 1;
}

.login-footer p {
  margin: 4px 0;
}

.footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: #fff;
}

.separator {
  color: rgba(255, 255, 255, 0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-content {
    max-width: 100%;
    padding: 20px;
  }

  .login-footer {
    font-size: 11px;
  }

  .footer-links {
    flex-direction: column;
    gap: 4px;
  }

  .separator {
    display: none;
  }
}
</style>
