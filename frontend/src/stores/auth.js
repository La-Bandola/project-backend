import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user:  null,
    token: localStorage.getItem('access_token') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async login(username, password) {
      const { data } = await api.post('/users/login/', { username, password })
      localStorage.setItem('access_token',  data.access)
      localStorage.setItem('refresh_token', data.refresh)
      this.token = data.access
      await this.fetchProfile()
    },

    async register(userData) {
      const { data } = await api.post('/users/register/', userData)
      localStorage.setItem('access_token',  data.access)
      localStorage.setItem('refresh_token', data.refresh)
      this.token = data.access
      this.user  = data.user
    },

    async fetchProfile() {
      const { data } = await api.get('/users/me/')
      this.user = data
    },

    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      this.token = null
      this.user  = null
    },
  },
})