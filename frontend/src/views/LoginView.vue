<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="bg-white p-8 rounded-2xl shadow-md w-full max-w-md">
      <h1 class="text-3xl font-bold text-center text-indigo-600 mb-2">ParCheck</h1>
      <p class="text-center text-gray-500 mb-6">Gestiona tus gastos compartidos</p>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
          <input
            v-model="form.username"
            placeholder="tu_usuario"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button
          type="submit"
          class="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition font-medium"
        >
          Ingresar
        </button>
      </form>

      <p class="text-center text-sm text-gray-500 mt-4">
        ¿No tienes cuenta?
        <router-link to="/register" class="text-indigo-600 hover:underline">Regístrate</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const auth   = useAuthStore()
const router = useRouter()
const error  = ref(null)
const form   = reactive({ username: '', password: '' })

const handleLogin = async () => {
  try {
    await auth.login(form.username, form.password)
    router.push('/')
  } catch {
    error.value = 'Credenciales incorrectas'
  }
}
</script>