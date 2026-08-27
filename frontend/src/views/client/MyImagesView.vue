<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import {
  useMessage,
  NCard,
  NImage,
  NButton,
  NPagination,
  NEmpty,
  NText,
  NPopconfirm,
  NPopover,
  NInput,
  NIcon,
  NSpin,
} from "naive-ui"
import { PricetagsOutline, CloseOutline } from "@vicons/ionicons5"
import api, { type Image, type Tag } from "@/api"
import { copyText, formatDate, formatSize } from "@/utils/format"

const message = useMessage()
const route = useRoute()
const router = useRouter()

const items = ref<Image[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(24)
const loading = ref(false)

const allTags = ref<Tag[]>([])
const newTagName = ref("")

const activeTagId = computed(() => {
  const v = Number(route.query.tag)
  return Number.isFinite(v) && v > 0 ? v : undefined
})
const activeTag = computed(() => allTags.value.find((t) => t.id === activeTagId.value) || null)

async function load() {
  loading.value = true
  try {
    const { data } = await api.listImages(page.value, pageSize.value, activeTagId.value)
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function loadTags() {
  try {
    const { data } = await api.listTags()
    allTags.value = data
  } catch {
    // 标签加载失败不影响图片列表展示
  }
}

function clearFilter() {
  router.replace({ path: "/app/images" })
}

async function remove(id: number) {
  try {
    await api.deleteImage(id)
    message.success("已删除")
    await load()
  } catch {
    message.error("删除失败")
  }
}

async function copy(url: string) {
  await copyText(url)
  message.success("链接已复制")
}

function onTagPanelShow(show: boolean) {
  if (show) newTagName.value = ""
}

async function toggleTag(img: Image, tagId: number) {
  const ids = img.tags.map((t) => t.id)
  const idx = ids.indexOf(tagId)
  if (idx >= 0) ids.splice(idx, 1)
  else ids.push(tagId)
  try {
    const { data } = await api.setImageTags(img.id, ids)
    img.tags = data
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "更新标签失败")
  }
}

async function createAndApply(img: Image) {
  const name = newTagName.value.trim()
  if (!name) return
  try {
    let tag = allTags.value.find((t) => t.name === name)
    if (!tag) {
      const { data } = await api.createTag(name)
      tag = data
      allTags.value.unshift(data)
    }
    const ids = img.tags.map((t) => t.id)
    if (!ids.includes(tag.id)) ids.push(tag.id)
    const { data } = await api.setImageTags(img.id, ids)
    img.tags = data
    newTagName.value = ""
    message.success("已添加标签")
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "添加标签失败")
  }
}

watch(
  () => route.query.tag,
  () => {
    page.value = 1
    load()
  },
)

onMounted(() => {
  load()
  loadTags()
})
</script>

<template>
  <n-card class="app-card" :bordered="false">
    <template #header>
      <div class="card-header">
        <span>我的图片</span>
        <div v-if="activeTag" class="filter-bar">
          <span class="filter-label">筛选：</span>
          <span class="tag-chip tag-chip--on">
            <n-icon :size="12"><PricetagsOutline /></n-icon>
            {{ activeTag.name }}
          </span>
          <n-button size="tiny" quaternary @click="clearFilter">
            <template #icon><n-icon><CloseOutline /></n-icon></template>
            清除
          </n-button>
        </div>
      </div>
    </template>
    <n-spin :show="loading">
      <n-empty v-if="!loading && !items.length" description="还没有图片，去上传吧" />
      <div v-else class="img-masonry">
        <div v-for="img in items" :key="img.id" class="img-tile">
          <div class="img-thumb">
            <n-image :src="img.url" object-fit="cover" />
          </div>
          <div class="img-meta">
            <n-text :ellipsis="true" style="max-width: 100%; font-weight: 600; font-size: 13px">
              {{ img.original_name }}
            </n-text>
            <n-text depth="3" style="font-size: 12px">
              {{ formatSize(img.size) }} · {{ formatDate(img.created_at) }}
            </n-text>
            <div v-if="img.tags.length" class="img-tags">
              <span v-for="t in img.tags" :key="t.id" class="tag-chip tag-chip--sm">{{ t.name }}</span>
            </div>
            <div class="img-actions">
              <n-button size="tiny" @click="copy(img.url)">复制</n-button>
              <n-popover trigger="click" placement="bottom" :width="280" @update:show="onTagPanelShow">
                <template #trigger>
                  <n-button size="tiny" secondary>标签</n-button>
                </template>
                <div class="tag-panel">
                  <div class="tag-panel-title">管理标签</div>
                  <div v-if="allTags.length" class="tag-chips">
                    <span
                      v-for="t in allTags"
                      :key="t.id"
                      class="tag-chip"
                      :class="{ 'tag-chip--on': img.tags.some((x) => x.id === t.id) }"
                      @click="toggleTag(img, t.id)"
                    >
                      {{ t.name }}
                    </span>
                  </div>
                  <div v-else class="tag-panel-empty">还没有标签，先创建一个吧</div>
                  <div class="tag-create">
                    <n-input
                      v-model:value="newTagName"
                      size="small"
                      placeholder="新建标签，回车确认"
                      @keyup.enter="createAndApply(img)"
                    />
                    <n-button size="small" type="primary" @click="createAndApply(img)">添加</n-button>
                  </div>
                </div>
              </n-popover>
              <n-popconfirm @positive-click="remove(img.id)">
                <template #trigger>
                  <n-button size="tiny" type="error">删除</n-button>
                </template>
                确认删除该图片？
              </n-popconfirm>
            </div>
          </div>
        </div>
      </div>
    </n-spin>
    <div v-if="total > pageSize" style="display: flex; justify-content: center; margin-top: 22px">
      <n-pagination
        v-model:page="page"
        :page-size="pageSize"
        :item-count="total"
        @update:page="load"
      />
    </div>
  </n-card>
</template>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
}
.filter-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-2);
}
.filter-label {
  color: var(--text-3);
}
.img-masonry {
  column-count: 5;
  column-gap: 16px;
}
@media (max-width: 1500px) {
  .img-masonry { column-count: 4; }
}
@media (max-width: 1100px) {
  .img-masonry { column-count: 3; }
}
@media (max-width: 760px) {
  .img-masonry { column-count: 2; }
}
.img-tile {
  background: var(--surface-solid);
  border-radius: var(--r-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--separator);
  break-inside: avoid;
  margin-bottom: 16px;
}
.img-thumb {
  background: var(--fill);
}
.img-thumb :deep(.n-image) {
  width: 100%;
  display: block;
}
.img-thumb :deep(img) {
  width: 100%;
  height: auto;
  display: block;
}
.img-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px 12px;
}
.img-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.img-actions {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}
.tag-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.tag-panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-1);
}
.tag-panel-empty {
  font-size: 12px;
  color: var(--text-3);
}
.tag-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tag-create {
  display: flex;
  gap: 6px;
}
.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 20px;
  background: var(--fill);
  color: var(--text-2);
  border: 1px solid var(--separator);
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
}
.tag-chip:hover {
  border-color: var(--accent);
  color: var(--accent);
}
.tag-chip--on {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
.tag-chip--on:hover {
  color: #fff;
  opacity: 0.9;
}
.tag-chip--sm {
  padding: 1px 8px;
  font-size: 11px;
  line-height: 18px;
  cursor: default;
}
</style>

