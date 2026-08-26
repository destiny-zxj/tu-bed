<script setup lang="ts">
import { onMounted, ref } from "vue"
import { NCard, NStatistic, NNumberAnimation } from "naive-ui"
import api, { type Stats } from "@/api"
import { formatSize } from "@/utils/format"

const stats = ref<Stats>({ total_users: 0, total_images: 0, total_storage_bytes: 0 })

onMounted(async () => {
  stats.value = (await api.adminStats()).data
})

const tiles = [
  { icon: "👤", label: "用户总数", tint: "rgba(0,122,255,.12)", color: "#007aff" },
  { icon: "🖼", label: "图片总数", tint: "rgba(52,199,89,.12)", color: "#34c759" },
  { icon: "💾", label: "存储用量", tint: "rgba(255,159,10,.12)", color: "#ff9f0a" },
]
</script>

<template>
  <div>
    <div class="app-title" style="margin-bottom: 18px">概览</div>
    <div class="stat-grid stagger">
      <n-card v-for="(t, i) in tiles" :key="t.label" class="app-card stat-tile" :bordered="false">
        <div class="stat-icon" :style="{ background: t.tint, color: t.color }">{{ t.icon }}</div>
        <div class="stat-label app-caption">{{ t.label }}</div>
        <div class="stat-value">
          <n-number-animation
            v-if="i < 2"
            :from="0"
            :to="(stats as any)[i === 0 ? 'total_users' : 'total_images']"
            style="font-weight: 700"
          />
          <template v-else>{{ formatSize(stats.total_storage_bytes) }}</template>
        </div>
      </n-card>
    </div>
  </div>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
}
.stat-tile {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.stat-icon {
  width: 46px;
  height: 46px;
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}
.stat-label {
  margin-top: 2px;
}
.stat-value {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--label);
  line-height: 1.1;
}
</style>
