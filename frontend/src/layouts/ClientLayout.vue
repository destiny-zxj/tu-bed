<script setup lang="ts">
import { useRouter } from "vue-router"
import { useMessage, NLayout, NLayoutHeader, NMenu, NAvatar, NText } from "naive-ui"
import type { MenuOption } from "naive-ui"
import { computed, ref, onMounted, onBeforeUnmount } from "vue"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const auth = useAuthStore()
const message = useMessage()

const menuOptions: MenuOption[] = [
  { label: "上传", key: "/app", icon: () => "⬆︎" },
  { label: "我的图片", key: "/app/images", icon: () => "🖼" },
  { label: "API 密钥", key: "/app/apikeys", icon: () => "🔑" },
]

const activeKey = computed(() => {
  const p = router.currentRoute.value.path
  if (p.startsWith("/app/images")) return "/app/images"
  if (p.startsWith("/app/apikeys")) return "/app/apikeys"
  return "/app"
})

function handleSelect(key: string) {
  router.push(key)
}

const userMenuShow = ref(false)
function toggleUser() {
  userMenuShow.value = !userMenuShow.value
}
function handleLogout() {
  userMenuShow.value = false
  auth.logout()
  message.success("已退出登录")
  router.push("/login")
}
function onClickOutside() {
  userMenuShow.value = false
}
onMounted(() => document.addEventListener("click", onClickOutside))
onBeforeUnmount(() => document.removeEventListener("click", onClickOutside))
</script>

<template>
  <n-layout style="height: 100vh" :native-scrollbar="false">
    <n-layout-header class="client-header glass" bordered>
      <div class="brand" @click="router.push('/app')">
        <div class="brand-logo">Tu</div>
        <span class="app-subtitle">TuBed</span>
      </div>
      <n-menu
        mode="horizontal"
        :value="activeKey"
        :options="menuOptions"
        :indent="18"
        class="client-menu"
        @update:value="handleSelect"
      />
      <div class="user-wrap">
        <div class="user-pill press" @click.stop="toggleUser">
          <n-avatar :size="30" round color="#007aff">
            {{ auth.user?.username?.charAt(0)?.toUpperCase() }}
          </n-avatar>
          <n-text style="font-weight: 600">{{ auth.user?.username }}</n-text>
        </div>
        <transition name="dropdown">
          <div v-if="userMenuShow" class="user-menu glass" @click.stop>
            <button class="user-menu-item" @click="handleLogout">退出登录</button>
          </div>
        </transition>
      </div>
    </n-layout-header>

    <div class="client-body">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </n-layout>
</template>

<style scoped>
.client-header {
  display: flex;
  align-items: center;
  gap: 28px;
  height: 60px;
  padding: 0 22px;
  position: sticky;
  top: 0;
  z-index: 20;
  border-bottom: 1px solid var(--separator);
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}
.brand-logo {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}
.client-menu {
  flex: 1;
}
.user-wrap {
  position: relative;
}
.user-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px 4px 4px;
  border-radius: var(--r-pill);
  background: var(--fill);
}
.user-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 140px;
  padding: 6px;
  border-radius: var(--r-md);
  z-index: 50;
}
.user-menu-item {
  display: block;
  width: 100%;
  text-align: left;
  border: none;
  background: transparent;
  padding: 9px 10px;
  border-radius: var(--r-sm);
  font-size: 13px;
  font-weight: 500;
  color: var(--label);
  cursor: pointer;
  transition: background 0.15s var(--ease);
}
.user-menu-item:hover {
  background: var(--fill-hover);
}
.user-menu-item:active {
  background: var(--fill);
}

/* 缓慢下拉：仅垂直滑动 + 淡入，无缩放蹦跳 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.24s var(--ease), transform 0.24s var(--ease);
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
.client-body {
  max-width: 1120px;
  margin: 0 auto;
  padding: 28px 22px 60px;
}

/* 页面切换：弹簧淡入 */
.page-enter-active {
  animation: rise 0.45s var(--spring) both;
}
.page-leave-active {
  transition: opacity 0.18s var(--ease);
}
.page-leave-to {
  opacity: 0;
}
</style>
