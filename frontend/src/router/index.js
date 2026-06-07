import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const routes = [
  {
    path:      '/login',
    name:      'login',
    component: () => import('@/views/LoginView.vue'),
    meta:      { public: true },
  },
  {
    path:      '/register',
    name:      'register',
    component: () => import('@/views/RegisterView.vue'),
    meta:      { public: true },
  },
  {
    path:      '/',
    name:      'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path:      '/parches/:id',
    name:      'parche',
    component: () => import('@/views/ParcheView.vue'),
  },
  {
    path:      '/perfil',
    name:      'perfil',
    component: () => import('@/views/ProfileView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Protege las rutas que requieren autenticación
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login' }
  }
})

export default router