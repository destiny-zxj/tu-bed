import request from "./request"

export interface User {
  id: number
  username: string
  email?: string
  is_admin: boolean
  is_active: boolean
  created_at: string
}

export interface Image {
  id: number
  owner_id: number
  url: string
  original_name: string
  mime_type: string
  size: number
  width?: number
  height?: number
  created_at: string
}

export interface ImageList {
  total: number
  items: Image[]
}

export interface ApiKey {
  id: number
  name: string
  prefix: string
  is_active: boolean
  created_at: string
  last_used_at?: string
}

export interface Stats {
  total_users: number
  total_images: number
  total_storage_bytes: number
}

const api = {
  login: (username: string, password: string) =>
    request.post<{ access_token: string }>("/auth/login", { username, password }),
  me: () => request.get<User>("/auth/me"),

  listImages: (page = 1, pageSize = 20) =>
    request.get<ImageList>("/images", { params: { page, page_size: pageSize } }),
  uploadImage: (file: File, apiKey?: string) => {
    const form = new FormData()
    form.append("file", file)
    return request.post<Image>("/images/upload", form, {
      params: apiKey ? { api_key: apiKey } : {},
    })
  },
  deleteImage: (id: number) => request.delete(`/images/${id}`),

  listApiKeys: () => request.get<ApiKey[]>("/apikeys"),
  createApiKey: (name: string) =>
    request.post<ApiKey & { key: string }>("/apikeys", { name }),
  deleteApiKey: (id: number) => request.delete(`/apikeys/${id}`),

  // admin
  adminStats: () => request.get<Stats>("/admin/stats"),
  adminListUsers: () => request.get<User[]>("/admin/users"),
  adminCreateUser: (data: { username: string; email?: string; password: string; is_admin: boolean }) =>
    request.post<User>("/admin/users", data),
  adminUpdateUser: (id: number, data: Record<string, unknown>) =>
    request.put<User>(`/admin/users/${id}`, data),
  adminDeleteUser: (id: number) => request.delete(`/admin/users/${id}`),
  adminListImages: (page = 1, pageSize = 20) =>
    request.get<ImageList>("/admin/images", { params: { page, page_size: pageSize } }),
  adminDeleteImage: (id: number) => request.delete(`/admin/images/${id}`),
}

export default api
