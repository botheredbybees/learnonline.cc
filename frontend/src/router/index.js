import { createRouter, createWebHistory } from 'vue-router';
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { guest: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/units/:id',
    name: 'Unit',
    component: () => import('../views/Unit.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/quests',
    name: 'Quests',
    component: () => import('../views/Quests.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/quests/:id',
    name: 'QuestDetail',
    component: () => import('../views/Quests.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/intro-quest/:id',
    name: 'IntroductoryQuest',
    component: () => import('../views/IntroductoryQuest.vue'),
    // No auth required for introductory quests
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isLoggedIn = store.state.auth.isLoggedIn
  const isAdmin = store.state.auth.user?.is_admin

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      next({ name: 'Login' })
    } else if (to.matched.some(record => record.meta.requiresAdmin) && !isAdmin) {
      // If route requires admin but user is not an admin
      next({ name: 'Home' })
    } else {
      next()
    }
  } else if (to.matched.some(record => record.meta.guest)) {
    if (isLoggedIn) {
      next({ name: 'Home' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router