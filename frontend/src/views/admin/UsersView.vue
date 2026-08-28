<script setup lang="ts">
import { h, onMounted, ref } from "vue"
import { useMessage, NCard, NSpace, NDataTable, NButton, NModal, NForm, NFormItem, NInput, NRadioGroup, NRadioButton, useDialog, NTag, NPagination, NSelect, NText } from "naive-ui"
import type { DataTableColumns, SelectOption } from "naive-ui"
import api, { type User } from "@/api"
import { formatDate } from "@/utils/format"
import { useAuthStore } from "@/stores/auth"

const message = useMessage()
const dialog = useDialog()
const auth = useAuthStore()
const users = ref<User[]>([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const showCreate = ref(false)
const form = ref({ username: "", email: "", password: "", is_admin: false })
const creating = ref(false)

const pageSizeOptions: SelectOption[] = [
  { label: "10 条/页", value: 10 },
  { label: "20 条/页", value: 20 },
  { label: "30 条/页", value: 30 },
]

const roleOptions: SelectOption[] = [
  { label: "普通用户", value: "false" },
  { label: "管理员", value: "true" },
]

async function load() {
  loading.value = true
  try {
    const { data } = await api.adminListUsers(page.value, pageSize.value)
    users.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function changePage(p: number) {
  page.value = p
  load()
}

function changePageSize(size: number) {
  pageSize.value = size
  page.value = 1
  load()
}

async function create() {
  if (!form.value.username || !form.value.password) {
    message.warning("请输入用户名和密码")
    return
  }
  creating.value = true
  try {
    await api.adminCreateUser({ ...form.value })
    message.success("已创建")
    showCreate.value = false
    form.value = { username: "", email: "", password: "", is_admin: false }
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "创建失败")
  } finally {
    creating.value = false
  }
}

function remove(row: User) {
  dialog.warning({
    title: "删除用户",
    content: `确认删除用户「${row.username}」？其图片也会一并删除。`,
    positiveText: "删除",
    onPositiveClick: async () => {
      await api.adminDeleteUser(row.id)
      message.success("已删除")
      // 删除后若当前页为空则回退一页
      if (users.value.length === 1 && page.value > 1) {
        page.value -= 1
      }
      await load()
    },
  })
}

async function toggleActive(row: User) {
  await api.adminUpdateUser(row.id, { is_active: !row.is_active })
  await load()
}

async function updateRole(row: User, value: boolean) {
  // 禁止管理员取消自己的管理员权限, 避免系统无管理员
  if (row.id === auth.user?.id && !value) {
    message.warning("不能取消自己的管理员权限")
    return
  }
  try {
    await api.adminUpdateUser(row.id, { is_admin: value })
    message.success(value ? "已设为管理员" : "已改为普通用户")
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "修改失败")
  }
}

const columns = (): DataTableColumns<User> => [
  { title: "ID", key: "id", width: 70 },
  { title: "用户名", key: "username", minWidth: 120 },
  { title: "邮箱", key: "email", minWidth: 140 },
  {
    title: "角色",
    key: "is_admin",
    render: (row) =>
      h(NSelect, {
        value: String(row.is_admin),
        options: roleOptions,
        size: "small",
        style: "width: 110px",
        "aria-label": "修改角色",
        onUpdateValue: (value: string) => updateRole(row, value === "true"),
      }),
  },
  {
    title: "状态",
    key: "is_active",
    render: (row) =>
      h(NTag, { type: row.is_active ? "success" : "error", round: true }, {
        default: () => (row.is_active ? "正常" : "禁用"),
      }),
  },
  { title: "创建时间", key: "created_at", minWidth: 150, render: (row) => formatDate(row.created_at) },
  {
    title: "操作",
    key: "actions",
    render: (row) =>
      h(NSpace, { size: 4 }, {
        default: () => [
          h(NButton, { size: "small", type: "warning", class: "press", onClick: () => toggleActive(row) }, {
            default: () => (row.is_active ? "禁用" : "启用"),
          }),
          h(NButton, { size: "small", type: "error", class: "press", onClick: () => remove(row) }, {
            default: () => "删除",
          }),
        ],
      }),
  },
]

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head" style="display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 18px">
      <div class="app-title">用户管理</div>
      <n-button type="primary" class="press" @click="showCreate = true">新建用户</n-button>
    </div>
    <n-card class="app-card" :bordered="false">
      <n-data-table :columns="columns()" :data="users" :loading="loading" :bordered="false" />
      <div class="table-footer">
        <n-text depth="3" class="total-text">共 {{ total }} 条</n-text>
        <div class="pager">
          <n-select
            :value="pageSize"
            :options="pageSizeOptions"
            size="small"
            style="width: 110px"
            @update:value="changePageSize"
          />
          <n-pagination
            v-model:page="page"
            :page-size="pageSize"
            :item-count="total"
            show-quick-jumper
            @update:page="changePage"
          />
        </div>
      </div>
    </n-card>
    <n-modal v-model:show="showCreate" title="新建用户" preset="card" style="width: 420px">
    <n-form @submit.prevent="create">
      <n-form-item label="用户名">
        <n-input v-model:value="form.username" size="large" />
      </n-form-item>
      <n-form-item label="邮箱">
        <n-input v-model:value="form.email" size="large" />
      </n-form-item>
      <n-form-item label="密码">
        <n-input v-model:value="form.password" type="password" size="large" />
      </n-form-item>
      <n-form-item label="角色">
        <n-radio-group v-model:value="form.is_admin">
          <n-space>
            <n-radio-button :value="false">普通用户</n-radio-button>
            <n-radio-button :value="true">管理员</n-radio-button>
          </n-space>
        </n-radio-group>
      </n-form-item>
      <n-button type="primary" block size="large" class="press" :loading="creating" @click="create">
        创建
      </n-button>
    </n-form>
    </n-modal>
  </div>
</template>

<style scoped>
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 18px;
  flex-wrap: wrap;
}
.total-text {
  font-size: 13px;
}
.pager {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
