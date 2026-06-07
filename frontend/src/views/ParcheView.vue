<template>
  <div class="min-h-screen bg-gray-50" v-if="auth.user">
    <!-- Navbar -->
    <nav class="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
      <router-link to="/" class="text-indigo-600 font-medium hover:underline">← Volver</router-link>
      <h1 class="text-xl font-bold text-indigo-600">{{ parche?.name }}</h1>
      <span class="text-sm text-gray-500">{{ parche?.members_count }} miembros</span>
    </nav>

    <div class="max-w-2xl mx-auto px-4 py-8 space-y-6">

      <!-- Código invitación -->
      <div class="bg-indigo-50 border border-indigo-200 rounded-xl px-5 py-3 flex justify-between items-center">
        <span class="text-sm text-indigo-700">Código de invitación</span>
        <strong class="text-indigo-800 tracking-widest">{{ parche?.invite_code }}</strong>
      </div>

      <!-- Balance personal -->
      <div class="bg-white rounded-xl shadow-sm p-5">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Mi balance</h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-green-50 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500 mb-1">Pagado</p>
            <p class="text-lg font-bold text-green-600">${{ balance.pagado }}</p>
          </div>
          <div class="bg-blue-50 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500 mb-1">Recibido</p>
            <p class="text-lg font-bold text-blue-600">${{ balance.recibido }}</p>
          </div>
          <div class="bg-red-50 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500 mb-1">Deudas</p>
            <p class="text-lg font-bold text-red-500">${{ balance.deudas }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500 mb-1">Neto</p>
            <p class="text-lg font-bold text-gray-700">${{ balance.neto }}</p>
          </div>
        </div>
      </div>

      <!-- Crear evento -->
      <div class="bg-white rounded-xl shadow-sm p-5">
        <h2 class="text-lg font-semibold text-gray-800 mb-3">Crear evento</h2>
        <form @submit.prevent="handleCrearEvento" class="space-y-3">
          <input
            v-model="eventoForm.name"
            placeholder="Nombre del evento"
            required
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <input
            v-model="eventoForm.total_amount"
            placeholder="Monto total"
            type="number"
            required
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <select
            v-model="eventoForm.split_type"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
          <option disabled value="">
          Seleccione un responsable
          </option>
          
            <option value="equal">Partes iguales</option>
            <option value="custom">Monto personalizado</option>
          </select>
          
          <select 
            v-model="eventoForm.responsible_id" required
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
          <option disabled value="">
          Seleccione un responsable
          </option>

          <option
            v-for="miembro in miembros"
            :key="miembro.id"
            :value="miembro.id"
          >
            {{ miembro.username }}
          </option>
        </select>

          <button
            type="submit"
            class="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition font-medium"
          >

            Crear evento
          </button>
        </form>
      </div>

      <!-- Lista de eventos -->
      <div class="space-y-4">
        <h2 class="text-lg font-semibold text-gray-800">Eventos</h2>

        <div
          v-for="(evento, i) in eventos"
          :key="i"
          class="bg-white rounded-xl shadow-sm p-5"
        >
          <div class="flex justify-between items-start mb-3">
            <div>
              <p class="font-semibold text-gray-800">{{ evento.name }}</p>
              <p class="text-sm text-gray-500">Total: ${{ evento.total_amount }}</p>
            </div>
            <span class="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">
              {{ evento.participants?.length }} participantes
            </span>
          </div>

          <div class="space-y-2">
            <div
              v-for="(p, j) in evento.participants"
              :key="j"
              class="flex justify-between items-center bg-gray-50 rounded-lg px-4 py-2"
            >
              <div>
                <p class="text-sm font-medium text-gray-700">{{ p.user?.username }}</p>
                <p class="text-xs text-gray-500">${{ p.amount_owed }}</p>
              </div>
              <div>
                <span v-if="p.paid" class="text-green-500 text-sm font-medium">✅ Pagado</span>
                <button
                  v-else-if="p.user && auth.user && p.user.id === auth.user.id"
                  @click="handlePagar(p.id)"
                  class="text-xs bg-green-600 text-white px-3 py-1 rounded-full hover:bg-green-700 transition"
                >
                  Marcar pagado
                </button>
                <span v-else class="text-red-400 text-sm">❌ Pendiente</span>
              </div>
            </div>
          </div>
        </div>

        <p v-if="eventos.length === 0" class="text-gray-400 text-sm text-center">
          No hay eventos aún
        </p>
      </div>

      <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
    </div>
  </div>

  <div v-else class="min-h-screen flex items-center justify-center">
    <p class="text-gray-400">Cargando...</p>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useParchesStore } from '@/stores/parches.js'
import { useAuthStore } from '@/stores/auth.js'
import api from '@/services/api.js'

const route   = useRoute()
const parches = useParchesStore()
const auth    = useAuthStore()
const parche  = ref(null)
const eventos = ref([])
const miembros = ref([])
const error   = ref(null)
const balance = ref({ pagado: 0, recibido: 0, deudas: 0, neto: 0 })

const eventoForm = reactive({
  name:         '',
  total_amount: '',
  split_type:   'equal',
})

onMounted(async () => {
  await auth.fetchProfile()
  parche.value = await parches.fetchParche(route.params.id)

  await fetchEventos()
  await fetchBalance()
  await fetchMiembros()
})

const fetchEventos = async () => {
  try {
    const { data } = await api.get(`/parches/${route.params.id}/eventos/`)
    eventos.value = data.map(evento => ({
      ...evento,
      participants: evento.participants.filter(p => p !== null && p.user !== null)
    }))
  } catch (e) {
    console.error('error cargando eventos:', e.response?.data)
  }
}

const fetchBalance = async () => {
  const { data } = await api.get(`/parches/${route.params.id}/balance/personal/`)
  balance.value = data
}

const fetchMiembros = async () => {
  try {
    const { data } = await api.get(
      `/parches/${route.params.id}/members/`
    )

    miembros.value = data
  } catch (e) {
    console.error('error cargando miembros:', e.response?.data)
  }
}

const handleCrearEvento = async () => {
  try {
    await api.post(`/parches/${route.params.id}/eventos/`, {
      name:            eventoForm.name,
      total_amount:    eventoForm.total_amount,
      split_type:      eventoForm.split_type,
      responsible_id:  eventoForm.responsible_id || null,
      participant_ids: [auth.user.id],
    })
    eventoForm.name         = ''
    eventoForm.total_amount = ''
    error.value             = null
    await fetchEventos()
    await fetchBalance()
  } catch {
    error.value = 'Error al crear el evento'
  }
}

const handlePagar = async (participanteId) => {
  try {
    await api.patch(`/participantes/${participanteId}/pagar/`, {})
    await fetchEventos()
    await fetchBalance()
  } catch {
    error.value = 'Error al marcar el pago'
  }
}
</script>
