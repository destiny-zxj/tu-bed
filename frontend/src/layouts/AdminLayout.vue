<script setup lang="ts">
import { useRouter } from "vue-router"
import { NLayout, NLayoutSider, NLayoutHeader, NMenu, NAvatar, NText, NSpace } from "naive-ui"
import type { MenuOption } from "naive-ui"
import { h, computed, ref, onMounted, onBeforeUnmount } from "vue"
import { useAuthStore } from "@/stores/auth"
import { useMessage } from "naive-ui"

const router = useRouter()
const auth = useAuthStore()
const message = useMessage()

const menuOptions: MenuOption[] = [
  { label: "概览", key: "/admin", icon: () => "📊" },
  { label: "用户管理", key: "/admin/users", icon: () => "👤" },
  { label: "图片管理", key: "/admin/images", icon: () => "🖼" },
  { label: "图床客户端", key: "/app", icon: () => "⬆︎" },
]

const activeKey = computed(() => {
  const p = router.currentRoute.value.path
  if (p.startsWith("/admin/users")) return "/admin/users"
  if (p.startsWith("/admin/images")) return "/admin/images"
  return "/admin"
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
  <n-layout style="height: 100vh" has-sider :native-scrollbar="false">
    <n-layout-sider
      class="admin-sider glass"
      :width="232"
      :collapsed-width="68"
      show-trigger="bar"
      collapse-mode="width"
      bordered
    >
      <div class="sider-brand">
        <div class="brand-logo">Tu</div>
        <span class="app-subtitle sider-name">TuBed</span>
      </div>
      <n-menu
        :value="activeKey"
        :options="menuOptions"
        :indent="18"
        class="admin-menu"
        @update:value="handleSelect"
      />
      <div class="sider-user">
        <div class="user-pill press" @click.stop="toggleUser">
          <n-avatar :size="32" round color="#007aff">
            {{ auth.user?.username?.charAt(0)?.toUpperCase() }}
          </n-avatar>
          <div class="user-meta">
            <n-text style="font-weight: 600; font-size: 13px">{{ auth.user?.username }}</n-text>
            <n-text depth="3" style="font-size: 11px">管理员</n-text>
          </div>
        </div>
        <transition name="dropdown">
          <div v-if="userMenuShow" class="user-menu glass" @click.stop>
            <button class="user-menu-item" @click="handleLogout">退出登录</button>
          </div>
        </transition>
      </div>
    </n-layout-sider>

    <n-layout>
      <n-layout-header class="admin-header glass">
        <span class="app-subtitle">管理后台</span>
      </n-layout-header>
      <div class="admin-body">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.admin-sider {
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
  border-right: 1px solid var(--separator);
  z-index: 20;
}
.sider-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 8px 18px;
}
.brand-logo {
  width: 36px;
  height: 36px;
  border-radius: 11px;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
  flex-shrink: 0;
}
.admin-menu {
  flex: 1;
}
.sider-user {
  position: relative;
  padding-top: 12px;
  border-top: 1px solid var(--separator);
}
.user-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: var(--r-md);
  background: var(--fill);
  width: 100%;
}
.user-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
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
.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}
.admin-header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid var(--separator);
}
.admin-body {
  padding: 26px 24px 60px;
}
.sider-name {
  white-space: nowrap;
}

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
