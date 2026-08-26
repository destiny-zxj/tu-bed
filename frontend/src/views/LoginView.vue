<script setup lang="ts">
import { ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useMessage, NCard, NForm, NFormItem, NInput, NButton, NText } from "naive-ui"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const route = useRoute()
const message = useMessage()
const auth = useAuthStore()

const loading = ref(false)
const form = ref({ username: "", password: "" })

async function onSubmit() {
  if (!form.value.username || !form.value.password) {
    message.warning("请输入用户名和密码")
    return
  }
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    const redirect = (route.query.redirect as string) || (auth.user?.is_admin ? "/admin" : "/app")
    message.success("登录成功")
    router.push(redirect)
  } catch {
    message.error("登录失败，请检查用户名或密码")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap app-aurora">
    <n-card class="login-card glass rise-in" :bordered="false">
      <div class="login-head">
        <div class="login-logo">Tu</div>
        <div class="app-title" style="margin-top: 16px">TuBed 图床</div>
        <div class="app-caption" style="margin-top: 6px">登录以管理你的图片空间</div>
      </div>

      <n-form @submit.prevent="onSubmit" style="margin-top: 28px">
        <n-form-item label="用户名" :show-feedback="false">
          <n-input
            v-model:value="form.username"
            placeholder="用户名"
            size="large"
            autocomplete="username"
          />
        </n-form-item>
        <n-form-item label="密码" :show-feedback="false" style="margin-top: 4px">
          <n-input
            v-model:value="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password-on="click"
            autocomplete="current-password"
            @keyup.enter="onSubmit"
          />
        </n-form-item>
        <n-button
          class="press"
          type="primary"
          block
          size="large"
          :loading="loading"
          style="margin-top: 18px; font-weight: 600"
          @click="onSubmit"
        >
          登录
        </n-button>
      </n-form>

      <div class="app-caption" style="text-align: center; margin-top: 18px; opacity: 0.7">
        简洁 · 安全 · 极速的私有图床
      </div>
    </n-card>
  </div>
</template>

<style scoped>
.login-wrap {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.login-card {
  width: 380px;
  max-width: 100%;
  border-radius: var(--r-xl);
  padding: 32px 28px;
}
.login-head {
  text-align: center;
}
.login-logo {
  width: 64px;
  height: 64px;
  margin: 0 auto;
  border-radius: 18px;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.02em;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
}
</style>
