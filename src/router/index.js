import { createRouter, createWebHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'welcome',
      component: WelcomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    // Owner dashboard
    {
      path: '/dashboard/pemilik',
      name: 'dashboard-owner',
      component: () => import('../views/DashboardOwner.vue'),
      meta: { requiresAuth: true, role: 'pengelola' },
    },
    // Tenant dashboard
    {
      path: '/dashboard/penghuni',
      name: 'dashboard-tenant',
      component: () => import('../views/DashboardTenant.vue'),
      meta: { requiresAuth: true, role: 'anak-kost' },
    },
  ],
})

// Global navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // redirect unauthenticated users to login, preserve intended route
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  if (to.meta.role && authStore.role !== to.meta.role) {
    // If user role mismatched, redirect to appropriate dashboard
    const target = authStore.role === 'pengelola' ? '/dashboard/pemilik' : '/dashboard/penghuni'
    next({ path: target })
    return
  }
  next()
})

export default router
