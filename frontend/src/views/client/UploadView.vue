<script setup lang="ts">
import { ref } from "vue"
import { useMessage, NCard, NUpload, NUploadDragger, NText, NP, NImage, NButton, NEmpty, NIcon } from "naive-ui"
import type { UploadCustomRequestOptions } from "naive-ui"
import { CloudUploadOutline } from "@vicons/ionicons5"
import api, { type Image } from "@/api"
import { copyText, formatSize } from "@/utils/format"

const message = useMessage()
const recent = ref<Image[]>([])
const uploading = ref(false)
const dragOver = ref(false)

const customRequest = async (options: UploadCustomRequestOptions) => {
  const file = options.file.file as File
  if (!file) {
    options.onError()
    return
  }
  uploading.value = true
  try {
    const { data } = await api.uploadImage(file)
    recent.value.unshift(data)
    message.success("上传成功")
    options.onFinish()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "上传失败")
    options.onError()
  } finally {
    uploading.value = false
  }
}

async function copyUrl(url: string) {
  await copyText(url)
  message.success("链接已复制")
}
</script>

<template>
  <div class="stagger">
    <n-card class="app-card" title="上传图片" :bordered="false">
      <n-upload
        multiple
        :custom-request="customRequest"
        :show-file-list="false"
        accept="image/*"
        @dragover="dragOver = true"
        @dragleave="dragOver = false"
      >
        <n-upload-dragger class="dropzone press" :class="{ 'dropzone--over': dragOver }">
          <div class="dropzone-inner">
            <div class="dropzone-icon">
              <n-icon :size="26"><CloudUploadOutline /></n-icon>
            </div>
            <n-text class="app-subtitle">点击或拖拽图片到此处</n-text>
            <n-p depth="3" class="app-caption" style="margin-top: 6px; display: block">
              支持 JPG / PNG / GIF / WEBP，可多选
            </n-p>
          </div>
        </n-upload-dragger>
      </n-upload>
    </n-card>

    <n-card class="app-card" title="最近上传" :bordered="false">
      <n-empty v-if="!recent.length" description="还没有上传记录" />
      <div v-else class="img-grid">
        <div v-for="img in recent" :key="img.id" class="img-tile press">
          <div class="img-thumb">
            <n-image :src="img.url" object-fit="cover" />
          </div>
          <div class="img-meta">
            <n-text :ellipsis="true" style="max-width: 100%; font-weight: 600; font-size: 13px">
              {{ img.original_name }}
            </n-text>
            <n-text depth="3" style="font-size: 12px">{{ formatSize(img.size) }}</n-text>
            <n-button size="small" block class="copy-btn" @click="copyUrl(img.url)">复制链接</n-button>
          </div>
        </div>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
.stagger {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.dropzone {
  border: 1.5px dashed var(--separator);
  border-radius: var(--r-lg);
  background: var(--fill);
  transition: border-color 0.25s var(--ease), background 0.25s var(--ease),
    transform 0.18s var(--ease);
}
.dropzone--over {
  border-color: var(--accent);
  background: var(--accent-soft);
}
.dropzone-inner {
  padding: 40px 24px;
  text-align: center;
}
.dropzone-icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 14px;
  border-radius: 16px;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}
.img-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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
  height: 130px;
  background: var(--fill);
}
.img-thumb :deep(.n-image) {
  width: 100%;
  height: 100%;
  display: block;
}
.img-thumb :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.img-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px 12px;
}
.copy-btn {
  margin-top: 4px;
}
</style>
