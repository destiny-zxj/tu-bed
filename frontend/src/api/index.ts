import request from "./request"

export interface User {
  id: number
  username: string
  email?: string
  is_admin: boolean
  is_active: boolean
  created_at: string
}

export interface TagBrief {
  id: number
  name: string
}

export interface Tag {
  id: number
  name: string
  image_count: number
  created_at: string
}

export interface Image {
  id: number
  owner_id: number
  owner_username?: string | null
  url: string
  original_name: string
  mime_type: string
  size: number
  width?: number
  height?: number
  created_at: string
  tags: TagBrief[]
}

export interface ImageList {
  total: number
  items: Image[]
}

export interface PagedList<T> {
  total: number
  items: T[]
}

export interface Stats {
  total_users: number
  total_images: number
  total_storage_bytes: number
}

export interface ApiKey {
  id: number
  name: string
  prefix: string
  is_active: boolean
  created_at: string
  last_used_at?: string | null
}

export interface ApiKeyCreated extends ApiKey {
  key: string
}

const api = {
  login: (username: string, password: string) =>
    request.post<{ access_token: string }>("/auth/login", { username, password }),
  me: () => request.get<User>("/auth/me"),

  listImages: (page = 1, pageSize = 20, tagId?: number) =>
    request.get<ImageList>("/images", {
      params: { page, page_size: pageSize, tag_id: tagId },
    }),
  uploadImage: (
    file: File,
    options?: {
      apiKey?: string
      onProgress?: (percent: number) => void
      signal?: AbortSignal
    },
  ) => {
    const form = new FormData()
    form.append("file", file)
    return request.post<Image>("/images/upload", form, {
      params: options?.apiKey ? { api_key: options.apiKey } : {},
      signal: options?.signal,
      onUploadProgress: options?.onProgress
        ? (e: { loaded: number; total?: number }) => {
            const total = e.total ?? file.size
            const percent = total ? Math.min(99, Math.round((e.loaded / total) * 100)) : 0
            options.onProgress!(percent)
          }
        : undefined,
    })
  },
  deleteImage: (id: number) => request.delete(`/images/${id}`),

  // tags
  listTags: () => request.get<Tag[]>("/tags"),
  createTag: (name: string) => request.post<Tag>("/tags", { name }),
  renameTag: (id: number, name: string) => request.put<Tag>(`/tags/${id}`, { name }),
  deleteTag: (id: number) => request.delete(`/tags/${id}`),
  listImageTags: (imageId: number) => request.get<TagBrief[]>(`/images/${imageId}/tags`),
  setImageTags: (imageId: number, tagIds: number[]) =>
    request.put<TagBrief[]>(`/images/${imageId}/tags`, { tag_ids: tagIds }),

  // api keys
  listApiKeys: (page = 1, pageSize = 20) =>
    request.get<PagedList<ApiKey>>("/apikeys", { params: { page, page_size: pageSize } }),
  createApiKey: (name: string) => request.post<ApiKeyCreated>("/apikeys", { name }),
  deleteApiKey: (id: number) => request.delete(`/apikeys/${id}`),

  // admin
  adminStats: () => request.get<Stats>("/admin/stats"),
  adminListUsers: (page = 1, pageSize = 20) =>
    request.get<PagedList<User>>("/admin/users", { params: { page, page_size: pageSize } }),
  adminCreateUser: (data: { username: string; email?: string; password: string; is_admin: boolean }) =>
    request.post<User>("/admin/users", data),
  adminUpdateUser: (id: number, data: Record<string, unknown>) =>
    request.put<User>(`/admin/users/${id}`, data),
  adminDeleteUser: (id: number) => request.delete(`/admin/users/${id}`),
  adminListImages: (page = 1, pageSize = 20, params: Record<string, unknown> = {}) =>
    request.get<ImageList>("/admin/images", { params: { page, page_size: pageSize, ...params } }),
  adminDeleteImage: (id: number) => request.delete(`/admin/images/${id}`),
  adminBatchDeleteImages: (ids: number[]) =>
    request.post<{ deleted: number; skipped: number; missing_ids: number[] }>("/admin/images/batch-delete", {
      image_ids: ids,
    }),

  // settings - user
  updateEmail: (email: string) => request.put<User>("/settings/user/email", { email }),
  updatePassword: (current_password: string, new_password: string) =>
    request.put<{ message: string }>("/settings/user/password", { current_password, new_password }),

  // settings - system storage
  getStorageConfig: () => request.get<StorageConfig>("/settings/storage"),
  updateStorageConfig: (data: Partial<StorageConfig>) =>
    request.put<StorageConfig>("/settings/storage", data),
}

export interface StorageConfig {
  drive: "local" | "s3" | "qiniu" | "oss" | "cos"
  upload_dir?: string | null
  public_base_url?: string | null
  qiniu_access_key?: string | null
  qiniu_secret_key?: string | null
  qiniu_bucket?: string | null
  qiniu_domain?: string | null
  s3_endpoint_url?: string | null
  s3_region_name?: string | null
  s3_access_key?: string | null
  s3_secret_key?: string | null
  s3_bucket?: string | null
  s3_public_domain?: string | null
  oss_endpoint?: string | null
  oss_bucket_name?: string | null
  oss_access_key_id?: string | null
  oss_access_key_secret?: string | null
  oss_public_url?: string | null
  cos_region?: string | null
  cos_bucket?: string | null
  cos_secret_id?: string | null
  cos_secret_key?: string | null
  cos_public_url?: string | null
}

export default api
