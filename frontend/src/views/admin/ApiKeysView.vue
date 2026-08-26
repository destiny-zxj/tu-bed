<script setup lang="ts">
import { h, onMounted, ref } from "vue"
import { NAlert, NButton, NCard, NDataTable, NForm, NFormItem, NInput, NModal, NSpace, NTag, useDialog, useMessage } from "naive-ui"
import type { DataTableColumns } from "naive-ui"
import api, { type ApiKey, type ApiKeyCreated } from "@/api"
import { copyText, formatDate } from "@/utils/format"

const message = useMessage()
const dialog = useDialog()

const keys = ref<ApiKey[]>([])
const loading = ref(false)

const showCreate = ref(false)
const creating = ref(false)
const newName = ref("")

const createdKey = ref<ApiKeyCreated | null>(null)
const createdKeyVisible = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await api.listApiKeys()
    keys.value = data
  } finally {
    loading.value = false
  }
}

async function create() {
  const name = newName.value.trim()
  if (!name) {
    message.warning("请输入名称")
    return
  }
  creating.value = true
  try {
    const { data } = await api.createApiKey(name)
    createdKey.value = data
    showCreate.value = false
    newName.value = ""
    createdKeyVisible.value = true
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "创建失败")
  } finally {
    creating.value = false
  }
}

async function copyKey() {
  if (!createdKey.value) return
  await copyText(createdKey.value.key)
  message.success("已复制")
}

function remove(row: ApiKey) {
  dialog.warning({
    title: "删除 API Key",
    content: `确认删除「${row.name}」（${row.prefix}…）？使用该 Key 的调用将立即失效。`,
    positiveText: "删除",
    onPositiveClick: async () => {
      await api.deleteApiKey(row.id)
      message.success("已删除")
      await load()
    },
  })
}

const columns = (): DataTableColumns<ApiKey> => [
  { title: "ID", key: "id", width: 70 },
  { title: "名称", key: "name", minWidth: 140 },
  {
    title: "前缀",
    key: "prefix",
    width: 130,
    render: (row) => h("code", { class: "key-prefix" }, { default: () => `${row.prefix}…` }),
  },
  {
    title: "状态",
    key: "is_active",
    width: 90,
    render: (row) =>
      h(NTag, { type: row.is_active ? "success" : "error", round: true }, {
        default: () => (row.is_active ? "启用" : "禁用"),
      }),
  },
  {
    title: "创建时间",
    key: "created_at",
    minWidth: 150,
    render: (row) => formatDate(row.created_at),
  },
  {
    title: "最近使用",
    key: "last_used_at",
    minWidth: 150,
    render: (row) => (row.last_used_at ? formatDate(row.last_used_at) : "—"),
  },
  {
    title: "操作",
    key: "actions",
    width: 90,
    render: (row) =>
      h(NButton, { size: "small", type: "error", class: "press", onClick: () => remove(row) }, {
        default: () => "删除",
      }),
  },
]

onMounted(load)
</script>

<template>
  <div class="apikeys-page">
    <n-alert type="info" :show-icon="false" class="keys-tip" :bordered="false">
      <div class="tip-text">
        API Key 用于无登录态上传图片，可配合 curl 或第三方工具使用：
        <code class="tip-code">curl -X POST "/api/images/upload?api_key=YOUR_KEY" -F "file=@image.png"</code>
      </div>
    </n-alert>

    <n-card class="app-card" title="API Keys 管理" :bordered="false">
      <template #header-extra>
        <n-button type="primary" class="press" @click="showCreate = true">新建 API Key</n-button>
      </template>
      <n-data-table :columns="columns()" :data="keys" :loading="loading" :bordered="false" />
    </n-card>

    <n-modal v-model:show="showCreate" title="新建 API Key" preset="card" style="width: 420px">
      <n-form @submit.prevent="create">
        <n-form-item label="名称">
          <n-input v-model:value="newName" size="large" placeholder="例如：终端脚本 / CI 上传" @keydown.enter="create" />
        </n-form-item>
        <n-button type="primary" block size="large" class="press" :loading="creating" @click="create">
          创建
        </n-button>
      </n-form>
    </n-modal>

    <n-modal v-model:show="createdKeyVisible" title="API Key 已创建" preset="card" style="width: 520px">
      <n-alert type="warning" title="请立即保存" :bordered="false" style="margin-bottom: 16px">
        Key 仅在创建时显示一次，关闭后将无法再次查看，请复制并妥善保管。
      </n-alert>
      <div class="key-box">
        <code>{{ createdKey?.key }}</code>
      </div>
      <div class="key-actions">
        <n-space>
          <n-button type="primary" class="press" @click="copyKey">复制 Key</n-button>
          <n-button class="press" @click="createdKeyVisible = false">我已保存</n-button>
        </n-space>
      </div>
    </n-modal>
  </div>
</template>

<style scoped>
.apikeys-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.keys-tip {
  border-radius: var(--r-lg);
}
.tip-text {
  font-size: 13px;
  line-height: 1.7;
}
.tip-code {
  margin-left: 4px;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--fill);
  font-size: 12px;
}
.key-prefix {
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--fill);
  font-size: 12px;
}
.key-box {
  padding: 14px 16px;
  border-radius: var(--r-md);
  background: var(--fill);
  border: 1px solid var(--separator);
  font-size: 13px;
  word-break: break-all;
  margin-bottom: 18px;
}
.key-box code {
  color: var(--label);
}
.key-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
