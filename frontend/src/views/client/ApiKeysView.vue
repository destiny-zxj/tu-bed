<script setup lang="ts">
import { h, onMounted, ref } from "vue"
import { useMessage, NCard, NDataTable, NButton, NModal, NForm, NFormItem, NInput, useDialog, NSpace, NText, NTag } from "naive-ui"
import type { DataTableColumns } from "naive-ui"
import api, { type ApiKey } from "@/api"
import { copyText, formatDate } from "@/utils/format"

const message = useMessage()
const dialog = useDialog()
const keys = ref<ApiKey[]>([])
const showCreate = ref(false)
const newName = ref("")
const createdKey = ref("")
const creating = ref(false)

async function load() {
  const { data } = await api.listApiKeys()
  keys.value = data
}

async function create() {
  if (!newName.value.trim()) {
    message.warning("请输入名称")
    return
  }
  creating.value = true
  try {
    const { data } = await api.createApiKey(newName.value.trim())
    createdKey.value = data.key
    newName.value = ""
    await load()
  } finally {
    creating.value = false
  }
}

async function remove(id: number) {
  dialog.warning({
    title: "删除密钥",
    content: "删除后使用该密钥的上传将失效，确认删除？",
    positiveText: "删除",
    onPositiveClick: async () => {
      await api.deleteApiKey(id)
      message.success("已删除")
      await load()
    },
  })
}

async function copy(key: string) {
  await copyText(key)
  message.success("已复制")
}

const columns = (): DataTableColumns<ApiKey> => [
  { title: "名称", key: "name", minWidth: 120 },
  {
    title: "前缀",
    key: "prefix",
    render: (row) => h(NTag, { type: "default", round: true }, { default: () => `${row.prefix}…` }),
  },
  {
    title: "状态",
    key: "is_active",
    render: (row) =>
      h(NTag, { type: row.is_active ? "success" : "error", round: true }, {
        default: () => (row.is_active ? "启用" : "禁用"),
      }),
  },
  { title: "创建时间", key: "created_at", render: (row) => formatDate(row.created_at) },
  {
    title: "操作",
    key: "actions",
    render: (row) =>
      h("n-button", { size: "small", type: "error", class: "press", onClick: () => remove(row.id) }, {
        default: () => "删除",
      }),
  },
]

onMounted(load)
</script>

<template>
  <n-card class="app-card" title="API 密钥" :bordered="false">
    <template #header-extra>
      <n-button type="primary" class="press" @click="showCreate = true">新建密钥</n-button>
    </template>
    <n-data-table :columns="columns()" :data="keys" :bordered="false" />
    <n-empty v-if="!keys.length" description="暂无密钥" style="margin-top: 16px" />
  </n-card>

  <n-modal v-model:show="showCreate" title="新建 API 密钥" preset="card" style="width: 420px">
    <n-form @submit.prevent="create">
      <n-form-item label="名称">
        <n-input v-model:value="newName" placeholder="例如：我的博客" size="large" />
      </n-form-item>
      <n-button type="primary" block size="large" class="press" :loading="creating" @click="create">
        生成
      </n-button>
    </n-form>
  </n-modal>

  <n-modal
    :show="!!createdKey"
    title="密钥已生成"
    preset="card"
    style="width: 460px"
    @update:show="(v: boolean) => { if (!v) createdKey = '' }"
  >
    <n-space vertical :size="12">
      <n-text>请妥善保存，密钥仅显示这一次：</n-text>
      <n-input
        :value="createdKey"
        readonly
        type="textarea"
        :autosize="{ minRows: 2 }"
        style="font-family: ui-monospace, monospace; letter-spacing: 0"
      />
      <n-button type="primary" block class="press" @click="copy(createdKey)">复制密钥</n-button>
    </n-space>
  </n-modal>
</template>
