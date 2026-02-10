<template>
  <LoginLayout>
    <div class="login-card">
      <div class="login-header">
        <div class="logo-wrapper">
          <img src="/logo.png" alt="Logo" class="logo" />
        </div>
        <h1 class="login-title">数据资产管理平台</h1>
        <p class="login-subtitle">政府数据资产登记试点系统</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
            clearable
            autocomplete="username"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            clearable
            autocomplete="current-password"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="captcha" v-if="showCaptcha">
          <div class="captcha-wrapper">
            <el-input
              v-model="loginForm.captcha"
              placeholder="请输入验证码"
              size="large"
              clearable
              maxlength="4"
            >
              <template #prefix>
                <el-icon><Key /></el-icon>
              </template>
            </el-input>
            <div class="captcha-image" @click="refreshCaptcha">
              <img v-if="captchaUrl" :src="captchaUrl" alt="验证码" />
              <span v-else class="captcha-placeholder">点击获取</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item>
          <div class="login-options">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <a href="#" class="forgot-password" @click.prevent="handleForgotPassword">忘记密码？</a>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>

        <!-- 第三方登录预留 -->
        <div v-if="showThirdPartyLogin" class="third-party-login">
          <el-divider>其他登录方式</el-divider>
          <div class="third-party-buttons">
            <el-tooltip content="微信登录" placement="top">
              <el-button circle :icon="ChatDotRound" @click="handleThirdPartyLogin('wechat')" />
            </el-tooltip>
            <el-tooltip content="企业微信登录" placement="top">
              <el-button circle :icon="OfficeBuilding" @click="handleThirdPartyLogin('work-wechat')" />
            </el-tooltip>
            <el-tooltip content="钉钉登录" placement="top">
              <el-button circle :icon="Notification" @click="handleThirdPartyLogin('dingtalk')" />
            </el-tooltip>
          </div>
        </div>
      </el-form>

      <!-- 快速登录提示（开发环境） -->
      <div v-if="isDev" class="dev-tips">
        <el-alert
          title="开发环境快速登录"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <div class="quick-login-list">
              <div v-for="account in devAccounts" :key="account.username" class="quick-login-item">
                <span>{{ account.label }}：</span>
                <el-link type="primary" @click="quickLogin(account)">
                  {{ account.username }} / {{ account.password }}
                </el-link>
              </div>
            </div>
          </template>
        </el-alert>
      </div>
    </div>
  </LoginLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Key, ChatDotRound, OfficeBuilding, Notification } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { requiredRule, usernameRule, lengthRule } from '@/utils/validate'
import LoginLayout from '@/layouts/LoginLayout.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const showCaptcha = ref(false) // 是否显示验证码
const captchaUrl = ref('') // 验证码图片URL
const showThirdPartyLogin = ref(false) // 是否显示第三方登录

// 是否为开发环境
const isDev = computed(() => import.meta.env.DEV)

// 开发环境快速登录账号
const devAccounts = [
  { username: 'admin', password: 'admin123', label: '管理员' },
  { username: 'auditor', password: 'auditor123', label: '审核员' },
  { username: 'holder', password: 'holder123', label: '数据持有方' },
  { username: 'evaluator', password: 'evaluator123', label: '评估机构' },
]

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
  captcha: '',
  remember: false,
})

// 表单验证规则
const loginRules: FormRules = {
  username: [
    requiredRule('请输入用户名'),
    usernameRule(),
  ],
  password: [
    requiredRule('请输入密码'),
    lengthRule(6, 20),
  ],
  captcha: showCaptcha.value
    ? [requiredRule('请输入验证码'), lengthRule(4, 4, '验证码为4位')]
    : [],
}

// 从本地存储恢复记住的用户名
onMounted(() => {
  const rememberedUsername = localStorage.getItem('remembered_username')
  if (rememberedUsername) {
    loginForm.username = rememberedUsername
    loginForm.remember = true
  }

  // 如果需要验证码，加载验证码
  if (showCaptcha.value) {
    refreshCaptcha()
  }
})

// 刷新验证码
const refreshCaptcha = () => {
  // 实际项目中应该调用后端API获取验证码
  captchaUrl.value = `/api/v1/auth/captcha?t=${Date.now()}`
}

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    // 验证表单
    await loginFormRef.value.validate()

    loading.value = true

    // 调用登录接口
    const success = await userStore.login({
      username: loginForm.username,
      password: loginForm.password,
    })

    if (success) {
      // 处理"记住我"
      if (loginForm.remember) {
        localStorage.setItem('remembered_username', loginForm.username)
      } else {
        localStorage.removeItem('remembered_username')
      }

      ElMessage.success('登录成功')

      // 获取重定向路径
      const redirect = (route.query.redirect as string) || '/dashboard'

      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        router.push(redirect)
      }, 500)
    }
  } catch (error: any) {
    console.error('Login error:', error)
    if (error.message) {
      ElMessage.error(error.message)
    }
  } finally {
    loading.value = false
  }
}

// 忘记密码
const handleForgotPassword = () => {
  ElMessage.info('请联系系统管理员重置密码')
}

// 第三方登录
const handleThirdPartyLogin = (type: string) => {
  ElMessage.info(`${type} 登录功能开发中...`)
}

// 快速登录（开发环境）
const quickLogin = (account: { username: string; password: string }) => {
  loginForm.username = account.username
  loginForm.password = account.password
  loginForm.remember = false
  handleLogin()
}
</script>

<style scoped>
.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.logo {
  width: 64px;
  height: 64px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  margin-top: 20px;
}

.captcha-wrapper {
  display: flex;
  gap: 12px;
  width: 100%;
}

.captcha-wrapper :deep(.el-input) {
  flex: 1;
}

.captcha-image {
  width: 120px;
  height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  transition: border-color 0.3s;
}

.captcha-image:hover {
  border-color: #409eff;
}

.captcha-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.captcha-placeholder {
  font-size: 12px;
  color: #909399;
}

.login-options {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-password {
  font-size: 14px;
  color: #409eff;
  text-decoration: none;
  transition: color 0.3s;
}

.forgot-password:hover {
  color: #66b1ff;
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
}

.third-party-login {
  margin-top: 24px;
}

.third-party-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
}

.dev-tips {
  margin-top: 24px;
}

.quick-login-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
}

.quick-login-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-input__wrapper) {
  padding: 12px 15px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    padding: 30px 20px;
  }

  .login-title {
    font-size: 24px;
  }

  .captcha-wrapper {
    flex-direction: column;
  }

  .captcha-image {
    width: 100%;
  }
}
</style>
