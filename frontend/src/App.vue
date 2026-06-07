<template>
  <router-view v-if="listo" />
  <p v-else>Cargando...</p>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

const auth  = useAuthStore()
const listo = ref(false)

onMounted(async () => {
  if (auth.token) {
    try {
      await auth.fetchProfile()
    } catch {
      auth.logout()
    }
  }
  listo.value = true  // ← solo renderiza cuando el perfil está listo
})
</script>