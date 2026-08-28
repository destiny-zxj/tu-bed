// 服务端地址配置
// 通过 Vite 环境变量 VITE_API_BASE 区分环境, 见 .env.development / .env.production
// 本地开发: http://127.0.0.1:8000
// 生产环境: https://tubed.tech-cub.cn
export const API_BASE: string =
  import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000"
