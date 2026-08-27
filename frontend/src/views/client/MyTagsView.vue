<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import {
  useMessage,
  NCard,
  NButton,
  NInput,
  NEmpty,
  NText,
  NIcon,
  NPopconfirm,
  NSpin,
} from "naive-ui"
import { PricetagsOutline } from "@vicons/ionicons5"
import api, { type Tag } from "@/api"

const router = useRouter()
const message = useMessage()

const tags = ref<Tag[]>([])
const loading = ref(false)
const newTagName = ref("")
const creating = ref(false)
const editingId = ref<number | null>(null)
const editName = ref("")

async function load() {
  loading.value = true
  try {
    const { data } = await api.listTags()
    tags.value = data
  } finally {
    loading.value = false
  }
}

async function createTag() {
  const name = newTagName.value.trim()
  if (!name) return
  creating.value = true
  try {
    const { data } = await api.createTag(name)
    tags.value.unshift(data)
    newTagName.value = ""
    message.success("标签已创建")
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "创建失败")
  } finally {
    creating.value = false
  }
}

function startEdit(tag: Tag) {
  editingId.value = tag.id
  editName.value = tag.name
}

async function confirmRename(tag: Tag) {
  const name = editName.value.trim()
  if (!name) {
    message.warning("名称不能为空")
    return
  }
  if (name === tag.name) {
    editingId.value = null
    return
  }
  try {
    const { data } = await api.renameTag(tag.id, name)
    Object.assign(tag, data)
    message.success("已重命名")
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "重命名失败")
  } finally {
    editingId.value = null
  }
}

async function removeTag(tag: Tag) {
  try {
    await api.deleteTag(tag.id)
    tags.value = tags.value.filter((t) => t.id !== tag.id)
    message.success("已删除")
  } catch {
    message.error("删除失败")
  }
}

function openTag(tag: Tag) {
  router.push({ path: "/app/images", query: { tag: tag.id } })
}

onMounted(load)
</script>

<template>
  <n-card class="app-card" :bordered="false">
    <template #header>
      <div class="card-header">
        <span>我的标签</span>
        <span class="card-sub">共 {{ tags.length }} 个标签</span>
      </div>
    </template>
    <div class="tag-create-bar">
      <n-input
        v-model:value="newTagName"
        placeholder="输入标签名，回车创建"
        :disabled="creating"
        @keyup.enter="createTag"
      />
      <n-button type="primary" :loading="creating" @click="createTag">创建标签</n-button>
    </div>
    <n-spin :show="loading">
      <n-empty v-if="!loading && !tags.length" description="还没有标签，创建第一个吧" />
      <div v-else class="tag-list">
        <div v-for="tag in tags" :key="tag.id" class="tag-row">
          <template v-if="editingId === tag.id">
            <n-input
              v-model:value="editName"
              size="small"
              class="tag-edit-input"
              @keyup.enter="confirmRename(tag)"
            />
            <n-button size="small" type="primary" @click="confirmRename(tag)">保存</n-button>
            <n-button size="small" quaternary @click="editingId = null">取消</n-button>
          </template>
          <template v-else>
            <div class="tag-name press" @click="openTag(tag)">
              <n-icon :size="16"><PricetagsOutline /></n-icon>
              <span>{{ tag.name }}</span>
            </div>
            <n-text depth="3" class="tag-count">{{ tag.image_count }} 张图片</n-text>
            <div class="tag-actions">
              <n-button size="tiny" quaternary @click="startEdit(tag)">重命名</n-button>
              <n-popconfirm @positive-click="removeTag(tag)">
                <template #trigger>
                  <n-button size="tiny" type="error" quaternary>删除</n-button>
                </template>
                删除后，图片上的该标签也会被移除，确认删除？
              </n-popconfirm>
            </div>
          </template>
        </div>
      </div>
    </n-spin>
  </n-card>
</template>

<style scoped>
.card-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.card-sub {
  font-size: 13px;
  color: var(--text-3);
}
.tag-create-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}
.tag-list {
  display: flex;
  flex-direction: column;
}
.tag-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 4px;
  border-bottom: 1px solid var(--separator);
}
.tag-row:last-child {
  border-bottom: none;
}
.tag-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-1);
  cursor: pointer;
}
.tag-name:hover {
  color: var(--accent);
}
.tag-count {
  font-size: 13px;
}
.tag-actions {
  margin-left: auto;
  display: flex;
  gap: 4px;
}
.tag-edit-input {
  width: 200px;
}
</style>
