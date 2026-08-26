import axios from "axios"
import { useAuthStore } from "@/stores/auth"

const request = axios.create({
  baseURL: "/api",
  timeout: 30000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token")
      useAuthStore().clear()
    }
    return Promise.reject(error)
  },
)

export default request
