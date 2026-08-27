import { defineStore } from 'pinia'
import { login as loginApi, getUserInfo, logout as logoutApi } from '@/api'
import { resetRouter } from '@/router'

interface UserState {
  token: string | null
  username: string
  nickname: string
  avatar: string | null
  permissions: string[]
  menus: any[]
  roles: string[]
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('apeadmin_token'),
    username: '',
    nickname: '',
    avatar: null,
    permissions: [],
    menus: [],
    roles: [],
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    async login(username: string, password: string, captcha?: { captcha_id: string; captcha_code: string }) {
      const data: any = await loginApi({ username, password, ...captcha })
      this.token = data.access_token
      localStorage.setItem('apeadmin_token', data.access_token)
      await this.fetchUserInfo()
    },

    async fetchUserInfo() {
      const data: any = await getUserInfo()
      this.username = data.username
      this.nickname = data.nickname
      this.avatar = data.avatar
      this.permissions = data.permissions || []
      this.menus = data.menus || []
      this.roles = data.roles || []
    },

    hasPermission(perm: string) {
      if (this.permissions.includes('*')) return true
      return this.permissions.includes(perm)
    },

    async logout() {
      try {
        await logoutApi()
      } catch {
        // ignore network errors on logout
      }
      this.reset()
    },

    reset() {
      this.token = null
      this.username = ''
      this.nickname = ''
      this.avatar = null
      this.permissions = []
      this.menus = []
      this.roles = []
      localStorage.removeItem('apeadmin_token')
      resetRouter()
    },
  },
})
