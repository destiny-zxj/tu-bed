import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/app" },
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { public: true },
    },
    {
      path: "/app",
      component: () => import("@/layouts/ClientLayout.vue"),
      meta: { requiresAuth: true },
      children: [
        { path: "", name: "client-home", component: () => import("@/views/client/UploadView.vue") },
        { path: "images", name: "client-images", component: () => import("@/views/client/MyImagesView.vue") },
        { path: "tags", name: "client-tags", component: () => import("@/views/client/MyTagsView.vue") },
      ],
    },
    {
      path: "/admin",
      component: () => import("@/layouts/AdminLayout.vue"),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: "", name: "admin-dashboard", component: () => import("@/views/admin/DashboardView.vue") },
        { path: "users", name: "admin-users", component: () => import("@/views/admin/UsersView.vue") },
        { path: "images", name: "admin-images", component: () => import("@/views/admin/ImagesView.vue") },
        { path: "apikeys", name: "admin-apikeys", component: () => import("@/views/admin/ApiKeysView.vue") },
        { path: "settings", name: "admin-settings", component: () => import("@/views/admin/SettingsView.vue") },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: "/app" },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    return { name: "login", query: { redirect: to.fullPath } }
  }
  if (auth.token && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return { name: "login" }
    }
  }
  if (to.meta.requiresAdmin && !auth.user?.is_admin) {
    return { name: "client-home" }
  }
  if (to.name === "login" && auth.token) {
    return { name: auth.user?.is_admin ? "admin-dashboard" : "client-home" }
  }
})

export default router
