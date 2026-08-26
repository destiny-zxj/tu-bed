import { defineStore } from "pinia"
import { ref } from "vue"
import api, { type User } from "@/api"

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem("token") || "")
  const user = ref<User | null>(null)

  async function login(username: string, password: string) {
    const { data } = await api.login(username, password)
    token.value = data.access_token
    localStorage.setItem("token", data.access_token)
    await fetchMe()
  }

  async function fetchMe() {
    if (!token.value) return
    const { data } = await api.me()
    user.value = data
  }

  function clear() {
    token.value = ""
    user.value = null
  }

  function logout() {
    clear()
    localStorage.removeItem("token")
  }

  return { token, user, login, fetchMe, clear, logout }
})
