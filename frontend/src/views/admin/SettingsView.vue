<script setup lang="ts">
import { onMounted, reactive, ref, computed } from "vue"
import {
  NCard,
  NTabs,
  NTabPane,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NSelect,
  NGrid,
  NGridItem,
  NSpace,
  NDivider,
  NAlert,
  useMessage,
} from "naive-ui"
import api, { type StorageConfig } from "@/api"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
const message = useMessage()

const DRIVER_OPTIONS = [
  { label: "本地磁盘 (local)", value: "local" },
  { label: "S3 兼容 (s3)", value: "s3" },
  { label: "七牛云 (qiniu)", value: "qiniu" },
  { label: "阿里云 OSS (oss)", value: "oss" },
  { label: "腾讯云 COS (cos)", value: "cos" },
]

/* ---------------- 用户信息 ---------------- */
const emailForm = reactive({ email: auth.user?.email ?? "" })
const emailLoading = ref(false)
async function saveEmail() {
  if (!emailForm.email) {
    message.warning("请输入邮箱")
    return
  }
  emailLoading.value = true
  try {
    await api.updateEmail(emailForm.email)
    message.success("邮箱已更新")
    await auth.fetchMe()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "邮箱更新失败")
  } finally {
    emailLoading.value = false
  }
}

const pwdForm = reactive({ current_password: "", new_password: "", confirm: "" })
const pwdLoading = ref(false)
async function savePassword() {
  if (!pwdForm.current_password || !pwdForm.new_password) {
    message.warning("请填写完整密码信息")
    return
  }
  if (pwdForm.new_password.length < 6) {
    message.warning("新密码至少 6 位")
    return
  }
  if (pwdForm.new_password !== pwdForm.confirm) {
    message.warning("两次输入的新密码不一致")
    return
  }
  pwdLoading.value = true
  try {
    await api.updatePassword(pwdForm.current_password, pwdForm.new_password)
    message.success("密码已修改")
    pwdForm.current_password = ""
    pwdForm.new_password = ""
    pwdForm.confirm = ""
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "密码修改失败")
  } finally {
    pwdLoading.value = false
  }
}

/* ---------------- 系统设置：存储 ---------------- */
const storage = reactive<StorageConfig>({
  drive: "local",
  upload_dir: "",
  public_base_url: "",
  qiniu_access_key: "",
  qiniu_secret_key: "",
  qiniu_bucket: "",
  qiniu_domain: "",
  s3_endpoint_url: "",
  s3_region_name: "",
  s3_access_key: "",
  s3_secret_key: "",
  s3_bucket: "",
  s3_public_domain: "",
  oss_endpoint: "",
  oss_bucket_name: "",
  oss_access_key_id: "",
  oss_access_key_secret: "",
  oss_public_url: "",
  cos_region: "",
  cos_bucket: "",
  cos_secret_id: "",
  cos_secret_key: "",
  cos_public_url: "",
})

// 当前正在使用的存储驱动（实际生效的 drive），仅在成功保存后才更新，
// 与下方下拉框的「待保存选择」相互独立。
const currentDrive = ref<string>("local")
const currentDriverName = computed(
  () => DRIVER_OPTIONS.find((o) => o.value === currentDrive.value)?.label ?? currentDrive.value,
)

// 切换下拉选择时不做任何副作用：上方展示的「当前使用驱动」保持不变，
// 只有点击保存且成功后，currentDrive 才会更新为新的 drive。
const storageLoading = ref(false)
const storageSaving = ref(false)

async function loadStorage() {
  storageLoading.value = true
  try {
    const cfg = (await api.getStorageConfig()).data
    Object.assign(storage, cfg)
    // 加载时同步「当前使用驱动」为后端实际生效的 drive
    currentDrive.value = cfg.drive
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "加载存储配置失败")
  } finally {
    storageLoading.value = false
  }
}

async function saveStorage() {
  storageSaving.value = true
  try {
    // 仅提交有值/被修改的字段，避免清空未填写的密钥
    const payload: Partial<StorageConfig> = { drive: storage.drive }
    ;(
      [
        "upload_dir", "public_base_url",
        "qiniu_access_key", "qiniu_secret_key", "qiniu_bucket", "qiniu_domain",
        "s3_endpoint_url", "s3_region_name", "s3_access_key", "s3_secret_key",
        "s3_bucket", "s3_public_domain",
        "oss_endpoint", "oss_bucket_name", "oss_access_key_id", "oss_access_key_secret",
        "oss_public_url", "cos_region", "cos_bucket", "cos_secret_id",
        "cos_secret_key", "cos_public_url",
      ] as (keyof StorageConfig)[]
    ).forEach((k) => {
      const v = storage[k]
      if (v !== null && v !== undefined && v !== "") payload[k] = v as any
    })
    const updated = (await api.updateStorageConfig(payload)).data
    Object.assign(storage, updated)
    // 保存成功后，刷新「当前使用驱动」展示
    currentDrive.value = updated.drive
    message.success("存储配置已保存并实时生效（已写入 .env，重启后仍保留）")
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "保存存储配置失败")
  } finally {
    storageSaving.value = false
  }
}

onMounted(loadStorage)
</script>

<template>
  <div class="settings-page">
    <n-card class="settings-card glass" :bordered="false">
      <n-tabs type="line" animated>
        <!-- 用户信息设置 -->
        <n-tab-pane name="user" tab="用户信息设置">
          <n-alert type="default" :show-icon="false" class="tip">
            当前登录账号：<b>{{ auth.user?.username }}</b>
          </n-alert>

          <n-divider title-placement="left">邮箱修改</n-divider>
          <n-form :model="emailForm" label-placement="top" class="form-col">
            <n-form-item label="邮箱地址">
              <n-input v-model:value="emailForm.email" placeholder="请输入新邮箱" clearable />
            </n-form-item>
            <n-space>
              <n-button type="primary" :loading="emailLoading" @click="saveEmail">保存邮箱</n-button>
            </n-space>
          </n-form>

          <n-divider title-placement="left">密码修改</n-divider>
          <n-form :model="pwdForm" label-placement="top" class="form-col">
            <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
              <n-grid-item span="2 m:1">
                <n-form-item label="当前密码">
                  <n-input
                    v-model:value="pwdForm.current_password"
                    type="password"
                    show-password-on="click"
                    placeholder="请输入当前密码"
                  />
                </n-form-item>
              </n-grid-item>
              <n-grid-item span="2 m:1">
                <n-form-item label="新密码">
                  <n-input
                    v-model:value="pwdForm.new_password"
                    type="password"
                    show-password-on="click"
                    placeholder="至少 6 位"
                  />
                </n-form-item>
              </n-grid-item>
              <n-grid-item span="2">
                <n-form-item label="确认新密码">
                  <n-input
                    v-model:value="pwdForm.confirm"
                    type="password"
                    show-password-on="click"
                    placeholder="再次输入新密码"
                  />
                </n-form-item>
              </n-grid-item>
            </n-grid>
            <n-space>
              <n-button type="primary" :loading="pwdLoading" @click="savePassword">修改密码</n-button>
            </n-space>
          </n-form>
        </n-tab-pane>

        <!-- 系统设置 -->
        <n-tab-pane name="system" tab="系统设置">
          <n-alert type="info" :show-icon="false" class="tip">
            存储配置修改后会立即生效，并持久化写入 <b>.env</b> 文件，服务器重启后依然保留，无需手动重启服务。
          </n-alert>

          <n-divider title-placement="left">文件存储配置</n-divider>
          <n-form :model="storage" label-placement="top" class="form-col" :disabled="storageLoading">
            <n-alert type="default" :show-icon="false" class="tip drive-hint">
              当前使用驱动：<b>{{ currentDriverName }}</b>（仅点击「保存配置」后才会变更）
            </n-alert>
            <n-form-item label="存储驱动">
              <n-select
                v-model:value="storage.drive"
                :options="DRIVER_OPTIONS"
              />
            </n-form-item>

            <!-- 本地 -->
            <template v-if="storage.drive === 'local'">
              <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
                <n-grid-item span="2 m:1">
                  <n-form-item label="本地存储目录 (UPLOAD_DIR)">
                    <n-input v-model:value="storage.upload_dir" placeholder="例如 ./uploads" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="访问基础地址 (PUBLIC_BASE_URL)">
                    <n-input v-model:value="storage.public_base_url" placeholder="例如 /uploads" />
                  </n-form-item>
                </n-grid-item>
              </n-grid>
            </template>

            <!-- 七牛 -->
            <template v-else-if="storage.drive === 'qiniu'">
              <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
                <n-grid-item span="2 m:1">
                  <n-form-item label="AccessKey">
                    <n-input v-model:value="storage.qiniu_access_key" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="SecretKey">
                    <n-input v-model:value="storage.qiniu_secret_key" type="password" show-password-on="click" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="存储空间 (Bucket)">
                    <n-input v-model:value="storage.qiniu_bucket" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="外链域名">
                    <n-input v-model:value="storage.qiniu_domain" placeholder="例如 https://cdn.example.com" />
                  </n-form-item>
                </n-grid-item>
              </n-grid>
            </template>

            <!-- S3 -->
            <template v-else-if="storage.drive === 's3'">
              <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
                <n-grid-item span="2 m:1">
                  <n-form-item label="Endpoint URL">
                    <n-input v-model:value="storage.s3_endpoint_url" placeholder="例如 https://s3.amazonaws.com" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="Region">
                    <n-input v-model:value="storage.s3_region_name" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="AccessKey">
                    <n-input v-model:value="storage.s3_access_key" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="SecretKey">
                    <n-input v-model:value="storage.s3_secret_key" type="password" show-password-on="click" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="Bucket">
                    <n-input v-model:value="storage.s3_bucket" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="外链域名 (可选)">
                    <n-input v-model:value="storage.s3_public_domain" placeholder="留空则用 endpoint+bucket 拼接" />
                  </n-form-item>
                </n-grid-item>
              </n-grid>
            </template>

            <!-- 阿里云 OSS -->
            <template v-else-if="storage.drive === 'oss'">
              <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
                <n-grid-item span="2">
                  <n-form-item label="Endpoint">
                    <n-input v-model:value="storage.oss_endpoint" placeholder="例如 https://oss-cn-hangzhou.aliyuncs.com" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="Bucket">
                    <n-input v-model:value="storage.oss_bucket_name" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="外链域名 (可选)">
                    <n-input v-model:value="storage.oss_public_url" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="AccessKeyId">
                    <n-input v-model:value="storage.oss_access_key_id" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="AccessKeySecret">
                    <n-input v-model:value="storage.oss_access_key_secret" type="password" show-password-on="click" />
                  </n-form-item>
                </n-grid-item>
              </n-grid>
            </template>

            <!-- 腾讯云 COS -->
            <template v-else-if="storage.drive === 'cos'">
              <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
                <n-grid-item span="2 m:1">
                  <n-form-item label="Region">
                    <n-input v-model:value="storage.cos_region" placeholder="例如 ap-guangzhou" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="Bucket">
                    <n-input v-model:value="storage.cos_bucket" placeholder="例如 example-1250000000" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="SecretId">
                    <n-input v-model:value="storage.cos_secret_id" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="SecretKey">
                    <n-input v-model:value="storage.cos_secret_key" type="password" show-password-on="click" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item span="2 m:1">
                  <n-form-item label="外链域名 (可选)">
                    <n-input v-model:value="storage.cos_public_url" />
                  </n-form-item>
                </n-grid-item>
              </n-grid>
            </template>

            <n-space class="save-row">
              <n-button type="primary" :loading="storageSaving" @click="saveStorage">保存配置</n-button>
            </n-space>
          </n-form>
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<style scoped>
.settings-page {
  max-width: 880px;
}
.settings-card {
  padding: 8px 8px 18px;
}
.tip {
  margin: 6px 4px 14px;
}
.drive-hint {
  margin: -6px 4px 16px;
}
.form-col {
  max-width: 720px;
}
.save-row {
  margin-top: 18px;
}
</style>
