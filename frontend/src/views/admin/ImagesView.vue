<script setup lang="ts">
import { computed, h, onMounted, ref } from "vue"
import {
  useMessage,
  NImage,
  NButton,
  NPagination,
  NEmpty,
  NText,
  NPopconfirm,
  NSpin,
  NInput,
  NSelect,
  NDatePicker,
  NForm,
  NFormItem,
  NDataTable,
  NTag,
  NDropdown,
  type DataTableColumns,
  type DataTableRowKey,
  type DropdownOption,
} from "naive-ui"
import api, { type Image, type User } from "@/api"
import { copyText, formatDate, formatSize } from "@/utils/format"
import { resolveUrl } from "@/utils/url"

const message = useMessage()
const items = ref<Image[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const loading = ref(false)

const keyword = ref("")
const ownerId = ref<number | null>(null)
const dateRange = ref<[number, number] | null>(null)

const users = ref<{ label: string; value: number }[]>([])
const userOptions = ref<{ label: string; value: number }[]>([])

// 是否已选择行（用于批量删除）
const checkedRowKeys = ref<DataTableRowKey[]>([])

// 表头下拉：全选 / 取消全选（仅作用于当前页）
const selectHeaderOptions: DropdownOption[] = [
  { label: "全选", key: "all" },
  { label: "取消全选", key: "none" },
]
function onSelectHeader(key: string) {
  if (key === "all") {
    checkedRowKeys.value = items.value.map((i) => i.id)
  } else {
    checkedRowKeys.value = []
  }
}

async function loadUsers() {
  try {
    const { data } = await api.adminListUsers(1, 200)
    users.value = data.items.map((u: User) => ({ label: u.username, value: u.id }))
    userOptions.value = [{ label: "全部用户", value: 0 }, ...users.value]
  } catch {
    userOptions.value = [{ label: "全部用户", value: 0 }]
  }
}

function buildParams() {
  const params: Record<string, unknown> = {}
  if (keyword.value.trim()) params.keyword = keyword.value.trim()
  if (ownerId.value && ownerId.value !== 0) params.owner_id = ownerId.value
  if (dateRange.value) {
    const start = new Date(dateRange.value[0])
    const end = new Date(dateRange.value[1])
    const fmt = (d: Date) => {
      const p = (n: number) => String(n).padStart(2, "0")
      return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
    }
    params.start_date = fmt(start)
    params.end_date = fmt(end)
  }
  return params
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.adminListImages(page.value, pageSize.value, buildParams())
    items.value = data.items
    total.value = data.total
    checkedRowKeys.value = []
  } finally {
    loading.value = false
  }
}

async function remove(id: number) {
  await api.adminDeleteImage(id)
  message.success("已删除")
  // 删除后若当前页已空且不是第一页，回退一页
  if (items.value.length === 1 && page.value > 1) {
    page.value -= 1
  }
  await load()
}

async function removeBatch() {
  const ids = checkedRowKeys.value.map((k) => Number(k))
  if (!ids.length) return
  try {
    const { data } = await api.adminBatchDeleteImages(ids)
    if (data.skipped > 0) {
      message.warning(`已删除 ${data.deleted} 张，跳过 ${data.skipped} 张不存在的图片`)
    } else {
      message.success(`已删除 ${data.deleted} 张图片`)
    }
    if (items.value.length === ids.length && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch {
    message.error("批量删除失败")
  }
}

async function copy(url: string) {
  await copyText(resolveUrl(url))
  message.success("链接已复制")
}

function search() {
  page.value = 1
  load()
}

function reset() {
  keyword.value = ""
  ownerId.value = null
  dateRange.value = null
  page.value = 1
  load()
}

function changePage(p: number) {
  page.value = p
  load()
}

onMounted(() => {
  loadUsers()
  load()
})

// 序号 = 当前页偏移 + 行内索引 + 1
const startIndex = computed(() => (page.value - 1) * pageSize.value)

const columns = computed<DataTableColumns<Image>>(() => [
  {
    type: "selection",
    multiple: true,
    width: 60,
    align: "center",
    fixed: "left",
    renderHeader: () =>
      h(
        NDropdown,
        {
          trigger: "click",
          options: selectHeaderOptions,
          showArrow: false,
          animated: false,
          themeOverrides: { optionColorHover: "transparent" },
          onSelect: (key: string) => onSelectHeader(key),
        },
        {
          default: () =>
            h(NButton, { text: true, type: "primary", size: "small" }, { default: () => "选择" }),
        }
      ),
  },
  {
    title: "序号",
    key: "index",
    width: 70,
    align: "center",
    render: (_row, rowIndex) => startIndex.value + rowIndex + 1,
  },
  {
    title: "缩略图",
    key: "url",
    width: 100,
    align: "center",
    render: (row) => h(NImage, { src: resolveUrl(row.url), width: 60, height: 60, "object-fit": "cover", "preview-src": resolveUrl(row.url) }),
  },
  {
    title: "文件名",
    key: "original_name",
    width: 240,
    maxWidth: 240,
    ellipsis: { tooltip: true },
    render: (row) => row.original_name,
  },
  {
    title: "大小",
    key: "size",
    width: 110,
    render: (row) => formatSize(row.size),
  },
  {
    title: "尺寸",
    key: "dimension",
    width: 110,
    render: (row) =>
      row.width && row.height ? `${row.width}×${row.height}` : "—",
  },
  {
    title: "所属用户",
    key: "owner_username",
    width: 130,
    ellipsis: { tooltip: true },
    render: (row) => row.owner_username || "未知",
  },
  {
    title: "上传时间",
    key: "created_at",
    width: 170,
    render: (row) => formatDate(row.created_at),
  },
  {
    title: "标签",
    key: "tags",
    width: 160,
    render: (row) =>
      row.tags && row.tags.length
        ? row.tags.map((t) => h(NTag, { size: "small", type: "info", bordered: false, style: "margin-right:4px" }, { default: () => t.name }))
        : h(NText, { depth: 3 }, { default: () => "—" }),
  },
  {
    title: "操作",
    key: "actions",
    width: 130,
    align: "center",
    fixed: "right",
    render: (row) =>
      h("div", { style: "display:flex;gap:6px;justify-content:center" }, [
        h(NButton, { size: "tiny", onClick: () => copy(row.url) }, { default: () => "复制" }),
        h(
          NPopconfirm,
          { onPositiveClick: () => remove(row.id) },
          {
            trigger: () =>
              h(NButton, { size: "tiny", type: "error" }, { default: () => "删除" }),
            default: () => "确认删除？",
          }
        ),
      ]),
  },
])
</script>

<template>
  <div class="img-page">
    <div class="app-title" style="margin-bottom: 18px">图片管理</div>

    <div class="img-toolbar">
      <n-form :show-feedback="false" inline>
        <n-form-item label="文件名">
          <n-input
            v-model:value="keyword"
            placeholder="按文件名搜索"
            clearable
            style="width: 200px"
            @keyup.enter="search"
          />
        </n-form-item>
        <n-form-item label="用户">
          <n-select
            v-model:value="ownerId"
            :options="userOptions"
            placeholder="全部用户"
            style="width: 160px"
            @update:value="search"
          />
        </n-form-item>
        <n-form-item label="日期">
          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            clearable
            style="width: 240px"
            @update:value="search"
          />
        </n-form-item>
        <n-form-item>
          <n-button type="primary" @click="search">搜索</n-button>
        </n-form-item>
        <n-form-item>
          <n-button tertiary @click="reset">重置</n-button>
        </n-form-item>
        <n-form-item v-if="checkedRowKeys.length">
          <n-popconfirm @positive-click="removeBatch">
            <template #trigger>
              <n-button type="error">删除选中 ({{ checkedRowKeys.length }})</n-button>
            </template>
            确认删除选中的 {{ checkedRowKeys.length }} 张图片？
          </n-popconfirm>
        </n-form-item>
      </n-form>
      <div v-if="total > 0" class="img-pager">
        <n-pagination
          :page="page"
          :page-size="pageSize"
          :item-count="total"
          show-size-picker
          :page-sizes="[5, 10, 20, 30]"
          @update:page="changePage"
          @update:page-size="(s: number) => { pageSize = s; page = 1; load() }"
        />
      </div>
    </div>

    <div class="img-body">
      <n-spin :show="loading" class="img-spin">
        <n-empty v-if="!items.length && !loading" description="暂无图片" class="img-empty" />
        <n-data-table
          v-else
          :columns="columns"
          :data="items"
          :row-key="(row: Image) => row.id"
          :row-props="() => ({ style: 'cursor:default' })"
          v-model:checked-row-keys="checkedRowKeys"
          :row-class-name="() => 'img-row'"
        />
      </n-spin>
    </div>
  </div>
</template>

<style scoped>
.img-page {
  height: calc(100vh - 26px - 30px);
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.img-toolbar {
  flex: 0 0 auto;
  margin-bottom: 16px;
  padding: 14px 16px;
  background: var(--surface-solid);
  border: 1px solid var(--separator);
  border-radius: var(--r-md);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.img-toolbar :deep(.n-form) {
  flex-wrap: nowrap;
}
.img-toolbar :deep(.n-form-item) {
  margin: 0 12px 0 0;
}
.img-body {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: auto;
}
.img-spin {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.img-spin :deep(.n-spin-body) {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.img-empty {
  margin: auto;
}
.img-pager {
  flex: 0 0 auto;
  display: flex;
  justify-content: flex-end;
  margin-left: auto;
}
.img-row :deep(.n-image) {
  cursor: zoom-in;
}
</style>
