import { defineStore } from 'pinia'
import api from '@/services/api'

export const useParchesStore = defineStore('parches', {
  state: () => ({
    parches:       [],
    parcheActual:  null,
  }),

  actions: {
    async fetchParches() {
      const { data } = await api.get('/parches/')
      this.parches = data
    },

    async fetchParche(id) {
      const { data } = await api.get(`/parches/${id}/`)
      this.parcheActual = data
      return data
    },

    async crearParche(parcheData) {
      const { data } = await api.post('/parches/', parcheData)
      this.parches.push(data)
      return data
    },

    async unirseParche(inviteCode) {
      const { data } = await api.post('/parches/join/', { invite_code: inviteCode })
      this.parches.push(data)
      return data
    },
  },
})