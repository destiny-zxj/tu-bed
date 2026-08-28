import { API_BASE } from "@/config"

// 将后端返回的相对地址(如 /uploads/xxx.png)拼接为完整的服务端地址。
// 若已经是完整 http(s) 地址则原样返回。
export function resolveUrl(url?: string | null): string {
  if (!url) return ""
  if (/^https?:\/\//i.test(url)) return url
  return `${API_BASE.replace(/\/$/, "")}${url.startsWith("/") ? "" : "/"}${url}`
}
