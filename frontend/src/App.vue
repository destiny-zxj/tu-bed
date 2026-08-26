<script setup lang="ts">
import { NConfigProvider, NMessageProvider, NDialogProvider, NGlobalStyle } from "naive-ui"
import type { GlobalThemeOverrides } from "naive-ui"

const fontStack =
  '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif'

const themeOverride: GlobalThemeOverrides = {
  common: {
    primaryColor: "#007aff",
    primaryColorHover: "#3395ff",
    primaryColorPressed: "#0062cc",
    primaryColorSuppl: "#3395ff",
    borderRadius: "12px",
    fontFamily: fontStack,
    cubicBezierEaseInOut: "cubic-bezier(0.4, 0, 0.2, 1)",
    cubicBezierEaseOut: "cubic-bezier(0, 32, 0.5, 1)",
  },
  Card: {
    borderRadius: "18px",
    paddingLarge: "24px",
    color: "rgba(255, 255, 255, 0.72)",
  },
  Modal: {
    borderRadius: "20px",
  },
  Button: {
    borderRadiusMedium: "10px",
    borderRadiusSmall: "8px",
    borderRadiusLarge: "12px",
    fontWeightStrong: "600",
  },
}
</script>

<template>
  <n-config-provider :theme-overrides="themeOverride">
    <n-message-provider>
      <n-dialog-provider>
        <n-global-style />
        <RouterView />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>
