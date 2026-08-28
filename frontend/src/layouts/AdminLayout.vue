<script setup lang="ts">
import { useRouter } from "vue-router"
import { NLayout, NLayoutSider, NLayoutContent, NMenu, NAvatar, NText, NIcon } from "naive-ui"
import type { MenuOption } from "naive-ui"
import { h, computed, ref, onMounted, onBeforeUnmount } from "vue"
import { useAuthStore } from "@/stores/auth"
import { useMessage } from "naive-ui"
import { BarChartOutline, PersonOutline, ImageOutline, KeyOutline, CloudUploadOutline, SettingsOutline } from "@vicons/ionicons5"

const router = useRouter()
const auth = useAuthStore()
const message = useMessage()

const menuOptions: MenuOption[] = [
  { label: "概览", key: "/admin", icon: () => h(NIcon, null, { default: () => h(BarChartOutline) }) },
  { label: "用户管理", key: "/admin/users", icon: () => h(NIcon, null, { default: () => h(PersonOutline) }) },
  { label: "图片管理", key: "/admin/images", icon: () => h(NIcon, null, { default: () => h(ImageOutline) }) },
  { label: "API Keys 管理", key: "/admin/apikeys", icon: () => h(NIcon, null, { default: () => h(KeyOutline) }) },
  { label: "图床客户端", key: "/app", icon: () => h(NIcon, null, { default: () => h(CloudUploadOutline) }) },
  { label: "设置", key: "/admin/settings", icon: () => h(NIcon, null, { default: () => h(SettingsOutline) }) },
]

const activeKey = computed(() => {
  const p = router.currentRoute.value.path
  if (p.startsWith("/admin/users")) return "/admin/users"
  if (p.startsWith("/admin/images")) return "/admin/images"
  if (p.startsWith("/admin/apikeys")) return "/admin/apikeys"
  if (p.startsWith("/admin/settings")) return "/admin/settings"
  return "/admin"
})

function handleSelect(key: string) {
  if (key === "/app") {
    window.open("/app", "_blank")
    return
  }
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
      :native-scrollbar="false"
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
      <n-layout-content class="admin-content">
        <div class="admin-body">
          <router-view v-slot="{ Component }">
            <transition name="page" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.admin-sider {
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-height: 100vh;
  padding: 16px 12px;
  border-right: 1px solid var(--separator);
  z-index: 100;
  position: relative;
}
/* 让 sider 不裁剪底部弹出的用户菜单 */
.admin-sider :deep(.n-layout-sider-scroll-container),
.admin-sider :deep(.n-layout-sider),
.admin-sider :deep(.n-scrollbar),
.admin-sider :deep(.n-scrollbar-container) {
  overflow: visible !important;
}
/* 让菜单区内部内容容器成为 flex 列，使底部用户块可用 margin-top:auto 贴底 */
.admin-sider :deep(.n-scrollbar-content) {
  display: flex !important;
  flex-direction: column !important;
  min-height: 100% !important;
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
  padding-top: 4px;
}
.sider-user {
  position: relative;
  margin-top: auto;
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
  bottom: calc(100% + 8px);
  left: 0;
  right: 0;
  padding: 6px;
  border-radius: var(--r-md);
  z-index: 50;
  background: var(--surface);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--separator);
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
  transform: translateY(10px);
}
.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

/* ---------- 收起态：隐藏文字、仅留图标、内容居中 ---------- */
.admin-sider.n-layout-sider--collapsed .sider-brand {
  justify-content: center;
  padding: 8px 0 18px;
}
.admin-sider.n-layout-sider--collapsed :deep(.sider-name),
.admin-sider.n-layout-sider--collapsed :deep(.user-meta) {
  display: none !important;
}
.admin-sider.n-layout-sider--collapsed .user-pill {
  justify-content: center;
  padding: 6px 0;
  width: auto;
}
/* 收起态下用户下拉浮出窄栏外，避免文字被裁 */
.admin-sider.n-layout-sider--collapsed .user-menu {
  width: 140px;
  left: 0;
  right: auto;
  transform: none;
}
.admin-content {
  background: transparent;
}
.admin-body {
  padding: 26px 24px 30px;
  min-height: 100vh;
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
