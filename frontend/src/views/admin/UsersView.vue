<script setup lang="ts">
import { h, onMounted, ref } from "vue"
import { useMessage, NCard, NSpace, NDataTable, NButton, NModal, NForm, NFormItem, NInput, NRadioGroup, NRadioButton, useDialog, NTag } from "naive-ui"
import type { DataTableColumns } from "naive-ui"
import api, { type User } from "@/api"
import { formatDate } from "@/utils/format"

const message = useMessage()
const dialog = useDialog()
const users = ref<User[]>([])
const showCreate = ref(false)
const form = ref({ username: "", email: "", password: "", is_admin: false })
const creating = ref(false)

async function load() {
  const { data } = await api.adminListUsers()
  users.value = data
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
      await load()
    },
  })
}

async function toggleActive(row: User) {
  await api.adminUpdateUser(row.id, { is_active: !row.is_active })
  await load()
}

const columns = (): DataTableColumns<User> => [
  { title: "ID", key: "id", width: 70 },
  { title: "用户名", key: "username", minWidth: 120 },
  { title: "邮箱", key: "email", minWidth: 140 },
  {
    title: "角色",
    key: "is_admin",
    render: (row) =>
      h(NTag, { type: row.is_admin ? "warning" : "default", round: true }, {
        default: () => (row.is_admin ? "管理员" : "普通用户"),
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
  <n-card class="app-card" title="用户管理" :bordered="false">
    <template #header-extra>
      <n-button type="primary" class="press" @click="showCreate = true">新建用户</n-button>
    </template>
    <n-data-table :columns="columns()" :data="users" :bordered="false" />
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
  </n-card>
</template>
