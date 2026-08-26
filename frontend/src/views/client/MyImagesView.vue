<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useMessage, NCard, NImage, NButton, NPagination, NEmpty, NText, NPopconfirm } from "naive-ui"
import api, { type Image } from "@/api"
import { copyText, formatDate, formatSize } from "@/utils/format"

const message = useMessage()
const items = ref<Image[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(24)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await api.listImages(page.value, pageSize.value)
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
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
  await copyText(location.origin + url)
  message.success("链接已复制")
}

onMounted(load)
</script>

<template>
  <n-card class="app-card" title="我的图片" :bordered="false">
    <n-empty v-if="!loading && !items.length" description="还没有图片，去上传吧" />
    <div v-else class="img-grid">
      <div v-for="img in items" :key="img.id" class="img-tile press">
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
          <div class="img-actions">
            <n-button size="tiny" @click="copy(img.url)">复制</n-button>
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
.img-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 16px;
}
.img-tile {
  background: var(--surface-solid);
  border-radius: var(--r-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--separator);
}
.img-thumb {
  height: 138px;
  background: var(--fill);
}
.img-thumb :deep(img) {
  width: 100%;
  height: 138px;
  object-fit: cover;
  display: block;
}
.img-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px 12px;
}
.img-actions {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}
</style>
